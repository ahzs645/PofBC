import unittest

from assess_salary_name_queue import classify


class HeldNameAssessmentTests(unittest.TestCase):
    def facts(self, **changes):
        return {'id': 1562, 'alreadyConnected': False, 'primaryCounts': [1, 3],
                'primaryYearOverlap': False, 'primaryDateOverlap': False,
                'rareSharedTitles': [], 'fullGivenNamesAgree': True, 'multipleGivenNames': True,
                'combinedNameLetters': 22, 'alternativeCanonicalNames': 0,
                'roles': [[], []], 'sharedTitles': [], 'scopes': [['employee-remuneration'], ['employee-remuneration']],
                'nearestYears': 1, 'nearestPayRatio': 1.15, 'rowCounts': [1, 3], **changes}

    def test_a_second_identifying_fact_is_required(self):
        self.assertEqual(classify(self.facts()), 'supported-likely-source-inference')
        self.assertEqual(classify(self.facts(multipleGivenNames=False, combinedNameLetters=10)),
                         'continuity-alone-insufficient-no-inference')
        self.assertEqual(classify(self.facts(fullGivenNamesAgree=False, multipleGivenNames=False)),
                         'initials-or-conflicting-given-names-no-inference')

    def test_primary_overlap_and_alternatives_override_continuity(self):
        for feature in ['primaryYearOverlap', 'primaryDateOverlap']:
            self.assertEqual(classify(self.facts(**{feature: True})), 'primary-periods-overlap-no-inference')
        self.assertEqual(classify(self.facts(alternativeCanonicalNames=1)), 'multiple-compatible-names-no-inference')
        self.assertEqual(classify(self.facts(primaryCounts=[0, 3])), 'primary-source-required')

    def test_role_change_gap_and_pay_jump_need_additional_evidence(self):
        self.assertEqual(classify(self.facts(roles=[['nurse'], ['manager']])), 'different-published-roles-no-inference')
        self.assertEqual(classify(self.facts(nearestYears=7)), 'reporting-gap-too-long-no-inference')
        self.assertEqual(classify(self.facts(nearestPayRatio=2)), 'pay-discontinuity-needs-evidence')

    def test_rare_position_is_an_explicit_likely_assumption_despite_initials(self):
        self.assertEqual(classify(self.facts(fullGivenNamesAgree=False, multipleGivenNames=False,
                                           combinedNameLetters=8, rareSharedTitles=['manager of public works'],
                                           sharedTitles=['manager of public works'], nearestPayRatio=1.01)),
                         'supported-likely-source-inference')


if __name__ == '__main__':
    unittest.main()
