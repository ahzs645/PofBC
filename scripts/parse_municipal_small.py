#!/usr/bin/env python3
"""Reproduce reviewed small-municipality schedules with two PDF text readers.

Each layout, reporting year, row count and printed control is reviewed against
the rendered original. PDFs are hash-pinned. Coordinates refer to the displayed
page, including PDF rotation. Missing amounts are not converted to zero.
"""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-small'
MONEY = re.compile(r'^-?\d[\d,]*(?:\.\d{1,2})?$')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def money(text):
    text = text.strip().replace('$', '').strip()
    if text.lower() == 'nil':
        return 0
    if text in ('', '-', '–', '—'):
        return None
    if not MONEY.fullmatch(text):
        raise ValueError(f'Unrecognized money cell: {text!r}')
    value = Decimal(text.replace(',', ''))
    return int(value * 100)


def dollars(cents):
    return None if cents is None else (cents // 100 if cents % 100 == 0 else cents / 100)


def mupdf_words(page):
    return [(*tuple(fitz.Rect(w[:4]) * page.rotation_matrix), w[4]) for w in page.get_text('words')]


def poppler_words(path, page_number):
    raw = subprocess.check_output(['pdftotext', '-f', str(page_number), '-l', str(page_number), '-bbox-layout', str(path), '-'])
    root = ET.fromstring(raw)
    return [(float(w.attrib['xMin']), float(w.attrib['yMin']), float(w.attrib['xMax']), float(w.attrib['yMax']), w.text or '')
            for w in root.iter() if w.tag.endswith('}word') or w.tag == 'word']


def extract(words, section):
    columns = section['columns']
    y0, y1 = section['y']
    words = [w for w in words if y0 <= (w[1] + w[3]) / 2 <= y1 and w[4] not in section.get('ignoreTokens', [])]
    pay_col = columns[section.get('anchorColumn', 'pay')]
    anchors = sorted((w for w in words if pay_col[0] <= (w[0] + w[2]) / 2 < pay_col[1] and MONEY.fullmatch(w[4])), key=lambda w: w[1])
    if len(anchors) != section['rowCount']:
        raise ValueError(f"Expected {section['rowCount']} pay cells; found {len(anchors)}")
    centers = [(w[1] + w[3]) / 2 for w in anchors]
    groups = [{k: [] for k in columns} for _ in centers]
    for word in words:
        x, y = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
        at = min(range(len(centers)), key=lambda i: abs(centers[i] - y))
        if abs(centers[at] - y) > section.get('maxRowDistance', 16):
            raise ValueError(f"Unassigned schedule text: {word[4]!r}")
        for field, (left, right) in columns.items():
            if left <= x < right and word[4] not in ('$', 's', 'A', '_$_', 'A_', '_'):
                groups[at][field].append(word)
    rows = []
    for group in groups:
        values = {}
        for field, cells in group.items():
            # Stable reading order for single-line names and wrapped positions.
            lines = []
            for word in sorted(cells, key=lambda w: ((w[1] + w[3]) / 2, w[0])):
                cy = (word[1] + word[3]) / 2
                if lines and abs(cy - lines[-1][0]) <= 3:
                    lines[-1][1].append(word)
                else:
                    lines.append((cy, [word]))
            text = ' '.join(w[4] for _, line in lines for w in sorted(line, key=lambda w: w[0])).strip()
            if field in ('name', 'position'):
                values[field] = text or None
            else:
                values[field] = money(text)
        if section.get('splitNamePosition'):
            values['name'], values['position'] = [v.strip() for v in values['name'].split(',', 1)]
        for before, after in section.get('fieldCorrections', {}).get('name', {}).items():
            if values['name'] == before:
                values['name'] = after
        position_fix = section.get('fieldCorrections', {}).get('positionByName', {}).get(values['name'])
        if position_fix:
            if values.get('position') != position_fix['before']:
                raise ValueError(f"Reviewed position correction no longer matches for {values['name']}")
            values['position'] = position_fix['after']
        if not values['name'] or re.search(r'^(total|consolidated|schedule|employees|remuneration)\b', values['name'], re.I):
            raise ValueError(f'Non-person row entered the schedule: {values}')
        if section.get('payComponents'):
            values['pay'] = sum(values[f] or 0 for f in section['payComponents'])
        if section.get('expensesIncludeBenefits'):
            values['expenses'] = None
        if values['pay'] is None or values['pay'] < 0:
            raise ValueError(f'Missing or negative remuneration: {values}')
        if section['category'] == 'employee-remuneration' and values['pay'] < 7_500_000:
            raise ValueError(f'Unexpected below-threshold employee: {values}')
        rows.append(values)
    missing_corrections = set(section.get('fieldCorrections', {}).get('positionByName', {})) - {r['name'] for r in rows}
    if missing_corrections:
        raise ValueError(f'Reviewed position correction rows disappeared: {missing_corrections}')
    return rows


def total(rows, field):
    return sum(r.get(field) or 0 for r in rows)


def build(config, cache, fetch=False):
    roster = json.loads((ROOT / 'research/salaries/municipal-audit/roster.json').read_text())
    employers = {e['employerSlug']: e for e in roster['municipalities']}
    pending, sources, reviews = {}, [], []
    for report in config['reports']:
        slug, year = report['employerSlug'], report['year']
        path = cache / report['cacheFile']
        if fetch and not path.exists():
            cache.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(urllib.request.Request(report['sourceUrl'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as response:
                path.write_bytes(response.read())
        raw = path.read_bytes()
        if sha(raw) != report['sha256']:
            raise ValueError(f'{slug} {year}: original PDF fingerprint changed')
        doc = fitz.open(stream=raw, filetype='pdf')
        for section in report['sections']:
            page_number = section['page']
            page = doc[page_number - 1]
            if section['yearEvidence'] not in page.get_text():
                raise ValueError(f'{slug} {year}: reviewed reporting-period heading is missing')
            a = extract(mupdf_words(page), section)
            b = extract(poppler_words(path, page_number), section)
            if a != b:
                raise ValueError(f'{slug} {year}: independent PDF readers disagree: {a} != {b}')
            if Counter(json.dumps(r, sort_keys=True) for r in a).most_common(1)[0][1] > 1:
                raise ValueError(f'{slug} {year}: duplicate-looking row requires review')
            controls = []
            for field, expected in section['controlsCents'].items():
                actual = total(a, field)
                residual = actual - expected
                if residual != section.get('reviewedResidualsCents', {}).get(field, 0):
                    raise ValueError(f'{slug} {year} {field}: source residual changed: {residual} cents')
                controls.append({'field': field, 'printedControl': dollars(expected), 'rowSum': dollars(actual),
                                 'residual': dollars(residual), 'basis': section.get('controlBasis', {}).get(field, 'Printed named-cohort subtotal')})
            category = section['category']
            source_id = f"municipal-small-{slug}-{year}-{category}"
            rows = [[slug, r['name'], r.get('position'), dollars(r['pay']), dollars(r.get('expenses')), page_number] for r in a]
            file = f'{slug}-{year}-{category}.json.gzip'
            data = gzip.compress(compact(rows), mtime=0)
            pending[file] = data
            audit_file = f'evidence/{slug}-{year}-{category}.json.gzip'
            pending[audit_file] = gzip.compress(compact({'originalPdfSha256': sha(raw), 'rows': a, 'controls': controls,
                'pdfPage': page_number, 'mupdfWords': mupdf_words(page), 'popplerWords': poppler_words(path, page_number)}), mtime=0)
            notes = report.get('notes', []) + section.get('notes', []) + [
                'Actual calendar reporting year confirmed from the original schedule; URL/upload year and index labels are not used as the reporting period.',
                'All published rows on the selected schedule were visually checked. Names and job titles remain as disclosed; a surname alone is not expanded.',
                'Blank and dash expenses remain missing. Explicit nil is zero. Remuneration never includes expenses.',
            ]
            if any(c['residual'] for c in controls):
                notes.append('Displayed individual amounts have the recorded small residual against the source subtotal. Values are preserved; rounding is a possible explanation, not a proven reconciliation.')
            source = {'id': source_id, 'employerSlug': slug, 'employerName': employers[slug]['employerName'], 'sector': 'Municipalities',
                      'year': year, 'periodType': 'calendar', 'periodStart': f'{year}-01-01', 'periodEnd': f'{year}-12-31',
                      'title': f"{employers[slug]['employerName']} {year} SOFI: {category}",
                      'sourceUrl': report['sourceUrl'], 'sourceIndexUrl': report['indexUrl'], 'sha256': sha(raw),
                      'file': file, 'dataSha256': sha(data), 'category': category,
                      'scope': 'named-employees-over-threshold' if category == 'employee-remuneration' else 'elected-officials',
                      'threshold': 75000 if category == 'employee-remuneration' else None,
                      'thresholdComparison': section.get('thresholdComparison', '>') if category == 'employee-remuneration' else None,
                      'currency': 'CAD', 'amountUnit': 'dollars', 'status': 'verified', 'verifiedOn': '2026-10-31',
                      'rowCount': len(rows), 'totalRemuneration': dollars(total(a, 'pay')), 'totalExpenses': dollars(total(a, 'expenses')),
                      'pages': [page_number], 'nameDisclosure': section.get('nameDisclosure', 'published-name'),
                      'positionDisclosure': 'published' if any(r[2] for r in rows) else 'not-published', 'notes': notes,
                      'validation': {'originalFingerprintVerified': True, 'independentReaders': ['PyMuPDF positioned words', 'Poppler bbox-layout positioned words'],
                                     'everyRowFieldAgreement': True, 'physicalPagesVisuallyReviewed': [page_number],
                                     'rowsIndependentlyChecked': len(rows), 'printedControls': controls,
                                     'fieldCorrections': section.get('fieldCorrections', {}), 'evidenceFile': audit_file}}
            if section.get('expensesIncludeBenefits'):
                source['expensesNote'] = 'The report combines employee expenses and taxable benefits; the combined values are retained only in the component audit and cannot be identified as expenses.'
            sources.append(source)
            print(f'{slug} {year} {category}: {len(rows)} rows; controls {controls}')
        reviews.append({'employerSlug': slug, 'year': year, 'sha256': sha(raw), 'sourceUrl': report['sourceUrl'], 'pdfPages': len(doc)})
    OUT.mkdir(parents=True, exist_ok=True)
    for file, data in pending.items():
        path = OUT / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    manifest = {'version': 1, 'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'],
                'coverageNotes': ['Reviewed original schedules from small northern and Interior municipalities. Only accepted schedules reach the salary build.'],
                'sources': sources, 'unparsedSources': config.get('unparsedSources', [])}
    (OUT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'original-verification.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=ROOT / 'tmp/municipal-small')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--config', type=Path, default=OUT / 'reviewed-layouts.json')
    args = parser.parse_args()
    build(json.loads(args.config.read_text()), args.cache, args.fetch)


if __name__ == '__main__':
    main()
