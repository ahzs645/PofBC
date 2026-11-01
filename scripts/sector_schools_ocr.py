#!/usr/bin/env python3
"""Stage two-layout OCR of pinned scanned SD42 originals; never accept salary rows."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/salaries/sector-schools/reviewed-inputs.json'
DEFAULT_OUTPUT = ROOT / 'research/salaries/sector-search-2026-10-31/schools/ocr-staging'


def ocr_page(task):
    pdf, physical_page, dpi = task
    with fitz.open(pdf) as document:
        png = document[physical_page - 1].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False).tobytes('png')
    env = dict(os.environ, OMP_THREAD_LIMIT='1')
    def read(psm):
        result = subprocess.run(['tesseract', 'stdin', 'stdout', '-l', 'eng', '--psm', str(psm)], input=png, capture_output=True, env=env, check=True)
        return result.stdout.decode('utf8', 'replace')
    first = read(3)
    candidate = bool(re.search(r'remun|remuncr|trustee|employees.{0,60}75[, .]?000', first, re.I | re.S))
    second = read(6) if candidate else None
    return {'physicalPage': physical_page, 'renderDpi': dpi, 'renderSha256': hashlib.sha256(png).hexdigest(), 'salaryCandidate': candidate, 'psm3': first, 'psm6': second}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, default=ROOT / '.cache/sector-schools')
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--dpi', type=int, default=160)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    receipts = []
    version = subprocess.check_output(['tesseract', '--version'], text=True).splitlines()[0]
    for item in json.loads(MANIFEST.read_text())['inputs']:
        if item['status'] != 'ocr-needed':
            continue
        pdf = args.cache_dir / item['cacheFile']
        if not pdf.exists() and args.download:
            request = urllib.request.Request(item['retrievedUrl'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=90) as response:
                pdf.write_bytes(response.read())
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Changed original: {pdf}')
        with fitz.open(pdf) as document:
            count = len(document)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            pages = list(pool.map(ocr_page, [(pdf, number, args.dpi) for number in range(1, count + 1)]))
        record = {'reviewed': '2026-10-31', 'sourceUrl': item['sourceUrl'], 'sourceSha256': item['sha256'], 'endingYear': item['endingYear'], 'engine': version, 'status': 'ocr-discovery-only-not-accepted', 'nextAction': 'Review full rendered salary cohort boundaries and all row fields; independently validate names, signs, columns, period and controls. Two layout modes of one OCR engine do not constitute independent reader acceptance.', 'pages': pages}
        name = f"sd42-{item['endingYear']}.json.gzip"
        data = gzip.compress(json.dumps(record, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)
        (args.output_dir / name).write_bytes(data)
        receipt = {'endingYear': item['endingYear'], 'sourceUrl': item['sourceUrl'], 'sourceSha256': item['sha256'], 'pages': count, 'salaryCandidatePages': [p['physicalPage'] for p in pages if p['salaryCandidate']], 'file': name, 'sha256': hashlib.sha256(data).hexdigest(), 'status': record['status']}
        receipts.append(receipt)
        (args.output_dir / 'index.json').write_text(json.dumps({'reviewed': '2026-10-31', 'complete': False, 'sources': receipts}, indent=2) + '\n')
        print(item['endingYear'], count, 'pages', len(receipt['salaryCandidatePages']), 'salary candidates', flush=True)
    (args.output_dir / 'index.json').write_text(json.dumps({'reviewed': '2026-10-31', 'complete': True, 'sources': receipts}, indent=2) + '\n')


if __name__ == '__main__':
    main()
