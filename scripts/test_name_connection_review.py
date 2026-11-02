import unittest

from build_name_connection_review import candidates, given_agrees, name_key, one_edit, parts


class NameConnectionReviewTests(unittest.TestCase):
    def group(self, name, employer='bci', period='2023/24'):
        surname, given = parts(name)
        return {'name': name, 'surname': surname, 'given': given, 'employer': employer,
                'pay': 100, 'periods': {period}, 'positions': {'Executive Vice President'}}

    def test_surname_edits_include_insertion_deletion_substitution_and_transposition(self):
        for a, b in [('pittman', 'pittmsn'), ('pittman', 'pitman'), ('pittman', 'pittmann'), ('pittman', 'pittamn')]:
            self.assertTrue(one_edit(a, b), (a, b))
            self.assertTrue(one_edit(b, a), (b, a))
        for a, b in [('pittman', 'pittman'), ('pittman', 'pitmsn'), ('smith', 'jones')]:
            self.assertFalse(one_edit(a, b), (a, b))

    def test_conflicting_middle_initials_do_not_become_candidates(self):
        self.assertTrue(given_agrees(('j',), ('jim',)))
        self.assertTrue(given_agrees(('jeff',), ('jeffrey',)))
        self.assertFalse(given_agrees(('jim', 'a'), ('jim', 'b')))
        self.assertFalse(given_agrees(('jo',), ('joanne',)))
        self.assertFalse(given_agrees((), ('jim',)))

    def test_pittman_typo_is_research_only_and_same_label_is_explicit(self):
        groups = {(0, name_key(name)): self.group(name) for name in ['Pittman, J.', 'Pittmsn, Jim']}
        result = candidates(groups, {})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'unreviewed-candidate')
        self.assertEqual(result[0]['shared_period_labels'], ['2023/24'])
        self.assertIn('inspect source', result[0]['caution'])
        self.assertEqual(len(groups), 2)

    def test_no_cross_employer_or_already_connected_pair(self):
        a = (0, name_key('Pittman, J.'))
        b = (1, name_key('Pittmsn, Jim'))
        groups = {a: self.group('Pittman, J.'), b: self.group('Pittmsn, Jim', 'other')}
        self.assertEqual(candidates(groups, {}), [])
        b = (0, b[1])
        groups = {a: self.group('Pittman, J.'), b: self.group('Pittmsn, Jim')}
        self.assertEqual(candidates(groups, {a: a, b: a}), [])

    def test_normalized_keys_match_accent_case_stops_and_embedded_position_rules(self):
        self.assertEqual(name_key('Tremblay, Émilie A.'), 'tremblay|emilie a')
        self.assertEqual(name_key('Glickman, Eva    Director, HR'), 'glickman|eva')
        self.assertNotEqual(name_key('Lee, Jane A'), name_key('Lee, Jane B'))


if __name__ == '__main__':
    unittest.main()
