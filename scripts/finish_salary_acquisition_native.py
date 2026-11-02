#!/usr/bin/env python3
"""Read newly recovered complete native salary scopes with MuPDF words."""
from __future__ import annotations
import collections,gzip,hashlib,json,pathlib,re
import fitz
ROOT=pathlib.Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/acquisition'
SPECS=[{'id':'providence-2023-24','employerSlug':'providence-health-care','employerName':'Providence Health Care Society','year':'2023/24','pdf':'/tmp/salary-queue-acquisition/cdc461cbb98dda93ede3.body','sha256':'521472f784463bf42626b9c74aeb72252167346b65b8a123031ca59e46ecb5f3','employeePages':list(range(58,223)),'boardPage':56,'employeePayRange':[330,435],'employeeExpenseRange':[470,550],'employeeNameEnd':330,'firstNameStart':220,'employeeBody':[211,735],'boardPayRange':[330,435],'boardExpenseRange':[470,550],'boardNameEnd':330,'boardBody':[172,590],'controls':[380612829,3560383]},
 {'id':'vch-2020-21','employerSlug':'vancouver-coastal-health','employerName':'Vancouver Coastal Health','year':'2020/21','pdf':'/tmp/salary-queue-acquisition/d188294cfedc3ff87cbb.body','sha256':'8d2d85205f0c4de6557e39cd8ee21ac2a38c90aa70611f1ca5bfb7c9f030d7ad','employeePages':list(range(4,156)),'boardPage':3,'employeePayRange':[330,405],'employeeExpenseRange':[480,560],'employeeNameEnd':330,'firstNameStart':None,'employeeBody':[70,740],'boardPayRange':[240,310],'boardExpenseRange':[320,400],'boardNameEnd':240,'boardBody':[115,435],'controls':[771927987,3773890]}]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def clean(text):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',text).strip())
def money(text):
 t=re.sub(r'\s+','',text)
 if t in ['-','‐','–','—','--']:return {'raw':text,'kind':'explicit-double-hyphen-marker' if t=='--' else 'explicit-dash','value':None}
 if re.fullmatch(r'[−-]?(?:\d{1,3}(?:,\d{3})+|\d+)',t):return {'raw':text,'kind':'number','value':int(t.replace(',','').replace('−','-'))}
 if re.fullmatch(r'\((?:\d{1,3}(?:,\d{3})+|\d+)\)',t):return {'raw':text,'kind':'number','value':-int(t[1:-1].replace(',',''))}
 raise ValueError('Nonliteral monetary cell: '+repr(text))
def in_col(w,bounds):return bounds[0]<=w[0] and w[2]<=bounds[1]
def near(words,y):return sorted([w for w in words if abs(w[1]-y)<.8],key=lambda w:w[0])
def join(words):return clean(' '.join(w[4] for w in words))
def read_scope(doc,spec,scope):
 pages=spec['employeePages'] if scope=='employees' else [spec['boardPage']];prefix='employee' if scope=='employees' else 'board';records=[];controls=[]
 for pn in pages:
  words=[list(w[:5]) for w in doc[pn-1].get_text('words')];body=spec[prefix+'Body'];payrange=spec[prefix+'PayRange'];exprange=spec[prefix+'ExpenseRange'];nameend=spec[prefix+'NameEnd']
  anchors=[]
  for w in words:
   if not (body[0]<w[1]<body[1] and in_col(w,payrange)):continue
   try:money(w[4])
   except ValueError:continue
   anchors.append(w)
  for anchor in anchors:
   line=near(words,anchor[1]);left=[w for w in line if w[0]<nameend];n=join(left)
   if not n:
    if spec['id']=='vch-2020-21' and scope=='board':
     controls.append({'physicalPage':pn,'label':None,'pay':anchor[4],'expenseWords':join([w for w in line if in_col(w,exprange)]),'basis':'Unlabelled printed board total row; not a named observation'});continue
    raise ValueError(('Unnamed pay row',spec['id'],pn,anchor))
   if n.upper().startswith(('TOTAL','SUBTOTAL')):
    controls.append({'physicalPage':pn,'label':n,'pay':anchor[4],'expenseWords':join([w for w in line if in_col(w,exprange)])});continue
   if scope=='employees' and spec['firstNameStart'] is not None:
    last=join([w for w in left if w[0]<spec['firstNameStart']]);first=join([w for w in left if w[0]>=spec['firstNameStart']]);n=last+(','+first if first else '')
   elif ',' not in n:raise ValueError(('Pay row without visible source name',spec['id'],pn,n))
   exps=[w for w in line if in_col(w,exprange)];rawexp=join(exps)
   if not rawexp:
    if spec['id']=='vch-2020-21' and scope=='board':exp={'raw':'','kind':'blank-source-cell','value':None}
    else:raise ValueError(('Missing expense source token',spec['id'],pn,n))
   else:exp=money(rawexp)
   pay=money(anchor[4]);row=[spec['employerSlug'],n,None,pay['value'],exp['value'],pn]
   records.append({'row':row,'scope':scope,'sourceRowOnPage':sum(r['row'][5]==pn for r in records)+1,'y':anchor[1],'rawNameColumns':[join(left)] if spec['firstNameStart'] is None or scope!='employees' else [last,first],'remunerationCell':pay,'expenseCell':exp,'sourceWords':line})
 return records,controls
def traces(doc,pages):
 out=[]
 for pn in pages:
  bad=[];count=0
  for t in doc[pn-1].get_texttrace():
   text=''.join(chr(c[0]) for c in t['chars']);count+=len(text)
   if text.strip() and (t['type']==3 or t['opacity']<.99 or all(c>.95 for c in t['color'])):bad.append({'type':t['type'],'opacity':t['opacity'],'color':t['color'],'text':text,'bbox':t['bbox']})
  if bad:raise ValueError(('Unpainted/white source text requires explicit review',pn,bad))
  out.append({'physicalPage':pn,'tracedChars':count,'unpaintedWhiteOrTransparentTextSpans':0})
 return out
def freeze(path,raw):
 if path.exists():assert path.read_bytes()==raw,('Frozen reader evidence differs',path)
 else:path.write_bytes(raw)

def build():
 result=[]
 for spec in SPECS:
  raw=pathlib.Path(spec['pdf']).read_bytes();assert sha(raw)==spec['sha256'];doc=fitz.open(spec['pdf']);assert not doc.is_repaired and raw.rstrip().endswith(b'%%EOF')
  emp,ctrl=read_scope(doc,spec,'employees');board,bctrl=read_scope(doc,spec,'board');numeric=[r for r in board if r['row'][3] is not None];held=[r for r in board if r['row'][3] is None]
  if spec['id']=='providence-2023-24':assert [sum(r['row'][3] for r in emp),sum(r['row'][4] or 0 for r in emp)]==spec['controls']
  pages=traces(doc,[spec['boardPage']]+spec['employeePages'])
  entry={'spec':spec,'reader':'MuPDF word rectangles and pay-cell anchors; no Poppler/PDFMiner rows used','employeeRecords':emp,'boardRecordsAllLiteral':board,'boardNumericPayRecords':numeric,'boardNonNumericPayRecords':held,'nativeControls':ctrl+bctrl,'pageTextPaintingGuards':pages,'pdfPages':len(doc),'sourceBytes':len(raw)};p=AREA/(spec['id']+'-mupdf-raw.json.gzip');freeze(p,gzip.compress(json.dumps(entry,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));result.append({'id':spec['id'],'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'employees':len(emp),'boardAll':len(board),'boardNumericPay':len(numeric),'boardNonNumericPay':len(held),'employeeRemuneration':sum(r['row'][3] for r in emp),'employeeExpenses':sum(r['row'][4] or 0 for r in emp),'expenseNulls':sum(r['row'][4] is None for r in emp),'expenseZeros':sum(r['row'][4]==0 for r in emp),'negativeExpenseRows':sum((r['row'][4] or 0)<0 for r in emp),'nativeControls':ctrl+bctrl})
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
