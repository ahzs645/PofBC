#!/usr/bin/env python3
"""Verify the additive consolidation against a frozen main snapshot, without git."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
import re
import unicodedata
from pathlib import Path
from check_salary_source_follow_through import (
    digest, serial, read, require, observation, group_key, group_hash, row_hash,
    strict_equal, inside, live_link_groups, verify_link_preservation,
    verify_employer_link_exports, verify_currency, verify_review_receipts,
    verify_source_rows, cents,
)

ROOT = Path(__file__).resolve().parents[1]
AREA = 'research/salaries/current-preservation-2026-11-06'
BASELINE_COMMIT = '7399fde18d2b278f5e99e2e201b915adadc7a8e2'
BASELINE_SHA256 = '366a80456756afe15de203665b5d29da70dda4041410b159b6df085da917ec62'
NEW_COLLECTIONS = {'provincial-elected': 2428, 'assembly-staff-recovery': 743, 'vpd-recovery': 1237, 'provincial-early-administration': 552}
ACCEPTED_INPUT_SHA256 = {'research/salaries/provincial-elected/sources.json': 'ebc325f240edfddd6732423501884911962a3c746fc2583b95629d4f12aba3ec', 'research/salaries/assembly-staff-recovery/sources.json': '0d512ff2a78c49b4c19c841b82b14c0458a9cca36b0c822cbe7d0f500a60f26e', 'research/salaries/vpd-recovery/sources.json': '8eac2b3ed8aa4aad9c76a9a532bc71701ccd1b9b96d71794da26dfad860f41ab', 'research/salaries/west-vancouver-title-recovery/corrections.json': '2ae723956f953e2be537254847df9cb3ba5e1d3482c5bbebec69f3392f1f0bf0'}
ACCEPTED_INPUT_SHA256['research/salaries/provincial-early-administration/sources.json'] = '1c1a1e373b13cc9f8abb48eceec37ff401ca7707d158106464a0207469408ddc'
ACCEPTED_INPUT_SHA256[AREA + '/confidence-withdrawals.json'] = '7db8ddd97f8a304e8a6dd3aa976d9593b108f1d7348239e529dbd874ae453551'
ACCEPTED_INPUT_SHA256.update({'research/salaries/provincial-early-administration/1999-00.audit.json': '73f03d6ef7cd34ca18a8555b8c8ae52e9c10c2f97f4a3aaae10e219ad50c7035', 'research/salaries/provincial-early-administration/2000-01.audit.json': 'fe65ffab5633d5e8e5475d194157a6e15cde647f1936bd8c6c3887f543a602b0', 'research/salaries/provincial-early-administration/2001-02.audit.json': '78c764eb71b72a2486268f0c76d650a5449772ab7c96c6584078c7074ef8b9b5', 'research/salaries/provincial-early-administration/2002-03.audit.json': 'a7d20153746ff14418e3d33ea92d2ddbcde65ba52b0e32aeb79ee21b072e6992', 'research/salaries/provincial-early-administration/2003-04.audit.json': 'e57488a949db6f59cde81522558050e2d0fe0b20209f69696a8941914c60ff5f', 'research/salaries/provincial-early-administration/2004-05.audit.json': '04743b803177b45f13d60fe67b02ea5f7e0bea91afbfc4509a6675961b93137b', 'research/salaries/provincial-early-administration/2005-06.audit.json': '9d263df60d542aaa0cbb9c4db1f6a7a4b61ea5457c4cec468945860d03a29c40', 'research/salaries/provincial-early-administration/overlap-check.json': '1ef9f2bdd527d5c42062010f428c271312d44f9d67e31710c7627a100c702140', 'research/salaries/provincial-early-administration/2003-04.independent-raw.txt': '07d3ce51c34c9538867b14693e2348d871b49129baff02e509b7fa04bdc85ef7'})
PRESERVED_CODE_SHA256 = {'scripts/check_salary_source_follow_through.py': 'd87ee7bfd951488af6924cc71ba028863fa1e0378933f16ad444dccbd6e58c6a', 'scripts/review_follow_through_names.py': '979c2de9075c538c6f050947d88201e93384c9d87ab87261ed13cfb348389252', 'scripts/check_salary_historical_releases.py': '376f9b22b797fe3ebdcb1d63483cafeb4d1914f62f8ba9b26623e8256a2fa50a', 'scripts/lib/repeat-name-connections.mjs': '982a243686c422f8f93a9f2d0315b894f9a6df41072a8ed044045b4fc56f9750'}
MUTABLE_INPUTS = {'research/salaries/name-links/decisions.csv', 'research/salaries/name-links/summary.json', 'research/salaries/README.md', 'research/salaries/collections.json', 'research/salaries/coverage-inventory.md', 'research/salaries/source-inventory.md'}


def original_rows(root, index):
    slugs = [e['slug'] for e in index['employers']]
    require(len(slugs) == len(set(slugs)), 'Duplicate employer')
    files = {p.name for p in (root / 'public/salaries/employers').glob('*.json.gzip')}
    require(files == {slug + '.json.gzip' for slug in slugs}, 'Missing or unindexed employer file')
    for e in index['employers']:
        rows = read(inside(root / 'public/salaries/employers', e['slug'] + '.json.gzip'))
        counts = Counter()
        for row in rows:
            require(isinstance(row, list) and len(row) == 7, 'Malformed employer row')
            name, position, pay, expenses, year_at, sid, page = row
            require(type(year_at) is int and 0 <= year_at < len(index['years']), 'Invalid period index')
            require(sid in index['sources'], 'Unknown source')
            counts[year_at] += 1
            yield observation(e['slug'], index['years'][year_at], name, position, pay, expenses, sid, page)
        require(len(e['counts']) == len(index['years']) and all(counts[i] == n for i, n in enumerate(e['counts'])), 'Employer period counts disagree')


def row_groups(rows):
    hashes = defaultdict(list)
    for row in rows:
        hashes[group_key(row[6], row[0], row[1])].append(row_hash(row))
    return {k: {'rows': len(v), 'sha256': group_hash(v)} for k, v in sorted(hashes.items())}


def inverse_corrections(rows, corrections):
    require(len(corrections) == 1752, 'Wrong title correction count')
    mapping = {}
    for c in corrections:
        key = observation(c['employerSlug'], c['year'], c['name'], c['position'], c['remuneration'], c['expenses'], c['sourceId'], c['page'])
        require(key not in mapping, 'Ambiguous corrected observation')
        mapping[key] = observation(c['employerSlug'], c['year'], c['sourcePrefix'], None, c['remuneration'], c['expenses'], c['sourceId'], c['page'])
    affected = {c['sourceId'] for c in corrections}
    seen = set()
    for row in rows:
        if row[6] in affected:
            require(row in mapping and row not in seen, 'Unrecognized/repeated title correction')
            seen.add(row)
            yield mapping[row]
        else:
            yield row
    require(len(seen) == len(mapping), 'Missing title corrections')



def correction_link_context(groups, corrections):
    # Only exact audited text splits can rename an old graph endpoint. This
    # collapses the old name-plus-title alias into the same disclosed clean name;
    # it cannot create a relationship between different disclosed people.
    def key(name):
        def letters(value):
            return re.sub('[^a-z]', '', unicodedata.normalize('NFD', value).lower())
        surname, *given = name.split(',')
        return letters(surname) + '|' + ' '.join(filter(None, (letters(part) for part in re.split(r'[\s.]+', ' '.join(given).strip()))))
    mapping = {}
    for c in corrections:
        old, new = (c['employerSlug'], key(c['sourcePrefix'])), key(c['name'])
        require(old not in mapping or mapping[old] == new, 'Ambiguous audited name-key correction')
        mapping[old] = new
    transformed = []
    for employer, group_key, name, aliases in groups:
        transformed.append([employer, mapping.get((employer, group_key), group_key), name,
                            [[mapping.get((employer, alias[0]), alias[0]), *alias[1:]] for alias in aliases
                             if mapping.get((employer, alias[0]), alias[0]) != mapping.get((employer, group_key), group_key)]])
    return transformed



def apply_confidence_withdrawals(groups, live_groups, receipt, original_rows, current_rows):
    allowed = {('vancouver-police', 'palmer|a a', 'palmer|a'),
               ('district-of-west-vancouver', 'stuart|sharon', 'stuart|s')}
    decisions = receipt.get('decisions', [])
    require(receipt.get('scope') == 'exactly-two-automatic-confidence-withdrawals'
            and receipt.get('baselineCommit') == BASELINE_COMMIT
            and receipt.get('sourceBackedReceiptsChanged') is False
            and len(decisions) == 2
            and {(d['employer'], d['targetKey'], d['aliasKey']) for d in decisions} == allowed,
            'Unapproved confidence withdrawal scope')
    changed = json.loads(json.dumps(groups))
    for d in decisions:
        e, target, alias = d['employer'], d['targetKey'], d['aliasKey']
        require(d['previousStatus'] == 'verified' and d['currentStatus'] == 'likely'
                and d['basis'] == 'automatic-distinctive-position-heuristic-only', 'Invalid confidence transition')
        for rows, field in [(original_rows, 'originalEmployerObservations'), (current_rows, 'currentEmployerObservations')]:
            selected = [r for r in rows if r[0] == e]
            actual = {'rows': len(selected), 'sha256': group_hash([row_hash(r) for r in selected])}
            require(actual == d[field], 'Confidence withdrawal observation evidence changed: ' + e)
        old = [a for g in changed if g[0] == e and g[1] == target for a in g[3] if a[0] == alias]
        new = [a for g in live_groups if g[0] == e and g[1] == target for a in g[3] if a[0] == alias]
        require(old and len(new) == 1 and all(a[2:4] == [d['previousStatus'], d['previousReason']] for a in old)
                and new[0][2:4] == [d['currentStatus'], d['currentReason']], 'Confidence withdrawal graph evidence changed')
        for edge in old:edge[2] = 'likely'
    return changed


def freeze(snapshot, destination):
    """Maintainer-only: snapshot must be git archive of the stated baseline commit."""
    index = read(snapshot / 'public/salaries/employers/index.json')
    groups = row_groups(original_rows(snapshot, index))
    require(sum(g['rows'] for g in groups.values()) == 1440498, 'Wrong main baseline')
    pins = [{'path': str(p.relative_to(snapshot)), 'sha256': digest(p.read_bytes())}
            for p in sorted((snapshot / 'research/salaries').rglob('*'))
            if p.is_file() and str(p.relative_to(snapshot)) not in MUTABLE_INPUTS]
    manifest = {'schemaVersion': 1, 'baselineCommit': BASELINE_COMMIT,
                'originalRecords': 1440498, 'originalCompiledRecords': 228364,
                'sourceDefinitions': index['sources'], 'groups': groups,
                'researchInputs': pins, 'collections': read(snapshot / 'research/salaries/collections.json'),
                'nameGroups': live_link_groups(snapshot)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(gzip.compress((serial(manifest) + '\n').encode(), compresslevel=9, mtime=0))
    print('Frozen baseline SHA256:', digest(destination.read_bytes()), 'inputs:', len(pins))


def verify(root=ROOT):
    root = Path(root)
    raw = (root / AREA / 'baseline.json.gzip').read_bytes()
    require(digest(raw) == BASELINE_SHA256, 'Frozen current baseline changed')
    baseline = json.loads(gzip.decompress(raw))
    require(baseline['baselineCommit'] == BASELINE_COMMIT, 'Wrong baseline commit')
    for pin in baseline['researchInputs']:
        require(digest(inside(root, pin['path']).read_bytes()) == pin['sha256'], 'Original research input changed: ' + pin['path'])
    for path, pin in {**ACCEPTED_INPUT_SHA256, **PRESERVED_CODE_SHA256}.items():
        require(digest(inside(root, path).read_bytes()) == pin, 'Approved recovery evidence changed: ' + path)
    old_collections = baseline['collections']
    collections = read(root / 'research/salaries/collections.json')
    require({k:v for k,v in collections.items() if k != 'collections'} == {k:v for k,v in old_collections.items() if k != 'collections'}, 'Collection metadata changed')
    require(collections['collections'] == old_collections['collections'] + list(NEW_COLLECTIONS), 'Collection registration must append each approved collection exactly once')
    index = read(root / 'public/salaries/employers/index.json')
    for sid, definition in baseline['sourceDefinitions'].items():
        require(strict_equal(index['sources'].get(sid), definition), 'Original source definition changed: ' + sid)
    expected = {}; source_pins = {}
    for collection, count in NEW_COLLECTIONS.items():
        folder = root / 'research/salaries' / collection
        manifest = read(folder / 'sources.json')
        local_count = 0
        for source in manifest['sources']:
            sid = source['id']
            require(sid not in expected and sid not in baseline['sourceDefinitions'], 'Duplicate or original new source ID')
            require(source.get('status') in {'accepted', 'verified', 'imported'}, 'Unaccepted new source')
            data_raw = inside(folder, source['file']).read_bytes()
            require(digest(data_raw) == source['dataSha256'], 'New source data hash changed')
            require(digest(inside(folder, source['originalFile']).read_bytes()) == source['sha256'], 'New original source hash changed')
            payload = json.loads(gzip.decompress(data_raw))
            rows = payload if isinstance(payload, list) else payload['rows']
            values = []
            for r in rows:
                require(len(r) in (5, 6) and r[0] == source['employerSlug'], 'Invalid new normalized row')
                values.append(observation(r[0], source['year'], *r[1:5], sid, r[5] if len(r) == 6 else None))
            require(len(values) == source['rowCount'] and sum(r[4] for r in values) == cents(source['totalRemuneration']), 'New source count or remuneration mismatch')
            expense_total = source.get('totalExpenses', source.get('totalDisclosedExpenses'))
            if expense_total is not None:
                require(sum(r[5] for r in values if r[5] is not None) == cents(expense_total), 'New expense total mismatch')
            current = index['sources'].get(sid)
            require(current is not None and current.get('sourceKind', '').startswith('official'), 'New source not officially imported')
            for field, value in {'sha256':source['sha256'], 'dataSha256':source['dataSha256'], 'year':source['year'], 'currency':source.get('currency', 'CAD'), 'url':source.get('sourceUrl',source.get('url'))}.items():
                require(current.get(field) == value, 'New source metadata mismatch: ' + sid + ' ' + field)
            expected[sid] = Counter(values)
            source_pins[sid] = {'collection': collection, 'rows': len(values), 'dataSha256': source['dataSha256']}
            local_count += len(values)
        require(local_count == count, 'New collection count changed: ' + collection)
    require(set(index['sources']) == set(baseline['sourceDefinitions']) | set(expected), 'Unapproved or missing live source IDs')
    corrections = read(root / 'research/salaries/west-vancouver-title-recovery/corrections.json')
    actual_new = defaultdict(Counter); old = []; total = compiled = 0
    current_evidence = []
    def tracked_rows():
        for row in original_rows(root, index):
            if row[0] in {'vancouver-police', 'district-of-west-vancouver'}:current_evidence.append(row)
            yield row
    for row in inverse_corrections(tracked_rows(), corrections):
        total += 1
        source = index['sources'][row[6]]
        compiled += source.get('sourceKind') == 'compiled' or source.get('scope') == 'compiled-unverified'
        if row[6] in baseline['sourceDefinitions']:old.append(row)
        else:actual_new[row[6]][row] += 1
    require(row_groups(old) == baseline['groups'], 'Original row multisets changed (including money, duplicate, anonymous, provenance or employer/period fields)')
    require(dict(actual_new) == expected, 'New sources not imported exactly once')
    require(total == 1440498 + sum(NEW_COLLECTIONS.values()) and compiled == baseline['originalCompiledRecords'], 'Compiled deletion or total row drift')
    require(index['recordCounts'] == {'compiled':compiled, 'official': total - compiled}, 'Stale live record totals')
    currency = verify_currency(root, baseline, index)
    receipts = verify_review_receipts(root, baseline)
    require(receipts == 461, 'Original reviewed receipt count changed')
    groups = live_link_groups(root)
    normalized_links = correction_link_context(baseline['nameGroups'], corrections)
    receipt = read(root / AREA / 'confidence-withdrawals.json')
    qualified_links = apply_confidence_withdrawals(normalized_links, groups, receipt, old, current_evidence)
    links = verify_link_preservation(qualified_links, groups)
    links['auditedHeuristicConfidenceWithdrawals'] = 2
    links['auditedTitleAliasesCollapsedToSameName'] = sum(len(g[3]) for g in baseline['nameGroups']) - sum(len(g[3]) for g in normalized_links)
    verify_employer_link_exports(root, groups, [e['slug'] for e in index['employers']])
    return {'accepted': True, 'baselineCommit': BASELINE_COMMIT, 'preservedOriginalRows': len(old),
            'preservedCompiledRows': compiled, 'currentRows':total, 'newRows':sum(NEW_COLLECTIONS.values()),
            'exactAuditedTitleCorrections':len(corrections), 'preservedResearchInputs':len(baseline['researchInputs']),
            'preservedSourceBackedReceipts':receipts, 'preservedCurrencyAnnotations':currency, **links, 'newSources':source_pins}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze-from', type=Path, help='Maintainer-only archived baseline checkout; never used in CI')
    args = parser.parse_args()
    if args.freeze_from:freeze(args.freeze_from, ROOT / AREA / 'baseline.json.gzip')
    else:print(json.dumps(verify(), indent=2))
