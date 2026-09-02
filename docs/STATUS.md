# Status — fatuus

**Atualizado:** 2026-09-02 · **Estágio:** em construção

## O que é

Kit open source que detecta vícios de linguagem sintética (*slop*) e caracteres de fingerprint invisíveis em texto gerado por IA, e recompõe o ritmo (*burstiness*) do texto — de forma determinística hoje, e agêntica na Camada 1 (em construção). Serve times de conteúdo e devs que geram texto com LLM e não querem publicar com marcas óbvias de IA.

## O que já funciona

- **Camada 0 (determinística):** normalizador de caracteres invisíveis (ZWSP, ZWNJ, ZWJ, BOM, marcadores de direção), métrica de *burstiness* (-1 a +1) sobre distribuição de comprimento de sentenças, dicionários de clichês sintéticos PT-BR/EN, sanitizador determinístico.
- **CLI (`fatuus probe` / `fatuus clean`):** inspeção com diagnóstico visual de score sintético e exportação JSON.
- 7 testes unitários, 100% passando.

## O que não funciona ainda

- **Camada 1 (motor agêntico Agno):** especificada — ver [`features/camada-1-agno`](features/camada-1-agno/) —, não implementada.
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

Em nenhum lugar — repositório público no GitHub (`acoplum/fatuus`), sem pacote publicado.
