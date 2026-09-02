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
