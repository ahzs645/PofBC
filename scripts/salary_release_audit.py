"""Verify immutable release inputs, with explicit archived text-only amendments."""
import gzip
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def rows(raw):
    payload = json.loads(gzip.decompress(raw))
    return payload if isinstance(payload, list) else payload['rows']


def metadata_sha(source):
    return hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve()), relative
    return path


def verify_frozen_release(folder, research):
    release = read(folder / 'release.json')
    baseline = read(folder / 'baseline.json')
    assert release['baseline'] == baseline['overall']
    ledger_path = research / 'release-amendments.json'
    ledger = read(ledger_path) if ledger_path.exists() else {}
    amendments = ledger.get('amendments', [])
    manifests = {}
    checked = 0
    applied = []
    for expected in release['imports']:
        collection = expected['collection']
        if collection not in manifests:
            manifests[collection] = read(inside(research, collection + '/sources.json'))
        source = next(s for s in manifests[collection]['sources'] if s['id'] == expected['sourceId'])
        assert source.get('status', 'verified') in {'verified', 'accepted', 'imported'}, source['id']
        raw = inside(research / collection, source['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source['dataSha256'], source['id']
        current_rows = rows(raw)
        assert len(current_rows) == source['rowCount'] == expected['rows'], source['id']
        assert source['sha256'] == expected['sourceSha256'], source['id']
        assert source['employerSlug'] == expected['employerSlug'] and source['year'] == expected['year'], source['id']
        assert (source.get('category') or source.get('scope')) == (expected.get('category') or expected.get('scope')), source['id']
        assert source['sourceUrl'] == expected['sourceUrl'], source['id']
        if source.get('publicWarning') != expected.get('publicWarning'):
            matches = [a for a in ledger.get('metadataAmendments', []) if a['collection'] == collection and a['sourceId'] == source['id'] and a['oldPublicWarning'] == expected.get('publicWarning') and a['newPublicWarning'] == source.get('publicWarning')]
            assert len(matches) == 1, f"{source['id']}: changed source qualification has no exact reviewed metadata amendment"
            amendment = matches[0]
            assert amendment['kind'] == 'clarify-control-scope' and amendment['reason']
            archived_path = inside(research, amendment['archivedSourceManifest'])
            assert hashlib.sha256(archived_path.read_bytes()).hexdigest() == amendment['archivedSourceManifestSha256']
            old_source = next(s for s in read(archived_path)['sources'] if s['id'] == source['id'])
            assert metadata_sha(old_source) == amendment['oldMetadataSha256']
            assert metadata_sha(source) == amendment['newMetadataSha256']
            assert old_source['dataSha256'] == source['dataSha256'] == expected['dataSha256']
            assert old_source.get('publicWarning') == expected.get('publicWarning')
            changed = sorted(k for k in set(old_source) | set(source) if old_source.get(k) != source.get(k))
            assert changed == amendment['changedFields'] and set(changed) <= {'notes', 'validation', 'publicWarning'}
            assert inside(research, amendment['reviewFile']).is_file()
            applied.append(source['id'] + ':metadata')
        if source['dataSha256'] != expected['dataSha256']:
            matches = [a for a in amendments if a['collection'] == collection and a['sourceId'] == source['id'] and a['oldDataSha256'] == expected['dataSha256'] and a['newDataSha256'] == source['dataSha256']]
            assert len(matches) == 1, f"{source['id']}: changed release input has no exact reviewed amendment"
            amendment = matches[0]
            assert amendment['kind'] == 'restore-published-text' and amendment['reason'] and amendment['reviewFile']
            assert inside(research, amendment['reviewFile']).is_file()
            archived = inside(research, amendment['archivedDataFile']).read_bytes()
            assert hashlib.sha256(archived).hexdigest() == expected['dataSha256'], source['id']
            old_rows = rows(archived)
            assert len(old_rows) == len(current_rows)
            changes = []
            for index, (before, after) in enumerate(zip(old_rows, current_rows)):
                # This amendment route permits only reviewed name/title repairs.
                # Money, employer, physical page and row multiplicity stay fixed.
                assert len(before) == len(after) == 6
                assert [before[i] for i in [0, 3, 4, 5]] == [after[i] for i in [0, 3, 4, 5]], (source['id'], index)
                if before != after:
                    changes.append({'rowIndex': index, 'before': before, 'after': after})
            assert changes and changes == amendment['rowChanges'], source['id']
            applied.append(source['id'])
        checked += 1
    for collection, manifest in manifests.items():
        expected_ids = {s['sourceId'] for s in release['imports'] if s['collection'] == collection}
        actual_ids = {s['id'] for s in manifest['sources'] if s.get('file') and s.get('status', 'verified') in {'verified', 'accepted', 'imported'}}
        assert expected_ids == actual_ids, f'{collection}: historical cohort set changed'
    added = sum(source['rows'] for source in release['imports'])
    assert added == release['officialRowsAdded']
    assert release['proposed']['officialRecords'] - release['baseline']['officialRecords'] == added
    assert release['baseline']['compiledRecords'] - release['proposed']['compiledRecords'] == release['compiledRowsReplaced']
    assert release['proposed']['records'] - release['baseline']['records'] == added - release['compiledRowsReplaced'] == release['netRowsAdded']
    for area, expected_hash in release.get('taskInputSha256', {}).items():
        assert hashlib.sha256((folder / area / 'work-queue.json').read_bytes()).hexdigest() == expected_hash, area
    if not release.get('taskInputSha256'):
        tasks = read(folder / 'work-queue.json')['tasks']
        fields = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods', 'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']
        actual = []
        for area in sorted({t['area'] for t in tasks}):
            actual.extend({**{key: task[key] for key in fields}, 'area': area, 'requestStatus': 'not-sent'} for task in read(folder / area / 'work-queue.json'))
        actual.sort(key=lambda task: (task['employerName'], task['route'], task['id']))
        assert actual == tasks, 'Historical task inputs changed'
    return {'historicalRelease': folder.name, 'records': release['proposed']['records'], 'sourceInputsVerified': checked, 'reviewedAmendments': applied}
