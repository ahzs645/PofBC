"""Meaningful missing-cell and source-component regressions for new municipal imports."""
import unittest
import hashlib
import json
from decimal import Decimal
import gap_municipal_emit as emit
from gap_municipal_transcribe import initial
from gap_municipal_transcribe_middle import sections as middle
from gap_municipal_transcribe_rossland_final import sections as final_rossland
from gap_municipal_transcribe_final import sections as final
import gap_municipal_finalize as finalize

class GapMunicipalTests(unittest.TestCase):
 def test_printed_nil_zero_is_distinct_from_blank_dash_and_missing(self):
  self.assertEqual(emit.amount('Nil'),Decimal('0'))
  self.assertEqual(emit.amount('0.00'),Decimal('0.00'))
  for token in [None,'','-','–','—']:self.assertIsNone(emit.amount(token))
  with self.assertRaises(ValueError):emit.amount('1O,000.00')
 def test_composite_unknown_benefit_is_never_silently_zero(self):
  s=middle()[0];r=s['rows'][3]
  self.assertIsNone(r['taxableBenefits'])
  with self.assertRaises(ValueError):emit.numeric_row(r,s)
  s['payRepresentation']='remuneration-column-excluding-separately-published-taxable-benefits'
  pay,expense=emit.numeric_row(r,s)
  self.assertEqual((pay,expense),(Decimal('6016'),Decimal('0')))
  self.assertIsNone(r['taxableBenefits'])
 def test_expense_inclusive_total_does_not_replace_literal_pay(self):
  s=initial()[-1];r=s['rows'][3]
  self.assertEqual(r['expenseInclusiveTotal'],'89967.79')
  self.assertEqual(emit.numeric_row(r,s),(Decimal('88877.79'),Decimal('90.00')))
  self.assertEqual(next(x for x in emit.controls(s) if x['field']=='expenseInclusiveTotal')['knownSumMinusPrintedControl'],1000)
 def test_known_expense_sum_never_establishes_missing_cells(self):
  s=final()[4];c=next(x for x in emit.controls(s) if x['field']=='expenses')
  self.assertEqual(c['knownSumMinusPrintedControl'],0)
  self.assertEqual(c['unknownRowCells'],6)
  self.assertFalse(c['allCellsKnown'])
  self.assertEqual(sum(emit.numeric_row(r,s)[1] is None for r in s['rows']),6)
 def test_source_subtotal_cannot_drop_the_first_100_mile_observation(self):
  s=final()[-1];self.assertEqual(len(s['rows']),8)
  self.assertEqual(s['rows'][0]['name'],'Bissat, David')
  c=next(x for x in emit.controls(s) if x['field']=='remunerationComponent')
  self.assertEqual(c['knownSumMinusPrintedControl'],83264.28)
  self.assertEqual(emit.numeric_row(s['rows'][0],s)[0],Decimal('83264.28'))
 def test_damaged_source_total_digits_are_not_reconstructed(self):
  s=final_rossland()[-2]
  self.assertTrue(all(r['expenseInclusiveTotal'] is None for r in s['rows']))
  self.assertEqual(s['rows'][0]['expenseInclusiveTotalRawVisible'],'3 493')
  self.assertEqual(emit.numeric_row(s['rows'][0],s),(Decimal('30000'),Decimal('8493')))
 def test_known_column_supplement_keeps_all_original_benefits_unknown(self):
  import json,gzip,hashlib
  section=json.loads((emit.AREA/'transcripts-abbotsford-known-column.json').read_bytes())['sections'][0]
  self.assertEqual(len(section['rows']),11)
  self.assertFalse(section['completeEmployeeSchedule'])
  for row in section['rows']:
   self.assertEqual(row['taxableBenefits'],'-')
   self.assertIsNone(emit.amount(row['taxableBenefits']))
   self.assertEqual(emit.numeric_row(row,section)[0],emit.amount(row['remunerationComponent']))
  proof=section['disjointSupplement'];prior=(emit.ROOT/proof['priorData']['path']).read_bytes()
  self.assertEqual(hashlib.sha256(prior).hexdigest(),proof['priorData']['sha256'])
  self.assertEqual(len(json.loads(gzip.decompress(prior))),449)
 def test_footnote_removal_is_limited_to_explicit_trailing_markers(self):
  self.assertEqual(emit.strip_footnote('Leslie Groulx**'),'Leslie Groulx')
  self.assertEqual(emit.strip_footnote('FORTIN: AL'),'FORTIN: AL')
  self.assertEqual(emit.strip_footnote('Mrs. J. Nightingale'),'Mrs. J. Nightingale')
 def test_reimbursement_footnote_does_not_adjust_reported_payment(self):
  s=final_rossland()[1];r=s['rows'][0]
  self.assertEqual(emit.numeric_row(r,s)[0],Decimal('180441.01'))
  self.assertTrue(any('14038.75' in x for x in s['sourceNotes']))

class MunicipalAcceptanceGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.outputs,_,_=emit.build()
 def simulated_decision(self):
  # This decision exists only in test memory and is never a source-review receipt.
  d=finalize.template(self.outputs);d['approvedBy']='/root'
  receipt_path='scripts/test_gap_municipal.py'
  receipt={'path':receipt_path,'sha256':hashlib.sha256((emit.ROOT/receipt_path).read_bytes()).hexdigest()}
  for r in d['cohortReviews']:
   r.update({'reviewerAgent':'/root/independent-test-fixture','approved':True,
    'completeIndependentLiteralFieldReview':True,'originalSourceAndPeriodConfirmed':True,
    'sourceControlResidualsAcceptedWithoutAdjustment':True,'receipt':receipt})
  for a in d['qualifiedDefinitionAdoptions']:
   a.update({'approvedBy':'/root','approved':True,'reason':'Simulated approval for a guard test only.'})
   if 'boundedDisjointElevenRowSupplementApproved' in a:
    a.update({'boundedDisjointElevenRowSupplementApproved':True,
     'prior449DataAndMetadataUnchanged':True,'unknownBenefitsRemainUnknown':True})
  return d
 def test_unapproved_template_never_marks_a_candidate_verified(self):
  with self.assertRaisesRegex(ValueError,'Root adoption'):
   finalize.accepted_outputs(self.outputs,finalize.template(self.outputs))
 def test_every_literal_payload_and_independent_reviewer_must_be_pinned(self):
  d=self.simulated_decision();d['cohortReviews'][0]['candidateDataSha256']='0'*64
  with self.assertRaisesRegex(ValueError,'current literal inputs'):
   finalize.accepted_outputs(self.outputs,d)
  d=self.simulated_decision();d['cohortReviews'][0]['reviewerAgent']='/root/gap_municipal'
  with self.assertRaisesRegex(ValueError,'independent reviewer'):
   finalize.accepted_outputs(self.outputs,d)
 def test_qualified_definitions_cannot_be_adopted_by_subtotal_or_default(self):
  d=self.simulated_decision();d['qualifiedDefinitionAdoptions']=[]
  with self.assertRaisesRegex(ValueError,'explicit adoption set'):
   finalize.accepted_outputs(self.outputs,d)
  d=self.simulated_decision()
  next(a for a in d['qualifiedDefinitionAdoptions'] if 'unknownBenefitsRemainUnknown' in a)['unknownBenefitsRemainUnknown']=False
  with self.assertRaisesRegex(ValueError,'unknownBenefitsRemainUnknown'):
   finalize.accepted_outputs(self.outputs,d)
 def test_review_receipt_change_invalidates_acceptance_and_data_stay_literal(self):
  d=self.simulated_decision();d['cohortReviews'][0]['receipt']=dict(d['cohortReviews'][0]['receipt'],sha256='f'*64)
  with self.assertRaisesRegex(ValueError,'receipt hash changed'):
   finalize.accepted_outputs(self.outputs,d)
  accepted,summary=finalize.accepted_outputs(self.outputs,self.simulated_decision())
  for path,raw in self.outputs.items():
   if path.endswith('.json.gzip') and not path.startswith('evidence/'):
    self.assertEqual(accepted[path],raw)
  self.assertEqual(summary['rows'],411)
  self.assertTrue(all(s['verified'] for s in json.loads(accepted['sources.json'])['sources']))
if __name__=='__main__':unittest.main()
