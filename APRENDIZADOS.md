# APRENDIZADOS · fatuus

### A1 · Separação determinística antes de inferência com LLM
**Data:** 2026-09-02 · **Origem:** Benchmarks (`watermarks-remover` e `unslop`)
**O que achávamos:** Que a detecção de IA exigia necessariamente chamadas a LLM e modelos de classificação de perplexidade.
**O que era:** A maioria dos resquícios e watermarks de LLM consiste em padrões lexicais estritos ("delve", "é importante ressaltar", "tapeçaria"), caracteres invisíveis (zero-width spaces) e simetria métrica de sentenças que podem ser detectados e mitigados em < 5ms via regex e estatística simples.
**O que muda:** Arquitetura dividida em Camada 0 (determinística, zero-cost, local) e Camada 1 (agentes Agno para reescritura de ritmo).
