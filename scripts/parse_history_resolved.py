#!/usr/bin/env python3
"""Reproduce narrowly qualified Merritt/Lake Cowichan disclosure recoveries.

Both PDF readers extract every original cell before publication selection. This
never edits the registry, earlier collections, generated app data, or originals.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, re, subprocess, urllib.request
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/municipal-history-resolved'
AUDIT = ROOT / 'research/salaries/municipal-history-pass/resolved'
SCHEMA = ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage']
READERS = ['PyMuPDF positioned words', 'Poppler bbox-layout positioned words']

def sha(raw): return hashlib.sha256(raw).hexdigest()
def compact(value): return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
def money(text):
    text = text.replace('$', '').replace(' ', '').strip()
    if text in ('', '-', '‐', '–', '—'): return None
    if not re.fullmatch(r'-?\d[\d,]*(?:\.\d{1,2})?|\(\d[\d,]*(?:\.\d{1,2})?\)', text):
        raise ValueError(f'Unreviewed monetary cell: {text!r}')
    if text.startswith('('): text = '-' + text[1:-1]
    value = Decimal(text.replace(',', ''))
    return int(value) if value == int(value) else float(value)
def cents(value):
    if value is None: raise ValueError('A missing cell cannot be treated as zero')
    return int(Decimal(str(value)) * 100)
def dollars(value): return int(value // 100) if value % 100 == 0 else float(Decimal(value) / 100)
def total(rows, field): return dollars(sum(cents(r[field]) for r in rows if r.get(field) is not None))
def fitz_words(page):
    return [{'x':w[0], 'y':w[1], 'right':w[2], 'bottom':w[3], 'text':w[4]} for w in page.get_text('words')]
def poppler_words(path, pages):
    out = {}
    for page in pages:
        raw = subprocess.check_output(['pdftotext', '-bbox-layout', '-f', str(page), '-l', str(page), str(path), '-'])
        tree = ET.fromstring(raw)
        out[page] = [{'x':float(w.attrib['xMin']), 'y':float(w.attrib['yMin']), 'right':float(w.attrib['xMax']), 'bottom':float(w.attrib['yMax']), 'text':w.text or ''} for w in tree.findall('.//{*}word')]
    return out
def read_table(words, layout):
    bounds, roles = layout['columns'], layout['roles']
    p = roles.index('pay'); lo, hi = bounds[p:p+2]; ylo, yhi = layout['yRange']
    anchors = sorted([w for w in words if lo <= w['x'] < hi and ylo <= w['y'] <= yhi and re.fullmatch(r'\d[\d,]*\.\d\d', w['text'])], key=lambda w:w['y'])
    if len(anchors) != layout['rows']: raise ValueError(f"Expected {layout['rows']} rows, found {len(anchors)}")
    rows, evidence = [], []
    for i, anchor in enumerate(anchors):
        lower = ylo - 2 if i == 0 else (anchors[i-1]['y'] + anchor['y']) / 2
        upper = yhi + 2 if i == len(anchors)-1 else (anchor['y'] + anchors[i+1]['y']) / 2
        selected = [w for w in words if lower <= w['y'] < upper and bounds[0] <= w['x'] < bounds[-1]]
        row = {}
        for n, role in enumerate(roles):
            ww = sorted([w for w in selected if bounds[n] <= w['x'] < bounds[n+1]], key=lambda w:(round(w['y']/2)*2,w['x']))
            text = ' '.join(w['text'] for w in ww).strip()
            row[role] = money(text) if role in ('pay', 'expenses', 'grantExpenses', 'total') else text or None
        if not row['name'] or row['pay'] is None or re.search(r'\b(total|employees|remuneration)\b', row['name'], re.I): raise ValueError('Invalid named row')
        rows.append(row); evidence.append({'fields':row, 'anchorY':anchor['y'], 'words':selected})
    return rows, evidence
def read_control(words, control):
    ww = sorted([w for w in words if abs(w['y']-control['y']) < 2], key=lambda w:w['x'])
    cells = []
    for lo, hi in control['columns']:
        cells.append(money(' '.join(w['text'] for w in ww if lo <= w['x'] < hi)))
    if cells != control['values']: raise ValueError(f"Changed original control: {cells} != {control['values']}")
    return cells
def extract(report, path):
    if sha(path.read_bytes()) != report['sha256']: raise ValueError('Changed original fingerprint; renewed review required')
    doc = fitz.open(path)
    for heading in report['requiredHeadings']:
        text = ' '.join(doc[heading['page']-1].get_text().split())
        if heading['text'] not in text: raise ValueError(f"Changed period/scope heading: {heading}")
    pages = sorted(set(c['layout']['page'] for c in report['cohorts']) | set(c['page'] for c in report['controls']))
    first = {p:fitz_words(doc[p-1]) for p in pages}; second = poppler_words(path,pages)
    controls = {}
    for control in report['controls']:
        a = read_control(first[control['page']], control); b = read_control(second[control['page']], control)
        if a != b: raise ValueError('Independent control readers disagree')
        controls[control['id']] = a
    results = []
    for cohort in report['cohorts']:
        layout = cohort['layout']; page = layout['page']
        rows, a = read_table(first[page], layout); other, b = read_table(second[page], layout)
        if rows != other: raise ValueError('Every-field independent PDF readers disagree')
        if rows != cohort['reviewedRows']: raise ValueError('Rows differ from complete rendered-page transcription')
        result = {'config':cohort, 'rawRows':rows, 'evidence':[{'page':page,'fields':r,'pymupdf':x,'poppler':y} for r,x,y in zip(rows,a,b)]}
        results.append(result)
    if report['employerSlug'] == 'city-of-merritt':
        council, employees = results[0]['rawRows'], results[1]['rawRows']
        if [total(council,f) for f in ['pay','expenses','grantExpenses']] != controls['council'] or total(employees,'pay') != controls['namedEmployees'][0]: raise ValueError('Literal named source control failed')
        observed = [dollars(cents(total(council,'pay'))+cents(total(employees,'pay'))+cents(controls['belowThreshold'][0]))]
        observed += [dollars(cents(total(council,f))+cents(total(employees,f))) for f in ['expenses','grantExpenses']]
        if observed != controls['printedB']: raise ValueError('Reviewed B aggregate identity changed')
    else:
        rows = results[0]['rawRows']
        named = [dollars(cents(a)-cents(b)) for a,b in zip(controls['allEmployees'][:2],controls['belowThreshold'][:2])]
        if [total(rows,'pay'),total(rows,'expenses')] != named: raise ValueError('Full original named-component controls failed')
        conflicts = [(r['name'], dollars(cents(r['pay'])+cents(r['expenses'])-cents(r['total']))) for r in rows if cents(r['pay'])+cents(r['expenses']) != cents(r['total'])]
        if conflicts != [('Jessica May',5000)]: raise ValueError(f'Unexpected row-total conflicts {conflicts}')
        below = controls['belowThreshold']
        if dollars(cents(below[0])+cents(below[1])-cents(below[2])) != 0.09: raise ValueError('Reviewed aggregate Total residual changed')
    return results, controls

def publication(report, result, controls):
    cohort = result['config']; withheld_names = cohort.get('withholdNames',[])
    raw = result['rawRows']; selected = [r for r in raw if r['name'] not in withheld_names]
    withheld = [r for r in raw if r['name'] in withheld_names]
    if len(withheld) != len(withheld_names): raise ValueError('Withheld row selection changed')
    missing_expenses = report.get('expenseMapping') == 'withhold-ambiguous-total'
    page = cohort['layout']['page']; stem = report['employerSlug']+'-'+report['year']+'-'+cohort['category']
    rows = [[report['employerSlug'],r['name'],r.get('position'),r['pay'],None if missing_expenses else r['expenses'],page] for r in selected]
    data = gzip.compress(compact(rows),mtime=0)
    complete = not withheld; employee = cohort['category'] == 'employee-remuneration'
    warning = report['publicWarning'] + (' '+cohort['publicWarning'] if cohort.get('publicWarning') else '')
    validation = {'originalFingerprintVerified':True,'independentReaders':READERS,'everyRowFieldAgreement':True,'completeRenderedRowTranscriptionAgreement':True,'physicalPagesVisuallyReviewed':[page],'periodEvidence':report['requiredHeadings'],'rowsIndependentlyChecked':len(raw),'acceptedRows':len(rows),'sourceNamedRowCount':len(raw),'withheldRows':withheld,'completeNamedCohort':complete,'completeExpensesDisclosure':not missing_expenses and complete,'sourceControls':controls,'publicationEvidence':report['publicationEvidence'],'evidenceFile':'evidence/'+stem+'.json.gzip'}
    if employee: validation['completeEmployeeSchedule'] = complete
    if report['employerSlug'] == 'city-of-merritt':
        validation['printedControls'] = [{'field':'pay','printedControl':total(raw,'pay'),'rowSum':total(selected,'pay'),'residual':0,'basis':'Literal named employee subtotal' if employee else 'Literal council subtotal'}]
        validation['observedCombinedBIdentity'] = {'pay':'council named + employee named + under75k remuneration','expenses':'sum of published named council and employee Expenses cells; missing cells not certified zero','grantExpenses':'sum of published named council and employee Grant Funded Expenses cells; missing cells not certified zero','residuals':[0,0,0],'explanationOfIssuerLabel':'Not established; exact arithmetic only'}
    else:
        validation['printedControls'] = [{'field':f,'printedControl':dollars(cents(a)-cents(b)),'completeOriginalNamedRowSum':total(raw,f),'completeOriginalResidual':0,'acceptedPartialRowSum':total(selected,f),'withheldRowSum':total(withheld,f),'basis':'All employees less all other employees; full eight-row source checked before withholding Jessica May'} for f,a,b in zip(['pay','expenses'],controls['allEmployees'][:2],controls['belowThreshold'][:2])]
    source = {'id':'municipal-history-resolved-'+stem,'employerSlug':report['employerSlug'],'employerName':report['employerName'],'sector':'Municipalities','year':report['year'],'periodType':'calendar','periodStart':report['year']+'-01-01','periodEnd':report['year']+'-12-31','title':report['employerName']+' '+report['year']+' SOFI: '+cohort['category'],'sourceKind':'official-pdf','sourceUrl':report['sourceUrl'],'sourceIndexUrl':report['sourceIndexUrl'],'sha256':report['sha256'],'file':stem+'.json.gzip','dataSha256':sha(data),'category':cohort['category'],'scope':'partial-named-employee-schedule' if withheld else 'named-employee-schedule' if employee else 'elected-officials','scopeDescription':cohort['scopeDescription'],'threshold':75000 if employee else None,'thresholdComparison':None,'currency':'CAD','amountUnit':'dollars','status':'verified','verifiedOn':'2026-11-01','rowCount':len(rows),'sourceNamedRowCount':len(raw),'withheldRowCount':len(withheld),'totalRemuneration':total(selected,'pay'),'totalExpenses':None if missing_expenses else total(selected,'expenses'),'pages':[page],'nameDisclosure':'as-published','positionDisclosure':'published','completeNamedCohort':complete,'completeExpensesDisclosure':not missing_expenses and complete,'expensesNote':report['expensesNote'],'publicWarning':warning,'notes':report['notes']+cohort.get('notes',[]),'validation':validation}
    if employee: source['completeEmployeeSchedule'] = complete
    evidence = {'originalSha256':report['sha256'],'sourceUrl':report['sourceUrl'],'periodEvidence':report['requiredHeadings'],'publicationEvidence':report['publicationEvidence'],'rows':result['evidence'],'acceptedNames':[r['name'] for r in selected],'withheldRows':withheld,'sourceControls':controls,'validation':validation,'layout':cohort['layout'],'expenseMapping':report.get('expenseMapping','literal separate Expense column'),'notes':source['notes'],'publicWarning':warning}
    evidence_bytes = gzip.compress(compact(evidence),mtime=0)
    source['provenanceFile'] = 'evidence/'+stem+'.json.gzip'; source['provenanceSha256'] = sha(evidence_bytes)
    return source, {stem+'.json.gzip':data,source['provenanceFile']:evidence_bytes}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify',action='store_true');ap.add_argument('--cache-dir',type=Path,default=Path('/tmp/history-resolved'));ap.add_argument('--output-dir',type=Path,default=BASE)
    args = ap.parse_args();cfg = json.loads((AUDIT/'reviewed-layouts.json').read_text());outputs={};sources=[]
    for report in cfg['reports']:
        p = args.cache_dir/report['cacheFile']
        if not p.exists():
            p.parent.mkdir(parents=True,exist_ok=True)
            with urllib.request.urlopen(urllib.request.Request(report['sourceUrl'],headers={'User-Agent':'Mozilla/5.0 official public salary verification'}),timeout=45) as response: p.write_bytes(response.read())
        results, controls = extract(report,p)
        for result in results:
            source, files = publication(report,result,controls);sources.append(source);outputs.update(files)
            print(source['employerSlug'],source['year'],source['category'],source['rowCount'],source['totalRemuneration'],source['totalExpenses'])
    outputs['sources.json'] = (json.dumps({'version':1,'rowSchema':SCHEMA,'sources':sources},ensure_ascii=False,indent=2)+'\n').encode()
    for name, raw in outputs.items():
        p = args.output_dir/name
        if args.verify:
            if not p.exists() or p.read_bytes() != raw: raise ValueError(f'Reproduction differs: {p}')
        else: p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'verify':args.verify}))
if __name__ == '__main__': main()
