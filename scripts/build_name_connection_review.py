#!/usr/bin/env python3
"""Reproduce a research queue; never change or merge published salary observations."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/name-links/connection-review-2026-11-02'


def letters(value):
    return re.sub('[^a-z]', '', unicodedata.normalize('NFD', value).lower())


def parts(name):
    surname, *given = re.split(r'\s{3,}|\t', name)[0].split(',')
    return letters(surname), tuple(filter(None, map(letters, re.split(r'[\s.]+', ' '.join(given).strip()))))


def name_key(name):
    surname, given = parts(name)
    return surname + '|' + ' '.join(given)


def given_agrees(left, right):
    """Candidate compatibility only; conflicting disclosed middle names exclude a pair."""
    if not left or not right:
        return False
    for at, (a, b) in enumerate(zip(left, right)):
        if a == b or (a[0] == b[0] and min(len(a), len(b)) == 1):
            continue
        short, long = sorted((a, b), key=len)
        if at == 0 and len(short) >= 3 and long.startswith(short):
            continue
        return False
    return True


def one_edit(left, right):
    """Exactly one insertion, deletion, substitution or adjacent transposition."""
    if left == right or abs(len(left) - len(right)) > 1:
        return False
    if len(left) == len(right):
        mismatches = [at for at, (a, b) in enumerate(zip(left, right)) if a != b]
        return len(mismatches) == 1 or (len(mismatches) == 2
            and mismatches[1] == mismatches[0] + 1
            and left[mismatches[0]] == right[mismatches[1]]
            and left[mismatches[1]] == right[mismatches[0]])
    short, long = sorted((left, right), key=len)
    at = next((i for i, (a, b) in enumerate(zip(short, long)) if a != b), len(short))
    return long[:at] + long[at + 1:] == short


def candidates(groups, joined):
    """One-edit surname variants within employers; no probabilistic identity assertions."""
    by_employer = defaultdict(list)
    for key, group in groups.items():
        if len(group['surname']) >= 5 and group['given']:
            by_employer[group['employer']].append((key, group))
    output = []
    for entries in by_employer.values():
        signatures = defaultdict(list)
        seen = set()
        for key, group in entries:
            surname = group['surname']
            forms = {surname, *(surname[:i] + surname[i + 1:] for i in range(len(surname)))}
            possible = {other for form in forms for other in signatures[(group['given'][0][0], form)]}
            for other_key in possible:
                pair = tuple(sorted((key, other_key)))
                if pair in seen:
                    continue
                seen.add(pair)
                other = groups[other_key]
                if joined.get(key, key) == joined.get(other_key, other_key):
                    continue
                if not one_edit(surname, other['surname']) or not given_agrees(group['given'], other['given']):
                    continue
                left, right = (groups[entry] for entry in pair)
                shared = sorted(left['periods'] & right['periods'])
                output.append({
                    'employer': group['employer'], 'name_a': left['name'], 'name_b': right['name'],
                    'highest_raw_amount': max(left['pay'], right['pay']),
                    'periods_a': sorted(left['periods']), 'periods_b': sorted(right['periods']),
                    'shared_period_labels': shared,
                    'shared_positions': sorted(left['positions'] & right['positions']),
                    'status': 'unreviewed-candidate',
                    'next_action': 'Read original names and row boundaries, then corroborate role and dates; compare currency and payment definitions separately.',
                    'caution': 'Both names occur under a shared reporting label; inspect source scope and possible homonyms.' if shared else 'Name resemblance and different reporting labels do not establish identity.'
                })
            for form in forms:
                signatures[(group['given'][0][0], form)].append(key)
    return sorted(output, key=lambda row: (-row['highest_raw_amount'], row['employer'], row['name_a'], row['name_b']))


def build(snapshot_ref=None):
    if snapshot_ref:
        snapshot_ref = subprocess.check_output(['git', 'rev-parse', '--verify', f'{snapshot_ref}^{{commit}}'], cwd=ROOT, text=True).strip()

    def read(path):
        if snapshot_ref:
            return subprocess.check_output(['git', 'show', f'{snapshot_ref}:{path.relative_to(ROOT)}'], cwd=ROOT)
        return path.read_bytes()

    index_path = ROOT / 'public/salaries/people/index.json'
    index = json.loads(read(index_path))
    groups = {}
    pins = []
    scanned = 0

    def pin(path):
        raw = read(path)
        pins.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
        return raw

    pin(index_path)
    for shard, count in sorted(index['shards'].items()):
        path = ROOT / f'public/salaries/people/{shard}.json.gzip'
        rows = json.loads(gzip.decompress(pin(path)))
        if len(rows) != count:
            raise ValueError(f'People index count mismatch: {shard}')
        scanned += len(rows)
        for name, position, pay, _expenses, employer, year, *_ in rows:
            surname, given = parts(name)
            key = (employer, name_key(name))
            group = groups.setdefault(key, {'name': name, 'surname': surname, 'given': given,
                'employer': index['employers'][employer][3], 'pay': pay, 'periods': set(), 'positions': set()})
            group['pay'] = max(pay, group['pay'])
            group['periods'].add(index['years'][year])
            if position:
                group['positions'].add(position)

    employer_at = {entry[3]: at for at, entry in enumerate(index['employers'])}
    joined = {}
    link_paths = (ROOT / 'public/salaries/links').glob('*.json.gzip')
    if snapshot_ref:
        link_paths = [ROOT / path for path in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', snapshot_ref, 'public/salaries/links'], cwd=ROOT, text=True).splitlines() if path.endswith('.json.gzip')]
    for path in sorted(link_paths):
        if path.name == 'top.json.gzip':
            continue
        for slug, key, _name, aliases in json.loads(gzip.decompress(pin(path)))['links']:
            at = employer_at[slug]
            for alias in [key, *(entry[0] for entry in aliases)]:
                joined[(at, alias)] = (at, key)

    decision_path = ROOT / 'research/salaries/name-links/decisions.csv'
    decisions = list(csv.DictReader(io.StringIO(pin(decision_path).decode())))
    pin(ROOT / 'research/salaries/name-links/reviewed.json')
    types = Counter(row['decision'] for row in decisions)
    queue = candidates(groups, joined)
    summary = {
        'schemaVersion': 1, 'purpose': 'Research prioritization; no new identity merges or pay corrections are applied.',
        'namedRowsScanned': scanned, 'employersInPeopleIndex': len(index['employers']),
        'normalizedNamesWithinEmployers': len(groups),
        'existingDecisions': dict(sorted(types.items())),
        'reviewedOverrides': sum(row['reason'].startswith('Reviewed:') for row in decisions),
        'heuristicVerifiedDecisions': sum(row['decision'] == 'verified' and not row['reason'].startswith('Reviewed:') for row in decisions),
        'additionalOneEditSurnameCandidates': len(queue),
        'candidateCautions': dict(sorted(Counter('shared-label' if row['shared_period_labels'] else 'no-shared-label' for row in queue).items())),
        'limits': [
            'This scans every published named row; unnamed observations cannot be linked by name.',
            'One-edit surname candidates require surnames at least five letters long and compatible given names at one employer. Other spelling changes, nicknames and cross-employer careers are outside this detector.',
            'Verified is the existing application status; it includes heuristics and must not be read as an independently sourced human identity verification.',
            'Amounts prioritize review only. They can have different currencies, definitions and unverified period labels; they are not comparable compensation rankings.',
            'No new identity inference, deletion, currency conversion or salary observation is published by this audit.'
        ]
    }
    return summary, queue, pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare regenerated research outputs without writing.')
    parser.add_argument('--snapshot-ref', help='Read a committed publication snapshot, preserving the original dated candidate queue after new aliases are adopted.')
    args = parser.parse_args()
    summary, queue, pins = build(args.snapshot_ref)
    outputs = {'summary.json': summary, 'surname-candidates.json': queue, 'inputs.json': pins}
    csv_buffer = io.StringIO(newline='')
    fields = ['employer', 'name_a', 'name_b', 'highest_raw_amount', 'periods_a', 'periods_b',
              'shared_period_labels', 'shared_positions', 'status', 'next_action', 'caution']
    writer = csv.DictWriter(csv_buffer, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows({key: '; '.join(value) if isinstance(value, list) else value
                     for key, value in row.items()} for row in queue)
    text_outputs = {'surname-candidates.csv': csv_buffer.getvalue()}
    for name, payload in outputs.items():
        text_outputs[name] = json.dumps(payload, indent=2, ensure_ascii=False) + '\n'
    for name, text in text_outputs.items():
        path = AREA / name
        if args.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit(f'Stale connection review: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
