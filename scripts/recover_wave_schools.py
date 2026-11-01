#!/usr/bin/env python3
"""Bounded school recovery: original-reader build and deterministic offline replay.

SD64 uses independent Poppler role-delimited and MuPDF geometric readers.
SD19/SD49 are scans: complete rendered manual transcripts are compared with
the original OCR overlay / fresh Tesseract, retaining explicit OCR corrections.
The OCR comparison is not represented as two independent native readers.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / 'research/salaries/recovery-schools'
RESEARCH = ROOT / 'research/salaries/recovery-wave-2026-11-01/schools'
CACHE = Path('/tmp/pofbc-schools')
IMAGE_CACHE = Path('/tmp/recovery-schools')
FIELDS = ['name', 'position', 'remuneration', 'expenses', 'pdfPage']
MONEY = r'-?\d[\d,]*(?:\.\d{2})?'
ROLES = [
    'ASSOCIATE SUPERINTENDENT', 'PRINCIPAL/VICE-PRINCIPAL',
    'OPERATIONS ADMINISTRATION', 'EXECUTIVE ADMINISTRATION',
    'MANAGER - INTERNATIONAL', 'SECRETARY TREASURER', 'DISTRICT PRINCIPAL',
    'OPERATIONS CUPE', 'SUPERINTENDENT', 'TEACHER', 'TRUSTEE', 'VICE-CHAIR', 'CHAIR',
]
SCAN_ROLES = [
    'Trustee (Vice Chair)', 'Trustee (Chair)', 'Speech language Patholoigist',
    'Manager of Operations', 'Secretary Treasurer', 'District Principal',
    'Teacher/Principal', 'Vice-Principal', 'Superintendent', 'Principal', 'Teacher', 'Trustee',
]
CONFIG = {
    19: {'name': 'Revelstoke', 'pages': [50, 51], 'mode': 'scan-overlay',
         'sha256': 'e9986f7cbe9443f0593ae1b88f2014575a33aab5582510c8088a8fbb162870c0',
         'controls': {'school-trustees': ['72982', '21665'], 'employee-remuneration': ['8210710', '148744']},
         'approvalPage': 2, 'approval': 'Declaration identifies June 30, 2025; signatures are redacted and visible date fields read December 19, 2025.',
         'corrections': [
             {'pdfPage': 50, 'field': 'name', 'before': 'Jodie Alien', 'after': 'Jodie Allen'},
             {'pdfPage': 50, 'field': 'name', 'before': 'lan Gardiner', 'after': 'Ian Gardiner'},
             {'pdfPage': 50, 'field': 'name', 'before': 'Gregory Kenyan', 'after': 'Gregory Kenyon'},
             {'pdfPage': 51, 'field': 'name', 'before': 'Roberts Kubik', 'after': 'Roberta Kubik'},
         ]},
    49: {'name': 'Central Coast', 'pages': [53], 'mode': 'scan-tesseract',
         'sha256': 'f3e643ccba15d44118d411f83ee956ce166b9fe51dc97378024659c7b6bb34f3',
         'controls': {'school-trustees': ['63096', '14225'], 'employee-remuneration': ['3601790', '32532']},
         'approvalPage': 3, 'approval': 'Declaration identifies June 30, 2025; signatures are redacted and visible date fields read November 19, 2025.',
         'corrections': [
             {'pdfPage': 53, 'field': 'name', 'before': 'HEDGES, MARC.', 'after': 'HEDGES, MARC'},
         ]},
    64: {'name': 'Gulf Islands', 'pages': [52, 53, 54], 'mode': 'native',
         'sha256': '38f70c4948dae2b68c560e2c4cbc0c95610b68c9448392f0c142798a954bad17',
         'controls': {'school-trustees': ['126054', '25345'], 'employee-remuneration': ['12228711', '223125']},
         'approvalPage': 3, 'approval': 'Declaration identifies June 30, 2025; signature area is redacted and adjacent date fields are blank. No adoption date is inferred.',
         'geometry': {52: [244, 396, 480], 53: [244, 396, 480], 54: [239, 382, 464]}},
}
PEER_RECEIPTS = {
    19: {'file': 'research/salaries/recovery-wave-2026-11-01/reviews/independent-manual-sd19-2025-comparison.json',
         'sha256': '61a1295c0784a653725cb5c59bd328d04e6a002056737612a27bc59df029e36a'},
    49: {'file': 'research/salaries/recovery-wave-2026-11-01/reviews/independent-manual-sd49-2025-comparison.json',
         'sha256': '529db236c50d5a17cefa93e2eff349342b80aaa6ff055375dbcfb43d62513e28'},
    64: {'file': 'research/salaries/recovery-wave-2026-11-01/reviews/independent-manual-sd64-2025-trustees-comparison.json',
         'sha256': '99f5247cc23b6150c02d3c5ff2864e7f544715f2f08a7f07c3ceb3103b47c117',
         'categories': ['school-trustees'], 'physicalPages': [52]},
}
NORMALIZED_PEER_RECEIPT = {
    'file': 'research/salaries/recovery-wave-2026-11-01/reviews/independent-manual-schools-normalized-payloads.json',
    'sha256': '3b790d418fab916c22f1a3f90e36c8ee3bffcb913025dcc4b560cd6dc08b745b',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def clean(value):
    return re.sub(r'\s+', ' ', value).strip()


def amount(value):
    value = value.replace('$', '').replace(',', '').strip()
    if value in ['', '-', '–', '—']:
        return None
    return str(Decimal(value))


def pack(value):
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
    return gzip.compress(raw, mtime=0), raw


def row_values(rows):
    return [[row[k] for k in FIELDS] for row in rows]


def totals(rows):
    return [str(sum((Decimal(r[k]) for r in rows if r[k] is not None), Decimal(0)))
            for k in ['remuneration', 'expenses']]


def native_poppler(text, config):
    """Parse lexical role delimiters without MuPDF coordinates or name lists."""
    rows = []
    role_pattern = '|'.join(re.escape(x) for x in ROLES)
    pattern = re.compile(r'^\s*(.+?)\s+(' + role_pattern + r')\s+\$\s*(' + MONEY +
                         r')\s+\$\s*(' + MONEY + r'|-)\s*$')
    control_rows = {}
    for pno in config['pages']:
        for line in text.split('\f')[pno - 1].splitlines():
            s = clean(line)
            if s.startswith('TOTAL ELECTED OFFICIALS') or s.startswith('TOTAL DETAILED EMPLOYEES >'):
                vals = re.findall(MONEY, s)
                category = 'school-trustees' if 'ELECTED' in s else 'employee-remuneration'
                control_rows[category] = [amount(x) for x in vals[-2:]]
            match = pattern.fullmatch(line)
            if not match:
                if ',' in line and '$' in line and not s.startswith(('TOTAL ', 'DETAILED ')):
                    raise ValueError(f'Unparsed native named row on physical page {pno}: {line}')
                continue
            name, role, pay, exp = match.groups()
            pay = amount(pay)
            rows.append({'name': clean(name), 'position': role, 'remuneration': pay,
                         'expenses': amount(exp), 'pdfPage': pno,
                         'category': 'school-trustees' if Decimal(pay) < 75000 else 'employee-remuneration',
                         'popplerSourceLine': line})
    assert control_rows == config['controls'], (control_rows, config['controls'])
    return rows


def native_mupdf(path, config):
    """Group words by physical baseline and then fixed geometric column bounds."""
    import fitz
    rows = []
    doc = fitz.open(path)
    for pno in config['pages']:
        groups = []
        for word in sorted(doc[pno - 1].get_text('words'), key=lambda w: ((w[1] + w[3]) / 2, w[0])):
            y = (word[1] + word[3]) / 2
            group = next((g for g in groups[-3:] if abs(g['y'] - y) < 2), None)
            if group is None:
                group = {'y': y, 'words': []}
                groups.append(group)
            group['words'].append(word)
        for group in groups:
            fields = [[] for _ in range(4)]
            words = sorted(group['words'], key=lambda w: w[0])
            for word in words:
                if word[4] == '$':
                    continue
                fields[sum(word[0] >= bound for bound in config['geometry'][pno])].append(word[4])
            name, role, pay, exp = [clean(' '.join(f)) for f in fields]
            if ',' not in name or name.startswith(('TOTAL ', 'DETAILED ')):
                continue
            assert re.fullmatch(MONEY, pay), (pno, fields)
            assert re.fullmatch(MONEY + r'|-', exp), (pno, fields)
            rows.append({'name': name, 'position': role, 'remuneration': amount(pay),
                         'expenses': amount(exp), 'pdfPage': pno,
                         'category': 'school-trustees' if pno == 52 and group['y'] < 280 else 'employee-remuneration',
                         'mupdfWords': [{'text': w[4], 'bbox': [round(v, 3) for v in w[:4]]} for w in words]})
    return rows


def manual_rows(sd):
    with (RESEARCH / f'sd{sd}-2025-manual.tsv').open() as stream:
        return [{'name': r['name'], 'position': r['position'] or None,
                 'remuneration': amount(r['remuneration']), 'expenses': amount(r['expenses']),
                 'pdfPage': int(r['pdfPage']), 'category': r['category']}
                for r in csv.DictReader(stream, delimiter='\t')]


def scan_machine_rows(sd, texts):
    """Parse OCR rows; any manual correction must be explicit and uniquely applied."""
    rows = []
    for pno, text in texts.items():
        for line in text.splitlines():
            if sd == 19:
                pattern = r'^\s*(.+?)\s+(' + '|'.join(re.escape(x) for x in SCAN_ROLES) + r')\s+(' + MONEY + r')(?:\s+(' + MONEY + r'))?\s*$'
                match = re.fullmatch(pattern, line)
                if not match:
                    continue
                name, role, pay, exp = match.groups()
            else:
                match = re.fullmatch(r'([A-Z][A-Z ,.\-]+?)\s+\$\s*(' + MONEY + r')\s+\$\s*(' + MONEY + r')\s*', line)
                if not match or match[1].startswith('TOTAL '):
                    continue
                name, pay, exp = match.groups()
                role = None
            pay = amount(pay)
            rows.append({'name': clean(name), 'position': role, 'remuneration': pay,
                         'expenses': amount(exp or ''), 'pdfPage': pno,
                         'category': 'school-trustees' if Decimal(pay) < 75000 else 'employee-remuneration',
                         'ocrSourceLine': line})
    return rows


def corrected_scan_rows(raw_rows, corrections):
    rows = [dict(r) for r in raw_rows]
    for correction in corrections:
        matches = [r for r in rows if r['pdfPage'] == correction['pdfPage'] and r[correction['field']] == correction['before']]
        assert len(matches) == 1, correction
        matches[0][correction['field']] = correction['after']
    return rows


def scan_texts(path, sd, config, rerun_ocr):
    import fitz
    doc = fitz.open(path)
    texts, images = {}, []
    IMAGE_CACHE.mkdir(exist_ok=True)
    for pno in config['pages']:
        image_path = IMAGE_CACHE / f'sd{sd:02}-p{pno}.png'
        doc[pno - 1].get_pixmap(matrix=fitz.Matrix(2, 2)).save(image_path)
        images.append({'pdfPage': pno, 'path': str(image_path), 'sha256': sha(image_path.read_bytes()), 'renderScale': 2})
        if config['mode'] == 'scan-overlay':
            text = subprocess.check_output(['pdftotext', '-layout', '-f', str(pno), '-l', str(pno), str(path), '-']).decode()
        else:
            text_path = image_path.with_suffix('.txt')
            if rerun_ocr or not text_path.exists():
                text_path.write_text(subprocess.check_output(['tesseract', str(image_path), 'stdout', '--psm', '6'], stderr=subprocess.DEVNULL).decode())
            text = text_path.read_text()
        texts[pno] = text
    return texts, images


def render_pages(path, sd, pages):
    import fitz
    doc = fitz.open(path)
    IMAGE_CACHE.mkdir(exist_ok=True)
    images = []
    for pno in pages:
        image_path = IMAGE_CACHE / f'sd{sd:02}-p{pno}.png'
        doc[pno - 1].get_pixmap(matrix=fitz.Matrix(2, 2)).save(image_path)
        images.append({'pdfPage': pno, 'path': str(image_path), 'sha256': sha(image_path.read_bytes()), 'renderScale': 2})
    return images


def build(rerun_ocr=False):
    COLLECTION.mkdir(exist_ok=True)
    inventory = json.loads((ROOT / 'research/salaries/continuation-2026-11-01/schools/inventory.json').read_text())
    sources, originals = [], []
    for sd, config in CONFIG.items():
        path = CACHE / f'ministry-sd{sd:02}-2025.pdf'
        assert sha(path.read_bytes()) == config['sha256'], sd
        entry = next(e for e in inventory['employers'] if e['districtNumber'] == sd)
        receipt = entry['currentOfficialSource']
        peer_receipt = PEER_RECEIPTS.get(sd)
        if peer_receipt:
            peer_bytes = (ROOT/peer_receipt['file']).read_bytes()
            assert sha(peer_bytes) == peer_receipt['sha256']
            peer = json.loads(peer_bytes)
            assert peer['originalSha256'] == config['sha256']
            candidate = peer.get('candidate', peer.get('candidateManual'))
            if candidate:
                assert candidate['sha256'] == sha((RESEARCH/f'sd{sd}-2025-manual.tsv').read_bytes())
            assert peer['candidateCorrections'] == []
            transcript = peer['independentRawTranscript']
            assert sha((ROOT/transcript['path']).read_bytes()) == transcript['sha256']
        images, raw_machine, machine_texts = [], [], {}
        if config['mode'] == 'native':
            text = subprocess.check_output(['pdftotext', '-layout', str(path), '-']).decode()
            rows, second = native_poppler(text, config), native_mupdf(path, config)
            assert row_values(rows) == row_values(second), [(a,b) for a,b in zip(row_values(rows),row_values(second)) if a != b]
            images = render_pages(path, sd, config['pages'])
        else:
            machine_texts, images = scan_texts(path, sd, config, rerun_ocr)
            rows = manual_rows(sd)
            raw_machine = scan_machine_rows(sd, machine_texts)
            second = corrected_scan_rows(raw_machine, config['corrections'])
            assert row_values(rows) == row_values(second), [(a,b) for a,b in zip(row_values(rows),row_values(second)) if a != b]
            assert [r['category'] for r in rows] == [r['category'] for r in second]
        original_ids = []
        for category in ['school-trustees', 'employee-remuneration']:
            cohort_peer = peer_receipt if peer_receipt and category in peer_receipt.get('categories', ['school-trustees', 'employee-remuneration']) else None
            subset = [r for r in rows if r['category'] == category]
            independent = [r for r in second if r['category'] == category]
            suffix = 'trustees' if category == 'school-trustees' else 'employees'
            key = f'sd{sd:02}-2025-{suffix}'
            normalized = [[entry['employerSlug'], r['name'], r['position'], float(r['remuneration']), None if r['expenses'] is None else float(r['expenses']), r['pdfPage']] for r in subset]
            packed, raw = pack(normalized)
            (COLLECTION / f'{key}.json.gzip').write_bytes(packed)
            evidence = {'version': 1, 'sourceSha256': config['sha256'], 'mode': config['mode'],
                        'rows': subset, 'independentRows': independent,
                        'printedControlTotals': config['controls'][category],
                        'rawMachineRows': [r for r in raw_machine if r['category'] == category],
                        'machinePageTexts': {str(k): v for k,v in machine_texts.items()},
                        'explicitOCRCorrections': config.get('corrections', []), 'renderedPages': images,
                        'manualTranscriptFile': f'research/salaries/recovery-wave-2026-11-01/schools/sd{sd}-2025-manual.tsv' if config['mode'] != 'native' else None,
                        'manualTranscriptSha256': sha((RESEARCH / f'sd{sd}-2025-manual.tsv').read_bytes()) if config['mode'] != 'native' else None}
            proof, _ = pack(evidence)
            (COLLECTION / f'{key}-evidence.json.gzip').write_bytes(proof)
            computed = totals(subset)
            residuals = [str(Decimal(a) - Decimal(b)) for a,b in zip(computed, config['controls'][category])]
            warning = None
            if any(Decimal(r) for r in residuals):
                if sd == 19:
                    warning = 'The 77 published employee rows total $8,210,710 remuneration and $150,762 expenses. The schedule prints $8,210,710 and $148,744, so the row expense sum is $2,018 higher than the printed employee expense total. The published rows and control are retained literally; the reason is unresolved.'
                elif sd == 49:
                    warning = 'The five published trustee rows total $63,095 remuneration and $14,225 expenses. The schedule prints $63,096 and $14,225, so the row remuneration sum is $1 lower than the printed trustee remuneration total. The published rows and control are retained literally; the reason is unresolved.'
                elif sd == 64 and category == 'school-trustees':
                    warning = 'The seven published trustee rows total $126,052 remuneration and $25,345 expenses. The schedule prints $126,054 and $25,345, so the row remuneration sum is $2 lower than the printed trustee remuneration total. The published rows and control are retained literally; the reason is unresolved.'
                else:
                    raise AssertionError((sd, category, computed, residuals))
            native = config['mode'] == 'native'
            source = {
                'id': 'recovery-schools-' + key, 'inputKey': f'sd{sd:02}-2025',
                'employerSlug': entry['employerSlug'], 'employerName': entry['employerName'],
                'sector': 'School districts', 'year': '2024/25', 'slug': '2024-25',
                'periodType': 'fiscal', 'periodStart': '2024-07-01', 'periodEnd': '2025-06-30',
                'title': f"{entry['employerName']}, year ended June 30, 2025: {suffix}",
                'sourceUrl': receipt['sourceUrl'], 'sourceIndexUrl': receipt['sourceIndexUrl'],
                'sha256': config['sha256'], 'file': f'{key}.json.gzip', 'dataSha256': sha(packed), 'normalizedSha256': sha(raw),
                'provenanceFile': f'{key}-evidence.json.gzip', 'provenanceSha256': sha(proof),
                'category': category, 'scope': 'elected-school-trustees' if suffix == 'trustees' else 'named-employees-over-75000',
                'scopeDescription': 'Complete published elected trustee remuneration schedule' if suffix == 'trustees' else 'Complete published named employee schedule exceeding $75,000 remuneration; under-threshold aggregates excluded',
                'currency': 'CAD', 'amountUnit': 'dollars', 'amountPrecision': 'whole-dollar-remuneration-and-published-expense-precision',
                'nameDisclosure': 'published-name-as-disclosed', 'positionDisclosure': 'not-published' if sd == 49 else 'published-as-disclosed',
                'rowCount': len(subset), 'totalRemuneration': float(computed[0]), 'totalExpenses': float(computed[1]),
                'pages': sorted({r['pdfPage'] for r in subset}), 'status': 'verified', 'sourceKind': 'official', 'verifiedOn': '2026-11-01',
                'notes': [
                    'The annual schedule prints year ended June 30, 2025. Fiscal period is July 1, 2024 through June 30, 2025; upload labels are not the reporting-period evidence.',
                    'Remuneration and expenses are separate reported payments, not annual base salary rates. Suppliers, below-threshold aggregate payroll, employer CPP/EI premiums and financial statement totals are excluded.',
                    'Blank or dash expense values remain null; explicit zeros remain zero. Published names, punctuation, unusual capitalization and source titles are preserved without inferred corrections.',
                    'Ministry-hosted original district SOFI convenience copy. ' + config['approval'],
                    ('Every row and field agrees between independent Poppler lexical parsing and PyMuPDF geometric grouping. Rendered schedule pages were reviewed for period, scope, column boundaries and controls.' if native else 'Every scan row was read from the rendered original and fully transcribed; OCR comparison retains explicit image-verified corrections. OCR is not represented as independent native text. ' + ('Complete independent peer image review compared every row and field; the hash-pinned receipt is linked in validation.' if cohort_peer else 'Complete independent peer image review is requested before integration.')),
                ],
                'publicWarning': warning,
                'validation': {
                    'originalFingerprintVerified': True,
                    'independentReaders': ['Poppler lexical role delimiters', 'PyMuPDF geometric columns'] if native else ['complete rendered manual transcript', 'original OCR overlay with explicit image corrections' if sd == 19 else 'Tesseract 5 PSM6 with explicit image corrections'],
                    'completeRowTextAmountsOrderAndMultiplicityAgree': True,
                    'rowsIndependentlyChecked': len(subset), 'rowsByPhysicalPage': dict(collections.Counter(str(r['pdfPage']) for r in subset)),
                    'componentColumns': ['remuneration', 'expenses'], 'printedControlTotals': config['controls'][category],
                    'computedComponentTotals': computed, 'controlResiduals': residuals,
                    'summaryReconciles': warning is None, 'allPublishedNamedControlsExact': warning is None,
                    'allPrintedComponentControlsExact': warning is None,
                    'knownExpenseValueCount': sum(r['expenses'] is not None for r in subset),
                    'unparsedInterRowText': 0, 'completeIndependentPeerImageReviewPending': not native and not cohort_peer,
                    'sourceApprovalPhysicalPage': config['approvalPage'],
                },
            }
            if category == 'employee-remuneration':
                source['completeEmployeeSchedule'] = True
                source['validation']['completeEmployeeSchedule'] = True
            if cohort_peer:
                source['validation']['independentRenderedReview'] = {**cohort_peer, 'physicalPages': cohort_peer.get('physicalPages', config['pages']),
                                                                      'rowsCheckedInThisCohort': len(subset), 'everyFieldCompared': True}
                source['validation']['independentNormalizedPayloadReview'] = NORMALIZED_PEER_RECEIPT
            sources.append(source)
            original_ids.append(source['id'])
        originals.append({'inputKey': f'sd{sd:02}-2025', 'cachePath': str(path), 'sha256': config['sha256'],
                          'sourceIds': original_ids, 'sourceUrl': receipt['sourceUrl'], 'sourceIndexUrl': receipt['sourceIndexUrl'],
                          'mode': config['mode'], 'actualWorkerVisualReviewPages': [config['approvalPage']] + config['pages'],
                          'fullWorkerRowImageTranscriptionPages': config['pages'] if config['mode'] != 'native' else [],
                          'independentPeerImageReviewRequiredPages': config['pages'] if config['mode'] != 'native' else [],
                          'independentPeerImageReviewCompletedPages': peer_receipt.get('physicalPages', config['pages']) if peer_receipt else [],
                          'approvalImage': render_pages(path, sd, [config['approvalPage']])[0],
                          'renderedPages': images})
    manifest = {'version': 1, 'reviewed': '2026-11-01', 'rowSchema': ['employerSlug'] + FIELDS, 'sources': sources}
    (COLLECTION / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (RESEARCH / 'original-receipts.json').write_text(json.dumps(originals, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(originals)} originals / {len(sources)} cohorts / {sum(s["rowCount"] for s in sources)} rows')


def verify_source(source, evidence):
    assert evidence['sourceSha256'] == source['sha256']
    assert row_values(evidence['rows']) == row_values(evidence['independentRows'])
    assert len(evidence['rows']) == source['rowCount']
    assert totals(evidence['rows']) == source['validation']['computedComponentTotals']
    assert evidence['printedControlTotals'] == source['validation']['printedControlTotals']
    residuals = [str(Decimal(a)-Decimal(b)) for a,b in zip(totals(evidence['rows']), evidence['printedControlTotals'])]
    assert residuals == source['validation']['controlResiduals']
    assert bool(source['publicWarning']) == any(Decimal(x) != 0 for x in residuals)
    review = source['validation'].get('independentRenderedReview')
    if review:
        review_bytes = (ROOT/review['file']).read_bytes()
        assert sha(review_bytes) == review['sha256']
        reviewed = json.loads(review_bytes)
        assert reviewed['originalSha256'] == source['sha256']
        candidate = reviewed.get('candidate', reviewed.get('candidateManual'))
        if candidate:
            assert candidate['sha256'] == evidence['manualTranscriptSha256']
        if 'normalizedComparisons' in reviewed:
            normalized_review = next(r for r in reviewed['normalizedComparisons'] if r['sourceId'] == source['id'])
            assert normalized_review['dataSha256'] == source['dataSha256']
            assert normalized_review['allSixFieldsExact']
        elif 'dataSha256' in reviewed:
            assert reviewed['sourceId'] == source['id']
            assert reviewed['dataSha256'] == source['dataSha256']
            assert reviewed['allSixFieldsExact']
    normalized_peer = source['validation'].get('independentNormalizedPayloadReview')
    if normalized_peer:
        raw_peer = (ROOT/normalized_peer['file']).read_bytes()
        assert sha(raw_peer) == normalized_peer['sha256']
        check = next(r for r in json.loads(raw_peer)['comparisons'] if r['sourceId'] == source['id'])
        assert check['dataSha256'] == source['dataSha256']
        assert check['provenanceSha256'] == source['provenanceSha256']
        assert check['originalSha256'] == source['sha256']
        assert check['rowsCompared'] == source['rowCount']
        assert check['allSixFieldsExact'] and check['rowCountAndTotalsMatchManifest']
    if evidence['manualTranscriptFile']:
        assert sha((ROOT/evidence['manualTranscriptFile']).read_bytes()) == evidence['manualTranscriptSha256']
        sd = int(source['inputKey'][2:4])
        assert [r for r in manual_rows(sd) if r['category'] == source['category']] == evidence['rows']
        raw = scan_machine_rows(sd, {int(p):t for p,t in evidence['machinePageTexts'].items()})
        corrected = corrected_scan_rows(raw, evidence['explicitOCRCorrections'])
        assert [r for r in corrected if r['category'] == source['category']] == evidence['independentRows']
    normalized = [[source['employerSlug'], r['name'], r['position'], float(r['remuneration']), None if r['expenses'] is None else float(r['expenses']), r['pdfPage']] for r in evidence['rows']]
    packed, raw = pack(normalized)
    assert sha(packed) == source['dataSha256']
    assert sha(raw) == source['normalizedSha256']
    assert packed == (COLLECTION / source['file']).read_bytes()


def verify(originals=False, rerun_ocr=False):
    sources = json.loads((COLLECTION/'sources.json').read_text())['sources']
    count = 0
    original_replay = {}
    for source in sources:
        proof = (COLLECTION/source['provenanceFile']).read_bytes()
        assert sha(proof) == source['provenanceSha256']
        evidence = json.loads(gzip.decompress(proof))
        verify_source(source, evidence)
        if originals:
            sd = int(source['inputKey'][2:4]); config = CONFIG[sd]
            path = CACHE/f'ministry-sd{sd:02}-2025.pdf'
            assert sha(path.read_bytes()) == source['sha256']
            if sd not in original_replay:
                if config['mode'] == 'native':
                    text = subprocess.check_output(['pdftotext','-layout',str(path),'-']).decode()
                    first, second = native_poppler(text, config), native_mupdf(path, config)
                    assert render_pages(path, sd, config['pages']) == evidence['renderedPages']
                else:
                    texts, images = scan_texts(path, sd, config, rerun_ocr)
                    first = manual_rows(sd)
                    second = corrected_scan_rows(scan_machine_rows(sd, texts), config['corrections'])
                    assert images == evidence['renderedPages']
                original_replay[sd] = (first, second)
            first, second = original_replay[sd]
            assert [r for r in first if r['category'] == source['category']] == evidence['rows']
            assert [r for r in second if r['category'] == source['category']] == evidence['independentRows']
        count += source['rowCount']
    print(f'Verified {len(sources)} recovery school cohorts / {count} rows' + (' against originals' if originals else ' by offline evidence replay'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--originals', action='store_true')
    parser.add_argument('--rerun-ocr', action='store_true')
    args = parser.parse_args()
    if args.build:
        build(args.rerun_ocr)
    verify(args.originals, args.rerun_ocr)


if __name__ == '__main__':
    main()
