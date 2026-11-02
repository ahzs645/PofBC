#!/usr/bin/env python3
"""Versioned row reader: preserve each OCR engine's within-line word order."""
import csv,gzip,io,json,statistics
from pathlib import Path
from finish_salary_municipal import ROOT,AREA,sha,money,layouts,normalize_text
def tess(evidence,cfg):
 words=[]
 for w in csv.DictReader(io.StringIO(evidence["tesseractRawTsv"]),delimiter="\t"):
  if w["level"]=="5" and w.get("text","").strip():
   words.append({"x":float(w["left"])+float(w["width"])/2,"y":float(w["top"])+float(w["height"])/2,"text":w["text"],"confidence":float(w["conf"]),"group":tuple(w[k] for k in ("block_num","par_num","line_num"))})
 groups={}
 for w in words:
  if cfg["top"]<w["y"]<cfg["bottom"] and cfg["name"][0]<w["x"]<cfg["name"][1]:groups.setdefault(w["group"],[]).append(w)
 names=sorted(groups.values(),key=lambda group:statistics.median(w["y"] for w in group));ys=[statistics.median(w["y"] for w in group) for group in names];out=[]
 for i,y in enumerate(ys):
  low=cfg["top"] if i==0 else (ys[i-1]+y)/2;high=cfg["bottom"] if i+1==len(ys) else (y+ys[i+1])/2;fields={}
  for field in ("name","position","remuneration","expenses","total"):
   if field not in cfg:continue
   left,right=cfg[field];kept=[w for w in words if left<w["x"]<right and low<w["y"]<high];lines={}
   for word in kept:lines.setdefault(word["group"],[]).append(word)
   ordered=sorted(lines.values(),key=lambda line:statistics.mean(w["y"] for w in line))
   text=" ".join(" ".join(w["text"] for w in sorted(line,key=lambda w:w["x"])) for line in ordered).strip()
   # A separate currency leader belongs to the adjacent pay column, not job title.
   if field=="position":text=" ".join(w for w in text.split() if w!="$")
   value={"raw":text,"confidence":min((w["confidence"] for w in kept),default=None),"words":kept}
   if field in ("remuneration","expenses","total"):value.update(money(text))
   fields[field]=value
  out.append({"anchorY":y,"rowBand":[low,high],"fields":fields})
 return out
def paddle(evidence,cfg):
 items=[]
 for box,text,confidence in evidence["rapidocrRaw"]:
  items.append({"x":sum(p[0] for p in box)/4,"y":sum(p[1] for p in box)/4,"text":text,"confidence":confidence,"box":box})
 anchors=sorted([b for b in items if cfg["top"]<b["y"]<cfg["bottom"] and cfg["name"][0]<b["x"]<cfg["name"][1]],key=lambda b:(b["y"],b["x"]));groups=[]
 for item in anchors:
  if groups and abs(item["y"]-statistics.mean(v["y"] for v in groups[-1]))<13:groups[-1].append(item)
  else:groups.append([item])
 centers=[statistics.mean(x["y"] for x in g) for g in groups];result=[]
 for i,y in enumerate(centers):
  bottom=cfg["bottom"] if i+1==len(centers) else (y+centers[i+1])/2;top=cfg["top"] if i==0 else (centers[i-1]+y)/2;fields={}
  for field in ("name","position","remuneration","expenses","total"):
   if field not in cfg:continue
   left,right=cfg[field];selected=sorted([b for b in items if left<b["x"]<right and top<b["y"]<bottom],key=lambda b:(b["y"],b["x"]));lines=[]
   for item in selected:
    if lines and abs(item["y"]-statistics.mean(v["y"] for v in lines[-1]))<13:lines[-1].append(item)
    else:lines.append([item])
   text=" ".join(" ".join(b["text"] for b in sorted(line,key=lambda b:b["x"])) for line in lines).strip()
   if field=="position":text=" ".join(w for w in text.split() if w!="$")
   value={"raw":text,"confidence":min((b["confidence"] for b in selected),default=None),"boxes":selected}
   if field in ("remuneration","expenses","total"):value.update(money(text))
   fields[field]=value
  result.append({"anchorY":y,"rowBand":[top,bottom],"fields":fields})
 return result
def run():
 sections=[]
 for cfg in layouts():
  path=AREA/"ocr"/f'{cfg["sourceKey"]}-p{cfg["physicalPage"]:02d}.json.gzip';e=json.loads(gzip.decompress(path.read_bytes()));a=tess(e,cfg);b=paddle(e,cfg);assert len(a)==len(b),(cfg,len(a),len(b));diff=[]
  for i,(x,y) in enumerate(zip(a,b)):
   for field in x["fields"]:
    v,w=x["fields"][field],y["fields"][field];same=(v["kind"]==w["kind"] and v["value"]==w["value"]) if field in ("remuneration","expenses","total") else normalize_text(v["raw"])==normalize_text(w["raw"])
    if not same:diff.append({"row":i+1,"field":field,"tesseract":v["raw"],"paddle":w["raw"]})
  sections.append({"layout":cfg,"evidenceFile":str(path.relative_to(ROOT)),"evidenceSha256":sha(path),"tesseractRows":a,"paddleRows":b,"equalRowCounts":True,"disagreements":diff,"acceptedRows":0})
 p=AREA/"reader-draft-v2.json.gzip";raw=gzip.compress(json.dumps({"sourceScopeComplete":False,"sections":sections,"acceptedRows":0,"readerChange":"Within each OCR line, join words left-to-right before joining wrapped lines. Separate currency leaders excluded from position. Both raw streams unchanged; original v1 evidence remains frozen."},ensure_ascii=False,separators=(",",":")).encode(),mtime=0)
 if p.exists():assert p.read_bytes()==raw,"Refuse to overwrite changed v2 staging"
 else:p.write_bytes(raw)
 print(json.dumps({"file":str(p.relative_to(ROOT)),"sha256":sha(p),"rows":sum(len(s["tesseractRows"]) for s in sections),"disagreements":sum(len(s["disagreements"]) for s in sections)}))
if __name__=="__main__":run()

