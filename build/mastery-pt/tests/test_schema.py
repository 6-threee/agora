import unittest
from lib.schema import Card, assign_ids, validate

class TestSchema(unittest.TestCase):
    def test_assign_ids_sequential_padded(self):
        out = assign_ids([Card("hola", "hello"), Card("adiós", "goodbye")])
        self.assertEqual(out[0]["id"], "esm-0001")
        self.assertEqual(out[1]["id"], "esm-0002")

    def test_card_dict_has_all_five_fields(self):
        out = assign_ids([Card("hablo", "I speak")])[0]
        self.assertEqual(set(out), {"id", "front", "back", "example", "exampleEn"})
        self.assertEqual(out["example"], "")

    def test_validate_flags_duplicate_front(self):
        cards = assign_ids([Card("hola", "hello"), Card("hola", "hi")])
        errs = validate(cards)
        self.assertTrue(any("duplicate front" in e for e in errs))

    def test_validate_flags_empty_required(self):
        cards = assign_ids([Card("", "hello")])
        self.assertTrue(any("empty front" in e for e in validate(cards)))

    def test_validate_passes_clean(self):
        cards = assign_ids([Card("hola", "hello"), Card("adiós", "goodbye")])
        self.assertEqual(validate(cards), [])

if __name__ == "__main__":
    unittest.main()
