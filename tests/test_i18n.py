import unittest

from ui_v2.i18n import TRANSLATIONS


class TranslationCatalogTests(unittest.TestCase):
    def test_all_supported_languages_have_the_same_keys(self):
        expected = set(TRANSLATIONS["en"])
        self.assertEqual(expected, set(TRANSLATIONS["ru"]))
        self.assertEqual(expected, set(TRANSLATIONS["uk"]))

    def test_translations_are_non_empty_and_format_placeholders_match(self):
        for key in TRANSLATIONS["en"]:
            values = [TRANSLATIONS[language][key] for language in ("ru", "en", "uk")]
            self.assertTrue(all(str(value).strip() for value in values), key)
            placeholder_sets = [
                {part.split("}", 1)[0] for part in str(value).split("{")[1:]}
                for value in values
            ]
            self.assertEqual(placeholder_sets[0], placeholder_sets[1], key)
            self.assertEqual(placeholder_sets[1], placeholder_sets[2], key)


if __name__ == "__main__":
    unittest.main()
