#!/usr/bin/env python3
"""Actual original-page regressions for the independent PHSA OCR workflow."""
import gzip
import hashlib
import json
import unittest
from pathlib import Path

import resolve_held_health_ocr as workflow
import resolve_held_health_overlays as overlays
import resolve_held_health_name_amendments as amendments


class HeldHealthOcr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=workflow.ROOT/'research/salaries/held-resolution-health/evidence/phsa-fy2024-25-ocr-p001.json.gzip'
        cls.evidence=json.loads(gzip.decompress(p.read_bytes()))
        cls.fixture=json.loads(gzip.decompress(workflow.FIXTURE.read_bytes()))['rows']

    def test_actual_native300_independent_rows_and_fixture(self):
        e=self.evidence
        rapid,_=workflow.rapid_rows(e['rapidocrRaw'],*e['imageDimensions'])
        tess,_=workflow.tess_rows(e['tesseractRawTsv'],*e['imageDimensions'])
        self.assertEqual(len(rapid),49)
        self.assertEqual(len(tess),49)
        self.assertEqual(e['pageConflicts'],[])
        escaped=[]
        for row,fixture in zip(e['rowEvidence'],self.fixture):
            self.assertEqual(row['candidateRow'][3:5],fixture[3:5])
            if row['candidateRow']!=fixture and not row['conflicts']:
                escaped.append(row)
        self.assertEqual(escaped,[])
        wrong=[r for r,f in zip(e['rowEvidence'],self.fixture) if r['candidateRow'][1]!=f[1]]
        self.assertEqual(len(wrong),1)
        self.assertIn('name-disagreement',wrong[0]['conflicts'])
        self.assertEqual(wrong[0]['candidateRow'][1],'Abubakar,lbrahim')

    def test_all18_explicit_dashes_match_reviewed_original_pixels(self):
        dash=[r for r,f in zip(self.evidence['rowEvidence'],self.fixture) if f[4] is None]
        self.assertEqual(len(dash),18)
        for row in dash:
            image=row['expenseOriginalImage']
            self.assertEqual((image['glyphWidth'],image['glyphHeight'],image['blackPixels']),(9,2,18))
            digest=hashlib.sha256(workflow.encode([image['glyphWidth'],image['glyphHeight'],image['packedMask']])).hexdigest()
            self.assertEqual(digest,workflow.DASH_MASK_SHA)
            self.assertTrue(image['isExplicitDash'])
            self.assertIsNone(row['candidateRow'][4])

    def test_unrecognized_amount_is_never_zero(self):
        self.assertEqual(workflow.money_token('0')['value'],0)
        self.assertEqual(workflow.money_token('-')['kind'],'explicit-dash')
        self.assertIsNone(workflow.money_token('-')['value'])
        self.assertEqual(workflow.money_token('')['kind'],'not-recognized')
        self.assertEqual(workflow.money_token('™m')['kind'],'unparsed')
        self.assertEqual(workflow.money_token('(812)')['value'],-812)

    def test_comparison_does_not_join_words_or_infer_letters(self):
        self.assertEqual(workflow.name_comparison('Abbas, Harun Nisha'),'Abbas,Harun Nisha')
        self.assertNotEqual(workflow.name_comparison('AbouMourad,YasserRifaat'),'Abou Mourad,Yasser Rifaat')
        self.assertNotEqual(workflow.name_comparison('Abubakar,lbrahim'),'Abubakar,Ibrahim')
        self.assertNotEqual(workflow.name_comparison('Jose'),'José')

    def test_real_guarded_money_and_name_repairs_remain_separate_from_raw(self):
        p=workflow.ROOT/'research/salaries/held-resolution-health/evidence/verified-real-ocr-repair-cases.json.gzip'
        cases=json.loads(gzip.decompress(p.read_bytes()))
        for case in cases:
            before=list(case['rawCandidateRow'])
            result=overlays.apply_verified_values(case['rawCandidateRow'],case['requestedFields'],case['resolvedValues'])
            self.assertEqual(result,case['resolvedRow'])
            self.assertEqual(case['rawCandidateRow'],before)
        henry=next(c for c in cases if c['rawCandidateRow'][1]=='Henry,Laura')
        self.assertEqual(henry['rawCandidateRow'][3],55479)
        self.assertEqual(henry['resolvedRow'][3],95479)
        conklin=next(c for c in cases if c['rawCandidateRow'][1]=='Conklin,James')
        self.assertIsNone(conklin['rawCandidateRow'][4])
        self.assertEqual(conklin['resolvedRow'][4],7487)
        dao=next(c for c in cases if c['rawCandidateRow'][1]=='Dao,Le Nguyen')
        self.assertIsNone(dao['rawCandidateRow'][4])
        self.assertEqual(dao['resolvedRow'][4],2717)

    def test_incomplete_or_wrong_field_review_stays_held(self):
        candidate=['provincial-health-services-authority','Henry,Laura',None,55479,None,100]
        with self.assertRaises(ValueError):
            overlays.apply_verified_values(candidate,['remuneration'],{'expenses':95479})
        with self.assertRaises(ValueError):
            overlays.apply_verified_values(candidate,['remuneration'],{'remuneration':None})
        with self.assertRaises(ValueError):
            overlays.apply_verified_values(candidate,['expenses'],{'expenses':False})

    def test_actual_shared_engine_name_escape_requires_separate_image_amendment(self):
        p=workflow.ROOT/'research/salaries/held-resolution-health/evidence/phsa-fy2024-25-ocr-p180.json.gzip'
        raw=json.loads(gzip.decompress(p.read_bytes()))['rowEvidence'][7]
        self.assertEqual(raw['candidateRow'][1],'Muir,lan')
        self.assertEqual(workflow.name_comparison(raw['tesseract']['name']),
                         workflow.name_comparison(raw['rapidocr']['name']))
        ordinary=json.loads((amendments.AUDIT/'manual-overlay-008.json').read_text())
        prior=next(r for r in ordinary['overlays'] if (r['physicalPage'],r['sourceRowOnPage'])==(180,8))
        self.assertEqual(prior['reviewedFields'],['remuneration'])
        self.assertEqual(prior['resolvedRow'][1],'Muir,lan')
        ledger=amendments.aggregate(check=True)
        self.assertEqual(len(ledger['amendments']),44)
        cases=[r for r in ledger['amendments'] if (r['physicalPage'],r['sourceRowOnPage'])==(180,8)]
        self.assertEqual(len(cases),1)
        self.assertEqual(cases[0]['beforeOrdinaryResolvedRow'][1],'Muir,lan')
        self.assertEqual(cases[0]['afterSupplementalRow'][1],'Muir,Ian')
        for case in ledger['amendments']:
            self.assertEqual(case['changedColumns'],[1])
            self.assertEqual([case['beforeOrdinaryResolvedRow'][i] for i in [0,2,3,4,5]],
                             [case['afterSupplementalRow'][i] for i in [0,2,3,4,5]])
        preserved=ledger['confirmedUnchanged']
        self.assertEqual({r['literalImageName'] for r in preserved},
                         {'de la Chevrotiere,Ginette','de la Rosa,Victor Manuel',
                          'Gallaza,Victoria louise Quijano'})
        for case in preserved:
            self.assertEqual(case['beforeRow'],case['confirmedRow'])
            self.assertEqual(case['changedColumns'],[])


if __name__=='__main__':
    unittest.main()
