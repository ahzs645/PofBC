#!/usr/bin/env python3
"""Finite PHSA earlier-history candidates, preserving independent raw OCR.

The independent TSV-line and Paddle-box readers and complete-cell pixel routines
are adapted from the earlier PHSA workflow; each new source gets its own literal
headers and geometry, not a prior report's controls or dash calibration.
"""
import argparse,collections,gzip,hashlib,json,re,statistics
from pathlib import Path
from gap_phsa_history_fetch import AREA,CACHE
import gap_phsa_history_readers as readers
import gap_phsa_history_pixels as pixels

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def dump(p,d):
 assert not p.exists(),str(p)
 p.write_bytes(gzip.compress((json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def adapt(d):
 return {**d,'sourceId':d['key'],'yearFromInventory':d['key'][5:],'renderer':{'imageDimensions':[d['imageWidth'],d['imageHeight']]},'sourceImagePath':d['sourceImageCachePath'],'rapidocrRaw':d['rapidOcrRaw']}
def profile(d):
 ws=readers.tess_words(d['tesseractRawTsv']);w,h=d['renderer']['imageDimensions'];nh=[x for x in ws if x['text'].lower()=='name' and x['x']<w*.5 and x['y']<h*.4]
 assert len(nh)==1,(d['key'],'name header',nh)
 hs={}
 for label in ['Name','Remuneration','Expenses']:
  xs=[x for x in ws if x['text'].lower()==label.lower() and abs(x['y']-nh[0]['y'])<30];assert len(xs)==1,(d['key'],label);hs[label]=xs[0]
 left=hs['Remuneration']['box'][0]-30;right=hs['Expenses']['box'][0]-30
 ns=sorted({x['line']:x['y'] for x in ws if x['x']<left and nh[0]['box'][3]<x['y']<h*.88}.values());pitch=statistics.median(b-a for a,b in zip(ns,ns[1:]))
 foot=[x for x in ws if x['text'].lower() in ['this','statement'] and x['y']>h*.85];assert foot
 return {'sourceId':d['key'],'sourceSha256':d['sourceSha256'],'imageDimensions':[w,h],'firstTableHeaders':hs,'namePayBoundary':left,'payExpenseBoundary':right,'sourceFirstTableRowPitchPixels':pitch,'sourceLegalFooterTop':min(x['box'][1] for x in foot),'tableBodyBottomFraction':.94,'derivation':'Actual new-source first-table printed headers and row spacing; each page has separate original name header, footer and control rule detection. No older-source controls.'}
def namekey(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip())
def payment_geometry(geo,ink,prof,one,two):
 import numpy as np
 left=int(prof['namePayBoundary'])+30;right=int(prof['payExpenseBoundary'])-15;top=geo['bodyTop'];bottom=geo['bodyBottom'];rule=np.flatnonzero(ink[top+int(geo['rowPitchPixels']):bottom,left:right].sum(axis=1)>(right-left)*.8);controlrule=top+int(geo['rowPitchPixels'])+int(rule[0]) if len(rule) else None
 if controlrule is not None:bottom=controlrule
 proj=ink[top:bottom,left:right].sum(axis=1);bands=[]
 for ys in pixels.groups(np.flatnonzero(proj>=3)):
  if ys[-1]-ys[0]+1<15 or sum(proj[ys[0]:ys[-1]+1])<100:continue
  bands.append({'top':top+ys[0],'bottom':top+ys[-1]+1,'center':top+(ys[0]+ys[-1])/2,'inkPixels':int(sum(proj[ys[0]:ys[-1]+1])),'sourcePaymentBandBox':[left,top+ys[0],right,top+ys[-1]+1]})
 offsets={'tesseract':[],'rapid':[]}
 for r in one:
  ps=[w['y'] for w in r['rawWords'] if prof['namePayBoundary']<=w['x']<prof['payExpenseBoundary']]
  if ps:offsets['tesseract'].append(r['y']-statistics.mean(ps))
 for r in two:
  if len(r['rawPayMatches'])==1:offsets['rapid'].append(r['y']-r['rawPayMatches'][0]['y'])
 offsets={k:statistics.median(v) if v else 0 for k,v in offsets.items()};pitch=statistics.median(b['center']-a['center'] for a,b in zip(bands,bands[1:])) if len(bands)>1 else geo['rowPitchPixels']
 return {**geo,'actualNameBands':geo['nameBands'],'nameBands':bands,'rowPitchPixels':pitch,'nameToPaymentOffsets':offsets,'censusColumnBox':[left,top,right,bottom],'paymentColumnControlRuleY':controlrule,'censusMethod':'All original painted remuneration-column horizontal bands, independent of OCR row predicates. Original name-column bands retained as additional evidence; no name band/recognized row agreement substitutes for full salary-anchor audit. Painted horizontal remuneration control rules explicitly end individual rows; unlabelled2009 and labelled2010 last controls personally source-viewed.'}
def analyze(key,revision):
 src=next(s for s in json.loads((AREA/'source-inventory.json').read_text())['sources'] if s['key']==key);fs=[AREA/'raw-ocr'/f'{key}-p{p:03d}.json.gzip' for p in range(3,src['pageCount']+1)]
 assert all(f.exists() for f in fs),(key,'capture incomplete')
 prof=profile(adapt(load(fs[0])));rows=[];pages=[];flags=[]
 for f in fs:
  if key=='phsa-2012-13' and '-p087.' in f.name:
   raw=load(f);assert not raw['rapidOcrRaw'];assert not readers.tess_words(raw['tesseractRawTsv']);pages.append({'physicalPage':87,'rawPath':str(f.relative_to(Path.cwd())),'rawSha256':sha(f.read_bytes()),'sourceImageSha256':raw['sourceImageSha256'],'tesseractCount':0,'rapidCount':0,'actualNameBandCount':0,'geometry':{'nameBands':[]},'rows':[],'outsidePaintedNameBands':{'tesseract':[],'rapid':[]},'disposition':'Actual original blank terminal page, independently classified from source pixels by school_north; absent OCR alone is not the acceptance reason.'});continue
  raw=load(f);d=adapt(raw);words=readers.tess_words(d['tesseractRawTsv']);footlines={x['line'] for x in words if x['text'].lower() in ['this','statement'] and x['y']>d['imageHeight']*.85};footwords=[x for x in words if x['line'] in footlines];pp={**prof,'sourceLegalFooterTop':min(x['box'][1] for x in footwords) if footwords else prof['sourceLegalFooterTop']};one,totals1,e1=readers.read_tesseract(d,pp);two,totals2,e2=readers.read_rapid(d,pp);geo,ink=pixels.page_geometry(d,pp);geo=payment_geometry(geo,ink,pp,one,two);pg={'physicalPage':d['physicalPage'],'rawPath':str(f.relative_to(Path.cwd())),'rawSha256':sha(f.read_bytes()),'sourceImageSha256':raw['sourceImageSha256'],'tesseractCount':len(one),'rapidCount':len(two),'actualNameBandCount':len(geo['nameBands']),'geometry':geo,'pageFooterWords':footwords,'readerErrors':e1+e2,'totalsTesseract':totals1,'totalsRapid':totals2,'rows':[]}
  # Original painted name bands supply a separate full body row census.
  for ix,band in enumerate(geo['nameBands']):
   a=[r for r in one if abs(r['y']-geo['nameToPaymentOffsets']['tesseract']-band['center'])<geo['rowPitchPixels']*.38];b=[r for r in two if abs(r['y']-geo['nameToPaymentOffsets']['rapid']-band['center'])<geo['rowPitchPixels']*.38];reasons=[]
   if len(a)!=1 or len(b)!=1:reasons.append('reader-row-anchor-cardinality')
   aa=a[0] if len(a)==1 else None;bb=b[0] if len(b)==1 else None
   glyph=pixels.expense_glyph(ink,geo,prof,ix)
   r={'sequence':len(rows)+1,'physicalPage':d['physicalPage'],'rowOnPage':ix+1,'sourceNameBand':band,'tesseract':aa,'rapid':bb,'expenseFullCellInk':glyph,'selected':None,'reasons':reasons}
   if aa and bb:
    if namekey(aa['name'])!=namekey(bb['name']):reasons.append('name-disagreement')
    if aa['pay']['kind']!='number' or bb['pay']['kind']!='number' or aa['pay']['value']!=bb['pay']['value']:reasons.append('remuneration-disagreement-or-nonnumeric')
    if aa['expense']['kind']=='number' and bb['expense']['kind']=='number':
     if aa['expense']['value']!=bb['expense']['value']:reasons.append('expense-numeric-disagreement')
    elif aa['expense']['kind'] not in ['explicit-dash','not-recognized'] or bb['expense']['kind'] not in ['explicit-dash','not-recognized']:reasons.append('expense-unparsed-or-disagreement')
    # The pixel shape is evidence only until source-specific personal dash calibration.
    elif glyph.get('blank') or glyph.get('connectedInkComponents')!=1 or glyph.get('aspectRatio',0)<2:reasons.append('expense-not-proven-single-horizontal-glyph')
    if aa['nameConfidence']<85 or bb['nameConfidence']<.93:reasons.append('low-name-confidence')
    if aa['payConfidence'] is None or aa['payConfidence']<85 or bb['payConfidence'] is None or bb['payConfidence']<.94:reasons.append('low-pay-confidence')
    if aa['expense']['kind']=='number' and (aa['expenseConfidence'] is None or aa['expenseConfidence']<85 or bb['expenseConfidence'] is None or bb['expenseConfidence']<.94):reasons.append('low-expense-confidence')
    r['selected']={'name':aa['name'],'position':None,'remuneration':aa['pay']['value'],'expenses':aa['expense']['value'] if aa['expense']['kind']=='number' else None,'pdfPage':d['physicalPage']}
   if reasons:flags.append({'sequence':r['sequence'],'physicalPage':d['physicalPage'],'rowOnPage':ix+1,'reasons':reasons})
   rows.append(r);pg['rows'].append(r['sequence'])
  # Retain every independent raw reader row which the pixel row census missed.
  pg['outsidePaintedNameBands']={'tesseract':[r for r in one if not any(abs(r['y']-geo['nameToPaymentOffsets']['tesseract']-b['center'])<geo['rowPitchPixels']*.38 for b in geo['nameBands'])],'rapid':[r for r in two if not any(abs(r['y']-geo['nameToPaymentOffsets']['rapid']-b['center'])<geo['rowPitchPixels']*.38 for b in geo['nameBands'])]}
  pages.append(pg)
 out={'key':key,'revision':revision,'source':src,'profile':prof,'rows':rows,'pages':pages,'flags':flags,'acceptedRows':0,'confidenceRules':{'tesseractName':85,'rapidName':.93,'tesseractMoney':85,'rapidMoney':.94,'meaning':'Finite review triggers, never probabilities or substitutes for source calibration/peer benchmarks.'},'dashStatus':'Uncalibrated candidates only; no unknown is accepted on OCR absence. Complete source-cell pixel masks retained.','noOutreach':True}
 dest=AREA/f'{key}-scan-candidate-{revision}.json.gzip';dump(dest,out)
 print(json.dumps({'key':key,'rows':len(rows),'flags':len(flags),'reasons':dict(collections.Counter(x for r in flags for x in r['reasons'])),'pageCounts':[[p['physicalPage'],p['tesseractCount'],p['rapidCount'],p['actualNameBandCount']] for p in pages if len(set([p['tesseractCount'],p['rapidCount'],p['actualNameBandCount']]))>1],'outside':sum(len(v) for p in pages for v in p['outsidePaintedNameBands'].values()),'candidate':str(dest)},ensure_ascii=False),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',action='append',required=True);p.add_argument('--revision',default='v1');a=p.parse_args()
 for k in a.key:analyze(k,a.revision)
