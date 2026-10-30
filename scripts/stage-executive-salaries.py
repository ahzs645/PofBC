#!/usr/bin/env python3
"""Keep executive compensation components outside the employee-remuneration build."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_page(path, expected_hash, page):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise ValueError(f'Executive source changed: {path.name}')
    return subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-layout', str(path), '-'], capture_output=True, check=True).stdout.decode()


def write(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'research/salaries/executive-staging')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = [
        {'id': 'bci-executives-2025-26', 'pdf': 'bci-2025-26.pdf', 'employerSlug': 'bc-investment-management-corporation',
         'year': '2025/26', 'sha256': '6fc5588d4e9bf1fbaba5b8b9375f6994e5819dbede8cb9295885bbc980a0c769', 'pdfPage': 53,
         'url': 'https://www.bci.ca/wp-content/uploads/2026/10/bci-corporate-annual-report-2025-2026.pdf',
         'rows': [
             ['Gordon J. Fyfe', 'Chief Executive Officer / Chief Investment Officer', 'CAD', 725196, 2064634, 2681002, 76069, 300879, 5847780],
             ['Daniel Garant', 'Executive VP & Global Head, Capital Markets & Credit Investments', 'CAD', 610000, 1622478, 1542493, 64722, 212566, 4052259],
             ['Lincoln Webb', 'Executive VP & Global Head, Infrastructure & Renewable Resources', 'CAD', 610000, 1622478, 1506721, 64722, 218982, 4022904],
             ['Ramy Rayes', 'Executive VP, Investment Strategy & Risk', 'CAD', 500000, 1136250, 1136881, 53887, 166797, 2993815],
             ['Jon Salon', 'Executive VP & Global Head, Private Equity', 'USD', 583333, 1846570, 695085, 32812, 61442, 3219242]
         ]},
        {'id': 'bci-executives-2017-18', 'pdf': 'bci-2017-18.pdf', 'employerSlug': 'bc-investment-management-corporation',
         'year': '2017/18', 'sha256': 'e5e8d4629a7247a12fa9a9fc81fa7f30a023be8a4a09b6253bd3f8eb6d811acd', 'pdfPage': 46,
         'url': 'https://www.bci.ca/wp-content/uploads/2018/01/17-18-corporate-annual-report-2018.pdf',
         'rows': [
             ['Gordon J. Fyfe', 'Chief Executive Officer / Chief Investment Officer', 'CAD', 579043, 1343013, 884946, 65045, 151129, 3023176],
             ['Daniel Garant', 'Senior Vice President, Public Markets', 'CAD', 249231, 833215, 610632, 30731, 170347, 1894155],
             ['Lincoln Webb', 'Senior Vice President, Infrastructure & Renewable Resources', 'CAD', 374712, 724500, 374528, 42711, 81328, 1597779],
             ['Jim Pittman', 'Senior Vice President, Private Equity', 'CAD', 374712, 709500, 374983, 42711, 61290, 1563196],
             ['Bryan Thomson', 'Senior Vice President, Public Equities', 'CAD', 320000, 476160, 548118, 36731, 69024, 1450034]
         ]}
    ]
    fields = ['nameAsPublished', 'position', 'currency', 'baseSalary', 'annualIncentive', 'longTermIncentive', 'pensionContributions', 'otherBenefits', 'totalCompensationAsPublished']
    manifest = []
    for source in sources:
        text = load_page(args.source_dir / source['pdf'], source['sha256'], source['pdfPage'])
        records = []
        for row in source['rows']:
            if row[0] not in text or any(f'{value:,}' not in text for value in row[3:]):
                raise ValueError(f'Source transcription no longer matches {row[0]}')
            record = dict(zip(fields, row))
            record['componentSumMinusPublishedTotal'] = sum(row[3:8]) - row[8]
            record['physicalPdfPage'] = source['pdfPage']
            records.append(record)
        entry = {k: v for k, v in source.items() if k not in ['rows', 'pdf']}
        entry.update(acceptedForEmployeeBuild=False, scope='executive-only', rowCount=len(records),
                     candidateFile=source['id'] + '.json', status='reviewed-executive-components-staged',
                     notes=['Current-period top-five executive rows only; comparative prior-year rows are not a complete historical cohort.',
                            'Incentives are attributed to their performance year and may be paid in a later fiscal year. This is not a cash-paid employee remuneration schedule.',
                            'Published component/total residuals are preserved, not balanced. Currency stays on each row; no CAD/USD sum or conversion is made.'])
        write(args.out / entry['candidateFile'], {'source': entry, 'rows': records})
        manifest.append(entry)
    pension_hash = '74d0ddf9410fc5707d7d9ff76123a8a2e12b07695a2973a1a23e24c46831876c'
    text = load_page(args.source_dir / 'bcpc-2025-26.pdf', pension_hash, 56)
    pension = [
        ['Laura Nashman', 'Chief executive officer', 460000, 45310],
        ['Joel Levinson', 'Vice-president, Information and Technology Services, and chief information officer', 299190, 29470],
        ['Aaron Walker-Duncan', 'Vice-president, Member and Employer Experience', 283168, 27892],
        ['Trevor Fedyna', 'Vice-president, Strategy and Insights, and chief financial officer', 273600, 26950],
        ['Karlena Lewis', 'General counsel and privacy officer', 273600, 26950],
        ['Erika Taylor', 'Vice-president, People and Culture', 254626, 25081],
        ['Renee Bilodeau', 'Vice-president, Board and Communication Services', 220000, 21670]
    ]
    records = []
    for name, position, base, pension_contribution in pension:
        if name not in text or any(f'{value:,}' not in text for value in [base, pension_contribution]):
            raise ValueError(f'Pension table transcription changed: {name}')
        records.append({'nameAsPublished': name, 'position': position, 'baseSalary': base, 'employerPensionContributions': pension_contribution,
                        'currency': 'CAD', 'totalRemuneration': None, 'physicalPdfPage': 56,
                        'notes': ['Base salary is prorated following an August 3, 2025 salary change.'] if name == 'Renee Bilodeau' else []})
    entry = {'id': 'bc-pension-executives-2025-26', 'employerSlug': 'bc-pension-corporation', 'year': '2025/26',
             'scope': 'executive-base-salary-and-pension', 'status': 'reviewed-executive-components-staged', 'acceptedForEmployeeBuild': False,
             'rowCount': 7, 'candidateFile': 'bc-pension-executives-2025-26.json', 'sha256': pension_hash, 'pdfPage': 56,
             'url': 'https://www.bcpensioncorp.ca/documents/d/corporate/bcpc-annual-report-2026-25',
             'notes': ['Base salary and employer pension contributions are separate components. No complete remuneration amount is supplied.',
                       'The footnote identifies other benefits, vehicle allowances and possible unused-vacation payments; no unreported amounts are inferred.']}
    write(args.out / entry['candidateFile'], {'source': entry, 'rows': records})
    manifest.append(entry)
    write(args.out / 'staging-manifest.json', {'reviewed': '2026-10-30', 'sources': manifest,
          'productionRowsAdded': 0, 'nextAction': 'Obtain all-employee disclosures, or add an explicitly separate executive-component view with row currencies before publication.'})
    print(json.dumps({'stagedExecutiveRows': 17, 'employeeRowsAdded': 0, 'currenciesPreserved': ['CAD', 'USD']}))


if __name__ == '__main__':
    main()
