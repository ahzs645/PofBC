#!/usr/bin/env python3
"""Independently read Tesseract and Paddle cell geometry for bounded municipal originals."""
import csv,gzip,hashlib,io,json,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/"research/salaries/queue-completion-2026-11-01/municipal"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def money(raw):
    token=re.sub(r"\s+","",raw).replace("$","")
    if token in ("-","–","—"):return {"kind":"explicit-dash","value":None,"raw":raw}
    if token=="":return {"kind":"missing-detection","value":None,"raw":raw}
    if re.fullmatch(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?",token):
        return {"kind":"number","value":float(token.replace(",","")) if "." in token else int(token.replace(",","")),"raw":raw}
    return {"kind":"unparsed","value":None,"raw":raw}
def tesseract_read(evidence,section):
    words=[w for w in csv.DictReader(io.StringIO(evidence["tesseractRawTsv"]),delimiter="\t") if w["level"]=="5" and w.get("text","").strip()]
    native=[]
    for w in words:
        native.append({"x":float(w["left"])+float(w["width"])/2,"y":float(w["top"])+float(w["height"])/2,"text":w["text"],"confidence":float(w["conf"]),"group":tuple(w[k] for k in ("block_num","par_num","line_num"))})
    # Tesseract's own line IDs supply name anchors, independent of Paddle boxes.
    anchors={}
    for w in native:
        if section["top"]<w["y"]<section["bottom"] and section["name"][0]<w["x"]<section["name"][1]:
            anchors.setdefault(w["group"],[]).append(w)
    rows=[]
    ordered=sorted(anchors.values(),key=lambda ws:statistics.median(w["y"] for w in ws))
    centers=[statistics.median(w["y"] for w in ws) for ws in ordered]
    for i,(ws,y) in enumerate(zip(ordered,centers)):
        lo=section["top"] if not i else (centers[i-1]+y)/2
        hi=section["bottom"] if i+1==len(centers) else (y+centers[i+1])/2
        fields={}
        for field in ("name","position","remuneration","expenses","total"):
            if field not in section:continue
            left,right=section[field];kept=sorted([w for w in native if left<w["x"]<right and lo<w["y"]<hi],key=lambda w:(round(w["y"]/12),w["x"]))
            raw=" ".join(w["text"] for w in kept).strip()
            fields[field]={"raw":raw,"confidence":min((w["confidence"] for w in kept),default=None),"words":kept}
            if field in ("remuneration","expenses","total"):fields[field].update(money(raw))
        rows.append({"anchorY":y,"rowBand":[lo,hi],"fields":fields})
    return rows
def paddle_read(evidence,section):
    boxes=[]
    for box,text,confidence in evidence["rapidocrRaw"]:
        boxes.append({"left":min(p[0] for p in box),"right":max(p[0] for p in box),"x":sum(p[0] for p in box)/4,"y":sum(p[1] for p in box)/4,"text":text,"confidence":confidence,"box":box})
    # Paddle name-box centers provide a separately implemented row grouping.
    names=sorted([b for b in boxes if section["top"]<b["y"]<section["bottom"] and section["name"][0]<b["x"]<section["name"][1]],key=lambda b:(b["y"],b["x"]))
    groups=[]
    for item in names:
        if groups and abs(item["y"]-statistics.mean(x["y"] for x in groups[-1]))<13:groups[-1].append(item)
        else:groups.append([item])
    ys=[statistics.mean(x["y"] for x in group) for group in groups];result=[]
    for i,y in enumerate(ys):
        lower=section["top"] if i==0 else (ys[i-1]+y)/2
        upper=section["bottom"] if i==len(ys)-1 else (y+ys[i+1])/2
        fields={}
        for field in ("name","position","remuneration","expenses","total"):
            if field not in section:continue
            bounds=section[field]
            selected=[b for b in boxes if bounds[0]<b["x"]<bounds[1] and lower<b["y"]<upper]
            selected.sort(key=lambda b:(round(b["y"]/13),b["left"]))
            text=" ".join(b["text"] for b in selected).strip()
            fields[field]={"raw":text,"confidence":min((b["confidence"] for b in selected),default=None),"boxes":selected}
            if field in ("remuneration","expenses","total"):fields[field].update(money(text))
        result.append({"anchorY":y,"rowBand":[lower,upper],"fields":fields})
    return result
def layouts():
    out=[]
    def add(key,page,scope,top,bottom,name,position,pay,expenses,total=None,expected=None):
        s={"sourceKey":key,"physicalPage":page,"scope":scope,"top":top,"bottom":bottom,"name":name,"remuneration":pay,"expenses":expenses}
        if position:s["position"]=position
        if total:s["total"]=total
        if expected is not None:s["expectedRows"]=expected
        out.append(s)
    for page in [6,7,8,9]:
        if page==9:n,p,g,e,z=[300,735],[735,1600],[1620,1900],[1930,2160],[2200,2420]
        else:n,p,g,e,z=[270,680],[680,1550],[1580,1840],[1880,2100],[2150,2380]
        if page==6:add("mission-2023",page,"elected-officials",608,980,n,p,g,e,z,7)
        add("mission-2023",page,"employee-remuneration",1115 if page==6 else 615,2050 if page==9 else 2765,n,p,g,e,z)
    for page in [6,7,8,9]:
        n,p,g,e=([165,485],[485,1500],[1560,1760],[1850,2040]) if page==6 else ([160,485],[485,1480],[1540,1745],[1800,2020])
        if page==6:add("mission-2024",page,"elected-officials",615,980,n,p,g,e,expected=7)
        add("mission-2024",page,"employee-remuneration",1112 if page==6 else 615,2060 if page==9 else 2768,n,p,g,e)
    for page in [6,7,8,9,10]:
        if page==6:n,p,g,e=[165,485],[485,1510],[1560,1760],[1850,2040]
        else:n,p,g,e=[175,500],[500,1500],[1540,1750],[1810,2025]
        if page==6:add("mission-2025",page,"elected-officials",605,965,n,p,g,e,expected=7)
        add("mission-2025",page,"employee-remuneration",1100 if page==6 else 612,2055 if page==10 else 2755,n,p,g,e)
    add("vernon-2025",4,"elected-officials",540,900,[300,900],[900,1400],[1550,1870],[2110,2300],expected=7)
    for page in [5,6,7]:
        for n,p,e in [([260,690],[700,940],[980,1200]),([1280,1690],[1710,1950],[2030,2260])]:
            add("vernon-2025",page,"employee-remuneration",560,2140 if page==7 else 3040,n,None,p,e,expected=32 if page==7 else 50)
    add("creston-2024",37,"employee-remuneration",1150,2310,[500,880],[880,1510],[1530,1780],[1800,2010],expected=27)
    return out
def normalize_text(raw):
    return re.sub(r"\s+","",raw)
def draft():
    result=[]
    for section in layouts():
        path=AREA/"ocr"/f'{section["sourceKey"]}-p{section["physicalPage"]:02d}.json.gzip'
        evidence=json.loads(gzip.decompress(path.read_bytes()));t=tesseract_read(evidence,section);p=paddle_read(evidence,section)
        disagreements=[]
        if len(t)==len(p):
            for i,(a,b) in enumerate(zip(t,p)):
                for field in a["fields"]:
                    x,y=a["fields"][field],b["fields"][field]
                    agree=(x["kind"]==y["kind"] and x["value"]==y["value"]) if field in ("remuneration","expenses","total") else normalize_text(x["raw"])==normalize_text(y["raw"])
                    if not agree:disagreements.append({"row":i+1,"field":field,"tesseract":x["raw"],"paddle":y["raw"]})
        record={"layout":section,"evidenceFile":str(path.relative_to(ROOT)),"evidenceSha256":sha(path),"tesseractRows":t,"paddleRows":p,"equalRowCounts":len(t)==len(p),"disagreements":disagreements,"acceptedRows":0}
        result.append(record);print(json.dumps({"source":section["sourceKey"],"page":section["physicalPage"],"scope":section["scope"],"column":section["name"],"tess":len(t),"paddle":len(p),"expected":section.get("expectedRows"),"fieldDisagreements":len(disagreements)}))
    path=AREA/"reader-draft.json.gzip";path.write_bytes(gzip.compress(json.dumps({"sourceScopeComplete":False,"sections":result,"acceptedRows":0},ensure_ascii=False,separators=(",",":")).encode(),mtime=0))
if __name__=="__main__":draft()

