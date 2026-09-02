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

### Testes
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### CLI

```bash
# Analisar um arquivo markdown (gera diagnóstico e métricas)
python3 -m fatuus.cli probe exemplos/exemplo_ia_pt.md --lang pt

# Em inglês
python3 -m fatuus.cli probe exemplos/exemplo_ia_en.md --lang en

# Sanitizar e remover clichês determinísticos
python3 -m fatuus.cli clean exemplos/exemplo_ia_pt.md --lang pt -o texto_limpo.md
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
