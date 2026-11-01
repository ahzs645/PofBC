#!/usr/bin/env python3
"""Stage one OCR reading of the image-only BC Housing 2024/25 salary schedule.

This is evidence preparation, not a salary acceptance/import command. It produces
no normalized employee records and cannot modify the app or salary registry.
"""
import argparse,concurrent.futures,gzip,hashlib,json,pathlib,subprocess,tempfile,urllib.request
import fitz
ROOT=pathlib.Path(__file__).resolve().parents[1]
URL='https://www.bchousing.org/sites/default/files/media/documents/BC-Housing-Management-Commission-Statement-of-Financial-Information-2025.pdf'
PIN='8d5d66718d79e31096c1bb8f1d33540999ba29249560c1d600af185dd87937a3'
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--cache-dir',type=pathlib.Path,default=pathlib.Path('/tmp/sector-crowns'));a.add_argument('--output-dir',type=pathlib.Path,default=ROOT/'research/salaries/sector-search-2026-10-31/crowns/ocr-stage');o=a.parse_args();o.cache_dir.mkdir(parents=True,exist_ok=True)
 pdf=o.cache_dir/(hashlib.sha256(URL.encode()).hexdigest()[:16]+'.pdf')
 if not pdf.exists():
  with urllib.request.urlopen(URL,timeout=60) as f:pdf.write_bytes(f.read())
 raw=pdf.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('Original PDF changed; re-review page range')
 tasks=[]
 with tempfile.TemporaryDirectory(prefix='crown-salary-ocr-') as td:
  doc=fitz.open(pdf)
  if len(doc)!=42 or any(p.get_text().strip() for p in doc):raise ValueError('Unexpected image-only original')
  for page in [1,2,3,*range(9,28)]:
   p=pathlib.Path(td)/f'page-{page}.png';doc[page-1].get_pixmap(matrix=fitz.Matrix(2.8,2.8)).save(p);tasks.append((page,p))
  def read(task):
   page,path=task;text=subprocess.check_output(['tesseract',str(path),'stdout','--psm','3'],stderr=subprocess.DEVNULL).decode()
   return {'pdfPage':page,'sourcePageUrl':URL+f'#page={page}','renderedPngSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ocrTextSha256':hashlib.sha256(text.encode()).hexdigest(),'text':text}
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:pages=list(ex.map(read,tasks))
 o.output_dir.mkdir(parents=True,exist_ok=True)
 evidence={'status':'first-ocr-reading-only-not-accepted','sourceUrl':URL,'sha256':PIN,'periodEnd':'2025-03-31','sourceIndexUrl':'https://www.bchousing.org/about/corporate-reports-plans','pdfPages':42,'schedulePhysicalPages':[10,27],'boardSchedulePhysicalPages':[9],'schedulePageRangeBasis':'Original contents physical page2 indexes the remuneration schedule at printed8. First OCR reading identifies physical9 as board members, physical10–26 as named employees and physical27 as remuneration controls. All row boundaries require full independent visual verification.','renderDpi':201.6,'tesseractVersion':subprocess.check_output(['tesseract','--version']).decode().splitlines()[0],'segmentationMode':3,'pages':pages,'individualRecordsImported':0,'nextActions':['Create an independent higher-resolution or alternative OCR reading.','Identify complete employee rows, header/board boundaries, source name initials and remuneration/expense columns.','Compare every field, inspect all disagreements against original rendered pages and reconcile printed monetary controls.','Accept only after exact reporting period, scope and full row review; do not infer a reason for residuals or force totals.']}
 payload=(json.dumps(evidence,ensure_ascii=False,separators=(',',':'))+'\n').encode();(o.output_dir/'bc-housing-2024-25-first-ocr.json.gzip').write_bytes(gzip.compress(payload,mtime=0));print(json.dumps({'pagesStaged':len(pages),'individualRecordsImported':0,'status':evidence['status']}))
if __name__=='__main__':main()
