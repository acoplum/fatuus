import os
import unittest
from unittest.mock import patch

os.environ["FATUUS_BASIC_AUTH_USER"] = "tester@example.com"
os.environ["FATUUS_BASIC_AUTH_PASSWORD"] = "s3cret-test-value"
os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from fastapi.testclient import TestClient

from starlette.websockets import WebSocketDisconnect

from fatuus.api import MAX_TEXT_LENGTH, app
from fatuus.gate import GateResult
from fatuus.pipeline import PipelineResult

AUTH = ("tester@example.com", "s3cret-test-value")

client = TestClient(app)


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


class TestBasicAuthMiddleware(unittest.TestCase):
    """Regressão do achado Critical #1: rotas montadas pelo AgentOS sem auth.

    A proteção migrou de `Depends` por rota para middleware ASGI (Camada 2):
    `Depends` não cobre `Mount` (StaticFiles do frontend) nem a WebSocket do
    AgentOS de forma explícita. O middleware roda antes do roteamento e
    cobre tudo — rotas próprias, as rotas do AgentOS, WebSocket e os
    estáticos.
    """

    def test_rejects_unauthenticated_requests_to_every_known_surface(self):
        self.assertEqual(client.post("/probe", json={}).status_code, 401)
        self.assertEqual(client.post("/clean", json={}).status_code, 401)
        self.assertEqual(client.get("/config").status_code, 401)
        self.assertEqual(client.get("/sessions").status_code, 401)
        self.assertEqual(client.post("/memories", json={}).status_code, 401)
        self.assertEqual(client.get("/").status_code, 401)

    def test_accepts_authenticated_requests(self):
        response = client.get("/config", auth=AUTH)
        self.assertEqual(response.status_code, 200)

    def test_rejects_wrong_credentials(self):
        response = client.get("/config", auth=("tester@example.com", "senha-errada"))
        self.assertEqual(response.status_code, 401)

    def test_websocket_route_rejects_unauthenticated_handshake(self):
        with self.assertRaises(WebSocketDisconnect) as cm:
            with client.websocket_connect("/workflows/ws"):
                pass
        self.assertEqual(cm.exception.code, 4401)

    def test_websocket_route_accepts_authenticated_handshake(self):
        with client.websocket_connect("/workflows/ws", auth=AUTH):
            pass


if __name__ == "__main__":
    unittest.main()
