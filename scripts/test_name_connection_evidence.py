import unittest

from review_name_connection_evidence import exact_witnesses, row_fingerprint, signature


class NameConnectionEvidenceTests(unittest.TestCase):
    years = ['2023', '2023/24', '2024']

    def row(self, name='Murthy,Srinivasa', pay=351290, expense=11382, year=1, source='official'):
        return [name, None, pay, expense, 0, year, source, 180]

    def test_original_and_compiled_labels_do_not_relabel_observations(self):
        official = self.row(year=0)
        compiled = self.row('Murtby, Srinivasa', year=1, source='compiled')
        evidence, problem = exact_witnesses([compiled], (0, 'murthy|srinivasa'),
            {signature(official, self.years): [official]}, self.years)
        self.assertIsNone(problem)
        self.assertEqual(evidence[0][0][5], 1)
        self.assertEqual(evidence[0][1][0][5], 0)

    def test_known_zero_unknown_expenses_and_cent_differences_remain_distinct(self):
        official = self.row(expense=None)
        compiled = self.row('Murtby, Srinivasa', expense=0, source='compiled')
        evidence, problem = exact_witnesses([compiled], (0, 'murthy|srinivasa'),
            {signature(official, self.years): [official]}, self.years)
        self.assertFalse(evidence)
        self.assertIsNotNone(problem)
        self.assertNotEqual(signature(self.row(pay=100.01), self.years), signature(self.row(pay=100), self.years))
        _, problem = exact_witnesses([self.row(expense=None)], (0, 'murthy|srinivasa'), {}, self.years)
        self.assertIn('unknown', problem)

    def test_equal_money_for_another_official_name_blocks_a_join(self):
        official = self.row()
        other = self.row('Murthy, Sriram')
        compiled = self.row('Murtby, Srinivasa', source='compiled')
        matches, problem = exact_witnesses([compiled], (0, 'murthy|srinivasa'),
            {signature(official, self.years): [official, other]}, self.years)
        self.assertFalse(matches)
        self.assertIn('not unique', problem)

    def test_every_observation_of_an_alias_must_be_supported(self):
        official = self.row()
        rows = [self.row('Murtby, Srinivasa', source='compiled'), self.row('Murtby, Srinivasa', pay=99, source='compiled')]
        matches, problem = exact_witnesses(rows, (0, 'murthy|srinivasa'),
            {signature(official, self.years): [official]}, self.years)
        self.assertFalse(matches)
        self.assertIsNotNone(problem)

    def test_alias_row_guard_preserves_multiplicity_and_nulls(self):
        a, b = self.row(), self.row(expense=None)
        self.assertEqual(row_fingerprint([a, b]), row_fingerprint([b, a]))
        self.assertNotEqual(row_fingerprint([a]), row_fingerprint([a, a]))
        self.assertNotEqual(row_fingerprint([b]), row_fingerprint([self.row(expense=0)]))

    def test_index_offsets_do_not_change_the_underlying_record_guard(self):
        index = {'employers': [['PHSA', 'Health', None, 'phsa']], 'years': self.years}
        shifted = {'employers': [['Other', 'Other', None, 'other'], *index['employers']], 'years': ['1990', *self.years]}
        row = self.row()
        moved = list(row)
        moved[4] += 1
        moved[5] += 1
        self.assertEqual(row_fingerprint([row], index), row_fingerprint([moved], shifted))


if __name__ == '__main__':
    unittest.main()
