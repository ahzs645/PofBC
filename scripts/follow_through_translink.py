#!/usr/bin/env python3
"""Rebuild the six hash-pinned TransLink employee disclosures, using two readers.

Only this collection is written. PDFs and the independent Poppler text are cached
outside the checkout; the originals are always fingerprinted before extraction.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

import fitz

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path('/workspace/salary-source-follow-through/cache-translink')
OUT = ROOT / 'research/salaries/follow-through-translink'
INPUT = Path('/workspace/salary-source-follow-through/additional-sources.json')
ROW_SCHEMA = ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage']
ENTITIES = [
    ('translink', 'South Coast British Columbia Transportation Authority'),
    ('british-columbia-rapid-transit-company', 'British Columbia Rapid Transit Company Ltd.'),
    ('coast-mountain-bus-company', 'Coast Mountain Bus Company Ltd.'),
    ('transit-police', 'TransLink Security Management Ltd.'),
    ('west-coast-express', 'West Coast Express Ltd.'),
]
RANGES = {
    2020: [(13, 28), (46, 67), (77, 141), (151, 156), (160, 160)],
    2021: [(12, 28), (45, 66), (76, 137), (146, 151), (155, 155)],
    2022: [(12, 27), (45, 67), (77, 147), (156, 162), (166, 166)],
    2023: [(12, 29), (47, 73), (84, 169), (180, 185), (189, 189)],
    2024: [(12, 33), (52, 80), (91, 186), (196, 202), (206, 206)],
    2025: [(12, 36), (55, 86), (97, 203), (214, 220), (224, 224)],
}
AMOUNT = re.compile(r'\$?\(?-?[\d,]+\)?$')
NONNAME = re.compile(r'^(?:Total\b|TOTAL\b|remuneration\b|Receiver\b|Notes:|\d+\.|For the|Name\b|Schedule\b|Paid in|Salary\b|Payments|Other\b|Expenses\b|\(\$\))')
ANONYMOUS = re.compile(r'^(?:CSO|Constable|Corporal|Sergeant|Staff Sergeant|Inspector|Special Constable|Community Safety Officer)\s+\d+$|FOIPP|withheld', re.I)
EXPECTED_COUNTS = {
    2020: [557, 847, 2635, 210, 6], 2021: [604, 857, 2496, 229, 7],
    2022: [578, 893, 2874, 238, 7], 2023: [654, 1029, 3504, 233, 6],
    2024: [799, 1129, 3896, 264, 6], 2025: [906, 1222, 4340, 266, 6],
}
# Exact differences (displayed individual row sums minus printed >$75,000
# control). No balancing changes are made to the source observations.
RESIDUALS = {
    (2022, 1): [3, 7, 7, -1], (2023, 1): [-1, -5, 17, 4],
    (2024, 2): [3859, -3212, 647, -12], (2025, 1): [0, 0, 0, 9],
    (2025, 4): [0, 0, 0, -1],
}
HELD = {(2024, 2)}
WRAP_REVIEW_PAGES = {
    2020: [124], 2021: [146], 2022: [45, 67], 2023: [47, 73],
    2024: [24, 62, 67, 70, 77, 78, 111, 115, 117, 196, 206],
    2025: [55, 56, 62, 66, 71, 73, 74, 82, 83, 85, 119, 123, 125, 135, 153, 156, 162, 164, 173, 174, 197, 214, 224],
}
BASE_WARNING = ('Remuneration is the published annual payment disclosure, not an annual salary rate or total compensation. '
                'It excludes pension benefits, non-taxable benefits and amounts payable under severance agreements. '
                'Expenses are separate. Blank/dash cells remain unknown (null), while numeric zero remains zero. '
                'Withheld-name individual payments, where present, retain name=null and separate source occurrences.')
HOLD_REASON = ('The complete 3,896-row CMBC 2024 candidate schedule agrees between both native readers, '
               'but row sums exceed printed salary payments by $3,859 and remuneration by $647, '
               'and fall below printed Other by $3,212 and expenses by $12. '
               'The source footnotes give no explanation. These larger control differences remain unresolved.')
HOLD_NEXT = ('Inspect a publicly issued revised/corrected official report or further official row-level control explanation; '
             'resolve the four printed subtotal differences before importing this cohort. '
             'Preserve all candidate values and controls without balancing or substituting totals.')


def clean(s):
    return ' '.join(s.replace('\xa0', ' ').replace('\xad', '-').split())


def money(s):
    s = clean(s).replace('$', '').replace(',', '')
    if not s or s in ['-', '–', '—']:
        return None
    return -int(s[1:-1]) if s.startswith('(') and s.endswith(')') else int(s)


def name_value(label):
    return None if ANONYMOUS.search(label) else label


def native_rows(page, pn):
    """Use positioned words and total-remuneration cells as row anchors."""
    words = [w for w in page.get_text('words') if clean(w[4])]
    anchors = sorted([w for w in words if 395 <= w[0] and w[2] <= 495 and w[1] > 145 and AMOUNT.fullmatch(clean(w[4]))], key=lambda w: w[1])
    result = []
    controls = []
    for ai, anchor in enumerate(anchors):
        y = anchor[1]
        same = [w for w in words if abs(w[1] - y) <= 2.6]
        cols = []
        rawcols = []
        for x0, x1 in [(245, 325), (325, 395), (395, 495), (495, 570)]:
            cell = sorted([w for w in same if x0 <= (w[0] + w[2]) / 2 < x1], key=lambda w: w[0])
            rawcols.append(clean(''.join(w[4] for w in cell)))
            cols.append(money(rawcols[-1]))
        left = sorted([w for w in same if w[0] < 245], key=lambda w: w[0])
        label = clean(' '.join(w[4] for w in left))
        if NONNAME.search(label) or not label:
            controls.append({'label': label, 'amounts': cols, 'rawAmounts': rawcols, 'pdfPage': pn, 'y': round(y, 2)})
            continue
        nexty = anchors[ai + 1][1] if ai + 1 < len(anchors) else y + 25
        extras = sorted([w for w in words if w[0] < 245 and y + 3 < w[1] < min(nexty - 2.6, y + 22)], key=lambda w: (round(w[1]), w[0]))
        extra = clean(' '.join(w[4] for w in extras))
        if extra and not NONNAME.search(extra) and not (',' in label and ',' in extra):
            label = clean(label + ' ' + extra)
        # Two reports put the surname on the line ABOVE the monetary cells.
        # A preceding line with its own monetary anchor is a separate employee.
        if ',' not in label and not ANONYMOUS.search(label):
            prior = sorted([w for w in words if w[0] < 245 and y - 16 < w[1] < y - 3 and all(abs(w[1] - a[1]) > 2.6 for a in anchors)], key=lambda w: (round(w[1]), w[0]))
            prefix = clean(' '.join(w[4] for w in prior))
            if ',' in prefix and not NONNAME.search(prefix):
                label = prefix + ' ' + label
        result.append({'label': label, 'amounts': cols, 'rawAmounts': rawcols, 'pdfPage': pn, 'y': round(y, 2)})
    return result, controls


def poppler_rows(text, pn):
    """Independently parse whitespace columns in pdftotext -layout output."""
    result = []
    controls = []
    lines = text.splitlines()
    for li, line in enumerate(lines):
        cells = [clean(c) for c in re.split(r'\s{2,}', line.strip())]
        if len(cells) not in (4, 5):
            continue
        label, *amounts = cells
        if not all(AMOUNT.fullmatch(c) or c in ['-', '–', '—'] for c in amounts):
            continue
        vals = list(map(money, amounts)) + ([None] if len(amounts) == 3 else [])
        if NONNAME.search(label):
            controls.append({'label': label, 'amounts': vals, 'pdfPage': pn})
            continue
        if not label or label.isdigit():
            continue
        if li + 1 < len(lines):
            nxt = clean(lines[li + 1])
            if nxt and not NONNAME.search(nxt) and len(re.split(r'\s{2,}', lines[li + 1].strip())) == 1 and not nxt.isdigit() and not (',' in label and ',' in nxt):
                label += ' ' + nxt
        if ',' not in label and not ANONYMOUS.search(label) and li > 0:
            previous = clean(lines[li - 1])
            if ',' in previous and len(re.split(r'\s{2,}', lines[li - 1].strip())) == 1 and not NONNAME.search(previous):
                label = previous + ' ' + label
        result.append({'label': label, 'amounts': vals, 'pdfPage': pn})
    return result, controls


def fingerprint(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def compact_json(d):
    return json.dumps(d, ensure_ascii=False, separators=(',', ':')).encode()


def write_gzip(path, data):
    raw = compact_json(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw, mtime=0))
    return hashlib.sha256(raw).hexdigest(), fingerprint(path)


def extract_report(source):
    year = int(source['year'])
    p = CACHE / f'{year}.pdf'
    assert fingerprint(p) == source['verification']['sha256']
    assert p.stat().st_size == source['verification']['bytes']
    layout = p.with_suffix('.layout.txt')
    subprocess.run(['pdftotext', '-layout', str(p), str(layout)], check=True)
    texts = layout.read_text().split('\f')
    doc = fitz.open(p)
    assert len(doc) == source['verification']['pdfPages']
    assert f'{year} Financial Information Act' in clean(doc[0].get_text())
    cohorts = []
    for idx, ((slug, employer), (first, last)) in enumerate(zip(ENTITIES, RANGES[year])):
        native, poppler, controls = [], [], []
        for pn in range(first, last + 1):
            text = clean(doc[pn - 1].get_text())
            assert 'Schedule of Remuneration and Expenses' in text
            assert employer in text
            assert f'For the year ended December 31, {year}' in text
            nr, nc = native_rows(doc[pn - 1], pn)
            pr, pc = poppler_rows(texts[pn - 1], pn)
            assert [(v['amounts'], v['pdfPage']) for v in nc] == [(v['amounts'], v['pdfPage']) for v in pc], (year, pn, 'printed control reader mismatch', nc, pc)
            native.extend(nr)
            poppler.extend(pr)
            controls.extend(nc)
        comparable = lambda rows: [(r['label'], r['amounts'], r['pdfPage']) for r in rows]
        n, pop = comparable(native), comparable(poppler)
        if n != pop:
            print('DISAGREE', year, slug, 'native', len(n), 'poppler', len(pop))
            nc, pc = Counter(map(repr, n)), Counter(map(repr, pop))
            print(' native only', list((nc - pc).items())[:20])
            print(' poppler only', list((pc - nc).items())[:20])
        assert n == pop, (year, slug, 'independent reader mismatch')
        assert len(native) == EXPECTED_COUNTS[year][idx], (year, slug, 'row census mismatch')
        assert all(r['amounts'][2] > 75000 for r in native), (year, slug, 'threshold mismatch')
        sums = [sum(r['amounts'][i] or 0 for r in native) for i in range(4)]
        over = [c for c in controls if 'over $75,000' in c['label']]
        assert len(over) == 1
        residuals = [s - c for s, c in zip(sums, over[0]['amounts'])]
        assert residuals == RESIDUALS.get((year, idx), [0, 0, 0, 0]), (year, slug, residuals)
        print(year, slug, len(native), 'named', sum(name_value(r['label']) is not None for r in native), 'sums', sums, 'controls', [(c['label'], c['amounts']) for c in controls])
        cohorts.append({'slug':slug, 'employer':employer, 'rows':native, 'controls':controls, 'readerAgreement':n==pop, 'sums':sums, 'residuals':residuals, 'index':idx, 'schedulePages':list(range(first,last+1))})
    return cohorts


def publish_report(source, cohorts):
    year = int(source['year'])
    accepted, held, decisions, summaries = [], [], [], []
    for c in cohorts:
        slug, idx, employee_rows = c['slug'], c['index'], c['rows']
        source_id = f'follow-through-translink-{year}-{slug}-employees'
        stem = f'{slug}-{year}'
        is_held = (year, idx) in HELD
        normalized = [[slug, name_value(r['label']), None, r['amounts'][2], r['amounts'][3], r['pdfPage']] for r in employee_rows]
        row_path = ('held/' if is_held else '') + stem + '.json.gzip'
        normalized_sha, data_sha = write_gzip(OUT / row_path, normalized)
        named = sum(row[1] is not None for row in normalized)
        component_errors = [
            {'row': i + 1, 'pdfPage': r['pdfPage'], 'sourceLabel': r['label'],
             'salaryPlusOtherMinusRemuneration': r['amounts'][0] + r['amounts'][1] - r['amounts'][2]}
            for i, r in enumerate(employee_rows)
            if r['amounts'][0] is not None and r['amounts'][1] is not None and r['amounts'][0] + r['amounts'][1] != r['amounts'][2]
        ]
        printed = next(v for v in c['controls'] if 'over $75,000' in v['label'])
        fields = ['salaryPayments', 'other', 'remuneration', 'expenses']
        checked_controls = [
            {'field': f, 'rowSum': c['sums'][i], 'printedControl': printed['amounts'][i], 'residual': c['residuals'][i],
             'basis': 'Complete individually disclosed employee rows over $75,000; blank/dash cells omitted from numeric sums but retained as null'}
            for i, f in enumerate(fields)
        ]
        evidence_path = f'evidence/{stem}.json.gzip'
        evidence = {
            'sourceId': source_id, 'sourceUrl': source['sourceUrl'], 'sourceSha256': source['verification']['sha256'],
            'year': str(year), 'employerSlug': slug, 'rowCount': len(normalized), 'namedRows': named,
            'withheldNameRows': len(normalized) - named, 'rowEvidenceSchema': ['label', 'amounts', 'rawAmounts', 'pdfPage', 'y'],
            'amountSchema': fields, 'rows': employee_rows, 'printedRows': c['controls'],
            'controls': checked_controls, 'rowComponentDifferences': component_errors,
            'rowsWithUnknownComponent': [i + 1 for i, r in enumerate(employee_rows) if None in r['amounts'][:2]],
            'independentReader': 'Poppler pdftotext -layout', 'everyRowAllFourFieldsAndPageAgree': True,
            'candidateOnly': is_held, 'normalizedSha256': normalized_sha, 'dataSha256': data_sha,
        }
        write_gzip(OUT / evidence_path, evidence)
        warning = BASE_WARNING
        if any(c['residuals']):
            warning += ' Displayed row sums minus printed employee subtotals are: ' + ', '.join(f'{f} {v:+d} CAD' for f, v in zip(fields, c['residuals'])) + '. Literal source amounts are retained; no balancing amounts are created.'
        notes = [
            'Complete individual employee schedule over $75,000, including individually disclosed withheld-name payments. Employer-wide below-threshold totals, board directors, Mayors’ Council, executive-component tables, suppliers and employer EI/CPP aggregates are excluded.',
            'The imported remuneration field is Total Remuneration. Salary Payments and Other are retained in row evidence; they are not substituted for the published total. No pension or executive-component amounts are added.',
            'The reporting headers explicitly say year ended December 31. Calendar years are preserved and are never relabelled as compiled fiscal editions.',
            'Published names and spelling are retained, with line wraps joined by a space. Anonymous staff labels identify individual source occurrences, not names; name remains null. No dedicated position column is published, so position remains null.',
            'Each legal report entity remains separate. The parent task verified the primary employer bridge from TransLink Security Management Ltd. to the existing transit-police employer, using TSML Policy 029 definitions (physical page 2) and the TransLink 2025 accountability organization chart. Security employee schedules use transit-police; existing metro-vancouver-transit-police compiled observations remain distinct. No compiled rows are reassigned or deleted.',
            'Compiled translink observations may contain mixed subsidiary attribution. These official entity-specific cohorts do not establish a complete compiled-group equivalence; no compiled attribution is moved automatically.',
            'PyMuPDF positioned-word extraction and independent Poppler layout extraction agree for every employee label, all four monetary cells and physical page. Wrapped names and uncertain blank/dash/negative columns were checked against rendered source pixels.',
        ]
        s = {
            'id': source_id, 'employerSlug': slug,
            'employerName': 'Transit Police (TransLink Security Management Ltd.)' if idx == 3 else c['employer'],
            'reportedEmployerName': c['employer'], 'sector': 'Municipal police' if idx == 3 else 'Crown corporations',
            'year': str(year), 'slug': str(year), 'periodType': 'calendar', 'periodStart': f'{year}-01-01', 'periodEnd': f'{year}-12-31',
            'title': f'{c["employer"]} {year}: individual employee remuneration and expenses',
            'sourceUrl': source['sourceUrl'], 'sourceIndexUrl': source['indexUrl'], 'sha256': source['verification']['sha256'],
            'pdfBytes': source['verification']['bytes'], 'pdfPages': source['verification']['pdfPages'],
            'file': row_path, 'dataSha256': data_sha, 'normalizedSha256': normalized_sha, 'provenanceFile': evidence_path,
            'category': 'employee-remuneration', 'scope': 'individual-employees-over-threshold',
            'threshold': 75000, 'thresholdComparison': '>', 'currency': 'CAD', 'amountUnit': 'dollars', 'amountPrecision': 'whole-dollars',
            'status': 'held-for-review' if is_held else 'verified', 'sourceKind': 'official', 'verifiedOn': '2026-11-02',
            'completeEmployeeSchedule': True, 'nameDisclosure': 'published-names-and-individually-withheld-names', 'positionDisclosure': 'not-published',
            'rowCount': len(normalized), 'namedRowCount': named, 'anonymousRowCount': len(normalized) - named,
            'totalRemuneration': c['sums'][2], 'totalExpenses': c['sums'][3], 'pages': sorted({r['pdfPage'] for r in employee_rows}),
            'publicWarning': warning, 'notes': notes,
            'validation': {'originalFingerprintVerified': True, 'documentPeriodChecked': True,
                           'sourcePixelsReviewed': True,
                           'physicalPagesVisuallyReviewed': sorted(set([x['pdfPage'] for x in c['controls']] + [p for p in WRAP_REVIEW_PAGES.get(year, []) if p in c['schedulePages']])),
                           'independentReaders': ['PyMuPDF positioned words', 'Poppler pdftotext -layout'],
                           'everyRowFieldAgreement': True, 'rowsIndependentlyChecked': len(normalized),
                           'printedControls': checked_controls, 'rowComponentDifferenceCount': len(component_errors),
                           'evidenceFile': evidence_path},
        }
        if is_held:
            s['candidateFile'] = s.pop('file')
            s['candidateRowCount'] = s.pop('rowCount')
            s['reason'], s['nextAction'] = HOLD_REASON, HOLD_NEXT
            held.append(s)
        else:
            accepted.append(s)
        decision = {'employerSlug': slug, 'sourceId': source_id, 'status': 'held-for-review' if is_held else 'accepted',
                    'rows': 0 if is_held else len(normalized), 'candidateRows': len(normalized), 'namedRows': named,
                    'anonymousRows': len(normalized) - named, 'controls': checked_controls,
                    'reason': HOLD_REASON if is_held else 'Complete source cohort independently extracted and checked against published controls; any small arithmetic residual is explicitly warned.',
                    'nextAction': HOLD_NEXT if is_held else 'Include this distinct employer/calendar-period cohort in the shared release.'}
        decisions.append(decision)
        summaries.append({'employerSlug': slug, 'status': decision['status'], 'pages': c['schedulePages'],
                          'rows': len(normalized), 'namedRows': named, 'anonymousRows': len(normalized) - named,
                          'controls': checked_controls, 'printedRows': c['controls'], 'rowComponentDifferenceCount': len(component_errors),
                          'rowEvidence': evidence_path, 'candidateFile': row_path})
    report = {'id': source['id'], 'year': str(year), 'sourceUrl': source['sourceUrl'], 'sourceIndexUrl': source['indexUrl'],
              'sha256': source['verification']['sha256'], 'pdfBytes': source['verification']['bytes'],
              'pdfPages': source['verification']['pdfPages'], 'actualPeriodStart': f'{year}-01-01', 'actualPeriodEnd': f'{year}-12-31',
              'documentPeriodEvidence': 'Cover reporting year and every employee table heading: For the year ended December 31, YEAR',
              'definitionPage': 11 if year in [2020, 2025] else 10,
              'definition': {'remuneration': 'Salary, wages, overtime, retroactive pay, vacation, banked time payout and other taxable benefits paid during the year; excludes non-taxable benefits and amounts payable under severance agreements. Report p.4 also excludes pension benefits.',
                             'expenses': 'Vehicle operating, travel, memberships, tuition, relocation, registration fees and similar amounts paid to employees or third parties on their behalf, not included in remuneration.'},
              'cohorts': summaries}
    (OUT / 'reports').mkdir(parents=True, exist_ok=True)
    (OUT / 'reports' / f'{year}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    disposition = {'id': source['id'], 'year': str(year), 'sourceUrl': source['sourceUrl'], 'sha256': source['verification']['sha256'],
                   'status': 'partially-accepted' if held else 'accepted', 'acceptedSources': len(accepted),
                   'acceptedRows': sum(s['rowCount'] for s in accepted), 'cohorts': decisions,
                   'excludedSections': ['board-directors', 'mayors-council', 'executive-component-compensation', 'suppliers', 'below-threshold-employee-aggregates', 'employer-EI-CPP-aggregates']}
    return accepted, held, disposition


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--years', nargs='*', type=int, default=list(RANGES))
    parser.add_argument('--write', action='store_true', help='Write a complete deterministic collection; requires all six years')
    args = parser.parse_args()
    if args.write:
        assert sorted(args.years) == sorted(RANGES), 'Only complete six-year collection writes are allowed'
        OUT.mkdir(parents=True, exist_ok=True)
    sources, held, dispositions = [], [], []
    for source in sorted(json.loads(INPUT.read_text()), key=lambda s: s['year']):
        if source['employerSlug'] == 'translink' and int(source['year']) in args.years:
            cohorts = extract_report(source)
            if args.write:
                a, h, d = publish_report(source, cohorts)
                sources.extend(a)
                held.extend(h)
                dispositions.append(d)
    if args.write:
        (OUT / 'sources.json').write_text(json.dumps({'version': 1, 'rowSchema': ROW_SCHEMA, 'sources': sources, 'unparsedSources': held}, ensure_ascii=False, indent=2) + '\n')
        (OUT / 'dispositions.json').write_text(json.dumps({'version': 1, 'reports': dispositions}, ensure_ascii=False, indent=2) + '\n')
        print('WROTE', len(sources), 'accepted sources', sum(s['rowCount'] for s in sources), 'accepted rows;', len(held), 'held cohorts')


if __name__ == '__main__':
    main()
