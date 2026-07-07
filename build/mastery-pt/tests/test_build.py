import json, re, unittest
from build import emit_deck_js

class TestBuild(unittest.TestCase):
    def test_emit_is_parseable_and_shaped(self):
        cards = [{"id":"esm-0001","front":"hola","back":"hello","example":"","exampleEn":""}]
        src = emit_deck_js(cards, "Spanish Mastery", "paid:spanish-mastery")
        self.assertTrue(src.startswith("var deck = "))
        # deck object is everything up to the first ';\n' terminator
        body = src.split(";\n", 1)[0]
        obj = json.loads(body[len("var deck = "):])
        self.assertEqual(obj["id"], "paid:spanish-mastery")
        self.assertEqual(obj["lang"], "es")
        self.assertEqual(obj["cards"][0]["front"], "hola")
        # footer must be present for the plugin to load it
        self.assertIn("module.exports = deck", src)

if __name__ == "__main__":
    unittest.main()
