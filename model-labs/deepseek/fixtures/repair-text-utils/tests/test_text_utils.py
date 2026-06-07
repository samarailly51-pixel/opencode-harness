import unittest

from text_utils import normalize_title, slugify


class TextUtilsTests(unittest.TestCase):
    def test_normalize_title_strips_and_title_cases(self) -> None:
        self.assertEqual(normalize_title("  hello harness  "), "Hello Harness")

    def test_slugify_lowercases_and_uses_hyphens(self) -> None:
        self.assertEqual(slugify("Hello Harness Lab"), "hello-harness-lab")


if __name__ == "__main__":
    unittest.main()
