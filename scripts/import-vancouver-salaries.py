#!/usr/bin/env python3
"""Verify Vancouver's official CSV against its JSON export and API annual controls.

Offline by default. Fetch current inputs separately; reviewed October 30 inputs are
retained compressed in research/salaries/vancouver/raw. No cents are rounded for import.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import shutil
import tempfile
from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/vancouver'
DATASET = 'https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/employee-remuneration-and-expenses-earning-over-75000'
CSV_URL = DATASET + '/exports/csv?lang=en&timezone=UTC&use_labels=false&delimiter=%2C'
JSON_URL = DATASET + '/exports/json?lang=en&timezone=UTC'
CONTROLS_URL = DATASET + '/records?select=year%2Ccount(*)%20as%20rows%2Csum(remuneration)%20as%20remuneration%2Csum(expenses)%20as%20expenses&group_by=year&order_by=year&limit=100'
FIELDS = ['year', 'name', 'department', 'title', 'remuneration', 'expenses']
CSV_HASH = 'deb6d8835da40bb4ae0189e12f8666542fc7ff9f1ca6809e42315f2a674cc34f'
JSON_HASH = 'c604f421a5ffc07a1bdc30835c41d777fb5d7c50bdd4e64dbad6bc2212adeb73'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix in ('.gz', '.gzip') else data


def number(value):
    if value is None or value == '':
        return None
    d = Decimal(str(value))
    if not d.is_finite() or d != d.quantize(Decimal('.01')):
        raise ValueError(f'Invalid source money: {value}')
    return int(d) if d == int(d) else float(d)


def total(values):
    return number(sum((Decimal(str(v)) for v in values if v is not None), Decimal(0)))


def canonical_row(row):
    return tuple(number(row[field]) if field in ('remuneration', 'expenses') else (row[field] or None) for field in FIELDS)


def normalized_name(value):
    return re.sub(r'\s*,\s*', ',', ' '.join(value.split()).casefold().replace('-', ''))


def comparison_key(name, amount):
    return normalized_name(name), int(Decimal(str(amount)).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN))


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def process(csv_path, json_path, controls_path, baseline_path, out):
    csv_bytes, json_bytes = read_bytes(csv_path), read_bytes(json_path)
    if digest(csv_bytes) != CSV_HASH or digest(json_bytes) != JSON_HASH:
        raise ValueError('Source bytes differ from the reviewed October 30 release; review the new release before accepting it.')
    reader = csv.DictReader(io.StringIO(csv_bytes.decode('utf-8-sig'), newline=''))
    if reader.fieldnames != FIELDS:
        raise ValueError('Unexpected Vancouver CSV schema')
    csv_rows = list(reader)
    json_rows = json.loads(json_bytes)
    if Counter(map(canonical_row, csv_rows)) != Counter(map(canonical_row, json_rows)):
        raise ValueError('CSV and JSON exports disagree, including multiplicity or missing values')
    controls = json.loads(read_bytes(controls_path))
    annual = {r['year'][:4]: r for r in controls['results']}
    years = sorted({r['year'] for r in csv_rows})
    if years != [str(y) for y in range(2008, 2026)] or len(csv_rows) != 49742:
        raise ValueError('Unexpected calendar coverage or row count')
    pending = {}
    for name, data in [('employee-remuneration.csv.gzip', csv_bytes), ('employee-remuneration.json.gzip', json_bytes), ('annual-controls.json.gzip', read_bytes(controls_path))]:
        pending['raw/' + name] = gzip.compress(data, mtime=0)
    sources = []
    for year in years:
        subset = [r for r in csv_rows if r['year'] == year]
        rows = [['city-of-vancouver', r['name'], ' · '.join(filter(None, [r['title'], r['department']])) or None,
                 number(r['remuneration']), number(r['expenses']), None] for r in subset]
        pay, expenses = total(r[3] for r in rows), total(r[4] for r in rows)
        control = annual[year]
        if len(rows) != control['rows'] or any(abs(Decimal(str(actual)) - Decimal(str(control[key]))) > Decimal('.001')
                                               for actual, key in [(pay, 'remuneration'), (expenses, 'expenses')]):
            raise ValueError(f'{year}: CSV does not reconcile with API controls')
        boundary = [r for r in rows if r[3] <= 75000]
        if boundary and not (year == '2017' and len(boundary) == 1 and boundary[0][1] == 'Hildebrandt, A' and boundary[0][3] == 75000):
            raise ValueError(f'{year}: new threshold exception requires source review')
        payload = gzip.compress(compact(rows) + b'\n', mtime=0)
        filename = f'{year}-employees.json.gzip'
        pending[filename] = payload
        notes = [
            'The City publishes calendar-year employee remuneration. This dataset includes salary, overtime, gratuity and vacation payouts, and excludes severance.',
            'This is the City of Vancouver open-data export, cross-checked against its JSON serialization and API annual totals. These are consistency checks within the same official dataset, not an independent reconciliation to every SOFI PDF.',
            'The City identifies its published Statement of Financial Information as authoritative. Those original reports were not retrievable in this pass.',
            'Blank expenses remain missing; explicit zero and negative expenses are preserved. The City cautions that expenses may not reconcile within the same reporting period.',
            'Published surnames and initials do not identify unique people. Asterisks in 2012 and 2013 indicate optional gratuity/vacation payouts and remain as published.',
            'Mayor and councillor records are outside this employee dataset. Retained compiled council records are separately classified and their exact reporting period remains unverified.'
        ]
        if boundary:
            notes.append('The 2017 export includes one employee at exactly $75,000 despite the dataset title saying over $75,000. That source row is preserved without changing the stated threshold.')
        sources.append({
            'id': f'vancouver-employees-{year}', 'year': year, 'periodType': 'calendar',
            'periodStart': f'{year}-01-01', 'periodEnd': f'{year}-12-31',
            'status': 'accepted', 'category': 'employee-remuneration', 'sourceKind': 'official-open-data',
            'employerSlug': 'city-of-vancouver', 'employerName': 'City of Vancouver', 'sector': 'Government',
            'title': f'City of Vancouver {year} employee remuneration and expenses',
            'sourceUrl': CSV_URL, 'indexUrl': 'https://opendata.vancouver.ca/explore/dataset/employee-remuneration-and-expenses-earning-over-75000/',
            'sha256': CSV_HASH, 'sha256Scope': 'Complete CSV containing all 18 calendar years',
            'file': filename, 'dataSha256': digest(payload), 'rowCount': len(rows),
            'totalRemuneration': pay, 'totalExpenses': expenses, 'currency': 'CAD',
            'threshold': 75000, 'thresholdComparison': '>', 'nameDisclosure': 'surname-and-initials',
            'positionDisclosure': 'published-title-and-department', 'notes': notes,
            'validation': {'date': '2026-10-30', 'everyFieldCsvJsonAgreement': True, 'jsonSourceUrl': JSON_URL,
                           'jsonSha256': JSON_HASH, 'apiAnnualCountAndTotalsAgreement': True, 'apiAnnualControlsUrl': CONTROLS_URL,
                           'apiAnnualControlsSha256': digest(read_bytes(controls_path)),
                           'missingExpenses': sum(r[4] is None for r in rows), 'negativeExpenses': sum(r[4] is not None and r[4] < 0 for r in rows),
                           'publishedThresholdExceptions': len(boundary), 'sofiPdfReconciliation': 'not-completed-source-unavailable'}
        })
    baseline = json.loads(read_bytes(baseline_path))
    employer = next(e for e in baseline['employers'] if e['slug'] == 'city-of-vancouver')
    replacements, comparisons = [], []
    for label, calendar in [('2017/18', '2018'), ('2020/21', '2020'), ('2023/24', '2023')]:
        at = baseline['years'].index(label)
        legacy = [r for r in employer['rows'] if r[4] == at]
        retained = [r for r in legacy if r[1] in ('Mayor', 'Councillor')]
        employees = [r for r in legacy if r[1] not in ('Mayor', 'Councillor')]
        source = [r for r in csv_rows if r['year'] == calendar]
        left = Counter(comparison_key(r[0], r[2]) for r in employees)
        right = Counter(comparison_key(r['name'], r['remuneration']) for r in source)
        if left != right:
            raise ValueError(f'{label}: the claimed calendar-year employee match no longer holds')
        rule = {
            'employerSlug': 'city-of-vancouver', 'compiledYear': label, 'replacementYear': calendar,
            'sourceIds': [f'vancouver-employees-{calendar}'], 'retainPositions': ['Mayor', 'Councillor'],
            'expectedRows': len(employees), 'expectedRetainedRows': len(retained),
            'selectedRowsSha256': digest(compact([r[:4] for r in employees])),
            'reason': f'All {len(employees):,} compiled employee name/pay pairs under {label} match the City calendar {calendar} export after documented comparison-only normalization. Replace these employee rows under the actual calendar year.',
            'evidence': 'vancouver/compiled-period-comparison.json'
        }
        if retained:
            rule['retainedSource'] = {
                'id': 'vancouver-compiled-council-' + label.replace('/', '-'), 'scope': 'elected-officials',
                'title': f'Vancouver mayor/council records retained from compiled edition {label}',
                'notes': ['These 11 mayor/councillor records are preserved from the immutable compiler snapshot. The employee year correction does not by itself prove their reporting period or verify their amounts.',
                          'Their original council/SOFI source remains to be checked; no calendar year is inferred and these are not counted as accepted official employee records.']
            }
        replacements.append(rule)
        comparisons.append({'compiledLabel': label, 'verifiedEmployeeCalendarYear': calendar, 'compiledRows': len(legacy),
                            'matchedEmployeeRows': len(employees), 'retainedCouncilRows': len(retained),
                            'unmatchedEmployeeRows': 0, 'officialEmployeeRowsAbsentAfterComparison': 0})
    comparison = {
        'baselineSha256': digest(baseline_path.read_bytes()), 'csvSha256': CSV_HASH,
        'method': 'Multiset of disclosed name/pay pairs. Casefold, whitespace collapse, ASCII-hyphen removal and comma-space normalization; Decimal ROUND_HALF_EVEN whole-dollar comparison only. All source cents and exact names remain unchanged on import. Exact Mayor/Councillor positions excluded from employee comparison.',
        'results': comparisons
    }
    manifest = {'version': 1, 'reviewed': '2026-10-30',
        'coverageNotes': ['Calendar-year employee records 2008–2025. Municipal reporting periods are not inferred from another municipality.',
                          'The official open-data export remains distinguishable from an original-SOFI reconciliation.'],
        'sources': sources, 'compiledReplacements': replacements}
    # All source, control and replacement checks have passed. Publish the complete
    # normalized collection together; a rejected source cannot leave mixed years.
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.vancouver-import-', dir=out.parent))
    backup = out.with_name(out.name + '.previous-import')
    if backup.exists():
        shutil.rmtree(stage)
        raise ValueError(f'Previous import backup exists: {backup}')
    try:
        for relative, data in pending.items():
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        write_json(stage / 'compiled-period-comparison.json', comparison)
        write_json(stage / 'sources.json', manifest)
        if (out / 'README.md').exists():
            shutil.copy2(out / 'README.md', stage / 'README.md')
        had_output = out.exists()
        if had_output:
            out.rename(backup)
        try:
            stage.rename(out)
        except Exception:
            if had_output:
                backup.rename(out)
            raise
        if had_output:
            shutil.rmtree(backup)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(json.dumps({'years': len(sources), 'officialEmployeeRows': len(csv_rows), 'compiledEmployeeRowsReplaced': sum(r['expectedRows'] for r in replacements),
                      'compiledCouncilRowsRetained': sum(r['expectedRetainedRows'] for r in replacements), 'csvJsonAllFieldsAgree': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=OUT / 'raw/employee-remuneration.csv.gzip')
    parser.add_argument('--json', type=Path, default=OUT / 'raw/employee-remuneration.json.gzip')
    parser.add_argument('--controls', type=Path, default=OUT / 'raw/annual-controls.json.gzip')
    parser.add_argument('--baseline', type=Path, default=ROOT / 'research/salaries/compiled-baseline.json.gzip')
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args()
    process(args.csv, args.json, args.controls, args.baseline, args.out)
