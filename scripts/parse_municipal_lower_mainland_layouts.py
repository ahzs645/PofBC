#!/usr/bin/env python3
"""Pinned-layout readers for official Lower Mainland municipal SOFI schedules.

These readers expose source components, physical PDF pages and exact text keys.
They never search arbitrary PDF monetary tables: only reviewed employee schedules
are eligible. The companion importer checks original hashes, fixed expected rows,
all component sums, source controls, independent PDF readers and table completeness.

Requires Poppler pdftotext, PyMuPDF and pypdf. No OCR or guessed names/titles.
"""
import re, json, sys, fitz
from pathlib import Path
from decimal import Decimal
from collections import Counter
AMT = '(?:\\(?-?\\d[\\d,]*(?:\\.\\d{2})?\\)?|[-‐–—])'

def split_amounts(line, n):
    line = line.replace('$', ' ')
    tokens = [(m[0], m.start(), m.end()) for m in re.finditer('\\S+', line) if m[0] != '$']
    if len(tokens) <= n or any((not re.fullmatch(AMT, t[0]) for t in tokens[-n:])):
        return None
    first = tokens[-n][1]
    prefix = line[:first].rstrip(' $')
    selected = tokens[-n:]
    if re.search('\\d[\\d,]{3,}(?:\\.\\d{2})?$', prefix) and len(tokens) > n + 1:
        candidate = tokens[-n - 1:]
        for i in range(len(candidate) - 2, -1, -1):
            if candidate[i][0] in ('-', '‐', '–', '—') and re.fullmatch('\\d[\\d,]*(?:\\.\\d{2})?', candidate[i + 1][0]):
                candidate[i:i + 2] = [('-' + candidate[i + 1][0], candidate[i][1], candidate[i + 1][2])]
                break
        if len(candidate) == n:
            selected = candidate
            first = selected[0][1]
            prefix = line[:first].rstrip(' $')
    if not prefix or not re.search('\\s{2,}', line[len(prefix):first]):
        return None
    return (prefix.strip(), [t[0] for t in selected])

def money(x):
    if x in ('-', '‐', '–', '—'):
        return None
    return Decimal(x.replace(',', '').replace('(', '-').replace(')', ''))

def key(s):
    return re.sub('[\\s$]', '', s).translate(str.maketrans('‐‑–—', '----'))

def fitz_rows(p):
    gs = []
    for w in sorted(p.get_text('words'), key=lambda w: (w[3], w[0])):
        g = next((g for g in gs[-3:] if abs(g[0] - w[3]) < 2.1), None)
        if g is None:
            g = [w[3], []]
            gs.append(g)
        g[1].append(w)
    return Counter((key(' '.join((w[4] for w in sorted(g[1], key=lambda w: w[0])))) for g in gs))

def parse_base(path):
    slug, year = path.stem.rsplit('-', 1)
    text = path.read_text()
    pages = text.split('\x0c')
    n = 4 if slug == 'west-vancouver' else 2 if slug == 'delta' else 3
    select = []
    for i, t in enumerate(pages):
        if slug == 'burnaby':
            yes = 'Last Name' in t and 'First Name' in t
        elif slug == 'surrey':
            yes = 'CITY EMPLOYEES' in t and 'REMUNERATION' in t
        elif slug == 'coquitlam':
            yes = 'First Initial' in t and 'Last Name' in t
        elif slug == 'north-vancouver-city':
            yes = 'Job Description' in t
        elif slug == 'new-westminster':
            yes = 'Employee Name' in t or 'EMPLOYEE NAME' in t
        elif slug == 'west-vancouver':
            yes = 'Employee Names' in t or 'Employee Name' in t
        elif slug == 'delta':
            yes = 'Name' in t and 'Remuneration ($)' in t and ('Expenses ($)' in t)
        else:
            return
        if yes:
            select.append(i)
    if not select:
        return {'key': path.stem, 'status': 'no-layout'}
    rows = []
    controls = None
    errors = []
    checks = []
    done = False
    doc = fitz.open(path.with_suffix('.pdf'))
    for at in select:
        if done:
            break
        alt = fitz_rows(doc[at])
        active = slug != 'west-vancouver'
        start = False
        for line in pages[at].splitlines():
            if slug == 'west-vancouver' and re.search('(Other )?Employee Names?', line):
                active = True
            if not active:
                continue
            pref = line.strip()
            if re.match('Total|Grand Total|Subtotal Employees >|Remuneration and expenses \\(over|with Remuneration exceeding', pref, re.I):
                sp = split_amounts(line, n)
                if not sp and slug == 'west-vancouver':
                    sp = split_amounts(line, 2)
                if sp and rows:
                    controls = sp[1]
                    done = True
                    break
            sp = split_amounts(line, n)
            if not sp:
                sp = split_amounts(line, n - 1)
                if sp and re.search('\\d[\\d,]+(?:\\.\\d+)?\\s*$', sp[0]):
                    sp = None
            if not sp:
                continue
            prefix, amts = sp
            actual_amts = amts[:]
            amts += ['-'] * (n - len(amts))
            if not re.search('[A-Za-z]', prefix) or re.match('(?:Total|Subtotal|Remuneration|NUMBER|with |Consolidated|Base |Employee|\\d+\\s+[><=])', prefix, re.I):
                continue
            if sum((money(a) or Decimal(0) for a in amts[:2])) < 1000:
                continue
            parts = re.split('\\s{2,}', prefix)
            if slug in ('burnaby', 'coquitlam') or (slug == 'north-vancouver-city' and year < '2025'):
                if len(parts) < 2:
                    errors.append(['name-split', at + 1, prefix])
                    continue
                name = parts[0] + ', ' + parts[1]
                position = ' '.join(parts[2:]) or None
            elif slug == 'north-vancouver-city':
                if len(parts) != 2:
                    errors.append(['position-split', at + 1, prefix])
                    continue
                name, position = parts
            else:
                name = prefix
                position = None
            rowkey = key(prefix + ' ' + ' '.join(actual_amts))
            if alt[rowkey]:
                alt[rowkey] -= 1
            else:
                errors.append(['reader-disagreement', at + 1, prefix, amts])
            rows.append({'name': name, 'position': position, 'raw': amts, 'page': at + 1, 'sourceKey': rowkey, 'sourcePrefix': prefix})
    if not controls:
        errors.append(['missing-subtotal'])
    sums = [sum((money(r['raw'][j]) or Decimal(0) for r in rows), Decimal(0)) for j in range(n)]
    if controls:
        if n == 4 and len(controls) == 2:
            vals = sums[2:]
        else:
            vals = sums
        deltas = [float(v - (money(c) or Decimal(0))) for v, c in zip(vals, controls)]
        if any((abs(d) > max(1, len(rows) / 2) for d in deltas)):
            errors.append(['subtotal-mismatch', deltas])
    else:
        deltas = []
    return {'key': path.stem, 'pages': [i + 1 for i in select if i + 1 <= max([r['page'] for r in rows], default=0)], 'n': len(rows), 'controls': controls, 'sums': list(map(str, sums)), 'deltas': deltas, 'errorCount': len(errors), 'errors': errors[:7], 'rows': rows}
import re, json, sys, fitz
from pathlib import Path
from decimal import Decimal
from collections import Counter
SLUGS = ['north-vancouver-district', 'port-coquitlam', 'port-moody', 'pemberton', 'white-rock', 'maple-ridge', 'whistler', 'squamish']

def solo(line, n):
    s = line.replace('$', '').strip().split()
    return s if len(s) == n and all((re.fullmatch('(?:\\(?-?\\d[\\d,]*(?:\\.\\d{2})?\\)?|[-‐–—])', x) for x in s)) else None

def parse_extended(path):
    slug, ys = path.stem.rsplit('-', 1)
    year = int(ys)
    if slug not in SLUGS:
        return parse_base(path)
    pages = path.read_text().split('\x0c')
    n = 3
    if slug in ['north-vancouver-district', 'port-coquitlam']:
        n = 4
    if slug in ['pemberton', 'whistler', 'squamish']:
        n = 2
    if slug == 'white-rock' and year <= 2023:
        n = 2
    if slug == 'maple-ridge' and year <= 2019:
        n = 2
    start = None
    end = None
    selected = []
    for at, p in enumerate(pages):
        if slug == 'north-vancouver-district':
            yes = 'Schedule of remuneration and expenses - Employees' in p or 'Schedule of Remuneration and Expenses - Employees' in p
        elif slug == 'port-coquitlam':
            yes = 'SCHEDULE OF EMPLOYEE REMUNERATION AND EXPENSES' in p and 'Position' in p and ('Name' in p)
        elif slug == 'port-moody':
            yes = bool(re.search('Staff \\(Greater than \\$75,000\\)', p, re.I))
        elif slug == 'pemberton':
            yes = bool(re.search('Other Employees\\s*>\\s*75,000', p, re.I))
        elif slug == 'white-rock':
            yes = bool(re.search('2\\. Employees', p))
        elif slug == 'maple-ridge':
            yes = bool(re.search('2\\)? Employees(?! below)', p))
        elif slug == 'whistler':
            yes = 'ELECTED OFFICIALS' in p and 'Remuneration' in p and ('Position' in p) and (p.count('Name') >= 2 or 'OTHER EMPLOYEES' in p)
        elif slug == 'squamish':
            yes = '6.2. Other Employees' in p
        if yes:
            if start is None:
                start = at
            selected.append(at)
    if start is None:
        return {'key': path.stem, 'status': 'no-layout'}
    if slug != 'north-vancouver-district':
        selected = list(range(start, min(start + 20, len(pages) - 1)))
    rows = []
    controls = None
    under = None
    errors = []
    done = False
    active = False
    used = []
    doc = fitz.open(path.with_suffix('.pdf'))
    nameheads = 0
    for at in selected:
        if done:
            break
        p = pages[at]
        alt = fitz_rows(doc[at])
        used.append(at + 1)
        if slug == 'north-vancouver-district' and year == 2022:
            p = re.sub('(Jalali-Farahani,Moe Mohammad)\\s*\\n( +115,634 +789 +116,423 +470)', '\\1  \\2', p)
            p = re.sub(r'Guppy,Tamsin Wendy Frances\s*\nSue( +104,814 +245 +105,059 +584)', r'Guppy,Tamsin Wendy Frances Sue\1', p)
        if slug in ['north-vancouver-district', 'port-coquitlam']:
            active = True
        for line in p.splitlines():
            pref = line.strip()
            if not active:
                if slug == 'port-moody' and re.search('Staff \\(Greater than \\$75,000\\)', line, re.I) or (slug == 'pemberton' and re.search('Other Employees\\s*>\\s*75,000', line, re.I)) or (slug == 'white-rock' and '2. Employees' in line) or (slug == 'maple-ridge' and re.search('2\\)? Employees(?! below)', line)) or (slug == 'squamish' and '6.2. Other Employees' in line):
                    active = True
                elif slug == 'whistler':
                    if 'Name' in line and 'Position' in line:
                        nameheads += 1
                    if nameheads == 2 or 'OTHER EMPLOYEES' in line:
                        active = True
                continue
            sp = split_amounts(line, n)
            if rows:
                if sp and (slug in ['north-vancouver-district', 'port-coquitlam'] and pref.startswith('Total Section') or (slug == 'port-moody' and pref.startswith('Total Staff (Greater')) or (slug == 'pemberton' and re.match('(?:3\\s+)?Total\\s*>', pref)) or (slug == 'squamish' and pref.startswith('Remuneration and Expense Exceeding'))):
                    controls = sp[1]
                    done = True
                    break
                if slug == 'maple-ridge':
                    ct = sp[1] if sp and pref.startswith('Subtotal') else solo(line, n)
                    if ct:
                        controls = ct
                        done = True
                        break
                if sp and (slug == 'white-rock' and pref.startswith('Consolidated total of all remuneration') or (slug == 'whistler' and re.match('OTHER,? EMPLOYEES\\s', pref))):
                    under = sp[1]
                    continue
                if under:
                    ct = sp[1] if sp and pref.startswith('Total Employees') else solo(line, n)
                    if ct:
                        controls = [str(money(t) - (money(u) or 0)) for t, u in zip(ct, under)]
                        done = True
                        break
                    continue
            if not sp:
                sp = split_amounts(line, n - 1)
                if sp and re.search('\\d[\\d,]+(?:\\.\\d+)?\\s*$', sp[0]):
                    sp = None
            if not sp:
                continue
            prefix, amts = sp
            if not re.search('[A-Za-z]', prefix) or re.match('(?:Total|Subtotal|Remuneration|NUMBER|with |Consolidated|Base |Employee|\\d+\\s+[><=]|Section|Page|Prepared|Staff)', prefix, re.I):
                continue
            if sum((money(a) or 0 for a in amts[:2])) < 1000:
                continue
            actual = amts[:]
            amts += ['-'] * (n - len(amts))
            parts = re.split('\\s{2,}', prefix)
            if slug == 'maple-ridge' and len(parts) == 3 and re.fullmatch('\\*+', parts[-1]):
                parts = parts[:2]
            if slug == 'pemberton' and year >= 2023:
                name = prefix
                position = None
            elif slug == 'north-vancouver-district' and year < 2025:
                if len(parts) == 1:
                    name = parts[0]
                    position = None
                elif len(parts) == 2 and parts[1] == 'F':
                    name = parts[0]
                    position = 'Firefighter'
                else:
                    errors.append(['position-split', at + 1, prefix])
                    continue
            elif len(parts) == 2:
                name, position = parts
            else:
                errors.append(['position-split', at + 1, prefix])
                continue
            rowkey = key(prefix + ' ' + ' '.join(actual))
            if alt[rowkey]:
                alt[rowkey] -= 1
            else:
                from pypdf import PdfReader
                alternate = Counter((key(l) for l in PdfReader(str(path.with_suffix('.pdf'))).pages[at].extract_text().splitlines()))
                if not alternate[rowkey] and rowkey not in key(PdfReader(str(path.with_suffix('.pdf'))).pages[at].extract_text()):
                    errors.append(['reader-disagreement', at + 1, prefix, amts])
            rows.append({'name': name, 'position': position, 'raw': amts, 'page': at + 1, 'sourceKey': rowkey, 'sourcePrefix': prefix})
    if not controls:
        errors.append(['missing-subtotal'])
    sums = [sum((money(r['raw'][j]) or Decimal(0) for r in rows), Decimal(0)) for j in range(n)]
    if controls:
        deltas = [float(v - (money(c) or Decimal(0))) for v, c in zip(sums, controls)]
        cents = any(('.' in a for r in rows for a in r['raw']))
        tolerance = 0.02 if cents else max(1, len(rows) / 2)
        if any((abs(d) > tolerance for d in deltas)):
            errors.append(['subtotal-mismatch', deltas])
    else:
        deltas = []
    return {'key': path.stem, 'pages': used, 'n': len(rows), 'controls': controls, 'sums': list(map(str, sums)), 'deltas': deltas, 'errorCount': len(errors), 'errors': errors[:9], 'rows': rows}
import re, json, fitz
from pathlib import Path
from decimal import Decimal
from collections import Counter

def parse_document(path):
    slug, ys = path.stem.rsplit('-', 1)
    year = int(ys)
    if slug not in ['anmore', 'bowen-island', 'lions-bay', 'langley-city', 'richmond']:
        return parse_extended(path)
    pages = path.read_text().split('\x0c')
    n = 3 if slug in ['langley-city', 'richmond'] else 2
    selected = []
    for at, p in enumerate(pages):
        if slug == 'anmore':
            yes = '2. Other Employees' in p
        elif slug == 'bowen-island':
            yes = 'SCHEDULE OF EMPLOYEE REMUNERATION AND EXPENSES' in p
        elif slug == 'lions-bay':
            yes = 'Employees in excess of $75,000:' in p
        elif slug == 'langley-city':
            yes = 'Schedule of Remuneration & Expenses - City Employees' in p
        else:
            yes = 'Employee Earnings in Excess of $75,000' in p
        if yes:
            selected.append(at)
    if not selected:
        return {'key': path.stem, 'status': 'no-layout'}
    rows = []
    controls = None
    under = None
    errors = []
    done = False
    used = []
    doc = fitz.open(path.with_suffix('.pdf'))
    for at in selected:
        if done:
            break
        alt = fitz_rows(doc[at])
        used.append(at + 1)
        active = slug not in ['anmore', 'lions-bay']
        for line in pages[at].splitlines():
            pref = line.strip()
            if not active:
                if '2. Other Employees' in line or 'Employees in excess of $75,000:' in line:
                    active = True
                continue
            sp = split_amounts(line, n)
            if rows:
                ct = solo(line.replace('$', ' '), n)
                if ct and slug in ['bowen-island', 'lions-bay']:
                    controls = ct
                    done = True
                    break
                if sp and slug == 'richmond' and pref.startswith('Total'):
                    controls = sp[1]
                    done = True
                    break
                if sp and (slug == 'anmore' and pref.startswith('Consolidated total of other') or (slug == 'langley-city' and pref.startswith('All Employees under'))):
                    under = sp[1]
                    continue
                if under:
                    if sp and pref.startswith('Total: Other Employees'):
                        ct = sp[1]
                    if ct:
                        controls = [str(money(t) - (money(u) or 0)) for t, u in zip(ct, under)]
                        done = True
                        break
                    continue
            if not sp:
                sp = split_amounts(line, n - 1)
                if sp and re.search('\\d[\\d,]+(?:\\.\\d+)?\\s*$', sp[0]):
                    sp = None
            if not sp:
                continue
            prefix, amts = sp
            actual = amts[:]
            amts += ['-'] * (n - len(amts))
            if not re.search('[A-Za-z]', prefix) or re.match('(?:Total|Subtotal|Remuneration|NUMBER|with |Consolidated|Base |Employee|\\d+\\s+[><=]|Section|Page|Prepared|Staff)', prefix, re.I):
                continue
            if sum((money(a) or 0 for a in amts[:2])) < 1000:
                continue
            parts = re.split('\\s{2,}', prefix)
            if slug in ['richmond', 'langley-city']:
                name = prefix
                position = None
            elif len(parts) == 2:
                name, position = parts
            else:
                errors.append(['position-split', at + 1, prefix])
                continue
            rowkey = key(prefix + ' ' + ' '.join(actual))
            if alt[rowkey]:
                alt[rowkey] -= 1
            else:
                errors.append(['reader-disagreement', at + 1, prefix, amts])
            rows.append({'name': name, 'position': position, 'raw': amts, 'page': at + 1, 'sourceKey': rowkey, 'sourcePrefix': prefix})
    if not controls:
        errors.append(['missing-subtotal'])
    sums = [sum((money(r['raw'][j]) or Decimal(0) for r in rows), Decimal(0)) for j in range(n)]
    if controls:
        deltas = [float(v - (money(c) or Decimal(0))) for v, c in zip(sums, controls)]
        cents = any(('.' in a for r in rows for a in r['raw']))
        tolerance = 0.02 if cents else max(1, len(rows) / 2)
        if any((abs(d) > tolerance for d in deltas)):
            errors.append(['subtotal-mismatch', deltas])
    else:
        deltas = []
    return {'key': path.stem, 'pages': used, 'n': len(rows), 'controls': controls, 'sums': list(map(str, sums)), 'deltas': deltas, 'errorCount': len(errors), 'errors': errors[:12], 'rows': rows}
