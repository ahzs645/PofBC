#!/usr/bin/env python3
"""Reconcile the explicit second root release and its narrow PHSA metadata amendment."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from finish_salary_queue_release_inputs import release_manifest

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'queue-completion-2026-11-01'
AREAS = ['acquisition', 'schools', 'municipal', 'phsa']
COLLECTIONS = {area: 'queue-completion-' + area for area in AREAS}
COLLECTIONS['acquisition'] = 'queue-completion-acquisition-release'
FIELDS = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods',
          'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']


def read(path):
    return json.loads(path.read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    value = json.loads(gzip.decompress(raw))
    return value if isinstance(value, list) else value['rows']


def fingerprint(rows):
    values = [json.dumps([r[0], r[1], exact_cents(r[2]),
              None if r[3] is None else exact_cents(r[3]), r[4]],
              ensure_ascii=False, separators=(',', ':')) for r in rows]
    return sha('\n'.join(sorted(values, key=lambda x: x.encode())).encode())


def exact_cents(value):
    assert type(value) in (int, float), 'Money must be a JSON number, not a boolean or string'
    amount = Decimal(str(value))
    assert amount.is_finite(), 'Nonfinite money is not a published amount'
    cents = amount * 100
    assert cents == cents.to_integral_value(), 'Subcent changes cannot be truncated in a fingerprint'
    return int(cents)


def pinned(root, relative, expected):
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve()), relative
    assert sha(path.read_bytes()) == expected, ('Frozen input changed', relative)


def current_parent_acceptance():
    selection = read(OUT / 'parent-acceptance-selection.json')
    assert selection['schema'] == 'salary-queue-parent-selection-v1'
    assert type(selection['selectedVersion']) is int and selection['selectedVersion'] == 2
    expected_path = str((OUT / 'parent-acceptance-v2.json').relative_to(ROOT))
    reference = selection['effectiveParentAcceptance']
    assert reference['path'] == expected_path, 'An explicit reviewed parent revision is required'
    pinned(ROOT, reference['path'], reference['sha256'])
    previous = selection['supersededPrepublicationParentAcceptance']
    assert previous['path'] == str((OUT / 'parent-acceptance.json').relative_to(ROOT))
    pinned(ROOT, previous['path'], previous['sha256'])
    acceptance = read(ROOT / reference['path'])
    assert acceptance['supersededPrepublicationParentAcceptance'] == previous
    assert acceptance['rootReleaseFreezeFile'] == 'integration/candidate-freeze-v2.json'
    return acceptance


def verify_baseline(before, groups, replacements):
    """Only explicitly reviewed whole compiled copies can disappear."""
    changes = {(entry['employerSlug'], entry['compiledYear'], 'pssdb-2026-10-22'): entry
               for entry in replacements}
    assert len(changes) == len(replacements), 'Duplicate compiled replacement scope'
    preserved, removed, found = 0, 0, set()
    for old in before['groups']:
        key = (old['employerSlug'], old['year'], old['sourceId'])
        actual = groups.get(key, [])
        if key in changes:
            decision = changes[key]
            assert old['sourceKind'] == 'compiled', 'Earlier official rows cannot be replaced'
            assert decision['expectedRetainedRows'] == 0 and old['rows'] == decision['expectedRows']
            assert not actual, ('A reviewed whole compiled copy was only partly removed', key)
            removed += old['rows']
            found.add(key)
        else:
            assert len(actual) == old['rows'] and fingerprint(actual) == old['rowMultisetSha256'], ('Earlier observations changed', key)
            preserved += old['rows']
    assert found == set(changes), 'Replacement is not an existing baseline group'
    assert preserved + removed == before['rows']
    return preserved, removed


def verify_peer_coverage(acceptance, source_ids):
    assert set(acceptance['candidateFreezeSha256']) == set(AREAS), 'All four final worker freezes are required'
    receipts = acceptance['reviewReceiptSha256']
    coverage = acceptance['sourceReviewReceipts']
    assert receipts and set(coverage) == set(source_ids), 'Every new source requires explicit pinned peer coverage'
    for identifier, paths in coverage.items():
        assert isinstance(paths, list) and paths and len(paths) == len(set(paths)), identifier
        assert all(path in receipts and path.startswith(('reviews/independent-', 'reviews/root-')) for path in paths), identifier


def verify_original_dispositions(dispositions, original):
    expected = {task['id'] for task in original['tasks']}
    entries = dispositions['originalQueueEntries']
    assert len(entries) == len(expected) and {task['id'] for task in entries} == expected
    done, external = [], []
    for item in entries:
        assert item['disposition'] in {'completed', 'issuer-dependent'}, item['id']
        assert item['evidence'] and item['reason'], item['id']
        (done if item['disposition'] == 'completed' else external).append(item)
    assert len(done) == 5 and len(external) == 4
    assert not dispositions['remainingPublicProcessingTasks'], 'Original public processing queue is unfinished'
    return done, external


def verify_outbox(outbox, tasks):
    assert outbox['requestCount'] == len(outbox['items']) == len(tasks) == 4
    for key in ['contactsSent', 'formsSubmitted', 'formalFoiApplicationsSubmitted', 'feesAuthorizedOrPaid']:
        assert type(outbox[key]) is int and outbox[key] == 0, ('Outreach status changed', key)
    matched = set()
    for request in outbox['items']:
        assert request['sent'] is False and request['submitted'] is False
        assert request['noFeeRoute']['feesAuthorized'] is False
        assert request['noFeeRoute']['formalFoiApplicationAuthorized'] is False
        found = [task for task in tasks if task['id'] in request['linkedTaskIds']]
        assert len(found) == 1, 'Each request must link one exact remaining original issue'
        task = found[0]
        assert request['employerSlug'] == task['employerSlug']
        assert request['reportingPeriods'] == task['reportingPeriods']
        assert task['id'] not in matched, 'Duplicate request for the same original issue'
        matched.add(task['id'])
    assert matched == {task['id'] for task in tasks}


def verify_historical_phsa(sources):
    assert len(sources) == 9 and {s['year'] for s in sources} == {f'{year}/{str(year + 1)[-2:]}' for year in range(2015, 2024)}, 'All nine historical PHSA cohorts are required'
    for source in sources:
        assert source['employerSlug'] == 'provincial-health-services-authority'
        assert (source.get('category') or source['scope']) == 'employee-remuneration'
        assert source['completeEmployeeSchedule'] is True
        assert source['validation']['completeEmployeeSchedule'] is True


def verify_phsa_provenance(source, rows, provenance):
    """A complete source needs closed field evidence, beyond metadata claims."""
    assert provenance['sourceId'] == source['id'].removeprefix('queue-completion-').removesuffix('-employees')
    assert provenance['sourceSha256'] == source['sha256']
    assert provenance['dataSha256'] == source['dataSha256']
    assert provenance['allNineSourceHoldoutsPassed'] is True
    holdouts = provenance['rootHoldoutComparisons']
    assert len(holdouts) == 1, 'Each historical layout requires its own passed holdout'
    detail = provenance['originalRowsAndPerFieldResolution']
    assert detail['sourceId'] == provenance['sourceId'] and detail['sourceSha256'] == source['sha256']
    assert detail['completePhysicalSource'] is True and not detail['pendingFields']
    assert len(rows) == detail['rowCount'] == len(detail['rows']) == source['rowCount']
    pages = detail['physicalPages']
    assert [p['physicalPage'] for p in pages] == list(range(1, source['validation']['physicalPdfPages'] + 1))
    expected_keys = [(p['physicalPage'], n) for p in pages for n in range(1, p['rows'] + 1)]
    assert [(r['row'][5], r['sourceRowOnPage']) for r in detail['rows']] == expected_keys
    closed = {'manual-original-image', 'manual-qualified-source-typography',
              'manual-blind-source-holdout', 'calibrated-paired-reader-confidence-corroboration',
              'original-source-explicit-dash-geometry', 'baseline-independent-reader-agreement'}
    counts = {field: Counter() for field in ['name', 'remuneration', 'expenses']}
    for row, entry in zip(rows, detail['rows']):
        assert row == entry['row'] and len(row) == 6
        assert row[0] == source['employerSlug'] and row[2] is None
        assert isinstance(row[1], str) and row[1].strip()
        assert type(row[3]) is int and (row[4] is None or type(row[4]) is int)
        raw = entry['rawCandidateRow']
        assert [row[i] for i in [0, 2, 5]] == [raw[i] for i in [0, 2, 5]]
        for field, index in [('name', 1), ('remuneration', 3), ('expenses', 4)]:
            route = entry['fields'][field]['status']
            assert route in closed, 'A pending or unknown field route cannot be published'
            assert field == 'name' or route != 'manual-qualified-source-typography'
            assert row[index] == raw[index] or route.startswith('manual-'), 'Automatic corroboration cannot change a cell'
            if field != 'name':
                assert row[index] is None or row[index] > 0 or route.startswith('manual-')
            if field == 'expenses' and row[index] is None:
                assert route in {'manual-original-image', 'manual-blind-source-holdout',
                                 'original-source-explicit-dash-geometry'}
            counts[field][route] += 1
    assert {field: dict(value) for field, value in counts.items()} == detail['fieldResolutionCounts']
    assert detail['fieldResolutionCounts'] == source['validation']['fieldResolutionCounts']
    pay = sum(row[3] for row in rows)
    expense = sum(row[4] for row in rows if row[4] is not None)
    assert [pay, expense] == [detail['diagnosticRemunerationSum'], detail['diagnosticKnownExpenseSum']]
    controls = detail['sourcePrintedControls']
    residuals = [pay - controls['remuneration'], expense - controls['expenses']]
    assert residuals == detail['diagnosticControlResiduals'] == source['validation']['sourceControlResiduals']
    assert detail['rootAdoptedQualifiedNameCases'] == source['validation']['rootAdoptedQualifiedNameCases']


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def md(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def build_report():
    baseline_raw = (OUT / 'baseline.json.gzip').read_bytes()
    baseline = json.loads(gzip.decompress(baseline_raw))
    before = read(OUT / 'baseline-row-fingerprints.json')
    acceptance = current_parent_acceptance()
    assert acceptance['accepted'] is True and acceptance['noOutreach'] is True
    pinned(OUT, 'baseline.json.gzip', acceptance['baselineFileSha256'])
    assert baseline['repositoryCommit'] == before['baselineCommit']
    pinned(OUT, 'baseline-row-fingerprints.json', acceptance['baselineRowFingerprintSha256'])
    frozen_paths = {}
    for area, expected in acceptance['candidateFreezeSha256'].items():
        pinned(OUT, area + '/candidate-freeze.json', expected)
        files = read(OUT / area / 'candidate-freeze.json')['files']
        frozen_paths[area] = {entry['path'] for entry in files}
        assert len(files) == len(frozen_paths[area]), area
        for entry in files:
            pinned(ROOT, entry['path'], entry['sha256'])
    for relative, expected in acceptance['reviewReceiptSha256'].items():
        pinned(OUT, relative, expected)
    pinned(OUT, acceptance['rootReleaseFreezeFile'], acceptance['rootReleaseFreezeSha256'])
    root_inputs = read(OUT / acceptance['rootReleaseFreezeFile'])['files']
    root_paths = {entry['path'] for entry in root_inputs}
    assert len(root_paths) == len(root_inputs)
    for entry in root_inputs:
        pinned(ROOT, entry['path'], entry['sha256'])
    original_acquisition = read(RESEARCH / 'queue-completion-acquisition/sources.json')
    expected_acquisition, _ = release_manifest(original_acquisition)
    assert read(RESEARCH / COLLECTIONS['acquisition'] / 'sources.json') == expected_acquisition
    pinned(OUT, 'integration/compiled-comparison.json', acceptance['compiledComparisonSha256'])
    comparison = read(OUT / 'integration/compiled-comparison.json')
    replacements = comparison['compiledReplacements']
    replacement_manifest = read(RESEARCH / 'queue-completion-replacements/sources.json')
    assert replacement_manifest['compiledReplacements'] == replacements
    assert replacement_manifest['sources'] == []
    pinned(ROOT, 'research/salaries/queue-completion-replacements/sources.json', acceptance['compiledReplacementManifestSha256'])
    for entry in comparison['comparisons']:
        if entry.get('pairedEvidenceFile'):
            pinned(ROOT, entry['pairedEvidenceFile'], entry['pairedEvidenceSha256'])
    index = read(ROOT / 'public/salaries/employers/index.json')
    coverage = read(ROOT / 'public/salaries/coverage.json')
    for identifier, source in baseline['sources'].items():
        assert index['sources'][identifier] == source, ('Earlier source metadata changed', identifier)
    groups, totals = defaultdict(list), Counter()
    for employer in index['employers']:
        rows = decode((ROOT / 'public/salaries/employers' / (employer['slug'] + '.json.gzip')).read_bytes())
        assert len(rows) == sum(employer['counts']), employer['slug']
        for row in rows:
            groups[(employer['slug'], index['years'][row[4]], row[5])].append([row[0], row[1], row[2], row[3], row[6]])
            totals['compiled' if index['sources'][row[5]].get('sourceKind') == 'compiled' else 'official'] += 1
    preserved, removed = verify_baseline(before, groups, replacements)
    registered = read(RESEARCH / 'collections.json')['collections']
    imports, manifests, phsa_sources = [], {}, []
    for area in AREAS:
        collection = COLLECTIONS[area]
        folder = RESEARCH / collection
        path = folder / 'sources.json'
        assert collection in registered, collection
        manifests[str(path.relative_to(ROOT))] = sha(path.read_bytes())
        sources = read(path)['sources']
        if area == 'phsa':
            phsa_sources = sources
        for source in sources:
            assert source['status'] == 'verified' and source['sourceKind'] == 'official'
            assert source['id'] not in baseline['sources'], source['id']
            required = [path, folder / source['file']]
            required.extend(folder / source[key] for key in ['evidenceFile', 'provenanceFile'] if source.get(key))
            assert all(str(p.resolve().relative_to(ROOT)) in frozen_paths[area] | root_paths for p in required), ('Unfrozen accepted source', source['id'])
            raw = (folder / source['file']).read_bytes()
            assert sha(raw) == source['dataSha256'], source['id']
            rows = decode(raw)
            assert len(rows) == source['rowCount']
            published = index['sources'][source['id']]
            for key in ['year', 'periodType', 'periodStart', 'periodEnd', 'notes', 'validation', 'publicWarning',
                        'sha256', 'dataSha256', 'completeEmployeeSchedule', 'retainCompiledPartition']:
                assert published.get(key) == source.get(key), (source['id'], key)
            assert published['url'] == source['sourceUrl']
            assert published['scope'] == (source.get('category') or source['scope'])
            assert source['publicWarning'].strip(), 'Visible scope/source qualification is mandatory'
            for key, hash_key in [('evidenceFile', 'evidenceSha256'), ('provenanceFile', 'provenanceSha256')]:
                if source.get(key):
                    pinned(folder, source[key], source[hash_key])
            if area == 'phsa':
                provenance = json.loads(gzip.decompress((folder / source['provenanceFile']).read_bytes()))
                verify_phsa_provenance(source, rows, provenance)
            for slug in {r[0] for r in rows}:
                expected = [[r[1], r[2], r[3], r[4], r[5]] for r in rows if r[0] == slug]
                actual = groups[(slug, source['year'], source['id'])]
                assert len(expected) == len(actual) and fingerprint(expected) == fingerprint(actual), source['id']
            imports.append({'collection': collection, 'sourceId': source['id'],
                            'employerSlug': source['employerSlug'], 'year': source['year'],
                            'scope': source.get('category') or source['scope'], 'rows': len(rows),
                            'sourceUrl': source['sourceUrl'], 'sourceSha256': source['sha256'],
                            'dataSha256': source['dataSha256'], 'publicWarning': source['publicWarning']})
    verify_peer_coverage(acceptance, [s['sourceId'] for s in imports])
    verify_historical_phsa(phsa_sources)
    import finish_salary_queue_phsa_release as phsa_release
    amendment = acceptance['phsaReleaseMetadataAdoption']
    assert amendment['path'] == str((OUT / 'integration/phsa-release-metadata-adoption.json').relative_to(ROOT))
    pinned(ROOT, amendment['path'], amendment['sha256'])
    root_references = {json.dumps(s['validation']['rootAcceptanceReceipt'], sort_keys=True)
                       for s in phsa_sources}
    assert len(root_references) == 1, 'All nine sources require the same complete root adoption'
    replayed_phsa = phsa_release.build(json.loads(next(iter(root_references))))
    assert replayed_phsa == read(RESEARCH / COLLECTIONS['phsa'] / 'sources.json'), (
        'Active PHSA source revisions or canonical review pins do not replay')
    phsa = [s for s in imports if s['collection'] == 'queue-completion-phsa']
    for rule in replacements:
        for identifier in rule['sourceIds']:
            accepted = next(s for s in imports if s['sourceId'] == identifier)
            assert accepted['sourceSha256'] == rule['sourceSha256'][identifier]
            assert accepted['dataSha256'] == rule['sourceDataSha256'][identifier]
    added, total = sum(s['rows'] for s in imports), sum(totals.values())
    assert totals['official'] == baseline['overall']['officialRecords'] + added
    assert totals['compiled'] == baseline['overall']['compiledRecords'] - removed
    assert total == preserved + added and index['recordCounts'] == dict(totals)
    assert coverage['officialRows'] == totals['official'] and coverage['legacyRowsRetained'] == totals['compiled']
    disposition_path = OUT / 'original-queue-dispositions.json'
    pinned(OUT, disposition_path.name, acceptance['originalQueueDispositionsSha256'])
    dispositions = read(disposition_path)
    done, external = verify_original_dispositions(dispositions, read(RESEARCH / 'held-resolution-2026-11-01/work-queue.json'))
    current_requests = read(OUT / 'acquisition/work-queue.json')
    current_requests = current_requests if isinstance(current_requests, list) else current_requests['tasks']
    wanted = {entry['id'] for entry in external}
    tasks = [task for task in current_requests if task['id'] in wanted]
    assert {task['id'] for task in tasks} == wanted
    for task in tasks:
        assert set(task) == set(FIELDS) and isinstance(task['reportingPeriods'], list)
    outbox_path = OUT / 'acquisition/outbox/outbox.json'
    pinned(OUT, str(outbox_path.relative_to(OUT)), acceptance['outboxSha256'])
    verify_outbox(read(outbox_path), tasks)
    direction_path = OUT / 'acquisition/outbox/user-direction-2026-11-01.json'
    pinned(OUT, str(direction_path.relative_to(OUT)), acceptance['outreachDirectionSha256'])
    direction = read(direction_path)
    assert direction['status'] == 'on-hold-by-user' and direction['doNotSend'] is True
    assert set(direction['outboxItemIds']) == {item['id'] for item in read(outbox_path)['items']}
    assert direction['outbox'] == {'path': str(outbox_path.relative_to(ROOT)),
                                   'sha256': acceptance['outboxSha256']}
    report = {'version': 1, 'asOf': '2026-11-01', 'timezone': 'America/Vancouver',
              'baselineCommit': baseline['repositoryCommit'], 'baselineFileSha256': sha(baseline_raw),
              'baseline': baseline['overall'],
              'proposed': {'records': total, 'officialRecords': totals['official'],
                           'compiledRecords': totals['compiled'], 'employers': len(index['employers']),
                           'acceptedSourceFiles': len(coverage['imports'])},
              'officialRowsAdded': added, 'compiledRowsReplaced': removed, 'netRowsAdded': added - removed,
              'baselineRowsPreservedExactly': preserved,
              'priorOfficialRowsPreservedExactly': baseline['overall']['officialRecords'],
              'originalReports': len({s['sourceSha256'] for s in imports}), 'acceptedCohorts': len(imports),
              'imports': imports, 'compiledReplacements': replacements,
              'historicalPhsaReportsCompleted': len(phsa), 'historicalPhsaRowsAdded': sum(s['rows'] for s in phsa),
              'originalQueueEntries': len(done) + len(external), 'originalQueueEntriesCompleted': len(done),
              'remainingOriginalPublicProcessingTasks': 0, 'issuerDependentOriginalQueueEntries': len(external),
              'outreachStatus': 'No requests, contacts, formal applications or fees sent.',
              'requestSendingStatus': 'on-hold-by-user',
              'requestSendingDirection': str(direction_path.relative_to(OUT)),
              'manifestSha256': manifests}
    save('release.json', report)
    save('work-queue.json', {'scope': 'Remaining issuer dependencies in the original queue; requests are on hold by user direction. Additional discovered gaps are a separate research inventory.', 'requestSendingStatus': 'on-hold-by-user', 'tasks': tasks})
    save('acquisition-list.json', {'requestStatus': 'on-hold-by-user', 'direction': str(direction_path.relative_to(OUT)), 'outbox': 'acquisition/outbox/outbox.json', 'candidates': tasks})
    for name in ['work-queue.csv', 'acquisition-list.csv']:
        with (OUT / name).open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator='\n')
            writer.writeheader()
            writer.writerows({k: '; '.join(task[k]) if k == 'reportingPeriods' else task[k] for k in FIELDS} for task in tasks)
    lines = ['# Salary queue completion and gap expansion', '',
        f'As of 1 November 2026, **{added:,} accepted official observations** replace **{removed:,} proved compiled copies** and increase the dataset by **{added - removed:,}** to **{total:,} records** across **{len(index["employers"])} employers**. All **{baseline["overall"]["officialRecords"]:,} earlier official observations and their source metadata** remain exact.', '',
        f'All **nine PHSA historical reports, 2015/16–2023/24**, are complete: **{sum(s["rows"] for s in phsa):,} employee observations**. Providence 2023/24 and Vancouver Coastal Health 2020/21 were recovered through the official Legislative Library. The parallel gap search adds the independently reviewed school and municipal sources below.', '',
        '| Measure | Before | After |', '| --- | ---: | ---: |',
        f'| All payment disclosures | {baseline["overall"]["records"]:,} | {total:,} |',
        f'| Official observations | {baseline["overall"]["officialRecords"]:,} | {totals["official"]:,} |',
        f'| Retained compiled observations | {baseline["overall"]["compiledRecords"]:,} | {totals["compiled"]:,} |', '',
        '| Employer / period | Scope | Official rows | Source qualification |', '| --- | --- | ---: | --- |']
    for source in imports:
        lines.append(f'| [{md(source["employerSlug"])} — {md(source["year"])}]({source["sourceUrl"]}) | {md(source["scope"])} | {source["rows"]:,} | {md(source["publicWarning"])} |')
    lines += ['', '## Original work queue', '',
        'Every public acquisition/processing item in the original nine-entry queue is complete. Five queue entries are resolved; two of them were linked aliases for the same nine PHSA reports. Four issuer-dependent copy/clarification entries remain explicit. Their recipient-verified request drafts are on hold at the user’s instruction. These issues cannot be resolved by assuming document dates or missing content. No contact or fee has been made.', '',
        '[Exact dispositions](original-queue-dispositions.json) · [Unsent requests](acquisition-list.md) · [Additional gaps found by agents](additional-gap-inventory.md)', '',
        '## Verification', '',
        'The release gate compares every earlier employer/year/source row multiset, preserving literal names, titles, cents, nulls, physical pages and repeated observations. Only the exact reviewed whole compiled cohort may disappear. Every new source must equal its published rows, retain its exact qualifications, and have pinned independent review evidence. Machine OCR corroboration and personal image review are counted separately. Source subtotal residuals are never balanced away.', '',
        '[Machine reconciliation](release.json) · [Source assumptions and reproduction](README.md)', '']
    (OUT / 'release.md').write_text('\n'.join(lines))
    lines = ['# Remaining copy and clarification requests', '',
        'Four original-queue issuer dependencies remain. The user instructed that these requests be held and noted in the repository; see the [recorded direction](acquisition/outbox/user-direction-2026-11-01.json). Concrete drafts and verified public recipients remain in the [outbox](acquisition/outbox/outbox.json). Nothing has been sent. Existing qualified salary observations remain published; only McBride’s ambiguous five council observations remain excluded.', '',
        '| Employer / period | Existing-record issue | Next action |', '| --- | --- | --- |']
    for task in tasks:
        lines.append(f'| [{md(task["employerName"])} — {md(", ".join(task["reportingPeriods"]))}]({task["sourceUrl"] or task["sourceIndexUrl"]}) | {md(task["reason"])} | {md(task["nextAction"])} |')
    lines += ['', '[CSV](acquisition-list.csv) · [JSON](acquisition-list.json) · [Exact original task dispositions](original-queue-dispositions.json)', '']
    (OUT / 'acquisition-list.md').write_text('\n'.join(lines))
    return {key: report[key] for key in ['officialRowsAdded', 'compiledRowsReplaced', 'netRowsAdded', 'historicalPhsaReportsCompleted', 'remainingOriginalPublicProcessingTasks', 'issuerDependentOriginalQueueEntries']}


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(build_report()))
