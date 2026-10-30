#!/usr/bin/env python3
"""Promote the verified Columbia Hydro Constructors schedules into an accepted salary collection.

The rows were staged by stage_chc_recovery.py from attributed captures of BC Hydro's Financial
Information Act returns (research/salaries/chc-recovery/). They are accepted only on the evidence
committed beside them: for every year, check_chc_pdf.py's comparison against the original PDF
(pdf-verification/<year>.json) must belong to the capture as it now stands, match the expected PDF
hash, and find every named row in both readers; and the reviewed summary-page figures
(pdf-verification/review.json) must equal the capture's controls. A capture edited after its
check, or a check that found a missing or extra row, stops the run.

Writes research/salaries/columbia-hydro-constructors/: one normalized gzip a year, rows
[employer slug, "Surname, Initials", null, remuneration, expenses, physical PDF page], and the
sources.json manifest that scripts/build-salaries.mjs reads. Standard library only; no downloads.

    python3 scripts/accept-chc-salaries.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / 'research/salaries/chc-recovery'
OUT = ROOT / 'research/salaries/columbia-hydro-constructors'
SLUG = 'sub-columbia-hydro-constructors'
NAME = 'Columbia Hydro Constructors Ltd.'
INDEX_URL = 'https://www.bchydro.com/about/accountability_reports/financial_reports.html'
YEARS = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17']
AGGREGATE_ONLY = ['2017-18']
CONTROL_KEYS = ['totalRemuneration', 'totalExpenses', 'belowThresholdRemuneration', 'belowThresholdExpenses', 'employerCppEi']


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    sys.exit(f'accept-chc-salaries: {message}')


def disclosed_name(raw: str) -> str:
    """"PR Adams" as the Hydro schedules are stored: "Adams, PR". The initials are not expanded."""
    initials, _, surname = raw.partition(' ')
    if not initials.isalpha() or not initials.isupper() or len(initials) > 3 or not surname.strip():
        fail(f'name is not initials then surname: {raw!r}')
    return f'{surname.strip()}, {initials}'


def checked(year: str, review: dict) -> tuple[dict, list]:
    capture_bytes = (STAGING / 'captures' / f'{year}.json').read_bytes()
    capture = json.loads(capture_bytes)
    check = json.loads((STAGING / 'pdf-verification' / f'{year}.json').read_bytes())
    candidates = json.loads((STAGING / 'candidates' / f'{year}.json').read_bytes())
    if check['captureSha256'] != sha256(capture_bytes):
        fail(f'{year}: the PDF check was made against a different capture; rerun check_chc_pdf.py')
    if not check['pdfSha256MatchesExpected'] or check['pdfSha256'] != capture['expectedPdfSha256FromEarlierPackage']:
        fail(f'{year}: original PDF hash does not match')
    if not check['namedRowComparisonPassed'] or len(check['readerResults']) != 2:
        fail(f'{year}: named rows were not confirmed by both readers')
    for reader in check['readerResults']:
        if not reader['allNamedRowsMatch'] or reader['missingRows'] or reader['extraRows'] or reader['unparsedMonetaryLines']:
            fail(f'{year}: {reader["reader"]} reported a difference')
        if reader['parsedNamedRows'] != len(candidates):
            fail(f'{year}: {reader["reader"]} read {reader["parsedNamedRows"]} rows, {len(candidates)} staged')
    reviewed = review['controls'][year]
    if any(reviewed[key] != capture['controls'][key] for key in CONTROL_KEYS) or reviewed['pdfPage'] != capture['controlsPdfPage']:
        fail(f'{year}: reviewed summary figures differ from the capture')
    return capture, candidates


def main() -> None:
    review = json.loads((STAGING / 'pdf-verification' / 'review.json').read_bytes())
    OUT.mkdir(parents=True, exist_ok=True)
    sources = []
    for year in YEARS:
        capture, candidates = checked(year, review)
        rows = [[SLUG, disclosed_name(row['rawName']), None, row['remuneration'], row['expenses'], row['pdfPage']] for row in candidates]
        data = gzip.compress((json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), compresslevel=9, mtime=0)
        (OUT / f'{year}.json.gzip').write_bytes(data)
        controls = capture['controls']
        remuneration = sum(row[3] for row in rows)
        expenses = sum(row[4] for row in rows)
        named_remuneration = controls['totalRemuneration'] - controls['belowThresholdRemuneration']
        named_expenses = controls['totalExpenses'] - controls['belowThresholdExpenses']
        pages = [page['pdfPage'] for page in capture['pages']]
        sources.append({
            'id': capture['sourceId'], 'year': capture['fiscalYear'], 'file': f'{year}.json.gzip',
            'employerSlug': SLUG, 'employerName': NAME, 'sector': 'Crown corporations',
            'title': f'{capture["sourceTitle"]}: Columbia Hydro Constructors Ltd. employee schedule',
            'sourceUrl': capture['sourceUrl'], 'indexUrl': INDEX_URL,
            'sha256': capture['expectedPdfSha256FromEarlierPackage'], 'dataSha256': sha256(data),
            'periodStart': capture['periodStart'], 'periodEnd': capture['periodEnd'], 'currency': 'CAD',
            'category': 'employee-remuneration', 'scope': 'named-employees-over-threshold',
            'scopeDescription': 'Named employees paid over $75,000, from the Columbia Hydro Constructors schedule in BC Hydro’s return; employee schedule only',
            'threshold': 75000, 'thresholdComparison': '>', 'thresholdRule': 'over',
            'nameDisclosure': 'surname-and-initials', 'positionDisclosure': 'not-published',
            'rowCount': len(rows), 'totalRemuneration': remuneration, 'totalExpenses': expenses,
            'status': 'verified', 'verifiedOn': review['reviewedOn'],
            'validation': {
                'physicalPdfPages': pages, 'summaryPdfPage': capture['controlsPdfPage'],
                'reportedTotal': [controls['totalRemuneration'], controls['totalExpenses']],
                'reportedUnderThreshold': [controls['belowThresholdRemuneration'], controls['belowThresholdExpenses']],
                'employerCppEiNotInTotal': controls['employerCppEi'],
                'residual': [remuneration - named_remuneration, expenses - named_expenses],
                'evidence': f'research/salaries/chc-recovery/pdf-verification/{year}.json',
                'review': 'research/salaries/chc-recovery/pdf-verification/review.json'
            },
            'notes': [
                'Columbia Hydro Constructors Ltd., a BC Hydro subsidiary, files its own employee schedule inside BC Hydro’s Financial Information Act return. Its rows are not part of BC Hydro’s.',
                'Names are surnames and initials as published, not resolved identities; repeated names are kept as separate rows.',
                'Named rows are reconciled with the printed total less the at-or-below-threshold aggregate; differences of a few dollars are left as published.'
            ]
        })
    manifest = {
        'version': 1, 'publisher': 'BC Hydro (Columbia Hydro Constructors Ltd. schedule)', 'verifiedAt': review['reviewedOn'],
        'sourceIndexUrl': INDEX_URL,
        'rowSchema': ['employer slug', 'disclosed name (surname, initials)', 'position (not published)', 'remuneration', 'expenses', 'physical PDF page'],
        'sources': sources,
        'aggregateOnlyPeriods': [{
            'year': '2017/18', 'sourceUrl': json.loads((STAGING / 'captures' / '2017-18.json').read_bytes())['sourceUrl'],
            'pdfPage': 175, 'reportedTotal': [208410, 12021], 'reportedUnderThreshold': [208410, 12021],
            'note': 'The schedule names no employee over $75,000; all its employee remuneration is in the at-or-below-threshold aggregate. No rows are imported, and this is not a year without employees.'
        } for _ in AGGREGATE_ONLY],
        'coverageNotes': ['Accepted on the PDF verification recorded in research/salaries/chc-recovery/pdf-verification/; see that folder’s review.json.']
    }
    (OUT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({source['year']: [source['rowCount'], source['validation']['residual']] for source in sources}))


if __name__ == '__main__':
    main()
