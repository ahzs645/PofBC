#!/usr/bin/env python3
"""Regression checks for real source hazards and complete evidence replay."""
import gzip
import json
import unittest

import continue_schools as s

class SchoolSchedules(unittest.TestCase):
    def test_missing_zero_and_negative_signs(self):
        for value in ['', '-', '$ -', '‐', '–', '—']:
            self.assertIsNone(s.decimal(value))
        self.assertEqual(s.decimal('$0.00'),'0.00')
        self.assertEqual(s.decimal('$542.93-'),'-542.93')
        self.assertEqual(s.decimal('(712)'),'-712')
        self.assertEqual(s.decimal('$ - *'),None)

    def test_scope_transitions_and_under_threshold_control(self):
        text='''Elected Officials
Alpha, A.       15,000.00       20.00
Total Elected Officials        15,000.00        20.00
Detailed Employees Exceeding $75,000
Beta, B.        100,000.00      0.00
Beta, B.        100,000.00      0.00
Total Detailed Employees Exceeding $75,000   200,000.00    0.00
Total Detailed Employees Equal to or Less Than $75,000  50,000.00  30.00
'''
        rows,controls=s.parse_poppler(text,{'pages':[1],'positions':False})
        self.assertEqual([r['category'] for r in rows],['school-trustees','employee-remuneration','employee-remuneration'])
        self.assertEqual(controls['employee-remuneration'],['200000.00','0.00'])
        self.assertEqual(len(rows),3)  # Repeated source rows retain multiplicity.

    def test_unparsed_published_name_is_blocking(self):
        text='Detailed Employees Exceeding $75,000\nMACRAILD PETER     105,732     0\n'
        with self.assertRaisesRegex(ValueError,'Unparsed potential named row'):
            s.parse_poppler(text,{'pages':[1],'positions':False})
        rows,_=s.parse_poppler(text,{'pages':[1],'positions':False,'literalNamesWithoutComma':['MACRAILD PETER']})
        self.assertEqual(rows[0]['name'],'MACRAILD PETER')

    def test_extra_compensation_component_cannot_be_expense(self):
        text='Detailed Employees Exceeding $75,000\nAlpha, A.  100,000.00  5,000.00  900.00\n'
        with self.assertRaisesRegex(ValueError,'Unexpected monetary components'):
            s.parse_poppler(text,{'pages':[1],'positions':False})

    def test_unknown_expense_control_is_not_zero(self):
        text='Elected Officials\nAlpha, A.   15,000.00  -\nTotal for Elected Officials  15,000.00  -\n'
        rows,controls=s.parse_poppler(text,{'pages':[1],'positions':False})
        self.assertIsNone(rows[0]['expenses'])
        self.assertEqual(controls['school-trustees'],['15000.00',None])

    def test_conflicting_period_and_hybrid_scan_review_guards(self):
        accepted=json.loads((s.COLLECTION/'sources.json').read_text())['sources']
        held=json.loads((s.INVENTORY/'held-candidates.json').read_text())
        self.assertFalse(any(r['inputKey']=='sd08-2026' and r['category']=='employee-remuneration' for r in accepted))
        conflict=next(r for r in held if r['inputKey']=='sd08-2026' and r['category']=='employee-remuneration')
        self.assertEqual(conflict['validation']['periodHeadingConflict']['pdfPage'],52)
        hybrid=next(r for r in held+accepted if r['inputKey']=='sd08-2019' and r['category']=='employee-remuneration')
        self.assertTrue(hybrid['completeEmployeeSchedule'])
        self.assertTrue(hybrid['validation']['completeEmployeeSchedule'])
        self.assertEqual(hybrid['rowCount'],209)
        self.assertEqual(hybrid['sourceKind'],'official-hybrid-pdf')
        proof=json.loads(gzip.decompress((s.COLLECTION/hybrid['validation']['scannedSupplementEvidence'][0]['file']).read_bytes()))
        fields=['name','position','remuneration','expenses','pdfPage']
        self.assertEqual([[r[k] for k in fields] for r in proof['manualRows']],[[r[k] for k in fields] for r in s.scanned_ocr_rows(proof['ocrText'],13)])

    def test_all_accepted_evidence_replays_offline(self):
        manifest=json.loads((s.COLLECTION/'sources.json').read_text())
        for source in manifest['sources']:
            with self.subTest(source=source['id']):
                packed=(s.COLLECTION/source['provenanceFile']).read_bytes()
                self.assertEqual(s.sha(packed),source['provenanceSha256'])
                s.verify_evidence(source,json.loads(gzip.decompress(packed)))

    def test_qualified_acceptance_and_only_remaining_period_hold(self):
        accepted=json.loads((s.COLLECTION/'sources.json').read_text())['sources']
        held=json.loads((s.INVENTORY/'held-candidates.json').read_text())
        self.assertEqual([(r['id'],r['rowCount']) for r in held],[('continuation-schools-sd08-2026-employees',340)])
        qualified=[r for r in accepted if any(x is not None and float(x)!=0 for x in r['validation']['controlResiduals'])]
        self.assertEqual(len(qualified),11)
        queue=json.loads((s.INVENTORY/'work-queue.json').read_text())
        for source in qualified:
            self.assertEqual(source['status'],'verified')
            self.assertFalse(source['validation']['summaryReconciles'])
            self.assertFalse(source['validation']['allPublishedNamedControlsExact'])
            self.assertTrue(source['publicWarning'])
            self.assertIn('independentQualificationAcceptance',source['validation'])
            self.assertFalse(any('parent' in note.lower() for note in source['notes']))
            clarification=next(r for r in queue if r['id'].endswith(source['id'].replace('continuation-schools-','')+'-issuer-clarification'))
            self.assertEqual(clarification['status'],'accepted-observations-unresolved-issuer-controls')
            self.assertEqual(clarification['route'],'clarification-request')
        hybrid=next(r for r in accepted if r['id']=='continuation-schools-sd08-2019-employees')
        self.assertEqual(hybrid['rowCount'],209)
        self.assertTrue(hybrid['completeEmployeeSchedule'])
        self.assertTrue(hybrid['validation']['completeEmployeeSchedule'])

    def test_all_sixty_districts_and_queue_routes(self):
        inventory=json.loads((s.INVENTORY/'inventory.json').read_text())
        self.assertEqual(len(inventory['employers']),60)
        self.assertEqual(len({e['districtNumber'] for e in inventory['employers']}),60)
        keys={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}
        queue=json.loads((s.INVENTORY/'work-queue.json').read_text())
        self.assertEqual(len({r['id'] for r in queue}),len(queue))
        for row in queue:
            self.assertEqual(set(row),keys)
            self.assertIn(row['route'],['processing','public-archive-research','ordinary-records-request','clarification-request','foi-fallback'])

if __name__=='__main__':unittest.main()
