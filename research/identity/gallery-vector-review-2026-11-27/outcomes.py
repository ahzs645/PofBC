"""Merge the fixed 420-design research cohort with the current gallery and the archived search records."""
import csv
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent


def read(name):
    with (ROOT / name).open(newline='') as source:
        return list(csv.DictReader(source))


def first(row, fields):
    return next((row.get(f) for f in fields if row.get(f)), '')


lookup = {parse_qs(urlsplit(row['Gallery link']).query)['mark'][0]: row for row in read('inventory.csv')}
requests = {r['Design ID']: r for r in read('public-sweep-designs.csv')}
indexed = defaultdict(set)
for r in read('public-search-readings.csv'):
    if r['Reader outcome'] == 'Indexed content readable':
        for key in r['Design IDs'].split(' | '):
            indexed[key].add(r['URL'])
studies = defaultdict(list)
for path in sorted(ROOT.glob('*followup.csv')):
    for row in read(path.name):
        key = first(row, ['Design ID', 'Mark ID', 'Gallery design ID', 'Gallery ID', 'Design id', 'Design reviewed', 'Designs checked'])
        if not key:
            raise ValueError(f'{path.name} needs its design ID column mapped')
        evidence = first(row, ['Review', 'Comparison and source limits', 'Evidence from this review', 'Evidence', 'Evidence or limitation', 'Comparison', 'Finding', 'Outcome', 'Result'])
        for design in key.split(' | '):
            # Additional rows in the tourism ledger describe related leads by name.
            if design in lookup:
                studies[design].append((path.name, evidence))

with (ROOT / 'public-sweep-outcomes.csv').open('w', newline='') as output:
    out = csv.writer(output, lineterminator='\n')
    out.writerow(['Design ID', 'Collection', 'Design', 'Baseline light tile', 'Current light tile', 'Current dark tile',
                  'Finding for the original design', 'Current light source artwork', 'Sources requested', 'Source requests with HTTP 200',
                  'Additional indexed pages read', 'Sector evidence ledger', 'Specimen comparison', 'Gallery link'])
    for row in read('public-sweep-input.csv'):
        key = row['Design ID']
        now, checks = lookup[key], requests[key]
        if key == 'school-district-36-logo-current':
            outcome = 'Confirmed as fully vector. All four filter references point to internal vector groups.'
        elif now['Light tile'] == 'Vector':
            outcome = 'The gallery now uses a verified vector for this design on a light page.'
        elif now['Light tile'] == 'Contains bitmap':
            outcome = 'This exact specimen includes bitmap content.'
        else:
            outcome = 'Light page retains the published raster. An exact positive vector remains unverified.'
        out.writerow([key, row['Collection'], now['Design'], row['Baseline light tile'], now['Light tile'], now['Dark tile'],
                      outcome, now['Default artwork'], checks['Source requests'], checks['Successful responses'],
                      ' | '.join(sorted(indexed[key])), ' | '.join(path for path,_ in studies[key]),
                      ' | '.join(note for _,note in studies[key]), now['Gallery link']])
