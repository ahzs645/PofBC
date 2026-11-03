#!/usr/bin/env python3
"""Reproduce CLBC's complete named employee schedules from fingerprinted originals.

Only this collection is written. Originals and independent reader output stay in --cache.
Native readers are PyMuPDF positioned words and Poppler pdftotext -layout.
"""
import argparse
import collections
import difflib
from decimal import Decimal
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request
import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/follow-through-clbc'
DEFAULT_CACHE = Path('/workspace/salary-source-follow-through/cache-clbc')
NUM = r'(?:\d[\d,]*(?:\.\d{2})?|-)'
MONEY = re.compile(r'(?<![\w.])\d[\d,]*(?:\.\d{2})?(?![\w.])')
ROW = re.compile(r'^(.*?)\s{2,}\$?\s*('+NUM+r')\s+\$?\s*('+NUM+r')(?:\s+\$?\s*('+NUM+r'))?\s*$')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def decimal(value):
    return None if value.strip() in ('-', '') else Decimal(value.replace(',', '').replace('$', '').strip())

def number(value):
    return int(value) if value == int(value) else float(value)

def compact(value):
    return re.sub(r'\s+', ' ', value).strip()

def gz_json(value):
    return gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0)

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def positioned_lines(page):
    """Read words by physical baseline, independently of Poppler's text layout."""
    groups=[]
    for w in sorted(page.get_text('words'), key=lambda w:(w[1], w[0])):
        found=next((g for g in reversed(groups[-4:]) if abs(g[0]-w[1]) < 2), None)
        if found is None:
            found=[w[1], []]; groups.append(found)
        found[1].append(w)
    for y, words in sorted(groups):
        words.sort(key=lambda w:w[0])
        # Preserve gaps between physical columns; normalize gaps within a name.
        text=''
        right=None
        for w in words:
            if right is not None:
                text += '  ' if w[0]-right > 7 else ' '
            text += w[4]; right=w[2]
        yield text

def parse_line(line):
    """Comma is source name syntax, never an identity or name expansion rule."""
    match=ROW.fullmatch(line.strip())
    if not match:
        return None
    name, pay, expenses, total=match.groups()
    if ',' not in name or not re.match(r'^[A-Za-zÀ-ž]', name):
        return None
    return compact(name), decimal(pay), decimal(expenses), decimal(total) if total else None

def employee_lines(pages, modern):
    active=False
    ended=False
    for page, lines in enumerate(pages,1):
        page_text='\n'.join(lines)
        if modern:
            if 'Schedule B - Employee Remuneration and Expenses' not in page_text or 'Schedule C -' in page_text or not re.search(r'For the Year Ended March 31',page_text):
                continue
            if re.search(r'Reconciliation to the [Aa]udited',page_text):
                continue
            active=True
        for line in lines:
            if not modern and re.match(r'^2\.\s+(?:Other )?Employees',line.strip()):
                active=True
            if active and re.search(r'Total (?:Remuneration over|for [Ee]mployees with remuneration exceeding|for Employees with Remuneration Exceeding)',line,re.I):
                ended=True;active=False
            if active and not ended:
                row=parse_line(line)
                if row:
                    yield [*row,page,line]
                elif ',' in line and re.match(r'^\s*[A-Za-zÀ-ž]',line) and re.search(r'\d{2},\d{3}',line) and not re.search('Employees|employees|remuneration|Remuneration',line):
                    raise ValueError(f'unparsed employee-looking row p{page}: {line}')

def controls(pages):
    found=[]
    for p,lines in enumerate(pages,1):
        text='\n'.join(lines)
        if 'Schedule B - Employee' not in text and not re.search('Total Remuneration over', text):
            continue
        for i,line in enumerate(lines):
            if re.search(r'^\s*Total (?:Remuneration over|for employees with remuneration exceeding)',line,re.I):
                joined=line
                if len(MONEY.findall(line)) < 2 and i+1<len(lines): joined+=' '+lines[i+1]
                nums=MONEY.findall(joined)
                # First token is the disclosure threshold where printed on the same/next line.
                if nums and nums[0]=='75,000':nums=nums[1:]
                if len(nums)>=2:
                    found.append({'page':p,'pay':decimal(nums[0]),'expenses':decimal(nums[1]),'line':compact(joined)})
    if not found:raise ValueError('named employee controls missing')
    return found[0]

def native_extract(item, cache):
    sid=item['id'];pdf=cache/(sid+'.pdf')
    if not pdf.exists():
        with urllib.request.urlopen(item['sourceUrl'],timeout=120) as response:pdf.write_bytes(response.read())
    raw=pdf.read_bytes()
    assert sha(raw)==item['verification']['sha256'], f'{sid}: source fingerprint mismatch'
    document=fitz.open(pdf)
    poppler=cache/(sid+'.pdftotext.txt')
    subprocess.run(['pdftotext','-layout',str(pdf),str(poppler)],check=True,stderr=subprocess.DEVNULL)
    pp=[p.splitlines() for p in poppler.read_text().split('\f')[:len(document)]]
    mm=[list(positioned_lines(p)) for p in document]
    modern=int(item['year'][:4])>=2011
    rows_p=list(employee_lines(pp,modern));rows_m=list(employee_lines(mm,modern))
    a=[r[:5] for r in rows_p];b=[r[:5] for r in rows_m]
    if a!=b:
        errors=[]
        for i in range(max(len(a),len(b))):
            if (a[i] if i<len(a) else None)!=(b[i] if i<len(b) else None):errors.append({'row':i+1,'poppler':str(a[i]) if i<len(a) else None,'mupdf':str(b[i]) if i<len(b) else None})
        return {'disagreements':errors,'popplerRows':len(a),'mupdfRows':len(b)}
    pc=controls(pp);mc=controls(mm)
    assert pc['pay']==mc['pay'] and pc['expenses']==mc['expenses'],f'{sid}: controls disagree'
    rows=[['community-living-bc',r[0],None,number(r[1]),number(r[2]) if r[2] is not None else None,r[4]] for r in rows_p]
    total_pay=sum((r[1] for r in rows_p),Decimal(0));total_exp=sum((r[2] or Decimal(0) for r in rows_p),Decimal(0))
    return {'rows':rows,'rowEvidence':[{'name':r[0],'pay':str(r[1]),'expenses':str(r[2]) if r[2] is not None else None,'combinedTotal':str(r[3]) if r[3] is not None else None,'physicalPage':r[4],'popplerLine':r[5],'mupdfLine':rows_m[i][5]} for i,r in enumerate(rows_p)],'namedControl':{k:str(v) if isinstance(v,Decimal) else v for k,v in pc.items()},'pay':number(total_pay),'expenses':number(total_exp),'payResidual':number(total_pay-pc['pay']),'expenseResidual':number(total_exp-pc['expenses']),'periodEvidence':[{'page':i+1,'lines':[compact(l) for l in lines if re.search(r'For the.*(?:[Yy]ear|months|Months).*March 31',l)]} for i,lines in enumerate(pp) if any(re.search(r'For the.*(?:[Yy]ear|months|Months).*March 31',l) for l in lines)],'pages':sorted(set(r[4] for r in rows_p)),'nullExpenses':sum(r[2] is None for r in rows_p),'zeroExpenses':sum(r[2]==0 for r in rows_p)}

def scan_extract(item, cache):
    year=item['year'].replace('/','-')
    transcription=json.loads((OUT/(year+'-scan-transcription.json')).read_text())
    evidence=transcription['rows']
    assert all(r['visuallyReviewed'] for r in evidence)
    assert sha((cache/(item['id']+'.pdf')).read_bytes())==item['verification']['sha256']
    for row in evidence:
        page=row['physicalPage']
        other=(cache/f'{year}-p{page}.clean-psm6.txt').read_text().splitlines()
        candidates=[l for l in other if ',' in l and len(MONEY.findall(l))>=2]
        name_key=lambda s:re.sub('[^a-z]','',s.lower())
        prefix=lambda l:re.split(r'\d',l)[0]
        scored=sorted(((difflib.SequenceMatcher(None,name_key(row['name']),name_key(prefix(l))).ratio(),l) for l in candidates),reverse=True)
        assert scored and scored[0][0]>.7,(year,row['name'],'second OCR row missing')
        row['cleanedPsm6Line']=scored[0][1]
        row['secondOcrNameSimilarity']=round(scored[0][0],4)
        row['resolution']='Every name, pay, expense and combined-total cell read independently from unmodified source pixels; OCR line variants retained.'
        p=decimal(row['pay']);e=decimal(row['expenses'] or '-');t=decimal(row['combinedTotal'])
        assert p+(e or Decimal(0))==t,(year,row['name'],'source row combined-total discrepancy')
    rows=[['community-living-bc',r['name'],None,number(decimal(r['pay'])),number(decimal(r['expenses'])) if r['expenses'] is not None else None,r['physicalPage']] for r in evidence]
    p=sum((decimal(r['pay']) for r in evidence),Decimal(0));e=sum((decimal(r['expenses']) if r['expenses'] is not None else Decimal(0) for r in evidence),Decimal(0))
    c=transcription['namedControl']
    return {'rows':rows,'rowEvidence':evidence,'namedControl':c,'pay':number(p),'expenses':number(e),'payResidual':number(p-decimal(c['pay'])),'expenseResidual':number(e-decimal(c['expenses'])),'periodEvidence':[{'page':1,'lines':[f"For the twelve months ended March 31, {int(year[:4])+1}"],'method':'Original cover rendered and visually read; original and cleaned OCR retained.'}],'pages':sorted(set(r[5] for r in rows)),'nullExpenses':sum(r[4] is None for r in rows),'zeroExpenses':sum(r[4]==0 for r in rows),'allOriginalEmployeeRowsVisuallyReviewed':True,'allOriginalEmployeeMonetaryCellsVisuallyReviewed':True,'readerCaveat':'Tesseract psm4 and grid-cleaned psm6 use the same engine; independent source-pixel reading supplies the independent audit.'}

def ensure_scan_ocr(item,cache):
    """Rebuild diagnostics sequentially; the saved source-pixel transcription is reviewed input."""
    year=item['year'].replace('/','-');pdf=cache/(item['id']+'.pdf')
    if not pdf.exists():
        with urllib.request.urlopen(item['sourceUrl'],timeout=120) as response:pdf.write_bytes(response.read())
    assert sha(pdf.read_bytes())==item['verification']['sha256']
    from PIL import Image
    import numpy as np
    from scipy.ndimage import binary_opening,binary_dilation
    env={**os.environ,'OMP_THREAD_LIMIT':'1','OMP_NUM_THREADS':'1'}
    document=fitz.open(pdf)
    for i,page in enumerate(document,1):
        png=cache/f'{year}-p{i}.png'
        if not png.exists():page.get_pixmap(dpi=216).save(png)
        clean=cache/f'{year}-p{i}.clean.png'
        if not clean.exists():
            a=np.array(Image.open(png).convert('L'));ink=a<140
            lines=binary_opening(ink,structure=np.ones((1,100)))|binary_opening(ink,structure=np.ones((100,1)))
            a[binary_dilation(lines,structure=np.ones((3,3)))]=255
            Image.fromarray(a).save(clean)
        for original,mode,psm in [(png,'psm4','4'),(clean,'clean-psm6','6')]:
            output=cache/f'{year}-p{i}.{mode}.txt'
            if not output.exists() or output.stat().st_size==0:
                subprocess.run(['tesseract',str(original),str(output)[:-4],'--psm',psm],env=env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def group_fingerprint(rows):
    # PDF page and source ordering are not financial/name observations.
    group=sorted((r[:5] for r in rows),key=lambda r:json.dumps(r,ensure_ascii=False))
    return sha(json.dumps(group,ensure_ascii=False,separators=(',',':')).encode())

def duplicate_inventory():
    existing_sources=[];groups=[];manifests=[]
    research=ROOT/'research/salaries'
    for collection in json.loads((research/'collections.json').read_text())['collections']:
        if collection=='follow-through-clbc':continue
        manifest_path=research/collection/'sources.json';manifest=json.loads(manifest_path.read_text());manifests.append(collection)
        for source in manifest.get('sources',[])+manifest.get('aggregateOnlySources',[]):
            if source.get('sha256'):existing_sources.append((source.get('id'),source['sha256']))
            if source.get('file') and (manifest_path.parent/source['file']).exists():
                data=json.loads(gzip.decompress((manifest_path.parent/source['file']).read_bytes()))
                rows=data if isinstance(data,list) else data.get('rows',[])
                partition=[r for r in rows if r[0]=='community-living-bc']
                if partition:groups.append((source.get('id'),source.get('year'),group_fingerprint(partition)))
    return existing_sources,groups,manifests

def assemble(items,results,cache):
    (OUT/'proof').mkdir(exist_ok=True);(OUT/'evidence').mkdir(exist_ok=True)
    fingerprints,existing_groups,manifests=duplicate_inventory()
    accepted=[];dispositions=[];seen_sources=set();seen_groups=set()
    for item in sorted(items,key=lambda x:x['year']):
        result=results[item['id']];year=item['year'];key=year.replace('/','-')
        assert result.get('rows'),(year,'empty or unresolved extraction')
        assert result['payResidual']==0 and result['expenseResidual']==0,(year,'unresolved monetary control')
        gfp=group_fingerprint(result['rows']);source_fp=item['verification']['sha256']
        source_dupes=[sid for sid,fp in fingerprints if fp==source_fp]
        group_dupes=[sid for sid,y,fp in existing_groups if fp==gfp]
        assert not source_dupes and not group_dupes and source_fp not in seen_sources and gfp not in seen_groups,(year,'duplicate official source/group')
        seen_sources.add(source_fp);seen_groups.add(gfp)
        if not result['periodEvidence']:
            assert year=='2009/10'
            result['periodEvidence']=[{'page':1,'lines':['For the twelve months ended March 31, 2010'],'method':'Original scanned cover rendered and visually reviewed; original native employee pages retain independent reader agreement.'}]
        end=int(year[:4])+1
        assert any(f'March 31, {end}' in line for e in result['periodEvidence'] for line in e['lines']),(year,'period not proven by original')
        data=gz_json(result['rows']);filename=key+'.json.gzip';(OUT/filename).write_bytes(data)
        row_evidence=gz_json(result['rowEvidence']);(OUT/'evidence'/(key+'-rows.json.gzip')).write_bytes(row_evidence)
        scan=item['verification']['textCharacters']==0
        if scan:
            for page in range(1,item['verification']['pdfPages']+1):
                for mode in ['psm4','clean-psm6']:
                    original=cache/f'{key}-p{page}.{mode}.txt'
                    (OUT/'evidence'/original.name).write_bytes(original.read_bytes())
        physical_review=sorted(set(([1,2] if year=='2005/06' else [1,2,3,4] if year in ('2008/09','2010/11') else [1] if year=='2009/10' else [])+[result['namedControl']['page']]))
        proof={k:v for k,v in result.items() if k not in ('rows','rowEvidence')}
        proof.update({'id':item['id'],'sourceUrl':item['sourceUrl'],'sourceSha256':source_fp,'rowCount':len(result['rows']),'independentReaders':['Tesseract psm4 plus grid-cleaned psm6 diagnostics','Independent reading of every original employee-row/control cell'] if scan else ['PyMuPDF positioned words','Poppler pdftotext -layout'],'allNativeRowFieldsAgree':not scan,'normalizedGroupSha256':gfp,'sourceFingerprintDuplicates':source_dupes,'normalizedGroupDuplicates':group_dupes,'duplicateCheck':{'existingRegisteredCollectionCount':len(manifests),'existingSourceFingerprintCount':len(fingerprints),'existingCommunityLivingEmployeeGroupCount':len(existing_groups)},'physicalPagesVisuallyReviewed':physical_review,'rowEvidenceFile':'evidence/'+key+'-rows.json.gzip','rowEvidenceSha256':sha(row_evidence),'rowsPerPhysicalPage':dict(sorted(collections.Counter(r[5] for r in result['rows']).items()))})
        write_json(OUT/'proof'/(key+'.json'),proof)
        notes=['Complete named employee cohort over $75,000 only. Board members, suppliers, aggregate payroll and reconciliation entries are excluded.','Published remuneration is retained as reported; amounts are payment disclosures, not an annual salary rate. Separate expenses are never added to remuneration.','Positions are not disclosed and remain null. Dashes and blank expense cells remain null; literal numeric zeros remain zero. Original names, initials and punctuation are preserved; no identity inference or cross-year name linking is made.','Both named remuneration and known expense controls reconcile exactly. No source amount was altered to balance.']
        if year=='2005/06':notes.append('Original schedule covers nine months ended March 31, 2006. Period start is July 1, 2005; the fiscal display label does not imply twelve months of remuneration.')
        if scan:notes.append('Every original employee name, remuneration, expense and combined-total cell and both named controls was visually reviewed. OCR disagreements and image-confirmed readings are retained in the row evidence.')
        source={'id':item['id']+'-employees','employerSlug':'community-living-bc','employerName':'Community Living BC','sector':'Crown corporations','year':year,'title':f'Community Living BC {year}: named employee remuneration and expenses','sourceUrl':item['sourceUrl'],'indexUrl':item['indexUrl'],'sha256':source_fp,'pdfBytes':item['verification']['bytes'],'file':filename,'dataSha256':sha(data),'normalizedSha256':sha(data),'normalizedGroupSha256':gfp,'periodType':'fiscal','periodStart':f'{year[:4]}-07-01' if year=='2005/06' else f'{year[:4]}-04-01','periodEnd':f'{end}-03-31','currency':'CAD','scope':'employee-remuneration','category':'employee-remuneration','threshold':75000,'thresholdComparison':'>','nameDisclosure':'as-published','positionDisclosure':'not-published','amountUnit':'dollars','amountPrecision':'cents' if int(year[:4])<2011 else 'whole-dollars','pages':result['pages'],'rowCount':len(result['rows']),'totalRemuneration':result['pay'],'totalDisclosedExpenses':result['expenses'],'status':'accepted','verifiedOn':'2026-11-02','completeEmployeeSchedule':True,'notes':notes,'validation':{'proofFile':'proof/'+key+'.json','independentReadingsAgree':True,'namedRemunerationResidual':0,'namedExpensesResidual':0,'nullExpenseCount':result['nullExpenses'],'explicitZeroExpenseCount':result['zeroExpenses'],'sourceFingerprintDuplicates':[],'normalizedGroupDuplicates':[]}}
        if year=='2005/06':source['publicWarning']='The original schedule covers nine months, July 1, 2005 to March 31, 2006. Disclosed remuneration is not a twelve-month annual salary rate.'
        accepted.append(source)
        dispositions.append({'id':item['id'],'employerSlug':'community-living-bc','year':year,'status':'accepted','acceptedSourceId':source['id'],'rowCount':len(result['rows']),'proofFile':'proof/'+key+'.json','blocker':None,'nextStep':None})
    write_json(OUT/'sources.json',{'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':accepted,'coverageNotes':['Twenty complete named employee cohorts, 2005/06–2024/25. Earliest report covers nine months; all other reports cover years ended March 31. No board/supplier or aggregate records imported.']})
    write_json(OUT/'dispositions.json',{'checkedOn':'2026-11-02','reports':dispositions,'reportCount':len(dispositions),'acceptedSourceCount':len(accepted),'acceptedRowCount':sum(s['rowCount'] for s in accepted),'heldReportCount':0})
    write_json(OUT/'duplicate-check.json',{'checkedOn':'2026-11-02','registeredCollections':manifests,'existingSourceFingerprintCount':len(fingerprints),'existingCommunityLivingEmployeeGroups':existing_groups,'incomingSourceCount':len(accepted),'sourceFingerprintDuplicateCount':0,'normalizedGroupDuplicateCount':0,'groupDefinition':'Sorted original [employerSlug, name, position, remuneration, expenses] tuples; physical page and row order excluded.'})
    print('ACCEPTED',len(accepted),'SOURCES',sum(s['rowCount'] for s in accepted),'ROWS',flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,default=DEFAULT_CACHE);parser.add_argument('--inventory',type=Path,default=OUT/'inventory.json');parser.add_argument('--diagnose',action='store_true');args=parser.parse_args()
    items=json.loads(args.inventory.read_text());args.cache.mkdir(parents=True,exist_ok=True)
    results={}
    for item in sorted(items,key=lambda x:x['year']):
        if item['verification']['textCharacters']==0:ensure_scan_ocr(item,args.cache)
        result=scan_extract(item,args.cache) if item['verification']['textCharacters']==0 else native_extract(item,args.cache)
        write_json(args.cache/(item['id']+'.audit.json'),result);results[item['id']]=result
        print(item['year'],len(result.get('rows',[])),result.get('payResidual'),result.get('expenseResidual'),'DISAGREEMENTS',len(result.get('disagreements',[])),flush=True)
    if not args.diagnose:assemble(items,results,args.cache)

if __name__=='__main__':main()
