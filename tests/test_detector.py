import unittest
from fatuus.detector import FatuusDetector


class TestFatuusDetector(unittest.TestCase):

    def setUp(self):
        self.detector_pt = FatuusDetector(lang="pt")
        self.detector_en = FatuusDetector(lang="en")

    def test_detect_invisible_chars(self):
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

    def test_detect_bidi_and_word_joiner_chars(self):
        text = "Texto\u202e com override\u202c, word joiner\u2060 e isolate\u2066."
        invisibles = self.detector_pt.detect_invisible_chars(text)
        names = [i["name"] for i in invisibles]
        self.assertIn("Right-to-Left Override (RLO)", names)
        self.assertIn("Pop Directional Formatting (PDF)", names)
        self.assertIn("Word Joiner (WJ)", names)
        self.assertIn("Left-to-Right Isolate (LRI)", names)

    def test_variation_selector_after_emoji_is_legitimate(self):
        text = "Feito \u2714\ufe0f com sucesso."
        invisibles = self.detector_pt.detect_invisible_chars(text)
        self.assertEqual(invisibles, [])

    def test_variation_selector_outside_emoji_is_a_watermark(self):
        text = "Texto\ufe0f com marca."
        invisibles = self.detector_pt.detect_invisible_chars(text)
        self.assertEqual(len(invisibles), 1)
        self.assertIn("Variation Selector", invisibles[0]["name"])

    def test_find_slop_matches_curly_apostrophes(self):
        text = "It\u2019s worth noting that this works."
        slops = self.detector_en.find_slop(text)
        self.assertEqual(len(slops), 1)
        self.assertEqual(slops[0]["term"], "It\u2019s worth noting")

    def test_find_structural_pt(self):
        text = "Não se trata de velocidade, mas de segurança do processo."
        matches = self.detector_pt.find_structural(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "não se trata de X, mas Y")

    def test_find_structural_en(self):
        text = "This is not only fast but also secure for everyone involved."
        matches = self.detector_en.find_structural(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "not only X but (also) Y")

    def test_typography_metrics(self):
        text = "O tempo mudou \u2014 e muito \u2014 nas \u201cúltimas\u201d semanas\u2026 com espaço\u00a0duro."
        result = self.detector_pt.analyze(text)
        typo = result["typography"]
        self.assertEqual(typo["em_dash_count"], 2)
        self.assertEqual(typo["curly_quote_count"], 2)
        self.assertEqual(typo["ellipsis_char_count"], 1)
        self.assertEqual(typo["space_lookalike_count"], 1)

    def test_formatting_metrics(self):
        text = (
            "# 🚀 Título com emoji\n"
            "- **Ponto um:** detalhe\n"
            "- **Ponto dois:** detalhe\n"
            "Texto com **negrito** solto.\n"
        )
        result = self.detector_pt.analyze(text)
        fmt = result["formatting"]
        self.assertEqual(fmt["emoji_heading_count"], 1)
        self.assertEqual(fmt["bold_bullet_count"], 2)
        self.assertEqual(fmt["bold_segment_count"], 3)

    def test_structural_count_raises_the_score(self):
        clean_text = "O sistema é rápido para todos os envolvidos no projeto."
        structural_text = (
            "It is not only fast but also secure for everyone involved."
        )
        clean_score = self.detector_en.analyze(clean_text)["synthetic_score"]
        structural_score = self.detector_en.analyze(structural_text)[
            "synthetic_score"
        ]
        self.assertGreater(structural_score, clean_score)

    def test_burstiness_metric(self):
        uniform_text = (
            "Esta é a primeira frase do teste. Esta é a segunda frase do teste. "
            "Esta é a terceira frase do teste. Esta é a quarta frase do teste."
        )
        m_uniform = self.detector_pt.calculate_sentence_metrics(uniform_text)
        self.assertLess(m_uniform["std_dev_words"], 1.0)
        self.assertLess(m_uniform["burstiness"], 0.0)

        varied_text = (
            "Sim. Absolutamente tudo mudou quando a arquitetura foi completamente reescrita após semanas de análise minuciosa. "
            "Não foi fácil. O time persistiu até o fim."
        )
        m_varied = self.detector_pt.calculate_sentence_metrics(varied_text)
        self.assertGreater(m_varied["std_dev_words"], 3.0)
        self.assertGreater(m_varied["burstiness"], m_uniform["burstiness"])


if __name__ == "__main__":
    unittest.main()
