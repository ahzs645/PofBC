#!/usr/bin/env python3
"""Reconcile the November source continuation, its scopes and remaining acquisition work."""
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'continuation-2026-11-01'
AREAS = ['municipal', 'health', 'schools', 'education', 'crowns', 'government-police']
FIELDS = ['id', 'employerSlug', 'employerName', 'sector', 'reportingPeriods', 'sourceUrl', 'sourceIndexUrl', 'status', 'route', 'nextAction', 'reason']
ROUTES = {'processing', 'public-archive-research', 'ordinary-records-request', 'clarification-request', 'foi-fallback'}
ACCEPTED = {'verified', 'accepted', 'imported'}


def read(path):
    return json.loads(path.read_text())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def md(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def compiled(source):
    return source.get('sourceKind') == 'compiled' or source.get('scope') == 'compiled-unverified'


def compiled_fingerprint(rows):
    """Pin literal four-field multisets, with currency represented as integer cents."""
    keys = [json.dumps([row[0], row[1], int(Decimal(str(row[2])) * 100),
                        None if row[3] is None else int(Decimal(str(row[3])) * 100)],
                       ensure_ascii=False, separators=(',', ':')) for row in rows]
    return digest('\n'.join(sorted(keys, key=lambda key: key.encode('utf-8'))).encode('utf-8'))


def main():
    baseline = read(OUT / 'baseline.json')
    index = read(ROOT / 'public/salaries/employers/index.json')
    audit = read(ROOT / 'public/salaries/coverage.json')
    municipal = read(RESEARCH / 'municipal-audit/coverage.json')
    registry = read(RESEARCH / 'collections.json')['collections']
    collections = [name for name in registry if name.startswith('continuation-')]
    assert all('continuation-' + area in collections for area in AREAS), 'All six sector handoffs must be registered'
    imports, aggregates = [], []
    for collection in collections:
        folder = RESEARCH / collection
        manifest = read(folder / 'sources.json')
        for source in manifest.get('aggregateOnlySources', []):
            if source.get('status') == 'verified-aggregate-only':
                assert source['rowCount'] == 0 and index['sources'][source['id']]['scope'] == 'aggregate-only'
                aggregates.append(dict(collection=collection, sourceId=source['id'], employerSlug=source['employerSlug'], year=source['year'], sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], rows=0))
        for source in manifest.get('sources', []):
            if not source.get('file') or source.get('status', 'verified') not in ACCEPTED:
                continue
            assert source['id'] not in baseline['sources'], f"Previously accepted source reimported: {source['id']}"
            assert isinstance(source.get('notes'), list) and all(isinstance(note, str) for note in source['notes']), source['id']
            raw = (folder / source['file']).read_bytes()
            assert digest(raw) == source['dataSha256'], source['id']
            payload = json.loads(gzip.decompress(raw))
            rows = payload if isinstance(payload, list) else payload['rows']
            assert len(rows) == source['rowCount'] and rows, source['id']
            assert len(source['sha256']) == 64 and source['sourceUrl'].startswith(('https://', 'http://')), source['id']
            start, end = date.fromisoformat(source['periodStart']), date.fromisoformat(source['periodEnd'])
            assert start <= end, source['id']
            if source.get('periodType') == 'calendar':
                assert source['periodStart'] == source['year'] + '-01-01' and source['periodEnd'] == source['year'] + '-12-31', source['id']
            if (end - start).days > 367:
                assert source.get('publicWarning'), f"Longer-than-annual period needs a visible qualification: {source['id']}"
            published = index['sources'][source['id']]
            assert published['scope'] == (source.get('category') or source['scope']), source['id']
            assert published['periodStart'] == source['periodStart'] and published['periodEnd'] == source['periodEnd'], source['id']
            for key in ['notes', 'validation', 'publicWarning']:
                expected = source.get(key, [] if key == 'notes' else None)
                assert published[key] == expected, (source['id'], key)
            assert published['sha256'] == source['sha256'] and published['dataSha256'] == source['dataSha256'], source['id']
            if source.get('completeEmployeeSchedule') is False:
                assert source['validation'].get('completeEmployeeSchedule') is False and published['completeEmployeeSchedule'] is False, source['id']
            if source.get('retainCompiledPartition'):
                assert published.get('retainCompiledPartition') is True and source['publicWarning'], source['id']
                assert source['validation'].get('compiledPartitionRetained') is True and source['validation'].get('compiledPartitionRetentionReason'), source['id']
            for file_key, hash_key in [('provenanceFile', 'provenanceSha256'), ('evidenceFile', 'evidenceSha256')]:
                if source.get(file_key):
                    assert digest((folder / source[file_key]).read_bytes()) == source[hash_key], source['id']
            unnamed = sum(row[1] is None for row in rows)
            if unnamed:
                assert source.get('nameDisclosure') == 'not-published', source['id']
            imports.append(dict(collection=collection, sourceId=source['id'], employerSlug=source['employerSlug'], employerName=source['employerName'], sector=source['sector'], year=source['year'], periodStart=source['periodStart'], periodEnd=source['periodEnd'], scope=source.get('category') or source['scope'], rows=len(rows), unnamedRows=unnamed, sourceUrl=source['sourceUrl'], sourceSha256=source['sha256'], dataSha256=source['dataSha256'], publicWarning=source.get('publicWarning'), retainCompiledPartition=source.get('retainCompiledPartition', False)))
    assert len({s['sourceId'] for s in imports}) == len(imports), 'Repeated new source ID'
    old_employers = {e['slug']: e for e in baseline['employers']}
    old_by_sector = defaultdict(Counter)
    for employer in old_employers.values():
        old_by_sector[employer['sector']].update({key: employer[key] for key in ['records', 'officialRecords', 'compiledRecords']})
        old_by_sector[employer['sector']]['employerEntries'] += 1
    current_by_sector, current_employers, compiled_partitions = defaultdict(Counter), [], {}
    for employer in index['employers']:
        raw = (ROOT / 'public/salaries/employers' / (employer['slug'] + '.json.gzip')).read_bytes()
        rows = json.loads(gzip.decompress(raw))
        retained = [r for r in rows if compiled(index['sources'][r[5]])]
        official_count = len(rows) - len(retained)
        compiled_years = Counter(index['years'][r[4]] for r in retained)
        for year, count in compiled_years.items():
            compiled_partitions[(employer['slug'], year)] = count
        current_by_sector[employer['sector']].update(records=len(rows), officialRecords=official_count, compiledRecords=len(retained), employerEntries=1)
        accepted_years = sorted({index['years'][r[4]] for r in rows if not compiled(index['sources'][r[5]])})
        current_employers.append(dict(slug=employer['slug'], employerName=employer['names'][-1], sector=employer['sector'], records=len(rows), officialRecords=official_count, compiledRecords=len(retained), officialYears=accepted_years, compiledYearCounts=dict(compiled_years), exportSha256=digest(raw), newEmployer=employer['slug'] not in old_employers, newOfficialEmployer=bool(official_count) and not old_employers.get(employer['slug'], {}).get('officialRecords', 0)))
    added = sum(s['rows'] for s in imports)
    total = sum(e['records'] for e in current_employers)
    official = sum(e['officialRecords'] for e in current_employers)
    retained_count = sum(e['compiledRecords'] for e in current_employers)
    replaced = baseline['overall']['compiledRecords'] - retained_count
    assert official == audit['officialRows'] and retained_count == audit['legacyRowsRetained']
    assert index['recordCounts'] == dict(official=official, compiled=retained_count)
    assert official - baseline['overall']['officialRecords'] == added
    assert total - baseline['overall']['records'] == added - replaced and total == official + retained_count
    removed = []
    for employer in baseline['employers']:
        for year, count in employer['compiledYearCounts'].items():
            after = compiled_partitions.get((employer['slug'], year), 0)
            assert after <= count, (employer['slug'], year)
            if after < count:
                removed.append(dict(employerSlug=employer['slug'], year=year, compiledRowsBefore=count, compiledRowsAfter=after, replacedRows=count-after))
    assert sum(r['replacedRows'] for r in removed) == replaced
    review = read(OUT / 'replacement-review.json')
    decisions = {(r['employerSlug'], r['year']): r for r in review['decisions']}
    assert len(decisions) == len(review['decisions'])
    snapshot_manifest = read(RESEARCH / 'baseline-manifest.json')
    snapshot_raw = (RESEARCH / snapshot_manifest['file']).read_bytes()
    assert digest(snapshot_raw) == snapshot_manifest['sha256'], 'Compiled snapshot changed'
    snapshot = json.loads(gzip.decompress(snapshot_raw))
    snapshot_partitions = defaultdict(list)
    for employer in snapshot['employers']:
        slug = index['aliases'].get(employer['slug'], employer['slug'])
        for row in employer['rows']:
            snapshot_partitions[(slug, snapshot['years'][row[4]])].append(row)
    for partition in removed:
        decision = decisions[(partition['employerSlug'], partition['year'])]
        assert decision['status'] == 'reviewed' and decision['reason'] and decision['sourceIds']
        assert all(decision[key] == value for key, value in partition.items()), partition
        assert all(source_id in index['sources'] for source_id in decision['sourceIds'])
        assert decision['baselineCommit'] == baseline['repositoryCommit']
        original_rows = snapshot_partitions[(partition['employerSlug'], partition['year'])]
        assert len(original_rows) == partition['compiledRowsBefore'], partition
        assert compiled_fingerprint(original_rows) == decision['compiledRowsSha256'], partition
        assert all(index['sources'][source_id]['dataSha256'] == decision['sourceDataSha256'][source_id] and index['sources'][source_id]['sha256'] == decision['sourceSha256'][source_id] for source_id in decision['sourceIds']), partition
    for source in imports:
        if source['retainCompiledPartition']:
            before = old_employers.get(source['employerSlug'], {}).get('compiledYearCounts', {}).get(source['year'], 0)
            assert compiled_partitions.get((source['employerSlug'], source['year']), 0) == before, source['sourceId']
    tasks, task_hashes = [], {}
    for area in AREAS:
        path = OUT / area / 'work-queue.json'
        task_hashes[area] = digest(path.read_bytes())
        for task in read(path):
            assert all(key in task for key in FIELDS) and isinstance(task['reportingPeriods'], list), (area, task.get('id'))
            assert task['route'] in ROUTES and task['reason'] and task['nextAction'], task['id']
            tasks.append({**{key: task[key] for key in FIELDS}, 'researchArea': area, 'requestStatus': 'not-sent'})
    assert len({t['id'] for t in tasks}) == len(tasks), 'Repeated work-queue ID'
    tasks.sort(key=lambda t: (t['sector'], t['employerName'], t['route'], t['id']))
    requests = [t for t in tasks if t['route'] in {'ordinary-records-request', 'clarification-request', 'foi-fallback'}]
    registered_count = sum(sum(bool(s.get('file')) and s.get('status', 'verified') in ACCEPTED for s in read(RESEARCH / name / 'sources.json').get('sources', [])) for name in registry)
    collection_summary = [dict(collection=name, cohorts=sum(s['collection'] == name for s in imports), rows=sum(s['rows'] for s in imports if s['collection'] == name), originalReports=len({s['sourceSha256'] for s in imports if s['collection'] == name})) for name in collections]
    result = dict(version=1, asOf='2026-11-01', timezone='America/Vancouver', baselineCommit=baseline['repositoryCommit'], baseline=baseline['overall'], proposed=dict(records=total, officialRecords=official, compiledRecords=retained_count, employerEntries=len(current_employers), acceptedSourceFiles=registered_count), officialRowsAdded=added, compiledRowsReplaced=replaced, netRowsAdded=added-replaced, originalReports=len({s['sourceSha256'] for s in imports + aggregates}), employerYears=len({(s['employerSlug'], s['year']) for s in imports + aggregates}), periods=sorted({s['year'] for s in imports}), unnamedRowsAdded=sum(s['unnamedRows'] for s in imports), countsByScope=dict(Counter({scope: sum(s['rows'] for s in imports if s['scope'] == scope) for scope in sorted({s['scope'] for s in imports})})), collections=collection_summary, imports=imports, aggregateOnlySources=aggregates, compiledPartitionsReplaced=removed, sectorCoverageBefore={k: dict(v) for k, v in old_by_sector.items()}, sectorCoverageAfter={k: dict(v) for k, v in current_by_sector.items()}, employers=current_employers, municipalCoverageBefore=baseline['municipalSummary'], municipalCoverageAfter=municipal['summary'], tasks=len(tasks), requestCandidates=len(requests), taskCountsByRoute=dict(Counter(t['route'] for t in tasks)), taskInputSha256=task_hashes)
    save('release.json', result)
    save('work-queue.json', dict(version=1, policy='Draft work only; no outreach or fees. Located documents are leads until accepted, and old pass queues may overlap.', tasks=tasks))
    save('acquisition-list.json', dict(version=1, requestStatus='not-sent', candidates=requests))
    for filename, entries in [('work-queue.csv', tasks), ('acquisition-list.csv', requests)]:
        with (OUT / filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS + ['researchArea', 'requestStatus'], lineterminator='\n')
            writer.writeheader()
            for task in entries:
                writer.writerow({key: '; '.join(task[key]) if key == 'reportingPeriods' else task[key] for key in writer.fieldnames})
    lines = ['# Salary source continuation — 1 November 2026', '', f"This pass accepts **{added:,} official observations** from **{result['originalReports']} original reports**, covering **{result['employerYears']} employer-years**. After **{replaced:,} reviewed compiled replacements**, the dataset grows from **{baseline['overall']['records']:,} to {total:,}** (**{added-replaced:,} net records**).", '', '## Collections', '', '| Collection | Official observations | Accepted cohorts | Original reports |', '| --- | ---: | ---: | ---: |']
    for row in collection_summary:
        lines.append(f"| [{md(row['collection'])}](../{row['collection']}/README.md) | {row['rows']:,} | {row['cohorts']} | {row['originalReports']} |")
    lines += ['', '## Coverage', '', '| Sector | Records before | Records after | Official records after | Employers after |', '| --- | ---: | ---: | ---: | ---: |']
    for sector, values in sorted(current_by_sector.items()):
        lines.append(f"| {md(sector)} | {old_by_sector[sector]['records']:,} | {values['records']:,} | {values['officialRecords']:,} | {values['employerEntries']} |")
    lines += ['', f"Official municipal coverage is **{municipal['summary']['withOfficialRecordsAfter']} of 161 current jurisdictions**, including **{municipal['summary']['withOfficialEmployeeRecords']}** with employees; **{municipal['summary']['withNoOfficialRecords']}** still lack accepted official records. Regional districts are outside this municipal denominator. shíshálh is a separate governance case; Okanagan Falls remains pending incorporation on 6 November 2026.", '', '## Source scope and replacement decisions', '', 'These are published payments, not complete employee rosters or annual base salary rates. Actual schedule headings determine periods; upload dates and index labels do not. Employee, council/trustee, board and executive-only scopes remain distinct. Monetary columns follow each original definition: expense-inclusive totals are not pay, unknown cells remain null, and disclosed zeros/negative recoveries are preserved. Non-person recipients and aggregate payroll are not turned into individual employees.', '', 'Native cohorts compare independently implemented readers row by row. Scanned and hybrid cohorts retain manual original-image transcription and OCR corroboration, with separate peer review. Receipts distinguish full machine agreement from the actual rendered rows and pages visually checked. Material issuer-control disagreements retain exact visible warnings and clarification tasks. No value is adjusted to force a subtotal match, and no numerical coincidence is asserted to explain a residual.', '', 'Partial or narrower originals cannot silently erase broader compiled data. Explicitly retained partitions require a public scope warning and a pinned validation reason, with consistent employee completeness flags. Retained official/compiled observations may overlap; grouping names in the interface does not prove identity or authorize deletion. [Reviewed replacements and retained overlaps](replacement-review.md) has a separate reviewed source/scope decision.', '', '## Important source findings', '',
        '- Provincial histories extend to fiscal 1999/00. Employee and OIC/appointee schedules stay separate; negative salary recoveries and source-control conflicts remain literal and visible. Later salary-only schedules have unknown travel, not zero.',
        '- ICBC 2016/17 is a 15-month transition, January 2016–March 2017, rather than an ordinary 12-month year. Receiver General payments are excluded as non-person recipients; unknown receiver expense cells do not establish an employee-only expense comparator.',
        '- School SD8 fiscal 2018/19 is a complete hybrid schedule of 209 employees: 169 native rows plus 40 manually reviewed scanned rows. Its fiscal 2025/26 employee schedule remains held because one page says 2025 while others say 2026; no typo is assumed.',
        '- Camosun excludes board-member employees and severance from its employee table. Seven unresolved compiled partitions remain alongside official sources, including Museum 2023/24 where the best salary match is an older fiscal original. No guessed fiscal-period correction is made.',
        '- Health additions are board records, not new employee schedules. PHSA employee OCR and VCH/Providence original retrieval remain unresolved. The BCCSS amalgamation evidence prevents creating false standalone employee gaps after its transfer to PHSA.',
        '- TRU 2024/25 is an official published original with an unsigned/undated approval form. That limitation is explicit; no signed or adopted original is claimed. Exact source-control qualifications and copy/clarification tasks remain available.',
        '', '## Employer histories added', '', '| Employer | Newly accepted periods | Added observations |', '| --- | --- | ---: |']
    for slug in sorted({s['employerSlug'] for s in imports}):
        accepted = [s for s in imports if s['employerSlug'] == slug]
        lines.append(f"| {md(accepted[0]['employerName'])} | {', '.join(sorted({s['year'] for s in accepted}))} | {sum(s['rows'] for s in accepted):,} |")
    lines += ['', '## Research and next actions', '']
    lines += [f'- [{area} inventory, findings and verification]({area}/README.md)' for area in AREAS]
    lines += [f'- [Independent {path.stem.replace("-", " ")} review](reviews/{path.name})' for path in sorted((OUT / 'reviews').glob('*.md'))]
    lines += ['', f"The [remaining queue](work-queue.csv) has **{len(tasks)} tasks**; the [copy and clarification list](acquisition-list.md) contains **{len(requests)} draft candidates**. Old pass lists may overlap and their totals must not be added. Source discovery is not a claim that every historical report has been found. Each sector inventory records accepted, located, held and unsuccessful retrievals separately.", '', 'No institution or municipality was contacted. No FOI request was submitted and no fee incurred. Public archives and ordinary access to existing adopted reports or native tables come before formal access fallback. Existing public scans requiring extraction are processing tasks.', '', '## Reproduce', '', 'Use collection guides for original-backed reproduction and offline evidence replay. Publication checks:', '', '```sh', 'node --test scripts/salary-data.test.mjs src/salaries/*.test.js src/government/salaries.test.js', 'npm run compare:municipal-periods', 'npm run build:salaries', 'npm run check:salaries', 'npm run audit:municipal-salaries', 'npm run follow-up:municipal-salaries', 'npm run review:sector-salaries', 'npm run review:municipal-wave', 'npm run review:municipal-history', 'npm run review:salary-continuation', 'npm run preview:salaries -- --build', '```', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    lines = ['# Source copy and clarification candidates', '', 'Draft actions only. No institution was contacted, no FOI submitted and no fee incurred. Request an existing adopted report or native schedule routinely before formal access fallback; scans already available remain processing tasks.', '', '| Employer / periods | Route | Blocker | Next action |', '| --- | --- | --- | --- |']
    for task in requests:
        label = md(task['employerName']) + ' — ' + md(', '.join(task['reportingPeriods']) or 'period to establish')
        lines.append(f"| [{label}]({task['sourceUrl'] or task['sourceIndexUrl']}) | {md(task['route'])} | {md(task['reason'])} | {md(task['nextAction'])} |")
    lines += ['', '[CSV](acquisition-list.csv) · [JSON](acquisition-list.json) · [All processing and archive tasks](work-queue.csv)', '']
    (OUT / 'acquisition-list.md').write_text('\n'.join(lines))
    print(json.dumps({key: result[key] for key in ['officialRowsAdded', 'compiledRowsReplaced', 'netRowsAdded', 'originalReports', 'employerYears', 'tasks', 'requestCandidates']}))


if __name__ == '__main__':
    main()
