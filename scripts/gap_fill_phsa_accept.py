#!/usr/bin/env python3
"""Root's exact normalized adoption of nine independently reviewed PHSA originals."""
import argparse
import collections
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02'
AREA = BASE / 'phsa_history'
COLLECTION = ROOT / 'research/salaries/gap-fill-phsa-history'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def pinned(reference):
    path = (ROOT / reference['path']).resolve()
    assert path.is_relative_to(ROOT) and sha(path.read_bytes()) == reference['sha256']
    return read(path)


def canonical_name(name):
    assert type(name) is str and name.strip()
    return re.sub(r'\s*,\s*', ',', ' '.join(name.split()))


def amount(value):
    if value is None:
        return None
    assert type(value) in [str, int, float], 'Boolean is not a monetary amount'
    number = Decimal(str(value))
    assert number.is_finite() and number * 100 == (number * 100).to_integral_value()
    return int(number) if number == number.to_integral_value() else float(number)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--index-sha', required=True)
    args = parser.parse_args()
    mp, ip = COLLECTION / 'sources-candidate.json', AREA / 'source-acceptance-index.json'
    assert sha(mp.read_bytes()) == args.candidate_sha
    assert sha(ip.read_bytes()) == args.index_sha
    index = read(ip)
    assert index['pendingPeerScopes'] == [] and index['noOutreach'] is True
    assert len(index['sources']) == 9
    contexts = pinned(index['sourceContextAcceptance'])
    assert index['sourceContextAcceptance']['sha256'] == 'e486351a8851756d83dfcea2a3a1f40968b49bc69513209c7bb5d8347018dda9'
    assert contexts['acceptedContextScope'] is True and contexts['acceptsNormalizedRows'] is False
    context_by_key = {r['key']: r for r in contexts['sources']}
    originals = {r['key']: r for r in pinned(index['inventory'])['sources']}
    sources = read(mp)['sources']
    by_key = {s['id'].removeprefix('gap-phsa-history-'): s for s in sources}
    assert set(by_key) == set(originals) == set(context_by_key)
    results, peer_refs, pages = [], {}, 0
    for item in index['sources']:
        key = item['key']
        source, original, context = by_key[key], originals[key], context_by_key[key]
        assert source['sha256'] == original['sourceSha256'] == context['sourceSha256']
        assert source['periodStart'] == context['periodStart'] == item['periodStart']
        assert source['periodEnd'] == context['periodEnd'] == item['periodEnd']
        assert item['printedEmployeeNarrativeCount'] == context['printedEmployeeNarrativeCount']
        controls = item['printedNamedControls']
        assert [controls['remuneration'], controls['expenses']] == list(context['printedNamedControls'].values())
        assert controls['physicalPage'] == context['controlPhysicalPage']
        for reference in item['peerReviews'] + item['pageCensusEvidence']:
            pinned(reference)
            peer_refs[reference['path']] = reference
        assert item['peerReviews'] and item['pageCensusEvidence']
        chosen = pinned(item['selectedInput'])
        if item['inputKind'] == 'native':
            assert chosen['fieldDifferences'] == []
            selected = chosen['popplerRows']
            second = chosen['mupdfRows']
            for a, b in zip(selected, second):
                assert [a[f] for f in ['name', 'position', 'remuneration', 'expenses', 'pdfPage']] == [b[f] for f in ['name', 'position', 'remuneration', 'expenses', 'pdfPage']]
            assert len(selected) == len(second)
        else:
            assert chosen['pending'] == [] and chosen['sourceSha256'] == source['sha256']
            assert chosen['primaryPersonalReceipts'] and chosen['primaryPersonallyReadRows'] > 0
            for reference in chosen['primaryPersonalReceipts']:
                pinned(reference)
            selected = []
            for n, row in enumerate(chosen['rows'], 1):
                assert row['sequence'] == n and not row['pending'] and row['selected'] is not None
                selected.append(row['selected'])
        expected = [[source['employerSlug'], canonical_name(r['name']), None,
                     amount(r['remuneration']), amount(r['expenses']), r['pdfPage']] for r in selected]
        assert all(r[3] is not None and type(r[5]) is int and r[5] >= 3 for r in expected)
        data = COLLECTION / source['file']
        assert sha(data.read_bytes()) == source['dataSha256']
        actual = read(data)
        assert actual == expected and len(actual) == item['actualNamedRows'] == source['rowCount']
        assert all(a[5] <= b[5] for a, b in zip(actual, actual[1:]))
        provenance_path = COLLECTION / source['provenanceFile']
        assert sha(provenance_path.read_bytes()) == source['provenanceSha256']
        provenance = read(provenance_path)
        assert provenance['sourceSha256'] == source['sha256']
        assert provenance['sourceSelection'] == item['selectedInput']
        assert provenance['sourceContextAcceptance'] == index['sourceContextAcceptance']
        assert len(provenance['rows']) == len(actual)
        for n, (record, proof, raw) in enumerate(zip(actual, provenance['rows'], selected), 1):
            assert [proof['rowIndex'], proof['pdfPage'], proof['name']] == [n, record[5], record[1]]
            if item['inputKind'] == 'native':
                assert proof['sourceFootnoteMarker'] == raw.get('sourceFootnoteMarker')
        sums = [sum((Decimal(str(r[c])) for r in actual if r[c] is not None), Decimal()) for c in [3, 4]]
        residuals = [sums[0] - Decimal(str(controls['remuneration'])), sums[1] - Decimal(str(controls['expenses']))]
        validation = source['validation']
        assert [Decimal(validation['literalRemunerationSum']), Decimal(validation['literalKnownExpenseSum'])] == sums
        assert list(map(Decimal, validation['literalNamedControlResiduals'])) == residuals
        assert validation['printedEmployeeNarrativeCount'] == context['printedEmployeeNarrativeCount']
        assert validation['sourceSelection'] == item['selectedInput']
        if any(residuals):
            assert 'differ from the printed named controls' in source['publicWarning']
        if key == 'phsa-2009-10':
            assert context['printedEmployeeNarrativeCount'] is None
            assert context['conflictingNarrativeCount'] == item['conflictingNarrativeCount'] == 1800
            assert context['conflictingNarrativeCountPeriodEnd'] == item['conflictingNarrativeCountPeriodEnd'] == '2009-03-31'
            assert 'contradictory narrative' in source['publicWarning']
        assert source['retainCompiledPartition'] is True
        assert source['completeEmployeeSchedule'] is validation['completeEmployeeSchedule'] is True
        assert validation['compiledPartitionRetained'] is True and validation['compiledPartitionRetentionReason']
        original_path = Path(original['cachePath'])
        assert sha(original_path.read_bytes()) == source['sha256']
        pages += original['pageCount']
        results.append({'sourceId': source['id'], 'sourceSha256': source['sha256'],
                        'dataSha256': source['dataSha256'], 'provenanceSha256': source['provenanceSha256'],
                        'rowCount': len(actual), 'exactNormalizedReconstruction': True,
                        'physicalPagesInPinnedOriginal': original['pageCount'],
                        'namedRowsByPhysicalPage': dict(collections.Counter(r[5] for r in actual)),
                        'literalRemunerationSum': str(sums[0]), 'literalKnownExpenseSum': str(sums[1]),
                        'literalNamedControlResiduals': list(map(str, residuals)),
                        'selectedInput': item['selectedInput'], 'peerReviews': item['peerReviews']})
    assert len(results) == 9 and sum(r['rowCount'] for r in results) == 22796 and pages == 602
    receipt = {'accepted': True, 'approvedBy': 'root', 'noOutreach': True,
               'candidateManifest': pin(mp), 'sourceAcceptanceIndex': pin(ip),
               'nineSourceContextAcceptance': index['sourceContextAcceptance'],
               'independentSourceReviewReceipts': list(peer_refs.values()), 'sources': results,
               'scope': 'Nine located original PHSA employee histories2006/07–2014/15;4082native and18714scanned payment observations. Root independently reconstructed all22796normalized records and checked every provenance name/page index and source/control/period/retention definition. Root personally read all9source definitions/firstheaders/finalcontrols plus428unique primary2013/14source targets and source typography contexts; South personally read23additional primary challenges and Municipal independently source-read459unique rows. Other years have separately pinned source-first independent reviewers and complete page/payment-band/expense-glyph/raw-reader censuses. This is bounded verification, not personal transcription of22796rows or a guarantee of all-name OCR accuracy.',
               'qualifications': 'All source control/count residuals remain explicit; no balancing, employee invention or compiled deletion. The2009/10repeated schedule period2010 and contradictory2009narrative remain separately disclosed. Some I/l case rendering follows qualified same-source typography, without a Unicode or identity claim. Numeric zero differs from dash/unknown; expenses are separate from remuneration; source footnotes remain evidence, not inferred job titles. Every original and superseded reader/firstreading/amendment is retained.',
               'reviewCode': pin(Path(__file__))}
    path = BASE / 'reviews/root-nine-phsa-history-source-acceptance.json'
    assert not path.exists()
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': pin(path), 'sources': 9, 'rows': 22796}))


if __name__ == '__main__':
    main()
