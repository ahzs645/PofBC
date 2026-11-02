#!/usr/bin/env python3
"""Read new school schedules using Poppler lines and independent MuPDF geometry.

Only literal spacing is normalized. No financial control supplies a row value.
Native text must be painted text: a hidden OCR layer is not a second reader.
"""
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02/school_native'
CACHE = Path('/workspace/gap-school-native-cache')
FIELDS = ['name', 'position', 'remuneration', 'expenses', 'pdfPage', 'category']
CASH = r'(?:\(?-?\d[\d,]*(?:\.\d{2})?\)?|[-–—])'
TAIL = re.compile(r'^(.*?)\s+(\$?\s*' + CASH + r')\s+(\$?\s*' + CASH + r')\s*(\*)?\s*$')
NUMERIC = re.compile(r'^\(?-?\d[\d,]*(?:\.\d{2})?\)?$')


def clean(value):
    return re.sub(r'\s+', ' ', value).strip()


def money(value):
    value = clean(value).replace('$', '').strip()
    if value in ('', '-', '–', '—'):
        return None
    if not NUMERIC.fullmatch(value):
        raise ValueError('Unparsed literal amount: ' + repr(value))
    return str(Decimal(value.replace(',', '').replace('(', '-').replace(')', '')))


def valid_name(value):
    return bool(re.match(r'^[A-Za-zÀ-ž]', value) and ',' in value and not re.search(r'\d', value)
                and not re.match(r'^(TOTAL|CONSOLIDATED|NAME|EMPLOYEES|REMUNERATION)', value, re.I))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pack(value):
    return gzip.compress((json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n').encode(), mtime=0)


def category(config, page, y=None):
    if page < config['employeeStartPage']:
        return 'school-trustees'
    if page == config['employeeStartPage'] == config['pages'][0] and y is not None and y < config['employeeStartY']:
        return 'school-trustees'
    return 'employee-remuneration'


def read_poppler(text, config):
    rows, skipped, controls = [], [], []
    pages = text.split('\f')
    for page in config['pages']:
        mode = category(config, page)
        if page == config['pages'][0] and config['employeeStartPage'] == page:
            mode = 'school-trustees'
        physical_lines = pages[page-1].splitlines()
        for line_number, line in enumerate(physical_lines, 1):
            stripped = clean(line)
            upper = stripped.upper()
            if re.match(r'^(?:A\. )?LIST OF EMPLOYEES|^EMPLOYEES WITH RENUMERATION', upper):
                mode = 'employee-remuneration'
            if re.match(r'^TOTAL', upper):
                controls.append({'pdfPage': page, 'line': line})
                if 'ELECTED OFFICIALS' in upper and config.get('employeeFollowsTrusteeTotal'):
                    mode = 'employee-remuneration'
                continue
            match = TAIL.match(line)
            if not match:
                continue
            prefix, pay, expense, footnote = match.groups()
            # Poppler may put a long title and its two amounts on consecutive
            # physical text lines even though the source paints one table row.
            # This joins text lines only; it supplies no new field value.
            preceding_line = None
            if not prefix.strip() and line_number > 1:
                prior = physical_lines[line_number-2]
                prior_parts = re.split(r'\s{2,}', prior.strip(), maxsplit=1)
                if len(prior_parts) == 2 and valid_name(prior_parts[0]) and not TAIL.match(prior):
                    prefix = prior
                    preceding_line = prior
            parts = re.split(r'\s{2,}', prefix.strip(), maxsplit=1)
            if len(parts) != 2:
                if valid_name(prefix):
                    skipped.append({'pdfPage': page, 'lineNumber': line_number, 'line': line, 'reason': 'name/title boundary unresolved'})
                continue
            name, title = map(clean, parts)
            if not valid_name(name):
                continue
            if money(pay) is None:
                raise ValueError('Named row lacks numeric remuneration: ' + line)
            rows.append({'name': name, 'position': title or None, 'remuneration': money(pay),
                         'expenses': money(expense), 'pdfPage': page, 'category': mode,
                         'sourceLine': line, 'lineNumber': line_number, 'expenseFootnote': footnote})
            if preceding_line is not None:
                rows[-1]['precedingPhysicalTextLine'] = preceding_line
    return rows, skipped, controls


def read_mupdf(raw_pages, config):
    rows, skipped = [], []
    for raw in raw_pages:
        page = raw['physicalPage']
        groups = []
        for word in sorted(raw['words'], key=lambda w: ((w[1]+w[3])/2, w[0])):
            y = (word[1]+word[3])/2
            group = next((g for g in groups[-4:] if abs(g['y']-y) < config.get('rowTolerance', 1.7)), None)
            if group is None:
                group = {'y': y, 'words': []}
                groups.append(group)
            group['words'].append(word)
        for group in groups:
            mode = category(config, page, group['y'])
            bounds = config.get('boundsByCategory', {}).get(mode, config['bounds'])
            cells = [[] for _ in range(4)]
            for word in sorted(group['words'], key=lambda w: w[0]):
                if word[4] in ('$', '*'):
                    continue
                cells[sum(word[0] >= b for b in bounds)].append(word[4])
            name, title, pay, expense = [clean(' '.join(c)) for c in cells]
            if not valid_name(name):
                continue
            if not NUMERIC.fullmatch(pay.replace('$', '')):
                skipped.append({'pdfPage': page, 'y': group['y'], 'cells': [name,title,pay,expense], 'words': group['words']})
                continue
            rows.append({'name': name, 'position': title or None, 'remuneration': money(pay),
                         'expenses': money(expense), 'pdfPage': page, 'category': mode,
                         'y': group['y'], 'words': group['words']})
    return rows, skipped


def summary(rows):
    out = {}
    for scope in ['school-trustees', 'employee-remuneration']:
        chosen = [r for r in rows if r['category'] == scope]
        out[scope] = {'rows': len(chosen), 'computedTotals': [str(sum((Decimal(r[f]) for r in chosen if r[f] is not None), Decimal())) for f in ['remuneration','expenses']],
                      'nullExpenses': sum(r['expenses'] is None for r in chosen),
                      'zeroExpenses': sum(r['expenses'] is not None and Decimal(r['expenses']) == 0 for r in chosen),
                      'rowsByPage': dict(Counter(r['pdfPage'] for r in chosen))}
    return out


def extract(config, check=False):
    import fitz
    key = config['key']
    path = Path(config['cachePath'])
    assert digest(path.read_bytes()) == config['sourceSha256']
    doc = fitz.open(path)
    text = subprocess.check_output(['pdftotext','-layout',str(path),'-']).decode()
    raw_pages=[]
    for number in config['pages']:
        page=doc[number-1]
        traces=page.get_texttrace()
        assert all(t['type'] == 0 and not all(c > .95 for c in t['color']) for t in traces), (key,number,'hidden or white native text requires OCR/source review')
        raw_pages.append({'physicalPage':number,'width':page.rect.width,'height':page.rect.height,
                          'words':page.get_text('words'),'paintedTextTraceTypes':list(sorted({t['type'] for t in traces})),
                          'paintedTextTraceCount':len(traces),'imageCount':len(page.get_images())})
    a,unresolved_a,controls=read_poppler(text,config)
    b,unresolved_b=read_mupdf(raw_pages,config)
    differences=[]
    for i in range(max(len(a),len(b))):
        av=[a[i][f] for f in FIELDS] if i<len(a) else None
        bv=[b[i][f] for f in FIELDS] if i<len(b) else None
        if av!=bv:differences.append({'sequence':i+1,'poppler':av,'mupdf':bv})
    result={'source':config,'popplerRawText':text,'mupdfRawPages':raw_pages,'popplerRows':a,'mupdfRows':b,
            'unresolvedPoppler':unresolved_a,'unresolvedMupdf':unresolved_b,'literalControlLines':controls,
            'independentReaderDifferences':differences,'summaries':summary(a),'acceptedRows':0}
    blob=pack(result);dest=AREA/config.get('candidateFile',key+'-native-candidate.json.gzip')
    if check:assert dest.read_bytes()==blob
    else:dest.write_bytes(blob)
    return {'key':key,'rowCounts':[len(a),len(b)],'unresolved':[len(unresolved_a),len(unresolved_b)],'differences':len(differences),'summaries':result['summaries']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--key',action='append');args=ap.parse_args()
    for config in json.loads((AREA/'native-specs.json').read_bytes()):
        if args.key and config['key'] not in args.key:continue
        print(json.dumps(extract(config,args.check),ensure_ascii=False),flush=True)


if __name__=='__main__':main()
