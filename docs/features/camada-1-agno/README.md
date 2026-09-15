# Camada 1 — Motor Agêntico (Agno)

**Estágio:** pronta — validada em produção; o pacote ainda tem a pendência de publicação no PyPI (FAT-11)

## Objetivo

Reescrever o texto que a Camada 0 sinalizou como sinteticamente marcado, recompondo ritmo e quebrando simetria, sem alterar fatos nem reintroduzir clichês.

## Detalhes

Workflow Agno com quatro agentes de papel único, executados em sequência:

1. **Agente de Cadência** — reorganiza períodos monotônicos, intercalando sentenças curtas com construções subordinadas.
2. **Agente Anti-Simetria** — quebra paralelismos rígidos e listas excessivamente simétricas.
3. **Agente de Integridade Semântica** — verifica que entidades, números e fatos do texto original foram preservados.
4. **Agente de Watermark Estatístico** — ativa só quando a Camada 0 sinaliza indício de watermark de token-sampling; depende de um LLM (local via Ollama/vLLM, ou cloud) — ao contrário da Camada 0, não é zero-cost.

Depois do pipeline, um **gate determinístico** — não é um agente — reexecuta `FatuusDetector`/`FatuusSanitizer` (Camada 0) sobre o output. Rejeita se: reintroduziu termo do dicionário de clichês, a burstiness não melhorou em relação à entrada, ou a variação de tamanho sair da faixa usada como proxy de fidelidade semântica nesta versão. Não há embeddings nesta versão. Se rejeitado, tenta de novo com o motivo da rejeição injetado no prompt, até N tentativas; esgotadas, devolve o texto original inalterado com um aviso — o pipeline nunca entrega um texto pior que a entrada. Isso é o que fecha o risco de "meta-slop" descrito em [`7-fatuus.md`](../../../../../frentes/1-opensource/projetos/7-fatuus.md).

Exposto via `AgentOS` do Agno: mesmo app FastAPI consumido pela Camada 2, com `SqliteDb` por padrão no self-hosted (sem infra externa a instalar — Postgres fica reservado para o `ee/`) e rotas customizadas equivalentes à CLI (`/probe`, `/clean`). Suporte a modelos locais (Ollama/vLLM) e cloud (Gemini, OpenAI, Anthropic) via os providers nativos do Agno.

**Fora de escopo nesta fase:** idiomas além de PT-BR/EN — confirmado pelos benchmarks `humanizer-ja`/`humanizer-ru` (ver [`7-fatuus.md`](../../../../../frentes/1-opensource/projetos/7-fatuus.md)), que não compartilham heurística entre idiomas; cada um exigiria dicionário de marcadores próprio.

## Métricas

- Taxa de aceitação do gate na primeira tentativa — há smoke de produção, mas não há série contínua instrumentada.
- Número médio de tentativas até aceitar ou cair no fallback — não instrumentado ainda.
- Latência do pipeline completo por texto — não instrumentado ainda (a Camada 0 sozinha já mede < 5ms).
