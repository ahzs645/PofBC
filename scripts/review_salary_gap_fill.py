#!/usr/bin/env python3
"""Verify the frozen65-lead expansion against its sources and previous app.

Offline release gate: no downloads, OCR runtimes, source caches or image tools.
The historical app is append-only. The sole same-scope supplement is the exact
eleven previously excluded Abbotsford known-component rows.
"""
from collections import Counter
import json
from pathlib import Path

from gap_fill_baseline import ROOT, AREA, read, sha, snapshot, verify_preserved, fingerprint
from gap_fill_previous_release import verify_registry_extension

BASELINE_SHA = 'fa35799b84e173aa7e61f9225935ec1936d744375107c14ccf709edeac937fa4'
OLD_ABBOTSFORD = 'wave-lower-mainland-city-of-abbotsford-2023-employee-remuneration'
NEW_ABBOTSFORD = 'gap-fill-municipal-city-of-abbotsford-2023-employee-remuneration'
ABBOTSFORD_SHA = '8cce0bc7013f866085cd7a301d406c2ce0438d2a6de5e20bf133b458c44db5ff'


def coalesce(value, fallback):
    return fallback if value is None else value


def metadata_equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(metadata_equal(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(metadata_equal(a, b) for a, b in zip(left, right))
    return left == right


def projected_metadata(source, directory, data_sha, retention=None):
    """The complete source object exported by build-salaries.mjs176–186.

    Use nullish defaults, preserving explicit zero and false. Keeping this
    projection independent of the builder catches altered app definitions.
    """
    year = str(source['year'])
    rule = '>=' if source.get('thresholdRule') == 'at-least' else '>' if source.get('thresholdRule') == 'over' else None
    fallback_title = f"{coalesce(source.get('employerName'), directory)} {year} {coalesce(source.get('category'), 'remuneration')}"
    metadata = {
        'id': source['id'], 'title': coalesce(source.get('title'), coalesce(source.get('sourceTitle'), fallback_title)),
        'url': coalesce(source.get('sourceUrl'), source.get('url')), 'year': year,
        'periodType': coalesce(source.get('periodType'), 'calendar' if len(year) == 4 else 'fiscal'),
        'sourceKind': coalesce(source.get('sourceKind'), 'official'),
        'periodStart': source.get('periodStart'), 'periodEnd': source.get('periodEnd'),
        'scope': coalesce(source.get('category'), source.get('scope')),
        'scopeDescription': coalesce(source.get('scopeDescription'), source.get('scope')),
        'threshold': source.get('threshold'), 'thresholdComparison': coalesce(source.get('thresholdComparison'), rule),
        'provenance': 'Official published schedule; independently downloaded and validated by the source importer.',
        'sha256': coalesce(source.get('sha256'), source.get('pdfSha256')), 'dataSha256': data_sha,
        'notes': coalesce(source.get('notes'), []), 'validation': source.get('validation'),
        'nameDisclosure': source.get('nameDisclosure'), 'positionDisclosure': source.get('positionDisclosure'),
        'travelSource': source.get('travelSource'), 'expensesNote': source.get('expensesNote'),
        'publicWarning': source.get('publicWarning'), 'currency': coalesce(source.get('currency'), 'CAD'),
    }
    if metadata['url'] is None:
        metadata.pop('url')  # JSON omits the builder's undefined url.
    if 'completeEmployeeSchedule' in source:
        metadata['completeEmployeeSchedule'] = source['completeEmployeeSchedule']
    if source.get('retainCompiledPartition') is True:
        metadata['retainCompiledPartition'] = True
    if retention is not None:
        validation = source.get('validation', {})
        if (retention.get('sourceId') != source['id'] or retention.get('sourceSha256') != metadata['sha256']
                or retention.get('dataSha256') != data_sha or retention.get('approvedBy') != 'root'
                or retention.get('retainCompiledPartition') is not True or not retention.get('reason')
                or type(source.get('completeEmployeeSchedule')) is not bool
                or retention.get('completeEmployeeSchedule') != source['completeEmployeeSchedule']
                or validation.get('compiledPartitionRetained') is not True
                or not validation.get('compiledPartitionRetentionReason') or not metadata['publicWarning']
                or validation.get('completeEmployeeSchedule') not in (None, source['completeEmployeeSchedule'])):
            raise ValueError('Compiled retention metadata adoption does not match exact source/scope')
        metadata['retainCompiledPartition'] = True
        metadata['validation'] = {**validation, 'completeEmployeeSchedule': source['completeEmployeeSchedule']}
    return metadata


def verify_metadata(source, actual, directory, data_sha, retention=None):
    if not metadata_equal(actual, projected_metadata(source, directory, data_sha, retention)):
        raise ValueError('App source definition differs from accepted source: ' + source['id'])


def pinned(ref, root=ROOT):
    path = (root / ref['path']).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Pinned file must exist within the repository')
    if sha(path.read_bytes()) != ref['sha256']:
        raise ValueError('Pinned evidence changed: ' + ref['path'])
    return read(path)


def collection_file(parent, relative, digest):
    path = (parent / relative).resolve()
    if not path.is_relative_to(parent.resolve()) or not path.is_file() or sha(path.read_bytes()) != digest:
        raise ValueError('Accepted collection file reference changed: ' + relative)
    return path


def freeze_entries(document):
    """Accept the two producer schemas without silently choosing between lists."""
    names = [key for key in ('files', 'inputs') if key in document]
    if len(names) != 1 or not isinstance(document[names[0]], list):
        raise ValueError('Exactly one producer frozen-input list is required')
    return document[names[0]]


def verify_supplement(source, rows, baseline, baseline_groups):
    """The only allowed extension of an already accepted official scope."""
    if source['id'] != NEW_ABBOTSFORD or source['sha256'] != ABBOTSFORD_SHA:
        raise ValueError('Unexpected same-scope supplement')
    if (source['employerSlug'], source['year'], source['scope']) != ('city-of-abbotsford', '2023', 'employee-remuneration'):
        raise ValueError('Supplement reporting scope changed')
    if source['completeEmployeeSchedule'] is not False or not source['validation'].get('partialCompensationDefinition'):
        raise ValueError('Known-component supplement must remain explicitly partial')
    old = baseline['sourceMetadata'][OLD_ABBOTSFORD]
    if old['sha256'] != source['sha256']:
        raise ValueError('Supplement original differs from prior source')
    held = old['validation']['heldRows']
    if len(held) != 11 or len(rows) != 11 or any(h['benefits'] is not None for h in held):
        raise ValueError('The exact eleven unknown-benefit observations are required')
    expected = [[h['name'], h['position'], h['knownRemunerationColumn'], h['expenses'], h['pdfPage']] for h in held]
    if fingerprint(rows) != fingerprint(expected):
        raise ValueError('Supplement differs from the exact eleven known source components')
    prior = baseline_groups[('city-of-abbotsford', '2023', OLD_ABBOTSFORD)]
    if len(prior) != 449 or {(r[0], r[4]) for r in prior} & {(r[0], r[4]) for r in rows}:
        raise ValueError('Supplement overlaps or replaces previously accepted observations')
    warning = source.get('publicWarning', '').lower()
    if not all(term in warning for term in ('partial', 'benefit', 'unknown')):
        raise ValueError('Partial compensation and unknown benefits must remain public')


def verify_novelty(sources, baseline, groups):
    prior_scopes = set()
    for slug, year, source_id in groups:
        old = baseline['sourceMetadata'].get(source_id)
        if old and old['sourceKind'].startswith('official'):
            prior_scopes.add((slug, year, old['scope']))
    new_scopes = set()
    for source, rows in sources:
        scope = (source['employerSlug'], source['year'], source['scope'])
        if scope in new_scopes:
            raise ValueError('Duplicate new official reporting scope: ' + repr(scope))
        new_scopes.add(scope)
        if scope in prior_scopes:
            verify_supplement(source, rows, baseline, groups)


def verify_dispositions(leads, ledger):
    expected = {r['id']: r for r in leads['records']}
    if len(expected) != 65 or len(ledger['records']) != 65:
        raise ValueError('All exact65original leads require a disposition')
    actual = {r['leadId']: r for r in ledger['records']}
    if len(actual) != 65 or set(actual) != set(expected):
        raise ValueError('Lead dispositions are missing or repeated')
    if ledger['noOutreach'] is not True or ledger['heldIssuerRequests'] != ['NIC', 'McBride', 'SD8', 'SD10']:
        raise ValueError('User-held requests or no-outreach direction changed')
    for lead_id, result in actual.items():
        if result['owner'] != expected[lead_id]['owner'] or not result.get('disposition'):
            raise ValueError('Lead ownership or substantive disposition missing')
        if result['remainingPublicProcessingTasks'] != 0:
            raise ValueError('A public processing task remains unfinished: ' + lead_id)
        if result.get('outreachSent') is not False:
            raise ValueError('Outreach was not authorized')


def verify():
    decision = read(AREA / 'parent-acceptance.json')
    if decision['accepted'] is not True or decision['noOutreach'] is not True:
        raise ValueError('Explicit final root acceptance is required')
    baseline_path = AREA / 'baseline.json.gzip'
    if sha(baseline_path.read_bytes()) != BASELINE_SHA:
        raise ValueError('Frozen baseline changed')
    baseline = read(baseline_path)
    freeze = pinned(decision['rootFreeze'])
    files = freeze['files']
    if len(files) != len({f['path'] for f in files}):
        raise ValueError('Repeated frozen input')
    for ref in files:
        # Images, gzipped native evidence and text are opaque pinned bytes.
        path = (ROOT / ref['path']).resolve()
        if not path.is_relative_to(ROOT) or sha(path.read_bytes()) != ref['sha256']:
            raise ValueError('Frozen root input changed: ' + ref['path'])
    archived = read(AREA / 'baseline-collections.json')
    verify_registry_extension(archived, read(ROOT / 'research/salaries/collections.json'), decision['collections'])
    for handoff in decision['workerHandoffs']:
        pinned(handoff)
    for producer in decision['producerFreezes']:
        frozen = pinned(producer)
        entries = freeze_entries(frozen)
        if len(entries) != len({e.get('path') or e['file'] for e in entries}):
            raise ValueError('Repeated producer frozen path')
        for entry in entries:
            relative = entry.get('path') or entry['file']
            path = (ROOT / relative).resolve()
            if not path.is_relative_to(ROOT) or sha(path.read_bytes()) != entry['sha256']:
                raise ValueError('Frozen producer evidence changed: ' + relative)
    for receipt in decision['peerReceipts']:
        pinned(receipt)
    retention_review = pinned(decision['compiledRetentionAdoptions'])
    if retention_review['accepted'] is not True or retention_review['noOutreach'] is not True:
        raise ValueError('Root compiled retention adoption is required')
    if retention_review['publishedCompiledBaseline'] != {'file': 'gap-fill-2026-11-02/baseline.json.gzip', 'sha256': BASELINE_SHA}:
        raise ValueError('Compiled preservation must use the exact prior published baseline')
    retentions = {r['sourceId']: r for r in retention_review['decisions']}
    if len(retentions) != len(retention_review['decisions']) or set(retentions) & set(baseline['sourceMetadata']):
        raise ValueError('Retention adoptions must target unique new sources only')
    leads = pinned(decision['inputLeads'])
    ledger = pinned(decision['leadDispositions'])
    verify_dispositions(leads, ledger)
    index, app_groups = snapshot()
    preserved = verify_preserved(baseline, index, app_groups)
    old_keys = {(g['employerSlug'], g['year'], g['sourceId']) for g in baseline['groups']}
    prior_groups = {key: rows for key, rows in app_groups.items() if key in old_keys}
    source_pairs = []
    imports = []
    for manifest_ref in decision['manifests']:
        manifest = pinned(manifest_ref)
        if manifest.get('reviewed') is False:
            raise ValueError('An unreviewed collection was registered')
        parent = (ROOT / manifest_ref['path']).parent
        for source in manifest['sources']:
            if source['id'] in baseline['sourceMetadata'] or not source['sourceKind'].startswith('official'):
                raise ValueError('New imports must have novel official source identifiers')
            if source.get('status') not in ('verified', 'accepted'):
                raise ValueError('A candidate source cannot be published: ' + source['id'])
            data_path = collection_file(parent, source['file'], source['dataSha256'])
            collection_file(parent, source['provenanceFile'], source['provenanceSha256'])
            for metadata in (source, source.get('validation', {})):
                if metadata.get('evidenceFile') is not None:
                    collection_file(parent, metadata['evidenceFile'], metadata['evidenceSha256'])
            values = read(data_path)
            if len(values) != source['rowCount'] or not values:
                raise ValueError('Empty or inconsistent salary cohort')
            if any(len(row) != 6 or row[0] != source['employerSlug'] for row in values):
                raise ValueError('Unexpected normalized source layout')
            expected = [row[1:] for row in values]
            key = (source['employerSlug'], source['year'], source['id'])
            actual = app_groups.get(key, [])
            if len(actual) != len(expected) or fingerprint(actual) != fingerprint(expected):
                raise ValueError('App observations differ from normalized original source: ' + source['id'])
            metadata = index['sources'].get(source['id'])
            verify_metadata(source, metadata, parent.name, sha(data_path.read_bytes()), retentions.get(source['id']))
            source_pairs.append((source, expected))
            imports.append({'sourceId': source['id'], 'employerSlug': source['employerSlug'],
                            'year': source['year'], 'scope': source['scope'], 'rows': len(expected),
                            'dataSha256': source['dataSha256'], 'sourceSha256': source['sha256'],
                            'rowMultisetSha256': fingerprint(expected)})
    if len({s['id'] for s, _ in source_pairs}) != len(source_pairs):
        raise ValueError('Repeated new source identifier')
    verify_novelty(source_pairs, baseline, prior_groups)
    new_ids = {s['id'] for s, _ in source_pairs}
    if set(retentions) != {s['id'] for s, _ in source_pairs if s.get('retainCompiledPartition') is not True}:
        raise ValueError('Every new source must explicitly preserve compiled scope, in its frozen metadata or a bounded root adoption')
    if set(index['sources']) != set(baseline['sourceMetadata']) | new_ids:
        raise ValueError('Unexpected app source outside the reviewed expansion')
    if set(app_groups) != old_keys | {(s['employerSlug'], s['year'], s['id']) for s, _ in source_pairs}:
        raise ValueError('Unexpected app observation group')
    added = sum(len(rows) for _, rows in source_pairs)
    counts = index['recordCounts']
    if counts['compiled'] != baseline['overall']['compiledRecords'] or counts['official'] != baseline['overall']['officialRecords'] + added:
        raise ValueError('Official/compiled reconciliation differs')
    release = {'schema': 'salary-additional65-release-v1', 'noOutreach': True,
               'before': baseline['overall'], 'proposed': {'records': preserved + added,
                   'officialRecords': counts['official'], 'compiledRecords': counts['compiled'], 'employers': len(index['employers'])},
               'leadsReviewed': 65, 'officialRowsAdded': added, 'compiledRowsRemoved': 0,
               'acceptedCohorts': len(imports), 'originalFiles': len({s['sourceSha256'] for s in imports}),
               'imports': imports, 'heldIssuerRequests': ledger['heldIssuerRequests']}
    if read(AREA / 'release.json') != release:
        raise ValueError('Committed release report differs from exact source/app reconciliation')
    return release


if __name__ == '__main__':
    result = verify()
    print(json.dumps({k: v for k, v in result.items() if k != 'imports'}))
