#!/usr/bin/env python3
"""Independent source-image context OCR for root's health period/definition review.

This is a third corroborating reader of complete original context images, not a
salary importer or a statement that OCR is infallible. Originals and all raw
outputs are pinned; unmatched header dates require personal original review.
"""
from concurrent.futures import ThreadPoolExecutor
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
INDEX = AREA / 'health_employees/source-context-image-index.json'
OUT = AREA / 'reviews/health-context-ocr'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(item):
    source, view = item
    path = ROOT / view['path']
    assert sha(path.read_bytes()) == view['sha256']
    env = {**os.environ, 'OMP_THREAD_LIMIT': '1'}
    proc = subprocess.run(['tesseract', str(path), 'stdout', '--psm', '6', 'tsv'],
                          capture_output=True, check=True, env=env)
    tsv = proc.stdout.decode('utf-8')
    words = [row for row in csv.DictReader(io.StringIO(tsv), delimiter='\t', quoting=csv.QUOTE_NONE)
             if row.get('level') == '5' and row.get('text', '').strip()]
    lines = {}
    for word in words:
        key = (word['block_num'], word['par_num'], word['line_num'])
        lines.setdefault(key, []).append(word)
    text = '\n'.join(' '.join(word['text'] for word in row) for row in lines.values())
    result = {'sourceKey': source['key'], 'sourceSha256': source['sourceSha256'],
              'originalImage': view, 'reader': 'Tesseract5 PSM6 original144dpi image',
              'rawTsv': tsv, 'rawStderr': proc.stderr.decode('utf-8'), 'text': text,
              'headerMarchYearEnds': re.findall(r'March\s*31\s*,?\s*(20\d{2})', text[:1800], re.I),
              'headerFiscalPairs': re.findall(r'\b(20\d{2})\s*[/–-]\s*(\d{2,4})\b', text[:1800])}
    raw = (json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    dest = OUT / (source['key'] + '-p' + str(view['physicalPage']) + '.json.gzip')
    blob = gzip.compress(raw, mtime=0)
    if dest.exists():
        assert dest.read_bytes() == blob, 'Preserve context OCR versions rather than overwrite differing evidence'
    else:
        dest.write_bytes(blob)
    return {'sourceKey': source['key'], 'physicalPage': view['physicalPage'],
            'purpose': view['purpose'], 'path': str(dest.relative_to(ROOT)), 'sha256': sha(blob),
            'headerMarchYearEnds': result['headerMarchYearEnds'],
            'headerFiscalPairs': result['headerFiscalPairs']}


def main():
    from PIL import Image, ImageDraw
    index = json.loads(INDEX.read_bytes())
    assert len(index['sources']) == 65
    OUT.mkdir(parents=True, exist_ok=True)
    items = [(source, view) for source in index['sources'] for view in source['images']]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(capture, items))
    sheets = []
    # Source-header snippets retain original pixels, with no resizing. A sheet
    # is only an analysis viewing aid; originals and crop boxes remain linked.
    for start in range(0, 65, 5):
        subset = index['sources'][start:start + 5]
        opened = [(source, Image.open(ROOT / source['images'][0]['path']).convert('RGB')) for source in subset]
        width = max(image.width for _, image in opened)
        height = sum(min(440, image.height) + 24 for _, image in opened)
        canvas = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(canvas)
        y = 0
        crop_refs = []
        for source, image in opened:
            draw.text((4, y + 4), source['key'] + ' — original first employee-page header', fill='black')
            y += 24
            box = [0, 0, image.width, min(440, image.height)]
            crop = image.crop(box)
            canvas.paste(crop, (0, y))
            crop_refs.append({'sourceKey': source['key'], 'originalImage': source['images'][0],
                              'integerCropBox': box, 'sheetBox': [0, y, crop.width, y + crop.height]})
            y += crop.height
        dest = OUT / ('source-headers-' + str(start + 1).zfill(2) + '-' + str(start + len(subset)).zfill(2) + '.png')
        canvas.save(dest)
        sheets.append({'path': str(dest.relative_to(ROOT)), 'sha256': sha(dest.read_bytes()),
                       'noResampling': True, 'sourceCrops': crop_refs})
    receipt = {'sourceCount': 65, 'contextImages': len(items), 'inputIndex': {
                   'path': str(INDEX.relative_to(ROOT)), 'sha256': sha(INDEX.read_bytes())},
               'codeSha256': sha(Path(__file__).read_bytes()), 'results': results,
               'sourceHeaderViewingSheets': sheets,
               'scope': 'Image-based context corroboration; header/controls still require root review, no salary acceptance inferred.'}
    dest = OUT / 'index.json'
    assert not dest.exists(), 'Preserve immutable index; issue a new revision'
    dest.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    first = {source['key']: source['images'][0]['physicalPage'] for source in index['sources']}
    missing = [entry['sourceKey'] for entry in results if entry['physicalPage'] == first[entry['sourceKey']]
               and not entry['headerMarchYearEnds'] and not entry['headerFiscalPairs']]
    print(json.dumps({'sourceCount': 65, 'contextImages': len(items), 'headerSheets': len(sheets),
                      'firstPageYearOcrUnmatched': missing}))


if __name__ == '__main__':
    main()
