"""Módulo de detecção e métricas de artificialidade de texto (Fatuus Detector)."""

import math
import re
from typing import Any, Dict, List
from .dicionarios import (
    SLOP_PATTERNS_EN,
    SLOP_PATTERNS_PT,
    SPACE_LOOKALIKE_CHARS,
    STRUCTURAL_PATTERNS_EN,
    STRUCTURAL_PATTERNS_PT,
    TYPOGRAPHIC_REPLACEMENTS,
    VARIATION_SELECTORS,
    ZERO_WIDTH_CHARS,
    is_emoji_base,
)

# Aspas curvas têm o mesmo comprimento (1 code point) das retas: dá para
# normalizar só para fins de match sem invalidar as posições reportadas.
_MATCH_NORMALIZATION = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'})

_EM_DASH_RE = re.compile(r"[\u2013\u2014]")
_BOLD_SEGMENT_RE = re.compile(r"\*\*[^*\n]+\*\*")
_BOLD_BULLET_RE = re.compile(r"^\s*[-*\u2022]\s+\*\*[^*\n]+\*\*", re.MULTILINE)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)


def _has_emoji(text: str) -> bool:
    return any(is_emoji_base(char) and not char.isascii() for char in text)


class FatuusDetector:
    """Analisador determinístico de características sintéticas em textos."""

    def __init__(self, lang: str = "pt"):
        self.lang = lang.lower()
        is_pt = self.lang.startswith("pt")
        self.slop_patterns = SLOP_PATTERNS_PT if is_pt else SLOP_PATTERNS_EN
        self.structural_patterns = (
            STRUCTURAL_PATTERNS_PT if is_pt else STRUCTURAL_PATTERNS_EN
        )

    def detect_invisible_chars(self, text: str) -> List[Dict[str, Any]]:
        """Identifica caracteres de zero-width ou invisíveis no texto.

        Seletores de variação só contam quando não seguem uma base emoji —
        nessa posição são o canal clássico de watermark por steganografia;
        depois de um emoji são apresentação legítima.
        """
        found = []
        for i, char in enumerate(text):
            if char in ZERO_WIDTH_CHARS:
                name = ZERO_WIDTH_CHARS[char]
            elif char in VARIATION_SELECTORS and not (
                i > 0 and is_emoji_base(text[i - 1])
            ):
                name = VARIATION_SELECTORS[char]
            else:
                continue
            found.append(
                {
                    "char_code": hex(ord(char)),
                    "name": name,
                    "position": i,
                }
            )
        return found

    def find_slop(self, text: str) -> List[Dict[str, Any]]:
        """Encontra ocorrências de clichês sintéticos (slop)."""
        normalized = text.translate(_MATCH_NORMALIZATION)
        matches = []
        for pattern in self.slop_patterns:
            for match in re.finditer(pattern, normalized, re.IGNORECASE):
                matches.append(
                    {
                        "term": text[match.start() : match.end()],
                        "start": match.start(),
                        "end": match.end(),
                        "pattern": pattern,
                    }
                )
        return sorted(matches, key=lambda x: x["start"])

    def find_structural(self, text: str) -> List[Dict[str, Any]]:
        """Encontra padrões estruturais de escrita sintética.

        Detectáveis por regex, mas sem substituição determinística segura:
        reescrevê-los é papel da Camada 1, não do sanitizador.
        """
        normalized = text.translate(_MATCH_NORMALIZATION)
        matches = []
        for name, pattern in self.structural_patterns:
            for match in re.finditer(pattern, normalized, re.IGNORECASE):
                matches.append(
                    {
                        "term": text[match.start() : match.end()],
                        "start": match.start(),
                        "end": match.end(),
                        "pattern": pattern,
                        "name": name,
                    }
                )
        return sorted(matches, key=lambda x: x["start"])

    def calculate_typography(self, text: str, word_count: int) -> Dict[str, Any]:
        """Métricas tipográficas associadas a saída de LLM."""
        em_dash_count = len(_EM_DASH_RE.findall(text))
        curly_count = sum(text.count(char) for char in TYPOGRAPHIC_REPLACEMENTS if char != "\u2026")
        ellipsis_count = text.count("\u2026")
        space_lookalike_count = sum(text.count(char) for char in SPACE_LOOKALIKE_CHARS)
        per_100 = (em_dash_count / max(word_count, 1)) * 100 if word_count else 0.0
        return {
            "em_dash_count": em_dash_count,
            "em_dash_per_100_words": round(per_100, 2),
            "curly_quote_count": curly_count,
            "ellipsis_char_count": ellipsis_count,
            "space_lookalike_count": space_lookalike_count,
        }

    def calculate_formatting(self, text: str) -> Dict[str, int]:
        """Sinais de formatação Markdown típicos de listicle de LLM."""
        headings = _HEADING_RE.findall(text)
        return {
            "bold_segment_count": len(_BOLD_SEGMENT_RE.findall(text)),
            "bold_bullet_count": len(_BOLD_BULLET_RE.findall(text)),
            "emoji_heading_count": sum(1 for h in headings if _has_emoji(h)),
        }

    def calculate_sentence_metrics(self, text: str) -> Dict[str, float]:
        """Calcula métricas de burstiness e distribuição de sentenças."""
        sentences = [
            s.strip()
            for s in re.split(r"[.!?]+(?:\s+|$)", text)
            if len(s.strip()) > 0
        ]
        if not sentences:
            return {
                "sentence_count": 0,
                "avg_words_per_sentence": 0.0,
                "std_dev_words": 0.0,
                "burstiness": 0.0,
            }

        word_counts = [len(s.split()) for s in sentences]
        count = len(word_counts)
        avg = sum(word_counts) / count

        if count < 2:
            return {
                "sentence_count": count,
                "avg_words_per_sentence": round(avg, 2),
                "std_dev_words": 0.0,
                "burstiness": 0.0,
            }

        variance = sum((x - avg) ** 2 for x in word_counts) / count
        std_dev = math.sqrt(variance)

        # Burstiness: B = (std_dev - avg) / (std_dev + avg)
        burstiness = (
            (std_dev - avg) / (std_dev + avg) if (std_dev + avg) > 0 else 0.0
        )

        return {
            "sentence_count": count,
            "avg_words_per_sentence": round(avg, 2),
            "std_dev_words": round(std_dev, 2),
            "burstiness": round(burstiness, 3),
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Executa análise completa de marcadores sintéticos."""
        words = text.split()
        word_count = len(words)
        invisible = self.detect_invisible_chars(text)
        slop_matches = self.find_slop(text)
        structural_matches = self.find_structural(text)
        sentence_metrics = self.calculate_sentence_metrics(text)
        typography = self.calculate_typography(text, word_count)
        formatting = self.calculate_formatting(text)

        # Cálculo de Score Sintético (0 = orgânico, 100 = artificial)
        slop_density = (
            (len(slop_matches) / max(word_count, 1)) * 100 if word_count else 0
        )
        burstiness = sentence_metrics.get("burstiness", 0.0)
        burstiness_penalty = max(0.0, (0.0 - burstiness) * 40)
        invisible_penalty = min(len(invisible) * 15, 30)
        structural_penalty = min(len(structural_matches) * 8, 24)
        # Travessão vira penalidade só acima de 1/100 palavras — abaixo disso
        # é pontuação normal, sobretudo em PT-BR.
        em_dash_penalty = min(
            max(0.0, typography["em_dash_per_100_words"] - 1.0) * 5, 10
        )
        formatting_penalty = min(
            formatting["bold_bullet_count"] * 2 + formatting["emoji_heading_count"] * 3,
            10,
        )

        raw_score = (
            (slop_density * 20)
            + burstiness_penalty
            + invisible_penalty
            + structural_penalty
            + em_dash_penalty
            + formatting_penalty
        )
        synthetic_score = min(100.0, round(raw_score, 1))

        return {
            "word_count": word_count,
            "synthetic_score": synthetic_score,
            "slop_count": len(slop_matches),
            "slop_density_per_100_words": round(slop_density, 2),
            "invisible_char_count": len(invisible),
            "structural_count": len(structural_matches),
            "sentence_metrics": sentence_metrics,
            "typography": typography,
            "formatting": formatting,
            "slop_matches": slop_matches,
            "structural_matches": structural_matches,
            "invisible_chars": invisible,
        }
