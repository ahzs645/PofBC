#!/usr/bin/env python3
"""Offline regression checks for the reviewed northern/Interior salary collection."""
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('north', ROOT / 'scripts/parse_municipal_north.py')
north = importlib.util.module_from_spec(spec)
spec.loader.exec_module(north)
COLLECTION = ROOT / 'research/salaries/municipal-north'


class ExtractionGuards(unittest.TestCase):
    def test_missing_zero_negative_and_cents_are_distinct(self):
        self.assertIsNone(north.amount('-'))
        self.assertIsNone(north.amount(''))
        self.assertEqual(north.amount('0'), 0)
        self.assertEqual(north.amount('(1,091.79)'), -109179)
        self.assertEqual(north.amount('27,539,267.16'), 2753926716)

    def test_duplicate_rows_cannot_disappear_in_independent_check(self):
        row = ['Example, A', None, 8000000, None, 1]
        with self.assertRaisesRegex(ValueError, 'Independent readers disagree'):
            north.compare([row, row], [row])

    def test_table_boundary_benefit_columns_and_below_threshold_row(self):
        text = '''For the year ended December 31, 2025
Name              Position       Remuneration  Benefits  Total Income  Expenses
Example, A        Analyst        80,000.00     500.00    80,500.00     0.00
Example, B        Clerk          74,000.00     1,500.00  75,500.00     -
Named subtotal                   154,000.00    2,000.00  156,000.00    0.00
Suppliers
Vendor, Inc.      Contractor     999,000.00    0.00      999,000.00    0.00
'''
        entry = {'year': '2025', 'cohorts': {'employees': {
            'pages': [1], 'columns': 4, 'controlRegex': '^Named subtotal',
            'rowSum': {'parts': [0, 1], 'total': 2}}}}
        with patch.object(north, 'read_layout', return_value=[text]), patch.object(north, 'verify_single_lines', return_value=[]):
            _, rows, components, review = north.parse_tables(Path('fixture.pdf'), entry)[0]
            self.assertEqual(len(rows), 2)
            self.assertEqual([r[2] for r in rows], [8000000, 7400000])
            self.assertEqual([r[3] for r in rows], [0, None])
            self.assertEqual(components[1][2], 7550000)
            self.assertTrue(review['allComponentSubtotalsExact'])
            with patch.object(north, 'read_layout', return_value=[text.replace('154,000.00', '154,001.00')]):
                with self.assertRaisesRegex(ValueError, 'subtotal mismatch'):
                    north.parse_tables(Path('fixture.pdf'), entry)
            with patch.object(north, 'read_layout', return_value=[text.replace('December 31, 2025', 'December 31, 2024')]):
                with self.assertRaisesRegex(ValueError, 'reporting period'):
                    north.parse_tables(Path('fixture.pdf'), entry)


class AcceptedFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((COLLECTION / 'sources.json').read_text())
        cls.inputs = json.loads((COLLECTION / 'reviewed-inputs.json').read_text())

    def test_hashes_counts_calendar_periods_and_audit_component_selection(self):
        entries = {(e['shortSlug'], e['year']): e for e in self.inputs['sources']}
        self.assertEqual(len(self.manifest['sources']), 30)
        self.assertEqual(sum(s['rowCount'] for s in self.manifest['sources']), 8806)
        for source in self.manifest['sources']:
            with self.subTest(source=source['id']):
                raw = (COLLECTION / source['file']).read_bytes()
                data = gzip.decompress(raw)
                rows = json.loads(data)
                auditraw = (COLLECTION / source['componentAuditFile']).read_bytes()
                audit = json.loads(gzip.decompress(auditraw))
                self.assertEqual(north.digest(raw), source['dataSha256'])
                self.assertEqual(north.digest(data), source['normalizedSha256'])
                self.assertEqual(north.digest(auditraw), source['componentAuditSha256'])
                self.assertEqual(len(rows), source['rowCount'])
                self.assertEqual(len(rows), len(audit['rows']))
                self.assertEqual(source['periodType'], 'calendar')
                self.assertEqual(source['periodStart'], source['year'] + '-01-01')
                self.assertEqual(source['periodEnd'], source['year'] + '-12-31')
                self.assertEqual(source['validation']['rowsIndependentlyChecked'], len(rows))
                entry = entries[(source['id'].split('-sofi-')[0], source['year'])]
                category = 'employees' if source['category'] == 'employee-remuneration' else 'elected-officials'
                if entry['parser'] == 'tables':
                    recipe = entry['cohorts'][category]
                    payindex = recipe.get('payIndex', 0)
                    expenseindex = recipe.get('expenseIndex', recipe['columns'] - 1)
                elif entry['parser'] in ('kamloops', 'fort-st-john'):
                    payindex, expenseindex = 0, 1 if entry['parser'] == 'fort-st-john' else -1
                else:
                    payindex, expenseindex = (None, 2) if category == 'employees' else (2, 3)
                for row, item in zip(rows, audit['rows']):
                    components = item['componentsCents']
                    expectedpay = sum(c or 0 for c in components[:2]) if payindex is None else components[payindex]
                    expectedexpense = components[expenseindex]
                    self.assertEqual(row[0], source['employerSlug'])
                    self.assertEqual(row[1:3], [item['name'], item['position']])
                    self.assertEqual(row[3], expectedpay / 100)
                    self.assertEqual(row[4], None if expectedexpense is None else expectedexpense / 100)
                    self.assertEqual(row[5], item['physicalPdfPage'])
                self.assertAlmostEqual(sum(row[3] for row in rows), source['totalRemuneration'], places=5)
                self.assertAlmostEqual(sum(row[4] or 0 for row in rows), source['totalExpenses'], places=5)

    def test_published_negative_expenses_and_low_remuneration_are_retained(self):
        byid = {s['id']: s for s in self.manifest['sources']}
        for sourceid, count in [('kamloops-sofi-2017-employees', 40), ('quesnel-sofi-2025-employees', 6)]:
            source = byid[sourceid]
            rows = json.loads(gzip.decompress((COLLECTION / source['file']).read_bytes()))
            self.assertEqual(sum(row[3] <= 75000 for row in rows), count)
        council = byid['penticton-sofi-2025-elected-officials']
        rows = json.loads(gzip.decompress((COLLECTION / council['file']).read_bytes()))
        self.assertEqual(next(r for r in rows if r[1] == 'Miller, James')[4], -206)
        employee = byid['penticton-sofi-2025-employees']
        rows = json.loads(gzip.decompress((COLLECTION / employee['file']).read_bytes()))
        self.assertEqual(next(r for r in rows if r[1] == 'Taylor, Chad')[4], -1091.79)


if __name__ == '__main__':
    unittest.main()
