#!/usr/bin/env python3
"""OCR the reviewed municipal scan/layout queue and archive candidates, never salary imports.

The register pins originals. Discovery examines every physical page; two detailed
OCR passes run on keyword candidates. Discovery is not a guarantee that every
salary table was recognized. Accepted rows need the separate reviewed importer.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
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
OUT = ROOT / 'research/salaries/municipal-ocr'
PATTERN = re.compile(r'remuner|\bsalari|\bsalary|\bemployees\b|\belected\b|\bpayroll\b|75[, .]000', re.I)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def packed(value):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)


def process_page(job):
    sid, number, scan, directory = job
    cache = Path(directory)
    base = cache / 'discovery' / f'{sid}-p{number:03}'
    try:
        doc = fitz.open(cache / (sid + '.pdf'))
        page = doc[number - 1]
        method = 'embedded-text'
        if scan:
            method = 'tesseract-110dpi-psm11'
            if not base.with_suffix('.txt').exists():
                raw = subprocess.check_output(['tesseract', 'stdin', 'stdout', '--dpi', '110', '--psm', '11'],
                    input=page.get_pixmap(dpi=110, colorspace=fitz.csGRAY).tobytes('png'),
                    env={**os.environ, 'OMP_THREAD_LIMIT': '1'}, stderr=subprocess.DEVNULL, timeout=45)
                base.with_suffix('.txt').write_bytes(raw)
            text = base.with_suffix('.txt').read_text()
        else:
            text = page.get_text()
            base.with_suffix('.txt').write_text(text)
        candidate = bool(PATTERN.search(text))
        result = {'sourceId': sid, 'physicalPage': number, 'discoveryMethod': method,
                  'candidate': candidate, 'discoverySha256': sha(text.encode())}
        if candidate:
            target = cache / 'tables' / f'{sid}-p{number:03}'
            for dpi, psm in [(250, 6), (300, 3)]:
                dest = Path(str(target) + f'-{dpi}dpi-psm{psm}')
                if not dest.with_suffix('.tsv').exists():
                    subprocess.run(['tesseract', 'stdin', str(dest), '--dpi', str(dpi), '--psm', str(psm), 'txt', 'tsv'],
                        input=page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY).tobytes('png'),
                        env={**os.environ, 'OMP_THREAD_LIMIT': '1'}, stderr=subprocess.DEVNULL, check=True, timeout=100)
            result['detailFiles'] = [target.name + f'-{dpi}dpi-psm{psm}.{ext}'
                                    for dpi, psm in [(250, 6), (300, 3)] for ext in ['txt', 'tsv']]
        return result
    except Exception as error:
        return {'sourceId': sid, 'physicalPage': number, 'error': str(error)}


def archive(originals, pages, cache):
    accepted = json.loads((OUT / 'sources.json').read_text())['sources']
    receipts = []
    (OUT / 'staging').mkdir(exist_ok=True)
    for original in originals:
        sid = original['id']
        selected = [page for page in pages if page['sourceId'] == sid]
        if len(selected) != original['pdfPages'] or len({p['physicalPage'] for p in selected}) != len(selected):
            raise ValueError(f'{sid}: incomplete or duplicate page discovery receipts')
        archived = []
        for page in selected:
            item = dict(page)
            if not item.get('error'):
                item['discoveryText'] = (cache / 'discovery' / f"{sid}-p{page['physicalPage']:03}.txt").read_text()
                item['detailContents'] = {name: (cache / 'tables' / name).read_text() for name in page.get('detailFiles', [])}
            archived.append(item)
        data = packed({'originalSha256': original['sha256'], 'pages': archived})
        filename = f'staging/{sid}.json.gzip'
        (OUT / filename).write_bytes(data)
        imported = [s for s in accepted if s['sourceUrl'] == original['sourceUrl']]
        receipts.append({**{k: original[k] for k in ['id', 'employerSlug', 'municipality', 'year', 'sourceUrl', 'archiveUrl', 'sha256', 'pdfPages', 'scanStatus']},
            'pageDiscoveryComplete': True, 'discoveryPages': len(selected),
            'pagesUsingOCRDiscovery': sum(p.get('discoveryMethod') != 'embedded-text' and not p.get('error') for p in selected),
            'candidatePages': [p['physicalPage'] for p in selected if p.get('candidate')],
            'errors': [p for p in selected if p.get('error')], 'evidenceFile': filename, 'evidenceSha256': sha(data),
            'acceptedSourceIds': [s['id'] for s in imported], 'acceptedRows': sum(s['rowCount'] for s in imported),
            'acceptedScopes': sorted({s['category'] for s in imported}),
            'status': 'reviewed-imports-with-retained-ocr' if imported else 'ocr-candidates-awaiting-row-and-control-review'})
    result = {'version': 1, 'asOf': '2026-10-31', 'ocrEngine': subprocess.check_output(['tesseract', '--version'], text=True).splitlines()[0],
        'discoveryCaveat': 'Keyword discovery covers every physical page but is not proof of exhaustive salary-table identification. OCR candidates, including incidental financial/supplier pages, are not imported salary rows.',
        'summary': {'reports': len(receipts), 'physicalPages': len(pages),
                    'candidatePages': sum(len(r['candidatePages']) for r in receipts),
                    'processingErrors': sum(len(r['errors']) for r in receipts),
                    'reportsWithReviewedImports': sum(bool(r['acceptedRows']) for r in receipts),
                    'acceptedRows': sum(r['acceptedRows'] for r in receipts)}, 'sources': receipts}
    (OUT / 'ocr-register.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-ocr'))
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--archive-existing', action='store_true', help='Package an already completed page-register.json without running OCR again')
    args = parser.parse_args()
    originals = json.loads((OUT / 'originals.json').read_text())
    args.cache.mkdir(parents=True, exist_ok=True)
    for original in originals:
        path = args.cache / (original['id'] + '.pdf')
        if not path.exists() and args.fetch:
            with urllib.request.urlopen(urllib.request.Request(original['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as response:
                path.write_bytes(response.read())
        if sha(path.read_bytes()) != original['sha256']:
            raise ValueError(f"{original['id']}: original fingerprint changed")
    if args.archive_existing:
        pages = json.loads((args.cache / 'page-register.json').read_text())
    else:
        for directory in ['discovery', 'tables']:
            (args.cache / directory).mkdir(exist_ok=True)
        jobs = [(r['id'], i + 1, n < 100 or r['scanStatus'] == 'image-or-no-text', str(args.cache))
                for r in sorted(originals, key=lambda r: (0 if 'municipal-small' in r['id'] or r['id'].startswith('terrace') else 1, r['pdfPages']))
                for i, n in enumerate(r['textCharsByPage'])]
        pages = []
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for page in pool.map(process_page, jobs):
                pages.append(page)
                if len(pages) % 50 == 0:
                    print(f'{len(pages)}/{len(jobs)} pages processed', flush=True)
        (args.cache / 'page-register.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n')
    archive(originals, pages, args.cache)


if __name__ == '__main__':
    main()
