#!/usr/bin/env python3
"""Regressions for actual source risks in northern municipal history."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest
import parse_history_north as parser

ROOT = Path(__file__).resolve().parents[1]
COL = ROOT / 'research/salaries/municipal-history-north'
SOURCES = json.loads((COL / 'sources.json').read_text())['sources']
SOURCE = {s['year'] + ':' + s['employerSlug']: s for s in SOURCES}


def rows(key):
    return json.loads(gzip.decompress((COL / (key + '.json.gzip')).read_bytes()))


def evidence(key):
    return json.loads(gzip.decompress((COL / 'evidence' / (key + '.json.gzip')).read_bytes()))['rows']


class HistoricalNorthTests(unittest.TestCase):
    def test_blank_dash_zero_negative_are_distinct(self):
        self.assertIsNone(parser.money(''))
        self.assertIsNone(parser.money('-'))
        self.assertEqual(parser.money('$0'), 0)
        self.assertEqual(parser.money('(1,234.56)'), -123456)
        self.assertEqual(parser.money('-5.25'), -525)
        with self.assertRaises(ValueError):
            parser.money('&96,018')

    def test_text_preserves_initials_and_currency_geometry_fails(self):
        self.assertEqual(parser.join([[0, 0, 5, 5, 'A'], [6, 0, 10, 5, '$']]), 'A $')
        section = {'page': 1, 'y': [0, 10], 'rowCount': 1,
                   'columns': {'name': [0, 20], 'position': [20, 50], 'pay': [50, 100]}}
        words = [[1, 1, 5, 6, 'A'], [25, 1, 30, 6, '$'], [60, 1, 80, 6, '75001']]
        with self.assertRaisesRegex(ValueError, 'non-person text'):
            parser.extract(words, section)

    def test_unnamed_positions_are_truthful_nulls(self):
        count = 0
        for year in ('2012', '2013', '2014'):
            source = SOURCE[year + ':city-of-williams-lake']
            cohort = rows('williams-lake-' + year)
            self.assertEqual(source['nameDisclosure'], 'not-published')
            self.assertTrue(all(r[1] is None and r[2] for r in cohort))
            self.assertIn('without employee names', source['publicWarning'])
            self.assertTrue(source['completeEmployeeSchedule'])
            count += len(cohort)
        self.assertEqual(count, 71)

    def test_actual_A_initials_are_preserved(self):
        self.assertIn('Cail, A', [r[1] for r in rows('williams-lake-2020')])
        self.assertIn('Ginter, A', [r[1] for r in rows('dawson-creek-2022')])
        self.assertIn('Iskender, A', [r[1] for r in rows('dawson-creek-2023')])

    def test_chetwynd_wrapped_titles_do_not_move_to_adjacent_employee(self):
        old = {r[1]: r[2] for r in rows('chetwynd-2018')}
        self.assertEqual(old['McAvany, Ellen'], 'Economic Development Officer & Parks Manager')
        self.assertEqual(old['Ennis, Deanne'], 'Deputy Director of Corporate Administration & HR Manager')
        new = {r[1]: r[2] for r in rows('chetwynd-2019')}
        self.assertEqual(new['Adams, Alex'], 'Director of Public Works & Engineering')
        self.assertEqual(new['Adams, Lorraine'], 'Maintenance Water/Sewer II')
        for year in ('2018', '2019'):
            self.assertIsNone(SOURCE[year + ':district-of-chetwynd']['thresholdComparison'])

    def test_dawson_2017_title_above_pay_anchor_stays_with_henderson(self):
        positions = {r[1]: r[2] for r in rows('dawson-creek-2017')}
        self.assertEqual(positions['Gower, Brooks'], 'Fire Fighter')
        self.assertEqual(positions['Henderson, Kevin'], 'General Manager of Infrastructure and Development Services')
        self.assertEqual(positions['Nilsen, Peter'], 'Energy Manager')
        self.assertEqual(positions['Fisher, Cindy'], 'Deputy Director of Corporate Administration')

    def test_nrrm_department_is_not_a_position_and_blank_is_not_zero(self):
        for source in SOURCES:
            if source['employerSlug'] == 'northern-rockies-regional-municipality':
                self.assertTrue(all(r[2] is None for r in rows(source['file'].removesuffix('.json.gzip'))))
                self.assertTrue(all(r.get('department') for r in evidence(source['file'].removesuffix('.json.gzip'))))
        exp2020 = [r[4] for r in rows('nrrm-2020')]
        exp2021 = [r[4] for r in rows('nrrm-2021')]
        self.assertIn(None, exp2020)
        self.assertNotIn(0, exp2020)
        self.assertIn(0, exp2021)

    def test_williams_lake_reviewed_ocr_artifact_only(self):
        hutton = next(r for r in rows('williams-lake-2015') if r[1] == 'Hutton, C.')
        self.assertEqual(hutton[2], 'Planner 1')
        self.assertEqual(hutton[3], 74077)

    def test_williams_lake_2019_keeps_all_33_and_scopes_expenses(self):
        cohort = rows('williams-lake-2019')
        source = SOURCE['2019:city-of-williams-lake']
        self.assertEqual(len(cohort), 33)
        self.assertEqual(cohort[0][3], 83235)
        self.assertEqual(sum(r[3] for r in cohort), 3153276)
        self.assertEqual(source['validation']['printedControls'][0]['residual'], 83235)
        broader = source['validation']['broaderControlComparisons'][0]
        self.assertEqual(broader['knownDisclosedCohortSum'], 100858)
        self.assertEqual(broader['printedAllEmployeeControl'], 100855)
        self.assertEqual(broader['difference'], 3)
        self.assertIsNone(broader['underThresholdComponent'])
        self.assertFalse(source['validation']['namedExpenseControlAvailable'])
        self.assertIn('cause remains unknown', source['publicWarning'])

    def test_blank_under_threshold_does_not_create_named_expense_control(self):
        for year in range(2015, 2024):
            source = SOURCE[str(year) + ':city-of-williams-lake']
            self.assertNotIn('expenses', [c['field'] for c in source['validation']['printedControls']])
            self.assertFalse(source['validation']['namedExpenseControlAvailable'])
            self.assertIsNone(source['validation']['broaderControlComparisons'][0]['underThresholdComponent'])
            self.assertIn('no named-only reconciliation', source['publicWarning'])

    def test_manifest_hashes_scope_money_and_unique_periods(self):
        self.assertEqual(len(SOURCES), 28)
        self.assertEqual(sum(s['rowCount'] for s in SOURCES), 1121)
        self.assertEqual(len({(s['employerSlug'], s['year'], s['category']) for s in SOURCES}), len(SOURCES))
        for source in SOURCES:
            data = (COL / source['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['dataSha256'])
            normalized = json.loads(gzip.decompress(data))
            self.assertEqual(len(normalized), source['rowCount'])
            self.assertAlmostEqual(sum(r[3] for r in normalized), source['totalRemuneration'], places=5)
            self.assertTrue(source['validation']['completeEmployeeSchedule'])
            self.assertTrue(all('$' not in (r[1] or '') + (r[2] or '') for r in normalized))
            evidence_path = COL / source['validation']['evidenceFile']
            self.assertEqual(hashlib.sha256(evidence_path.read_bytes()).hexdigest(), source['validation']['evidenceSha256'])

    def test_explicit_old_scope_amendment_preserves_frozen_binaries(self):
        archive = ROOT / 'research/salaries/municipal-history-pass/corrections/north-expense-scope/pr27-original/archive-manifest.json'
        manifest = json.loads(archive.read_text())
        for path, sha in manifest['frozenBinaryHashes'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), sha)
        old = json.loads((ROOT / 'research/salaries/municipal-wave-north/sources.json').read_text())['sources']
        for source in old:
            if source['employerSlug'] == 'city-of-williams-lake':
                self.assertFalse(source['validation']['namedExpenseControlAvailable'])
                self.assertNotIn('expenses', [c['field'] for c in source['validation']['printedControls']])
                self.assertIsNone(source['validation']['broaderControlComparisons'][0]['underThresholdExpenses'])

    def test_small_village_supplement_keeps_accents_and_expense_total_separate(self):
        directory = COL / 'supplemental'
        sources = json.loads((directory / 'sources.json').read_text())['sources']
        self.assertEqual(sum(s['rowCount'] for s in sources), 3)
        self.assertEqual(len(sources), 2)
        cohorts = {s['employerSlug']: json.loads(gzip.decompress((directory / s['file']).read_bytes())) for s in sources}
        self.assertEqual(cohorts['village-of-hazelton'][0][1:5], ['Robyn Carlé', 'CAO', 79320.57, 554.6])
        self.assertEqual(cohorts['village-of-port-clements'][0][1:5], ['Dobson, Marjorie', None, 95500.1, 774.96])
        detail = json.loads(gzip.decompress((directory / 'evidence/port-clements-2025.json.gzip').read_bytes()))['rows'][0]
        self.assertEqual(detail['printedTotal'], 9627506)
        self.assertNotEqual(detail['pay'], detail['printedTotal'])
        for source in sources:
            self.assertTrue(all(c['residual'] == 0 for c in source['validation']['printedControls']))

    def test_council_supplement_preserves_actual_scope_and_unnamed_labels(self):
        directory = COL / 'council'
        sources = json.loads((directory / 'sources.json').read_text())['sources']
        self.assertEqual(len(sources), 30)
        self.assertEqual(sum(s['rowCount'] for s in sources), 225)
        unnamed = []
        for source in sources:
            self.assertEqual(source['category'], 'elected-officials')
            self.assertIsNone(source['threshold'])
            self.assertNotIn('completeEmployeeSchedule', source)
            self.assertNotIn('completeEmployeeSchedule', source['validation'])
            self.assertTrue(source['completeCouncilSchedule'])
            cohort = json.loads(gzip.decompress((directory / source['file']).read_bytes()))
            if source['nameDisclosure'] == 'not-published':
                unnamed.extend(cohort)
                self.assertTrue(all(r[1] is None and r[2] for r in cohort))
        self.assertEqual(len(unnamed), 21)
        self.assertIn('Councillor Bonnell', [r[2] for r in unnamed])
        wl2015 = json.loads(gzip.decompress((directory / 'williams-lake-2015-council.json.gzip').read_bytes()))
        self.assertEqual(wl2015[1][1], 'Bonnell, I.')
        wl2011 = json.loads(gzip.decompress((directory / 'williams-lake-2011-council.json.gzip').read_bytes()))
        self.assertEqual(wl2011[5][1], 'Natlie Lynn Montoya')
        hazelton = next(s for s in sources if s['employerSlug'] == 'village-of-hazelton')
        self.assertEqual(hazelton['validation']['printedControls'][1]['residual'], 0.1)


if __name__ == '__main__':
    unittest.main()
