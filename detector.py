"""Módulo de detecção e métricas de artificialidade de texto (Fatuus Detector)."""

import math
import re
from typing import Any, Dict, List
from dicionarios import SLOP_PATTERNS_EN, SLOP_PATTERNS_PT, ZERO_WIDTH_CHARS


class FatuusDetector:
    """Analisador determinístico de características sintéticas em textos."""

    def __init__(self, lang: str = "pt"):
        self.lang = lang.lower()
        self.slop_patterns = (
            SLOP_PATTERNS_PT if self.lang.startswith("pt") else SLOP_PATTERNS_EN
        )

    def detect_invisible_chars(self, text: str) -> List[Dict[str, Any]]:
        """Identifica caracteres de zero-width ou invisíveis no texto."""
        found = []
        for i, char in enumerate(text):
            if char in ZERO_WIDTH_CHARS:
                found.append(
                    {
                        "char_code": hex(ord(char)),
                        "name": ZERO_WIDTH_CHARS[char],
                        "position": i,
                    }
                )
        return found

    def find_slop(self, text: str) -> List[Dict[str, Any]]:
        """Encontra ocorrências de clichês sintéticos (slop)."""
        matches = []
        for pattern in self.slop_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(
                    {
                        "term": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "pattern": pattern,
                    }
                )
        return sorted(matches, key=lambda x: x["start"])

    def calculate_sentence_metrics(self, text: str) -> Dict[str, float]:
        """Calcula métricas de burstiness e distribuição de sentenças."""
        # Divide por pontuações de fim de frase (. ! ?)
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
        # Varia de -1 (perfeitamente uniforme / LLM clássico) a +1 (altamente variado / humano)
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
        sentence_metrics = self.calculate_sentence_metrics(text)

        # Cálculo de Score Sintético (0 = 100% orgânico, 100 = altamente artificial)
        # 1. Densidade de slop por 100 palavras
        slop_density = (
            (len(slop_matches) / max(word_count, 1)) * 100 if word_count else 0
        )

        # 2. Penalidade por burstiness baixo/negativo (distribuição muito homogênea)
        burstiness = sentence_metrics.get("burstiness", 0.0)
        burstiness_penalty = max(0.0, (0.0 - burstiness) * 40)

        # 3. Penalidade por caracteres invisíveis
        invisible_penalty = min(len(invisible) * 15, 30)

        raw_score = (
            (slop_density * 20) + burstiness_penalty + invisible_penalty
        )
        synthetic_score = min(100.0, round(raw_score, 1))

        return {
            "word_count": word_count,
            "synthetic_score": synthetic_score,
            "slop_count": len(slop_matches),
            "slop_density_per_100_words": round(slop_density, 2),
            "invisible_char_count": len(invisible),
            "sentence_metrics": sentence_metrics,
            "slop_matches": slop_matches,
            "invisible_chars": invisible,
        }
