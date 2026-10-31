"""Prevent silent precision loss, broad glyph repair or promotion of held sources."""
from copy import deepcopy
from decimal import Decimal
import gzip
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("island_import", Path(__file__).with_name("import-island-health-salaries.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class IslandHealthImportTests(unittest.TestCase):
    def test_mixed_precision_and_negative_missing_semantics(self):
        self.assertEqual(mod.amount("83925.79"), Decimal("83925.79"))
        self.assertEqual(mod.amount("2,240.83"), Decimal("2240.83"))
        self.assertEqual(mod.amount("-   210"), Decimal(-210))
        self.assertEqual(mod.amount("(3,743)"), Decimal(-3743))
        self.assertIsNone(mod.amount("‐"))
        self.assertEqual(mod.amount("0.00"), Decimal(0))

    def test_unknown_glyph_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.amount("1ϯ,ϭϭϳ")
        for args in (("1ϯ,ϭϭϳ", "2023/24", 295, "MACNEIL,KATHRYN E"),
                     ("1ϯ,ϭϭϳ", "2024/25", 296, "MACNEIL,KATHRYN E"),
                     ("1ϯ,ϭϭϳ", "2024/25", 295, "OTHER,NAME")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                mod.amount(mod.reviewed_expense_token(*args))

    def test_reviewed_glyph_has_exact_cell_scope(self):
        token = mod.reviewed_expense_token("1ϯ,ϭϭϳ", "2024/25", 295, "MACNEIL,KATHRYN E")
        self.assertEqual(mod.amount(token), Decimal(13117))
        row = mod.parse_row("MACNEIL,KATHRYN E     409,201    1ϯ,ϭϭϳ", 295, "2024/25")
        self.assertEqual(row[3:5], [Decimal(409201), Decimal(13117)])

    def test_employee_cents_are_never_rounded(self):
        row = mod.parse_row("ABBEY, DARIN      92,227.71      8,449.33", 1, "2017/18")
        self.assertEqual(row[3:5], [Decimal("92227.71"), Decimal("8449.33")])
        encoded = json.dumps(row, default=mod.json_number)
        self.assertEqual(json.loads(encoded, parse_float=Decimal)[3:5], row[3:5])

    def test_unknown_data_line_and_below_threshold_fail(self):
        for line in ("UNKNOWN EMPLOYEE DATA", "EXAMPLE,NAME     74,999     10", "EXAMPLE,NAME     75,000     -"):
            with self.subTest(line=line), self.assertRaises(ValueError):
                mod.parse_row(line, 1, "2024/25")

    def test_held_sources_have_no_accepted_paths(self):
        manifest = json.loads((mod.COLLECTION / "sources.json").read_text())
        held = [source for source in manifest["sources"] if source["status"] == "held-for-review"]
        self.assertEqual([source["year"] for source in held], ["2022/23", "2023/24"])
        for source in held:
            self.assertNotIn("file", source)
            self.assertFalse(source["accepted"])
            self.assertTrue(source["candidateFile"].startswith("staging/"))

    def test_source_count_discrepancy_blocks_promotion(self):
        self._assert_promotion_fails("2022/23")

    def test_source_expense_discrepancy_blocks_promotion(self):
        self._assert_promotion_fails("2023/24")

    def _assert_promotion_fails(self, year):
        review = json.loads((mod.COLLECTION / "reviewed-inputs.json").read_text())
        reviewed = deepcopy(next(source for source in review["sources"] if source["year"] == year))
        reviewed["heldReason"] = None
        rows = json.loads(gzip.decompress((mod.COLLECTION / "staging" / (year.replace("/", "-") + ".json.gzip")).read_bytes()), parse_float=Decimal)
        for row in rows:
            row[3] = Decimal(str(row[3]))
            if row[4] is not None:
                row[4] = Decimal(str(row[4]))
        with self.assertRaises(ValueError):
            mod.validate_controls(rows, {}, reviewed)


if __name__ == "__main__":
    unittest.main()
