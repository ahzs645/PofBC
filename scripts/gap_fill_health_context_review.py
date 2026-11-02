#!/usr/bin/env python3
"""Root's independent, pinned source-context replay and control review aids.

This prepares evidence, not source acceptance. Personal image observations and
the separate field-exception peer review must be recorded before acceptance.
"""
import collections
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re

import fitz

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02'
OUT = AREA / 'reviews/health-context-root'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def control(context):
    for row in context['allPrintedControls']:
        if re.search(r'equal.*greater|greater.*75|over.*75|(?:total|employees)\s*>\s*\$?75|remuneration exceeding', row['label'], re.I):
            return row
    return None


def norm_money(text):
    return text.replace(',', '').replace('$', '').strip()


def main():
    from PIL import Image, ImageDraw
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'source-context-replay.json'
    assert not output.exists(), 'Preserve evidence and issue an additive version'
    context_path = AREA / 'health_employees/source-context-review-packet.json'
    image_path = AREA / 'health_employees/source-context-image-index.json'
    ocr_path = AREA / 'reviews/health-context-ocr/index.json'
    contexts = json.loads(context_path.read_bytes())['sources']
    images = {s['key']: s for s in json.loads(image_path.read_bytes())['sources']}
    ocr = json.loads(ocr_path.read_bytes())
    ocr_by = {(e['sourceKey'], e['physicalPage']): e for e in ocr['results']}
    results = []
    strips = []
    for context in contexts:
        key = context['key']
        source = Path(context['sourceCachePath'])
        assert sha(source.read_bytes()) == context['sourceSha256']
        doc = fitz.open(source)
        replayed = []
        for image in images[key]['images']:
            path = ROOT / image['path']
            assert sha(path.read_bytes()) == image['sha256']
            pix = doc[image['physicalPage'] - 1].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            assert sha(pix.samples) == image['rawPixelSha256']
            with Image.open(path) as original:
                assert original.size == (pix.width, pix.height)
                assert original.convert('RGB').tobytes() == pix.samples
            replayed.append(ref(path))
        first = context['employeePhysicalPages'][0]
        ocr_ref = ocr_by[(key, first)]
        assert sha((ROOT / ocr_ref['path']).read_bytes()) == ocr_ref['sha256']
        ocr_data = json.loads(gzip.decompress((ROOT / ocr_ref['path']).read_bytes()))
        pairs = ocr_data['headerFiscalPairs']
        start = context['candidateYear'][:4]
        end = context['expectedYearEnd']
        matching_pair = any(a == start and b in (end, end[-2:]) for a, b in pairs)
        assert end in ocr_data['headerMarchYearEnds'] or matching_pair, (key, 'Period not corroborated by independent image reader')
        named = control(context)
        residual = None
        view = None
        if named:
            residual = [str(Decimal(context['candidateRemunerationSum']) - Decimal(str(named['remuneration']))),
                        str(Decimal(context['candidateKnownExpenseSum']) - Decimal(str(named['expenses'] or 0)))]
            page = doc[named['physicalPage'] - 1]
            words = page.get_text('words')
            targets = []
            expected = Decimal(str(named['remuneration']))
            for word in words:
                try:
                    value = Decimal(norm_money(word[4]))
                except Exception:
                    continue
                if value == expected:
                    rect = fitz.Rect(word[:4]) * page.rotation_matrix
                    targets.append(rect)
            assert len(targets) == 1, (key, 'Control location ambiguous', targets)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            full = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            y = (targets[0].y0 + targets[0].y1)
            box = [0, max(0, int(y) - 55), pix.width, min(pix.height, int(y) + 115)]
            cropped = full.crop(box)
            dest = OUT / (key + '-named-control.png')
            cropped.save(dest)
            view = {**ref(dest), 'sourceSha256': context['sourceSha256'], 'physicalPage': named['physicalPage'],
                    'dpi': 144, 'integerCropBox': box, 'noResampling': True,
                    'purpose': 'Named control and surrounding original source pixels; crop located from literal control token, not a replacement source'}
            strips.append((key, cropped, view))
        results.append({'sourceKey': key, 'sourceSha256': context['sourceSha256'],
                        'candidateYear': context['candidateYear'], 'candidateRowsBeforeFinalPeerClosure': context['candidateEmployeeRows'],
                        'sourceImagesPixelReplayed': replayed, 'independentImagePeriodOcr': ocr_ref,
                        'periodImageCorroborationPassed': True, 'printedNamedControl': named,
                        'literalResidualBeforeFinalPeerClosure': residual,
                        'controlSelectionAddendum': named != context['printedNamedControlCandidate'],
                        'namedControlViewingAid': view})
        doc.close()
    sheets = []
    for start in range(0, len(strips), 7):
        group = strips[start:start + 7]
        canvas = Image.new('RGB', (max(v.width for _, v, _ in group), sum(v.height + 26 for _, v, _ in group)), 'white')
        draw = ImageDraw.Draw(canvas)
        y = 0
        for key, value, view in group:
            draw.text((4, y + 4), key + ' — literal named control', fill='black')
            y += 26
            canvas.paste(value, (0, y))
            y += value.height
        dest = OUT / ('named-controls-' + str(start + 1).zfill(2) + '-' + str(start + len(group)).zfill(2) + '.png')
        canvas.save(dest)
        sheets.append({**ref(dest), 'sourceCrops': [view for _, _, view in group], 'noResampling': True})
    receipt = {'status': 'Independent evidence replay complete; awaiting personal control-strip review and separate row-exception closure',
               'sourceCount': len(results), 'sourceImagesReplayed': sum(len(s['sourceImagesPixelReplayed']) for s in results),
               'inputs': [ref(context_path), ref(image_path), ref(ocr_path), ref(Path(__file__))],
               'sources': results, 'controlViewingSheets': sheets,
               'scope': 'Original raster and independent image-OCR period corroboration for all sources, plus literal named-control selection. Does not assert a personal transcription of every row.'}
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sources': len(results), 'replayedOriginalImages': receipt['sourceImagesReplayed'],
                      'controls': len(strips), 'controlSheets': len(sheets),
                      'controlAddenda': [(r['sourceKey'], r['literalResidualBeforeFinalPeerClosure']) for r in results if r['controlSelectionAddendum']]}))


if __name__ == '__main__':
    main()
