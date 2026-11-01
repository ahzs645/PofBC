"""Offline source-fidelity checks for the Interior historical continuation."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

import history_interior as parser


class InteriorHistoryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((parser.OUT/'reviewed-layouts.json').read_text())
        cls.sources={s['id']:s for s in json.loads((parser.OUT/'sources.json').read_text())['sources']}

    def source(self,slug,year,category='employee-remuneration'):
        return self.sources[f'history-interior-{slug}-{year}-{category}']

    def rows(self,source):
        return json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))

    def evidence(self,source):
        return json.loads(gzip.decompress((parser.OUT/source['provenanceFile']).read_bytes()))

    def test_every_cell_reproduces_from_each_independent_reader(self):
        for report in self.config['reports']:
            for cohort in report['cohorts']:
                source=self.source(report['employerSlug'],report['year'],cohort['category'])
                evidence=self.evidence(source)
                self.assertEqual(evidence['originalPdfSha256'],report['sha256'])
                self.assertEqual(evidence['periodEvidence'],report['periodEvidence'])
                for reader in ['mupdfWords','popplerWords']:
                    rows=[]
                    for page in evidence['pages']:
                        extracted=parser.extract(page[reader],page['layout'])
                        for row in extracted:
                            if cohort.get('splitRolePrefix'):
                                match=re.fullmatch(r'(COUNCILLOR|MAYOR)\s+(.*)',row['name'],re.I)
                                row['name'],row['position']=match[2],match[1]
                            if cohort.get('splitRoleSuffix'):
                                match=re.fullmatch(r'(.*?)\s+(Mayor(?:\s*/\s*Councillor)?|Councillor)',row['name'],re.I)
                                row['name'],row['position']=match[1],match[2]
                            row['pdfPage']=page['physicalPage']
                        rows+=extracted
                    if cohort.get('reviewedRowSelection'):
                        rows,excluded=parser.select_reviewed_rows(rows,cohort['reviewedRowSelection'])
                        self.assertEqual(excluded,evidence['excludedRows'])
                    expected=[[report['employerSlug'],r['name'],r.get('position'),parser.dollars(r['pay']),parser.dollars(r.get('expenses')),r['pdfPage']] for r in rows]
                    self.assertEqual(expected,self.rows(source),source['id']+' '+reader)
                    self.assertEqual(len(rows),source['rowCount'])
                    for field,control in cohort['controlsCents'].items():
                        self.assertEqual(parser.total(rows,field)-control,cohort.get('reviewedResidualsCents',{}).get(field,0))
                for file_field,hash_field in [('file','dataSha256'),('provenanceFile','provenanceSha256')]:
                    self.assertEqual(hashlib.sha256((parser.OUT/source[file_field]).read_bytes()).hexdigest(),source[hash_field])

    def test_distinct_calendar_cohorts_do_not_duplicate_prior_acceptance(self):
        prior=json.loads((parser.ROOT/'research/salaries/municipal-wave-interior/sources.json').read_text())['sources']
        prior_keys={(s['employerSlug'],s['year'],s['category']) for s in prior}
        keys=[(s['employerSlug'],s['year'],s['category']) for s in self.sources.values()]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertFalse(set(keys)&prior_keys)
        for source in self.sources.values():
            self.assertEqual(source['periodType'],'calendar')
            self.assertEqual(source['periodStart'],source['year']+'-01-01')
            self.assertEqual(source['periodEnd'],source['year']+'-12-31')
            self.assertTrue(source['validation']['periodEvidence'])

    def test_currency_and_summary_words_cannot_leak_into_names_or_positions(self):
        for source in self.sources.values():
            for row in self.rows(source):
                text=' '.join(x for x in row[1:3] if x)
                self.assertNotRegex(text,r'[$€£]')
                self.assertNotRegex(text.lower(),r'\b(consolidated|subtotal|schedule|reconciliation|named subtotal)\b')
        cases=[('district-of-sparwood','2012','Woodall, J',None),('district-of-sparwood','2014','Wight, N',None),('district-of-sparwood','2020','Templin, J',None),('city-of-trail','2022','Yuris, Terry',None),('city-of-trail','2023','Yuris, Terry',None),('city-of-trail','2024','Wookey, Jeffery',None),('district-of-clearwater','2024','Wooliscroft, Shane','Public Works Foreman'),('city-of-rossland','2015','Mr. P. LaFond','Building Inspector'),('city-of-rossland','2021','Zanussi, R','Public Works Foreman'),('city-of-rossland','2022','Zanussi, R','Public Works Foreman'),('city-of-rossland','2024','Zanussi, R','Public Works Foreman')]
        for slug,year,name,position in cases:
            self.assertEqual(self.rows(self.source(slug,year))[-1][1:3],[name,position])

    def test_initials_and_printed_suffix_roles_survive_extraction(self):
        source=self.source('town-of-princeton','2022','elected-officials')
        self.assertIn('WILLIS, TYLER A',{r[1] for r in self.rows(source)})
        for year in ['2012','2013','2014']:
            source=self.source('district-of-sparwood',year,'elected-officials')
            rows=self.rows(source)
            self.assertTrue(any(' A' in r[1] for r in rows))
            self.assertTrue(all(r[2] in ['Mayor','Councillor','Mayor / Councillor'] for r in rows))
            self.assertFalse(any(re.search(r'\b(Mayor|Councillor)\b',r[1],re.I) for r in rows))
        rows=self.rows(self.source('district-of-sparwood','2014','elected-officials'))
        self.assertIn(['Halko, L','Mayor / Councillor'],[r[1:3] for r in rows])

    def test_pay_components_exclude_expense_inclusive_total_and_never_impute_unknown(self):
        source=self.source('city-of-rossland','2021');evidence=self.evidence(source)
        for row,published in zip(evidence['rows'],self.rows(source)):
            self.assertIsNotNone(row['remunerationComponent']);self.assertIsNotNone(row['taxableBenefits'])
            self.assertEqual(row['pay'],row['remunerationComponent']+row['taxableBenefits'])
            self.assertEqual(published[3],parser.dollars(row['pay']))
        self.assertTrue(any(row['expenseInclusiveTotal']!=row['pay'] for row in evidence['rows']))
        page=evidence['pages'][0];layout=page['layout'];words=copy.deepcopy(page['mupdfWords'])
        left,right=layout['columns']['taxableBenefits'];y0,y1=layout['y']
        at=next(i for i,w in enumerate(words) if left<=(w[0]+w[2])/2<right and y0<=(w[1]+w[3])/2<=y1 and parser.MONEY.fullmatch(w[4]))
        words[at][4]='-'
        with self.assertRaisesRegex(ValueError,'Unknown remuneration component'):parser.extract(words,layout)
        council=self.evidence(self.source('city-of-rossland','2021','elected-officials'))['rows']
        self.assertTrue(any(row['taxableBenefits']==0 for row in council))
        self.assertEqual(next(row['taxableBenefits'] for row in council if row['name']=='Mr. D. Lewis'),700)

    def test_source_clipping_spelling_missing_and_threshold_exceptions_are_preserved(self):
        rows=self.rows(self.source('city-of-rossland','2022'))
        self.assertEqual(next(r[2] for r in rows if r[1]=='Lamont, S'),'Manager of Operations &')
        rows=self.rows(self.source('city-of-rossland','2024'))
        self.assertEqual(next(r[3:5] for r in rows if r[1]=='Newton, R'),[73739,5370])
        self.assertTrue(any(r[4] is None for r in self.rows(self.source('city-of-rossland','2022'))))
        self.assertTrue(any(r[2]=='Bylaw Officier' for r in rows))
        for year in ['2022','2023','2024']:
            self.assertTrue(all(r[2] is None for r in self.rows(self.source('city-of-trail',year))))
        self.assertIn('Benson, Beverly',{r[1] for r in self.rows(self.source('city-of-trail','2022','elected-officials'))})
        self.assertIn('Benson, Beverley',{r[1] for r in self.rows(self.source('city-of-trail','2023','elected-officials'))})
        self.assertIsNone(parser.money('-'));self.assertIsNone(parser.money(''))
        self.assertEqual(parser.money('0.00'),0);self.assertEqual(parser.money('(12.34)'),-1234)

    def test_nonzero_residuals_always_have_exact_public_qualification(self):
        for source in self.sources.values():
            controls=source['validation']['printedControls']
            if any(c['residual'] for c in controls):
                self.assertRegex(source['publicWarning'],r'cause.*unconfirmed')
                for control in controls:
                    self.assertIn(f"{control['residual']:+g} CAD",source['publicWarning'])
            else:self.assertIsNone(source['publicWarning'])
        source=self.source('district-of-clearwater','2024')
        self.assertFalse(source['validation']['expensesControlPublished'])
        self.assertEqual([c['field'] for c in source['validation']['printedControls']],['pay'])
        self.assertIsNone(self.source('city-of-rossland','2022')['thresholdComparison'])
        self.assertEqual(self.source('city-of-trail','2024')['thresholdComparison'],'>')

    def test_missing_pay_and_changed_original_fail_instead_of_reusing_stale_review(self):
        source=self.source('city-of-trail','2024');page=self.evidence(source)['pages'][0];layout=page['layout'];left,right=layout['columns']['pay'];y0,y1=layout['y'];words=page['mupdfWords']
        anchor=next(w for w in words if left<=(w[0]+w[2])/2<right and y0<=(w[1]+w[3])/2<=y1 and parser.MONEY.fullmatch(w[4]))
        with self.assertRaisesRegex(ValueError,'pay cells'):parser.extract([w for w in words if w is not anchor],layout)
        with tempfile.TemporaryDirectory() as cache,tempfile.TemporaryDirectory() as out:
            report=self.config['reports'][0];(Path(cache)/report['cacheFile']).write_bytes(b'%PDF changed')
            with self.assertRaisesRegex(ValueError,'fingerprint changed'):parser.build(self.config,Path(cache),Path(out))

    def test_independently_reviewed_large_residuals_do_not_remove_people_or_change_cells(self):
        cases=[('district-of-sparwood','2018','elected-officials',11,[55310,0]),('district-of-sparwood','2022','employee-remuneration',25,[0,190]),('district-of-sparwood','2023','employee-remuneration',28,[232018,6089]),('town-of-princeton','2022','employee-remuneration',20,[13775,-9340.53])]
        for slug,year,category,count,residuals in cases:
            source=self.source(slug,year,category)
            self.assertEqual(len(self.rows(source)),count)
            self.assertEqual([c['residual'] for c in source['validation']['printedControls']],residuals)
            self.assertTrue(source['validation']['independentCrossReviewFile'].endswith('interior-qualified-history.md'))
        rows=self.rows(self.source('district-of-sparwood','2023'))
        self.assertEqual(rows[0][1:5],['Alstad, K',None,92436,2139])
        self.assertEqual(rows[1][1:5],['Bilodeau, K',None,139582,3950])
        self.assertIsNone(next(r[4] for r in rows if r[1]=='Stratton, T'))
        self.assertTrue({'Chechotko, A','LeBlanc, A','Lucas, A','Pinchak, A'} <= {r[1] for r in rows})
        rows=self.rows(self.source('town-of-princeton','2022'))
        self.assertEqual(next(r[2:5] for r in rows if r[1]=='PARSLEY, MARUEEN M'),['ESS Supervisor & Recovery Manager',108411,20552.16])
        self.assertEqual({r[1] for r in rows if r[3]<75000},{'LIBERATORE, LENARD L','WONG, JOSEPH GK'})

    def test_lytton_employee_scope_roles_and_literal_zero(self):
        source=self.source('village-of-lytton','2021','elected-officials');rows=self.rows(source)
        self.assertEqual(rows[0][1:5],['Jan Polderman','Mayor',7500,0])
        self.assertEqual(next(r[2] for r in rows if r[1]=='Robert Leitch'),'Councillor')
        self.assertEqual([r[1] for r in self.rows(self.source('village-of-lytton','2023'))],['Michael Baker','Alba Banman','Ron Dickinson'])
        council=self.source('village-of-lytton','2023','elected-officials');rows=self.rows(council)
        self.assertEqual(len(rows),7)
        self.assertEqual(next(r[2] for r in rows if r[1]=='Jan Polderman'),'former Mayor final payment')
        self.assertIn('Winona (Nonie) McCann',{r[1] for r in rows})
        self.assertFalse(any('Chief' in str(r[1:3]) for r in rows))
        evidence=self.evidence(council)
        self.assertEqual(len(evidence['publishedGroupRows']),10)
        self.assertEqual({r['name'] for r in evidence['excludedRows']},{'Kyle Parker (Co-Fire Chief)','Dion Moody (Co-Fire Chief)','Jason Phillips (former Fire Chief)'})

    def test_explicit_empty_employee_schedule_preserves_aggregate_without_fake_records(self):
        manifest=json.loads((parser.OUT/'sources.json').read_text());source=manifest['aggregateOnlySources'][0]
        self.assertEqual(source['employerSlug'],'village-of-lytton');self.assertEqual(source['year'],'2022')
        self.assertEqual(source['status'],'verified-aggregate-only');self.assertEqual(source['rowCount'],0)
        self.assertNotIn('file',source)
        raw=(parser.OUT/source['provenanceFile']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),source['provenanceSha256'])
        evidence=json.loads(gzip.decompress(raw));review=evidence['review']
        for words in evidence['readers'].values():
            def region(bounds):
                left,top,right,bottom=bounds
                return [w for w in words if left<=(w[0]+w[2])/2<right and top<=(w[1]+w[3])/2<bottom]
            from collections import Counter
            self.assertEqual(Counter(w[4] for w in region(review['zeroNamedBounds'])),Counter(review['zeroNamedTokens']))
            for field,cell in review['aggregateCells'].items():
                self.assertEqual(parser.money(' '.join(w[4] for w in sorted(region(cell['bounds']),key=lambda w:w[0]))),cell['cents'])
        self.assertEqual(source['validation']['sourceControls']['belowThresholdRemuneration'],181393.87)
        self.assertEqual(source['validation']['sourceControls']['belowThresholdExpenses'],10611.11)


if __name__=='__main__':unittest.main()
