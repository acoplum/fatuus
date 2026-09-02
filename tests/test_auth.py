import os
import unittest

os.environ["FATUUS_BASIC_AUTH_USER"] = "tester@example.com"
os.environ["FATUUS_BASIC_AUTH_PASSWORD"] = "s3cret-test-value"

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fatuus.auth import require_basic_auth

app = FastAPI()


@app.get("/protegido")
def protegido(user: str = Depends(require_basic_auth)):
    return {"user": user}


client = TestClient(app)


class TestRequireBasicAuth(unittest.TestCase):
    def test_rejects_missing_credentials(self):
        response = client.get("/protegido")
        self.assertEqual(response.status_code, 401)

    def test_rejects_wrong_password(self):
        response = client.get(
            "/protegido", auth=("tester@example.com", "senha-errada")
        )
        self.assertEqual(response.status_code, 401)

    def test_accepts_correct_credentials(self):
        response = client.get(
            "/protegido", auth=("tester@example.com", "s3cret-test-value")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"user": "tester@example.com"})


if __name__ == "__main__":
    unittest.main()
