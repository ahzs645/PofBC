#!/usr/bin/env python3
"""Inventory BC municipal salary source links without certifying their contents.

The roster is derived from the Province's legal-name workbook and CivicInfo's
directory. Discovery follows public official-site links only, with a bounded
request budget. A successful link search is never an accepted salary import.
Network collection is explicit; the salary build remains entirely offline.
"""
import argparse
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-audit'
AS_OF = '2026-10-31'
ROSTER_URL = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/local-governments/finance/local-government-statistics/legal_name_and_incorporation_2024.xlsx'
DIRECTORY_URL = 'https://www.civicinfo.bc.ca/municipalities'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def key(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '', value)


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()).strip('-')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def make_roster(workbook, directory):
    from openpyxl import load_workbook
    directory_rows = json.loads(directory.read_text())
    roster, region = [], None
    for row in load_workbook(workbook, data_only=True).active.values:
        if row[0] and (row[0].endswith('Regional District') or row[0].startswith('Regional District')):
            region = row[0]
        raw = row[1]
        if row[0] == 'Northern Rockies Regional Municipality':
            raw, region = 'Northern Rockies, Regional Municipality', 'Northern Rockies Regional Municipality'
        if not raw:
            continue
        place, suffix = raw.split(',', 1)
        place = place.split(' - ')[0].strip()
        if place == 'shíshálh Nation Government District':
            kind, employer_name = 'Indigenous government district', place
        elif place == 'Northern Rockies':
            kind, employer_name = 'Regional municipality', 'Northern Rockies Regional Municipality'
        elif place == 'Bowen Island':
            kind, employer_name = 'Island municipality', 'Bowen Island Municipality'
        elif place == 'Whistler':
            kind, employer_name = 'Resort municipality', 'Resort Municipality of Whistler'
        elif place == 'Sun Peaks':
            kind, employer_name = 'Mountain resort municipality', 'Sun Peaks Mountain Resort Municipality'
        else:
            kind = re.search(r'\b(City|Township|Town|District|Village)\b', suffix).group(1)
            employer_name = f'{kind} of {place}'
        employer_slug = {'Bowen Island': 'bowen-island'}.get(place, slug(employer_name))
        if employer_name == 'Township of Langley':
            employer_slug = 'langley-township'
        candidates = [r for r in directory_rows if key(r['name'].split('(')[0]) == key(place)]
        if len(candidates) > 1:
            candidates = [r for r in candidates if kind.lower() in r['name'].lower() or (kind == 'Township' and '(district)' in r['name'].lower())]
        if len(candidates) != 1:
            raise ValueError(f'Unresolved official directory identity: {raw}: {candidates}')
        directory_row = candidates[0]
        roster.append({
            'municipality': place, 'employerSlug': employer_slug, 'employerName': employer_name,
            'governmentType': kind, 'regionalDistrict': region, 'legalNameInWorkbook': raw.strip(),
            'incorporationDateInWorkbook': row[2], 'website': directory_row['url'],
            'directoryUrl': f"{DIRECTORY_URL}?id={directory_row['id']}",
            'status': 'special-governance' if place == 'shíshálh Nation Government District' else 'current',
        })
    if len(roster) != 161 or len({r['employerSlug'] for r in roster}) != 161:
        raise ValueError('The reviewed provincial roster must contain 161 distinct entries')
    pending = next(r for r in directory_rows if r['name'].startswith('Okanagan Falls'))
    roster.append({
        'municipality': 'Okanagan Falls', 'employerSlug': 'district-of-okanagan-falls',
        'employerName': 'District of Okanagan Falls', 'governmentType': 'District',
        'regionalDistrict': 'Regional District of Okanagan-Similkameen', 'website': pending['url'],
        'directoryUrl': f"{DIRECTORY_URL}?id={pending['id']}", 'status': 'pending-incorporation',
        'effectiveFrom': '2026-11-06',
        'statusSourceUrl': 'https://news.gov.bc.ca/releases/2026HMA0069-000747',
        'notes': ['Already listed by CivicInfo, but the Province specifies incorporation on 6 November 2026. Do not count earlier municipal salary years as missing.'],
    })
    roster.sort(key=lambda r: (key(r['municipality']), r['governmentType']))
    inputs = OUT / 'inputs'
    inputs.mkdir(parents=True, exist_ok=True)
    (inputs / 'legal_name_and_incorporation_2024.xlsx').write_bytes(workbook.read_bytes())
    save(inputs / 'civicinfo-directory.json', directory_rows)
    value = {
        'version': 1, 'asOf': AS_OF,
        'sources': [{'url': ROSTER_URL, 'file': 'inputs/legal_name_and_incorporation_2024.xlsx', 'sha256': digest(workbook.read_bytes())},
                    {'url': DIRECTORY_URL, 'file': 'inputs/civicinfo-directory.json', 'retrievedOn': AS_OF}],
        'scopeNotes': [
            'The 2024 provincial workbook has 160 entries in its municipal-name column, including shíshálh Nation Government District, plus Northern Rockies Regional Municipality in the first column.',
            'The directory has 162 entries because it already includes the pending District of Okanagan Falls. It is excluded from the current-coverage denominator as of 31 October 2026.',
            'The roster preserves shíshálh Nation Government District as a distinct governance case; provincial municipal SOFI or FIPPA requirements are not assumed to apply to it.',
            'Metro Vancouver is a regional district in the site’s Municipalities sector and is not counted as one of these municipal jurisdictions.',
            'Jumbo Glacier was dissolved in December 2021 and is outside the current-municipality denominator. Historical records, if found, require a separate former-employer entry.',
        ],
        'municipalities': roster,
    }
    save(OUT / 'roster.json', value)
    return value


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.parts, self.href, self.label = [], [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.href = dict(attrs).get('href')
            self.label = []

    def handle_data(self, data):
        self.parts.append(data)
        if self.href is not None:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.href:
            self.links.append((self.href, ' '.join(' '.join(self.label).split())))
            self.href = None


def relevance(url, label):
    text = urllib.parse.unquote(url + ' ' + label).lower()
    if re.search(r'\bsofi\b|statement.?of.?financial.?information|financial.?information.?statement|remuneration', text):
        return 100
    if re.search(r'financial.?report|annual.?report|financial.?statement', text):
        return 80
    if re.search(r'finance|financial|budget', text):
        return 60
    if re.search(r'city.?hall|municipal.?hall|government|administration|departments|documents|reports', text):
        return 20
    return 0


def discover(entry, page_limit=9):
    website = entry['website']
    # Prefer HTTPS for directory entries still advertising an HTTP URL.
    if website.startswith('http://'):
        website = 'https://' + website[7:]
    allowed_host = urllib.parse.urlsplit(website).hostname.removeprefix('www.')
    queue, seen, receipts, candidates = [(1000, 0, website, 'Official website')], set(), [], {}
    while queue and len(receipts) < page_limit:
        queue.sort(key=lambda r: (-r[0], r[1], r[2]))
        score, depth, url, label = queue.pop(0)
        url = urllib.parse.urldefrag(url)[0]
        if url in seen:
            continue
        seen.add(url)
        receipt = {'url': url, 'depth': depth, 'checkedOn': AS_OF}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (public municipal salary source research)'})
            with urllib.request.urlopen(req, timeout=18) as response:
                content_type = response.headers.get('Content-Type', '')
                data = response.read(8_000_001)
                receipt.update({'httpStatus': response.status, 'resolvedUrl': response.url, 'contentType': content_type,
                                'bytes': len(data), 'sha256': digest(data)})
            if len(data) > 8_000_000:
                receipt['status'] = 'response-too-large'
            elif data.startswith(b'%PDF') or 'pdf' in content_type:
                receipt['status'] = 'pdf-downloaded-unreviewed'
                candidates[url] = {'url': url, 'label': label, 'kind': 'report-linked-unreviewed', 'foundOn': url,
                                   'yearsInLabel': re.findall(r'\b(?:19|20)\d{2}\b', urllib.parse.unquote(label + ' ' + url))}
            elif 'html' in content_type or b'<html' in data[:2000].lower():
                receipt['status'] = 'html-read'
                parser = Links()
                parser.feed(data.decode('utf-8', errors='replace'))
                page_text = ' '.join(parser.parts)
                receipt['containsSofiTerms'] = bool(re.search(r'\bsofi\b|statement of financial information|remuneration', page_text, re.I))
                for href, text in parser.links:
                    # HTMLParser already decodes attribute character references.
                    # Decoding again corrupts query keys such as &currentDir into
                    # the legacy &curren character entity.
                    target = urllib.parse.urldefrag(urllib.parse.urljoin(receipt['resolvedUrl'], href))[0]
                    target = urllib.parse.quote(target, safe=':/?&=%+#@,;!$()*[]')
                    parts = urllib.parse.urlsplit(target)
                    if parts.scheme not in ('http', 'https') or target == url:
                        continue
                    link_score = relevance(target, text)
                    document = bool(re.search(r'\.(?:pdf|xlsx?|csv)(?:\?|$)|filestream\.ashx|documentcenter/view|document/view', target, re.I))
                    if link_score >= 80 or (document and receipt['containsSofiTerms'] and re.search(r'\b20\d{2}\b', text)):
                        candidates.setdefault(target, {'url': target, 'label': text, 'kind': 'report-linked-unreviewed' if document else 'archive-linked-unreviewed',
                                                       'foundOn': receipt['resolvedUrl'],
                                                       'yearsInLabel': sorted(set(re.findall(r'\b(?:19|20)\d{2}\b', urllib.parse.unquote(text + ' ' + target))))})
                    host = (parts.hostname or '').removeprefix('www.')
                    # Only follow the official domain or a subdomain. External linked
                    # council/document hosts are recorded, never crawled indiscriminately.
                    same_site = host == allowed_host or host.endswith('.' + allowed_host)
                    if same_site and not document and link_score and depth < 2 and target not in seen:
                        queue.append((link_score, depth + 1, target, text))
            else:
                receipt['status'] = 'non-html-unreviewed'
        except Exception as error:
            receipt.update({'status': 'fetch-failed', 'error': str(error)[:350]})
            if isinstance(error, urllib.error.HTTPError):
                receipt['httpStatus'] = error.code
        receipts.append(receipt)
    result = {k: entry[k] for k in ('municipality', 'employerSlug', 'website')}
    result.update({'checkedOn': AS_OF, 'method': 'Bounded traversal of links actually present on the official website; at most two link hops.',
                   'status': 'source-links-found-awaiting-review' if candidates else 'no-source-link-found-in-bounded-search',
                   'pagesChecked': receipts, 'candidates': sorted(candidates.values(), key=lambda r: (r['kind'], r['url']))})
    if not any(r.get('status') == 'html-read' for r in receipts):
        result['status'] = 'official-site-unavailable-in-this-environment'
    if entry['status'] == 'pending-incorporation':
        result['status'] = 'not-yet-incorporated'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', type=Path)
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--discover', action='store_true')
    parser.add_argument('--only', help='Comma-separated employer slugs')
    parser.add_argument('--pages', type=int, default=9)
    args = parser.parse_args()
    if args.workbook or args.directory:
        if not args.workbook or not args.directory:
            parser.error('--workbook and --directory are required together')
        roster = make_roster(args.workbook, args.directory)
        print(f"Roster: {len(roster['municipalities'])} entries, including pending Okanagan Falls", flush=True)
    else:
        roster = json.loads((OUT / 'roster.json').read_text())
    if args.discover:
        entries = roster['municipalities']
        if args.only:
            selected = set(args.only.split(','))
            entries = [e for e in entries if e['employerSlug'] in selected]
        receipts_dir = OUT / 'discovery'
        receipts_dir.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(discover, entry, args.pages): entry for entry in entries}
            for future in as_completed(futures):
                result = future.result()
                save(receipts_dir / f"{result['employerSlug']}.json", result)
                print(f"{result['employerSlug']}: {result['status']}; {len(result['candidates'])} candidate links", flush=True)


if __name__ == '__main__':
    main()
