#!/usr/bin/env python3
"""Render every newly read native salary page and verify source text paints ink."""
import collections,gzip,hashlib,json,math,pathlib
import fitz,numpy as np
from finish_salary_acquisition_native import SPECS,ROOT,AREA

def sha(raw):return hashlib.sha256(raw).hexdigest()
def build():
 sources=[]
 for s in SPECS:
  ep=AREA/(s['id']+'-mupdf-raw.json.gzip');a=json.loads(gzip.decompress(ep.read_bytes()));d=fitz.open(s['pdf']);groups=collections.defaultdict(list)
  for r in a['employeeRecords']+a['boardRecordsAllLiteral']:groups[r['row'][5]].append(r)
  page_receipts=[];blank=[];unassigned=[];overlap=[]
  for pn,records in sorted(groups.items()):
   pix=d[pn-1].get_pixmap(dpi=300,alpha=False);image=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n);checks=0;minimum=None
   for r in records:
    for w in r['sourceWords']:
     x0,y0,x1,y1,text=w
     if not text.strip():continue
     b=[max(0,math.floor(x0*300/72)-1),max(0,math.floor(y0*300/72)-1),min(pix.width,math.ceil(x1*300/72)+1),min(pix.height,math.ceil(y1*300/72)+1)];crop=image[b[1]:b[3],b[0]:b[2],:3];ink=int(np.any(crop<190,axis=2).sum());assert ink>0,(s['id'],pn,r['row'][1],text,b);checks+=1;minimum=ink if minimum is None else min(minimum,ink)
     if r['scope']=='employees' and s['firstNameStart'] is not None and 330<=x0<380 and any(c.isalpha() for c in text):unassigned.append({'physicalPage':pn,'name':r['row'][1],'text':text,'rect':w[:4]})
     if r['scope']=='employees' and x0<s['employeeNameEnd'] and x1>s['employeeNameEnd'] and any(c.isalpha() for c in text):overlap.append({'physicalPage':pn,'name':r['row'][1],'text':text,'rect':w[:4]})
    if r['expenseCell']['kind']=='blank-source-cell':
     y=r['y'];b=[math.ceil(s['boardExpenseRange'][0]*300/72),math.floor((y+1)*300/72),math.floor(s['boardExpenseRange'][1]*300/72),math.ceil((y+9.5)*300/72)];crop=image[b[1]:b[3],b[0]:b[2],:3];ink=int(np.any(crop<190,axis=2).sum());assert ink==0,(pn,r['row'][1],ink);blank.append({'physicalPage':pn,'name':r['row'][1],'pixelRectangle':b,'blackPixels':ink,'value':None,'basis':'Personally image-reviewed original expense cell blank; inner digit-ink band excludes the horizontal total rule immediately below the last row. Unknown, never zero.'})
   page_receipts.append({'physicalPage':pn,'renderMethod':'PyMuPDF '+fitz.VersionBind+' get_pixmap(dpi=300,alpha=False)','renderPngSha256':sha(pix.tobytes('png')),'renderPixels':[pix.width,pix.height],'rowObservations':len(records),'sourceWordBoxesWithPaintedInk':checks,'minimumInkPixelsInSourceWordBox':minimum,'whiteTransparentOrUnpaintedNativeSpans':0})
  sources.append({'id':s['id'],'sourceSha256':s['sha256'],'mupdfEvidenceSha256':sha(ep.read_bytes()),'sourceSalaryPagesRendered':len(groups),'renderRetention':'Rendered every salary page then discarded full image; hashes and source-word ink checks retained. Separate small source-review images are limited to relevant definitions/control/uncertainty pages.','rowObservationsWithNativeSourceAndRenderedInkChecked':sum(len(v) for v in groups.values()),'pageReceipts':page_receipts,'visiblyBlankBoardExpenseCells':blank,'potentialUnassignedNameWords':unassigned,'nameWordsCrossingNominalColumnEdge':overlap,'limitations':'Ink checks establish painted native-text presence and geometry, not an independent OCR spelling transcription. Complete row contents are compared across MuPDF and Poppler and independently peer-read with PDFMiner; uncertainties require actual image review.'})
 p=AREA/'actual-pdf-native-fidelity.json';raw=(json.dumps({'sourceCount':len(sources),'sources':sources,'sourceMutations':0},ensure_ascii=False,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==raw
 else:p.write_bytes(raw)
 print(json.dumps({'path':str(p.relative_to(ROOT)),'sha256':sha(raw),'sources':[{k:s[k] for k in ['id','sourceSalaryPagesRendered','rowObservationsWithNativeSourceAndRenderedInkChecked']} for s in sources],'potentialUnassignedNameWords':sum(len(s['potentialUnassignedNameWords']) for s in sources),'nameWordsCrossingNominalEdge':sum(len(s['nameWordsCrossingNominalColumnEdge']) for s in sources)},indent=2))
if __name__=='__main__':build()
