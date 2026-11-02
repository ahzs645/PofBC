#!/usr/bin/env python3
"""Reproduce the continued source-spelling decisions and account for every previously held pair."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

from build_name_connection_review import name_key
from review_name_connection_evidence import evidence_row, is_compiled

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/name-links/continuation-2026-11-02'
PRIOR = ROOT / 'research/salaries/name-links/source-verification-2026-11-02/review-results.json'
REVIEWED = ROOT / 'research/salaries/name-links/continuation-reviewed.json'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_review():
    """Bind manual acceptance to all source crops, receipt sheets and locator evidence."""
    plans = read(AREA / 'review-plan.json')
    manifest = read(AREA / 'render-manifest.json')
    visual = read(AREA / 'visual-review.json')
    if visual['reviewPlanSha256'] != sha(AREA / 'review-plan.json') or visual['renderManifestSha256'] != sha(AREA / 'render-manifest.json'):
        raise ValueError('The reviewed plan or rendering manifest changed')
    if manifest['issues']:
        raise ValueError('An original row could not be rendered')
    renders = {(r['planIndex'], r['evidenceIndex']): r for r in manifest['cases']}
    expected = {(i, j) for i, p in enumerate(plans) for j in range(len(p['reviewRows']))}
    if len(renders) != len(manifest['cases']) or set(renders) != expected:
        raise ValueError('The rendering census does not cover every planned original row')
    for (i, j), r in renders.items():
        e = plans[i]['reviewRows'][j]
        for key in ['sourceId', 'physicalPage', 'pdfSha256', 'rowSha256', 'role']:
            if r[key] != e[key]:
                raise ValueError('Rendered original row differs from its source evidence')
        if sha(ROOT / r['crop']) != r['cropSha256'] or sha(ROOT / r['locator']['path']) != r['locator']['sha256']:
            raise ValueError('A reviewed crop or original-row locator changed')
    sheets = set()
    for s in visual['sheets']:
        number = s['sheet']
        if number in sheets or sha(AREA / 'renders' / f'sheet-{number:02d}.png') != s['sha256']:
            raise ValueError('A reviewed contact sheet changed or is duplicated')
        items = {(r['planIndex'], r['evidenceIndex']) for r in manifest['cases'] if r['sheet'] == number}
        if items != {(r['planIndex'], r['evidenceIndex']) for r in s['items']}:
            raise ValueError('The personal review does not cover its sheet')
        sheets.add(number)
    if sheets != {r['sheet'] for r in manifest['cases']}:
        raise ValueError('An original sheet was not personally reviewed')
    reviews = {r['planIndex']: r for r in visual['plans']}
    if len(reviews) != len(visual['plans']) or set(reviews) != set(range(len(plans))):
        raise ValueError('A proposed spelling has no manual disposition')
    entries = []
    for i, p in enumerate(plans):
        review = reviews[i]
        if review['candidateId'] != p['id']:
            raise ValueError('Manual review has drifted to another candidate')
        if review['decision'] != 'verified-source-spelling':
            if review['decision'] != 'held' or not review.get('reason'):
                raise ValueError('Invalid or unexplained manual disposition')
            continue
        if p.get('compiledWitnessesMissing'):
            raise ValueError('A compiled observation is not fully supported')
        if name_key(review['printedName']) != name_key(p['toName']):
            raise ValueError('The personally read printed name differs from the preferred spelling')
        evidence = list({(e['sourceId'], e['physicalPage']): {'sourceId': e['sourceId'], 'pdfPage': e['physicalPage']}
                         for e in p['reviewRows']}.values())
        witnesses = [{'rowSha256': e['rowSha256'], 'sourceId': e['sourceId'], 'pdfSha256': e['pdfSha256'],
                      'pdfPage': e['physicalPage'], **({'printedNameKey': name_key(p['toName'])} if p['kind'] == 'source-extraction' else {})}
                     for e in p['reviewRows']]
        proof = ({'compiledNameKey': name_key(p['fromName']), 'compiledRowsSha256': p['aliasRowsSha256']}
                 if p['kind'] == 'compiled-row' else
                 {'kind': 'rendered-source-spelling', 'aliasNameKey': name_key(p['fromName']), 'aliasRowsSha256': p['aliasRowsSha256']})
        entries.append({'employer': p['employer'], 'names': [p['fromName'], p['toName']], 'preferredName': p['toName'],
                        'decision': 'verified', 'candidateId': p['id'], 'reviewPlanIndex': i,
                        'note': ('The retained compiled spelling was checked against the rendered official name and its unique complete remuneration-and-expense row.'
                                 if p['kind'] == 'compiled-row' else
                                 'The original PDF prints the preferred name; the other spelling is an extraction error. Every official alias row was personally checked; retained compiled observations require their own complete financial witnesses.')
                                + ' All original observations, amounts and reporting labels are retained.',
                        'evidence': evidence, 'proof': {**proof, 'witnesses': witnesses}})
    payload = {'schemaVersion': 1, 'scope': 'Continued source-spelling review at one employer; no payment edits, deleted rows, date relabeling or currency conversions.',
               'visualReview': {'path': str((AREA / 'visual-review.json').relative_to(ROOT)), 'sha256': sha(AREA / 'visual-review.json')},
               'renderManifest': {'path': str((AREA / 'render-manifest.json').relative_to(ROOT)), 'sha256': sha(AREA / 'render-manifest.json')},
               'decisions': entries}
    return payload, plans, reviews


def graph(groups):
    lookup = {}
    for g in groups:
        slug, key, name, aliases = g
        members = {key: ('verified', name), **{a[0]: (a[2], a[1]) for a in aliases}}
        for member, (status, spelling) in members.items():
            lookup[(slug, member)] = {'key': key, 'name': name, 'status': status, 'members': members}
    return lookup


def verified_equivalents(slug, key, lookup):
    """A likely relationship must never supply evidence for a verified identity or separation."""
    g = lookup.get((slug, key))
    if not g or g['status'] != 'verified':
        return {key}
    return {k for k, (status, _) in g['members'].items() if status == 'verified'}


def current_groups():
    groups = {}
    for path in sorted((ROOT / 'public/salaries/links').glob('*.json.gzip')):
        if path.name == 'top.json.gzip':
            continue
        for g in json.loads(gzip.decompress(path.read_bytes()))['links']:
            pair = (g[0], g[1])
            if pair in groups and groups[pair] != g:
                raise ValueError('Alias and preferred surname slices disagree')
            groups[pair] = g
    return list(groups.values())


def build_ledger(payload, plans, reviews):
    pins = read(AREA / 'inputs.json')
    for f in pins['files']:
        if sha(ROOT / f['path']) != f['sha256']:
            raise ValueError(f"Preserved input changed; review again: {f['path']}")
    prior = [r for r in read(PRIOR) if r['status'].startswith('hold-') or r['status'] == 'identity-supported-currency-treatment-held']
    if len(prior) != pins['priorHeldCandidates']:
        raise ValueError('The starting held queue changed')
    baseline = json.loads(gzip.decompress((AREA / 'baseline-links.json.gzip').read_bytes()))
    if sha(AREA / 'baseline-links.json.gzip') != pins['baselineLinksSha256']:
        raise ValueError('The previous name graph snapshot changed')
    groups = current_groups()
    lookup = graph(groups)
    # Every existing verified/likely relationship must survive. Canonical spellings may improve.
    preserved = 0
    for g in baseline['groups']:
        slug, key, _, aliases = g
        target = lookup.get((slug, key))
        if not target:
            raise ValueError('A previous name group disappeared')
        for a in aliases:
            now = lookup.get((slug, a[0]))
            if not now or now['key'] != target['key'] or (a[2] == 'verified' and now['status'] != 'verified'):
                raise ValueError('A previous name relationship was lost or downgraded')
            preserved += 1
    wanted = {(r['employer'], k) for r in prior for n in r['names']
              for k in verified_equivalents(r['employer'], name_key(n), lookup)}
    index = read(ROOT / 'public/salaries/people/index.json')
    official = defaultdict(dict)
    named_rows = 0
    for shard in sorted(index['shards']):
        rows = json.loads(gzip.decompress((ROOT / f'public/salaries/people/{shard}.json.gzip').read_bytes()))
        named_rows += len(rows)
        for r in rows:
            k = (index['employers'][r[4]][3], name_key(r[0]))
            if k in wanted and not is_compiled(r, index['sources']):
                official[k].setdefault(r[6], r)
    by_candidate = defaultdict(list)
    for i, p in enumerate(plans):
        by_candidate[p['id']].append(i)
    baseline_graph = graph(baseline['groups'])
    final = []
    for old in prior:
        slug = old['employer']
        a, b = (name_key(n) for n in old['names'])
        ga, gb = lookup.get((slug, a)), lookup.get((slug, b))
        entry = {'id': old['id'], 'employer': slug, 'names': old['names'], 'previousStatus': old['status'],
                 'status': old['status'], 'pending': True, 'reason': old['reason'], 'evidence': old['evidence'],
                 'reviewPlanIndices': by_candidate[old['id']]}
        if ga and gb and ga['key'] == gb['key']:
            verified = ga['status'] == gb['status'] == 'verified'
            ba, bb = baseline_graph.get((slug, a)), baseline_graph.get((slug, b))
            entry.update(status='connected-verified' if verified else 'held-connected-likely', pending=not verified,
                         reason=('The existing name graph now connects both spellings through verified source evidence.' if verified else
                                 'Both spellings already appear in one application history, but its connecting path includes a likely link. This does not establish a verified identity.'),
                         preferredName=ga['name'], graphConfidence='verified' if verified else 'likely',
                         connectedBeforeThisPass=bool(ba and bb and ba['key'] == bb['key']))
        else:
            sides = []
            for key in [a, b]:
                available = {}
                for eq in sorted(verified_equivalents(slug, key, lookup)):
                    for sid, r in official[(slug, eq)].items():
                        available.setdefault(sid, r)
                sides.append(available)
            common = sorted(set(sides[0]) & set(sides[1]))
            if common:
                sid = common[0]
                entry.update(status='keep-apart-separate-primary-rows', pending=False,
                             reason='The original schedule contains separate named rows under the spellings or their verified source corrections. A surname resemblance does not justify joining these rows.',
                             evidence=[evidence_row(side[sid], index) for side in sides])
            elif by_candidate[old['id']]:
                held = [reviews[i] for i in by_candidate[old['id']] if reviews[i]['decision'] == 'held']
                entry.update(status='held-after-source-row-review' if held else 'held-after-related-spelling-correction',
                             reason=' '.join(r['reason'] for r in held) if held else
                             'A related compiled spelling was corrected to a different official name; this does not establish the original proposed pair. The pair remains held.')
        final.append(entry)
    statuses = dict(sorted(Counter(r['status'] for r in final).items()))
    pending = sum(r['pending'] for r in final)
    summary = {'schemaVersion': 1, 'priorHeldCandidates': len(prior), 'newSourceSpellingCorrections': len(payload['decisions']),
               'compiledSpellingCorrections': sum('kind' not in r['proof'] for r in payload['decisions']),
               'officialExtractionSpellingCorrections': sum(r['proof'].get('kind') == 'rendered-source-spelling' for r in payload['decisions']),
               'personallyReviewedPlans': len(plans), 'personallyReadOriginalRows': len(read(AREA / 'render-manifest.json')['cases']),
               'candidatePairsResolved': len(prior) - pending, 'candidatePairsStillHeld': pending, 'statuses': statuses,
               'newlyVerifiedCandidatePairs': sum(r['status'] == 'connected-verified' and not r['connectedBeforeThisPass'] for r in final),
               'previouslyVerifiedIndirectPairs': sum(r['status'] == 'connected-verified' and r['connectedBeforeThisPass'] for r in final),
               'importantDistinction': 'Source-spelling corrections are not a count of verified candidate pairs or newly discovered people. A likely graph path stays unverified.',
               'currency': 'Pittman remains held: the later USD executive compensation must be displayed and excluded from CAD comparisons consistently before joining. No conversion is assumed.'}
    preservation = {'baseCommit': pins['baseCommit'], 'preservedInputFiles': len(pins['files']),
                    'publishedNamedObservationsUnchanged': named_rows, 'previousNameGroupsPreserved': len(baseline['groups']),
                    'previousRelationshipsPreserved': preserved, 'sourceDefinitionsAmountsAndPeriodLabelsChanged': False,
                    'previousReviewedFilesUnchanged': True, 'outreachSent': False}
    return summary, final, preservation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--write-reviewed', action='store_true', help='Prepare the reviewed payload before rebuilding name links.')
    args = parser.parse_args()
    payload, plans, reviews = checked_review()
    outputs = {REVIEWED: json.dumps(payload, indent=2, ensure_ascii=False) + '\n'}
    if not args.write_reviewed:
        summary, results, preservation = build_ledger(payload, plans, reviews)
        outputs.update({AREA / 'summary.json': json.dumps(summary, indent=2) + '\n',
                        AREA / 'review-results.json': json.dumps(results, indent=2, ensure_ascii=False) + '\n',
                        AREA / 'preservation-check.json': json.dumps(preservation, indent=2) + '\n'})
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer, lineterminator='\n')
        writer.writerow(['id', 'employer', 'name_a', 'name_b', 'status', 'pending', 'reason', 'primary_links'])
        for r in results:
            writer.writerow([r['id'], r['employer'], *r['names'], r['status'], r['pending'], r['reason'],
                             '; '.join(e['sourceUrl'] + (f"#page={e['physicalPage']}" if e['physicalPage'] else '') for e in r['evidence'] if e.get('sourceUrl'))])
        outputs[AREA / 'review-results.csv'] = buffer.getvalue()
        print(json.dumps(summary))
    for path, value in outputs.items():
        if args.check:
            if not path.exists() or path.read_text() != value:
                raise SystemExit(f'Stale continued name review: {path.relative_to(ROOT)}')
        else:
            path.write_text(value)
    print(f"Checked {len(payload['decisions'])} continued source-spelling corrections")


if __name__ == '__main__':
    main()
