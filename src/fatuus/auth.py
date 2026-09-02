"""Autenticação HTTP Basic para a API do Fatuus."""

import os
import secrets
from typing import Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

_security = HTTPBasic()


def _expected_credentials() -> Tuple[str, str]:
    user = os.environ.get("FATUUS_BASIC_AUTH_USER")
    password = os.environ.get("FATUUS_BASIC_AUTH_PASSWORD")
    if not user or not password:
        raise RuntimeError(
            "FATUUS_BASIC_AUTH_USER e FATUUS_BASIC_AUTH_PASSWORD precisam "
            "estar definidos no ambiente antes de subir a API."
        )
    return user, password


def require_basic_auth(
    credentials: HTTPBasicCredentials = Depends(_security),
) -> str:
    expected_user, expected_password = _expected_credentials()
    user_ok = secrets.compare_digest(credentials.username, expected_user)
    password_ok = secrets.compare_digest(credentials.password, expected_password)
    if not (user_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
