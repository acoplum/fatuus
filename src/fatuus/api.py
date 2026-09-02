"""App FastAPI/AgentOS da Camada 0 + Camada 1 do Fatuus."""

import os
from pathlib import Path

from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.os import AgentOS
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .auth import BasicAuthMiddleware
from .detector import FatuusDetector
from .pipeline import HumanizationPipeline
from .sanitizer import FatuusSanitizer

MODEL_ID = os.environ.get("FATUUS_GEMINI_MODEL", "gemini-3.7-flash")

# 20 000 caracteres ≈ 3 300 palavras em PT-BR: um artigo ou post longo, que é
# o caso de uso real da ferramenta. O teto existe por custo, não por formato:
# uma chamada a /clean vira até 12 chamadas ao Gemini (3 iterações × até 4
# agentes), cada uma carregando o texto inteiro na entrada e na saída — nesse
# limite, ~120 mil tokens de tráfego no pior caso de uma única requisição.
MAX_TEXT_LENGTH = 20_000


class TextRequest(BaseModel):
    text: str = Field(max_length=MAX_TEXT_LENGTH)
    lang: str = "pt"


base_app = FastAPI(title="Fatuus API", version="0.1.0")
base_app.add_middleware(BasicAuthMiddleware)


@base_app.post("/probe")
def probe(payload: TextRequest) -> dict:
    detector = FatuusDetector(lang=payload.lang)
    return detector.analyze(payload.text)


@base_app.post("/clean")
def clean(payload: TextRequest) -> dict:
    sanitizer = FatuusSanitizer(lang=payload.lang)
    sanitized = sanitizer.clean(payload.text)

    pipeline = HumanizationPipeline(Gemini(id=MODEL_ID), lang=payload.lang)
    result = pipeline.run(sanitized["cleaned_text"], original_text=payload.text)

    return {
        "cleaned_text": result.final_text,
        "layer0": sanitized,
        "layer1_accepted": result.accepted,
        "layer1_attempts": result.attempts,
        "gate_reasons": result.gate.reasons,
    }


# Build do frontend (Camada 2): `npm run build` em frontend/ gera
# frontend/dist/, que o Dockerfile copia para o mesmo caminho relativo
# dentro da imagem.
STATIC_DIR = os.environ.get("FATUUS_STATIC_DIR", "frontend/dist")


# Registrada em `base_app`, antes de `AgentOS(...)` construir sua própria
# rota `GET /` (que devolve metadados da API, não o frontend). Por padrão o
# AgentOS resolve esse conflito de rota substituindo a nossa pela dele
# (`on_route_conflict="preserve_agentos"`); por isso o construtor abaixo passa
# `on_route_conflict="preserve_base_app"` explicitamente, para que a rota
# definida aqui vença. Sem o build do frontend presente, devolve 404 em vez
# de quebrar a importação do módulo.
@base_app.get("/")
def frontend_index():
    index_path = Path(STATIC_DIR) / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(index_path)


# Nenhum agente é registrado diretamente no AgentOS: a Camada 1 constrói os
# 4 agentes por requisição (pipeline.py), porque o texto e o idioma variam
# a cada chamada. Registrar agentes fixos aqui fica para quando o frontend
# (Fase 3) precisar dos endpoints nativos de chat/streaming do AgentOS.
_CORS_ORIGINS_ENV = os.environ.get("FATUUS_CORS_ORIGINS")
CORS_ALLOWED_ORIGINS = (
    [orig.strip() for orig in _CORS_ORIGINS_ENV.split(",") if orig.strip()]
    if _CORS_ORIGINS_ENV
    else [
        "https://fatuus-571033381701.southamerica-east1.run.app",
        "https://fatuus-lnpwo6gq7a-rj.a.run.app",
        "http://localhost:8080",
        "http://localhost:8099",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8099",
    ]
)

_db = SqliteDb(db_file="/tmp/fatuus-agentos.db")
_agent_os = AgentOS(
    description="Fatuus — Camada 0 + Camada 1",
    agents=[],
    db=_db,
    base_app=base_app,
    on_route_conflict="preserve_base_app",
    cors_allowed_origins=CORS_ALLOWED_ORIGINS,
)
app = _agent_os.get_app()

# check_dir=False evita que a IMPORTAÇÃO do módulo quebre em ambiente
# sem o frontend buildado (teste/dev). Uma requisição real a "/assets/*"
# sem o diretório ainda derruba com 500 (Starlette valida no primeiro
# request, não só na montagem) — aceitável porque em produção o
# Dockerfile sempre gera frontend/dist/assets antes do container subir.
# O build do Vite (Task 10) usa `assetsDir` padrão e referencia os
# arquivos como `/assets/...` a partir de `index.html`, então montar
# apenas este subpath não colide com nenhuma rota do AgentOS (que não
# reivindica nada sob "/assets").
app.mount(
    "/assets",
    StaticFiles(directory=f"{STATIC_DIR}/assets", check_dir=False),
    name="frontend-assets",
)


if __name__ == "__main__":
    _agent_os.serve(app="fatuus.api:app", port=int(os.environ.get("PORT", 8080)))
