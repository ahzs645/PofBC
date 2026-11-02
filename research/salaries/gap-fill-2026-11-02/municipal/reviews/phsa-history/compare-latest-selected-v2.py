"""Additive comparison of locked personal source transcripts to final producer choices."""
import gzip
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
BASE = pathlib.Path(__file__).resolve().parent
PRODUCER = ROOT / "research/salaries/gap-fill-2026-11-02/phsa_history"


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gzip' else path.read_text())


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def name(value):
    return re.sub(r'\s*,\s*', ',', re.sub(r'\s+', ' ', value.strip()))


def fields(row):
    return [name(row['name']), row.get('position'), row['remuneration'], row['expenses'], row['pdfPage']]


holdouts = read(BASE / 'latest-two-scans-first-independent-holdout-transcript.json')['rows']
all_results = []
for key in ['phsa-2013-14', 'phsa-2014-15']:
    paths = ([BASE / 'phsa-2013-14-peer-final-source-readings.json'] if key == 'phsa-2013-14' else
             sorted(BASE.glob('phsa-2014-15-first-transcript-part-*.json')))
    paths += [BASE / (key + ('-adaptive-23-first-source-transcript.json' if key.endswith('13-14') else '-adaptive-three-first-source-transcript.json'))]
    expected = {}
    for path in paths:
        for row in read(path)['rows']:
            if row['sequence'] in expected:
                assert fields(expected[row['sequence']]) == fields(row)
            expected[row['sequence']] = dict(row)
    if key == 'phsa-2014-15':
        # Source-only correction was recorded before any latest-year candidate access.
        paths.append(BASE / 'phsa-2014-15-own-source-reread-before-candidate-001.json')
        expected[1636]['name'] = 'Jacobucci,Tina'
    overlaps = []
    for row in holdouts:
        if row['sourceKey'] != key:
            continue
        if row['sequence'] in expected:
            assert fields(expected[row['sequence']]) == fields(row), (key, row['sequence'], fields(expected[row['sequence']]), fields(row))
            overlaps.append(row['sequence'])
        else:
            expected[row['sequence']] = dict(row)
    paths.append(BASE / 'latest-two-scans-first-independent-holdout-transcript.json')
    candidate_path = PRODUCER / (key + '-scan-selected-v2.json.gzip')
    candidate = read(candidate_path)
    actual = {row['sequence']: row['selected'] for row in candidate['rows']}
    differences = []
    for seq, row in sorted(expected.items()):
        if fields(row) != fields(actual[seq]):
            differences.append({'sequence': seq, 'expected': fields(row), 'selected': fields(actual[seq]),
                                'sourceImagePath': row['sourceImagePath'], 'sourceImageSha256': row['sourceImageSha256']})
    result = {'sourceKey': key, 'candidatePin': pin(candidate_path), 'transcriptPins': [pin(path) for path in paths],
              'phase': 'first comparison to selected-v2 after source-first transcripts locked',
              'personallyImageReadUniqueRows': len(expected), 'moneyCells': 2 * len(expected),
              'scope': 'Complete fields for bounded personal source-image rows; whole-source computational verification is separate.',
              'normalization': 'collapse whitespace and comma-adjacent whitespace only; preserve word boundaries, case, spelling, punctuation',
              'holdoutOverlapSequences': overlaps, 'differences': differences, 'allFieldsAgree': not differences,
              'candidateRows': len(actual), 'candidatePending': candidate['pending'],
              'finalSourceRows': [expected[seq] for seq in sorted(expected)], 'noOutreach': True}
    destination = BASE / (key + '-selected-v2-first-independent-comparison.json')
    assert not destination.exists(), destination
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(key, 'human', len(expected), 'differences', len(differences), 'pin', pin(destination))
    for item in differences:
        print(item['sequence'], item['expected'], item['selected'])
    all_results.append(result)
