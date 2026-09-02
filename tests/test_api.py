import os
import unittest
from unittest.mock import patch

os.environ["FATUUS_BASIC_AUTH_USER"] = "tester@example.com"
os.environ["FATUUS_BASIC_AUTH_PASSWORD"] = "s3cret-test-value"
os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from fastapi.testclient import TestClient

from fatuus.api import MAX_TEXT_LENGTH, app
from fatuus.auth import require_basic_auth
from fatuus.gate import GateResult
from fatuus.pipeline import PipelineResult

AUTH = ("tester@example.com", "s3cret-test-value")

client = TestClient(app)

# Rotas de documentação geradas pelo próprio FastAPI: são `starlette.routing.Route`,
# não carregam dependências e só expõem a superfície da API, não dados.
DOC_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


def _carries_auth_dependency(route) -> bool:
    dependant = getattr(route, "dependant", None)
    if dependant is None:
        return False
    pending = [dependant]
    while pending:
        current = pending.pop()
        if current.call is require_basic_auth:
            return True
        pending.extend(current.dependencies)
    return False


class TestProbeEndpoint(unittest.TestCase):
    def test_requires_auth(self):
        response = client.post("/probe", json={"text": "olá", "lang": "pt"})
        self.assertEqual(response.status_code, 401)

    def test_returns_camada0_analysis(self):
        response = client.post(
            "/probe", json={"text": "É importante ressaltar que sim."}, auth=AUTH
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("synthetic_score", body)
        self.assertGreater(body["slop_count"], 0)


class TestCleanEndpoint(unittest.TestCase):
    @patch("fatuus.api.HumanizationPipeline.run")
    def test_returns_pipeline_result(self, mock_run):
        mock_run.return_value = PipelineResult(
            final_text="Texto limpo.",
            accepted=True,
            attempts=1,
            gate=GateResult(accepted=True, reasons=[]),
        )
        response = client.post(
            "/clean",
            json={"text": "É importante ressaltar que sim.", "lang": "pt"},
            auth=AUTH,
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["cleaned_text"], "Texto limpo.")
        self.assertTrue(body["layer1_accepted"])

    @patch("fatuus.api.HumanizationPipeline.run")
    def test_passes_the_pre_sanitization_text_as_gate_baseline(self, mock_run):
        mock_run.return_value = PipelineResult(
            final_text="Texto limpo.",
            accepted=True,
            attempts=1,
            gate=GateResult(accepted=True, reasons=[]),
        )
        original = "É importante ressaltar que sim."

        client.post("/clean", json={"text": original, "lang": "pt"}, auth=AUTH)

        self.assertEqual(mock_run.call_args.kwargs["original_text"], original)


class TestInputSizeLimit(unittest.TestCase):
    """Achado #5: uma chamada a /clean pode virar até 12 chamadas ao Gemini."""

    def test_rejects_text_above_the_limit(self):
        for path in ("/probe", "/clean"):
            with self.subTest(path=path):
                response = client.post(
                    path,
                    json={"text": "a" * (MAX_TEXT_LENGTH + 1), "lang": "pt"},
                    auth=AUTH,
                )
                self.assertEqual(response.status_code, 422)

    def test_accepts_text_at_the_limit(self):
        response = client.post(
            "/probe", json={"text": "a" * MAX_TEXT_LENGTH, "lang": "pt"}, auth=AUTH
        )
        self.assertEqual(response.status_code, 200)


class TestRouteAuthInventory(unittest.TestCase):
    """Regressão do achado Critical #1: rotas montadas pelo AgentOS sem auth.

    Inclui a rota WebSocket `/workflows/ws`, que passa a falhar fechada:
    `HTTPBasic` só aceita `Request`, então a dependência levanta antes do
    handshake. Nenhum agente ou workflow é registrado no AgentOS hoje, então
    essa rota não é usada — se a Fase 3 precisar dela, o auth de WebSocket
    tem que ser escrito à parte.
    """

    def test_every_mounted_route_carries_the_auth_dependency(self):
        unprotected = [
            f"{sorted(getattr(route, 'methods', []) or ['WS'])} {route.path}"
            for route in app.routes
            if route.path not in DOC_PATHS and not _carries_auth_dependency(route)
        ]
        self.assertEqual(unprotected, [], f"{len(unprotected)} rota(s) sem auth")

    def test_agentos_routes_reject_anonymous_requests(self):
        rotas = (("GET", "/config"), ("GET", "/sessions"), ("POST", "/memories"))
        for method, path in rotas:
            with self.subTest(path=path):
                response = client.request(method, path, json={})
                self.assertEqual(response.status_code, 401)

    def test_agentos_routes_accept_authenticated_requests(self):
        response = client.get("/config", auth=AUTH)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
