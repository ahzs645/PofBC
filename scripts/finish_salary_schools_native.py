#!/usr/bin/env python3
"""Two independent native readers for new, source-specific school schedules.

Poppler physical text lines and MuPDF word geometry are retained independently.
No normalization changes spelling, initials, source titles, zeroes or controls.
Native agreement is a candidate check; review is required before registration.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/schools'
COLLECTION = ROOT/'research/salaries/queue-completion-schools'
FIELDS = ('name', 'position', 'remuneration', 'expenses', 'pdfPage', 'category')
MONEY = re.compile(r'\$?\s*\(?-?\d[\d,]*(?:\.\d{2})?\)?$')


def clean(value):
    return re.sub(r'\s+', ' ', value).strip()


def amount(value):
    value = value.replace('$', '').replace(',', '').strip().rstrip('*').strip()
    value = re.sub(r'^-\s+(?=\d)', '-', value)
    if value in ('', '-', '–', '—'):
        return None
    if not MONEY.fullmatch(value):
        raise ValueError('Nonliteral monetary cell: '+repr(value))
    return str(Decimal(value.replace('(', '-').replace(')', '')))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def category_at(config, page, y):
    if str(page) in config.get('pageCategories', {}):
        return config['pageCategories'][str(page)]
    return 'school-trustees' if page == config['pages'][0] and y < config['trusteeEndY'] else 'employee-remuneration'


def has_positions(config, category):
    return config.get('positionsByCategory', {}).get(category, config['positions'] and (category == 'school-trustees' or not config.get('employeePositionsAbsent')))


def valid_name(value, category, config):
    if not value or not re.match(r'^(?:\*+\s*)?[A-Za-zÀ-ž]', value):
        return False
    if re.search(r'\d', value) or value.upper().startswith(('TOTAL', 'REMUNERATION TO', 'CONSOLIDATED')):
        return False
    if ',' in value:
        return True
    return config.get('trusteesWithoutCommas', False) and category == 'school-trustees' and not value.upper().startswith(('TOTAL', 'NAME', 'REMUNERATION'))


def poppler_rows(text, config):
    pages = text.split('\f')
    rows = []
    mode = 'school-trustees'
    controls = []
    for page in config['pages']:
        position_col, pay_col, expense_col = config.get('popplerColumnsByPage', {}).get(str(page), config['popplerColumns'])
        if str(page) in config.get('pageCategories', {}):
            mode = config['pageCategories'][str(page)]
        for line in pages[page-1].splitlines():
            stripped = clean(line)
            upper = stripped.upper()
            if any(re.search(pattern, upper) for pattern in config['employeeSwitchPatterns']):
                mode = 'employee-remuneration'
            # Column headings establish independent physical-text columns.
            if re.search(r'\b(?:NAME|EMPLOYEE|POSITION)\b', upper) and re.search(r'\bREMUNERATION\b', upper) and re.search(r'\bEXPENSE', upper):
                if re.search(r'\bPOSITION\b', upper) and not config.get('fixedPopplerPositionColumn'):
                    position_col = re.search(r'\bPOSITION\b', line, re.I).start()
                pay_col = re.search(r'\bREMUNERATION\b', line, re.I).start()
                expense_col = re.search(r'\bEXPENSE', line, re.I).start()
            if not stripped:
                continue
            if re.match(r'^(?:TOTAL|REMUNERATION TO|GRAND TOTAL|CONSOLIDATED TOTAL|EMPLOYEES EARNING REMUNERATION OF LESS)', upper):
                controls.append({'pdfPage': page, 'sourceLine': line})
                continue
            has_position = has_positions(config, mode)
            position_last = mode in config.get('positionLastCategories', [])
            name = clean(line[:position_col if has_position and not position_last else pay_col])
            position = clean(line[position_col:] if position_last else line[position_col:pay_col]) if has_position else ''
            pay = clean(line[pay_col:expense_col])
            expense = clean(line[expense_col:position_col] if position_last else line[expense_col:])
            if config.get('splitPopplerNamePositionAtFirstGap') and has_position and not position_last:
                prefix = line[:pay_col].rstrip().rstrip('$').rstrip().lstrip()
                parts = re.split(r'\s{2,}', prefix, maxsplit=1)
                if len(parts) == 2:
                    name, position = map(clean, parts)
            if config.get('currencyDelimitedCells'):
                cash_cells = list(re.finditer(r'\$\s*\d[\d,]*\.\d{2}', line))
                if len(cash_cells) == 2:
                    prefix = line[:cash_cells[0].start()]
                    name, position = clean(prefix[:position_col]), clean(prefix[position_col:])
                    pay, expense = [match.group() for match in cash_cells]
            if config.get('integerCurrencyDelimitedCells'):
                cash_cells = list(re.finditer(r'-?\s*\$\s*(?:\d[\d,]*(?:\.\d{2})?|[-–])', line))
                if len(cash_cells) == 2:
                    prefix = line[:cash_cells[0].start()]
                    name, position = clean(prefix[:position_col]), clean(prefix[position_col:])
                    pay, expense = [match.group() for match in cash_cells]
            name = name.rstrip('$').strip()
            position = position.rstrip('$').strip()
            if valid_name(name, mode, config) and MONEY.fullmatch(pay.replace('$', '').strip()):
                rows.append({'name': name, 'position': position or None, 'remuneration': amount(pay),
                             'expenses': amount(expense), 'pdfPage': page, 'category': mode, 'sourceLine': line})
            elif has_position and not name and position and not pay and not expense and rows and rows[-1]['pdfPage'] == page:
                rows[-1]['position'] = clean((rows[-1]['position'] or '')+' '+position)
                rows[-1].setdefault('continuationLines', []).append(line)
    return rows, controls


def mupdf_rows(document, config):
    rows = []
    page_geometry = []
    for number in config['pages']:
        page = document[number-1]
        groups = []
        for word in sorted(page.get_text('words'), key=lambda w: ((w[1]+w[3])/2, w[0])):
            y = (word[1]+word[3])/2
            group = next((g for g in reversed(groups[-3:]) if abs(g['y']-y) < config.get('rowTolerance', 2)), None)
            if group is None:
                group = {'y': y, 'words': []}
                groups.append(group)
            group['words'].append(word)
        for group in groups:
            category = category_at(config, number, group['y'])
            has_position = has_positions(config, category)
            geometry = config.get('geometryByCategory', {}).get(category, config['geometry'])
            bounds = geometry if has_position else [geometry[1], geometry[1], geometry[2]]
            cells = [[] for _ in range(4)]
            for word in sorted(group['words'], key=lambda w: w[0]):
                if word[4] == '$':
                    continue
                cells[sum(word[0] >= bound for bound in bounds)].append(word[4])
            values = [clean(' '.join(cell)) for cell in cells]
            if category in config.get('positionLastCategories', []):
                name, pay, expense, position = values
            else:
                name, position, pay, expense = values
            if valid_name(name, category, config) and MONEY.fullmatch(pay.replace('$', '').strip()):
                words = [{'x0': round(w[0], 4), 'y0': round(w[1], 4), 'x1': round(w[2], 4),
                          'y1': round(w[3], 4), 'text': w[4]} for w in sorted(group['words'], key=lambda w: w[0])]
                rows.append({'name': name, 'position': position or None, 'remuneration': amount(pay),
                             'expenses': amount(expense), 'pdfPage': number, 'category': category, 'y': group['y'], 'words': words})
            elif has_position and not name and position and not pay and not expense and rows and rows[-1]['pdfPage'] == number:
                rows[-1]['position'] = clean((rows[-1]['position'] or '')+' '+position)
                rows[-1].setdefault('continuationWords', []).extend(group['words'])
        trace = page.get_texttrace()
        # The absence of this flag is not a source-fidelity certification.
        nonpainted = [{'seqno': t['seqno'], 'type': t['type'], 'color': t['color'], 'bbox': list(t['bbox'])}
                      for t in trace if t['type'] == 3 or all(v > .95 for v in t['color'])]
        page_geometry.append({'physicalPage': number, 'width': page.rect.width, 'height': page.rect.height,
                              'wordCount': len(page.get_text('words')), 'nonpaintedOrWhiteTextRuns': nonpainted})
    return rows, page_geometry


def fields(row):
    return [row[field] for field in FIELDS]


def source_candidate(config, originals=True):
    import fitz
    path = Path(config['cachePath'])
    assert sha(path.read_bytes()) == config['sha256'], 'Original source fingerprint differs'
    document = fitz.open(path)
    text = subprocess.check_output(['pdftotext', '-layout', str(path), '-']).decode()
    first, controls = poppler_rows(text, config)
    second, geometry = mupdf_rows(document, config)
    amendments = []
    raw_second = None
    if config.get('imageAmendmentFile'):
        raw_second = json.loads(json.dumps(second))
        amendment_path = ROOT/config['imageAmendmentFile']
        amendments = json.loads(amendment_path.read_text())
        for amendment in amendments:
            assert amendment['reader'] == 'mupdf'
            row = second[amendment['sequence']-1]
            assert row['pdfPage'] == amendment['pdfPage']
            assert row[amendment['field']] == amendment['before']
            crop_path = Path(amendment['originalImageCropPath'])
            if not crop_path.exists():
                crop_path = AREA/'images'/crop_path.name
            assert sha(crop_path.read_bytes()) == amendment['originalImageCropSha256']
            row[amendment['field']] = amendment['after']
    differences = []
    for index in range(max(len(first), len(second))):
        a = fields(first[index]) if index < len(first) else None
        b = fields(second[index]) if index < len(second) else None
        if a != b:
            differences.append({'sequence': index+1, 'poppler': a, 'mupdf': b})
    summaries = {}
    for category in ('school-trustees', 'employee-remuneration'):
        chosen = [r for r in first if r['category'] == category]
        summaries[category] = {'rows': len(chosen), 'computedTotals': [str(sum((Decimal(r[f]) for r in chosen if r[f] is not None), Decimal(0))) for f in ('remuneration', 'expenses')],
                               'nullExpenseRows': sum(r['expenses'] is None for r in chosen), 'zeroExpenseRows': sum(r['expenses'] is not None and Decimal(r['expenses']) == 0 for r in chosen)}
    result = {'config': config, 'originalSha256': config['sha256'], 'popplerText': text, 'popplerRows': first,
            'mupdfRows': second, 'pageGeometry': geometry, 'literalControlLines': controls,
            'nativeReaderDifferences': differences, 'summaries': summaries, 'acceptedRows': 0}
    if raw_second is not None:
        result.update(rawMupdfRowsBeforeImageAmendments=raw_second, imageVerifiedReaderAmendments=amendments)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--specs', type=Path, default=AREA/'native-source-specs.json')
    parser.add_argument('--source', action='append')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for config in json.loads(args.specs.read_text()):
        if args.source and config['key'] not in args.source:
            continue
        candidate = source_candidate(config)
        raw = (json.dumps(candidate, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
        path = AREA/(config['key']+'-native-candidate.json.gzip')
        packed = gzip.compress(raw, mtime=0)
        if args.check:
            assert path.read_bytes() == packed, 'Fresh original/native replay differs'
        else:
            if path.exists():
                raise ValueError('Native candidate is immutable; use --check or a new revision filename')
            path.write_bytes(packed)
        print(json.dumps({'source': config['key'], 'popplerRows': len(candidate['popplerRows']), 'mupdfRows': len(candidate['mupdfRows']),
                          'differences': len(candidate['nativeReaderDifferences']), 'summaries': candidate['summaries'], 'proofSha256': sha(packed)}))


if __name__ == '__main__':
    main()
