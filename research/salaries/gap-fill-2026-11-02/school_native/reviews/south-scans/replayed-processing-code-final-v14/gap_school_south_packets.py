#!/usr/bin/env python3
"""Source-only reviewer packets: field flags, held-out agreements, recovered rows."""
import gzip,json,hashlib,math,re
from pathlib import Path
from gap_school_south_fetch import AREA,CACHE
from gap_school_south_scan import SPECS

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def run(n):
 import fitz
 from PIL import Image,ImageDraw
 d=load(AREA/f'sd{n}-scan-reviewed-candidate-v10.json.gzip');raw=load(AREA/f'sd{n}-scan-parsed-v9.json.gzip');old=load(AREA/f'sd{n}-scan-candidate-v6.json.gzip');rows=d['rows'];one=raw['tesseractRows'];two=raw['paddleRows'];source=json.loads((AREA/f'sd{n}-sofi-2025-retrieval.json').read_text());pdf=CACHE/f'sd{n}-sofi-2025.pdf';assert sha(pdf.read_bytes())==source['sha256'];doc=fitz.open(pdf);root=AREA/'scan-peer-images';root.mkdir(exist_ok=True);pages={};targets=[]
 oldflags={x['sequence'] for x in old['remainingTrueFieldDifferences']};manualseqs={i for i,r in enumerate(rows,1) if r['legacySequenceV6'] in oldflags};recovered={i for i,r in enumerate(rows,1) if r['legacySequenceV6'] is None};confidence=[]
 for i,(a,c,r) in enumerate(zip(one,two,rows),1):
  ta=[float(w['conf'])/100 for w in a['tesseractWords'] if re.search('[A-Za-z0-9]',w['text']) and w['text'] not in ['S','$']];ra=[w['confidence'] for w in c['paddleBoxes'] if re.search('[A-Za-z0-9]',w['text']) and w['text'] not in ['S','$']];confidence.append((min(ta,default=0),min(ra,default=0),i))
 low={i for a,c,i in confidence if (a<.3 or c<.7) and i not in manualseqs and i not in recovered};pool=[i for i in range(1,len(rows)+1) if i not in manualseqs and i not in recovered];risks=[i for a,c,i in sorted(confidence,key=lambda z:(min(z[:2]),z[2])) if i in pool][:5];remaining=[i for i in pool if i not in risks];randoms=sorted(remaining,key=lambda i:sha(f'south-school-source-holdout-v1:{n}:{i}'.encode()))[:5];holdouts=set(risks+randoms)
 for i in sorted(manualseqs|recovered|low|holdouts):
  a,c=one[i-1],two[i-1];p=a['pdfPage'];cy=(a['sourceY300dpi']+c['sourceY300dpi'])/2
  if p not in pages:
   pix=doc[p-1].get_pixmap(dpi=300);pages[p]=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  box=[20,max(0,math.floor(cy-25)),min(2460,pages[p].width),math.ceil(cy+25)];im=pages[p].crop(box);out=root/f'sd{n}-seq{i}-original300.png';im.save(out);kind=[]
  if i in manualseqs:kind.append('initial-true-field-flag')
  if i in recovered:kind.append('complete-page-census-recovered-row')
  if i in low:kind.append('confidence-only-primary-image-audit')
  if i in holdouts:kind.append('withheld-guarded-agreement-benchmark')
  targets.append({'district':n,'sequence':i,'legacySequenceV6':rows[i-1]['legacySequenceV6'],'physicalPage':p,'sourceRowYCenters300Dpi':[a['sourceY300dpi'],c['sourceY300dpi']],'integerBox300Dpi':box,'path':str(out),'sha256':sha(out.read_bytes()),'kinds':kind})
 for label,predicate in [('flags',lambda t:'initial-true-field-flag' in t['kinds'] or 'complete-page-census-recovered-row' in t['kinds']),('confidence',lambda t:'confidence-only-primary-image-audit' in t['kinds']),('holdouts',lambda t:'withheld-guarded-agreement-benchmark' in t['kinds'])]:
  xs=[t for t in targets if predicate(t)]
  for start in range(0,len(xs),15):
   batch=xs[start:start+15];canvas=Image.new('RGB',(2440,len(batch)*80),'white');dr=ImageDraw.Draw(canvas)
   for j,t in enumerate(batch):dr.text((10,j*80),f'SD{n} seq{t["sequence"]} p{t["physicalPage"]} SOURCE',fill='black');canvas.paste(Image.open(t['path']),(0,j*80+22))
   canvas.save(root/f'sd{n}-{label}-sheet-{start//15+1}.png')
 contexts=[]
 for p in sorted({1,2,3,SPECS[n]['pages'][0],SPECS[n]['pages'][-1]}):
  out=root/f'sd{n}-context-p{p}-180.png';doc[p-1].get_pixmap(dpi=180).save(out);contexts.append({'physicalPage':p,'dpi':180,'path':str(out),'sha256':sha(out.read_bytes())})
 dashpacket=json.loads((AREA/'expense-dash-source-benchmark-packet.json').read_text());dash=[{k:x[k] for k in ['district','sequence','sourceSha256','physicalPage','box300Dpi','path','sha256']} for x in dashpacket['sourceOnlyImageTargets'] if x['district']==n]
 result={'district':n,'source':{k:source[k] for k in ['sourceUrl','sha256','cachePath']},'candidateSnapshot':{'path':str(AREA/f'sd{n}-scan-reviewed-candidate-v10.json.gzip'),'sha256':sha((AREA/f'sd{n}-scan-reviewed-candidate-v10.json.gzip').read_bytes())},'rawReaderSnapshot':{'path':str(AREA/f'sd{n}-scan-parsed-v9.json.gzip'),'sha256':sha((AREA/f'sd{n}-scan-parsed-v9.json.gzip').read_bytes())},'salaryPages':SPECS[n]['pages'],'targets':targets,'contexts':contexts,'sourceOnlyExpenseGlyphBenchmarks':dash,'guardedAgreementPolicy':{'requirements':['Both independent OCR row readers agree on literal fields under explicitly recorded whitespace/printed-uppercase conventions.','Rows pass complete-page independent payment census and actual source-specific field geometry; all real disagreements and suspicious field syntax image-read.','Model score below Tesseract0.30 or Rapid0.70 requires personal source-image audit; scores are prioritization signals, not accuracy probabilities.','10 preselected source-only peer benchmarks per report include5 lowest-score agreement rows and5 deterministic agreement holdouts.','All complete expense-cell dash ink must fit a separately personally and independently image-checked source-specific one-component horizontal-glyph calibration. Blank or absent OCR alone never establishes null or zero.','All unknown literal residuals disclosed; amounts not adjusted to balance.'],'peerFlagReadScope':'Read every initial true field flag and recovered row independently. Primary audits confidence-only agreement cases; reviewer audits their receipts and reads10 withheld benchmark rows personally.','initialTrueFlagCount':len(manualseqs),'recoveredRowCount':len(recovered),'confidenceOnlyPrimaryAuditCount':len(low),'peerHoldoutCount':len(holdouts)},'noChosenValuesIncluded':True,'noOutreach':True}
 (AREA/f'sd{n}-scan-source-only-peer-packet.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'district':n,'flags':len(manualseqs),'recovered':len(recovered),'confidence':len(low),'holdouts':len(holdouts)}),flush=True)
if __name__=='__main__':
 for n in [35,38,69,70,78,79]:run(n)
