#!/usr/bin/env python3
"""Preserve visible approval, period, scope and controls from refreshed originals."""
import hashlib,json
from pathlib import Path
from gap_school_north_parse import ROOT,AREA

APPROVAL={8:3,28:2,54:1,58:3,59:3,60:3,81:1,82:1}

def main():
 import fitz
 out=AREA/'context-images';out.mkdir(exist_ok=True);pages=[]
 for spec in json.loads((AREA/'ocr-plan.json').read_text()):
  n=spec['number'];raw=Path(spec['path']).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==spec['sha256']
  doc=fitz.open(stream=raw,filetype='pdf')
  wanted=sorted(set([APPROVAL[n],spec['salaryPages'][0],spec['salaryPages'][-1]]))
  for page in wanted:
   pix=doc[page-1].get_pixmap(dpi=180,alpha=False)
   path=out/f'sd{n:02}-physical{page:03}.png';pix.save(path)
   pages.append({'number':n,'physicalPage':page,'sourceSha256':spec['sha256'],'sourceUrl':spec['sourceUrl'],'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'renderDpi':180,'purpose':['approval-and-internal-period'] if page==APPROVAL[n] else ['scope-transition-or-printed-controls']})
 (AREA/'source-context-image-index.json').write_text(json.dumps({'method':'Full refreshed-original pages rendered at180dpi; all captions/periods/signatures/control figures remain sourcepixels, not inferred from OCR.','images':pages,'acceptedRows':0},indent=2)+'\n')

if __name__=='__main__':main()
