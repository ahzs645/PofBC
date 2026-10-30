#!/usr/bin/env python3
"""Verify BCCSS 2016/17 against the original PDF using two extraction engines."""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
SHA = '80f991ee3bc034534a23240fb1e57f613a0fe1a2c17a0eb7f87d0a8990ba2bd3'
URL = 'https://www.phsa.ca/about-site/Documents/BCCSS%20Statement%20of%20Financial%20Information%202016-17.pdf'
SLUG = 'bc-clinical-and-support-services-society'
ROW = re.compile(r'^(.+?)\s{2,}\$?\s*([\d,]+)\s+\$?\s*([\d,]+|-)\s*$')


def amount(value):
    return None if value == '-' else int(value.replace(',', ''))


def layout_rows(pdf):
    text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True, capture_output=True).stdout.decode()
    pages = text.split('\f')
    output = []
    for pg in range(48, 54):
        page = pages[pg - 1]
        if not all(s in page for s in ['FOR EMPLOYEES', 'MARCH 31, 2017']):
            raise ValueError(f'Page {pg}: incorrect schedule or period')
        started = False
        for line in page.splitlines():
            if 'Employee Name' in line:
                started = True
                continue
            if line.strip().startswith('Employees with remuneration'):
                break
            if not started or not line.strip():
                continue
            match = ROW.fullmatch(line.strip())
            if match:
                name, pay, expense = match.groups()
                if ',' not in name:
                    raise ValueError(f'Unexpected non-name row on page {pg}')
                output.append([SLUG, name, None, amount(pay), amount(expense), pg])
            elif not line.strip().isdigit():
                raise ValueError(f'Page {pg}: unparsed employee line: {line}')
    if 'Employees with remuneration equal to or greater than $75,000' not in pages[52]:
        raise ValueError('Inclusive threshold statement missing')
    for control in ['28,855,034', '958,981', '63,881,477', '728,774', '92,736,511', '1,687,755']:
        if control not in pages[52]:
            raise ValueError(f'Published control {control} missing')
    return output


def coordinate_rows(pdf):
    doc = fitz.open(pdf)
    rows = []
    for pg in range(48, 54):
        groups = {}
        for word in doc[pg - 1].get_text('words'):
            groups.setdefault(round(word[1], 1), []).append(word)
        for y, words in sorted(groups.items()):
            if y < 115:
                continue
            words.sort(key=lambda w: w[0])
            text = ' '.join(w[4] for w in words)
            if text.startswith('Employees with remuneration'):
                break
            name = ' '.join(w[4] for w in words if w[0] < 380)
            if ',' not in name:
                continue
            values = [w[4] for w in words if w[0] >= 380 and w[4] != '$']
            if len(values) != 2 or not re.fullmatch(r'[\d,]+', values[0]):
                raise ValueError(f'Page {pg}: ambiguous PDF columns')
            rows.append([SLUG, name, None, amount(values[0]), amount(values[1]), pg])
    return rows


def process(pdf, out):
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != SHA:
        raise ValueError('PDF differs from the visually reviewed original')
    first, second = layout_rows(pdf), coordinate_rows(pdf)
    if first != second:
        raise ValueError('Independent PDF readers disagree')
    if len(first) != 306 or sum(r[3] for r in first) != 28855034 or sum(r[4] or 0 for r in first) != 958981:
        raise ValueError('Named employee controls do not reconcile')
    if any(r[3] < 75000 for r in first):
        raise ValueError('Unexpected below-threshold row')
    out.mkdir(parents=True, exist_ok=True)
    data = gzip.compress((json.dumps(first, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), mtime=0)
    (out / '2016-17.json.gzip').write_bytes(data)
    source = {
        'id': 'bccss-employees-2016-17', 'year': '2016/17', 'periodType': 'fiscal',
        'periodStart': '2016-04-01', 'periodEnd': '2017-03-31', 'status': 'verified',
        'employerSlug': SLUG, 'employerName': 'BC Clinical and Support Services Society', 'sector': 'Health authorities',
        'title': 'BCCSS 2016/17 employee remuneration and expenses', 'category': 'employee-remuneration',
        'sourceUrl': URL, 'indexUrl': 'https://www.phsa.ca/about/accountability/budget-financials', 'sha256': SHA,
        'file': '2016-17.json.gzip', 'dataSha256': hashlib.sha256(data).hexdigest(), 'currency': 'CAD',
        'rowCount': 306, 'totalRemuneration': 28855034, 'totalExpenses': 958981,
        'threshold': 75000, 'thresholdComparison': '>=', 'nameDisclosure': 'as-published',
        'validation': {'date': '2026-10-30', 'physicalPdfPages': [48, 53], 'rowsPerPage': [56, 56, 56, 56, 56, 26],
                       'independentReaders': ['Poppler layout', 'PyMuPDF positioned words'], 'everyRowAndPageAgree': True,
                       'printedRemunerationReconcilesExactly': True, 'printedExpensesReconcileExactly': True,
                       'visuallyReviewedPhysicalPages': [16, 48, 49, 50, 51, 52, 53], 'expenseDashesRetainedAsMissing': 60,
                       'employeeTableExcludesBoardPage': 47, 'aggregateRowsExcluded': True},
        'notes': ['BCCSS is a separate reporting employer. Its employee rows are not appended to PHSA or relabelled as PHSA employees.',
                  'The report describes BCCSS as a society and says operations commenced April 1, 2016 after services transferred from PHSA; see physical PDF page 16.',
                  'The schedule is cash-based remuneration, including disclosed employee payments; it is not an annual salary rate. Employer benefit costs and contracted labour explain why it differs from accrual financial statements.',
                  'Names and whole-dollar amounts are preserved. Sixty expense dashes remain missing, not disclosed zero; the disclosed numeric values reconcile exactly to the named subtotal.',
                  'The inclusive $75,000 threshold is taken from the named subtotal heading. Board, below-threshold and all-employee totals are excluded from individual records.']
    }
    manifest = {'version': 1, 'sources': [source], 'employerDecision': {
        'canonicalSlug': SLUG, 'relatedEmployerSlug': 'provincial-health-services-authority',
        'relationship': 'Separate society; transferred services began operations on April 1, 2016',
        'evidenceUrl': URL, 'physicalPdfPage': 16,
        'aggregationRule': 'Do not merge employers or deduplicate people across these employers without payment-specific evidence.'}}
    (out / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'rows': len(first), 'remuneration': source['totalRemuneration'], 'expenses': source['totalExpenses'], 'allRowsAgree': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'research/salaries/bccss')
    args = parser.parse_args()
    process(args.pdf, args.out)
