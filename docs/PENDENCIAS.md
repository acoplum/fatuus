# PENDÊNCIAS · fatuus

| # | Pendência | Status | Passo |
|---|---|---|---|
| FAT-1 | Implementar workflow Agno (agentes de cadência, anti-simetria e integridade semântica) via `AgentOS` com `SqliteDb` | feita | 5 |
| FAT-2 | Implementar agente de watermark estatístico (token-sampling), ativação condicional | feita | 6 |
| FAT-3 | Implementar gate determinístico de aceitação (rerun Camada 0 + fallback ao texto original) | feita | 7 |
| FAT-4 | Implementar suporte a Ollama/vLLM local via Agno | aberta | 8 |
| FAT-5 | Criar UI interativa em React com Monaco/ProseMirror, heatmap de slop e streaming SSE do pipeline | aberta | 9 |
| FAT-6 | Configurar GitHub Actions (CI) com lint, mypy e pytest | aberta | — |
| FAT-7 | Verificar a Camada 1 em produção: redeploy pós-fix de auth e smoke test com entrada que comprovadamente entre na Camada 1, guardando o JSON bruto (`layer1_attempts` ≠ 0) | feita | 7 |
| FAT-8 | Retry guiado: levar os motivos de rejeição do gate de volta aos agentes, hoje o retry é só reamostragem | aberta | 7 |
| FAT-9 | Recalibrar a faixa de variação de tamanho do gate: hoje rejeita reescritas compactas/fiéis (confirmado em produção, 0,38x o original), só aceita reescritas que crescem | feita | 7 |
