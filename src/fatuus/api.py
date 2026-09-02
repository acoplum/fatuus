"""App FastAPI/AgentOS da Camada 0 + Camada 1 do Fatuus."""

import os

from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.os import AgentOS
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from .auth import require_basic_auth
from .detector import FatuusDetector
from .pipeline import HumanizationPipeline
from .sanitizer import FatuusSanitizer

MODEL_ID = os.environ.get("FATUUS_GEMINI_MODEL", "gemini-3.7-flash")


class TextRequest(BaseModel):
    text: str
    lang: str = "pt"


# A dependência de auth fica no app inteiro, não rota a rota: o
# `AgentOS.get_app()` monta mais de 100 rotas próprias (memories, sessions,
# migrations de schema) neste mesmo `base_app`, e o auth nativo do Agno é
# no-op enquanto `OS_SECURITY_KEY` não estiver definida. Rotas incluídas
# depois herdam `app.router.dependencies`, então declarar aqui cobre tudo
# que o AgentOS montar. `tests/test_api.py` guarda isso por inventário de rotas.
base_app = FastAPI(
    title="Fatuus API",
    version="0.1.0",
    dependencies=[Depends(require_basic_auth)],
)


@base_app.post("/probe")
def probe(payload: TextRequest) -> dict:
    detector = FatuusDetector(lang=payload.lang)
    return detector.analyze(payload.text)


@base_app.post("/clean")
def clean(payload: TextRequest) -> dict:
    sanitizer = FatuusSanitizer(lang=payload.lang)
    sanitized = sanitizer.clean(payload.text)

    pipeline = HumanizationPipeline(Gemini(id=MODEL_ID), lang=payload.lang)
    result = pipeline.run(sanitized["cleaned_text"])

    return {
        "cleaned_text": result.final_text,
        "layer0": sanitized,
        "layer1_accepted": result.accepted,
        "layer1_attempts": result.attempts,
        "gate_reasons": result.gate.reasons,
    }


# Nenhum agente é registrado diretamente no AgentOS: a Camada 1 constrói os
# 4 agentes por requisição (pipeline.py), porque o texto e o idioma variam
# a cada chamada. Registrar agentes fixos aqui fica para quando o frontend
# (Fase 3) precisar dos endpoints nativos de chat/streaming do AgentOS.
_db = SqliteDb(db_file="/tmp/fatuus-agentos.db")
_agent_os = AgentOS(
    description="Fatuus — Camada 0 + Camada 1", agents=[], db=_db, base_app=base_app
)
app = _agent_os.get_app()


if __name__ == "__main__":
    _agent_os.serve(app="fatuus.api:app", port=int(os.environ.get("PORT", 8080)))
