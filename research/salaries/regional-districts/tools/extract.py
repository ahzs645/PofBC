"""Extract one schedule with two independent engines and compare.

Usage: python3 -I extract.py <config.json> <schedule-id> <out.json>
"""
import sys, re, json, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rdlib import *

FOOT = re.compile(r'\s*(\*+|†+)$')


def clean_name(n):
    m = FOOT.search(n)
    if m:
        return n[:m.start()].rstrip(), m.group(1)
    return n, None


def assign_cells_by_count(cells, cfg):
    n = len(cfg['columns'])
    if len(cells) == n:
        return dict(zip(cfg['columns'], cells))
    rule = cfg.get('missingRule', {}).get(str(len(cells)))
    if rule:
        return {c: (cells[i] if i is not None else None) for c, i in zip(cfg['columns'], rule)}
    raise ValueError(f'cell count {len(cells)} != {n}: {cells}')


def engine_a(cfg):
    rows, controls, orphans = [], [], []
    stop = re.compile(cfg['stopRegex'], re.I)
    skip = re.compile(cfg.get('skipRegex', r'^$'), re.I)
    header = re.compile(cfg['headerRegex'], re.I)
    for page in cfg['pages']:
        lines = layout_page(cfg.get('pdfLayout', cfg['pdf']), page)
        in_table = False
        page_rows = []
        for raw in lines:
            if header.search(raw):
                in_table = True
                continue
            if not in_table or not raw.strip():
                continue
            if cfg.get('endRegex') and re.search(cfg['endRegex'], raw, re.I):
                in_table = False
                continue
            if stop.search(raw):
                segs = layout_segments(raw)
                text, cells = split_amount_tail(segs)
                controls.append({'page': page, 'label': ' '.join(s[2] for s in text), 'cells': cells})
                if cfg.get('stopEndsTableOnPage', True):
                    in_table = False
                continue
            halves = [raw]
            if cfg.get('twoSided'):
                # right block starts at the first text segment following a numeric cell
                segs0 = layout_segments(raw)
                seen_num, cut = False, None
                for st, en, sx in segs0:
                    toks = [t for t in sx.split(' ') if t != '$']
                    if toks and all(is_amount_tok(t) for t in toks):
                        seen_num = True
                    elif sx != '$' and seen_num:
                        if is_amount_tok(sx.split(' ')[0]):
                            raise ValueError(f'ambiguous two-sided line {raw!r}')
                        cut = st
                        break
                halves = [raw[:cut], raw[cut:]] if cut else [raw]
            for side, part in enumerate(halves):
                if not part.strip():
                    continue
                segs = layout_segments(part)
                text, cells = split_amount_tail(segs)
                if text and cells and ',' in text[0][2]:
                    page_rows.append({'page': page, 'side': side, 'text': text, 'cells': cells, 'raw': part.rstrip()})
                elif skip.search(part.strip()):
                    continue
                else:
                    orphans.append({'page': page, 'line': part.rstrip()})
        # name/position split
        if cfg.get('hasPosition'):
            pos_cols = {}
            for sd in {r['side'] for r in page_rows}:
                starts = collections.Counter(r['text'][1][0] for r in page_rows if len(r['text']) >= 2 and r['side'] == sd)
                pos_cols[sd] = starts.most_common(1)[0][0] if starts else None
        page_rows.sort(key=lambda r: r['side'])
        for r in page_rows:
            t = r['text']
            area = None
            if cfg.get('textColumns'):
                if len(t) != 3:
                    raise ValueError(f'expected 3 text cells, got {t}')
                name, pos, area = t[0][2], t[1][2], t[2][2]
            elif cfg.get('hasPosition'):
                pos_col = pos_cols[r['side']]
                if len(t) == 2:
                    name, pos = t[0][2], t[1][2]
                elif len(t) == 1 and pos_col and t[0][0] < pos_col < t[0][1]:
                    s = t[0][2]; k = pos_col - t[0][0]
                    if s[k - 1] != ' ':
                        raise ValueError(f'cannot split {s!r}')
                    name, pos = s[:k].rstrip(), s[k:]
                    r['splitByColumn'] = True
                else:
                    name, pos = t[0][2], ' '.join(x[2] for x in t[1:])
                    r['multiSegmentPosition'] = len(t) > 2
            else:
                if len(t) != 1:
                    raise ValueError(f'unexpected text segments {t}')
                name, pos = t[0][2], None
            name, mark = clean_name(name)
            if pos is not None:
                pos, pmark = clean_name(pos)
                mark = (mark or '') + ('|pos:' + pmark if pmark else '') or None
            vals = assign_cells_by_count(r['cells'], cfg)
            rows.append({'page': page, 'name': name, 'footnoteMark': mark, 'position': pos, 'area': area, 'cells': vals,
                         'flags': {k: True for k in ('splitByColumn', 'multiSegmentPosition') if r.get(k)}})
    return rows, controls, orphans


def engine_b(cfg):
    rows, controls, orphans = [], [], []
    stop = re.compile(cfg['stopRegex'], re.I)
    skip = re.compile(cfg.get('skipRegex', r'^$'), re.I)
    header = re.compile(cfg['headerRegex'], re.I)
    ncol = len(cfg['columns'])
    cf = None
    if cfg.get('charFontPrefix'):
        pref = cfg['charFontPrefix']
        cf = lambda o: o.get('fontname', '') != pref
    for page in cfg['pages']:
        lines, width = plumber_lines(cfg['pdf'], page, char_filter=cf)
        in_table = False
        cand = []
        cut_x = None
        for ln in lines:
            txt = join_words(ln['words'])
            if header.search(txt):
                in_table = True
                if cfg.get('textColumns'):
                    cfg.setdefault('_hdrx', {})[page] = [next(w['x0'] for w in ln['words'] if w['text'] == h) for h in cfg['textColumnHeaders']]
                if cfg.get('twoSided'):
                    cut_x = 99999
                continue
            if not in_table:
                continue
            if cfg.get('endRegex') and re.search(cfg['endRegex'], txt, re.I):
                in_table = False
                continue
            if stop.search(txt):
                nums = [w['text'] for w in ln['words'] if is_amount_tok(w['text']) and w['text'] != '$']
                controls.append({'page': page, 'label': txt, 'cells': nums})
                if cfg.get('stopEndsTableOnPage', True):
                    in_table = False
                continue
            parts = [ln['words']]
            if cfg.get('twoSided'):
                seen_num, k = False, None
                for j, w in enumerate(ln['words']):
                    if w['text'] == '$':
                        continue
                    if is_amount_tok(w['text']):
                        seen_num = True
                    elif seen_num:
                        k = j
                        break
                if k is not None:
                    parts = [ln['words'][:k], ln['words'][k:]]
                    cut_x = ln['words'][k]['x0'] - 1 if cut_x is None or cut_x > 9000 else min(cut_x, ln['words'][k]['x0'] - 1)
            for ws in parts:
                if not ws:
                    continue
                # trailing numeric words
                i = len(ws)
                while i > 0 and (ws[i - 1]['text'] == '$' or is_amount_tok(ws[i - 1]['text'])):
                    # a bare number set at ordinary word spacing after a text word is part of the text (e.g. 'Operator 2')
                    if i - 2 >= 0 and not is_amount_tok(ws[i - 2]['text']) and ws[i - 2]['text'] != '$' \
                            and ws[i - 1]['x0'] - ws[i - 2]['x1'] < 6 and not STRONGAMT.match(ws[i - 1]['text']):
                        break
                    i -= 1
                textw, numw = ws[:i], [w for w in ws[i:] if w['text'] != '$']
                if textw and numw and ',' in join_words(textw):
                    cand.append({'text': textw, 'nums': numw})
                elif skip.search(join_words(ws)):
                    continue
                else:
                    orphans.append({'page': page, 'line': join_words(ws)})
        # column anchors from right edges of real numbers on this page (per side)
        def anchors_for(group):
            xs = [w['x1'] for c in group for w in c['nums'] if not DASH.match(w['text'])]
            a, _ = cluster(xs, cfg.get('clusterGap', 12))
            return a
        sides = [cand]
        if cfg.get('twoSided'):
            sides = [[c for c in cand if c['text'][0]['x0'] < cut_x], [c for c in cand if c['text'][0]['x0'] >= cut_x]]
        for group in sides:
            if not group:
                continue
            anchors = anchors_for(group)
            if len(anchors) != ncol:
                raise ValueError(f'page {page}: {len(anchors)} numeric column anchors, expected {ncol}: {anchors}')
            # position boundary: left edge of position column = most common x0 after the largest gap
            pos_x = None
            if cfg.get('textColumns'):
                pass
            elif cfg.get('hasPosition'):
                xs = []
                for c in group:
                    tw = c['text']
                    gaps = [(tw[j + 1]['x0'] - tw[j]['x1'], j) for j in range(len(tw) - 1)]
                    if gaps:
                        g, j = max(gaps)
                        if g > 8:
                            xs.append(round(tw[j + 1]['x0']))
                pos_x = collections.Counter(xs).most_common(1)[0][0]
            for c in group:
                tw = c['text']
                area = None
                if cfg.get('textColumns'):
                    hx = cfg['_hdrx'][page]
                    name = join_words([w for w in tw if w['x0'] < hx[1] - 1.5])
                    pos = join_words([w for w in tw if hx[1] - 1.5 <= w['x0'] < hx[2] - 1.5])
                    area = join_words([w for w in tw if w['x0'] >= hx[2] - 1.5])
                elif pos_x is not None:
                    name = join_words([w for w in tw if w['x0'] < pos_x - 1.5])
                    pos = join_words([w for w in tw if w['x0'] >= pos_x - 1.5]) or None
                else:
                    name, pos = join_words(tw), None
                name, mark = clean_name(name)
                if pos is not None:
                    pos, pmark = clean_name(pos)
                    mark = (mark or '') + ('|pos:' + pmark if pmark else '') or None
                vals = {col: None for col in cfg['columns']}
                filled = set()
                for w in c['nums']:
                    k = min(range(ncol), key=lambda j: abs(anchors[j] - w['x1']))
                    if k in filled:
                        raise ValueError(f'page {page}: two cells in one column for {name}')
                    filled.add(k)
                    vals[cfg['columns'][k]] = w['text']
                rows.append({'page': page, 'name': name, 'footnoteMark': mark, 'position': pos, 'area': area, 'cells': vals,
                             'top': round(tw[0]['top'], 1), 'x0': round(tw[0]['x0'], 1)})
    return rows, controls, orphans


def normalize(rows, cfg):
    out = []
    for r in rows:
        cells = {k: (to_amount(v) if v is not None else None) for k, v in r['cells'].items()}
        out.append({**r, 'values': cells, 'blankCells': [k for k, v in r['cells'].items() if v is None],
                    'dashCells': [k for k, v in r['cells'].items() if v is not None and DASH.match(v.replace('$', '').strip())]})
    return out


def main():
    conf = json.load(open(sys.argv[1]))
    sid = sys.argv[2]
    cfg = conf[sid]
    if cfg.get('twoSided'):
        cfg['_cut'] = {}
        for page in cfg['pages']:
            for raw in layout_page(cfg['pdf'], page):
                if re.search(cfg['headerRegex'], raw, re.I):
                    occ = [m.start() for m in re.finditer(re.escape(cfg['twoSidedHeaderWordA']), raw)]
                    cfg['_cut'][page] = occ[1] - 2
                    break
    a, ac, ao = engine_a(cfg)
    b, bc, bo = engine_b(cfg)
    a, b = normalize(a, cfg), normalize(b, cfg)
    if cfg.get('twoSided'):
        # compare as multisets ordered by page, then side order; reorder B to A's reading order (left col then right col)
        key = lambda r: (r['page'], r['name'])
        a_sorted, b_sorted = sorted(a, key=key), sorted(b, key=key)
    else:
        a_sorted, b_sorted = a, b
    diffs = []
    if len(a_sorted) != len(b_sorted):
        diffs.append(f'row count A={len(a_sorted)} B={len(b_sorted)}')
    for i, (x, y) in enumerate(zip(a_sorted, b_sorted)):
        for f in ('page', 'name', 'footnoteMark', 'position', 'area'):
            if x[f] != y[f]:
                diffs.append(f'row {i + 1} {f}: A={x[f]!r} B={y[f]!r}')
        for k in cfg['columns']:
            if x['values'][k] != y['values'][k] or (k in x['dashCells']) != (k in y['dashCells']):
                diffs.append(f'row {i + 1} {k}: A={x["cells"][k]!r} B={y["cells"][k]!r} ({x["name"]})')
    res = {'id': sid, 'rowsA': len(a), 'rowsB': len(b), 'diffs': diffs,
           'controlsA': ac, 'controlsB': bc, 'orphansA': ao, 'orphansB': bo,
           'rows': [{'page': r['page'], 'name': r['name'], 'footnoteMark': r['footnoteMark'], 'position': r['position'],
                     'area': r.get('area'), 'cells': r['cells'], 'flags': r.get('flags', {})} for r in a]}
    json.dump(res, open(sys.argv[3], 'w'), indent=1, ensure_ascii=False)
    print(f'{sid}: A={len(a)} B={len(b)} diffs={len(diffs)} orphansA={len(ao)} orphansB={len(bo)}')
    for d in diffs[:15]:
        print('  DIFF', d)
    for o in ao[:30]:
        print('  ORPHAN-A', o)
    for o in bo[:30]:
        print('  ORPHAN-B', o)
    for c in ac:
        print('  CTRL-A', c)
    for c in bc:
        print('  CTRL-B', c)
    flagged = [r for r in a if r.get('flags')]
    for r in flagged:
        print('  FLAG', r['page'], r['name'], r['position'], r['flags'])


if __name__ == '__main__':
    main()
