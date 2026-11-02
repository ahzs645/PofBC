#!/usr/bin/env python3
"""Complete SD50 salary scope: raw Tesseract lines and independent Paddle boxes.

Undetected OCR expense cells are unresolved strings until image amendments;
missing detection is never itself interpreted as a printed expense dash.
"""
import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/schools'
RAW_SHA = 'b7484e78b4619df486ad22629c4172096ca07991acfe6b2b7a6fcdef5743440d'
DECIMAL_MONEY = re.compile(r'\d[\d,]*\.\d{2}')
ROLE = re.compile(r'\s+(TRUSTEE|EXEMPT STAFF|ADMINISTRATIVE OFFIC|TEACHER[:.]?|TEMPORARY|CUPE 12 MTH)\s+')
FIELDS = ['name', 'position', 'remuneration', 'expenses', 'pdfPage', 'category']


def clean(value):
    return re.sub(r'\s+', ' ', value).strip()


def cash(value):
    matches = DECIMAL_MONEY.findall(value)
    return matches[0].replace(',', '') if len(matches) == 1 else 'UNRESOLVED:'+value


def tesseract_rows(pages):
    result = []
    for page in pages:
        number = page['physicalPage']
        if number not in [8, 9]:
            continue
        for line in page['tesseractText'].splitlines():
            role = ROLE.search(line)
            if not role or ',' not in line[:role.start()]:
                continue
            suffix = line[role.end():]
            money = DECIMAL_MONEY.search(suffix)
            assert money, line
            title = role.group(1)
            result.append({'name': clean(line[:role.start()]), 'position': title,
                           'remuneration': money.group().replace(',', ''),
                           'expenses': cash(suffix[money.end():]), 'pdfPage': number,
                           'category': 'school-trustees' if title == 'TRUSTEE' else 'employee-remuneration',
                           'rawSourceLine': line})
    return result


def paddle_rows(pages):
    result = []
    for page in pages:
        number = page['physicalPage']
        if number not in [8, 9]:
            continue
        groups = []
        for box, text, confidence in sorted(page['rapidOcrRaw'], key=lambda r: sum(p[1] for p in r[0])/4):
            y = sum(p[1] for p in box)/4
            if not ((830 < y < 1090 or 1380 < y < 2840) if number == 8 else 720 < y < 2120):
                continue
            group = next((g for g in groups[-3:] if abs(g['y']-y) < 8), None)
            if group is None:
                group = {'y': y, 'boxes': []}
                groups.append(group)
            group['boxes'].append({'box': box, 'text': text, 'confidence': confidence})
        for group in groups:
            cells = [[] for _ in range(4)]
            for word in sorted(group['boxes'], key=lambda w: min(p[0] for p in w['box'])):
                cells[sum(min(p[0] for p in word['box']) >= x for x in [965, 1570, 2025])].append(word['text'])
            name, title, pay, expense = [clean(' '.join(c)) for c in cells]
            result.append({'name': name, 'position': title, 'remuneration': cash(pay), 'expenses': cash(expense),
                           'pdfPage': number, 'category': 'school-trustees' if number == 8 and group['y'] < 1100 else 'employee-remuneration',
                           'sourceY300dpi': group['y'], 'rawSourceBoxes': group['boxes']})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--check-amendments', action='store_true')
    args = parser.parse_args()
    path = AREA/'bounded-original-ocr.json.gzip'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == RAW_SHA
    pages = [p for p in json.loads(gzip.decompress(path.read_bytes()))['pages'] if p['key'] == 'sd50-2025']
    first = tesseract_rows(pages)
    second = paddle_rows(pages)
    differences = []
    for i in range(max(len(first), len(second))):
        a = [first[i][f] for f in FIELDS] if i < len(first) else None
        b = [second[i][f] for f in FIELDS] if i < len(second) else None
        if a != b:
            differences.append({'sequence': i+1, 'tesseract': a, 'paddle': b})
    out = {'sourceSha256': '7a45c601bc2edf00849d090f24394d032e84424ea7c42804ae188b74780973a4',
           'rawBothEngineSha256': RAW_SHA, 'tesseractRows': first, 'paddleRows': second, 'differencesBeforeImageAmendments': differences,
           'acceptedRows': 0}
    raw = (json.dumps(out, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
    output = AREA/'sd50-2025-both-reader-fields.json.gzip'
    blob = gzip.compress(raw, mtime=0)
    if args.check or args.check_amendments:
        assert output.read_bytes() == blob, 'Raw independent OCR parsing replay differs'
    else:
        if output.exists():
            raise ValueError('Raw reader proof immutable; use --check')
        output.write_bytes(blob)
    if args.check_amendments:
        proof = json.loads(gzip.decompress((AREA/'sd50-2025-image-checked-candidate-v2.json.gzip').read_bytes()))
        for engine, rows, key in [('tesseract', first, 'tesseractRows'), ('paddle', second, 'paddleRows')]:
            for amendment in proof['imageVerifiedAmendments']:
                if amendment['engine'] != engine:
                    continue
                row = rows[amendment['sequence']-1]
                assert row['pdfPage'] == amendment['pdfPage']
                assert row[amendment['field']] == amendment['before']
                row[amendment['field']] = amendment['after']
            assert [[r[f] for f in FIELDS] for r in rows] == [[r[f] for f in FIELDS] for r in proof[key]], 'Original-image amendment replay differs'
    summary = {'rows': [len(first), len(second)], 'rawReaderFieldDisagreements': len(differences)}
    if args.check_amendments:
        summary.update(originalImageAmendmentReplay='PASS', allFinalAmendedFieldsAgree=True)
    elif not args.check:
        summary['differences'] = differences
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
