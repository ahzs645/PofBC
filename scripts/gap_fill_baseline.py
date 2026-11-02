#!/usr/bin/env python3
"""Capture and compare the exact pre-expansion salary observations offline."""
import argparse
from collections import defaultdict
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
BASELINE_COMMIT = 'de42c55e98e42b8001f07e4ecbd210f892ab2716'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def exact_cents(value):
    if type(value) not in (int, float):
        raise ValueError('Published money must be a finite JSON number')
    amount = Decimal(str(value)) * 100
    if not amount.is_finite() or amount != amount.to_integral_value():
        raise ValueError('Published money must preserve exact cents')
    return int(amount)


def fingerprint(rows):
    serial = [json.dumps([r[0], r[1], exact_cents(r[2]),
                          None if r[3] is None else exact_cents(r[3]), r[4]],
                         ensure_ascii=False, separators=(',', ':')) for r in rows]
    return sha('\n'.join(sorted(serial, key=lambda x: x.encode('utf-8'))).encode('utf-8'))


def snapshot(root=ROOT):
    index = read(root / 'public/salaries/employers/index.json')
    groups = defaultdict(list)
    for employer in index['employers']:
        payload = read(root / 'public/salaries/employers' / (employer['slug'] + '.json.gzip'))
        rows = payload if isinstance(payload, list) else payload['rows']
        if len(rows) != sum(employer['counts']):
            raise ValueError('Employer row count changed: ' + employer['slug'])
        for row in rows:
            groups[(employer['slug'], index['years'][row[4]], row[5])].append(
                [row[0], row[1], row[2], row[3], row[6]])
    return index, groups


def capture(root=ROOT):
    index, groups = snapshot(root)
    return {
        'schema': 'salary-gap-fill-baseline-v1', 'repositoryCommit': BASELINE_COMMIT,
        'overall': {'records': sum(index['recordCounts'].values()),
                    'officialRecords': index['recordCounts']['official'],
                    'compiledRecords': index['recordCounts']['compiled'],
                    'employers': len(index['employers'])},
        'sourceMetadata': index['sources'],
        'groups': [{'employerSlug': slug, 'year': year, 'sourceId': source,
                    'rows': len(rows), 'rowMultisetSha256': fingerprint(rows)}
                   for (slug, year, source), rows in sorted(groups.items())],
    }


def metadata_equal(left, right):
    """Compare nested source definitions without Python's bool/number coercion."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(metadata_equal(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(metadata_equal(a, b) for a, b in zip(left, right))
    return left == right


def verify_preserved(baseline, index, groups):
    for source_id, metadata in baseline['sourceMetadata'].items():
        if not metadata_equal(index['sources'].get(source_id), metadata):
            raise ValueError('Earlier source metadata changed: ' + source_id)
    preserved = 0
    for entry in baseline['groups']:
        key = (entry['employerSlug'], entry['year'], entry['sourceId'])
        rows = groups.get(key, [])
        if len(rows) != entry['rows'] or fingerprint(rows) != entry['rowMultisetSha256']:
            raise ValueError('Earlier observations changed: ' + repr(key))
        preserved += len(rows)
    if preserved != baseline['overall']['records']:
        raise ValueError('Baseline row accounting changed')
    return preserved


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='Create once; refuses to replace a baseline')
    args = ap.parse_args()
    path = AREA / 'baseline.json.gzip'
    if args.write:
        if path.exists():
            raise SystemExit('Baseline exists; refusing to replace historical inputs')
        result = capture()
        assert result['overall'] == {'records': 1125685, 'officialRecords': 897321,
                                     'compiledRecords': 228364, 'employers': 254}
        raw = (json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
        path.write_bytes(gzip.compress(raw, mtime=0))
    baseline = read(path)
    index, groups = snapshot()
    print(json.dumps({'preservedRows': verify_preserved(baseline, index, groups),
                      'baselineSha256': sha(path.read_bytes()), 'groups': len(baseline['groups'])}))


if __name__ == '__main__':
    main()
