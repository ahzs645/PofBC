#!/usr/bin/env python3
"""Package original renders/OCR and the explicitly scoped visual review receipts."""
from pathlib import Path
import csv,gzip,hashlib,json,fitz
from follow_through_rru_langara import ROOT,CACHE,CONFIG,PRINTED_COMPONENTS,sha,js,gz
for kind in ['rru','langara']:
 out=ROOT/'research/salaries'/('follow-through-'+kind)
 manifest=json.loads((out/'sources.json').read_text());byid={s['id']:s for s in manifest['sources']}
 for key,c in CONFIG.items():
  if not key.startswith(kind+'-'):continue
  sid=key.replace('rru-','rru-sofi-').replace('langara-','langara-sofi-')+'-employees'
  if c.get('scan') and sid in byid:continue
  visual=out/'visual'/f'{key}.json';v=json.loads(visual.read_text());v['reviewedPhysicalPages']=c['pages'];v['reviewedOn']='2026-11-02'
  v['reviewScope']='Full page rendered contact sheets inspected for reporting-period headers, complete alphabetic employee continuation, board/employee boundaries, first/last rows and separate totals/reconciliation blocks. Original controls inspected as enlarged crops. Exact six-field values for digital schedules are independently validated with PyMuPDF and Poppler; contact sheets are not claimed as a manual pixel audit of every employee cell.'
  v['status']='scanned-schedule-held-pending-cell-validation' if c.get('scan') else 'reviewed'
  v['contactSheets']=[{'file':str(p.relative_to(out)),'sha256':sha(p.read_bytes())} for p in sorted((out/'visual').glob(key+'-contact-*.jpg'))]
  d=fitz.open(CACHE/('additional-source-'+key+'.pdf'));controls=[]
  anchors=[]
  if key in PRINTED_COMPONENTS:
   anchors=[(c['pages'][0],PRINTED_COMPONENTS[key]['belowThreshold'][0],'below-threshold'),(c['pages'][-1],PRINTED_COMPONENTS[key]['combined'][0],'combined')]
   if key=='rru-2021-22':anchors[0]=(28,PRINTED_COMPONENTS[key]['belowThreshold'][0],'below-threshold')
  elif not c.get('scan'):anchors=[(c['pages'][-1],c['control'][0],'named-employee-subtotal')]
  for n,num,label in anchors:
   rect=d[n-1].search_for(f'{num:,}')[0];clip=fitz.Rect(40,max(rect.y0-9,0),570,min(rect.y1+28,792));f=out/'visual'/f'{key}-{label}-control.png';d[n-1].get_pixmap(matrix=fitz.Matrix(3,3),clip=clip).save(f)
   controls.append({'pdfPage':n,'file':str(f.relative_to(out)),'sha256':sha(f.read_bytes()),'bboxPoints':list(clip),'scale':3,'printedRemunerationAnchor':num})
  v['controlCrops']=controls
  if c.get('scan'):
   ocr=[]
   for n in c['pages']:
    b=CACHE/f'{key}-ocr-p{n:02}'
    txt=b.with_suffix('.txt').read_text();tsv=b.with_suffix('.tsv').read_text();im=b.with_suffix('.png')
    ocr.append({'pdfPage':n,'renderScale':3,'renderSha256':sha(im.read_bytes()),'tesseractPsm':6,'ocrText':txt,'ocrTsv':tsv})
   gz(out/'evidence'/f'{key}-ocr-unaccepted.json.gzip',{'sourceId':key,'status':'held-for-review','normalizationAuthorized':False,'reason':'Employee text absent from both original PDF readers; OCR has visible errors and has not met complete cell reconciliation. These are evidence candidates only, never input observations.','pages':ocr})
   v['ocrEvidenceFile']=f'evidence/{key}-ocr-unaccepted.json.gzip'
  else:
   sid=key.replace('rru-','rru-sofi-').replace('langara-','langara-sofi-')+'-employees';s=byid[sid];s['validation']['physicalPagesVisuallyReviewed']=c['pages'];s['validation']['visualReviewFile']=str(visual.relative_to(out));s['validation']['visualReviewScope']=v['reviewScope']
  js(visual,v)
 js(out/'sources.json',manifest)
