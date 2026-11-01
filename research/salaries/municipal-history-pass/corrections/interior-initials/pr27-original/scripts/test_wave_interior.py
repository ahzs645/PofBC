"""Offline Southern Interior source regressions using both retained PDF readers."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import wave_interior as parser


class InteriorSourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((parser.OUT/'reviewed-layouts.json').read_text())
        cls.sources={s['id']:s for s in json.loads((parser.OUT/'sources.json').read_text())['sources']}

    def get_source(self,slug,year,category='employee-remuneration'):
        return self.sources[f'wave-interior-{slug}-{year}-{category}']

    def test_each_independent_reader_reproduces_complete_published_cohort(self):
        for report in self.config['reports']:
            for cohort in report['cohorts']:
                source=self.get_source(report['employerSlug'],report['year'],cohort['category'])
                evidence=json.loads(gzip.decompress((parser.OUT/source['provenanceFile']).read_bytes()))
                actual=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
                self.assertEqual(len(actual),cohort['rowCount'])
                for reader in ['mupdfWords','popplerWords']:
                    all_rows=[]
                    for page in evidence['pages']:
                        extracted=parser.extract(page[reader],page['layout'])
                        for row in extracted:
                            if cohort.get('splitRolePrefix'):
                                role,name=row['name'].split(' ',1);row['name'],row['position']=name,role
                            row['pdfPage']=page['physicalPage']
                        all_rows+=extracted
                    expected=[[report['employerSlug'],r['name'],r.get('position'),parser.dollars(r['pay']),parser.dollars(r.get('expenses')),r['pdfPage']] for r in all_rows]
                    self.assertEqual(expected,actual,source['id']+' '+reader)
                    for field,printed in cohort['controlsCents'].items():
                        self.assertEqual(parser.total(all_rows,field)-printed,cohort['reviewedResidualsCents'][field])
                self.assertEqual(hashlib.sha256((parser.OUT/source['file']).read_bytes()).hexdigest(),source['dataSha256'])
                self.assertEqual(hashlib.sha256((parser.OUT/source['provenanceFile']).read_bytes()).hexdigest(),source['provenanceSha256'])

    def test_missing_zero_negative_and_expense_inclusive_total_are_distinct(self):
        self.assertIsNone(parser.money('-'));self.assertIsNone(parser.money(''))
        self.assertEqual(parser.money('0.00'),0);self.assertEqual(parser.money('(252.96)'),-25296)
        source=self.get_source('city-of-rossland','2025')
        rows=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
        harris=next(row for row in rows if row[1]=='Harris, T')
        self.assertEqual(harris[3:5],[74396,4227])
        self.assertNotEqual(harris[3],78623)
        self.assertTrue(any(row[4] is None for row in rows))

    def test_rendered_glyph_corrections_preserve_disclosed_names_and_titles(self):
        cases=[('district-of-clearwater','2025','Fraser, Britton','Utility Operator II - Public Works'),('sun-peaks-mountain-resort-municipality','2024','McDougall, Shawn','Utility Technician')]
        for slug,year,name,title in cases:
            source=self.get_source(slug,year);rows=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
            self.assertEqual(next(r[2] for r in rows if r[1]==name),title)
        source=self.get_source('district-of-sparwood','2024');rows=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
        self.assertIn('PAULI, ETHAN',{r[1] for r in rows});self.assertIn('LIU, TAO',{r[1] for r in rows})
        source=self.get_source('district-of-summerland','2023');rows=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
        self.assertEqual(len(rows),60);self.assertEqual({r[5] for r in rows},{5,6});self.assertIn('Renée Belyk',{r[1] for r in rows})

    def test_every_nonzero_source_residual_has_visible_qualification(self):
        for source in self.sources.values():
            residuals=[c['residual'] for c in source['validation']['printedControls']]
            if any(residuals):
                self.assertIsInstance(source['publicWarning'],str)
                self.assertRegex(source['publicWarning'],r'cause.*unconfirmed')
            else:self.assertIsNone(source['publicWarning'])
        source=self.get_source('district-of-clearwater','2025')
        self.assertFalse(source['validation']['expensesControlPublished'])
        self.assertEqual([c['field'] for c in source['validation']['printedControls']],['pay'])

    def test_lost_pay_cell_stops_extraction(self):
        source=self.get_source('village-of-new-denver','2025');evidence=json.loads(gzip.decompress((parser.OUT/source['provenanceFile']).read_bytes()));page=evidence['pages'][0];section=page['layout'];pay=section['columns']['pay'];words=page['mupdfWords'];anchor=next(w for w in words if section['y'][0] <= (w[1]+w[3])/2 <= section['y'][1] and pay[0] <= (w[0]+w[2])/2 <pay[1] and parser.MONEY.fullmatch(w[4]))
        with self.assertRaisesRegex(ValueError,'pay cells'):parser.extract([w for w in words if w is not anchor],section)

    def test_last_employee_fields_stop_before_controls_and_footnotes(self):
        expected=[('district-of-summerland','2023','Tracy Zimmerman','Human Resources Coordinator'),('district-of-clearwater','2025','Wooliscroft, Shane','Public Works Foreman'),('district-of-clearwater','2023','Wooliscroft, Shane','Public Works Foreman'),('city-of-rossland','2025','Zanussi, R','Public Works Foreman'),('sun-peaks-mountain-resort-municipality','2024','McDougall, Shawn','Utility Technician'),('district-of-barriere','2023','C. YOUNG',None),('district-of-sparwood','2025','WRIGHT, K',None),('district-of-sparwood','2024','WRIGHT, KAYDIA',None),('village-of-new-denver','2025','Macaulay, Keith',None),('town-of-princeton','2023','WILLIAMS, JEANIE L','Accounting/HR Manager'),('district-of-coldstream','2021','Whiteley Keith','Operations Superintendent')]
        for slug,year,name,title in expected:
            source=self.get_source(slug,year);rows=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
            self.assertEqual(rows[-1][1:3],[name,title])
        for source in self.sources.values():
            rows=json.loads(gzip.decompress((parser.OUT/source['file']).read_bytes()))
            self.assertFalse(any('consolidated' in str(row[1:3]).casefold() or 'subtotal' in str(row[1:3]).casefold() for row in rows))

    def test_qualified_controls_preserve_missing_cells_and_threshold_exceptions(self):
        princeton=self.get_source('town-of-princeton','2023');rows=json.loads(gzip.decompress((parser.OUT/princeton['file']).read_bytes()))
        self.assertEqual(len(rows),19);self.assertEqual({r[1] for r in rows if r[4] is None},{'CRAMER, NICHOLAS M','THOMAS, JARED'})
        self.assertEqual({r[1] for r in rows if r[3]<75000},{'GUGLIELMINO, ANDREA F','MCNAUGHTON, MARK'})
        self.assertTrue(princeton['completeEmployeeSchedule']);self.assertFalse(princeton['validation']['expensesComplete'])
        self.assertIn('$44.78',princeton['publicWarning']);self.assertIn('Two published expense dashes remain missing',princeton['publicWarning'])
        coldstream=self.get_source('district-of-coldstream','2021');evidence=json.loads(gzip.decompress((parser.OUT/coldstream['provenanceFile']).read_bytes()))
        self.assertEqual(len(evidence['rows']),19);self.assertTrue(all(r['expenses'] is not None for r in evidence['rows']))
        self.assertTrue(all(r['pay']+r['expenses']==r['expenseInclusiveTotal'] for r in evidence['rows']))
        self.assertEqual([c['residual'] for c in coldstream['validation']['printedControls']],[0,-300,-300])
        self.assertIn('$300 below',coldstream['publicWarning']);self.assertTrue(coldstream['completeEmployeeSchedule'])

    def test_changed_original_cannot_reuse_reviewed_layout(self):
        with tempfile.TemporaryDirectory() as cache,tempfile.TemporaryDirectory() as out:
            report=self.config['reports'][0];(Path(cache)/report['cacheFile']).write_bytes(b'%PDF changed')
            with self.assertRaisesRegex(ValueError,'fingerprint changed'):parser.build(self.config,Path(cache),Path(out))


if __name__=='__main__':unittest.main()
