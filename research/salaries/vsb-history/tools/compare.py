import os
import json, sys, re
from decimal import Decimal
def money(s):
    if s is None or s == '-': return None
    neg = s.startswith('(') and s.endswith(')')
    d = Decimal(s.strip('()').replace(',', ''))
    return -d if neg else d
F = ['page', 'surname', 'given', 'position', 'rem', 'exp']
for y in sys.argv[1:]:
    d = json.load(open(f'{os.environ.get("VSB_WORK", "vsb-work")}/out/{y}.json'))
    A = [[r[k] for k in F] for r in d['layout']]; B = [[r[k] for k in F] for r in d['plumber']]
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(A, B)) if a != b]
    print('==', y, 'rows', len(A), len(B), 'diffs', len(diffs) + abs(len(A) - len(B)))
    for x in diffs[:10]: print('  ', x)
    rows = d['plumber']
    R = sum(money(r['rem']) for r in rows); E = sum(money(r['exp']) or 0 for r in rows)
    print('  computed', R, E, 'tail', d['layoutTail'][:1], d['plumberTail'][:1])
    low = [r for r in rows if money(r['rem']) <= 75000]; print('  <=75000:', [(r['surname'], r['rem']) for r in low])
    neg = [r for r in rows if (money(r['exp']) or 0) < 0 or money(r['rem']) < 0]; print('  negative:', [(r['surname'], r['rem'], r['exp']) for r in neg])
    odd = [r for r in rows if re.search(r"[^A-Za-z\-' .,()*]", r['surname'] + r['given'])]; print('  odd chars:', [(r['surname'], r['given']) for r in odd][:20])
    print('  expNull', sum(r['exp'] in (None, '-') for r in rows), 'expBlank(None)', sum(r['exp'] is None for r in rows))
