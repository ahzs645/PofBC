"""Record a statement of operations read by eye from the page image, where the PDF has no text layer
(a scan). The same checks as transcribe_statement.py apply: the revenue lines must add to the
printed revenue total, the expense lines to the printed expense total, and revenue less expense to
the printed result. Nothing is written unless they pass.

Usage (from the repository root), with the lines on standard input, one per line:

    python3 -I research/finance/scripts/record_statement.py <body> <year> <pdf url> <pdf page> \
        <printed page> <unit> "<statement title>" < lines.txt

    revenue|<label as printed>|<amount as printed>|<category>
    revenue-total|<label or (total, unlabelled)>|<amount>
    expense|<label>|<amount>
    expense-total|<label>|<amount>
    surplus|<label>|<amount>

Amounts are as printed, in the statement's unit; brackets are negative.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcribe_statement import OUT, write_index  # noqa: E402
from statement_text import amount  # noqa: E402

CATEGORIES = {'province', 'federal', 'own-source', 'other-entity', 'investment', 'deferred-capital-amortization', 'other'}


def main():
    body, year, url, page, printed, unit, title = sys.argv[1:8]
    rows = []
    for line in sys.stdin.read().strip().split('\n'):
        parts = line.split('|')
        section, label, value = parts[0].strip(), parts[1].strip(), amount(parts[2])
        category = parts[3].strip() if len(parts) > 3 else ''
        if section == 'revenue' and category not in CATEGORIES:
            raise SystemExit(f'{label}: category {category!r}')
        rows.append((section, label, value, category))
    total = lambda s: sum(r[2] for r in rows if r[0] == s)
    one = lambda s: [r[2] for r in rows if r[0] == s]
    checks = []
    for section, total_section in (('revenue', 'revenue-total'), ('expense', 'expense-total')):
        if len(one(total_section)) != 1 or total(section) != one(total_section)[0]:
            checks.append(f'{section} lines {total(section):,} against {one(total_section)}')
    if len(one('surplus')) != 1 or one('revenue-total')[0] - one('expense-total')[0] != one('surplus')[0]:
        checks.append('revenue less expense is not the printed result')
    if checks:
        raise SystemExit('not written: ' + '; '.join(checks))
    folder = os.path.join(OUT, body)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f'{year}.csv'), 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['section', 'label_as_printed', 'amount_as_printed', 'category', 'pdf_page', 'printed_page'])
        for section, label, value, category in rows:
            w.writerow([section, label, value, category, page, printed])
    write_index({'body_id': body, 'fiscal_year': year, 'url': url, 'unit': unit, 'statement_title': title, 'pdf_page': page,
                 'printed_page': printed, 'pdf_pages': '', 'method': 'scanned page with no text layer: read from the page image; totals reconciled',
                 'checked': '2026-11-27'})
    print(f'written {folder}/{year}.csv: revenue {one("revenue-total")[0]:,}, expense {one("expense-total")[0]:,}, result {one("surplus")[0]:,}')


if __name__ == '__main__':
    main()
