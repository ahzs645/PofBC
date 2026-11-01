#!/usr/bin/env python3
"""Regress the actual difficult-source decisions, rather than guessed repairs."""
import gzip, hashlib, json, tempfile, unittest
from pathlib import Path
from parse_history_resolved import AUDIT, BASE, cents, extract, money

class HistoryResolvedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=json.loads((BASE/'sources.json').read_text())['sources']
        cls.config=json.loads((AUDIT/'reviewed-layouts.json').read_text())
    def source(self,slug,category='employee-remuneration'):
        return next(s for s in self.sources if s['employerSlug']==slug and s['category']==category)
    def evidence(self,s):return json.loads(gzip.decompress((BASE/s['provenanceFile']).read_bytes()))
    def rows(self,s):return json.loads(gzip.decompress((BASE/s['file']).read_bytes()))
    def test_source_fingerprints_and_all_fields_are_pinned(self):
        self.assertEqual(sum(s['rowCount'] for s in self.sources),60)
        self.assertEqual(len(self.sources),3)
        for s in self.sources:
            raw=(BASE/s['file']).read_bytes();evraw=(BASE/s['provenanceFile']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),s['dataSha256'])
            self.assertEqual(hashlib.sha256(evraw).hexdigest(),s['provenanceSha256'])
            ev=self.evidence(s)
            for r in ev['rows']:
                self.assertEqual(r['pymupdf']['fields'],r['poppler']['fields'])
                self.assertEqual(r['fields'],r['pymupdf']['fields'])
            originals={r['fields']['name']:r['fields'] for r in ev['rows']}
            for r in self.rows(s):
                o=originals[r[1]]
                self.assertEqual(r[1:4],[o['name'],o['position'],o['pay']])
                self.assertEqual(r[4],None if s['employerSlug']=='city-of-merritt' else o['expenses'])
                self.assertEqual(r[5],s['pages'][0])
    def test_unknown_components_never_become_zero(self):
        for text in ['', '-', '‐','–','—']:self.assertIsNone(money(text))
        self.assertEqual(money('0.00'),0)
        self.assertEqual(money('(12.30)'),-12.3)
        with self.assertRaises(ValueError):cents(None)
        with self.assertRaises(ValueError):money('75,OOO')
    def test_changed_original_is_rejected_before_processing(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'%PDF changed');f.flush()
            with self.assertRaisesRegex(ValueError,'fingerprint'):extract(self.config['reports'][0],Path(f.name))
    def test_merritt_b_is_observed_combined_not_employee_only(self):
        s=self.source('city-of-merritt');v=s['validation'];c=v['sourceControls']
        self.assertEqual(s['totalRemuneration'],4779040.1)
        self.assertEqual(c['printedB'],[7842227.42,116206.03,48141.93])
        self.assertEqual(c['council'],[186501.5,29645.85,576.49])
        self.assertEqual(c['belowThreshold'],[2876685.82,None,None])
        self.assertEqual(cents(c['printedB'][0])-cents(c['council'][0])-cents(c['belowThreshold'][0]),cents(s['totalRemuneration']))
        self.assertEqual(v['observedCombinedBIdentity']['residuals'],[0,0,0])
        self.assertIn('not used as an employee-only control',s['publicWarning'])
    def test_merritt_both_raw_columns_survive_but_app_expenses_are_missing(self):
        for s in self.sources:
            if s['employerSlug']!='city-of-merritt':continue
            self.assertTrue(all(r[4] is None for r in self.rows(s)))
            self.assertIsNone(s['totalExpenses'])
            self.assertFalse(s['completeExpensesDisclosure'])
            self.assertIn('does not define whether they overlap',s['expensesNote'])
        s=self.source('city-of-merritt');raw={r['fields']['name']:r['fields'] for r in self.evidence(s)['rows']}
        self.assertEqual((raw['Ferris Holly']['expenses'],raw['Ferris Holly']['grantExpenses']),(None,4694.28))
        self.assertEqual((raw['Hart Adam']['expenses'],raw['Hart Adam']['grantExpenses']),(None,1259.07))
        self.assertEqual((raw['Gill Ryan']['expenses'],raw['Gill Ryan']['grantExpenses']),(4026.04,2672.94))
    def test_source_names_titles_markers_and_ess_annotation_survive(self):
        s=self.source('city-of-merritt');raw={r['fields']['name']:r['fields'] for r in self.evidence(s)['rows']}
        self.assertEqual(raw['Johnston Carl']['position'],'Building Offical I')
        self.assertEqual(raw['Walder Katrina']['position'],'Court Liasion/Foreperson')
        self.assertEqual((raw['Natkinniemi, Kevin']['marker'],raw['Natkinniemi, Kevin']['pay']),('**',189378.04))
        self.assertEqual((raw['Croasdale Robert']['marker'],raw['Croasdale Robert']['pay']),('*',106338.32))
        c=self.source('city-of-merritt','elected-officials');rows=self.rows(c)
        self.assertEqual(rows[1][1:5],['Charney, Wendy','Councillor (incl ESS $5,497.77)',27592.34,None])
    def test_official_posting_does_not_claim_signed_merritt_adoption(self):
        s=self.source('city-of-merritt');p=s['validation']['publicationEvidence']
        self.assertFalse(p['approvalSignaturesPresent']);self.assertFalse(p['approvalDatesPresent'])
        self.assertIn('signed adoption is not claimed',s['publicWarning'])
    def test_lake_known_seven_rows_do_not_publish_jessica_or_repair_pay(self):
        s=self.source('town-of-lake-cowichan');rows=self.rows(s);ev=self.evidence(s)
        self.assertEqual(len(rows),7);self.assertEqual(s['sourceNamedRowCount'],8)
        self.assertNotIn('Jessica May',[r[1] for r in rows]);self.assertEqual(s['withheldRowCount'],1)
        held=ev['withheldRows'][0]
        self.assertEqual(held,{'name':'Jessica May','position':'Fire Risk Officer','pay':92354.93,'expenses':5429.75,'total':92784.68})
        self.assertEqual(cents(held['pay'])+cents(held['expenses'])-cents(held['total']),500000)
        self.assertEqual(s['totalRemuneration'],729610.84);self.assertEqual(s['totalExpenses'],15015.4)
        for row in ev['rows']:
            r=row['fields']
            if r['name']!='Jessica May':self.assertEqual(cents(r['pay'])+cents(r['expenses']),cents(r['total']))
    def test_partial_flags_and_controls_do_not_assert_a_complete_lake_cohort(self):
        s=self.source('town-of-lake-cowichan');v=s['validation']
        for obj in [s,v]:
            self.assertFalse(obj['completeEmployeeSchedule']);self.assertFalse(obj['completeNamedCohort'])
        self.assertEqual(v['rowsIndependentlyChecked'],8)
        self.assertEqual([c['completeOriginalResidual'] for c in v['printedControls']],[0,0])
        for c in v['printedControls']:
            self.assertEqual(cents(c['acceptedPartialRowSum'])+cents(c['withheldRowSum']),cents(c['printedControl']))
        self.assertIn('Partial employee schedule',s['publicWarning']);self.assertIn('0.09',s['publicWarning'])
    def test_no_already_accepted_lake_council_duplicate_or_guessed_boundary(self):
        lake=[s for s in self.sources if s['employerSlug']=='town-of-lake-cowichan']
        self.assertEqual([s['category'] for s in lake],['employee-remuneration'])
        self.assertTrue(all(s['thresholdComparison'] is None for s in self.sources))

if __name__=='__main__':unittest.main()
