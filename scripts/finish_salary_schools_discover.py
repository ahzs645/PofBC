#!/usr/bin/env python3
"""Additive school public-record acquisition and registered-scope inventory.

No old collections, registry, generated exports or institutional contacts change.
The network acquisition command follows public official links only. Its receipts
remain discovery evidence until a complete named schedule is separately checked.
"""
import argparse
import concurrent.futures
import hashlib
import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/queue-completion-2026-11-01/schools'
CACHE = Path('/tmp/queue-completion-schools')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current = {'url': dict(attrs).get('href', ''), 'text': ''}

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.links.append(self.current)
            self.current = None


def retrieve(item):
    key, url = item['key'], item['url']
    CACHE.mkdir(exist_ok=True)
    result = dict(item)
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            result.update(httpStatus=response.status, finalUrl=response.url)
    except urllib.error.HTTPError as error:
        raw = error.read()
        result.update(httpStatus=error.code, finalUrl=error.url)
    except Exception as error:
        return {**result, 'error': str(error)}
    suffix = '.pdf' if raw.startswith(b'%PDF') else '.json' if raw[:1] in (b'[', b'{') else '.html'
    path = CACHE / (key + suffix)
    path.write_bytes(raw)
    result.update(cachePath=str(path), sha256=sha(raw), bytes=len(raw))
    if suffix == '.html':
        parser = Links()
        parser.feed(raw.decode(errors='replace'))
        result['links'] = [{'url': urljoin(result['finalUrl'], link['url']),
                            'text': ' '.join(link['text'].split())} for link in parser.links]
    elif suffix == '.pdf':
        import fitz
        document = fitz.open(path)
        result['pdfPages'] = len(document)
        result['nativeRelevantPages'] = [
            {'physicalPage': i + 1, 'text': page.get_text()}
            for i, page in enumerate(document)
            if re.search(r'\bSOFI\b|statement of financial information|corrected|remuneration', page.get_text(), re.I)
        ]
    return result


def acquisition(plan):
    if (AREA/'candidate-freeze.json').exists():
        raise ValueError('Public research frozen; use --verify-receipts')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(retrieve, plan))
    AREA.mkdir(parents=True, exist_ok=True)
    (AREA / 'public-route-receipts.json').write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + '\n')
    return receipts


def inventory():
    registered = []
    collections = json.loads((ROOT / 'research/salaries/collections.json').read_text())['collections']
    inputs = []
    for collection in collections:
        path = ROOT / 'research/salaries' / collection / 'sources.json'
        inputs.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())})
        registered += [s for s in json.loads(path.read_text())['sources'] if s.get('sector') == 'School districts']
    old = json.loads((ROOT / 'research/salaries/continuation-2026-11-01/schools/inventory.json').read_text())
    employers = []
    for employer in old['employers']:
        accepted = [s for s in registered if s['employerSlug'] == employer['employerSlug']]
        missing = [category for category in ('employee-remuneration', 'school-trustees')
                   if not any(s['year'] == '2024/25' and s['category'] == category for s in accepted)]
        employers.append({'districtNumber': employer['districtNumber'], 'employerSlug': employer['employerSlug'],
                          'employerName': employer['employerName'], 'registeredSourceIds': [s['id'] for s in accepted],
                          'current2024_25MissingCategories': missing,
                          'currentOriginalCandidate': employer['currentOfficialSource'],
                          'districtOriginalCandidates': [s for s in employer['sourceCandidates']
                                                         if s.get('sourceKind') != 'official-ministry-convenience-copy']})
    return {'auditDate': '2026-11-01', 'basis': 'Actual registered original source scopes, not represented/compiled employer count.',
            'registeredSchoolScopes': len(registered), 'registeredSchoolEmployers': len({s['employerSlug'] for s in registered}),
            'registeredCollectionInputs': inputs, 'employers': employers}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch-plan', type=Path)
    parser.add_argument('--inventory', action='store_true')
    parser.add_argument('--verify-receipts', action='store_true')
    args = parser.parse_args()
    if args.fetch_plan:
        result = acquisition(json.loads(args.fetch_plan.read_text()))
        print(json.dumps({'receipts': len(result), 'successful': sum(r.get('httpStatus') == 200 for r in result)}))
    if args.inventory:
        if (AREA/'candidate-freeze.json').exists():
            raise ValueError('Baseline school inventory frozen')
        result = inventory()
        AREA.mkdir(parents=True, exist_ok=True)
        (AREA / 'registered-gap-inventory.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({k: v for k, v in result.items() if k not in ('employers', 'registeredCollectionInputs')}))
    if args.verify_receipts:
        receipts = json.loads((AREA/'public-route-receipts.json').read_text())
        for receipt in receipts:
            if receipt.get('cachePath'):
                assert sha(Path(receipt['cachePath']).read_bytes()) == receipt['sha256']
        print(json.dumps({'publicReceiptsFingerprintReplay': 'PASS', 'receipts': len(receipts), 'networkRequests': 0}))


if __name__ == '__main__':
    main()
