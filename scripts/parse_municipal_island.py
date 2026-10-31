#!/usr/bin/env python3
"""Reproduce reviewed municipal salary imports, with original-file fingerprints.

Usage: python scripts/parse_municipal_island.py --source-dir /tmp/municipal-island
Optional --fetch downloads the exact URLs in reviewed-inputs.json; changed bytes fail.
PyMuPDF and Poppler pdftotext are required. No totals are used to manufacture rows.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/municipal-island'
M = r'(?:\(?-?\s*\d[\d,]*(?:\.\d+)?\)?|-)'
PAIR = re.compile(r'\s{2,}('+M+r')(?:\s+('+M+r'))?\s*$')
TRIPLE = re.compile(r'\s{2,}('+M+r')\s+('+M+r')\s+('+M+r')\s*$')


def digest(data): return hashlib.sha256(data).hexdigest()
def norm(s): return re.sub(r'[^\w]', '', s).casefold()
def compact(value): return (json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
def number(s):
    if s is None: return None
    s = re.sub(r'[$,\s]', '', str(s))
    if s in ('', '-'): return None
    if s.startswith('(') and s.endswith(')'): s = '-'+s[1:-1]
    return Decimal(s)
def json_number(value):
    if value is None: return None
    return int(value) if value == int(value) else float(value)
def sum_values(rows, index): return sum((row[index] or Decimal(0) for row in rows), Decimal(0))


def source_bytes(source_dir, entry, fetch):
    target = source_dir / entry['localFile']
    snapshot=OUT/'raw'/(entry['localFile']+'.gzip')
    if not target.exists() and snapshot.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(gzip.decompress(snapshot.read_bytes()))
    if not target.exists() and fetch:
        url = urllib.parse.quote(entry['url'], safe=':/?&=%~')
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=90) as response: target.write_bytes(response.read())
    data = target.read_bytes()
    if digest(data) != entry['sha256']: raise ValueError(f'Unreviewed source bytes: {target}')
    return target, data


def extract_pages(path):
    data = subprocess.run(['pdftotext', '-layout', str(path), '-'], check=True, capture_output=True).stdout.decode()
    return data.split('\f')


def simple_rows(pages, entry):
    rows = []
    for page_number in entry['pages']:
        page = pages[page_number-1]
        for section in entry.get('pageSlices',[]):
            if section['page']==page_number:
                if section.get('after'): page=page.split(section['after'],1)[1]
                if section.get('before'): page=page.split(section['before'],1)[0]
        # The 2025 Saanich PDF vertically offsets this wrapped name and expense.
        # Both text extraction and the original positioned PDF block were reviewed.
        if entry['id'] == 'saanich-2025-employees' and page_number == 41:
            before = re.search(r'Blick McStravick,\s+448\s*\nAmanda\s+Park Planner Designer\s+88,878', page)
            if not before: raise ValueError('Reviewed Saanich wrapped row changed')
            page = page[:before.start()]+'Blick McStravick, Amanda  Park Planner Designer  88,878  448'+page[before.end():]
        pending = None
        for line in page.splitlines():
            line = line.replace('$', '')
            match = PAIR.search(line)
            if match:
                prefix = line[:match.start()].strip()
                fields = re.split(r',\s+|\s+-\s+', prefix, maxsplit=1) if entry.get('combinedNamePosition') else re.split(r'\s{2,}', prefix)
                if len(fields)<2 or not re.fullmatch(r"[A-Za-zÀ-ÿ'’. -]+(?:,.*)?", fields[0]): continue
                if any(term in fields[0].lower() for term in ('total', 'summary', 'name')): continue
                pay, expenses = number(match[1]), number(match[2])
                if pay is None: continue
                # Explicit reviewed page boundaries select the employee or council table.
                if entry['category']=='employee-remuneration' and (pay<75000 or pay==75000 and entry.get('thresholdRule','over')=='over'): raise ValueError(f'Unexpected threshold row {fields}')
                name=fields[0].rstrip('*') if entry.get('removeNameFootnotes') else fields[0]
                row = [name, ' '.join(fields[1:]), pay, expenses, page_number]
                rows.append(row); pending = row
            elif entry.get('appendPositionLines') and pending and line.strip() and not re.search(r'\d',line) and 18<=line.index(line.strip())<50 and len(line.strip())<65:
                pending[1]+=' '+line.strip()
            elif entry['city']=='saanich' and pending and line.strip()!='Exempt' and line.strip() and not re.search(r'\d|TOTAL|ADD:|STATEMENT|SCHEDULE|Prepared', line) and len(line.strip())<40 and line.index(line.strip())<10:
                pending[0] += ' '+line.strip()
            elif line.strip(): pending = None
    return rows


def verify_positioned_simple(path, rows, entry):
    document = fitz.open(path)
    for pno in entry['pages']:
        selected = [row for row in rows if row[4]==pno]
        page = document[pno-1]
        page_text = norm(page.get_text())
        position_headers=[w[0] for w in page.get_text('words') if w[4]=='Position']
        money_headers=[w[0] for w in page.get_text('words') if w[4].lower().startswith('remuneration')]
        money_x=entry.get('moneyX',380)
        name_x=entry.get('nameX',175 if entry['city']=='saanich' else min(position_headers)-1 if position_headers else 210)
        role_text=norm(' '.join(w[4] for w in page.get_text('words') if name_x<=w[0]<money_x))
        for name, position, *_ in selected:
            if norm(name) not in page_text: raise ValueError(f'Name absent in independent PDF extraction: {pno}: {name}')
            if norm(position) not in page_text and norm(position) not in role_text: raise ValueError(f'Position absent in independent PDF extraction: {pno}: {position}')
        if entry['city']=='saanich' and entry['year']=='2025':
            # In this source the expense baseline is 2.4 points above salary; a
            # wrapped name has a 10.38-point offset. Native blocks preserve the cells.
            blocks = page.get_text('blocks')
            for row in selected:
                matches = [b for b in blocks if norm(row[0]+row[1]) in norm(b[4])]
                if len(matches)!=1: raise ValueError(f'Ambiguous positioned row {row[0]}')
                lines=matches[0][4].splitlines(); joined=''
                for i,line in enumerate(lines):
                    joined+=norm(line)
                    if norm(row[0]+row[1]) in joined:
                        values=[number(s) for s in lines[i+1:] if re.fullmatch(M,s.replace('$','').strip())]
                        break
                if values[:2]!=row[2:4]: raise ValueError(f'Positioned cells disagree: {row}')
        else:
            lines=[]
            for word in sorted(page.get_text('words'),key=lambda w:(w[1],w[0])):
                if not lines or abs(lines[-1][0]-word[1])>3: lines.append([word[1],[]])
                lines[-1][1].append(word)
            actual=[]
            for _, line in lines:
                left=' '.join(w[4] for w in sorted(line,key=lambda w:w[0]) if w[0]<name_x)
                candidates=[r for r in selected if norm(r[0]+(' '+r[1] if entry.get('combinedNamePosition') else '')).startswith(norm(left)) and norm(left)]
                exact=[r for r in candidates if norm(r[0]+(' '+r[1] if entry.get('combinedNamePosition') else ''))==norm(left)]
                candidates=exact or candidates
                if not candidates: continue
                cells=[number(w[4]) for w in sorted(line,key=lambda w:w[0]) if w[0]>=money_x and re.fullmatch(M,w[4])]
                # Monetary tokens to the right are salary and expenses, omitting $.
                if not cells: continue
                names={norm(r[0]) for r in candidates}
                if len(names)!=1:raise ValueError(f'Ambiguous positioned name on page {pno}: {left}')
                actual.append((next(iter(names)),*tuple((cells+[None])[:2])))
            expected=Counter((norm(r[0]),r[2],r[3]) for r in selected)
            if Counter(actual)!=expected:
                raise ValueError(f'Independent monetary cells disagree {entry["id"]} page {pno}: {expected-Counter(actual)} / {Counter(actual)-expected}')
    return {'independentPdfReaders':'Poppler layout plus PyMuPDF positioned monetary cells and name/title text',
            'allMonetaryCellsAgree':True,'rowsIndependentlyChecked':len(rows)}


def read_victoria_csv(raw):
    try: text = raw.decode('utf-8-sig')
    except UnicodeDecodeError: text = raw.decode('cp1252')
    reader=csv.DictReader(io.StringIO(text));fields=reader.fieldnames
    n=next(k for k in fields if k.lower()=='employee');t=next(k for k in fields if k.lower()=='title')
    p=next(k for k in fields if k.lower().startswith('remuneration'))
    e=next(k for k in fields if k.strip().lower()=='expenses')
    b=next((k for k in fields if k.lower().startswith('taxable')),None)
    rows=[]; aggregates=[]
    for raw_row in reader:
        if raw_row[n] and raw_row[t]:
            rows.append([raw_row[n].strip(),raw_row[t].strip(),number(raw_row[p]),number(raw_row[e]),None,number(raw_row[b]) if b else None])
        else: aggregates.append(raw_row)
    return rows,aggregates


def victoria_rows(pages, csv_rows, entry):
    by_key=defaultdict(list)
    for row in csv_rows:by_key[norm(row[0]+row[1])].append(row)
    rows=[];components=[];disagreements=[];seen=Counter()
    for pno in entry['pages']:
        page=pages[pno-1]
        for replacement in entry.get('layoutRepairs',[]):
            if replacement['page']==pno:
                if replacement['before'] not in page:raise ValueError('Reviewed layout repair no longer matches')
                page=page.replace(replacement['before'],replacement['after'])
        for line in page.splitlines():
            line=line.replace('$','');m=TRIPLE.search(line)
            if not m:continue
            prefix=line[:m.start()].strip();key=norm(prefix);candidates=by_key.get(key,[])
            if not candidates:
                # Explicit source-title or clipped-PDF-name differences are pinned in the review.
                alias=entry.get('prefixAliases',{}).get(key)
                if alias:candidates=by_key.get(alias,[])
            if not candidates:continue
            if len(candidates)!=1:raise ValueError('Ambiguous Victoria source row')
            original=candidates[0];key=norm(original[0]+original[1]);seen[key]+=1
            values=[number(m[i]) for i in range(1,4)]
            position=entry.get('publishedTitles',{}).get(original[0],original[1])
            rows.append([original[0],position,values[0],values[2],pno]);components.append([original[0],values[0],values[1],values[2],pno])
            csv_values=[original[2],original[5],original[3]]
            if any(a is not None and b is not None and a!=b for a,b in zip(values,csv_values)):
                disagreements.append({'name':original[0],'page':pno,'pdf':[json_number(v) for v in values],'csv':[json_number(v) for v in csv_values]})
    expected=Counter(norm(r[0]+r[1]) for r in csv_rows)
    if seen!=expected:raise ValueError(f'Victoria PDF/CSV identities differ: {expected-seen} / {seen-expected}')
    return rows,components,disagreements


def run(args):
    config=json.loads((OUT/'reviewed-inputs.json').read_text());pending={};sources=[];audits=[]
    catalog_path,catalog_raw=source_bytes(args.source_dir,config['catalog'],args.fetch)
    catalog={item['id']:item for item in json.loads(catalog_raw)['results']}
    pending['raw/'+config['catalog']['localFile']+'.gzip']=gzip.compress(catalog_raw,mtime=0)
    for entry in config['accepted']:
        path,raw=source_bytes(args.source_dir,entry,args.fetch)
        audit={};components=[]
        if entry['format']=='pdf':
            pages=extract_pages(path);document=fitz.open(path)
            if not re.search(entry['periodEvidence'], ' '.join(' '.join(pages[:6]+[pages[p-1] for p in entry['pages']]).split()), re.I):raise ValueError(f'Period evidence missing: {entry["id"]}')
            if entry['city']=='victoria':
                csv_path,csv_raw=source_bytes(args.source_dir,entry['companionCsv'],args.fetch)
                csv_rows,aggregates=read_victoria_csv(csv_raw)
                rows,components,disagreements=victoria_rows(pages,csv_rows,entry)
                audit={'comparison':'Every named CSV identity and position matched to the original PDF; explicit reviewed title/clipping differences retained below. PDF monetary values take precedence.',
                       'companionCsvUrl':entry['companionCsv']['url'],'companionCsvSha256':digest(csv_raw),'csvPdfMonetaryDifferences':disagreements,
                       'excludedAggregateCsvRows':len(aggregates),'independentPdfMonetaryCheck':'Original PDF named control totals compared with all three extracted monetary columns; companion official CSV supplies an independent tabular rendering.'}
                pending['raw/'+entry['companionCsv']['localFile']+'.gzip']=gzip.compress(csv_raw,mtime=0)
                actual_components=[sum_values(components,i) for i in (1,2,3)]
                expected_components=[Decimal(str(v)) for v in entry['componentTotals']]
                if actual_components!=expected_components:raise ValueError(f'Victoria component mismatch {entry["id"]}')
                audit['pdfPrintedComponentSubtotals']=entry['printedComponentSubtotals']
                audit['extractedComponentTotals']=[json_number(v) for v in actual_components]
                audit['componentResiduals']=[json_number(a-Decimal(str(b))) for a,b in zip(actual_components,entry['printedComponentSubtotals'])]
                # The complete raw CSV and component ledger remain reviewable.
                pending['review/'+entry['id']+'-components.json.gzip']=gzip.compress(compact([[json_number(v) if isinstance(v,Decimal) else v for v in r] for r in components]),mtime=0)
            else:
                rows=simple_rows(pages,entry)
                audit=verify_positioned_simple(path,rows,entry)
            audit['pdfPages']=len(document)
        else:
            rows,aggregates=read_victoria_csv(raw)
            rows=[row[:5] for row in rows]
            audit={'validationBasis':'Official CSV schema, named-row count, monetary validity and all retained source bytes. Original PDF reconciliation is not completed for this early release.',
                   'excludedAggregateRows':len(aggregates),'originalPdfReconciliation':'not-completed'}
            pending['raw/'+entry['localFile']+'.gzip']=gzip.compress(raw,mtime=0)
        if entry['city']=='victoria':
            csv_source=entry.get('companionCsv',entry)
            item_id=re.search(r'/items/([^/]+)/data',csv_source['url'])[1]
            item=catalog[item_id]
            if item['owner']!='CityOfVictoriaBC' or entry['year'] not in item['title'] or 'employee' not in item['title'].lower():raise ValueError('Victoria official catalog does not establish year and scope')
            audit['catalogEvidence']={'itemId':item_id,'owner':item['owner'],'title':item['title'],'catalogSha256':digest(catalog_raw)}
        if len(rows)!=entry['rowCount']:raise ValueError(f'Count mismatch {entry["id"]}: {len(rows)}')
        totals=[sum_values(rows,i) for i in (2,3)]
        if totals!=[Decimal(str(v)) for v in entry['totals']]:raise ValueError(f'Total mismatch {entry["id"]}: {totals}')
        for row in rows:
            if not row[0] or row[2] is None or row[2]<=0:raise ValueError('Invalid named monetary row')
            for value in row[2:4]:
                if value is not None and value!=value.quantize(Decimal('.01')):raise ValueError('Unreviewed sub-cent amount')
        normalized=[[entry['employerSlug']]+[json_number(v) if isinstance(v,Decimal) else v for v in row] for row in rows]
        payload=compact(normalized);compressed=gzip.compress(payload,mtime=0);filename=entry['id']+'.json.gzip'
        pending[filename]=compressed
        audit.update({'rowsByPhysicalPage':dict(sorted(Counter(row[4] for row in rows if row[4]).items())),
                      'missingExpenses':sum(row[3] is None for row in rows),'negativeExpenses':sum(row[3] is not None and row[3]<0 for row in rows),
                      'sourceFingerprintVerified':True,'printedNamedSubtotals':entry.get('printedTotals'),
                      'namedSubtotalResiduals':[json_number(a-Decimal(str(b))) for a,b in zip(totals,entry.get('printedTotals',entry['totals']))]})
        notes=list(entry.get('notes',[]))
        source={'id':entry['id'],'employerSlug':entry['employerSlug'],'employerName':entry['employerName'],'sector':'Municipalities',
                'year':entry['year'],'slug':entry['year'],'periodType':'calendar','periodStart':entry['year']+'-01-01','periodEnd':entry['year']+'-12-31',
                'title':entry['employerName']+' '+entry['year']+' '+('employee remuneration' if entry['category']=='employee-remuneration' else 'council remuneration'),
                'sourceUrl':entry['url'],'sourceIndexUrl':entry['indexUrl'],'sha256':digest(raw),'file':filename,'dataSha256':digest(compressed),'normalizedSha256':digest(payload),
                'category':entry['category'],'scope':'named-employees-over-threshold' if entry['category']=='employee-remuneration' else 'elected-officials',
                'currency':'CAD','amountUnit':'dollars','amountPrecision':entry.get('amountPrecision','cents'),'threshold':75000 if entry['category']=='employee-remuneration' else None,
                'thresholdRule':entry.get('thresholdRule','over') if entry['category']=='employee-remuneration' else None,'nameDisclosure':entry.get('nameDisclosure','published-full-name'),
                'positionDisclosure':entry.get('positionDisclosure','published'),'rowCount':len(rows),'totalRemuneration':json_number(totals[0]),'totalExpenses':json_number(totals[1]),
                'pages':entry.get('pages',[]),'status':'accepted','verifiedOn':'2026-10-31','notes':notes,'validation':audit}
        sources.append(source);audits.append({'id':entry['id'],'rows':len(rows),'totals':source['totalRemuneration'],'validation':audit})
        print(entry['id'],len(rows),[json_number(v) for v in totals])
    for relative,data in pending.items():
        target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    manifest={'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources,
              'catalogEvidence':config['catalog'],'unparsedSources':config.get('held',[]),'coverageNotes':['Calendar-year disclosures; employee and elected-official cohorts remain distinct. No unverified compiled partitions are removed by this collection.']}
    (OUT/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (OUT/'validation.json').write_text(json.dumps({'reviewedOn':'2026-10-31','sourceCount':len(sources),'rows':sum(s['rowCount'] for s in sources),'sources':audits},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-dir',type=Path,required=True);parser.add_argument('--fetch',action='store_true');run(parser.parse_args())
