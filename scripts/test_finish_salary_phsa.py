#!/usr/bin/env python3
"""Real-source PHSA regressions; stdlib only, no OCR/Pillow/numpy CI dependency."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest import mock

import finish_salary_phsa_rows as readers
import finish_salary_phsa_geometry as geometry
import finish_salary_phsa_policy as policy
import finish_salary_phsa_resolutions as resolutions
import finish_salary_phsa_batches as batches
import finish_salary_phsa_finalize as finalizer
import finish_salary_phsa_ledger as field_ledger
import finish_salary_phsa_triangulation as triangulation
import finish_salary_phsa_supersessions as supersessions
import finish_salary_phsa_money_peer as money_peer
import finish_salary_phsa_promote as promotion
import finish_salary_phsa_adoption_supersessions as adoption_revisions
import finish_salary_phsa_direct_money_peer as direct_money
import finish_salary_phsa_money_supersessions as money_revisions
import finish_salary_phsa_money_canonical as canonical_money
import finish_salary_phsa_canonical_supplements as canonical_supplements
import finish_salary_phsa_current_canonical as current_canonical
import finish_salary_phsa_money_provenance as money_provenance
import finish_salary_phsa_money_sparse_current as sparse_current

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
EVIDENCE=ROOT/'research/salaries/queue-completion-phsa/evidence'


def load(path):return json.loads(gzip.decompress(path.read_bytes()))


class PhsaHistorical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures=[]
        for p in sorted((AREA/'overlays').glob('*-first-table-image-overlay.json')):
            overlay=json.loads(p.read_text());proof=ROOT/overlay['overlays'][0]['pageEvidencePath']
            page=load(proof);raw=load(ROOT/page['rawPage']['path'])
            profile=json.loads((AREA/(overlay['sourceId']+'-processing-profile-001.json')).read_text())
            cls.fixtures.append((overlay,page,raw,profile))
        cls.page=cls.fixtures[0][1];cls.row=cls.page['rows'][0]

    def test_all_nine_real_first_tables_have_complete_independent_rows(self):
        self.assertEqual(len(self.fixtures),9)
        self.assertEqual([o['resolvedRows'] for o,_,_,_ in self.fixtures],[36,36,37,55,58,55,44,42,42])
        for overlay,page,raw,profile in self.fixtures:
            tess,_,_=readers.read_tesseract(raw,profile);rapid,_,_=readers.read_rapid(raw,profile)
            self.assertEqual(len(tess),overlay['resolvedRows'])
            self.assertEqual(len(rapid),overlay['resolvedRows'])
            self.assertFalse(page['pageGeometryNeedsReview'])
            self.assertFalse(any(r['name'].startswith('This statement') for r in tess+rapid))

    def test_actual_literal_quote_in_tsv_never_swallows_later_employees(self):
        _,_,raw,profile=self.fixtures[1]
        tess,_,_=readers.read_tesseract(raw,profile)
        self.assertIn('"9,337',raw['tesseractRawTsv'])
        self.assertEqual(len(tess),36)
        self.assertEqual(readers.name_comparison(tess[-1]['name']),'Ahuja,Jagvinder K.')
        self.assertEqual(tess[15]['pay']['kind'],'unparsed')
        self.assertIsNone(tess[15]['pay']['value'])

    def test_real_205_dashes_and_200_numeric_expenses_are_distinguished(self):
        dash=numeric=0
        for overlay,page,_,profile in self.fixtures:
            for row,truth in zip(page['rows'],overlay['overlays']):
                observed=geometry.is_source_dash(row['expenseOriginalImage'],profile['dashCalibration'])
                if truth['resolvedRow'][4] is None:
                    dash+=1;self.assertTrue(observed)
                else:numeric+=1;self.assertFalse(observed)
        self.assertEqual((dash,numeric),(205,200))

    def test_all_real_benchmark_eligible_fields_match_independent_image_truth(self):
        eligible=0
        for overlay,page,_,_ in self.fixtures:
            for row,truth in zip(page['rows'],overlay['overlays']):
                classified=policy.classify(row,page)
                for field,index in policy.FIELD_INDEX.items():
                    if classified['fields'][field]['eligibleToResolveUnreservedConfidenceOnly']:
                        expected=truth['resolvedRow'][index]
                        if field=='name':expected=readers.name_comparison(expected)
                        self.assertEqual(classified['fields'][field]['value'],expected)
                        eligible+=1
        self.assertGreater(eligible,300)

    def test_explicit_source_spelling_is_not_dictionary_expanded(self):
        overlay=next(o for o,_,_,_ in self.fixtures if o['sourceId']=='phsa-2022-23')
        row=next(r for r in overlay['overlays'] if r['sourceRowOnPage']==35)
        self.assertEqual(row['resolvedRow'][1],'Adams,Bradley Willam')
        self.assertNotEqual(readers.name_comparison('Bradley Willam'),readers.name_comparison('Bradley William'))

    def test_policy_confidence_allowlist_and_strict_both_reader_candidate_types(self):
        row=copy.deepcopy(self.row)
        row['fieldConflicts']['expenses']=['tesseract-expense-confidence-below-90']
        row['tesseract']['expense']={'kind':'number','value':1,'raw':'1'}
        row['rapidocr']['expense']={'kind':'number','value':1,'raw':'1'}
        row['candidateRow'][4]=1
        self.assertTrue(policy.classify(row,self.page)['fields']['expenses']['eligibleToResolveUnreservedConfidenceOnly'])
        for target in ['tesseract','rapidocr','candidate']:
            for invalid in [True,1.0,0,-1,None]:
                bad=copy.deepcopy(row)
                if target=='candidate':bad['candidateRow'][4]=invalid
                else:bad[target]['expense']['value']=invalid
                result=policy.classify(bad,self.page)
                self.assertFalse(result['fields']['expenses']['eligibleToResolveUnreservedConfidenceOnly'])
                self.assertIn('expenses',result['manualFieldsBeforeExistingReviewCoverage'])
        bad=copy.deepcopy(row);bad['fieldConflicts']['expenses']=['unparsed-confidence-below-unknown']
        self.assertFalse(policy.classify(bad,self.page)['fields']['expenses']['eligibleToResolveUnreservedConfidenceOnly'])

    def test_name_quality_guards_preserve_source_fragments_and_punctuation_boundaries(self):
        for name in ["D'Iorio,Anna",'D’Iorio,Anna','Gfeller-Ingledew,Paris-Ann PA',
                     'McIlwaine,Anna','Mcllwaine,Anna','Zulfiqar,Muhammad*',
                     'Example,Name!','Example,Name¥','Example,Name§','Example,Name]']:
            row=copy.deepcopy(self.row);row['candidateRow'][1]=name
            row['tesseract']['name']=name;row['rapidocr']['name']=name
            row['fieldConflicts']['name']=['tesseract-name-confidence-below-85']
            result=policy.classify(row,self.page)
            self.assertIn('name',result['manualFieldsBeforeExistingReviewCoverage'])
            self.assertEqual(row['candidateRow'][1],name)
        self.assertEqual(policy.extra_name_guard('García,Ana'),[])

    def test_field_reviews_never_widen_scope_or_rewrite_other_columns(self):
        before=['provincial-health-services-authority','Henry,Laura',None,55479,None,104]
        after=resolutions.apply_values(before,['remuneration'],{'remuneration':95479})
        self.assertEqual(after[3],95479);self.assertEqual(before[3],55479)
        self.assertEqual([before[i] for i in [0,1,2,4,5]],[after[i] for i in [0,1,2,4,5]])
        with self.assertRaises(ValueError):resolutions.apply_values(before,['remuneration'],{'expenses':95479})
        with self.assertRaises(ValueError):resolutions.apply_values(before,['expenses'],{'expenses':True})

    def test_only_full_candidate_manifests_count_as_review_batches(self):
        paths=batches.full_batch_paths(AREA/'batches','phsa-2015-16')
        self.assertTrue(paths)
        self.assertFalse(any('images' in p.name or 'target-views' in p.name for p in paths))
        seen=set()
        for p in paths:
            batch=json.loads(p.read_text())
            for row in batch['rows']:
                for field in row['reviewTargetFields']:
                    key=(row['physicalPage'],row['sourceRowOnPage'],field)
                    self.assertNotIn(key,seen);seen.add(key)

    def test_finite_rn_m_qualification_never_authorizes_other_letters_or_expansion(self):
        # Native low-resolution rn may join into m; this validates only a
        # declared pair, never selects the dictionary-looking alternative.
        self.assertEqual(resolutions.segmentation_difference('Turner,Anna','Tumer,Anna'),[
            {'primaryStartZeroBased':2,'alternativeStartZeroBased':2,'primaryVisibleSegment':'rn','alternativeVisibleSegment':'m'}])
        self.assertEqual(resolutions.segmentation_difference('Tumer,Anna','Turner,Anna')[0]['primaryVisibleSegment'],'m')
        for primary,alternative in [('Turner,Anna','Turner,Anne'),('Tumer,Ann','Turner,Anna'),
                                    ('Turner,Ian','Tumer,lan'),('Turner,Anna','Turner,Anna')]:
            with self.assertRaises(ValueError):resolutions.segmentation_difference(primary,alternative)

    def test_one_closed_source_case_cannot_add_alternatives_or_move_scope(self):
        reference={'path':'research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-history-2019-20-001-seq203-exact-source-ambiguity-ledger.json',
                   'sha256':'f781f5c14be0a38a56a8888f7c73d26bfbef68eae63190ddbdd38a61427c1e2c'}
        review={'sourceId':'phsa-2019-20','sourceSha256':'0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02',
                'batch':'phsa-2019-20-001','closedSourceNameQualificationLedgers':[reference]}
        exact=resolutions.closed_source_cases(review)[(7,7)]
        self.assertEqual(exact['chosenName'],'Bangham,Tanni Debora')
        self.assertEqual(exact['authorizedFields'],['name'])
        self.assertEqual(len(exact['visibleAlternatives']),4)
        original=resolutions.pinned
        for fault in ['extra-alternative','unknown-row','changed-primary','changed-crop']:
            def changed(path,digest):
                value=copy.deepcopy(original(path,digest))
                if str(path)==str(ROOT/reference['path']):
                    case=value['sourceNameSegmentationExceptions'][0]
                    if fault=='extra-alternative':case['visibleAlternatives'].append('Bangham,Tanya Debora')
                    elif fault=='unknown-row':case['sourceRowOnPage']=8
                    elif fault=='changed-primary':case['proposedName']='Bangham,Tanya Debora'
                    else:case['actualSourceEvidence']['originalFullRowCropSha256']='0'*64
                return value
            with mock.patch.object(resolutions,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):resolutions.closed_source_cases(review)
        wrong=copy.deepcopy(review);wrong['batch']='phsa-2019-20-002'
        with self.assertRaises(ValueError):resolutions.closed_source_cases(wrong)
        # Name-only exception cannot carry an amount change through its scope.
        with self.assertRaises(ValueError):resolutions.apply_values(self.row['candidateRow'],['name'],{'name':exact['chosenName'],'remuneration':1})

    def test_distinct_preferred_name_readings_remain_an_exact_qualified_case(self):
        path=field_ledger.REVIEWS/'root-phsa-history-2022-23-batch-002-name394-exact-source-ambiguity-ledger.json'
        reference=field_ledger.pin(path);source=field_ledger.pinned(reference)
        review={k:source[k]for k in ['sourceId','sourceSha256','batch']}
        review['closedSourceNameQualificationLedgers']=[reference]
        exact=resolutions.closed_source_cases(review)[(106,17)]
        self.assertEqual(exact['chosenName'],'Lambi-Raine,Dylan Elizabeth Kann')
        self.assertEqual(set(exact['visibleAlternatives']),{'Lambi-Raine,Dylan Elizabeth Karn','Lambi-Raine,Dylan Elizabeth Kam'})
        self.assertFalse(exact['caseProvenByPixels'])
        self.assertIn('peer preferred Kam',exact['assumptionBasis'])
        with self.assertRaises(ValueError):resolutions.segmentation_difference('Kann','Karn')
        with self.assertRaises(ValueError):resolutions.apply_values(self.row['candidateRow'],['name'],{'name':exact['chosenName'],'expenses':1})

    def test_explicit_source_observation_is_basis_but_missing_context_still_fails(self):
        path=field_ledger.REVIEWS/'root-phsa-history-2019-20-batch-004-fourteen-source-segmentation-cases.json'
        reference=field_ledger.pin(path);document=field_ledger.pinned(reference)
        review={k:document[k]for k in ['sourceId','sourceSha256','batch']}
        review['sourceTypographyQualifications']=reference
        qualified=resolutions.typography_cases(review)
        self.assertEqual(len(qualified),14)
        self.assertEqual(qualified[(21,49)]['assumptionBasis'],document['qualifications'][0]['ownSourceObservation'])
        actual=resolutions.pinned
        def no_context(candidate,digest):
            value=copy.deepcopy(actual(candidate,digest))
            if candidate==path:value['qualifications'][0]['ownSourceObservation']=''
            return value
        with mock.patch.object(resolutions,'pinned',side_effect=no_context):
            with self.assertRaises(ValueError):resolutions.typography_cases(review)

    def test_four_new_closed_cases_do_not_expand_generic_rn_m_policy(self):
        path=field_ledger.REVIEWS/'independent-phsa-history-batches-2019-20-007-effective-twentyfour-plus-four-name-ledger.json'
        reference=field_ledger.pin(path);document=field_ledger.pinned(reference)
        review={k:document[k]for k in ['sourceId','sourceSha256','batch']}
        review['closedSourceNameQualificationLedgers']=[reference]
        cases=resolutions.closed_source_cases(review)
        self.assertEqual(set(cases),{(46,54),(47,46),(50,1),(50,4)})
        case=cases[(50,1)]
        self.assertEqual(case['chosenName'],'Jakkavannangsri,Simon')
        self.assertEqual(case['visibleAlternatives'],['Jakkavanrangsri,Simon'])
        self.assertFalse(case['caseProvenByPixels'])
        with self.assertRaises(ValueError):resolutions.segmentation_difference(case['chosenName'],case['visibleAlternatives'][0])

    def test_exact_six_case_root_count_cannot_omit_or_widen_the_pinned_ledger(self):
        path=field_ledger.REVIEWS/'root-phsa-history-2019-20-batch-010-six-closed-exact-source-ledger.json'
        reference=field_ledger.pin(path);document=field_ledger.pinned(reference)
        review={k:document[k]for k in ['sourceId','sourceSha256','batch']}
        review['closedSourceNameQualificationLedgers']=[reference]
        qualified=resolutions.closed_source_cases(review)
        self.assertEqual(len(qualified),6)
        case=next(c for c in qualified.values()if c['chosenName']=='Li,Xim')
        self.assertEqual(set(case['visibleAlternatives']),{'Li,Xiru','Li,Xiu','Li,Xm','Li,Xin'})
        actual=resolutions.pinned
        for fault in ['count','unknown-alternative','wrong-crop']:
            def changed(candidate,digest):
                value=copy.deepcopy(actual(candidate,digest))
                if fault=='count'and candidate.name=='root-phsa-history-2019-20-batch-010-six-name-exact-adoption.json':
                    value['qualifiedCases']=5
                if candidate==path:
                    if fault=='unknown-alternative':value['sourceNameSegmentationExceptions'][0]['visibleAlternatives'].append('Li,Unprinted')
                    if fault=='wrong-crop':value['sourceNameSegmentationExceptions'][0]['cropSha256']='0'*64
                return value
            with mock.patch.object(resolutions,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):resolutions.closed_source_cases(review)

    def test_finalizer_fails_closed_on_pending_nonfield_drift_and_unreviewed_money(self):
        row={'row':[self.row['candidateRow'][0],'Literal,Name',None,100000,None,2],
             'rawCandidateRow':[self.row['candidateRow'][0],'Literal,Name',None,100000,None,2],
             'sourceRowOnPage':1,'fields':{f:{'status':'baseline-independent-reader-agreement'} for f in policy.FIELD_INDEX}}
        row['fields']['expenses']['status']='original-source-explicit-dash-geometry'
        source={'sourceId':'test','sourceSha256':'testsha','completePhysicalSource':True,'pendingFields':[],'rowCount':1,'rows':[row],
                'physicalPages':[{'physicalPage':1,'rows':0},{'physicalPage':2,'rows':1}]}
        inventory={'id':'test','sourceSha256':'testsha','pdfPages':2}
        self.assertEqual(finalizer.validate_source(source,inventory)[0][3],100000)
        pending=copy.deepcopy(source);pending['pendingFields']=[{'field':'name'}]
        with self.assertRaises(ValueError):finalizer.validate_source(pending,inventory)
        drift=copy.deepcopy(source);drift['rows'][0]['row'][2]='Invented title'
        with self.assertRaises(ValueError):finalizer.validate_source(drift,inventory)
        money=copy.deepcopy(source);money['rows'][0]['row'][3]=0;money['rows'][0]['rawCandidateRow'][3]=0
        with self.assertRaises(ValueError):finalizer.validate_source(money,inventory)
        for fault in ['source','hash','row-count','page-count','row-sequence']:
            bad=copy.deepcopy(source)
            if fault=='source':bad['sourceId']='different'
            elif fault=='hash':bad['sourceSha256']='different'
            elif fault=='row-count':bad['physicalPages'][1]['rows']=2
            elif fault=='page-count':bad['physicalPages'].pop(0)
            else:bad['rows'][0]['sourceRowOnPage']=2
            with self.assertRaises(ValueError):finalizer.validate_source(bad,inventory)

    def test_exact_legacy_root_decision_keeps_14_cases_and_rejects_mutation(self):
        filename='root-phsa-history-2015-16-batch-001-typography-adoption.json'
        path=field_ledger.REVIEWS/filename
        adoptions=field_ledger.typography_adoptions()
        original_cases=json.loads(path.read_text())['cases']
        original_keys={(r['physicalPage'],r['sourceRowOnPage']) for r in original_cases}
        selected=[v for k,v in adoptions.items() if k[0]=='phsa-2015-16' and (k[1],k[2]) in original_keys]
        self.assertEqual(len(selected),14)
        self.assertTrue(all(v['sourceSha256']=='f8bc28af7e87f57c51973f5ed581e50fe414f00486659551ad5c8171b98f73a3' for v in selected))
        original=Path.read_bytes
        for fault in ['decision','cases','peer']:
            def changed(p):
                raw=original(p)
                if p==path:
                    value=json.loads(raw)
                    if fault=='decision':value['decision']='Not adopted'
                    elif fault=='cases':value['cases'].pop()
                    else:value['independentPeerSha256']='0'*64
                    return json.dumps(value).encode()
                return raw
            with mock.patch.object(Path,'read_bytes',changed):
                with self.assertRaises(ValueError):field_ledger.typography_adoptions()

    def test_actual_historical_money_repairs_remain_field_limited(self):
        path=AREA/'overlays/phsa-2015-16-manual-overlay-003.json'
        overlay=json.loads(path.read_text())
        by_key={(r['physicalPage'],r['sourceRowOnPage']):r for r in overlay['overlays']}
        for key,field,value in [((78,1),'expenses',5135),((79,1),'expenses',57),
                                ((82,18),'remuneration',77773),((111,16),'expenses',5579)]:
            row=by_key[key];index=policy.FIELD_INDEX[field]
            self.assertEqual(row['resolvedRow'][index],value)
            self.assertNotEqual(row['rawCandidateRow'][index],value)
            self.assertIn(field,row['reviewedFields'])
            self.assertEqual([row['resolvedRow'][i] for i in [0,2,5]],[row['rawCandidateRow'][i] for i in [0,2,5]])

    def test_holdout_source_identity_is_parsed_instead_of_filename_substring(self):
        paths=sorted(field_ledger.REVIEWS.glob('root-phsa-history-*-holdout-source-comparison.json'))
        pins=[field_ledger.pin(path) for path in paths]
        for source in ['phsa-2015-16','phsa-2016-17']:
            selected=finalizer.source_pins(pins,source)
            self.assertEqual(len(selected),1)
            receipt=field_ledger.pinned(selected[0])
            self.assertEqual(receipt['sourceId'],source)
            self.assertEqual(receipt['rows'],10)
            self.assertNotIn(source,Path(selected[0]['path']).name)

    def test_real_neither_reader_money_needs_exact_fresh_peer(self):
        page=load(EVIDENCE/'phsa-2016-17-rows-p028.json.gzip');row=page['rows'][27]
        self.assertFalse(triangulation.matches_reader(row,'remuneration',84876))
        confirmation=triangulation.confirmations()[('phsa-2016-17',28,28,'remuneration')]
        self.assertEqual(confirmation['confirmedValue'],84876)
        self.assertEqual(confirmation['sourceSha256'],page['sourceSha256'])
        self.assertEqual(Path(confirmation['effectiveAuthorOverlay']['path']).name,'phsa-2016-17-manual-overlay-001-v2-canonical.json')
        for filename in ['phsa-2016-17-manual-overlay-001.json','phsa-2016-17-manual-overlay-001-v2-canonical.json']:
            overlay=json.loads((AREA/'overlays'/filename).read_text())
            actual=next(r for r in overlay['overlays']if(r['physicalPage'],r['sourceRowOnPage'])==(28,28))
            self.assertEqual(actual['resolvedRow'][3],84876)
        self.assertIn('root-phsa-history-money-triangulation-001-peer-comparison.json',confirmation['peerComparison']['path'])

    def test_revised_overlay_cannot_change_original_field_or_row_scope(self):
        before=json.loads((AREA/'overlays/phsa-2015-16-manual-overlay-003.json').read_text());after=copy.deepcopy(before)
        old=ROOT/'old.json';new=ROOT/'new.json'
        sidecar={'sourceId':before['sourceId'],'sourceSha256':before['sourceSha256'],'batch':before['batch'],
                 'supersededOverlay':{'path':'old.json'},'effectiveOverlay':{'path':'new.json'},
                 'reason':'Source-peer reread corrects exact previously requested amounts','oldFrozenFilesRemainUnchanged':True}
        def loaded(reference):return (old,before)if reference['path']=='old.json'else(new,after)
        with mock.patch.object(supersessions,'load',side_effect=loaded):
            after['overlays'][0]['resolvedRow'][1]='Explicit source correction'
            self.assertEqual(supersessions.validate(sidecar),(old,new))
            after['overlays'][0]['reviewedFields'].append('unrequested-field')
            with self.assertRaises(ValueError):supersessions.validate(sidecar)
            after['overlays'][0]['reviewedFields'].pop();after['overlays'][0]['rawCandidateRow'][3]+=1
            with self.assertRaises(ValueError):supersessions.validate(sidecar)

    def test_author_money_error_does_not_override_correct_source_reader(self):
        page=load(EVIDENCE/'phsa-2019-20-rows-p012.json.gzip');row=page['rows'][40]
        self.assertTrue(triangulation.matches_reader(row,'remuneration',104307))
        self.assertFalse(triangulation.matches_reader(row,'remuneration',104807))
        overlay=json.loads((AREA/'overlays/phsa-2019-20-manual-overlay-002.json').read_text())
        final=next(r for r in overlay['overlays']if(r['physicalPage'],r['sourceRowOnPage'])==(12,41))
        self.assertEqual(final['resolvedRow'][3],104307)
        self.assertEqual(final['rawCandidateRow'][3],104307)
        raw=json.loads((field_ledger.REVIEWS/'author-phsa-history-2019-20-002-image-first-transcript.json').read_text())
        first=next(r for r in raw['rows']if r['sequence']==60)
        self.assertEqual(first['literalSourceValuesFirstPass']['remuneration'],104807)
        confirmed=triangulation.confirmations()[('phsa-2019-20',12,41,'remuneration')]
        self.assertEqual(confirmed['confirmedValue'],104307)

    def test_count_independent_money_peer_preserves_first_pass_errors_and_exact_scope(self):
        document=json.loads((AREA/'triangulation/money-peer-confirmations-003.json').read_text())
        reference=document['peerInputs'][0];overlay=document['confirmations'][0]['effectiveAuthorOverlay']
        replay=money_peer.build(reference,overlay)
        self.assertEqual(replay,document)
        self.assertEqual(replay['confirmedMonetaryFields'],38)
        self.assertEqual(replay['originalAuthorOwnSourceCorrections'],1)
        self.assertEqual(replay['originalPeerOwnSourceCorrections'],1)
        actual=field_ledger.pinned
        for fault in ['value','field','source','overlay','crop','incomplete','author-raw-history']:
            def altered(pin):
                value=copy.deepcopy(actual(pin))
                if pin==reference:
                    if fault=='value':value['rows'][0]['finalRootSourceReading']+=1
                    elif fault=='field':value['rows'][0]['field']='remuneration'
                    elif fault=='source':value['sourceSha256']='0'*64
                    elif fault=='crop':value['rows'][0]['sourceImageCropSha256']='0'*64
                    elif fault=='incomplete':value['rows'].pop()
                if pin==overlay and fault=='overlay':value['overlays'][0]['resolvedRow'][4]=99999
                if fault=='author-raw-history' and Path(pin['path']).name=='independent-phsa-history-batches-2019-20-003-original-transcript-v2.json':
                    value['rows'][0]['literalSourceValuesFirstPass']['expenses']+=1
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(reference,overlay)
        mixed=json.loads((AREA/'triangulation/money-peer-confirmations-004.json').read_text())
        self.assertEqual(money_peer.build(mixed['peerInputs'][0],mixed['confirmations'][0]['effectiveAuthorOverlay']),mixed)
        self.assertEqual(mixed['completeFrozenSourceTargetFields'],12)
        self.assertEqual(mixed['confirmedMonetaryFields'],4)
        self.assertEqual(mixed['originalAuthorOwnSourceCorrections'],7)
        actual_exists=Path.exists
        def unavailable_temporary_views(path):
            if str(path).startswith('/tmp/independent-phsa-history-2019-003-money-peer/'):
                return False
            return actual_exists(path)
        with mock.patch.object(Path,'exists',unavailable_temporary_views):
            self.assertEqual(money_peer.build(reference,overlay),document)

    def test_publication_cannot_promote_a_partial_or_unaccepted_source_set(self):
        reference={'path':'not-a-real-root-adoption.json','sha256':'0'*64}
        for receipt in [{'acceptedAllNineHistoricalPhsaSources':False,'sources':[]},
                        {'acceptedAllNineHistoricalPhsaSources':True,'sources':[]},
                        {'acceptedAllNineHistoricalPhsaSources':True,'sources':[{'sourceId':'phsa-2015-16'}]*9}]:
            with mock.patch.object(field_ledger,'pinned',return_value=receipt):
                with self.assertRaises(ValueError):promotion.build(reference)

    def test_complete_money_peer_preserves_literal_dash_and_all_reading_histories(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-009.json').read_text())
        reference=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(reference,overlay),doc)
        self.assertEqual((doc['completeFrozenSourceTargetFields'],doc['confirmedMonetaryFields']),(51,50))
        self.assertEqual(len(doc['literalSourceDashFieldsConfirmedSeparately']),1)
        self.assertTrue(all(type(r['confirmedValue'])is int and r['confirmedValue']>0 for r in doc['confirmations']))
        actual=field_ledger.pinned
        for fault in ['raw-first','raw-source','raw-sha','raw-batch','peer-first','intermediate','null-as-positive','source-pixel','missing-target']:
            def changed(pin):
                value=copy.deepcopy(actual(pin))
                if pin==reference:
                    if fault=='peer-first':value['rows'][0]['firstPeerSourceValue']+=1
                    elif fault=='intermediate':value['rows'][0]['intermediateAuthorSourceValue']+=1
                    elif fault=='null-as-positive':
                        dash=next(x for x in value['rows']if x['finalAuthorSourceValue']is None)
                        dash['eligibleForPositiveMoneyConfirmation']=True
                    elif fault=='missing-target':value['rows'].pop()
                if Path(pin['path']).name=='independent-phsa-municipal-history-2019-20-009-original-transcript.json':
                    if fault=='raw-first':
                        row=next(x for x in value['transcript']if x['sequence']==9)
                        row['literalValues']['remuneration']+=1
                    elif fault=='raw-source':value['sourceId']='phsa-1900-01'
                    elif fault=='raw-sha':value['sourceSha256']='0'*64
                    elif fault=='raw-batch':value['batch']='phsa-2019-20-999'
                if fault=='source-pixel' and Path(pin['path']).name.endswith('009-fiftyone-money-source-fidelity.json'):
                    value['rows'][0]['actual1200PixelsMatch']=False
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(reference,overlay)
        original_exists=Path.exists
        def no_workspace_views(path):
            return False if str(path).startswith('/workspace/salary-review-')else original_exists(path)
        with mock.patch.object(Path,'exists',no_workspace_views):
            self.assertEqual(money_peer.build(reference,overlay),doc)

    def test_ordered_root_raw_joins_author_money_by_exact_source_tuple(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-010.json').read_text())
        reference=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(reference,overlay),doc)
        self.assertEqual((doc['confirmedMonetaryFields'],doc['originalAuthorOwnSourceCorrections']),(52,7))
        actual=field_ledger.pinned
        def reversed_author_rows(pin):
            value=copy.deepcopy(actual(pin))
            if Path(pin['path']).name=='independent-phsa-history-batches-2019-20-007-fiftytwo-money-author-choices.json':
                value['rows'].reverse()
            return value
        with mock.patch.object(field_ledger,'pinned',side_effect=reversed_author_rows):
            self.assertEqual(money_peer.build(reference,overlay),doc)
        for fault in ['packet-order','wrong-first','wrong-correction','moved-tuple']:
            def altered(pin):
                value=copy.deepcopy(actual(pin))
                if pin==reference and fault=='packet-order':value['rows'][0]['rootSourceOnlyPacketIndex']=2
                if Path(pin['path']).name=='independent-phsa-history-batches-2019-20-007-fiftytwo-money-author-choices.json':
                    if fault=='wrong-first':value['rows'][0]['initialImageFirstValue']+=1
                    if fault=='moved-tuple':value['rows'][0]['physicalPage']+=1
                if Path(pin['path']).name=='independent-phsa-history-batches-2019-20-007-postcomparison-money-source-rereads.json'and fault=='wrong-correction':
                    value['ownCorrections'][0]['literalSourceReread']+=1
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(reference,overlay)

    def test_disjoint_municipal_money_peers_preserve_secondary_rollback_and_1938(self):
        for number,count in [(11,4),(12,47)]:
            doc=json.loads((AREA/f'triangulation/money-peer-confirmations-{number:03d}.json').read_text())
            peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
            self.assertEqual(money_peer.build(peer,overlay),doc)
            self.assertEqual(doc['confirmedMonetaryFields'],count)
            actual=field_ledger.pinned
            for fault in ['first','secondary','scope','final']:
                def altered(reference):
                    value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                    if fault=='first'and name=='independent-phsa-municipal-history-2019-20-004-original-transcript.json':
                        value['rows'][0]['imageFirstValues']['expenses']+=1
                    if fault=='secondary'and name=='independent-phsa-municipal-history-2019-20-004-postcomparison-money-reread-transcript.json':
                        next(x for x in value['rows']if x['sequence']==141)['secondSourceReading']+=1
                    if fault=='scope'and reference==peer:value['rows'].pop()
                    if fault=='final'and reference==peer:
                        if number==11:value['rows'][0]['finalLiteralSourceValue']+=1
                        else:value['rows'][0]['authorEffectiveSourceValue']+=1
                    return value
                with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                    with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)
        direct=triangulation.confirmations()[('phsa-2019-20',26,34,'expenses')]
        self.assertEqual(direct['confirmedValue'],1938)

    def test_root_sequence_indexed_raw_is_complete_and_own_pay_error_remains_explicit(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-013.json').read_text())
        peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(peer,overlay),doc)
        self.assertEqual((doc['confirmedMonetaryFields'],doc['originalAuthorOwnSourceCorrections'],doc['originalPeerOwnSourceCorrections']),(44,1,2))
        actual=field_ledger.pinned
        for fault in ['missing-original-field','wrong-first','wrong-source','injected-wrong-batch','changed-source-map','changed-own-correction']:
            def altered(reference):
                value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                if name=='root-phsa-history-2019-20-batch-011-image-transcript.json':
                    if fault=='missing-original-field':value['readings']['1'].pop('name')
                    elif fault=='wrong-first':value['readings']['195']['remuneration']+=1
                    elif fault=='wrong-source':value['sourceId']='phsa-1900-01'
                    elif fault=='injected-wrong-batch':value['batch']='phsa-2019-20-999'
                    elif fault=='changed-source-map':value['sourceOnlyTargetViewsSha256']='0'*64
                if fault=='changed-own-correction'and name=='root-phsa-history-2019-20-batch-011-pay195-additive-own-source-correction.json':
                    value['finalLiteralSourceReading']+=1
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)

    def test_unchanged_eight_money_fields_require_source_raw_exact_scope_and_effective_overlay(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-014.json').read_text())
        peer=doc['peerInputs'][0];path=ROOT/peer['path']
        self.assertEqual(triangulation.adopt_table_peer(path,peer['sha256'],None),doc)
        self.assertEqual(len(doc['confirmations']),8)
        actual=field_ledger.pinned
        for fault in ['missing-field','wrong-raw','uncertainty','wrong-image','wrong-overlay']:
            def altered(reference):
                value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                if reference==peer:
                    if fault=='missing-field':value['rows'].pop()
                    elif fault=='wrong-image':value['rows'][0]['sourceImage']['sha256']='0'*64
                if name=='independent-phsa-history-batches-2021-22-money003-eight-source-first.json':
                    if fault=='wrong-raw':value['rows'][0]['literalImageValue']+=1
                    if fault=='uncertainty':value['rows'][0]['uncertainty']='Unresolved original digit'
                if fault=='wrong-overlay'and reference==doc['confirmations'][0]['effectiveAuthorOverlay']:
                    target=doc['confirmations'][0]
                    row=next(r for r in value['overlays']if(r['physicalPage'],r['sourceRowOnPage'])==(target['physicalPage'],target['sourceRowOnPage']))
                    row['resolvedRow'][3]+=1
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):triangulation.adopt_table_peer(path,peer['sha256'],None)

    def test_root_name_revision_selects_only_exact_corrected_case(self):
        path=AREA/'adoption-supersessions/phsa-2022-23-004-root-adoption-v2.json'
        selector=json.loads(path.read_text());old,new=adoption_revisions.validate(selector)
        self.assertNotEqual(old,new)
        self.assertEqual(selector['authorizedChangedNameCases'][0]['newPrimary'],'Urmaza,Jenylyn')
        for fault in ['row','money','old-primary','source']:
            bad=copy.deepcopy(selector)
            if fault=='row':bad['authorizedChangedNameCases'][0]['sourceRowOnPage']=2
            elif fault=='money':bad['authorizedChangedNameCases'][0]['allowedFields'].append('remuneration')
            elif fault=='old-primary':bad['authorizedChangedNameCases'][0]['oldPrimary']='Unprinted,Guess'
            else:bad['sourceId']='phsa-2021-22'
            with self.assertRaises(ValueError):adoption_revisions.validate(bad)
        chosen=field_ledger.typography_adoptions()[('phsa-2022-23',197,1)]
        self.assertEqual(chosen['chosenName'],'Urmaza,Jenylyn')
        # A later canonical full-family revision may follow this literal-name
        # correction. Its exact immutable ancestry must still retain this gate.
        selectors={json.dumps(json.loads(p.read_text())['effectiveRootAdoption'],sort_keys=True):(p,json.loads(p.read_text()))
                   for p in (AREA/'adoption-supersessions').glob('*.json')}
        current=chosen['rootAdoption'];ancestry=[]
        while json.dumps(current,sort_keys=True)in selectors:
            selection,proof=selectors[json.dumps(current,sort_keys=True)]
            ancestry.append(field_ledger.pin(selection));current=proof['supersededRootAdoption']
        self.assertIn(field_ledger.pin(path),ancestry)

    def test_only_exact_legacy_fourteen_adoption_can_use_its_original_embedded_case_schema(self):
        path=adoption_revisions.LEGACY14
        document=json.loads(path.read_text())
        self.assertTrue(adoption_revisions.accepted(path,document))
        self.assertEqual(len(adoption_revisions.cases(document,path)),14)
        reference=adoption_revisions.case_ledger(path,document)
        self.assertEqual(reference['sha256'],document['caseLedgerSha256'])
        first=document['cases'][0]
        self.assertEqual(adoption_revisions.family(first),[adoption_revisions.primary(first),first['alternative']])
        review={k:document[k]for k in ['sourceId','sourceSha256','batch']}
        review['sourceTypographyQualifications']=[copy.deepcopy(first)]
        self.assertEqual(len(resolutions.typography_cases(review)),1)
        changed=copy.deepcopy(review);changed['sourceTypographyQualifications'][0]['assumptionBasis']='Unpinned replacement context'
        with self.assertRaises(ValueError):resolutions.typography_cases(changed)
        for fault in ['decision','case','peer','count','injected-boolean']:
            bad=copy.deepcopy(document)
            if fault=='decision':bad['decision']='Accept arbitrary names'
            elif fault=='case':bad['cases'][0]['chosenContextualTranscription']='Unknown,Guess'
            elif fault=='peer':bad['independentPeerSha256']='0'*64
            elif fault=='count':bad['qualifiedNameCases']=13
            else:bad['acceptedQualifiedCases']=True
            self.assertFalse(adoption_revisions.accepted(path,bad))
        self.assertFalse(adoption_revisions.accepted(path.with_name('unrecognized-legacy.json'),document))

    def test_only_exact_hyphen_authority_has_a_synthetic_selection_batch(self):
        path=adoption_revisions.LEGACY_HYPHEN
        document=json.loads(path.read_text())
        self.assertTrue(adoption_revisions.accepted(path,document))
        self.assertEqual(adoption_revisions.source_identity(path,document)[2],'phsa-2015-16-hyphen-supplement')
        self.assertEqual(adoption_revisions.case_ledger(path,document),field_ledger.pin(path))
        case=next(iter(adoption_revisions.cases(document,path).values()))
        self.assertEqual(adoption_revisions.family(case),['Gfeller-Ingledew,Paris-Ann PA','Gfeller-lngledew,Paris-Ann PA'])
        for fault in ['unknown-row','changed-primary','extra-case','changed-source']:
            bad=copy.deepcopy(document)
            if fault=='unknown-row':bad['exactCases'][0]['sourceRowOnPage']=16
            elif fault=='changed-primary':bad['exactCases'][0]['chosenContextualTranscription']='Unknown,Guess'
            elif fault=='extra-case':bad['exactCases'].append(copy.deepcopy(bad['exactCases'][0]))
            else:bad['sourceSha256']='0'*64
            self.assertFalse(adoption_revisions.accepted(path,bad))
            with self.assertRaises(KeyError):adoption_revisions.source_identity(path,bad)

    def test_pinned_historical_name_case_crop_and_alternative_shapes(self):
        document=json.loads((field_ledger.REVIEWS/'independent-phsa-education-2015-16-003-source-typography-qualifications.json').read_text())
        case=document['cases'][0]
        self.assertEqual(adoption_revisions.family(case),['McIndoe,Sue','Mclndoe,Sue'])
        self.assertEqual(adoption_revisions.crop(case),case['originalFullRowCropSha256'])
        nested={'actualSourceEvidence':{'originalFullRowCropSha256':case['originalFullRowCropSha256']}}
        self.assertEqual(adoption_revisions.crop(nested),case['originalFullRowCropSha256'])
        for value in [None,'','0'*63,'not-a-hash','A'*64]:
            with self.assertRaises(ValueError):adoption_revisions.crop({'cropSha256':value})
        with self.assertRaises(ValueError):adoption_revisions.crop({})

    def test_direct_fresh_source_pay_is_exact_field_not_name_authority(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-006.json').read_text())
        peer,overlay,proof=doc['peerInputs'][0],doc['confirmations'][0]['effectiveAuthorOverlay'],doc['pixelProof']
        self.assertEqual(direct_money.build(peer,overlay,proof),doc)
        self.assertEqual(doc['confirmedMonetaryFields'],2)
        self.assertEqual(next(r['confirmedValue']for r in doc['confirmations']if r['physicalPage']==90),83813)
        actual=field_ledger.pinned
        for fault in ['value','unresolved','widened-scope','wrong-source']:
            def changed(reference):
                value=copy.deepcopy(actual(reference))
                if reference==peer:
                    if fault=='value':value['entries'][2]['literalSourceValue']+=1
                    elif fault=='unresolved':value['entries'][2]['realUncertainty']='unknown digit'
                    elif fault=='widened-scope':value['entries'].append(copy.deepcopy(value['entries'][2]))
                    else:value['sourceSha256']='0'*64
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):direct_money.build(peer,overlay,proof)

    def test_canonical_mixed_peer_binds_six_unchanged_money_and_all31_targets(self):
        peer=field_ledger.pin(field_ledger.REVIEWS/'independent-phsa-history-peer-health-2019-20-017-thirtyone-final-source-comparison.json')
        overlay=field_ledger.pin(AREA/'overlays/phsa-2019-20-manual-overlay-017.json')
        result=money_peer.build(peer,overlay)
        self.assertEqual(result['confirmedMonetaryFields'],6)
        self.assertEqual(result['completeFrozenSourceTargetFields'],31)
        actual=field_ledger.pinned
        for fault in ['amount','source','first-value','crop','missing-target','money-qualification','pixel','overlay']:
            def changed(reference):
                d=copy.deepcopy(actual(reference))
                if reference==peer:
                    row=next(r for r in d['rows']if r['field']=='remuneration')
                    if fault=='amount':row['literalSourceValue']+=1
                    elif fault=='source':d['sourceSha256']='0'*64
                    elif fault=='first-value':row['firstPeerWhole600VisualValue']+=1
                    elif fault=='crop':row['cropSha256']='0'*64
                    elif fault=='missing-target':d['rows'].pop()
                    elif fault=='money-qualification':row['sourceTypographyQualificationProposed']=True
                    elif fault=='pixel':row['actualSourceOriginalWhole600AndNative300PixelExact']=False
                if reference==overlay and fault=='overlay':
                    target=result['confirmations'][0]
                    row=next(r for r in d['overlays']if(r['physicalPage'],r['sourceRowOnPage'])==(target['physicalPage'],target['sourceRowOnPage']))
                    row['resolvedRow'][field_ledger.FIELDS[target['field']]]+=1
                return d
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):money_peer.build(peer,overlay)

    def test_exact_closed_canonical_version_keeps_old_three_and_new_six_families(self):
        review=json.loads((field_ledger.REVIEWS/'root-phsa-history-2022-23-batch-002-resolutions.json').read_text())
        old=resolutions.closed_source_cases(review)[(106,17)]
        self.assertEqual(len(old['visibleAlternatives'])+1,3)
        review['closedSourceNameQualificationLedgers']=[field_ledger.pin(field_ledger.REVIEWS/'root-phsa-history-2022-23-batch-002-name394-canonical-six-source-ledger.json')]
        current=resolutions.closed_source_cases(review)[(106,17)]
        self.assertEqual(len(current['visibleAlternatives'])+1,6)
        actual=resolutions.pinned
        for fault in ['unknown-predecessor','changed-primary','extra-letter','wrong-ledger']:
            def changed(path,digest):
                d=copy.deepcopy(actual(path,digest))
                if path.name=='source-name-exact-case-policy-017.json':
                    c=d['approvedCases'][0]
                    if fault=='unknown-predecessor':c['supersedesExactClosedAuthority']['rootAdoption']['sha256']='0'*64
                    elif fault=='changed-primary':c['primary']='Unknown,Guess'
                    elif fault=='extra-letter':c['completeVisibleAlternatives'].append('Unknown,Guess')
                    else:c['exactCaseLedger']['sha256']='0'*64
                return d
            with mock.patch.object(resolutions,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):resolutions.closed_source_cases(review)

    def test_root53_current_correction_preserves_wrong_firsts_and_unique_cold394(self):
        peer=field_ledger.pin(field_ledger.REVIEWS/'root-phsa-history-2019-20-batch-012-fiftythree-money-final-source-comparison-v2.json')
        overlay=field_ledger.pin(AREA/'overlays/phsa-2019-20-manual-overlay-012.json')
        result=money_peer.build(peer,overlay)
        self.assertEqual(result['confirmedMonetaryFields'],53)
        self.assertEqual(result['originalAuthorOwnSourceCorrections'],10)
        self.assertEqual(result['originalPeerOwnSourceCorrections'],7)
        actual=field_ledger.pinned
        for fault in ['current394','first394','unrelated52','missing53','fresh-exposed','fresh-first','fresh-unfrozen','proof']:
            def changed(reference):
                d=copy.deepcopy(actual(reference))
                if reference==peer:
                    row=next(r for r in d['rows']if r['sequence']==394 and r['field']=='remuneration')
                    if fault=='current394':row['rootCurrentSourceReading']=89600
                    elif fault=='first394':row['rootFirstImageReading']=99600
                    elif fault=='unrelated52':d['rows'][0]['authorCurrentSourceReading']='1'
                    elif fault=='missing53':d['rows'].pop()
                if reference['path'].endswith('author-phsa-history-schools-2019-20-012-money394-source-first.json'):
                    if fault=='fresh-exposed':d['correspondingAuthorOrPeerAmountsOpened']=True
                    elif fault=='fresh-first':d['rows'][0]['literalImageValue']=89600
                    elif fault=='fresh-unfrozen':d['frozen']=False
                if reference['path'].endswith('twentyone-plus394-canonical-pixel-proof.json')and fault=='proof':
                    next(r for r in d['rows']if r['sequence']==394)['rgbPixelsExactlyReproducedFromWholeOriginalPage']=False
                return d
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):money_peer.build(peer,overlay)

    def test_current42_finance_preserves_first_secondary_and_restored_first(self):
        peer=field_ledger.pin(field_ledger.REVIEWS/'root-phsa-history-2019-20-batch-014-fortytwo-money-final-source-comparison.json')
        overlay=field_ledger.pin(AREA/'overlays/phsa-2019-20-manual-overlay-014.json')
        result=money_peer.build(peer,overlay)
        self.assertEqual((result['confirmedMonetaryFields'],result['originalAuthorOwnSourceCorrections'],result['originalPeerOwnSourceCorrections']),(42,7,7))
        actual=field_ledger.pinned
        for fault in ['first','current','secondary','restoration','source','third-unfrozen','third-shared-omission','third-own-error']:
            def changed(reference):
                d=copy.deepcopy(actual(reference))
                if reference==peer:
                    if fault=='first':d['rows'][0]['rootFirstImageValue']+=1
                    elif fault=='current':d['rows'][0]['rootFinalSourceValue']+=1
                    elif fault=='source':d['sourceId']='phsa-1900-01'
                if reference['path'].endswith('fortytwo-current-actual600-assessment.json')and fault=='secondary':d['rows'][0]['rootCurrent600SourceReading']+=1
                if reference['path'].endswith('expense264-additive-restoration.json')and fault=='restoration':d['rootWrongSecondary600Reading']=3958
                if reference['path'].endswith('thirteen-money-source-first.json'):
                    if fault=='third-unfrozen':d['frozen']=False
                    elif fault=='third-own-error':d['sourceOnlyOwnCorrections'][0]['firstVisualValue']+=1
                if reference['path'].endswith(('thirteen-money-source-first.json','thirteen-money-final-comparison.json'))and fault=='third-shared-omission':
                    d['rows']=[r for r in d['rows']if r['sequence']!=97]
                return d
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):money_peer.build(peer,overlay)

    def test_exhaustive282_money_exact_peer_partition_and_explicit_dash(self):
        peer=field_ledger.pin(field_ledger.REVIEWS/'independent-phsa-history-2019-20-016-all282-financial-source-closure.json')
        overlay=field_ledger.pin(AREA/'overlays/phsa-2019-20-manual-overlay-016.json')
        result=money_peer.build(peer,overlay)
        self.assertEqual(result['confirmedMonetaryFields'],281)
        self.assertEqual(len(result['independentPeerImageFirstTranscripts']),3)
        self.assertEqual(result['originalAuthorOwnSourceCorrections'],44)
        self.assertEqual(result['originalPeerOwnSourceCorrections'],4)
        self.assertEqual(result['literalSourceDashFieldsConfirmedSeparately'][0]['value'],None)
        actual=field_ledger.pinned
        for fault in ['current','cold','null-zero','missing','duplicate-partition','source']:
            def changed(reference):
                d=copy.deepcopy(actual(reference))
                if reference==peer:
                    if fault=='current':d['rows'][0]['finalSourceLiteral']+=1
                    elif fault=='cold':d['rows'][0]['originalColdLiteral']+=1
                    elif fault=='null-zero':next(r for r in d['rows']if r['finalSourceLiteral']is None)['finalSourceLiteral']=0
                    elif fault=='missing':d['rows'].pop()
                    elif fault=='duplicate-partition':d['exactDisjointPeerPartition'][1]=d['exactDisjointPeerPartition'][0]
                    else:d['sourceSha256']='0'*64
                return d
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):money_peer.build(peer,overlay)

    def test_wholepage36_source_first_and_author_postpeer_correction(self):
        peer=field_ledger.pin(field_ledger.REVIEWS/'independent-phsa-history-batches-peer-municipal-2019-20-015-thirtysix-money-final-comparison.json')
        actual=field_ledger.pinned;review=actual(peer);source=tuple(review[k]for k in ['sourceId','sourceSha256','batch'])
        def replay():return canonical_money.wholepage_literal_peer(actual(peer),source,field_ledger.pinned,money_peer.source_image_check,money_peer.unique,money_peer.key)
        facts,raw,author_errors,peer_errors=replay()
        self.assertEqual((len(facts),author_errors,peer_errors),(36,3,0))
        for fault in ['first','current','post-correction','pixel','exposure']:
            def changed(reference):
                d=copy.deepcopy(actual(reference))
                if reference['path'].endswith('thirtysix-money-source-first.json')and fault=='first':d['rows'][0]['literalImageValue']+=1
                if reference['path'].endswith('postcomparison-thirtysix-money-source-rereads.json'):
                    if fault=='current':d['rows'][0]['currentSourceLiteral']+=1
                    elif fault=='exposure':d['freshPeerChoicesOpened']=True
                if reference['path'].endswith('post-peer-remuneration189-own-source-correction.json')and fault=='post-correction':d['ownFirstFrozenAndSecondSourceRereadValue']+=1
                if reference['path'].endswith('thirtysix-money-source-pixel-proof.json')and fault=='pixel':d['rows'][0]['checks']['whole600']=False
                return d
            with mock.patch.object(field_ledger,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):replay()

    def test_exact_hyphen_supplement_metadata_revision_has_no_fake_batch_or_money_change(self):
        oldref=field_ledger.pin(canonical_supplements.ORIGINAL_PATH)
        selectorref=field_ledger.pin(AREA/'adoption-supersessions/phsa-2015-16-hyphen-i-root-typography-canonical.json')
        revised=canonical_supplements.build(oldref,selectorref)
        old=json.loads(canonical_supplements.ORIGINAL_PATH.read_text())
        self.assertNotIn('batch',revised)
        self.assertEqual(revised['overlays'][0]['resolvedRow'],old['overlays'][0]['resolvedRow'])
        self.assertEqual(len(revised['overlays'][0]['nameTypographyQualification']['visibleAlternatives'])+1,16)
        sidecar=json.loads((AREA/'overlay-supersessions/phsa-2015-16-hyphen-name-supplement-002-canonical.json').read_text())
        for fault in ['money','field','name','crop','unknown-supplement']:
            bad=copy.deepcopy(revised)
            row=bad['overlays'][0]
            if fault=='money':row['resolvedRow'][3]+=1
            elif fault=='field':row['reviewedFields'].append('remuneration')
            elif fault=='name':row['resolvedRow'][1]='Unknown,Guess'
            elif fault=='crop':row['cropSha256']='0'*64
            else:bad['originalSpecialSupplement']['path']='unknown.json'
            with self.assertRaises((ValueError,FileNotFoundError)):
                canonical_supplements.validate_selection(sidecar,old,bad)

    def test_eleven_root_closed_names_accept_explicit_basis_and_reject_extra_letters(self):
        ref=field_ledger.pin(field_ledger.REVIEWS/'root-phsa-history-2019-20-batch-015-eleven-exact-policy-ledger.json')
        doc=field_ledger.pinned(ref)
        review={k:doc[k]for k in ['sourceId','sourceSha256','batch']}
        review['closedSourceNameQualificationLedgers']=[ref]
        result=resolutions.closed_source_cases(review)
        self.assertEqual(len(result),11)
        actual=resolutions.pinned
        for fault in ['empty-basis','extra-alternative','unknown-row','money-field']:
            def changed(path,digest):
                d=copy.deepcopy(actual(path,digest))
                if path==ROOT/ref['path']:
                    c=d['cases'][0]
                    if fault=='empty-basis':c['sourceAssumptionBasis']=''
                    elif fault=='extra-alternative':c['visibleAlternatives'].append('Unknown,Guess')
                    elif fault=='unknown-row':c['sourceRowOnPage']=1
                    else:c['allowedFields']=['name','remuneration']
                return d
            with mock.patch.object(resolutions,'pinned',side_effect=changed):
                with self.assertRaises(ValueError):resolutions.closed_source_cases(review)

    def test_closed_scopes_and_mixed_authority_keep_distinct_generic_cases(self):
        for filename,count in [('root-phsa-history-2019-20-batch-005-three-name-exact-adoption.json',3),('root-phsa-history-2019-20-batch-007-four-name-exact-adoption.json',4)]:
            p=field_ledger.REVIEWS/filename;d=json.loads(p.read_text())
            scoped=adoption_revisions.cases(d,p)
            self.assertEqual(len(scoped),count)
            self.assertTrue(all(c['physicalPage']>0 for c in scoped.values()))
            changed=copy.deepcopy(d);changed['exactCases'][0]['visibleAlternatives'].append('Unknown,Guess')
            with self.assertRaises(ValueError):adoption_revisions.cases(changed,p)
        p=field_ledger.REVIEWS/'root-phsa-history-2019-20-batch-006-canonical-municipal-supplemental-six-full-scope-segmentation-adoption.json';mixed=json.loads(p.read_text())
        self.assertEqual(len(adoption_revisions.cases(mixed,p)),6)
        generic={k for k,v in field_ledger.typography_adoptions().items()if v['rootAdoption']==field_ledger.pin(p)}
        self.assertEqual(len(generic),5)
        source={k:mixed[k]for k in ['sourceId','sourceSha256','batch']};source['closedSourceNameQualificationLedgers']=[mixed['exactCaseLedger']]
        closed=resolutions.closed_source_cases(source)
        self.assertEqual(len(closed),1)
        self.assertFalse({k[1:]for k in generic}&set(closed))

    def test_cross_source_rebase_preserves_unrelated_field_provenance(self):
        path=AREA/'triangulation/money-peer-confirmations-001-v6.json';d=json.loads(path.read_text())
        original=json.loads((AREA/'triangulation/money-peer-confirmations-001-v5.json').read_text())
        self.assertEqual(d['adapter'],'unchanged-money-overlay-revision-v2')
        self.assertEqual(len(d['preservedUnchangedFieldProvenance']),14)
        self.assertEqual(d['unchangedFreshMoneyFieldsRebound'],1)
        old={(r['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field']):r for r in original['confirmations']}
        for r in d['confirmations']:
            k=r['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field']
            if r['sourceId']!='phsa-2018-19':self.assertEqual(r,old[k])
        confirmed=triangulation.confirmations()[('phsa-2016-17',28,28,'remuneration')]
        self.assertEqual(confirmed['confirmationLedger'],field_ledger.pin(AREA/'triangulation/money-peer-confirmations-001-v5.json'))
        selector=json.loads((AREA/'triangulation/confirmation-supersessions/money-peer-confirmations-001-v6.json').read_text());actual=money_revisions.load
        for fault in ['missing-preserved','changed-pointer','changed-unrelated-value']:
            def changed(reference):
                p,doc=actual(reference);doc=copy.deepcopy(doc)
                if reference==selector['effectiveConfirmation']:
                    if fault=='missing-preserved':doc['preservedUnchangedFieldProvenance'].pop()
                    elif fault=='changed-pointer':doc['preservedUnchangedFieldProvenance'][0]['confirmationLedger']=field_ledger.pin(AREA/'triangulation/money-peer-confirmations-001.json')
                    else:doc['confirmations'][0]['confirmedValue']+=1
                return p,doc
            with mock.patch.object(money_revisions,'load',side_effect=changed):
                with self.assertRaises(ValueError):money_revisions.validate(selector)

    def test_exact_retirement_preserves_other19_root_cases_and_old_histories(self):
        sidecar=json.loads((AREA/'adoption-supersessions/phsa-2019-20-011-root-adoption-canonical-retired.json').read_text())
        oldpath,newpath=adoption_revisions.validate(sidecar)
        old=json.loads(oldpath.read_text());new=json.loads(newpath.read_text())
        self.assertEqual(len(adoption_revisions.cases(old,oldpath)),21)
        self.assertEqual(len(adoption_revisions.cases(new,newpath)),19)
        self.assertEqual(len(sidecar['authorizedRetiredNameCases']),2)
        for fault in ['unknown-row','crop','direct-name','financial-field','missing-root-retirement']:
            bad=copy.deepcopy(sidecar)
            if fault=='unknown-row':bad['authorizedRetiredNameCases'][0]['sourceRowOnPage']=1
            elif fault=='crop':bad['authorizedRetiredNameCases'][0]['originalFullRowCropSha256']='0'*64
            elif fault=='direct-name':bad['authorizedRetiredNameCases'][0]['currentDirectLiteral']='Unknown,Guess'
            elif fault=='financial-field':bad['authorizedRetiredNameCases'][0]['allowedFields']=['name','expenses']
            else:bad['authorizedRetiredNameCases'].pop()
            with self.assertRaises(ValueError):adoption_revisions.validate(bad)

    def test_current201_map_has_exact_human_pointers_and_name_only_revision(self):
        doc,decisions=current_canonical.decisions()
        self.assertEqual(len(decisions),201)
        self.assertEqual(sum(r['currentSourceStatus']=='qualified'for r in decisions.values()),70)
        p=field_ledger.REVIEWS/'author-phsa-history-2019-20-batch-001-canonical-current201-resolutions.json';review=json.loads(p.read_text())
        current_canonical.validate_review(review,resolutions.typography_cases(review))
        for fault in ['money','unapproved-name','wrong-map','missing-family']:
            bad=copy.deepcopy(review)
            if fault=='money':next(r for r in bad['resolutions']if'remuneration'in r['resolvedValues'])['resolvedValues']['remuneration']+=1
            elif fault=='unapproved-name':next(r for r in bad['resolutions']if'name'in r['resolvedValues'])['resolvedValues']['name']='Unknown,Guess'
            elif fault=='wrong-map':bad['canonicalCurrentSourceNameRevision']['authorizedCurrent201DecisionMap']['sha256']='0'*64
            else:
                q=resolutions.typography_cases(bad);q.pop(next(k for k in q if k in decisions))
                with self.assertRaises(ValueError):current_canonical.validate_review(bad,q)
                continue
            with self.assertRaises(ValueError):current_canonical.validate_review(bad,resolutions.typography_cases(bad))

    def test_source_first_pointer_correction_keeps_52_root_and_one_cold394(self):
        old=field_ledger.pinned(money_provenance.ORIGINAL)
        corrected=money_provenance.build(money_provenance.ORIGINAL)
        self.assertEqual(corrected['sourceFirstPointerCorrections'],52)
        self.assertEqual(len(corrected['confirmations']),53)
        for before,after in zip(old['confirmations'],corrected['confirmations']):
            changed=copy.deepcopy(after);changed['imageFirstTranscript']=before['imageFirstTranscript']
            self.assertEqual(changed,before)
            expected=corrected['independentCold394FirstTranscript']if(after['physicalPage'],after['sourceRowOnPage'],after['field'])==(88,13,'remuneration')else corrected['originalRoot53FirstTranscript']
            self.assertEqual(after['imageFirstTranscript'],expected)
        actual=money_revisions.load;sidecar=json.loads((AREA/'triangulation/confirmation-supersessions/money-peer-confirmations-023-v2.json').read_text())
        for fault in ['pointer','amount','scope']:
            def changed(reference):
                path,d=actual(reference);d=copy.deepcopy(d)
                if reference==sidecar['effectiveConfirmation']:
                    if fault=='pointer':d['confirmations'][0]['imageFirstTranscript']=corrected['independentCold394FirstTranscript']
                    elif fault=='amount':d['confirmations'][0]['confirmedValue']+=1
                    else:d['confirmations'].pop()
                return path,d
            with mock.patch.object(money_revisions,'load',side_effect=changed):
                with self.assertRaises(ValueError):money_revisions.validate(sidecar)

    def test_current_scoped_1200_source_peer_confirms_two_money_fields_only(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-016.json').read_text())
        peer,overlay,proof=doc['peerInputs'][0],doc['confirmations'][0]['effectiveAuthorOverlay'],doc['pixelProof']
        self.assertEqual(direct_money.build(peer,overlay,proof),doc)
        self.assertEqual((doc['completeFrozenSourcePeerFields'],doc['confirmedMonetaryFields']),(8,2))
        actual=field_ledger.pinned
        for fault in ['wrong-first','uncertain-money','wrong-source','wrong-proof','moved-field']:
            def altered(reference):
                value=copy.deepcopy(actual(reference))
                if reference==peer:
                    if fault=='wrong-first':value['rows'][0]['value']+=1
                    elif fault=='uncertain-money':value['rows'][0]['uncertain']=True
                    elif fault=='wrong-source':value['sourceId']='phsa-1900-01'
                    elif fault=='moved-field':value['rows'][0]['physicalPage']+=1
                if fault=='wrong-proof'and reference==proof:value['rows'][0]['dpi']=600
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):direct_money.build(peer,overlay,proof)

    def test_scoped_eighty_eight_review_replays_nine_money_errors_and_fresh_adjudication(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-020.json').read_text())
        peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(peer,overlay),doc)
        self.assertEqual((doc['completeFrozenSourceTargetFields'],doc['confirmedMonetaryFields']),(88,67))
        self.assertEqual((doc['originalAuthorOwnSourceCorrections'],doc['originalPeerOwnSourceCorrections']),(7,9))
        actual=field_ledger.pinned
        for fault in ['author-header','peer-first','third-first','third-final','pixel','missing-target']:
            def altered(reference):
                value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                if fault=='author-header'and name=='independent-phsa-schools-2019-20-batch-006-original-transcript.json':
                    value['sourceSha256']='0'*64
                if reference==peer:
                    if fault=='peer-first':next(r for r in value['rows']if r['field']=='remuneration')['firstPeerSourceValue']+=1
                    if fault=='missing-target':value['rows'].pop()
                if fault=='third-first'and name=='independent-phsa-history-peer-schools-2019-20-006-twentyfour-source-first.json':
                    next(r for r in value['entries']if r['field']=='remuneration')['literalSourceValue']+=1
                if fault=='third-final'and name=='independent-phsa-history-peer-schools-2019-20-006-twentyfour-final-source-comparison.json':
                    next(r for r in value['rows']if r['field']=='remuneration')['currentLiteralSourceValue']+=1
                if fault=='pixel'and name=='author-phsa-history-schools-2019-20-006-supplemental-eighty-eight-source-pixel-proof.json':
                    value['rows'][0]['actualOriginal1200PixelsIndependentlyReproducedExactly']=False
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)

    def test_new_literal_tuple_schema_preserves_source_first_and_author_corrections(self):
        for number,count in [(18,40),(19,4)]:
            doc=json.loads((AREA/f'triangulation/money-peer-confirmations-{number:03d}.json').read_text())
            peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
            self.assertEqual(money_peer.build(peer,overlay),doc)
            self.assertEqual(doc['confirmedMonetaryFields'],count)
            actual=field_ledger.pinned
            for fault in ['source','raw-first','original-author-first','missing-scope']:
                def altered(reference):
                    value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                    if reference==peer:
                        if fault=='source':value['sourceId']='phsa-1900-01'
                        if fault=='missing-scope':value['rows'].pop()
                    if fault=='raw-first'and name in ['independent-phsa-history-batches-peer-2019-20-013-forty-money-source-first.json','independent-phsa-history-batches-peer-2021-22-008-four-money-source-first.json']:
                        value['rows'][0]['literalImageValue']+=1
                    if fault=='original-author-first'and name in ['independent-phsa-municipal-history-2019-20-013-original-transcript.json','independent-phsa-municipal-history-2021-22-008-original-transcript.json']:
                        seq=doc['confirmations'][0]['physicalPage'];target=actual(peer)['rows'][0]
                        row=next(r for r in value['rows']if(r['physicalPage'],r['sourceRowOnPage'])==(target['physicalPage'],target['sourceRowOnPage']))
                        row['imageFirstValues'][target['field']]+=1
                    return value
                with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                    with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)

    def test_single_source_money_revision_retains_real_first_reading_and_current_overlay(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-021-v2.json').read_text())
        peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(peer,overlay),doc)
        self.assertEqual(doc['confirmations'][0]['confirmedValue'],78316)
        actual=field_ledger.pinned
        for fault in ['author-first','peer-first','missing-pixel-proof','changed-crop']:
            def altered(reference):
                value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                if fault=='author-first'and name=='independent-phsa-education-2021-22-005-image-first-transcript.json':
                    next(r for r in value['readings']if r['sequence']==281)['value']+=1
                if fault=='peer-first'and name=='root-phsa-history-2021-22-batch-005-one-money-image-first.json':
                    value['rows'][0]['rootFirstImageReading']+=1
                if reference==peer:
                    if fault=='missing-pixel-proof':value['source1200RgbReproducedExactly']=False
                    if fault=='changed-crop':value['rows'][0]['cropSha256']='0'*64
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)

    def test_monetary_confirmation_revision_cannot_change_value_scope_or_source_history(self):
        sidecar=json.loads((AREA/'triangulation/confirmation-supersessions/money-peer-confirmations-021-v2.json').read_text())
        old,new=money_revisions.validate(sidecar)
        self.assertNotEqual(old,new)
        actual=money_revisions.load
        for fault in ['amount','row','source','reading-history','overlay']:
            def altered(reference):
                path,value=actual(reference);value=copy.deepcopy(value)
                if path in [old,new]:
                    if fault=='amount':value['confirmations'][0]['confirmedValue']+=1
                    if fault=='row':value['confirmations'][0]['sourceRowOnPage']+=1
                    if fault=='source':value['confirmations'][0]['sourceSha256']='0'*64
                    if fault=='reading-history'and path==new:value['originalPeerOwnSourceCorrections']=1
                    if fault=='overlay'and path==new:value['confirmations'][0]['effectiveAuthorOverlay']=sidecar['supersededConfirmation']
                return path,value
            with mock.patch.object(money_revisions,'load',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_revisions.validate(sidecar)

    def test_canonical_missed_dot_revision_is_one_name_only_and_preserves_old_uncertainty(self):
        sidecar=json.loads((AREA/'overlay-supersessions/phsa-2021-22-manual-overlay-005-v2.json').read_text())
        old_path,new_path=supersessions.validate(sidecar)
        old,new=map(lambda p:json.loads(p.read_text()),[old_path,new_path])
        differences=[(a,b)for a,b in zip(old['overlays'],new['overlays'])if(a['resolvedRow'],a['nameTypographyQualification'])!=(b['resolvedRow'],b['nameTypographyQualification'])]
        self.assertEqual(len(differences),1)
        before,after=differences[0]
        self.assertEqual((before['physicalPage'],before['sourceRowOnPage']),(119,31))
        self.assertEqual(before['resolvedRow'][1],'Mundl,Jacqueline')
        self.assertEqual(after['resolvedRow'][1],'Mundi,Jacqueline')
        self.assertIsNotNone(before['nameTypographyQualification'])
        self.assertIsNone(after['nameTypographyQualification'])
        self.assertEqual(before['resolvedRow'][2:],after['resolvedRow'][2:])
        self.assertEqual(resolutions.ordinary(ROOT/new['reviewInput']['path'],new['reviewInput']['sha256']),new)

    def test_sparse_early001_complete55_preserves_first_current_and_correction_history(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-027.json').read_text())
        peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(peer,overlay),doc)
        self.assertEqual((len(doc['confirmations']),doc['originalAuthorOwnSourceCorrections'],doc['originalPeerOwnSourceCorrections']),(55,3,1))
        actual=field_ledger.pinned
        for fault in ['raw-unfrozen','missing-common-target','root-first','author-first','author-source','changed-correction','pixel-scope','false-counter']:
            def altered(reference):
                value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                if name=='root-phsa-history-2019-20-001-fiftyfive-money-source-first.json':
                    if fault=='raw-unfrozen':value['frozen']=False
                    if fault=='root-first':value['rows'][0]['firstWhole600LiteralImageValue']+=1
                    if fault=='pixel-scope':value['sourcePixelReproduction'].pop()
                    if fault=='false-counter':value['counts']['rootOwnBeforeChoiceValueCorrections']=1
                if fault=='missing-common-target'and name in ['root-phsa-history-2019-20-001-fiftyfive-money-source-first.json','root-phsa-history-2019-20-001-fiftyfive-money-final-source-comparison.json']:
                    value['rows'].pop()
                if name=='independent-phsa-history-2019-20-001-fiftyfive-scoped-author-current-history-before-root-choices.json':
                    if fault=='author-first':value['rows'][0]['originalSparseFirstValue']+=1
                    if fault=='author-source':value['sourceId']='phsa-1900-01'
                if reference==peer and fault=='changed-correction':value['oldSelectedSourceValueCorrections'][0]['currentLiteralValue']+=1
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)

    def test_sparse_early001_financial_revision_changes_only_three_reviewed_amounts(self):
        overlay=json.loads((AREA/'overlays/phsa-2019-20-manual-overlay-001-v3-canonical-money.json').read_text())
        review=field_ledger.pinned(overlay['reviewInput'])
        sparse_current.validate_financial_review(review)
        for fault in ['name','status','unreviewed-money','wrong-reviewed-money','field-membership','name-authority','correction-summary']:
            changed=copy.deepcopy(review)
            if fault=='name':next(r for r in changed['resolutions']if'name'in r['resolvedValues'])['resolvedValues']['name']+='a'
            if fault=='status':changed['resolutions'][0]['status']='resolved-from-original-image'if changed['resolutions'][0]['status']!='resolved-from-original-image'else'resolved-with-source-typography-qualification'
            if fault=='unreviewed-money':
                confirmed={(r['physicalPage'],r['sourceRowOnPage'],r['field'])for r in json.loads((AREA/'triangulation/money-peer-confirmations-027.json').read_text())['confirmations']}
                row=next(r for r in changed['resolutions']if 'remuneration'in r['resolvedValues']and(r['physicalPage'],r['sourceRowOnPage'],'remuneration')not in confirmed)
                row['resolvedValues']['remuneration']+=1
            if fault=='wrong-reviewed-money':next(r for r in changed['resolutions']if(r['physicalPage'],r['sourceRowOnPage'])==(7,41))['resolvedValues']['remuneration']+=1
            if fault=='field-membership':changed['resolutions'][0]['resolvedValues'].pop(next(iter(changed['resolutions'][0]['resolvedValues'])))
            if fault=='name-authority':changed['canonicalCurrentSourceNameRevision']['allFinancialValuesAndOriginalRequestedFieldScopeRemainIdentical']=False
            if fault=='correction-summary':changed['canonicalCurrentFinancialSourceRevision']['exactSourceCorrections'][0]['currentLiteralValue']+=1
            with self.assertRaises((ValueError,KeyError)):sparse_current.validate_financial_review(changed)

    def test_unchanged_scoped_two_money_fields_keep_actual_author_raw_bound(self):
        doc=json.loads((AREA/'triangulation/money-peer-confirmations-017.json').read_text())
        peer=doc['peerInputs'][0];overlay=doc['confirmations'][0]['effectiveAuthorOverlay']
        self.assertEqual(money_peer.build(peer,overlay),doc)
        self.assertEqual(len(doc['confirmations']),2)
        actual=field_ledger.pinned
        for fault in ['author-source','author-first','peer-first','missing-field']:
            def altered(reference):
                value=copy.deepcopy(actual(reference));name=Path(reference['path']).name
                if name=='independent-phsa-history-2021-22-batch-006-full-image-first.json':
                    if fault=='author-source':value['sourceId']='phsa-1900-01'
                    if fault=='author-first':
                        target=doc['confirmations'][0];row=next(r for r in value['rows']if(r['physicalPage'],r['sourceRowOnPage'],r['field'])==(target['physicalPage'],target['sourceRowOnPage'],target['field']))
                        row['literalSourceValue']+=1
                if reference==peer:
                    if fault=='peer-first':value['rows'][0]['peerInitialImageFirstValue']+=1
                    if fault=='missing-field':value['rows'].pop()
                return value
            with mock.patch.object(field_ledger,'pinned',side_effect=altered):
                with self.assertRaises((ValueError,KeyError)):money_peer.build(peer,overlay)


if __name__=='__main__':unittest.main()
