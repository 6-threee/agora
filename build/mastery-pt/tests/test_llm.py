import unittest
from lib.llm import chunks, parse_arrow_lines

class TestLLM(unittest.TestCase):
    def test_chunks_splits_evenly(self):
        self.assertEqual(list(chunks([1,2,3,4,5], 2)), [[1,2],[3,4],[5]])

    def test_parse_arrow_lines(self):
        text = "hablo → I speak\ngarbage line\nhablé → I spoke\n"
        self.assertEqual(parse_arrow_lines(text),
                         [("hablo", "I speak"), ("hablé", "I spoke")])

    def test_parse_trims_whitespace(self):
        self.assertEqual(parse_arrow_lines("  a  →  b  "), [("a", "b")])

if __name__ == "__main__":
    unittest.main()
