"""Extract VSB SOFI employee schedule with two engines:
 A) poppler `pdftotext -layout -fixed 2` text (character columns ~ x/2pt), split by column positions;
 B) pdfplumber character/word geometry (x in points), split by column positions.
Both engines locate columns per page independently from their own output."""
import sys, re, json, subprocess, collections
from decimal import Decimal
import pdfplumber

AMT_RE = re.compile(r'^\(?-?[\d,]+(?:\.\d{2})?\)?$')
HEAD_RE = re.compile(r'Employees with Remuneration Excee', re.I)
CAMEL = re.compile(r'(?<=[a-z])(?=[A-Z])')

def mode(xs):
    return collections.Counter(xs).most_common(1)[0][0] if xs else None

def is_total_line(text):
    t = text.strip()
    if re.match(r'(?i)^total', t): return True
    toks = t.replace('$', ' ').split()
    return len(toks) == 2 and all(AMT_RE.match(x) for x in toks)

def skip_line(text):
    t = text.strip()
    return (not t or re.fullmatch(r'\d{1,3}', t) or 'Last Name' in t or 'Schedule of Remuneration' in t
            or ('Remuneration' in t and 'Expenses' in t))

def peel(tokens, rem_end, tol):
    """tokens: list of dicts(start,end,text). Return (text_tokens, amount_tokens)."""
    toks = list(tokens); amts = []
    while toks and (toks[-1]['text'] in ('-', '$') or (AMT_RE.match(toks[-1]['text']) and (rem_end is None or toks[-1]['end'] >= rem_end - tol))):
        amts.insert(0, toks.pop())
        if len([a for a in amts if a['text'] != '$']) == 2 and toks and toks[-1]['text'] != '$': break
    return toks, [a for a in amts if a['text'] != '$']

def rem_end_guess(lines):
    ends = []
    for toks in lines:
        if len(toks) >= 3 and (AMT_RE.match(toks[-1]['text']) or toks[-1]['text'] == '-') and AMT_RE.match(toks[-2]['text']):
            ends.append(toks[-2]['end'])
    return mode(ends)

def columns(textrows):
    """textrows: list of token lists (text part). G=modal start of 2nd token, P=modal start of 3rd token where 2nd at G."""
    G = mode([round(t[1]['start']) for t in textrows if len(t) >= 3])
    P = mode([round(t[2]['start']) for t in textrows if len(t) >= 3 and abs(round(t[1]['start']) - G) <= 0])
    return G, P

def assign(toks, G, P, tol, splitter):
    cells = [[], [], []]; notes = []
    for t in toks:
        if t['start'] >= P - tol: cells[2].append(t['text'])
        elif t['start'] >= G - tol:
            if t['end'] > P + tol:  # straddles into position column
                a, b = splitter(t, P); notes.append(('given|position', t['text'], a, b)); cells[1].append(a); cells[2].append(b)
            else: cells[1].append(t['text'])
        else:
            if t['end'] > G + tol:  # straddles surname|given
                a, b = splitter(t, G); notes.append(('surname|given', t['text'], a, b)); cells[0].append(a); cells[1].append(b)
            else: cells[0].append(t['text'])
    return [' '.join(c) for c in cells], notes

def literal(a):
    return a['text']

def run_engine(pages_tokens, tol, splitter, fallback=None):
    """pages_tokens: list of (pageno, [ (linekey, [tokens]) ]). Shared state machine; geometry from engine."""
    started = done = False; rows = []; anomalies = []; tail = []
    for pi, lines in pages_tokens:
        if done:
            tail += [' '.join(t['text'] for t in toks) for _, toks in lines]; continue
        body = []
        for key, toks in lines:
            text = ' '.join(t['text'] for t in toks)
            if done: tail.append(text); continue
            if not started:
                if HEAD_RE.search(text): started = True
                continue
            if is_total_line(text): done = True; tail.append(text); continue
            if skip_line(text): continue
            body.append((key, toks, text))
        if not body: continue
        re_end = rem_end_guess([b[1] for b in body])
        peeled = [(key, *peel(toks, re_end, 4 * tol), text) for key, toks, text in body]
        exp_end = mode([a[1]['end'] for _, _, a, _ in peeled if len(a) == 2])
        G, P = columns([t for _, t, a, _ in peeled if a])
        for key, toks, amts, text in peeled:
            if not amts or not toks:
                anomalies.append({'page': pi, 'line': text, 'why': 'no amounts or no text'}); continue
            (sur, giv, pos), notes = assign(toks, G, P, tol, splitter)
            if not giv and fallback:
                sur, giv, note = fallback([t['text'] for t in toks if t['start'] < G - tol]); notes.append(note)
            if len(amts) == 2: r, e = amts[0]['text'], amts[1]['text']
            elif abs(amts[0]['end'] - re_end) <= abs(amts[0]['end'] - exp_end): r, e = amts[0]['text'], None
            else: r, e = None, amts[0]['text']
            if r is None or r == '-' or not sur or not giv:
                anomalies.append({'page': pi, 'line': text, 'why': 'unresolved cells'}); continue
            rows.append({'page': pi, 'surname': sur, 'given': giv, 'position': pos or None, 'rem': r, 'exp': e, 'key': key, 'boundaryNotes': notes})
    return rows, anomalies, tail

def layout_engine(pdf):
    txt = subprocess.run(['pdftotext', '-layout', '-fixed', '2', pdf, '-'], capture_output=True, text=True).stdout
    out = []
    for pi, p in enumerate(txt.split('\f'), 1):
        lines = []
        for li, ln in enumerate(p.splitlines()):
            toks = [{'start': m.start(), 'end': m.end(), 'text': m.group()} for m in re.finditer(r'\S+', ln)]
            if toks: lines.append((li, toks))
        out.append((pi, lines))
    def splitter(t, boundary):
        # layout text has no intra-word positions: split at a lowercase->uppercase transition, only if unique
        cuts = [m.start() for m in CAMEL.finditer(t['text'])]
        if len(cuts) != 1: raise ValueError('ambiguous glued token ' + t['text'])
        return t['text'][:cuts[0]], t['text'][cuts[0]:]
    def fallback(surtoks):
        # overflowing surname pushed the given name left of its column in the character grid
        last = surtoks[-1]; cuts = [m.start() for m in CAMEL.finditer(last)]
        if len(cuts) == 1:
            return ' '.join(surtoks[:-1] + [last[:cuts[0]]]), last[cuts[0]:], ('overflow-camel', last)
        if len(surtoks) >= 2 and not cuts:
            return ' '.join(surtoks[:-1]), last, ('overflow-last-token', ' '.join(surtoks))
        return ' '.join(surtoks), '', ('overflow-unresolved', ' '.join(surtoks))
    return run_engine(out, 1, splitter, fallback)

def plumber_engine(pdf):
    out = []
    with pdfplumber.open(pdf) as doc:
        for pi, page in enumerate(doc.pages, 1):
            words = page.extract_words(x_tolerance=1.5, y_tolerance=2, keep_blank_chars=False, return_chars=True)
            words.sort(key=lambda w: (w['top'], w['x0']))
            lines = []
            for w in words:
                if lines and abs(lines[-1][0] - w['top']) <= 2.5: lines[-1][1].append(w)
                else: lines.append([w['top'], [w]])
            pl = []
            for top, ws in lines:
                ws.sort(key=lambda w: w['x0'])
                pl.append((round(top, 3), [{'start': w['x0'], 'end': w['x1'], 'text': w['text'], 'chars': w['chars']} for w in ws]))
            out.append((pi, pl))
    def splitter(t, boundary):
        a = ''.join(c['text'] for c in t['chars'] if c['x0'] < boundary - 1.5)
        b = ''.join(c['text'] for c in t['chars'] if c['x0'] >= boundary - 1.5)
        return a, b
    return run_engine(out, 3, splitter)

if __name__ == '__main__':
    pdf, out = sys.argv[1], sys.argv[2]
    res = {}
    for name, fn in [('layout', layout_engine), ('plumber', plumber_engine)]:
        try:
            rows, an, tail = fn(pdf)
        except Exception as ex:
            rows, an, tail = [], [{'why': 'engine error: ' + repr(ex)}], []
        for r in rows:
            r.pop('chars', None)
        res[name] = rows; res[name + 'Anomalies'] = an; res[name + 'Tail'] = tail[:12]
    json.dump(res, open(out, 'w'), indent=0, default=str)
    print(pdf, 'layout', len(res['layout']), len(res['layoutAnomalies']), 'plumber', len(res['plumber']), len(res['plumberAnomalies']))
