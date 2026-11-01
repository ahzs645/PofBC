#!/usr/bin/env python3
"""Recover NIC FY2019/20's complete employee schedule from a truncated archive.

MuPDF reads/repairs the archived raw bytes. Separately, Ghostscript recovers the
five table pages, then Poppler parses their physical layout. White source text
(job titles) is excluded from exported records. The whole board package is NOT
claimed recovered. Offline evidence can be replayed without original PDF files.
"""
import argparse,collections,gzip,hashlib,json,re,subprocess
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/held-resolution-education';AUDIT=ROOT/'research/salaries/held-resolution-2026-11-01/education';CACHE=Path('/tmp/nic-held-resolution')
PDF=CACHE/'96885489bda14c25.body';SIGNED=CACHE/'50bb24515f0ff2a3.body';RECOVERED=CACHE/'board-salary-pages-gs.pdf'
SHA='d96d0241e6d16b7383161079dfb90e44f29db6c4a72d3a35ccd50646da00eef0';SIGNEDSHA='43fd43a1d642fd6ad49efa92b8428d8663a4a410eec74d2d615b30fecb7e661d'
ORIGINALURL='https://www.nic.bc.ca/pdf/bog/agenda/2020-2021/20201022_BOG_agenda.pdf';ARCHIVEURL='https://web.archive.org/web/20211205173843id_/https://www.nic.bc.ca/pdf/bog/agenda/2020-2021/20201022_BOG_agenda.pdf'
NUM=r'(?:-?\d+(?:,\d{3})*|\(\d+(?:,\d{3})*\))';SID='held-resolution-nic-sofi-2019-20-employees'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def enc(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
def money(x):
 if x in ['', '-', '–']:return None
 assert re.fullmatch(NUM,x),x
 return int(x.replace(',','').replace('(','-').replace(')',''))
def primary(words,page,board=False):
 # The hidden white title column starts at213.8pt; visible names end to its left.
 hy=min(w[1] for w in words if w[4]=='Name') if board else max(w[1] for w in words if w[4]=='Name')
 anchors=sorted([w for w in words if 395<w[0]<470 and hy+5<w[1]<735 and (not board or w[1]<450) and re.fullmatch(NUM,w[4])],key=lambda w:w[1]);rows=[];proof=[];controls=[]
 for a in anchors:
  nw=sorted([w for w in words if w[0]<210 and abs(w[1]-a[1])<1.5],key=lambda w:w[0]);name=' '.join(w[4] for w in nw)
  exp=[w for w in words if 470<w[0]<580 and abs(w[1]-a[1])<1.5 and (re.fullmatch(NUM,w[4]) or w[4]=='-')];assert len(exp)==1,(page,name,a,exp)
  vals=[money(a[4]),money(exp[0][4])]
  if ',' not in name or name.startswith(('Consolidated','TOTAL')):
   label='below-threshold' if name.startswith('Consolidated') else 'overall' if name=='TOTAL' else 'board-subtotal' if board else 'named-subtotal'
   controls.append(dict(physicalPage=page,label=label,values=vals,baseline=round(a[1],4)));continue
  assert board or vals[0]>75000,(page,name,vals)
  rows.append(['north-island-college',name,None,*vals,page]);proof.append(dict(physicalPage=page,name=name,remunerationToken=a[4],expenseToken=exp[0][4],baseline=round(a[1],4)))
 return rows,proof,controls

def secondary(text,page,board=False):
 rows=[];proof=[];controls=[];lines=text.splitlines();heads=[i for i,l in enumerate(lines) if re.search(r'\bName\s+.*Remuneration\s+Expenses',l)];assert heads,(page,lines[:10]);start=heads[0] if board else heads[-1]
 for line in lines[start+1:]:
  if board and re.match(r'B\.\s+Other Employees',line):break
  # Pay/expense terminal cells, independent of either native coordinate reader.
  m=re.fullmatch(r'(.*?)\s{2,}('+NUM+r')\s+('+NUM+r'|-)\s*',line)
  if not m:continue
  name=re.split(r'\s{2,}',m[1].strip())[0];vals=[money(m[2]),money(m[3])]
  if ',' not in name or name.startswith(('Consolidated','TOTAL')):
   label='below-threshold' if name.startswith('Consolidated') else 'overall' if name=='TOTAL' else 'board-subtotal' if board else 'named-subtotal'
   controls.append(dict(physicalPage=page,label=label,values=vals));continue
  rows.append(['north-island-college',name,None,*vals,page]);proof.append(line)
 return rows,proof,controls

def recover():
 assert sha(PDF.read_bytes())==SHA and sha(SIGNED.read_bytes())==SIGNEDSHA
 r=subprocess.run(['gs','-q','-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dFirstPage=26','-dLastPage=30','-sOutputFile='+str(RECOVERED),str(PDF)],capture_output=True,text=True,check=True)
 return r.stderr+r.stdout

def extract():
 log=recover();doc=fitz.open(PDF);gd=fitz.open(RECOVERED);assert len(gd)==5
 pop=subprocess.run(['pdftotext','-layout',str(RECOVERED),'-'],capture_output=True,text=True,check=True).stdout.split('\f');rows=[];ev=[]
 for i,p in enumerate(range(26,31)):
  page=doc[p-1];assert 'FOR THE YEAR ENDED MARCH 31, 2020' in ' '.join(page.get_text().split());words=[list(w[:5]) for w in page.get_text('words')];a,proof,ca=primary(words,p);b,raw,cb=secondary(pop[i],p)
  assert a==b,(p,'native reader disagreement',a,b)
  assert [dict(physicalPage=x['physicalPage'],label=x['label'],values=x['values']) for x in ca]==cb,(p,ca,cb)
  whites=[dict(text=''.join(chr(c[0]) for c in t['chars']),bbox=list(t['bbox']),color=list(t['color']),type=t['type']) for t in page.get_texttrace() if tuple(t['color'])==(1.0,1.0,1.0)]
  # Check actual render success from each independent repair; images remain /tmp.
  for engine,pg in [('mupdf',page),('ghostscript',gd[i])]:pg.get_pixmap(matrix=fitz.Matrix(2,2)).save(CACHE/'images'/f'nic-recovered-{engine}-p{p}.png')
  board=None
  if p==26:
   ba,bp,bc=primary(words,p,True);bb,br,bcc=secondary(pop[i],p,True);assert ba==bb and [x['values'] for x in bc]==[x['values'] for x in bcc];board=dict(rows=ba,rowEvidence=bp,controls=bc,popplerRows=br)
  rows+=a;ev.append(dict(physicalPage=p,printedSchedulePage=i+1,words=words,popplerGhostscriptLayout=pop[i],rowEvidence=proof,printedControls=ca,excludedWhiteTextSpans=whites,boardControlEvidence=board))
 return rows,dict(originalSha256=SHA,ghostscriptRepairLog=log,pages=ev,sourcePackageComplete=False,completeEmployeeSchedule=True,originalByteLength=1048576,originalReportedLength=3739511,archiveWarning='299 wayback content truncated by "length"')

def scan_rows(text,page):
 # Original signed scan OCR is supplementary corroboration; these are NOT imports.
 out=[]
 for line in text.splitlines():
  line=re.sub(r'\s+[tHi|\\\x27]+$','',line.strip())
  m=re.fullmatch(r'(.+?,\s*.+?)\s+('+NUM+r')\s+('+NUM+r'|-)\s*',line)
  if not m:continue
  name=m[1]
  if name=='Melgaard, Matthew ,':name='Melgaard, Matthew'
  if name=="O'Connell, Chery!":name="O'Connell, Cheryl"
  out.append(['north-island-college',name,None,money(m[2]),money(m[3]),page])
 return out

def build():
 rows,ev=extract();assert len(rows)>100
 board=ev['pages'][0]['boardControlEvidence'];bpay=sum(r[3] for r in board['rows']);bexp=sum(r[4] or 0 for r in board['rows']);assert [bpay,bexp]==board['controls'][0]['values']==[16375,12727]
 pay=sum(r[3] for r in rows);exp=sum(r[4] or 0 for r in rows);assert [pay,exp]==ev['pages'][-1]['printedControls'][0]['values']==[13045792,543386]
 assert [pay+bpay+15484088,exp+bexp+454520]==[28546255,1010633]
 scan=[]
 for sp,pp in [(5,27),(6,29)]:
  txt=(CACHE/f'nic-signed-p{sp}.txt').read_text();sr=scan_rows(txt,pp);target=[r for r in rows if r[5]==pp];assert sr==target,(sp,sr,target)
  scan.append(dict(signedScanPhysicalPage=sp,archivedPackagePhysicalPage=pp,rowCount=len(sr),rows=sr,rawTesseractText=txt,manualImageCorrections=([dict(raw='Melgaard, Matthew ,',visible='Melgaard, Matthew'),dict(raw="O'Connell, Chery!",visible="O'Connell, Cheryl")] if sp==6 else []),method='Tesseract PSM6 on3x signed source render, manually checked against source images; native archive rows from independent readers agree exactly. Stray margin-line OCR characters are discarded; no independent second OCR engine claimed.'))
 ev['signedScanCorroboration']=scan
 raw=enc(rows);gz=gzip.compress(raw,mtime=0);egz=gzip.compress(enc(ev),mtime=0);(OUT/(SID+'.json.gzip')).write_bytes(gz);(OUT/'evidence'/(SID+'.json.gzip')).write_bytes(egz)
 source=dict(id=SID,employerSlug='north-island-college',employerName='North Island College',sector='Universities and colleges',year='2019/20',slug='2019-20',periodType='fiscal',periodStart='2019-04-01',periodEnd='2020-03-31',category='employee-remuneration',scope='employee-remuneration',currency='CAD',sourceKind='official',status='verified',verifiedOn='2026-11-01',file=SID+'.json.gzip',title='North Island College FY2019/20 employee remuneration and expenses, recovered from archived October 22, 2020 Board agenda',sourceUrl=ARCHIVEURL,sourceIndexUrl='https://web.archive.org/web/20210123014602id_/https://www.nic.bc.ca/about-us/board-of-governors/meeting-schedule/',originalSourceUrl=ORIGINALURL,sha256=SHA,dataSha256=sha(gz),normalizedSha256=sha(raw),rowCount=len(rows),totalRemuneration=pay,totalExpenses=exp,pages=list(range(26,31)),completeEmployeeSchedule=True,sourcePackageComplete=False,positionDisclosure='not visibly published; white job-title text excluded',notes=['Complete five-page published named employee schedule above $75,000; separate Board amounts and below-threshold aggregates are excluded. Missing/dash expenses remain null, explicit zeros would remain zero; no negative amounts occur. Remuneration is the source amount, not base salary or an expense-inclusive total.','Job-title strings embedded as white text are invisible in the published pages and are not used; every exported position is null.','Raw archived bytes are incomplete; the complete employee schedule is recovered by independent MuPDF and Ghostscript PDF repair paths. Original package completeness is not claimed.','Two surviving employee pages and all overall totals agree with the separate signed official SOFI scan dated October 27, 2020. That scan itself omits employee pages 1, 3 and 5.'],publicWarning='The archived official Board package is truncated at1,048,576 bytes; its archival header reports an original length of3,739,511 bytes and Warning299: content truncated by "length". All five employee schedule pages were recovered and independently checked, but the complete Board package was not recovered. The agenda attachment approval pages are unsigned; two employee pages and overall totals agree with a separately signed official SOFI scan. Invisible white job-title text is excluded.',validation=dict(completeEmployeeSchedule=True,sourcePackageComplete=False,sourceFingerprintLocked=True,allNamesAndMonetaryCellsIndependentlyVerified=True,independentMethod='MuPDF repair/read of raw archived bytes versus independent Ghostscript repair of five source pages followed by Poppler physical-layout reader. Exact ordered visible name/pay/expense/page equality; hidden white titles excluded.',rowCountsByPdfPage=dict(collections.Counter(r[5] for r in rows)),printedNamedControl=[13045792,543386],namedControlResidualRowSumMinusPrinted=[0,0],printedBoardControl=[16375,12727],printedBelowThresholdControl=[15484088,454520],printedOverallControl=[28546255,1010633],expenseDashesOrBlankRetainedAsMissing=sum(r[4] is None for r in rows),explicitZeroExpenseRows=sum(r[4]==0 for r in rows),negativeExpenseRows=sum(r[4] is not None and r[4]<0 for r in rows),evidenceFile='evidence/'+SID+'.json.gzip',evidenceSha256=sha(egz),signedScanSha256=SIGNEDSHA,signedScanMatchingRowCount=sum(x['rowCount'] for x in scan)),cacheFile=str(PDF))
 source['notes'].append('Archived official minutes of October 22, 2020 record a carried motion approving the Financial Information Act information for the year ended March 31, 2020 (physical/printed page4, item4.2.1); the agenda attachment itself has unsigned approval lines.')
 source['validation']['approvalEvidence']=dict(sourceUrl='https://web.archive.org/web/20221001112128id_/https://www.nic.bc.ca/pdf/bog/minutes/20201022_BOG_regular_minutes.pdf',originalSourceUrl='https://www.nic.bc.ca/pdf/bog/minutes/20201022_BOG_regular_minutes.pdf',sha256='4f6655723d597ccd08e684e42feaa9be018b5511590c4b0c3bc3b378d1698196',physicalPage=4,item='4.2.1',cacheFile=str(CACHE/'efefa9daac3c0e3b.body'))
 source['publicWarning']='The archived official Board package is truncated at 1,048,576 bytes; its archival header reports an original length of 3,739,511 bytes and Warning 299: content truncated by "length". Its complete five-page employee salary schedule has been recovered and independently verified. The currently hosted nine-page SOFI omits salary pages 1, 3 and 5; its two surviving salary pages and overall totals match. Separate official minutes record Board approval on October 22, 2020. A request for a complete original source copy is prepared but unsent. Invisible job-title text is excluded.'
 bs=board_source(source,ev,board['rows']);dump(OUT/'sources.json',dict(version=1,rowSchema=['employerSlug','name','position','remuneration','expenses','pdfPage'],sources=[source,bs]));print('Built employee',len(rows),'rows',pay,exp,'and Board',len(board['rows']),'rows',bpay,bexp,'signedscanmatch',sum(x['rowCount'] for x in scan))

def board_source(employee,ev,rows):
 import copy
 s=copy.deepcopy(employee);sid='held-resolution-nic-sofi-2019-20-board';payload=enc(rows);data=gzip.compress(payload,mtime=0);(OUT/(sid+'.json.gzip')).write_bytes(data)
 s.update(id=sid,file=sid+'.json.gzip',title='North Island College FY2019/20 Board remuneration and expenses, recovered from archived October 22, 2020 Board agenda',category='board-remuneration',scope='board-remuneration',rowCount=15,totalRemuneration=16375,totalExpenses=12727,pages=[26],completeEmployeeSchedule=False,completeBoardSchedule=True,dataSha256=sha(data),normalizedSha256=sha(payload))
 s['notes']=['Complete 15-person Board of Governors table on printed salary schedule page1, recovered package physical26. Separate named employees and below-threshold employee aggregates are excluded. Remuneration and expenses are the source columns, without salary annualization or inferred components.','Job/role strings embedded as invisible white text are excluded; every position is null. Jain, Vikas expense dash remains null.','The overall archived official package is truncated; the complete Board table is recovered. Separate official minutes record approval of Financial Information Act information for year ended March 31, 2020. The current signed nine-page scan lacks the Board page, so its individual Board rows are not independently corroborated there.']
 s['publicWarning']=s['publicWarning'].replace('Its complete five-page employee salary schedule has been recovered and independently verified.','Its complete 15-person Board table has been recovered and independently verified. The Board table is absent from the separately signed nine-page scan.')
 s['validation']=dict(completeEmployeeSchedule=False,completeBoardSchedule=True,sourcePackageComplete=False,sourceFingerprintLocked=True,allNamesAndMonetaryCellsIndependentlyVerified=True,independentMethod=employee['validation']['independentMethod'],rowCountsByPdfPage={'26':15},printedBoardControl=[16375,12727],boardControlResidualRowSumMinusPrinted=[0,0],expenseDashesOrBlankRetainedAsMissing=sum(r[4] is None for r in rows),explicitZeroExpenseRows=sum(r[4]==0 for r in rows),negativeExpenseRows=0,evidenceFile=employee['validation']['evidenceFile'],evidenceSha256=employee['validation']['evidenceSha256'],evidenceRowPath='pages[0].boardControlEvidence.rows',approvalEvidence=employee['validation']['approvalEvidence'])
 return s

def verify(originals=False):
 s=json.loads((OUT/'sources.json').read_text())['sources'][0];data=(OUT/s['file']).read_bytes();assert sha(data)==s['dataSha256'];rows=json.loads(gzip.decompress(data));assert sha(gzip.decompress(data))==s['normalizedSha256'];b=(OUT/s['validation']['evidenceFile']).read_bytes();assert sha(b)==s['validation']['evidenceSha256'];ev=json.loads(gzip.decompress(b));actual=[]
 for e in ev['pages']:
  a,proof,controls=primary(e['words'],e['physicalPage']);b,_,cc=secondary(e['popplerGhostscriptLayout'],e['physicalPage']);assert a==b and proof==e['rowEvidence'] and controls==e['printedControls'];assert [dict(physicalPage=x['physicalPage'],label=x['label'],values=x['values']) for x in controls]==cc;actual+=a
  if e['boardControlEvidence']:
   ba,bp,bc=primary(e['words'],e['physicalPage'],True);bb,_,bcc=secondary(e['popplerGhostscriptLayout'],e['physicalPage'],True);assert ba==bb==e['boardControlEvidence']['rows'] and bp==e['boardControlEvidence']['rowEvidence'] and bc==e['boardControlEvidence']['controls'];assert [x['values'] for x in bc]==[x['values'] for x in bcc]
 assert actual==rows and all(r[2] is None for r in rows);assert len(rows)==s['rowCount'];assert [sum(r[3] for r in rows),sum(r[4] or 0 for r in rows)]==[s['totalRemuneration'],s['totalExpenses']]
 for c in ev['signedScanCorroboration']:assert scan_rows(c['rawTesseractText'],c['archivedPackagePhysicalPage'])==c['rows']==[r for r in rows if r[5]==c['archivedPackagePhysicalPage']]
 sources=json.loads((OUT/'sources.json').read_text())['sources']
 if len(sources)>1:
  bs=sources[1];bgz=(OUT/bs['file']).read_bytes();assert sha(bgz)==bs['dataSha256'] and sha(gzip.decompress(bgz))==bs['normalizedSha256'];br=json.loads(gzip.decompress(bgz));assert br==ev['pages'][0]['boardControlEvidence']['rows'] and len(br)==15;assert [sum(r[3] for r in br),sum(r[4] or 0 for r in br)]==[16375,12727];assert all(r[2] is None for r in br)
 if originals:
  a,_=extract();assert a==rows
 print('Verified NIC2019/20 employee',len(rows),'+ Board',sum(x['rowCount'] for x in sources if x['category']=='board-remuneration'),'rows','with original independent repairs' if originals else 'offline evidence replay')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='store_true');p.add_argument('--originals',action='store_true');a=p.parse_args();build() if a.build else verify(a.originals)
