import os
import unittest
from unittest.mock import patch

os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from fatuus.models import build_model


class TestBuildModel(unittest.TestCase):
    def test_defaults_to_gemini(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FATUUS_MODEL_PROVIDER", None)
            model = build_model()
        self.assertEqual(type(model).__name__, "Gemini")

    def test_gemini_model_id_env_compat(self):
        with patch.dict(
            os.environ,
            {"FATUUS_MODEL_PROVIDER": "gemini", "FATUUS_GEMINI_MODEL": "gemini-x"},
        ):
            model = build_model()
        self.assertEqual(model.id, "gemini-x")

    def test_fatuus_model_id_wins_over_gemini_env(self):
        with patch.dict(
            os.environ,
            {
                "FATUUS_MODEL_PROVIDER": "gemini",
                "FATUUS_GEMINI_MODEL": "gemini-x",
                "FATUUS_MODEL_ID": "gemini-y",
            },
        ):
            model = build_model()
        self.assertEqual(model.id, "gemini-y")

    def test_vllm_requires_model_id(self):
        with patch.dict(os.environ, {"FATUUS_MODEL_PROVIDER": "vllm"}):
            os.environ.pop("FATUUS_MODEL_ID", None)
            with self.assertRaises(ValueError):
                build_model()

    def test_unknown_provider_raises(self):
        with patch.dict(os.environ, {"FATUUS_MODEL_PROVIDER": "banana"}):
            with self.assertRaises(ValueError):
                build_model()


if __name__ == "__main__":
    unittest.main()
