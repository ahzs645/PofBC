#!/usr/bin/env python3
"""Check every frozen surname candidate against published primary-source observations."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

from build_name_connection_review import name_key, parts

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/name-links/connection-review-2026-11-02'
AREA = ROOT / 'research/salaries/name-links/source-verification-2026-11-02'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def row_fingerprint(rows):
    return digest(sorted(digest(row) for row in rows))


def is_compiled(row, sources):
    source = sources[row[6]]
    return source.get('sourceKind') == 'compiled' or source.get('scope') == 'compiled-unverified'


def signature(row, years):
    # Keep null expenses distinct from disclosed zero. Require exact cents, never a pay tolerance.
    return (row[4], years[row[5]][:4], round(row[2] * 100),
            None if row[3] is None else round(row[3] * 100))


def evidence_row(row, index):
    source = index['sources'][row[6]]
    return {'row': row, 'rowSha256': digest(row), 'periodLabel': index['years'][row[5]],
            'sourceId': row[6], 'sourceUrl': source.get('url'), 'pdfSha256': source.get('sha256'),
            'physicalPage': row[7] if len(row) > 7 else None, 'scope': source.get('scope')}


def exact_witnesses(typo_rows, target_key, financial, years):
    matches = []
    for row in typo_rows:
        if row[3] is None:
            return [], 'The compiled expense is unknown, so a full financial row cannot be compared.'
        witnesses = financial.get(signature(row, years), [])
        keys = {(w[4], name_key(w[0])) for w in witnesses}
        if keys != {target_key}:
            return [], ('The financial tuple is not unique to the proposed official name.'
                        if target_key in keys else 'No exact official remuneration-and-expense tuple matches every compiled observation.')
        matches.append((row, sorted(witnesses, key=lambda w: (w[6], w[7] or 0, w[0]))))
    return matches, None


def build():
    raw_candidates = (BASE / 'surname-candidates.json').read_bytes()
    candidates = json.loads(raw_candidates)
    index = json.loads((ROOT / 'public/salaries/people/index.json').read_text())
    employer_at = {row[3]: at for at, row in enumerate(index['employers'])}
    wanted = {(employer_at[c['employer']], name_key(c[name]))
              for c in candidates for name in ['name_a', 'name_b']}
    grouped = defaultdict(list)
    financial = defaultdict(list)
    input_pins = [{'path': 'public/salaries/people/index.json', 'sha256': hashlib.sha256((ROOT / 'public/salaries/people/index.json').read_bytes()).hexdigest()}]
    for shard, count in sorted(index['shards'].items()):
        path = ROOT / f'public/salaries/people/{shard}.json.gzip'
        raw = path.read_bytes()
        input_pins.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
        rows = json.loads(gzip.decompress(raw))
        if len(rows) != count:
            raise ValueError(f'People shard does not match its index: {shard}')
        for row in rows:
            key = (row[4], name_key(row[0]))
            if key in wanted:
                grouped[key].append(row)
            source = index['sources'][row[6]]
            if not is_compiled(row, index['sources']) and source.get('url') and source.get('sha256'):
                financial[signature(row, index['years'])].append(row)

    dispositions = []
    for at, candidate in enumerate(candidates, 1):
        keys = [(employer_at[candidate['employer']], name_key(candidate[name])) for name in ['name_a', 'name_b']]
        a, b = (grouped[key] for key in keys)
        official_a = [r for r in a if not is_compiled(r, index['sources'])]
        official_b = [r for r in b if not is_compiled(r, index['sources'])]
        result = {'id': at, 'employer': candidate['employer'], 'names': [candidate['name_a'], candidate['name_b']],
                  'candidateSha256': digest(candidate), 'rowCounts': [len(a), len(b)],
                  'officialRowCounts': [len(official_a), len(official_b)], 'evidence': []}
        if official_a and official_b:
            common = sorted({r[6] for r in official_a} & {r[6] for r in official_b})
            if common:
                source_id = common[0]
                pair = [next(r for r in rows if r[6] == source_id) for rows in [official_a, official_b]]
                result.update(status='keep-apart-distinct-names-in-one-primary-schedule',
                              reason='The same original schedule discloses both names as separate rows; no affirmative identity evidence supports a join.')
            else:
                pair = [official_a[0], official_b[0]]
                result.update(status='hold-two-primary-spellings',
                              reason='Both spellings occur in accepted official disclosures. A dated biography or explicit employer correction is needed to establish a connection.')
            result['evidence'] = [evidence_row(row, index) for row in pair]
        elif not official_a and not official_b:
            result.update(status='hold-primary-source-needed',
                          reason='Both names are retained compiled observations; accepted primary-source rows are unavailable for either spelling.')
        else:
            typo, target, target_key = (a, official_b, keys[1]) if not official_a else (b, official_a, keys[0])
            matches, blocker = exact_witnesses(typo, target_key, financial, index['years'])
            if blocker:
                result.update(status='hold-financial-row-not-established', reason=blocker)
                result['evidence'] = [evidence_row(target[0], index)]
            else:
                # This is a queue for visual source review, never an automatic identity decision.
                result.update(status='ready-for-rendered-source-review',
                              reason='Every observation of one compiled-only spelling matches exact pay and expenses for one unique official name in the corresponding year-label prefix.',
                              compiledName=typo[0][0], proposedName=matches[0][1][0][0],
                              compiledNameKey=name_key(typo[0][0]), targetNameKey=target_key[1],
                              compiledRowsSha256=row_fingerprint(typo),
                              compiledGivenNameIsInitial=bool(parts(typo[0][0])[1] and len(parts(typo[0][0])[1][0]) == 1))
                result['matches'] = [{'compiled': evidence_row(row, index), 'official': evidence_row(witnesses[0], index),
                                      'otherIdenticalWitnesses': len(witnesses) - 1} for row, witnesses in matches]
                result['evidence'] = [pair['official'] for pair in result['matches']]
        if result['employer'] == 'bc-investment-management-corporation' and set(result['names']) == {'Pittman, J.', 'Pittmsn, Jim'}:
            result.update(status='identity-supported-currency-treatment-held',
                          reason='The prior BCI primary-source review supports Jim Pittman, but the later amount is USD executive total compensation. Currency-aware display and comparisons must precede an application join.',
                          priorReview='research/salaries/name-links/connection-review-2026-11-02/case-findings.json')
        dispositions.append(result)

    summary = {'schemaVersion': 1, 'candidates': len(dispositions),
               'frozenCandidateFileSha256': hashlib.sha256(raw_candidates).hexdigest(),
               'sourceBaselineCommit': 'c76141a55',
               'statuses': dict(sorted(Counter(row['status'] for row in dispositions).items())),
               'rules': ['Exact remuneration cents and disclosed expense cents; null is not zero.',
                         'Every compiled-only observation under the proposed alias must have a witness.',
                         'The monetary tuple must be unique to one official normalized name at this employer and year-label prefix.',
                         'Financial agreement is a source-row lead, not an identity decision; rendered originals must be reviewed before adoption.',
                         'No deletions, amount edits, date relabeling or currency conversion.']}
    return summary, dispositions, input_pins


def reviewed_links(dispositions):
    manifest_path = AREA / 'render-manifest.json'
    visual_path = AREA / 'visual-review.json'
    manifest = json.loads(manifest_path.read_text())
    visual = json.loads(visual_path.read_text())
    by_sheet = defaultdict(list)
    by_case = defaultdict(list)
    for row in manifest['cases']:
        by_sheet[row['sheet']].append(row)
        by_case[row['id']].append(row)
        if hashlib.sha256((ROOT / row['crop']).read_bytes()).hexdigest() != row['cropSha256']:
            raise ValueError('A reviewed original-row crop changed')
    reviewed_sheets = set()
    for sheet in visual['sheets']:
        path = AREA / 'renders' / f"sheet-{sheet['sheet']:02d}.png"
        if hashlib.sha256(path.read_bytes()).hexdigest() != sheet['sha256']:
            raise ValueError('A visually reviewed contact sheet changed')
        if Counter(sheet['caseIds']) != Counter(row['id'] for row in by_sheet[sheet['sheet']]):
            raise ValueError('Visual review does not cover the source rows on its sheet')
        reviewed_sheets.add(sheet['sheet'])
    held = set(visual.get('heldCaseIds', []))
    entries = []
    for case in dispositions:
        if case['status'] != 'ready-for-rendered-source-review' or case['id'] in held:
            continue
        renders = by_case[case['id']]
        if len(renders) != len(case['matches']) or not all(row['sheet'] in reviewed_sheets for row in renders):
            continue
        for match, render in zip(case['matches'], renders):
            source = match['official']
            if (source['sourceId'], source['physicalPage'], source['pdfSha256']) != (render['sourceId'], render['physicalPage'], render['pdfSha256']):
                raise ValueError('Rendered source identity differs from the proposed evidence')
        entries.append({
            'employer': case['employer'], 'names': [case['compiledName'], case['proposedName']],
            'preferredName': case['proposedName'], 'decision': 'verified', 'candidateId': case['id'],
            'note': 'The compiled spelling was checked against the rendered official name and its unique remuneration-and-expense row. Original observations and period caveats are retained.',
            'evidence': list({(row['sourceId'], row['physicalPage']): {'sourceId': row['sourceId'], 'pdfPage': row['physicalPage']} for row in case['evidence']}.values()),
            'proof': {'compiledNameKey': case['compiledNameKey'], 'compiledRowsSha256': case['compiledRowsSha256'],
                      'witnesses': [{'rowSha256': row['rowSha256'], 'sourceId': row['sourceId'], 'pdfSha256': row['pdfSha256'], 'pdfPage': row['physicalPage']} for row in case['evidence']]}
        })
    return {'schemaVersion': 1, 'scope': 'Reviewed source-spelling corrections at one employer. No payment deletions, period relabeling or verified lifetime identities.',
            'visualReview': {'path': str(visual_path.relative_to(ROOT)), 'sha256': hashlib.sha256(visual_path.read_bytes()).hexdigest()},
            'renderManifest': {'path': str(manifest_path.relative_to(ROOT)), 'sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest()},
            'decisions': entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--write-reviewed', action='store_true', help='Publish only the explicitly reviewed, still-supported spelling corrections.')
    args = parser.parse_args()
    summary, dispositions, pins = build()
    payload = reviewed_links(dispositions) if (AREA / 'visual-review.json').exists() else None
    approved = {row['candidateId'] for row in payload['decisions']} if payload else set()
    final = [{**row, 'evidenceStatus': row['status'],
              'status': 'verified-source-spelling-connection' if row['id'] in approved else row['status']}
             for row in dispositions]
    summary['finalStatuses'] = dict(sorted(Counter(row['status'] for row in final).items()))
    summary['visuallyReviewedCorrections'] = len(approved)
    outputs = {'summary.json': json.dumps(summary, indent=2) + '\n',
               'dispositions.json': json.dumps(dispositions, indent=2, ensure_ascii=False) + '\n',
               'review-results.json': json.dumps(final, indent=2, ensure_ascii=False) + '\n',
               'inputs.json': json.dumps(pins, indent=2) + '\n'}
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(['id', 'employer', 'name_a', 'name_b', 'status', 'reason', 'primary_links'])
    for row in final:
        writer.writerow([row['id'], row['employer'], *row['names'], row['status'], row['reason'],
                         '; '.join(f"{e['sourceUrl']}#page={e['physicalPage']}" if e['physicalPage'] else e['sourceUrl'] or '' for e in row['evidence'])])
    outputs['dispositions.csv'] = buffer.getvalue()
    for name, value in outputs.items():
        path = AREA / name
        if args.check:
            if not path.exists() or path.read_text() != value:
                raise SystemExit(f'Stale evidence review: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
    if args.write_reviewed:
        if payload is None:
            raise SystemExit('Rendered source review is required before adopting a connection')
        path = ROOT / 'research/salaries/name-links/source-reviewed.json'
        text = json.dumps(payload, indent=2, ensure_ascii=False) + '\n'
        if args.check:
            if path.read_text() != text:
                raise SystemExit('Source-reviewed application links are stale')
        else:
            path.write_text(text)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
