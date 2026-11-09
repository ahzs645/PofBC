"""Shared extraction helpers: two independent engines (poppler pdftotext -layout, pdfplumber words)."""
import re, subprocess, json, hashlib
from decimal import Decimal

AMT = re.compile(r'^\$?\s*(\(?-?[\d,]+(?:\.\d+)?\)?|-+|–|—)$')
NUMONLY = re.compile(r'^-?\d{1,3}(?:,\d{3})*(?:\.\d+)?$|^-?\d+(?:\.\d+)?$|^\(\d{1,3}(?:,\d{3})*(?:\.\d+)?\)$')
STRONGAMT = re.compile(r'^\$?\(?-?\d{1,3}(?:,\d{3})+(?:\.\d\d)?\)?$|^\$?\(?-?\d+\.\d\d\)?$')
DASH = re.compile(r'^(-+|–|—)$')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def to_amount(tok):
    """Literal cell -> Decimal or None for a dash. Never imputes."""
    t = tok.replace('$', '').strip()
    if DASH.match(t):
        return None
    neg = t.startswith('(') and t.endswith(')')
    t = t.strip('()').replace(',', '')
    v = Decimal(t)
    return -v if neg else v


def is_amount_tok(t):
    t = t.replace('$', '').strip()
    return bool(t) and (bool(NUMONLY.match(t)) or bool(DASH.match(t)))


# ---------------- Engine A: poppler pdftotext -layout ----------------
def layout_page(pdf, page):
    out = subprocess.run(['pdftotext', '-layout', '-f', str(page), '-l', str(page), pdf, '-'],
                         capture_output=True, text=True, check=True).stdout
    return out.split('\n')


def layout_segments(line):
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r'\S+(?: \S+)*', line)]


def split_amount_tail(segs):
    """Split segments into text segments and trailing amount cells. Segments like '$ 19,129' are amounts."""
    cells = []
    i = len(segs)
    while i > 0:
        s = segs[i - 1][2]
        if s == '$':
            i -= 1
            continue
        parts = s.split(' ')
        # a segment may contain several single-space separated amounts e.g. "$ 1,200" or "- 34"
        if all(is_amount_tok(p) or p == '$' for p in parts):
            toks = [p for p in parts if p != '$']
            cells = toks + cells
            i -= 1
            continue
        # trailing amount glued to text by one space: 'Something 1,234' -> split last token
        if STRONGAMT.match(parts[-1]) and len(parts) > 1 and not any(is_amount_tok(p) for p in parts[:-1]):
            # only accept if the text part is not itself part of a name (handled by caller review)
            cells = [parts[-1]] + cells
            segs = segs[:i - 1] + [(segs[i - 1][0], segs[i - 1][1], ' '.join(parts[:-1]))]
            break
        break
    return segs[:i], cells


# ---------------- Engine B: pdfplumber words ----------------
def plumber_lines(pdf_path, page, ytol=2.5, char_filter=None, x_tolerance=1.5):
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        p = pdf.pages[page - 1]
        if char_filter:
            p = p.filter(lambda o: o.get('object_type') != 'char' or char_filter(o))
        words = p.extract_words(x_tolerance=x_tolerance, y_tolerance=2, keep_blank_chars=False, use_text_flow=False)
        width = p.width
    words.sort(key=lambda w: (round(w['top'], 1), w['x0']))
    lines = []
    for w in words:
        mid = (w['top'] + w['bottom']) / 2
        for ln in lines:
            if abs(ln['mid'] - mid) <= ytol:
                ln['words'].append(w)
                break
        else:
            lines.append({'mid': mid, 'words': [w]})
    for ln in lines:
        ln['words'].sort(key=lambda w: w['x0'])
        merged = []
        for w in ln['words']:
            if merged and w['x0'] - merged[-1]['x1'] < 0.8:
                m = dict(merged[-1]); m['text'] += w['text']; m['x1'] = max(m['x1'], w['x1'])
                merged[-1] = m
            else:
                merged.append(w)
        ln['words'] = merged
    lines.sort(key=lambda l: l['mid'])
    return lines, width


def join_words(ws, gap_space=0.0):
    out = ''
    prev = None
    for w in ws:
        if prev is not None:
            out += ' '
        out += w['text']
        prev = w
    return out


def cluster(values, gap):
    vals = sorted(values)
    groups = []
    for v in vals:
        if groups and v - groups[-1][-1] <= gap:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [sum(g) / len(g) for g in groups], groups


def money(d):
    return float(d) if d is not None else None


def dsum(vals):
    return sum((v for v in vals if v is not None), Decimal('0'))
