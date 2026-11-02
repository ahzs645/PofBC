#!/usr/bin/env python3
"""Save every metadata result for two bounded public Rossland approval queries."""
import concurrent.futures
import json
import urllib.parse
import urllib.request
from pathlib import Path

AREA = Path(__file__).resolve().parents[1] / 'research/salaries/gap-fill-2026-11-02/municipal'


def request(spec):
    key, page, params = spec
    url = 'https://rossland.civicweb.net/api/documents/search?' + urllib.parse.urlencode({
        **params, 'page': page, 'ordercolumn': 'relevance', 'orderascending': 'false'})
    with urllib.request.urlopen(url, timeout=45) as response:
        result = json.load(response)
    target = AREA / 'routes' / f'api-{key}-page{page}.json'
    target.write_text(json.dumps({'url': url, 'response': result}, ensure_ascii=False, indent=2) + '\n')
    return {'query': key, 'page': page, 'total': result['Total'], 'results': result['Results']}


def main():
    specs = []
    for key, pages, params in [
        ('approval-statement2015', 6, {'all': '2015', 'exact': 'Statement of Financial Information'}),
        ('approval-june22-2015', 9, {'all': '2015', 'exact': 'June 22'})]:
        specs.extend((key, p, params) for p in range(1, pages + 1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(request, specs))
    (AREA / 'approval-search-all-metadata.json').write_text(json.dumps({
        'noOutreach': True, 'method': 'Public CivicWeb GET search metadata only; a result is not adoption evidence.',
        'pages': results}, ensure_ascii=False, indent=2) + '\n')
    for result in results:
        for row in result['results']:
            if '2015' in row['TitleHtml'] or '2014' in row['TitleHtml']:
                print(row['Id'], row['TitleHtml'])


if __name__ == '__main__':
    main()
