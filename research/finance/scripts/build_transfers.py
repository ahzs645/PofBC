"""Match the Government Transfers payees to site bodies and write the matched rows.

Usage (from the repository root):

    node research/finance/scripts/dump_bodies.mjs research/finance/cache/bodies.json
    python3 -I research/finance/scripts/build_transfers.py \
        research/finance/cache/transfers  research/finance/cache/bodies.json  research/finance

A payee is matched to a body by, in order:

  1. decision  transfers/alias-decisions.csv, read by hand: a payee spelling and the body it is, or a
               blank body to keep the payee out (an ambiguous or wrong match);
  2. school-district  "SCHOOL DISTRICT NO 5 …", "BOARD OF EDUCATION OF SCHOOL DISTRICT NO. 5 …":
               the district by its number;
  3. name      the payee's words equal one of a body's names (its name, short name or aliases), with
               "British Columbia" read as "BC" and a corporate suffix (Ltd., Inc., Corporation,
               Society) ignored. A spelling that names more than one body is kept out.

Everything else is kept out: unmatched organizations and every individual. The raw files stay in the
cache, which is not committed; only matched rows are written.

Writes:
  aliases.csv            every payee spelling matched to a body, with the rule, the years seen, the
                         number of rows, and the spellings as printed; decisions that keep a payee
                         out are listed with a blank body
  transfers/fye<YYYY>.csv  the matched rows of each year, as printed: payee, ministry, amount
  transfers/totals.csv   each file's row count and total, and how much of it is matched
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transfers_common as t  # noqa: E402

SUFFIX = re.compile(r' (LTD|INC|LIMITED|CORP|CORPORATION|SOCIETY)$')
SCHOOL = re.compile(r'^(?:BOARD OF (?:EDUCATION|SCHOOL TRUSTEES) OF )?SCHOOL DISTRICT (?:NO )?0*(\d{1,2})\b(.*)$')
NOT_A_BOARD = re.compile(r'\b(FOUNDATION|PARENT|PAC|DPAC|ASSOCIATION|SOCIETY|TEACHERS|UNION|CLUB|COUNCIL|STUDENTS|CUPE)\b')


def strip(key):
    return SUFFIX.sub('', key)


def main():
    cache, bodies_path, out_dir = sys.argv[1:4]
    bodies = json.load(open(bodies_path))
    ids = {b['id'] for b in bodies}
    by_name = defaultdict(set)
    for body in bodies:
        for name in body['names']:
            by_name[strip(t.payee_key(name))].add(body['id'])

    decisions = {}
    with open(os.path.join(out_dir, 'transfers', 'alias-decisions.csv'), newline='') as f:
        for row in csv.DictReader(f):
            key = t.payee_key(row['payee_key'])
            if row['body_id'] and row['body_id'] not in ids:
                raise SystemExit(f'alias-decisions.csv: {row["body_id"]} is not a site body')
            decisions[key] = row

    def match(key):
        if key in decisions:
            row = decisions[key]
            return (row['body_id'] or None, 'decision', row['note'])
        m = SCHOOL.match(key)
        if m and not NOT_A_BOARD.search(m.group(2)):
            body = f'school-district-{int(m.group(1))}'
            if body in ids:
                return (body, 'school-district', '')
        found = by_name.get(strip(key), set())
        if len(found) == 1:
            return (next(iter(found)), 'name', '')
        if len(found) > 1:
            return (None, 'ambiguous', 'Names more than one site body: ' + ', '.join(sorted(found)))
        return (None, None, '')

    aliases = {}
    totals = []
    os.makedirs(os.path.join(out_dir, 'transfers'), exist_ok=True)
    for fye in sorted(t.FILES):
        rows = t.rows_of(cache, fye)
        matched = []
        for payee, ministry, amount in rows:
            key = t.payee_key(payee)
            body, rule, note = match(key)
            if rule in ('decision', 'ambiguous') or body:
                entry = aliases.setdefault(key, {'payee_key': key, 'body_id': body or '', 'rule': rule, 'first_fye': fye, 'last_fye': fye, 'rows': 0, 'spellings': set(), 'note': note})
                entry['last_fye'] = fye
                entry['rows'] += 1
                entry['spellings'].add(payee)
            if body:
                matched.append({'fye': fye, 'payee_as_printed': payee, 'ministry_as_printed': ministry, 'amount': amount, 'body_id': body, 'match_rule': rule})
        with open(os.path.join(out_dir, 'transfers', f'fye{fye}.csv'), 'w', newline='') as f:
            w = csv.DictWriter(f, ['fye', 'payee_as_printed', 'ministry_as_printed', 'amount', 'body_id', 'match_rule'], lineterminator='\n')
            w.writeheader()
            w.writerows(sorted(matched, key=lambda r: (r['body_id'], r['payee_as_printed'], r['ministry_as_printed'], -r['amount'])))
        totals.append({'fye': fye, 'rows': len(rows), 'total': sum(r[2] for r in rows), 'matched_rows': len(matched),
                       'matched_total': sum(r['amount'] for r in matched), 'bodies': len({r['body_id'] for r in matched}), 'source_url': t.url_of(fye)})
        print(f'FYE {fye}: {len(rows)} rows, ${totals[-1]["total"]:,}; matched {len(matched)} rows, ${totals[-1]["matched_total"]:,}, {totals[-1]["bodies"]} bodies', file=sys.stderr)

    with open(os.path.join(out_dir, 'transfers', 'totals.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, list(totals[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(totals)
    for key in decisions:
        if key not in aliases:
            print(f'alias-decisions.csv: {key} is in no file', file=sys.stderr)
    with open(os.path.join(out_dir, 'aliases.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['payee_key', 'body_id', 'rule', 'first_fye', 'last_fye', 'rows', 'spellings', 'note'], lineterminator='\n')
        w.writeheader()
        for entry in sorted(aliases.values(), key=lambda e: (e['body_id'] == '', e['body_id'], e['payee_key'])):
            w.writerow({**entry, 'spellings': ' | '.join(sorted(entry['spellings']))})


if __name__ == '__main__':
    main()
