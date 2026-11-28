"""Extract the Public Accounts' "Consolidated Revenue Fund: Schedule of Voted Appropriations by
Ministry" from each year's CRF Supplementary Schedules PDF, as printed.

Usage (from the repository root; needs poppler's pdftotext):

    python3 -I research/finance/scripts/extract_voted_appropriations.py \
        research/finance/cache/crf  research/finance/estimates

It reads `pa-<yyyy-yy>-crf-supplementary-schedules.pdf` from the cache directory (fetched from
https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/<yyyy-yy>/pa-<yyyy-yy>-crf-supplementary-schedules.pdf)
and writes, in $ thousands as printed:

  votes.csv        one row per vote and the ministry or special office that accessed it: the
                   Estimates (the voted appropriation as presented to the Legislative Assembly), other
                   authorizations, total appropriation, total actual expense and the variance, each
                   with its PDF page
  vote-totals.csv  the printed total of every vote that more than one ministry accessed, and the
                   printed "Total Voted Expense" of each year
  checks.csv       each printed total against the sum of the rows it covers

How it reads a page: words come from `pdftotext -bbox` with their positions. The row of "$" signs
under the headings gives the five figure columns; a figure belongs to the last column whose "$"
starts left of the figure's right edge (figures are right-aligned under their "$"). A vote number
opens a vote; text between the description column and the figures is the accessing ministry, which
may wrap onto the next line. A line of figures with no ministry before it is the vote's total. A
blank cell stays blank. Brackets are negative.
"""

import csv
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

BASE = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/'
NUMBER = re.compile(r'^\(?-?\d[\d,]*\)?$')
TITLE = 'Schedule of Voted Appropriations by Ministry'
COLUMNS = ['estimates', 'other_authorizations', 'total_appropriation', 'actual_expense', 'variance']


def words_of(pdf, page):
    out = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-bbox', pdf, '-'], capture_output=True, text=True).stdout
    out = re.sub(r'<!DOCTYPE[^>]*>', '', out).replace('xmlns="http://www.w3.org/1999/xhtml"', '')
    root = ET.fromstring(out)
    words = []
    raw = [(w.text or '').strip() for w in root.iter('word')]
    boxes = [tuple(float(w.get(k)) for k in ('xMin', 'yMin', 'xMax', 'yMax')) for w in root.iter('word')]
    # A landscape table printed on a portrait page runs vertically: reading order runs towards
    # smaller y, and lines advance with x. Turn it so rows run down and columns run right.
    turned = any(t.startswith('Appropriations') and (b[3] - b[1]) > 2 * (b[2] - b[0]) for t, b in zip(raw, boxes))
    for t, (x0, y0, x1, y1) in zip(raw, boxes):
        t = re.sub(r'\.{2,}$', '', t)  # dot leaders run onto a word in some years
        if not t:
            continue
        if turned:
            words.append({'t': t, 'x0': -y1, 'x1': -y0, 'y': x0})
        else:
            words.append({'t': t, 'x0': x0, 'x1': x1, 'y': y0})
    if turned:
        shift = -min(w['x0'] for w in words)
        for w in words:
            w['x0'] += shift
            w['x1'] += shift
    return words


def page_text(pdf, page):
    return subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-layout', pdf, '-'], capture_output=True, text=True).stdout


def page_count(pdf):
    info = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
    return int(re.search(r'Pages:\s+(\d+)', info).group(1))


def lines_of(words):
    lines = []
    for w in sorted(words, key=lambda w: (w['y'], w['x0'])):
        if lines and abs(lines[-1]['y'] - w['y']) < 3.5:
            lines[-1]['words'].append(w)
        else:
            lines.append({'y': w['y'], 'words': [w]})
    for line in lines:
        line['words'].sort(key=lambda w: w['x0'])
    return lines


def amount(t):
    neg = t.startswith('(')
    value = int(t.strip('()').replace(',', ''))
    return -value if neg else value


def printed_page(text):
    head = text.strip().split('\n')[0].strip()
    m = re.match(r'^(\d+)\s', head) or re.search(r'\s(\d+)$', head)
    return m.group(1) if m else ''


def schedule_pages(pdf):
    pages = []
    for page in range(6, min(page_count(pdf), 40) + 1):
        text = page_text(pdf, page)
        if TITLE in text and 'Vote' in text and 'Accessing' in text:
            pages.append(page)
    return pages


def extract(pdf, year):
    rows, totals, grand = [], [], None
    vote = None  # {'no', 'description', 'ministry_rows'}
    pending = []  # ministry name words
    for page in schedule_pages(pdf):
        words = words_of(pdf, page)
        text = page_text(pdf, page)
        folio = printed_page(text)
        lines = lines_of(words)
        dollars = None
        for line in lines:
            ts = [w['t'] for w in line['words']]
            if ts and all(t == '$' for t in ts) and len(ts) == 5:
                dollars = [w['x0'] for w in line['words']]
        if not dollars:
            raise SystemExit(f'{year} p.{page}: no "$" row')
        ministry_x = next(w['x0'] for w in words if w['t'].startswith('Ministry/Special')) - 10
        start = next(i for i, line in enumerate(lines) if [w['t'] for w in line['words']] == ['$'] * 5) + 1
        for line in lines[start:]:
            ws = line['words']
            if line is lines[-1] and len(ws) == 1 and re.fullmatch(r'\d{1,3}', ws[0]['t']):
                continue  # the page's folio
            texts = [w for w in ws if not NUMBER.match(w['t']) or w['x1'] < ministry_x]
            figures = [w for w in ws if NUMBER.match(w['t']) and w['x1'] >= dollars[0] - 5]
            label = ' '.join(w['t'] for w in texts)
            if re.match(r'^\d?\d?\s*(Amounts reported|For a breakdown|This schedule)', label) or label.startswith('PROVINCE OF') or label.startswith('PUBLIC ACCOUNTS'):
                break
            if label.startswith('Total Voted Expense'):
                pending = ['__grand__']
                if not figures:
                    continue
            first = ws[0]
            if re.fullmatch(r'\d{1,3}', first['t']) and first['x1'] < ministry_x - 100 and first['x0'] < dollars[0] - 300:
                vote = {'no': first['t'], 'description': [], 'page': page}
                pending = []
                desc = [w for w in texts[1:] if w['x0'] < ministry_x - 2]
                mins = [w for w in texts[1:] if w['x0'] >= ministry_x - 2]
                vote['description'] = [w['t'] for w in desc]
                pending += [w['t'] for w in mins]
            elif not figures:
                desc = [w for w in texts if w['x0'] < ministry_x - 2]
                mins = [w for w in texts if w['x0'] >= ministry_x - 2]
                if vote and desc:
                    vote['description'] += [w['t'] for w in desc]
                pending += [w['t'] for w in mins]
                continue
            else:
                if vote and pending != ['__grand__']:
                    vote['description'] += [w['t'] for w in texts if w['x0'] < ministry_x - 2]
                pending += [w['t'] for w in texts if w['x0'] >= ministry_x - 2]
            if not figures:
                continue
            values = {}
            for w in figures:
                column = max(i for i, x in enumerate(dollars) if x <= w['x1'])
                if COLUMNS[column] in values:
                    raise SystemExit(f'{year} p.{page}: two figures in {COLUMNS[column]}: {label}')
                values[COLUMNS[column]] = amount(w['t'])
            record = {c: values.get(c, '') for c in COLUMNS}
            source = {'pdf_page': page, 'printed_page': folio}
            if pending == ['__grand__']:
                grand = {'fiscal_year': year, 'vote': 'all', 'description': 'Total Voted Expense', **record, **source}
                pending = []
            elif pending:
                rows.append({'fiscal_year': year, 'vote': vote['no'], 'description': vote['description'],
                             'ministry_as_printed': ' '.join(pending), **record, **source})
                pending = []
            else:
                totals.append({'fiscal_year': year, 'vote': vote['no'], 'description': vote['description'], **record, **source})
    if not grand:
        raise SystemExit(f'{year}: no Total Voted Expense')
    # A description can wrap past the vote's first figures, so it is joined once the vote is read.
    for r in rows + totals:
        r['description'] = ' '.join(r['description'])
    return rows, totals, grand


def check(rows, totals, grand):
    out = []
    by_vote = {}
    for row in rows:
        by_vote.setdefault(row['vote'], []).append(row)
    voted = {t['vote'] for t in totals}
    for t in totals:
        members = by_vote.get(t['vote'], [])
        for c in COLUMNS:
            got = sum(r[c] or 0 for r in members)
            printed = t[c] or 0
            out.append({'fiscal_year': t['fiscal_year'], 'total': f"vote {t['vote']}", 'column': c, 'printed': printed, 'sum_of_rows': got, 'difference': printed - got, 'ok': 'yes' if abs(printed - got) <= len(members) else 'no'})
    for c in COLUMNS:
        got = sum(r[c] or 0 for r in rows)
        printed = grand[c] or 0
        out.append({'fiscal_year': grand['fiscal_year'], 'total': 'Total Voted Expense', 'column': c, 'printed': printed, 'sum_of_rows': got, 'difference': printed - got, 'ok': 'yes' if abs(printed - got) <= len(rows) else 'no'})
    # a vote total must exist for every vote with more than one accessing ministry
    for v, members in by_vote.items():
        if len(members) > 1 and v not in voted:
            out.append({'fiscal_year': grand['fiscal_year'], 'total': f'vote {v}', 'column': 'all', 'printed': '', 'sum_of_rows': '', 'difference': '', 'ok': 'no (no printed total)'})
    return out


def main():
    cache, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    years = sorted(m.group(1) for f in os.listdir(cache) if (m := re.match(r'pa-(\d{4}-\d{2})-crf-supplementary-schedules\.pdf$', f)))
    all_rows, all_totals, all_checks = [], [], []
    for year in years:
        pdf = os.path.join(cache, f'pa-{year}-crf-supplementary-schedules.pdf')
        url = f'{BASE}{year}/pa-{year}-crf-supplementary-schedules.pdf'
        try:
            rows, totals, grand = extract(pdf, year)
        except SystemExit as error:
            print(f'skipped {year}: {error}', file=sys.stderr)
            continue
        checks = check(rows, totals, grand)
        bad = [c for c in checks if not c['ok'].startswith('yes')]
        print(f'{year}: {len(rows)} rows, {len(totals)} vote totals, grand estimates {grand["estimates"]}, {len(bad)} failed checks', file=sys.stderr)
        for r in rows + totals + [grand]:
            r['source_url'] = url
        all_rows += rows
        all_totals += totals + [grand]
        all_checks += checks
    fields = ['fiscal_year', 'vote', 'description', 'ministry_as_printed', *COLUMNS, 'pdf_page', 'printed_page', 'source_url']
    with open(os.path.join(out_dir, 'votes.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fields, lineterminator='\n')
        w.writeheader()
        w.writerows(all_rows)
    with open(os.path.join(out_dir, 'vote-totals.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, [x for x in fields if x != 'ministry_as_printed'], lineterminator='\n')
        w.writeheader()
        w.writerows(all_totals)
    with open(os.path.join(out_dir, 'checks.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['fiscal_year', 'total', 'column', 'printed', 'sum_of_rows', 'difference', 'ok'], lineterminator='\n')
        w.writeheader()
        w.writerows(all_checks)


if __name__ == '__main__':
    main()
