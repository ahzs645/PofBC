"""Offline regression checks for the reviewed municipal disclosure tables."""
import copy
import gzip
import json
import unittest

import parse_sector_municipal as parser


class PittMeadowsSchedules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((parser.OUT / 'reviewed-layouts.json').read_text())
        cls.sources = json.loads((parser.OUT / 'sources.json').read_text())['sources']

    def evidence(self, year, category):
        report = next(r for r in self.config['reports'] if r['year'] == year)
        section = next(s for s in report['sections'] if s['category'] == category)
        source = next(s for s in self.sources if s['year'] == year and s['category'] == category)
        words = json.loads(gzip.decompress((parser.OUT / source['validation']['evidenceFile']).read_bytes()))
        return section, source, words

    def test_missing_and_explicit_zero_remain_distinct(self):
        for value in ['', '-', '–', '—']:
            self.assertIsNone(parser.money(value))
        self.assertEqual(parser.money('0'), 0)
        self.assertEqual(parser.money('0.00'), 0)
        self.assertEqual(parser.money('1,234.56'), 123456)
        with self.assertRaises(ValueError):
            parser.money('1,234 5,678')

    def test_all_fields_and_controls_reproduce_from_both_retained_readers(self):
        parser.build(self.config, parser.OUT, check_data=True)
        self.assertEqual(sum(s['rowCount'] for s in self.sources), 411)
        self.assertEqual(sum(s['rowCount'] for s in self.sources if s['category'] == 'employee-remuneration'), 360)
        self.assertEqual({s['year'] for s in self.sources}, {'2013', '2019', '2020', '2021', '2022', '2025'})

    def test_benefits_are_pay_and_expenses_are_separate(self):
        section, source, evidence = self.evidence('2020', 'employee-remuneration')
        rows = parser.extract(evidence['mupdfWords'], section)
        for row in rows:
            self.assertEqual(row['pay'], row['salary'] + row['benefits'])
        self.assertEqual(source['totalRemuneration'], 4808406)
        self.assertEqual(source['totalExpenses'], 52721)

    def test_first_employee_ablenas_is_not_lost_at_the_table_boundary(self):
        section, _, evidence = self.evidence('2021', 'employee-remuneration')
        rows = parser.extract(evidence['mupdfWords'], section)
        self.assertEqual(rows[0]['name'], 'ABLENAS, ANDREW')
        self.assertEqual(len(rows), 56)

    def test_rendered_2013_corrections_are_literal_and_fail_if_text_changes(self):
        section, _, evidence = self.evidence('2013', 'employee-remuneration')
        rows = parser.extract(evidence['mupdfWords'], section)
        self.assertEqual(rows[9]['salary'], 10247600)
        self.assertEqual(rows[8]['expenses'], 858900)
        self.assertEqual(rows[8]['position'], 'Deputy CAO/Director of Ops. & Dev. Services')
        self.assertEqual(rows[17]['position'], 'Business Analyst/IT Coordinator')
        altered = copy.deepcopy(section)
        altered['corrections'][0]['before'] = 'a changed source cell'
        with self.assertRaisesRegex(ValueError, 'correction changed'):
            parser.extract(evidence['mupdfWords'], altered)

    def test_removing_a_salary_cell_fails_instead_of_losing_a_row(self):
        section, _, evidence = self.evidence('2020', 'employee-remuneration')
        words = evidence['mupdfWords']
        salary = section['columns']['salary']
        anchor = next(w for w in words if section['y'][0] <= (w[1]+w[3])/2 <= section['y'][1]
                      and salary[0] <= (w[0]+w[2])/2 < salary[1] and w[4] not in ('$', 'S'))
        with self.assertRaisesRegex(ValueError, 'salary anchors'):
            parser.extract([w for w in words if w is not anchor], section)

    def test_reported_source_residual_is_preserved_and_disclosed(self):
        _, source, _ = self.evidence('2022', 'employee-remuneration')
        self.assertEqual(source['validation']['controls'][0]['residual'], -4)
        self.assertIn('unresolved', source['publicWarning'])

    def test_two_parksville_pages_form_one_complete_employee_schedule(self):
        source = next(s for s in self.sources if s['employerSlug'] == 'city-of-parksville' and s['category'] == 'employee-remuneration')
        rows = json.loads(gzip.decompress((parser.OUT / source['file']).read_bytes()))
        self.assertEqual(len(rows), 72)
        self.assertEqual({row[5] for row in rows}, {8, 9})
        self.assertEqual(len([row for row in rows if row[1].startswith('Ross, Sarah')]), 2)
        self.assertEqual(source['totalRemuneration'], 7489244.86)
        self.assertEqual(source['validation']['adoptionEvidence']['resolution'], '26-129')

    def test_expense_inclusive_threshold_and_payroll_variance_do_not_change_revelstoke_pay(self):
        source = next(s for s in self.sources if s['employerSlug'] == 'city-of-revelstoke' and s['category'] == 'employee-remuneration')
        rows = json.loads(gzip.decompress((parser.OUT / source['file']).read_bytes()))
        self.assertEqual(len(rows), 65)
        self.assertTrue(all(row[3] > 75000 for row in rows))
        self.assertEqual(source['totalRemuneration'], 6910239)
        self.assertEqual(source['totalExpenses'], 77888)
        self.assertIn('unresolved', source['publicWarning'])


if __name__ == '__main__':
    unittest.main()
