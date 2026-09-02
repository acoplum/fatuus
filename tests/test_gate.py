import unittest

from fatuus.gate import evaluate_gate


class TestEvaluateGate(unittest.TestCase):
    def test_accepts_candidate_without_slop_with_better_burstiness(self):
        original = (
            "É importante ressaltar que o sistema funciona bem. É importante "
            "ressaltar que o sistema é rápido. É importante ressaltar que o "
            "sistema é seguro."
        )
        candidate = (
            "O sistema funciona bem. É rápido, seguro, e resolveu um problema "
            "real que ninguém tinha atacado antes com essa profundidade."
        )
        result = evaluate_gate("pt", original, candidate)
        self.assertTrue(result.accepted, result.reasons)

    def test_size_ratio_can_be_measured_against_a_separate_baseline(self):
        pre_sanitizacao = (
            "É importante ressaltar que o sistema funciona bem. É importante "
            "ressaltar que o sistema é rápido. É importante ressaltar que o "
            "sistema é seguro."
        )
        sanitizado = "o sistema funciona bem. o sistema é rápido. o sistema é seguro."
        candidate = (
            "O sistema funciona bem. É rápido, seguro, e resolveu um problema "
            "real que ninguém tinha atacado antes com essa profundidade."
        )

        contra_sanitizado = evaluate_gate("pt", sanitizado, candidate)
        contra_original = evaluate_gate(
            "pt", sanitizado, candidate, size_baseline_text=pre_sanitizacao
        )

        self.assertFalse(contra_sanitizado.accepted)
        self.assertTrue(
            any("variação de tamanho" in r for r in contra_sanitizado.reasons)
        )
        self.assertTrue(contra_original.accepted, contra_original.reasons)

    def test_rejects_candidate_with_reintroduced_slop(self):
        original = "O sistema funciona bem."
        candidate = "É importante ressaltar que o sistema funciona bem."
        result = evaluate_gate("pt", original, candidate)
        self.assertFalse(result.accepted)
        self.assertTrue(any("clichê" in r for r in result.reasons))

    def test_rejects_candidate_with_worse_burstiness(self):
        original = (
            "O sistema funciona bem, mas tem uma falha rara. Ela aparece só "
            "sob carga alta, e ninguém tinha visto isso antes."
        )
        candidate = (
            "O sistema funciona bem. O sistema tem uma falha. A falha é rara. "
            "A falha aparece sob carga."
        )
        result = evaluate_gate("pt", original, candidate)
        self.assertFalse(result.accepted)
        self.assertTrue(any("burstiness" in r for r in result.reasons))

    def test_rejects_candidate_much_shorter_than_original(self):
        original = (
            "Primeira frase relevante aqui. Segunda frase com mais contexto "
            "técnico embutido. Terceira frase fechando o raciocínio com uma "
            "conclusão prática."
        )
        candidate = "Resumo curto."
        result = evaluate_gate("pt", original, candidate)
        self.assertFalse(result.accepted)
        self.assertTrue(any("variação de tamanho" in r for r in result.reasons))


if __name__ == "__main__":
    unittest.main()
