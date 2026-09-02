# APRENDIZADOS · fatuus

### FAT-A1 · Separação determinística antes de inferência com LLM
**Data:** 2026-09-02 · **Origem:** Benchmarks (`watermarks-remover` e `unslop`)
**O que achávamos:** Que a detecção de IA exigia necessariamente chamadas a LLM e modelos de classificação de perplexidade.
**O que era:** A maioria dos resquícios e watermarks de LLM consiste em padrões lexicais estritos ("delve", "é importante ressaltar", "tapeçaria"), caracteres invisíveis (zero-width spaces) e simetria métrica de sentenças que podem ser detectados e mitigados em < 5ms via regex e estatística simples.
**O que muda:** Arquitetura dividida em Camada 0 (determinística, zero-cost, local) e Camada 1 (agentes Agno para reescritura de ritmo).

### FAT-A2 · Benchmark de referências precisa de verificação primária, não estimativa
**Data:** 2026-09-02 · **Origem:** revisão do benchmark em `frentes/1-opensource/projetos/7-fatuus.md`
**O que achávamos:** Que a tabela de sete repositórios de referência (estrelas, stack, técnica) estava correta como registrada.
**O que era:** Verificação via GitHub API + README bruto mostrou estrelas desatualizadas em 5 dos 7 repos (de 2x a 3,2x o valor real), stack errada em 2 (`humanize-text` é Python, não HTML/JS; `patina` é Node/TS, não Markdown) e três claims funcionais sem lastro no README (`humanize-text` não suporta PT-BR; `humanizer-ru` não trata ordem direta/indireta; `humanizer-ja` não é específico de pontuação/partículas). Nenhum repo era inexistente ou tinha owner trocado — o erro foi generalizar sem checar a fonte primária.
**O que muda:** Tabela de benchmark corrigida com dados verificados. Toda citação de repositório externo (estrelas, stack, técnica) neste projeto passa a exigir checagem contra o README/API real antes de entrar em documento, não estimativa por familiaridade com o nome do projeto.
