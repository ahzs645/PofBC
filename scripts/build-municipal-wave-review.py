#!/usr/bin/env python3
"""Reconcile the municipal gap-filling pass and publish its source/action register."""
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from salary_release_audit import verify_frozen_release

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'municipal-next-pass'
AREAS = ['lower-mainland', 'capital', 'island', 'north', 'interior']
FIELDS = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods', 'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']
ROUTES = {'processing', 'public-archive-research', 'ordinary-records-request', 'clarification-request', 'foi-fallback'}


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def text(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def main():
    if '--frozen' in sys.argv:
        print(json.dumps(verify_frozen_release(OUT, RESEARCH)))
        return
    baseline = read(OUT / 'baseline.json')
    coverage = read(RESEARCH / 'municipal-audit/coverage.json')
    audit = read(ROOT / 'public/salaries/coverage.json')
    index = read(ROOT / 'public/salaries/employers/index.json')
    registered = read(RESEARCH / 'collections.json')['collections']
    collections = [name for name in registered if name.startswith('municipal-wave-')]
    assert len(collections) == len(AREAS), 'All five reviewed regional handoffs must be registered'
    roster = {entry['employerSlug']: entry for entry in baseline['municipalities']}
    imports = []
    for collection in collections:
        manifest = read(RESEARCH / collection / 'sources.json')
        for source in manifest['sources']:
            if not source.get('file') or source.get('status', 'verified') not in {'accepted', 'verified', 'imported'}:
                continue
            assert source['employerSlug'] in roster and roster[source['employerSlug']]['status'] == 'current', source['id']
            raw = (RESEARCH / collection / source['file']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == source['dataSha256'], source['id']
            rows = json.loads(gzip.decompress(raw))
            assert len(rows) == source['rowCount'], source['id']
            assert source['year'].isdigit() and source['periodStart'] == source['year'] + '-01-01' and source['periodEnd'] == source['year'] + '-12-31', source['id']
            published = index['sources'][source['id']]
            assert published['publicWarning'] == source.get('publicWarning'), source['id']
            assert published['notes'] == source.get('notes', []), source['id']
            if source.get('completeEmployeeSchedule') is False:
                assert published.get('completeEmployeeSchedule') is False, source['id']
                assert source['validation'].get('completeEmployeeSchedule') is False, source['id']
            imports.append(dict(collection=collection, sourceId=source['id'], employerSlug=source['employerSlug'], year=source['year'], category=source['category'], rows=len(rows), sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], dataSha256=source['dataSha256'], publicWarning=source.get('publicWarning')))
    added = sum(source['rows'] for source in imports)
    total = sum(sum(employer['counts']) for employer in index['employers'])
    official = audit['officialRows']
    compiled = audit['legacyRowsRetained']
    removed = baseline['overall']['compiledRecords'] - compiled
    assert official - baseline['overall']['officialRecords'] == added
    assert total - baseline['overall']['records'] == added - removed
    assert official + compiled == total
    before = {entry['employerSlug']: entry for entry in baseline['municipalities']}
    newly_covered = [entry for entry in coverage['municipalities'] if entry['officialRecords'] and not before[entry['employerSlug']]['officialRecords']]
    tasks = []
    for area in AREAS:
        entries = read(OUT / area / 'work-queue.json')
        assert isinstance(entries, list), area
        for task in entries:
            assert all(key in task for key in FIELDS), (area, task.get('id'))
            assert isinstance(task['reportingPeriods'], list) and task['route'] in ROUTES, task['id']
            assert task['nextAction'] and task['reason'], task['id']
            tasks.append({**{key: task[key] for key in FIELDS}, 'area': area, 'requestStatus': 'not-sent'})
    assert len({task['id'] for task in tasks}) == len(tasks)
    tasks.sort(key=lambda task: (task['employerName'], task['route'], task['id']))
    requests = [task for task in tasks if task['route'] in {'ordinary-records-request', 'clarification-request', 'foi-fallback'}]
    result = dict(version=1, asOf='2026-10-31', baselineCommit=baseline['repositoryCommit'], baseline=baseline['overall'], proposed=dict(records=total, officialRecords=official, compiledRecords=compiled, employerEntries=len(index['employers'])), officialRowsAdded=added, compiledRowsReplaced=removed, netRowsAdded=added-removed, municipalCoverageBefore=baseline['municipalSummary'], municipalCoverageAfter=coverage['summary'], newlyCoveredMunicipalities=[entry['employerSlug'] for entry in newly_covered], imports=imports, taskCountsByRoute=dict(Counter(task['route'] for task in tasks)), tasks=len(tasks), requestCandidates=len(requests))
    save('release.json', result)
    save('work-queue.json', dict(version=1, policy='Draft actions only; no messages, FOI filings or fees. Public documents requiring extraction/OCR are processing tasks. Index labels remain unverified until the named schedule is checked.', tasks=tasks))
    save('acquisition-list.json', dict(version=1, candidates=requests, existingDetailedMunicipalList='../municipal-audit/follow-up.json', requestStatus='not-sent'))
    for name, entries in [('work-queue.csv', tasks), ('acquisition-list.csv', requests)]:
        with (OUT / name).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS + ['area', 'requestStatus'], lineterminator='\n')
            writer.writeheader()
            for task in entries:
                writer.writerow({key: '; '.join(task[key]) if key == 'reportingPeriods' else task[key] for key in writer.fieldnames})
    lines = ['# Filling the remaining municipal salary gaps', '', 'This pass starts from merged PR #25 (917,420 records; 57 of 161 current municipalities with accepted official records). Five research agents worked on different regions, prioritizing municipalities with no accepted official records and retaining historical source leads.', '', f"Accepted **{added:,} official observations**, replaced **{removed:,} proved compiled observations**, and added **{added-removed:,} net records**. The app contains **{total:,} records**. Official municipal coverage is now **{coverage['summary']['withOfficialRecordsAfter']} of 161**, with **{coverage['summary']['withNoOfficialRecords']}** still lacking accepted official records.", '', '## Newly covered municipalities', '', '| Municipality | Employee calendar years | Council calendar years | Official records now |', '| --- | --- | --- | ---: |']
    for entry in newly_covered:
        lines.append(f"| {text(entry['employerName'])} | {', '.join(entry['officialEmployeeYears']) or '—'} | {', '.join(entry['officialCouncilYears']) or '—'} | {entry['officialRecords']:,} |")
    lines += ['', '## Source collections', '', '| Region | Official records added | Cohorts |', '| --- | ---: | ---: |']
    for area in AREAS:
        sources = [source for source in imports if source['collection'] == 'municipal-wave-' + area]
        lines.append(f"| [{area}]({area}/README.md) | {sum(source['rows'] for source in sources):,} | {len(sources)} |")
    lines += ['', '## Remaining work', '', f"The [complete queue](work-queue.csv) contains {len(tasks)} tasks across this pass. The [copy/clarification candidates](acquisition-list.md) identify {len(requests)} actions that may need an existing electronic file, an adopted report, or an explanation. These can overlap the [detailed province-wide follow-up list](../municipal-audit/follow-up.md); do not add their counts.", '', 'See the [full 161-jurisdiction coverage table](../municipal-audit/coverage.md) for every remaining municipality, source links, accepted calendar years and retained unverified compiled editions. Regional districts are outside that denominator; Okanagan Falls is pending incorporation on November 6, 2026.', '', 'Named employee and council schedules remain separate. Reporting years come from the schedule, not upload dates. Remuneration follows source column definitions; expenses stay separate. Blank/dash amounts remain missing and explicit zeros/negative amounts remain as printed. Original values are never changed to balance a subtotal. Source residuals have visible warnings; unverified OCR and ambiguous rows remain held.', '', 'No requests or messages were sent. Check public archives and council attachments first, then request an existing adopted schedule or spreadsheet routinely; formal FOI remains a fallback after checking the relevant access route.', '', '## Reproduce', '', 'Each collection README describes original retrieval and row-level verification. The offline publication checks are:', '', '```sh', 'python3 -m unittest discover -s scripts -p \'test_*.py\'', 'node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js', 'npm run compare:municipal-periods', 'npm run build:salaries', 'npm run check:salaries', 'npm run audit:municipal-salaries', 'npm run follow-up:municipal-salaries', 'npm run review:sector-salaries', 'npm run review:municipal-wave', 'npm run preview:salaries -- --build', '```', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    lines = ['# Municipal copy and clarification candidates', '', 'Draft actions only; none has been sent. Existing public originals requiring OCR or extraction remain in the processing queue. Routine access to an existing adopted schedule/native spreadsheet comes before a formal FOI fallback.', '', '| Municipality / periods | Route | Reason | Next action |', '| --- | --- | --- | --- |']
    for task in requests:
        url = task['sourceUrl'] or task['sourceIndexUrl']
        label = text(task['employerName']) + ' — ' + text(', '.join(task['reportingPeriods']) or 'period to establish')
        lines.append(f"| [{label}]({url}) | {text(task['route'])} | {text(task['reason'])} | {text(task['nextAction'])} |")
    lines += ['', '[CSV](acquisition-list.csv) · [JSON](acquisition-list.json) · [Province-wide detailed follow-up](../municipal-audit/follow-up.md)', '']
    (OUT / 'acquisition-list.md').write_text('\n'.join(lines))
    print(json.dumps({key: result[key] for key in ['officialRowsAdded', 'compiledRowsReplaced', 'netRowsAdded', 'tasks', 'requestCandidates', 'newlyCoveredMunicipalities']}))


if __name__ == '__main__':
    main()
