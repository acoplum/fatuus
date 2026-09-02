#!/usr/bin/env python3
"""CLI Standalone para Análise e Limpeza de Textos Sintéticos (Fatuus Probe).

Uso:
  python3 fatuus_probe.py probe <arquivo.md> [--lang pt|en]
  python3 fatuus_probe.py clean <arquivo.md> [--lang pt|en] [-o saida.md]
"""

import argparse
import json
import sys
from pathlib import Path
from detector import FatuusDetector
from sanitizer import FatuusSanitizer


def format_report(result: dict, filename: str) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append(f"  FATUUS PROBE — Relatório de Análise Sintética")
    lines.append(f"  Arquivo: {filename}")
    lines.append("=" * 60)
    lines.append(f"• Total de Palavras:          {result['word_count']}")
    lines.append(f"• Score Sintético (0-100):     {result['synthetic_score']}%")

    # Diagnóstico rápido do score
    score = result["synthetic_score"]
    if score >= 60:
        diag = "🔴 ALTO PADRÃO DE IA (Clichês frequentes, cadência uniforme)"
    elif score >= 30:
        diag = "🟡 MODERADO (Alguns padrões sintéticos detectados)"
    else:
        diag = "🟢 BAIXO / ORGÂNICO (Ritmo natural e vocabulário variado)"
    lines.append(f"• Diagnóstico:                 {diag}")

    lines.append("\n--- Métricas Estruturais ---")
    metrics = result["sentence_metrics"]
    lines.append(f"• Quantidade de Sentenças:     {metrics['sentence_count']}")
    lines.append(f"• Média de Palavras/Frase:     {metrics['avg_words_per_sentence']}")
    lines.append(f"• Desvio Padrão de Comprimento:{metrics['std_dev_words']}")
    lines.append(f"• Burstiness Score (-1 a +1):  {metrics['burstiness']}")

    lines.append("\n--- Ocorrências de Slop / Clichês ---")
    lines.append(f"• Clichês Encontrados:         {result['slop_count']}")
    lines.append(f"• Densidade (por 100 palavras): {result['slop_density_per_100_words']}")

    if result["slop_matches"]:
        lines.append("• Termos destacados:")
        for m in result["slop_matches"][:15]:
            lines.append(f"   - '{m['term']}' (pos {m['start']})")
        if len(result["slop_matches"]) > 15:
            lines.append(f"   ... e mais {len(result['slop_matches']) - 15} ocorrências")

    lines.append("\n--- Caracteres Invisíveis / Watermarks ---")
    lines.append(f"• Caracteres Zero-Width:       {result['invisible_char_count']}")
    for inv in result["invisible_chars"]:
        lines.append(f"   - {inv['name']} ({inv['char_code']}) na posição {inv['position']}")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fatuus Probe: CLI exploratória para textos sintéticos.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando 'probe'
    probe_parser = subparsers.add_parser("probe", help="Analisa o texto e gera relatório de artificialidade")
    probe_parser.add_argument("file", type=str, help="Caminho para o arquivo markdown ou texto")
    probe_parser.add_argument("--lang", type=str, default="pt", choices=["pt", "en"], help="Idioma (pt ou en)")
    probe_parser.add_argument("--json", action="store_true", help="Saída em formato JSON puro")

    # Subcomando 'clean'
    clean_parser = subparsers.add_parser("clean", help="Aplica sanitização determinística no texto")
    clean_parser.add_argument("file", type=str, help="Caminho para o arquivo a limpar")
    clean_parser.add_argument("--lang", type=str, default="pt", choices=["pt", "en"], help="Idioma (pt ou en)")
    clean_parser.add_argument("-o", "--output", type=str, help="Arquivo de destino (imprime no stdout se omitido)")

    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Erro: arquivo '{args.file}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")

    if args.command == "probe":
        detector = FatuusDetector(lang=args.lang)
        result = detector.analyze(content)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_report(result, str(path)))

    elif args.command == "clean":
        sanitizer = FatuusSanitizer(lang=args.lang)
        res = sanitizer.clean(content)
        cleaned = res["cleaned_text"]

        if args.output:
            Path(args.output).write_text(cleaned, encoding="utf-8")
            print(f"✓ Arquivo sanitizado salvo em '{args.output}' ({res['invisible_removed']} caracteres invisíveis removidos, {res['slop_replaced']} clichês simplificados)")
        else:
            print(cleaned)


if __name__ == "__main__":
    main()
