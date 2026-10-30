#!/usr/bin/env python3
"""Import reviewed BCIT employee SOFI schedules, preserving their printed names.

Requires Poppler pdftotext and pdfplumber. Source fingerprints, fiscal headings,
complete Exhibit B page sequences, per-page counts, every name and monetary cell
(independently extracted from PDF coordinates), and printed totals are checked
before outputs are written. Normal salary builds need neither PDFs nor PDF tools.
Year arguments are fiscal year END. New sources require reviewed-inputs.json.
"""
import argparse
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / 'research/salaries/bcit/reviewed-inputs.json'
INDEX_URL = 'https://www.bcit.ca/financial-services/financial-reports/'
EMPLOYER = 'bcit'
AMOUNT = r'(?:\d{1,3}(?:,\d{3})+|\d+)'
EXPENSE = rf'(?:\({AMOUNT}\)|{AMOUNT}|-)'
ROW = re.compile(rf'^\s*([^\s\d].*?)\s{{2,}}({AMOUNT})\s+({EXPENSE})\s*$')
TOTAL = re.compile(rf'^\s*({AMOUNT})\s+({AMOUNT})\s*$')
PAGE_HEADER = re.compile(r'^\s*Page\s*(\d+)\s+EXHIBIT B\s*$', re.M)
UNDER_LABEL = re.compile(r'ZZ --- Salaries under \$75,?000')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def number(value):
    if value == '-':
        return None
    if not re.fullmatch(EXPENSE, value):
        raise ValueError(f'Invalid whole-dollar cell: {value!r}')
    return int(value.replace(',', '').replace('(', '-').replace(')', ''))


def normalized_name(value):
    return ' '.join(value.split())


def join_split_amounts(words):
    """Rejoin adjacent numeric glyph groups within one PDF monetary cell.

    The 2014/15 summary inserts a whitespace character inside 73,371,238,
    making the word extractor return '7' and '3,371,238' despite a 0.04-point
    glyph gap. Geometry, not an assumed numeric value, establishes the join.
    """
    result = []
    for word in sorted(words, key=lambda item: item['x0']):
        if (result and word['x0'] >= 250 and result[-1]['x0'] >= 250
                and 0 <= word['x0'] - result[-1]['x1'] < 1.5
                and re.fullmatch(r'[\d,()]+', word['text'])
                and re.fullmatch(r'[\d,()]+', result[-1]['text'])):
            result[-1] = {**result[-1], 'text': result[-1]['text'] + word['text'], 'x1': word['x1']}
        else:
            result.append(word)
    return result


def parse(text, spec):
    """Parse only the complete, independently dated employee Exhibit B."""
    pages = text.split('\f')
    if pages[-1].strip() == '':
        pages.pop()
    year = spec['yearEnd']
    heading = f'FOR THE YEAR ENDED MARCH 31, {year}'
    if heading not in pages[0] or len(pages) != spec['pdfPageCount']:
        raise ValueError('BCIT fiscal cover or physical PDF page count changed')
    title_pages = [i for i, page in enumerate(pages, 1)
                   if re.search(r'STATEMENT OF EMPLOYEES[’\x27] REMUNERATION AND EXPENSES', page)]
    if title_pages != [spec['pages'][0] - 1]:
        raise ValueError('Missing, repeated or relocated employee schedule title')
    if heading not in pages[title_pages[0] - 1]:
        raise ValueError('Employee schedule fiscal year mismatch')
    board_page = pages[spec['pages'][-1]]
    if 'STATEMENT OF BOARD OF GOVERNORS' not in board_page or heading not in board_page:
        raise ValueError('Employee schedule does not end at the expected board schedule')
    approval_pages = [i for i, page in enumerate(pages, 1)
                      if 'STATEMENT OF FINANCIAL INFORMATION APPROVAL' in page and heading in page]
    if not approval_pages:
        raise ValueError('Missing financial information approval section')
    rows, found_pages, printed_pages, counts, cells_by_page = [], [], [], [], {}
    totals, under_totals = [], []
    for pdf_page, page in enumerate(pages, 1):
        header = PAGE_HEADER.search(page)
        if not header:
            continue
        found_pages.append(pdf_page)
        printed_pages.append(int(header[1]))
        page_rows, cells = [], []
        for line in page.splitlines():
            total = TOTAL.fullmatch(line)
            if total:
                pay, expenses = map(number, total.groups())
                totals.append([pay, expenses])
                cells.append(['', pay, expenses])
                continue
            match = ROW.fullmatch(line)
            if match:
                name, pay, expenses = match.groups()
                name, pay, expenses = normalized_name(name), number(pay), number(expenses)
                cells.append([name, pay, expenses])
                if UNDER_LABEL.fullmatch(name):
                    under_totals.append([pay, expenses])
                    continue
                if not re.search(r'[^\W\d_]', name) or pay < 75000 or name.startswith(('Total', 'ZZ ---')):
                    raise ValueError(f'Invalid employee row on PDF page {pdf_page}: {line!r}')
                page_rows.append([EMPLOYER, name, None, pay, expenses, pdf_page])
                continue
            if (not line.strip() or PAGE_HEADER.fullmatch(line)
                    or re.fullmatch(r'\s*(?:NAME|Name)\s+(?:SALARY\*|Remuneration)\s+(?:EXPENSES|Expenses)\s*', line)
                    or line.strip().startswith(('*Salary may include', '*May include'))):
                continue
            raise ValueError(f'Unparsed employee-schedule line on PDF page {pdf_page}: {line!r}')
        rows.extend(page_rows)
        counts.append(len(page_rows))
        cells_by_page[pdf_page] = cells
    if (found_pages != spec['pages'] or printed_pages != spec['printedPages']
            or counts != spec['pageCounts'] or len(rows) != spec['rowCount']):
        raise ValueError(f'Incomplete or changed employee page sequence/counts: {found_pages}, {counts}')
    if found_pages != list(range(found_pages[0], found_pages[-1] + 1)):
        raise ValueError('Employee schedule physical pages are not contiguous')
    if (printed_pages != list(range(printed_pages[0], printed_pages[-1] + 1))
            and not spec.get('printedPaginationException')):
        raise ValueError('Employee schedule printed pages are not contiguous')
    if totals != [[spec['printedTotalRemuneration'], spec['printedTotalExpenses']]]:
        raise ValueError(f'Missing, repeated or changed printed totals: {totals}')
    if under_totals != [[spec['underThresholdRemuneration'], None]]:
        raise ValueError(f'Missing, repeated or changed below-threshold aggregate: {under_totals}')
    pay_sum = sum(row[3] for row in rows)
    expense_sum = sum(row[4] for row in rows if row[4] is not None)
    if (pay_sum, expense_sum) != (spec['totalRemuneration'], spec['totalDisclosedExpenses']):
        raise ValueError('Employee row sums differ from the reviewed source values')
    pay_residual = pay_sum + under_totals[0][0] - totals[0][0]
    expense_residual = expense_sum - totals[0][1]
    rounding_bound = (len(rows) + 2) * 0.5
    if max(abs(pay_residual), abs(expense_residual)) > rounding_bound:
        raise ValueError('Printed row/aggregate discrepancy exceeds the independent whole-dollar rounding bound')
    if sum(',' not in row[1] for row in rows) != spec['namesWithoutComma']:
        raise ValueError('Unexpected change in disclosed name boundaries')
    if sum(row[4] is not None and row[4] < 0 for row in rows) != spec['negativeExpenseRows']:
        raise ValueError('Unexpected change in expense recoveries')
    return rows, cells_by_page, {
        'remunerationResidual': pay_residual, 'expensesResidual': expense_residual,
        'maximumIndependentWholeDollarRoundingDifference': rounding_bound,
        'approvalPdfPages': approval_pages,
    }


def verify_coordinates(pdf_path, expected, spec):
    """Compare every name/cell with rows assembled using PDF word coordinates."""
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) != spec['pdfPageCount']:
            raise ValueError('Independent PDF page count disagrees')
        for page_no, expected_cells in expected.items():
            words = sorted(pdf.pages[page_no - 1].extract_words(x_tolerance=1.5, y_tolerance=2),
                           key=lambda word: (word['top'], word['x0']))
            lines = []
            for word in words:
                if not lines or abs(word['top'] - lines[-1][0]['top']) > 2:
                    lines.append([word])
                else:
                    lines[-1].append(word)
            actual = []
            for line in lines:
                line = join_split_amounts(line)
                if (len(line) < 2 or not re.fullmatch(AMOUNT, line[-2]['text'])
                        or not re.fullmatch(EXPENSE, line[-1]['text'])):
                    continue
                # Only the salary/expense columns, not footer numbers or dates.
                if line[-2]['x0'] < 250 or line[-1]['x0'] <= line[-2]['x1']:
                    raise ValueError(f'Unexpected monetary geometry on PDF page {page_no}')
                actual.append([normalized_name(' '.join(word['text'] for word in line[:-2])),
                               number(line[-2]['text']), number(line[-1]['text'])])
            if actual != expected_cells:
                mismatch = next(((i, a, b) for i, (a, b) in enumerate(zip(actual, expected_cells)) if a != b), None)
                raise ValueError(f'Independent extraction differs on PDF page {page_no}: '
                                 f'{len(actual)} vs {len(expected_cells)} cells; first mismatch {mismatch}')


def make_source(spec, rows, compressed, normalized, checks, verified_on):
    end = spec['yearEnd']
    year = f'{end - 1}/{str(end)[-2:]}'
    slug = year.replace('/', '-')
    notes = [
        'The complete Exhibit B employee schedule is imported. Board members, suppliers, totals and the below-threshold aggregate are excluded.',
        ('Salary may include overtime, allowances, part-time and termination settlement, as stated in this report.'
         if end <= 2021 else 'Remuneration may include overtime, allowances and part-time salary, as stated in this report.'),
        'Printed dash expenses remain missing; printed numeric zeroes and negative expense recoveries retain their meanings.',
        (f"Displayed named remuneration plus the below-threshold aggregate differs from the printed total by ${checks['remunerationResidual']:+,}; "
         f"displayed named expenses differ from the printed expense total by ${checks['expensesResidual']:+,}. "
         'Both comparisons fit the independent whole-dollar rounding bound, but the report does not establish the cause. No row value is adjusted. '
         'The under-threshold expense aggregate is a dash, not a measured zero.'),
    ]
    if end == 2021:
        notes.append('The 2020/21 source itself truncates many name strings to 14 characters, including 13 names without a surname/given-name comma. The printed strings are preserved; names are not expanded from other years and these records cannot establish unique identities.')
    elif spec['namesWithoutComma']:
        notes.append(f"{spec['namesWithoutComma']} published name lacks a surname/given-name comma. Its order is retained without guessing a boundary.")
    if spec.get('printedPaginationException'):
        notes.append(spec['printedPaginationException'])
    return {
        'id': f'bcit-sofi-{slug}-employees', 'employerSlug': EMPLOYER,
        'employerName': 'British Columbia Institute of Technology', 'sector': 'Education',
        'year': year, 'slug': slug, 'file': f'{slug}-employees.json.gzip',
        'title': f'BCIT Financial Information Act Return {year}: Exhibit B',
        'sourceUrl': spec['sourceUrl'], 'sourceIndexUrl': INDEX_URL,
        'sha256': spec['sha256'], 'dataSha256': digest(compressed), 'normalizedSha256': digest(normalized),
        'periodStart': f'{end - 1}-04-01', 'periodEnd': f'{end}-03-31', 'currency': 'CAD',
        'category': 'employee-remuneration', 'scope': 'employee-remuneration',
        'scopeDescription': 'Named employees earning $75,000 or more, Exhibit B',
        'threshold': 75000, 'thresholdRule': 'at-least', 'amountPrecision': 'whole-dollars',
        'nameDisclosure': 'published-truncated-names' if end == 2021 else 'as-published',
        'positionDisclosure': 'not-published', 'rowCount': len(rows),
        'totalRemuneration': spec['totalRemuneration'], 'totalDisclosedExpenses': spec['totalDisclosedExpenses'],
        'pages': spec['pages'], 'printedPages': spec['printedPages'],
        'status': 'verified', 'verifiedOn': verified_on, 'notes': notes,
        'validation': {
            'physicalPdfPages': [spec['pages'][0], spec['pages'][-1]],
            'printedPages': [spec['printedPages'][0], spec['printedPages'][-1]],
            'internalFiscalYearEnd': end, 'sourceFingerprintLocked': True,
            'completeEmployeeSchedule': True, 'rowCountChecked': True,
            'rowCountsByPdfPage': dict(zip(spec['pages'], spec['pageCounts'])),
            'allNamesAndMonetaryCellsIndependentlyVerified': True,
            'independentMethod': 'pdftotext layout rows compared cell-for-cell with pdfplumber positioned-word rows, including both aggregates',
            'visualReviewPdfPages': spec.get('visualReviewPdfPages', []),
            'signedApprovalVisuallyVerified': True,
            'signedApprovalDate': spec['signedApprovalDate'],
            'summaryTotalReconciled': checks['remunerationResidual'] == checks['expensesResidual'] == 0,
            'roundingCompatible': True, **checks,
            'namedRemunerationSum': spec['totalRemuneration'],
            'underThresholdAggregateExcluded': spec['underThresholdRemuneration'],
            'underThresholdExpenses': None, 'printedAllEmployeeRemuneration': spec['printedTotalRemuneration'],
            'namedExpensesSum': spec['totalDisclosedExpenses'], 'printedAllEmployeeExpenses': spec['printedTotalExpenses'],
            'namesWithoutVerifiedBoundary': spec['namesWithoutComma'],
            'expenseDashesRetainedAsMissing': sum(row[4] is None for row in rows),
            'negativeExpenseRows': spec['negativeExpenseRows'], 'unparsedNumericLines': 0,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-salary-sources'))
    parser.add_argument('--output', type=Path, default=ROOT / 'research/salaries/bcit')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--years', type=int, nargs='+', help='Reviewed fiscal year ends to process; default all')
    parser.add_argument('--verified-on', default=date.today().isoformat())
    args = parser.parse_args()
    specs = json.loads(INPUTS.read_text())['sources']
    allowed = {spec['yearEnd'] for spec in specs}
    if args.years and set(args.years) - allowed:
        parser.error(f'Unreviewed fiscal year ends: {sorted(set(args.years) - allowed)}')
    selected = [spec for spec in specs if not args.years or spec['yearEnd'] in args.years]
    outputs = []
    for spec in selected:
        path = args.cache / f"bcit-financial-{spec['yearEnd']}.pdf"
        if not path.exists():
            if args.offline:
                raise ValueError(f'Missing reviewed source: {path}')
            request = urllib.request.Request(spec['sourceUrl'], headers={'User-Agent': 'PofBC salary source importer'})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            if not raw.startswith(b'%PDF') or digest(raw) != spec['sha256']:
                raise ValueError(f"Official {spec['yearEnd']} source changed or is not a PDF; review before importing")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        raw = path.read_bytes()
        if digest(raw) != spec['sha256']:
            raise ValueError(f"Official {spec['yearEnd']} PDF changed; review before importing")
        text = subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)
        rows, cells, checks = parse(text, spec)
        verify_coordinates(path, cells, spec)
        normalized = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode()
        compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
        source = make_source(spec, rows, compressed, normalized, checks, args.verified_on)
        outputs.append((source, compressed))
        print(f"BCIT {source['year']}: {len(rows):,} rows, ${source['totalRemuneration']:,} remuneration; "
              f"residuals ${checks['remunerationResidual']:+,} / ${checks['expensesResidual']:+,}; all rows independently checked.", flush=True)
    # A validation failure above leaves every accepted input untouched.
    if args.check_only:
        return
    args.output.mkdir(parents=True, exist_ok=True)
    registry_path = args.output / 'sources.json'
    registry = json.loads(registry_path.read_text()) if registry_path.exists() else {'version': 1, 'sources': []}
    replacements = {source['id'] for source, _ in outputs}
    registry['sources'] = sorted([source for source in registry['sources'] if source['id'] not in replacements]
                                 + [source for source, _ in outputs], key=lambda source: source['year'])
    registry['rowSchema'] = ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage']
    for source, compressed in outputs:
        (args.output / source['file']).write_bytes(compressed)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
