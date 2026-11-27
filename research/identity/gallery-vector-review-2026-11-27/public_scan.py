"""Check publisher sources and find related publication and artwork leads for the recorded baseline.

Run with Python 3 and PyMuPDF. The first argument is a writable cache outside the repository.
HTTP and PDF results describe the retrieved file, not whether its logo is an exact match.
"""
import csv
import hashlib
import io
import json
import re
import sys
import threading
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urljoin, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import pymupdf

ROOT = Path(__file__).resolve().parent
CACHE = Path(sys.argv[1])
CACHE.mkdir(exist_ok=True, parents=True)
LIBRARY = 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api'
MAX_BYTES = 14 * 1024 * 1024
limits = defaultdict(lambda: threading.Semaphore(4))
requests = {}
html_candidates = {}
library_hits = {}
pdf_lock = threading.Lock()
pymupdf.TOOLS.mupdf_display_errors(False)
pymupdf.TOOLS.mupdf_display_warnings(False)
inputs = list(csv.DictReader((ROOT / 'public-sweep-input.csv').open()))
traces = {r['Design ID']: {} for r in inputs}


def canonical(url):
    try:
        p = urlsplit(url.strip())
        if p.scheme not in ('https', 'http') or not p.hostname:
            return ''
        return urlunsplit((p.scheme, p.netloc, quote(p.path or '/', safe="/%:@;=,+()!$&'*-._~"), p.query, ''))
    except ValueError:
        return ''


def fetch(url):
    key = hashlib.sha256(url.encode()).hexdigest()
    meta = CACHE / (key + '.json')
    body = CACHE / (key + '.bin')
    if meta.exists():
        m = json.loads(meta.read_text())
        return m, body.read_bytes() if body.exists() else b''
    out = b''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; public design bibliography review)', 'Accept': '*/*'})
        with limits[urlsplit(url).hostname], urlopen(req, timeout=18) as response:
            kind = response.headers.get_content_type()
            size = response.headers.get('Content-Length')
            if size and int(size) > MAX_BYTES:
                m = {'status': 'Over 14 MiB', 'type': kind, 'url': response.geturl()}
            else:
                out = response.read(MAX_BYTES + 1)
                m = {'status': str(response.status), 'type': kind, 'url': response.geturl()}
                if len(out) > MAX_BYTES:
                    m['status'] = 'Over 14 MiB'
                    out = b''
    except (OSError, ValueError, HTTPError) as exc:
        m = {'status': 'HTTP ' + str(exc.code) if isinstance(exc, HTTPError) else type(exc).__name__, 'type': '', 'url': url}
    if out:
        body.write_bytes(out)
    meta.write_text(json.dumps(m))
    return m, out


def linked_score(url, label):
    s = (urlsplit(url).path + ' ' + label).lower()
    if re.search(r'facebook|pinterest|instagram|linkedin|twitter|\.woff|/plugins/|/wp-admin|googleapis', url):
        return 0
    if re.search(r'logo|wordmark|signature|identit|brand|media.kit|press.kit', s):
        if re.search(r'\.(?:svg|ai|eps|zip|pdf)(?:$|\W)', s):
            return 12
        if not re.search(r'\.(?:jpe?g|webp|gif|png|css|js)(?:$|\W)', s):
            return 7
    if re.search(r'annual.report|annual.review|strategic.plan|graphic.standards|accountability.report|annualreport', s):
        return 9 if '.pdf' in s else 6
    if re.search(r'\.svg(?:$|\W)', s) and not re.search(r'icon|hamburger|sprite|arrow|\.min\.', s):
        return 4
    if re.search(r'/media/?$|newsroom|publications|annual-reports', s):
        return 3
    return 0


class Links(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.out = {}
        self.inline = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        label = ' '.join(str(a.get(k) or '') for k in ('class', 'id', 'alt', 'title', 'aria-label'))
        if tag == 'svg' and re.search(r'logo|brand|wordmark', label, re.I):
            self.inline += 1
        for k in ('href', 'src', 'data-src'):
            raw = a.get(k)
            if not raw or raw.startswith(('#', 'javascript:', 'mailto:', 'data:')):
                continue
            url = canonical(urljoin(self.base, raw))
            if not url:
                continue
            score = linked_score(url, label)
            if score:
                self.out[url] = max(score, self.out.get(url, 0))


def inspect(url):
    m, data = fetch(url)
    category = m['type'] or 'Unavailable'
    details = ''
    if not data:
        return m['status'], category, details
    if data.startswith(b'%PDF-'):
        category = 'PDF'
        try:
            # MuPDF uses global state; parse one document at a time.
            with pdf_lock, pymupdf.open(stream=data, filetype='pdf') as doc:
                page = doc[0]
                details = f'{len(doc)} pages; cover has {len(page.get_images())} raster objects and {len(page.get_drawings())} path groups'
        except Exception as exc:
            details = 'Cover analysis unavailable: ' + type(exc).__name__
    elif re.search(rb'<svg(?:\s|>)', data[:3000], re.I) and b'<html' not in data[:3000].lower():
        category = 'SVG'
        details = 'Contains image reference' if re.search(rb'<(?:[\w-]+:)?(?:feImage|image)\b', data, re.I) else 'No bitmap image element found'
    elif data.startswith(b'PK\x03\x04'):
        category = 'ZIP'
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                names = [n for n in z.namelist() if re.search(r'\.(svg|eps|ai|pdf)$', n, re.I)]
                details = f'{len(names)} vector-capable files; ' + ', '.join(names[:4])
        except zipfile.BadZipFile:
            details = 'ZIP directory unavailable'
    elif 'html' in category or b'<html' in data[:3000].lower():
        category = 'HTML'
        parser = Links(m['url'])
        parser.feed(data.decode('utf-8', errors='replace'))
        html_candidates[url] = sorted(parser.out, key=lambda u: -parser.out[u])
        details = f'{len(parser.out)} publication/brand links; {parser.inline} inline SVGs with logo or brand labels'
    elif data[:4] == b'\x89PNG' or data[:2] == b'\xff\xd8' or data[:3] == b'GIF' or data[8:12] == b'WEBP':
        category = 'Raster file'
    return m['status'], category, details


def stage(stage_name, links):
    unique = set()
    for key, urls in links.items():
        for u in urls:
            url = canonical(u)
            if url:
                traces[key].setdefault(url, stage_name)
                unique.add(url)
    def run(u):
        try:
            return u, inspect(u)
        except Exception as exc:
            return u, ('Analysis error', '', type(exc).__name__)
    todo = sorted(unique - requests.keys())
    with ThreadPoolExecutor(20) as pool:
        for u, record in pool.map(run, todo):
            requests[u] = record
    print(stage_name, len(todo), 'new requests', flush=True)


def library_query(r, size=10):
    name = r['Publisher search name']
    if r['Design ID'].startswith('school-district-'):
        number = re.search(r'school-district-(\d+)', r['Design ID']).group(1)
        name = f'School District No. {number}'
    return LIBRARY + '/discover/search/objects?' + urlencode({'query': '"' + name + '"', 'size': size})


def words(s):
    return {w for w in re.findall(r'[a-z0-9]+', s.lower()) if len(w) > 2 and w not in
            {'the','and','british','columbia','canada','district','association','city','village','town','corporation','society','regional','school','office','ministry'}}


def parse_library(r):
    try:
        for url in library[r['Design ID']]:
            m, raw = fetch(url)
            if raw:
                break
        result = json.loads(raw)['_embedded']['searchResult']
        candidates = []
        needle = words(r['Publisher search name'])
        if not needle:
            return []
        for item in result.get('_embedded', {}).get('objects', []):
            v = item['_embedded']['indexableObject']
            title = v.get('name','')
            authors = ' '.join(a['value'] for a in v['metadata'].get('dc.contributor.author', []))
            overlap = len(needle & words(title+' '+authors)) / len(needle)
            if overlap < .6:
                continue
            rank = overlap + (0.4 if re.search('annual report|service plan|strategic plan', title, re.I) else 0)
            candidates.append((rank, v))
        return [v for _,v in sorted(candidates,key=lambda pair:-pair[0])[:2]]
    except (ValueError, KeyError):
        return []


def from_library(v):
    # Some records hold several versions. Inspect the first two PDFs in the original-file bundle.
    urls = []
    try:
        _, b = fetch(v['_links']['bundles']['href'])
        bundles = json.loads(b)['_embedded']['bundles']
        original = next((x for x in bundles if x['name'] == 'ORIGINAL'), None)
        if original:
            _, b = fetch(original['_links']['bitstreams']['href'])
            streams = json.loads(b).get('_embedded', {}).get('bitstreams', [])
            urls = [s['_links']['content']['href'] for s in streams if s['name'].lower().endswith('.pdf')][:2]
    except (ValueError, KeyError):
        pass
    return urls


seeded, sites, library = {}, {}, {}
for r in inputs:
    key = r['Design ID']
    links = [canonical(x) for x in r['Publisher and specimen URLs'].split(' | ')]
    seeded[key] = list(dict.fromkeys(u for u in links if u))[:5]
    sites[key] = []
    for u in seeded[key]:
        host = urlsplit(u).hostname or ''
        if host and not re.search(r'archive.org|llbc\.|gov.bc.ca|cloudfront|amazonaws|edl.io|simpleview|squarespace|sanity.io|blob.core|wixstatic|wikimedia|staticflickr', host):
            home = urljoin(u, '/')
            if home not in sites[key]:
                sites[key].append(home)
    library[key] = [library_query(r)]

stage('Cited source or specimen', seeded)
stage('Publisher website', sites)
stage('Legislative Library catalogue', library)
for r in inputs:
    key = r['Design ID']
    if requests[canonical(library[key][0])][0] != '200':
        library[key].append(library_query(r,5))
stage('Alternate catalogue result set', library)

search_results = defaultdict(list)
with (ROOT / 'public-search-leads.csv').open() as results:
    for result in csv.DictReader(results):
        if result['Result URL']:
            for key in result['Design IDs'].split(' | '):
                search_results[key].append(result['Result URL'])
stage('Independent public search result', search_results)

catalogue = {r['Design ID']:parse_library(r) for r in inputs}
unique_items = {v['uuid']:v for values in catalogue.values() for v in values}
with ThreadPoolExecutor(10) as workers:
    docs = dict(zip(unique_items, workers.map(from_library, unique_items.values())))
publications = {}
for key, items in catalogue.items():
    publications[key] = [u for v in items for u in docs.get(v['uuid'], [])]
    library_hits[key] = ['https://digitalcollections.llbc.leg.bc.ca/handle/'+v['handle'] for v in items]
stage('New library publication', publications)

for name in ('New publisher link', 'Link from publication or brand page'):
    found = {}
    for key, history in traces.items():
        choices = list(dict.fromkeys(u for page in history for u in html_candidates.get(page, [])[:5] if u not in history))
        found[key] = sorted(choices, key=lambda u:-linked_score(u,''))[:5]
    stage(name, found)


def write(filename, headers, rows):
    with (ROOT / filename).open('w', newline='') as output:
        w = csv.writer(output,lineterminator='\n')
        w.writerow(headers)
        w.writerows(rows)


write('public-sweep-requests.csv',['URL','HTTP or read status','Asset type','File-level evidence'],
      [[u,*requests[u]] for u in sorted(requests)])
write('public-sweep-designs.csv',['Design ID','Collection','Baseline light tile','Source requests','Successful responses',
      'New linked publication or asset requests','Library records with matching title or author','Requests by source'],
      [[r['Design ID'],r['Collection'],r['Baseline light tile'],len(t),sum(requests[u][0]=='200' for u in t),
        sum(s in ('Independent public search result','New library publication','New publisher link','Link from publication or brand page') for s in t.values()),
        ' | '.join(library_hits[r['Design ID']]),' | '.join(f'{stage}: {u}' for u,stage in t.items())]
       for r in inputs for t in [traces[r['Design ID']]]])
