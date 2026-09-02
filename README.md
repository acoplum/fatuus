# Fatuus — Laboratório Exploratório (Incubação)

Protótipo determinístico e suíte de testes de artificialidade sintética do projeto **Fatuus**.

## Estrutura do Módulo

- [`fatuus_probe.py`](fatuus_probe.py): CLI standalone para inspecionar e limpar markdown / texto.
- [`detector.py`](detector.py): Cálculo de *Burstiness*, detecção de caracteres invisíveis e densidade de clichês sintéticos.
- [`sanitizer.py`](sanitizer.py): Higienizador determinístico de texto e normalizador de pontuação.
- [`dicionarios.py`](dicionarios.py): Dicionários de termos e padrões em PT-BR e EN.
- [`test_probe.py`](test_probe.py): Testes unitários com stdlib (`python3 -m unittest test_probe.py`).
- [`exemplos/`](exemplos/): Amostras de texto em Português e Inglês para teste comparativo.

## Como Executar

### 1. Rodar os Testes
```bash
python3 -m unittest test_probe.py
```

### 2. Analisar um Arquivo (Probe)
```bash
# Análise em Português
python3 fatuus_probe.py probe exemplos/exemplo_ia_pt.md --lang pt

# Análise em Inglês
python3 fatuus_probe.py probe exemplos/exemplo_ia_en.md --lang en

# Saída em JSON para pipelines
python3 fatuus_probe.py probe exemplos/exemplo_ia_pt.md --lang pt --json
```

### 3. Sanitizar Texto (Clean)
```bash
python3 fatuus_probe.py clean exemplos/exemplo_ia_pt.md --lang pt -o texto_limpo.md
```
