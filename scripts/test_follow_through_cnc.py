#!/usr/bin/env python3
"""Source-led regression checks for CNC scan/native reconstruction."""
import copy,gzip,json,pathlib,unittest
import follow_through_cnc as cnc

class CNCSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=cnc.OUT
        cls.artifacts=cnc.build_artifacts()
        cls.manifest=json.loads(cls.artifacts['sources.json'])
        cls.sources=cls.manifest['sources']
        cls.rows={s['year']:json.loads(gzip.decompress(cls.artifacts[s['file']])) for s in cls.sources}
        cls.reviews=json.loads((cnc.OUT/'reviewed-corrections.json').read_text())
    def test_unknown_expenses_are_not_explicit_zero(self):
        for cell in ['', '-', '—', '–',' $ - ']:self.assertIsNone(cnc.amount(cell))
        self.assertEqual(cnc.amount('0'),0)
        self.assertEqual(cnc.amount('$ 1,835'),1835)
        self.assertEqual(cnc.amount('-25'),-25)
    def test_corrupt_ocr_money_requires_visible_cell_review(self):
        for cell in ['97 341','167 ,662','§,765','786 ;','z','~',':','1,83','1,,835']:
            with self.assertRaises(ValueError):cnc.amount(cell)
    def test_complete_source_page_counts(self):
        self.assertEqual([s['rowCount'] for s in self.sources],[205,236,258,268,278,312,338])
        self.assertEqual(sum(s['rowCount'] for s in self.sources),1895)
        for source in self.sources:
            self.assertTrue(source['completeEmployeeSchedule'])
            self.assertEqual(len(source['pages']),len(source['validation']['sourceRowsPerPhysicalPage']))
    def test_partial_page_cannot_pass_as_complete(self):
        spec=json.loads((cnc.OUT/'reviewed-controls.json').read_text())['years']['2022-23']
        with self.assertRaises(ValueError):cnc.validate_rows(self.rows['2022/23'][:-1],spec)
    def test_original_physical_pages_vary(self):
        self.assertEqual(self.rows['2019/20'][0][5],2)
        self.assertEqual(self.rows['2020/21'][0][5],3)
        self.assertEqual(self.rows['2024/25'][0][5],2)
        self.assertEqual(self.rows['2024/25'][-1][5],8)
    def test_correction_must_have_one_exact_source_witness(self):
        review=self.reviews['years']['2018-19'];old=copy.deepcopy(review['corrections'][0]['before'])
        old[3]+=1
        with self.assertRaises(ValueError):cnc.apply_review([old],{'corrections':[review['corrections'][0]],'additions':[]})
    def test_correction_preserves_visible_amount_not_control_target(self):
        row=next(r for r in self.rows['2018/19'] if r[1]=='Rose, Gregory')
        self.assertEqual(row[3:],[79716,1835,6])
        source=self.sources[0]
        self.assertEqual(source['validation']['remunerationSubtotalResidual'],-5)
        self.assertEqual(source['validation']['expensesSubtotalResidual'],-1)
    def test_native_three_hidden_surnames_are_not_published_names(self):
        fitz=json.loads(gzip.decompress((cnc.OUT/'evidence/2020-21-fitz.json.gzip').read_bytes()))
        poppler=json.loads(gzip.decompress((cnc.OUT/'evidence/2020-21-poppler.json.gzip').read_bytes()))
        differences=[(a,b) for a,b in zip(fitz,poppler) if a!=b]
        self.assertEqual(len(differences),3)
        self.assertEqual([a[1] for a,b in differences],['Chambers-Richard, Tamara','de la Pena Gonzal, Rafael','Montgomery-Hewe, Chris'])
        self.assertEqual([b[1] for a,b in differences],['Chambers-Richards, Tamara','de la Pena Gonzalez, Rafael','Montgomery-Hewett, Chris'])
        for a,b in differences:self.assertEqual(a[2:],b[2:])
    def test_native_original_totals_independently_reproduced(self):
        rows=self.rows['2020/21']
        self.assertEqual((len(rows),sum(r[3] for r in rows),sum(r[4] or 0 for r in rows),sum(r[4] is None for r in rows)),(258,25302809,184800,138))
        source=self.sources[2]
        self.assertEqual((source['validation']['remunerationSubtotalResidual'],source['validation']['expensesSubtotalResidual']),(-24,1))
    def test_blank_and_dash_cells_remain_distinguishable(self):
        source=next(s for s in self.sources if s['year']=='2021/22')
        self.assertEqual((source['validation']['blankExpenseRows'],source['validation']['dashExpenseRows']),(14,120))
        cells=json.loads(gzip.decompress(self.artifacts[source['validation']['reviewedCellsFile']]))
        self.assertEqual({r['row'][1] for r in cells if r['expenseCellState']=='blank'},cnc.BLANK_EXPENSE_NAMES_2021)
        for cell in cells:
            if cell['expenseCellState'] in ('blank','dash'):self.assertIsNone(cell['row'][4])
    def test_source_single_name_has_no_invented_first_name(self):
        row=next(r for r in self.rows['2024/25'] if r[1]=='Ramandeep')
        self.assertEqual(row,['college-of-new-caledonia','Ramandeep',None,79802,None,6])
    def test_source_threshold_never_filters_visible_employee_rows(self):
        row=next(r for r in self.rows['2024/25'] if r[1]=='Esau, Darrell')
        self.assertEqual(row[3:5],[48128,32353])
        self.assertTrue(all(s['thresholdComparison'] is None for s in self.sources))
    def test_source_order_and_missing_rows_restored(self):
        names=[r[1] for r in self.rows['2022/23']]
        self.assertEqual(names[names.index('Little, Jennifer')+1],'Little, Gail')
        self.assertEqual(names[names.index('Bassett, Tyler')+1],'Bax, Carolyn')
        names=[r[1] for r in self.rows['2019/20']]
        self.assertEqual(names[names.index('Pearce, Graham')+1],'Penny, Jonathon')
    def test_ocr_layout_omissions_are_exposed(self):
        evidence=json.loads(self.artifacts['extraction-evidence.json'])
        for report in evidence['reports']:
            if report['year']=='2020/21':continue
            reader=report['readerComparison']
            self.assertEqual(reader['unresolvedDisagreements'],[])
            self.assertEqual(reader['rowsAgreeingAfterVisibleCellCorrections']+len(reader['missingRowsRequiringVisualCompletion']),report['rowCount'])
        self.assertFalse(self.sources[0]['validation']['ocrEngineIndependence'])
    def test_no_board_or_control_row_is_an_employee(self):
        for rows in self.rows.values():
            self.assertTrue(all(r[2] is None for r in rows))
            self.assertFalse(any(r[1].startswith(('Total','Board','Last Name')) for r in rows))
    def test_all_seven_dispositions_are_concrete(self):
        decisions=json.loads(self.artifacts['dispositions.json'])['sources']
        self.assertEqual(len(decisions),7)
        self.assertEqual({s['acceptedSourceId'] for s in decisions},{s['id'] for s in self.sources})
        for decision in decisions:
            self.assertEqual(decision['status'],'imported')
            self.assertEqual(decision['unresolvedEmployeeFields'],[])
            self.assertEqual(decision['heldScopes'][0]['scope'],'board-remuneration')
    def test_deterministic_reviewed_artifacts(self):
        self.assertEqual(self.artifacts,cnc.build_artifacts())
        for file,data in self.artifacts.items():self.assertEqual((cnc.OUT/file).read_bytes(),data,file)
        for source in self.sources:
            compressed=self.artifacts[source['file']]
            self.assertEqual(compressed[4:8],b'\0\0\0\0')
            self.assertEqual(cnc.sha(compressed),source['dataSha256'])
    def test_crop_receipts_match(self):
        for year,review in self.reviews['years'].items():
            for patch in review['corrections']+review['additions']:
                crop=patch['visualEvidence']
                self.assertEqual(cnc.sha((cnc.OUT/crop['file']).read_bytes()),crop['sha256'])
                self.assertEqual(crop['physicalPdfPage'],(patch.get('after') or patch['row'])[5])

if __name__=='__main__':unittest.main()
