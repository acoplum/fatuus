# Camada 2 — Frontend Interativo (React)

## Objetivo

Dar visibilidade em tempo real do que a Camada 0/1 faz com o texto — onde estão os clichês, como a cadência mudou, o que o pipeline aceitou ou rejeitou — para quem revisa conteúdo antes de publicar.

## Detalhes

Consome o mesmo app FastAPI do `AgentOS` (ver [camada-1-agno](../camada-1-agno/)): chamada síncrona para `/probe` e `/clean` (equivalente à CLI), e streaming SSE — nativo do `AgentOS` — para acompanhar o pipeline agente-a-agente conforme ele roda, sem protocolo próprio.

Telas: editor de entrada, heatmap de termos sintéticos, gráfico de burstiness antes/depois, comparador de diff lado a lado, e indicador de quantas tentativas o gate levou para aceitar (ou se caiu no fallback de devolver o texto original).

**Fora de escopo nesta fase:** autenticação/multiusuário — o self-hosted assume uma pessoa por instância local.

## Métricas

- Tempo até o usuário ver o primeiro resultado do pipeline na tela — não instrumentado ainda.
- Depende da Camada 1 estar implementada para ter dado real a medir.
