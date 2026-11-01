#!/usr/bin/env python3
"""Parser regressions for source row boundaries and pay/expense fidelity."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest

P=Path(__file__).with_name('continue_government_police.py')
spec=importlib.util.spec_from_file_location('continuation_government_police',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SourceRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg={s['id']:s for s in json.loads(m.CONFIG_PATH.read_text())['sources']}
    def evidence(self,suffix):
        key=next(k for k in self.cfg if k.endswith(suffix));cfg=self.cfg[key]
        ev=json.loads(gzip.decompress((m.OUT/'evidence'/f'{key}.json.gzip').read_bytes()))
        return cfg,ev
    def test_wrapped_employee_initial_stays_in_same_row(self):
        cfg,ev=self.evidence('2001-02-employees');p=next(p for p in ev['pages'] if p['pdfPage']==22)
        expected=['public-service','DEWITT-VAN OOSTEN, J M',None,87739,4946,22]
        self.assertIn(expected,m.parse_pa_words(p['nativeWords'],cfg,22))
        self.assertIn(expected,m.parse_pa_layout(p['popplerLayout'],cfg,22))
    def test_literal_source_name_is_not_repaired(self):
        cfg,ev=self.evidence('2004-05-employees');p=next(p for p in ev['pages'] if p['pdfPage']==39)
        self.assertIn(['public-service','ST , T',None,83080,None,39],m.parse_pa_words(p['nativeWords'],cfg,39))
    def test_travel_alone_cannot_become_salary(self):
        cfg,_=self.evidence('1999-00-employees');cfg=copy.deepcopy(cfg);cfg['columnStarts']=[63]
        words=[[63,150,90,160,'SMITH,',0,0,0],[92,150,98,160,'J',0,0,1],[215,150,240,160,'9,999',0,0,2]]
        with self.assertRaisesRegex(ValueError,'Missing salary'):
            m.parse_pa_words(words,cfg,1)
    def test_vpd_zero_and_dash_have_distinct_meanings(self):
        c={'employerSlug':'vancouver-police'}
        rows=m.parse_vpd_layout('One, A  Chief Constable  120,000  0\nTwo, B  Superintendent  110,000  -',c,1)
        self.assertEqual([r[4] for r in rows],[0,None])
    def test_vpd_metadata_is_executive_only(self):
        manifest=json.loads((m.OUT/'sources.json').read_text())
        sources=[s for s in manifest['sources'] if s['employerSlug']=='vancouver-police']
        self.assertEqual(len(sources),10)
        for source in sources:
            self.assertEqual(source['category'],'executive-only')
            self.assertFalse(source['completeEmployeeSchedule'])
            self.assertFalse(source['validation']['completeEmployeeSchedule'])
            self.assertIn('executive',source['scope'].lower())
    def test_wrapped_acrd_name_and_title(self):
        cfg,ev=self.evidence('alberni-clayoquot-2025-employees');p=ev['pages'][0]
        expected=['alberni-clayoquot-regional-district','Hallberg Dodds, Charity','Planning Technician/Bylaw Enforcement Officer',77252,164,35]
        self.assertIn(expected,m.parse_acrd_layout(p['popplerLayout'],cfg,35))
        self.assertIn(expected,m.parse_acrd_words(p['nativeWords'],cfg,35))
    def test_source_multiplicity_and_null_expenses_preserved(self):
        cfg,ev=self.evidence('2001-02-employees')
        repeated=[r for r in ev['rows'] if r[1]=='SIMS, R']
        self.assertEqual(len(repeated),2)
        self.assertNotEqual(repeated[0][3],repeated[1][3])
        self.assertTrue(any(r[4] is None for r in ev['rows']))
    def test_appointee_negative_salary_is_literal(self):
        cfg,ev=self.evidence('2000-01-appointees')
        self.assertIn(['public-service','Carroll, P',None,-984,None,11],ev['rows'])
        self.assertIn(['public-service','Davis, B D',None,-2410,None,11],ev['rows'])
    def test_appointee_wrapped_name_without_comma_is_not_repaired(self):
        cfg,ev=self.evidence('2002-03-appointees');p=next(p for p in ev['pages'] if p['pdfPage']==11)
        rows=[r for text in p['independentColumnTexts'] for r in m.parse_oic_column(text,cfg,11)]
        self.assertIn(['public-service','DELAUNAY-BELLEVILLE K A',None,19096,None,11],rows)
    def test_east_kootenay_expense_is_not_balanced_to_control(self):
        cfg,ev=self.evidence('east-kootenay-2023-employees')
        row=next(r for r in ev['rows'] if r[1]=='THOMPSON')
        self.assertEqual(row[4],7004)
        self.assertEqual(sum(r[4] for r in ev['rows'] if r[4] is not None),35988)
    def test_east_kootenay_name_marker_and_job_level(self):
        cfg,ev=self.evidence('east-kootenay-2025-employees')
        row=next(r for r in ev['rows'] if r[1]=='RONNQUIST')
        self.assertEqual(row[3:5],[170060,None])
        self.assertTrue(any(r[2]=='Operator 2' for r in ev['rows']))
        self.assertEqual(len(ev['rows']),56)
    def test_salary_only_expense_metadata_remains_unavailable(self):
        manifest=json.loads((m.OUT/'sources.json').read_text())
        sources=[s for s in manifest['sources'] if self.cfg[s['id']]['parser'] in ['pa-employees','pa-appointees'] and s['year']>='2003/04']
        self.assertEqual(len(sources),6)
        for source in sources:
            self.assertIsNone(source['totalExpenses'])
            self.assertEqual(source['totalKnownExpenses'],0)
            self.assertEqual(source['validation']['expenseComparatorAvailability'],'unavailable')
            self.assertFalse(any(c['field']=='expenses' for c in source['validation']['printedControls']))
    def test_reported_zero_expenses_remain_zero(self):
        row=['vancouver-police','Bruce, M.','Superintendent',133891,0,1]
        self.assertEqual(m.expense_totals([row])['totalExpenses'],0)
        self.assertIsNone(m.expense_totals([[*row[:4],None,1]])['totalExpenses'])
    def test_offline_replay_and_deterministic_payloads(self):
        m.build(Path('/unused'),check=True)

if __name__=='__main__':unittest.main()
