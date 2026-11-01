"""Preserve literal observations when resolving held source schedules."""
import importlib.util
import copy
from pathlib import Path
import unittest

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


if __name__ == '__main__':
    unittest.main()
