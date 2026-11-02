#!/usr/bin/env python3
"""Reconstruct source fields from immutable raw pages, exact reviews and policy.

This is an audit/provisional candidate ledger, not a whole-source acceptance gate.
It preserves original flags and distinguishes image review, source dash proof,
baseline reader agreement and calibrated confidence-only corroboration.
"""
import argparse
import collections
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import finish_salary_phsa_policy as policy

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
REVIEWS=ROOT/'research/salaries/queue-completion-2026-11-01/reviews'
FIELDS=policy.FIELD_INDEX
LEGACY_EXACT_ADOPTION={
    'root-phsa-history-2015-16-batch-001-typography-adoption.json':
        '41410273e366a0cee07268d8d2af077fa95daef4edd9a5bfef9c00be35b3448c'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=None)
def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def pinned(reference):
    path=ROOT/reference['path']
    if not path.resolve().is_relative_to(ROOT):raise ValueError('Review evidence must be repository-relative')
    if sha(path.read_bytes())!=reference['sha256']:raise ValueError('Pinned field evidence changed: '+str(path))
    return json.loads(path.read_text())


def chosen_name(case):
    for key in ['chosenContextualTranscription','resolvedContextualName','proposedName','chosenName','primaryName']:
        if key in case:return case[key]
    raise ValueError('Exact contextual source-name primary is missing')


def typography_adoptions():
    result={}
    paths=set(REVIEWS.glob('root-phsa-history-*typography*adoption*.json'))|set(REVIEWS.glob('root-phsa-history-*segmentation-adoption.json'))
    import finish_salary_phsa_adoption_supersessions as adoption_supersessions
    paths,adoption_selections=adoption_supersessions.selected(paths)
    for path in sorted(paths):
        adoption=json.loads(path.read_text());source=adoption.get('sourceId')
        if not source:continue
        accepted=adoption.get('acceptedQualifiedCases') is True
        if path.name in LEGACY_EXACT_ADOPTION:
            if sha(path.read_bytes())!=LEGACY_EXACT_ADOPTION[path.name]:raise ValueError('Exact legacy root adoption changed')
            # The first frozen adoption predates the boolean convention. Its
            # pinned explicit decision,14-case list and independent peer are
            # the authority; do not edit it or infer acceptance from a filename.
            accepted=(adoption.get('decision')=='Adopt exactly14 qualified contextual source-glyph readings; no pixel-proved casing claim.'
                      and adoption.get('qualifiedNameCases')==14 and len(adoption.get('cases',[]))==14)
        if not accepted:continue
        cases=adoption.get('cases',adoption.get('exactCases'))
        ledger_reference=adoption.get('exactCaseLedger')
        adopted_ledger=pinned(ledger_reference) if ledger_reference else None
        if cases is None and ledger_reference:
            ledger=adopted_ledger;cases=ledger.get('qualifications',ledger.get('cases',ledger.get('sourceTypographyQualifications')))
            if ledger['sourceSha256']!=adoption['sourceSha256']:raise ValueError('Adopted source typography ledger identity changed')
        if cases is None:raise ValueError('Root adoption has no exact case set')
        if ledger_reference and any(not any(c.get(k)for k in ['basis','assumptionBasis','contextualAssumption','ownSourceObservation','sourceAssumptionBasis'])for c in cases):
            # Some root documents deliberately embed compact exact summaries.
            # Recover only their matching FULL pinned ledger dictionaries;
            # cases() verifies scope, primary, full finite family and crop.
            full=adoption_supersessions.cases(adoption,path)
            cases=[full[(c['physicalPage'],c['sourceRowOnPage'])]if not any(c.get(k)for k in ['basis','assumptionBasis','contextualAssumption','ownSourceObservation','sourceAssumptionBasis'])else c for c in cases]
        if adoption.get('caseLedgerFile'):
            pp=REVIEWS/adoption['caseLedgerFile']
            if sha(pp.read_bytes())!=adoption['caseLedgerSha256']:raise ValueError('Root-adopted original case ledger changed')
        if adoption.get('independentPeer'):pinned(adoption['independentPeer'])
        if adoption.get('independentPeerFile'):
            pp=REVIEWS/adoption['independentPeerFile']
            if sha(pp.read_bytes())!=adoption['independentPeerSha256']:raise ValueError('Root-adopted independent case peer changed')
        for case in cases:
            key=(source,case['physicalPage'],case['sourceRowOnPage'])
            if key in result:raise ValueError('More than one root typography adoption for a source name')
            result[key]={'chosenName':chosen_name(case),'sourceSha256':adoption['sourceSha256'],
                         **({'qualificationKind':case['ambiguityKind']} if 'ambiguityKind' in case else {}),
                         'rootAdoption':pin(path),'completeAdoptionEvidence':adoption,
                         'originalCaseEvidence':case,'allAdditionalRootAlternativesRetained':True,
                         'caseProvenByPixels':False,'sourcePublicWarningRequired':True}
            if path in adoption_selections:result[key]['rootAdoptionSupersession']=adoption_selections[path]
    return result


def verify_overlay(path,overlay):
    """Replay derived review bytes offline; no OCR models or original-PDF cache."""
    import finish_salary_phsa_resolutions as resolutions
    kind=overlay.get('kind')
    if kind=='complete-first-table-independent-image-benchmark-review':
        expected=resolutions.benchmark(overlay['sourceId'])
    elif kind=='canonical-source-typography-metadata-supplement-revision':
        import finish_salary_phsa_canonical_supplements as canonical_supplements
        expected=canonical_supplements.build(overlay['originalSpecialSupplement'],overlay['rootAdoptionSupersession'])
    elif kind=='expressly-reserved-three-case-hyphen-source-name-supplement':
        import finish_salary_phsa_supplements as supplements
        expected=supplements.build()[overlay['sourceId']]
    elif kind=='complete-sixteen-case-additive-mac-prefix-name-review':
        import finish_salary_phsa_mac as mac
        expected=mac.build()[overlay['sourceId']]
    else:
        reference=overlay['reviewInput']
        expected=resolutions.ordinary(ROOT/reference['path'],reference['sha256'])
    if (json.dumps(expected,ensure_ascii=False,indent=2)+'\n').encode()!=path.read_bytes():
        raise ValueError('Derived source-review overlay does not replay exactly: '+str(path))


def manual_fields(verify=False):
    result={};inputs=[]
    import finish_salary_phsa_supersessions as supersessions
    selected,_=supersessions.selected((AREA/'overlays').glob('phsa-*-*.json'))
    for path in selected:
        overlay=json.loads(path.read_text())
        if 'overlays' not in overlay:continue
        if verify:verify_overlay(path,overlay)
        source=overlay['sourceId'];inputs.append(pin(path))
        if overlay.get('reviewInput'):
            reference=overlay['reviewInput'];ip=ROOT/reference['path']
            if sha(ip.read_bytes())!=reference['sha256']:raise ValueError('Immutable image-review input changed')
        for row in overlay['overlays']:
            proof=ROOT/row['pageEvidencePath']
            if sha(proof.read_bytes())!=row['pageEvidenceSha256']:raise ValueError('Reviewed raw source row changed')
            for field in row['reviewedFields']:
                key=(source,row['physicalPage'],row['sourceRowOnPage'],field)
                if key in result:raise ValueError('Overlapping image-reviewed field scopes')
                result[key]={'value':row['resolvedRow'][FIELDS[field]],'rawCandidateRow':row['rawCandidateRow'],
                             'status':row['resolutionStatus'],'nameTypographyQualification':row.get('nameTypographyQualification') if field=='name' else None,
                             'overlay':pin(path),'sourceReview':row['reviewInput'],
                             'pageEvidenceSha256':row['pageEvidenceSha256']}
    return result,inputs


def holdout_fields():
    result={};receipts=[];reviewer_corrections=0
    inventory=json.loads((AREA/'source-inventory.json').read_text())['sources']
    expected={s['id']:s for s in inventory};required={f'phsa-{year}-{str(year+1)[-2:]}'for year in range(2015,2024)}
    if set(expected)!=required or len(inventory)!=9:raise ValueError('Exactly nine distinct historical source identities are required')
    seen_sources=set()
    for path in sorted(REVIEWS.glob('root-phsa-history-*-holdout-source-comparison.json')):
        review=json.loads(path.read_text())
        if not review['allRequestedFieldsMatchExactly'] or review['candidateChanges'] or review['unresolvedFields']:
            raise ValueError('Source holdout failed: paired-reader policy must halt/revise')
        source=review['sourceId']
        if source not in expected or source in seen_sources:raise ValueError('Unknown or duplicate source-layout holdout')
        seen_sources.add(source);packet=pinned(review['sourceOnlyPacket']);candidate=pinned(review['candidate'])
        pinned(review['imageFirstTranscript'])
        if (packet['sourceId'],candidate['sourceId'])!=(source,source) or review['candidate']!=packet['fullCandidate']:
            raise ValueError('Holdout source/candidate pin differs from the frozen source-only packet')
        if packet['sourceSha256']!=review['sourceSha256'] or candidate['sourceSha256']!=review['sourceSha256'] or review['sourceSha256']!=expected[source]['sourceSha256']:
            raise ValueError('Holdout original-source identity mismatch')
        if review['rows']!=10 or len(packet['rows'])!=10 or len(candidate['rows'])!=10:
            raise ValueError('Every source-layout holdout requires all ten complete selected rows')
        row_keys=set()
        for row,blind in zip(candidate['rows'],packet['rows']):
            key=(row['physicalPage'],row['sourceRowOnPage'])
            if key in row_keys or key!=(blind['physicalPage'],blind['sourceRowOnPage']) or row['sourceId']!=source or blind['sourceId']!=source:
                raise ValueError('Duplicate/mislabelled/misaligned source holdout row')
            row_keys.add(key)
            fields=row['reviewTargetFields']
            if fields!=blind['reviewTargetFields'] or not fields or len(fields)!=len(set(fields)) or set(fields)!=set(row['expectedValues']) or not set(fields)<=set(FIELDS):
                raise ValueError('Frozen source holdout field scope differs')
            for field in row['reviewTargetFields']:
                value=row['expectedValues'][field]
                if field=='name':
                    if not isinstance(value,str) or not value.strip():raise ValueError('Unparsed source holdout name')
                elif type(value)is not int or value<=0:raise ValueError('Holdout policy only permits strictly positive integer money')
                key=(source,row['physicalPage'],row['sourceRowOnPage'],field)
                if key in result:raise ValueError('Duplicate holdout field')
                result[key]={'value':row['expectedValues'][field],'status':'independent-blind-source-policy-holdout',
                             'rootComparison':pin(path),'imageFirstTranscript':review['imageFirstTranscript'],
                             'sourceOnlyPacket':review['sourceOnlyPacket']}
        reviewer_corrections+=review['reviewerReadingCorrections']
        receipts.append(pin(path))
    if seen_sources!=required:raise ValueError('All nine distinct source-layout holdouts must close')
    return result,receipts,reviewer_corrections


def build(source_filter=None,verify_overlays=False):
    inventory=json.loads((AREA/'source-inventory.json').read_text())['sources']
    actual={s['sourceId']:s for s in json.loads((REVIEWS/'independent-phsa-history-source-context-controls.json').read_text())['sources']}
    manual,manual_inputs=manual_fields(verify_overlays);holdout,holdout_inputs,own_corrections=holdout_fields()
    if set(manual)&set(holdout):raise ValueError('Holdout was not disjoint from preexisting manual fields')
    import finish_salary_phsa_triangulation as triangulation
    money_peers=triangulation.confirmations()
    reserved,_=policy.reserved_fields();adoptions=typography_adoptions();sources=[]
    import finish_salary_phsa_retirements as retirements
    retired_cases=retirements.records()
    for key,proof in manual.items():
        q=proof['nameTypographyQualification']
        if not q or not q.get('closedExactCaseRootAdoption'):continue
        adoption=pinned(q['closedExactCaseRootAdoption']);pinned(q['closedExactCasePolicy'])
        if adoption.get('acceptedQualifiedCases') is not True:raise ValueError('Unadopted closed source-name exception')
        row_key=key[:3]
        if row_key in adoptions:raise ValueError('Closed source case overlaps another qualification authority')
        adoptions[row_key]={'chosenName':q['chosenName'],'sourceSha256':adoption['sourceSha256'],
                           'qualificationKind':'exact-root-bound-source-name-alternatives',
                           'rootAdoption':q['closedExactCaseRootAdoption'],'completeAdoptionEvidence':adoption,
                           'originalCaseEvidence':q['originalCaseEvidence'],'closedCasePolicy':q['closedExactCasePolicy'],
                           'allAdditionalRootAlternativesRetained':True,'caseProvenByPixels':False,'sourcePublicWarningRequired':True}
    for source in inventory:
        key=source['id']
        if source_filter and key not in source_filter:continue
        paths=sorted((COLLECTION/'evidence').glob(key+'-rows-p*.json.gzip'));pages=[];rows=[]
        pending=[];qualified=[];counts=collections.Counter();field_counts=collections.defaultdict(collections.Counter)
        for path in paths:
            page=json.loads(gzip.decompress(path.read_bytes()));pn=page['physicalPage'];pages.append({'physicalPage':pn,**pin(path),'rows':len(page['rows'])})
            if (page['sourceId'],page['sourceSha256'])!=(key,source['sourceSha256']):
                raise ValueError('Staged physical page is from a different original source')
            for row in page['rows']:
                assessment=policy.classify(row,page);final=list(row['candidateRow']);field_proof={}
                for field,index in FIELDS.items():
                    fk=(key,pn,row['sourceRowOnPage'],field);rk=fk[:3]
                    if fk in manual:
                        proof=manual[fk]
                        if proof['rawCandidateRow']!=row['candidateRow']:raise ValueError('Image overlay binds a different raw observation')
                        final[index]=proof['value'];status='manual-original-image';detail=proof
                        if proof['nameTypographyQualification']:
                            q=adoptions.get(rk)
                            if q is None:status='pending-exact-root-typography-adoption'
                            elif q['sourceSha256']!=source['sourceSha256'] or q['chosenName']!=proof['value']:
                                raise ValueError('Root adopted a different exact contextual source name')
                            else:status='manual-qualified-source-typography';detail={**proof,'rootCaseAdoption':q};qualified.append({'physicalPage':pn,'sourceRowOnPage':row['sourceRowOnPage'],**q})
                        elif field!='name' and proof['value'] is not None and not triangulation.matches_reader(row,field,proof['value']):
                            peer=money_peers.get(fk)
                            if peer is None:status='pending-fresh-source-money-peer';detail={**proof,'neitherIndependentParsedReaderMatches':True}
                            elif peer['sourceSha256']!=source['sourceSha256'] or peer['confirmedValue']!=proof['value'] or peer['effectiveAuthorOverlay']!=proof['overlay']:
                                raise ValueError('Fresh source-money peer does not bind the effective reviewed amount')
                            else:detail={**proof,'freshIndependentSourceMoneyPeer':peer}
                    elif fk in holdout:
                        proof=holdout[fk]
                        if proof['value']!=final[index]:raise ValueError('A passed source holdout changed candidate data')
                        status='manual-blind-source-holdout';detail=proof
                    elif fk in reserved:
                        status='pending-frozen-image-review';detail={'frozenFieldScopePreserved':True}
                    elif field in assessment['manualFieldsBeforeExistingReviewCoverage']:
                        status='pending-source-image-review';detail=assessment['fields'][field]
                    elif assessment['fields'][field]['eligibleToResolveUnreservedConfidenceOnly']:
                        status='calibrated-paired-reader-confidence-corroboration';detail=assessment['fields'][field]
                        if detail['value']!=final[index]:raise ValueError('Confidence policy may not change any salary value')
                    elif field=='expenses' and final[index] is None:
                        status='original-source-explicit-dash-geometry';detail=row['expenseOriginalImage']
                    else:
                        status='baseline-independent-reader-agreement';detail=assessment['fields'][field]
                    field_counts[field][status]+=1;field_proof[field]={'status':status,'evidence':detail,
                                                                    'originalRawFlags':row['fieldConflicts'].get(field,[])}
                    if status.startswith('pending-'):pending.append({'sourceId':key,'physicalPage':pn,'sourceRowOnPage':row['sourceRowOnPage'],'field':field,'status':status})
                if final!=row['candidateRow']:counts['rowsChangedFromRawCandidate']+=1
                counts['originalFlaggedRows']+=bool(row['requestedFields'])
                rows.append({'row':final,'rawCandidateRow':row['candidateRow'],'sourceRowOnPage':row['sourceRowOnPage'],
                             'sourcePageEvidence':pin(path),'sourceImageSha256':page['sourceImageSha256'],
                             'originalRawFieldFlags':row['fieldConflicts'],'fields':field_proof})
        pns=[p['physicalPage'] for p in pages]
        if len(pns)!=len(set(pns)):raise ValueError('Duplicate physical source pages')
        complete=set(pns)==set(range(1,source['pdfPages']+1))
        pay=sum(r['row'][3] for r in rows if type(r['row'][3]) in [int,float])
        expense=sum(r['row'][4] for r in rows if type(r['row'][4]) in [int,float])
        controls=actual[key]['finalPagePrintedControls']
        sources.append({'sourceId':key,'sourceSha256':source['sourceSha256'],'completePhysicalSource':complete,
                        **({'rootAcceptedQualifiedNameRetirements':[r for r in retired_cases if r['sourceId']==key]}
                           if any(r['sourceId']==key for r in retired_cases)else {}),
                        'physicalPages':pages,'rowCount':len(rows),'rows':rows,'pendingFields':pending,
                        'fieldResolutionCounts':{f:dict(v) for f,v in field_counts.items()},'counts':dict(counts),
                        'rootAdoptedQualifiedNameCases':qualified,'diagnosticRemunerationSum':pay,
                        'diagnosticKnownExpenseSum':expense,'sourcePrintedControls':controls,
                        'diagnosticControlResiduals':[pay-controls['remuneration'],expense-controls['expenses']],
                        'expenseNullRows':sum(r['row'][4] is None for r in rows),
                        'explicitZeroExpenseRows':sum(r['row'][4]==0 for r in rows),
                        'negativeExpenseRows':sum(r['row'][4] is not None and r['row'][4]<0 for r in rows)})
    import finish_salary_phsa_supersessions as supersessions
    _,selection_pins=supersessions.selected((AREA/'overlays').glob('phsa-*-*.json'))
    return {'version':2,'fieldPolicy':pin(policy.POLICY),'sourceInventory':pin(AREA/'source-inventory.json'),
            'processingProfiles':pin(AREA/'processing-profile-index-001.json'),
            'sourceContextControls':pin(REVIEWS/'independent-phsa-history-source-context-controls.json'),
            'independentOriginalRowGeometry':pin(policy.ANCHORS),
            'sources':sources,'manualOverlayInputs':manual_inputs,'manualOverlaySupersessions':selection_pins,
            'rootHoldoutComparisons':holdout_inputs,'completedSourceHoldouts':len(holdout_inputs),
            'holdoutReviewerReadingCorrectionsDisclosed':own_corrections,
            'allNineSourceHoldoutsPassed':len(holdout_inputs)==9,
            'noSourceAcceptanceClaimUntilEveryManualFieldPolicyGateControlAndIndependentClosureCloses':True}


def run():
    result=build();out=AREA/'field-ledger-progress.json.gzip'
    out.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    summary=[{k:s[k] for k in ['sourceId','completePhysicalSource','rowCount','diagnosticRemunerationSum','diagnosticKnownExpenseSum','diagnosticControlResiduals']}
             |{'pendingFields':len(s['pendingFields']),'fieldResolutionCounts':s['fieldResolutionCounts']} for s in result['sources']]
    (AREA/'field-ledger-progress-summary.json').write_text(json.dumps({'sources':summary,'allNineSourceHoldoutsPassed':result['allNineSourceHoldoutsPassed'],
                                                                   'holdoutReviewerCorrections':result['holdoutReviewerReadingCorrectionsDisclosed']},indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':run()
