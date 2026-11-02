#!/usr/bin/env python3
"""Pin root's personally viewed PHSA packet and replay its original pixels.

The receipts are candidate-aware primary readings, not independent blind OCR.
This closure preserves provisional typography cases for additive resolution.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    base = AREA / 'reviews/phsa-2013-primary'
    packet_path = AREA / 'phsa_history/source-only-packets/phsa-2013-14-v4/packet.json'
    candidate_path = AREA / 'phsa_history/phsa-2013-14-scan-candidate-v4.json.gzip'
    packet = json.loads(packet_path.read_bytes())
    candidate = json.loads(gzip.decompress(candidate_path.read_bytes()))
    receipts, rows, sheets = [], [], []
    for number in range(1, 18):
        path = base / f'batch-{number:03d}.json'
        raw = path.read_bytes()
        receipt = json.loads(raw)
        assert receipt['candidateAware'] is True
        assert receipt['sourceOnlyPacketSha256'] == sha(packet_path.read_bytes())
        assert receipt['candidateSha256'] == sha(candidate_path.read_bytes())
        receipts.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(raw)})
        rows.extend(receipt['rows'])
        sheets.extend(receipt['contactSheetsPersonallyViewed'])
    assert sorted(sheets) == list(range(1, 37))
    assert len(rows) == len({r['sequence'] for r in rows}) == packet['targetCount'] == 422
    assert {r['sequence'] for r in rows} == {t['sequence'] for t in packet['targets']}
    source = Path(candidate['source']['cachePath'])
    assert sha(source.read_bytes()) == candidate['source']['sourceSha256']
    doc = fitz.open(source)
    page_records, crop_count = [], 0
    targets = {}
    for target in packet['targets']:
        targets.setdefault(target['physicalPage'], []).append(target)
    for page in candidate['pages']:
        pn = page['physicalPage']
        raw_path = ROOT / page['rawPath']
        raw_bytes = raw_path.read_bytes()
        assert sha(raw_bytes) == page['rawSha256']
        raw = json.loads(gzip.decompress(raw_bytes))
        assert raw['sourceSha256'] == candidate['source']['sourceSha256']
        pix = doc[pn - 1].get_pixmap(dpi=300, alpha=False)
        raster_bytes = pix.tobytes('png')
        assert sha(raster_bytes) == page['sourceImageSha256'] == raw['sourceImageSha256']
        raster = Image.open(io.BytesIO(raster_bytes)).convert('RGB')
        for target in targets.get(pn, []):
            assert target['wholeOriginalPageRasterSha256'] == sha(raster_bytes)
            crop_path = ROOT / target['sourceCropPath']
            crop_bytes = crop_path.read_bytes()
            assert sha(crop_bytes) == target['sourceCropSha256']
            actual = Image.open(io.BytesIO(crop_bytes)).convert('RGB')
            expected = raster.crop(target['cropBoxOriginalPixels'])
            assert actual.size == expected.size and actual.tobytes() == expected.tobytes()
            crop_count += 1
        page_records.append({'physicalPage': pn, 'rawPath': page['rawPath'],
                             'rawSha256': page['rawSha256'],
                             'originalRasterSha256': sha(raster_bytes),
                             'paymentBands': len(page['rows'])})
    assert crop_count == 422
    for sheet in packet['contactSheets']:
        assert sha((ROOT / sheet['path']).read_bytes()) == sheet['sha256']
    result = {
        'key': 'phsa-2013-14', 'reviewer': 'root', 'candidateAware': True,
        'status': 'All initial source-packet rows personally read; finite typography cases remain for additive source review before final adoption.',
        'method': 'Root personally viewed all 36 unaltered source contact sheets and checked literal names, pay and expenses. A separate municipal reviewer made values-blind first readings. Every 300dpi original salary-page raster and all 422 displayed crops were independently reproduced byte/pixel-exact from the pinned PDF; no image recognizer substitutes for the personal readings.',
        'sourceSha256': candidate['source']['sourceSha256'],
        'packet': {'path': str(packet_path.relative_to(ROOT)), 'sha256': sha(packet_path.read_bytes())},
        'candidate': {'path': str(candidate_path.relative_to(ROOT)), 'sha256': sha(candidate_path.read_bytes())},
        'firstReadingReceipts': receipts, 'rows': sorted(rows, key=lambda r: r['sequence']),
        'originalSalaryPageReplays': page_records, 'sourceCropsPixelExact': crop_count,
        'provisionalTypographySequences': [30, 459, 1723, 1734, 1848, 2348, 2350, 2351, 2352, 2353, 2354, 2440, 2460, 3047, 3054],
        'noOutreach': True, 'reviewCodeSha256': sha(Path(__file__).read_bytes()),
    }
    path = base / 'initial-personal-source-reading-index.json'
    assert not path.exists(), 'Keep the initial readings immutable; add corrections separately.'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()),
                      'personallyReadRows': len(rows), 'originalPagesReplayed': len(page_records),
                      'cropsPixelExact': crop_count}))


if __name__ == '__main__':
    main()
