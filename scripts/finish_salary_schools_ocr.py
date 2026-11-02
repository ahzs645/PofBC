#!/usr/bin/env python3
"""Bounded school image capture, using the reserved single OCR worker only."""
import argparse
import gzip
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/schools'
CACHE = Path('/tmp/queue-completion-schools')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def render(plan):
    import fitz
    documents = {}
    out = []
    for entry in plan:
        path = Path(entry['pdfPath'])
        assert sha(path.read_bytes()) == entry['sourceSha256']
        if str(path) not in documents:
            documents[str(path)] = fitz.open(path)
        page = documents[str(path)][entry['physicalPage']-1]
        image_path = CACHE/(entry['key']+'-p'+str(entry['physicalPage'])+'-300dpi.png')
        page.get_pixmap(dpi=300).save(image_path)
        out.append({**entry, 'imagePath': str(image_path), 'imageSha256': sha(image_path.read_bytes()),
                    'renderMethod': 'actual PDF page.get_pixmap(dpi=300), preserving original clipping/masks'})
    (AREA/'bounded-ocr-image-plan.json').write_text(json.dumps(out, indent=2)+'\n')


def capture(plan):
    for key in ('OMP_THREAD_LIMIT', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[key] = '1'
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR(intra_op_num_threads=1, inter_op_num_threads=1, max_side_len=4096)
    output = []
    for entry in plan:
        path = Path(entry['imagePath'])
        assert sha(path.read_bytes()) == entry['imageSha256']
        text = subprocess.check_output(['tesseract', str(path), 'stdout', '--psm', '6'], stderr=subprocess.DEVNULL).decode()
        result = {**entry, 'tesseractText': text}
        if entry.get('independentSalaryOcr'):
            boxes, elapsed = engine(str(path))
            result.update(rapidOcrRaw=boxes, rapidOcrElapsedSeconds=elapsed)
        output.append(result)
        print(entry['key'], entry['physicalPage'], 'captured', flush=True)
    raw = (json.dumps({'capturedOn': '2026-11-01', 'engineReaders': ['Tesseract5.5 PSM6', 'RapidOCR1.4.4 Paddle PP-OCR ONNX'],
                       'threadCaps': 1, 'overlappingOcrInference': False, 'pages': output, 'acceptedRows': 0}, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
    path = AREA/'bounded-original-ocr.json.gzip'
    path.write_bytes(gzip.compress(raw, mtime=0))
    print('receipt', sha(path.read_bytes()), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', type=Path)
    parser.add_argument('--capture', action='store_true')
    args = parser.parse_args()
    if args.render:
        render(json.loads(args.render.read_text()))
    if args.capture:
        capture(json.loads((AREA/'bounded-ocr-image-plan.json').read_text()))


if __name__ == '__main__':
    main()
