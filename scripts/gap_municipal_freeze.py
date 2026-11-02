#!/usr/bin/env python3
"""Freeze municipal producer inputs only after explicit root source acceptance.

Independent reviews written by this worker under municipal/reviews are excluded:
those are separate peer assignments and can still receive additive receipts.
This command never creates or supplies a source-acceptance decision.
"""
import argparse
import hashlib
import json
from pathlib import Path
from gap_municipal_emit import AREA, COL, ROOT, build, packed
from gap_municipal_finalize import ACCEPTANCE, accepted_outputs
from gap_municipal_qualification_check import replay

FREEZE = AREA / 'producer-freeze.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_accepted():
    if not ACCEPTANCE.is_file():
        raise ValueError('Root acceptance.json is required; no automatic source adoption')
    outputs, _, _ = build()
    accepted, summary = accepted_outputs(outputs, json.loads(ACCEPTANCE.read_bytes()))
    for path, raw in accepted.items():
        assert (COL / path).read_bytes() == raw, path
    assert (AREA / 'accepted-summary.json').read_bytes() == packed(summary)
    assert summary['sources'] == 52 and summary['rows'] == 411
    replay()
    proof = json.loads((AREA / 'abbotsford-known-column-supplement.json').read_bytes())
    for field in ['priorManifest', 'priorData']:
        pin = proof[field]
        assert sha((ROOT / pin['path']).read_bytes()) == pin['sha256'], field
    return summary


def input_paths():
    files = [p for p in AREA.rglob('*') if p.is_file()
             and 'reviews' not in p.relative_to(AREA).parts
             and p.name not in ['producer-freeze.json', 'handoff-final.json']]
    files += [p for p in COL.rglob('*') if p.is_file()]
    files += list((ROOT / 'scripts').glob('gap_municipal*.py'))
    files.append(ROOT / 'scripts/test_gap_municipal.py')
    return sorted(set(files))


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    summary = verify_accepted()
    if args.write:
        pins = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p.read_bytes())}
                for p in input_paths()]
        FREEZE.write_bytes(packed({'status': 'accepted-producer-inputs-frozen',
                                  'noOutreach': True, 'sources': 52, 'rows': 411,
                                  'acceptedManifestSha256': sha((COL / 'sources.json').read_bytes()),
                                  'acceptanceDecisionSha256': summary['acceptanceDecisionSha256'],
                                  'peerWorkReviewsExcluded': True, 'files': pins}))
    else:
        frozen = json.loads(FREEZE.read_bytes())
        expected = {str(p.relative_to(ROOT)) for p in input_paths()}
        assert expected == {p['path'] for p in frozen['files']}, 'Producer input set changed'
        for pin in frozen['files']:
            assert sha((ROOT / pin['path']).read_bytes()) == pin['sha256'], pin['path']
    print(json.dumps({'status': 'pass', 'sources': 52, 'rows': 411,
                      'frozenFiles': len(json.loads(FREEZE.read_bytes())['files']),
                      'noOutreach': True}, indent=2))


if __name__ == '__main__':
    run()
