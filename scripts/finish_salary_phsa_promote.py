#!/usr/bin/env python3
"""Promote all nine immutable held candidates only after exact root adoption.

The candidates, source validation and provenance files remain unchanged. Only
the separate active manifest receives verified status and the final acceptance
pins. This is an offline deterministic metadata operation, not source research.
"""
import argparse
import copy
import gzip
import json

import finish_salary_phsa_finalize as finalizer
import finish_salary_phsa_ledger as ledger
import finish_salary_phsa_canonical as canonical


def selected_candidate_path(source, accepted):
    revision = accepted.get('candidateRevision')
    if type(revision) is not int or revision not in (3, 4):
        raise ValueError('Root must explicitly select immutable candidate revision 3 or 4')
    expected = ledger.AREA / 'candidates' / f'{source}-source-v{revision}.json'
    if accepted['finalCandidate']['path'] != str(expected.relative_to(ledger.ROOT)):
        raise ValueError('Root candidate path differs from its explicitly selected revision')
    return expected


def verify_canonical_source_review(source, source_sha, accepted, original):
    references = accepted.get('canonicalSourceViewReviewReceipts')
    if not isinstance(references, list) or len(references) != 1:
        raise ValueError('Exactly one complete root canonical source closure is required per source')
    canonical.validate(references[0], source, source_sha, original)
    expected_count = accepted.get('canonicalQualifiedNameCount')
    if (type(expected_count) is not int or expected_count < 0
            or expected_count != len(original['rootAdoptedQualifiedNameCases'])):
        raise ValueError('Canonical qualified-name scope differs from the selected provenance')
    corrections = accepted.get('canonicalNameCorrections')
    if not isinstance(corrections, list):
        raise ValueError('Root must explicitly enumerate canonical name corrections, including none')
    locations = {(row['row'][5], row['sourceRowOnPage']): row for row in original['rows']}
    seen = set()
    for correction in corrections:
        location = (correction['physicalPage'], correction['sourceRowOnPage'])
        if location in seen or location not in locations:
            raise ValueError('Canonical name correction has a repeated or absent original row')
        seen.add(location)
        row = locations[location]
        if row['row'][1] != correction['value']:
            raise ValueError('Selected candidate retains a superseded canonical name reading')
        if correction.get('requiresDirectLiteral') is True and (
                row['fields']['name']['status'] == 'manual-qualified-source-typography'):
            raise ValueError('A clear canonical literal correction cannot retain an old glyph waiver')
        ledger.pinned(correction['evidence'])


def build(root_reference):
    adoption=ledger.pinned(root_reference)
    if adoption.get('acceptedAllNineHistoricalPhsaSources') is not True:
        raise ValueError('Explicit root adoption of all nine complete source scopes is required')
    if adoption.get('canonicalSourceViewAuditComplete') is not True:
        raise ValueError('All nine canonical whole-page source audits must be closed before promotion')
    inventory={s['id']:s for s in json.loads((ledger.AREA/'source-inventory.json').read_text())['sources']}
    entries=adoption['sources'];by_source={s['sourceId']:s for s in entries}
    if len(entries)!=9 or len(by_source)!=9 or set(by_source)!=set(inventory):
        raise ValueError('Root adoption must identify exactly the nine original sources once')
    result=[]
    for source in inventory:
        spec=inventory[source];accepted=by_source[source]
        selected_candidate_path(source, accepted)
        candidate=ledger.pinned(accepted['finalCandidate'])
        if (candidate['id'],candidate['sha256'],candidate['dataSha256'],candidate['provenanceSha256'])!=(
                'queue-completion-'+source+'-employees',spec['sourceSha256'],
                accepted['dataSha256'],accepted['provenanceSha256']):
            raise ValueError('Root candidate/source/data/provenance identity differs')
        if accepted['sourceSha256']!=spec['sourceSha256'] or candidate['status']!='held-for-peer-review':
            raise ValueError('Only the exact held original-source candidate may be promoted')
        validation=candidate['validation']
        if (validation['completeEmployeeSchedule'] is not True
                or validation['finalIndependentSourceClosureAndRootAcceptanceStillRequired'] is not True
                or validation['allNineSourceHoldoutsPassed'] is not True
                or candidate['retainCompiledPartition'] is not True):
            raise ValueError('Candidate final source/publication gates are incomplete')
        payload_path=ledger.COLLECTION/candidate['file']
        if ledger.sha(payload_path.read_bytes())!=candidate['dataSha256']:
            raise ValueError('Final original salary payload changed')
        provenance_path=ledger.COLLECTION/candidate['provenanceFile']
        if ledger.sha(provenance_path.read_bytes())!=candidate['provenanceSha256']:
            raise ValueError('Final original provenance changed')
        provenance=json.loads(gzip.decompress(provenance_path.read_bytes()))
        original=provenance['originalRowsAndPerFieldResolution']
        verify_canonical_source_review(source, spec['sourceSha256'], accepted, original)
        rows=finalizer.validate_source(original,spec)
        if finalizer.packed(rows)!=payload_path.read_bytes() or candidate['rowCount']!=len(rows):
            raise ValueError('Complete source provenance does not reproduce exact payload bytes')
        residual=accepted['acceptedLiteralControlResiduals']
        if (len(residual)!=2 or any(type(v)is not int for v in residual)
                or residual!=validation['sourceControlResiduals']
                or residual!=original['diagnosticControlResiduals']):
            raise ValueError('Literal source residual was not exactly adopted')
        if [sum(r[3]for r in rows),sum(r[4]or 0 for r in rows)]!=[
                candidate['totalRemuneration'],candidate['totalDisclosedExpenses']]:
            raise ValueError('Active source monetary totals differ from literal rows')
        evidence=ledger.pinned({'path':str((ledger.COLLECTION/candidate['evidenceFile']).relative_to(ledger.ROOT)),
                                'sha256':candidate['evidenceSha256']})
        if evidence['validation']!=validation or evidence['status']!='held-for-peer-review':
            raise ValueError('Immutable candidate validation evidence differs')
        peer=ledger.pinned(accepted['independentSourceClosure'])
        if (peer['sourceId'],peer['sourceSha256'],peer['candidateMetadata'],peer['payload']['sha256'],
                peer['provenance']['sha256'],peer['checkedLiteralNamedRows'],peer['checkedCompletePhysicalPages'])!=(
                source,spec['sourceSha256'],accepted['finalCandidate'],candidate['dataSha256'],
                candidate['provenanceSha256'],len(rows),spec['pdfPages']):
            raise ValueError('Independent final source closure pins a different scope')
        for flag in ['independentRawPlusOnlyExactPinnedOverlayReconstructionEqualsPayload',
                     'allOriginalRowOrderMultiplicityAndNonreviewedFieldsPreserved',
                     'everyFieldHasExactlyOneClosedEvidenceRoute']:
            if peer[flag] is not True:raise ValueError('Independent final source replay has an open gate')
        if peer['literalSourceControlResiduals']!=residual:
            raise ValueError('Independent source residual differs from root-adopted literal controls')
        active=copy.deepcopy(candidate);active['status']='verified'
        active['validation']['finalIndependentSourceClosureAndRootAcceptanceStillRequired']=False
        active['validation']['rootAcceptanceReceipt']=root_reference
        active['validation']['independentSourceClosure']=accepted['independentSourceClosure']
        active['validation']['canonicalSourceViewReviewReceipts']=accepted['canonicalSourceViewReviewReceipts']
        active['validation']['canonicalCandidateRevision']=accepted['candidateRevision']
        result.append(active)
    return {'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':result}


def run(root_reference,check=False):
    result=build(root_reference);out=ledger.COLLECTION/'sources.json'
    raw=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if check:
        if out.read_bytes()!=raw:raise ValueError('Active promoted source manifest does not replay')
    else:
        if out.exists():
            previous=json.loads(out.read_text())
            if any(s['status']=='verified' for s in previous['sources']) and out.read_bytes()!=raw:
                raise ValueError('Never overwrite a different already verified source manifest')
        out.write_bytes(raw)
    print(json.dumps({'activeManifest':ledger.pin(out),'sources':9,'rows':sum(s['rowCount']for s in result['sources'])}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root-adoption',required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    path,digest=a.root_adoption.rsplit('=',1);run({'path':path,'sha256':digest},a.check)
