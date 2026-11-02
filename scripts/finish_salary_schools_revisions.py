#!/usr/bin/env python3
"""Replay additive source-image amendments without rewriting frozen native v1."""
import argparse
import copy
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/schools'
COLLECTION = ROOT/'research/salaries/queue-completion-schools'
LEDGER = ROOT/'research/salaries/queue-completion-2026-11-01/reviews/independent-school-extension-acquisition-sd61-footer-correction-ledger.json'
LEDGER_SHA = '86e1e54c9a79b5ac870550b70ad94faceec28227e7c3782fd7a095490d2f6d3b'
PROOF_SHA = '81656dd314e2013d666d390d75bd39ed9e312b63c5f7f1c4c0a1c94213e3e7e3'
DATA_SHA = 'd113332f757cc735cd5eb78d6d0c5c43132e629981f9e05e303386ab900415bc'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value, newline=False):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':'))+ ('\n' if newline else '')).encode(), mtime=0)


def revised_sd61():
    original_proof_path = AREA/'sd61-2025-native-candidate.json.gzip'
    original_data_path = COLLECTION/'sd61-2025-employees.json.gzip'
    assert sha(LEDGER.read_bytes()) == LEDGER_SHA
    assert sha(original_proof_path.read_bytes()) == PROOF_SHA
    assert sha(original_data_path.read_bytes()) == DATA_SHA
    ledger = json.loads(LEDGER.read_text())
    proof = json.loads(gzip.decompress(original_proof_path.read_bytes()))
    data = json.loads(gzip.decompress(original_data_path.read_bytes()))
    assert len(ledger['corrections']) == 20
    proof['priorFrozenNativeProof'] = {'file': str(original_proof_path.relative_to(ROOT)), 'sha256': PROOF_SHA}
    proof['rawPopplerRowsBeforeSourceFooterAmendments'] = copy.deepcopy(proof['popplerRows'])
    proof['rawMupdfRowsBeforeSourceFooterAmendments'] = copy.deepcopy(proof['mupdfRows'])
    proof['sourceFooterImageLedger'] = {'file': str(LEDGER.relative_to(ROOT)), 'sha256': LEDGER_SHA}
    for correction in ledger['corrections']:
        index = correction['employeeIndexZeroBased']
        assert data[index] == correction['beforeRow']
        before, after = correction['beforeRow'], correction['afterRow']
        assert before[:2]+before[3:] == after[:2]+after[3:]
        assert before[2] == correction['beforePosition'] and after[2] == correction['afterPosition']
        for image in correction['actualOriginalImageCrops']:
            assert sha((ROOT/image['path']).read_bytes()) == image['sha256']
        data[index] = list(after)
        for reader, field in [('poppler', 'popplerRows'), ('mupdf', 'mupdfRows')]:
            matches = [(i,r) for i,r in enumerate(proof[field]) if r['category'] == 'employee-remuneration' and r['name'] == before[1] and r['pdfPage'] == before[5]]
            assert len(matches) == 1
            sequence, row = matches[0]
            assert row['position'] == before[2]
            row['position'] = after[2]
            proof['imageVerifiedReaderAmendments'].append({'reader': reader, 'sequence': sequence+1, 'pdfPage': row['pdfPage'],
                'field': 'position', 'before': before[2], 'after': after[2],
                'reason': 'Actual source body title is separate from the centred printed page footer; exact independent image ledger correction, not generic removal of title digits.',
                'sourceImageLedgerFile': str(LEDGER.relative_to(ROOT)), 'sourceImageLedgerSha256': LEDGER_SHA,
                'actualOriginalImageCrops': correction['actualOriginalImageCrops']})
    fields = ['name','position','remuneration','expenses','pdfPage','category']
    assert [[r[f] for f in fields] for r in proof['popplerRows']] == [[r[f] for f in fields] for r in proof['mupdfRows']]
    employees = [r for r in proof['popplerRows'] if r['category'] == 'employee-remuneration']
    assert len(data) == len(employees) == 1370
    assert all(row[1:3] == [item['name'],item['position']] for row,item in zip(data,employees))
    for column, expected in [(3,'143280208.11'), (4,'608455.92')]:
        assert sum((Decimal(str(row[column])) for row in data if row[column] is not None), Decimal(0)) == Decimal(expected)
    proof['sourceFooterAmendmentScope'] = 'Exactly20 employee position fields per native reader; all named/payment/page/multiplicity fields and controls unchanged. Frozen v1 bytes remain immutable.'
    return encode(proof, newline=True), encode(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    proof_raw, data_raw = revised_sd61()
    proof_path = AREA/'sd61-2025-native-candidate-v2.json.gzip'
    data_path = COLLECTION/'sd61-2025-employees-v2.json.gzip'
    if args.check:
        assert proof_path.read_bytes() == proof_raw
        assert data_path.read_bytes() == data_raw
    else:
        if proof_path.exists() or data_path.exists():
            raise ValueError('Reviewed revision already frozen; use --check')
        proof_path.write_bytes(proof_raw)
        data_path.write_bytes(data_raw)
        path = AREA/'source-revisions.json'
        revisions = json.loads(path.read_text()) if path.exists() else {}
        revisions['sd61-2025'] = {'proofFile': proof_path.name, 'dataFileByCategory': {'employee-remuneration': data_path.name}}
        path.write_text(json.dumps(revisions, indent=2)+'\n')
    print(json.dumps({'source': 'sd61-2025', 'revisedPositionFields': 20, 'proofSha256': sha(proof_raw), 'dataSha256': sha(data_raw), 'frozenV1Unchanged': True}))


if __name__ == '__main__':
    main()
