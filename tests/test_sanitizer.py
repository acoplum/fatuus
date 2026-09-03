import unittest
from fatuus.sanitizer import FatuusSanitizer


class TestFatuusSanitizer(unittest.TestCase):

    def setUp(self):
        self.sanitizer_pt = FatuusSanitizer(lang="pt")
        self.sanitizer_en = FatuusSanitizer(lang="en")

    def test_remove_invisible_chars(self):
        text = "Hello\u200b World\ufeff!"
        cleaned, count = self.sanitizer_en.remove_invisible_chars(text)
        self.assertEqual(cleaned, "Hello World!")
        self.assertEqual(count, 2)

    def test_remove_bidi_and_word_joiner(self):
        text = "abc\u202edef\u2060ghi\u2066jkl"
        cleaned, count = self.sanitizer_pt.remove_invisible_chars(text)
        self.assertEqual(cleaned, "abcdefghijkl")
        self.assertEqual(count, 3)

    def test_variation_selector_after_emoji_is_kept(self):
        text = "Feito \u2714\ufe0f com sucesso\ufe0f."
        cleaned, count = self.sanitizer_pt.remove_invisible_chars(text)
        self.assertEqual(cleaned, "Feito \u2714\ufe0f com sucesso.")
        self.assertEqual(count, 1)

    def test_normalize_typography(self):
        text = "\u201cAspas\u201d e \u2018simples\u2019 com reticências\u2026 e espaço\u00a0duro\u2028fim"
        cleaned, count = self.sanitizer_pt.normalize_typography(text)
        self.assertEqual(cleaned, '"Aspas" e \'simples\' com reticências... e espaço duro\nfim')
        self.assertEqual(count, 7)

    def test_deslop_pt_capitalizes_sentence_start(self):
        text = "É importante ressaltar que no cenário atual o software é um divisor de águas."
        res = self.sanitizer_pt.clean(text)
        cleaned = res["cleaned_text"]
        self.assertNotIn("É importante ressaltar que", cleaned)
        self.assertTrue(cleaned.startswith("Hoje,"), cleaned)
        self.assertIn("um marco", cleaned)

    def test_deslop_does_not_touch_mixed_case_words(self):
        text = "É importante ressaltar que iPhone é popular."
        res = self.sanitizer_pt.clean(text)
        self.assertTrue(res["cleaned_text"].startswith("iPhone é popular"), res["cleaned_text"])

    def test_deslop_en(self):
        text = "We must delve into this problem. It is a testament to our team."
        res = self.sanitizer_en.clean(text)
        cleaned = res["cleaned_text"]
        self.assertNotIn("delve into", cleaned)
        self.assertIn("explore", cleaned)
        self.assertIn("evidence of", cleaned)

    def test_deslop_en_with_curly_apostrophe(self):
        # A normalização tipográfica roda antes do deslop, então o padrão
        # com apóstrofo reto alcança texto escrito com apóstrofo curvo.
        text = "It\u2019s worth noting that the fix works."
        res = self.sanitizer_en.clean(text)
        self.assertTrue(res["cleaned_text"].startswith("The fix works"), res["cleaned_text"])

    def test_every_slop_pattern_has_a_sanitizer_counterpart(self):
        """Assimetria detector↔sanitizer: todo clichê detectado em PT/EN
        precisa sair do texto depois do clean()."""
        from fatuus.detector import FatuusDetector

        samples = {
            "pt": (
                "É importante ressaltar que sim. No cenário atual tudo mudou. "
                "No mundo de hoje nada para. No mundo contemporâneo segue. "
                "Vale a pena notar o efeito. Vale lembrar que existe. Em suma, foi. "
                "Em conclusão, fim. Por fim, mas não menos importante, ok. "
                "Como mencionado anteriormente, segue. Um divisor de águas real. "
                "Desempenha um papel fundamental na rede. Uma ampla gama de itens. "
                "Uma vasta gama de casos. Um vislumbre de futuro. "
                "Mergulhar fundo em dados. Desvendar os segredos do código. "
                "Farol de esperança para nós. Tapeçaria cultural rica. "
                "Um testemunho de força. Essencial para garantir acesso. "
                "Sempre em constante evolução aqui. Impulsionar o crescimento já. "
                "Podemos concluir que deu certo. É inegável que houve avanço. "
                "Cabe destacar que funciona. Nos dias de hoje corre. "
                "Diante desse cenário agimos. Cada vez mais presente na rotina. "
                "Uma verdadeira revolução no setor. Mudança de paradigma total. "
                "Abordagem holística do tema. Embarcar em uma jornada nova. "
                "Elevar o nível do time. Desbloquear o potencial da equipe. "
                "É fundamental compreender o contexto."
            ),
            "en": (
                "Let us delve into this. A testament to the work. "
                "A tapestry of ideas. A beacon of hope. A crucial role here. "
                "A pivotal moment came. A real game-changer arrived. "
                "It is important to note that it works. "
                "In today's fast-paced world we move. In today's world we act. "
                "In today's digital landscape we build. "
                "Navigating the landscape of tech. Harnessing the power of data. "
                "Unleashing the potential of teams. A myriad of options. "
                "A plethora of tools. Fostering a sense of trust. "
                "Poised to grow fast. It underscores the need for care. "
                "A vibrant ecosystem thrives. In conclusion, done. "
                "Last but not least, thanks. An ever-evolving field. "
                "An ever-changing market. In the realm of science. "
                "At the end of the day, results. When it comes to quality, yes. "
                "It's worth noting the gain. Needless to say, it shipped. "
                "Embark on a journey now. Dive deep into the code. "
                "A treasure trove of data. A paradigm shift occurred. "
                "A holistic approach helps. It seamlessly integrates here. "
                "Elevate your writing today. Unlock the full potential of it."
            ),
        }
        for lang, sample in samples.items():
            with self.subTest(lang=lang):
                from fatuus.sanitizer import FatuusSanitizer

                detector = FatuusDetector(lang=lang)
                self.assertGreater(len(detector.find_slop(sample)), 20)
                cleaned = FatuusSanitizer(lang=lang).clean(sample)["cleaned_text"]
                leftovers = detector.find_slop(cleaned)
                self.assertEqual(
                    [m["term"] for m in leftovers], [], f"sobrou slop: {leftovers}"
                )


if __name__ == "__main__":
    unittest.main()
