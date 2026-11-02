"""Real-source parser and omission guards for seven additional school reports."""
import copy
import gzip
import json
from pathlib import Path
import unittest

import gap_school_native_extract as native
import gap_school_native_coverage as coverage
import gap_school_native_scan_parse as scanned
import gap_school_native_build as build

AREA=Path(__file__).resolve().parents[1]/'research/salaries/gap-fill-2026-11-02/school_native'


class NativeSchoolSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proofs={}
        for c in json.loads((AREA/'native-specs.json').read_bytes()):
            p=AREA/c.get('candidateFile',c['key']+'-native-candidate.json.gzip')
            cls.proofs[c['key']]=json.loads(gzip.decompress(p.read_bytes()))

    def test_all_five_complete_schedules_have_exact_row_multiplicity(self):
        expected={'sd34-2025':1215,'sd40-2025':489,'sd41-2025':1778,'sd57-2025':848,'sd62-2025':909}
        self.assertEqual(sum(expected.values()),5239)
        for key,count in expected.items():
            p=self.proofs[key]
            self.assertEqual(len(p['popplerRows']),count)
            self.assertEqual(len(p['mupdfRows']),count)
            self.assertEqual(p['unresolvedPoppler'],[])
            self.assertEqual(p['unresolvedMupdf'],[])

    def test_frost_split_physical_text_line_never_drops_a_named_payment(self):
        p=self.proofs['sd34-2025']
        r=next(r for r in p['popplerRows'] if r['name']=='Frost, Shelly')
        self.assertEqual([r['remuneration'],r['expenses']],['133747.80','4905.36'])
        self.assertIn('Senior Manager,Budget & Student Demographics',r['precedingPhysicalTextLine'])
        self.assertEqual(p['summaries']['employee-remuneration']['computedTotals'],['129600389.79','813496.13'])

    def test_clipped_title_differences_remain_review_targets(self):
        p=self.proofs['sd34-2025']
        self.assertEqual(len(p['independentReaderDifferences']),10)
        for d in p['independentReaderDifferences']:
            self.assertEqual(d['poppler'][0],d['mupdf'][0])
            self.assertEqual(d['poppler'][2:],d['mupdf'][2:])
            self.assertNotEqual(d['poppler'][1],d['mupdf'][1])
        self.assertEqual(p['acceptedRows'],0)

    def test_district_burnaby_original_preserves_two_cells_hidden_ocr_misread(self):
        p=self.proofs['sd41-2025'];self.assertTrue(p['source']['sourceUrl'].startswith('https://burnabyschools.ca/'))
        rows={r['name']:r for r in p['popplerRows']}
        self.assertEqual(rows['CECH, PETER E']['expenses'],'2852.99')
        self.assertEqual(rows['HAYES, LARRY']['expenses'],'743.15')
        self.assertEqual(p['summaries']['employee-remuneration']['computedTotals'],['185691610.04','844485.58'])

    def test_sooke_whole_dollar_values_are_never_balanced_to_controls(self):
        p=self.proofs['sd62-2025']
        self.assertEqual(p['summaries']['employee-remuneration']['computedTotals'],['94036344','460411'])
        self.assertEqual(p['summaries']['school-trustees']['computedTotals'],['162656','16297'])

    def test_explicit_zero_is_distinct_from_dash_and_unparsed_text(self):
        self.assertEqual(native.money('0.00'),'0.00')
        self.assertIsNone(native.money('-'))
        with self.assertRaises(ValueError):native.money('O.00')
        self.assertEqual(scanned.amount(''), 'UNRESOLVED:missing-detection')
        self.assertEqual(scanned.amount('-'), 'UNRESOLVED:source-dash-needs-image-confirmation')
        self.assertEqual(scanned.amount('$0.00'),'0.00')

    def test_complete_raw_payment_coverage_passes_all_sources(self):
        for p in self.proofs.values():
            entries=coverage.geometry_audit(p)
            self.assertEqual(sum(e['disposition']=='included-named-observation' for e in entries),len(p['mupdfRows']))
            coverage.text_audit(p)

    def test_deleting_a_real_row_fails_independent_geometry_coverage(self):
        p=copy.deepcopy(self.proofs['sd40-2025']);p['mupdfRows'].pop(70)
        with self.assertRaises(AssertionError):coverage.geometry_audit(p)

    def test_footnoted_or_comma_free_names_cannot_silently_disappear(self):
        p=copy.deepcopy(self.proofs['sd40-2025'])
        # Raw monetary row remains present even if a restrictive name predicate
        # would refuse its footnote or missing comma.
        p['mupdfRows'].pop(0)
        for w in p['mupdfRawPages'][0]['words']:
            if w[4]=='ANDRES,':w[4]='*ANDRES';break
        with self.assertRaises(AssertionError):coverage.geometry_audit(p)

    def test_total_surname_is_not_an_aggregate_control(self):
        self.assertIsNone(coverage.NONPERSON.match('TOTAL, JOHN'))
        self.assertIsNotNone(coverage.NONPERSON.match('TOTAL FOR ELECTED OFFICIALS'))

    def test_omitted_physical_text_row_cannot_silently_disappear(self):
        p=copy.deepcopy(self.proofs['sd57-2025']);p['popplerRows'].pop(50)
        with self.assertRaises(AssertionError):coverage.text_audit(p)

    def test_sd53_currency_glyph_error_changes_only_after_source_image_read(self):
        rows,evidence,_=build.scanned(53,None)
        original=json.loads(gzip.decompress((AREA/'sd53-2025-scan-parsed-v1.json.gzip').read_bytes()))
        self.assertEqual(original['tesseractRows'][96]['expenses'],'6000')
        self.assertEqual(rows[96]['expenses'],'0.00')
        amendment=next(x for x in evidence['sourceImageAmendments'] if x['reader']=='tesseract' and x['sequence']==97 and x['field']=='expenses')
        self.assertEqual([amendment['before'],amendment['after']],['6000','0.00'])
        self.assertIn('sourceImage',amendment)

    def test_sd53_named_rows_retain_explicit_zeroes_and_nine_dollar_residual(self):
        from decimal import Decimal
        rows,_,controls=build.scanned(53,None)
        employees=[r for r in rows if r['category']=='employee-remuneration']
        trustees=[r for r in rows if r['category']=='school-trustees']
        self.assertEqual([len(employees),len(trustees)],[184,7])
        self.assertEqual(sum(Decimal(r['remuneration']) for r in employees),Decimal('19422067.55'))
        self.assertEqual(sum(Decimal(r['expenses']) for r in employees),Decimal('230923.87'))
        self.assertEqual(sum(Decimal(r['expenses']) for r in trustees),Decimal('43932.02'))
        self.assertEqual(next(c for c in controls if c['scope']=='school-trustees')['literalPrintedControls'],['102893.49','43923.02'])

    def test_sd84_source_dashes_stay_null_and_trustee_titles_stay_undisclosed(self):
        rows,evidence,_=build.scanned(84,None)
        self.assertEqual(len(rows),46)
        self.assertEqual(sum(r['expenses'] is None for r in rows),14)
        self.assertTrue(all(r['position'] is None for r in rows if r['category']=='school-trustees'))
        self.assertTrue(any(a['after'] is None and str(a['before']).startswith('UNRESOLVED:') for a in evidence['sourceImageAmendments']))

    def test_separate_source_spacing_reads_add_no_letters_or_identity(self):
        rows,evidence,_=build.scanned(53,None)
        self.assertEqual(rows[48]['name'],'DELL, LISA A')
        self.assertEqual(rows[76]['name'],'HUTCHISON, NIKKI L')
        for seq in [49,77]:
            a=next(a for a in evidence['sourceImageAmendments'] if a['reader']=='tesseract' and a['sequence']==seq and a['field']=='name')
            self.assertTrue(build.equal([a['before']],[a['after']]))

    def test_root_clipped_prefixes_never_expand_hidden_title_text(self):
        peer=json.loads((AREA.parent/'reviews/root-five-native-school-source-review.json').read_bytes())
        c=next(c for c in json.loads((AREA/'native-specs.json').read_bytes()) if c['districtNumber']==34)
        rows,_,_=build.native(c,peer)
        self.assertEqual(next(r for r in rows if r['name']=='Frost, Shelly')['position'],'Senior Manager,Budget & Stude')
        self.assertEqual(next(r for r in rows if r['name']=='Senft, Andrea')['position'],'Manager, Early Learning & Child')
        changed=copy.deepcopy(c);changed['sourceUrl']='https://example.invalid/wrong-original.pdf'
        with self.assertRaises(AssertionError):build.native(changed,peer)


if __name__=='__main__':unittest.main()
