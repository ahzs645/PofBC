import copy
from decimal import Decimal
import unittest

import resolve_held_municipal as r


class McBrideCouncilHoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision=r.read(r.REPORT/'decision-and-year-comparison.json')
        cls.evidence=r.read(r.OUT/'evidence/annual-native-row-comparison.json.gzip')

    def test_complete_five_row_annual_table_independently_agrees(self):
        peer,_=r.held_from_frozen_peer()
        rows=r.annual_equality(self.evidence['readerInputs'],peer)
        self.assertEqual(len(rows),5)
        sums=[sum(Decimal(str(row[index]))for row in rows)for index in (1,2,3)]
        self.assertEqual(sums,[Decimal('45600'),Decimal('42578.05'),Decimal('88178.05')])

    def test_explicit_table_year_cannot_be_replaced_by_report_footer(self):
        peer,_=r.held_from_frozen_peer()
        inputs=copy.deepcopy(self.evidence['readerInputs'])
        inputs['popplerLayout']=inputs['popplerLayout'].replace('VILLAGE COUNCIL 2024','VILLAGE COUNCIL 2025')
        with self.assertRaises(AssertionError):r.annual_equality(inputs,peer)

    def test_nothing_imported_or_relabelled(self):
        manifest=r.read(r.OUT/'sources.json')
        self.assertEqual(manifest['sources'],[])
        self.assertEqual(manifest['heldCandidates'][0]['printedCouncilYear'],'2024')
        self.assertEqual(manifest['heldCandidates'][0]['reportYear'],'2025')
        self.assertEqual(self.decision['acceptedRows'],0)
        self.assertIsNone(self.decision['proposedInferredYear'])

    def test_all_five_expenses_conflict_with_accepted_2024(self):
        comparison=self.decision['heldVsAccepted2024']
        self.assertEqual(len(comparison),5)
        self.assertTrue(all(row['role']==row['prior2024Role']and row['pay']==row['prior2024Pay']for row in comparison))
        self.assertTrue(all(row['unresolvedPeriodExpense']!=row['prior2024Expense']for row in comparison))
        self.assertEqual(sum(Decimal(str(row['expenseDifference']))for row in comparison),Decimal('-17573.82'))
        self.assertEqual([len(h['rows'])for h in self.decision['acceptedCouncilHistory']],[8,6,5])

    def test_draft_and_adoption_are_explicitly_distinguished(self):
        originals=r.read(r.REPORT/'originals-and-status.json')
        draft=next(o for o in originals if o['key']=='annual-agenda-draft')
        self.assertIn('DRAFT',draft['status'])
        self.assertEqual(draft['salaryPage'],10)
        adopted=self.decision['sofiAdoption']
        self.assertEqual(adopted['motion'],'090630.26')
        self.assertEqual(adopted['physicalPage'],3)
        self.assertIn('No council row',adopted['limitation'])

    def test_normalized_task_queue_has_only_eleven_keys(self):
        expected={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
        tasks=r.read(r.REPORT/'work-queue.json')
        self.assertEqual(len(tasks),2)
        self.assertTrue(all(set(t)==expected for t in tasks))
        self.assertEqual(tasks[1]['route'],'clarification-request')
        self.assertIn('not-sent',tasks[1]['status'])


if __name__=='__main__':unittest.main()
