# Status — fatuus

**Atualizado:** 2026-09-02 · **Estágio:** em construção

## O que é

Kit open source que detecta vícios de linguagem sintética (*slop*) e caracteres de fingerprint invisíveis em texto gerado por IA, e recompõe o ritmo (*burstiness*) do texto — de forma determinística hoje, e agêntica na Camada 1 (em construção). Serve times de conteúdo e devs que geram texto com LLM e não querem publicar com marcas óbvias de IA.

## O que já funciona

- **Camada 0 (determinística):** normalizador de caracteres invisíveis (ZWSP, ZWNJ, ZWJ, BOM, marcadores de direção), métrica de *burstiness* (-1 a +1) sobre distribuição de comprimento de sentenças, dicionários de clichês sintéticos PT-BR/EN, sanitizador determinístico.
- **CLI (`fatuus probe` / `fatuus clean`):** inspeção com diagnóstico visual de score sintético e exportação JSON.
- **Camada 1 (motor agêntico Agno):** pipeline com agentes de cadência, anti-simetria e integridade semântica orquestrados via `AgentOS`, expostos em FastAPI com `SqliteDb`. Agente de watermark estatístico com ativação condicional. Gate determinístico de aceitação com retry. Roda ponta a ponta em teste (sanitizador → workflow → gate, com o modelo mockado); **não verificada em produção ainda** — ver abaixo.
  - **Limitações conhecidas:**
    - Gate de fidelidade v1 usa proxy de variação de tamanho de texto em lugar de similaridade semântica real — não há embeddings nesta versão. A razão é medida contra o texto pré-sanitização, não contra o texto que a Camada 1 recebe.
    - O retry é reamostragem, não retry guiado: cada tentativa recebe o mesmo texto de entrada, e os motivos de rejeição do gate não chegam a nenhum agente.
    - `agno[os]` traz `uvicorn` sem extras de performance (`uvicorn[standard]`) — aceitável para este teste, revisar se performance importar depois.
- 49 testes, 100% passando (`pytest`).

## O que ainda não foi verificado em produção

A Camada 1 **nunca rodou de ponta a ponta contra o Gemini em produção**, ao contrário do que este arquivo afirmava antes. O deploy de teste de 2026-09-02 subiu e respondeu, mas o texto do smoke test — `"É importante ressaltar que o sistema é robusto e escalável."` — sanitiza para uma frase só, com burstiness `0.0`: `_needs_layer1` devolve `False` e o pipeline pula a Camada 1 sem chamar o modelo nenhuma vez. Isso é reproduzível a partir do código como está. O que aquele smoke test provou foi a Camada 0 servida por HTTP.

Verificar exige um redeploy e um smoke test com entrada que comprovadamente entre na Camada 1, guardando o JSON bruto da resposta: `layer1_attempts` diferente de zero e `cleaned_text` diferente de `layer0.cleaned_text`.

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
- **Camada 1 (teste):** sem ambiente no ar. O deploy de teste de 2026-09-02 (Cloud Run, projeto `acoplum`, região `southamerica-east1`, revisão `fatuus-00001-pzh`) foi **apagado no mesmo dia**, como contenção do achado da revisão final: as mais de 100 rotas montadas pelo `AgentOS` estavam sem autenticação num serviço público. Redeploy só depois do fix revisado.
- **Pacote PyPI:** não publicado ainda.
