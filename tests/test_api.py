import os
import unittest
from unittest.mock import patch

os.environ["FATUUS_BASIC_AUTH_USER"] = "tester@example.com"
os.environ["FATUUS_BASIC_AUTH_PASSWORD"] = "s3cret-test-value"
os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from fastapi.testclient import TestClient

from fatuus.api import app
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


if __name__ == "__main__":
    unittest.main()
