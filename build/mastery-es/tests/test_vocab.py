import unittest
from lib.vocab import parse_vocab_json

class TestVocab(unittest.TestCase):
    def test_parse_plain_json_array(self):
        text = '[{"front":"gato","back":"cat","example":"El gato duerme.","exampleEn":"The cat sleeps."}]'
        cards = parse_vocab_json(text)
        self.assertEqual(cards[0].front, "gato")
        self.assertEqual(cards[0].exampleEn, "The cat sleeps.")

    def test_parse_strips_code_fence(self):
        text = '```json\n[{"front":"sol","back":"sun","example":"Hace sol.","exampleEn":"It is sunny."}]\n```'
        self.assertEqual(parse_vocab_json(text)[0].front, "sol")

    def test_parse_skips_incomplete(self):
        text = '[{"front":"x","back":"y","example":"","exampleEn":""},{"front":"z"}]'
        cards = parse_vocab_json(text)
        self.assertEqual(len(cards), 1)

if __name__ == "__main__":
    unittest.main()
