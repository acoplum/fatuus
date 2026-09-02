# ROADMAP · fatuus

## Fase 1 — Motor Determinístico & CLI

- [x] **1. Normalizador de Caracteres Invisíveis** — ✅ feito em 2026-09-02
  - Remoção de Zero-Width Space (ZWSP), ZWNJ, ZWJ, BOM e marcadores de direção de texto.
- [x] **2. Métrica Estatística de Burstiness** — ✅ feito em 2026-09-02
  - Cálculo de média, desvio padrão e índice de burstiness (-1 a +1) baseado na distribuição do comprimento de sentenças.
- [x] **3. Dicionários de Slop & Sanitizador** — ✅ feito em 2026-09-02
  - Dicionários de termos sintéticos em PT-BR e EN com substituição e des-clichêização determinística.
- [x] **4. CLI Standalone (`fatuus probe` / `clean`)** — ✅ feito em 2026-09-02
  - Inspeção visual com diagnóstico de probabilidade sintética e exportação JSON.

---

## Fase 2 — Motor Agêntico com Agno (Atual)

Detalhe completo em [`features/camada-1-agno`](features/camada-1-agno/). Gate: pipeline aceita ou recusa um texto de teste conhecido (com clichê + baixa burstiness) sem regressão nos 7 testes da Fase 1.

- [x] **5. Workflow Agno com agentes de papel único** — ✅ feito em 2026-09-02
  - Agente de Cadência → Agente Anti-Simetria → Agente de Integridade Semântica, orquestrados via `AgentOS`, expostos em FastAPI com `SqliteDb` por padrão no self-hosted.
- [x] **6. Agente de Watermark Estatístico** — ✅ feito em 2026-09-02
  - Ativa condicionalmente quando a Camada 0 sinaliza indício de watermark de token-sampling. Depende de LLM (local ou cloud) — não é zero-cost, ao contrário da Camada 0.
- [x] **7. Gate determinístico de aceitação** — ✅ feito em 2026-09-02
  - Reroda `FatuusDetector` sobre o output do pipeline. Rejeita clichê reintroduzido, caractere invisível reintroduzido, burstiness que não melhorou, ou variação de tamanho fora da faixa — a variação de tamanho é o proxy desta versão para fidelidade semântica, não há embeddings. Retry por **reamostragem** até N tentativas (`Loop` do Agno com `forward_iteration_output=False`): cada tentativa reexecuta os mesmos agentes sobre o mesmo texto de entrada e a variação vem só da amostragem do modelo — os motivos de rejeição do gate não chegam a nenhum agente. Esgotadas as tentativas, devolve o texto da Camada 0.
  - **Retry guiado por feedback do gate fica para depois** — é o que transformaria a reamostragem em correção dirigida.
- [ ] **8. Suporte a Modelos Locais (Ollama / vLLM)**
  - Execução 100% offline sem envio de texto a APIs externas.

**Fora de escopo nesta fase:** suporte a idiomas além de PT-BR/EN.

---

## Fase 3 — Interface Web React

Detalhe completo em [`features/camada-2-frontend`](features/camada-2-frontend/).

- [ ] **9. Frontend Interativo**
  - Editor com heatmap em tempo real de termos sintéticos, gráfico de burstiness, comparador de diff antes/depois e streaming SSE do pipeline agente-a-agente — consumindo o mesmo FastAPI app do `AgentOS` (passo 5).
