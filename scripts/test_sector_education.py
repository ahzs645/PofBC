"""Regression checks for SFU source boundaries and disclosed source anomalies."""
import gzip
import json
import unittest
from pathlib import Path

from parse_sector_education import core

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'research/salaries/sector-education'


def rows(period):
    return json.loads(gzip.decompress((DATA / f'sfu-{period}-employees.json.gzip').read_bytes()))


class SectorEducationTests(unittest.TestCase):
    def test_wrapped_before_money_baseline_stays_one_name(self):
        actual = [r for r in rows('2020-21') if r[1] == 'Aragon Sanchez, Fernando Martin']
        self.assertEqual([(r[3], r[4], r[5]) for r in actual], [(152833, 2260, 44)])

    def test_wrapped_after_money_baseline_joins_literal_hyphen(self):
        actual = [r for r in rows('2025-26') if r[1] == 'Belisle-Pipon, Jean-Christophe']
        self.assertEqual([(r[3], r[4], r[5]) for r in actual], [(138610, 4975, 53)])
        other = [r for r in rows('2025-26') if r[1] == 'Ackkiniraj Chandrasekar, Angayarkanni']
        self.assertEqual([(r[3], r[5]) for r in other], [(100568, 52)])

    def test_published_negative_expense_is_not_erased(self):
        actual = [r for r in rows('2025-26') if r[1] == 'Ghai, Sandhya']
        self.assertEqual([(r[3], r[4], r[5]) for r in actual], [(124849, -1727, 60)])

    def test_repeated_disclosed_name_retains_multiplicity(self):
        actual = [r for r in rows('2025-26') if r[1] == 'Zhang, Lin']
        self.assertEqual(len(actual), 3)
        self.assertEqual(sorted(r[3] for r in actual), [84531, 97761, 162573])

    def test_three_schmidt_conflicts_keep_original_disclosed_names(self):
        actual = {r[1]: (r[3], r[4], r[5]) for r in rows('2017-18') if r[1] in ['Schmidt, Michele', 'Schmidt, G', 'Schmidt, Margaret']}
        self.assertEqual(actual, {
            'Schmidt, Michele': (119776, 4725, 55),
            'Schmidt, G': (81003, 6570, 55),
            'Schmidt, Margaret': (132061, 811, 55),
        })
        manifest = json.loads((DATA / 'sources.json').read_text())['sources']
        source = next(s for s in manifest if s['year'] == '2017/18')
        self.assertEqual(source['validation']['compiledNameConflicts'], 3)
        self.assertIn('three matching payment cells', source['publicWarning'])
        self.assertIn("official 'Schmidt, Margaret' ($132,061, $811) versus compiled 'Schmidt, Michele'", source['publicWarning'])

    def test_unassigned_money_is_rejected(self):
        # A plausible extra monetary token must not disappear from a row.
        words = [(58, 80, 85, 90, 'Name'), (155, 80, 225, 90, 'Remuneration'),
                 (255, 80, 292, 90, 'Expenses'), (58, 100, 100, 110, 'Example,'),
                 (104, 100, 120, 110, 'Alex'), (199, 100, 228, 110, '100,000'),
                 (274, 100, 293, 110, '1,000'), (245, 100, 257, 110, '500')]
        with self.assertRaises(AssertionError):
            core(words, 1)

    def test_material_years_stay_outside_accepted_manifest(self):
        manifest = json.loads((DATA / 'sources.json').read_text())['sources']
        self.assertEqual([s['year'] for s in manifest], ['2017/18', '2018/19', '2020/21', '2021/22', '2024/25', '2025/26'])
        self.assertEqual(sum(s['rowCount'] for s in manifest), 13527)
        for source in manifest:
            v = source['validation']
            if v['remunerationResidual'] or v['expensesResidual']:
                self.assertFalse(v['summaryTotalReconciled'])
                self.assertIn('Cause unresolved', source['publicWarning'])


if __name__ == '__main__':
    unittest.main()
