#!/usr/bin/env python3
"""Reproduce reviewed Southern Interior historical schedules with two independent PDF readers.

Each layout, reporting year, row count and printed control is reviewed against
the rendered original. PDFs are hash-pinned. Coordinates refer to the displayed
page, including PDF rotation. Missing amounts are not converted to zero.
"""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-history-interior'
MONEY = re.compile(r'^-?\d[\d,]*(?:\.\d{1,2})?$')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def money(text):
    text = text.strip().replace('$', '').strip()
    if text.startswith('(') and text.endswith(')'): text = '-' + text[1:-1]
    if text.lower() == 'nil':
        return 0
    if text in ('', '-', '–', '—'):
        return None
    if not MONEY.fullmatch(text):
        raise ValueError(f'Unrecognized money cell: {text!r}')
    value = Decimal(text.replace(',', ''))
    return int(value * 100)


def dollars(cents):
    return None if cents is None else (cents // 100 if cents % 100 == 0 else cents / 100)


def mupdf_words(page):
    return [(*tuple(fitz.Rect(w[:4]) * page.rotation_matrix), w[4]) for w in page.get_text('words')]


def poppler_words(path, page_number):
    raw = subprocess.check_output(['pdftotext', '-f', str(page_number), '-l', str(page_number), '-bbox-layout', str(path), '-'])
    root = ET.fromstring(raw)
    return [(float(w.attrib['xMin']), float(w.attrib['yMin']), float(w.attrib['xMax']), float(w.attrib['yMax']), w.text or '')
            for w in root.iter() if w.tag.endswith('}word') or w.tag == 'word']


def extract(words, section):
    words = [(*w[:4], w[4][1:] if re.fullmatch(r'\$[0-9][0-9,.]*', w[4]) else w[4]) for w in words]
    corrections=section.get('monetaryTokenCorrections',{})
    numeric_bounds=[bounds for field,bounds in section['columns'].items() if field not in ('name','position','department')]
    words=[(*w[:4],corrections.get(w[4],w[4]) if any(left <= (w[0]+w[2])/2 < right for left,right in numeric_bounds) else w[4]) for w in words]
    columns = section['columns']
    y0, y1 = section['y']
    words = [w for w in words if y0 <= (w[1] + w[3]) / 2 <= y1 and w[4] not in section.get('ignoreTokens', [])]
    pay_col = columns[section.get('anchorColumn', 'pay')]
    anchors = sorted((w for w in words if pay_col[0] <= (w[0] + w[2]) / 2 < pay_col[1] and MONEY.fullmatch(w[4])), key=lambda w: w[1])
    if len(anchors) != section['rowCount']:
        raise ValueError(f"Expected {section['rowCount']} pay cells; found {len(anchors)}")
    centers = [(w[1] + w[3]) / 2 + section.get('reviewedAnchorYOffsets',{}).get(str(i),0) for i,w in enumerate(anchors)]
    groups = [{k: [] for k in columns} for _ in centers]
    for word in words:
        x, y = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
        at = min(range(len(centers)), key=lambda i: abs(centers[i] - y))
        if abs(centers[at] - y) > section.get('maxRowDistance', 16):
            raise ValueError(f"Unassigned schedule text: {word[4]!r}")
        for field, (left, right) in columns.items():
            if left <= x < right:
                if field not in ('name', 'position', 'department') and word[4] in section.get('currencyTokens',['$']): continue
                groups[at][field].append(word)
    rows = []
    for group in groups:
        values = {}
        for field, cells in group.items():
            # Stable reading order for single-line names and wrapped positions.
            lines = []
            for word in sorted(cells, key=lambda w: ((w[1] + w[3]) / 2, w[0])):
                cy = (word[1] + word[3]) / 2
                if lines and abs(cy - lines[-1][0]) <= 3:
                    lines[-1][1].append(word)
                else:
                    lines.append((cy, [word]))
            text = ' '.join(w[4] for _, line in lines for w in sorted(line, key=lambda w: w[0])).strip()
            if field in ('name', 'position', 'department'):
                if re.search(r'[$€£]',text):raise ValueError(f'Currency leaked into a text field: {field}={text}')
                values[field] = text or None
            else:
                values[field] = money(text)
        if section.get('splitNamePosition'):
            values['name'], values['position'] = [v.strip() for v in values['name'].split(',', 1)]
        for before, after in section.get('fieldCorrections', {}).get('name', {}).items():
            if values['name'] == before:
                values['name'] = after
        position_fix = section.get('fieldCorrections', {}).get('positionByName', {}).get(values['name'])
        if position_fix:
            accepted_before = position_fix['before'] if isinstance(position_fix['before'], list) else [position_fix['before']]
            if values.get('position') not in accepted_before:
                raise ValueError(f"Reviewed position correction no longer matches for {values['name']}")
            values['position'] = position_fix['after']
        if not values['name'] or re.search(r'^(total|consolidated|schedule|employees|remuneration)\b', values['name'], re.I):
            raise ValueError(f'Non-person row entered the schedule: {values}')
        if section.get('payComponents'):
            if any(values.get(f) is None for f in section['payComponents']):
                raise ValueError('Unknown remuneration component cannot be converted to zero')
            values['pay'] = sum(values[f] for f in section['payComponents'])
        if section.get('expensesIncludeBenefits'):
            values['expenses'] = None
        if values['pay'] is None or values['pay'] < 0:
            raise ValueError(f'Missing or negative remuneration: {values}')
        if section['category'] == 'employee-remuneration' and values['pay'] < 7_500_000 and not section.get('allowPublishedThresholdExceptions'):
            raise ValueError(f'Unexpected below-threshold employee: {values}')
        rows.append(values)
    missing_corrections = set(section.get('fieldCorrections', {}).get('positionByName', {})) - {r['name'] for r in rows}
    if missing_corrections:
        raise ValueError(f'Reviewed position correction rows disappeared: {missing_corrections}')
    return rows


def total(rows, field):
    return sum(r.get(field) or 0 for r in rows)


def select_reviewed_rows(rows,selection):
    """Select explicitly identified council roles from a published mixed group."""
    included={r['publishedName']:r for r in selection['includedRows']}
    expected=set(included)|set(selection['excludedPublishedNames'])
    if {r['name'] for r in rows}!=expected:raise ValueError('Reviewed mixed-group membership changed')
    selected=[];excluded=[]
    for row in rows:
        if row['name'] in included:
            identity=included[row['name']]
            selected.append(dict(row,name=identity['name'],position=identity['position']))
        else:excluded.append(row)
    return selected,excluded


def build(config, cache, output=OUT, fetch=False):
    sources, audits, aggregate_only = [], [], []
    pending = {}
    for report in config['reports']:
        path = cache / report['cacheFile']
        if not path.exists() and fetch:
            cache.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(urllib.request.Request(report['sourceUrl'], headers={'User-Agent':'Mozilla/5.0'}), timeout=60) as response:
                path.write_bytes(response.read())
        raw = path.read_bytes()
        if sha(raw) != report['sha256']:
            raise ValueError(f"Original fingerprint changed: {report['employerSlug']} {report['year']}")
        doc = fitz.open(stream=raw, filetype='pdf')
        for proof in report['periodEvidence']:
            normalized = lambda text: re.sub(r'\s+', '', text).casefold()
            if normalized(proof['text']) not in normalized(doc[proof['physicalPage']-1].get_text()):
                raise ValueError(f"Reporting-period proof changed: {proof}")
        for cohort in report['cohorts']:
            all_rows, evidence_pages = [], []
            category = cohort['category']
            for section in cohort['sections']:
                layout = dict(section, category=category)
                page = section['page']
                words_a = mupdf_words(doc[page-1]); words_b = poppler_words(path, page)
                a, b = extract(words_a, layout), extract(words_b, layout)
                if a != b:
                    raise ValueError(f"Independent readers disagree: {report['employerSlug']} p{page}: {a} != {b}")
                for row in a:
                    if cohort.get('splitRolePrefix'):
                        match = re.fullmatch(r'(COUNCILLOR|MAYOR)\s+(.*)', row['name'], re.I)
                        if not match: raise ValueError('Reviewed role prefix changed')
                        row['name'], row['position'] = match[2], match[1]
                    if cohort.get('splitRoleSuffix'):
                        match=re.fullmatch(r'(.*?)\s+(Mayor(?:\s*/\s*Councillor)?|Councillor)',row['name'],re.I)
                        if not match:raise ValueError('Reviewed role suffix changed')
                        row['name'],row['position']=match[1],match[2]
                    row['pdfPage'] = page
                all_rows += a
                evidence_pages.append({'physicalPage':page,'layout':layout,'mupdfWords':words_a,'popplerWords':words_b})
            published_group_rows=None;excluded_rows=[]
            if cohort.get('reviewedRowSelection'):
                published_group_rows=all_rows
                all_rows,excluded_rows=select_reviewed_rows(all_rows,cohort['reviewedRowSelection'])
            controls=[]
            for field, printed in cohort['controlsCents'].items():
                actual=total(all_rows,field); residual=actual-printed
                if residual != cohort.get('reviewedResidualsCents',{}).get(field,0):
                    raise ValueError(f"Control changed: {report['employerSlug']} {report['year']} {category} {field}: actual {actual}, printed {printed}, residual {residual}")
                controls.append({'field':field,'printedControl':dollars(printed),'rowSum':dollars(actual),'residual':dollars(residual),'basis':cohort.get('controlBasis',{}).get(field,'Printed named-cohort subtotal')})
            rows=[[report['employerSlug'],r['name'],r.get('position'),dollars(r['pay']),dollars(r.get('expenses')),r['pdfPage']] for r in all_rows]
            if len(rows)!=cohort['rowCount']:raise ValueError('Complete cohort count changed')
            file=f"{report['employerSlug']}-{report['year']}-{category}.json.gzip"
            payload=gzip.compress(compact(rows),mtime=0);pending[file]=payload
            evidence_file='evidence/'+file
            evidence={'originalPdfSha256':sha(raw),'periodEvidence':report['periodEvidence'],'pages':evidence_pages,'rows':all_rows,'controls':controls}
            if published_group_rows is not None:
                evidence['publishedGroupRows']=published_group_rows
                evidence['excludedRows']=excluded_rows
                evidence['reviewedRowSelection']=cohort['reviewedRowSelection']
            pending[evidence_file]=gzip.compress(compact(evidence),mtime=0)
            notes=report.get('notes',[])+cohort.get('notes',[])+[
                'The original printed calendar period establishes the year; upload paths and later meeting dates do not change it.',
                'Remuneration preserves the published compensation column, including any disclosed benefits, overtime or other payments. It is not an annual base salary rate. Expense-inclusive totals are retained only in supporting evidence.',
                'Names, initials and available positions remain as disclosed. Blank or dash expenses remain null; explicit zero and negative values are retained. These threshold disclosures are not complete employee rosters.',
                'Every name, title and monetary component agrees between independently positioned PyMuPDF and Poppler words. Rendered original table headings, first and last row boundaries, wrapped text and printed controls were checked; complete council tables and any residual-bearing employee tables were additionally reviewed.',
            ]
            warning=None
            if any(c['residual'] for c in controls):
                warning='Published row sums minus printed named-cohort controls: '+', '.join({'pay':'remuneration','expenses':'expenses','expenseInclusiveTotal':'expense-inclusive total','remunerationComponent':'remuneration component','taxableBenefits':'taxable benefits'}.get(c['field'],c['field'])+' '+f"{c['residual']:+g} CAD" for c in controls)+'. Amounts are retained as printed; the cause is unconfirmed.'
            if cohort.get('publicWarning'): warning=cohort['publicWarning']
            source={'id':f"history-interior-{report['employerSlug']}-{report['year']}-{category}",'employerSlug':report['employerSlug'],'employerName':report['employerName'],'sector':'Municipalities','year':report['year'],'periodType':'calendar','periodStart':report['year']+'-01-01','periodEnd':report['year']+'-12-31','title':f"{report['employerName']} {report['year']} official {category}",'sourceUrl':report['sourceUrl'],'sourceIndexUrl':report['indexUrl'],'sha256':sha(raw),'file':file,'dataSha256':sha(payload),'provenanceFile':evidence_file,'provenanceSha256':sha(pending[evidence_file]),'category':category,'scope':'named-employees-over-threshold' if category=='employee-remuneration' else 'elected-officials','scopeDescription':cohort.get('scopeDescription','Published named employee schedule' if category=='employee-remuneration' else 'Published elected officials'),'threshold':75000 if category=='employee-remuneration' else None,'thresholdComparison':cohort.get('thresholdComparison') if category=='employee-remuneration' else None,'currency':'CAD','amountUnit':'dollars','amountPrecision':report.get('amountPrecision','cents'),'status':'verified','verifiedOn':'2026-11-01','rowCount':len(rows),'totalRemuneration':dollars(total(all_rows,'pay')),'totalExpenses':dollars(total(all_rows,'expenses')),'pages':sorted(set(r['pdfPage'] for r in all_rows)),'nameDisclosure':'published-name-as-disclosed','positionDisclosure':'published' if any(r.get('position') for r in all_rows) else 'not-published','notes':notes,'publicWarning':warning,'validation':{'originalFingerprintVerified':True,'periodEvidence':report['periodEvidence'],'independentReaders':['PyMuPDF positioned words','Poppler bbox-layout positioned words'],'everyRowFieldAgreement':True,'physicalPagesVisuallyReviewed':sorted(set(r['pdfPage'] for r in all_rows)),'rowsIndependentlyChecked':len(rows),'printedControls':controls,'allPrintedComponentControlsExact':not any(c['residual'] for c in controls),'expensesControlPublished':'expenses' in cohort['controlsCents'],'publishedThresholdExceptions':sum(r['pay']<=7500000 for r in all_rows) if category=='employee-remuneration' else None,'evidenceFile':evidence_file}}
            if category=='employee-remuneration':
                source['completeEmployeeSchedule']=cohort.get('completeEmployeeSchedule',True)
                source['validation']['completeEmployeeSchedule']=cohort.get('completeEmployeeSchedule',True)
            if cohort.get('expensesNote'):source['expensesNote']=cohort['expensesNote']
            if 'expensesComplete' in cohort:source['validation']['expensesComplete']=cohort['expensesComplete']
            if cohort.get('independentCrossReviewFile'):
                source['validation']['independentCrossReviewFile']=cohort['independentCrossReviewFile']
                source['validation']['acceptanceBasis']='Faithful complete published cohort transcription with explicit unresolved source-control qualification after independent full-row and rendered-page review.'
            sources.append(source)
            print(source['id'],len(rows),'rows',[(c['field'],c['residual']) for c in controls])
        if report.get('aggregateOnlyReview'):
            review=report['aggregateOnlyReview'];page=doc[review['physicalPage']-1]
            readers={'mupdfWords':mupdf_words(page),'popplerWords':poppler_words(path,review['physicalPage'])}
            cells={}
            for reader,words in readers.items():
                def region(bounds):
                    left,top,right,bottom=bounds
                    return [w for w in words if left<=(w[0]+w[2])/2<right and top<=(w[1]+w[3])/2<bottom]
                if Counter(w[4] for w in region(review['zeroNamedBounds']))!=Counter(review['zeroNamedTokens']):raise ValueError('Explicit no-named-employee statement changed')
                cells[reader]={}
                for field,cell in review['aggregateCells'].items():
                    value=money(' '.join(w[4] for w in sorted(region(cell['bounds']),key=lambda w:w[0])))
                    if value!=cell['cents']:raise ValueError('Reviewed below-threshold aggregate changed')
                    cells[reader][field]=value
            if cells['mupdfWords']!=cells['popplerWords']:raise ValueError('Aggregate-only readers disagree')
            evidence_file=f"evidence/{report['employerSlug']}-{report['year']}-aggregate-only.json.gzip"
            pending[evidence_file]=gzip.compress(compact(dict(originalPdfSha256=sha(raw),periodEvidence=report['periodEvidence'],review=review,readers=readers,aggregateCellsCents=cells)),mtime=0)
            aggregate_only.append(dict(id=f"history-interior-{report['employerSlug']}-{report['year']}-aggregate-only",employerSlug=report['employerSlug'],employerName=report['employerName'],sector='Municipalities',year=report['year'],title=f"{report['employerName']} {report['year']} explicit no named employee schedule",sourceUrl=report['sourceUrl'],sourceIndexUrl=report['indexUrl'],sha256=sha(raw),periodStart=report['year']+'-01-01',periodEnd=report['year']+'-12-31',periodType='calendar',category='employee-remuneration',scope='aggregate-only-employee-schedule',threshold=75000,thresholdComparison='>',currency='CAD',amountUnit='dollars',amountPrecision='cents',rowCount=0,totalRemuneration=0,totalExpenses=0,pages=[review['physicalPage']],verifiedOn='2026-11-01',status='verified-aggregate-only',provenanceFile=evidence_file,provenanceSha256=sha(pending[evidence_file]),validation=dict(originalFingerprintVerified=True,periodEvidence=report['periodEvidence'],independentReaders=['PyMuPDF positioned words','Poppler bbox-layout positioned words'],explicitNoNamedEmployeeTextVerified=True,aggregateCellsVerifiedByBothReaders=True,visuallyReviewedPhysicalPages=[review['physicalPage']],sourceControls={field:dollars(cell['cents']) for field,cell in review['aggregateCells'].items()},namedRemunerationSum=0,namedExpensesSum=0),notes=['The published Employees over $75,000 section explicitly says None with dash amounts. No individual record is created. This is not a claim of no employees or payroll.','The separately printed consolidated under-threshold employee aggregate is remuneration $181,393.87, expenses $10,611.11 and combined $192,004.98. Aggregate payroll is not individual salary data.','The separately printed Elected Officials group has unresolved role/scope and combined-total issues; that group is held and is not used to infer employee amounts.']))
        audits.append({key:report[key] for key in ['employerSlug','year','sourceUrl','sha256','cacheFile','periodEvidence']})
        doc.close()
    output.mkdir(parents=True,exist_ok=True)
    for file,data in pending.items():
        path=output/file;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    (output/'sources.json').write_text(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'coverageNotes':['Verified additional Southern Interior historical calendar schedules. Compiled records and aliases are untouched.'],'sources':sources,'aggregateOnlySources':aggregate_only},ensure_ascii=False,indent=2)+'\n')
    (output/'original-verification.json').write_text(json.dumps(audits,indent=2)+'\n')
    return sources


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir',type=Path,default=Path('/tmp/history-interior-cache'))
    parser.add_argument('--output-dir',type=Path,default=OUT)
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--render-review-dir',type=Path,help='Optionally reproduce full rendered salary pages from the hash-verified originals')
    args=parser.parse_args();config=json.loads((OUT/'reviewed-layouts.json').read_text());build(config,args.cache_dir,args.output_dir,args.fetch)
    if args.render_review_dir:
        args.render_review_dir.mkdir(parents=True,exist_ok=True)
        for report in config['reports']:
            raw=(args.cache_dir/report['cacheFile']).read_bytes()
            if sha(raw)!=report['sha256']:raise ValueError('Original changed before rendering')
            with fitz.open(stream=raw,filetype='pdf') as doc:
                pages=sorted({section['page'] for cohort in report['cohorts'] for section in cohort['sections']}|({report['aggregateOnlyReview']['physicalPage']} if report.get('aggregateOnlyReview') else set()))
                for page in pages:
                    doc[page-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(args.render_review_dir/f"{report['employerSlug']}-{report['year']}-p{page}.png")


if __name__=='__main__':main()
