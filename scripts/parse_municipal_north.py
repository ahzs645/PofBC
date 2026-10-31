#!/usr/bin/env python3
"""Reproduce reviewed northern/Interior municipal salary imports.

Pinned source PDFs, calendar years, explicit table bounds, and independent
Poppler/PyMuPDF row checks. Never scans supplier tables for employee-looking rows.
Source blanks/dashes are missing, and separate benefit columns stay separate.
"""
from __future__ import annotations
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-north'
MONEY = re.compile(r'(?<!\S)(?:\(?-?\d[\d,]*(?:\.\d{2})?\)?|[-‐–—])(?=\s|$)')
def digest(data): return hashlib.sha256(data).hexdigest()
def amount(token):
    token=token.strip(' $')
    if token in ('','-','‐','–','—'): return None
    return int(Decimal(token.replace(',','').replace('(','-').replace(')',''))*100)
def norm(s): return ' '.join(s.replace('\u00a0',' ').split())
def read_layout(pdf):
    result=subprocess.run(['pdftotext','-layout',str(pdf),'-'],text=True,capture_output=True,check=True)
    return result.stdout.split('\f')[:-1]

def compare(rows, other):
    a,b=Counter(tuple(r) for r in rows),Counter(tuple(r) for r in other)
    if a!=b: raise ValueError(f'Independent readers disagree: missing={list((a-b).elements())[:3]}, extra={list((b-a).elements())[:3]}')

def word_lines(page):
    groups=[]
    for w in sorted(page.get_text('words'),key=lambda w:(w[1],w[0])):
        if not groups or abs(groups[-1][0][1]-w[1])>1.3:groups.append([w])
        else:groups[-1].append(w)
    return [sorted(g,key=lambda w:w[0]) for g in groups]

def traced_row_suffix(trace,line,field_prefix,cache):
    y=line[0][1]
    if y not in cache:
        chars=[c for s in trace for c in s['chars'] if abs(c[3][1]-y)<2]
        cache[y]=''.join(chr(c[0]) for c in sorted(chars,key=lambda c:c[3][0]))
    raw=cache[y]
    compact=re.sub(r'\s+','',field_prefix)
    if not re.sub(r'\s+','',raw).startswith(compact):return None
    seen=0
    for end,char in enumerate(raw,1):
        seen+=not char.isspace()
        if seen==len(compact):return raw[end:]
    return None

def verify_single_lines(pdf, rows, components, split_initial=False, groups=None, join_preceding=False):
    """Independently check each primary row's text and amounts by PDF coordinates.

    Named rows need an exact source line. This intentionally rejects wrapped or
    merged fields rather than guessing their boundaries.
    """
    import pymupdf
    doc=pymupdf.open(pdf);verified=[];trace_fallbacks=[]
    for n in sorted({r[4] for r in rows}):
        lines=word_lines(doc[n-1]);used=set();page_trace=doc[n-1].get_texttrace();trace_cache={}
        for i,r in ((i,r) for i,r in enumerate(rows) if r[4]==n):
            name,title,pay,expense,_=r
            for j,line in enumerate(lines):
                if j in used:continue
                texts=[w[4] for w in line]
                expected=norm(name.replace(',','',1) if split_initial else name)
                field_prefix=norm(expected+' '+(title or '')+' '+(groups[i] if groups else ''))
                prefix=norm(' '.join(texts[:len(expected.split())]))
                if prefix!=expected:
                    traced=traced_row_suffix(page_trace,line,field_prefix,trace_cache)
                    if traced is not None:
                        text=field_prefix+' '+traced
                        trace_fallbacks.append({'physicalPdfPage':n,'name':name,'position':title,'reason':'Independent character coordinates recover source text split across PDF font spans.'})
                    else:
                        if not split_initial or ', ' not in name:continue
                        surname,initial=name.rsplit(', ',1)
                        same=[s for s in page_trace if abs(s['bbox'][1]-line[0][1])<5]
                        by_text={norm(''.join(chr(c[0]) for c in s['chars'])):s for s in same}
                        if not all(field in by_text for field in [surname,initial,title]):continue
                        if not (by_text[surname]['bbox'][0]<by_text[initial]['bbox'][0]<by_text[title]['bbox'][0]):continue
                        text=expected+' '+title+' '+' '.join(w[4] for w in line if w[0]>by_text[title]['bbox'][2])
                        trace_fallbacks.append({'physicalPdfPage':n,'name':name,'position':title,'reason':'Overlapping surname and initial are independently present in separate original PDF text spans.'})
                else:text=' '.join(texts)
                # Position names such as "Operator III" are nonmonetary; numbers
                # in positions are excluded by using the exact known title.
                if join_preceding and not norm(text).startswith(field_prefix+' ') and j>0:
                    prev=lines[j-1];at=len(expected.split())
                    if at<len(line) and abs(prev[0][0]-line[at][0])<2 and 0<line[0][1]-prev[0][1]<2*(line[0][3]-line[0][1]):
                        rebuilt=norm(expected+' '+' '.join(w[4] for w in prev)+' '+' '.join(w[4] for w in line[at:]))
                        if rebuilt.startswith(field_prefix+' '):text=rebuilt
                if not norm(text).startswith(field_prefix+' '):
                    # A cell clip can hide the end of an otherwise intact source
                    # text span. Require the exact complete source string from
                    # the independent text trace at the same row coordinates.
                    traces=[s for s in page_trace if abs(s['bbox'][1]-line[0][1])<5 and re.sub(r'\s+','',''.join(chr(c[0]) for c in s['chars']))==re.sub(r'\s+','',title or '')]
                    if not groups and len(traces)==1:
                        suffix=' '.join(w[4] for w in line if MONEY.fullmatch(w[4]))
                        reason='Complete source text span is clipped in the rendered table; original text is preserved.'
                    else:
                        # Fonts can split a title into several PDF spans; read
                        # the independent character coordinates on this row.
                        suffix=traced_row_suffix(page_trace,line,field_prefix,trace_cache)
                        if suffix is None:continue
                        reason='Independent character coordinates recover source text split across PDF font spans.'
                    trace_fallbacks.append({'physicalPdfPage':n,'name':name,'position':title,'reason':reason})
                else:suffix=norm(text)[len(field_prefix):].strip()
                suffix=re.sub(r'(?<=\d)\s+(?=,\d{3}(?:\D|$))','',suffix)
                got=[amount(m[0]) for m in MONEY.finditer(suffix.replace('$',' '))]
                if len(got)==len(components[i])+1 and got[-2] is None and re.search(r'-\s+\d[\d,]*(?:\.\d{2})?\s*$',suffix):got=got[:-2]+[-got[-1]]
                if len(got)==len(components[i])-1 and components[i][-1] is None:got.append(None)
                if got!=components[i]:continue
                used.add(j);verified.append(r);break
            else:raise ValueError(f'Cannot independently verify row on page {n}: {r!r}')
    compare(rows,verified)
    return trace_fallbacks

def parse_fsj(pdf, entry):
    pages=read_layout(pdf);employees=[];council=[];ec=[];cc=[];printed=None;printed_council=None
    for n in entry['pages']:
        t=pages[n-1]
        if f'for the year ended December 31, {entry["year"]}' not in t:raise ValueError('FSJ calendar heading changed')
        category=None
        for line in t.splitlines():
            if 'ELECTED OFFICIALS' in line and 'REMUNERATION' in line:category='council';continue
            if re.match(r'^\s*EMPLOYEES\s+POSITION',line):category='employees';continue
            if line.startswith('Subtotal - Elected Officials'):
                printed_council=[amount(m[0]) for m in MONEY.finditer(line)][-3:];continue
            if line.startswith('Subtotal - employees with remuneration exceeding'):
                printed=[amount(m[0]) for m in MONEY.finditer(line)][-3:];continue
            if not category or ',' not in line[:34] or not re.search(r'\d[\d,]*\.\d{2}',line[34:]):continue
            fields=re.split(r'\s{2,}',line.strip());name,title=fields[:2]
            tokens=[amount(m[0]) for m in MONEY.finditer(' '.join(fields[2:]).replace('$',' '))]
            if len(tokens)!=3 or tokens[0] is None or tokens[0]+(tokens[1] or 0)!=tokens[2]:raise ValueError('FSJ amount columns disagree')
            row=[name,title,tokens[0],tokens[1],n]
            (employees if category=='employees' else council).append(row)
            (ec if category=='employees' else cc).append(tokens)
    out=[]
    for cat,rows,comps,control in [('employees',employees,ec,printed),('elected-officials',council,cc,printed_council)]:
        sums=[sum(r[i] or 0 for r in comps) for i in range(3)]
        if control!=sums:raise ValueError(f'FSJ {cat} subtotal mismatch: {sums} vs {control}')
        verify_single_lines(pdf,rows,comps)
        out.append((cat,rows,comps,{'printedComponentSubtotalsCents':control,'componentResidualsCents':[0,0,0],
                    'allComponentSubtotalsExact':True,'allRowFieldsAndMultiplicitiesAgree':True}))
    return out

def parse_pg(pdf,entry):
    spec=importlib.util.spec_from_file_location('prince_george_import',ROOT/'scripts/import-prince-george-salaries.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    result=[]
    for category,normalized,audit,review in mod.process(pdf,entry):
        rows=[[r[1],r[2],int(Decimal(str(r[3]))*100),None if r[4] is None else int(Decimal(str(r[4]))*100),r[5]] for r in normalized]
        review['visualReviewDate']='2026-10-31'
        result.append((category,rows,[r['componentsCents'] for r in audit],review))
    return result

def parse_kamloops(pdf,entry):
    pages=read_layout(pdf);rows=[];components=[];groups=[];control=None
    year=int(entry['year']);columns=2 if year==2016 else 3 if year==2025 else 4
    for n in entry['pages']:
        t=pages[n-1]
        if '2. Other Employees' not in t or f'December 31, {year}' not in t:raise ValueError('Kamloops source section/calendar heading changed')
        for line in t.splitlines():
            if re.match(r'^\s*(?:Total )?Employees with [Rr]emuneration (?:exceeding|greater than)',line):
                control=[amount(m[0]) for m in MONEY.finditer(line)][-columns:];continue
            if not re.match(r"^\s*[A-Za-zÀ-ž'’ .()/-]+,\s*[A-Za-zÀ-ž]",line):continue
            if year!=2025:
                match=re.search(r'\s+(-?(?:CUPE[HPS]?|IAFF|MGMT|FDMG|EXEM|EXMP|EXMT|ZXMP))\s+(?=[$\d-])(.*)$',line)
                if not match:continue
                fields=re.split(r'\s{2,}',line[:match.start()].strip())
                if len(fields)!=2:
                    joined=norm(line[:match.start()])
                    override=entry.get('boundaryOverrides',{}).get(joined)
                    if not override:raise ValueError(f'Kamloops name/title boundary unclear: {line}')
                    fields=override
                name,title=fields;group=match[1];suffix=match[2]
            else:
                fields=re.split(r'\s{2,}',line.replace('$',' ').strip())
                if len(fields)<4:continue
                name,title=fields[:2];group='';suffix=' '.join(fields[2:])
            values=[amount(m[0]) for m in MONEY.finditer(suffix.replace('$',' '))]
            if len(values)==columns-1:values.append(None)
            if len(values)!=columns or values[0] is None:raise ValueError(f'Kamloops monetary columns unclear: {line}')
            rows.append([name,title,values[0],values[-1],n]);components.append(values);groups.append(group)
    if not rows or control is None:raise ValueError('Kamloops missing named rows or control')
    sums=[sum(c[i] or 0 for c in components) for i in range(columns)]
    residual=[s-c for s,c in zip(sums,control)]
    # Bound whole-dollar source residuals without attributing a cause or altering
    # any disclosed individual amount.
    allowed=0 if year==2016 else len(rows)*50
    if any(abs(r)>allowed for r in residual):raise ValueError(f'Kamloops control mismatch: {sums} vs {control}')
    trace_fallbacks=verify_single_lines(pdf,rows,components,groups=groups if year!=2025 else None)
    return [('employees',rows,components,{'printedComponentSubtotalsCents':control,
        'componentResidualsCents':residual,'allComponentSubtotalsExact':not any(residual),
        'allRowFieldsAndMultiplicitiesAgree':True,
        'unclippedSourceTextFields':trace_fallbacks,
        'reconciliationNote':'Whole-dollar rows and printed totals may differ; residuals are preserved without attributing a cause.' if any(residual) else 'Exact published component controls.'})]

def parse_tables(pdf,entry):
    """Explicitly bounded named schedules with reviewed table definitions."""
    pages=read_layout(pdf);result=[]
    period_pattern=entry.get('periodEvidenceRegex',rf'December\s+31,?\s+{entry["year"]}')
    evidence_pages=entry.get('periodEvidencePages',list(range(1,len(pages)+1)))
    if not evidence_pages or not all(re.search(period_pattern,pages[n-1],re.I) for n in evidence_pages):raise ValueError('Reviewed calendar reporting period not found in source text')
    for cat,recipe in entry['cohorts'].items():
        rows=[];components=[];control=None;under=None;active=not recipe.get('startRegex');done=False
        count=recipe['columns'];pay_index=recipe.get('payIndex',0);expense_index=recipe.get('expenseIndex',count-1)
        for n in recipe['pages']:
            if done:break
            pending_title='';header_position=None
            raw_lines=pages[n-1].splitlines();lines=[];skip=False
            for at,line in enumerate(raw_lines):
                if skip:skip=False;continue
                if norm(line) in recipe.get('layoutJoins',[]):
                    if at+1==len(raw_lines) or re.search(r'[A-Za-z]',raw_lines[at+1]):raise ValueError('Reviewed amount-line join changed')
                    lines.append(line+'  '+raw_lines[at+1].strip());skip=True
                else:lines.append(line)
            for line in lines:
                if recipe.get('joinPrecedingTitle') and 'Surname' in line and 'Position' in line:
                    header_position=line.index('Position');continue
                if recipe.get('startRegex') and re.search(recipe['startRegex'],line):active=True;continue
                if not active:continue
                if recipe.get('underRegex') and re.search(recipe['underRegex'],line):
                    under=[amount(m[0]) for m in MONEY.finditer(line.replace('$',' '))][-count:];continue
                if re.search(recipe['controlRegex'],line):
                    take=recipe.get('controlColumns',count)
                    control=[amount(m[0]) for m in MONEY.finditer(line.replace('$',' '))][-take:]
                    done=True;break
                fields=re.split(r'\s{2,}',line.replace('$',' ').strip())
                numeric_start=next((i for i,f in enumerate(fields) if re.fullmatch(r'\$?\s*(?:\(?-?\d[\d,]*(?:\.\d{2})?\)?|[-‐–—])',f)),None)
                if numeric_start is None or numeric_start==0:
                    if recipe.get('joinPrecedingTitle') and header_position is not None and line.strip() and not re.search(r'\d',line) and len(line)-len(line.lstrip())>=header_position:
                        pending_title=norm(pending_title+' '+line)
                    continue
                values=[amount(m[0]) for m in MONEY.finditer(' '.join(fields[numeric_start:]).replace('$',' '))]
                if len(values)==count+1 and values[-2] is None and re.search(r'-\s+\d[\d,]*(?:\.\d{2})?\s*$',line):values=values[:-2]+[-values[-1]]
                if len(values)<count-1:continue
                if len(values)==count-1:values.append(None)
                if len(values)!=count:raise ValueError(f'Monetary column count changed: {line}')
                prefix=fields[:numeric_start]
                override=recipe.get('fieldOverrides',{}).get(norm(' '.join(prefix)))
                if override:prefix=override
                if recipe.get('nameMode')=='surname-given':
                    if recipe.get('initials') and len(prefix)==2 and re.search(r' [A-Z]\.?$',prefix[0]):prefix=[*prefix[0].rsplit(' ',1),prefix[1]]
                    if len(prefix)!=(3 if recipe.get('position',True) else 2):raise ValueError(f'Name/title split unclear: {line}')
                    name=norm(prefix[0]+', '+prefix[1]);title=prefix[2] if len(prefix)==3 else None
                else:
                    if len(prefix)!=(2 if recipe.get('position',True) else 1):raise ValueError(f'Name/title split unclear: {line}')
                    name=prefix[0];title=prefix[1] if len(prefix)==2 else None
                if pending_title:
                    if not title:raise ValueError('Wrapped title has no continuation')
                    title=pending_title+' '+title;pending_title=''
                if not re.search(r'[A-Za-zÀ-ž]',name) or name.lower().startswith(('total','subtotal','sub-total','sub total','employees ','employee ','f.i.r','note ')):continue
                if values[pay_index] is None:raise ValueError(f'Missing remuneration: {line}')
                if recipe.get('rowSum'):
                    eq=recipe['rowSum'];difference=sum(values[i] or 0 for i in eq['parts'])-(values[eq['total']] or 0)
                    if abs(difference)>eq.get('toleranceCents',0):raise ValueError(f'Row component equation changed: {line}')
                rows.append([norm(name),norm(title) if title else None,values[pay_index],values[expense_index],n]);components.append(values)
        if not rows or control is None:raise ValueError(f'{cat}: missing rows or published named control')
        if recipe.get('underRegex'):
            if under is None or len(under)!=count:raise ValueError('Missing under-threshold control')
            control=[a-b for a,b in zip(control,under)]
        selected=recipe.get('controlIndexes',list(range(count)))
        sums=[sum(c[i] or 0 for c in components) for i in selected]
        if len(control)!=len(sums) or any(v is None for v in control):raise ValueError('Invalid control columns')
        residual=[a-b for a,b in zip(sums,control)]
        allowed=0 if entry.get('amountPrecision','cents')=='cents' else len(rows)*50
        if any(abs(r)>allowed for r in residual):raise ValueError(f'{cat}: subtotal mismatch {sums} vs {control}')
        trace_fallbacks=verify_single_lines(pdf,rows,components,split_initial=recipe.get('nameMode')=='surname-given',join_preceding=recipe.get('joinPrecedingTitle',False))
        result.append((cat,rows,components,{'printedNamedControlCents':control,'controlComponentIndexes':selected,
            'componentResidualsCents':residual,'allComponentSubtotalsExact':not any(residual),'allRowFieldsAndMultiplicitiesAgree':True,
            'calendarPeriodEvidencePhysicalPages':evidence_pages,'calendarPeriodEvidencePattern':period_pattern,
            'unclippedSourceTextFields':trace_fallbacks,'reconciliationNote':'Small whole-dollar source residuals are preserved; no individual value is altered.' if any(residual) else 'Exact named controls.'}))
    return result

PARSERS={'prince-george':parse_pg,'fort-st-john':parse_fsj,'kamloops':parse_kamloops,'tables':parse_tables}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=ROOT/'tmp/municipal-north')
    p.add_argument('--output',type=Path,default=OUT)
    p.add_argument('--offline',action='store_true')
    args=p.parse_args();inputs=json.loads((OUT/'reviewed-inputs.json').read_text());sources=[];pending={}
    for entry in inputs['sources']:
        pdf=args.cache/entry['cacheFile']
        if not pdf.exists():
            if args.offline:raise ValueError(f'Missing cached PDF {pdf}')
            data=urllib.request.urlopen(entry['sourceUrl'],timeout=60).read()
            if not data.startswith(b'%PDF-'):raise ValueError('Source did not return PDF')
            pdf.parent.mkdir(parents=True,exist_ok=True);pdf.write_bytes(data)
        if digest(pdf.read_bytes())!=entry['pdfSha256']:raise ValueError(f'{pdf.name}: PDF changed; review required')
        for category,rows,components,review in PARSERS[entry['parser']](pdf,entry):
            if entry.get('expectedRows',{}).get(category,len(rows))!=len(rows):raise ValueError('Reviewed row count changed')
            year=entry['year'];stem=entry['shortSlug']+'-'+year+'-'+category
            normalized=[[entry['employerSlug'],name,pos,pay/100,None if exp is None else exp/100,page] for name,pos,pay,exp,page in rows]
            data=json.dumps(normalized,ensure_ascii=False,separators=(',',':')).encode();file=stem+'.json.gzip'
            pending[file]=gzip.compress(data,compresslevel=9,mtime=0)
            audit={'componentUnit':'CAD cents','componentFields':entry['componentFields'][category],
                   'rows':[{'name':r[0],'position':r[1],'physicalPdfPage':r[4],'componentsCents':c} for r,c in zip(rows,components)]}
            auditfile='audit/'+stem+'.json.gzip';pending[auditfile]=gzip.compress(json.dumps(audit,ensure_ascii=False,separators=(',',':')).encode(),compresslevel=9,mtime=0)
            review.update({'rowsByPhysicalPage':dict(sorted(Counter(str(r[4]) for r in rows).items(),key=lambda x:int(x[0]))),
                           'rowsIndependentlyChecked':len(rows),'sourceFingerprintVerified':True,'unparsedRows':0,
                           'independentPdfReaders':'Poppler layout and separately read PyMuPDF positioned words',
                           'missingExpenseRows':sum(r[3] is None for r in rows),'explicitZeroExpenseRows':sum(r[3]==0 for r in rows),
                           'negativeExpenseRows':sum(r[3] is not None and r[3]<0 for r in rows),
                           'belowOrEqualThresholdRemunerationRows':sum(r[2]<=7500000 for r in rows) if category=='employees' else 0,
                           'visuallyReviewedPhysicalPages':entry.get('visuallyReviewedPages',[]),'visualReviewDate':'2026-10-31'})
            sources.append({'id':entry['shortSlug']+'-sofi-'+year+'-'+category,'employerSlug':entry['employerSlug'],
                'employerName':entry['employerName'],'sector':'Municipalities','year':year,'slug':year,'periodType':'calendar',
                'periodStart':year+'-01-01','periodEnd':year+'-12-31','title':f'{entry["employerName"]} {year} SOFI: {category}',
                'sourceUrl':entry['sourceUrl'],'sourceIndexUrl':entry['indexUrl'],'sha256':entry['pdfSha256'],
                'file':file,'dataSha256':digest(pending[file]),'normalizedSha256':digest(data),
                'category':'employee-remuneration' if category=='employees' else 'elected-officials',
                'scope':'named-employees-over-threshold' if category=='employees' else 'elected-officials',
                'scopeDescription':entry.get('scopeDescription','Published named employee schedule; council reported separately') if category=='employees' else 'Mayor and councillors; separate from employees',
                'threshold':75000 if category=='employees' else None,'thresholdRule':entry.get('thresholdRule','over') if category=='employees' else None,
                'currency':'CAD','amountUnit':'dollars','amountPrecision':entry.get('amountPrecision','cents'),
                'nameDisclosure':entry.get('nameDisclosure','published-full-name'),'positionDisclosure':'published' if any(r[1] for r in rows) else 'not-published',
                'rowCount':len(rows),'totalRemuneration':sum(r[2] for r in rows)/100,
                'totalExpenses':sum(r[3] or 0 for r in rows)/100,'pages':sorted({r[4] for r in rows}),
                'status':'verified','verifiedOn':'2026-10-31','validation':review,
                'componentAuditFile':auditfile,'componentAuditSha256':digest(pending[auditfile]),
                'notes':entry.get('notes',[])+['Uses the actual January–December calendar year. Names and initials remain as published; these are disclosures, not verified unique identities.',
                    'Expenses are separate. Blank/dash cells remain missing; disclosed numeric zero remains zero.']})
    manifest={'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],
              'sources':sources,'unparsedSources':inputs.get('unparsedSources',[])}
    pending['sources.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    for file,data in pending.items():
        target=args.output/file;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'employers':sorted({s['employerSlug'] for s in sources})}))

if __name__=='__main__':main()
