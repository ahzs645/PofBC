#!/usr/bin/env python3
"""Verify CHC's original PDFs and rebuild the five reviewed employee schedules.

Poppler layout extraction and PyMuPDF column-coordinate extraction are compared
as multisets, then checked against the earlier staging fingerprints. Every source
schedule/summary page was visually inspected on 2026-10-30. Re-running this command
does not constitute a new visual review: changed PDF bytes fail closed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/columbia-hydro-constructors'
SLUG = 'sub-columbia-hydro-constructors'
ROW = re.compile(r'([A-Z]{1,5})\s+([^\d]+?)\s+(\d[\d,]*)\s+(\d[\d,]*)(?=\s|$)')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def raw_fingerprint(rows):
    return digest(json.dumps(sorted(rows), ensure_ascii=False, separators=(',', ':')).encode())


def verify_heading(text, entry, page_number, sheet):
    compact = ' '.join(text.split())
    required = ['COLUMBIA HYDRO CONSTRUCTORS LTD.',
                'Schedule of Remuneration Paid to Employees and Expenses Paid to or',
                f'on Behalf of Employees During the Year Ended March 31, {entry["periodEnd"][:4]}',
                f'{sheet} of {len(entry["pages"])}']
    if not all(v in compact for v in required):
        raise ValueError(f'Employer, scope, year or sheet sequence not verified on page {page_number}')


def layout_rows(text, page):
    result = []
    for line in text.splitlines():
        if not re.match(r'^\s*[A-Z]{1,5}\s{2,}', line):
            continue
        matches = list(ROW.finditer(line))
        if not matches or len(matches) > 2:
            raise ValueError(f'Unparsed employee line on page {page}: {line!r}')
        residue = ROW.sub('', line)
        if residue.strip():
            raise ValueError(f'Unparsed employee residue on page {page}: {residue!r}')
        for m in matches:
            name = m[1] + ' ' + ' '.join(m[2].split())
            pay, expense = (int(m[i].replace(',', '')) for i in (3, 4))
            if pay <= 75000:
                raise ValueError('Unexpected employee remuneration at or below the named threshold')
            result.append((name, pay, expense, page))
    return result


def coordinate_rows(page, physical_page):
    """Independent reader/parser: identify fixed remuneration column right edges."""
    words = page.get_text('words')
    result = []
    for half in (0, 1):
        offset = 288 * half
        salary_words = sorted([w for w in words if abs(w[2] - (204 + offset)) < 1
                               and re.fullmatch(r'\d[\d,]*', w[4]) and w[1] > 85],
                              key=lambda w: w[1])
        for salary in salary_words:
            aligned = [w for w in words if abs(w[1] - salary[1]) < 0.8]
            initials = [w[4] for w in aligned if abs(w[0] - (42 + offset)) < 1]
            surname = [w for w in aligned if 69 + offset < w[0] < 169 + offset]
            expense = [w[4] for w in aligned if abs(w[2] - (282 + offset)) < 1]
            if len(initials) != 1 or len(expense) != 1 or not surname:
                raise ValueError(f'Column layout is incomplete on page {physical_page}')
            name = initials[0] + ' ' + ' '.join(w[4] for w in sorted(surname))
            result.append((name, int(salary[4].replace(',', '')), int(expense[0].replace(',', '')), physical_page))
    return result


def coordinate_controls(page):
    words = page.get_text('words')
    values = {}
    for label, keys in [('Consolidated', ('belowThresholdRemuneration', 'belowThresholdExpenses')),
                        ('Total', ('totalRemuneration', 'totalExpenses')),
                        ('Receiver', ('employerCppEi',))]:
        labels = [w for w in words if w[4] == label and w[0] < 50]
        if len(labels) != 1:
            raise ValueError(f'Missing unique source control {label}')
        for right, key in zip((492, 570), keys):
            amounts = [w[4] for w in words if abs(w[1] - labels[0][1]) < 1
                       and abs(w[2] - right) < 1 and re.fullmatch(r'\d[\d,]*', w[4])]
            if len(amounts) != 1:
                raise ValueError(f'Control amount column {key} was not resolved')
            values[key] = int(amounts[0].replace(',', ''))
    return values


def process(pdf, entry):
    import pymupdf
    raw = pdf.read_bytes()
    if digest(raw) != entry['pdfSha256']:
        raise ValueError(f'{pdf.name}: PDF fingerprint changed; review required')
    text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], stderr=subprocess.DEVNULL, text=True)
    layout = text.split('\f')
    document = pymupdf.open(pdf)
    if len(document) != len(layout) - 1:
        raise ValueError('PDF readers disagree on document page count')
    a, b = [], []
    for sheet, n in enumerate(entry['pages'], 1):
        verify_heading(layout[n-1], entry, n, sheet)
        verify_heading(document[n-1].get_text(), entry, n, sheet)
        if n != entry['pages'][-1]:
            a += layout_rows(layout[n-1], n)
            b += coordinate_rows(document[n-1], n)
        elif layout_rows(layout[n-1], n):
            raise ValueError('Unexpected named rows on summary page')
    if Counter(a) != Counter(b):
        raise ValueError(f'Independent extraction differs: {list((Counter(a)-Counter(b)).elements())[:3]} / {list((Counter(b)-Counter(a)).elements())[:3]}')
    if raw_fingerprint(a) != entry['stagedRawRowFingerprint']:
        raise ValueError('Original-PDF rows do not match the staged multiset')
    controls = coordinate_controls(document[entry['pages'][-1]-1])
    if controls != entry['controls']:
        raise ValueError('Original PDF controls do not match visually reviewed values')
    pay, expense = sum(r[1] for r in a), sum(r[2] for r in a)
    residual = [pay - (controls['totalRemuneration'] - controls['belowThresholdRemuneration']),
                expense - (controls['totalExpenses'] - controls['belowThresholdExpenses'])]
    bound = (len(a)+2)/2
    if any(abs(v) > bound for v in residual):
        raise ValueError('Unexplained source residual exceeds whole-dollar compatibility bound')
    rows = [[SLUG, name.split(' ', 1)[1] + ', ' + name.split(' ', 1)[0], None, p, e, n]
            for name, p, e, n in a]
    review = {
        'pdfSha256Verified': True, 'sourcePdfPageCount': len(document), 'sourcePages': entry['pages'],
        'employeeScheduleSheetsComplete': True, 'popplerLayoutRows': len(a),
        'pyMuPdfCoordinateRows': len(b), 'independentReadersMultisetEqual': True,
        'priorStagingMultisetEqual': True, 'everySchedulePageVisuallyReviewedOn': '2026-10-30',
        'visuallyReviewedPhysicalPages': entry['pages'], 'aggregateColumnsVerifiedAgainstOriginalPdf': True,
        'sourceControls': controls, 'namedRemunerationSum': pay, 'namedExpensesSum': expense,
        'remunerationResidual': residual[0], 'expensesResidual': residual[1],
        'exactAggregateReconciliation': not any(residual),
        'hypotheticalWholeDollarRoundingBound': bound,
        'residualExplanation': 'Cause unknown; individual values preserved. Compatibility with rounding is not evidence of its cause.',
        'rowsByPhysicalPage': {str(n):sum(r[-1]==n for r in rows) for n in entry['pages']},
        'explicitZeroExpenseRows': sum(r[4] == 0 for r in rows),
        'exactDuplicateSourceRows': sum(n-1 for n in Counter(tuple(r[:5]) for r in rows).values()),
    }
    return rows, review


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-municipal-hydro'))
    p.add_argument('--output', type=Path, default=OUT)
    p.add_argument('--offline', action='store_true')
    args = p.parse_args()
    inputs = json.loads((OUT/'reviewed-inputs.json').read_text())['sources']
    pending, sources, aggregates = {}, [], []
    for entry in inputs:
        pdf = args.cache / (entry['slug']+'.pdf')
        if not pdf.exists():
            if args.offline: raise ValueError(f'Missing source {pdf}')
            data = urllib.request.urlopen(entry['sourceUrl'], timeout=60).read()
            if not data.startswith(b'%PDF-'): raise ValueError('Source did not return a PDF')
            pdf.parent.mkdir(parents=True, exist_ok=True); pdf.write_bytes(data)
        rows, review = process(pdf, entry)
        common = {
            'id': entry['id'], 'employerSlug': SLUG, 'employerName': 'Columbia Hydro Constructors Ltd.',
            'sector': 'Crown corporations', 'year': entry['year'], 'slug': entry['slug'],
            'title': f"Columbia Hydro Constructors Ltd. employee remuneration, {entry['year']}",
            'sourceUrl': entry['sourceUrl'], 'sourceIndexUrl': 'https://www.bchydro.com/about/accountability_reports/financial_reports.html',
            'sha256': entry['pdfSha256'], 'periodStart': entry['periodStart'], 'periodEnd': entry['periodEnd'],
            'periodType': 'fiscal', 'category': 'employee-remuneration', 'scope': 'named-employees-over-threshold',
            'threshold':75000, 'thresholdRule':'over', 'currency':'CAD', 'amountUnit':'dollars',
            'amountPrecision':'whole-dollar', 'nameDisclosure':'surname-and-initials', 'positionDisclosure':'not-published',
            'rowCount':len(rows), 'totalRemuneration':sum(r[3] for r in rows), 'totalExpenses':sum(r[4] for r in rows),
            'pages':entry['pages'], 'verifiedOn':'2026-10-30', 'validation':review,
            'notes':[
                'Separate legal employer mapped to the existing government-atlas subsidiary id; not combined with BC Hydro employees.',
                'Source initials are retained, moved after the surname for consistent name ordering; given names and unique identities are not inferred.',
                'The under-threshold aggregate and employer CPP/EI payment are not individual employee records.',
                'Original PDF bytes, all named rows and aggregate columns have now been checked. Source residuals remain unadjusted.'
            ]
        }
        if rows:
            normalized=json.dumps(rows, ensure_ascii=False, separators=(',',':')).encode()
            data=gzip.compress(normalized,compresslevel=9,mtime=0)
            file=entry['slug']+'.json.gzip';pending[file]=data
            sources.append({**common,'status':'verified','file':file,'dataSha256':digest(data),'normalizedSha256':digest(normalized)})
        else:
            aggregates.append({**common,'status':'verified-aggregate-only','scope':'aggregate-only-employee-schedule',
                'notes':common['notes']+['No named employee rows appear in the one-sheet 2017/18 schedule. This does not mean no employees or no payroll.']})
    pending['sources.json']=json_bytes({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources,'aggregateOnlySources':aggregates})
    args.output.mkdir(parents=True,exist_ok=True)
    for name,data in pending.items(): (args.output/name).write_bytes(data)
    print(json.dumps({'acceptedRows':sum(s['rowCount'] for s in sources),'acceptedPeriods':len(sources),'verifiedAggregateOnlyPeriods':len(aggregates),'sources':[{k:s[k] for k in ['year','rowCount','totalRemuneration','totalExpenses']} for s in sources]},indent=2))


if __name__=='__main__': main()
