#!/usr/bin/env python3
"""Batch 006 source-fidelity audit; never reads full candidate values."""
import hashlib,json
from pathlib import Path
import fitz,numpy as np
from PIL import Image,ImageDraw
BASE=Path("research/salaries/held-resolution-2026-11-01/reviews")
PREFIX="independent-phsa-nic-reviewer-006"
MANIFEST=Path("research/salaries/held-resolution-2026-11-01/health/review-batch-006-images.json")
SOURCE=Path("/tmp/sector-health/phsa-2025.pdf")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(MANIFEST)=="0a780d8db722b113b9a48718a1533fe6f3fed821031d5b8e8330f24c55dcae47"
assert sha(SOURCE)=="809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c"
m=json.loads(MANIFEST.read_text());doc=fitz.open(SOURCE)
pages={};out=[];sheets=[]
for index,r in enumerate(m["rows"]):
    pn=r["physicalPage"]; crop=Image.open(r["cropPath"]).convert("RGB")
    assert sha(r["cropPath"])==r["cropSha256"]
    if pn not in pages:
        assert sha(r["fullPageImagePath"])==r["fullPageImageSha256"]
        tile=np.array(Image.open(r["fullPageImagePath"]).convert("L"))[:,190:2210]
        rowmap={}
        for y,row in enumerate(tile):rowmap.setdefault(row.tobytes(),[]).append(y)
        pix=doc[pn-1].get_pixmap(dpi=300,alpha=False)
        painted=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
        pages[pn]=(tile,rowmap,painted,hashlib.sha256(pix.tobytes("png")).hexdigest())
    tile,rowmap,painted,pagehash=pages[pn];b=np.array(crop.convert("L"));k=int(np.argmin(b.mean(axis=1)))
    matches=[int(v-k) for v in rowmap.get(b[k].tobytes(),[]) if v>=k and v-k+len(b)<=len(tile) and np.array_equal(tile[v-k:v-k+len(b)],b)]
    assert len(matches)==1,(pn,r["sourceRowOnPage"],matches)
    y=matches[0];rect=(190,y,2210,y+50);actual=painted.crop(rect)
    path=BASE/f"{PREFIX}-painted-p{pn:03d}-r{r['sourceRowOnPage']:02d}.png"
    if path.exists():raise RuntimeError(f"Refuse overwrite {path}")
    actual.save(path)
    diff=np.any(np.array(actual)!=np.array(crop),axis=2)
    out.append({**r,"tileCropPath":r["cropPath"],"tileCropSha256":r["cropSha256"],"cropPath":str(path.resolve()),"cropSha256":sha(path),"actualPdfCropBox300Dpi":list(rect),"sourcePdfRenderedPagePngSha256":pagehash,"differentRgbPixels":int(diff.sum()),"nameRegionDifferentRgbPixels":int(diff[:,:1300].sum()),"paintedPixelIdenticalToTileCrop":bool(not diff.any())})
for offset in range(0,len(out),10):
    group=out[offset:offset+10];sheet=Image.new("RGB",(2020,75*len(group)),"white");draw=ImageDraw.Draw(sheet)
    for j,r in enumerate(group):
        draw.text((2,j*75+1),f"ACTUAL PDF 300dpi | p{r['physicalPage']} row{r['sourceRowOnPage']:02d} | "+", ".join(r["reviewTargetFields"]),fill="black")
        sheet.paste(Image.open(r["cropPath"]),(0,j*75+25))
    path=BASE/f"{PREFIX}-painted-sheet-{offset//10+1:02d}.png";assert not path.exists();sheet.save(path)
    sheets.append({"path":str(path.resolve()),"sha256":sha(path),"rows":[[r["physicalPage"],r["sourceRowOnPage"]] for r in group]})
receipt={"reviewedOn":"2026-11-01","reviewer":"recovery_municipal (NIC reviewer)","basis":"Independent PyMuPDF get_pixmap(dpi=300,alpha=False) on actual official PDF; respects PDF clipping/masks. Native tile images used ONLY to locate original row pixel coordinates by exact 50-row template matching, never as corrected source content. Full candidate batch not read.","sourcePath":str(SOURCE),"sourceSha256":sha(SOURCE),"imageManifestSha256":sha(MANIFEST),"renderer":fitz.VersionBind,"renderDpi":300,"rows":out,"contactSheets":sheets,"rowCount":len(out),"identicalRowCrops":sum(r["paintedPixelIdenticalToTileCrop"] for r in out),"differentRowCrops":sum(not r["paintedPixelIdenticalToTileCrop"] for r in out),"acceptedEmployeeRows":0}
path=BASE/f"{PREFIX}-painted-source-fidelity.json";assert not path.exists();path.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({"receipt":str(path),"sha256":sha(path),"rowCount":len(out),"identical":receipt["identicalRowCrops"],"different":receipt["differentRowCrops"]}))

