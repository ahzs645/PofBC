"""Preserve literal observations when resolving held source schedules."""
import importlib.util
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('held_review', Path(__file__).with_name('review-salary-held-resolution.py'))
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class HeldResolutionPreservationTests(unittest.TestCase):
    def setUp(self):
        self.key = ('example', '2024/25', 'official-example')
        self.rows = [['Surname, J', None, 75000.25, None, 5],
                     ['Surname, J', None, 75000.25, None, 5]]
        self.before = {'rows': 2, 'groups': [{'employerSlug': self.key[0],
            'year': self.key[1], 'sourceId': self.key[2], 'rows': 2,
            'rowMultisetSha256': REVIEW.fingerprint(self.rows)}]}

    def test_new_cohorts_and_order_do_not_change_previous_rows(self):
        groups = {self.key: list(reversed(self.rows)),
                  ('other', '2025', 'new-source'): [['Other', None, 90000, 0, 1]]}
        self.assertEqual(REVIEW.verify_baseline(self.before, groups), 2)

    def test_repeated_rows_cannot_be_collapsed(self):
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {self.key: self.rows[:1]})

    def test_unknown_expenses_cannot_become_zero(self):
        changed = [list(row) for row in self.rows]
        changed[0][3] = 0
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {self.key: changed})

    def test_reporting_period_cannot_be_inferred_from_later_package(self):
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {('example', '2025/26', self.key[2]): self.rows})

    def test_painted_name_and_physical_page_stay_literal(self):
        for field, value in [(0, 'Surname, John'), (1, 'Hidden job title'), (4, 6)]:
            changed = [list(row) for row in self.rows]
            changed[0][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                REVIEW.verify_baseline(self.before, {self.key: changed})


class RequiredReviewCoverageTests(unittest.TestCase):
    def setUp(self):
        self.acceptance = {'candidateFreezeSha256': {area: 'a' * 64 for area in REVIEW.AREAS},
            'reviewReceiptSha256': {'reviews/independent-source.json': 'b' * 64},
            'sourceReviewReceipts': {'new-source': ['reviews/independent-source.json']}}

    def test_explicit_independent_coverage_is_accepted(self):
        REVIEW.verify_review_coverage(self.acceptance, ['new-source'])

    def test_empty_or_incomplete_worker_freezes_cannot_disable_gate(self):
        for areas in [{}, {'education': 'a' * 64}]:
            value = copy.deepcopy(self.acceptance)
            value['candidateFreezeSha256'] = areas
            with self.subTest(areas=areas), self.assertRaises(AssertionError):
                REVIEW.verify_review_coverage(value, ['new-source'])

    def test_each_new_source_requires_a_pinned_independent_receipt(self):
        for field, change in [('reviewReceiptSha256', {}), ('sourceReviewReceipts', {}),
                              ('sourceReviewReceipts', {'new-source': []}),
                              ('sourceReviewReceipts', {'new-source': ['reviews/unpinned.json']})]:
            value = copy.deepcopy(self.acceptance)
            value[field] = change
            with self.subTest(field=field, change=change), self.assertRaises(AssertionError):
                REVIEW.verify_review_coverage(value, ['new-source'])

    def test_unrelated_peer_receipt_cannot_cover_an_added_source_implicitly(self):
        with self.assertRaises(AssertionError):
            REVIEW.verify_review_coverage(self.acceptance, ['new-source', 'another-source'])


class FrozenHeldResolutionTests(unittest.TestCase):
    def check_index_change(self, change):
        original = REVIEW.read
        def read(path):
            value = original(path)
            if Path(path).as_posix().endswith('public/salaries/employers/index.json'):
                value = copy.deepcopy(value)
                change(value)
            return value
        with patch.object(REVIEW, 'read', side_effect=read):
            return REVIEW.validate_frozen_resolution()

    def test_later_unrelated_totals_do_not_rewrite_pr36(self):
        path = REVIEW.OUT / 'release.json'
        before = path.read_bytes()
        result = self.check_index_change(lambda value: value.update(recordCounts={'official': 9999999, 'compiled': 0}))
        self.assertEqual(result['records'], 1037040)
        self.assertEqual(result['sourceInputsVerified'], 6)
        self.assertEqual(path.read_bytes(), before)

    def test_qualified_declaration_warning_cannot_disappear(self):
        def change(value):
            value['sources']['held-resolution-schools-sd10-2025-employees']['publicWarning'] = None
        with self.assertRaises(AssertionError):
            self.check_index_change(change)

    def test_verified_reporting_period_cannot_drift(self):
        def change(value):
            value['sources']['held-resolution-phsa-2024-25-employees']['periodEnd'] = '2024-03-31'
        with self.assertRaises(AssertionError):
            self.check_index_change(change)

    def test_employee_scope_cannot_become_aggregate(self):
        def change(value):
            value['sources']['held-resolution-phsa-2024-25-employees']['scope'] = 'aggregate-only'
        with self.assertRaises(AssertionError):
            self.check_index_change(change)

    def test_one_published_source_row_cannot_disappear(self):
        original = REVIEW.decode
        def decode(raw):
            rows = original(raw)
            if rows and len(rows[0]) == 7:
                for index, row in enumerate(rows):
                    if row[5] == 'held-resolution-phsa-2024-25-employees':
                        return rows[:index] + rows[index + 1:]
            return rows
        with patch.object(REVIEW, 'decode', side_effect=decode), self.assertRaises(AssertionError):
            REVIEW.validate_frozen_resolution()


if __name__ == '__main__':
    unittest.main()
