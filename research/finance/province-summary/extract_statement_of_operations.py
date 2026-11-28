#!/usr/bin/env python3
"""Read the Consolidated Statement of Operations from each year's Summary Financial Statements.

The Province of British Columbia publishes its Summary Financial Statements with each year's
Public Accounts at

    https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/
        public-accounts/<yyyy-yy>/pa-<yyyy-yy>-summary-financial-statements.pdf

The statement of operations gives total revenue by source and total expense by function, in
$ millions, for the year (and, from 2000-01, the year's Estimates and the prior year as then
restated). This script finds that page in each PDF and writes every line as printed.

Standard library only, plus the `pdftotext` command (poppler) for the text layer.

    python3 -I extract_statement_of_operations.py [--fetch] [cache-dir] [out-dir]

  --fetch    download any PDF missing from the cache first (urllib)
  cache-dir  where the PDFs are (default: ./cache next to this script; not committed)
  out-dir    where the CSVs go (default: this script's directory)

Writes statement-of-operations.csv and statement-of-operations-footnotes.csv. The sums are checked
by scripts/build-budget.mjs, not here, so a misread line fails the site's build check.
"""

import csv
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST, LAST = 1999, 2025  # fiscal years 1999-00 to 2025-26
BASE = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts'
NUMBER = re.compile(r'(?<![\w(])(\(\d{1,3}(?:,\d{3})*\)|-?\d{1,3}(?:,\d{3})*|[–—])(?![\w)])')


def years():
    for start in range(FIRST, LAST + 1):
        yield f'{start}-{str(start + 1)[2:]}'


def url_for(year):
    return f'{BASE}/{year}/pa-{year}-summary-financial-statements.pdf'


def fetch(cache):
    os.makedirs(cache, exist_ok=True)
    for year in years():
        path = os.path.join(cache, f'pa-{year}-summary-financial-statements.pdf')
        if os.path.exists(path):
            continue
        request = urllib.request.Request(url_for(year), headers={'User-Agent': 'research-extractor'})
        with urllib.request.urlopen(request) as response, open(path, 'wb') as out:
            out.write(response.read())


def pages_of(pdf):
    text = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, check=True, text=True).stdout
    return text.split('\f')


def find_page(pages):
    """The statement of operations: its title in the page head, revenue and expense, and a result."""
    for index, page in enumerate(pages):
        lines = [line for line in page.splitlines() if line.strip()]
        head = '\n'.join(lines[:8])
        if not re.search(r'Statement of Operations', head) or re.search(r'by Sector|Notes? to|Change in|Cash Flow|Auditor', head):
            continue
        if any(re.match(r'\s*Revenue\b', line) for line in lines) and any(re.match(r'\s*Expense\b', line) for line in lines):
            return index
    raise SystemExit('statement of operations not found')


def printed_page(page):
    first = next(line for line in page.splitlines() if line.strip())
    match = re.match(r'\s*(\d+)\s{3,}', first) or re.search(r'\s{3,}(\d+)\s*$', first)
    return match.group(1) if match else ''


def value(token):
    if token in '–—':
        return 0
    negative = token.startswith('(')
    number = int(token.strip('()').replace(',', ''))
    return -number if negative else number


def tokens(line):
    """The line with dot leaders blanked (positions kept), its label part and its numbers."""
    blank = re.sub(r'(?:\s?\.){3,}\.*|…+', lambda m: ' ' * len(m.group()), line)
    numbers = []
    # Numbers are read from the right while what remains ends in one, two or more spaces apart.
    rest = blank.rstrip()
    while True:
        match = re.search(r'(?:^|\s)(\(\d{1,3}(?:,\d{3})*\)|-?\d{1,3}(?:,\d{3})*|[–—])$', rest)
        if not match:
            break
        token = match.group(1)
        end = match.end(1)
        before = rest[:match.start(1)]
        # A figure stands two or more spaces clear of the label; a note reference such as
        # "(Note 27)" or a wrapped "7)" is set close to its words and stays label.
        if before.strip() and not before.endswith('  '):
            break
        numbers.insert(0, (token, end))
        rest = before.rstrip()
    label = rest.strip()
    return label, numbers


FOOTNOTE_MARK = re.compile(r'^(.*?[a-z)])(\d)$')


def clean_heading(label):
    """The heading without note references, footnote marks or the "Less:" that sets a sign."""
    text = re.sub(r'\s*\((?:see )?Notes?[^)]*\)', '', label)
    text = re.sub(r'\s*\(see page \d+\)', '', text)
    mark = FOOTNOTE_MARK.match(text)
    if mark and not re.search(r'\d{4}$', text):
        text = mark.group(1)
    return re.sub(r'\s+', ' ', text).strip()


def footnote_marks(label):
    text = re.sub(r'\s*\((?:see )?Notes?[^)]*\)', '', label).strip()
    mark = FOOTNOTE_MARK.match(text)
    return mark.group(2) if mark else ''


def read_rows(page):
    """Each printed line with its label and figures, joining labels that wrap onto the next line."""
    rows = []
    pending = None
    raw = page.splitlines()
    for line in raw:
        if not line.strip() or re.fullmatch(r'[\s.…]*', line):
            continue
        label, numbers = tokens(line)
        if re.fullmatch(r'(\$\s*)+', label.replace('Revenue', '').strip() or 'x') and '$' in line:
            # "Revenue  $  $  $": the units row, which also opens the revenue section.
            rows.append({'label': 'Revenue', 'numbers': [], 'dollars': [m.end() for m in re.finditer(r'\$', line)]})
            pending = None
            continue
        if numbers:
            if pending is not None and (not label or label[0].islower() or label[0].isdigit() or pending.endswith(('-', '(Note'))):
                joined = (pending[:-1] + label) if pending.endswith('-') else f'{pending} {label}'.strip()
                rows.append({'label': joined, 'numbers': numbers})
            else:
                if pending is not None:
                    rows.append({'label': pending, 'numbers': []})
                rows.append({'label': label, 'numbers': numbers})
            pending = None
        else:
            if pending is not None:
                if label[0].islower() or pending.endswith(('-', '(Note')):
                    pending = (pending[:-1] + label) if pending.endswith('-') else f'{pending} {label}'
                    continue
                rows.append({'label': pending, 'numbers': []})
            pending = label
    if pending is not None:
        rows.append({'label': pending, 'numbers': []})
    return rows


def columns_of(rows):
    """Column right edges, from the rows that fill every column."""
    units = next(row for row in rows if row.get('dollars'))
    count = len(units['dollars'])
    full = [row['numbers'] for row in rows if len(row['numbers']) == count]
    edges = []
    for at in range(count):
        ends = sorted(numbers[at][1] for numbers in full)
        edges.append(ends[len(ends) // 2])
    return edges


def place(numbers, edges):
    """Each figure to the column whose right edge is nearest."""
    if len(numbers) == len(edges):
        return [value(token) for token, _ in numbers]
    placed = [None] * len(edges)
    for token, end in numbers:
        at = min(range(len(edges)), key=lambda i: abs(edges[i] - end))
        placed[at] = value(token)
    return placed


def extract(year, pdf):
    pages = pages_of(pdf)
    index = find_page(pages)
    page = pages[index]
    rows = read_rows(page)
    edges = columns_of(rows)
    names = ['estimate', 'actual', 'prior_year'] if len(edges) == 3 else ['actual', 'prior_year']
    title = ' '.join(line.strip() for line in page.splitlines()[:12] if re.search(r'Statement of Operations', line))
    out = []
    section = None
    closed = set()
    for row in rows:
        label = row['label']
        heading = clean_heading(label)
        if row.get('dollars'):
            section = 'revenue'
            continue
        if re.match(r'Expense\b', label) and not row['numbers']:
            section = 'expense'
            continue
        if section is None or not row['numbers']:
            continue
        figures = dict(zip(names, place(row['numbers'], edges)))
        if section in ('revenue', 'expense') and section not in closed:
            is_total = not heading or re.match(r'(Total|Operating expense)', heading, re.I)
            kind = 'total' if is_total else 'item'
            if is_total:
                closed.add(section)
        else:
            section = 'result'
            # The accumulated surplus and comprehensive income follow; footnote marks print as lone digits.
            if not heading or re.match(r'Accumulated|Other comprehensive|and agencies|corporations and agencies', heading, re.I):
                break
            kind = 'result' if heading.startswith('Surplus (deficit) for the year') else 'adjustment'
        out.append({
            'fiscal_year': year, 'fy_end': f'{int(year[:4]) + 1}-03-31', 'section': section, 'kind': kind,
            'heading': heading or ('Total' if kind == 'total' else ''), 'label_as_printed': label,
            'footnotes': footnote_marks(label),
            'estimate': figures.get('estimate', ''), 'actual': figures['actual'], 'prior_year': figures['prior_year'],
            'unit': '$ millions', 'source_url': url_for(year), 'pdf_page': index + 1, 'printed_page': printed_page(page),
            'table_title': title,
        })
    notes = []
    tail = page.split('\n')
    for at, line in enumerate(tail):
        if re.fullmatch(r'\s*\d\s*', line) and at + 1 < len(tail):
            text = []
            for follow in tail[at + 1:]:
                if not follow.strip() or re.fullmatch(r'\s*\d\s*', follow) or 'accompanying notes' in follow:
                    break
                text.append(follow.strip())
            notes.append({'fiscal_year': year, 'mark': line.strip(), 'text': re.sub(r'-\s+(?=[a-z])', '', ' '.join(text)),
                          'source_url': url_for(year), 'pdf_page': index + 1})
    for row in out:
        for key in ('estimate', 'actual', 'prior_year'):
            row[key] = '' if row[key] is None else row[key]
    return out, notes


def main(argv):
    do_fetch = '--fetch' in argv
    args = [arg for arg in argv if not arg.startswith('--')]
    cache = args[0] if args else os.path.join(HERE, 'cache')
    out_dir = args[1] if len(args) > 1 else HERE
    if do_fetch:
        fetch(cache)
    rows, notes = [], []
    for year in years():
        pdf = os.path.join(cache, f'pa-{year}-summary-financial-statements.pdf')
        if not os.path.exists(pdf):
            print(f'{year}: no PDF in {cache} (run with --fetch)', file=sys.stderr)
            continue
        got, marks = extract(year, pdf)
        for line, row in enumerate(got, 1):
            row['line'] = line
        rows += got
        notes += marks
    fields = ['fiscal_year', 'fy_end', 'section', 'line', 'kind', 'heading', 'label_as_printed', 'footnotes',
              'estimate', 'actual', 'prior_year', 'unit', 'source_url', 'pdf_page', 'printed_page', 'table_title']
    with open(os.path.join(out_dir, 'statement-of-operations.csv'), 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    with open(os.path.join(out_dir, 'statement-of-operations-footnotes.csv'), 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['fiscal_year', 'mark', 'text', 'source_url', 'pdf_page'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(notes)
    print(f'{len(rows)} lines from {len({row["fiscal_year"] for row in rows})} years; {len(notes)} footnotes')


if __name__ == '__main__':
    main(sys.argv[1:])
