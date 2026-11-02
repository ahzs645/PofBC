#!/usr/bin/env python3
"""Reproduce the assessment and disposition of all 3,173 previously held name pairs.

Assessments use the frozen pre-review graph. Outcomes use the current graph, distinguishing
verified local relationships from qualified inference. This never edits raw observations.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

from build_name_connection_review import name_key, parts, one_edit, given_agrees
from review_name_connection_evidence import evidence_row, is_compiled, row_fingerprint

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/name-links/held-completion-2026-11-02'
PRIOR = ROOT / 'research/salaries/name-links/continuation-2026-11-02/review-results.json'


def read(path):
    return json.loads(path.read_text())


def classify(f):
    """Blocking features are deliberately checked before any positive continuity inference."""
    if f['alreadyConnected']:
        return 'existing-connection-retains-confidence'
    if f['id'] == 1:
        return 'currency-implementation-and-primary-identity-review'
    if not all(f['primaryCounts']):
        return 'primary-source-required'
    if f['primaryYearOverlap'] or f['primaryDateOverlap']:
        return 'primary-periods-overlap-no-inference'
    rare = bool(f['rareSharedTitles'])
    if not (f['fullGivenNamesAgree'] or rare):
        return 'initials-or-conflicting-given-names-no-inference'
    if f['alternativeCanonicalNames']:
        return 'multiple-compatible-names-no-inference'
    if all(f['roles']) and not f['sharedTitles']:
        return 'different-published-roles-no-inference'
    if f['scopes'][0] != f['scopes'][1]:
        return 'different-disclosure-scopes-no-inference'
    gap_limit = 6 if rare or f['multipleGivenNames'] else 1
    if f.get('nearestYears', 99) > gap_limit:
        return 'reporting-gap-too-long-no-inference'
    if f.get('nearestPayRatio', 99) > (3 if rare else 1.5):
        return 'pay-discontinuity-needs-evidence'
    if sum(f['rowCounts']) < 3:
        return 'too-few-observations-no-inference'
    if not (rare or f['multipleGivenNames'] or f['combinedNameLetters'] >= 20):
        return 'continuity-alone-insufficient-no-inference'
    return 'supported-likely-source-inference'


def graph(groups):
    return {(slug, member): (slug, key) for slug, key, _, aliases in groups
            for member in [key, *[a[0] for a in aliases]]}


def decision_components(rows):
    parent = {}

    def find(k):
        parent.setdefault(k, k)
        if parent[k] != k:
            parent[k] = find(parent[k])
        return parent[k]

    for r in rows:
        if r['decision'] == 'verified' and r['joined_to']:
            a, b = (r['employer'], name_key(r['name'])), (r['employer'], name_key(r['joined_to']))
            parent[find(a)] = find(b)
    return find


def assess():
    prior = [r for r in read(PRIOR) if r['pending']]
    if len(prior) != 3173:
        raise ValueError('The frozen starting queue must contain exactly 3,173 pairs')
    index = read(ROOT / 'public/salaries/people/index.json')
    employers = {e[3]: at for at, e in enumerate(index['employers'])}
    baseline = json.loads(gzip.decompress((AREA / 'baseline-links.json.gzip').read_bytes()))
    linked = {(employers[slug], key): (employers[slug], canonical)
              for (slug, key), (_, canonical) in graph(baseline['groups']).items()}
    wanted = {(employers[c['employer']], name_key(n)) for c in prior for n in c['names']}
    rows, names = defaultdict(list), {}
    pins = []
    all_rows = []
    for shard in sorted(index['shards']):
        path = ROOT / f'public/salaries/people/{shard}.json.gzip'
        raw = path.read_bytes()
        pins.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
        current = json.loads(gzip.decompress(raw))
        if len(current) != index['shards'][shard]:
            raise ValueError('People index count changed')
        all_rows.extend(current)
        for r in current:
            k = (r[4], name_key(r[0]))
            names.setdefault(k, r[0])
            if k in wanted:
                rows[k].append(r)
    titles = {(k[0], r[1].casefold().strip()) for k, rs in rows.items() for r in rs if r[1]}
    holders = defaultdict(set)
    for r in all_rows:
        title = (r[4], (r[1] or '').casefold().strip())
        if title in titles:
            holders[title].add(name_key(r[0]))
    # Search all names at the employer for alternatives, including names outside this queue.
    signatures, neighbors = defaultdict(set), defaultdict(set)
    for k in wanted:
        surname, given = parts(names.get(k, ''))
        if given:
            for form in {surname, *(surname[:j] + surname[j+1:] for j in range(len(surname)))}:
                signatures[(k[0], given[0][0], form)].add(k)
    for k, n in names.items():
        surname, given = parts(n)
        if not given:
            continue
        possible = {w for form in {surname, *(surname[:j] + surname[j+1:] for j in range(len(surname)))}
                    for w in signatures[(k[0], given[0][0], form)]}
        for w in possible:
            s, g = parts(names[w])
            if k != w and (s == surname or one_edit(s, surname)) and given_agrees(g, given):
                neighbors[w].add(linked.get(k, k))

    def primary(rs):
        return [r for r in rs if not is_compiled(r, index['sources'])]

    def years(rs):
        return {int(index['years'][r[5]][:4]) for r in rs}

    def interval(r):
        s = index['sources'][r[6]]
        return (s['periodStart'], s['periodEnd']) if s.get('periodStart') and s.get('periodEnd') else None

    results = []
    for c in prior:
        a, b = [(employers[c['employer']], name_key(n)) for n in c['names']]
        ra, rb = rows[a], rows[b]
        oa, ob = primary(ra), primary(rb)
        sa, ga = parts(c['names'][0]); sb, gb = parts(c['names'][1])
        shared = {r[1].casefold().strip() for r in ra if r[1]} & {r[1].casefold().strip() for r in rb if r[1]}
        nearest = min(((abs(int(index['years'][x[5]][:4]) - int(index['years'][y[5]][:4])),
                        max(x[2], y[2]) / max(1, min(x[2], y[2])), x, y) for x in oa for y in ob),
                      default=None, key=lambda t: (t[0], t[1]))
        f = {'id': c['id'], 'employer': c['employer'], 'names': c['names'],
             'rowCounts': [len(ra), len(rb)], 'primaryCounts': [len(oa), len(ob)],
             'aliasRowsSha256': [row_fingerprint(ra, index), row_fingerprint(rb, index)],
             'alreadyConnected': linked.get(a, a) == linked.get(b, b),
             'sharedTitles': sorted(shared), 'rareSharedTitles': sorted(t for t in shared if len(holders[(a[0], t)]) <= 3),
             'alternativeCanonicalNames': len((neighbors[a] | neighbors[b]) - {linked.get(a, a), linked.get(b, b)}),
             'fullGivenNamesAgree': bool(ga and gb and len(ga[0]) >= 3 and ga == gb),
             'multipleGivenNames': len(ga) > 1 and len(gb) > 1,
             'combinedNameLetters': min(len(sa + ''.join(ga)), len(sb + ''.join(gb))),
             'primaryYearOverlap': bool(years(oa) & years(ob)),
             'primaryDateOverlap': any(ia[0] <= ib[1] and ib[0] <= ia[1] for x in oa for y in ob
                                       if (ia := interval(x)) and (ib := interval(y))),
             'roles': [sorted({r[1].casefold().strip() for r in rs if r[1]}) for rs in [oa, ob]],
             'scopes': [sorted({str(index['sources'][r[6]].get('scope')) for r in rs}) for rs in [oa, ob]],
             'evidence': [evidence_row(nearest[2], index), evidence_row(nearest[3], index)] if nearest else []}
        if nearest:
            f.update(nearestYears=nearest[0], nearestPayRatio=nearest[1])
        f['assessment'] = classify(f)
        results.append(f)
    return results, index, rows, pins


NEXT = {
    'primary-source-required': 'Locate the original remuneration schedules or official professional identity evidence; a salary match is not established.',
    'primary-periods-overlap-no-inference': 'Inspect both original rows, positions and full names in the overlapping period; do not remove or merge either payment on surname similarity.',
    'initials-or-conflicting-given-names-no-inference': 'Obtain an official full-name/role bridge or a verified original spelling. Shared surname and initials do not identify a person.',
    'multiple-compatible-names-no-inference': 'Resolve the competing same-employer names using an official professional biography or original full-name schedule.',
    'different-published-roles-no-inference': 'Find an official career/role transition connecting the names; pay continuity does not establish that transition.',
    'different-disclosure-scopes-no-inference': 'Resolve the differing disclosure categories before considering a connection.',
    'reporting-gap-too-long-no-inference': 'Find intervening disclosure years or an official professional biography spanning the reporting gap.',
    'pay-discontinuity-needs-evidence': 'Resolve the payment/role discontinuity from original source definitions or an official career history.',
    'too-few-observations-no-inference': 'Find another original disclosure or explicit professional identity evidence.',
    'continuity-alone-insufficient-no-inference': 'Obtain a second identifying fact. A common given name, similar surname and adjacent pay are insufficient.',
}


def outcomes(assessments, index, rows):
    groups = {}
    for path in sorted((ROOT / 'public/salaries/links').glob('*.json.gzip')):
        if path.name == 'top.json.gzip':
            continue
        for g in json.loads(gzip.decompress(path.read_bytes()))['links']:
            groups[(g[0], g[1])] = g
    linked = graph(groups.values())
    decisions = list(csv.DictReader((ROOT / 'research/salaries/name-links/decisions.csv').open()))
    verified = decision_components(decisions)
    old_decisions = list(csv.DictReader(io.StringIO(gzip.decompress((AREA / 'baseline-decisions.csv.gzip').read_bytes()).decode())))
    old_edges = [r for r in old_decisions if r['decision'] == 'verified' and r['joined_to']]
    for r in old_edges:
        if verified((r['employer'], name_key(r['name']))) != verified((r['employer'], name_key(r['joined_to']))):
            raise ValueError('A previously verified local relationship disappeared')
    base = json.loads(gzip.decompress((AREA / 'baseline-links.json.gzip').read_bytes()))
    baseline_lookup = graph(base['groups'])
    baseline_members = {(slug, key): {key, *[a[0] for a in aliases]} for slug, key, _, aliases in base['groups']}
    live_members = {(slug, key): {key, *[a[0] for a in aliases]} for slug, key, _, aliases in groups.values()}
    preserved = 0
    for slug, key, _, aliases in base['groups']:
        target = linked.get((slug, key))
        if not target or any(linked.get((slug, a[0])) != target for a in aliases):
            raise ValueError('A previous connected group was lost')
        preserved += len(aliases)
    professional = read(AREA / 'professional-review.json')
    exclusions = {cid: e for e in professional['exclusions'] for cid in e['ids']}
    employer_at = {e[3]: at for at, e in enumerate(index['employers'])}
    final = []
    for f in assessments:
        slug = f['employer']; a, b = [(slug, name_key(n)) for n in f['names']]
        connected = linked.get(a, a) == linked.get(b, b)
        entry = {k: f[k] for k in ['id', 'employer', 'names', 'assessment', 'aliasRowsSha256', 'primaryCounts']}
        if connected:
            confidence = 'verified' if verified(a) == verified(b) else 'likely'
            entry.update(outcome=f'connected-{confidence}', pending=False,
                         nextAction='Connection is published. Retain each original observation, source period and compensation definition; likely relationships remain assumptions.')
        elif f['id'] in exclusions:
            entry.update(outcome='kept-separate-after-professional-review', pending=True, nextAction=exclusions[f['id']]['finding'])
        else:
            corrected = [bool(live_members.get(linked.get(k, k), {k[1]}) - baseline_members.get(baseline_lookup.get(k, k), {k[1]})) for k in [a, b]]
            entry.update(outcome='related-spelling-corrected-pair-unconfirmed' if any(corrected) and f['assessment'] != 'existing-connection-retains-confidence' else 'unconfirmed-keep-separate',
                         pending=True, nextAction=NEXT.get(f['assessment'], 'Obtain individual primary identity evidence before connecting these histories.'))
        entry['publicSourceLeads'] = list({(r[6], r[7] if len(r) > 7 else None):
            {'sourceId': r[6], 'periodLabel': index['years'][r[5]], 'url': index['sources'][r[6]].get('url'),
             'physicalPage': r[7] if len(r) > 7 else None}
            for n in f['names'] for r in rows[(employer_at[slug], name_key(n))]
            if not is_compiled(r, index['sources'])}.values())
        final.append(entry)
    preservation = {'baseCommit': base['baseCommit'], 'previousGroupsPreserved': len(base['groups']),
                    'previousRelationshipsPreserved': preserved, 'previousVerifiedLocalEdgesPreserved': len(old_edges),
                    'rawObservationValuesChanged': False, 'compensationCurrencyConversions': 0}
    return final, preservation


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--assess-only', action='store_true')
    args = parser.parse_args()
    assessments, index, rows, pins = assess()
    outputs = {AREA / 'assessments.json': encoded(assessments)}
    if not args.assess_only:
        final, preservation = outcomes(assessments, index, rows)
        summary = {'startingHeldPairs': 3173, 'pairsAssessed': len(final),
                   'assessmentCounts': dict(Counter(f['assessment'] for f in assessments)),
                   'outcomes': dict(Counter(f['outcome'] for f in final)),
                   'remainingUnconfirmedPairs': sum(f['pending'] for f in final),
                   'scope': 'Identity connections among already published observations; no salary rows added or deleted. All pairs assessed from original dataset evidence; public professional checks target selected cases, not every person.'}
        outputs[AREA / 'review-results.json'] = encoded(final)
        outputs[AREA / 'summary.json'] = encoded(summary)
        outputs[AREA / 'preservation-check.json'] = encoded(preservation)
        out = io.StringIO(); writer = csv.writer(out, lineterminator='\n')
        writer.writerow(['candidate_id', 'employer', 'name_a', 'name_b', 'outcome', 'assessment', 'next_action', 'public_sources'])
        for f in final:
            writer.writerow([f['id'], f['employer'], *f['names'], f['outcome'], f['assessment'], f['nextAction'],
                             ' | '.join(sorted({e['url'] for e in f['publicSourceLeads'] if e['url']}))])
        outputs[AREA / 'review-results.csv'] = out.getvalue()
        follow_up = defaultdict(lambda: {'names': set(), 'ids': set(), 'sources': set()})
        employers = {e[3]: at for at, e in enumerate(index['employers'])}
        for f in final:
            if not f['pending']:
                continue
            for name, primary_count in zip(f['names'], f['primaryCounts']):
                if primary_count:
                    continue
                for r in rows[(employers[f['employer']], name_key(name))]:
                    label = index['years'][r[5]]
                    item = follow_up[(f['employer'], label)]
                    item['names'].add(name); item['ids'].add(f['id'])
                    for at, coverage in enumerate(index['coverage'].get(f['employer'], [])):
                        if index['years'][at][:4] != label[:4]:
                            continue
                        for sid in coverage.get('sourceIds', []):
                            source = index['sources'].get(sid, {})
                            if source.get('url'):
                                item['sources'].add(source['url'])
        source_csv = io.StringIO(); writer = csv.writer(source_csv, lineterminator='\n')
        writer.writerow(['employer', 'compiled_label_unverified', 'names_without_primary_observations', 'candidate_ids', 'located_original_leads', 'next_action'])
        for (employer, label), item in sorted(follow_up.items()):
            writer.writerow([employer, label, ' | '.join(sorted(item['names'])), ' | '.join(map(str, sorted(item['ids']))),
                             ' | '.join(sorted(item['sources'])), 'Inspect the original row and compensation definition, then public archives if necessary. The compiled label is not a verified calendar year. Record any document request in the repo; do not send it.'])
        outputs[AREA / 'original-source-follow-up.csv'] = source_csv.getvalue()
        backlog = ['# Unconfirmed identity connections', '',
                   'All salary observations are already published. These pairs still need identity evidence; they are not missing salary imports. Do not send procurement requests without authorization.', '',
                   '| Employer | Pairs needing evidence | Starting candidate IDs |', '| --- | ---: | --- |']
        by_employer = defaultdict(list)
        for f in final:
            if f['pending']:
                by_employer[f['employer']].append(f['id'])
        for employer, ids in sorted(by_employer.items()):
            backlog.append(f"| {employer} | {len(ids)} | {', '.join(map(str, ids))} |")
        backlog.extend(['', 'See [review-results.csv](review-results.csv) for every name pair, specific blocker and available original source links. Same-period records are retained independently; this is not a claim that every pair represents different people.', '',
                        'The [original-source follow-up](original-source-follow-up.csv) groups names without primary observations by employer and unverified compiled label. It lists other located official schedules as leads; an absent primary name is not proof that an entire report is missing. Public archive work and source-row review come before considering a document request. No outreach is authorized.', ''])
        outputs[AREA / 'remaining-evidence.md'] = '\n'.join(backlog)
        print(json.dumps(summary, indent=2))
    for path, value in outputs.items():
        if args.check:
            if not path.exists() or path.read_text() != value:
                raise ValueError(f'Review output is stale: {path.relative_to(ROOT)}')
        else:
            path.write_text(value)


if __name__ == '__main__':
    main()
