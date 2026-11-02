#!/usr/bin/env python3
"""Discovery-only OCR of the recovered official2014annual report."""
import concurrent.futures,gzip,hashlib,json,re
from pathlib import Path
import fitz
from gap_municipal_scan import AREA,process
if __name__=='__main__':
 p=Path('/workspace/gap-municipal-cache/rossland-annual2014.pdf');d=fitz.open(p);s={'employerSlug':'city-of-rossland','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cachedOriginal':str(p)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rs=list(pool.map(process,[(s,n+1) for n in range(len(d))]))
 (AREA/'annual2014-ocr-discovery-summary.json').write_text(json.dumps({'sourceUrl':'https://rossland.civicweb.net/document/3696/','sourceSha256':s['sha256'],'discoveryOnly':True,'physicalPages':len(d),'candidates':[x for x in rs if re.search(r'remuneration|councillor|\$75,000',x['text'],re.I)]},ensure_ascii=False,indent=2)+'\n');print('finished',len(d))
