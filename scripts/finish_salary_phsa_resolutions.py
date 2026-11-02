#!/usr/bin/env python3
"""Replay hash-pinned historical PHSA image reviews without widening field scope."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
EXACT='resolved-from-original-image'
QUALIFIED={'resolved-with-source-typography-qualification','resolved-qualified-typography'}
FIELDS={'name':1,'remuneration':3,'expenses':4}
SEGMENTATION_POLICY=AREA/'source-name-segmentation-review-policy-002.json'
SEGMENTATION_POLICY_SHA='fcfc11b7872b8c111018dd5b74494ea25391d14e1e905aa327f6a435c6e1e40c'
CLOSED_CASE_POLICIES=[(AREA/'source-name-exact-case-policy-003.json','3da14db00810790ca9fdbe3729ec52e6e0d9b1086e88698d6126d549291b1a1d'),
                      (AREA/'source-name-exact-case-policy-004.json','9a2f82b753971b4b25a8ff63abd1674215d704850f1d1ac53bd9bb3ccc260c31'),
                      (AREA/'source-name-exact-case-policy-005.json','175217a01017d57f2300518eb3c6e87770a093fa2c2e4765e50e82116324fb42'),
                      (AREA/'source-name-exact-case-policy-006.json','9d072042974ec9954fca8cd320086f32255fd076cc94dfd835b3bfc4b0cd5fe7'),
                      (AREA/'source-name-exact-case-policy-007.json','67a4e03a01de990536f26c67f5b2980198042a10988aea7da7b8903add5c90a7'),
                      (AREA/'source-name-exact-case-policy-008.json','5eaaed01420823f117c163609c95e76f7b0e5f04821335de0f25ff2517673613'),
                      (AREA/'source-name-exact-case-policy-009.json','4446cdbcd9f43f43f2c09df1022e718d3b755d9dffd556ba20d6354b0bef5f94'),
                      (AREA/'source-name-exact-case-policy-010.json','a76cabe0450b45564005672282284159a27f53c5011734c50b089721690ed1fe'),
                      (AREA/'source-name-exact-case-policy-011.json','e987bbb7d9defac135e76fb05630917c4c86c021d4cd3507816345613eb55592'),
                      (AREA/'source-name-exact-case-policy-012.json','d99b9ceedeb12cd7bb0884ccb9c2128af64b611704f61b1ec190be46e4c1932c'),
                      (AREA/'source-name-exact-case-policy-013.json','4e8eac76748cfd6fc175f5ad2ed6be9d830d94cca23dfeecd214b020cdb1ffc5'),
                      (AREA/'source-name-exact-case-policy-014.json','56e377842c62dd97dee5b9eba732fd3cbb8d0729e5fc22ee9da420ab33a94273'),
                      (AREA/'source-name-exact-case-policy-015.json','fd4cdc09e85868612b6991d9c355338020b54a6e1a7eb5dabbc973e4b6d1b0ba'),
                      (AREA/'source-name-exact-case-policy-016.json','cba75b7e4aac067579e924d31434b36a4efd4d5183b42cb6378bbbe6c8e7105e'),
                      (AREA/'source-name-exact-case-policy-017.json','9f5356bae189cb7008b1f8ae033d666ac6076fd330248e45e27c0f9ef924bb82'),
                      (AREA/'source-name-exact-case-policy-018.json','fdb94566d5afde198d7aaa43106129165ec98cc1b84e1adfd34dcfe0d5c2cfed'),
                      (AREA/'source-name-exact-case-policy-019.json','bf3da94f47d7d603c3c521a9a6184150e1ec71cde0d556cece3c12f3736f64ce'),
                      (AREA/'source-name-exact-case-policy-020.json','f25e7e0ddb89b5afbaa1b3b38cd62a1cb8cf0218ee36b37b3bd31a2d3b95b8c7'),
                      (AREA/'source-name-exact-case-policy-021.json','239104455ff8f7dc4d54f77083ff25fd6d0d1496cfa0cb203872d1a290325f8d'),
                      (AREA/'source-name-exact-case-policy-022.json','7c16eccd8501f35078d73c7f4ea9b88fef0f649393cb3544dff1b2ae0fc66806')]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pinned(path,digest):
    if sha(path.read_bytes())!=digest:raise ValueError('Pinned source-review input changed: '+str(path))
    return json.loads(path.read_text())


def apply_values(before,requested,values):
    if len(requested)!=len(set(requested)) or set(requested)!=set(values) or not set(requested)<=set(FIELDS):
        raise ValueError('Review may change exactly its explicitly requested fields')
    result=list(before)
    for field,value in values.items():
        if field=='name':
            if not isinstance(value,str) or not value.strip():raise ValueError('Missing source name remains held')
        elif value is None:
            if field!='expenses':raise ValueError('Missing source remuneration remains held')
        elif type(value) not in (int,float) or not math.isfinite(value):
            raise ValueError('Unparsed or boolean source money is not a literal amount')
        result[FIELDS[field]]=value
    return result


def segmentation_difference(primary,alternative):
    """Validate a declared finite rn/m alternative without choosing a reading."""
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def walk(i,j):
        if i==len(primary) and j==len(alternative):return ()
        if i<len(primary) and j<len(alternative) and primary[i]==alternative[j]:
            tail=walk(i+1,j+1)
            if tail is not None:return tail
        for left,right in [('rn','m'),('m','rn')]:
            if primary.startswith(left,i) and alternative.startswith(right,j):
                tail=walk(i+len(left),j+len(right))
                if tail is not None:return ((i,j,left,right),)+tail
        return None
    changed=walk(0,0)
    if not changed:raise ValueError('Only explicitly declared rn/m source segmentations are qualified')
    return [{'primaryStartZeroBased':a,'alternativeStartZeroBased':b,
             'primaryVisibleSegment':left,'alternativeVisibleSegment':right} for a,b,left,right in changed]


def closed_source_cases(review):
    """Closed root-pinned exceptions; no generic extra-letter authority."""
    references=review.get('closedSourceNameQualificationLedgers',[])
    if not isinstance(references,list):raise ValueError('Explicit closed case-ledger pins must be listed')
    allowed={}
    for path,digest in CLOSED_CASE_POLICIES:
        policy=pinned(path,digest)
        for case in policy['approvedCases']:
            key=(case['sourceId'],case['physicalPage'],case['sourceRowOnPage'])
            reference={'path':str(path.relative_to(ROOT)),'sha256':digest}
            if key in allowed:
                previous,previous_policy=allowed[key][-1]
                if case.get('supersedesExactClosedAuthority')!={'policy':previous_policy,'rootAdoption':previous['rootAdoption'],'exactCaseLedger':previous['exactCaseLedger']}:
                    raise ValueError('Duplicate closed exception lacks exact historic authority selection')
                if any(case[k]!=previous[k]for k in ['sourceId','sourceSha256','batch','physicalPage','sourceRowOnPage','originalFullRowCropSha256']):
                    raise ValueError('Canonical closed authority changes its original source identity/primary')
                old=set(previous['completeVisibleAlternatives']);new=set(case['completeVisibleAlternatives'])
                revision=case.get('canonicalAuthorityRevision')
                if revision:
                    import finish_salary_phsa_adoption_supersessions as versions
                    _,selector=versions.load(revision['rootAdoptionSupersession']);oldpath,newpath=versions.validate(selector)
                    if (selector['supersededRootAdoption']!=previous['rootAdoption']or selector['effectiveRootAdoption']!=case['rootAdoption']
                            or selector['supersededCaseLedger']!=previous['exactCaseLedger']or selector['effectiveCaseLedger']!=case['exactCaseLedger']):
                        raise ValueError('Closed canonical replacement lacks the exact root authority chain')
                    beforecase=versions.cases(versions.load(previous['rootAdoption'])[1],oldpath)[key[1:]]
                    aftercase=versions.cases(versions.load(case['rootAdoption'])[1],newpath)[key[1:]]
                    if versions.primary(aftercase)!=case['primary']or set(versions.family(aftercase))!=new:
                        raise ValueError('Closed canonical policy differs from its exact selected root case')
                    if revision.get('unchangedCaseDictionaryRebind')is True:
                        if beforecase!=aftercase or old!=new:raise ValueError('Unchanged closed authority rebind changed a case dictionary')
                    else:
                        _,current=versions.load(revision['currentSourceAcceptance'])
                        rows=[r for r in current['rows']if(r['physicalPage'],r['sourceRowOnPage'])==key[1:]]
                        if (current.get('accepted')is not True or(current['sourceId'],current['sourceSha256'])!=(case['sourceId'],case['sourceSha256'])
                                or len(rows)!=1 or rows[0]['currentAcceptedSourceLiteral']!=case['primary']
                                or set(rows[0]['currentCompleteVisibleAlternatives'])!=new or rows[0]['currentSourceStatus']!='qualified'):
                            raise ValueError('Closed canonical replacement lacks exact current root source-family acceptance')
                else:
                    if case['primary']!=previous['primary']or not old<new:raise ValueError('Canonical closed authority must retain and expand its exact finite family')
                    for extra in new-old:
                        for before in old:
                            try:segmentation_difference(before,extra);break
                            except ValueError:pass
                        else:raise ValueError('Closed canonical expansion adds an unadopted extra-letter transform')
            allowed.setdefault(key,[]).append((case,reference))
    result={}
    for reference in references:
        original=pinned(ROOT/reference['path'],reference['sha256'])
        entries=original.get('sourceNameSegmentationExceptions',original.get('separateClosedRrMExceptionsAwaitingExactRootAdoption',original.get('cases',[])))
        if not entries:raise ValueError('No explicit closed source-case entries')
        for case in entries:
            key=(case.get('sourceId',original['sourceId']),case['physicalPage'],case['sourceRowOnPage'])
            if key not in allowed:raise ValueError('Unknown source row has no closed exception authority')
            versions=[v for v in allowed[key]if v[0]['exactCaseLedger']==reference]
            if len(versions)!=1:raise ValueError('Closed case ledger must select one exact historical/canonical authority')
            authority,policy_reference=versions[0];adoption=pinned(ROOT/authority['rootAdoption']['path'],authority['rootAdoption']['sha256'])
            identity=(key[0],original['sourceSha256'],original['batch'])
            expected=(authority['sourceId'],authority['sourceSha256'],authority['batch'])
            if identity!=expected or (review['sourceId'],review['sourceSha256'],review['batch'])!=expected:
                raise ValueError('Closed exception source/year/batch scope differs')
            if reference!=authority['exactCaseLedger'] or adoption.get('acceptedQualifiedCases') is not True:
                raise ValueError('Exact root adoption is required before closed exception overlay')
            if adoption['exactCaseLedger']!=reference or (adoption['sourceId'],adoption['sourceSha256'],adoption['batch'])!=expected:
                raise ValueError('Closed root adoption pins a different original ledger')
            primary=case.get('proposedName',case.get('primary',case.get('chosenContextualTranscription')));alternatives=case['visibleAlternatives']
            actual_crop=case.get('cropSha256',case.get('actualSourceEvidence',{}).get('originalFullRowCropSha256'))
            if primary!=authority['primary'] or len(alternatives)!=len(set(alternatives)) or set(alternatives)!=set(authority['completeVisibleAlternatives']):
                raise ValueError('Closed exception primary or complete alternative set differs')
            if actual_crop!=authority['originalFullRowCropSha256'] or case.get('caseProvenByPixels') is not False:
                raise ValueError('Closed exception source crop or honest ambiguity differs')
            root_cases=adoption.get('exactCases',adoption.get('closedCases'))
            if root_cases is None:
                if type(adoption.get('qualifiedCases'))is int:
                    if adoption['qualifiedCases']!=len(entries)or not entries:
                        raise ValueError('Exact root adoption count differs from pinned closed ledger')
                    root_cases=entries
                else:root_cases=[adoption]
            matches=[c for c in root_cases if (c['physicalPage'],c['sourceRowOnPage'])==key[1:]]
            if len(matches)!=1:raise ValueError('Exact root source-row adoption missing')
            root_case=matches[0];root_primary=root_case.get('primary',root_case.get('proposedName',root_case.get('chosenContextualTranscription')))
            if root_primary!=primary or set(root_case['visibleAlternatives'])!=set(alternatives):
                raise ValueError('Root did not adopt the exact finite case set')
            if root_case.get('allowedFields',['name'])!=['name']:raise ValueError('Closed source-case authority is name-only')
            basis=case.get('assumptionBasis',case.get('basis',case.get('sourceAssumptionBasis')))
            if not basis:raise ValueError('Closed exception needs original-source ambiguity basis')
            row_key=key[1:]
            if row_key in result:raise ValueError('Duplicate closed name exception')
            result[row_key]={'originalCaseEvidence':case,'chosenName':primary,
                             'visibleAlternatives':[v for v in alternatives if v!=primary],
                             'characterPositionsZeroBased':[],'assumptionBasis':basis,'caseProvenByPixels':False,
                             'requiresExactPeerAndRootCaseAdoption':True,'sourceCaseLedger':reference,
                             'ambiguityKind':'exact-root-bound-source-name-alternatives',
                             'closedExactCaseRootAdoption':authority['rootAdoption'],
                             'closedExactCasePolicy':policy_reference,
                             'authorizedFields':['name'],'cropSha256':actual_crop}
    return result


def typography_cases(review):
    spec=review.get('sourceTypographyQualifications',[])
    ledger_pin=None
    if isinstance(spec,dict):
        path=ROOT/spec['path'];ledger=pinned(path,spec['sha256']);ledger_pin=spec
        if ledger['sourceSha256']!=review['sourceSha256'] or ledger['batch']!=review['batch']:
            raise ValueError('Wrong original-source typography ledger')
        cases=ledger.get('qualifications',ledger.get('cases',[]))
    elif isinstance(spec,list):cases=spec
    else:raise ValueError('Unrecognized explicit source-typography evidence')
    result={}
    for case in cases:
        key=(case['physicalPage'],case['sourceRowOnPage'])
        if key in result:raise ValueError('Duplicate qualified source-name case')
        chosen=case.get('chosenContextualTranscription',case.get('proposedName',case.get('resolvedContextualName')))
        alternative=case.get('typographicallyPossibleAlternative',case.get('visibleAlternative'))
        listed=case.get('visibleAlternatives',case.get('visibleIOrLowerLAlternatives'))
        if listed is None and alternative is None and 'alternative'in case:
            # Canonical metadata revisions preserve unchanged embedded legacy
            # case dictionaries. Only those exact original14 dictionaries may
            # use the historical singular key.
            import finish_salary_phsa_adoption_supersessions as revisions
            legacy=json.loads(revisions.LEGACY14.read_text())
            matches=[c for c in legacy['cases']if(c['physicalPage'],c['sourceRowOnPage'])==key]
            if (not revisions.exact_legacy14(revisions.LEGACY14,legacy)
                    or (review['sourceId'],review['sourceSha256'],review['batch'])!=(legacy['sourceId'],legacy['sourceSha256'],legacy['batch'])
                    or len(matches)!=1 or case!=matches[0]):
                raise ValueError('Singular alternative is restricted to exact legacy14 case dictionaries')
            alternative=case['alternative']
        if isinstance(listed,list):
            alternatives=[v for v in listed if v!=chosen]
        elif isinstance(alternative,str):
            # Preserve an explicitly enumerated multi-glyph alternative set; no
            # letters or new alternative spellings are manufactured here.
            alternatives=alternative.split(' / ')
        else:alternatives=[]
        basis=case.get('basis',case.get('assumptionBasis',case.get('contextualAssumption',case.get('ownSourceObservation'))))
        if not chosen or not alternatives or not basis:
            raise ValueError('Qualified transcription needs its exact visible alternatives and source context')
        kind=case.get('ambiguityKind','I-l-source-case');differences=set();segments=[]
        if kind=='rn-m-source-segmentation':
            reference=case.get('qualificationPolicy')
            expected={'path':str(SEGMENTATION_POLICY.relative_to(ROOT)),'sha256':SEGMENTATION_POLICY_SHA}
            if reference!=expected:raise ValueError('rn/m qualification needs the exact new policy pin')
            pinned(SEGMENTATION_POLICY,SEGMENTATION_POLICY_SHA)
            for alternate in alternatives:segments.append({'visibleAlternative':alternate,'segments':segmentation_difference(chosen,alternate)})
        elif kind=='I-l-source-case':
            for alternate in alternatives:
                if len(chosen)!=len(alternate):raise ValueError('I/l source case cannot expand name letters')
                changed=[i for i,(a,b) in enumerate(zip(chosen,alternate)) if a!=b]
                if not changed or any({chosen[i],alternate[i]}!={'I','l'} for i in changed):
                    raise ValueError('Typography authority does not permit other name letters or expansion')
                differences.update(changed)
        else:raise ValueError('Unadopted source-name ambiguity kind')
        if case.get('caseProvenByPixels') is True:raise ValueError('Qualified case must not claim a pixel case proof')
        result[key]={'originalCaseEvidence':case,'chosenName':chosen,'visibleAlternatives':alternatives,
                     'characterPositionsZeroBased':sorted(differences),'assumptionBasis':basis,
                     'caseProvenByPixels':False,'requiresExactPeerAndRootCaseAdoption':True,
                     'sourceCaseLedger':ledger_pin}
        if segments:result[key].update({'ambiguityKind':kind,'declaredSourceSegmentations':segments,'qualificationPolicy':reference})
    for key,value in closed_source_cases(review).items():
        if key in result:raise ValueError('Closed exception must not overlap generic glyph policy')
        result[key]=value
    return result


def ordinary(review_path,review_sha):
    review=pinned(review_path,review_sha);source=review['sourceId'];batch=review['batch']
    batch_number=batch.rsplit('-',1)[1]
    bp=AREA/'batches'/f'{source}-batch-{batch_number}.json'
    ip=AREA/'batches'/f'{source}-batch-{batch_number}-images.json'
    frozen=pinned(bp,review['frozenBatchSha256']);images=pinned(ip,review['imageManifestSha256'])
    if frozen['sourceSha256']!=review['sourceSha256'] or images['sourceSha256']!=review['sourceSha256']:
        raise ValueError('Original-source hash differs from the image review')
    if review.get('unresolvedRows') not in [[],0]:raise ValueError('Unresolved source fields remain held')
    if review.get('rawTranscriptPath'):
        rp=ROOT/review['rawTranscriptPath']
        if sha(rp.read_bytes())!=review['rawTranscriptSha256']:raise ValueError('Image-first raw transcript changed')
    qualification=typography_cases(review)
    if review.get('canonicalCurrentFinancialSourceRevision'):
        from finish_salary_phsa_money_sparse_current import validate_financial_review
        validate_financial_review(review)
    elif review.get('canonicalCurrentSourceNameRevision'):
        from finish_salary_phsa_current_canonical import validate_review
        validate_review(review,qualification)
    policy_reserved=set()
    if frozen.get('fieldPolicy'):
        import finish_salary_phsa_policy as policy
        if frozen['fieldPolicy']['sha256']!=policy.POLICY_SHA:
            raise ValueError('Batch does not bind the approved new field policy')
        for reservation_pin in frozen['priorFieldReservationPins']:
            reservation=pinned(ROOT/reservation_pin['path'],reservation_pin['sha256'])
            if 'reservations' in reservation:
                for rr in reservation['reservations']:
                    if rr['sourceId']==source:
                        policy_reserved.update((rr['physicalPage'],rr['sourceRowOnPage'],f) for f in rr['reviewTargetFields'])
            elif reservation.get('sourceId')==source:
                entries=reservation.get('rows',reservation.get('overlays',[]))
                for rr in entries:
                    policy_reserved.update((rr['physicalPage'],rr['sourceRowOnPage'],f)
                                           for f in rr.get('reviewTargetFields',rr.get('reviewedFields',[])))
    by_key={(r['physicalPage'],r['sourceRowOnPage']):r for r in frozen['rows']}
    resolutions=review['resolutions'];seen=set();overlays=[];field_counts=collections.Counter()
    for resolution in resolutions:
        key=(resolution['physicalPage'],resolution['sourceRowOnPage'])
        if key in seen or key not in by_key:raise ValueError('Duplicate or out-of-scope source resolution')
        seen.add(key);original=by_key[key]
        if resolution['reviewTargetFields']!=original['reviewTargetFields']:
            raise ValueError('Do not widen an already frozen requested-field scope')
        if resolution['cropSha256']!=original['cropSha256']:raise ValueError('Reviewed actual source crop changed')
        status=resolution['status']
        if status!=EXACT and status not in QUALIFIED:raise ValueError('No accepted explicit source-resolution status')
        before=original['rawCandidateRow'];after=apply_values(before,original['reviewTargetFields'],resolution['resolvedValues'])
        q=qualification.get(key)
        if status in QUALIFIED:
            if q is None or 'name' not in original['reviewTargetFields'] or after[1]!=q['chosenName']:
                raise ValueError('Qualified case must bind the same explicitly reviewed source name')
            crop=q.get('cropSha256',q['originalCaseEvidence'].get('cropSha256',q['originalCaseEvidence'].get('originalFullRowCropSha256')))
            if crop is not None and crop!=original['cropSha256']:raise ValueError('Qualified visible source crop differs')
        elif q is not None:raise ValueError('Qualified typography must not be silently labelled exact glyph resolution')
        proof=ROOT/original['pageEvidencePath'];page=pinned_gzip(proof,original['pageEvidenceSha256'])
        row=page['rows'][key[1]-1]
        if row['candidateRow']!=before or page['sourceSha256']!=review['sourceSha256']:
            raise ValueError('Original row identity or candidate changed')
        if frozen.get('fieldPolicy'):
            assessment=policy.classify(row,page)
            expected=[f for f in assessment['manualFieldsBeforeExistingReviewCoverage'] if (*key,f) not in policy_reserved]
            if expected!=original['reviewTargetFields'] or row['requestedFields']!=original['rawOriginalRequestedFields']:
                raise ValueError('Versioned policy targets do not replay their original flags/reservations')
        elif row['requestedFields']!=original['reviewTargetFields']:raise ValueError('Original source flags differ')
        field_counts.update(original['reviewTargetFields'])
        overlays.append({'physicalPage':key[0],'sourceRowOnPage':key[1],'rawCandidateRow':before,
                         'resolvedRow':after,'reviewedFields':original['reviewTargetFields'],
                         'changedFields':[f for f in original['reviewTargetFields'] if before[FIELDS[f]]!=after[FIELDS[f]]],
                         'resolutionStatus':status,'nameTypographyQualification':q,
                         'pageEvidencePath':original['pageEvidencePath'],'pageEvidenceSha256':original['pageEvidenceSha256'],
                         'rawPageEvidence':original['rawPageEvidence'],'cropSha256':original['cropSha256'],
                         'reviewInput':{'path':str(review_path.relative_to(ROOT)),'sha256':review_sha}})
    if seen!=set(by_key) or len(overlays)!=frozen['rowsToReview']:
        raise ValueError('A complete frozen review batch has missing source resolutions')
    if set(qualification)-seen:raise ValueError('Unrequested typography case needs a separate supplemental ledger')
    return {'frozen':True,'sourceId':source,'sourceSha256':review['sourceSha256'],'batch':batch,
            'reviewInput':{'path':str(review_path.relative_to(ROOT)),'sha256':review_sha},
            'frozenBatch':{'path':str(bp.relative_to(ROOT)),'sha256':review['frozenBatchSha256']},
            'imageManifest':{'path':str(ip.relative_to(ROOT)),'sha256':review['imageManifestSha256']},
            'resolvedRows':len(overlays),'reviewedFieldCounts':dict(field_counts),
            'exactGlyphRows':sum(o['resolutionStatus']==EXACT for o in overlays),
            'qualifiedTypographyRows':sum(o['resolutionStatus'] in QUALIFIED for o in overlays),
            'qualifiedCasesRequirePeerAndRootAdoptionBeforeSourceAcceptance':bool(qualification),
            'overlays':overlays,'rawOcrAndFrozenBatchesUnchanged':True}


def pinned_gzip(path,digest):
    if sha(path.read_bytes())!=digest:raise ValueError('Pinned raw source page changed')
    return json.loads(gzip.decompress(path.read_bytes()))


def benchmark(source):
    pp=AREA/(source+'-processing-profile-001.json');profile=json.loads(pp.read_text())
    fixture=ROOT/profile['fixture']['path']
    if sha(fixture.read_bytes())!=profile['fixture']['sha256']:raise ValueError('Image-first benchmark changed')
    literal=list(csv.DictReader(fixture.open(),delimiter='\t'))
    pn=profile['firstSalaryPhysicalPage'];proof=COLLECTION/'evidence'/f'{source}-rows-p{pn:03d}.json.gzip'
    page=json.loads(gzip.decompress(proof.read_bytes()))
    if page['pageGeometryNeedsReview'] or len(page['rows'])!=len(literal):raise ValueError('Source fixture does not cover the complete actual table')
    overlays=[]
    for original,reading in zip(page['rows'],literal):
        if original['sourceRowOnPage']!=int(reading['sourceRowOnPage']) or pn!=int(reading['physicalPage']):
            raise ValueError('Fixture source row mapping differs')
        pay=reading['remunerationLiteral'].replace(',','');expense=reading['expensesLiteral']
        if not pay.isdigit():raise ValueError('Unparsed literal source remuneration')
        expense_value=None if expense in ['-','–','—'] else int(expense.replace(',',''))
        after=apply_values(original['candidateRow'],list(FIELDS),
                           {'name':reading['name'],'remuneration':int(pay),'expenses':expense_value})
        overlays.append({'physicalPage':pn,'sourceRowOnPage':original['sourceRowOnPage'],
                         'rawCandidateRow':original['candidateRow'],'resolvedRow':after,'reviewedFields':list(FIELDS),
                         'changedFields':[f for f in FIELDS if original['candidateRow'][FIELDS[f]]!=after[FIELDS[f]]],
                         'resolutionStatus':'independent-image-first-complete-table-transcription',
                         'nameTypographyQualification':None,'pageEvidencePath':str(proof.relative_to(ROOT)),
                         'pageEvidenceSha256':sha(proof.read_bytes()),'rawPageEvidence':page['rawPage'],
                         'reviewInput':profile['fixture']})
    return {'frozen':True,'sourceId':source,'sourceSha256':profile['sourceSha256'],
            'kind':'complete-first-table-independent-image-benchmark-review',
            'reviewInput':profile['fixture'],'resolvedRows':len(overlays),
            'reviewedFieldCounts':{f:len(overlays) for f in FIELDS},'overlays':overlays,
            'firstTableOnlyNotAWholeSourceAcceptanceClaim':True}


def write(value,path,check=False):
    data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    if check:
        if path.read_bytes()!=data:raise ValueError('Frozen image-review overlay does not replay')
    else:
        if path.exists():raise ValueError('Never overwrite a frozen source-review overlay')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps({'path':str(path.relative_to(ROOT)),'sha256':sha(data),'resolvedRows':value['resolvedRows']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--review');p.add_argument('--benchmark-source');p.add_argument('--out',required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.review:
        path,digest=a.review.rsplit('=',1);value=ordinary(ROOT/path,digest)
    elif a.benchmark_source:value=benchmark(a.benchmark_source)
    else:raise ValueError('Specify a pinned source review or complete image-first benchmark')
    write(value,ROOT/a.out,a.check)
