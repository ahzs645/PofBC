#!/usr/bin/env python3
"""Reproduce Metro Vancouver native-text employee schedules, preserving residuals.

Two text readers must agree on every name, component, page, and row boundary.
This deliberately never balances published individual values to financial totals.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/sector-government-police'
INDEX = 'https://metrovancouver.org/about-us/budgets-and-financial-plans'
MONEY = r'(?:-?\d[\d,]*|-)'
LINE = re.compile(r'^(.+?\S)\s{2,}\$?\s*(' + MONEY + r')\s+\$?\s*(' + MONEY + r')\s+\$?\s*(' + MONEY + r')\s*$')
CONFIG = {
    2022: {'sha256': '0bd858681074e1bbdce3227b39f12a284b2cadabafd51a608f6a4b1b5139390e', 'printed': [144427823, 15313377, 2487967], 'count': 1394, 'pages': [55, 84]},
    2023: {'sha256': 'e46777b9eef15f4fca87f99d7b8ac17e17a290c65fc6d8f48b149df088c6e5ea', 'printed': [170389381, 34425925, 3699180], 'count': 1634, 'pages': [64, 104]},
    2024: {'sha256': '074859ef49fd2a857e3e7f593ad6d3172bce5f418760c54fceb5de70c85faf41', 'printed': [192721244, 18984039, 4070835], 'count': 1696, 'pages': [71, 113]},
    2025: {'sha256': '4dcc974b93f73fd83e06f52c232e642e9a056686f84463cbc049522003f25543', 'printed': [203458940, 18103572, 3000920], 'count': 1780, 'pages': [73, 117]},
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def packed(data):
    return gzip.compress(encoded(data), mtime=0)


def amount(text):
    # No dash=zero legend exists in these originals. Preserve missing cells.
    return None if text == '-' else int(text.replace(',', ''))


def source_url(year):
    prefix = 'statement-of-financial-information' if year == 2025 else 'statement-financial-information'
    return f'https://metrovancouver.org/about-us/Documents/{prefix}-{year}.pdf'


def extract(pdf_path, year):
    import fitz
    doc = fitz.open(pdf_path)
    layout = subprocess.run(['pdftotext', '-layout', str(pdf_path), '-'], check=True, capture_output=True, text=True).stdout.split('\f')
    primary, second, pages = [], [], []
    for i, page in enumerate(doc):
        text = page.get_text()
        if not (text.startswith('Schedule 2') and '\nEmployees\n' in text):
            continue
        assert re.search(rf'For the year ended December 31,\s*{year}', text)
        assert 'Payments (1)' in text and 'and Other (2)' in text and 'Expenses (3)' in text
        pages.append(i + 1)
        words = page.get_text('words')
        anchors = [w for w in words if w[0] < 220 and ',' in w[4] and w[1] > 120 and not w[4].startswith('$')]
        for anchor in anchors:
            line = sorted([w for w in words if abs(w[1] - anchor[1]) < 1.4], key=lambda w: w[0])
            nums = [w for w in line if re.fullmatch(MONEY, w[4])]
            if len(nums) != 3:
                raise ValueError(f'Unreviewed row {year} page {i + 1}: {line}')
            name = ' '.join(w[4] for w in line if w[0] < nums[0][0] and w[4] != '$')
            primary.append([name, *[amount(w[4]) for w in nums], i + 1])
        for line in layout[i].splitlines():
            match = LINE.match(line)
            if match and ',' not in match[1] and match[1].strip() not in {'$', 'less'}:
                raise ValueError(f'Unreviewed non-name monetary row {year} page {i + 1}: {line}')
            if match and ',' in match[1] and not match[1].strip().startswith('remuneration '):
                second.append([match[1].strip(), *[amount(match[j]) for j in (2, 3, 4)], i + 1])
    if primary != second:
        raise ValueError(f'{year}: PyMuPDF and Poppler disagree: counts {len(primary)}/{len(second)}; extra {[r for r in primary if r not in second][:3]}; missing {[r for r in second if r not in primary][:3]}')
    assert pages == list(range(CONFIG[year]['pages'][0], CONFIG[year]['pages'][1] + 1))
    assert len(primary) == CONFIG[year]['count']
    assert all(r[1] is not None and r[1] + (r[2] or 0) > 75000 for r in primary)
    return primary


def build(cache, fetch=False, check_data=False):
    sources = []
    for year, cfg in CONFIG.items():
        evidence_file = f'evidence/metro-vancouver-{year}-components.json.gzip'
        if check_data:
            evidence = json.loads(gzip.decompress((OUT / evidence_file).read_bytes()))
            assert evidence['originalSha256'] == cfg['sha256']
            rows = evidence['rows']
        else:
            path = cache / f'metro{year}.pdf'
            if fetch and not path.exists():
                request = urllib.request.Request(source_url(year), headers={'User-Agent': 'Mozilla/5.0'})
                path.write_bytes(urllib.request.urlopen(request, timeout=60).read())
            assert sha(path.read_bytes()) == cfg['sha256'], f'{year}: source fingerprint changed'
            rows = extract(path, year)
            evidence = {'originalSha256': cfg['sha256'], 'rowSchema': ['name', 'salaryPayments', 'taxableBenefitsAndOther', 'expenses', 'pdfPage'], 'readers': ['PyMuPDF words, anchored names and three monetary cells', 'Poppler pdftotext -layout, full-line table grammar'], 'bothReadersAgree': True, 'rows': rows}
            (OUT / evidence_file).write_bytes(packed(evidence))
        assert len(rows) == cfg['count']
        held = [r for r in rows if r[1] is None or r[2] is None]
        normalized = [['metro-vancouver', r[0], None, r[1] + r[2], r[3], r[4]] for r in rows if r[1] is not None and r[2] is not None]
        # Full-source controls use all known cells, never accepted-subset sums.
        totals = [sum(r[j] for r in rows if r[j] is not None) for j in (1, 2, 3)]
        missing = [sum(r[j] is None for r in rows) for j in (1, 2, 3)]
        residuals = [actual - printed for actual, printed in zip(totals, cfg['printed'])]
        filename = f'metro-vancouver-{year}-employees.json.gzip'
        data = packed(normalized)
        if check_data:
            assert (OUT / filename).read_bytes() == data
        else:
            (OUT / filename).write_bytes(data)
        signs = [f'{x:+,}' for x in residuals]
        coverage_warning = (f'Partial employee cohort: {len(held)} named rows with an undisclosed benefits/other component are held from the {len(rows)}-row original; {len(normalized)} accepted.' if held else f'All {len(rows)} named employee rows are transcribed.')
        warning = (coverage_warning + f' Full-original known-cell sums differ from printed subtotals: salary payments ${signs[0]}, taxable benefits and other ${signs[1]}, expenses ${signs[2]} (known-cell sums minus controls). {missing[2]} expense dashes remain missing. Published values are unchanged; residual causes and dash semantics remain unresolved.')
        sources.append({
            'id': f'sector-government-police-metro-vancouver-{year}-employees',
            'employerSlug': 'metro-vancouver', 'employerName': 'Metro Vancouver',
            'sector': 'Municipalities', 'governanceType': 'regional-district',
            'year': str(year), 'periodType': 'calendar', 'periodStart': f'{year}-01-01', 'periodEnd': f'{year}-12-31',
            'category': 'employee-remuneration', 'scope': 'employee-remuneration',
            'file': filename, 'dataSha256': sha(data), 'sha256': cfg['sha256'],
            'sourceUrl': source_url(year), 'sourceIndexUrl': INDEX,
            'title': f'Metro Vancouver {year} SOFI: Schedule 2, employees',
            'status': 'accepted', 'rowCount': len(normalized),
            'totalRemuneration': sum(r[3] for r in normalized), 'totalExpenses': sum(r[4] for r in normalized if r[4] is not None),
            'completeEmployeeSchedule': not held, 'originalNamedRowCount': len(rows), 'heldRowCount': len(held),
            'heldRows': [{'name': r[0], 'salaryPayments': r[1], 'taxableBenefitsAndOther': r[2], 'expenses': r[3], 'pdfPage': r[4], 'reason': 'Benefits/other is a published dash without a zero legend; composite remuneration is incomplete.'} for r in held],
            'pages': list(range(cfg['pages'][0], cfg['pages'][1] + 1)),
            'threshold': 75000, 'thresholdComparison': '>', 'currency': 'CAD', 'amountUnit': 'dollars',
            'verifiedOn': '2026-10-31', 'publicWarning': warning,
            'notes': [
                'Remuneration is Salary Payments (Base Salary Payments in 2022–2023) plus Taxable Benefits and Other. Schedule 3 defines the remuneration reconciliation using these two components. Expenses remain separate.',
                'The original publishes whole-dollar individual cells. No assumption about rounding explains or repairs the retained source subtotal residuals.',
                'Published dashes have no zero legend and remain missing. Rows with a missing pay component are held from the accepted composite-remuneration cohort; known salary and all original cells remain in full-source component evidence.',
                'Job titles are not published in Schedule 2; position remains missing.',
                'The aggregate for employees with remuneration of $75,000 or less is excluded. This is a threshold payment disclosure, not an employee roster or an annual salary-rate table.',
                'Schedule 1 contains directors and standing committee members, including appointed non-elected members. Those rows are outside this employee cohort and have not been imported here.',
                'Regional district; excluded from the 161-current-municipality denominator. The existing app employer sector label is retained pending a separate taxonomy change.',
                'Existing compiled records and their fiscal-looking unverified labels are retained; no calendar-year equivalence or deletion is inferred.'
            ],
            'validation': {'method': 'Complete PyMuPDF/Poppler native-text field agreement; original hash pinned; internal year and page sequence checked', 'bothReadersAgree': True,
                           'printedControlsScope': 'Complete original named table, including held rows; rowSum is the sum of known cells and does not assert missing dashes are zero. Not the accepted subset.',
                           'printedControls': [{'field': field, 'printedControl': printed, 'rowSum': actual, 'residual': residual, 'missingCells': missing_count}
                                               for field, printed, actual, residual, missing_count in zip(['salaryPayments', 'taxableBenefitsAndOther', 'expenses'], cfg['printed'], totals, residuals, missing)],
                           'evidenceFile': evidence_file, 'evidenceSha256': sha((OUT / evidence_file).read_bytes())}
        })
    manifest = {'version': 1, 'rowSchema': ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage'], 'sources': sources}
    destination = OUT / 'sources.json'
    if check_data:
        assert json.loads(destination.read_text()) == manifest
    else:
        destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sources': len(sources), 'rows': sum(s['rowCount'] for s in sources), 'controls': {s['year']: s['validation']['printedControls'] for s in sources}}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/tmp/pofbc-sector-government-police'))
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--check-data', action='store_true')
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    build(args.cache, fetch=args.fetch, check_data=args.check_data)
