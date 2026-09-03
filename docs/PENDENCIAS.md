# PENDÊNCIAS · fatuus

| # | Pendência | Status | Passo |
|---|---|---|---|
| FAT-1 | Implementar workflow Agno (agentes de cadência, anti-simetria e integridade semântica) via `AgentOS` com `SqliteDb` | feita | 5 |
| FAT-2 | Implementar agente de watermark estatístico (token-sampling), ativação condicional | feita | 6 |
| FAT-3 | Implementar gate determinístico de aceitação (rerun Camada 0 + fallback ao texto original) | feita | 7 |
| FAT-4 | Implementar suporte a Ollama/vLLM local via Agno | feita | 8 |
| FAT-5 | Criar UI interativa em React com heatmap de slop, régua de burstiness e diff unificado (textarea simples, sem Monaco; sem streaming SSE — decisão revista no design da Camada 2) | feita | 9 |
| FAT-6 | Configurar GitHub Actions (CI) com lint, mypy e pytest | aberta | 14 |
| FAT-7 | Verificar a Camada 1 em produção: redeploy pós-fix de auth e smoke test com entrada que comprovadamente entre na Camada 1, guardando o JSON bruto (`layer1_attempts` ≠ 0) | feita | 7 |
| FAT-8 | Retry guiado: levar os motivos de rejeição do gate de volta aos agentes, hoje o retry é só reamostragem | feita | 7 |
| FAT-9 | Recalibrar a faixa de variação de tamanho do gate: hoje rejeita reescritas compactas/fiéis (confirmado em produção, 0,38x o original), só aceita reescritas que crescem | feita | 7 |
| FAT-10 | Bloqueia o próximo deploy no Cloud Run: CORS do `AgentOS` (`allow_credentials=True`, allowlist incluindo `agno.com`/`localhost:3000`) permite leitura cross-origin autenticada. Fix: `AgentOS(..., cors_allowed_origins=[...])`, substituindo allowlist default e travando com teste de regressão. | feita | 9 |
| FAT-11 | Publicar `fatuus` 0.1.0 no PyPI — `python -m build` e `twine check` já validados; falta credencial PyPI do titular | aberta | 13 |
| FAT-12 | Definir `FATUUS_CORS_ORIGINS` com as URLs do Cloud Run no próximo deploy — as URLs de produção saíram do código (repo público não carrega infra); sem a env o CORS cobre só localhost | feita | — |
| FAT-13 | Rotacionar a credencial Basic Auth de produção — a atual circulou em texto plano em sessões de assistentes de IA | aberta | — |
