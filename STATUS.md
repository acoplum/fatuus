# STATUS · fatuus

Última atualização: 2026-09-02

## Onde estamos

Motor determinístico inicial (Camada 0) implementado em Python puro (stdlib), com detecção de caracteres zero-width, cálculo estatístico de *burstiness* (-1 a +1), dicionários de clichês sintéticos (PT-BR e EN) e sanitizador. CLI exploratória funcional e suíte de testes unitários passando.

## Componentes

| Componente | Estado | Detalhe |
|---|---|---|
| **Camada 0 (Determinística)** | 🟢 Operacional | Detector de watermarks/zero-width, métrica de burstiness, deslop determinístico |
| **CLI (`fatuus probe` / `clean`)** | 🟢 Operacional | Inspeção com diagnóstico visual e exportação JSON |
| **Camada 1 (Agno Engine)** | 🟡 Especificado | Workflows agênticos para des-simetrização e reescritura contextual |
| **Frontend React** | ⚪ Planejado | Interface interativa com heatmap de slop e diff antes/depois |
| **Packaging PyPI** | ⚪ Planejado | Distribuição via `pyproject.toml` |

## Testes

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
7 testes passando (100% verde).
