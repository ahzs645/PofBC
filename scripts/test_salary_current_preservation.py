"""Adversarial tests for the additive release's immutable multiset contract."""
import copy
import unittest
from pathlib import Path
from check_salary_current_preservation import row_groups, inverse_corrections, read, observation, correction_link_context, verify_link_preservation, apply_confidence_withdrawals, group_hash, row_hash, BASELINE_COMMIT


class CurrentPreservationTests(unittest.TestCase):
    def setUp(self):
        self.row = observation('employer', '2024', 'Name, A', None, 100000.01, None, 'compiled', 5)

    def test_order_independent_but_duplicates_are_preserved(self):
        other = tuple([*self.row[:2], 'Name, B', *self.row[3:]])
        self.assertEqual(row_groups([self.row, other, self.row]), row_groups([other, self.row, self.row]))
        self.assertNotEqual(row_groups([self.row, other]), row_groups([self.row, other, self.row]))
        self.assertNotEqual(row_groups([self.row]), row_groups([]))

    def test_every_original_observation_field_is_pinned(self):
        for at, replacement in enumerate(['other', '2025', None, 'Manager', 10000002, 0, 'official', 6]):
            changed = list(self.row); changed[at] = replacement
            with self.subTest(field=at):
                self.assertNotEqual(row_groups([self.row]), row_groups([changed]))

    def test_exact_cent_money_rejects_fractional_cents(self):
        with self.assertRaisesRegex(ValueError, 'exact cents'):
            observation('a', '2024', None, None, 0.001, None, 's', None)


    def test_name_graph_normalization_is_limited_to_exact_audited_splits(self):
        corrections = [{'employerSlug': 'e', 'sourcePrefix': 'Name, Ada   Analyst', 'name': 'Name, Ada'}]
        groups = [['e', 'name|ada', 'Name, Ada', [['name|ada analyst', 'Name, Ada   Analyst', 'verified', []], ['name|a', 'Name, A', 'likely', []]]]]
        transformed = correction_link_context(groups, corrections)
        self.assertEqual(len(transformed[0][3]), 1)
        self.assertEqual(transformed[0][3][0][0], 'name|a')
        with self.assertRaisesRegex(ValueError, 'disappeared'):
            verify_link_preservation(transformed, [])
        self.assertEqual(verify_link_preservation(transformed, [['e', 'name|ada', 'Name, Ada', [['name|a', 'Name, A', 'likely', []]]]])['preservedNameRelationships'], 1)


    def test_confidence_withdrawals_reject_extra_transitions_and_changed_evidence(self):
        identities = [('vancouver-police', 'palmer|a a', 'palmer|a'), ('district-of-west-vancouver', 'stuart|sharon', 'stuart|s')]
        groups, live, decisions, rows = [], [], [], []
        for employer, target, alias in identities:
            row = (employer, *self.row[1:]);rows.append(row)
            pin = {'rows': 1, 'sha256': group_hash([row_hash(row)])}
            groups.append([employer, target, 'Target', [[alias, 'Alias', 'verified', 'Prior heuristic']]])
            live.append([employer, target, 'Target', [[alias, 'Alias', 'likely', 'Qualified uncertainty']]])
            decisions.append({'employer': employer, 'targetKey': target, 'aliasKey': alias,
                              'previousStatus': 'verified', 'currentStatus': 'likely',
                              'previousReason': 'Prior heuristic', 'currentReason': 'Qualified uncertainty',
                              'basis': 'automatic-distinctive-position-heuristic-only',
                              'originalEmployerObservations': pin, 'currentEmployerObservations': pin})
        receipt = {'scope': 'exactly-two-automatic-confidence-withdrawals', 'baselineCommit': BASELINE_COMMIT,
                   'sourceBackedReceiptsChanged': False, 'decisions': decisions}
        self.assertEqual(verify_link_preservation(apply_confidence_withdrawals(groups, live, receipt, rows, rows), live)['preservedNameRelationships'], 2)
        extra = copy.deepcopy(receipt);extra['decisions'].append(copy.deepcopy(decisions[0]))
        with self.assertRaisesRegex(ValueError, 'scope'):
            apply_confidence_withdrawals(groups, live, extra, rows, rows)
        modified = copy.deepcopy(rows);modified[0] = (*rows[0][:4], 99, *rows[0][5:])
        with self.assertRaisesRegex(ValueError, 'observation evidence'):
            apply_confidence_withdrawals(groups, live, receipt, rows, modified)
        modified_live = copy.deepcopy(live);modified_live[0][3][0][3] = 'Different rationale'
        with self.assertRaisesRegex(ValueError, 'graph evidence'):
            apply_confidence_withdrawals(groups, modified_live, receipt, rows, rows)
        groups.append(['unrelated', 'a|b', 'B', [['a|c', 'C', 'verified', 'Must retain']]])
        qualified = apply_confidence_withdrawals(groups, live, receipt, rows, rows)
        with self.assertRaisesRegex(ValueError, 'disappeared'):
            verify_link_preservation(qualified, live)

    def fixture(self):
        corrections = read(Path(__file__).resolve().parents[1] / 'research/salaries/west-vancouver-title-recovery/corrections.json')
        rows = [observation(c['employerSlug'], c['year'], c['name'], c['position'], c['remuneration'], c['expenses'], c['sourceId'], c['page']) for c in corrections]
        return corrections, rows

    def test_inverse_changes_only_the_two_audited_text_fields(self):
        corrections, rows = self.fixture()
        restored = list(inverse_corrections([self.row, *rows], corrections))
        self.assertEqual(restored[0], self.row)
        for actual, original, correction in zip(restored[1:], rows, corrections):
            self.assertEqual(actual[:2], original[:2])
            self.assertEqual(actual[4:], original[4:])
            self.assertEqual(actual[2:4], (correction['sourcePrefix'], None))

    def test_inverse_rejects_missing_duplicate_and_unaudited_rows(self):
        corrections, rows = self.fixture()
        for modified in [rows[:-1], [*rows, rows[0]]]:
            with self.assertRaises(ValueError):list(inverse_corrections(modified, corrections))
        for at, replacement in enumerate(['other', '2025', 'New name', 'New title', 99, 0, 'other-source', 999]):
            modified = copy.deepcopy(rows)
            changed = list(modified[0]);changed[at] = replacement;modified[0] = tuple(changed)
            with self.subTest(field=at), self.assertRaises(ValueError):
                list(inverse_corrections(modified, corrections))
        with self.assertRaises(ValueError):list(inverse_corrections(rows, corrections[:-1]))


if __name__ == '__main__':unittest.main()
