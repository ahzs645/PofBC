"""Guard preservation against meaningful payment, scope and multiplicity changes."""
import copy
import unittest

import gap_fill_baseline as baseline


class BaselinePreservationTests(unittest.TestCase):
    def setUp(self):
        self.key = ('employer', '2024/25', 'source-one')
        self.rows = [['Smith, A', 'Analyst', 123456.78, None, 12],
                     ['Smith, A', 'Analyst', 123456.78, None, 12],
                     ['Lee, B', None, 80000, 0, 13]]
        self.metadata = {'source-one': {'scope': 'employee-remuneration', 'year': '2024/25',
                                        'publicWarning': 'Expense dashes remain unknown.'}}
        self.before = {'overall': {'records': 3}, 'sourceMetadata': self.metadata,
                       'groups': [{'employerSlug': self.key[0], 'year': self.key[1],
                                   'sourceId': self.key[2], 'rows': 3,
                                   'rowMultisetSha256': baseline.fingerprint(self.rows)}]}

    def verify(self, rows=None, metadata=None):
        return baseline.verify_preserved(self.before,
            {'sources': self.metadata if metadata is None else metadata},
            {self.key: self.rows if rows is None else rows})

    def test_new_sources_do_not_change_prior_payment_evidence(self):
        metadata = {**self.metadata, 'source-two': {'scope': 'school-trustees'}}
        self.assertEqual(self.verify(metadata=metadata), 3)
        self.assertEqual(self.verify(rows=list(reversed(self.rows))), 3)

    def test_duplicate_payment_observations_cannot_disappear(self):
        with self.assertRaises(ValueError):
            self.verify(rows=self.rows[1:])

    def test_pay_expenses_name_title_and_physical_page_are_protected(self):
        for field, value in [(0, 'Smith, Alex'), (1, 'Senior Analyst'), (2, 123456.79),
                             (3, 0), (4, 11)]:
            rows = copy.deepcopy(self.rows)
            rows[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.verify(rows=rows)

    def test_source_scope_period_and_qualifications_are_protected(self):
        for field, value in [('scope', 'executive-only'), ('year', '2023/24'),
                             ('publicWarning', '')]:
            metadata = copy.deepcopy(self.metadata)
            metadata['source-one'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.verify(metadata=metadata)

    def test_boolean_scope_and_nested_qualifications_cannot_become_numbers(self):
        self.metadata['source-one'].update({
            'completeEmployeeSchedule': False,
            'validation': {
                'unknownBenefitsRemainUnknown': True,
                'expenseChecks': [False, {'zeroIsExplicit': True}],
                'explicitZeroExpenseRows': 0,
            },
        })
        self.assertEqual(self.verify(metadata=copy.deepcopy(self.metadata)), 3)
        mutations = [
            (('completeEmployeeSchedule',), 0),
            (('completeEmployeeSchedule',), 0.0),
            (('validation', 'unknownBenefitsRemainUnknown'), 1),
            (('validation', 'expenseChecks', 0), 0),
            (('validation', 'expenseChecks', 1, 'zeroIsExplicit'), 1.0),
            (('validation', 'explicitZeroExpenseRows'), False),
        ]
        for path, value in mutations:
            metadata = copy.deepcopy(self.metadata)
            parent = metadata['source-one']
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = value
            with self.subTest(path=path, value=value), self.assertRaisesRegex(
                    ValueError, 'Earlier source metadata changed'):
                self.verify(metadata=metadata)

    def test_nonmonetary_or_subcent_values_are_rejected(self):
        for value in [True, '80000', float('nan'), float('inf'), 80000.001]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                baseline.exact_cents(value)


if __name__ == '__main__':
    unittest.main()
