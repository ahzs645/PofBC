"""Build regional-district manifest, data and evidence files from dual-engine extraction outputs."""
import sys, os, json, gzip, re, subprocess, hashlib, io
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rdlib import to_amount, DASH, sha256_file, layout_page

SCR = os.path.dirname(HERE)
RD = os.path.join(SCR, 'rd')
OUT = os.path.join(SCR, 'out-rd')
DEST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTION = 'regional-districts'

ENG = {
    'pdftotext': subprocess.run(['pdftotext', '-v'], capture_output=True, text=True).stderr.splitlines()[0].strip(),
    'pdfplumber': __import__('pdfplumber').__version__,
}

RDS = {
    'cvrd': dict(slug='cowichan-valley-regional-district', name='Cowichan Valley Regional District',
                 index='https://cvrd.ca/government-administration/finance/financial-statements/statements-of-financial-information/',
                 urls={2023: 'https://cvrd.ca/wp-content/uploads/2025/09/Clean-signed-2023-SOFI-report_202406271216203550.pdf',
                       2024: 'https://cvrd.ca/wp-content/uploads/2026/05/2024-SOFI-Report-FINAL.pdf',
                       2025: 'https://cvrd.ca/wp-content/uploads/2026/06/2025-Final-SOFI-Report.pdf'},
                 nameDisclosure='surname-initial', conf='cvrd.json'),
    'tnrd': dict(slug='thompson-nicola-regional-district', name='Thompson-Nicola Regional District',
                 index='https://www.tnrd.ca/services/budget-finance/annual-financial-reports/',
                 urls={2023: 'https://wpcdn.tnrd.ca/wp-content/uploads/2024/06/21115159/TNRD-Statements-and-Schedules-of-Financial-Information-2023.pdf',
                       2024: 'https://wpcdn.tnrd.ca/wp-content/uploads/2025/08/15101915/TNRD-Statements-and-Schedules-of-Financial-Information-2024-signed-revised.pdf',
                       2025: 'https://wpcdn.tnrd.ca/wp-content/uploads/2026/07/08092006/TNRD-2025-Statement-of-Financial-Information-Signed.pdf'},
                 nameDisclosure='surname-given-name', conf='tnrd.json'),
    'rdn': dict(slug='regional-district-of-nanaimo', name='Regional District of Nanaimo',
                index='https://rdn.bc.ca/financial-reports',
                urls={2023: 'https://rdn.bc.ca/sites/default/files/inline-files/2023%20Statement%20of%20Financial%20Information%281%29.pdf',
                      2024: 'https://rdn.bc.ca/sites/default/files/inline-files/2024%20Statement%20of%20Financial%20Information_0.pdf',
                      2025: 'https://rdn.bc.ca/sites/default/files/2025%20Statement%20of%20Financial%20Information.pdf'},
                nameDisclosure='surname-initial', conf='rdn.json'),
    'rdno': dict(slug='regional-district-of-north-okanagan', name='Regional District of North Okanagan',
                 index=None,
                 urls={2023: 'https://www.rdno.ca/sites/default/files/2024-06/240619_RPT_SOFI_signed.pdf',
                       2024: 'https://www.rdno.ca/sites/default/files/2025-06/250618_RPT_SOFI_2024_signed.pdf',
                       2025: 'https://www.rdno.ca/sites/default/files/2026-06/260617_RPT_SOFI_2025_signed.pdf'},
                 nameDisclosure='surname-given-name', conf='rdno.json'),
}

# remuneration column, expenses column, named-control label regex + cell indexes, threshold info, under-threshold/total labels
SPEC = {
    ('cvrd', 'elected'): dict(rem='remuneration', exp='expenses', ctl=r'^$', ctlIdx=(0, 1),
                              ctlBasis='Printed board schedule total line (unlabelled, directly below the named rows).'),
    ('cvrd', 'employees'): dict(rem='remuneration', exp='expenses', ctl=r'^Subtotal$', ctlIdx=(0, 1),
                                under=r'^Consolidated total of employees earning less than', underIdx=(0, 1), total=r'^Total Remuneration and Expenses for Employees$', totalIdx=(0, 1),
                                threshold=75000, cmp='>', thresholdText='EARNINGS GREATER THAN $75,000'),
    ('tnrd', 'elected'): dict(rem='remuneration', exp='expenses', ctl=r'^Consolidated total, elected', ctlIdx=(0, 1),
                              ctlBasis='Printed "Consolidated total, elected officals" line.'),
    ('tnrd', 'employees'): dict(rem='total', exp='expenses', ctl=r'^Total, employees earning \$75,000 or more$', ctlIdx=(2, 3),
                                under=r'^Consolidated total, employees earning \$75,000 or less$', underIdx=(2, 3), total=r'^Total$', totalIdx=(2, 3),
                                threshold=75000, cmp='>=', thresholdText='Total, employees earning $75,000 or more'),
    ('rdn', 'elected'): dict(rem='remuneration', exp='expenses', ctl=r'^Total Remuneration and Expenses$', ctlIdx=(0, 1),
                             ctlBasis='Printed "Total Remuneration and Expenses" line.'),
    ('rdn', 'employees'): dict(rem='total', exp='expenses', ctl=r'Individual', ctlIdx=(-2, -1),
                               under=r'Summary', underIdx=(-2, -1), total=r'^Total Remuneration and Expenses Paid$', totalIdx=(-2, -1),
                               threshold=75000, cmp='>', thresholdText='Total Individual Remuneration Paid over $75,000'),
    ('rdno', 'elected'): dict(rem='remuneration', exp='expenses', ctl=r'^Total$', ctlIdx=(0, 1),
                              ctlBasis='Printed "Total" line of the Board of Directors and Alternate Directors schedule.'),
    ('rdno', 'employees'): dict(rem='remuneration', exp='expenses', ctl=r'^SUBTOTAL$', ctlIdx=(0, 1),
                                under=r'^Employees Under', underIdx=(0, 1), total=r'^TOTAL$', totalIdx=(0, 1),
                                threshold=75000, cmp='>', thresholdText='Covering staff report: schedule of each employee whose remuneration "exceeds $75,000"; consolidated line "Employees Under $75,000"'),
}

EXTRA_NOTES = {
    ('cvrd', 2023, 'elected'): ['Printed footnotes: "* Director term ended in November 2022"; "** Director term with the CVRD ended in November 2023". Markers are kept in evidence and omitted from the normalized position.'],
    ('cvrd', 2024, 'elected'): ['Printed footnotes: "* Chair/Director term with the CVRD ended in November 2024"; "** Director term with the CVRD ended in November 2024". Markers are kept in evidence and omitted from the normalized position.',
                                'A stray lone dash is printed on its own line between the director and alternate blocks; it belongs to no named row and is recorded in evidence.'],
    ('cvrd', 2025, 'elected'): ['Printed footnotes: "* Director term with the CVRD ended in March 2025"; "** ... ended in November 2025"; "*** ... ended in June 2025". Markers are kept in evidence and omitted from the normalized name.'],
    ('tnrd', 2024, 'employees'): ['This is the revised signed 2024 SOFI; its approval page states it was re-approved by the Board on August 14, 2025 after a clerical error in the June 26, 2025 submission.'],
    ('rdno', 2023, 'employees'): ['The 2023 schedule prints a separate "Employer portion of CPP and EI premiums" expense-column line (479,614) included in the printed TOTAL; it is not a named row.'],
}


def gz(obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0, compresslevel=9, filename='') as f:
        f.write(raw)
    return buf.getvalue()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def find_ctl(controls, pat):
    hits = [c for c in controls if re.search(pat, c['label'].strip())]
    if len(hits) != 1:
        raise ValueError(f'control {pat!r}: {len(hits)} hits in {controls}')
    c = hits[0]
    cells = [x for x in c['cells'] if not re.fullmatch(r'\$?75,000', x) and not re.fullmatch(r'\d', x)]
    return c, cells


def fnum(d):
    if d is None:
        return None
    f = float(d)
    return int(f) if f == int(f) and False else round(f, 2)


def main():
    os.makedirs(os.path.join(DEST, 'evidence'), exist_ok=True)
    sources, readme = [], []
    for rd, meta in RDS.items():
        for year in (2023, 2024, 2025):
            for kind in ('elected', 'employees'):
                sid_local = f'{rd}-{year}-{kind}'
                outp = os.path.join(OUT, sid_local + '.json')
                r = subprocess.run(['python3', '-I', os.path.join(HERE, 'extract.py'), os.path.join(HERE, meta['conf']), sid_local, outp],
                                   capture_output=True, text=True)
                if r.returncode:
                    raise SystemExit(r.stderr)
                ex = json.load(open(outp))
                spec = SPEC[(rd, kind)]
                conf = json.load(open(os.path.join(HERE, meta['conf'])))[sid_local]
                pdf = os.path.join(RD, f'{rd}-{year}.pdf')
                pdf_sha = sha256_file(pdf)
                scope = 'elected-officials' if kind == 'elected' else 'employee-remuneration'
                file_base = f"{meta['slug']}-{year}-{scope}"
                source_id = f'{COLLECTION}-{file_base}'
                problems = list(ex['diffs'])
                if ex['rowsA'] != ex['rowsB']:
                    problems.append('engine row counts differ')
                # controls agree across engines
                norm = lambda cs: [x for x in cs if not re.fullmatch(r'\$?75,000', x) and not re.fullmatch(r'\d', x)]
                ca = [(c['page'], norm(c['cells'])) for c in ex['controlsA']]
                cb = [(c['page'], norm(c['cells'])) for c in ex['controlsB']]
                if ca != cb:
                    problems.append(f'printed control cells differ between engines: {ca} vs {cb}')
                # year stated on schedule page(s)
                for pg in conf['pages']:
                    txt = '\n'.join(layout_page(conf.get('pdfLayout', pdf), pg))
                    if str(year) not in txt and pg == conf['pages'][0]:
                        problems.append(f'year {year} not printed on schedule page {pg}')
                rows, held, literal = [], [], []
                internal = []
                for i, row in enumerate(ex['rows']):
                    cells = row['cells']
                    vals = {k: (to_amount(v) if v is not None else None) for k, v in cells.items()}
                    lit = {'name': row['name'], 'position': row['position'], 'cells': cells, 'physicalPage': row['page']}
                    if row.get('area') is not None:
                        lit['area'] = row['area']
                    if row['footnoteMark']:
                        lit['footnoteMark'] = row['footnoteMark']
                    if row['flags']:
                        lit['layoutSplitByCharacterColumn'] = True
                    literal.append(lit)
                    rem, exp = vals[spec['rem']], vals[spec['exp']]
                    # component consistency (published components vs published total)
                    if rd == 'tnrd' and kind == 'employees':
                        comp = (vals['operational'] or 0) + (vals['emergency'] or 0)
                        if abs(comp - vals['total']) > 1:
                            internal.append({'name': row['name'], 'componentsSum': str(comp), 'printedTotal': cells['total']})
                    if rd == 'rdn' and kind == 'employees':
                        comp = sum((vals[c] or 0) for c in conf['columns'] if c not in ('total', 'expenses'))
                        if comp != vals['total']:
                            internal.append({'name': row['name'], 'componentsSum': str(comp), 'printedTotal': cells['total']})
                    if rem is None:
                        held.append({**lit, 'reason': 'Remuneration cell is a printed dash with no zero legend; row held from normalized payments rather than treated as zero.'})
                        continue
                    rows.append([meta['slug'], row['name'], row['position'], fnum(rem), fnum(exp), row['page']])
                # reconciliation
                ctl, cells = find_ctl(ex['controlsA'], spec['ctl'])
                p_rem, p_exp = to_amount(cells[spec['ctlIdx'][0]]), to_amount(cells[spec['ctlIdx'][1]])
                named_rem = sum((Decimal(str(x[3])) for x in rows), Decimal(0))
                named_exp = sum((Decimal(str(x[4])) for x in rows if x[4] is not None), Decimal(0))
                held_exp = sum((to_amount(h['cells'][spec['exp']]) or 0 for h in held), Decimal(0))
                tol = Decimal('0.5') * (len(rows) + len(held))
                recon = [{'field': 'remuneration', 'printedControl': float(p_rem), 'printedControlLabel': ctl['label'] or '(unlabelled total line)',
                          'physicalPage': ctl['page'], 'namedRowSum': float(named_rem), 'residual': float(named_rem - p_rem),
                          'heldRowCells': 0, 'withinWholeDollarRounding': abs(named_rem - p_rem) <= tol},
                         {'field': 'expenses', 'printedControl': float(p_exp), 'printedControlLabel': ctl['label'] or '(unlabelled total line)',
                          'physicalPage': ctl['page'], 'namedRowSum': float(named_exp), 'heldRowExpenses': float(held_exp),
                          'residual': float(named_exp + held_exp - p_exp), 'dashExpenseCellsCountedAsNull': sum(1 for x in rows if x[4] is None),
                          'withinWholeDollarRounding': abs(named_exp + held_exp - p_exp) <= tol}]
                if 'under' in spec:
                    uc, ucells = find_ctl(ex['controlsA'], spec['under'])
                    tc, tcells = find_ctl(ex['controlsA'], spec['total'])
                    # under-threshold line cells: label-less lines in layout have '$75,000' stripped above
                    ui = spec['underIdx']
                    u_rem, u_exp = to_amount(ucells[ui[0]]), to_amount(ucells[ui[1]])
                    t_rem, t_exp = to_amount(tcells[spec['totalIdx'][0]]), to_amount(tcells[spec['totalIdx'][1]])
                    recon.append({'field': 'remuneration', 'basis': 'printed total less consolidated under-threshold line',
                                  'printedTotal': float(t_rem), 'printedUnderThreshold': float(u_rem), 'printedTotalLessUnder': float(t_rem - u_rem),
                                  'namedRowSum': float(named_rem), 'residual': float(named_rem - (t_rem - u_rem)),
                                  'withinWholeDollarRounding': abs(named_rem - (t_rem - u_rem)) <= tol})
                    if not (rd == 'rdno' and year == 2023):
                        recon.append({'field': 'expenses', 'basis': 'printed total less consolidated under-threshold line',
                                      'printedTotal': float(t_exp), 'printedUnderThreshold': float(u_exp), 'printedTotalLessUnder': float(t_exp - u_exp),
                                      'namedRowSum': float(named_exp), 'residual': float(named_exp - (t_exp - u_exp)),
                                      'withinWholeDollarRounding': abs(named_exp - (t_exp - u_exp)) <= tol})
                primary_ok = recon[0]['withinWholeDollarRounding'] and recon[1]['withinWholeDollarRounding']
                if not primary_ok:
                    problems.append('named rows do not reconcile to the printed control: ' + '; '.join(
                        f"{c['field']} rows sum {c['namedRowSum']:,.2f} vs printed {c['printedControl']:,.2f} (residual {c['residual']:+,.2f}, beyond whole-dollar rounding)"
                        for c in recon[:2] if not c['withinWholeDollarRounding']) + '. Both engines read the same rows and printed total; no missing, hidden or unclassified row was found, so the cause is not determinable from the document and no row or amount is inferred.')
                status = 'accepted' if not problems else 'held-for-review'
                # threshold sanity (employees)
                below = []
                if kind == 'employees':
                    below = [x[1] for x in rows if (Decimal(str(x[3])) <= 75000 if spec['cmp'] == '>' else Decimal(str(x[3])) < 75000)]
                    if below:
                        problems.append(f'rows at/below threshold: {below}')
                        status = 'held-for-review'
                data_bytes = gz(rows)
                ev = {
                    'sourceId': source_id, 'sourceSha256': pdf_sha, 'sourceUrl': meta['urls'][year], 'sourceIndexUrl': meta['index'],
                    'year': str(year), 'periodType': 'calendar', 'scope': scope, 'physicalPages': conf['pages'],
                    'columns': conf['columns'], 'remunerationColumn': spec['rem'], 'expensesColumn': spec['exp'],
                    'extraction': {
                        'engineA': {'tool': ENG['pdftotext'], 'mode': 'pdftotext -layout, rows split on runs of 2+ spaces, numeric cells assigned by count with a documented blank-cell rule'},
                        'engineB': {'tool': f"pdfplumber {ENG['pdfplumber']}", 'mode': 'extract_words grouped by baseline, numeric cells assigned to columns by clustering right edges of printed numbers on each page'},
                        'rowByRowAgreement': not ex['diffs'], 'rowsEngineA': ex['rowsA'], 'rowsEngineB': ex['rowsB'],
                        'unclassifiedLinesInsideTable': {'engineA': ex['orphansA'], 'engineB': ex['orphansB']},
                    },
                    'printedControls': ex['controlsA'],
                    'reconciliation': recon,
                    'publishedComponentInconsistencies': internal,
                    'heldRows': held,
                    'literalRows': literal,
                }
                if conf.get('pdfLayout'):
                    ev['extraction']['engineA']['input'] = {
                        'note': 'The signed PDF carries two text layers: the original schedule text and a duplicate Helvetica overlay added by the signing/scanning step, which interleaves every line in poppler output. Engine A ran on a derived copy with only the Helvetica text objects removed (pypdf content-stream filter, nothing else altered); engine B ran on the original file with Helvetica characters filtered out.',
                        'derivedSha256': sha256_file(conf['pdfLayout'])}
                ev_bytes = gz(ev)
                notes = []
                if kind == 'employees':
                    notes.append(f"Named employee cohort as printed ({spec['thresholdText']}). Remuneration is the published "
                                 + ('Total Remuneration column; component columns are retained in evidence only.' if spec['rem'] == 'total' else 'Remuneration column.'))
                else:
                    notes.append('Board directors and alternate directors as printed. Not a complete employee schedule.')
                if rd == 'rdno' and kind == 'elected':
                    notes.append('The schedule prints Position and Area as separate columns; the normalized position is the literal Position cell and the Area cell is kept in evidence.')
                if rd == 'tnrd' and kind == 'employees':
                    notes.append('Blank Emergency Response cells are left blank in evidence; Total Remuneration is the published field imported.')
                notes.append('Expense cells printed as a dash have no zero legend and remain null.')
                notes += EXTRA_NOTES.get((rd, year, kind), [])
                if held:
                    notes.append(f"{len(held)} named row(s) print a dash for remuneration ({', '.join(h['name'] for h in held)}); held from normalized payments and kept in evidence; their expenses are counted in the expense reconciliation.")
                if internal:
                    notes.append(f'{len(internal)} row(s) print components that do not sum to the printed total; the printed total is imported unchanged (see evidence).')
                res_txt = '; '.join(f"{c['field']} {c['residual']:+.2f}" for c in recon[:2])
                warning = ('These are published payment disclosures, not a complete workforce roster or an annualized base salary rate. '
                           + ('Names are printed as surname and initial only. ' if meta['nameDisclosure'] == 'surname-initial' else '')
                           + 'Expense dashes remain unknown rather than zero. '
                           + f'Named row sums minus the printed named control: {res_txt} CAD. '
                           + ('Held dash-remuneration rows are not shown as zero payments. ' if held else ''))
                entry = {
                    'id': source_id, 'employerSlug': meta['slug'], 'employerName': meta['name'], 'sector': 'Municipalities',
                    'governanceType': 'regional-district', 'year': str(year), 'periodType': 'calendar',
                    'periodStart': f'{year}-01-01', 'periodEnd': f'{year}-12-31',
                    'sourceUrl': meta['urls'][year], 'sourceIndexUrl': meta['index'], 'sha256': pdf_sha,
                    'file': f'{file_base}.json.gzip', 'dataSha256': sha(data_bytes),
                    'provenanceFile': f'evidence/{file_base}.json.gzip', 'provenanceSha256': sha(ev_bytes),
                    'category': scope, 'scope': scope,
                    'title': f"{meta['name']} {year} " + ('Board Director Remuneration and Expenses' if kind == 'elected' else 'Employee Remuneration and Expenses'),
                    'status': status, 'verified': status == 'accepted', 'sourceKind': 'official',
                    'rowCount': len(rows), 'totalRemuneration': float(named_rem), 'totalExpenses': float(named_exp),
                    'pages': conf['pages'], 'currency': 'CAD', 'amountUnit': 'dollars',
                    'threshold': spec.get('threshold'), 'thresholdComparison': spec.get('cmp'),
                    'completeEmployeeSchedule': kind == 'employees', 'nameDisclosure': meta['nameDisclosure'],
                    'notes': notes, 'publicWarning': warning,
                    'validation': {
                        'method': 'Two independent native-text extractions (poppler pdftotext -layout and pdfplumber word geometry) agree row-for-row on page, name, position, footnote markers and every numeric cell; every non-row line inside the table region is listed in evidence; named row sums are reconciled to the printed controls without adjusting any cell.',
                        'engines': [ENG['pdftotext'], f"pdfplumber {ENG['pdfplumber']}"],
                        'pages': conf['pages'], 'rowsEngineA': ex['rowsA'], 'rowsEngineB': ex['rowsB'], 'rowByRowAgreement': not ex['diffs'],
                        'heldRows': len(held), 'printedControls': recon, 'publishedComponentInconsistencies': len(internal),
                        'reportingYearReadFromSchedule': True, 'textLayer': 'native', 'ocr': False, 'problems': problems,
                    },
                }
                if status != 'accepted':
                    entry['holdReason'] = '; '.join(problems)
                    entry.pop('file'); entry.pop('dataSha256')
                else:
                    open(os.path.join(DEST, entry['file']), 'wb').write(data_bytes)
                open(os.path.join(DEST, entry['provenanceFile']), 'wb').write(ev_bytes)
                sources.append(entry)
                print(f"{source_id}: {status} rows={len(rows)} held={len(held)} rem={named_rem} exp={named_exp} recon={[ (c['field'], c['residual']) for c in recon]} internal={len(internal)} problems={problems}")
    manifest = {'version': 1, 'collection': COLLECTION,
                'coverageNotes': ['Regional district SOFI schedules (calendar years 2023-2025) for Cowichan Valley, Thompson-Nicola, Nanaimo and North Okanagan, imported from the official signed PDFs with dual-engine native-text extraction.',
                                  'Regional districts are filed under the Municipalities sector, matching existing regional-district sources.'],
                'sources': sources}
    json.dump(manifest, open(os.path.join(SCR, 'sources-draft.json'), 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
