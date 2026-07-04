import unittest
from lib.qc import parse_verdicts

class TestQC(unittest.TestCase):
    def test_parse_ok_and_bad(self):
        text = "hablo | OK\nhablé | BAD: wrong tense\n"
        v = parse_verdicts(text)
        self.assertTrue(v["hablo"])
        self.assertFalse(v["hablé"])

    def test_ignores_noise(self):
        self.assertEqual(parse_verdicts("random\n"), {})

if __name__ == "__main__":
    unittest.main()
