#!/usr/bin/env python3
"""Read-only verification of the 61-document salary source follow-through release.

Old employer rows (including anonymous observations) are checked against immutable
source/employer/period multisets. Every new normalized row is consumed exactly once
from the current employer exports. Name links are compared as labelled graphs.
"""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
AREA = 'research/salaries/source-follow-through-2026-11-02'
COLLECTIONS = ('follow-through-clbc', 'follow-through-cnc', 'follow-through-rru',
               'follow-through-langara', 'follow-through-small-crowns',
               'follow-through-translink', 'follow-through-worksafe-uvic')
PINS = {
    'baseline.json.gzip': '8f414198c5d2612972b071dd99ffd9ffdf37a2066f7eee24dfb0aa16cd8ec3ee',
    'baseline-row-groups.json.gzip': '2377f2220fdae030a2cf484dfce43091d16c484f4231d451c5705a409a01cb89',
    'baseline-live-links.json.gzip': 'c6b77c67224e1bbb554abb76b54b52e815e0861e888cca0081e30b9082a6f47c',
    'source-qualifications.json': '720c1e3bd87d24bfab5af9b812cdd4743e5cc9f5d97ac6b96e19a72e871f3322',
    'name-review-rru.json': 'b3e2b409ed0efe9f34a20497f8c951bb38033dd7e067ee7c52bd20e3f9c6bf04',
    'name-review-cnc.json': '416d65ab51729bcb303f8831caf21977ddfd438476adcf6b42a739ccfac2c4bf',
    'provided-source-backlog.json': '88f864e71d588308760ad9b20330d1b1b07d482a454db884e52ebcd3dc5b7c5a',
    'backlog-reconciliation.json': '8e530484dded211587c6c5cac9f013ef05a7ff593e7b69c4a406f79fa9ae57a9',
    'concurrent-main.json': '5fae15c739ecd783139bd2abc5a160871a42aba9a8b940d9e5565f5363de5c70',
}
EXPECTED_OLD_ROWS = 1385021
EXPECTED_COMPILED_ROWS = 228364
EXPECTED_NEW_ROWS = 55477
EXPECTED_NEW_SOURCES = 84
HELD_ID = 'follow-through-translink-2024-coast-mountain-bus-company-employees'
HELD_ROWS = 3896
ACCEPTED = {'accepted', 'verified', 'imported'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def serial(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def inside(root, relative):
    require(type(relative) is str and relative, 'Missing relative input path')
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()) and path != root.resolve(),
            'Input escapes its collection: ' + relative)
    return path


def strict_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(strict_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(strict_equal(a, b) for a, b in zip(left, right))
    return left == right


def json_equal(left, right):
    """JS exports encode an integral JSON number without a trailing .0."""
    if type(left) in (int, float) and type(right) in (int, float):
        return Decimal(str(left)) == Decimal(str(right))
    if type(left) is not type(right):return False
    if isinstance(left, dict):return left.keys() == right.keys() and all(json_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):return len(left) == len(right) and all(json_equal(a, b) for a, b in zip(left, right))
    return left == right


def cents(value):
    require(type(value) in (int, float), 'Money must be a finite JSON number')
    amount = Decimal(str(value)) * 100
    require(amount.is_finite() and amount == amount.to_integral_value(),
            'Money must preserve exact cents')
    return int(amount)


def observation(slug, year, name, position, pay, expenses, source, page):
    require(type(slug) is str and type(year) is str and type(source) is str,
            'Observation identifiers must be strings')
    require(name is None or type(name) is str and bool(name.strip()), 'Invalid disclosed name')
    require(position is None or type(position) is str, 'Invalid disclosed position')
    require(page is None or type(page) is int and page > 0, 'Invalid physical PDF page')
    return (slug, year, name, position, cents(pay),
            None if expenses is None else cents(expenses), source, page)


def row_hash(stable):
    """The immutable baseline contract uses original JSON money values, not cents."""
    return digest(serial(stable).encode())


def group_hash(row_hashes):
    # Sorting a list, rather than a set, preserves duplicate observations.
    return digest(serial(sorted(row_hashes)).encode())


def group_key(source, employer, year):
    require(all('|' not in s for s in (source, employer, year)), 'Ambiguous group identifier')
    return source + '|' + employer + '|' + year


def verify_old_groups(baseline, frozen, sources, hashes, compiled_rows):
    require(frozen.get('schemaVersion') == 1 and isinstance(frozen.get('groups'), dict),
            'Invalid baseline row-group schema')
    for source, definition in baseline['sourceDefinitions'].items():
        require(strict_equal(definition, sources.get(source)), 'Original source definition changed: ' + source)
    expected = frozen['groups']
    require(set(hashes) == set(expected), 'Original source/employer/period groups changed')
    count = 0
    for key, pin in expected.items():
        values = hashes[key]
        require(len(values) == pin['rows'] and group_hash(values) == pin['sha256'],
                'Original observations changed: ' + key)
        count += len(values)
    require(count == frozen['rows'] == baseline['originalRecords'], 'Original row accounting changed')
    require(compiled_rows == baseline['originalCompiledRecords'], 'Original compiled observations changed')
    return count


def row_metrics(rows):
    # Rows are canonical observations with exact integer-cent money fields.
    return {
        'rows': len(rows), 'payCents': sum(r[4] for r in rows),
        'knownExpenseCents': sum(r[5] for r in rows if r[5] is not None),
        'nullExpenses': sum(r[5] is None for r in rows),
        'zeroExpenses': sum(r[5] == 0 for r in rows),
        'anonymousRows': sum(r[2] is None for r in rows),
        'nullPositions': sum(r[3] is None for r in rows),
    }


def verify_source_rows(source, expected, actual):
    require(Counter(expected) == Counter(actual),
            'New source observations/multiplicity differ: ' + source['id'])
    metrics = row_metrics(expected)
    require(metrics['rows'] == source['rowCount'], 'New source row count changed: ' + source['id'])
    require(metrics['payCents'] == cents(source['totalRemuneration']),
            'New source remuneration total changed: ' + source['id'])
    expenses = source.get('totalExpenses', source.get('totalDisclosedExpenses'))
    require(expenses is not None and metrics['knownExpenseCents'] == cents(expenses),
            'New source expense total changed: ' + source['id'])
    if 'namedRowCount' in source:
        require(metrics['rows'] - metrics['anonymousRows'] == source['namedRowCount'],
                'New source named count changed: ' + source['id'])
    if 'anonymousRowCount' in source:
        require(metrics['anonymousRows'] == source['anonymousRowCount'],
                'New source anonymous count changed: ' + source['id'])
    return metrics


def verify_held_candidate(source, raw, live_source_ids):
    sid = source.get('id')
    require(sid == HELD_ID and source.get('status') == 'held-for-review'
            and source.get('candidateRowCount') == HELD_ROWS and not source.get('file')
            and bool(source.get('reason', '').strip()) and bool(source.get('nextAction', '').strip()),
            'Unexpected or incomplete held source')
    require(digest(raw) == source['dataSha256'], 'Held candidate hash changed')
    data = json.loads(gzip.decompress(raw));rows = data if isinstance(data, list) else data['rows']
    require(len(rows) == HELD_ROWS, 'Held candidate row count changed')
    require(sid not in live_source_ids, 'Held CMBC candidate source is published')


QUALIFICATION_FIELDS = ('id', 'url', 'year', 'periodType', 'periodStart', 'periodEnd',
                        'sourceKind', 'scope', 'scopeDescription', 'threshold', 'thresholdComparison',
                        'nameDisclosure', 'positionDisclosure', 'currency', 'completeEmployeeSchedule')


def qualification_metadata_fingerprint(source, employers):
    values = [source.get(field) for field in QUALIFICATION_FIELDS]
    # JSON.stringify writes an integral JavaScript Number without a .0 suffix.
    values = [int(value) if type(value) is float and value.is_integer() else value for value in values]
    return digest(serial([*values, sorted(employers)]).encode())


def normalized_qualification_metadata(source):
    def first(*values):
        return next((value for value in values if value is not None), None)
    year = first(source.get('year'), source.get('label'))
    comparison = '>=' if source.get('thresholdRule') == 'at-least' else '>' if source.get('thresholdRule') == 'over' else None
    return {
        'id': source['id'], 'url': first(source.get('sourceUrl'), source.get('url')),
        'year': year, 'periodType': first(source.get('periodType'), 'calendar' if re.fullmatch(r'\d{4}', year or '') else 'fiscal'),
        'periodStart': source.get('periodStart'), 'periodEnd': source.get('periodEnd'),
        'sourceKind': first(source.get('sourceKind'), 'official'),
        'scope': first(source.get('category'), source.get('scope')),
        'scopeDescription': first(source.get('scopeDescription'), source.get('scope')),
        'threshold': source.get('threshold'), 'thresholdComparison': first(source.get('thresholdComparison'), comparison),
        'nameDisclosure': source.get('nameDisclosure'), 'positionDisclosure': source.get('positionDisclosure'),
        'currency': first(source.get('currency'), 'CAD'), 'completeEmployeeSchedule': source.get('completeEmployeeSchedule'),
    }


def verify_qualification(source, current, decision):
    sid = source['id']
    require(decision.get('sourceId') == sid and decision.get('approvedBy') == 'root'
            and decision.get('sourceSha256') == source['sha256']
            and decision.get('dataSha256') == source['dataSha256']
            and decision.get('employerSlug') == source.get('employerSlug')
            and decision.get('completeEmployeeSchedule') is True
            and decision.get('retainCompiledPartition') is True
            and bool(decision.get('reason', '').strip()), 'Invalid/stale source qualification: ' + sid)
    require(current is not None, 'Accepted source absent from live index: ' + sid)
    employers = [source['employerSlug']]
    require(qualification_metadata_fingerprint(current, employers)
            == qualification_metadata_fingerprint(normalized_qualification_metadata(source), employers)
            == decision.get('metadataSha256'), 'Invalid/stale source qualification metadata fingerprint: ' + sid)
    expected = {
        'sha256': source['sha256'], 'dataSha256': source['dataSha256'],
        'year': source.get('year', source.get('label')), 'url': source['sourceUrl'],
        'scope': source.get('category', source.get('scope')),
        'periodStart': source.get('periodStart'), 'periodEnd': source.get('periodEnd'),
        'currency': source.get('currency', 'CAD'), 'completeEmployeeSchedule': True,
        'retainCompiledPartition': True,
        'publicWarning': ' '.join(x for x in (source.get('publicWarning'), decision['reason']) if x),
    }
    for field, value in expected.items():
        require(strict_equal(current.get(field), value), 'Qualified live source metadata changed: ' + sid + ' ' + field)
    validation = {**(source.get('validation') or {}), 'completeEmployeeSchedule': True,
                  'compiledPartitionRetained': True, 'compiledPartitionRetentionReason': decision['reason']}
    require(json_equal(current.get('validation'), validation), 'Qualified validation changed: ' + sid)
    require(current.get('sourceKind', '').startswith('official'), 'New source misclassified as compiled: ' + sid)


def expected_reports():
    fiscal = lambda label, years: {'additional-source-' + label + f'-{y}-{str(y+1)[-2:]}' for y in years}
    return {
        'follow-through-clbc': fiscal('clbc', range(2005, 2025)),
        'follow-through-cnc': fiscal('cnc', range(2018, 2025)),
        'follow-through-rru': fiscal('rru', range(2021, 2026)),
        'follow-through-langara': fiscal('langara', range(2022, 2025)),
        'follow-through-small-crowns': fiscal('bcfsa', range(2019, 2026)) | fiscal('bcib', range(2019, 2025)) | {'additional-source-pavco-2024-25'},
        'follow-through-translink': {'additional-source-translink-' + str(y) for y in range(2020, 2026)},
        'follow-through-worksafe-uvic': {'additional-source-worksafebc-' + str(y) for y in range(2023, 2026)} | fiscal('uvic', (2019, 2023, 2024)),
    }


def verify_dispositions(collection, payload, accepted, held):
    reports = payload.get('reports', payload.get('sources', payload.get('dispositions')))
    require(isinstance(reports, list), 'Missing document dispositions: ' + collection)
    identifiers = [r.get('id', r.get('leadId')) for r in reports]
    require(len(set(identifiers)) == len(identifiers)
            and set(identifiers) == expected_reports()[collection], 'Document dispositions changed: ' + collection)
    referenced = Counter()
    held_seen = 0
    for report in reports:
        report_id = report.get('id', report.get('leadId'))
        require(report.get('status') in {'accepted', 'imported', 'accepted-official', 'accepted-official-with-public-qualifications', 'partially-accepted'},
                'Document has no final accepted disposition: ' + report_id)
        cohorts = report.get('cohorts')
        if cohorts is None:
            sid = report.get('acceptedSourceId', report.get('sourceId'))
            require(sid in accepted, 'Disposition references an unaccepted source: ' + report_id)
            source = accepted[sid]
            count = report.get('employeeRows', report.get('rowCount'))
            require(count == source['rowCount'], 'Disposition row count changed: ' + report_id)
            original = report.get('originalSha256', report.get('pdfSha256', report.get('originalSourceSha256', report.get('sourceSha256'))))
            if original is not None:
                require(original == source['sha256'], 'Disposition original fingerprint changed: ' + report_id)
            referenced[sid] += 1
        else:
            accepted_count = accepted_rows = 0
            for cohort in cohorts:
                sid = cohort.get('sourceId')
                if cohort.get('status') == 'accepted':
                    require(sid in accepted, 'Disposition cohort is unaccepted: ' + str(sid))
                    source = accepted[sid]
                    require(cohort.get('rows') == source['rowCount']
                            and source['sha256'] == report.get('sha256')
                            and source['sourceUrl'] == report.get('sourceUrl'), 'Disposition cohort differs: ' + sid)
                    referenced[sid] += 1; accepted_count += 1; accepted_rows += source['rowCount']
                else:
                    require(sid == HELD_ID and cohort.get('status') == 'held-for-review'
                            and cohort.get('rows') == 0 and cohort.get('candidateRows') == HELD_ROWS
                            and bool(cohort.get('reason', '').strip()) and bool(cohort.get('nextAction', '').strip()),
                            'Held cohort lacks its concrete blocker: ' + str(sid))
                    require(sid in held, 'Held disposition has no candidate source')
                    held_seen += 1
            require(accepted_count == report.get('acceptedSources') and accepted_rows == report.get('acceptedRows'),
                    'Document accepted cohort accounting changed: ' + report_id)
    require(referenced == Counter({sid: 1 for sid in accepted}), 'Accepted sources lack unique document dispositions: ' + collection)
    require(held_seen == (1 if collection == 'follow-through-translink' else 0), 'Held cohort accounting changed')
    return len(reports)


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, node):
        self.parent.setdefault(node, node)
        root = node
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[node] != node:
            old = self.parent[node]; self.parent[node] = root; node = old
        return root

    def union(self, left, right):
        self.parent[self.find(left)] = self.find(right)

    def connected(self, left, right):
        return left in self.parent and right in self.parent and self.find(left) == self.find(right)


def verify_link_preservation(baseline_groups, live_groups):
    any_path, verified_path = UnionFind(), UnionFind()
    def unpack(group):
        require(isinstance(group, list) and len(group) == 4, 'Invalid packed name group')
        employer, key, name, aliases = group
        require(all(type(s) is str and s for s in (employer, key, name)) and isinstance(aliases, list),
                'Invalid packed name group identifiers')
        for alias in aliases:
            require(isinstance(alias, list) and len(alias) >= 4 and all(type(s) is str and s for s in alias[:2])
                    and alias[2] in ('verified', 'likely'), 'Invalid packed name relationship')
        return employer, key, aliases
    for group in live_groups:
        employer, key, aliases = unpack(group)
        primary = (employer, key)
        for alias in aliases:
            other = (employer, alias[0]); any_path.union(primary, other)
            if alias[2] == 'verified':verified_path.union(primary, other)
    relationships = verified = 0
    for group in baseline_groups:
        employer, key, aliases = unpack(group)
        for alias in aliases:
            left, right = (employer, key), (employer, alias[0])
            require(any_path.connected(left, right), 'Original grouped name relationship disappeared: ' + employer + ' ' + key + ' / ' + alias[0])
            if alias[2] == 'verified':
                require(verified_path.connected(left, right), 'Original verified name relationship was downgraded: ' + employer + ' ' + key + ' / ' + alias[0])
                verified += 1
            relationships += 1
    return {'preservedNameGroups': len(baseline_groups), 'preservedNameRelationships': relationships,
            'preservedVerifiedRelationships': verified}


def live_link_groups(root):
    groups, seen = [], set()
    folder = root / 'public/salaries/links'
    for path in sorted(folder.glob('*.json.gzip')):
        if path.name == 'top.json.gzip':continue
        payload = read(path)
        require(isinstance(payload.get('links'), list), 'Missing live name-link wrapper: ' + str(path))
        for group in payload['links']:
            key = serial(group)
            if key not in seen:groups.append(group);seen.add(key)
    require(groups, 'Live name-link exports are missing')
    return groups


def verify_employer_link_exports(root, groups, known_employers):
    expected = {slug: [] for slug in known_employers}
    require(len(expected) == len(known_employers) and all(
        re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) is not None for slug in expected),
        'Invalid/repeated indexed employer link export identifier')
    for group in groups:
        slug = group[0]
        require(slug in expected, 'Unknown employer in public name graph')
        if group[3]:expected[slug].append(group)
    folder = root / 'public/salaries/links/employers'
    require(folder.is_dir(), 'Employer link exports are missing')
    require({path.name for path in folder.iterdir()} == {slug + '.json.gzip' for slug in expected},
            'Employer link export inventory has missing/unknown files')
    reviewed_names = set()
    for path in (root / 'public/salaries/links').glob('*.json.gzip'):
        reviewed_names.update(read(path).get('reviewedNames', []))
    for slug, wanted in expected.items():
        payload = read(folder / (slug + '.json.gzip'))
        require(isinstance(payload.get('links'), list)
                and Counter(serial(group) for group in payload['links']) == Counter(serial(group) for group in wanted),
                'Employer link groups differ from the full public graph: ' + slug)
        wanted_reviewed = {slug + '|' + group[1] for group in wanted} & reviewed_names
        actual_reviewed = payload.get('reviewedNames', [])
        require(len(actual_reviewed) == len(set(actual_reviewed)) and set(actual_reviewed) == wanted_reviewed,
                'Employer reviewed-name markers differ from the public graph: ' + slug)
    return len(expected)


def verify_required_name_links(decisions, groups):
    expected = []
    for entry in decisions:
        proof = entry['proof']
        require(entry.get('decision') == 'verified' and entry.get('preferredName'), 'New name review must remain verified')
        expected.append([entry['employer'], proof['targetNameKey'], entry['preferredName'],
                         [[proof['aliasNameKey'], entry['names'][0], 'verified', 'Required individually reviewed source-copy bridge']]])
    try:
        verify_link_preservation(expected, groups)
    except ValueError as error:
        raise ValueError('Required new verified source-copy output is absent or downgraded: ' + str(error)) from error
    return len(expected)


NAME_REVIEW_NODE = r'''
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {validateFollowThroughNameReview} from './scripts/lib/follow-through-name-connections.mjs';
const area='research/salaries/source-follow-through-2026-11-02/';
const payloads=['name-review-rru.json','name-review-cnc.json'].map(f=>JSON.parse(readFileSync(area+f)));
const index=JSON.parse(readFileSync('public/salaries/people/index.json'));
const wanted=new Set(payloads.flatMap(p=>p.decisions.map(d=>d.employer)));
const rows=[];
for(const shard of Object.keys(index.shards)) {
  const part=JSON.parse(gunzipSync(readFileSync('public/salaries/people/'+shard+'.json.gzip')));
  for(const row of part) if(wanted.has(index.employers[row[4]][3])) rows.push(row);
}
const counts=payloads.map(p=>validateFollowThroughNameReview(p,rows,index,process.cwd()).length);
if(counts[0]!==12||counts[1]!==6) throw new Error('Required 12 RRU and 6 CNC reviewed decisions changed');
console.log(JSON.stringify({validatedNewNameDecisions:counts[0]+counts[1]}));
'''


def verify_new_name_receipts(root, inputs):
    decisions = []
    for name, count in [('name-review-rru.json', 12), ('name-review-cnc.json', 6)]:
        payload = inputs[name]
        require(payload.get('reviewer') == 'root' and len(payload.get('decisions', [])) == count,
                'New source-copy review count/authority changed: ' + name)
        decisions.extend(payload['decisions'])
    result = subprocess.run(['node', '--input-type=module', '-e', NAME_REVIEW_NODE], cwd=root,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    require(result.returncode == 0, 'Latest source-copy receipt validation failed:\n' + result.stderr[-6000:])
    require(json.loads(result.stdout).get('validatedNewNameDecisions') == 18, 'New source-copy validation coverage changed')
    return decisions


def verify_backlog_mapping(provided, reconciliation, backlog, resolve_ref, catalog):
    original = provided['sources']; decisions = reconciliation['dispositions']; live = backlog['sources']
    def keyed(rows, label):
        mapping = {row['id']: row for row in rows}
        require(len(mapping) == len(rows), 'Repeated backlog identifier: ' + label)
        return mapping
    old, planned, current = keyed(original, 'provided'), keyed(decisions, 'reconciled'), keyed(live, 'live')
    require(set(old) == set(planned) == set(current), 'Backlog identifier set differs from provided evidence')
    accepted_ids = []; accepted_rows = 0; counts = Counter(); stale = 0
    cohort_fields = ('sourceId', 'manifest', 'file', 'rowCount', 'dataSha256', 'sourceSha256',
                     'employerSlug', 'year', 'periodStart', 'periodEnd')
    for identifier, decision in planned.items():
        entry = current[identifier]; status = decision['recommendedBacklogStatus']
        require(entry.get('status') == status, 'Backlog status is stale: ' + identifier)
        require(entry.get('employeeScopeComplete') is decision['employeeScopeComplete'], 'Backlog completeness changed: ' + identifier)
        refs = decision['currentAcceptedEmployeeCohorts']; ids = [ref['sourceId'] for ref in refs]
        require(HELD_ID not in ids and len(ids) == len(set(ids)), 'Held/repeated source in imported backlog pointers')
        require(entry.get('acceptedSourceIds') == ids, 'Backlog accepted source pointers changed: ' + identifier)
        manifests = entry.get('acceptedManifests', [])
        require(len(manifests) == len(set(manifests)) and set(manifests) == {ref['manifest'] for ref in refs},
                'Backlog accepted manifest pointers changed: ' + identifier)
        if entry.get('acceptedSourceId') is not None:
            require(entry['acceptedSourceId'] in ids, 'Stale singular accepted source pointer: ' + identifier)
        if entry.get('acceptedManifest') is not None:
            require(entry['acceptedManifest'] in manifests, 'Stale singular accepted manifest pointer: ' + identifier)
        total = sum(ref['rowCount'] for ref in refs)
        require(entry.get('acceptedRows') == decision['acceptedEmployeeRows'] == total, 'Backlog accepted rows changed: ' + identifier)
        packed_refs = [{k: ref.get(k) for k in cohort_fields} for ref in refs]
        require(entry.get('acceptedCohorts', []) == packed_refs, 'Backlog cohort provenance changed: ' + identifier)
        require(json_equal(entry.get('heldCohorts', []), decision['heldCohorts']), 'Backlog held cohort scope changed: ' + identifier)
        if status == 'imported':
            require(refs and decision['employeeScopeComplete'] is True and not decision['heldCohorts'], 'Imported backlog entry is incomplete')
            counts['imported'] += 1
        elif status == 'partially-imported':
            require(identifier == 'additional-source-translink-2024' and refs
                    and decision['employeeScopeComplete'] is False and len(decision['heldCohorts']) == 1
                    and decision['heldCohorts'][0]['sourceId'] == HELD_ID, 'Partial TransLink scope changed')
            counts['partial'] += 1
        else:
            require(not refs and not total and decision['blockers'] and bool(entry.get('nextAction', '').strip()),
                    'Open backlog entry lacks its concrete blocker')
            counts['open'] += 1
        for ref in refs:
            resolve_ref(ref)
            matches = [lead for lead in catalog if lead.get('acceptedSourceId') == ref['sourceId']
                       and lead.get('employerSlug') == ref['employerSlug'] and lead.get('year') == ref['year']
                       and lead.get('status') == 'imported' and lead.get('rows') == ref['rowCount']]
            require(matches, 'Published source catalog lacks accepted backlog cohort: ' + ref['sourceId'])
        if decision.get('group') == 'original73' and decision.get('providedPendingStatusIsStale'):
            stale += 1
            for lead in catalog:
                for ref in refs:
                    same = lead.get('employerSlug') == ref['employerSlug'] and lead.get('year') == ref['year']
                    same = same and (lead.get('url') == ref.get('sourceUrl') or lead.get('id') == identifier)
                    require(not (same and lead.get('scope') in (None, 'employee-remuneration') and lead.get('status') != 'imported'),
                            'Published source catalog retains a stale held employee lead: ' + identifier)
        accepted_ids.extend(ids); accepted_rows += total
    require(len(accepted_ids) == len(set(accepted_ids)), 'Backlog repeats an accepted employee cohort across documents')
    held_catalog = [lead for lead in catalog if lead.get('id') == HELD_ID]
    require(len(held_catalog) == 1 and held_catalog[0].get('status') == 'held-for-review'
            and not held_catalog[0].get('acceptedSourceId') and held_catalog[0].get('rows', 0) == 0,
            'Published source catalog imports or loses held CMBC')
    return {'backlogEntries': len(current), 'backlogImportedEntries': counts['imported'],
            'backlogPartialEntries': counts['partial'], 'backlogOpenEntries': counts['open'],
            'backlogAcceptedEmployeeCohorts': len(accepted_ids), 'backlogAcceptedEmployeeRows': accepted_rows,
            'staleOriginalPendingEntriesResolved': stale}


def verify_backlog(root, inputs, index, group_counts):
    reconciliation = inputs['backlog-reconciliation.json']
    require(reconciliation['providedInput'] == AREA + '/provided-source-backlog.json'
            and reconciliation['providedInputSha256'] == PINS['provided-source-backlog.json'], 'Reconciliation provided-input pin changed')
    manifests = {}
    def resolve_ref(ref):
        sid = ref['sourceId']; require(sid in index['sources'] and sid != HELD_ID, 'Unpublished/held backlog source reference')
        path = inside(root, ref['manifest'])
        if ref['manifest'] not in manifests:manifests[ref['manifest']] = read(path)
        found = [source for source in manifests[ref['manifest']]['sources'] if source['id'] == sid]
        require(len(found) == 1 and found[0].get('status', 'accepted') in ACCEPTED, 'Backlog manifest pointer does not resolve: ' + sid)
        source = found[0]; file = inside(path.parent, source['file']); raw = file.read_bytes()
        require(str(file.relative_to(root)) == ref['file'] and digest(raw) == ref['dataSha256']
                == (source.get('dataSha256') or source.get('normalizedSha256')) == index['sources'][sid]['dataSha256'],
                'Backlog payload pointer/hash changed: ' + sid)
        require(ref['sourceSha256'] == source.get('sha256', source.get('pdfSha256')) == index['sources'][sid]['sha256'],
                'Backlog original source fingerprint changed: ' + sid)
        data = json.loads(gzip.decompress(raw));rows = data if isinstance(data, list) else data['rows']
        require(len(rows) == source['rowCount'] == ref['rowCount']
                == group_counts[(sid, ref['employerSlug'], ref['year'])], 'Backlog accepted/live row count changed: ' + sid)
        require(source.get('year', source.get('label')) == ref['year']
                and source.get('periodStart') == ref['periodStart'] and source.get('periodEnd') == ref['periodEnd'],
                'Backlog reporting period changed: ' + sid)
    result = verify_backlog_mapping(inputs['provided-source-backlog.json'], reconciliation,
                                   read(root / 'research/salaries/source-backlog.json'), resolve_ref,
                                   read(root / 'public/salaries/coverage.json')['sourceCatalog'])
    require(result == {'backlogEntries': 134, 'backlogImportedEntries': 110, 'backlogPartialEntries': 1,
                       'backlogOpenEntries': 23, 'backlogAcceptedEmployeeCohorts': 134,
                       'backlogAcceptedEmployeeRows': 333100, 'staleOriginalPendingEntriesResolved': 20}, 'Reconciled backlog accounting changed')
    return result


def verify_currency(root, baseline, index):
    path = 'research/salaries/record-annotations.json'
    pins = [p for p in baseline['researchInputs'] if p['path'] == path]
    require(len(pins) == 1 and digest((root / path).read_bytes()) == pins[0]['sha256'], 'Original currency annotation receipt changed')
    annotations = read(root / path)
    require(strict_equal(annotations, read(root / 'public/salaries/record-annotations.json')), 'Published currency annotations are stale')
    usd = [a for a in annotations['annotations'] if a.get('id') == 'bci-pittman-2023-24-usd-total-compensation']
    require(len(usd) == 1 and usd[0].get('currency') == 'USD', 'Pittman USD treatment is missing')
    people = read(root / 'public/salaries/people/index.json')
    require(strict_equal(people['sources'], index['sources']) and people['years'] == index['years'], 'People index metadata is stale')
    top = read(root / 'public/salaries/people/top.json.gzip')
    require(top.get('comparisonCurrency') == 'CAD', 'People rankings lost their CAD comparison scope')
    def decoded(row):
        require(isinstance(row, list) and len(row) == 8, 'Invalid people ranking row')
        require(type(row[4]) is int and 0 <= row[4] < len(people['employers'])
                and type(row[5]) is int and 0 <= row[5] < len(people['years']), 'Stale people ranking indices')
        return observation(people['employers'][row[4]][3], people['years'][row[5]], *row[:4], row[6], row[7])
    annotated = {}
    for annotation in annotations['annotations']:
        r = annotation['record']
        key = observation(r['employer'], r['period'], r['name'], r['position'], r['pay'], r['expenses'], r['sourceId'], r['pdfPage'])
        annotated[key] = annotation['currency']
        exported = read(root / 'public/salaries/employers' / (r['employer'] + '.json.gzip'))
        count = sum(observation(r['employer'], index['years'][row[4]], *row[:4], row[5], row[6]) == key for row in exported)
        require(count == 1, 'Annotated original observation changed or duplicated')
    for row in top['rows']:
        key = decoded(row)
        require(annotated.get(key, index['sources'][row[6]].get('currency', 'CAD')) == 'CAD', 'Non-CAD observation leaked into CAD rankings')
    unranked = Counter(decoded(row) for row in top.get('unrankedRows', []))
    for key, currency in annotated.items():
        if currency != 'CAD':require(unranked[key] == 1, 'Non-CAD observation is missing from unranked top access')
    return len(annotated)


def verify_concurrent_main_review(root, baseline, capsule):
    relative = 'research/salaries/name-links/reviewed.json'
    pins = [pin for pin in baseline['researchInputs'] if pin['path'] == relative]
    require(len(pins) == 1 and capsule.get('schemaVersion') == 1
            and capsule.get('reviewedFile') == relative
            and re.fullmatch(r'[a-f0-9]{40}', capsule.get('mainCommit', '')) is not None
            and capsule.get('baselineReviewedFileSha256') == pins[0]['sha256'],
            'Concurrent main review capsule disagrees with the immutable baseline')
    archive = root / AREA / 'baseline-code.tar.gz'
    require(digest(archive.read_bytes()) == baseline['baselineCodeSha256'], 'Historical code archive changed')
    with tarfile.open(archive, 'r:gz') as stream:
        original = stream.extractfile(relative).read()
    require(digest(original) == pins[0]['sha256'], 'Archived original four manual decisions changed')
    old = json.loads(original)
    require(len(capsule.get('baselineDecisions', [])) == 4
            and strict_equal(old.get('decisions'), capsule['baselineDecisions']),
            'Concurrent capsule changed the original four manual decisions')
    additions = capsule.get('additionalDecisions', [])
    require(len(additions) == 1 and additions[0].get('decision') == 'verified'
            and additions[0].get('preferredName') in additions[0].get('names', []),
            'Concurrent capsule must approve exactly one explicit verified addition')
    raw = (root / relative).read_bytes()
    require(digest(raw) == capsule.get('reviewedFileSha256'), 'Concurrent manual review file differs from its exact approved capsule')
    require(strict_equal(json.loads(raw).get('decisions'), capsule['baselineDecisions'] + additions),
            'Manual review file changed old decisions or added an unapproved decision')
    return len(additions)


def verify_review_receipts(root, baseline, concurrent=None):
    counts = {'source-reviewed.json': 251, 'continuation-reviewed.json': 43,
              'held-completion-reviewed.json': 167, 'reviewed.json': None}
    preserved = 0
    for name, count in counts.items():
        relative = 'research/salaries/name-links/' + name
        pins = [p for p in baseline['researchInputs'] if p['path'] == relative]
        path = root / relative
        if name == 'reviewed.json' and concurrent is not None:
            verify_concurrent_main_review(root, baseline, concurrent)
            continue
        require(len(pins) == 1 and digest(path.read_bytes()) == pins[0]['sha256'],
                'Original name-review receipt changed: ' + name)
        if count is not None:
            require(len(read(path)['decisions']) == count, 'Original reviewed decision count changed: ' + name)
            preserved += count
    return preserved


def load_inputs(root):
    values = {}
    for name, expected in PINS.items():
        path = root / AREA / name
        require(digest(path.read_bytes()) == expected, 'Immutable follow-through input changed: ' + name)
        values[name] = read(path)
    baseline = values['baseline.json.gzip']
    require(baseline['originalRecords'] == EXPECTED_OLD_ROWS
            and baseline['originalCompiledRecords'] == EXPECTED_COMPILED_ROWS, 'Frozen baseline accounting changed')
    require(values['baseline-row-groups.json.gzip']['rows'] == EXPECTED_OLD_ROWS, 'Frozen anonymous-inclusive baseline changed')
    require(values['baseline-live-links.json.gzip']['count'] == len(values['baseline-live-links.json.gzip']['groups']) == 22598,
            'Frozen name graph accounting changed')
    archive = root / AREA / 'baseline-code.tar.gz'
    require(digest(archive.read_bytes()) == baseline['baselineCodeSha256'], 'Historical code archive changed')
    with tarfile.open(archive, 'r:gz') as stream:
        registry_bytes = stream.extractfile('research/salaries/collections.json').read()
    registry_pin = next(p for p in baseline['researchInputs'] if p['path'] == 'research/salaries/collections.json')
    require(digest(registry_bytes) == registry_pin['sha256'], 'Archived collection registry changed')
    old_registry = json.loads(registry_bytes)
    require(read(root / 'research/salaries/collections.json') == {**old_registry, 'collections': old_registry['collections'] + list(COLLECTIONS)},
            'Live registry is not the exact seven-collection extension')
    return values


def verify(root=ROOT, check_graph=True):
    root = Path(root).resolve(); inputs = load_inputs(root)
    baseline, frozen = inputs['baseline.json.gzip'], inputs['baseline-row-groups.json.gzip']
    qualifications = inputs['source-qualifications.json']
    require(qualifications.get('accepted') is True and qualifications.get('noOutreach') is True, 'Source qualifications are not accepted')
    decisions = qualifications['decisions']
    qualified = {d['sourceId']: d for d in decisions}
    require(len(qualified) == len(decisions) == EXPECTED_NEW_SOURCES, 'New qualification coverage changed')
    index = read(root / 'public/salaries/employers/index.json')
    sources, expected_rows, source_collections, held = {}, {}, {}, {}
    document_count = 0
    for collection in COLLECTIONS:
        folder = root / 'research/salaries' / collection
        manifest = read(folder / 'sources.json'); local = {}
        for source in manifest.get('sources', []):
            sid = source.get('id')
            require(sid and sid not in sources and sid not in baseline['sourceDefinitions'], 'Repeated/pre-existing new source identifier')
            require(source.get('status') in ACCEPTED and source.get('completeEmployeeSchedule') is True
                    and source.get('category') == 'employee-remuneration' and 'file' in source, 'Unaccepted employee source in manifest: ' + sid)
            file = inside(folder, source['file']); raw = file.read_bytes()
            require(digest(raw) == source.get('dataSha256'), 'Normalized source file hash changed: ' + sid)
            data = json.loads(gzip.decompress(raw)); rows = data if isinstance(data, list) else data['rows']
            require(rows and all(isinstance(r, list) and len(r) == 6 for r in rows), 'Malformed normalized employee payload: ' + sid)
            allowed = {source['employerSlug']}
            values = []
            for slug, name, position, pay, expenses, page in rows:
                require(slug in allowed, 'Unexpected employer in normalized source: ' + sid)
                # New source slugs already identify their disclosed legal employers.
                # A mutable live alias table must not reassign an accepted cohort.
                values.append(observation(slug, source['year'], name, position, pay, expenses, sid, page))
            require(sid in qualified, 'New source has no immutable qualification: ' + sid)
            verify_qualification(source, index['sources'].get(sid), qualified[sid])
            verify_source_rows(source, values, values)
            sources[sid] = source; local[sid] = source; expected_rows[sid] = values; source_collections[sid] = collection
        local_held = {}
        for source in manifest.get('unparsedSources', []):
            sid = source.get('id')
            require(sid not in held, 'Repeated held source')
            file = inside(folder, source['candidateFile']);raw = file.read_bytes()
            verify_held_candidate(source, raw, index['sources'])
            held[sid] = source; local_held[sid] = source
        document_count += verify_dispositions(collection, read(folder / 'dispositions.json'), local, local_held)
    require(len(sources) == EXPECTED_NEW_SOURCES and set(sources) == set(qualified), 'Accepted source/qualification coverage differs')
    require(document_count == 61 and set(held) == {HELD_ID}, 'Final document/held dispositions changed')
    require(sum(len(r) for r in expected_rows.values()) == EXPECTED_NEW_ROWS, 'Accepted employee total changed')
    require(set(index['sources']) == set(baseline['sourceDefinitions']) | set(sources), 'Live index contains missing or unreviewed source IDs')
    old_hashes, actual_rows = defaultdict(list), defaultdict(list)
    group_counts = Counter()
    total = compiled = official = anonymous = 0
    slugs = [e['slug'] for e in index['employers']]
    require(len(slugs) == len(set(slugs)), 'Repeated employer export identifier')
    employer_files = {p.name for p in (root / 'public/salaries/employers').glob('*.json.gzip')}
    require(employer_files == {slug + '.json.gzip' for slug in slugs}, 'Unindexed/missing employer export files')
    for employer in index['employers']:
        slug = employer['slug']
        require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) is not None, 'Invalid employer export path')
        rows = read(root / 'public/salaries/employers' / (slug + '.json.gzip'))
        require(isinstance(rows, list) and len(rows) == sum(employer['counts']), 'Employer export row count changed: ' + slug)
        year_counts = Counter()
        for row in rows:
            require(isinstance(row, list) and len(row) == 7, 'Malformed employer export row')
            name, position, pay, expenses, year_at, sid, page = row
            require(type(year_at) is int and 0 <= year_at < len(index['years']), 'Invalid employer year index')
            require(sid in index['sources'] and sid != HELD_ID, 'Unknown/held observation published')
            year = index['years'][year_at]; stable = [slug, year, name, position, pay, expenses, sid, page]
            group_counts[(sid, slug, year)] += 1
            obs = observation(*stable)
            year_counts[year_at] += 1; total += 1; anonymous += name is None
            definition = index['sources'][sid]
            is_compiled = definition.get('sourceKind') == 'compiled' or definition.get('scope') == 'compiled-unverified'
            compiled += is_compiled; official += not is_compiled
            if sid in baseline['sourceDefinitions']:old_hashes[group_key(sid, slug, year)].append(row_hash(stable))
            else:actual_rows[sid].append(obs)
        require(all(year_counts[i] == count for i, count in enumerate(employer['counts'])), 'Employer period count changed: ' + slug)
    preserved = verify_old_groups(baseline, frozen, index['sources'], old_hashes, compiled)
    require(total == EXPECTED_OLD_ROWS + EXPECTED_NEW_ROWS and compiled == EXPECTED_COMPILED_ROWS
            and official == baseline['originalOfficialRecords'] + EXPECTED_NEW_ROWS, 'Live append-only row accounting changed')
    require(index['recordCounts'].get('compiled') == compiled and index['recordCounts'].get('official') == official,
            'Live index row totals are stale')
    financial = {}
    for sid, source in sources.items():
        financial[sid] = {'collection': source_collections[sid], 'sourceSha256': source['sha256'],
                          'dataSha256': source['dataSha256'], 'employerSlug': source['employerSlug'],
                          'year': source['year'], **verify_source_rows(source, expected_rows[sid], actual_rows[sid])}
    require(set(actual_rows) == set(sources), 'Published new source set differs from accepted manifests')
    annotation_count = verify_currency(root, baseline, index)
    review_count = verify_review_receipts(root, baseline, inputs['concurrent-main.json'])
    result = {'schemaVersion': 1, 'checkedOn': '2026-11-02', 'accepted': True, 'noOutreach': True,
              'immutableInputSha256': PINS, 'acceptedDocuments': document_count, 'acceptedEmployeeSources': len(sources), 'acceptedEmployeeRows': EXPECTED_NEW_ROWS,
              'heldEmployeeSources': len(held), 'heldCandidateRowsExcluded': HELD_ROWS, 'preservedOriginalRows': preserved,
              'preservedCompiledRows': compiled, 'currentRows': total, 'currentOfficialRows': official,
              'currentAnonymousRows': anonymous, 'preservedCurrencyAnnotations': annotation_count,
              'preservedPinnedNameDecisions': review_count, 'sourceChecks': financial}
    result.update(verify_backlog(root, inputs, index, group_counts))
    if check_graph:
        groups = live_link_groups(root)
        result.update(verify_link_preservation(inputs['baseline-live-links.json.gzip']['groups'], groups))
        result['verifiedEmployerLinkExports'] = verify_employer_link_exports(root, groups, slugs)
        new_decisions = verify_new_name_receipts(root, inputs)
        result['validatedNewNameDecisions'] = verify_required_name_links(new_decisions, groups)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true', help='Write release-validation.json only after all checks pass')
    args = parser.parse_args()
    result = verify(args.root)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.write:
        (args.root.resolve() / AREA / 'release-validation.json').write_text(text)
    print(text, end='')


if __name__ == '__main__':main()
