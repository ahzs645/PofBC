#!/usr/bin/env python3
"""Import the employee schedules recovered by the 12 Nov 2026 collection-priorities register.

research/audits/evidence-reconciliation-2026-11-12/collection-priorities.json records each
original's URL, SHA-256, schedule pages and printed controls. This importer:

* downloads (or reads from --cache) each original and refuses it unless its SHA-256 equals
  the register fingerprint;
* native-text schedules (UNBC 2021/22, SD57 2023/24): reads every named row twice, with
  Poppler `pdftotext -layout` lines and with pdfplumber word geometry (header-anchored
  right-aligned amount columns, modal left edge of the position column), and requires
  exact agreement of page, name, position and both literal amount cells;
* the scanned Fort St. James 2024 page: OCRs a 300 dpi Poppler render with Tesseract and
  requires exact agreement with a visual transcription of the same render, plus each
  row's printed Total column equal to remuneration + expenses;
* reconciles named remuneration and expenses to the printed controls exactly, and writes
  nothing if any check fails.

Expense cells keep their literal form in the evidence file ('0.00', '-', blank, '(23.46)');
in the normalized rows a printed dash or blank is null (repository convention) and a printed
zero stays 0. Requires Poppler, pdfplumber and (for Fort St. James) Tesseract and Pillow.
The salary build reads only the checked-in outputs and needs none of these tools.

Usage: python3 scripts/import_collection_priorities_2026_11_12.py --cache DIR [--sources unbc,sd57,fsj]
"""
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / 'research/audits/evidence-reconciliation-2026-11-12/collection-priorities.json'
OUT = ROOT / 'research/salaries/collection-priorities-2026-11-12'
VERIFIED_ON = '2026-11-13'
MONEY = r'\(?-?[\d,]+\.\d{2}\)?'

# Fort St. James page 8, typed from the 300 dpi render ('' = blank cell, '-' = printed dash).
FSJ_VISUAL = [
    ('Bihori, A', 'Corporate Officer', '99,251.50', '12,184.22', '111,435.72'),
    ('Braun, D', 'Asst Fire Chief', '95,237.72', '1,137.21', '96,374.93'),
    ('Clarke, S', 'Chief Financial Officer', '90,756.64', '9,764.93', '100,521.57'),
    ('Claughton, R', 'Equipment Operator', '90,003.98', '', '90,003.98'),
    ('Constantine, C', 'Human Resources', '68,927.28', '6,437.92', '75,365.20'),
    ('Croquet, A', 'Equipment Operator', '97,313.23', '', '97,313.23'),
    ('Crowley, V', 'Library Director', '80,772.50', '', '80,772.50'),
    ('Greenaway, C', 'Mechanic', '103,217.57', '70.00', '103,287.57'),
    ('Hassman, M', 'Asset Management', '104,476.02', '4,059.92', '108,535.94'),
    ('Kosmick, P', 'Public Works Foreman', '116,128.51', '3,600.89', '119,729.40'),
    ('Kossey, V', 'Fire /Bylaw officer', '75,188.82', '677.38', '75,866.20'),
    ('Legebokoff, R', 'Equipment Operator', '88,699.62', '4,058.00', '92,757.62'),
    ('Lowther, D', 'Director of Public Works', '128,296.45', '310.00', '128,606.45'),
    ('McVey, R', 'Fire Chief', '99,373.52', '886.94', '100,260.46'),
    ('Phillips, C', 'Arena Supervisor', '90,429.07', '-', '90,429.07'),
    ('Sanghera, P', 'Labourer', '83,615.39', '167.30', '83,782.69'),
    ('Schlamp, N', 'Equipment Operator', '98,732.85', '3,943.30', '102,676.15'),
    ('Spooner, T', 'Equipment Operator', '88,623.51', '23.00', '88,646.51'),
    ('Tritt, D', 'Sanitation Operator', '87,367.86', '', '87,367.86'),
    ('Willick, R', 'Chief Administrative Officer', '153,549.76', '7,724.10', '161,273.86'),
]
# Printed page-8 controls, read visually (the OCR of the shaded totals row is unreliable) and
# checked arithmetically: named rows, and named + below-threshold + council = grand totals.
FSJ_PRINTED = {'namedRemuneration': '1,939,961.80', 'namedExpenses': '55,045.11', 'namedTotal': '1,995,006.91',
               'belowThresholdRemuneration': '738,381.47', 'belowThresholdExpenses': '15,561.26', 'belowThresholdTotal': '753,942.73',
               'councilRemuneration': '82,530.40', 'councilExpenses': '37,898.47', 'councilTotal': '120,428.87',
               'grandRemuneration': '2,760,873.67', 'grandExpenses': '108,504.84', 'grandTotal': '2,869,378.51'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def amount(text):
    """Literal printed amount to Decimal; '(x)' is negative. Dash/blank are not amounts."""
    if text in ('', '-'):
        return None
    negative = text.startswith('(') and text.endswith(')')
    value = Decimal(text.strip('()').replace(',', ''))
    return -value if negative else value


def cell_kind(text):
    value = amount(text)
    return 'blank' if text == '' else 'dash' if text == '-' else 'zero' if value == 0 else 'negative' if value < 0 else 'value'


def require(condition, message):
    if not condition:
        raise SystemExit(f'Refusing to write: {message}')


def original(lead, cache):
    path = Path(cache) / f"{lead['id']}.pdf"
    if not path.exists():
        request = urllib.request.Request(lead['source_url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=120) as response:
            path.write_bytes(response.read())
    data = path.read_bytes()
    require(sha(data) == lead['binary']['sha256'], f"{lead['id']}: SHA-256 {sha(data)} differs from the register fingerprint")
    require(len(data) == lead['binary']['bytes'], f"{lead['id']}: byte length differs from the register")
    return path, data


def layout_text(pdf, page):
    return subprocess.run(['pdftotext', '-layout', '-f', str(page), '-l', str(page), str(pdf), '-'], capture_output=True, text=True, check=True).stdout


def reader_poppler(pdf, first, last, start, stop):
    """Reader A: Poppler layout lines and a regular expression."""
    line_re = re.compile(rf'^(?P<name>\S.*?)(?:\s{{2,}}(?P<pos>\S.*?))?\s{{2,}}(?P<rem>{MONEY})(?:\s+(?P<exp>{MONEY}|-))?\s*$')
    rows, skipped, started, stopped = [], [], start is None, False
    for page in range(first, last + 1):
        in_body = False
        for raw in layout_text(pdf, page).split('\n'):
            line = raw.rstrip()
            if stopped:
                break
            if re.search(r'Remuneration\s+(Total\s+)?Expense', line):
                in_body = True
                continue
            if not in_body or not line.strip():
                continue
            if not started:
                started = bool(re.search(start, line))
                continue
            if re.search(stop, line):
                stopped = True
                break
            match = line_re.match(line)
            if match:
                rows.append({'pdfPage': page, 'name': match['name'].strip(), 'position': (match['pos'] or '').strip() or None,
                             'remuneration': match['rem'], 'expenses': match['exp'] or '', 'sourceLine': line})
            else:
                skipped.append({'pdfPage': page, 'line': line.strip()})
    require(stopped, f'control line {stop!r} not found')
    return rows, skipped


def reader_geometry(pdf, first, last, start, stop):
    """Reader B: pdfplumber glyph boxes grouped into words, lines and x-defined columns."""
    money = re.compile(rf'^{MONEY}$')
    rows, started, stopped = [], start is None, False
    with pdfplumber.open(pdf) as document:
        for page in range(first, last + 1):
            if stopped:
                break
            # Painted space glyphs can overlap digits; words are rebuilt from x gaps alone.
            words = document.pages[page - 1].filter(lambda o: not (o.get('object_type') == 'char' and o.get('text') == ' ')) \
                .extract_words(x_tolerance=1.5, y_tolerance=2)
            lines = []
            for word in sorted(words, key=lambda w: (round(w['top']), w['x0'])):
                if lines and abs(lines[-1][0]['top'] - word['top']) <= 2.5:
                    lines[-1].append(word)
                else:
                    lines.append([word])
            lines = [sorted(line, key=lambda w: w['x0']) for line in lines]
            header_at = next(i for i, line in enumerate(lines) if any(w['text'] == 'Remuneration' for w in line) and any(w['text'] == 'Position' for w in line))
            rem_x1 = next(w['x1'] for w in lines[header_at] if w['text'] == 'Remuneration')
            exp_x1 = next(w['x1'] for w in lines[header_at] if re.match(r'Expenses?$', w['text']))
            data = []
            for line in lines[header_at + 1:]:
                text = ' '.join(w['text'] for w in line)
                if not started:
                    started = bool(re.search(start, text))
                    continue
                if re.search(stop, text):
                    stopped = True
                    break
                amounts = [w for w in line if (money.match(w['text']) or w['text'] == '-') and w['x1'] > rem_x1 - 80]
                if amounts:
                    data.append((line, amounts))
            starts = Counter()
            for line, amounts in data:
                text_words = [w for w in line if w not in amounts]
                for previous, current in zip(text_words, text_words[1:]):
                    if current['x0'] - previous['x1'] >= 6:
                        starts[round(current['x0'])] += 1
            position_x = starts.most_common(1)[0][0]
            for line, amounts in data:
                text_words = [w for w in line if w not in amounts]
                rem = [w['text'] for w in amounts if abs(w['x1'] - rem_x1) < abs(w['x1'] - exp_x1)]
                exp = [w['text'] for w in amounts if abs(w['x1'] - rem_x1) >= abs(w['x1'] - exp_x1)]
                require(len(rem) == 1 and len(exp) <= 1, f'page {page}: ambiguous amount columns in {[w["text"] for w in line]}')
                rows.append({'pdfPage': page, 'name': ' '.join(w['text'] for w in text_words if w['x0'] < position_x - 2),
                             'position': ' '.join(w['text'] for w in text_words if w['x0'] >= position_x - 2) or None,
                             'remuneration': rem[0], 'expenses': exp[0] if exp else '',
                             'geometry': {'top': round(line[0]['top'], 2), 'positionColumnX0': position_x}})
    return rows


def native_cohort(pdf, first, last, start, stop):
    a, skipped = reader_poppler(pdf, first, last, start, stop)
    b = reader_geometry(pdf, first, last, start, stop)
    fields = ('pdfPage', 'name', 'position', 'remuneration', 'expenses')
    require(len(a) == len(b), f'readers disagree on row count ({len(a)} vs {len(b)})')
    for x, y in zip(a, b):
        require(all(x[f] == y[f] for f in fields), f'readers disagree: {x} vs {y}')
    for x, y in zip(a, b):
        x['geometry'] = y['geometry']
    return a, skipped


def ocr_fsj(pdf, page):
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', '300', '-png', str(pdf), f'{tmp}/p'], check=True)
        image = Image.open(next(Path(tmp).glob('p*.png')))
        width, height = image.size
        require((width, height) == (2550, 3300), f'unexpected render size {image.size}')
        box = (int(width * 0.14), int(height * 0.29), int(width * 0.84), int(height * 0.645))
        image.crop(box).save(f'{tmp}/employees.png')
        table = subprocess.run(['tesseract', f'{tmp}/employees.png', '-', '--psm', '6'], capture_output=True, text=True, check=True).stdout
        whole = subprocess.run(['tesseract', next(str(p) for p in Path(tmp).glob('p*.png')), '-', '--psm', '3'], capture_output=True, text=True, check=True).stdout
        version = subprocess.run(['tesseract', '--version'], capture_output=True, text=True).stdout.splitlines()[0]
    return table, whole, box, version


def fsj_cohort(pdf, page):
    table, whole, box, version = ocr_fsj(pdf, page)
    require(re.search(r'year ended December 31, 2024', whole, re.I), 'Fort St. James page header does not establish calendar 2024')
    # Tesseract's page layout splits the shaded heading inside "Remuneration".
    require(re.search(r'Employees with Remun\s*eration and Expenses over \$75,000', whole), 'Fort St. James scope heading not found')
    ocr = []
    for line in table.splitlines():
        match = re.match(rf'^(?P<name>[A-Z][A-Za-z\'-]+, [A-Z])\s+(?P<pos>.+?)\s+(?P<rem>{MONEY})\s+(?:(?P<exp>{MONEY}|-)\s*[|}}\]]?\s*)?\$\s*(?P<tot>{MONEY})\s*$', line.strip())
        if match:
            ocr.append((match['name'], match['pos'], match['rem'], match['exp'] or '', match['tot']))
    require(ocr == FSJ_VISUAL, 'Tesseract rows differ from the visual transcription')
    for row in FSJ_VISUAL:
        require((amount(row[2]) or 0) + (amount(row[3]) or 0) == amount(row[4]), f'printed row total differs: {row}')
    p = {k: amount(v) for k, v in FSJ_PRINTED.items()}
    for part in ('Remuneration', 'Expenses', 'Total'):
        require(p[f'named{part}'] + p[f'belowThreshold{part}'] + p[f'council{part}'] == p[f'grand{part}'], f'printed {part} controls do not add up')
    require(sum(amount(r[4]) for r in FSJ_VISUAL) == p['namedTotal'], 'named Total column differs from its control')
    rows = [{'pdfPage': page, 'name': n, 'position': pos, 'remuneration': rem, 'expenses': exp, 'printedTotal': tot} for n, pos, rem, exp, tot in FSJ_VISUAL]
    return rows, {'tesseractVersion': version, 'render': 'pdftoppm 300 dpi PNG of the embedded 300 ppi page scan', 'cropBox': box,
                  'tesseractPageSegmentation': 6, 'rawOcrText': table, 'headerOcrText': whole}


def write_gzip(path, value):
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
    blob = gzip.compress(raw, mtime=0)
    path.write_bytes(blob)
    return sha(raw), sha(blob)


def reconcile(rows, printed_rem, printed_exp):
    rem = sum(amount(r['remuneration']) for r in rows)
    exp = sum(amount(r['expenses']) or 0 for r in rows)
    return {'printedControlTotals': [f'{printed_rem:.2f}', f'{printed_exp:.2f}'], 'computedComponentTotals': [f'{rem:.2f}', f'{exp:.2f}'],
            'controlResiduals': [f'{rem - printed_rem:.2f}', f'{exp - printed_exp:.2f}'], 'summaryReconciles': rem == printed_rem and exp == printed_exp}


def emit(spec, rows, extra_evidence, lead, pdf_sha):
    file = f"{spec['key']}.json.gzip"
    evidence_file = f"evidence/{spec['key']}.json.gzip"
    normalized = [[spec['slug'], r['name'], r['position'], float(amount(r['remuneration'])),
                   None if amount(r['expenses']) is None else float(amount(r['expenses'])), r['pdfPage']] for r in rows]
    normalized_sha, data_sha = write_gzip(OUT / file, normalized)
    recon = reconcile(rows, spec['printedRemuneration'], spec['printedExpenses'])
    require(recon['summaryReconciles'], f"{spec['id']}: named rows do not reconcile to the printed controls {recon}")
    kinds = Counter(cell_kind(r['expenses']) for r in rows)
    evidence = {'sourceId': spec['id'], 'registerLead': lead['id'], 'sourceUrl': lead['source_url'], 'sourceSha256': pdf_sha,
                'method': spec['method'], 'rows': rows, 'reconciliation': recon, 'expenseCellForms': dict(kinds), **extra_evidence}
    provenance_raw, provenance_sha = write_gzip(OUT / evidence_file, evidence)
    pages = sorted({r['pdfPage'] for r in rows})
    source = {
        'id': spec['id'], 'registerLead': lead['id'], 'employerSlug': spec['slug'], 'employerName': lead['employer'], 'sector': spec['sector'],
        'year': lead['reporting_period'], 'slug': lead['reporting_period'].replace('/', '-'), 'periodType': spec['periodType'],
        'periodStart': spec['periodStart'], 'periodEnd': lead['period_end'], 'title': spec['title'],
        'sourceUrl': lead['source_url'], 'sourceIndexUrl': lead['official_index_url'], 'sha256': pdf_sha,
        'file': file, 'dataSha256': data_sha, 'normalizedSha256': normalized_sha, 'provenanceFile': evidence_file, 'provenanceSha256': provenance_sha,
        'category': spec['scope'], 'scope': spec['scope'], 'scopeDescription': spec['scopeDescription'],
        'threshold': spec['threshold'], 'thresholdComparison': spec['thresholdComparison'],
        'currency': 'CAD', 'amountUnit': 'dollars', 'amountPrecision': 'cents',
        'nameDisclosure': spec['nameDisclosure'], 'positionDisclosure': 'published',
        'rowCount': len(rows), 'totalRemuneration': float(sum(amount(r['remuneration']) for r in rows)),
        'totalExpenses': float(sum(amount(r['expenses']) or 0 for r in rows)), 'pages': pages,
        **({'printedPages': spec['printedPages']} if spec.get('printedPages') else {}),
        'status': 'verified', 'sourceKind': 'official', 'completeEmployeeSchedule': spec['complete'], 'verifiedOn': VERIFIED_ON,
        'notes': spec['notes'],
        'validation': {
            'sourceFingerprintLocked': True, 'originalFingerprintVerified': True, 'registerFingerprint': lead['binary']['sha256'],
            'completeEmployeeSchedule': spec['complete'], 'independentReaders': spec['readers'], 'independentMethod': spec['method'],
            'rowsIndependentlyChecked': len(rows), 'allFieldsOrderAndMultiplicityAgree': True,
            'rowCountsByPdfPage': {str(k): v for k, v in sorted(Counter(r['pdfPage'] for r in rows).items())},
            **recon,
            'zeroExpenseRows': kinds.get('zero', 0), 'dashExpenseRows': kinds.get('dash', 0), 'blankExpenseRows': kinds.get('blank', 0),
            'nullExpenseRows': kinds.get('dash', 0) + kinds.get('blank', 0), 'negativeExpenseRows': kinds.get('negative', 0),
            'expenseCellConvention': 'Printed dash and blank expense cells are null in the normalized rows; the evidence file keeps which was printed. Printed 0.00 stays 0.',
            'reportingPeriodBasis': spec['periodBasis'],
            'approvalEvidence': lead['approval'],
            'excludedAggregates': spec['excluded'],
            'visualReview': spec['visualReview'],
        },
    }
    return source


SPECS = {
    'unbc': lambda lead: {
        'key': 'unbc-2021-22-employees', 'id': 'unbc-sofi-2021-22-employees', 'slug': 'university-of-northern-bc', 'sector': 'Universities and colleges',
        'periodType': 'fiscal', 'periodStart': '2021-04-01', 'scope': 'employee-remuneration',
        'title': 'UNBC Statement of Financial Information 2021/22: employee remuneration (Board package, 16 September 2022)',
        'scopeDescription': 'Named employees with remuneration over $75,000; board schedule and aggregate rows excluded',
        'threshold': 75000, 'thresholdComparison': '>', 'nameDisclosure': 'published-full-name', 'complete': True,
        'printedPages': list(range(16, 23)),
        'printedRemuneration': Decimal('40670870.80'), 'printedExpenses': Decimal('619232.02'),
        'readers': ['Poppler pdftotext -layout lines', 'pdfplumber glyph-box word geometry'],
        'method': 'pdftotext -layout rows compared field-for-field (page, name, position, literal remuneration and expense cells) with pdfplumber glyph-geometry columns; exact agreement required',
        'periodBasis': 'Every schedule page is headed "FOR THE YEAR ENDED MARCH 31, 2022"; the approved Board motion covers the Financial Information Act report to March 31, 2022.',
        'excluded': {'belowThresholdRemuneration': 30112798.91, 'belowThresholdExpenses': 547360.71, 'grandTotalRemuneration': 70783669.71,
                     'grandTotalExpenses': 1166592.73, 'boardSchedulePdfPage': 10},
        'visualReview': 'Rendered PDF page 17 and compared the final rows and all three printed control lines; no row values were changed.',
        'notes': [
            'The complete named employee schedule on physical PDF pages 11-17 (printed package pages 16-22 of 120) of the 16 September 2022 Board public-session package is imported with positions and original cents. The Board of Governors schedule (PDF page 10; board members receive no remuneration) and the below-threshold and grand totals are not employee rows.',
            'Named remuneration sums exactly to the printed $40,670,870.80 and expenses to the printed $619,232.02. All 80 printed 0.00 expense cells are kept as explicit zeros; the schedule prints no dash or blank expense cells.',
            'Approval: the approved minutes of the 16 September 2022 Board public session record motion 2022BP09.16.03 approving the Financial Information Act report to March 31, 2022 as presented (item 7(i)(a)).',
            'The source states that total remuneration excludes employer payments for non-taxable benefits, CPP, EI and WCB and payments under severance agreements, and that accrual accounting causes differences from the financial statements.',
        ],
    },
    'sd57': lambda lead: {
        'key': 'sd57-2023-24-employees', 'id': 'sd57-sofi-2023-24-employees', 'slug': 'school-district-57', 'sector': 'School districts',
        'periodType': 'fiscal', 'periodStart': '2023-07-01', 'scope': 'employee-remuneration',
        'title': 'School District No. 57 (Prince George), year ended June 30, 2024: employees',
        'scopeDescription': 'Complete published named employee table above the source $75,000 threshold; trustees are a separate source',
        'threshold': 75000, 'thresholdComparison': '>', 'nameDisclosure': 'published-name-as-disclosed', 'complete': True,
        'printedRemuneration': Decimal('84247372.38'), 'printedExpenses': Decimal('858990.53'),
        'readers': ['Poppler pdftotext -layout lines', 'pdfplumber glyph-box word geometry'],
        'method': 'pdftotext -layout rows compared field-for-field (page, name, position, literal remuneration and expense cells) with pdfplumber glyph-geometry columns; exact agreement required',
        'periodBasis': 'Every schedule page is headed "Year Ended June 30, 2024".',
        'excluded': {'electedOfficialsRemuneration': 157468.76, 'electedOfficialsExpenses': 50318.76, 'belowThresholdRemuneration': 51347360.47,
                     'belowThresholdExpenses': 344768.21, 'employeesAndElectedTotalRemuneration': 135752201.61, 'employeesAndElectedTotalExpenses': 1254077.50,
                     'employerCppEi': 8193624.69, 'electedOfficialsPdfPage': 56},
        'visualReview': 'Rendered PDF page 61 and confirmed the parenthesized (23.46) expense cell and dash cells; no row values were changed.',
        'notes': [
            'Official fiscal-year payment disclosure from the district Statement of Financial Information 2023/2024 (physical PDF pages 56-71). Employees begin below the "Elected Officials" section on page 56; trustees are imported separately as school-trustees, below-threshold totals and employer CPP/EI are excluded.',
            'Named remuneration sums exactly to the printed $84,247,372.38 and expenses to the printed $858,990.53. 111 printed dash expense cells are null; one printed (23.46) expense cell is kept as -23.46, as the printed control includes it.',
            'Approval: the SOFI declaration on PDF page 3 is signed by the board chair, superintendent and secretary-treasurer, dated November 14, 2024.',
            'The report (PDF page 76) explains that the remuneration schedule is cash-basis while the audited statements are accrual-basis, that some salaries are capitalized, and that taxable benefits paid to benefit suppliers appear as remuneration, so totals differ from the financial statements.',
        ],
    },
    'sd57-trustees': lambda lead: {
        'key': 'sd57-2023-24-trustees', 'id': 'sd57-sofi-2023-24-trustees', 'slug': 'school-district-57', 'sector': 'School districts',
        'periodType': 'fiscal', 'periodStart': '2023-07-01', 'scope': 'school-trustees',
        'title': 'School District No. 57 (Prince George), year ended June 30, 2024: trustees',
        'scopeDescription': 'Complete published school trustee (elected officials) remuneration table',
        'threshold': None, 'thresholdComparison': None, 'nameDisclosure': 'published-name-as-disclosed', 'complete': False,
        'printedRemuneration': Decimal('157468.76'), 'printedExpenses': Decimal('50318.76'),
        'readers': ['Poppler pdftotext -layout lines', 'pdfplumber glyph-box word geometry'],
        'method': 'pdftotext -layout rows compared field-for-field with pdfplumber glyph-geometry columns; exact agreement required',
        'periodBasis': 'Schedule page headed "Year Ended June 30, 2024".',
        'excluded': {},
        'visualReview': 'Elected-official rows checked against the printed "Total, Elected Officials" line.',
        'notes': [
            'The seven trustees listed under "Elected Officials" on PDF page 56 are a separate elected cohort, not employees, following the repository convention for school-district trustees. Their remuneration and expenses sum exactly to the printed Total, Elected Officials ($157,468.76; $50,318.76).',
        ],
    },
    'fsj': lambda lead: {
        'key': 'district-of-fort-st-james-2024-employees', 'id': 'fort-st-james-sofi-2024-employees', 'slug': 'district-of-fort-st-james', 'sector': 'Municipalities',
        'periodType': 'calendar', 'periodStart': '2024-01-01', 'scope': 'employee-remuneration',
        'title': 'District of Fort St. James 2024 Statement of Financial Information: employee remuneration',
        'scopeDescription': 'Named employees with remuneration and expenses over $75,000 (the source threshold is on combined remuneration plus expenses)',
        'threshold': None, 'thresholdComparison': None, 'nameDisclosure': 'published-surname-and-initial', 'complete': True,
        'printedRemuneration': Decimal('1939961.80'), 'printedExpenses': Decimal('55045.11'),
        'readers': ['Tesseract OCR of a 300 dpi Poppler render', 'visual transcription of the same render'],
        'method': 'Scanned page: Tesseract rows required to equal a visual transcription cell for cell; each printed row Total equals remuneration + expenses; named, below-threshold and council controls add to the printed grand totals',
        'periodBasis': 'Page 8 is headed "Schedule of Employee Remuneration and Expenses for the year ended December 31, 2024".',
        'excluded': {'councilRemuneration': 82530.40, 'councilExpenses': 37898.47, 'belowThresholdRemuneration': 738381.47, 'belowThresholdExpenses': 15561.26,
                     'grandTotalRemuneration': 2760873.67, 'grandTotalExpenses': 108504.84, 'employerCpp': 117031.89, 'employerEi': 45437.08},
        'visualReview': 'Every row, the dash and blank expense cells and the printed totals were read from 300 dpi crops of page 8.',
        'notes': [
            'The scanned page 8 schedule "Employees with Remuneration and Expenses over $75,000" is imported in full: 20 named rows with surname and initial, position, remuneration and expenses. Council remuneration and the "All under $75,000" aggregate on the same page are not employee rows.',
            'The source threshold is on remuneration plus expenses. Constantine, C (Human Resources) is listed with remuneration $68,927.28 and expenses $6,437.92 (printed total $75,365.20); the row is preserved as published, not filtered for remuneration below $75,000, and expenses are not merged into pay.',
            'Named remuneration sums exactly to the printed $1,939,961.80 and expenses to the printed $55,045.11. Four blank expense cells and one printed dash are null; the evidence file records which.',
            'Approval: the statement approving the included statements and schedules (PDF page 12) is signed by the CFO and the mayor, dated June 10, 2025. The page notes that remuneration comes from T4 reporting and expenses are departmentalized, so figures differ from the financial statements.',
        ],
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', required=True, help='directory for the original PDFs (outside the repository)')
    parser.add_argument('--sources', default='unbc,sd57,fsj')
    args = parser.parse_args()
    leads = {lead['id']: lead for lead in json.loads(REGISTER.read_text())['leads']}
    (OUT / 'evidence').mkdir(parents=True, exist_ok=True)
    sources = []
    for key in args.sources.split(','):
        if key == 'unbc':
            lead = leads['unbc-sofi-2021-22-approval-follow-through']
            pdf, data = original(lead, args.cache)
            for page in range(11, 18):
                require('FOR THE YEAR ENDED MARCH 31, 2022' in layout_text(pdf, page), f'UNBC page {page} period header')
            rows, skipped = native_cohort(pdf, 11, 17, None, r'^\s*Total remuneration >')
            require(all(re.fullmatch(r'(Return to agenda page 1|Page \d+ of 120)', s['line']) for s in skipped), f'UNBC unparsed lines {skipped}')
            sources.append(emit(SPECS['unbc'](lead), rows, {'skippedLines': skipped}, lead, sha(data)))
        elif key == 'sd57':
            lead = leads['sd57-sofi-2023-24']
            pdf, data = original(lead, args.cache)
            for page in range(56, 72):
                require('Year Ended June 30, 2024' in layout_text(pdf, page), f'SD57 page {page} period header')
            trustees, skipped_t = native_cohort(pdf, 56, 56, r'^\s*Elected Officials:', r'^\s*Total, Elected Officials')
            rows, skipped = native_cohort(pdf, 56, 71, r'Employees with Remuneration Exceeding \$75,000:', r'^\s*Total for Employees with Remuneration Exceeding')
            require(not skipped and not skipped_t, f'SD57 unparsed lines {skipped + skipped_t}')
            require(not {r['name'] for r in rows} & {r['name'] for r in trustees}, 'trustee rows leaked into the employee cohort')
            sources.append(emit(SPECS['sd57'](lead), rows, {'skippedLines': skipped}, lead, sha(data)))
            sources.append(emit(SPECS['sd57-trustees'](lead), trustees, {'skippedLines': skipped_t}, lead, sha(data)))
        elif key == 'fsj':
            lead = leads['fort-st-james-sofi-2024']
            pdf, data = original(lead, args.cache)
            rows, ocr = fsj_cohort(pdf, 8)
            sources.append(emit(SPECS['fsj'](lead), rows, {'ocr': ocr, 'printedControls': FSJ_PRINTED}, lead, sha(data)))
        else:
            raise SystemExit(f'unknown source {key}')
    manifest = {
        'version': 1,
        'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'],
        'register': str(REGISTER.relative_to(ROOT)),
        'importer': 'scripts/import_collection_priorities_2026_11_12.py',
        'coverageNotes': ['Employee schedules accepted from the 12 November 2026 collection-priorities register. Each original matches the register SHA-256; every row was read by two independent methods and the named rows reconcile exactly to the printed controls.'],
        'sources': sources,
    }
    (OUT / 'sources.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    for source in sources:
        print(source['id'], source['rowCount'], source['validation']['computedComponentTotals'], source['validation']['controlResiduals'])


if __name__ == '__main__':
    main()
