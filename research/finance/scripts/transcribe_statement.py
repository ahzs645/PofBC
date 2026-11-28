"""Transcribe the revenue and expense lines of one statement of operations into
research/finance/statements/<body>/<fiscal year>.csv, and check them against the printed totals.

Usage (from the repository root):

    python3 -I research/finance/scripts/transcribe_statement.py <body id> <fiscal year> <pdf url> \
        <pdf page> [--column N] [--unit thousands|dollars] [--printed P] [--title "..."] [--write]

It reads the page from the text that statement_text.py keeps (fetching the PDF if needed), and
takes, for each line between the "Revenue" heading and the expense total, the label and the figure
in column N counted from the right (2 by default: the current year, with the prior year to its
right). Labels that wrap onto a second line are joined. Every line gets a revenue category from the
fixed vocabulary (province, federal, own-source, other-entity, investment,
deferred-capital-amortization, other) by the rules below; RULES_BY_BODY can override a label.

Without --write it prints the page, the lines it read and the checks, and writes nothing. With
--write it writes the CSV only if every check passes: the revenue lines add to the printed revenue
total, the expense lines to the printed expense total, and revenue less expense to the printed
surplus or deficit line. The page is still read by a person: the script only does the arithmetic.

The CSV keeps every figure as printed (in the statement's unit) with its PDF page and printed page.
index.csv in the same folder records the statement: body, year, URL, unit, title and pages.
"""

import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statement_text import pages_of, amount, NUMBER  # noqa: E402

OUT = os.path.join('research', 'finance', 'statements')

# Revenue categories, matched in order against the label as printed (lower case).
RULES = [
    (r'recognized from deferred capital|amortization of deferred|deferred capital (contributions|grants) (amortized|recognized)|capital (contributions|grants?) (amortized|recognized)|amortization of (capital|deferred)', 'deferred-capital-amortization'),
    (r'government business enterprise', 'other'),
    (r'recoveries from other health authorities|bc government reporting entities|other government (reporting )?entit|from members', 'other-entity'),
    (r'government of canada|federal|canada\b(?! student)', 'federal'),
    (r'ministry|province of british columbia|provincial|medical services plan|government of british columbia|grants? from the province', 'province'),
    (r'investment|interest|endowment income|income from investments', 'investment'),
    (r'tuition|student fees|patients|clients and residents|ancillary|sales|fees|contract services|rentals?|parking|passenger|fares|premium|tolls|admission', 'own-source'),
]


INDEX_FIELDS = ['body_id', 'fiscal_year', 'url', 'unit', 'statement_title', 'pdf_page', 'printed_page', 'pdf_pages', 'method', 'checked', 'note']


def write_index(entry):
    """Add or replace one statement in statements/index.csv, keeping every other row and its note."""
    index = os.path.join(OUT, 'index.csv')
    rows = list(csv.DictReader(open(index, newline=''))) if os.path.exists(index) else []
    old = next((r for r in rows if r['body_id'] == entry['body_id'] and r['fiscal_year'] == entry['fiscal_year']), {})
    rows = [r for r in rows if r is not old]
    rows.append({**entry, 'note': entry.get('note') or old.get('note', '')})
    rows.sort(key=lambda r: (r['body_id'], r['fiscal_year']))
    temporary = index + '.tmp'
    with open(temporary, 'w', newline='') as f:
        w = csv.DictWriter(f, INDEX_FIELDS, lineterminator='\n', restval='', extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    os.replace(temporary, index)


def categorize(label):
    low = label.lower()
    for pattern, category in RULES:
        if re.search(pattern, low):
            return category
    return 'other'


def read(page_text, column):
    """The page's revenue lines, revenue total, expense lines, expense total and surplus line."""
    state = None
    revenue, expense = [], []
    totals = {}
    pending = []
    for raw in page_text.split('\n'):
        line = raw.strip()
        if not line:
            continue
        words = line.split()
        nums = []
        while words and (words[-1] == '$' or NUMBER.match(words[-1].replace('$', ''))):
            token = words.pop()
            if token != '$':
                nums.insert(0, token)
        label = ' '.join(w for w in words if w != '$').strip()
        if state is None and re.match(r'^revenues?\b', label, re.I) and not nums:
            state = 'revenue'
            continue
        if state is None:
            continue
        if re.match(r'^expenses?\b', label, re.I) and len(nums) < column:
            state = 'expense'
            pending = []
            continue
        if len(nums) < column:
            # A label that wraps after its figures ("... and BC  134,904" / "government reporting
            # entities") continues the line above when it starts in lower case.
            target = revenue if state == 'revenue' else expense if state == 'expense' else None
            if label and label[0].islower() and not pending and target:
                target[-1] = (f'{target[-1][0]} {label}', target[-1][1])
            elif label and not re.match(r'^(see accompanying|\d+$)', label, re.I):
                pending.append(label)
            continue
        value = amount(nums[-column])
        full = ' '.join(pending + [label]).strip()
        pending = []
        if state == 'revenue':
            if not full or re.match(r'^total', full, re.I):
                totals['revenue'] = (full or '(total, unlabelled)', value)
                state = 'between'
            else:
                revenue.append((full, value))
        elif state == 'between':
            continue
        elif state == 'expense':
            if not full or re.match(r'^total', full, re.I):
                totals['expense'] = (full or '(total, unlabelled)', value)
                state = 'after'
            else:
                expense.append((full, value))
        elif state == 'after':
            totals['surplus'] = (full, value)
            break
    return revenue, totals.get('revenue'), expense, totals.get('expense'), totals.get('surplus')


def main():
    args = [a for a in sys.argv[1:]]
    opt = lambda name, default=None: args[args.index(name) + 1] if name in args else default
    body, year, url, page = args[0], args[1], args[2], int(args[3])
    column = int(opt('--column', 2))
    unit = opt('--unit', 'thousands')
    printed = opt('--printed', '')
    title = opt('--title', '')
    pages = pages_of(url)
    text = pages[page - 1]
    if not title:
        title = next((line.strip() for line in text.split('\n')[:8] if re.match(r'^\s*(consolidated )?statements? of', line, re.I)), '')
    if not printed:
        # The folio, where the page prints one on a line of its own at the foot.
        tail = [line.strip() for line in text.split('\n') if line.strip()]
        printed = tail[-1] if tail and re.fullmatch(r'\d{1,3}', tail[-1]) else ''
    if '--quiet' not in args:
        print(re.sub(r' {3,}', ' | ', text))
    revenue, rtotal, expense, etotal, surplus = read(text, column)
    checks = []
    if not rtotal or not etotal or not surplus:
        checks.append(f'missing total: revenue {rtotal} expense {etotal} surplus {surplus}')
    else:
        if sum(v for _, v in revenue) != rtotal[1]:
            checks.append(f'revenue lines {sum(v for _, v in revenue)} != total {rtotal[1]}')
        if sum(v for _, v in expense) != etotal[1]:
            checks.append(f'expense lines {sum(v for _, v in expense)} != total {etotal[1]}')
        if rtotal[1] - etotal[1] != surplus[1]:
            checks.append(f'revenue - expense {rtotal[1] - etotal[1]} != {surplus[0]} {surplus[1]}')
    rows = [('revenue', label, value, categorize(label)) for label, value in revenue]
    if rtotal:
        rows.append(('revenue-total', rtotal[0], rtotal[1], ''))
    rows += [('expense', label, value, '') for label, value in expense]
    if etotal:
        rows.append(('expense-total', etotal[0], etotal[1], ''))
    if surplus:
        rows.append(('surplus', surplus[0], surplus[1], ''))
    for row in rows:
        print('  ' + ' | '.join(str(x) for x in row))
    print('CHECKS:', 'all pass' if not checks else '; '.join(checks), '| read: revenue', rtotal and f'{rtotal[1]:,}', 'expense', etotal and f'{etotal[1]:,}', 'surplus', surplus and f'{surplus[1]:,}')
    if '--write' in args:
        if checks:
            raise SystemExit('not written: checks fail')
        folder = os.path.join(OUT, body)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f'{year}.csv'), 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['section', 'label_as_printed', 'amount_as_printed', 'category', 'pdf_page', 'printed_page'])
            for section, label, value, category in rows:
                w.writerow([section, label, value, category, page, printed])
        write_index({'body_id': body, 'fiscal_year': year, 'url': url, 'unit': unit, 'statement_title': title,
                     'pdf_page': page, 'printed_page': printed, 'pdf_pages': len(pages), 'method': 'pdftotext -layout; every line checked against the page; totals reconciled',
                     'checked': '2026-11-27'})
        print('written', os.path.join(folder, f'{year}.csv'))


if __name__ == '__main__':
    main()
