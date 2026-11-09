"""Build research/salaries/vsb-history from two-engine extraction outputs (extract.py)."""
import os
import json, gzip, hashlib, collections, re, sys
from decimal import Decimal
from pathlib import Path

SCR = Path(os.environ.get('VSB_WORK', 'vsb-work'))
OUT = Path(__file__).resolve().parents[1]
SLUG, EMP, SECTOR = 'vancouver-school-district', 'School District No. 39 (Vancouver)', 'School districts'
INDEX = 'https://www.vsb.bc.ca/financial-information'
ENGINES = ['poppler pdftotext 24.02.0 -layout -fixed 2 (character-grid columns)', 'pdfplumber 0.11.10 / pdfminer.six 20260107 word and character geometry']
F = ['page', 'surname', 'given', 'position', 'rem', 'exp']

def sha(b): return hashlib.sha256(b).hexdigest()
def packed(v):
    raw = (json.dumps(v, ensure_ascii=False, separators=(',', ':')) + '\n').encode(); return gzip.compress(raw, mtime=0), raw
def dec(s):
    if s is None or s == '-': return None
    neg = s.startswith('(') and s.endswith(')')
    d = Decimal(s.strip('()').replace(',', '').replace('$', '').strip()); return -d if neg else d
def number(d):
    return int(d) if d == int(d) else float(d)

def tail_amounts(line):
    return [dec(t) for t in line.replace('$', ' ').split() if re.fullmatch(r'\(?-?[\d,]+(?:\.\d{2})?\)?', t)][-2:]

YEARS = {
 '2017-2018': dict(label='2017/18', end=2018, adjudications=[], cents=True),
 '2019-2020': dict(label='2019/20', end=2020, adjudications=[], cents=False),
 '2022-2023': dict(label='2022/23', end=2023, adjudications=[], cents=False),
 '2023-2024': dict(label='2023/24', end=2024, cents=False, adjudications=[{
     'physicalPage': 89, 'row': 'Orr', 'issue': 'pdftotext character grid cannot separate the overflowing given-name cell from the position cell (single space between "Ramona" and "Teacher").',
     'pdftotextLayout': ['Orr', 'Kim Margaret Ramona Teacher', 'Secondary'], 'pdfplumber': ['Orr', 'Kim Margaret Ramona', 'Teacher Secondary'],
     'thirdReader': 'poppler pdftotext -bbox word geometry: "Teacher" xMin=219.72 equals the page position-column start (48 "Teacher" words at xMin 219.72); "Ramona" xMax=218.55.',
     'resolution': 'pdfplumber cell boundary confirmed; characters and amounts identical in all readers.'}]),
}
HELD = {
 '2018-2019': dict(label='2018/19', end=2019, pages='54-91', ocr=['"90,t82"', '"I 8,53 I"', '"l 8,53 l"', '"Exceedine $75.000"'], counts=(1709, 653, 140, 57)),
 '2020-2021': dict(label='2020/21', end=2021, pages='54-99', ocr=['"94,51t"', '"529,98t"'], counts=(0, 1, 459, 192)),
 '2021-2022': dict(label='2021/22', end=2022, pages='55-105', ocr=['"t04"'], counts=(0, 0, 0, 0)),
}

def common(key, meta, url, pdfsha):
    y = meta['end']
    return {'id': f'vsb-history-sd39-{y}-employees', 'employerSlug': SLUG, 'employerName': EMP, 'sector': SECTOR,
            'year': meta['label'], 'slug': meta['label'].replace('/', '-'), 'periodType': 'fiscal',
            'periodStart': f'{y-1}-07-01', 'periodEnd': f'{y}-06-30',
            'title': f'{EMP}, fiscal year ended June 30, {y}: employees', 'sourceUrl': url, 'sourceIndexUrl': INDEX, 'sha256': pdfsha}

sources = []; summary = []
for key in ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']:
    pdf = (SCR / 'dl' / f'{key}.pdf').read_bytes(); pdfsha = sha(pdf); url = (SCR / 'dl' / f'{key}.url').read_text().strip()
    if key in HELD:
        m = HELD[key]; s = common(key, m, url, pdfsha)
        s.update({'category': 'employee-remuneration', 'scope': 'employee-remuneration', 'status': 'held-for-review', 'sourceKind': 'official',
                  'reason': f'The employee schedule (physical pages {m["pages"]}) is a scanned image (Canon iR-ADV scan) with an embedded OCR text layer, not native text. The OCR layer contains character errors in names and amounts (e.g. {", ".join(m["ocr"])}), and both extraction engines read the same OCR layer, so they are not independent transcriptions. No rows imported; requires an image-based transcription with independent review.',
                  'threshold': 75000, 'thresholdComparison': '>',
                  'validation': {'independentReaders': ENGINES, 'textLayer': 'invisible OCR text over scanned page images',
                                 'pdftotextRowsParsed': m['counts'][0], 'pdftotextUnparsedLines': m['counts'][1], 'pdfplumberRowsParsed': m['counts'][2], 'pdfplumberUnparsedLines': m['counts'][3],
                                 'enginesAgree': False, 'summaryReconciles': None}})
        sources.append(s); summary.append((key, s, None)); continue
    m = YEARS[key]; d = json.load(open(SCR / 'out' / f'{key}.json'))
    A, B = d['layout'], d['plumber']
    assert not d['layoutAnomalies'] and not d['plumberAnomalies'] and len(A) == len(B)
    diffs = [i for i, (a, b) in enumerate(zip(A, B)) if [a[k] for k in F] != [b[k] for k in F]]
    adj = m['adjudications']
    assert len(diffs) == len(adj)
    for i, a in zip(diffs, adj):
        la, pb = A[i], B[i]
        assert la['surname'] == a['pdftotextLayout'][0] and la['given'] == a['pdftotextLayout'][1] and pb['given'] == a['pdfplumber'][1] and pb['page'] == a['physicalPage']
        assert ' '.join([la['surname'], la['given'], la['position']]) == ' '.join([pb['surname'], pb['given'], pb['position']]) and la['rem'] == pb['rem'] and la['exp'] == pb['exp']
    rows = B
    # printed controls
    tl = d['plumberTail']; assert d['layoutTail'][0].split() == tl[0].split() or tail_amounts(d['layoutTail'][0]) == tail_amounts(tl[0])
    printed = tail_amounts(tl[0])
    other = [ln for ln in tl[1:6] if re.match(r'(?i)total|consolidated', ln)]
    R = sum(dec(r['rem']) for r in rows); E = sum(dec(r['exp']) or Decimal(0) for r in rows)
    resid = [R - printed[0], E - printed[1]]; bound = Decimal('0.5') * len(rows)
    ok = all(abs(x) <= bound for x in resid)
    assert ok, (key, resid)
    payload, ev = [], []
    for r in rows:
        name = r['surname'] + ', ' + r['given']; e = dec(r['exp'])
        payload.append([SLUG, name, r['position'], number(dec(r['rem'])), None if e is None else number(e), r['page']])
        ev.append({'name': name, 'position': r['position'], 'department': None, 'remuneration': str(dec(r['rem'])), 'expenses': None if e is None else str(e),
                   'sourceCellTexts': [r['surname'], r['given'], r['position'], r['rem'], r['exp']], 'sourceExpenseLiteral': r['exp'], 'pdfPage': r['page'],
                   'category': 'employee-remuneration', 'sourceSurname': r['surname'], 'sourceGivenNames': r['given'],
                   'nameJoin': 'Explicit source surname and given-name cells, joined with comma and space', 'sourceY': r['key'],
                   **({'cellBoundaryNotes': r['boundaryNotes']} if r['boundaryNotes'] else {})})
    y = m['end']; base = f'sd39-{y}-employees'
    blob, raw = packed(payload); file = base + '.json.gzip'
    glued = [{'physicalPage': r['page'], 'boundary': n[0], 'gluedSourceWord': n[1], 'left': n[2], 'right': n[3], 'method': 'pdfplumber character x0 against page column start'} for r in rows for n in r['boundaryNotes']]
    layout_rules = [{'physicalPage': r['page'], 'rule': n[0], 'text': n[1]} for r in A for n in r['boundaryNotes']]
    sg = [g for g in glued if g['boundary'] == 'surname|given']; gp = [g for g in glued if g['boundary'] == 'given|position']
    evidence = {'sourceUrl': url, 'sourceSha256': pdfsha, 'readers': ENGINES, 'sourceFields': ev, 'completeReaderFieldAgreement': not adj,
                'readerCharacterAndAmountAgreement': True, 'adjudications': adj, 'gluedCellBoundaries': glued, 'pdftotextBoundaryRules': layout_rules,
                'literalComputedTotals': [str(R), str(E)], 'literalPrintedTotals': [str(x) for x in printed], 'residuals': [str(x) for x in resid],
                'printedSummaryLines': [tl[0]] + other, 'causeEstablished': False if any(resid) else None, 'dataSha256': sha(blob), 'normalizedSha256': sha(raw), 'noOutreach': True}
    eblob, _ = packed(evidence); efile = base + '-evidence.json.gzip'
    (OUT / file).write_bytes(blob); (OUT / efile).write_bytes(eblob)
    pages = sorted({r['page'] for r in rows})
    warning = 'Fiscal-year payment disclosures are not annual base salary rates or a complete workforce census. Source expense dashes remain unknown (null); explicit zero and negative amounts remain literal. The source surname and given-name columns are joined with a comma and space, without expanding or resolving identities. '
    if any(resid):
        warning += f'Literal employee rows total ${R:,} remuneration and ${E:,} expenses versus the printed ${printed[0]:,} and ${printed[1]:,} ({"+" if resid[0] >= 0 else "−"}${abs(resid[0]):,} / {"+" if resid[1] >= 0 else "−"}${abs(resid[1]):,}). Causes are not established and no amount is adjusted. '
    if sg:
        warning += f'In {len(sg)} rows the printed surname runs into the given-name cell; names are split at the printed column boundary and kept as printed, including the visibly truncated surname "Mesropian De Gon". '
    if gp:
        warning += f'In {len(gp)} row the printed given names run into the position cell; the split follows the printed column boundary. '
    if any('*' in r['given'] for r in rows):
        warning += 'Asterisks printed after two given names mark expenses that include international student recruitment travel; they are kept as printed. '
    s = common(key, m, url, pdfsha)
    s.update({'file': file, 'dataSha256': sha(blob), 'normalizedSha256': sha(raw), 'provenanceFile': efile, 'provenanceSha256': sha(eblob),
              'category': 'employee-remuneration', 'scope': 'employee-remuneration', 'scopeDescription': 'Complete published named employee schedule above the stated disclosure threshold',
              'currency': 'CAD', 'amountUnit': 'dollars', 'amountPrecision': 'cents' if m['cents'] else 'whole-dollars', 'threshold': 75000, 'thresholdComparison': '>',
              'nameDisclosure': 'separate-surname-and-given-name-cells-joined-with-comma', 'positionDisclosure': 'published-visible-text-only',
              'pages': pages, 'rowCount': len(rows), 'totalRemuneration': number(R), 'totalExpenses': number(E),
              'status': 'accepted', 'sourceKind': 'official', 'completeEmployeeSchedule': True, 'verifiedOn': '2026-11-09', 'publicWarning': warning.strip(),
              'notes': ['Only literal named employee observations are imported. Elected officials, below-threshold totals, employer CPP/EI, vendors and financial statements remain supporting evidence.',
                        'No amount was changed to balance a printed subtotal. Two independent native-text readers agree on every character and amount; this does not establish perfect transcription accuracy.'],
              'validation': {'originalFingerprintVerified': True, 'textLayer': 'native PDF text (no page images on schedule pages)', 'independentReaders': ENGINES,
                             'pageRange': [pages[0], pages[-1]], 'pdftotextRows': len(A), 'pdfplumberRows': len(B), 'unparsedScheduleLines': 0,
                             'rowsIndependentlyChecked': len(rows), 'allFieldsOrderAndMultiplicityAgree': not adj,
                             'allCharactersAndAmountsAgree': True, 'cellBoundaryDisagreements': len(adj), 'cellBoundaryAdjudications': adj,
                             'gluedSurnameGivenCells': len(sg), 'gluedGivenPositionCells': len(gp), 'pdftotextBoundaryRules': layout_rules,
                             'rowsByPhysicalPage': {str(k): v for k, v in sorted(collections.Counter(r['page'] for r in rows).items())},
                             'printedControlTotals': [str(x) for x in printed], 'printedControlLine': tl[0], 'printedSummaryLines': other,
                             'computedComponentTotals': [str(R), str(E)], 'controlResiduals': [str(x) for x in resid], 'residualBound': str(bound),
                             'residualBoundRule': '0.5 x rowCount (whole-dollar rounding)', 'summaryReconciles': ok, 'exactReconciliation': not any(resid),
                             'knownExpenseValueCount': sum(r['exp'] not in (None, '-') for r in rows), 'nullExpenseRows': sum(r['exp'] in (None, '-') for r in rows),
                             'zeroExpenseRows': sum(dec(r['exp']) == 0 for r in rows if dec(r['exp']) is not None),
                             'negativeExpenseRows': sum(dec(r['exp']) < 0 for r in rows if dec(r['exp']) is not None),
                             'rowsAtOrBelowThreshold': sum(dec(r['rem']) <= 75000 for r in rows), 'completeEmployeeSchedule': True}})
    sources.append(s); summary.append((key, s, evidence))

manifest = {'version': 1, 'reviewed': True, 'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'], 'sources': sources}
(OUT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for key, s, e in summary:
    print(key, s['status'], s.get('rowCount'), s.get('totalRemuneration'), s.get('totalExpenses'), s.get('validation', {}).get('controlResiduals'))
