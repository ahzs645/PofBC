#!/usr/bin/env python3
"""Acceptance regressions for the finite nine-history extension."""
import unittest,pathlib,json,gzip,copy
from unittest import mock
import gap_health_other_history_export as export
from gap_health_employees_native import amount
ROOT=pathlib.Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_other_history';COLLECTION=ROOT/'research/salaries/gap-fill-health-other-history'
class OtherHistoryContracts(unittest.TestCase):
 def sources(self):return json.load(open(COLLECTION/'sources-candidate.json'))['sources']
 def test_period_punctuation_is_not_changed_to_invent_a_comma(self):
  s=next(s for s in self.sources() if s['year']=='2009/10');rows=json.load(gzip.open(COLLECTION/s['file'],'rt'));found=[r for r in rows if r[1]=='WILSON. TOM'];self.assertEqual(len(found),1);self.assertEqual(found[0][3:],[77451,0,47]);self.assertEqual(len(rows),2245)
 def test_northern_summary_difference_is_not_filled_with_an_invented_employee(self):
  s=next(s for s in self.sources() if s['year']=='2014/15');self.assertEqual(s['rowCount'],1254);self.assertEqual(s['validation']['printedEmployeeSummaryCount'],1255);self.assertIn('1,254',s['publicWarning']);self.assertFalse(s['validation']['residualCauseEstablished'])
 def test_negative_expense_zero_and_missing_cells_preserve_distinct_source_values(self):
  negative=[];missing=0;zeros=0
  for s in self.sources():
   rows=json.load(gzip.open(COLLECTION/s['file'],'rt'));prov=json.load(gzip.open(COLLECTION/s['provenanceFile'],'rt'))['rows']
   for r,p in zip(rows,prov):
    literal=p['rawExpenseToken']
    if literal in (None,'','-'):
     self.assertIsNone(r[4]);missing+=1
    elif amount(literal)==0:self.assertEqual(r[4],0);zeros+=1
    if r[4] is not None and r[4]<0:negative.append((r[1],r[4]))
  self.assertGreater(missing,0);self.assertGreater(zeros,0);self.assertIn(('FANKBONER,MORGAN ALEXA',-81.43),negative)
 def test_monetary_source_counts_cover_all_anchors_including_footer_and_comma_free_name(self):
  census=json.load(open(AREA/'complete-monetary-column-census.json'))
  n=next(s for s in census['sources'] if s['key']=='northern-health-2014-15');self.assertEqual(n['totalMonetaryColumnAnchors'],1257);self.assertEqual(n['parsedEmployeeObservations'],1254);self.assertEqual(n['classifications']['published nonnamed control/aggregate anchor'],3)
  early=next(s for s in census['sources'] if s['key']=='northern-health-2003-04');self.assertEqual(early['classifications']['published page-number footer anchor'],8)
 def test_unapproved_peer_amount_change_fails_closed(self):
  real=export.pinned
  def changed(path,h):
   value=real(path,h)
   if path==export.PEER_FINAL:value['rows'][0]['remuneration']='0'
   return value
  with mock.patch.object(export,'pinned',changed):
   with self.assertRaises(AssertionError):export.peer_selection()
 def test_missing_top_level_retention_flag_is_rejected(self):
  source=copy.deepcopy(self.sources()[0]);export.validate_retention(source);del source['retainCompiledPartition']
  with self.assertRaises(KeyError):export.validate_retention(source)
 def test_all_source_retention_and_complete_scope_flags_agree(self):
  for s in self.sources():export.validate_retention(s);self.assertTrue(s['completeEmployeeSchedule'])
 def test_fraser_detail_is_supporting_and_unresolved_names_are_not_new_employees(self):
  c=json.load(open(AREA/'fraser-contract-context/comparison-candidate.json'));self.assertEqual(c['totalNamedDetailRows'],492);self.assertEqual(c['uniqueExactNameAndPaymentOverlaps'],430);self.assertEqual(c['unresolvedComparisonRows'],62);self.assertTrue(c['noSalaryRowsAppended']);self.assertTrue(c['noPositionsAdopted']);self.assertFalse(any(s['employerSlug']=='fraser-health' for s in self.sources()))
 def test_all_literal_fraser_fields_agree_between_independent_engines(self):
  c=json.load(open(AREA/'fraser-contract-context/comparison-candidate.json'));self.assertEqual(c['twoReaderLiteralFieldDifferences'],[]);self.assertEqual(c['flags'],[]);self.assertEqual(c['expectedNamedDetailCountFromActualContractSummary']['total'],402+88+2)
if __name__=='__main__':unittest.main()
