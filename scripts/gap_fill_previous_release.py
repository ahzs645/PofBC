#!/usr/bin/env python3
"""Verify PR37's frozen source evidence after an append-only salary expansion.

The historical release is never rewritten with later totals. Its one mutable
integration input, collections.json, is verified against an exact archived copy
and an explicit reviewed list of new collections. All other pins stay literal.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

from gap_fill_baseline import read, sha, snapshot, verify_preserved

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
OLD = ROOT / 'research/salaries/queue-completion-2026-11-01'


def verify_registry_extension(archived, active, additions):
    if not isinstance(additions, list) or any(type(s) is not str or not s for s in additions):
        raise ValueError('Explicit collection identifiers are required')
    if len(set(additions)) != len(additions) or set(additions) & set(archived['collections']):
        raise ValueError('New collections cannot duplicate historical collections')
    expected = {**archived, 'collections': archived['collections'] + additions}
    if active != expected:
        raise ValueError('Collection registry must preserve the exact historical prefix and fields')


def load_previous():
    spec = importlib.util.spec_from_file_location('gap_fill_pr37_review',
        ROOT / 'scripts/review-salary-queue-release-v2.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    previous = load_previous()
    acceptance = previous.current_parent_acceptance()
    assert acceptance['accepted'] is True and acceptance['noOutreach'] is True
    previous.pinned(OLD, 'baseline.json.gzip', acceptance['baselineFileSha256'])
    previous.pinned(OLD, 'baseline-row-fingerprints.json', acceptance['baselineRowFingerprintSha256'])
    checked = {}

    def pin(root, relative, expected):
        path = (root / relative).resolve()
        assert path.is_relative_to(ROOT.resolve()), relative
        key = str(path)
        if key in checked:
            assert checked[key] == expected, ('Contradictory historical fingerprint', relative)
            return
        assert sha(path.read_bytes()) == expected, ('Historical input changed', relative)
        checked[key] = expected

    for area, digest in acceptance['candidateFreezeSha256'].items():
        pin(OLD, area + '/candidate-freeze.json', digest)
        files = read(OLD / area / 'candidate-freeze.json')['files']
        assert len(files) == len({entry['path'] for entry in files})
        for entry in files:
            pin(ROOT, entry['path'], entry['sha256'])
    for relative, digest in acceptance['reviewReceiptSha256'].items():
        pin(OLD, relative, digest)
    pin(OLD, acceptance['rootReleaseFreezeFile'], acceptance['rootReleaseFreezeSha256'])
    inputs = read(OLD / acceptance['rootReleaseFreezeFile'])['files']
    assert len(inputs) == len({entry['path'] for entry in inputs})
    registry = 'research/salaries/collections.json'
    registry_entries = [entry for entry in inputs if entry['path'] == registry]
    assert len(registry_entries) == 1, 'The exact historical integration registry must be pinned'
    archived_path = AREA / 'baseline-collections.json'
    assert sha(archived_path.read_bytes()) == registry_entries[0]['sha256']
    selection_path = AREA / 'parent-acceptance.json'
    additions = []
    if selection_path.exists():
        selection = read(selection_path)
        assert selection['accepted'] is True and selection['noOutreach'] is True
        additions = selection['collections']
    verify_registry_extension(read(archived_path), read(ROOT / registry), additions)
    for entry in inputs:
        if entry['path'] != registry:
            pin(ROOT, entry['path'], entry['sha256'])
    for relative, digest in read(OLD / 'release.json')['manifestSha256'].items():
        pin(ROOT, relative, digest)

    # Independent source-review coverage and the explicit final nine PHSA
    # revisions remain exactly the accepted historical inputs.
    historical = read(OLD / 'release.json')
    previous.verify_peer_coverage(acceptance, [s['sourceId'] for s in historical['imports']])
    import finish_salary_queue_phsa_release as phsa
    expected_phsa = phsa.build()
    assert expected_phsa == read(ROOT / 'research/salaries/queue-completion-phsa/sources.json')

    outbox = OLD / 'acquisition/outbox/outbox.json'
    pin(OLD, str(outbox.relative_to(OLD)), acceptance['outboxSha256'])
    pin(OLD, 'original-queue-dispositions.json', acceptance['originalQueueDispositionsSha256'])
    done, external = previous.verify_original_dispositions(
        read(OLD / 'original-queue-dispositions.json'),
        read(ROOT / 'research/salaries/held-resolution-2026-11-01/work-queue.json'))
    wanted = {task['id'] for task in external}
    tasks = [task for task in read(OLD / 'acquisition/work-queue.json') if task['id'] in wanted]
    previous.verify_outbox(read(outbox), tasks)
    direction_path = OLD / 'acquisition/outbox/user-direction-2026-11-01.json'
    pin(OLD, str(direction_path.relative_to(OLD)), acceptance['outreachDirectionSha256'])
    direction = read(direction_path)
    assert direction['status'] == 'on-hold-by-user' and direction['doNotSend'] is True
    assert set(direction['outboxItemIds']) == {item['id'] for item in read(outbox)['items']}

    # Every earlier source's app metadata and payment row is preserved. Later
    # sources may extend totals, but cannot silently replace prior observations.
    baseline = read(AREA / 'baseline.json.gzip')
    index, groups = snapshot()
    preserved = verify_preserved(baseline, index, groups)
    assert baseline['overall']['records'] == historical['proposed']['records'] == 1125685
    assert historical['officialRowsAdded'] == 91934 and historical['compiledRowsReplaced'] == 3289
    return {'historicalRelease': OLD.name, 'frozenFilesVerified': len(checked),
            'historicalSources': len(historical['imports']), 'preservedRows': preserved,
            'newCollections': additions, 'requestSendingStatus': 'on-hold-by-user'}


if __name__ == '__main__':
    print(json.dumps(verify()))
