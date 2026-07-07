import os, unittest
from lib.frequency import top_forms

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "es_top_words.csv")

class TestFrequency(unittest.TestCase):
    def test_returns_n_forms_in_rank_order(self):
        forms = top_forms(5, DATA)
        self.assertEqual(forms, ["que", "de", "no", "a", "la"])

    def test_excludes_header(self):
        self.assertNotIn("word", top_forms(10, DATA))

    def test_count_matches_request(self):
        self.assertEqual(len(top_forms(2000, DATA)), 2000)

if __name__ == "__main__":
    unittest.main()
