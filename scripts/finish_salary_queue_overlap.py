#!/usr/bin/env python3
"""Prove complete compiled copies; retain partial overlaps and literal source nulls."""
import argparse
import collections
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/salaries'
OUT = RESEARCH / 'queue-completion-2026-11-01/integration'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def money(value):
    assert type(value) in (int, float), 'Comparison money must be numeric, not boolean or string'
    amount = Decimal(str(value))
    assert amount.is_finite(), 'Nonfinite comparison money'
    cents = amount * 100
    assert cents == cents.to_integral_value(), 'Do not truncate fractional cents for a cohort match'
    return int(cents)


def comparison_key(name, pay, expenses):
    # Compilation removed punctuation in some names. Preserve every Unicode
    # letter/digit, including accents; do not expand initials or match aliases.
    literal = ''.join(char for char in name.casefold() if char.isalnum())
    return literal, money(pay), 0 if expenses is None else money(expenses)


def compare(official, compiled):
    """A whole-cohort multiset proof; a partial overlap never permits removal."""
    assert all(row[2] is None for row in official), 'Do not discard source job titles'
    assert all(row[1] is None for row in compiled), 'Compiled titled observations need their own scope review'
    official_keys = collections.Counter(comparison_key(r[1], r[3], r[4]) for r in official)
    compiled_keys = collections.Counter(comparison_key(r[0], r[2], r[3]) for r in compiled)
    return {'officialRows': len(official), 'compiledRows': len(compiled),
            'matchedRows': sum((official_keys & compiled_keys).values()),
            'officialOnly': sum((official_keys - compiled_keys).values()),
            'compiledOnly': sum((compiled_keys - official_keys).values()),
            'completeMultisetMatch': bool(official) and official_keys == compiled_keys}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def write(path, data, check):
    if check:
        assert path.read_bytes() == data, ('Comparison does not replay', path)
    else:
        assert not path.exists(), ('Never overwrite a frozen comparison', path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    baseline_manifest = json.loads((RESEARCH / 'baseline-manifest.json').read_text())
    baseline_raw = (RESEARCH / baseline_manifest['file']).read_bytes()
    assert sha(baseline_raw) == baseline_manifest['sha256']
    snapshot = json.loads(gzip.decompress(baseline_raw))
    baseline_public_raw = (RESEARCH / 'queue-completion-2026-11-01/baseline.json.gzip').read_bytes()
    baseline_public = json.loads(gzip.decompress(baseline_public_raw))
    sources = json.loads((RESEARCH / 'queue-completion-acquisition/sources.json').read_text())['sources']
    comparisons, replacements = [], []
    for slug, year, identifier in [
            ('providence-health-care', '2023/24', 'queue-completion-providence-2023-24-employees'),
            ('vancouver-coastal-health', '2020/21', 'queue-completion-vch-2020-21-employees')]:
        source = next(s for s in sources if s['id'] == identifier)
        raw = (RESEARCH / 'queue-completion-acquisition' / source['file']).read_bytes()
        assert sha(raw) == source['dataSha256']
        assert source['completeEmployeeSchedule'] is True and source['status'] == 'verified'
        official = json.loads(gzip.decompress(raw))
        employer = next(e for e in snapshot['employers'] if e['slug'] == slug)
        compiled = [r for r in employer['rows'] if snapshot['years'][r[4]] == year]
        # VCH includes separately titled executive observations. Comparing their
        # full names/pay/expenses detects overlap but cannot establish same scope.
        plain = [[r[0], None, r[2], r[3], r[4]] for r in compiled]
        findings = compare(official, plain)
        findings['compiledTitledRows'] = sum(r[1] is not None for r in compiled)
        findings['sourceId'] = identifier
        findings['sourceSha256'] = source['sha256']
        findings['sourceDataSha256'] = sha(raw)
        findings['compiledYear'] = year
        findings['officialYear'] = source['year']
        findings['decision'] = 'retain-entire-partial-overlap'
        if findings['completeMultisetMatch']:
            assert slug == 'providence-health-care' and not findings['compiledTitledRows']
            assert all(r[3] is not None for r in compiled), 'Unknown compiled expense needs separate review'
            assert len(compiled) == len(official) == 3289
            buckets = collections.defaultdict(list)
            for n, row in enumerate(official):
                buckets[comparison_key(row[1], row[3], row[4])].append((n, row))
            paired = []
            for n, row in enumerate(compiled):
                official_n, accepted = buckets[comparison_key(row[0], row[2], row[3])].pop()
                assert row[2] == accepted[3]
                assert row[3] == accepted[4] or (row[3] == 0 and accepted[4] is None)
                paired.append({'compiledOrdinal': n, 'compiledLiteralRow': row,
                               'officialOrdinal': official_n, 'officialLiteralRow': accepted})
            assert all(not values for values in buckets.values())
            evidence_path = OUT / 'providence-complete-compiled-pairing.json.gzip'
            evidence = gzip.compress(encode({'sourceId': identifier,
                'sourceSha256': source['sha256'], 'sourceDataSha256': sha(raw),
                'baselineSnapshotSha256': sha(baseline_raw), 'pairs': paired}), mtime=0)
            write(evidence_path, evidence, args.check)
            # Match the builder's original snapshot order and JSON serialization.
            selected = [[r[0], r[1], r[2], r[3]] for r in compiled]
            selected_hash = sha(json.dumps(selected, ensure_ascii=False, separators=(',', ':')).encode())
            findings.update(decision='replace-complete-compiled-employee-copy',
                            sourceDashReplacingCompiledZero=sum(r[4] is None for r in official),
                            pairedEvidenceFile=str(evidence_path.relative_to(ROOT)),
                            pairedEvidenceSha256=sha(evidence), selectedRowsSha256=selected_hash)
            replacements.append({'employerSlug': slug, 'compiledYear': year,
                'replacementYear': source['year'], 'sourceIds': [identifier],
                'sourceSha256': {identifier: source['sha256']},
                'sourceDataSha256': {identifier: sha(raw)}, 'expectedRows': len(compiled),
                'expectedRetainedRows': 0, 'selectedRowsSha256': selected_hash,
                'retainPositions': [], 'kind': 'duplicate-compiled-copy',
                'reason': 'The complete3289-row compiled employee cohort matches the complete internally dated2023/24 official employee schedule on all name letters/digits, exact remuneration and every known expense, preserving multiplicity. Case/punctuation/whitespace are comparison-only;588source expense dashes replace compiled zeros as unknown, never as source zeros. No job title, board or elected observation is selected.',
                'evidence': str((OUT / 'compiled-comparison.json').relative_to(ROOT))})
        comparisons.append(findings)
    result = {'frozen': True, 'asOf': '2026-11-01',
        'baselineCommit': baseline_public['repositoryCommit'],
        'baselinePublicSha256': sha(baseline_public_raw),
        'baselineSnapshotSha256': sha(baseline_raw),
        'policy': 'Only whole-cohort multiset proof authorizes deletion. Unicode letters/digits and exact cents are mandatory. Case, punctuation and whitespace changes are comparison-only. A source null may compare to a compiled zero, but the published official expense remains null. No alias, initial expansion, dictionary correction, rounding, cross-employer identity or partial-overlap deletion.',
        'comparisons': comparisons, 'compiledReplacements': replacements}
    write(OUT / 'compiled-comparison.json', encode(result), args.check)
    print(json.dumps({'comparedSources': len(comparisons),
                      'completeReplacementRows': sum(r['expectedRows'] for r in replacements)}))


if __name__ == '__main__':
    main()
