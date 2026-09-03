# Status — fatuus

**Atualizado:** 2026-09-03 · **Estágio:** em construção

## O que é

Kit open source que detecta vícios de linguagem sintética (*slop*) e caracteres de fingerprint invisíveis em texto gerado por IA, e recompõe o ritmo (*burstiness*) do texto — de forma determinística hoje, e agêntica na Camada 1 (em construção). Serve times de conteúdo e devs que geram texto com LLM e não querem publicar com marcas óbvias de IA.

## O que já funciona

- **Camada 0 (determinística):** normalizador de caracteres invisíveis (ZWSP, ZWNJ, ZWJ, BOM, soft hyphen, word joiner, controles bidi LRE/RLE/PDF/LRO/RLO e isolates, operadores matemáticos invisíveis, seletores de variação fora de emoji), normalização tipográfica (aspas curvas, reticências, espaços disfarçados, separadores de linha Unicode), métrica de *burstiness* (-1 a +1), métricas de travessão e formatação Markdown (bullets com negrito, emoji em heading), dicionários de clichês sintéticos PT-BR/EN (36 padrões PT, 35 EN), padrões estruturais do "Signs of AI writing" detectados separadamente, sanitizador determinístico com fix de capitalização em início de sentença. **Assimetria detector↔sanitizer fechada:** todo clichê detectado tem substituição, garantido por teste de invariante.
- **CLI (`fatuus probe` / `fatuus clean`):** inspeção com diagnóstico visual de score sintético e exportação JSON.
- **Skill para agentes:** [`SKILL.md`](../SKILL.md) na raiz, formato das referências (`blader/humanizer`) — Camada 0 via CLI + guia de reescrita + gate como checklist.
- **CLA:** [`CLA.md`](../CLA.md) + verificação automática (`.github/workflows/cla.yml`, mecanismo do `spec-registro-decisao`). Ativa no primeiro push.
- **Camada 1 (motor agêntico Agno):** pipeline com agentes de cadência, anti-simetria e integridade semântica, expostos em FastAPI com `SqliteDb`. Agente de watermark estatístico com ativação condicional. Gate determinístico de aceitação com **retry guiado** (FAT-8): a partir da 2ª tentativa os motivos de rejeição do gate são anexados ao prompt dos agentes de reescrita. Provedores de modelo: `gemini` (nuvem), `ollama` e `vllm` (locais, sem envio de texto a API externa), via `FATUUS_MODEL_PROVIDER`. **Verificada em produção em 2026-09-02** contra o Gemini real (`gemini-3.7-flash`) — ver evidência abaixo (anterior à expansão da Camada 0 e ao retry guiado).
  - **Limitações conhecidas:**
    - Gate de fidelidade v1 usa proxy de variação de tamanho de texto em lugar de similaridade semântica real — não há embeddings nesta versão. A razão é medida contra o texto pré-sanitização, faixa `[0.3x, 1.4x]` (FAT-9, recalibrada em 2026-09-02 a partir do caso real de produção: uma fusão de 3 frases clichê repetidas em 1 frase natural media 0,33-0,38x e era rejeitada pelo piso antigo de 0,7x — compressão legítima de clichê, não perda de conteúdo). Segue sendo um proxy grosseiro, não similaridade semântica de verdade.
    - Ollama/vLLM verificados por teste unitário; falta smoke test contra um servidor local real.
    - `agno[os]` traz `uvicorn` sem extras de performance (`uvicorn[standard]`) — aceitável para este teste, revisar se performance importar depois.
- **Camada 2 (frontend React):** painel duplo com cards modulares, visualizador de texto com abas (`Diff`, `Texto Limpo`, `Lado a Lado`, `Original`), botão de cópia com feedback, heatmap com pills de contagem — incluindo padrões estruturais com cor própria — e card explicativo do pipeline. Servido como build estático pelo mesmo FastAPI app do `AgentOS`, em `/`. Validação de limite de 20 000 caracteres no cliente. Testado e **implantado com sucesso no Cloud Run** (revisão `fatuus-00005-g6j`, com expansão da Camada 0, retry guiado e CORS configurado).
  - **Limitações conhecidas:** sem streaming (spinner simples até a resposta final), sem histórico de análises anteriores, sem multiusuário (Basic Auth global, uma credencial por instância self-hosted).
  - **Migração do middleware de auth:** Basic Auth saiu de um `Depends` do FastAPI — que nunca cobria o `Mount` do Starlette usado para servir o frontend, nem rotas WebSocket — para um middleware ASGI puro (`BasicAuthMiddleware`, em `src/fatuus/auth.py`), cobrindo HTTP e WebSocket por igual. Isso fechou de passagem o gap de `/docs`, `/openapi.json` e `/redoc` sem autenticação, documentado antes nesta página como residual aceito. A revisão de segurança da migração também achou e corrigiu uma regressão real: credencial não-ASCII no header `Authorization` derrubava `secrets.compare_digest` com `TypeError` não tratado, virando 500 em vez de 401 limpo — corrigido comparando bytes UTF-8.
  - **Conflito de rota com o `AgentOS`:** `AgentOS.get_app()` reivindica `GET /` por padrão para sua própria rota JSON de metadados, o que sombrearia o `index.html` do frontend. Resolvido com o parâmetro documentado `on_route_conflict="preserve_base_app"` do construtor do `AgentOS` (mecanismo suportado, não workaround), com teste de regressão (`TestFrontendRootRoute`) guardando contra uma versão futura do `agno` reverter o comportamento.
  - **CORS restrito (FAT-10):** `AgentOS` configurado com `cors_allowed_origins` explícito. Em 2026-09-02 as URLs de produção **saíram do código** (repo público não carrega infra): o default cobre só localhost e o deploy define `FATUUS_CORS_ORIGINS` — pendência FAT-12 para o próximo deploy.
  - **Verificação:** 75 testes de backend passando (`pytest`), 38 testes de frontend passando (`npm test`, dentro de `frontend/`), build do frontend (`tsc` + `vite`) e pacote PyPI (`python -m build` + `twine check`) validados.

## Evidência da verificação em produção (2026-09-02)

Redeploy pós-fix de segurança, revisão `fatuus-00001-5z6`. Confirmado por request real, com autenticação:

- Rotas antes abertas (`/memories`, `/config`, `/health`) agora exigem Basic Auth — 401 sem credencial, 200 com.
- `POST /clean` com texto que aciona a Camada 1 (3 frases com clichê repetido): `layer1_attempts: 3` (rodou as 3 tentativas de verdade, chamando o Gemini) e `layer1_accepted: false` — o gate rejeitou por variação de tamanho (0,38x), e o `cleaned_text` devolvido foi o da Camada 0, exatamente como a invariante "nunca pior que a Camada 0" promete.

**Após o fix da FAT-9** (revisão `fatuus-00003-9sm`), o mesmo texto de entrada foi reenviado: `layer1_accepted: true`, `layer1_attempts: 1`, `cleaned_text: "O sistema funciona bem. Além de rápido, oferece segurança."` — aceito de primeira, sem clichê, sem repetição. Confirma que a Camada 1 não só executa contra o Gemini real, mas também aceita uma reescrita típica depois da recalibração do piso.

## O que não funciona ainda

- **Suporte a idiomas além de PT-BR/EN:** fora de escopo nesta fase — cada idioma exige dicionário de marcadores próprio, não há heurística universal.
- **Publicação no PyPI:** pacote construído e validado (`twine check`), falta a credencial do titular (FAT-11).
- **CI:** sem GitHub Actions de teste ainda (FAT-6).
- **Deploy atualizado:** implantada revisão `fatuus-00005-g6j` (commit `e20127d`) com Camada 0 expandida, retry guiado e `FATUUS_CORS_ORIGINS` ativo (FAT-12 concluída). Falta rotação da credencial Basic Auth (FAT-13).

## Como rodar agora

```bash
python3 -m unittest discover -s tests -p "test_*.py"

python3 -m fatuus.cli probe exemplos/exemplo_ia_pt.md --lang pt
python3 -m fatuus.cli clean exemplos/exemplo_ia_pt.md --lang pt -o texto_limpo.md
```

## Onde está publicado

- **Repositório:** GitHub público (`acoplum/fatuus`).
- **Camada 1 e 2 (teste/produção):** Cloud Run, projeto `acoplum`, região `southamerica-east1`, revisão `fatuus-00005-g6j`, URL `https://fatuus-571033381701.southamerica-east1.run.app` (e `https://fatuus-lnpwo6gq7a-rj.a.run.app`) — deploy de 2026-09-03 com a Camada 2 (frontend React com cards, visualizador em abas, botão de cópia, heatmap e explicações), Camada 0 expandida e retry guiado. Acesso via Basic Auth em todas as rotas.
- **Pacote PyPI:** não publicado ainda.
