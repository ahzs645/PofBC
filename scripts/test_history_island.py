"""Regression checks for source-specific Island historical disclosure semantics."""
import gzip
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('history_island',ROOT/'scripts/import_history_island.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

class HistoryIslandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((M.OUT/'sources.json').read_text())
        cls.sources={(s['employerSlug'],s['year'],s['category']):s for s in cls.manifest['sources']}
        cls.evidence={e['sourceId']:e for e in json.loads(gzip.decompress((M.OUT/'extraction-evidence.json.gzip').read_bytes()))}

    def source(self,slug,year,kind='employee-remuneration'):
        return self.sources[(slug,str(year),kind)]

    def rows(self,slug,year,kind='employee-remuneration'):
        source=self.source(slug,year,kind)
        return json.loads(gzip.decompress((M.OUT/source['file']).read_bytes()))

    def test_full_offline_two_reader_replay(self):
        M.verify_offline()

    def test_currency_distinguishes_unknown_zero_negative_and_malformed(self):
        self.assertIsNone(M.money('-'));self.assertIsNone(M.money(''))
        self.assertEqual(M.money('0'),0);self.assertEqual(M.money('(256)'),-256)
        self.assertEqual(M.money('$104,649.90'),104649.9)
        with self.assertRaises(ValueError):M.money('3,3463.64')

    def test_initial_A_and_bottom_aligned_roles_survive(self):
        rows=self.rows('city-of-courtenay',2021)
        row=next(r for r in rows if r[1]=='Berard, A.')
        self.assertEqual(row[2],'Manager of Financial Planning, Payroll & Business Performance')
        self.assertEqual(row[3:5],[101801,1279])
        older=self.rows('village-of-cumberland',2015)
        self.assertEqual(next(r[2]for r in older if r[1]=='Parker, Rachel'),'Deputy Corporate Officer')
        self.assertEqual(next(r[2]for r in older if r[1]=='Williamson, Michael'),'Manager of Protective Services')
        self.assertEqual(next(r[2]for r in older if r[1]=='Topham, Sundance'),'CAO')

    def test_visible_title_clips_are_not_expanded(self):
        for year,name,end in [(2022,'Berard, A.','Perfo'),(2023,'Wyka, R.','Busine'),(2024,'Wyka, R.','Performa')]:
            source=self.source('city-of-courtenay',year);row=next(r for r in self.rows('city-of-courtenay',year)if r[1]==name)
            self.assertTrue(row[2].endswith(end));self.assertIn('hidden suffix',source['notes'][-1])

    def test_unusable_expense_preserves_known_pay_and_literal_evidence(self):
        source=self.source('district-of-ucluelet',2023);rows=self.rows('district-of-ucluelet',2023)
        row=next(r for r in rows if r[1]=='Fortune Abigail')
        self.assertEqual(row[2:],["Manager of Parks and Recreation",104649.9,None,30])
        self.assertEqual(len(rows),15);self.assertTrue(source['completeEmployeeSchedule'])
        self.assertFalse(source['expensesComplete']);self.assertFalse(source['validation']['expensesComplete'])
        self.assertIn('3,3463.64',source['publicWarning'])
        ev=next(e for e in self.evidence[source['id']]['rows']if e['row'][0]=='Fortune Abigail')
        self.assertEqual(ev['unusableExpenseLiteral'],'3,3463.64')
        self.assertIn('3,3463.64',[w[4]for w in ev['words']])

    def test_blank_expense_and_expense_inclusive_total_are_separate(self):
        source=self.source('town-of-port-mcneill',2021)
        row=next(r for r in self.rows('town-of-port-mcneill',2021)if r[1]=='Sinclair, Scott')
        self.assertEqual(row[3:],[78193,None,28])
        ev=next(e for e in self.evidence[source['id']]['rows']if e['row'][0]=='Sinclair, Scott')
        self.assertEqual(ev['printedAdditionalTotal'],78193)
        row=next(r for r in self.rows('town-of-gibsons',2024)if r[1]=='Thomas, Katie')
        self.assertEqual(row[3:5],[91747,None])

    def test_tofino_benefits_are_evidence_not_invented_inclusive_pay(self):
        source=self.source('district-of-tofino',2021,'elected-officials')
        self.assertEqual(source['totalRemuneration'],109203)
        self.assertEqual(source['totalDisclosedExpenses'],5159.88)
        self.assertIn('Benefits',source['scopeDescription']);self.assertIn('excluded',source['publicWarning'])
        ev=self.evidence[source['id']]['rows']
        self.assertEqual(round(sum(r['printedBenefits']for r in ev),2),15560.49)
        self.assertEqual(next(r['printedBenefits']for r in ev if r['row'][0]=='Andrea McQuade'),0)
        self.assertEqual(source['validation']['rowSumMinusNamedControl'],[0,-6])

    def test_calendar_period_is_source_printed_not_upload_date(self):
        source=self.source('town-of-port-mcneill',2021)
        self.assertEqual(source['validation']['periodProof']['physicalPdfPage'],32)
        self.assertIn('December 31, 2021',source['validation']['periodProof']['printedText'])
        source=self.source('town-of-gibsons',2021)
        self.assertIn('/2026/',source['sourceUrl']);self.assertEqual(source['periodStart'],'2021-01-01')

    def test_ocr_overlay_requires_complete_human_transcriptions(self):
        source=self.source('district-of-lantzville',2025,'elected-officials')
        self.assertTrue(source['validation']['bothFullImageTranscriptionsAgree'])
        rows=self.rows('district-of-lantzville',2025,'elected-officials')
        self.assertEqual(next(r[4]for r in rows if r[1]=='Jones, Joan'),-256)
        self.assertEqual(next(r[1]for r in rows if r[1].startswith('Savage')),'Savage, Ian')
        self.assertIn('$93,289',source['publicWarning'])
        self.assertNotIn('thresholdComparison',self.source('district-of-lantzville',2025))
        employees=self.rows('district-of-lantzville',2025)
        self.assertEqual(next(r[2]for r in employees if r[1]=='Thurlin, Eric'),'Maintenance Technician III')
        self.assertIn('Long, Aria',[r[1]for r in employees])

    def test_native_parser_rejects_full_page_scan_overlay(self):
        class Scan:
            number=3;rect=M.fitz.Rect(0,0,612,792)
            def get_image_info(self):return [{'bbox':(0,0,612,792)}]
        with self.assertRaisesRegex(AssertionError,'OCR overlay'):
            M.positioned(Scan(),dict(slug='district-of-lantzville',year='2025'))

    def test_controls_use_decimal_arithmetic_without_fake_residuals(self):
        self.assertEqual(self.source('district-of-tofino',2012)['validation']['rowSumMinusNamedControl'],[0,None])
        self.assertEqual(self.source('district-of-tofino',2013)['validation']['rowSumMinusNamedControl'],[0,0])
        source=self.source('city-of-courtenay',2024)
        self.assertEqual(source['validation']['rowSumMinusNamedControl'],[-3,8])
        self.assertIn('cause is unresolved',source['publicWarning'])

    def test_unavailable_below_threshold_expenses_do_not_become_zero(self):
        cfg=dict(slug='district-of-tofino',year='2021',kind='employees')
        unknown=[dict(scope='all',printedValues=[10,6]),dict(scope='under',printedValues=[3,None])]
        explicit_zero=[dict(scope='all',printedValues=[10,6]),dict(scope='under',printedValues=[3,0])]
        self.assertEqual(M.expected_named(unknown,cfg),[7,None])
        self.assertEqual(M.expected_named(explicit_zero,cfg),[7,6])
        for year,known,broader,difference in [(2012,39581.3,39581.3,0),(2021,16773.81,16773.82,-0.01)]:
            source=self.source('district-of-tofino',year);validation=source['validation']
            self.assertIsNone(validation['expectedNamedControl'][1]);self.assertIsNone(validation['rowSumMinusNamedControl'][1])
            self.assertFalse(validation['namedEmployeeExpenseComparatorAvailable'])
            comparison=validation['broaderEmployeeExpenseComparison']
            self.assertEqual(comparison['knownNamedEmployeeExpenses'],known)
            self.assertEqual(comparison['printedAllEmployeeExpenses'],broader)
            self.assertEqual(comparison['knownNamedMinusAllEmployeeExpenses'],difference)
            self.assertIsNone(comparison['printedBelowThresholdExpense'])
            self.assertIn('different scopes',source['publicWarning'])
            self.assertIn('not a named expense reconciliation',source['publicWarning'])

    def test_qualified_issuer_residual_does_not_change_named_pay(self):
        source=self.source('village-of-tahsis',2019,'elected-officials')
        rows=self.rows('village-of-tahsis',2019,'elected-officials')
        self.assertEqual(len(rows),5);self.assertEqual(source['totalRemuneration'],29124)
        self.assertEqual(source['validation']['expectedNamedControl'],[28125,16175])
        self.assertEqual(source['validation']['rowSumMinusNamedControl'],[999,0])
        self.assertEqual(next(r[3]for r in rows if r[1]=='Joshua Lambert'),4094)
        self.assertIn('$+999.00',source['publicWarning'])
        self.assertIn('unsigned, undated',self.source('district-of-tofino',2021)['publicWarning'])

    def test_remaining_work_queue_is_normalized_and_separates_acquisition(self):
        queue=json.loads((M.AUDIT/'work-queue.json').read_text())
        fields={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
        self.assertEqual(len(queue),len({t['id']for t in queue}))
        for task in queue:self.assertEqual(set(task),fields)
        routes={t['route']for t in queue}
        self.assertTrue({'processing','public-archive-research','ordinary-records-request','clarification-request'}.issubset(routes))
        self.assertFalse(any(t['route']=='foi-fallback'for t in queue))
        unique_governance=[t for t in queue if t['employerSlug']=='shishalh-nation-government-district']
        self.assertTrue(unique_governance)
        self.assertTrue(all(t['route']=='public-archive-research'for t in unique_governance))

    def test_cohorts_do_not_duplicate_baseline_or_turn_aggregates_into_people(self):
        baseline={r['employerSlug']:r for r in json.loads((M.AUDIT.parent/'baseline.json').read_text())['municipalities']}
        for source in self.manifest['sources']:
            key='officialEmployeeYears'if source['category']=='employee-remuneration'else'officialCouncilYears'
            self.assertNotIn(source['year'],baseline[source['employerSlug']][key])
            for row in json.loads(gzip.decompress((M.OUT/source['file']).read_bytes())):
                self.assertFalse(any(t in row[1]for t in ['Consolidated','Total -','Aggregate']))
                self.assertFalse(any(t in (row[2]or'')for t in ['Consolidated','Statement of','Schedule 1']))

if __name__=='__main__':unittest.main()
