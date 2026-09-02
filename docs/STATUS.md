# Status — fatuus

**Atualizado:** 2026-09-02 · **Estágio:** em construção

## O que é

Kit open source que detecta vícios de linguagem sintética (*slop*) e caracteres de fingerprint invisíveis em texto gerado por IA, e recompõe o ritmo (*burstiness*) do texto — de forma determinística hoje, e agêntica na Camada 1 (em construção). Serve times de conteúdo e devs que geram texto com LLM e não querem publicar com marcas óbvias de IA.

## O que já funciona

- **Camada 0 (determinística):** normalizador de caracteres invisíveis (ZWSP, ZWNJ, ZWJ, BOM, marcadores de direção), métrica de *burstiness* (-1 a +1) sobre distribuição de comprimento de sentenças, dicionários de clichês sintéticos PT-BR/EN, sanitizador determinístico.
- **CLI (`fatuus probe` / `fatuus clean`):** inspeção com diagnóstico visual de score sintético e exportação JSON.
- **Camada 1 (motor agêntico Agno):** pipeline com agentes de cadência, anti-simetria e integridade semântica orquestrados via `AgentOS`, expostos em FastAPI com `SqliteDb`. Agente de watermark estatístico com ativação condicional. Gate determinístico de aceitação com retry. **Verificada em produção em 2026-09-02** contra o Gemini real (`gemini-3.7-flash`) — ver evidência abaixo.
  - **Limitações conhecidas:**
    - Gate de fidelidade v1 usa proxy de variação de tamanho de texto em lugar de similaridade semântica real — não há embeddings nesta versão. A razão é medida contra o texto pré-sanitização, faixa `[0.3x, 1.4x]` (FAT-9, recalibrada em 2026-09-02 a partir do caso real de produção: uma fusão de 3 frases clichê repetidas em 1 frase natural media 0,33-0,38x e era rejeitada pelo piso antigo de 0,7x — compressão legítima de clichê, não perda de conteúdo). Segue sendo um proxy grosseiro, não similaridade semântica de verdade.
    - O retry é reamostragem, não retry guiado: cada tentativa recebe o mesmo texto de entrada, e os motivos de rejeição do gate não chegam a nenhum agente.
    - `agno[os]` traz `uvicorn` sem extras de performance (`uvicorn[standard]`) — aceitável para este teste, revisar se performance importar depois.
- **Camada 2 (frontend React):** painel duplo — editor à esquerda, relatório à direita — servido como build estático pelo mesmo FastAPI app do `AgentOS`, em `/`. Heatmap de termos sintéticos (destaque inline + lista resumo), régua de burstiness com dois marcadores (antes/depois), diff unificado (`jsdiff`) e indicador de quantas tentativas o gate levou. Validação de limite de 20 000 caracteres no cliente. 3 chamadas síncronas por análise (`/probe` + `/clean`), sem streaming SSE — decisão revista no design da Camada 2 (ver [`docs/features/camada-2-frontend`](features/camada-2-frontend/)): o spinner simples não precisa de progresso incremental.
  - **Limitações conhecidas:** sem streaming (spinner simples até a resposta final), sem histórico de análises anteriores, sem multiusuário (Basic Auth global, uma credencial por instância self-hosted).
  - **Migração do middleware de auth:** Basic Auth saiu de um `Depends` do FastAPI — que nunca cobria o `Mount` do Starlette usado para servir o frontend, nem rotas WebSocket — para um middleware ASGI puro (`BasicAuthMiddleware`, em `src/fatuus/auth.py`), cobrindo HTTP e WebSocket por igual. Isso fechou de passagem o gap de `/docs`, `/openapi.json` e `/redoc` sem autenticação, documentado antes nesta página como residual aceito. A revisão de segurança da migração também achou e corrigiu uma regressão real: credencial não-ASCII no header `Authorization` derrubava `secrets.compare_digest` com `TypeError` não tratado, virando 500 em vez de 401 limpo — corrigido comparando bytes UTF-8.
  - **Conflito de rota com o `AgentOS`:** `AgentOS.get_app()` reivindica `GET /` por padrão para sua própria rota JSON de metadados, o que sombrearia o `index.html` do frontend. Resolvido com o parâmetro documentado `on_route_conflict="preserve_base_app"` do construtor do `AgentOS` (mecanismo suportado, não workaround), com teste de regressão (`TestFrontendRootRoute`) guardando contra uma versão futura do `agno` reverter o comportamento.
  - **Verificação:** 56 testes de backend passando (`pytest`), 31 testes de frontend passando (`npm test`, dentro de `frontend/`), build Docker multi-stage (estágio Node + runtime Python) verificado localmente com build real e smoke test do container — 401 sem credencial em `/`, `/assets/*` e `/probe`, 200 com credencial e resposta real (HTML, asset, JSON). **Ainda não implantado no Cloud Run** — existe como código commitado no submódulo, verificado localmente.
- 56 testes de backend, 100% passando (`pytest`; `python3 -m unittest discover` conta menos — contagem de subtestes difere entre os dois runners).

## Evidência da verificação em produção (2026-09-02)

Redeploy pós-fix de segurança, revisão `fatuus-00001-5z6`. Confirmado por request real, com autenticação:

- Rotas antes abertas (`/memories`, `/config`, `/health`) agora exigem Basic Auth — 401 sem credencial, 200 com.
- `POST /clean` com texto que aciona a Camada 1 (3 frases com clichê repetido): `layer1_attempts: 3` (rodou as 3 tentativas de verdade, chamando o Gemini) e `layer1_accepted: false` — o gate rejeitou por variação de tamanho (0,38x), e o `cleaned_text` devolvido foi o da Camada 0, exatamente como a invariante "nunca pior que a Camada 0" promete.

**Após o fix da FAT-9** (revisão `fatuus-00003-9sm`), o mesmo texto de entrada foi reenviado: `layer1_accepted: true`, `layer1_attempts: 1`, `cleaned_text: "O sistema funciona bem. Além de rápido, oferece segurança."` — aceito de primeira, sem clichê, sem repetição. Confirma que a Camada 1 não só executa contra o Gemini real, mas também aceita uma reescrita típica depois da recalibração do piso.

## O que não funciona ainda

- **Suporte a idiomas além de PT-BR/EN:** fora de escopo nesta fase — cada idioma exige dicionário de marcadores próprio, não há heurística universal.
- **Empacotamento PyPI:** planejado, não feito.

## Como rodar agora

```bash
python3 -m unittest discover -s tests -p "test_*.py"

python3 -m fatuus.cli probe exemplos/exemplo_ia_pt.md --lang pt
python3 -m fatuus.cli clean exemplos/exemplo_ia_pt.md --lang pt -o texto_limpo.md
```

## Onde está publicado

- **Repositório:** GitHub público (`acoplum/fatuus`).
- **Camada 1 (teste):** Cloud Run, projeto `acoplum`, região `southamerica-east1`, revisão `fatuus-00003-9sm`, URL `https://fatuus-571033381701.southamerica-east1.run.app` — deploy de 2026-09-02, pós-fix de segurança e da FAT-9 (a primeira revisão, `fatuus-00001-pzh`, foi apagada no mesmo dia como contenção: as mais de 100 rotas do `AgentOS` estavam sem autenticação num serviço público). Acesso via Basic Auth em todas as rotas.
- **Pacote PyPI:** não publicado ainda.
