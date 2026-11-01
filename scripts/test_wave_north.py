"""Protect the reviewed source boundaries, missing values and column meanings."""
import gzip
import json
from pathlib import Path
import unittest

from scripts.parse_wave_north import money

OUT = Path(__file__).resolve().parents[1] / 'research/salaries/municipal-wave-north'


class NorthernMunicipalSourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((OUT / 'sources.json').read_text())['sources']
        cls.rows = {source['id'].removeprefix('municipal-wave-north-'):
                    json.loads(gzip.decompress((OUT / source['file']).read_bytes())) for source in cls.sources}

    def test_cohort_counts_and_council_separation(self):
        self.assertEqual(sum(s['rowCount'] for s in self.sources if s['category'] == 'employee-remuneration'), 373)
        self.assertEqual(sum(s['rowCount'] for s in self.sources if s['category'] == 'elected-officials'), 28)
        self.assertEqual(len({s['employerSlug'] for s in self.sources}), 5)
        self.assertEqual(len(self.sources), 12)

    def test_wrapped_title_and_name_column_are_separate(self):
        rows = self.rows['district-of-chetwynd-2024']
        self.assertEqual(rows[0][1:5], ['Berg, Emily', 'Heavy Equipment Operator', 85827, 1177])
        brake = next(r for r in rows if r[1] == 'Brake, Blaine')
        self.assertEqual(brake[2], 'Public Works Lead Hand Supervisor')
        ennis = next(r for r in rows if r[1] == 'Ennis, Deanne')
        self.assertEqual(ennis[2], 'Corporate Officer / Human Resources Manager')

    def test_department_does_not_become_job_title_or_name(self):
        rows = self.rows['northern-rockies2024']
        barry = next(r for r in rows if r[1] == 'BARRY, SCOTT')
        self.assertIsNone(barry[2])
        self.assertEqual(barry[3], 251439)
        source = next(s for s in self.sources if s['id'].endswith('northern-rockies2024'))
        evidence = json.loads(gzip.decompress((OUT / source['validation']['evidenceFile']).read_bytes()))
        self.assertIn(['BARRY, SCOTT', 'CAO', 25143900, 884200, 5], evidence['rows'])
        self.assertIn('ESTATE OF RYAN KERR', {r[1] for r in self.rows['northern-rockies2025']})

    def test_dashes_stay_missing_and_explicit_zero_survives(self):
        lafleur = next(r for r in self.rows['taylor2022'] if r[1] == 'Lafleur, T')
        self.assertIsNone(lafleur[4])
        jones = next(r for r in self.rows['district-of-chetwynd-2025'] if r[1] == 'Jones, Jean')
        self.assertEqual(jones[4], 0)
        aspenden = self.rows['northern-rockies2025'][0]
        self.assertIsNone(aspenden[4])

    def test_totals_do_not_attach_to_last_employee(self):
        rows = self.rows['city-of-williams-lake-2024']
        self.assertEqual(rows[-1][1:5], ['Zakall, J.', 'Facility Maintenance III', 85189, 284])
        self.assertEqual(sum(r[3] for r in rows), 5149051)
        self.assertNotIn('Consolidated', ' '.join(r[1] for r in rows))
        self.assertTrue(any(s.get('publicWarning') for s in self.sources if s['employerSlug'] == 'city-of-williams-lake'))
        young = next(r for r in self.rows['city-of-dawson-creek-2024'] if r[1] == 'Young, T')
        self.assertEqual(young[2], 'Corporate Officer')
        self.assertFalse(any('Consolidated' in (r[2] or '') for rows in self.rows.values() for r in rows))

    def test_money_preserves_negative_and_rejects_merged_cells(self):
        self.assertEqual(money('-1,234.56'), -123456)
        self.assertIsNone(money('—'))
        self.assertEqual(money('0.00'), 0)
        with self.assertRaises(ValueError):
            money('21,880175,330')


if __name__ == '__main__':
    unittest.main()
