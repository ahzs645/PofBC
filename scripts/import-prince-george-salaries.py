#!/usr/bin/env python3
"""Import reviewed City of Prince George calendar-year SOFI schedules.

Every row is compared between Poppler layout text and a separate PyMuPDF word
coordinate parser. All component subtotals reconcile exactly in integer cents.
The review pins source bytes; changed PDFs require a new review. Missing 2023 is
held without inventing rows. Source components are retained in audit files.
"""
from __future__ import annotations
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/prince-george'
SLUG = 'city-of-prince-george'
MONEY = re.compile(r'(?<!\w)(?:\(?-?\d[\d,]*\.\d{2}\)?|-(?!\w))(?=\s|$)')
ELECTED_LABELS = ['Portion', 'Allowance', 'S.168(1)(a)', 'S.168(1)(b)', 'S.168(1)(c)']


def digest(data): return hashlib.sha256(data).hexdigest()


def cents(token):
    if token in ('', '-', ','): return None
    if not MONEY.fullmatch(token): raise ValueError(f'Invalid money token {token!r}')
    return int(Decimal(token.replace(',', '').replace('(', '-').replace(')', ''))*100)


def dollars(value): return None if value is None else value / 100


def component_labels(year):
    return ['Pay', 'Payout', 'Payout', 'Compensation', '$75,000', 'Expenses'] if year < 2022 else ['Pay', 'Compensation **', 'Expenses']


def amount_from_components(values, year, elected=False):
    if elected:
        if values[2] != sum(v or 0 for v in values[:2]):
            raise ValueError('Elected official base and vehicle allowance do not equal the printed remuneration total')
        return values[2], values[3]
    if values[0] is None: raise ValueError('Missing base-pay cell')
    if year < 2022:
        if values[4] != sum(v or 0 for v in values[:4]):
            raise ValueError('Employee components do not equal the separately printed remuneration total')
        pay = values[4]
    else:
        pay = sum(v or 0 for v in values[:2])
    if pay is None or pay <= 7500000:
        raise ValueError('Named employee below the strict over-$75,000 threshold')
    return pay, values[-1]


def anchors_from_layout(header, labels):
    anchors=[];start=0
    for label in labels:
        start=header.index(label,start)+len(label);anchors.append(start)
    return anchors


def layout_values(line, anchors, tolerance):
    values=[None]*len(anchors);found=[];seen=set()
    for m in MONEY.finditer(line):
        i=min(range(len(anchors)),key=lambda i:abs(m.end()-anchors[i]))
        if abs(m.end()-anchors[i])>=tolerance: continue
        if i in seen: raise ValueError(f'Two monetary tokens in one column: {line!r}')
        values[i]=cents(m[0]);seen.add(i);found.append(m)
    return values,found


def parse_employee_layout(text, year, expected_pages):
    rows=[];groups=[];page_counts={};printed=None;printed_count=None;summary_page=None
    seen_pages=[]
    for n,page in enumerate(text.split('\f'),1):
        header=next((s for s in page.splitlines() if s.strip().startswith('Employee ') and 'Position' in s and 'Expenses' in s),None)
        if header is None: continue
        seen_pages.append(n)
        compact=' '.join(page.upper().split())
        if f'JANUARY 1, {year} TO DECEMBER 31, {year}' not in compact:
            raise ValueError(f'Unverified employee calendar period on physical page {n}')
        anchors=anchors_from_layout(header,component_labels(year));count=0
        for line in page.splitlines():
            if 'Group:' in line and not any(c.isdigit() for c in line): groups.append(line.strip())
            if re.match(r'^\s*(?:Total )?Remuneration over \$75,000 and expenses:',line):
                if printed is not None: raise ValueError('Repeated grand named-employee subtotal')
                printed,_=layout_values(line,anchors,5)
                printed_count=int(re.search(r'expenses:\s+(\d+)',line)[1]);summary_page=n
            if ',' not in line[:45] or not MONEY.search(line) or re.match(r'^\s*(?:Total )?Remuneration ',line): continue
            values,tokens=layout_values(line,anchors,5)
            if not tokens: continue
            prefix=line[:tokens[0].start()].strip(' $')
            # Source glyphs are adjacent at the name/title boundary. The separate
            # PDF text spans and rendered page establish this exact split.
            if year==2019 and n==18 and prefix=='Rubadeau,Tkachuk, Jennifer ACivic Events Coordinator':
                name,position='Rubadeau,Tkachuk, Jennifer A','Civic Events Coordinator'
            else:
                fields=re.split(r'\s{2,}',prefix)
                if len(fields)!=2: raise ValueError(f'Unresolved name/title boundary on page {n}: {prefix!r}')
                name,position=fields
            pay,expense=amount_from_components(values,year)
            rows.append([name,position,pay,expense,n,values]);count+=1
        page_counts[str(n)]=count
    if seen_pages != expected_pages: raise ValueError(f'Employee section pages changed: {seen_pages}')
    if printed is None or printed_count != len(rows): raise ValueError('Printed employee count disagrees with extraction')
    sums=[sum(r[5][i] or 0 for r in rows) for i in range(len(printed))]
    if sums != printed: raise ValueError(f'Employee component subtotals disagree: {sums} != {printed}')
    return rows,{'rowsByPhysicalPage':page_counts,'printedNamedEmployeeCount':printed_count,
                 'printedComponentSubtotalsCents':printed,'allComponentSubtotalsExact':True,
                 'summaryPhysicalPage':summary_page,'sourceGroupHeadings':list(dict.fromkeys(groups))}


def positioned_words(page):
    import pymupdf
    out=[]
    for w in page.get_text('words'):
        box=pymupdf.Rect(w[:4])*page.rotation_matrix
        value=(*box,w[4])
        # The 2019 headers use four closely overprinted text layers. Deduplicate
        # only identical glyph text at the same location, never payment records.
        if not any(v[4]==value[4] and abs(v[0]-value[0])<0.6 and abs(v[1]-value[1])<0.6 for v in out[-120:]): out.append(value)
    return out


def coordinate_values(line, anchors, tolerance=16):
    values=[None]*len(anchors);found=[];seen=set()
    for w in line:
        if not MONEY.fullmatch(w[4]): continue
        i=min(range(len(anchors)),key=lambda i:abs(w[2]-anchors[i]))
        if abs(w[2]-anchors[i])>=tolerance:continue
        if i in seen: raise ValueError('Multiple PDF-coordinate monetary cells in one column')
        values[i]=cents(w[4]);found.append(w);seen.add(i)
    return values,found


def parse_employee_coordinates(document, year, pages):
    rows=[]
    for n in pages:
        ws=positioned_words(document[n-1]);head=next(w for w in ws if w[4]=='Employee')
        hs=sorted([w for w in ws if abs(w[1]-head[1])<0.7],key=lambda w:w[0])
        position_start=next(w[0] for w in hs if w[4]=='Position')-3.5
        labels=['Pay','Payout','Payout','Compensation','$75,000','Expenses'] if year<2022 else ['Pay','**','Expenses']
        anchors=[];left=0
        for label in labels:
            w=next(w for w in hs if w[4]==label and w[0]>=left);anchors.append(w[2]);left=w[2]
        base_words=[w for w in ws if re.fullmatch(r'\d[\d,]*\.\d{2}',w[4]) and abs(w[2]-anchors[0])<6 and w[1]>head[1]+4]
        for base in sorted(base_words,key=lambda w:w[1]):
            line=sorted([w for w in ws if abs(w[1]-base[1])<1.1],key=lambda w:w[0])
            name=' '.join(w[4] for w in line if w[0]<position_start)
            joined=year==2019 and n==18 and name=='Rubadeau,Tkachuk, Jennifer ACivic'
            if joined: name='Rubadeau,Tkachuk, Jennifer A'
            if ',' not in name or name.startswith(('Total','Remuneration')):continue
            values,monetary=coordinate_values(line,anchors)
            first=min(w[0] for w in monetary)
            position=' '.join(w[4] for w in line if position_start<=w[0]<first and w[4]!='$')
            if joined:
                spans=[''.join(chr(c[0]) for c in span['chars']) for span in document[n-1].get_texttrace()]
                if name not in spans or 'Civic Events Coordinator' not in spans: raise ValueError('Reviewed joined-cell evidence changed')
                position='Civic '+position
            pay,expense=amount_from_components(values,year)
            rows.append([name,position,pay,expense,n,values])
    return rows


def parse_council_layout(text, year, n):
    page=text.split('\f')[n-1]
    if f'{year} ELECTED OFFICIALS' not in page.upper():raise ValueError('Elected schedule year missing')
    header=next(s for s in page.splitlines() if re.match(r'^\s*Name\s+Position',s))
    anchors=anchors_from_layout(header,ELECTED_LABELS);rows=[];printed=None
    for line in page.splitlines():
        if re.search(r'\b(Councilor|Mayor)\s+',line):
            name,position,_=re.split(r'\s{2,}',line.strip(' *'),maxsplit=2)
            values,_=layout_values(line,anchors,8)
            pay,expense=amount_from_components(values,year,True)
            rows.append([name,position,pay,expense,n,values])
        elif rows and line.count('$')>=5:
            printed,_=layout_values(line,anchors,8)
    sums=[sum(r[5][i] or 0 for r in rows) for i in range(5)]
    if printed != sums:raise ValueError(f'Elected component controls disagree: {sums} != {printed}')
    return rows,{'rowsByPhysicalPage':{str(n):len(rows)},'printedComponentSubtotalsCents':printed,
                 'allComponentSubtotalsExact':True,'summaryPhysicalPage':n}


def parse_council_coordinates(document,year,n):
    ws=positioned_words(document[n-1]);head=next(w for w in ws if w[4]=='Name')
    anchors=[next(w[2] for w in ws if w[4]==label and abs(w[1]-head[1])<9) for label in ELECTED_LABELS]
    rows=[]
    for position in sorted((w for w in ws if w[4] in ('Councilor','Mayor')),key=lambda w:w[1]):
        line=sorted([w for w in ws if abs(w[1]-position[1])<1.2],key=lambda w:w[0])
        name=' '.join(w[4] for w in line if w[0]<position[0]-1 and w[4]!='***')
        values,_=coordinate_values(line,anchors,30)
        pay,expense=amount_from_components(values,year,True)
        rows.append([name,position[4],pay,expense,n,values])
    return rows


def compare_readers(layout,coordinates):
    def key(r):return tuple(r[:5])+tuple(r[5])
    a,b=Counter(map(key,layout)),Counter(map(key,coordinates))
    if a!=b:raise ValueError(f'PDF readers disagree: missing={list((a-b).elements())[:3]}, extra={list((b-a).elements())[:3]}')


def glyph_corrected_fields(page,name,position):
    """2019 font glyph16 is a rendered hyphen; glyph15 is the real comma."""
    corrections=[];mapping={}
    for span in page.get_texttrace():
        if span['font']!='FranklinGothicBook':continue
        original=''.join(chr(c[0]) for c in span['chars'])
        corrected=''.join('-' if c[0]==44 and c[1]==16 else chr(c[0]) for c in span['chars'])
        if original!=corrected:mapping[original]=corrected
    result=[]
    for field,value in [('name',name),('position',position)]:
        corrected=mapping.get(value,value)
        # Field strings can have whitespace normalization; compare normalized span text.
        if corrected==value:
            for original,replacement in mapping.items():
                if ' '.join(original.split())==value:corrected=' '.join(replacement.split());break
        if corrected!=value:corrections.append({'field':field,'extracted':value,'rendered':corrected,'font':'FranklinGothicBook','glyphId':16})
        result.append(corrected)
    return *result,corrections


def process(pdf,entry):
    import pymupdf
    raw=pdf.read_bytes()
    if digest(raw)!=entry['pdfSha256']:raise ValueError('Source PDF fingerprint changed; review required')
    text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True)
    document=pymupdf.open(pdf)
    if len(document)!=entry['pdfPages'] or len(text.split('\f'))-1!=len(document):raise ValueError('PDF page count changed')
    year=int(entry['year']);employees,employee_review=parse_employee_layout(text,year,entry['employeePages'])
    employee_coordinates=parse_employee_coordinates(document,year,entry['employeePages'])
    compare_readers(employees,employee_coordinates)
    council,council_review=parse_council_layout(text,year,entry['electedPage'])
    compare_readers(council,parse_council_coordinates(document,year,entry['electedPage']))
    results=[]
    for category,rows,review in [('employees',employees,employee_review),('elected-officials',council,council_review)]:
        normalized=[];audit=[];corrections=[]
        for name,position,pay,expense,n,components in rows:
            if year==2019:
                name,position,changes=glyph_corrected_fields(document[n-1],name,position)
                corrections.extend({'physicalPdfPage':n,**c} for c in changes)
            normalized.append([SLUG,name,position,dollars(pay),dollars(expense),n])
            audit.append({'name':name,'position':position,'physicalPdfPage':n,'componentsCents':components})
        expected_count=entry['employeeRows'] if category=='employees' else entry['electedRows']
        if len(rows)!=expected_count:raise ValueError('Reviewed row count changed')
        review.update({'sourceFingerprintVerified':True,'pdfPages':len(document),
                      'independentPdfReaders':'Poppler layout and separately parsed PyMuPDF word coordinates',
                      'allRowFieldsAndMultiplicitiesAgree':True,'rowsIndependentlyChecked':len(rows),
                      'unparsedRows':0,'glyphCorrections':corrections,
                      'negativeExpenseRows':sum(r[3] is not None and r[3]<0 for r in rows),
                      'missingExpenseRows':sum(r[3] is None for r in rows),
                      'explicitZeroExpenseRows':sum(r[3]==0 for r in rows),
                      'exactDuplicateSourceRows':sum(v-1 for v in Counter(tuple(r[:5]) for r in normalized).values()),
                      'visuallyReviewedPhysicalPages':entry['visuallyReviewedPages'] if category=='employees' else [entry['electedPage']],
                      'visualReviewDate':'2026-10-30'})
        if year==2019 and category=='employees':review['joinedCellCorrection']={'physicalPdfPage':18,'name':'Rubadeau-Tkachuk, Jennifer A','position':'Civic Events Coordinator','evidence':'Rendered page and separate PDF text spans establish the boundary; no monetary value changed.'}
        results.append((category,normalized,audit,review))
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=Path('/tmp/pofbc-additional-sources'))
    p.add_argument('--output',type=Path,default=OUT)
    p.add_argument('--offline',action='store_true')
    args=p.parse_args();inputs=json.loads((OUT/'reviewed-inputs.json').read_text())
    pending={};sources=[]
    for entry in inputs['sources']:
        pdf=args.cache/('prince-george-'+entry['year']+'.pdf')
        if not pdf.exists():
            if args.offline:raise ValueError(f'Missing cached PDF {pdf}')
            raw=urllib.request.urlopen(entry['sourceUrl'],timeout=60).read()
            if not raw.startswith(b'%PDF-'):raise ValueError('Official URL did not return a PDF')
            pdf.parent.mkdir(parents=True,exist_ok=True);pdf.write_bytes(raw)
        for category,rows,audit,review in process(pdf,entry):
            data=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode();compressed=gzip.compress(data,compresslevel=9,mtime=0)
            year=entry['year'];file=year+'-'+category+'.json.gzip';pending[file]=compressed
            auditfile='audit/'+year+'-'+category+'-components.json.gzip'
            schema=(['basePay','overtimePayout','vacationPayout','otherCompensation','printedRemuneration','expenses'] if int(year)<2022 else ['basePay','otherCompensation','expenses']) if category=='employees' else ['taxableNonExpensePortion','vehicleAllowance','printedRemuneration','expenses','benefits']
            auditdata=json.dumps({'componentUnit':'CAD cents','componentFields':schema,'rows':audit},ensure_ascii=False,separators=(',',':')).encode()
            pending[auditfile]=gzip.compress(auditdata,compresslevel=9,mtime=0)
            source={'id':'prince-george-sofi-'+year+'-'+category,'employerSlug':SLUG,'employerName':'City of Prince George',
                    'sector':'Municipalities','year':year,'slug':year,'periodType':'calendar',
                    'periodStart':year+'-01-01','periodEnd':year+'-12-31',
                    'title':f'City of Prince George {year} Statement of Financial Information: {category}',
                    'sourceUrl':entry['sourceUrl'],'sourceIndexUrl':'https://www.princegeorge.ca/finance',
                    'sha256':entry['pdfSha256'],'file':file,'dataSha256':digest(compressed),'normalizedSha256':digest(data),
                    'category':'employee-remuneration' if category=='employees' else 'elected-officials',
                    'scope':'named-employees-over-threshold' if category=='employees' else 'elected-officials',
                    'scopeDescription':'Published employee cohort, including Library employees where present' if category=='employees' else 'Mayor and councillor remuneration; separate from the employee cohort',
                    'threshold':75000 if category=='employees' else None,'thresholdRule':'over' if category=='employees' else None,
                    'currency':'CAD','amountUnit':'dollars','amountPrecision':'cents','nameDisclosure':'published-full-name',
                    'positionDisclosure':'published','rowCount':len(rows),
                    'totalRemuneration':float(sum(Decimal(str(r[3])) for r in rows)),
                    'totalExpenses':float(sum(Decimal(str(r[4])) for r in rows if r[4] is not None)),
                    'pages':sorted({r[-1] for r in rows}),'status':'verified','verifiedOn':'2026-10-30',
                    'validation':review,'componentAuditFile':auditfile,'componentAuditSha256':digest(pending[auditfile]),
                    'notes':['Actual January–December calendar year; not relabelled as an April–March fiscal period.',
                             'Source cents and negative expenses are preserved. Expense blanks and dashes remain missing; numeric zero remains zero.',
                             'Names and repeated observations are source disclosures, not independently verified personal identities.']}
            if category=='employees':
                source['notes'] += ['The employee threshold applies to remuneration, not base pay. No under-threshold aggregates, suppliers, employer payroll charges or elected officials are included.',
                    '2019–2021 use the published total remuneration column once; base, overtime, vacation and other pay are retained only as audit components.' if int(year)<2022 else 'Remuneration is the exact sum of the two source compensation columns: base pay plus all other compensation. Expenses are separate. Blank/dash component cells contribute no amount, and their original missing markers remain in the component audit.',
                    'Cohort definitions change: 2020–2022 explicitly include a Library group; 2019 includes Library positions in its combined list. The 2024–2025 schedules have no Library group.']
                if year=='2025':source['notes'].append('The printed all-employees other-compensation grand total $3,293,593.88 does not equal the printed named $2,930,049.95 plus under-threshold $467,608.80 subtotals (difference -$104,064.87). The named rows exactly reconcile to their own subtotals; the unrelated grand total is preserved as a source discrepancy and not used to alter them.')
            else:
                source['notes'] += ['Uses the report total S.168(1)(a), including the vehicle allowance once. Reported benefits S.168(1)(c) are retained separately in the component audit and are not added to remuneration.',
                    'Published expense treatment excludes GST where applicable. Contract/committee footnote markers are not part of names; the source report supplies their context.']
            if year=='2019':source['notes'].append('The embedded FranklinGothicBook glyph16 renders a hyphen but extracts as a comma. Glyph-based reviewed field corrections restore those hyphens; glyph15 commas are preserved. See validation.glyphCorrections.')
            sources.append(source)
    manifest={'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources,
              'unparsedSources':[{'id':'prince-george-sofi-2023','employerSlug':SLUG,'year':'2023','periodType':'calendar',
                 'sourceUrl':'https://pub-princegeorge.escribemeetings.com/filestream.ashx?DocumentId=26123',
                 'indexUrl':'https://www.princegeorge.ca/finance','status':'held-for-review',
                 'reason':'Official 2023 attachment returned HTTP 403; original PDF not obtained or verified.',
                 'nextAction':'Obtain the original 2023 SOFI PDF from the City or an accessible official archive, then verify both named schedules.'}]}
    pending['sources.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    for name,data in pending.items():
        path=args.output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps({'acceptedSources':len(sources),'employeeRows':sum(s['rowCount'] for s in sources if s['category']=='employee-remuneration'),
                      'electedOfficialRows':sum(s['rowCount'] for s in sources if s['category']=='elected-officials'),
                      'periods':[{'year':s['year'],'category':s['category'],'rows':s['rowCount'],'remuneration':s['totalRemuneration'],'expenses':s['totalExpenses']} for s in sources]},indent=2))


if __name__=='__main__':main()
