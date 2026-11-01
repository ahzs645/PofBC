#!/usr/bin/env python3
"""Reconcile the historical municipal continuation against its deployed baseline."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'municipal-history-pass'
AREAS = ['lower-mainland', 'capital', 'island', 'north', 'interior', 'resolved']
FIELDS = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods', 'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']
ROUTES = {'processing', 'public-archive-research', 'ordinary-records-request', 'clarification-request', 'foi-fallback'}


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def cell(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def validate_frozen_release(root=ROOT):
    """Verify the released inputs without absorbing later, unrelated salary work."""
    research = Path(root) / 'research/salaries'
    out = research / 'municipal-history-pass'
    baseline = read(out / 'baseline.json')
    release = read(out / 'release.json')
    before = {row['employerSlug']: row for row in baseline['municipalities']}
    index = read(Path(root) / 'public/salaries/employers/index.json')
    registered = read(research / 'collections.json')['collections']
    required = ['municipal-history-' + area for area in AREAS]
    assert all(name in registered for name in required), 'All six historical handoffs must remain registered'
    # The six handoffs include north supplemental/council collections. New
    # collections may be registered later, but do not join this released pass.
    released_sources = release['imports'] + release['aggregateOnlySources']
    collections = list(dict.fromkeys(source['collection'] for source in released_sources))
    assert all(name in collections for name in required), 'Released regional collection list changed'
    assert all(name in registered and any(name == area or name.startswith(area + '/') for area in required)
               for name in collections), 'Released historical collection is unregistered or outside the six handoffs'
    actual = []
    aggregate_only = []
    seen_ids = set()
    for collection in collections:
        manifest = read(research / collection / 'sources.json')
        for aggregate, source in ([(False, entry) for entry in manifest.get('sources', [])]
                                  + [(True, entry) for entry in manifest.get('aggregateOnlySources', [])]):
            if aggregate:
                if source.get('status') != 'verified-aggregate-only':
                    continue
            elif not source.get('file') or source.get('status', 'verified') not in {'verified', 'accepted', 'imported'}:
                continue
            identifier = source['id']
            assert identifier not in seen_ids, f'Duplicate historical source ID: {identifier}'
            seen_ids.add(identifier)
            slug = source['employerSlug']
            assert slug in before and before[slug]['status'] == 'current', identifier
            assert source['year'].isdigit() and source['periodType'] == 'calendar', identifier
            assert source['periodStart'] == source['year'] + '-01-01' and source['periodEnd'] == source['year'] + '-12-31', identifier
            published = index['sources'][identifier]
            for key in ['id', 'year', 'periodType', 'periodStart', 'periodEnd', 'sha256', 'threshold', 'thresholdComparison']:
                assert published.get(key) == source.get(key), f'{identifier}: published {key} differs'
            assert published['url'] == source['sourceUrl'], identifier
            assert published.get('sourceKind') in {'official', 'official-pdf', 'official-open-data'}, identifier
            assert published.get('publicWarning') == source.get('publicWarning'), f'{identifier}: published warning differs'
            assert published.get('notes', []) == source.get('notes', []), f'{identifier}: published notes differ'
            assert published.get('validation') == source.get('validation'), f'{identifier}: published validation differs'
            if aggregate:
                assert source['rowCount'] == 0 and published['scope'] == 'aggregate-only', identifier
                if source.get('provenanceFile'):
                    evidence = (research / collection / source['provenanceFile']).read_bytes()
                    assert hashlib.sha256(evidence).hexdigest() == source['provenanceSha256'], identifier
                aggregate_only.append(dict(collection=collection, sourceId=identifier, employerSlug=slug,
                                           year=source['year'], sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], rows=0))
                continue
            raw = (research / collection / source['file']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == source['dataSha256'], f'{identifier}: normalized hash differs'
            payload = json.loads(gzip.decompress(raw))
            rows = payload if isinstance(payload, list) else payload['rows']
            assert len(rows) == source['rowCount'], identifier
            assert published['dataSha256'] == source['dataSha256'] and published['scope'] == source['category'], identifier
            if 'completeEmployeeSchedule' in source:
                assert published.get('completeEmployeeSchedule') == source['completeEmployeeSchedule'], identifier
            if source.get('completeEmployeeSchedule') is False:
                assert source['validation'].get('completeEmployeeSchedule') is False, identifier
            anonymous = sum(row[1] is None for row in rows)
            if anonymous:
                assert source.get('nameDisclosure') == 'not-published', identifier
            actual.append(dict(collection=collection, sourceId=identifier, employerSlug=slug, year=source['year'],
                               category=source['category'], rows=len(rows), unnamedRows=anonymous,
                               sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], dataSha256=source['dataSha256'],
                               publicWarning=source.get('publicWarning')))
    assert actual == release['imports'], 'Historical release inputs changed; review the original release explicitly'
    assert aggregate_only == release['aggregateOnlySources'], 'Historical aggregate-only inputs changed'
    assert release['baseline'] == baseline['overall'] and release['baselineCommit'] == baseline['repositoryCommit'], 'Historical baseline changed'
    assert release['municipalCoverageBefore'] == baseline['municipalSummary'], 'Historical municipal baseline changed'
    for totals in [release['baseline'], release['proposed']]:
        assert totals['records'] == totals['officialRecords'] + totals['compiledRecords'], 'Historical total does not reconcile'
    added = sum(source['rows'] for source in actual)
    assert added == release['officialRowsAdded']
    assert release['proposed']['officialRecords'] - release['baseline']['officialRecords'] == added
    assert release['baseline']['compiledRecords'] - release['proposed']['compiledRecords'] == release['compiledRowsReplaced']
    assert release['proposed']['records'] - release['baseline']['records'] == added - release['compiledRowsReplaced'] == release['netRowsAdded']
    assert release['proposed']['acceptedSourceFiles'] - release['baseline']['acceptedSourceFiles'] == len(actual)
    assert sum(source['rows'] for source in actual if source['category'] == 'employee-remuneration') == release['employeeRowsAdded']
    assert sum(source['rows'] for source in actual if source['category'] == 'elected-officials') == release['councilRowsAdded']
    assert sum(source['unnamedRows'] for source in actual) == release['unnamedRowsAdded']
    assert len({source['sourceSha256'] for source in actual + aggregate_only}) == release['originalReports']
    assert len({(source['employerSlug'], source['year']) for source in actual + aggregate_only}) == release['municipalityYears']
    assert set(release['taskInputSha256']) == set(AREAS), 'Historical queue input list changed'
    tasks = []
    for area in AREAS:
        path = out / area / 'work-queue.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == release['taskInputSha256'][area], f'{area}: historical queue input changed'
        for task in read(path):
            assert all(key in task for key in FIELDS), (area, task.get('id'))
            assert task['route'] in ROUTES and isinstance(task['reportingPeriods'], list), task['id']
            tasks.append({**{key: task[key] for key in FIELDS}, 'area': area, 'requestStatus': 'not-sent'})
    assert len({task['id'] for task in tasks}) == len(tasks), 'Historical queue IDs must be unique'
    tasks.sort(key=lambda task: (task['employerName'], task['route'], task['id']))
    requests = [task for task in tasks if task['route'] in {'ordinary-records-request', 'clarification-request', 'foi-fallback'}]
    assert tasks == read(out / 'work-queue.json')['tasks'], 'Historical combined queue differs from its handoffs'
    assert requests == read(out / 'acquisition-list.json')['candidates'], 'Historical acquisition list differs from its handoffs'
    assert len(tasks) == release['tasks'] and len(requests) == release['requestCandidates']
    assert dict(Counter(task['route'] for task in tasks)) == release['taskCountsByRoute']
    return dict(historicalRelease='municipal-history-pass', records=release['proposed']['records'],
                sourceInputsVerified=len(actual), aggregateOnlySourcesVerified=len(aggregate_only),
                officialRowsAdded=added, queueInputsVerified=len(AREAS))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frozen', action='store_true', help='Verify the historical release without rewriting it or counting later imports')
    args = parser.parse_args(argv)
    if args.frozen:
        print(json.dumps(validate_frozen_release()))
        return
    baseline = read(OUT / 'baseline.json')
    before = {row['employerSlug']: row for row in baseline['municipalities']}
    coverage = read(RESEARCH / 'municipal-audit/coverage.json')
    current = {row['employerSlug']: row for row in coverage['municipalities']}
    audit = read(ROOT / 'public/salaries/coverage.json')
    index = read(ROOT / 'public/salaries/employers/index.json')
    registered = read(RESEARCH / 'collections.json')['collections']
    required = ['municipal-history-' + area for area in AREAS]
    assert all(name in registered for name in required), 'All six historical handoffs must be registered'
    collections = [name for name in registered if name.startswith('municipal-history-')]
    imports = []
    aggregate_only = []
    for collection in collections:
        manifest = read(RESEARCH / collection / 'sources.json')
        for source in manifest.get('aggregateOnlySources', []):
            if source.get('status') != 'verified-aggregate-only':
                continue
            assert source['rowCount'] == 0 and source['employerSlug'] in before
            assert index['sources'][source['id']]['scope'] == 'aggregate-only'
            aggregate_only.append(dict(collection=collection, sourceId=source['id'], employerSlug=source['employerSlug'], year=source['year'], sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], rows=0))
        for source in manifest['sources']:
            if not source.get('file') or source.get('status', 'verified') not in {'verified', 'accepted', 'imported'}:
                continue
            slug = source['employerSlug']
            assert slug in before and before[slug]['status'] == 'current', source['id']
            raw = (RESEARCH / collection / source['file']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == source['dataSha256'], source['id']
            payload = json.loads(gzip.decompress(raw))
            rows = payload if isinstance(payload, list) else payload['rows']
            assert len(rows) == source['rowCount'], source['id']
            assert source['year'].isdigit() and source['periodStart'] == source['year'] + '-01-01' and source['periodEnd'] == source['year'] + '-12-31', source['id']
            published = index['sources'][source['id']]
            assert published['publicWarning'] == source.get('publicWarning') and published['notes'] == source.get('notes', []), source['id']
            assert published['validation'] == source.get('validation'), source['id']
            if source.get('completeEmployeeSchedule') is False:
                assert published.get('completeEmployeeSchedule') is False and source['validation'].get('completeEmployeeSchedule') is False, source['id']
            anonymous = sum(row[1] is None for row in rows)
            if anonymous:
                assert source.get('nameDisclosure') == 'not-published', source['id']
            imports.append(dict(collection=collection, sourceId=source['id'], employerSlug=slug, year=source['year'], category=source['category'], rows=len(rows), unnamedRows=anonymous, sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], dataSha256=source['dataSha256'], publicWarning=source.get('publicWarning')))
    added = sum(source['rows'] for source in imports)
    total = sum(sum(entry['counts']) for entry in index['employers'])
    official = audit['officialRows']
    compiled = audit['legacyRowsRetained']
    replaced = baseline['overall']['compiledRecords'] - compiled
    assert official - baseline['overall']['officialRecords'] == added
    assert total - baseline['overall']['records'] == added - replaced and official + compiled == total
    tasks = []
    fingerprints = {}
    for area in AREAS:
        path = OUT / area / 'work-queue.json'
        fingerprints[area] = hashlib.sha256(path.read_bytes()).hexdigest()
        for task in read(path):
            assert all(key in task for key in FIELDS), (area, task.get('id'))
            assert task['route'] in ROUTES and isinstance(task['reportingPeriods'], list), task['id']
            tasks.append({**{key: task[key] for key in FIELDS}, 'area': area, 'requestStatus': 'not-sent'})
    assert len({task['id'] for task in tasks}) == len(tasks), 'Queue IDs must be unique'
    tasks.sort(key=lambda task: (task['employerName'], task['route'], task['id']))
    requests = [task for task in tasks if task['route'] in {'ordinary-records-request', 'clarification-request', 'foi-fallback'}]
    municipalities = []
    for slug in sorted({source['employerSlug'] for source in imports}):
        sources = [source for source in imports if source['employerSlug'] == slug]
        municipalities.append(dict(employerSlug=slug, employerName=current[slug]['employerName'], addedRows=sum(s['rows'] for s in sources), newEmployeeYears=sorted({s['year'] for s in sources if s['category'] == 'employee-remuneration'} - set(before[slug]['officialEmployeeYears'])), newCouncilYears=sorted({s['year'] for s in sources if s['category'] == 'elected-officials'} - set(before[slug]['officialCouncilYears'])), officialEmployeeYears=current[slug]['officialEmployeeYears'], officialCouncilYears=current[slug]['officialCouncilYears'], newlyOfficial=not before[slug]['officialRecords']))
    amendments = read(RESEARCH / 'release-amendments.json')
    registered_sources = sum(sum(bool(s.get('file')) and s.get('status', 'verified') in {'verified', 'accepted', 'imported'} for s in read(RESEARCH / name / 'sources.json').get('sources', [])) for name in registered)
    result = dict(version=1, asOf='2026-10-31', timezone='America/Vancouver', baselineCommit=baseline['repositoryCommit'], baseline=baseline['overall'], proposed=dict(records=total, officialRecords=official, compiledRecords=compiled, employerEntries=len(index['employers']), acceptedSourceFiles=registered_sources), officialRowsAdded=added, compiledRowsReplaced=replaced, netRowsAdded=added-replaced, employeeRowsAdded=sum(s['rows'] for s in imports if s['category'] == 'employee-remuneration'), councilRowsAdded=sum(s['rows'] for s in imports if s['category'] == 'elected-officials'), unnamedRowsAdded=sum(s['unnamedRows'] for s in imports), originalReports=len({s['sourceSha256'] for s in imports + aggregate_only}), municipalityYears=len({(s['employerSlug'], s['year']) for s in imports + aggregate_only}), municipalities=municipalities, imports=imports, aggregateOnlySources=aggregate_only, municipalCoverageBefore=baseline['municipalSummary'], municipalCoverageAfter=coverage['summary'], correctedPriorTextRows=sum(len(a['rowChanges']) for a in amendments['amendments']), metadataAmendments=len(amendments['metadataAmendments']), taskInputSha256=fingerprints, tasks=len(tasks), requestCandidates=len(requests), taskCountsByRoute=dict(Counter(task['route'] for task in tasks)))
    save('release.json', result)
    save('work-queue.json', dict(version=1, policy='Draft work only. No outreach or fees. Indexed archive labels do not establish reporting periods; existing public documents requiring extraction/OCR are processing tasks.', tasks=tasks))
    save('acquisition-list.json', dict(version=1, requestStatus='not-sent', candidates=requests, existingMunicipalFollowUp='../municipal-audit/follow-up.json'))
    for name, entries in [('work-queue.csv', tasks), ('acquisition-list.csv', requests)]:
        with (OUT / name).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS + ['area', 'requestStatus'], lineterminator='\n')
            writer.writeheader()
            for task in entries:
                writer.writerow({key: '; '.join(task[key]) if key == 'reportingPeriods' else task[key] for key in writer.fieldnames})
    lines = ['# Municipal historical disclosure continuation', '', f"This pass accepts **{added:,} official observations** from **{result['originalReports']} original reports**, covering **{result['municipalityYears']} municipality-years**. It replaces **{replaced:,} proved compiled observations**, for **{added-replaced:,} net additional records**. The dataset grows from **{baseline['overall']['records']:,} to {total:,}**.", '', f"Official municipal coverage is **{coverage['summary']['withOfficialRecordsAfter']} of 161**, including **{coverage['summary']['withOfficialEmployeeRecords']}** with employee schedules. **{coverage['summary']['withNoOfficialRecords']}** current jurisdictions still lack accepted official records. Historical additions extend coverage at previously represented municipalities as well as filling new jurisdictions.", '', '## Histories added', '', '| Municipality | New employee calendar years | New council calendar years | Added observations |', '| --- | --- | --- | ---: |']
    for entry in municipalities:
        lines.append(f"| {cell(entry['employerName'])} | {', '.join(entry['newEmployeeYears']) or '—'} | {', '.join(entry['newCouncilYears']) or '—'} | {entry['addedRows']:,} |")
    if aggregate_only:
        lines += ['', 'Verified aggregate-only periods: ' + '; '.join(current[s['employerSlug']]['employerName'] + ' ' + s['year'] for s in aggregate_only) + '. The source explicitly reports no named employee cohort; aggregate payroll is not converted into individual records.']
    lines += ['', '## Source decisions and corrections', '', f"The new inputs contain {result['employeeRowsAdded']:,} employee and {result['councilRowsAdded']:,} elected-official observations. {result['unnamedRowsAdded']} records have no separately published name field; their actual printed positions or labels and payments remain available without inventing a name or joining identities across years.", '', 'Periods come from the named schedule and original report, not the upload URL or meeting date. Each accepted source has original and normalized hashes, physical pages, row-level corroboration and rendered review. PDF OCR overlays are distinguished from native tables; two configurations of one OCR engine are not called independent engines. Missing or malformed expense amounts remain null with exact source evidence. Source columns determine remuneration; expense-inclusive totals are not pay, and undefined benefits/grant components are not silently added.', '', 'Faithful published rows can carry unresolved source-control qualifications. Each such source has a visible warning identifying known sums, printed controls, scope differences and missing components. No amounts are changed to balance totals; an unknown component is not assigned zero. Partial employee cohorts have explicit completeness=false flags and cannot silently replace compiled partitions.', '', f"This pass also restores {result['correctedPriorTextRows']} published initials dropped by an old text filter and corrects {result['metadataAmendments']} prior source-control scope descriptions. Counts and monetary cells in those earlier inputs remain unchanged. [Archived originals, exact amendments and independent review](corrections/interior-initials/central-review.md) and [control-scope review](corrections/north-expense-scope/central-review.md) preserve what PR27 originally published; the frozen release validator verifies the archival bytes and exact permitted repairs.", '', '## Regional and independent reviews', '']
    for area in AREAS:
        lines.append(f'- [{area} sources, histories and remaining blockers]({area}/README.md)')
    for review in sorted((OUT / 'reviews').glob('*.md')):
        lines.append(f'- [Independent {review.stem.replace("-", " ")} review](reviews/{review.name})')
    lines += ['', '## What remains', '', f"The [remaining queue](work-queue.csv) contains {len(tasks)} tasks in this pass; the [copy/clarification list](acquisition-list.md) contains {len(requests)} candidates. These may overlap older lists: do not add their counts. Use the [current province-wide coverage table](../municipal-audit/coverage.md) for all 161 jurisdictions and exact accepted years. Located archive years remain leads until each original and cohort is verified; this review does not claim every historical report has been found.", '', 'No municipality was contacted and no FOI request or fee was submitted. Search public finance pages and council attachments first; request an existing adopted report or native table routinely if retrieval fails, with formal access as a fallback. Regional districts remain outside the municipal denominator, shíshálh is a separate governance case, and Okanagan Falls is pending incorporation on November 6, 2026.', '', '## Reproduce', '', 'Use each collection guide for pinned-original extraction. Offline publication checks:', '', '```sh', 'python3 -m unittest discover -s scripts -p \'test_*.py\'', 'node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js', 'npm run compare:municipal-periods', 'npm run build:salaries', 'npm run check:salaries', 'npm run audit:municipal-salaries', 'npm run follow-up:municipal-salaries', 'npm run review:sector-salaries', 'npm run review:municipal-wave', 'npm run review:municipal-history', 'npm run preview:salaries -- --build', '```', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    lines = ['# Historical source copy and clarification candidates', '', 'Draft actions only; no requests sent. Existing public files needing OCR/row review remain processing tasks. Ordinary access to an existing report or spreadsheet comes before a formal FOI fallback.', '', '| Municipality / periods | Route | Blocker | Next action |', '| --- | --- | --- | --- |']
    for task in requests:
        label = cell(task['employerName']) + ' — ' + cell(', '.join(task['reportingPeriods']) or 'period to establish')
        lines.append(f"| [{label}]({task['sourceUrl'] or task['sourceIndexUrl']}) | {cell(task['route'])} | {cell(task['reason'])} | {cell(task['nextAction'])} |")
    lines += ['', '[CSV](acquisition-list.csv) · [JSON](acquisition-list.json) · [Current province-wide follow-up](../municipal-audit/follow-up.md)', '']
    (OUT / 'acquisition-list.md').write_text('\n'.join(lines))
    print(json.dumps({key: result[key] for key in ['officialRowsAdded', 'compiledRowsReplaced', 'netRowsAdded', 'municipalityYears', 'originalReports', 'unnamedRowsAdded', 'tasks', 'requestCandidates']}))


if __name__ == '__main__':
    main()
