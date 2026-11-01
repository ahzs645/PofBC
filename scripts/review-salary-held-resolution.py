#!/usr/bin/env python3
"""Reconcile held-source resolutions and preserve every earlier salary observation."""
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'held-resolution-2026-11-01'
AREAS = ['education', 'schools', 'municipal', 'health']
FIELDS = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods',
          'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']
ACCEPTED = {'verified', 'accepted', 'imported'}


def read(path):
    return json.loads(path.read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    value = json.loads(gzip.decompress(raw))
    return value if isinstance(value, list) else value['rows']


def fingerprint(rows):
    keys = [json.dumps([r[0], r[1], int(Decimal(str(r[2])) * 100),
                       None if r[3] is None else int(Decimal(str(r[3])) * 100), r[4]],
                       ensure_ascii=False, separators=(',', ':')) for r in rows]
    return sha('\n'.join(sorted(keys, key=lambda x: x.encode())).encode())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def pinned(root, relative, expected):
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve()) and sha(path.read_bytes()) == expected, relative


def md(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def verify_baseline(before, groups):
    """No earlier official or compiled row may disappear, change, or multiply."""
    count = 0
    for old in before['groups']:
        key = (old['employerSlug'], old['year'], old['sourceId'])
        current = groups.get(key, [])
        assert len(current) == old['rows'] and fingerprint(current) == old['rowMultisetSha256'], ('Baseline observations changed', key)
        count += old['rows']
    assert count == before['rows']
    return count


def verify_review_coverage(acceptance, source_ids):
    """An empty acceptance ledger must never disable a required review gate."""
    assert set(acceptance['candidateFreezeSha256']) == set(AREAS), 'All four worker freezes are required'
    receipts = acceptance['reviewReceiptSha256']
    assert receipts, 'Pinned independent review receipts are required'
    coverage = acceptance['sourceReviewReceipts']
    assert set(coverage) == set(source_ids), 'Every new accepted source needs explicit peer coverage'
    for identifier, paths in coverage.items():
        assert isinstance(paths, list) and paths and len(paths) == len(set(paths)), identifier
        assert all(path in receipts and path.startswith('reviews/independent-') for path in paths), identifier


def main():
    baseline_raw = (OUT / 'baseline.json.gzip').read_bytes()
    baseline = json.loads(gzip.decompress(baseline_raw))
    before = read(OUT / 'baseline-row-fingerprints.json')
    assert before['baselineCommit'] == baseline['repositoryCommit']
    acceptance = read(OUT / 'parent-acceptance.json')
    assert acceptance['accepted'] is True and acceptance['noOutreach'] is True
    assert set(acceptance['candidateFreezeSha256']) == set(AREAS), 'All four worker freezes are required'
    assert acceptance['reviewReceiptSha256'], 'Pinned review receipts are required'
    assert sha((OUT / 'baseline-row-fingerprints.json').read_bytes()) == acceptance['baselineRowFingerprintSha256']
    for relative, expected in acceptance['reviewReceiptSha256'].items():
        pinned(OUT, relative, expected)
    frozen_paths = {}
    for area, expected in acceptance['candidateFreezeSha256'].items():
        freeze = OUT / area / 'candidate-freeze.json'
        assert sha(freeze.read_bytes()) == expected, area
        files = read(freeze)['files']
        frozen_paths[area] = {file['path'] for file in files}
        assert len(frozen_paths[area]) == len(files), area
        for file in files:
            pinned(ROOT, file['path'], file['sha256'])
    index = read(ROOT / 'public/salaries/employers/index.json')
    coverage = read(ROOT / 'public/salaries/coverage.json')
    for identifier, source in baseline['sources'].items():
        assert index['sources'][identifier] == source, ('Prior source metadata changed', identifier)
    groups = defaultdict(list)
    totals = Counter()
    for employer in index['employers']:
        rows = decode((ROOT / 'public/salaries/employers' / (employer['slug'] + '.json.gzip')).read_bytes())
        assert len(rows) == sum(employer['counts']), employer['slug']
        for row in rows:
            source = index['sources'][row[5]]
            groups[(employer['slug'], index['years'][row[4]], row[5])].append([row[0], row[1], row[2], row[3], row[6]])
            totals['compiled' if source.get('sourceKind') == 'compiled' else 'official'] += 1
    preserved = verify_baseline(before, groups)
    registered = read(RESEARCH / 'collections.json')['collections']
    imports = []
    manifests = {}
    for area in AREAS:
        collection = 'held-resolution-' + area
        folder = RESEARCH / collection
        manifest_path = folder / 'sources.json'
        if not manifest_path.exists():
            assert area == 'health', 'Missing collection: ' + collection
            continue
        manifests[str(manifest_path.relative_to(ROOT))] = sha(manifest_path.read_bytes())
        for source in read(manifest_path)['sources']:
            if source.get('status', 'verified') not in ACCEPTED:
                continue
            assert collection in registered and source['id'] not in baseline['sources'], source['id']
            assert source.get('sourceKind') == 'official' and isinstance(source['notes'], list), source['id']
            required_paths = [manifest_path, folder / source['file']]
            required_paths += [folder / source[key] for key in ['evidenceFile', 'provenanceFile'] if source.get(key)]
            assert all(str(path.relative_to(ROOT)) in frozen_paths[area] for path in required_paths), ('Unfrozen accepted source input', source['id'])
            raw = (folder / source['file']).read_bytes()
            assert sha(raw) == source['dataSha256'], source['id']
            rows = decode(raw)
            assert len(rows) == source['rowCount'], source['id']
            published = index['sources'][source['id']]
            for key in ['year', 'periodType', 'periodStart', 'periodEnd', 'notes', 'validation',
                        'publicWarning', 'sha256', 'dataSha256', 'completeEmployeeSchedule']:
                assert published.get(key) == source.get(key), (source['id'], key)
            assert published['scope'] == (source.get('category') or source['scope']), source['id']
            assert published['url'] == source['sourceUrl'], source['id']
            for key, hash_key in [('evidenceFile', 'evidenceSha256'), ('provenanceFile', 'provenanceSha256')]:
                if source.get(key):
                    pinned(folder, source[key], source[hash_key])
            for slug in {row[0] for row in rows}:
                expected = [[r[1], r[2], r[3], r[4], r[5]] for r in rows if r[0] == slug]
                actual = groups[(slug, source['year'], source['id'])]
                assert len(expected) == len(actual) and fingerprint(expected) == fingerprint(actual), source['id']
            imports.append({'collection': collection, 'sourceId': source['id'],
                            'employerSlug': source['employerSlug'], 'year': source['year'],
                            'scope': source.get('category') or source['scope'], 'rows': len(rows),
                            'sourceUrl': source['sourceUrl'], 'sourceSha256': source['sha256'],
                            'dataSha256': source['dataSha256'], 'publicWarning': source.get('publicWarning')})
    verify_review_coverage(acceptance, [source['sourceId'] for source in imports])
    added = sum(source['rows'] for source in imports)
    total = sum(totals.values())
    assert totals['official'] - baseline['overall']['officialRecords'] == added
    assert totals['compiled'] == baseline['overall']['compiledRecords']
    assert total == preserved + added and total - baseline['overall']['records'] == added
    assert index['recordCounts'] == dict(totals)
    assert coverage['officialRows'] == totals['official'] and coverage['legacyRowsRetained'] == totals['compiled']
    tasks, completed, task_hashes = [], [], {}
    completed_ids = set(acceptance['completedTaskIds'])
    seen = set()
    for area in AREAS:
        path = OUT / area / 'work-queue.json'
        raw = path.read_bytes()
        task_hashes[area] = sha(raw)
        entries = json.loads(raw)
        entries = entries if isinstance(entries, list) else entries['tasks']
        for task in entries:
            assert set(task) == set(FIELDS) and isinstance(task['reportingPeriods'], list), task.get('id')
            assert task['id'] not in seen, task['id']
            seen.add(task['id'])
            item = {**task, 'researchArea': area, 'requestStatus': 'not-sent'}
            (completed if task['id'] in completed_ids else tasks).append(item)
    assert completed_ids <= seen
    tasks.sort(key=lambda t: (t['sector'], t['employerName'], t['id']))
    requests = [t for t in tasks if t['route'] in {'ordinary-records-request', 'clarification-request', 'foi-fallback'}]
    report = {'version': 1, 'asOf': '2026-11-01', 'timezone': 'America/Vancouver',
              'baselineCommit': baseline['repositoryCommit'], 'baselineFileSha256': sha(baseline_raw),
              'baseline': baseline['overall'],
              'proposed': {'records': total, 'officialRecords': totals['official'],
                           'compiledRecords': totals['compiled'], 'employers': len(index['employers']),
                           'acceptedSourceFiles': len(coverage['imports'])},
              'officialRowsAdded': added, 'compiledRowsReplaced': 0, 'netRowsAdded': added,
              'baselineRowsPreservedExactly': preserved,
              'priorOfficialRowsPreservedExactly': baseline['overall']['officialRecords'],
              'originalReports': len({s['sourceSha256'] for s in imports}), 'acceptedCohorts': len(imports),
              'imports': imports, 'openTasks': len(tasks), 'completedTasks': len(completed),
              'unsentRequestCandidates': len(requests), 'taskInputSha256': task_hashes,
              'manifestSha256': manifests}
    save('release.json', report)
    save('work-queue.json', {'tasks': tasks})
    save('task-dispositions.json', {'completed': completed, 'open': tasks,
         'policy': 'Changed tasks in this bounded follow-up only; earlier frozen queues overlap and are not additive missing-record counts.'})
    save('acquisition-list.json', {'requestStatus': 'not-sent', 'candidates': requests})
    lines = ['# Held-source resolution: release reconciliation', '',
             f'As of 1 November 2026, **{added:,} newly accepted official observations** increase the app to **{total:,} records** across **{len(index["employers"])} employers**. All **{preserved:,} earlier observations**, including **{baseline["overall"]["officialRecords"]:,} official observations**, are preserved exactly. No compiled rows are removed.', '',
             '| Measure | Before | After |', '| --- | ---: | ---: |',
             f'| All disclosed payment records | {baseline["overall"]["records"]:,} | {total:,} |',
             f'| Accepted official observations | {baseline["overall"]["officialRecords"]:,} | {totals["official"]:,} |',
             f'| Retained compiled observations | {baseline["overall"]["compiledRecords"]:,} | {totals["compiled"]:,} |', '',
             '| Source / period | Scope | Accepted observations | Qualification |',
             '| --- | --- | ---: | --- |']
    for source in imports:
        lines.append(f'| [{md(source["employerSlug"])} — {md(source["year"])}]({source["sourceUrl"]}) | {md(source["scope"])} | {source["rows"]:,} | {md(source["publicWarning"] or "No additional source warning")} |')
    lines += ['', f'**{len(tasks)} changed tasks remain open**; **{len(completed)} are resolved** in the [disposition ledger](task-dispositions.json). **{len(requests)} unsent source-copy or clarification candidates** appear in the [acquisition list](acquisition-list.md). Earlier frozen queues overlap and must not be added as unique missing-report counts.', '',
              'The baseline gate compares literal names, positions, cents, null expenses, physical page and row multiplicity for every employer/year/source group. Each new published group must equal its normalized source payload. Exact source qualifications, original/data/evidence hashes and independent review receipts are checked. Source-control differences are not balanced away.', '',
              '[Full machine reconciliation](release.json) · [Assumptions and held cases](README.md) · [Current catalog comparison](../sunshine-lists/comparison.md)', '']
    (OUT / 'release.md').write_text('\n'.join(lines))
    for filename, entries in [('work-queue.csv', tasks), ('acquisition-list.csv', requests)]:
        with (OUT / filename).open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS + ['researchArea', 'requestStatus'], lineterminator='\n')
            writer.writeheader()
            for task in entries:
                writer.writerow({key: '; '.join(task[key]) if key == 'reportingPeriods' else task[key] for key in writer.fieldnames})
    lines = ['# Unsent source-copy and clarification candidates', '',
             'These are changed tasks in the held-source follow-up. No request, FOI, contact or fee has been made.', '',
             '| Employer / period | Route | Source issue | Next action |', '| --- | --- | --- | --- |']
    for task in requests:
        lines.append(f'| [{md(task["employerName"])} — {md(", ".join(task["reportingPeriods"]))}]({task["sourceUrl"] or task["sourceIndexUrl"]}) | {md(task["route"])} | {md(task["reason"])} | {md(task["nextAction"])} |')
    lines += ['', '[CSV](acquisition-list.csv) · [JSON](acquisition-list.json) · [All changed tasks](work-queue.csv)', '']
    (OUT / 'acquisition-list.md').write_text('\n'.join(lines))
    print(json.dumps({key: report[key] for key in ['officialRowsAdded', 'netRowsAdded', 'acceptedCohorts', 'openTasks', 'unsentRequestCandidates']}))


if __name__ == '__main__':
    main()
