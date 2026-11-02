#!/usr/bin/env python3
"""Independent Tesseract-word and Rapid-box row assembly for eight source layouts.

No detection is not a dash. Missing/unparseable monetary cells are explicit flags;
source-pixel and image amendments are a separate reviewed stage.
"""
import argparse,collections,csv,gzip,hashlib,io,json,re,statistics
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_north'
FIELD_NAMES=['name','position','remuneration','expenses','pdfPage','category']
DEFS={
 8:{'columns':[70,300,300,390,480],'positions':False,'precision':'whole-dollars','trusteePages':[51],'trusteeEnd':310},
 28:{'columns':[70,310,310,425,555],'positions':False,'precision':'cents','trusteePages':[49],'trusteeEnd':350},
 54:{'columns':[35,220,350,430,500],'positions':True,'precision':'cents','trusteePages':[48],'trusteeEnd':1000},
 58:{'columns':[4,175,330,415,510],'positions':True,'precision':'cents','trusteePages':[50],'trusteeEnd':185},
 59:{'columns':[40,240,410,500,565],'positions':True,'precision':'cents','trusteePages':[53],'trusteeEnd':1000,'excludePages':[52],'columnsByPage':{53:[40,230,345,440,525]}},
 60:{'columns':[55,230,370,455,545],'positions':True,'precision':'cents','trusteePages':[53],'trusteeEnd':250},
 81:{'columns':[50,220,340,450,535],'positions':True,'precision':'cents','trusteePages':[50],'trusteeEnd':280},
 82:{'columns':[10,230,385,495,608],'positions':True,'precision':'cents','trusteePages':[52],'trusteeEnd':270,'excludePages':[58]},
}
def clean(t):return re.sub(r'\s+',' ',t).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
def pack(v):return gzip.compress((json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
def money(text,precision):
 text=clean(text).replace('$','').strip();note=''
 m=re.search(r'\*+$',text)
 if m:note=m.group();text=text[:m.start()].strip()
 if text in ('-','–','—'):return None,note
 if not text:return 'UNRESOLVED:missing',note
 compact=re.sub(r'\s+','',text)
 pattern=r'-?(?:\d{1,3}(?:,\d{3})+|\d+)' + (r'\.\d{2}' if precision=='cents' else '')
 if not re.fullmatch(pattern,compact):return 'UNRESOLVED:'+text,note
 return str(Decimal(compact.replace(',',''))),note

def words(raw,engine):
 if engine=='tesseract':
  out=[]
  # Literal quote characters in OCR must never trigger CSV quoting.
  for w in csv.DictReader(io.StringIO(raw['tesseractRawTsv']),delimiter='\t',quoting=csv.QUOTE_NONE):
   if w['level']!='5' or not w['text'].strip():continue
   x,y,width,height=[float(w[k])*72/300 for k in ['left','top','width','height']]
   out.append({'x0':x,'y0':y,'x1':x+width,'y1':y+height,'text':w['text'],'confidence':float(w['conf'])/100,'lineKey':[w['block_num'],w['par_num'],w['line_num']]})
  return out
 out=[]
 for box,text,confidence in raw['rapidRaw'] or []:
  out.append({'x0':min(x[0] for x in box)*72/300,'y0':min(x[1] for x in box)*72/300,'x1':max(x[0] for x in box)*72/300,'y1':max(x[1] for x in box)*72/300,'text':text,'confidence':float(confidence)})
 return out

def grouped(ws,tolerance=2.8):
 groups=[]
 for w in sorted(ws,key=lambda a:((a['y0']+a['y1'])/2,a['x0'])):
  cy=(w['y0']+w['y1'])/2
  g=next((g for g in reversed(groups[-3:]) if abs(g['y']-cy)<=tolerance),None)
  if g is None:g={'y':cy,'words':[]};groups.append(g)
  g['words'].append(w)
 return groups

def parse(raw,number,engine):
 d=DEFS[number];page=raw['physicalPage']
 if page in d.get('excludePages',[]):return []
 allwords=words(raw,engine);left,pos,pay,expense,right=d.get('columnsByPage',{}).get(page,d['columns'])
 namewords=[w for w in allwords if left<=w['x0']<(pos if d['positions'] else pay)]
 if engine=='tesseract':
  byline=collections.defaultdict(list)
  for w in namewords:byline[tuple(w['lineKey'])].append(w)
  ngroups=sorted([{'y':statistics.median((w['y0']+w['y1'])/2 for w in ws),'words':ws,'lineKey':list(k)} for k,ws in byline.items()],key=lambda g:g['y'])
 else:ngroups=grouped(namewords)
 offsets=[]
 for lo,hi in [(pos,pay),(pay,expense),(expense,right)]:
  ws=[w for w in allwords if lo<=w['x0']<hi]
  deltas=[]
  for g in ngroups:
   eligible=[((w['y0']+w['y1'])/2-g['y']) for w in ws if abs((w['y0']+w['y1'])/2-g['y'])<7]
   if eligible:deltas.append(min(eligible,key=abs))
  offsets.append(statistics.median(deltas) if len(deltas)>=3 else 0)
 rows=[]
 for g in ngroups:
  y=g['y'];name=clean(' '.join(w['text'] for w in sorted(g['words'],key=lambda x:x['x0'])))
  if not re.match(r"^[A-Za-zÀ-ž*‘'\"]",name):continue
  norm=re.sub(r'[^a-z]','',name.lower())
  if norm.startswith(('whoseremuneration','paidtoeach','total','detailed','yearended','electedofficials','otheremployees','kootenaylake','consolidatedtotal','pensionplan','canadapensionplan','scheduleof','alistof','bremuneration','cremuneration','demployer','financialinformation','preparedasrequired','notesthese')):continue
  if re.match(r'^(?:TOTAL\b|DETAILED\b|ELECTED\b|NAME\b|SCHOOL\b|PREPARED\b|NOTES\b|THE EMPLOYER\b|SDS\b|FINANCIAL\b|FISCAL\b|DATE\b|A\. LIST\b|B\. REMUNERATION\b|C\. REMUNERATION\b|D\. EMPLOYER\b)',name,re.I):continue
  picked=[w for w in allwords if pos<=w['x0']<right and (w.get('lineKey')==g.get('lineKey') if engine=='tesseract' and number!=28 else abs((w['y0']+w['y1'])/2-y-offsets[0 if w['x0']<pay else 1 if w['x0']<expense else 2])<=3.4)]
  cells=[[],[],[]]
  for w in sorted(picked,key=lambda x:x['x0']):cells[0 if w['x0']<pay else 1 if w['x0']<expense else 2].append(w)
  role,pay_text,expense_text=[clean(' '.join(w['text'] for w in c)) for c in cells]
  if not pay_text and not ',' in name:continue
  # Name-looking line with no amount remains flagged, not silently dropped.
  if not re.search(r'\d',pay_text) and ',' not in name:continue
  remuneration,_=money(pay_text,d['precision']);expenses,annotation=money(expense_text,d['precision'])
  flags=[]
  if ',' not in name:flags.append('name-has-no-detected-comma')
  if any(isinstance(v,str) and v.startswith('UNRESOLVED:') for v in [remuneration,expenses]):flags.append('unparsed-or-undetected-source-money')
  confidence_words=g['words']+[w for w in picked if w['text'].strip() not in ('$', '-', '–', '—', '*', '**')]
  minimum=min([w['confidence'] for w in confidence_words] or [0])
  if minimum<.80:flags.append('low-reader-confidence-not-a-source-accuracy-probability')
  category='school-trustees' if page in d['trusteePages'] and y<d['trusteeEnd'] else 'employee-remuneration'
  rows.append({'name':name,'position':role or None if d['positions'] else None,'remuneration':remuneration,'expenses':expenses,'pdfPage':page,'category':category,'sourceYPoints':round(y,5),'independentGeometryColumnYOffsets':offsets,'sourceNameWords':g['words'],'sourceOtherWords':picked,'rawMoneyCells':[pay_text,expense_text],'expenseFootnote':annotation,'readerConfidenceMinimum':minimum,'flags':flags})
 return rows

def signature(r):
 vals=[r[k] for k in FIELD_NAMES]
 # Comma layout is harmless, but a given-name word boundary is source data.
 # Removing all name whitespace hid JenniferA/Jennifer A and Shy lah/Shylah.
 return [re.sub(r'\s*,\s*',', ',clean(v)) if i==0 and isinstance(v,str) else re.sub(r'\s+','',v) if i==1 and isinstance(v,str) else v for i,v in enumerate(vals)]
def build():
 results=[]
 for number in DEFS:
  allrows={e:[] for e in ['tesseract','rapid']};pages=[]
  for p in sorted((AREA/'raw-ocr').glob(f'sd{number:02}-p*.json.gzip')):
   raw=json.loads(gzip.decompress(p.read_bytes()))
   alternate=AREA/'extra-tesseract'/p.name
   if alternate.exists():
    extra=json.loads(gzip.decompress(alternate.read_bytes()));assert extra['baseRawSha256']==sha(p.read_bytes());raw['tesseractRawTsv']=extra['tesseractRawTsv']
   pages.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'physicalPage':raw['physicalPage']})
   for engine in allrows:allrows[engine].extend(parse(raw,number,engine))
  if not pages:continue
  a,b=allrows.values();diffs=[]
  for i in range(max(len(a),len(b))):
   ra=a[i] if i<len(a) else None;rb=b[i] if i<len(b) else None
   if not ra or not rb or signature(ra)!=signature(rb):diffs.append({'sequence':i+1,'tesseract':[ra[k] for k in FIELD_NAMES] if ra else None,'rapid':[rb[k] for k in FIELD_NAMES] if rb else None})
  out={'sourceNumber':number,'layout':DEFS[number],'rawPages':pages,'comparison':'Ignore layout whitespace only when comparing recognized names/titles; retain Tesseract word spacing in preferred source transcription. No case, punctuation, glyph or numeric equivalence is assumed.','readers':allrows,'differencesBeforeImageReview':diffs,'acceptedRows':0}
  path=AREA/f'sd{number:02}-raw-reader-rows.json.gzip';blob=pack(out);path.write_bytes(blob)
  summary={'number':number,'pages':len(pages),'readerRows':[len(a),len(b)],'diffs':len(diffs),'flagCounts':{e:dict(collections.Counter(f for r in rows for f in r['flags'])) for e,rows in allrows.items()},'sha256':sha(blob)};results.append(summary);print(json.dumps(summary))
 return results
if __name__=='__main__':build()
