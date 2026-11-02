#!/usr/bin/env python3
"""Rebuild CNC reviewed employee cohorts from original PDF reader/OCR evidence.

Scans use two separately segmented Tesseract readings. Corrections must be in the
reviewed corrections file, tied to a page and original candidate, never a subtotal.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,pathlib,re,subprocess,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/follow-through-cnc'
CACHE=pathlib.Path('/workspace/salary-source-follow-through/cache-cnc')
MONEY=re.compile(r'^-?(?:\d+|\d{1,3}(?:,\d{3})+)$')
SLUG='college-of-new-caledonia'
YEARS=['2018-19','2019-20','2020-21','2021-22','2022-23','2023-24','2024-25']
def amount(value):
    value=value.replace('$','').strip()
    if value in ('','-','—','–'): return None
    if not MONEY.fullmatch(value): raise ValueError(f'Invalid money cell: {value!r}')
    return int(value.replace(',',''))
def tsv_lines(path):
    opener=gzip.open if str(path).endswith('.gzip') else open
    with opener(path,'rt') as handle:
        words=[r for r in csv.DictReader(handle,delimiter='\t') if r['text'].strip()]
    lines=collections.defaultdict(list)
    for r in words:
        if r['level']=='5': lines[tuple(r[k] for k in ('block_num','par_num','line_num'))].append(r)
    return list(lines.values())
def ocr_rows(year,mode=6):
    rows=[]; controls=[]; details=[]; active=False;done=False
    for page in range(1,10):
        path=CACHE/f'{year}-p{page:02}-300-psm{mode}.tsv'
        if not path.exists(): path=path.with_name(path.name+'.gzip')
        if not path.exists(): continue
        lines=tsv_lines(path)
        header=[]
        for line in lines:
            if ' '.join(r['text'] for r in line).startswith('Last Name First Name'):
                header=line
        if not header: continue
        first=next(int(r['left']) for r in header if r['text']=='First')
        last=next(int(r['left']) for r in header if r['text']=='Last')
        payx=next((int(r['left']) for r in header if r['text']=='Remuneration'),1450)
        expx=next((int(r['left']) for r in header if r['text']=='Expenses'),1900)
        # The table's column origins establish cells, while segmentation can vary.
        # Pay/expense amounts are right aligned; header starts are left of all numbers.
        for line in lines:
            text=' '.join(r['text'] for r in line)
            if text.startswith('Other Employees'):
                active=True; continue
            if text.startswith('Total, other employees') or text.startswith('Total other employees'):
                if active: controls.append({'page':page,'text':text})
                done=True;active=False
            if done or not active: continue
            cols=[[],[],[],[]]
            namewords=[r for r in line if re.search('[A-Za-z]',r['text']) and int(r['left'])<payx-100]
            if not namewords: continue
            first_boundary=first-last+min(int(r['left']) for r in namewords)-25
            for r in line:
                x=int(r['left']); col=0 if x<first_boundary else 1 if x<payx-50 else 2 if x<expx-45 else 3
                cols[col].append(r['text'])
            cells=[' '.join(c).replace('$','').strip() for c in cols]
            if not cells[0] or cells[0] in ('Last Name','Total','Other Employees') or cells[0].startswith(('COLLEGE','Total','Last')): continue
            try: pay=amount(cells[2]); expense=amount(cells[3])
            except ValueError: continue
            if pay is None or not cells[1]: continue
            row=[SLUG,cells[0]+', '+cells[1],None,pay,expense,page]
            rows.append(row);details.append({'page':page,'row':row,'cells':cells,'line':text,'top':min(int(r['top']) for r in line)})
    return rows,controls,details

def native_rows(year='2020-21',reader='fitz'):
    import fitz,xml.etree.ElementTree as ET
    pdf=CACHE/f'{year}.pdf'; pages={}
    if reader=='fitz':
        d=fitz.open(pdf)
        for i,p in enumerate(d): pages[i+1]=[(*w[:4],w[4]) for w in p.get_text('words')]
    elif reader=='poppler':
        xml=CACHE/f'{year}-bbox.html'
        subprocess.run(['pdftotext','-bbox',str(pdf),str(xml)],check=True)
        doc=ET.parse(xml); ns={'h':'http://www.w3.org/1999/xhtml'}
        for i,p in enumerate(doc.findall('.//h:page',ns)):
            pages[i+1]=[(float(w.attrib['xMin']),float(w.attrib['yMin']),float(w.attrib['xMax']),float(w.attrib['yMax']),w.text or '') for w in p.findall('h:word',ns)]
    rows=[];active=False;done=False
    for page,words in pages.items():
        lines=collections.defaultdict(list)
        for w in sorted(words,key=lambda w:(w[1],w[0])):
            key=next((k for k in lines if abs(k-w[1])<2),w[1])
            lines[key].append(w)
        for y,line in sorted(lines.items()):
            line.sort();text=' '.join(w[4] for w in line)
            if text=='Other Employees': active=True;continue
            if text.startswith('Total, other employees'): done=True;active=False
            if done or not active: continue
            cols=[[],[],[],[]]
            for w in line:
                x=w[0];col=0 if x<157 else 1 if x<380 else 2 if x<480 else 3
                cols[col].append(w[4])
            cells=[' '.join(c).replace('$','').strip() for c in cols]
            if not cells[0] or cells[0].startswith(('Last','COLLEGE','Total')):continue
            try:pay=amount(cells[2]); expense=amount(cells[3])
            except ValueError:continue
            if pay is None or not cells[1]:continue
            rows.append([SLUG,cells[0]+', '+cells[1],None,pay,expense,page])
    return rows

def sha(b):return hashlib.sha256(b).hexdigest()
def write_json(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def candidates():
    OUT.mkdir(parents=True,exist_ok=True)
    for year in YEARS:
        for mode in [4,6]:
            r,c,d=ocr_rows(year,mode)
            write_json(CACHE/f'{year}-candidate-psm{mode}.json',{'rows':r,'controls':c,'details':d})
            print(year,mode,len(r),sum(x[3] for x in r),sum(x[4] or 0 for x in r),sum(x[4] is None for x in r),dict(collections.Counter(x[5] for x in r)))
    a=native_rows();b=native_rows(reader='poppler');write_json(CACHE/'2020-21-native.json',a);print('native',len(a),sum(x[3] for x in a),sum(x[4] or 0 for x in a),'poppler',len(b),a==b)

BLANK_EXPENSE_NAMES_2021={
 'Bennett, Bruce','Bergen, Kylie','Berlin, Howard','Carter, Chris',
 'Catherall, Jennifer','Dyck, Candice','Frizzell, Garth','Goudreau, Christien',
 'Howard, Gwendolynne','Johnson, Clarie','Jones, Yvonne','Little, Jennifer',
 'MacDonald, Cheryl','Taylor, Andrew'}

def canonical_bytes(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()

def apply_review(rows,review):
    """Apply only exact reviewed candidate replacements, preserving occurrence order."""
    result=[r.copy() for r in rows]
    for patch in review['corrections']:
        matches=[i for i,r in enumerate(result) if r==patch['before']]
        if len(matches)!=1: raise ValueError(f'Correction has {len(matches)} exact witnesses: {patch["before"]}')
        result[matches[0]]=patch['after'].copy()
    for addition in review['additions']:
        matches=[i for i,r in enumerate(result) if r[1]==addition['insertBefore'] and r[5]==addition['row'][5]]
        if len(matches)!=1: raise ValueError(f'Insertion has {len(matches)} anchors: {addition}')
        result.insert(matches[0],addition['row'].copy())
    return result

def compare_secondary(raw,accepted,review):
    """Reconcile alternate segmentation with visible-cell corrections; expose omissions."""
    lookup={r[1]:r for r in accepted}
    assert len(lookup)==len(accepted),'Duplicate names require occurrence-aware review'
    aliases={p['before'][1].lstrip('|; '):p for p in review['corrections']}
    found=[];disagreements=[]
    for original in raw:
        row=original.copy();row[1]=row[1].lstrip('|; ')
        patch=aliases.get(row[1])
        if patch:
            for i in range(6):
                old,new=patch['before'][i],patch['after'][i]
                if old!=new:
                    if row[i] not in (old,new) and not (i==1 and row[i]==str(old).lstrip('|; ')):
                        disagreements.append({'readerRow':original,'reviewedRow':patch['after'],'field':i})
                    row[i]=new
        expected=lookup.get(row[1])
        if expected!=row:disagreements.append({'readerRow':original,'afterReviewedCorrections':row,'reviewedRow':expected})
        else:found.append(row[1])
    missing=[r for r in accepted if r[1] not in found]
    return {'rawRowCount':len(raw),'rowsAgreeingAfterVisibleCellCorrections':len(found),
            'missingRowsRequiringVisualCompletion':missing,'unresolvedDisagreements':disagreements}

def validate_rows(rows,spec):
    expected=collections.Counter(dict(zip(spec['physicalPdfPages'],spec['sourceRowsPerPhysicalPage'])))
    actual=collections.Counter(r[5] for r in rows)
    if actual!=expected:raise ValueError(f'Physical-page completeness differs: {actual} != {expected}')
    for row in rows:
        if len(row)!=6 or row[0]!=SLUG or not isinstance(row[1],str) or not row[1].strip() or row[2] is not None:
            raise ValueError(f'Invalid employee row: {row}')
        if type(row[3]) is not int or row[3]<0 or (row[4] is not None and type(row[4]) is not int):
            raise ValueError(f'Invalid monetary fields: {row}')
    return True

def build_artifacts():
    global CACHE
    previous_cache=CACHE;CACHE=OUT/'evidence/ocr'
    reviews=json.loads((OUT/'reviewed-corrections.json').read_text())
    controls=json.loads((OUT/'reviewed-controls.json').read_text())
    discoveries=json.loads((OUT/'source-discovery.json').read_text())
    artifacts={};sources=[];dispositions=[];evidence=[]
    for year,discovery in zip(YEARS,discoveries):
        assert discovery['year'].replace('/','-')==year
        review=reviews['years'][year];spec=controls['years'][year]
        raw6,_,details=ocr_rows(year,6);raw4,_,_=ocr_rows(year,4)
        if year=='2020-21':
            rows=json.loads(gzip.decompress((OUT/'evidence/2020-21-fitz.json.gzip').read_bytes()))
            second=json.loads(gzip.decompress((OUT/'evidence/2020-21-poppler.json.gzip').read_bytes()))
            hidden=[]
            assert len(rows)==len(second)
            for visible,encoded in zip(rows,second):
                assert visible[:1]+visible[2:]==encoded[:1]+encoded[2:]
                if visible[1]!=encoded[1]:hidden.append({'visibleName':visible[1],'encodedName':encoded[1],'physicalPdfPage':visible[5]})
            assert len(hidden)==3
            secondary={'nativeReaders':'PyMuPDF word rectangles versus Poppler bbox words','comparedRows':len(rows),'allMonetaryCellsAndSourceOrderAgree':True,'visiblyClippedNames':hidden,
                       'ocrRemunerationAndExpenseCellsAgree':[[r[3],r[4],r[5]] for r in rows]==[[r[3],r[4],r[5]] for r in raw6]}
        else:
            rows=apply_review(raw6,review);secondary=compare_secondary(raw4,rows,review)
            if secondary['unresolvedDisagreements']:raise ValueError((year,secondary['unresolvedDisagreements']))
        validate_rows(rows,spec)
        pay=sum(r[3] for r in rows);expense=sum(r[4] or 0 for r in rows)
        nulls=sum(r[4] is None for r in rows);blanks=14 if year=='2021-22' else 0
        residual=[pay-spec['namedEmployeeSubtotal'][0],expense-spec['namedEmployeeSubtotal'][1]]
        payload=canonical_bytes(rows);compressed=gzip.compress(payload,mtime=0)
        file=year+'.json.gzip';artifacts[file]=compressed
        cell_evidence=[]
        for ordinal,row in enumerate(rows,1):
            expense_state='blank' if year=='2021-22' and row[1] in BLANK_EXPENSE_NAMES_2021 else 'dash' if row[4] is None else 'explicit-zero' if row[4]==0 else 'numeric'
            cell_evidence.append({'sourceRowOrdinal':ordinal,'row':row,'expenseCellState':expense_state,'positionCellState':'not-published','firstNameCellState':'blank' if row[1]=='Ramandeep' else 'published'})
        evfile=f'evidence/{year}-reviewed-cells.json.gzip';artifacts[evfile]=gzip.compress(canonical_bytes(cell_evidence),mtime=0)
        sources.append({'id':f'cnc-sofi-{year}-employees','employerSlug':SLUG,'employerName':'College of New Caledonia','sector':'Colleges','year':year.replace('-','/'),
          'slug':year,'file':file,'title':discovery['title']+' — complete named employee schedule',
          'sourceUrl':discovery['sourceUrl'],'indexUrl':discovery['indexUrl'],'sha256':discovery['verification']['sha256'],'pdfBytes':discovery['verification']['bytes'],
          'dataSha256':sha(compressed),'normalizedSha256':sha(payload),'periodType':'fiscal','periodStart':year[:4]+'-04-01','periodEnd':str(int(year[:4])+1)+'-03-31',
          'periodEvidence':'Employee schedule header explicitly reads APRIL 1, '+year[:4]+' TO MARCH 31, '+str(int(year[:4])+1)+'; all accepted physical pages visually reviewed.',
          'category':'employee-remuneration','scope':'named-employees-source-threshold-schedule','threshold':75000,'thresholdRule':'source-labelled-over','thresholdComparison':None,
          'currency':'CAD','amountUnit':'dollars','nameDisclosure':'published-visible-name','positionDisclosure':'not-published',
          'rowCount':len(rows),'totalRemuneration':pay,'totalExpenses':expense,'pages':spec['physicalPdfPages'],'status':'verified','sourceKind':'official','verifiedOn':'2026-11-02',
          'completeEmployeeSchedule':True,'retainCompiledPartition':True,
          'publicWarning':'Source remuneration can include taxable benefits and other payments; expenses remain separate. The source-labelled named schedule includes some remuneration below $75,000. Displayed cells and documented subtotal differences are preserved. Existing compiled observations remain available.',
          'notes':['Other Employees schedule only. Board, supplier, below-threshold aggregates and reconciliation lines are excluded. Positions are not published for this cohort.',
            'Source defines remuneration as any form of salary, wages, bonuses, gratuities, taxable benefits, payments into trust or income deferral paid to/on behalf of the employee during the fiscal year; severance-agreement amounts are excluded.',
            'Source expenses include amounts paid on College purchasing cards on behalf of employees. Dashes and blanks remain null, distinct from explicit numeric zero.',
            f'Displayed employee rows minus printed named subtotal: remuneration {residual[0]:+d} CAD; known expenses {residual[1]:+d} CAD. No cells were altered to balance controls.',
            '2020/21 visible clipped surnames are preserved; longer hidden Poppler strings are extraction evidence only.' if year=='2020-21' else 'Two separately segmented Tesseract readings were compared; every row was checked against original rendered pixels. Both OCR passes use the same engine.',
            'The current official index no longer links 2018/19; the supplied official PDF URL remains available and matches the discovery fingerprint.' if year=='2018-19' else 'Current official index contains the source PDF link.'],
          'validation':{'completeEmployeeSchedule':True,'physicalPdfPages':spec['physicalPdfPages'],'sourceRowsPerPhysicalPage':spec['sourceRowsPerPhysicalPage'],
            'independentReaders':['PyMuPDF words','Poppler bbox words','Tesseract PSM 4 and 6','Original rendered page visual reading'] if year=='2020-21' else ['Tesseract 5.5.0 PSM 4','Tesseract 5.5.0 PSM 6','Original rendered page visual reading'],
            'ocrEngineIndependence':False,'independentlyComparedRows':len(rows),'allEmployeeRowsVisuallyReviewed':True,
            'computedRemuneration':pay,'computedKnownExpenses':expense,'nullExpenseRows':nulls,'dashExpenseRows':nulls-blanks,'blankExpenseRows':blanks,'explicitZeroExpenseRows':sum(r[4]==0 for r in rows),
            'printedRemunerationSubtotal':spec['namedEmployeeSubtotal'][0],'printedExpensesSubtotal':spec['namedEmployeeSubtotal'][1],'remunerationSubtotalResidual':residual[0],'expensesSubtotalResidual':residual[1],
            'reviewedCellsFile':evfile,'reviewedCellsSha256':sha(artifacts[evfile]),'renderedSourceFidelityReceipt':'research/salaries/follow-through-cnc/visual-review.json',
            'sourceControlReceipt':'research/salaries/follow-through-cnc/reviewed-controls.json','reviewedCorrectionsSha256':sha((OUT/'reviewed-corrections.json').read_bytes())}})
        evidence.append({'year':year.replace('-','/'),'rowCount':len(rows),'readerComparison':secondary,
          'namedSubtotal':spec['namedEmployeeSubtotal'],'displayedRowSums':[pay,expense],'displayedMinusNamedSubtotal':residual,
          'printedAllEmployeesMinusNamedAndBelowThreshold':[spec['allEmployeesTotal'][i]-spec['namedEmployeeSubtotal'][i]-spec['belowThresholdEmployeeAggregate'][i] for i in range(2)],
          'printedReconciliationMinusEmployeesAndBoard':[spec['reconciliationTotal'][i]-spec['allEmployeesTotal'][i]-spec['boardTotal'][i] for i in range(2)],
          'boardCohort':'Not imported; separate board review required.','reviewedCellEvidence':evfile})
        dispositions.append({'id':discovery['id'],'year':year.replace('-','/'),'status':'imported','scope':'employee-remuneration','acceptedSourceId':sources[-1]['id'],
          'acceptedManifest':'research/salaries/follow-through-cnc/sources.json','employeeRows':len(rows),'salaryRowsReconciled':True,'sourcePixelsReviewed':True,
          'reviewedPhysicalPages':spec['physicalPdfPages'],'documentPeriodChecked':True,'originalSha256':discovery['verification']['sha256'],
          'heldScopes':[{'scope':'board-remuneration','status':'not-imported','reason':'Separate Board of Governors cohort is outside this complete employee import.'}],
          'unresolvedEmployeeFields':[],'nextAction':'Accepted complete employee schedule. Retain displayed source residuals; separately review the Board of Governors schedule if that cohort is needed.'})
    artifacts['sources.json']=(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources},ensure_ascii=False,indent=2)+'\n').encode()
    artifacts['dispositions.json']=(json.dumps({'version':1,'sources':dispositions},ensure_ascii=False,indent=2)+'\n').encode()
    artifacts['extraction-evidence.json']=(json.dumps({'version':1,'reviewedOn':'2026-11-02','totalAcceptedEmployeeRows':sum(s['rowCount'] for s in sources),'reports':evidence},ensure_ascii=False,indent=2)+'\n').encode()
    CACHE=previous_cache
    return artifacts

def extract_originals():
    """Download fingerprinted originals and run sequential OCR; no write to public services."""
    import fitz,os
    CACHE.mkdir(parents=True,exist_ok=True)
    discoveries=json.loads((OUT/'source-discovery.json').read_text());specs=json.loads((OUT/'reviewed-controls.json').read_text())['years']
    for discovery in discoveries:
        year=discovery['year'].replace('/','-');pdf=CACHE/(year+'.pdf')
        if not pdf.exists():subprocess.run(['curl','--fail','--location','--silent','--show-error',discovery['sourceUrl'],'-o',str(pdf)],check=True)
        if sha(pdf.read_bytes())!=discovery['verification']['sha256']:raise ValueError(f'Original PDF fingerprint changed: {year}')
        document=fitz.open(pdf)
        for page in specs[year]['physicalPdfPages']:
            png=CACHE/f'{year}-p{page:02}-300.png'
            if not png.exists():document[page-1].get_pixmap(dpi=300).save(png)
            for mode in [4,6]:
                base=png.with_name(png.stem+f'-psm{mode}')
                if not base.with_suffix('.tsv').exists():
                    env=os.environ.copy();env['OMP_THREAD_LIMIT']='1';env['OMP_NUM_THREADS']='1'
                    subprocess.run(['tesseract',str(png),str(base),'--psm',str(mode),'txt','tsv'],check=True,env=env)
        print(f'{year}: original fingerprint verified; OCR pages '+','.join(map(str,specs[year]['physicalPdfPages'])),flush=True)


def verify_original_extraction():
    """Require original fingerprints and all cached reader rows to reproduce fixtures."""
    global CACHE
    source_cache=CACHE
    discoveries=json.loads((OUT/'source-discovery.json').read_text())
    for discovery in discoveries:
        year=discovery['year'].replace('/','-');pdf=source_cache/(year+'.pdf')
        if sha(pdf.read_bytes())!=discovery['verification']['sha256']:
            raise ValueError(f'Original PDF fingerprint changed: {year}')
        for mode in [4,6]:
            CACHE=source_cache;actual=ocr_rows(year,mode)[0]
            CACHE=OUT/'evidence/ocr';expected=ocr_rows(year,mode)[0]
            if actual!=expected:raise ValueError(f'Original OCR rows differ from reviewed inputs: {year} PSM {mode}')
    CACHE=source_cache
    for reader in ['fitz','poppler']:
        actual=native_rows(reader=reader)
        expected=json.loads(gzip.decompress((OUT/'evidence'/f'2020-21-{reader}.json.gzip').read_bytes()))
        if actual!=expected:raise ValueError(f'Original native rows differ: {reader}')
    print('Original PDF fingerprints and both OCR/native reader rows reproduce reviewed inputs.')

def main():
    global CACHE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=pathlib.Path);parser.add_argument('--extract',action='store_true');parser.add_argument('--candidates',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--build',action='store_true')
    args=parser.parse_args()
    if args.cache:CACHE=args.cache
    if args.extract:
        extract_originals()
        verify_original_extraction()
    if args.candidates:candidates()
    if args.build or args.check:
        artifacts=build_artifacts()
        for file,data in artifacts.items():
            path=OUT/file
            if args.check:
                if not path.exists() or path.read_bytes()!=data:raise ValueError(f'Artifact differs from reviewed inputs: {path}')
            else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        for receipt in ['reviewed-corrections.json','reviewed-controls.json']:
            document=json.loads((OUT/receipt).read_text())
            for year,entry in document['years'].items():
                items=entry.get('corrections',[])+entry.get('additions',[])+([entry] if 'visualEvidence' in entry else [])
                for item in items:
                    visual=item['visualEvidence'];file=OUT/visual['file']
                    if sha(file.read_bytes())!=visual['sha256']:raise ValueError(f'Visual crop fingerprint mismatch: {file}')
        manifest=json.loads(artifacts['sources.json'])
        print(('Verified' if args.check else 'Built')+f' {len(manifest["sources"])} CNC employee schedules / {sum(s["rowCount"] for s in manifest["sources"]):,} rows.')
if __name__=='__main__':main()
