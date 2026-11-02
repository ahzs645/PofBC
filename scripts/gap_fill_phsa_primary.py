#!/usr/bin/env python3
"""Record root's bounded, candidate-aware personal original-image checks.

Run only after personally viewing the listed original contact sheets. This is
not an image recognizer and does not substitute for the values-blind peer.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
KEY = 'phsa-2013-14'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheets', required=True)
    parser.add_argument('--batch', type=int, required=True)
    parser.add_argument('--overrides', default='{}')
    parser.add_argument('--notes', default='')
    args = parser.parse_args()
    packet_path = AREA / f'phsa_history/source-only-packets/{KEY}-v4/packet.json'
    candidate_path = AREA / f'phsa_history/{KEY}-scan-candidate-v4.json.gzip'
    assert sha(packet_path.read_bytes()) == '5e48b1af9ac8a3f0cc87b9a54b5bf338b9b5f25a69debe84f08b0942cd4e6794'
    assert sha(candidate_path.read_bytes()) == '0d980edd6cc19f437fa14fc7c0508f40429cbfafd5138a6dd8c5805ead67b9a5'
    packet = json.loads(packet_path.read_bytes())
    candidate = json.loads(gzip.decompress(candidate_path.read_bytes()))
    targets = {t['sequence']: t for t in packet['targets']}
    overrides = {int(k): v for k, v in json.loads(args.overrides).items()}
    sheets = [int(n) for n in args.sheets.split(',')]
    results = []
    for number in sheets:
        sheet = packet['contactSheets'][number - 1]
        assert sha((ROOT / sheet['path']).read_bytes()) == sheet['sha256']
        for seq in sheet['sequences']:
            row = candidate['rows'][seq - 1]['tesseract']
            actual = {'name': None, 'remuneration': None, 'expenses': None} if row is None else {
                'name': row['name'], 'remuneration': row['pay']['value'], 'expenses': row['expense']['value']}
            actual.update(overrides.pop(seq, {}))
            assert actual['name'] and actual['remuneration'] is not None, (seq, 'Explicit source fields required')
            target = targets[seq]
            assert sha((ROOT / target['sourceCropPath']).read_bytes()) == target['sourceCropSha256']
            results.append({'sequence': seq, **actual, 'pdfPage': target['physicalPage'],
                            'sourceCropPath': target['sourceCropPath'], 'sourceCropSha256': target['sourceCropSha256']})
    assert not overrides
    out = AREA / 'reviews/phsa-2013-primary'
    out.mkdir(exist_ok=True)
    path = out / f'batch-{args.batch:03d}.json'
    assert not path.exists(), 'Preserve original readings; correct additively'
    receipt = {'key': KEY, 'reviewer': 'root', 'candidateAware': True,
               'method': 'Root personally viewed every listed unaltered original-source contact-sheet row and checked the selected literal name, pay and expense against the preserved OCR candidate. Explicit source corrections below. This is candidate-aware primary confirmation; Municipal has a separate values-blind first transcript.',
               'sourceOnlyPacketSha256': sha(packet_path.read_bytes()), 'candidateSha256': sha(candidate_path.read_bytes()),
               'contactSheetsPersonallyViewed': sheets, 'rows': results, 'notes': args.notes,
               'noOutreach': True, 'reviewCodeSha256': sha(Path(__file__).read_bytes())}
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()), 'rows': len(results)}))


if __name__ == '__main__':
    main()
