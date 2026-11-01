#!/usr/bin/env python3
"""Regression fixtures for the real contradictory-year source resolution."""
import copy
import gzip
import json
import unittest

import resolve_held_schools as s
import resolve_held_schools_sd08 as native


class HeldSchoolResolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=json.loads((s.COLLECTION/'sources.json').read_text())['sources']
        cls.proofs={r['id']:json.loads(gzip.decompress((s.COLLECTION/r['provenanceFile']).read_bytes())) for r in cls.sources}

    def test_complete_offline_payload_and_provenance_replay(self):
        self.assertEqual(len(self.sources),3)
        self.assertEqual(sum(r['rowCount'] for r in self.sources),398)
        for source in self.sources:
            self.assertEqual(s.sha((s.COLLECTION/source['provenanceFile']).read_bytes()),source['provenanceSha256'])
            proof=self.proofs[source['id']]
            if source['id']==native.ID:native.verify_source(source,proof)
            else:s.verify_source(source,proof)

    def test_sd10_explicit_salary_year_does_not_establish_conflicting_approval(self):
        for source in self.sources[:2]:
            self.assertEqual(source['periodEnd'],'2025-06-30')
            self.assertEqual(source['validation']['conflictingDeclarationPeriodEnd'],'2024-06-30')
            self.assertFalse(source['validation']['approvalFor2025Established'])
            self.assertIn('December 18, 2024',source['publicWarning'])
            self.assertIn('approval/adoption of the 2025 SOFI is not established',source['publicWarning'])

    def test_two_independent_ocr_engines_never_adjust_money(self):
        proof=self.proofs['held-resolution-schools-sd10-2025-employees']
        corrections=proof['explicitImageVerifiedCorrections']
        self.assertEqual({c['engine'] for c in corrections},{'Tesseract','RapidOCR'})
        self.assertTrue(all(c['field'] in ['name','position'] for c in corrections))
        self.assertEqual(len(s.tesseract_rows(proof['rawTesseractPageTexts'])),58)
        self.assertEqual(len(s.rapid_rows(proof['rawRapidPageResults'])),58)

    def test_literal_clipped_titles_and_glyphs_survive(self):
        rows=self.proofs['held-resolution-schools-sd10-2025-employees']['rows']
        names={r['name']:r for r in rows}
        self.assertEqual(names['Mervyn, Stephanie']['position'],'TEACHERS, TEACH ON')
        self.assertEqual(names['Smedbol, Naomi']['position'],'TEACHERS, TEACHER ON')
        self.assertIn('Momeyer, Erika C.',names)
        self.assertIn('McLellan, Michael',names)
        self.assertEqual(names['Kipkie, Scott']['expenses'],'0.00')

    def test_sd8_uses_final_payment_pages_with_complete_dated_corroboration(self):
        source=next(r for r in self.sources if r['id']==native.ID);proof=self.proofs[native.ID]
        self.assertEqual(source['sha256'],native.FINAL_SHA)
        self.assertEqual(source['pages'],list(range(51,60)))
        self.assertIn('June 30, 2025',proof['fullSourcePagesPopplerText']['52'])
        self.assertIn('June 30, 2026',proof['agendaContextPagesPopplerText']['186'])
        self.assertEqual(proof['agendaToFinalComparison']['rowsCompared'],340)
        self.assertEqual(source['dataSha256'],'d88fecc9e02f2f9c3942796ec2d01e9a4e5025cbe9fbf58b417deda317d4e2c3')
        self.assertTrue(all(b['pdfPage']==a['pdfPage']+134 for a,b in zip(proof['rows'],proof['agendaCorroborationRows'])))

    def test_sd8_draft_financial_context_is_not_promoted_to_payment_original(self):
        source=next(r for r in self.sources if r['id']==native.ID)
        self.assertTrue(source['validation']['agendaFinancialStatementSubsectionMarkedDraft'])
        self.assertFalse(source['validation']['agendaSalaryPagesMarkedDraft'])
        self.assertFalse(source['validation']['chosenPaymentSourceMarkedDraft'])
        self.assertFalse(source['validation']['SOFIAdoptionMotionEstablished'])

    def test_sd8_nulls_scope_and_unresolved_reconciliation_are_literal(self):
        source=next(r for r in self.sources if r['id']==native.ID);rows=self.proofs[native.ID]['rows']
        self.assertTrue(all(r['position'] is None for r in rows))
        self.assertEqual(sum(r['expenses'] is None for r in rows),198)
        self.assertTrue(source['validation']['allPublishedNamedControlsExact'])
        self.assertFalse(source['validation']['allPrintedComponentControlsExact'])
        self.assertEqual(source['validation']['aggregateReconciliationPrintedMinusScheduleControls'],['-14','390'])
        self.assertIn('cause is unresolved',source['publicWarning'])
        self.assertFalse(any(r['employerSlug']=='school-district-08' and r['category']=='school-trustees' for r in self.sources))

    def test_changed_row_cannot_pass(self):
        source=self.sources[0];proof=copy.deepcopy(self.proofs[source['id']]);proof['rows'][0]['remuneration']='0'
        with self.assertRaises(AssertionError):s.verify_source(source,proof)

    def test_changed_queue_has_exact_eleven_key_schema(self):
        queue=json.loads((s.RESEARCH/'work-queue.json').read_text())
        keys={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
        self.assertEqual(len(queue),4)
        for row in queue:self.assertEqual(set(row),keys)


if __name__=='__main__':unittest.main()
