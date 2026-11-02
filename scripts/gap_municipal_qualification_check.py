#!/usr/bin/env python3
"""Prove approval qualifications change metadata without changing literal salary evidence."""
import gzip
import hashlib
import json
from pathlib import Path
from gap_municipal_emit import AREA, ROOT, build, packed


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replay():
    before, _, _ = build(include_publication_qualifications=False)
    after, _, _ = build()
    archive = gzip.decompress((AREA / 'candidate-manifest-before-approval-qualifications.json.gzip').read_bytes())
    assert before['sources.json'] == archive
    first = json.loads(before['sources.json'])['sources']
    current = json.loads(after['sources.json'])['sources']
    assert len(first) == len(current) == 52
    rows = []
    for old, new in zip(first, current):
        assert old['id'] == new['id']
        assert before[old['file']] == after[new['file']]
        qualification = new['validation'].get('sourcePublicationQualification')
        old_meta = json.loads(json.dumps(old))
        new_meta = json.loads(json.dumps(new))
        old_evidence = json.loads(gzip.decompress(before[old['provenanceFile']]))
        new_evidence = json.loads(gzip.decompress(after[new['provenanceFile']]))
        if qualification:
            notes = qualification['publicNotes']
            assert [x for x in new_meta['notes'] if x not in notes] == old_meta['notes']
            assert [x for x in new_evidence['sourceDefinitions'] if x not in notes] == old_evidence['sourceDefinitions']
            assert new_evidence.pop('sourcePublicationQualification') == qualification
            assert new_meta['validation'].pop('sourcePublicationQualification') == qualification
            for key in ['notes', 'publicWarning', 'provenanceSha256']:
                old_meta.pop(key)
                new_meta.pop(key)
            old_evidence.pop('sourceDefinitions')
            new_evidence.pop('sourceDefinitions')
        assert old_meta == new_meta
        assert old_evidence == new_evidence
        rows.append({'sourceId': new['id'], 'sourceSha256': new['sha256'],
                     'rowCount': new['rowCount'], 'dataSha256': new['dataSha256'],
                     'priorProvenanceSha256': old['provenanceSha256'],
                     'qualifiedProvenanceSha256': new['provenanceSha256'],
                     'approvalQualificationAdded': bool(qualification),
                     'salaryDataAndLiteralEvidenceUnchanged': True})
    receipt_path = ROOT / 'research/salaries/gap-fill-2026-11-02/school_native/reviews/municipal-earliest-12-peer-source-review.json'
    receipt = json.loads(receipt_path.read_bytes())
    by_id = {s['id']: s for s in first}
    for pin in receipt['candidatePayloadPins']:
        assert pin['dataSha256'] == by_id[pin['sourceId']]['dataSha256']
        assert pin['provenanceSha256'] == by_id[pin['sourceId']]['provenanceSha256']
    health_path = ROOT / 'research/salaries/gap-fill-2026-11-02/health_employees/peer-municipal/peer-acceptance.json'
    health = json.loads(health_path.read_bytes())
    for pin in health['proofs']:
        assert sha((ROOT / pin['path']).read_bytes()) == pin['sha256']
    health_payload_path = health_path.parent / 'normalized-payload-verification.json'
    health_payload = json.loads(health_payload_path.read_bytes())
    assert health_payload['rowsVerified'] == 262 and not health_payload['errors']
    for pin in health_payload['sources']:
        assert pin['dataSha256'] == by_id[pin['sourceId']]['dataSha256']
        assert pin['provenanceSha256'] == by_id[pin['sourceId']]['provenanceSha256']
    assert {p['sourceId'] for p in receipt['candidatePayloadPins']} .isdisjoint(
        {p['sourceId'] for p in health_payload['sources']})
    assert len(receipt['candidatePayloadPins']) + len(health_payload['sources']) == 52
    return {'status': 'pass-metadata-only-source-approval-qualification-replay',
            'noOutreach': True, 'salaryDataChanged': False, 'salaryRows': 411,
            'candidateManifestBeforeSha256': sha(before['sources.json']),
            'candidateManifestAfterSha256': sha(after['sources.json']),
            'peerReviewedFirst22CohortsStillLiteralByteExact': True,
            'peerReceipt': {'path': str(receipt_path.relative_to(ROOT)), 'sha256': sha(receipt_path.read_bytes())},
            'peerReviewedRemaining30CohortsStillLiteralByteExact': True,
            'remainingPeerReceipt': {'path': str(health_path.relative_to(ROOT)), 'sha256': sha(health_path.read_bytes())},
            'rows': rows}


if __name__ == '__main__':
    record = replay()
    target = AREA / 'source-approval-qualification-replay.json'
    target.write_bytes(packed(record))
    print(json.dumps({k: v for k, v in record.items() if k != 'rows'}, indent=2))
