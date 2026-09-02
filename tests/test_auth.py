import base64
import os
import unittest

os.environ["FATUUS_BASIC_AUTH_USER"] = "tester@example.com"
os.environ["FATUUS_BASIC_AUTH_PASSWORD"] = "s3cret-test-value"

from fatuus.auth import is_authorized


def _basic_header(username: str, password: str) -> str:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"


class TestIsAuthorized(unittest.TestCase):
    def test_rejects_missing_header(self):
        self.assertFalse(is_authorized(None))

    def test_rejects_non_basic_scheme(self):
        self.assertFalse(is_authorized("Bearer abc123"))

    def test_rejects_malformed_base64(self):
        self.assertFalse(is_authorized("Basic not-valid-base64!!"))

    def test_rejects_wrong_password(self):
        header = _basic_header("tester@example.com", "senha-errada")
        self.assertFalse(is_authorized(header))

    def test_accepts_correct_credentials(self):
        header = _basic_header("tester@example.com", "s3cret-test-value")
        self.assertTrue(is_authorized(header))

    def test_rejects_non_ascii_credentials_without_crashing(self):
        header = _basic_header("usuário", "senhá")
        self.assertFalse(is_authorized(header))


if __name__ == "__main__":
    unittest.main()
