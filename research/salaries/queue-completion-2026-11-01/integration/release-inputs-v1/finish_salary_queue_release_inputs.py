#!/usr/bin/env python3
"""Publish reviewed replacement metadata while preserving the frozen worker handoff."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
AREA = RESEARCH / 'queue-completion-2026-11-01/integration'


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def release_manifest(original):
    """Only rebase unchanged data paths and correct the two retention descriptions."""
    result = copy.deepcopy(original)
    amendments = []
    for source in result['sources']:
        source['file'] = '../queue-completion-acquisition/' + source['file']
        if source['employerSlug'] != 'providence-health-care':
            continue
        before = source['publicWarning']
        old_tail = 'This official fiscal-year scope coexists with retained compiled observations; equivalent periods or matching identities are not assumed.'
        assert before.endswith(old_tail), source['id']
        source['publicWarning'] = before[:-len(old_tail)] + (
            'A complete comparison replaced the 3,289-row compiled employee copy with the official employee schedule. '
            'This does not establish identities across different periods or turn unknown source expenses into zero.')
        amendments.append({'sourceId': source['id'], 'field': 'publicWarning',
                           'before': before, 'after': source['publicWarning']})
        before = source['validation']['compiledPartitionRetentionReason']
        source['validation']['compiledPartitionRetentionReason'] = (
            'Retain any compiled observations outside an exact separately reviewed replacement. '
            'The complete 3,289-row employee copy is selected only by the separately source- and data-hash-pinned root comparison.'
            + (' This Board scope removes no additional observations.' if source['category'] == 'board-remuneration' else ''))
        amendments.append({'sourceId': source['id'], 'field': 'validation.compiledPartitionRetentionReason',
                           'before': before, 'after': source['validation']['compiledPartitionRetentionReason']})
    assert len(amendments) == 4
    return result, amendments


def write(path, raw, check):
    if check:
        assert path.read_bytes() == raw, ('Released metadata does not replay', path)
    else:
        assert not path.exists(), ('Never overwrite frozen metadata', path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    original_path = RESEARCH / 'queue-completion-acquisition/sources.json'
    original_raw = original_path.read_bytes()
    assert sha(original_raw) == '4b06e21e635220ab88ae0346ced441f515be3c4a8635c8d0651ce2874b25b570'
    original = json.loads(original_raw)
    result, amendments = release_manifest(original)
    comparison_path = AREA / 'compiled-comparison.json'
    comparison_raw = comparison_path.read_bytes()
    comparison = json.loads(comparison_raw)
    peer_path = RESEARCH / 'queue-completion-2026-11-01/reviews/independent-queue-compiled-replacement-review.json'
    peer_raw = peer_path.read_bytes()
    peer = json.loads(peer_raw)
    assert peer['verdict'] == 'PASS-complete-Providence-employee-copy-replacement-only; retain-all-VCH-partial-overlap'
    assert peer['authorComparison']['sha256'] == sha(comparison_raw)
    assert len(comparison['compiledReplacements']) == 1
    data_pins = {}
    for source in original['sources']:
        path = original_path.parent / source['file']
        assert sha(path.read_bytes()) == source['dataSha256']
        data_pins[str(path.relative_to(ROOT))] = source['dataSha256']
    release_path = RESEARCH / 'queue-completion-acquisition-release/sources.json'
    released_raw = encode(result)
    write(release_path, released_raw, args.check)
    replacement_path = RESEARCH / 'queue-completion-replacements/sources.json'
    replacements_raw = encode({'version': 1, 'sources': [],
        'compiledReplacements': comparison['compiledReplacements']})
    write(replacement_path, replacements_raw, args.check)
    adoption = {'frozen': True, 'reviewedOn': '2026-11-01', 'reviewer': '/root',
        'originalFrozenManifest': {'path': str(original_path.relative_to(ROOT)), 'sha256': sha(original_raw)},
        'releasedManifest': {'path': str(release_path.relative_to(ROOT)), 'sha256': sha(released_raw)},
        'replacementManifest': {'path': str(replacement_path.relative_to(ROOT)), 'sha256': sha(replacements_raw)},
        'compiledComparison': {'path': str(comparison_path.relative_to(ROOT)), 'sha256': sha(comparison_raw)},
        'independentReplacementPeer': {'path': str(peer_path.relative_to(ROOT)), 'sha256': sha(peer_raw)},
        'unchangedData': data_pins, 'sourceMetadataChanges': amendments,
        'pathRebasing': 'All four data paths resolve to the exact unchanged files in the frozen worker collection. Only the released collection is registered; source IDs and observations are not duplicated.',
        'decision': 'Adopt the complete independently proved Providence employee-copy replacement. Correct the two public retention descriptions and their default-retention explanations so they do not falsely claim the removed employee copy still coexists. Preserve every original worker handoff byte, all source/data hashes, payment amounts, names, scope, periods, definitions, evidence, and all VCH partial-overlap qualifications.',
        'requiresWholeFrozenWorkerAndSeparateRootReleaseFreeze': True}
    write(AREA / 'acquisition-metadata-adoption.json', encode(adoption), args.check)
    print(json.dumps({'releasedSources': len(result['sources']), 'metadataFieldChanges': len(amendments),
                      'unchangedDataFiles': len(data_pins), 'compiledRowsReplaced': 3289}))


if __name__ == '__main__':
    main()
