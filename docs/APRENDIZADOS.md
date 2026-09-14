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

### FAT-A3 · Burstiness (σ−μ)/(σ+μ) quase nunca é positiva em texto natural
**Data:** 2026-09-02 · **Origem:** recalibração do gate ao adicionar a checagem estrutural
**O que achávamos:** Que exigir melhora estrita de burstiness no gate só afetava texto uniforme de LLM — texto humano "saudável" teria burstiness positiva e passaria.
**O que era:** A fórmula B = (σ−μ)/(σ+μ) só fica positiva quando o desvio-padrão supera a média de palavras por frase — o que exige alternância extrema (frases de 1 palavra ao lado de frases de 20+). Texto humano típico mede entre −0,7 e −0,1. Exigir melhora estrita rejeitava qualquer reescrita que só corrigisse clichê ou padrão estrutural sem mexer no ritmo.
**O que muda:** O gate ganhou duas faixas (`gate.py`): burstiness negativa era o problema e precisa melhorar; burstiness já saudável só precisa não piorar além de 0,1 de tolerância. Teste de regressão `test_healthy_burstiness_only_needs_to_not_get_worse`.

### FAT-A4 · CI precisa executar o mesmo contrato do release
**Data:** 2026-09-14 · **Origem:** FAT-6 / preparação da distribuição
**O que achávamos:** Que as suítes locais documentadas bastavam para manter lint, tipos, backend e frontend alinhados entre contribuições.
**O que era:** Não havia workflow que executasse esses gates em push ou pull request; além disso, mypy revelou dois contratos de tipo que a suíte de comportamento não exercitava (`any` usado como tipo e a lista de `Step` passada ao Agno).
**O que muda:** O repositório agora instala as dependências de desenvolvimento, roda Ruff, mypy e pytest no Python e build/testes do frontend em `.github/workflows/ci.yml`; os dois pontos de tipo foram corrigidos sem alterar o comportamento do pipeline.
