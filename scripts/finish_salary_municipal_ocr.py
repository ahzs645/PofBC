#!/usr/bin/env python3
"""Bounded new municipal raw OCR; original painting and two independent engines."""
import os
for key in ["OMP_THREAD_LIMIT","OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"]:os.environ[key]="1"
import argparse,json,gzip,hashlib,subprocess,time
from pathlib import Path
import fitz
CACHE=Path("/tmp/queue-completion-municipal")
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"research/salaries/queue-completion-2026-11-01/municipal"
SPECS=[
 {"key":"mission-2023","sha256":"82e0ab886a7e8a1e464e3afa25127be7176de79881b93b7602c5a101c8f4d6ac","salaryPages":[6,7,8,9],"supportPages":[1,2]},
 {"key":"mission-2024","sha256":"a4fa12aba963169e276fcd69680887ff788f731fd3ac5260135b88705db4e5a9","salaryPages":[6,7,8,9],"supportPages":[1,2]},
 {"key":"mission-2025","sha256":"23864d9e618e6ceaab92a67e06d38f43d7433e00b747ae53785d8f39f8822624","salaryPages":[6,7,8,9,10],"supportPages":[1,2]},
 {"key":"vernon-2025","sha256":"83a9e5a60b67e1df5016762ab5e8bd9cc3fc054e55ddc28b1a4c1a8cff7d0197","salaryPages":[4,5,6,7],"supportPages":[1,2,3]},
 {"key":"creston-2024","sha256":"24a6cd0394f42596859f15cb4a1ec811c28c5a5c09e004a3766aa78130396ac6","salaryPages":[37],"supportPages":[1,3,4]}
]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encode(obj):return json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()
def run():
 from rapidocr_onnxruntime import RapidOCR
 import importlib.metadata
 engine=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1)
 (AUDIT/"ocr").mkdir(parents=True,exist_ok=True);(CACHE/"images").mkdir(exist_ok=True);(CACHE/"tess").mkdir(exist_ok=True)
 summary=[]
 for spec in SPECS:
  source=CACHE/(spec["key"]+".pdf");assert sha(source)==spec["sha256"];doc=fitz.open(source)
  for pn in sorted(spec["salaryPages"]+spec["supportPages"]):
   target=AUDIT/"ocr"/f'{spec["key"]}-p{pn:02d}.json.gzip'
   if target.exists():
    old=json.loads(gzip.decompress(target.read_bytes()));assert old["sourceSha256"]==spec["sha256"];summary.append({"source":spec["key"],"page":pn,"evidenceSha256":sha(target),"cached":True});continue
   start=time.perf_counter();pix=doc[pn-1].get_pixmap(dpi=300,alpha=False);image=CACHE/"images"/f'{spec["key"]}-p{pn:02d}.png';pix.save(image)
   prefix=CACHE/"tess"/f'{spec["key"]}-p{pn:02d}';subprocess.run(["tesseract",str(image),str(prefix),"-l","eng","--psm","6","txt","tsv"],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   raw,elapsed=engine(str(image));assert raw,(spec["key"],pn)
   payload={"sourceKey":spec["key"],"sourcePath":str(source),"sourceSha256":spec["sha256"],"physicalPage":pn,"salaryPage":pn in spec["salaryPages"],"render":{"method":"PyMuPDF actual page.get_pixmap(dpi=300,alpha=False); honors PDF clipping/masks","pymupdfVersion":fitz.VersionBind,"dpi":300,"pixelSize":[pix.width,pix.height],"imagePath":str(image),"imageSha256":sha(image)},"engines":{"rapidocrVersion":importlib.metadata.version("rapidocr_onnxruntime"),"rapidocrModel":"Bundled PaddleOCR models via RapidOCR ONNX","tesseractVersion":subprocess.check_output(["tesseract","--version"],text=True).splitlines()[0],"tesseractPsm":6,"allThreadCaps":1},"rapidocrRaw":raw,"rapidocrElapsed":elapsed,"tesseractRawText":prefix.with_suffix(".txt").read_text(),"tesseractRawTsv":prefix.with_suffix(".tsv").read_text(),"wallSeconds":time.perf_counter()-start}
   target.write_bytes(gzip.compress(encode(payload),mtime=0));row={"source":spec["key"],"page":pn,"evidenceSha256":sha(target),"seconds":round(payload["wallSeconds"],2)};summary.append(row);print(json.dumps(row),flush=True)
 out=AUDIT/"ocr-run-receipt.json";out.write_text(json.dumps({"date":"2026-11-01","singleWorker":True,"sourceSpecs":SPECS,"pages":summary,"sourcePeriodLabelsUnverifiedUntilOriginalReview":True},indent=2)+"\n");print(json.dumps({"complete":True,"pages":len(summary),"receipt":str(out),"sha256":sha(out)}),flush=True)
if __name__=="__main__":run()

