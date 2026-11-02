"""Regression checks tied to actual school extraction/review failure cases."""
import gzip
import hashlib
import json
import unittest
from decimal import Decimal
from pathlib import Path

import finish_salary_schools_native as native
import finish_salary_schools_scan as scan

ROOT = Path(__file__).resolve().parents[1]
AREA = native.AREA
COLLECTION = native.COLLECTION


def read_gzip(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def native_proof(number):
    revised = AREA/f'sd{number:02}-2025-native-candidate-v2.json.gzip'
    if revised.exists():
        return read_gzip(revised)
    return read_gzip(AREA/f'sd{number:02}-2025-native-candidate.json.gzip')


class SchoolCompletionChecks(unittest.TestCase):
    def test_every_complete_native_scope_replays_from_original_poppler_text(self):
        for number in [22, 23, 27, 33, 36, 43, 44, 61, 68, 73]:
            proof = native_proof(number)
            rows, _ = native.poppler_rows(proof['popplerText'], proof['config'])
            for amendment in proof.get('imageVerifiedReaderAmendments', []):
                if amendment['reader'] == 'poppler':
                    row = rows[amendment['sequence']-1]
                    self.assertEqual(row[amendment['field']], amendment['before'])
                    row[amendment['field']] = amendment['after']
            self.assertEqual([native.fields(r) for r in rows], [native.fields(r) for r in proof['popplerRows']])
            self.assertEqual([native.fields(r) for r in rows], [native.fields(r) for r in proof['mupdfRows']])

    def test_low_paid_elected_person_is_not_lost_by_employee_threshold(self):
        row = next(r for r in native_proof(27)['popplerRows'] if r['name'] == 'COATES MELISSA')
        self.assertEqual((row['category'], row['remuneration'], row['expenses']), ('school-trustees', '638', '1739'))

    def test_all_four_leading_footnote_staff_remain_named_observations(self):
        rows = native_proof(73)['popplerRows']
        starred = [r for r in rows if r['name'].startswith('*')]
        self.assertEqual([r['name'] for r in starred], ['**** ARMSTRONG, DAWN', '*** BREWER, TREVOR', '** ENGLESON, KRISTIN', '* MACPHERSON, LAUREL H'])
        self.assertEqual(sum(r['category'] == 'employee-remuneration' for r in rows), 1067)

    def test_negative_expense_currency_is_not_a_dash_or_absolute_value(self):
        row = next(r for r in native_proof(73)['popplerRows'] if r['name'] == 'CASSIDY, TRINA M')
        self.assertEqual(row['expenses'], '-590')
        self.assertEqual(native.amount('-$ 590'), '-590')
        self.assertIsNone(native.amount('$ -'))
        self.assertEqual(native.amount('$ 0'), '0')

    def test_reordered_surrey_position_column_is_kept_after_money(self):
        proof = native_proof(36)
        first = next(r for r in proof['popplerRows'] if r['category'] == 'employee-remuneration')
        self.assertEqual(native.fields(first), ["A'BEAR, DAVID BRIAN", 'ADMINISTRATOR', '174134', '13652', 58, 'employee-remuneration'])
        self.assertEqual(len(proof['popplerRows']), 4830)

    def test_expense_only_tax_authority_is_not_imported_as_employee(self):
        proof = native_proof(23)
        self.assertIn('Canada Revenue Agency', proof['popplerText'])
        self.assertFalse(any('Canada Revenue Agency' in r['name'] for r in proof['popplerRows']))
        self.assertEqual(proof['summaries']['employee-remuneration']['rows'], 1626)

    def test_clipped_name_title_boundary_preserves_both_raw_and_image_amended_fields(self):
        proof = native_proof(61)
        self.assertEqual(proof['rawMupdfRowsBeforeImageAmendments'][488]['name'], 'GUERRERO HERNANDEZ, CUAUHTEINFORMATION')
        row = proof['mupdfRows'][488]
        self.assertEqual(row['name'], 'GUERRERO HERNANDEZ, CUAUHTE')
        self.assertEqual(row['position'], 'INFORMATION SYSTEMS - SERVER ADMINISTRATOR')
        self.assertEqual(len([a for a in proof['imageVerifiedReaderAmendments'] if a['reader'] == 'mupdf' and a['sequence'] == 489]), 2)

    def test_shared_ocr_capital_i_error_is_explicit_and_old_bytes_unchanged(self):
        old = COLLECTION/'sd50-2025-employees.json.gzip'
        new = COLLECTION/'sd50-2025-employees-v2.json.gzip'
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(), '8ef567c55c22e061658f7eaca221edba46f73277d4aa2f2dfc139c88ef6ef161')
        before, after = read_gzip(old), read_gzip(new)
        changed = [(a, b) for a, b in zip(before, after) if a != b]
        self.assertEqual(len(changed), 1)
        self.assertEqual((changed[0][0][1], changed[0][1][1]), ('Keir, lan J.', 'Keir, Ian J.'))
        self.assertEqual(changed[0][0][2:], changed[0][1][2:])

    def test_every_actual_sd61_footer_is_separate_from_employee_position(self):
        ledger_path = ROOT/'research/salaries/queue-completion-2026-11-01/reviews/independent-school-extension-acquisition-sd61-footer-correction-ledger.json'
        ledger = json.loads(ledger_path.read_text())
        original_path = COLLECTION/'sd61-2025-employees.json.gzip'
        self.assertEqual(hashlib.sha256(original_path.read_bytes()).hexdigest(), 'd113332f757cc735cd5eb78d6d0c5c43132e629981f9e05e303386ab900415bc')
        old = read_gzip(original_path)
        new = read_gzip(COLLECTION/'sd61-2025-employees-v2.json.gzip')
        self.assertEqual(len(ledger['corrections']), 20)
        self.assertEqual(sum(a != b for a,b in zip(old,new)), 20)
        for correction in ledger['corrections']:
            index = correction['employeeIndexZeroBased']
            self.assertEqual(old[index], correction['beforeRow'])
            self.assertEqual(new[index], correction['afterRow'])
            self.assertEqual(new[index][2], 'TEACHER')
            self.assertEqual(new[index][:2]+new[index][3:], old[index][:2]+old[index][3:])

    def test_undetected_ocr_cell_stays_unresolved_until_source_dash_review(self):
        self.assertEqual(scan.cash('S'), 'UNRESOLVED:S')
        raw = read_gzip(AREA/'sd50-2025-both-reader-fields.json.gzip')
        self.assertTrue(raw['paddleRows'][21]['expenses'].startswith('UNRESOLVED:'))
        final = read_gzip(AREA/'sd50-2025-image-checked-candidate-v2.json.gzip')
        self.assertIsNone(final['paddleRows'][21]['expenses'])
        dash_amendments = [a for a in final['imageVerifiedAmendments'] if a['field'] == 'expenses']
        self.assertEqual(len(dash_amendments), 8)

    def test_manifest_rows_precision_period_and_compiled_partitions(self):
        manifest = json.loads((COLLECTION/'sources.json').read_text())
        self.assertEqual(len(manifest['sources']), 22)
        self.assertEqual(sum(s['rowCount'] for s in manifest['sources']), 15138)
        keys = set()
        for source in manifest['sources']:
            key = (source['employerSlug'], source['year'], source['category'])
            self.assertNotIn(key, keys)
            keys.add(key)
            self.assertTrue(source['retainCompiledPartition'])
            self.assertTrue(source['publicWarning'])
            self.assertTrue(source['validation']['compiledPartitionRetained'])
            self.assertTrue(source['validation']['compiledPartitionRetentionReason'])
            self.assertEqual(source['validation']['completeEmployeeSchedule'], source['completeEmployeeSchedule'])
            self.assertEqual((source['periodType'], source['periodStart'], source['periodEnd']), ('fiscal', '2024-07-01', '2025-06-30'))
            data_path = COLLECTION/source['file']
            self.assertEqual(hashlib.sha256(data_path.read_bytes()).hexdigest(), source['dataSha256'])
            rows = read_gzip(data_path)
            self.assertEqual(len(rows), source['rowCount'])
            self.assertTrue(all(len(row) == 6 for row in rows))
            evidence = read_gzip(COLLECTION/source['provenanceFile'])
            for row, original in zip(rows, evidence['readerOneFields']):
                self.assertEqual(row[0], source['employerSlug'])
                self.assertEqual(row[1:3], original[:2])
                self.assertEqual(Decimal(str(row[3])), Decimal(original[2]))
                self.assertEqual(row[4] is None, original[3] is None)
                if row[4] is not None:
                    self.assertEqual(Decimal(str(row[4])), Decimal(original[3]))
                self.assertEqual((row[5], source['category']), (original[4], original[5]))
            if source['id'] in ['queue-completion-schools-sd61-2025-employees', 'queue-completion-schools-sd50-2025-employees']:
                self.assertTrue(source['file'].endswith('-employees-v2.json.gzip'))
            for field, index in [('totalRemuneration', 3), ('totalExpenses', 4)]:
                total = sum((Decimal(str(row[index])) for row in rows if row[index] is not None), Decimal(0))
                self.assertEqual(total, Decimal(str(source[field])))
        existing = set()
        for collection in json.loads((ROOT/'research/salaries/collections.json').read_text())['collections']:
            if collection == 'queue-completion-schools':
                continue
            for source in json.loads((ROOT/'research/salaries'/collection/'sources.json').read_text())['sources']:
                if source.get('sector') == 'School districts':
                    existing.add((source['employerSlug'], source['year'], source['category']))
        self.assertFalse(keys & existing, 'Already registered named cohort duplicated')


if __name__ == '__main__':
    unittest.main()
