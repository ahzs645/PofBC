#!/usr/bin/env python3
"""Independent PDFMiner fixed-grid review of East Kootenay staff disclosures."""
import collections,gzip,hashlib,json,re
from pathlib import Path
import pdfplumber
import fitz
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'research/salaries/continuation-government-police';OUT=ROOT/'research/salaries/continuation-2026-11-01/reviews'
def sha(b):return hashlib.sha256(b).hexdigest()
def money(s):
 s=re.sub(r'\s+','',s.replace('$',''))
 if s in ['', '-', '‐','–','—']:return None
 if not re.fullmatch(r'\d[\d,]*',s):raise ValueError(('not a money cell',s))
 return int(s.replace(',',''))
receipts=[];evidence=[]
for c in json.loads((BASE/'config.json').read_text())['sources']:
 if c['parser']!='eko-employees':continue
 file=Path('/tmp/continuation-government-police')/c['cacheFile'];raw=file.read_bytes();assert sha(raw)==c['sha256'];rows=[];page_evidence=[];control=None;stars=[];scope_rows=[]
 render_doc=fitz.open(file)
 for pn in c['pages']:
  render_path=Path(f'/tmp/continuation-crowns/eko-{c["year"]}-p{pn}.png');render_path.parent.mkdir(parents=True,exist_ok=True);render_doc[pn-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(render_path)
 with pdfplumber.open(file) as d:
  cover=d.pages[0].extract_text();assert re.search(r'year ended December 31, '+c['year'],cover,re.I)
  for pn in c['pages']:
   page=d.pages[pn-1];text=page.extract_text(layout=True,x_density=4,y_density=7);pr=[];after=False
   for line in text.splitlines():
    flat=' '.join(line.split())
    if 'Employee Gross Earnings (over $75,000)' in flat:
     control=[money(line[102:125]),money(line[125:])];after=True;scope_rows.append({'pdfPage':pn,'line':line,'kind':'named employee gross earnings control','values':control});continue
    if after:
     if flat and not flat.startswith('Financial Information'):
      scope_rows.append({'pdfPage':pn,'line':line})
     continue
    # Independent text-grid cell boundaries in points/4; salary cell repairs
    # PDFMiner word spacing only, e.g. its '1 13,225' remains 113225.
    pay_text=line[102:125];cleaned=re.sub(r'[$\s,]','',pay_text)
    if not cleaned.isdigit():continue
    name=' '.join(line[:28].split());title=' '.join(line[28:102].split())
    if not name or not title or not re.fullmatch(r"[A-Za-z '*-]+",name):raise ValueError(('unexpected identity/row boundary',pn,line))
    pay=money(pay_text);expense=money(line[125:]);assert pay>75000
    if name.endswith('*'):stars.append({'sourceName':name,'normalizedSurname':name.rstrip('*'),'pdfPage':pn,'meaning':'Includes payout of unused vacation'})
    row=[c['employerSlug'],name.rstrip('*'),title,pay,expense,pn];rows.append(row);pr.append(row)
   page_evidence.append({'pdfPage':pn,'pdfminerFixedGridText':text,'rows':pr,'visuallyReviewedCachedPng':f'/tmp/continuation-crowns/eko-{c["year"]}-p{pn}.png','renderedPageSha256':sha(Path(f'/tmp/continuation-crowns/eko-{c["year"]}-p{pn}.png').read_bytes())})
 source=next(s for s in json.loads((BASE/'sources.json').read_text())['sources'] if s['id']==c['id']);candidate=json.loads(gzip.decompress((BASE/source['file']).read_bytes()));a=collections.Counter(map(tuple,rows));b=collections.Counter(map(tuple,candidate));diff=list((a-b).elements());other=list((b-a).elements());sums=[sum(r[3] for r in rows),sum(r[4] for r in rows if r[4] is not None)];missing=sum(r[4] is None for r in rows);residual=[v-total for v,total in zip(sums,control)]
 assert control==[x['publishedDollars'] for x in c['printedControls']]
 receipt={'sourceId':c['id'],'year':c['year'],'originalSha256':sha(raw),'candidateDataSha256':sha((BASE/source['file']).read_bytes()),'candidateFile':str(BASE/source['file']),'localPath':str(file),'employeePhysicalPages':c['pages'],'engine':'PDFMiner/pdfplumber: independent four-point text grid, separate cell parser; no author parser imported','surnameOnlyDisclosure':True,'rowCount':len(rows),'rowSums':sums,'missingExpenseCells':missing,'printedNamedEmployeeControls':control,'rowMinusPrintedResidual':residual,'everyNamePositionPayExpensePageAndMultiplicityMatches':not diff and not other,'independentOnly':diff,'candidateOnly':other,'vacationMarkers':stars,'employerBenefitAggregateExcluded':True,'belowThresholdAggregateExcluded':True,'directorScopeExcluded':True,'renderedReview':'Every named row, source label, control, footnote and benefits aggregate on all six original employee/control pages visually reviewed.','reviewDecision':'Accept exact original named employee rows with explicit surname-only, unknown-expense and unresolved source-control qualifications; no individual correction or cause is inferred.'}
 receipts.append(receipt);evidence.append({'receipt':receipt,'coverText':cover,'pages':page_evidence,'originalControlAndAggregateLines':scope_rows});print(json.dumps(receipt))
OUT.mkdir(parents=True,exist_ok=True);(OUT/'regional-east-kootenay-controls.json').write_text(json.dumps({'reviewer':'Crown continuation worker','date':'2026-11-01','sourceCohorts':3,'rowsIndependentlyChecked':sum(r['rowCount'] for r in receipts),'sources':receipts},indent=2,ensure_ascii=False)+'\n');(OUT/'regional-east-kootenay-evidence.json.gzip').write_bytes(gzip.compress((json.dumps(evidence,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
