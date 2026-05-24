import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.auth import router  # noqa: E402
from app.services.security import require_current_user  # noqa: E402

TEST_USER = {
    "id": 3,
    "full_name": "Morgan Patel",
    "email": "morgan@example.com",
    "created_at": "2026-05-24T11:00:00",
}


class AuthApiTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[require_current_user] = lambda: TEST_USER
        self.client = TestClient(app)

    @patch("app.api.auth.create_session")
    @patch("app.api.auth.create_session_token", return_value="token-123")
    @patch("app.api.auth.create_user")
    @patch("app.api.auth.hash_password", return_value=("hash-value", "salt-value"))
    def test_register_returns_token_and_user(
        self,
        _mock_hash_password,
        mock_create_user,
        _mock_create_session_token,
        mock_create_session,
    ):
        mock_create_user.return_value = TEST_USER

        response = self.client.post(
            "/auth/register",
            json={
                "full_name": "Morgan Patel",
                "email": "morgan@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["token"], "token-123")
        self.assertEqual(response.json()["user"]["email"], "morgan@example.com")
        mock_create_session.assert_called_once_with(3, "token-123")

    @patch("app.api.auth.verify_password", return_value=False)
    @patch("app.api.auth.get_user_by_email")
    def test_login_rejects_invalid_credentials(
        self,
        mock_get_user_by_email,
        _mock_verify_password,
    ):
        mock_get_user_by_email.return_value = {
            **TEST_USER,
            "password_hash": "wrong-hash",
            "password_salt": "wrong-salt",
        }

        response = self.client.post(
            "/auth/login",
            json={
                "email": "morgan@example.com",
                "password": "bad-password",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid email or password.")

    def test_me_returns_current_user(self):
        response = self.client.get(
            "/auth/me",
            headers={"Authorization": "Bearer active-token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["full_name"], "Morgan Patel")


if __name__ == "__main__":
    unittest.main()
