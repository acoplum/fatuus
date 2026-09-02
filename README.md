# Fatuus

> Desconstrução de marcas sintéticas, unslop e humanização de texto.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

O **Fatuus** (*do latim fatum / fatuus* — "o que foi proferido", "ilusório") é um kit de código aberto para identificar vícios de linguagem sintética (*slop*), remover marcas d'água estatísticas e recompor o ritmo orgânico (*burstiness*) de textos gerados por inteligência artificial.

## Arquitetura em Duas Camadas

1. **Camada 0 — Determinística (Zero-Cost, < 5ms):**
   - Detecção e remoção de caracteres invisíveis / zero-width (fingerprints).
   - Sanitização de clichês clássicos de LLM (*"é importante ressaltar"*, *"no cenário atual"*, *"mergulhar em"*, *"delve into"*, *"testament to"*).
   - Cálculo do índice estatístico de *Burstiness* (-1 a +1) sobre a variação do comprimento de sentenças.

2. **Camada 1 — Agêntica com Agno (Em desenvolvimento):**
   - Agentes de cadência e anti-simetria para quebra de paralelismos rígidos e reescrita semântica.

## Instalação e Uso

### Setup

```bash
pip install -e ".[serve,dev]"
cp .env.example .env  # preencher GOOGLE_API_KEY, FATUUS_BASIC_AUTH_USER, FATUUS_BASIC_AUTH_PASSWORD
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

## Licença

Distribuído sob a licença [Apache-2.0](LICENSE).
