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
    - `/docs`, `/openapi.json` e `/redoc` do `AgentOS` continuam acessíveis sem autenticação — decisão deliberada: divulgam a superfície da API, não dado nenhum.
- 50 testes, 100% passando (`pytest`; `python3 -m unittest discover` conta menos — contagem de subtestes difere entre os dois runners).

## Evidência da verificação em produção (2026-09-02)

Redeploy pós-fix de segurança, revisão `fatuus-00001-5z6`. Confirmado por request real, com autenticação:

- Rotas antes abertas (`/memories`, `/config`, `/health`) agora exigem Basic Auth — 401 sem credencial, 200 com.
- `POST /clean` com texto que aciona a Camada 1 (3 frases com clichê repetido): `layer1_attempts: 3` (rodou as 3 tentativas de verdade, chamando o Gemini) e `layer1_accepted: false` — o gate rejeitou por variação de tamanho, e o `cleaned_text` devolvido foi o da Camada 0, exatamente como a invariante "nunca pior que a Camada 0" promete.
- Isso comprova que a Camada 1 executa de ponta a ponta contra o Gemini real; não comprova que o gate aceita reescritas típicas — ver limitação acima.

## O que não funciona ainda

- **Camada 2 (frontend React):** especificada — ver [`features/camada-2-frontend`](features/camada-2-frontend/) —, não implementada.
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
- **Camada 1 (teste):** Cloud Run, projeto `acoplum`, região `southamerica-east1`, revisão `fatuus-00001-5z6`, URL `https://fatuus-571033381701.southamerica-east1.run.app` — deploy de 2026-09-02, pós-fix de segurança (a primeira revisão, `fatuus-00001-pzh`, foi apagada no mesmo dia como contenção: as mais de 100 rotas do `AgentOS` estavam sem autenticação num serviço público). Acesso via Basic Auth em todas as rotas.
- **Pacote PyPI:** não publicado ainda.
