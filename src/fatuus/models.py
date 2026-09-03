"""Fábrica do modelo LLM usado pela Camada 1.

Provedores suportados, escolhidos por `FATUUS_MODEL_PROVIDER`:

- `gemini` (padrão) — nuvem, exige `GOOGLE_API_KEY`.
- `ollama` — local, sem envio de texto a API externa. Host em
  `FATUUS_OLLAMA_HOST` (padrão `http://localhost:11434`).
- `vllm` — local via API OpenAI-compatible do vLLM. URL em `VLLM_BASE_URL`
  (padrão do agno: `http://localhost:8000/v1/`) e chave em `VLLM_API_KEY`
  (qualquer valor, o vLLM local não valida).

`FATUUS_MODEL_ID` define o modelo; sem ele, cada provedor usa seu padrão.
`FATUUS_GEMINI_MODEL` segue aceito por compatibilidade com deploys antigos.
"""

import os
from typing import Any

DEFAULT_GEMINI_MODEL = "gemini-3.7-flash"
DEFAULT_OLLAMA_MODEL = "llama3.1"


def build_model() -> Any:
    provider = os.environ.get("FATUUS_MODEL_PROVIDER", "gemini").lower()
    model_id = os.environ.get("FATUUS_MODEL_ID")

    if provider == "gemini":
        from agno.models.google import Gemini

        return Gemini(
            id=model_id
            or os.environ.get("FATUUS_GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        )

    if provider == "ollama":
        from agno.models.ollama import Ollama

        host = os.environ.get("FATUUS_OLLAMA_HOST", "http://localhost:11434")
        return Ollama(id=model_id or DEFAULT_OLLAMA_MODEL, host=host)

    if provider == "vllm":
        if not model_id:
            raise ValueError(
                "FATUUS_MODEL_PROVIDER=vllm exige FATUUS_MODEL_ID com o nome "
                "do modelo servido"
            )
        from agno.models.vllm import VLLM

        return VLLM(id=model_id)

    raise ValueError(
        f"FATUUS_MODEL_PROVIDER desconhecido: {provider!r} "
        "(suportados: gemini, ollama, vllm)"
    )
