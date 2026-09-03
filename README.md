# Fatuus

> Desconstrução de marcas sintéticas, unslop e humanização de texto.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

O **Fatuus** (*do latim fatum / fatuus* — "o que foi proferido", "ilusório") é um kit de código aberto para identificar vícios de linguagem sintética (*slop*), remover marcas d'água estatísticas e recompor o ritmo orgânico (*burstiness*) de textos gerados por inteligência artificial.

## Arquitetura em Três Camadas

1. **Camada 0 — Determinística (Zero-Cost, < 5ms):**
   - Detecção e remoção de caracteres invisíveis: zero-width, controles bidirecionais (override/isolate), word joiner, operadores matemáticos invisíveis e seletores de variação fora de emoji (fingerprints e steganografia).
   - Normalização tipográfica: aspas curvas, reticências, espaços disfarçados (NBSP e família) e separadores de linha Unicode.
   - Sanitização de clichês clássicos de LLM — 36 padrões PT-BR e 35 EN (*"é importante ressaltar"*, *"no cenário atual"*, *"delve into"*, *"paradigm shift"*), com capitalização corrigida em início de sentença.
   - Detecção de padrões estruturais do "Signs of AI writing" (*"not only X but also Y"*, *"não se trata de X, mas Y"*) — sinalizados para a Camada 1, sem substituição cega.
   - Métricas: índice de *Burstiness* (-1 a +1), densidade de travessão e sinais de formatação Markdown (bullets com negrito, emoji em heading).

2. **Camada 1 — Agêntica com Agno:**
   - Agentes de cadência e anti-simetria para quebra de paralelismos rígidos e reescrita semântica, com gate determinístico de aceitação e **retry guiado** — os motivos de rejeição do gate voltam ao prompt dos agentes. Verificada em produção contra o Gemini real (ver [`docs/STATUS.md`](docs/STATUS.md)).
   - Provedores de modelo: **Gemini** (nuvem), **Ollama** e **vLLM** (locais, sem envio de texto a API externa), via `FATUUS_MODEL_PROVIDER`.

3. **Camada 2 — Frontend React:**
   - Painel duplo (editor à esquerda, relatório à direita), com heatmap de termos sintéticos e padrões estruturais, diff unificado e régua de burstiness antes/depois.

## Uso por agentes de IA

O [`SKILL.md`](SKILL.md) empacota o Fatuus como *skill*: um agente aplica a Camada 0 pela CLI e usa o guia de reescrita + gate como checklist para a parte estrutural.

## Instalação e Uso

### Setup

```bash
pip install -e ".[serve,dev]"
cp .env.example .env  # preencher GOOGLE_API_KEY, FATUUS_BASIC_AUTH_USER, FATUUS_BASIC_AUTH_PASSWORD
```

### Frontend (Camada 2)

```bash
cd frontend
npm install
npm run build   # gera frontend/dist/, servido pelo FastAPI em `/`
npm run dev     # opcional: dev server com proxy para localhost:8080
```

### Testes

```bash
pytest
```

### CLI (Camada 0 — determinística, sem chave de API)

```bash
python3 -m fatuus.cli probe exemplos/exemplo_ia_pt.md --lang pt
python3 -m fatuus.cli clean exemplos/exemplo_ia_pt.md --lang pt -o texto_limpo.md
```

### API (Camada 0 + Camada 1 — exige `GOOGLE_API_KEY`)

```bash
set -a; source .env; set +a
uvicorn fatuus.api:app --port 8080
# noutro terminal:
curl -u "$FATUUS_BASIC_AUTH_USER:$FATUUS_BASIC_AUTH_PASSWORD" \
  -X POST localhost:8080/clean \
  -H 'content-type: application/json' \
  -d '{"text": "É importante ressaltar que...", "lang": "pt"}'
```

### Modelos locais (Ollama / vLLM)

A Camada 1 roda 100% local, sem envio de texto a API externa:

```bash
# Ollama
FATUUS_MODEL_PROVIDER=ollama FATUUS_MODEL_ID=llama3.1 uvicorn fatuus.api:app --port 8080

# vLLM (API OpenAI-compatible)
FATUUS_MODEL_PROVIDER=vllm FATUUS_MODEL_ID=<modelo-servido> VLLM_API_KEY=local uvicorn fatuus.api:app --port 8080
```

### Como Biblioteca Python

```python
from fatuus import FatuusDetector, FatuusSanitizer

detector = FatuusDetector(lang="pt")
resultado = detector.analyze("É importante ressaltar que no cenário atual...")

print(f"Score Sintético: {resultado['synthetic_score']}%")
print(f"Burstiness: {resultado['sentence_metrics']['burstiness']}")

sanitizer = FatuusSanitizer(lang="pt")
limpo = sanitizer.clean("É importante ressaltar que...")
print(limpo["cleaned_text"])
```

## Contribuição

Contribuições exigem aceite do [CLA](CLA.md) — a verificação é automática no primeiro pull request. Sem o aceite, a contribuição não pode ser integrada.

## Licença

Distribuído sob a licença [Apache-2.0](LICENSE).
