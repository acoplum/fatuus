"""Autenticação HTTP Basic para a API do Fatuus, como middleware ASGI.

Cobre HTTP e WebSocket, e roda antes do roteamento — por isso alcança o
`Mount` do StaticFiles do frontend (Camada 2) e as rotas nativas do
AgentOS, que `Depends` por rota nunca cobriu.
"""

import base64
import binascii
import os
import secrets
from typing import Optional, Tuple

from starlette.types import ASGIApp, Receive, Scope, Send


def _expected_credentials() -> Tuple[str, str]:
    user = os.environ.get("FATUUS_BASIC_AUTH_USER")
    password = os.environ.get("FATUUS_BASIC_AUTH_PASSWORD")
    if not user or not password:
        raise RuntimeError(
            "FATUUS_BASIC_AUTH_USER e FATUUS_BASIC_AUTH_PASSWORD precisam "
            "estar definidos no ambiente antes de subir a API."
        )
    return user, password


def _parse_basic_auth_header(header: Optional[str]) -> Optional[Tuple[str, str]]:
    if not header or not header.lower().startswith("basic "):
        return None
    try:
        decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None
    if ":" not in decoded:
        return None
    username, password = decoded.split(":", 1)
    return username, password


def is_authorized(authorization_header: Optional[str]) -> bool:
    """Valida o header `Authorization: Basic ...` contra as credenciais do ambiente."""
    credentials = _parse_basic_auth_header(authorization_header)
    if credentials is None:
        return False
    username, password = credentials
    expected_user, expected_password = _expected_credentials()
    return secrets.compare_digest(username, expected_user) and secrets.compare_digest(
        password, expected_password
    )


class BasicAuthMiddleware:
    """Middleware ASGI puro: cobre `http` e `websocket`, antes do roteamento.

    `@app.middleware("http")` do FastAPI é `BaseHTTPMiddleware`, que ignora
    qualquer escopo que não seja `http` — uma conexão WebSocket passaria
    direto, sem checar credencial. Implementar no nível ASGI evita essa
    lacuna.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        raw_header = headers.get(b"authorization")
        header_value = raw_header.decode("latin-1") if raw_header else None

        if is_authorized(header_value):
            await self.app(scope, receive, send)
            return

        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 4401})
            return

        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"www-authenticate", b"Basic"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"detail": "Credenciais inv\\u00e1lidas"}',
            }
        )
