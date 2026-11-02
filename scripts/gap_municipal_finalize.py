#!/usr/bin/env python3
"""Apply an explicit, pinned independent-review decision to municipal candidates.

This module never treats successful OCR or arithmetic controls as source review.
The producer always constructs the original candidate bytes first. An acceptance
decision must name every cohort, pin those exact candidate bytes and a nonempty
independent peer receipt, and explicitly adopt any qualified pay definition.
No acceptance decision is created automatically by this script.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02/municipal'
COLLECTION = ROOT / 'research/salaries/gap-fill-municipal'
ACCEPTANCE = AREA / 'acceptance.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def packed(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def compressed(value):
    return gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode(), mtime=0)


def read_receipt(pin):
    path = (ROOT / pin['path']).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Peer receipt must be an existing repository file')
    raw = path.read_bytes()
    if not raw or sha(raw) != pin['sha256']:
        raise ValueError('Peer receipt hash changed: ' + pin['path'])
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(raw)}


def accepted_outputs(candidate_outputs, decision):
    candidate_manifest = candidate_outputs['sources.json']
    if decision.get('candidateManifestSha256') != sha(candidate_manifest):
        raise ValueError('Acceptance does not pin the current candidate manifest')
    if decision.get('approvedBy') != '/root' or decision.get('noOutreach') is not True:
        raise ValueError('Root adoption and no-outreach declaration are required')
    manifest = json.loads(candidate_manifest)
    sources = manifest['sources']
    reviews = decision.get('cohortReviews', [])
    if len(reviews) != len(sources) or len({r['sourceId'] for r in reviews}) != len(reviews):
        raise ValueError('Every candidate cohort requires one explicit independent review')
    review_by_id = {r['sourceId']: r for r in reviews}
    if set(review_by_id) != {s['id'] for s in sources}:
        raise ValueError('Review cohort set differs from the candidate manifest')
    adoptions = decision.get('qualifiedDefinitionAdoptions', [])
    if len({r['sourceId'] for r in adoptions}) != len(adoptions):
        raise ValueError('Repeated qualified-definition adoption')
    adoption_by_id = {r['sourceId']: r for r in adoptions}
    required_adoptions = {
        s['id'] for s in sources
        if s['validation'].get('partialCompensationDefinition')
        or any('Pay is uniformly the literal Remuneration column' in n for n in s['notes'])
    }
    if set(adoption_by_id) != required_adoptions:
        raise ValueError('Qualified pay definitions require an exact explicit adoption set')
    outputs = dict(candidate_outputs)
    original_count = len({s['sha256'] for s in sources})
    receipt_pins = {}
    for source in sources:
        review = review_by_id[source['id']]
        if review.get('approved') is not True:
            raise ValueError('Source is not independently approved: ' + source['id'])
        for field in ['completeIndependentLiteralFieldReview', 'originalSourceAndPeriodConfirmed',
                      'sourceControlResidualsAcceptedWithoutAdjustment']:
            if review.get(field) is not True:
                raise ValueError('Independent review declaration missing: ' + source['id'] + ' ' + field)
        if not review.get('reviewerAgent') or review['reviewerAgent'] == '/root/gap_municipal':
            raise ValueError('An independent reviewer must be named')
        for field, expected in [('sourceSha256', source['sha256']),
                                ('candidateDataSha256', source['dataSha256']),
                                ('candidateProvenanceSha256', source['provenanceSha256']),
                                ('rowCount', source['rowCount'])]:
            if review.get(field) != expected:
                raise ValueError('Peer review does not pin current literal inputs: ' + source['id'] + ' ' + field)
        receipt = read_receipt(review['receipt'])
        receipt_pins[receipt['path']] = receipt
        source['status'] = 'accepted'
        source['verified'] = True
        source['validation']['candidateOnly'] = False
        source['validation']['independentPeerVerified'] = True
        source['validation']['method'] = (
            'Complete author source transcription, preserved raw OCR/native readers, and complete '
            'independent image-first peer verification of each named literal field and scope. '
            'Printed source inconsistencies and unknown cells remain unchanged and qualified.'
        )
        source['validation']['independentReview'] = copy.deepcopy(review)
        evidence_path = source['provenanceFile']
        evidence = json.loads(gzip.decompress(candidate_outputs[evidence_path]))
        evidence['status'] = 'accepted-after-complete-independent-source-review'
        evidence['candidateEvidenceSha256'] = source['provenanceSha256']
        evidence['independentReview'] = copy.deepcopy(review)
        evidence['rawOcrLimitations'] += (
            ' Final acceptance is supported by the pinned independent source review, '
            'rather than an assumption that either raw reader is error-free.'
        )
        if source['id'] in required_adoptions:
            adoption = adoption_by_id[source['id']]
            if adoption.get('approvedBy') != '/root' or adoption.get('approved') is not True:
                raise ValueError('Qualified pay definition has not been adopted by root')
            if adoption.get('candidateDataSha256') != source['dataSha256'] or not adoption.get('reason'):
                raise ValueError('Qualified definition must pin exact values and explain adoption')
            if source['validation'].get('partialCompensationDefinition'):
                for field in ['boundedDisjointElevenRowSupplementApproved',
                              'prior449DataAndMetadataUnchanged', 'unknownBenefitsRemainUnknown']:
                    if adoption.get(field) is not True:
                        raise ValueError('Bounded supplement adoption declaration missing: ' + field)
                if source['rowCount'] != 11 or source['completeEmployeeSchedule'] is not False:
                    raise ValueError('Unexpected partial-supplement boundary')
            source['validation']['qualifiedDefinitionAdoption'] = copy.deepcopy(adoption)
            evidence['qualifiedDefinitionAdoption'] = copy.deepcopy(adoption)
        new_evidence = compressed(evidence)
        outputs[evidence_path] = new_evidence
        source['provenanceSha256'] = sha(new_evidence)
    outputs['sources.json'] = packed(manifest)
    summary = {
        'status': 'accepted-after-complete-independent-source-review',
        'noOutreach': True, 'approvedBy': '/root', 'sources': len(sources),
        'originals': original_count, 'rows': sum(s['rowCount'] for s in sources),
        'candidateManifestSha256': sha(candidate_manifest),
        'acceptanceDecisionSha256': sha(packed(decision)),
        'peerReceipts': list(receipt_pins.values()),
        'outputs': [{'path': str((COLLECTION / p).relative_to(ROOT)), 'sha256': sha(b)}
                    for p, b in outputs.items()]
    }
    return outputs, summary


def template(candidate_outputs):
    manifest = json.loads(candidate_outputs['sources.json'])
    reviews = []
    adoptions = []
    for source in manifest['sources']:
        reviews.append({
            'sourceId': source['id'], 'sourceSha256': source['sha256'],
            'candidateDataSha256': source['dataSha256'],
            'candidateProvenanceSha256': source['provenanceSha256'],
            'rowCount': source['rowCount'], 'reviewerAgent': None,
            'approved': False, 'completeIndependentLiteralFieldReview': False,
            'originalSourceAndPeriodConfirmed': False,
            'sourceControlResidualsAcceptedWithoutAdjustment': False,
            'receipt': {'path': None, 'sha256': None}
        })
        if source['validation'].get('partialCompensationDefinition') or any(
                'Pay is uniformly the literal Remuneration column' in n for n in source['notes']):
            adoption = {'sourceId': source['id'], 'candidateDataSha256': source['dataSha256'],
                        'approvedBy': None, 'approved': False, 'reason': None}
            if source['validation'].get('partialCompensationDefinition'):
                adoption.update({'boundedDisjointElevenRowSupplementApproved': False,
                                 'prior449DataAndMetadataUnchanged': False,
                                 'unknownBenefitsRemainUnknown': False})
            adoptions.append(adoption)
    return {'candidateManifestSha256': sha(candidate_outputs['sources.json']),
            'approvedBy': None, 'noOutreach': True,
            'cohortReviews': reviews, 'qualifiedDefinitionAdoptions': adoptions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', action='store_true', help='Write an unapproved review template only')
    args = parser.parse_args()
    from gap_municipal_emit import build
    outputs, _, _ = build()
    if args.template:
        target = AREA / 'acceptance-template.json'
        target.write_bytes(packed(template(outputs)))
        print(str(target.relative_to(ROOT)))
    else:
        if not ACCEPTANCE.is_file():
            raise SystemExit('No acceptance.json exists; candidates remain unverified.')
        _, summary = accepted_outputs(outputs, json.loads(ACCEPTANCE.read_bytes()))
        print(json.dumps({k: v for k, v in summary.items() if k != 'outputs'}, indent=2))


if __name__ == '__main__':
    main()
