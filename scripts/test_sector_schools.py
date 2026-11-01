"""Source-backed regressions for SD42 fiscal disclosures; originals are not needed in CI."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / 'research/salaries/sector-schools'
spec = importlib.util.spec_from_file_location('sector_schools_sd42', ROOT / 'scripts/sector_schools_sd42.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


class SchoolSourceRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((COLLECTION / 'sources.json').read_text())['sources']

    def source(self, ending_year, category='employee-remuneration'):
        return next(source for source in self.sources if source['periodEnd'] == f'{ending_year}-06-30' and source['category'] == category)

    def rows(self, source):
        return json.loads(gzip.decompress((COLLECTION / source['file']).read_bytes()))

    def test_periods_cohorts_and_source_fingerprints_are_preserved(self):
        self.assertEqual(len(self.sources), 32)
        self.assertEqual(sum(s['rowCount'] for s in self.sources), 10568)
        self.assertEqual({s['category'] for s in self.sources}, {'employee-remuneration', 'school-trustees'})
        inputs = {i['endingYear']: i for i in json.loads((COLLECTION / 'reviewed-inputs.json').read_text())['inputs']}
        for source in self.sources:
            ending = int(source['periodEnd'][:4])
            self.assertEqual(source['periodStart'], f'{ending - 1}-07-01')
            self.assertEqual(source['year'], f'{ending - 1}/{str(ending)[2:]}')
            self.assertEqual(source['sha256'], inputs[ending]['sha256'])
            for file_key, hash_key in [('file', 'dataSha256'), ('provenanceFile', 'provenanceSha256')]:
                self.assertEqual(hashlib.sha256((COLLECTION / source[file_key]).read_bytes()).hexdigest(), source[hash_key])

    def test_row_values_and_reported_residuals_are_lossless(self):
        for source in self.sources:
            rows = self.rows(source)
            evidence = json.loads(gzip.decompress((COLLECTION / source['provenanceFile']).read_bytes()))
            self.assertEqual(len(rows), source['rowCount'])
            self.assertEqual(len(rows), len(evidence['rows']))
            for row, original in zip(rows, evidence['rows']):
                self.assertEqual(Decimal(str(row[3])), Decimal(original['remuneration']))
                self.assertEqual(None if row[4] is None else Decimal(str(row[4])), None if original['expenses'] is None else Decimal(original['expenses']))
                self.assertEqual(row[5], original['page'])
                self.assertEqual(row[2], original['position'])
            for index, field in [(3, 'totalRemuneration'), (4, 'totalExpenses')]:
                total = sum(Decimal(str(row[index] or 0)) for row in rows)
                self.assertEqual(total, Decimal(str(source[field])))
                printed = Decimal(evidence['printedNamedControls'][index - 3].replace(',', ''))
                self.assertEqual(total - printed, Decimal(str(source['validation']['controlResiduals'][index - 3])))

    def test_negative_and_missing_expenses_keep_their_source_meaning(self):
        negative = next(row for row in self.rows(self.source(2024)) if row[1] == 'POGREBINSKY, KATERINA')
        self.assertEqual(negative[4], -252.96)
        blank = next(row for row in self.rows(self.source(2019, 'school-trustees')) if row[1] == 'CLARKSON, KENNETH B.')
        self.assertIsNone(blank[4])
        no_titles = self.rows(self.source(2014))
        self.assertTrue(all(row[2] is None for row in no_titles))

    def test_joined_names_and_footnotes_do_not_change_identity_or_amounts(self):
        rows = {row[1]: row for row in self.rows(self.source(2025))}
        self.assertEqual(rows['DO COITO ANTUNES MAFRA, DULCE'][2:5], ['TEACHER', 89619, 14])
        self.assertEqual(rows['DOS LIMA LLOYD, GABRIEL LUIS'][2:5], ['MANAGER, MARKETING & RECRUITMENT, INTERNATIONAL EDUCATION', 128493, 53533])
        self.assertEqual(rows['PENACERRADA, CARLO GATCHALI'][2], 'TEACHER')
        self.assertFalse(any('*' in name for name in rows))
        self.assertEqual(self.source(2025)['validation']['controlResiduals'], [17, -5])
        self.assertEqual(self.source(2026)['validation']['controlResiduals'], [-8, -9])

    def test_every_nonzero_source_control_residual_is_publicly_warned(self):
        residual_sources = [s for s in self.sources if any(s['validation']['controlResiduals'])]
        self.assertEqual(len(residual_sources), 4)
        for source in residual_sources:
            self.assertIn('Sum of published row amounts minus', source['publicWarning'])
            self.assertIn('cause is unconfirmed', source['publicWarning'])
        self.assertTrue(all(s['publicWarning'] is None for s in self.sources if not any(s['validation']['controlResiduals'])))

    def test_changed_original_is_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as cache, tempfile.TemporaryDirectory() as output:
            (Path(cache) / 'sd42-2005.pdf').write_bytes(b'%PDF-not-the-reviewed-original')
            with self.assertRaisesRegex(ValueError, 'fingerprint changed: 2005'):
                importer.build(Path(cache), Path(output))


if __name__ == '__main__':
    unittest.main()
