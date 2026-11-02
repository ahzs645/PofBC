#!/usr/bin/env python3
"""Capture two independent OCR readers of exact scanned salary pages, once."""
import argparse,csv,gzip,hashlib,io,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_north';CACHE=Path('/workspace/gap-school-north-cache')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);args=ap.parse_args()
 for k in ('OMP_THREAD_LIMIT','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
 import fitz
 from rapidocr_onnxruntime import RapidOCR
 eng=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1,max_side_len=4096)
 rawdir=AREA/'raw-ocr';rawdir.mkdir(exist_ok=True)
 for spec in json.loads(args.plan.read_text()):
  path=Path(spec['path']);assert sha(path.read_bytes())==spec['sha256'];doc=fitz.open(path)
  for num in spec['salaryPages']:
   dest=rawdir/f"sd{spec['number']:02}-p{num:03}.json.gzip"
   if dest.exists():continue
   png=CACHE/f"sd{spec['number']:02}-p{num:03}-300dpi.png";page=doc[num-1];page.get_pixmap(dpi=300).save(png)
   tsv=subprocess.check_output(['tesseract',str(png),'stdout','--psm','6','tsv'],stderr=subprocess.DEVNULL).decode()
   rapid,elapsed=eng(str(png))
   raw={'sourceSha256':spec['sha256'],'sourceUrl':spec['sourceUrl'],'physicalPage':num,'pageWidthPoints':page.rect.width,'pageHeightPoints':page.rect.height,'renderDpi':300,'imageSha256':sha(png.read_bytes()),'renderMethod':'Original complete PDF page.get_pixmap(dpi=300), no replacement text layer or partial clipping','readers':['Tesseract5.5.0 PSM6 word TSV','RapidOCR1.4.4 PP-OCRv4 ONNX independent text detector/recognizer'],'tesseractRawTsv':tsv,'rapidRaw':rapid,'rapidElapsed':elapsed,'acceptedRows':0}
   blob=gzip.compress((json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0);dest.write_bytes(blob);png.unlink()
   print(spec['number'],num,len(rapid or []),flush=True)
if __name__=='__main__':main()
