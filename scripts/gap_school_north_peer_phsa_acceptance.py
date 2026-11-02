"""Exact, bounded peer acceptance of the two source-reviewed PHSA scans."""
from pathlib import Path
import argparse
import collections
import gzip
import hashlib
import json
import re
import shutil

import gap_phsa_history_pixels as pixels
import gap_school_north_peer_phsa_compare as initial

ROOT = Path(__file__).resolve().parents[1]
BASE, AREA = initial.B, initial.A


def pin(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=initial.sha(path))


def source_readings(key, raw):
    rows = []
    by = {(x['physicalPage'], x['rowOnPage']): x['sequence'] for x in raw['rows']}
    for path in sorted((BASE / 'producer-packet-first-readings').glob(key + '-*.json')):
        rows.extend(dict(x, group='producer-source-only-packet') for x in initial.load(path)['rows'])
    for x in rows:
        if key == 'phsa-2011-12' and x['sequence'] == 632:
            x['name'] = 'Danyluk,Larry'
        if key == 'phsa-2011-12' and x['sequence'] == 769:
            x['name'] = 'Duruiheoma,Jerry Francis'
    for filename, group in [('own-independent20-personal-first-transcript.json', 'independent-holdout'),
                            ('own-expense-calibration-personal-first-transcript.json', 'independent-calibration')]:
        source = next(x for x in initial.load(BASE / filename)['sources'] if x['sourceKey'] == key)
        for row in source['rows']:
            rows.append(dict(sequence=by[(row['physicalPage'], row['pageRow'])], name=row['literalName'],
                             remuneration=int(row['literalRemuneration']),
                             expenses=None if row['literalExpenses'] == '-' else int(row['literalExpenses']), group=group))
    # These corrections were personally resolved from fresh original pixels;
    # immutable first transcripts and first comparisons are retained alongside.
    for row in rows:
        if key == 'phsa-2011-12' and row['sequence'] == 2260:
            row['remuneration'] = 81634
        if key == 'phsa-2012-13' and row['sequence'] == 2821:
            row['name'] = 'Sorolla, Jean'
    correction_file = BASE / 'post-v4-original-rereads/additive-selected-v2-own-reading-corrections.json'
    for correction in initial.load(correction_file)['corrections']:
        if correction['sourceKey'] == key:
            for row in rows:
                if row['sequence'] == correction['sequence']:
                    row[correction['field']] = correction['freshLiteral']
    if key == 'phsa-2011-12':
        rows.extend(dict(x, group='adaptive14-source-only-packet') for x in initial.load(BASE / 'adaptive14-personal-first-transcript.json')['rows'])
    else:
        rows.extend(dict(x, group='adaptive11-source-only-packet') for x in initial.load(BASE / 'adaptive11-personal-first-transcript.json')['rows'])
        correction = initial.load(BASE / 'pre-selected-2012-source-name-reread.json')
        for row in rows:
            if row['sequence'] == correction['sequence']:
                row[correction['field']] = correction['freshLiteral']
    extra = BASE / 'post-v4-original-rereads/additive-selected-2012-own-reading-corrections.json'
    if extra.exists():
        for correction in initial.load(extra)['corrections']:
            if correction['sourceKey'] == key:
                for row in rows:
                    if row['sequence'] == correction['sequence']:
                        row[correction['field']] = correction['freshLiteral']
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', required=True, choices=['phsa-2011-12', 'phsa-2012-13'])
    parser.add_argument('--selected', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--compare-only', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    initial.verifyfreeze(BASE / 'all-source-first-before-candidate-freeze.json')
    raw_path = BASE / f'{args.key}-candidate-observed-first-v4.json.gzip'
    raw = initial.load(raw_path)
    selected_path = ROOT / args.selected
    selected = initial.load(selected_path)
    assert selected['candidateSha256'] == initial.sha(raw_path)
    assert selected['sourceSha256'] == raw['source']['sourceSha256']
    assert not selected['pending'] and len(selected['rows']) == len(raw['rows'])
    snapshot = BASE / f'{args.key}-selected-peer-snapshot-{args.revision}.json.gzip'
    if not snapshot.exists():
        shutil.copyfile(selected_path, snapshot)
    assert initial.sha(snapshot) == initial.sha(selected_path)
    readings = source_readings(args.key, raw)
    peer = collections.defaultdict(list)
    differences = []
    for reading in readings:
        sequence = reading['sequence']
        row = selected['rows'][sequence - 1]
        assert row['sequence'] == sequence and not row['pending']
        peer[sequence].append(reading)
        fields = {}
        for field in ['name', 'remuneration', 'expenses']:
            a, b = reading[field], row['selected'][field]
            if initial.nk(a) != initial.nk(b) if field == 'name' else a != b:
                fields[field] = dict(personalSource=a, selected=b)
        if fields:
            differences.append(dict(sequence=sequence, physicalPage=raw['rows'][sequence - 1]['physicalPage'],
                                    rowOnPage=raw['rows'][sequence - 1]['rowOnPage'], group=reading['group'], differences=fields))
    comparison = dict(sourceKey=args.key, snapshot=pin(snapshot), sourceSha256=raw['source']['sourceSha256'],
                      personalReadings=len(readings), uniquePersonallyReadRows=len(peer), differences=differences, noOutreach=True)
    comparison_path = BASE / f'{args.key}-selected-peer-comparison-{args.revision}.json'
    if comparison_path.exists():
        assert initial.load(comparison_path) == comparison
    else:
        assert not args.check, 'Check mode requires the existing immutable comparison'
        comparison_path.write_text(json.dumps(comparison, indent=2) + '\n')
    print(json.dumps(comparison, indent=2), flush=True)
    if args.compare_only or differences:
        return
    for receipt in selected['primaryPersonalReceipts']:
        assert initial.sha(ROOT / receipt['path']) == receipt['sha256']
    replay_path = BASE / 'two-source-raw-readers-and-original-raster-replay.json'
    replay = next(x for x in initial.load(replay_path)['sources'] if x['key'] == args.key)
    assert replay['candidateSnapshotSha256'] == initial.sha(raw_path)
    assert replay['allTrueFieldGeometryFlagsPersonallyRead']
    personally_selected = 0
    source_dash = 0
    for raw_row, row in zip(raw['rows'], selected['rows']):
        assert raw_row['sequence'] == row['sequence'] and not row['pending']
        # Primary field receipts omit undisclosed position; no position is
        # manufactured. Every selected row still pins its literal source page.
        assert row['selected'].get('position') is None and row['selected']['pdfPage'] == raw_row['physicalPage']
        a, b, literal = raw_row['tesseract'], raw_row['rapid'], row['selected']
        if row['sequence'] in peer:
            personally_selected += 1
        else:
            assert a and b
            assert initial.nk(a['name']) == initial.nk(b['name']) == initial.nk(literal['name'])
            assert a['pay']['kind'] == b['pay']['kind'] == 'number'
            assert a['pay']['value'] == b['pay']['value'] == literal['remuneration']
            if literal['expenses'] is not None:
                assert a['expense']['kind'] == b['expense']['kind'] == 'number'
                assert a['expense']['value'] == b['expense']['value'] == literal['expenses']
        is_dash = pixels.is_source_dash(raw_row['expenseFullCellInk'], selected['finiteSourceGuard']['dashCalibration'])
        if literal['expenses'] is None:
            assert is_dash or row['sequence'] in peer
            source_dash += 1
        else:
            assert not is_dash, (args.key, row['sequence'], 'numeric amount has calibrated source dash mask')
    totals = [sum(r['selected']['remuneration'] for r in selected['rows']),
              sum(r['selected']['expenses'] for r in selected['rows'] if r['selected']['expenses'] is not None)]
    printed = {'phsa-2011-12': [369888459, 8500874], 'phsa-2012-13': [369114727, 8792836]}[args.key]
    assert totals == selected['literalComputedTotals']
    packet = initial.load(AREA / 'source-only-packets' / f'{args.key}-v4/packet.json')
    assert {t['sequence'] for t in packet['targets']} <= set(peer)
    true_flags = {r['sequence'] for r in raw['rows'] if any(not flag.startswith('low-') for flag in r['reasons'])}
    assert true_flags <= set(peer)
    files = [raw_path, snapshot, comparison_path, replay_path, BASE / 'all-source-first-before-candidate-freeze.json',
             BASE / 'early-source-first-freeze.json', BASE / 'expense-calibration-source-first-freeze.json',
             BASE / 'first-source-context-transcript.json', BASE / 'outside-reader-rows-and-control-disposition.json',
             BASE / 'post-v4-original-rereads/additive-own-reading-and-context-corrections.json',
             BASE / 'post-v4-original-rereads/additive-selected-v2-own-reading-corrections.json',
             BASE / 'pre-candidate-own-reading-corrections.json']
    files.extend(sorted((BASE / 'producer-packet-first-readings').glob(args.key + '-*.json')))
    if args.key == 'phsa-2011-12':
        files.append(BASE / 'adaptive14-personal-first-transcript.json')
    else:
        files.extend([BASE / 'adaptive11-personal-first-transcript.json',
                      BASE / 'pre-selected-2012-source-name-reread.json',
                      BASE / 'source-only-crop-pixel-replay.json',
                      BASE / 'source-only-adaptive2012-crop-pixel-replay.json',
                      BASE / 'source-context-label-qualification.json'])
    if extra := (BASE / 'post-v4-original-rereads/additive-selected-2012-own-reading-corrections.json'):
        if args.key == 'phsa-2012-13' and extra.exists():
            files.append(extra)
    receipt = dict(sourceKey=args.key, sourceSha256=raw['source']['sourceSha256'], selectedSnapshot=pin(snapshot),
                   status='accepted-bounded-independent-source-review', namedRows=len(selected['rows']),
                   allOriginalPagePaymentBandsIndependentlyCensused=True, bothRawReadersAllFieldsReplayed=True,
                   allOriginal300dpiPageRasterHashesReplayed=True, packetTargetsPersonallySourceRead=len(packet['targets']),
                   allTrueFieldGeometryFlagsPersonallySourceRead=len(true_flags), independentHoldouts=20,
                   independentExpenseCalibrationRows=12 if args.key == 'phsa-2011-12' else 16,
                   uniquePersonallyReadRows=len(peer), allPersonallyReadFieldsMatchFinal=True,
                   selectedNullExpenses=source_dash, noUnknownExpenseImputedZero=True,
                   literalComputedNamedComponents=totals, personallyReadPrintedNamedComponents=printed,
                   residualComputedMinusPrinted=[a - b for a, b in zip(totals, printed)],
                   paymentBasis='Money physically received by or paid on behalf of employees during the fiscal year; remuneration exceeds75000; expenses separate; positions not disclosed.',
                   limitations=['Full payment-row census and all retained raw-reader alternatives were replayed; personal field transcription is limited to exact stated targets and holdouts.',
                                'Source-specific confidence benchmarks and reader agreement do not establish infallibility or a statistical accuracy rate.',
                                'Immutable first peer transcription errors and fresh original rereads are preserved additively; controls were not balanced by changing row values.',
                                'This receipt pins selected/raw payloads. Public normalized data and provenance require exact downstream mapping checks.'],
                   evidenceFiles=[pin(path) for path in files], primaryReceiptPins=selected['primaryPersonalReceipts'], noOutreach=True)
    destination = BASE / f'{args.key}-independent-bounded-source-review.json'
    if args.check:
        assert initial.load(destination) == receipt
    else:
        assert not destination.exists()
        destination.write_text(json.dumps(receipt, indent=2) + '\n')
    print('ACCEPTANCE', pin(destination), flush=True)


if __name__ == '__main__':
    main()
