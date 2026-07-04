import unittest
from lib.verbs import lines_to_cards

class TestVerbs(unittest.TestCase):
    def test_lines_to_cards_are_lean(self):
        cards = lines_to_cards([("hablo", "I speak"), ("hablé", "I spoke")])
        self.assertEqual(cards[0].front, "hablo")
        self.assertEqual(cards[0].back, "I speak")
        self.assertEqual(cards[0].example, "")
        self.assertEqual(cards[0].exampleEn, "")

    def test_dedups_identical_forms(self):
        cards = lines_to_cards([("vivimos", "we live"), ("vivimos", "we lived")])
        self.assertEqual(len(cards), 1)

if __name__ == "__main__":
    unittest.main()
