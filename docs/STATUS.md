# Status — fatuus

**Atualizado:** 2026-09-02 · **Estágio:** em construção

## O que é

Kit open source que detecta vícios de linguagem sintética (*slop*) e caracteres de fingerprint invisíveis em texto gerado por IA, e recompõe o ritmo (*burstiness*) do texto — de forma determinística hoje, e agêntica na Camada 1 (em construção). Serve times de conteúdo e devs que geram texto com LLM e não querem publicar com marcas óbvias de IA.

## O que já funciona

- **Camada 0 (determinística):** normalizador de caracteres invisíveis (ZWSP, ZWNJ, ZWJ, BOM, marcadores de direção), métrica de *burstiness* (-1 a +1) sobre distribuição de comprimento de sentenças, dicionários de clichês sintéticos PT-BR/EN, sanitizador determinístico.
- **CLI (`fatuus probe` / `fatuus clean`):** inspeção com diagnóstico visual de score sintético e exportação JSON.
- **Camada 1 (motor agêntico Agno):** pipeline com agentes de cadência, anti-simetria e integridade semântica orquestrados via `AgentOS`, expostos em FastAPI com `SqliteDb`. Agente de watermark estatístico com ativação condicional. Gate determinístico de aceitação com retry. Deploy de teste confirmado em Cloud Run com sucesso (smoke test `/probe` e `/clean` operacionais).
  - **Limitações conhecidas:**
    - Gate de fidelidade v1 usa proxy de variação de tamanho de texto em lugar de similaridade semântica real — não há embeddings nesta versão.
    - Campo `attempts` do resultado do pipeline é sempre `1` — retry interno do `Loop` do Agno não expõe contagem real de iterações nesta versão.
    - `agno[os]` traz `uvicorn` sem extras de performance (`uvicorn[standard]`) — aceitável para este teste, revisar se performance importar depois.
- 7 testes unitários, 100% passando.

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
- **Camada 1 (teste):** Cloud Run, projeto `acoplum`, região `southamerica-east1`, revisão `fatuus-00001-pzh`, URL `https://fatuus-571033381701.southamerica-east1.run.app` — deploy de teste realizado em 2026-09-02.
- **Pacote PyPI:** não publicado ainda.
