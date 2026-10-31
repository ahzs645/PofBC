"""Keep the accepted transcription exceptions distinct from financial reconciliation."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from parse_municipal_lower_mainland import verify_data
from parse_municipal_small import extract

ROOT = Path(__file__).resolve().parents[1] / 'research/salaries'


class QualifiedMunicipalTests(unittest.TestCase):
    def test_lower_mainland_exceptions_preserve_cells_and_all_residuals(self):
        folder = ROOT / 'municipal-lower-mainland'
        sources = json.loads((folder / 'sources.json').read_text())['sources']
        reviewed = json.loads((folder / 'reviewed-inputs.json').read_text())['sources']
        for key, count, residuals in [('surrey-2025', 1543, [12, -1, 473]),
                                      ('north-vancouver-city-2022', 275, [0, -143, -1])]:
            source = next(s for s in sources if s['inputKey'] == key)
            config = next(s for s in reviewed if s['key'] == key)
            self.assertEqual(verify_data(source, config), count)
            self.assertEqual(source['validation']['controlResiduals'], residuals)
            self.assertFalse(source['validation']['allComponentSubtotalsExact'])
            self.assertIn('unresolved', source['publicWarning'])
            # Any later change still invalidates the normalized source. A source
            # exception must never become a blanket bypass of data integrity.
            changed = copy.deepcopy(source)
            changed['totalExpenses'] += 1
            with self.assertRaisesRegex(ValueError, 'totalExpenses mismatch'):
                verify_data(changed, config)

    def test_montrose_preserves_employee_cells_without_changing_council(self):
        folder = ROOT / 'municipal-small'
        config = json.loads((folder / 'reviewed-layouts.json').read_text())
        report = next(r for r in config['reports'] if r['employerSlug'] == 'village-of-montrose')
        for section in report['sections']:
            category = section['category']
            evidence = json.loads(gzip.decompress((folder / f'evidence/village-of-montrose-2023-{category}.json.gzip').read_bytes()))
            a = extract(evidence['mupdfWords'], section)
            b = extract(evidence['popplerWords'], section)
            self.assertEqual(a, b)
            self.assertEqual(a, evidence['rows'])
            controls = {c['field']: c for c in evidence['controls']}
            if category == 'employee-remuneration':
                self.assertEqual(len(a), 3)
                self.assertEqual(sum(r['pay'] for r in a), 26928716)
                self.assertEqual(sum(r['expenses'] for r in a), 650365)
                self.assertEqual(controls['expenses']['residual'], -36)
            else:
                self.assertEqual(len(a), 5)
                self.assertTrue(all(c['residual'] == 0 for c in controls.values()))


if __name__ == '__main__':
    unittest.main()
