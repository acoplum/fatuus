"""Testes unitários para o motor determinístico do Fatuus."""

import unittest
from detector import FatuusDetector
from sanitizer import FatuusSanitizer


class TestFatuusDetector(unittest.TestCase):

    def setUp(self):
        self.detector_pt = FatuusDetector(lang="pt")
        self.detector_en = FatuusDetector(lang="en")

    def test_detect_invisible_chars(self):
        # Texto com zero-width space (\u200B) e BOM (\uFEFF)
        text = "Texto com marca\u200b invisível e\ufeff zero-width."
        invisibles = self.detector_pt.detect_invisible_chars(text)
        self.assertEqual(len(invisibles), 2)
        self.assertEqual(invisibles[0]["name"], "Zero Width Space (ZWSP)")
        self.assertEqual(invisibles[1]["name"], "Zero Width No-Break Space (BOM)")

    def test_find_slop_pt(self):
        text = (
            "É importante ressaltar que no cenário atual a tecnologia desempenha um papel fundamental. "
            "Podemos mergulhar fundo em uma ampla gama de tópicos para desvendar os segredos."
        )
        slops = self.detector_pt.find_slop(text)
        self.assertGreaterEqual(len(slops), 4)
        terms = [s["term"].lower() for s in slops]
        self.assertTrue(any("é importante ressaltar" in t for t in terms))
        self.assertTrue(any("no cenário atual" in t for t in terms))
        self.assertTrue(any("desempenha um papel fundamental" in t for t in terms))

    def test_find_slop_en(self):
        text = (
            "Let us delve into the vibrant ecosystem. This is a testament to the crucial role of AI. "
            "In conclusion, we are navigating the landscape of modern tech."
        )
        slops = self.detector_en.find_slop(text)
        self.assertGreaterEqual(len(slops), 4)
        terms = [s["term"].lower() for s in slops]
        self.assertTrue(any("delve into" in t for t in terms))
        self.assertTrue(any("a testament to" in t for t in terms))
        self.assertTrue(any("crucial role" in t for t in terms))

    def test_burstiness_uniform_vs_varied(self):
        # Texto uniforme (baixa variabilidade)
        uniform_text = (
            "Esta é a primeira frase do teste. Esta é a segunda frase do teste. "
            "Esta é a terceira frase do teste. Esta é a quarta frase do teste."
        )
        m_uniform = self.detector_pt.calculate_sentence_metrics(uniform_text)
        self.assertLess(m_uniform["std_dev_words"], 1.0)
        self.assertLess(m_uniform["burstiness"], 0.0)

        # Texto variado (alta variabilidade)
        varied_text = (
            "Sim. Absolutamente tudo mudou quando a arquitetura foi completamente reescrita após semanas de análise minuciosa. "
            "Não foi fácil. O time persistiu até o fim."
        )
        m_varied = self.detector_pt.calculate_sentence_metrics(varied_text)
        self.assertGreater(m_varied["std_dev_words"], 3.0)
        self.assertGreater(m_varied["burstiness"], m_uniform["burstiness"])


class TestFatuusSanitizer(unittest.TestCase):

    def setUp(self):
        self.sanitizer_pt = FatuusSanitizer(lang="pt")
        self.sanitizer_en = FatuusSanitizer(lang="en")

    def test_remove_invisible_chars(self):
        text = "Hello\u200b World\ufeff!"
        cleaned, count = self.sanitizer_en.remove_invisible_chars(text)
        self.assertEqual(cleaned, "Hello World!")
        self.assertEqual(count, 2)

    def test_deslop_pt(self):
        text = "É importante ressaltar que no cenário atual o software é um divisor de águas."
        res = self.sanitizer_pt.clean(text)
        cleaned = res["cleaned_text"]
        self.assertNotIn("É importante ressaltar que", cleaned)
        self.assertIn("hoje,", cleaned)
        self.assertIn("um marco", cleaned)

    def test_deslop_en(self):
        text = "We must delve into this problem. It is a testament to our team."
        res = self.sanitizer_en.clean(text)
        cleaned = res["cleaned_text"]
        self.assertNotIn("delve into", cleaned)
        self.assertIn("explore", cleaned)
        self.assertIn("evidence of", cleaned)


if __name__ == "__main__":
    unittest.main()
