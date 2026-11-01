"""Regression guards for published Metro missing cells and partial coverage."""
import gzip
import json
from pathlib import Path
import unittest

OUT = Path(__file__).resolve().parents[1] / 'research/salaries/sector-government-police'


class MetroPublishedScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((OUT / 'sources.json').read_text())['sources']

    def test_missing_components_are_held_and_complete_source_evidence_retained(self):
        self.assertEqual(sum(s['rowCount'] for s in self.sources), 6495)
        self.assertEqual(sum(s['originalNamedRowCount'] for s in self.sources), 6504)
        self.assertEqual(sum(s['heldRowCount'] for s in self.sources), 9)
        for source in self.sources:
            evidence = json.loads(gzip.decompress((OUT / source['validation']['evidenceFile']).read_bytes()))
            self.assertEqual(len(evidence['rows']), source['originalNamedRowCount'])
            self.assertEqual(source['completeEmployeeSchedule'], source['heldRowCount'] == 0)
            self.assertEqual(sum(r[2] is None for r in evidence['rows']), source['heldRowCount'])
        first = self.sources[0]
        self.assertIn({'name': 'Atherton, Heather', 'salaryPayments': 97242, 'taxableBenefitsAndOther': None, 'expenses': 2868, 'pdfPage': 55,
                       'reason': 'Benefits/other is a published dash without a zero legend; composite remuneration is incomplete.'}, first['heldRows'])

    def test_expense_dashes_do_not_become_zero(self):
        full_missing, accepted_missing = 0, 0
        for source in self.sources:
            evidence = json.loads(gzip.decompress((OUT / source['validation']['evidenceFile']).read_bytes()))['rows']
            accepted = json.loads(gzip.decompress((OUT / source['file']).read_bytes()))
            self.assertEqual(len(accepted), source['rowCount'])
            full_missing += sum(r[3] is None for r in evidence)
            accepted_missing += sum(r[4] is None for r in accepted)
        self.assertEqual(full_missing, 376)
        self.assertEqual(accepted_missing, 374)

    def test_pay_uses_two_disclosed_components_and_excludes_expenses(self):
        source = self.sources[-1]
        accepted = json.loads(gzip.decompress((OUT / source['file']).read_bytes()))
        abad = next(r for r in accepted if r[1] == 'Abad, Christian')
        self.assertEqual(abad, ['metro-vancouver', 'Abad, Christian', None, 108593, 15138, 73])
        held_names = {r['name'] for r in source['heldRows']}
        self.assertNotIn('Anggabrata, Dion', {r[1] for r in accepted})
        self.assertIn('Anggabrata, Dion', held_names)
        self.assertIn('Complete original named table', source['validation']['printedControlsScope'])


if __name__ == '__main__':
    unittest.main()
