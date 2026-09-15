# Camada 2 — Frontend Interativo (React)

**Estágio:** pronta — build, testes e deploy no Cloud Run validados; métricas de uso ainda não instrumentadas

## Objetivo

Dar visibilidade em tempo real do que a Camada 0/1 faz com o texto — onde estão os clichês, como a cadência mudou, o que o pipeline aceitou ou rejeitou — para quem revisa conteúdo antes de publicar.

## Detalhes

Consome o mesmo app FastAPI do `AgentOS` (ver [camada-1-agno](../camada-1-agno/)): 3 chamadas síncronas por análise para `/probe` e `/clean` (equivalente à CLI). **Sem streaming SSE** — decisão revista em relação ao plano original desta página: o design da Camada 2 concluiu que o spinner simples até a resposta final não precisa de progresso incremental do pipeline agente-a-agente. Detalhe da decisão em [`docs/superpowers/specs/2026-09-02-camada2-frontend-design.md`](../../../../../../docs/superpowers/specs/2026-09-02-camada2-frontend-design.md) (spec no repo HQ).

Telas: editor de entrada, heatmap de termos sintéticos (destaque inline + lista resumo), régua de burstiness antes/depois (dois marcadores), diff unificado, e indicador de quantas tentativas o gate levou para aceitar (ou se caiu no fallback de devolver o texto original).

**Fora de escopo nesta fase:** autenticação/multiusuário — o self-hosted assume uma pessoa por instância local.

## Métricas

- Tempo até o usuário ver o primeiro resultado do pipeline na tela — não instrumentado ainda.
- A Camada 1 já está implementada e validada; falta instrumentar o tempo até o primeiro resultado em uso real.
