# ROADMAP · fatuus

## Fase 1 — Motor Determinístico & CLI (Atual)

- [x] **1. Normalizador de Caracteres Invisíveis** — ✅ feito em 2026-09-02
  - Remoção de Zero-Width Space (ZWSP), ZWNJ, ZWJ, BOM e marcadores de direção de texto.
- [x] **2. Métrica Estatística de Burstiness** — ✅ feito em 2026-09-02
  - Cálculo de média, desvio padrão e índice de burstiness (-1 a +1) baseado na distribuição do comprimento de sentenças.
- [x] **3. Dicionários de Slop & Sanitizador** — ✅ feito em 2026-09-02
  - Dicionários de termos sintéticos em PT-BR e EN com substituição e des-clichêização determinística.
- [x] **4. CLI Standalone (`fatuus probe` / `clean`)** — ✅ feito em 2026-09-02
  - Inspeção visual com diagnóstico de probabilidade sintética e exportação JSON.

---

## Fase 2 — Motor Agêntico com Agno

- [ ] **5. Integração com Agno Agents Framework**
  - Workflows de revisão sintática e variação de ritmo usando agentes especializados.
- [ ] **6. Agente Anti-Simetria e Quebra de Paralelismo**
  - Reorganização de períodos monótonos e listas excessivamente simétricas.
- [ ] **7. Suporte a Modelos Locais (Ollama / vLLM)**
  - Execução 100% offline sem envio de texto a APIs externas.

---

## Fase 3 — Interface Web React

- [ ] **8. Frontend Interativo**
  - Editor com heatmap em tempo real de termos sintéticos, gráfico de burstiness e visualizador de diff antes/depois.
