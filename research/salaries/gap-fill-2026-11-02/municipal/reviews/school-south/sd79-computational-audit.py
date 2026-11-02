#!/usr/bin/env python3
"""Read-only computational review of SD79; personal image scope stays112rows."""
import copy,csv,gzip,hashlib,io,json,re,sys
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
if not (ROOT/'scripts').exists():ROOT=Path('/workspace/PofBC')
sys.path.insert(0,str(ROOT/'scripts'))
import fitz
import gap_school_south_scan as scan
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_south'
OUT=ROOT/'research/salaries/gap-fill-2026-11-02/municipal/reviews/school-south'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def pin(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def value(v):
 try:return Decimal(v)
 except Exception:return None
def layout(s):return re.sub(r'\s*,\s*',', ',' '.join(s.split())) if isinstance(s,str) else s

def run():
 selected_path=AREA/'sd79-scan-reviewed-candidate-v14.json.gzip';selected=load(selected_path)
 assert sha(selected_path.read_bytes())=='f658928ea0ea464a943382a925e0778ca37eea1161cefc3c9510b4421bb1847b'
 raw_path=Path(selected['rawReaderReplay']['path']);assert sha(raw_path.read_bytes())==selected['rawReaderReplay']['sha256'];raw_selected=load(raw_path)
 pdf=Path('/workspace/gap-school-south-cache/sd79-sofi-2025.pdf');source_sha='a46b4157713d5351996d98fedbb3530d029a6747e9ece90d330b37f4f9ea2b32';assert sha(pdf.read_bytes())==source_sha;doc=fitz.open(pdf)
 original_spec=copy.deepcopy(scan.SPECS[79]);first=[];second=[];pages=[];outside=[];anchors=[]
 monetary=lambda s:bool(re.search(r'\d[.,]\d{2}\)?$',str(s).strip()))
 known_controls={59:{Decimal('126624.00'):'elected-official subtotal'},69:{Decimal('57938687.24'):'named-employee subtotal',Decimal('32578425.29'):'unnamed employee aggregate',Decimal('90643736.53'):'consolidated total'}}
 for pn in range(59,70):
  proof=next(p for p in raw_selected['rawProofs'] if p['path'].endswith(f'-p{pn}.json.gzip'));path=Path(proof['path']);raw=load(path);assert sha(path.read_bytes())==proof['sha256'];assert raw['sourceSha256']==source_sha
  pix=doc[pn-1].get_pixmap(dpi=300);png_sha=sha(pix.tobytes('png'));assert png_sha==raw['imageSha256']
  a=scan.tesseract(raw,79);b=scan.paddle(raw,79);first+=a;second+=b
  assert a==[r for r in raw_selected['tesseractRows'] if r['pdfPage']==pn]
  assert b==[r for r in raw_selected['paddleRows'] if r['pdfPage']==pn]
  scan.SPECS[79]={**copy.deepcopy(original_spec),'ranges':{},'defaultRange':[0,10000]}
  try:wide=[scan.tesseract(raw,79),scan.paddle(raw,79)]
  finally:scan.SPECS[79]=copy.deepcopy(original_spec)
  counts=[]
  for label,small,whole in zip(['tesseract','rapidocr'],[a,b],wide):
   selected_y={r['sourceY300dpi'] for r in small};extras=[]
   for r in whole:
    if r['sourceY300dpi'] in selected_y:continue
    if not any(value(r[k]) is not None for k in ['remuneration','expenses']):continue
    canonical=re.sub(r'\s+','',r['name']).upper()
    is_control=pn==69 and canonical=='RECEIVERGENERALOF CANADA'.replace(' ','') and value(r['expenses'])==Decimal('5396794.95')
    statutory=pn==69 and r['name']=='Prepared as required' and value(r['expenses'])==Decimal(6) and 'section' in str(r['remuneration']).lower()
    item={'reader':label,'physicalPage':pn,'name':r['name'],'remuneration':r['remuneration'],'expenses':r['expenses'],'sourceY300dpi':r['sourceY300dpi'],'disposition':'explicitly labelled employer CPP/EI aggregate, personally read on sourcepage69' if is_control else ('statutory Schedule1section6 reference, personally read sourcefooter, not money' if statutory else 'UNEXPLAINED')};extras.append(item);outside.append(item)
   counts.append({'reader':label,'selectedRows':len(small),'fullPageRowsBeforeControlClassification':len(whole),'outsideAnyMoneyRows':len(extras)})
  # Separate full-page pay-anchor census, directly from raw token streams rather
  # than the row readers' tableYwindows or rowlabel exclusion rules.
  token_sets=[];ts=[]
  for w in csv.DictReader(io.StringIO(raw['tesseractRawTsv']),delimiter='\t',quoting=csv.QUOTE_NONE):
   if w['level']=='5' and 1550<=int(w['left'])<2020 and monetary(w['text']):ts.append({'text':w['text'],'y':int(w['top'])+int(w['height'])/2})
  token_sets.append(('tesseract',ts,a))
  rs=[]
  for box,text,score in raw['rapidOcrRaw']:
   if 1550<=min(p[0] for p in box)<2020 and monetary(text):rs.append({'text':text,'y':sum(p[1] for p in box)/4})
  token_sets.append(('rapidocr',rs,b))
  for label,tokens,small in token_sets:
   for token in tokens:
    matched=next((r for r in small if abs(r['sourceY300dpi']-token['y'])<18),None)
    if matched:disposition='named-row anchor matched independently replayed row'
    else:
     literal=re.sub(r'^[S$]\s*','',token['text']).replace(',','');num=value(literal)
     disposition=known_controls.get(pn,{}).get(num,'UNEXPLAINED')
    anchors.append({'physicalPage':pn,'reader':label,'rawToken':token,'disposition':disposition})
  pages.append({'physicalPage':pn,'sourceCompletePagePngSha256':png_sha,'rawOcrProof':pin(path),'readers':counts})
 assert len(first)==len(second)==len(selected['rows'])==560
 (OUT/'sd79-computational-discovery-before-classification.json').write_text(json.dumps({'outside':outside,'unexplainedAnchors':[r for r in anchors if r['disposition']=='UNEXPLAINED']},indent=2)+'\n')
 assert not [r for r in outside if r['disposition']=='UNEXPLAINED']
 assert not [r for r in anchors if r['disposition']=='UNEXPLAINED']
 old=load(Path(selected['initialCandidate']['path']));oldcoords={(r['pdfPage'],r['sourceY300dpi']):i for i,r in enumerate(old['tesseractRows'],1)}
 manual={};extra={};adaptive={};receipt_pins=[]
 for proof in selected['manualSourceReadings']:
  path=Path(proof['path']);assert sha(path.read_bytes())==proof['sha256'];record=json.loads(path.read_bytes());receipt_pins.append(pin(path))
  if 'primary-flag-source-readings' in path.name:
   for row in record['readings']:assert row['sequence'] not in manual;manual[row['sequence']]=row
  elif 'primary-confidence-and-recovered' in path.name:
   for row in record['readings']:extra[row['sequence']]=row
  else:
   for row in record['readings']:
    if row['district']==79:adaptive[row['sequence']]=row
 personally_read={r['sequence'] for r in json.loads((OUT/'sd79-first-source-transcript.json').read_bytes())['rows']}
 row_audit=[];spacing=[];uncovered_low=[]
 for seq,(one,two,chosen) in enumerate(zip(first,second,selected['rows']),1):
  legacy=oldcoords.get((one['pdfPage'],one['sourceY300dpi']));expected={f:one[f] for f in scan.FIELDS};kinds=[]
  if legacy in manual:expected.update({f:manual[legacy][f] for f in scan.FIELDS});kinds.append('pinned primary original-image literal receipt')
  if seq in extra:expected.update(extra[seq]['fields']);kinds.append('pinned original-image confidence/recovered receipt')
  if seq in adaptive:expected.update(adaptive[seq]['fields']);kinds.append('pinned adaptive source-image receipt')
  if expected['name'].startswith('*'):expected['name']=re.sub(r'^\*{1,2}\s*','',expected['name'])
  assert all(expected[f]==chosen[f] for f in scan.FIELDS),(seq,'selected field replay')
  ta=[float(w['conf'])/100 for w in one['tesseractWords'] if re.search('[A-Za-z0-9]',w['text']) and w['text'] not in ['S','$']]
  ra=[w['confidence'] for w in two['paddleBoxes'] if re.search('[A-Za-z0-9]',w['text']) and w['text'] not in ['S','$']]
  minima=[min(ta,default=0),min(ra,default=0)];assert minima==chosen['readerConfidenceMinimaNotAccuracyProbabilities']
  low=minima[0]<.30 or minima[1]<.70
  if low and not kinds:uncovered_low.append(seq)
  if not kinds:
   assert all(scan.comparison(one[f],f,79)==scan.comparison(two[f],f,79) for f in scan.FIELDS),(seq,'unreviewed field difference')
   assert not any(str(one[f]).startswith('UNRESOLVED:') or str(two[f]).startswith('UNRESOLVED:') for f in ['remuneration','expenses'])
  for field in ['name','position']:
   if layout(one[field])!=layout(two[field]) and seq not in personally_read:spacing.append({'sequence':seq,'physicalPage':one['pdfPage'],'field':field,'tesseract':one[field],'rapidocr':two[field],'sourceY300dpi':one['sourceY300dpi']})
  row_audit.append({'sequence':seq,'physicalPage':one['pdfPage'],'sixSelectedFieldsReplayExactly':True,'modelScoreMinimaNotAccuracyProbabilities':minima,'belowExplicitScoreGuard':low,'personalSourceReceiptKinds':kinds or ['guarded dual-reader agreement'],'peerPersonallyImageRead':seq in personally_read})
 assert not uncovered_low
 result={'reviewerAgent':'/root/gap_municipal','phase':'additive-computational-whole-source-audit','sourceSha256':source_sha,'selectedCandidate':pin(selected_path),'rawReaderSnapshot':pin(raw_path),'originalSourceSalaryPageRasterReplays':11,'rawRowReaderCounts':[len(first),len(second)],'selectedRowsReplayed':560,'allSelectedLiteralFieldsReplayExactly':True,'uncoveredLowModelScoreRows':uncovered_low,'unreviewedWordBoundaryDifferences':spacing,'wholePageMoneyAnchorCount':len(anchors),'wholePageMoneyAnchors':anchors,'outsideWindowAnyMoneyRows':outside,'pages':pages,'primaryReceiptPinsAudited':receipt_pins,'rowAudit':row_audit,'scopeLimit':'This is a computational rerun of the two preserved raw OCR row readers plus independent selection/score/pay-anchor checks. It does not rerun OCR recognition models, nor expand the112-row personal original-image transcription scope. Full-page raster hashes were independently regenerated from the exact PDF.','noOutreach':True}
 p=OUT/'sd79-computational-whole-source-audit.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'rows':560,'originalRasterPages':11,'unreviewedWordBoundaryDifferences':spacing,'outsideAnyMoneyRows':outside,'anchors':len(anchors)},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
