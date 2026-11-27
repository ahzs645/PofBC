"""Extract the Public Accounts table "Adjusted Net Income of Crown Corporations, Agencies and the
SUCH Sector" (before 2004-05: "... of Crown Corporations and Agencies") from each year's
Supplementary Information PDF, as published.

Usage (from the repository root; needs poppler's pdftotext):

    python3 -I research/finance/public-accounts-23-1/scripts/extract_adjusted_net_income.py \
        research/finance/public-accounts-23-1/cache  research/finance/public-accounts-23-1

It reads `pa-<yyyy-yy>-supplementary-information.pdf` files from the cache directory (fetched from
https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/<yyyy-yy>/pa-<yyyy-yy>-supplementary-information.pdf)
and writes:

  adjusted-net-income.csv          one row per table row and year, figures in $ millions as printed
  adjusted-net-income-columns.csv  each year's column headings, as printed
  adjusted-net-income-checks.csv   each printed subtotal against the sum of the rows above it
  adjusted-net-income-footnotes.csv  the table's footnotes, by year and number; a row's `footnotes`
                                   gives the numbers on its name, and `cN:M` for footnote M on column N

How it reads a page: words come from `pdftotext -bbox` with their positions. The row of "$" signs
under the headings gives the six figure columns; a figure belongs to the last column whose "$"
starts left of the figure's right edge (figures are right-aligned under their "$"). Landscape pages
whose text runs vertically are turned first. A blank cell stays blank: it is not read as zero.
Brackets are negative. A superscript footnote number on a name is kept apart from the name.
"""

import csv
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

BASE = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/'
NUMBER = re.compile(r'^\(?-?\d[\d,]*\)?$')
DASH = {'—', '–', '-'}
SECTION = re.compile(r'^(?:—\s*)?(?:Taxpayer[–-]supported \(|Self[–-]supported \(|SUCH Sector$|Continued$|Government Business Enterprises|Commercial Crown)|—\s*Continued$', re.I)
TOTAL = re.compile(r'^(?:sub[–-]?\s*total|total\b|net impact\b|taxpayer[–-]supported crown corporations and agencies$|self[–-]supported crown corporations and agencies$|such sector$)', re.I)


def words_of(pdf, page):
    out = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-bbox', pdf, '-'], capture_output=True, text=True).stdout
    out = re.sub(r'<!DOCTYPE[^>]*>', '', out).replace('xmlns="http://www.w3.org/1999/xhtml"', '')
    root = ET.fromstring(out)
    words = []
    for w in root.iter('word'):
        x0, y0, x1, y1 = (float(w.get(k)) for k in ('xMin', 'yMin', 'xMax', 'yMax'))
        words.append({'t': (w.text or '').strip(), 'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1})
    return [w for w in words if w['t']]


def orient(words):
    """Turn a page whose text runs vertically so that rows run down and columns run right."""
    rev = next((w for w in words if w['t'] == 'Revenue'), None)
    if rev and (rev['y1'] - rev['y0']) > (rev['x1'] - rev['x0']):
        # Reading order runs towards smaller y, and lines advance with x.
        return [{'t': w['t'], 'row': w['x0'], 'c0': -w['y1'], 'c1': -w['y0'], 'h': w['x1'] - w['x0']} for w in words]
    return [{'t': w['t'], 'row': w['y0'], 'c0': w['x0'], 'c1': w['x1'], 'h': w['y1'] - w['y0']} for w in words]


def lines_of(words, tolerance=2.5):
    lines = []
    for w in sorted(words, key=lambda w: (w['row'], w['c0'])):
        if lines and abs(lines[-1]['row'] - w['row']) <= tolerance:
            lines[-1]['words'].append(w)
        else:
            lines.append({'row': w['row'], 'words': [w]})
    for line in lines:
        # Dot leaders are dropped, and remembered: a name with a leader is a row even if it is blank.
        line['dotted'] = any('...' in w['t'] for w in line['words'])
        kept = []
        for w in line['words']:
            text = re.sub(r'\.{3,}.*$', '', w['t']) if not re.fullmatch(r'\.{3,}', w['t']) else ''
            if text:
                kept.append({**w, 't': text})
        line['words'] = sorted(kept, key=lambda w: w['c0'])
        # Some years set names with discretionary hyphens, so "Pavilion" arrives as "Pa", "vil", "ion"
        # with no gap between them: those pieces are one word.
        merged = []
        for w in line['words']:
            # A superscript footnote number set tight against a figure is not part of it.
            similar = abs(w['h'] - merged[-1]['h']) <= 0.15 * max(w['h'], merged[-1]['h']) if merged else False
            if merged and similar and w['c0'] - merged[-1]['c1'] < 0.5:
                last = merged[-1]
                merged[-1] = {**last, 't': last['t'] + w['t'], 'c1': w['c1'], 'h': max(last['h'], w['h'])}
            else:
                merged.append(dict(w))
        line['words'] = merged
    return lines


def value_of(text):
    if text in DASH:
        return 0
    negative = text.startswith('(') or text.startswith('-')
    digits = re.sub(r'[^\d]', '', text)
    return -int(digits) if negative else int(digits)


def clean_label(words, label_height):
    """The row's name, and any footnote marker printed after it."""
    marks = []
    kept = []
    for i, w in enumerate(words):
        t = w['t']
        if re.fullmatch(r'\.{2,}', t):
            continue
        last = i == len(words) - 1
        if last and re.fullmatch(r'\d{1,2}\.?', t) and w['h'] < label_height * 0.85:
            marks.append(t.rstrip('.'))
            continue
        kept.append(t)
    text = ' '.join(kept)
    text = re.sub(r'\s*\.{2,}.*$', '', text)            # dot leaders
    m = re.search(r'(?<=[A-Za-z\)’\'])(\d{1,2})\.?$', text)  # a marker glued to the last word
    if m and not re.search(r'\d{3,}', text.split()[-1]):
        marks.append(m.group(1))
        text = text[:m.start()]
    text = text.rstrip(' .')
    m = re.search(r' (\d{1,2})$', text)                    # a marker set apart by a space
    if m:
        marks.append(m.group(1))
        text = text[:m.start()]
    text = re.sub(r'^[–—-]\s*Continued\s+', '', text)        # a "—Continued" heading run into the name
    return re.sub(r'\s+', ' ', text).strip(), marks


def join_wrapped(parts):
    """A name printed over two lines, with a word broken at a hyphen joined again."""
    text = ' '.join(part for part in parts if part).strip()
    text = re.sub(r'^[–—-]\s*Continued\s+', '', text)
    return re.sub(r'(?<=[a-z])- (?=[a-z])', '', text)


def read_page(pdf, page):
    words = orient(words_of(pdf, page))
    lines = lines_of(words)
    dollar_line = next((l for l in lines if sum(1 for w in l['words'] if w['t'] == '$') >= 5), None)
    if not dollar_line:
        return None
    anchors = [w for w in dollar_line['words'] if w['t'] == '$']
    first = anchors[0]['c0']
    # Headings: the lines between the "In Millions" line (or the title) and the "$" line.
    head_lines = [l for l in lines if dollar_line['row'] - 60 < l['row'] < dollar_line['row']
                  and not any(re.fullmatch(r'In|Mil|Millions|lions', w['t']) for w in l['words'])]
    labels = [[] for _ in anchors]
    for l in head_lines:
        for w in l['words']:
            if w['c1'] < first - 30 or re.fullmatch(r'\d+', w['t']):
                continue
            mid = (w['c0'] + w['c1']) / 2
            at = min(range(len(anchors)), key=lambda i: abs((anchors[i]['c0'] + anchors[i]['c1']) / 2 - mid))
            labels[at].append(w['t'])
    columns = [re.sub(r'\d+$', '', ' '.join(parts)).strip() for parts in labels]
    section_title = ' '.join(w['t'] for w in dollar_line['words'] if w['c1'] < first - 30)
    title_line = next((l for l in lines if any(w['t'] == 'Adjusted' for w in l['words']) and l['row'] < dollar_line['row'] - 10 and l['words'][0]['c0'] < first - 100), None)
    title = ' '.join(w['t'] for w in title_line['words']) if title_line else ''
    body = [l for l in lines if l['row'] > dollar_line['row'] + 1]
    label_heights = [w['h'] for l in body for w in l['words'] if w['c1'] < first - 30 and re.search('[A-Za-z]', w['t'])]
    label_height = sorted(label_heights)[len(label_heights) // 2] if label_heights else 10
    rows = []
    section = section_title
    pending = []
    printed = None
    notes = []
    unread = []
    for index, l in enumerate(body):
        if re.search(r'PROVINCE OF BRITISH COLUMBIA|PUBLIC ACCOUNTS', ' '.join(w['t'] for w in l['words'])):
            continue
        # Beyond the last column there is only the folio, or a running head set in the margin.
        margin = [w for w in l['words'] if w['c0'] > anchors[-1]['c1'] + 40]
        if len(margin) == 1 and re.fullmatch(r'\d{1,3}', margin[0]['t']) and len(l['words']) == 1:
            printed = margin[0]['t']
            continue
        inside = [w for w in l['words'] if w not in margin]
        label_words = [w for w in inside if w['c1'] < first - 20]
        figure_words = [w for w in inside if w['c1'] >= first - 20]
        # A footnote number set against a bracketed figure, "(162)5", is the figure and its footnote.
        split = []
        for w in figure_words:
            m = re.fullmatch(r'(\(\d[\d,]*\))(\d{1,2})', w['t'])
            if m:
                cut = w['c0'] + (w['c1'] - w['c0']) * len(m.group(1)) / len(w['t'])
                split += [{**w, 't': m.group(1), 'c1': cut}, {**w, 't': m.group(2), 'c0': cut, 'h': 0}]
            else:
                split.append(w)
        figure_words = split
        small = [w for w in figure_words if w['h'] < label_height * 0.85 and re.fullmatch(r'\d{1,2}', w['t'])]
        figures = [w for w in figure_words if (NUMBER.match(w['t']) or w['t'] in DASH) and w not in small]
        text = ' '.join(w['t'] for w in label_words)
        dotted = l['dotted']
        # A footnote line ends the table; a lone number away from the columns is the folio.
        prose = sum(1 for w in figure_words if re.search(r'[A-Za-z]{2,}', w['t'])) >= 3
        if label_words and (re.match(r'^\d{1,2} ?[A-Z][a-z]', text) or prose):
            mark = None
            for rest in body[index - 1 if index and re.fullmatch(r'\d{1,2}', ' '.join(w['t'] for w in body[index - 1]['words'])) else index:]:
                line_text = ' '.join(w['t'] for w in rest['words'])
                m = re.match(r'^(\d{1,2}) ?([A-Z][a-z].*)$', line_text)
                if re.fullmatch(r'\d{1,2}', line_text) and rest['words'][0]['h'] < label_height * 0.85:
                    mark = line_text            # a superscript set on a line of its own
                elif m:
                    notes.append({'mark': m.group(1), 'text': m.group(2)})
                elif mark and line_text:
                    notes.append({'mark': mark, 'text': line_text})
                    mark = None
                elif notes and line_text and not re.fullmatch(r'\d{1,3}', line_text):
                    notes[-1]['text'] += ' ' + line_text
                elif re.fullmatch(r'\d{1,3}', line_text):
                    printed = line_text
            break
        unread.extend(f'{page}: {w["t"]}' for w in figure_words if w not in small and w not in figures)
        if not label_words and len(figure_words) == 1 and re.fullmatch(r'\d{1,3}', figure_words[0]['t']) and figure_words[0]['c0'] > anchors[-1]['c1']:
            printed = figure_words[0]['t']
            continue
        if not inside:
            continue
        if not label_words and not figures:
            continue
        if not figures:
            name, _ = clean_label(label_words, label_height)
            if not name:
                continue
            if SECTION.search(name) and not dotted:
                section = join_wrapped([name]) if not re.search(r'Continued$', name) else section
                pending = []
                continue
            # A row whose cells are all blank has its dot leader; a wrapped name does not.
            nxt = body[index + 1] if index + 1 < len(body) else None
            next_is_dots = nxt is not None and nxt['dotted'] and not nxt['words']
            if dotted or next_is_dots:
                full = join_wrapped(pending + [name])
                rows.append({'section': section, 'name': full, 'marks': clean_label(label_words, label_height)[1], 'cells': [None] * len(anchors)})
                pending = []
            else:
                pending.append(name)
            continue
        cells = [None] * len(anchors)
        for w in figures:
            at = max([i for i, a in enumerate(anchors) if a['c0'] < w['c1']] or [0])
            if cells[at] is not None:
                raise ValueError(f'{pdf} p{page}: two figures in one cell on line "{text}"')
            cells[at] = value_of(w['t'])
        name, marks = clean_label(label_words, label_height)
        for w in small:
            at = max([i for i, a in enumerate(anchors) if a['c0'] < w['c0']] or [0])
            marks.append(f'c{at + 1}:{w["t"]}')
        if not name and not pending and rows and all(c is None for c in rows[-1]['cells']):
            # Figures printed on the line after their name (older layouts that wrap).
            rows[-1]['cells'] = cells
            continue
        full = join_wrapped(pending + [name])
        pending = []
        rows.append({'section': section, 'name': full, 'marks': marks, 'cells': cells})
    if unread:
        raise ValueError(f'{pdf}: words in the figure columns that are not figures: {unread}')
    return {'columns': columns, 'title': title, 'rows': rows, 'printed': printed, 'notes': notes}


def heading_key(text):
    """A heading's words, for comparing one page's headings with another's."""
    return re.sub(r'[^a-z]', '', re.sub(r'\bthe\b', '', text.lower()))


def find_pages(pdf):
    count = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    pages = []
    for page in range(1, count + 1):
        text = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-layout', pdf, '-'], capture_output=True, text=True).stdout
        if re.search(r'Adjusted Net Income of Crown Corporations', text) and re.search(r'Revenue', text):
            pages.append(page)
    return pages


def main(cache, out_dir):
    files = sorted(name for name in os.listdir(cache) if re.search(r'pa-\d{4}-\d{2}-supplementary-information\.pdf$', name))
    rows_out, columns_out, checks_out, notes_out = [], [], [], []
    for name in files:
        year = re.search(r'pa-(\d{4}-\d{2})-supp', name).group(1)
        fy_end = f'{int(year[:4]) + 1}-03-31'
        url = f'{BASE}{year}/pa-{year}-supplementary-information.pdf'
        pdf = os.path.join(cache, name)
        order = 0
        seen_columns = None
        for page in find_pages(pdf):
            table = read_page(pdf, page)
            if not table:
                continue
            if seen_columns is None:
                seen_columns = table['columns']
                for position, label in enumerate(table['columns']):
                    columns_out.append({'fiscal_year': year, 'position': position + 1, 'heading_as_printed': label, 'source_url': url, 'pdf_page': page})
            elif [heading_key(c) for c in table['columns']] != [heading_key(c) for c in seen_columns]:
                raise ValueError(f'{year} p{page}: columns differ from the first page: {table["columns"]} vs {seen_columns}')
            for note in table['notes']:
                notes_out.append({'fiscal_year': year, 'mark': note['mark'], 'text': note['text'], 'source_url': url, 'pdf_page': page})
            for row in table['rows']:
                order += 1
                rows_out.append({
                    'fiscal_year': year, 'fy_end': fy_end, 'row': order, 'section_as_printed': row['section'],
                    'name_as_printed': row['name'], 'footnotes': ' '.join(row['marks']),
                    'is_subtotal': 'yes' if TOTAL.match(row['name']) else '',
                    **{f'c{i + 1}': '' if v is None else v for i, v in enumerate(row['cells'])},
                    'unit': '$ millions', 'source_url': url, 'pdf_page': page, 'printed_page': table['printed'] or '',
                    'table_title': table['title']
                })
        # Each subtotal against the rows since the previous subtotal (or the section's start).
        # A "Net impact" line is checked against the subtotals since the last one, or, where there are
        # none, against every row since it.
        year_rows = [r for r in rows_out if r['fiscal_year'] == year]
        start = 0
        impact_start = 0
        for i, r in enumerate(year_rows):
            if r['is_subtotal'] != 'yes':
                continue
            if re.match(r'^net impact', r['name_as_printed'], re.I):
                block = year_rows[impact_start:i]
                subtotals = [p for p in block if p['is_subtotal'] == 'yes']
                parts = subtotals if subtotals else block
                impact_start = start = i + 1
            else:
                parts = [p for p in year_rows[start:i] if p['is_subtotal'] != 'yes']
                start = i + 1
            if not parts:
                continue
            for c in range(1, 7):
                printed = r[f'c{c}']
                total = sum(int(p[f'c{c}']) for p in parts if p[f'c{c}'] != '')
                if printed == '' and total == 0:
                    continue
                gap = (int(printed) if printed != '' else 0) - total
                checks_out.append({'fiscal_year': year, 'subtotal_row': r['row'], 'subtotal_as_printed': r['name_as_printed'], 'column': c,
                                   'printed': printed, 'sum_of_rows': total, 'rows_summed': len(parts), 'difference': gap,
                                   'within_rounding': 'yes' if abs(gap) <= max(2, len(parts) // 2) else 'no'})
    write(os.path.join(out_dir, 'adjusted-net-income.csv'), rows_out)
    write(os.path.join(out_dir, 'adjusted-net-income-columns.csv'), columns_out)
    write(os.path.join(out_dir, 'adjusted-net-income-checks.csv'), checks_out)
    write(os.path.join(out_dir, 'adjusted-net-income-footnotes.csv'), notes_out)
    years = sorted({r['fiscal_year'] for r in rows_out})
    print(f'{len(rows_out)} rows, {len(years)} years ({years[0]} to {years[-1]}); '
          f'{sum(1 for c in checks_out if c["within_rounding"] == "no")} of {len(checks_out)} subtotal checks outside rounding')


def write(path, rows):
    with open(path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
