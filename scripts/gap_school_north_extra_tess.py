#!/usr/bin/env python3
"""Independent Tesseract layout revision for ruled Quesnel pages; rawPSM6 stays."""
import gzip,hashlib,json,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_north';CACHE=Path('/workspace/gap-school-north-cache')
os.environ['OMP_THREAD_LIMIT']='1';os.environ['OMP_NUM_THREADS']='1'
import fitz
out=AREA/'extra-tesseract';out.mkdir(exist_ok=True)
doc=fitz.open(CACHE/'sd28-sofi-2025.pdf')
for num in range(49,54):
 raw=AREA/'raw-ocr'/f'sd28-p{num:03}.json.gzip';dest=out/raw.name
 if dest.exists():continue
 png=CACHE/f'sd28-p{num}-extra.png';doc[num-1].get_pixmap(dpi=300).save(png)
 tsv=subprocess.check_output(['tesseract',str(png),'stdout','--psm','3','tsv'],stderr=subprocess.DEVNULL).decode()
 result={'baseRawSha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'physicalPage':num,'renderDpi':300,'imageSha256':hashlib.sha256(png.read_bytes()).hexdigest(),'reader':'Tesseract5.5 PSM3 detects ruled source layout; original failed PSM6 capture preserved','tesseractRawTsv':tsv}
 dest.write_bytes(gzip.compress((json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));png.unlink();print(num,flush=True)
