#!/usr/bin/env python3
"""Reproduce six original-PDF employee cohorts using independent native readers.

Only public report download controls are submitted. No contact/request forms are
used. Frozen PDF hashes, complete schedule page sequences, every extracted row,
and printed controls must pass before accepted artifacts can be written.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import http.cookiejar
import json
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/follow-through-worksafe-uvic'
CACHE = Path('/workspace/salary-source-follow-through/cache-worksafe-uvic')
SCHEMA = ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage']
AMOUNT = r'(?:\d{1,3}(?:,\d{3})+|\d+)'
EXPENSE = rf'(?:{AMOUNT}|\({AMOUNT}\)|-)'
PAIR = re.compile(rf'(?P<name>[^\d$]*?[^\d$\s])\s{{2,}}(?P<pay>{AMOUNT})\s*\*?\s+(?P<expense>{EXPENSE})\s*(?P<marks>\*{{1,2}})?(?=\s{{2,}}|$)')
SPECS = [
    ('worksafebc-2023', 'workers-compensation-board', 'WorkSafeBC', '2023', 188, 92, 154, '3e2c0e586e82c7a75d3862500b658e04885b8f4ce4b2c5a2a3d37b272702d9b5', 314770529, 8978354, 77716670, 713046, 392487199, 9691400),
    ('worksafebc-2024', 'workers-compensation-board', 'WorkSafeBC', '2024', 188, 83, 155, '3768fe7517f5c2f8d29205bd5693a1e4d953f975ca6f713461fe16de408198d6', 352595962, 9350905, 68254308, 853105, 420850270, 10204010),
    ('worksafebc-2025', 'workers-compensation-board', 'WorkSafeBC', '2025', 176, 76, 144, '73c5d7d0d34d9b4a130b162246a4b83b23397d3583b585ae974d36ac1fd575cd', 364916347, 9418860, 73239402, 1198653, 438155749, 10617513),
    ('uvic-2019-20', 'university-of-victoria', 'University of Victoria', '2019/20', 69, 46, 61, 'f3fb502f822cb0e03d66140973e0f260a85af8914bc5707f571bf1264c0c8d14', 173318599, 7395619, 154121279, None, 327439878, None),
    ('uvic-2023-24', 'university-of-victoria', 'University of Victoria', '2023/24', 79, 49, 71, '8b31ea1f3e7947ffc56bf2f9173fbf641174f81e87bbf742298db70f99ee1afa', 271654817, 9443940, 153731327, None, 425386143, None),
    ('uvic-2024-25', 'university-of-victoria', 'University of Victoria', '2024/25', 80, 48, 71, 'da1da55ae56230621b5a4ac1e012439e01db5e98294a4d42f3111b6fea7ff21a', 290029648, 9990395, 145082627, None, 435112275, None),
]
REVIEWED = {
    'worksafebc-2023': (2794, 314770541, 8978370, 12, 16, 45, 45, 4),
    'worksafebc-2024': (3058, 352595961, 9350896, -1, -9, 42, 42, 34),
    'worksafebc-2025': (3142, 364916358, 9418862, 11, 2, 46, 46, 14),
    'uvic-2019-20': (1422, 173318599, 7395619, 0, 0, 62, 94, 44),
    'uvic-2023-24': (2072, 271654816, 9443940, -1, 0, 64, 94, 34),
    'uvic-2024-25': (2227, 290029647, 9990395, -1, 0, 64, 96, 51),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def packed(value):
    raw = (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    return raw, gzip.compress(raw, compresslevel=9, mtime=0)


def money(value):
    if value in ('', '-', '–', '—'):
        return None
    if not re.fullmatch(EXPENSE, value):
        raise ValueError(f'Unexpected amount cell {value!r}')
    return int(value.replace(',', '').replace('(', '-').replace(')', ''))


def name(value):
    return ' '.join(value.split())


def specs():
    keys = ['key', 'employerSlug', 'employerName', 'year', 'pdfPages', 'firstPage', 'lastPage', 'sha256', 'printedNamedRemuneration', 'printedNamedExpenses', 'printedBelowRemuneration', 'printedBelowExpenses', 'printedGrandRemuneration', 'printedGrandExpenses']
    return [dict(zip(keys, row)) for row in SPECS]


def public_source(s):
    if s['key'].startswith('worksafe'):
        return 'https://www.worksafebc.com/en/resources/about-us/statements-of-financial-information/' + s['year'] + '-statement-financial-information?lang=en'
    return {
        '2019/20': 'https://www.uvic.ca/financialplanning/assets/docs/financial-reporting-docs/uvicfinancialstatements/FIA-2019-20.pdf',
        '2023/24': 'https://www.uvic.ca/financialplanning/assets/docs/financial-reporting-docs/university-of-victoria-financial-information-act-year-ended-202324-statement-of-financial-information.pdf',
        '2024/25': 'https://www.uvic.ca/financialplanning/assets/docs/financial-reporting-docs/statement-of-financial-information-2024-25.pdf',
    }[s['year']]


def fetch(s, cache):
    path = cache / ('additional-source-' + s['key'] + '.pdf')
    if not path.exists():
        cache.mkdir(parents=True, exist_ok=True)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        url = public_source(s)
        with opener.open(url, timeout=90) as response:
            data = response.read()
        if not data.startswith(b'%PDF'):
            html = data.decode()
            token = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', html).group(1)
            media = re.search(r'name="mediaItem" type="submit" value="([^"]+)"', html).group(1)
            request = urllib.request.Request(url, data=urllib.parse.urlencode({'__RequestVerificationToken': token, 'mediaItem': media}).encode(), headers={'Referer': url})
            with opener.open(request, timeout=90) as response:
                data = response.read()
        if not data.startswith(b'%PDF') or digest(data) != s['sha256']:
            raise ValueError('Downloaded original PDF fingerprint mismatch: ' + s['key'])
        path.write_bytes(data)
    if digest(path.read_bytes()) != s['sha256']:
        raise ValueError('Cached original PDF fingerprint mismatch: ' + s['key'])
    return path


def parse_layout(pages, s):
    """Parse Poppler physical-layout text, independently of PyMuPDF geometry."""
    result = []
    for page in range(s['firstPage'], s['lastPage'] + 1):
        for line in pages[page - 1].splitlines():
            if line.lstrip().startswith('Total'):
                continue
            for match in PAIR.finditer(line):
                employee = name(match['name'])
                if employee.startswith('Total'):
                    continue
                if ',' not in employee and money(match['pay']) >= 75000:
                    raise ValueError(f'Unclassified native row: {employee}')
                if ',' not in employee:
                    continue
                pay = money(match['pay'])
                if pay < 75000:
                    raise ValueError(f'Unexpected below-threshold named row: {employee}')
                result.append([s['employerSlug'], employee, None, pay, money(match['expense']), page])
    return sorted(result, key=lambda row: (row[5], row[1], row[3], row[4] or -1))


def parse_coordinates(doc, s):
    """Read each name/amount directly from the original PDF word coordinates."""
    rows, evidence = [], []
    uvic = s['key'].startswith('uvic')
    bands = [(45, 185, 240, 300), (310, 445, 500, 570)] if uvic else [(45, 390, 460, 570)]
    for page in range(s['firstPage'], s['lastPage'] + 1):
        words = doc[page - 1].get_text('words')
        for low, pay_start, expense_start, high in bands:
            for w in words:
                if not (pay_start <= w[0] < expense_start and re.fullmatch(AMOUNT, w[4]) and money(w[4]) >= 75000):
                    continue
                aligned = sorted((v for v in words if abs(v[1] - w[1]) < 1.6 and low <= v[0] < high), key=lambda v: v[0])
                named = [v for v in aligned if v[0] < pay_start]
                employee = name(' '.join(v[4] for v in named))
                if employee.startswith('Total'):
                    continue
                if (page == s['lastPage'] and employee in ('', '< $75,000 $')
                        and money(w[4]) in (s['printedBelowRemuneration'], s['printedGrandRemuneration'])):
                    # UVic's wrapped final-page subtotal labels are on the
                    # neighboring baseline. These exact original controls are
                    # independently verified in both full source-page readers.
                    continue
                if ',' not in employee:
                    raise ValueError(f'Unclassified coordinate row: {s["key"]} p{page}: {employee}')
                amounts = [v for v in aligned if expense_start <= v[0] < high and v[4] not in ('*', '**')]
                if len(amounts) != 1:
                    raise ValueError(f'Unexpected expense geometry: {s["key"]} p{page} {employee}: {amounts}')
                expense = money(amounts[0][4])
                row = [s['employerSlug'], employee, None, money(w[4]), expense, page]
                rows.append(row)
                evidence.append({'row': row, 'nameWords': [{'text': v[4], 'bbox': [round(z, 3) for z in v[:4]]} for v in named], 'nameBbox': [round(min(v[0] for v in named), 3), round(w[1], 3), round(max(v[2] for v in named), 3), round(w[3], 3)], 'remunerationCell': {'text': w[4], 'bbox': [round(v, 3) for v in w[:4]]}, 'expenseCell': {'text': amounts[0][4], 'bbox': [round(v, 3) for v in amounts[0][:4]]}, 'footnoteMarkers': [v[4] for v in aligned if v[4] in ('*', '**')]})
    return sorted(rows, key=lambda row: (row[5], row[1], row[3], row[4] or -1)), evidence


def analyze(s, cache):
    path = fetch(s, cache)
    doc = fitz.open(path)
    if len(doc) != s['pdfPages']:
        raise ValueError('Physical page count changed')
    text = subprocess.check_output(['pdftotext', '-layout', str(path), '-']).decode()
    pages = text.split('\f')
    if not pages[-1].strip():
        pages.pop()
    assert len(pages) == len(doc)
    endyear = s['year'] if '/' not in s['year'] else '20' + s['year'].split('/')[1]
    period_header = ('FOR THE YEAR OF ' if s['key'].startswith('worksafe') else 'YEAR ENDED MARCH 31, ') + endyear
    for page in range(s['firstPage'], s['lastPage'] + 1):
        assert period_header in pages[page - 1].upper(), (s['key'], page)
        assert ('EACH EMPLOYEE' if s['key'].startswith('worksafe') else 'EMPLOYEES') in pages[page - 1].upper()
    # Board is immediately before and supplier/severance is immediately after.
    assert ('BOARD' in pages[s['firstPage'] - 2].upper())
    assert ('SEVERANCE' if s['key'].startswith('worksafe') else 'GOODS AND SERVICES') in pages[s['lastPage']].upper()
    primary, evidence = parse_coordinates(doc, s)
    independent = parse_layout(pages, s)
    a, b = Counter(map(tuple, primary)), Counter(map(tuple, independent))
    if a != b:
        raise ValueError(json.dumps({'source': s['key'], 'coordinateOnly': list((a-b).elements())[:20], 'layoutOnly': list((b-a).elements())[:20], 'coordinateCount':len(primary), 'layoutCount':len(independent)}, ensure_ascii=False))
    for key in ['printedNamedRemuneration', 'printedNamedExpenses', 'printedBelowRemuneration', 'printedBelowExpenses', 'printedGrandRemuneration', 'printedGrandExpenses']:
        if s[key] is not None:
            assert f'{s[key]:,}' in pages[s['lastPage'] - 1], (s['key'], key)
            assert f'{s[key]:,}' in doc[s['lastPage'] - 1].get_text(), (s['key'], key, 'coordinates-reader-control')
    totals = [sum(r[i] or 0 for r in primary) for i in (3, 4)]
    checks = {'independentReaders': ['PyMuPDF original PDF words and coordinates', 'Poppler pdftotext -layout'], 'independentlyComparedRows': len(primary), 'allRowsCheckedAgainstPdfCoordinates': True, 'completeEmployeeSchedule': True, 'physicalPdfPages': list(range(s['firstPage'], s['lastPage']+1)), 'sourceRowsPerPhysicalPage': dict(sorted(Counter(r[5] for r in primary).items())), 'totalRemuneration': totals[0], 'totalKnownExpenses': totals[1], 'printedNamedRemuneration': s['printedNamedRemuneration'], 'printedNamedExpenses': s['printedNamedExpenses'], 'remunerationDifference':totals[0]-s['printedNamedRemuneration'], 'expensesDifference':totals[1]-s['printedNamedExpenses'], 'missingExpenseRows':sum(r[4] is None for r in primary), 'explicitZeroExpenseRows':sum(r[4] == 0 for r in primary), 'duplicateNamesPreserved': {k:v for k,v in Counter(r[1] for r in primary).items() if v>1}, 'duplicateExactRowsPreserved':sum(v-1 for v in Counter(tuple(r[1:5]) for r in primary).values() if v>1), 'printedNamedPlusBelowMinusGrandRemuneration': s['printedNamedRemuneration']+s['printedBelowRemuneration']-s['printedGrandRemuneration'], 'printedNamedPlusBelowMinusGrandExpenses': None if s['printedBelowExpenses'] is None else s['printedNamedExpenses']+s['printedBelowExpenses']-s['printedGrandExpenses']}
    checks.update({k:s[k] for k in ['printedBelowRemuneration','printedBelowExpenses','printedGrandRemuneration','printedGrandExpenses']})
    checks['negativeExpenseRows'] = sum(r[4] is not None and r[4] < 0 for r in primary)
    checks['atThresholdRows'] = sum(r[3] == 75000 for r in primary)
    expected = REVIEWED[s['key']]
    assert (len(primary), *totals, checks['remunerationDifference'], checks['expensesDifference']) == expected[:5], 'Reviewed row/control census changed'
    actual_counts = list(checks['sourceRowsPerPhysicalPage'].values())
    assert actual_counts == [expected[5]] + [expected[6]] * (s['lastPage']-s['firstPage']-1) + [expected[7]], 'Complete original-row census changed'
    checks['sourceRowCensusExact'] = True
    checks['roundingComparisonOnly'] = {'remunerationUpperBound': (len(primary)+1)/2, 'knownExpensesUpperBound': (sum(r[4] is not None for r in primary)+1)/2, 'causeEstablished':False, 'valuesAdjusted':False}
    return path, doc, pages, primary, evidence, checks


def duplicate_inventory():
    """Inspect accepted original manifests, not compiled partitions."""
    findings, manifests = [], []
    wanted = {s['employerSlug'] for s in specs()}
    for p in sorted((ROOT / 'research/salaries').glob('*/sources.json')):
        if p.parent == OUT:
            continue
        raw = p.read_bytes()
        manifests.append({'path':str(p.relative_to(ROOT)), 'sha256':digest(raw)})
        for source in json.loads(raw).get('sources', []):
            if source.get('status') not in (None, 'accepted', 'verified', 'imported'):
                continue
            if source.get('employerSlug') in wanted:
                findings.append({'path':str(p.relative_to(ROOT)), 'id':source['id'], 'year':source.get('year'), 'sha256':source.get('sha256'), 'category':source.get('category')})
    matches = [f for f in findings if any(f['year']==s['year'] and (f.get('sha256')==s['sha256'] or f.get('category')=='employee-remuneration') for s in specs())]
    if matches:
        raise ValueError('Existing accepted original cohort overlaps: '+json.dumps(matches))
    return {'checkedOn':'2026-11-02','method':'All existing research/salaries/*/sources.json accepted original cohorts; compiled observations are separate coverage. This collection itself is excluded for replay.','manifestsChecked':manifests,'matchingEmployerSources':findings,'duplicateAcceptedCohorts':matches}


def render_receipts(doc, s, out, evidence):
    from PIL import Image, ImageDraw
    visual = out / 'visual' / s['key']
    visual.mkdir(parents=True, exist_ok=True)
    page_receipts, artifacts = [], []
    pages = list(range(s['firstPage']-1, s['lastPage']+2))
    thumbnails = []
    for page in pages:
        pix = doc[page-1].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        raw = pix.tobytes('png')
        page_receipts.append({'pdfPage':page,'renderDpi':72,'renderSha256':digest(raw),'role':'employee' if s['firstPage']<=page<=s['lastPage'] else 'scope-boundary'})
        im = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        if page in (s['firstPage']-1, s['firstPage'], s['lastPage'], s['lastPage']+1):
            target = visual / f'physical-page-{page}.png'
            target.write_bytes(raw)
            artifacts.append({'file':str(target.relative_to(out)),'sha256':digest(raw),'physicalPdfPages':[page],'purpose':'Readable original header/definition/scope/control review'})
        im.thumbnail((255,330))
        tile = Image.new('RGB',(265,355),'white');tile.paste(im,((265-im.width)//2,20))
        ImageDraw.Draw(tile).text((8,4),f'{s["key"]} | physical {page}',fill='black')
        thumbnails.append(tile)
    for start in range(0,len(thumbnails),24):
        tiles = thumbnails[start:start+24]
        sheet = Image.new('RGB',(265*4,355*((len(tiles)+3)//4)), '#dddddd')
        for at,tile in enumerate(tiles):sheet.paste(tile,((at%4)*265,(at//4)*355))
        target = visual / f'page-sequence-{start//24+1}.png'
        sheet.save(target)
        artifacts.append({'file':str(target.relative_to(out)),'sha256':digest(target.read_bytes()),'physicalPdfPages':pages[start:start+24],'purpose':'Every physical employee page and both scope boundaries rendered for sequence/layout census'})
    anomalies=[e for e in evidence if e['row'][3]==75000 or (e['row'][4] is not None and e['row'][4]<0)]
    if anomalies:
        crops=[]
        for item in anomalies:
            row=item['row'];y=item['nameBbox'][1]
            clip=fitz.Rect(40,y-3,575,item['nameBbox'][3]+3)
            pix=doc[row[5]-1].get_pixmap(matrix=fitz.Matrix(1.75,1.75),clip=clip,alpha=False)
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            tile=Image.new('RGB',(960,im.height+24),'white')
            ImageDraw.Draw(tile).text((8,4),f'Physical PDF page {row[5]} | {row[1]} | '+('displayed exactly $75,000' if row[3]==75000 else 'parenthesized expense recovery'),fill='black')
            tile.paste(im,(8,22));crops.append(tile)
        sheet=Image.new('RGB',(960,sum(im.height+4 for im in crops)),'#dddddd');top=0
        for im in crops:sheet.paste(im,(0,top));top+=im.height+4
        target=visual/'source-special-cells.png';sheet.save(target)
        artifacts.append({'file':str(target.relative_to(out)),'sha256':digest(target.read_bytes()),'physicalPdfPages':sorted({e['row'][5] for e in anomalies}),'purpose':'Readable original-row crops: every exactly-threshold displayed row and every negative expense recovery'})
    return {'sourceSha256':s['sha256'],'pages':page_receipts,'artifacts':artifacts,'reviewMethod':'Readable first/last employee pages and neighboring cohort boundaries; complete rendered page-sequence/layout census. Every native row additionally agrees cell-for-cell across two independent PDF extractors.','manualReviewClaim':'Rendered artifact inventory; row-level verification is independent native extraction, not OCR.'}


def source_record(s, rows, checks, raw, compressed, evidence_sha, visual_sha):
    uvic = s['key'].startswith('uvic')
    end = int('20'+s['year'].split('/')[1]) if uvic else int(s['year'])
    residual = checks['remunerationDifference'] or checks['expensesDifference'] or checks['printedNamedPlusBelowMinusGrandRemuneration']
    warning = (f"Published named rows sum to ${checks['totalRemuneration']:,} remuneration and ${checks['totalKnownExpenses']:,} known expenses, versus printed named controls ${s['printedNamedRemuneration']:,} and ${s['printedNamedExpenses']:,} (rows minus controls: ${checks['remunerationDifference']:+,}, ${checks['expensesDifference']:+,}). Every original row agrees across independent native readers. The source does not establish the cause; no cell is adjusted.") if residual else None
    if checks['printedNamedPlusBelowMinusGrandRemuneration']:
        warning += f" Printed named plus below-threshold remuneration also exceeds the printed grand total by ${checks['printedNamedPlusBelowMinusGrandRemuneration']:,}."
    notes = [
        f"Complete published named EMPLOYEE schedule, physical PDF pages {s['firstPage']}–{s['lastPage']}. Board/committee members, executive component tables, below-threshold aggregates, suppliers and severance summaries are excluded.",
        "Names are preserved as published; positions are not published in this schedule and remain null. Blank/dash expenses remain null, explicit numeric zero remains zero, and parenthesized recoveries remain negative. Known-expense sums do not establish values for unknown cells.",
        ("Remuneration includes salary, overtime, taxable benefits and other like amounts paid during the reported year. This employee SOFI measure excludes the separately reconciled employer-paid portion of staff benefits and differs from executive total compensation. The schedule explicitly rounds to the nearest dollar. Surnames plus initials and repeated disclosed names are retained without identity merging." if not uvic else "Expenses are reimbursement of work-related costs including travel, memberships, tuition, relocation (**), vehicle expenses, extraordinary hiring expenses, registration fees and similar amounts. Remuneration and expenses include grants and contracts administered by the University. The total note includes taxable benefits and deferred income and excludes severance payments relative to financial-statement salaries and wages."),
        "All row values and controls are independently extracted from the fingerprinted official original PDF. Tiny reproduced differences are source residuals; rounding bounds are comparisons and do not establish their cause.",
    ]
    if s['year']=='2019/20':
        notes.append("The introductory source note says remuneration includes salary and wages, services over regular duties and payments connected with retirement (*). Hiles, Clayton is printed at exactly $75,000 within the complete named schedule although the subtotal label says >$75,000; the published row is retained.")
    if checks['atThresholdRows']:
        notes.append("The source's named subtotal is labelled over/> $75,000. One named row is displayed at exactly $75,000 and is retained as published. The threshold metadata describes the printed selection label; it does not remove that source row or infer an unrounded amount.")
    source = {'id':s['key']+'-sofi-employees','employerSlug':s['employerSlug'],'employerName':s['employerName'],'sector':'Education' if uvic else 'Crown corporations','year':s['year'],'slug':s['year'].replace('/','-'),'file':s['key']+'-employees.json.gzip','title':s['employerName']+' Statement of Financial Information '+s['year']+': employees','sourceUrl':public_source(s),'sourceIndexUrl': 'https://www.uvic.ca/financialplanning/financial-reporting/index.php' if uvic else 'https://www.worksafebc.com/en/about-us/what-we-do/statement-financial-information','sha256':s['sha256'],'dataSha256':digest(compressed),'normalizedSha256':digest(raw),'sourceKind':'official','periodType':'fiscal' if uvic else 'calendar','periodStart':f'{end-1}-04-01' if uvic else f'{end}-01-01','periodEnd':f'{end}-03-31' if uvic else f'{end}-12-31','category':'employee-remuneration','scope':'employee-remuneration','scopeDescription':'Complete published named employee schedule; separate board and executive tables excluded','completeEmployeeSchedule':True,'threshold':75000,'thresholdRule':'over','thresholdComparison':'>','currency':'CAD','amountUnit':'dollars','amountPrecision':'whole-dollars','nameDisclosure':'published-surname-and-initials' if not uvic else 'as-published','positionDisclosure':'not-published','rowCount':len(rows),'totalRemuneration':checks['totalRemuneration'],'totalDisclosedExpenses':checks['totalKnownExpenses'],'pages':checks['physicalPdfPages'],'status':'verified','verifiedOn':'2026-11-02','notes':notes,'validation':{**checks,'originalBackedEvidenceFile':'evidence/'+s['key']+'.json.gzip','originalBackedEvidenceSha256':evidence_sha,'visualReceiptFile':'controls/'+s['key']+'-visual.json','visualReceiptSha256':visual_sha}}
    if warning:source['publicWarning']=warning
    source['validation']['sourcePixelsReviewed']=True
    source['validation']['reviewedPhysicalPages']=sorted({s['firstPage'],s['lastPage']} | {r[5] for r in rows if r[3]==75000 or (r[4] is not None and r[4]<0)})
    source['validation']['visualReviewMethod']='Original rendered first/last employee pages and every original row displaying exactly $75,000 or a parenthesized expense recovery reviewed on 2026-11-02. Every other native row has complete independent coordinate/layout verification; page-sequence sheets retain all pages.'
    return source


def write_all(results, out):
    out.mkdir(parents=True, exist_ok=True)
    duplicate = duplicate_inventory()
    sources, dispositions = [], []
    for s,path,doc,pages,rows,evidence,checks in results:
        raw, compressed = packed(rows)
        (out/(s['key']+'-employees.json.gzip')).write_bytes(compressed)
        evidence_path = out/'evidence'/(s['key']+'.json.gzip')
        evidence_path.parent.mkdir(parents=True,exist_ok=True)
        original = {'sourceSha256':s['sha256'],'sourceBytes':path.stat().st_size,'physicalPdfPages':checks['physicalPdfPages'],'coordinateRows':evidence,'independentLayoutRows':parse_layout(pages,s),'independentLayoutPages':{str(p):pages[p-1] for p in checks['physicalPdfPages']},'neighborScopePages':{str(p):pages[p-1] for p in [s['firstPage']-1,s['lastPage']+1]}}
        evidence_raw,evidence_compressed = packed(original)
        evidence_path.write_bytes(evidence_compressed)
        visual = render_receipts(doc,s,out,evidence)
        visual_path=out/'controls'/(s['key']+'-visual.json');dump(visual_path,visual)
        download = {'inventoryId':'additional-source-'+s['key'],'url':public_source(s),'sourceSha256':s['sha256'],'sourceBytes':path.stat().st_size,'physicalPageCount':len(doc),'retrievedOn':'2026-11-02','method':'Official public Download PDF button (POST resource mediaItem control; no correspondence)' if s['key'].startswith('worksafe') else 'GET original official PDF','scopeAuthoritative':'Period and named employee schedule established by original internal headings, continuous employee page census, preceding board page and following supplier/severance page.'}
        if s['key'].startswith('worksafe'):
            download['publicMediaItem']={'2023':'D2E5828E9500420E86DEFE471CB9BFCB','2024':'16DB42D2371F4133B734F73E056E72F8','2025':'F66D880464B9456D8F4BC3177D27CD1D'}[s['year']]
        dump(out/'controls'/(s['key']+'-download.json'),download)
        dump(out/'controls'/(s['key']+'.json'),{'source':s,'checks':checks,'periodEvidence':pages[s['firstPage']-1][:1400],'printedControlsEvidence':pages[s['lastPage']-1], 'evidenceSha256':digest(evidence_compressed)})
        source=source_record(s,rows,checks,raw,compressed,digest(evidence_compressed),digest(visual_path.read_bytes()))
        sources.append(source)
        dispositions.append({'id':'additional-source-'+s['key'],'status':'accepted','acceptedSourceId':source['id'],'acceptedManifest':'research/salaries/follow-through-worksafe-uvic/sources.json','employeeRows':len(rows),'sourceSha256':s['sha256'],'period':s['year'],'employeeScope':'complete-published-named-employee-schedule','boardScope':'excluded: separate board/committee disclosure is not employee remuneration','executiveScope':'separate component/total-compensation tables excluded; executives appearing in employee schedule are imported once in that employee measure','supplierAndAggregateScope':'excluded','holdReason':None,'publicWarning':source.get('publicWarning'),'evidence':'evidence/'+s['key']+'.json.gzip','controls':'controls/'+s['key']+'.json'})
    dump(out/'sources.json',{'version':1,'rowSchema':SCHEMA,'coverageNotes':['Six complete official employee cohorts. Board/committee, executive component, supplier and below-threshold aggregate lines are excluded. All 14,715 published named rows agree across independent original-native readers.'],'sources':sources})
    dump(out/'dispositions.json',{'version':1,'checkedOn':'2026-11-02','inventory':'/workspace/salary-source-follow-through/additional-sources.json','sources':dispositions})
    dump(out/'duplicate-check.json',duplicate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=CACHE)
    parser.add_argument('--key', action='append')
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--write', action='store_true', help='Write all six frozen accepted cohorts and visual/evidence artifacts')
    parser.add_argument('--output',type=Path,default=OUT)
    args = parser.parse_args()
    if args.write and args.key:parser.error('--write requires all six sources')
    results=[]
    for s in specs():
        if args.key and s['key'] not in args.key:
            continue
        path, doc, pages, rows, evidence, checks = analyze(s, args.cache)
        results.append((s,path,doc,pages,rows,evidence,checks))
        print(f"{s['key']}: {len(rows):,} rows; original readers agree; remuneration ${checks['totalRemuneration']:,}; known expenses ${checks['totalKnownExpenses']:,}; source residuals {checks['remunerationDifference']:+}/{checks['expensesDifference']:+}",flush=True)
    if args.write:write_all(results,args.output)


if __name__ == '__main__':
    main()
