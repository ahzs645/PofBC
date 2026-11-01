#!/usr/bin/env python3
"""Combine sector search handoffs and reconcile this release with its frozen baseline."""
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'sector-search-2026-10-31'
SECTORS = ['municipal', 'health', 'schools', 'education', 'crowns', 'government-police']
COLLECTIONS = [f'sector-{name}' for name in ['municipal', 'health', 'schools', 'education', 'crowns', 'government-police']]
ROUTES = {'processing', 'public-archive-research', 'ordinary-records-request', 'clarification-request', 'foi-fallback'}
FIELDS = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods', 'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def cell(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def main():
    baseline = read(OUT / 'baseline.json')
    if '--frozen' in sys.argv:
        # PR25 is a historical release. Later municipal imports must not rewrite
        # its totals or cause its old baseline reconciliation to absorb new rows.
        release = read(OUT / 'release.json')
        actual = []
        for collection in COLLECTIONS:
            for source in read(RESEARCH / collection / 'sources.json')['sources']:
                raw = (RESEARCH / collection / source['file']).read_bytes()
                assert hashlib.sha256(raw).hexdigest() == source['dataSha256'], source['id']
                assert len(json.loads(gzip.decompress(raw))) == source['rowCount'], source['id']
                actual.append(dict(collection=collection, sourceId=source['id'], employerSlug=source['employerSlug'], year=source['year'], scope=source['category'], rows=source['rowCount'], sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], dataSha256=source['dataSha256'], publicWarning=source.get('publicWarning')))
        assert actual == release['imports'], 'Historical release input changed; review the original release explicitly'
        assert release['baseline'] == baseline['overall']
        assert sum(source['rows'] for source in actual) == release['officialRowsAdded']
        assert release['proposed']['officialRecords'] - release['baseline']['officialRecords'] == release['officialRowsAdded']
        assert release['baseline']['compiledRecords'] - release['proposed']['compiledRecords'] == release['compiledRowsReplaced']
        assert release['proposed']['records'] - release['baseline']['records'] == release['officialRowsAdded'] - release['compiledRowsReplaced'] == release['netRowsAdded']
        for area, expected in release['taskInputSha256'].items():
            assert hashlib.sha256((OUT / area / 'work-queue.json').read_bytes()).hexdigest() == expected, area
        print(json.dumps({'historicalRelease': 'PR25', 'records': release['proposed']['records'], 'sourceInputsVerified': len(actual)}))
        return
    index = read(ROOT / 'public/salaries/employers/index.json')
    current = defaultdict(lambda: dict(employerEntries=0, records=0, officialRecords=0, compiledRecords=0, employersWithOfficialRecords=0))
    current_employers = []
    for employer in index['employers']:
        raw = (ROOT / 'public/salaries/employers' / f"{employer['slug']}.json.gzip").read_bytes()
        rows = json.loads(gzip.decompress(raw))
        official = sum(index['sources'][row[5]].get('sourceKind') != 'compiled' and index['sources'][row[5]].get('scope') != 'compiled-unverified' for row in rows)
        group = current[employer['sector']]
        group['employerEntries'] += 1
        group['records'] += len(rows)
        group['officialRecords'] += official
        group['compiledRecords'] += len(rows) - official
        group['employersWithOfficialRecords'] += bool(official)
        current_employers.append(dict(slug=employer['slug'], records=len(rows), officialRecords=official, exportSha256=hashlib.sha256(raw).hexdigest()))
    imports = []
    for collection in COLLECTIONS:
        for source in read(RESEARCH / collection / 'sources.json')['sources']:
            imports.append(dict(collection=collection, sourceId=source['id'], employerSlug=source['employerSlug'], year=source['year'], scope=source['category'], rows=source['rowCount'], sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], dataSha256=source['dataSha256'], publicWarning=source.get('publicWarning')))
    tasks = []
    fingerprints = {}
    for sector in SECTORS:
        path = OUT / sector / 'work-queue.json'
        fingerprints[sector] = hashlib.sha256(path.read_bytes()).hexdigest()
        entries = read(path)
        assert isinstance(entries, list), sector
        for task in entries:
            assert all(field in task for field in FIELDS), (sector, task.get('id'))
            assert task['route'] in ROUTES and isinstance(task['reportingPeriods'], list), task['id']
            assert task['nextAction'] and task['reason'], task['id']
            tasks.append({**task, 'researchArea': sector, 'requestStatus': 'not-sent'})
    assert len({task['id'] for task in tasks}) == len(tasks), 'Task IDs must be globally unique'
    tasks.sort(key=lambda task: (task['sector'], task['employerName'], task['route'], task['id']))
    requests = [task for task in tasks if task['route'] in {'ordinary-records-request', 'clarification-request', 'foi-fallback'}]
    municipal = read(RESEARCH / 'municipal-audit/follow-up.json')
    overall = {key: sum(value[key] for value in current.values()) for key in ['records', 'officialRecords', 'compiledRecords', 'employerEntries', 'employersWithOfficialRecords']}
    registered = read(RESEARCH / 'collections.json')['collections']
    overall['acceptedSourceFiles'] = sum(sum(bool(source.get('file')) and source.get('status', 'accepted') in {'accepted', 'verified', 'imported'} for source in read(RESEARCH / collection / 'sources.json').get('sources', [])) for collection in registered)
    added = sum(source['rows'] for source in imports)
    replaced = baseline['overall']['compiledRecords'] - overall['compiledRecords']
    assert overall['officialRecords'] - baseline['overall']['officialRecords'] == added
    assert overall['records'] - baseline['overall']['records'] == added - replaced
    release = dict(version=1, asOf='2026-10-31', timezone='America/Vancouver', baselineCommit=baseline['repositoryCommit'], baseline=baseline['overall'], proposed=overall, officialRowsAdded=added, compiledRowsReplaced=replaced, netRowsAdded=added-replaced, sectors=dict(current), imports=imports, employers=current_employers, taskInputSha256=fingerprints, taskCountsByRoute=dict(Counter(task['route'] for task in tasks)), taskCountsByArea=dict(Counter(task['researchArea'] for task in tasks)), tasks=len(tasks), requestCandidates=len(requests), municipalJurisdictionsWithoutOfficialRecords=municipal['summary']['currentJurisdictionsWithoutOfficialRecords'], municipalDetailedRequests=municipal['summary']['specificRequestCandidates'])
    save('release.json', release)
    save('work-queue.json', dict(version=1, asOf='2026-10-31', policy='Research and draft requests only. No outside messages, FOI filings or fee commitments. A task can cover several reports; counts are tasks, not unique documents or missing jurisdictions. Indexed years remain discovery labels until verified in the original.', tasks=tasks))
    save('acquisition-list.json', dict(version=1, asOf='2026-10-31', policy='Use the public archive first, then request an existing adopted report or electronic schedule routinely. Formal access is a fallback if routine access fails. No request has been sent. Includes the 11 existing municipal request candidates; their detailed wording is linked separately. Do not add their counts.', candidates=requests, existingMunicipalList='../municipal-audit/follow-up.json'))
    for name, entries in [('work-queue.csv', tasks), ('acquisition-list.csv', requests)]:
        with (OUT / name).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS + ['researchArea', 'requestStatus'], lineterminator='\n')
            writer.writeheader()
            for task in entries:
                writer.writerow({key: '; '.join(task[key]) if key == 'reportingPeriods' else task[key] for key in writer.fieldnames})
    lines = ['# Salary histories and source follow-up', '', 'Reviewed 31 October 2026 (America/Vancouver). Six research agents searched municipalities, health, schools, postsecondary institutions, Crown corporations, government, police and regional districts. This is a source-discovery and verified-import pass; it does not establish complete historical coverage.', '', f"This release accepts **{added:,} official observations**, replaces **{replaced:,} compiled observations** through reviewed fiscal replacements and a hash-pinned InBC period correction, and adds **{added-replaced:,} net records**. The dataset grows from **{baseline['overall']['records']:,} to {overall['records']:,}**. Exact cross-calendar municipal replacement decisions remain separately hash-pinned; partial overlaps are retained.", '', '| Collection | Official records added | Cohorts |', '| --- | ---: | ---: |']
    for collection in COLLECTIONS:
        sources = [source for source in imports if source['collection'] == collection]
        lines.append(f"| [{collection}](../{collection}/README.md) | {sum(source['rows'] for source in sources):,} | {len(sources)} |")
    lines += ['', '## Start here', '', '- [Acquisition and clarification list](acquisition-list.md): specific routine-copy and explanation candidates; no requests sent.', '- [Complete processing and historical research queue](work-queue.csv): one row per actionable task, with source links, periods and next action.', '- [Machine-readable release reconciliation](release.json): every accepted cohort, original/data hashes, warnings and baseline comparison.', '- [Municipality coverage](../municipal-audit/coverage.md) and [existing municipal requests](../municipal-audit/follow-up.md): province-wide municipal roster and deeper source tasks.', '', '## Coverage and assumptions', '', 'A linked document is a lead until its internal reporting period, named schedule, rows and monetary definitions have been checked. School, health and university fiscal periods differ from calendar municipal periods. Upload dates and archive labels do not establish salary years. These are payment disclosures, not annual base salary rates or complete employee rosters.', '', 'Employee, trustee, council, board and executive scopes stay distinct. Printed dashes and blanks remain missing; numeric zeros and negative expenses remain as disclosed. Metro Vancouver remuneration combines salary with benefits/other compensation. Nine Metro rows with an undisclosed component remain held, and the partial cohorts carry visible warnings. Small unresolved published subtotal residuals are retained and disclosed; no balancing edits or rounding explanation is inferred.', '', 'Official SFU and SD42 complete fiscal schedules replace the corresponding compiled partitions after scope review. SD42 includes trustee schedules, and the two compiler spellings are joined under the official district identity. Compiler name/title enrichments are not carried into official records without source support. Three SFU years with material source-control discrepancies remain held. See [replacement review](replacement-review.md).', '', f"The municipal denominator remains 161 current jurisdictions, excluding regional districts. {municipal['summary']['currentJurisdictionsWithoutOfficialRecords']} still lack accepted official records. Metro Vancouver is a regional district. New school and regional-district discovery inventories are broader than the employers with records in the app.", '', '## Research areas', '']
    for sector in SECTORS:
        lines.append(f"- [{sector} findings and receipts]({sector}/README.md) — {sum(task['researchArea'] == sector for task in tasks)} follow-up tasks.")
    lines += ['', '## Reproduce', '', 'Use each collection README to download/re-extract hash-pinned original reports. The application build itself is offline:', '', '```sh', 'python3 -m unittest discover -s scripts -p \'test_*.py\'', 'node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js', 'npm run compare:municipal-periods', 'npm run build:salaries', 'npm run check:salaries', 'npm run audit:municipal-salaries', 'npm run follow-up:municipal-salaries', 'npm run review:sector-salaries', 'npm run preview:salaries -- --build', '```', '', 'Original extraction, rendered review, independent-reader agreement and source residuals are retained per collection. Queue CSV files are generated from the six normalized handoffs. The frozen baseline is the previously deployed main commit; rebuilds assert that official additions, compiled replacements and the total change reconcile.', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    acquisition = ['# Acquisition and clarification candidates', '', f"{len(requests)} tasks across this search pass. These are draft actions; no requests have been sent. This includes the 11 existing municipal request candidates; their [detailed request wording](../municipal-audit/follow-up.md) remains available. Public originals needing OCR or extraction are in the [processing queue](work-queue.csv), not counted here.", '', 'Ask for existing adopted SOFI/payment schedules, amendments and an existing CSV/spreadsheet where available. Do not request creation of a new analysis. Start with ordinary public access; use formal FOI only if needed after that route. Confirm the public body and employee/board/police scope before requesting.', '', '| Employer / periods | Route | Evidence and blocker | Next action |', '| --- | --- | --- | --- |']
    for task in requests:
        url = task['sourceUrl'] or task['sourceIndexUrl']
        label = cell(task['employerName']) + (' — ' + cell(', '.join(task['reportingPeriods'])) if task['reportingPeriods'] else ' — period to establish')
        acquisition.append(f"| [{label}]({url}) | {cell(task['route'])} | {cell(task['reason'])} | {cell(task['nextAction'])} |")
    acquisition += ['', 'The complete machine-readable list includes source/index URLs and task IDs: [CSV](acquisition-list.csv), [JSON](acquisition-list.json).', '']
    (OUT / 'acquisition-list.md').write_text('\n'.join(acquisition))
    print(json.dumps({key: release[key] for key in ['officialRowsAdded', 'compiledRowsReplaced', 'netRowsAdded', 'tasks', 'requestCandidates']}))


if __name__ == '__main__':
    main()
