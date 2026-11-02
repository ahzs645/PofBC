#!/usr/bin/env python3
"""Independent Poppler bbox-layout horizontal-line reader for new native originals."""
from __future__ import annotations
import gzip,hashlib,json,pathlib,re,subprocess,xml.etree.ElementTree as E
from finish_salary_acquisition_native import SPECS,ROOT,AREA

def digest(raw):return hashlib.sha256(raw).hexdigest()
def tidy(s):return re.sub(r'\s*,\s*',',',' '.join(s.split()))
def literal_amount(s):
 token=''.join(s.split())
 if token in {'-','‐','–','—','--'}:return None
 sign=-1 if token.startswith('(') and token.endswith(')') else 1
 token=token.strip('()').replace('−','-')
 if not re.fullmatch(r'-?[0-9]+(?:,[0-9]{3})*',token):raise ValueError(('Not a source money token',s))
 return sign*int(token.replace(',',''))
def pdf_words(pdf):
 raw=subprocess.check_output(['pdftotext','-bbox-layout',pdf,'-']);tree=E.fromstring(raw);pages=[]
 for page in tree.iter('{http://www.w3.org/1999/xhtml}page'):
  words=[]
  for w in page.iter('{http://www.w3.org/1999/xhtml}word'):
   if w.text:words.append({'x0':float(w.attrib['xMin']),'x1':float(w.attrib['xMax']),'top':float(w.attrib['yMin']),'bottom':float(w.attrib['yMax']),'text':w.text})
  pages.append(words)
 return pages,digest(raw)
def horizontal_rows(words):
 groups=[]
 for w in sorted(words,key=lambda w:(w['top'],w['x0'])):
  if not groups or abs(groups[-1][0]['top']-w['top'])>1.1:groups.append([w])
  else:groups[-1].append(w)
 return [sorted(g,key=lambda w:w['x0']) for g in groups]
def read(pages,spec,scope):
 records=[];prefix='employee' if scope=='employees' else 'board';wanted=spec['employeePages'] if scope=='employees' else [spec['boardPage']]
 for pn in wanted:
  for line in horizontal_rows(pages[pn-1]):
   y=line[0]['top'];low,high=spec[prefix+'Body']
   if not low-3<y<high+2:continue
   cell=lambda bounds:[w for w in line if bounds[0]<=w['x0'] and w['x1']<=bounds[1]]
   left=[w for w in line if w['x0']<spec[prefix+'NameEnd']];text=tidy(' '.join(w['text'] for w in left))
   if not text or text.upper().startswith(('TOTAL','SUBTOTAL')):continue
   paycell=cell(spec[prefix+'PayRange'])
   if not paycell:continue
   paytext=tidy(' '.join(w['text'] for w in paycell))
   try:pay=literal_amount(paytext)
   except ValueError:continue
   if spec['firstNameStart'] is not None and scope=='employees':
    last=tidy(' '.join(w['text'] for w in left if w['x0']<spec['firstNameStart']));first=tidy(' '.join(w['text'] for w in left if w['x0']>=spec['firstNameStart']));name=last+(','+first if first else '')
   else:
    if ',' not in text:continue
    name=text
   expense=cell(spec[prefix+'ExpenseRange']);exptext=tidy(' '.join(w['text'] for w in expense))
   if not exptext:
    if not (spec['id']=='vch-2020-21' and scope=='board'):raise ValueError(('No printed expense token',pn,name))
    exp=None
   else:exp=literal_amount(exptext)
   records.append({'row':[spec['employerSlug'],name,None,pay,exp,pn],'rawRemuneration':paytext,'rawExpenses':exptext,'rawLineWords':line})
 return records
def freeze(path,raw):
 if path.exists():assert path.read_bytes()==raw,('Frozen reader evidence differs',path)
 else:path.write_bytes(raw)

def build():
 summaries=[]
 for spec in SPECS:
  assert digest(pathlib.Path(spec['pdf']).read_bytes())==spec['sha256'];pages,rawsha=pdf_words(spec['pdf']);emp=read(pages,spec,'employees');board=read(pages,spec,'board');a={'spec':spec,'reader':'Poppler bbox-layout words; independently grouped horizontal word lines and columns. No MuPDF/PDFMiner extracted rows used.','rawBboxXmlSha256':rawsha,'employeeRecords':emp,'boardRecordsAllLiteral':board};p=AREA/(spec['id']+'-poppler-raw.json.gzip');freeze(p,gzip.compress(json.dumps(a,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));summaries.append({'id':spec['id'],'employees':len(emp),'boardAll':len(board),'employeeRemuneration':sum(r['row'][3] for r in emp),'employeeExpenses':sum(r['row'][4] or 0 for r in emp),'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())})
 print(json.dumps(summaries,indent=2))
if __name__=='__main__':build()
