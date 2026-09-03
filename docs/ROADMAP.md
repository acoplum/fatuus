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
  - Reroda `FatuusDetector` sobre o output do pipeline. Rejeita clichê reintroduzido, caractere invisível reintroduzido, padrão estrutural que aumentou, burstiness que não melhorou (quando era negativa) ou piorou além da tolerância (quando já era saudável — ver FAT-A3), ou variação de tamanho fora da faixa — a variação de tamanho é o proxy desta versão para fidelidade semântica, não há embeddings. Esgotadas as tentativas, devolve o texto da Camada 0.
  - **Retry guiado** — ✅ feito em 2026-09-02 (FAT-8): a partir da 2ª tentativa, os motivos de rejeição do gate são anexados ao prompt dos agentes de reescrita, transformando a reamostragem em correção dirigida. O agente de integridade semântica não recebe o feedback — o papel dele é comparar original e reescrita.
- [x] **8. Suporte a Modelos Locais (Ollama / vLLM)** — ✅ feito em 2026-09-02
  - Fábrica de modelo em `src/fatuus/models.py`, selecionada por `FATUUS_MODEL_PROVIDER` (`gemini` | `ollama` | `vllm`). Ollama e vLLM rodam 100% local, sem envio de texto a API externa. Verificado por teste unitário; smoke test contra um Ollama real fica para quando houver host disponível.

**Fora de escopo nesta fase:** suporte a idiomas além de PT-BR/EN.

---

## Fase 3 — Interface Web React

Detalhe completo em [`features/camada-2-frontend`](features/camada-2-frontend/).

- [x] **9. Frontend Interativo** — ✅ feito em 2026-09-02
  - Editor com heatmap de termos sintéticos (destaque inline + lista resumo), régua de burstiness antes/depois, diff unificado e indicador de tentativas do gate — consumindo `/probe` e `/clean` do mesmo FastAPI app do `AgentOS` (passo 5), 3 chamadas síncronas por análise, sem streaming SSE (decisão revista no design da Camada 2: o spinner simples da v1 não precisa de progresso incremental). Em 2026-09-02, o heatmap passou a destacar também os padrões estruturais (cor própria + resumo separado).

---

## Fase 4 — Distribuição & Hardening

- [x] **10. Expansão da Camada 0** — ✅ feito em 2026-09-02
  - Caracteres invisíveis: controles bidi (LRE/RLE/PDF/LRO/RLO, isolates), word joiner, operadores matemáticos invisíveis e seletores de variação fora de emoji (referência: `watermarks-remover`). Normalização tipográfica (aspas curvas, reticências, espaços disfarçados). Padrões estruturais do "Signs of AI writing" (negação contrastiva, "not only X but also Y", "whether you're X or Y") como detecção separada — reescrevê-los é papel da Camada 1. Métricas de travessão e formatação Markdown (bullets com negrito, emoji em heading) no score. Assimetria detector↔sanitizer fechada: todo clichê detectado tem substituição, com teste de invariante.
- [x] **11. Skill para agentes** — ✅ feito em 2026-09-02
  - [`SKILL.md`](../SKILL.md) na raiz, no formato das referências (`blader/humanizer`): Camada 0 via CLI + guia de reescrita estrutural + gate como checklist de autoverificação. Em inglês, que é o canal de distribuição das referências que mais renderam adoção.
- [x] **12. CLA ativo** — ✅ feito em 2026-09-02
  - [`CLA.md`](../CLA.md) + verificação automática em `.github/workflows/cla.yml` (mecanismo do `spec-registro-decisao`). Ativa no primeiro push.
- [ ] **13. Publicar no PyPI** (FAT-11)
  - Gate: `pip install fatuus` instala a 0.1.0 e `fatuus probe` roda. Build e `twine check` já validados.
- [ ] **14. CI com GitHub Actions** (FAT-6)
  - Gate: pytest + testes do frontend rodando em PR.
