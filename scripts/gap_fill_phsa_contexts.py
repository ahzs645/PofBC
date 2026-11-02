#!/usr/bin/env python3
"""Replay exact PHSA source context pixels for root's personal review."""
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    sources_path = AREA / 'phsa_history/source-inventory.json'
    index_path = AREA / 'phsa_history/context-image-inventory.json'
    sources = {s['key']: s for s in json.loads(sources_path.read_bytes())['sources']}
    index = json.loads(index_path.read_bytes())
    output = AREA / 'reviews/phsa-context-root'
    output.mkdir(exist_ok=True)
    receipt = output / 'original-context-pixel-replay.json'
    assert not receipt.exists()
    records, strips = [], []
    for key in sorted(sources):
        source = sources[key]
        path = Path(source['cachePath'])
        assert sha(path.read_bytes()) == source['sourceSha256']
        doc = fitz.open(path)
        for item in [r for r in index if r['key'] == key]:
            image_path = ROOT / item['path']
            assert sha(image_path.read_bytes()) == item['sha256']
            pix = doc[item['physicalPage'] - 1].get_pixmap(dpi=item['dpi'], alpha=False)
            assert sha(pix.tobytes('png')) == item['sha256']
            records.append(item)
        first = ROOT / next(r['path'] for r in index if r['key'] == key and r['physicalPage'] == 3)
        original = Image.open(first).convert('RGB')
        box = [0, 0, original.width, 500]
        target = output / f'{key}-first-salary-header.png'
        assert not target.exists()
        original.crop(box).save(target)
        strips.append({'key': key, 'sourceSha256': source['sourceSha256'],
                       'wholeOriginalPage': pin(first), 'cropBoxOriginalPixels': box, **pin(target)})
        if key == 'phsa-2012-13':
            target = output / 'phsa-2012-13-original-controls-p86-180.png'
            assert not target.exists()
            doc[85].get_pixmap(dpi=180, alpha=False).save(target)
            strips.append({'key': key, 'sourceSha256': source['sourceSha256'],
                           'physicalPage': 86, 'dpi': 180, 'wholeOriginalPageFreshRender': True, **pin(target)})
    receipt.write_text(json.dumps({'sourceInventory': pin(sources_path), 'contextInventory': pin(index_path),
                                   'all36OriginalContextPngsReplayed': records,
                                   'firstSalaryHeaderSourceStrips': strips, 'noOutreach': True,
                                   'reviewCode': pin(Path(__file__))}, indent=2) + '\n')
    print(json.dumps({'receipt': pin(receipt), 'originalContextRendersExact': len(records),
                      'additionalSourceViews': len(strips)}))


if __name__ == '__main__':
    main()
