#!/usr/bin/env python3
"""Second independent raster geometry: remuneration ink anchors each named row.

This closes dense-font name-band joins in the separately preserved first ledger.
It does not OCR money, infer names, force a printed count, or accept source data.
"""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from finish_salary_phsa_review_geometry import TOPS, runs

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "research/salaries/queue-completion-2026-11-01"
# Visible source column boundaries, independently checked on the nine source
# context samples; these match the printed per-source remuneration/expense heads.
PAY_X = {
    "phsa-2015-16": [1537,1902], "phsa-2016-17": [1515,1899],
    "phsa-2017-18": [1485,1880], "phsa-2018-19": [1663,1982],
    "phsa-2019-20": [1743,2060], "phsa-2020-21": [1753,2075],
    "phsa-2021-22": [1783,2132], "phsa-2022-23": [1701,2106],
    "phsa-2023-24": [1702,2105],
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run(primary, out, only=None):
    evidence = json.loads(gzip.decompress(primary.read_bytes()))
    inventory_path = AREA/"phsa/source-inventory.json"
    sources = json.loads(inventory_path.read_text())["sources"]
    assert sha(inventory_path.read_bytes()) == evidence["sourceInventorySha256"]
    result = {"reviewer": "held_health_review", "version":1,
              "scriptSha256":sha(Path(__file__).read_bytes()),
              "primaryActualRenderLedger": {"path":str(primary.relative_to(ROOT)),
                                             "sha256":sha(primary.read_bytes())},
              "method":"Independent actual RGB300dpi source pixels. Per-source remuneration-column vertical ink bands are geometric row anchors; original name-column ink is retained within midpoint-bounded rows. No OCR, money recognition, name inference or forced count.",
              "parameters":{"gray":"PIL RGB-to-L<128", "payColumnX":PAY_X,
                            "minimumPayInkPixelsPerRow":3,"maximumPayVerticalDelta":7,
                            "sourceSpecificTopCuts":TOPS,"nameColumnX":[190,1450]},
              "sources":[], "limits":[
                  "Renders and row-band geometry are machine checks; names/money are not personally read for every row.",
                  "Full semantic field accuracy still requires independent readers and original-image resolutions.",
                  "Name-band joins in primary ledger remain immutable and are explained by this additional geometric pass.",
                  "Every unusual pay band, empty name row or reader row mismatch must be source-reviewed."]}
    for source in sources:
        key = source["id"]
        if only and key not in only:
            continue
        parent = next(s for s in evidence["sources"] if s["sourceId"]==key)
        assert sha(Path(source["cachePath"]).read_bytes())==source["sourceSha256"]
        doc=fitz.open(source["cachePath"])
        item={"sourceId":key,"sourceSha256":source["sourceSha256"],"pages":[]}
        for previous in parent["pages"]:
            pn=previous["physicalPage"]
            if previous["scope"]!="named-employees":
                continue
            pix=doc[pn-1].get_pixmap(dpi=300,alpha=False)
            assert [pix.width,pix.height,pix.n]==[2550,3300,3]
            rgb=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
            ink=np.asarray(Image.fromarray(rgb).convert("L"))<128
            top,bottom=previous["bodyTop"],previous["bodyBottom"]
            x0,x1=PAY_X[key]
            ys=np.flatnonzero(ink[top:bottom,x0:x1].sum(axis=1)>=3)+top
            bands=runs(ys,7)
            centers=[(a+b)/2 for a,b in bands]
            rows=[]
            for i,(a,b) in enumerate(bands):
                y0=round((centers[i-1]+centers[i])/2) if i else top
                y1=round((centers[i]+centers[i+1])/2) if i+1<len(bands) else bottom
                name=ink[y0:y1,190:1450];yy,xx=np.where(name)
                bounds=[190+int(xx.min()),y0+int(yy.min()),191+int(xx.max()),y0+int(yy.max())+1] if len(xx) else None
                rows.append({"sourceRowOnPage":i+1,"payInkBand":[a,b],
                             "nameRowBox":[190,y0,1450,y1],"nameInkBounds":bounds,
                             "nameInkPixels":int(len(xx)),
                             "needsSourceGeometryReview":bool(b-a+1>42 or len(xx)<50)})
            item["pages"].append({"physicalPage":pn,
                "actualRenderedPngSha256FromPrimary":previous["actualRenderedPngSha256"],
                "primaryNameInkBands":previous["namedInkBandCount"],
                "remunerationInkBandCount":len(bands),
                "differencePayMinusPrimaryName":len(bands)-previous["namedInkBandCount"],
                "bodyTop":top,"bodyBottom":bottom,"rows":rows})
            if pn%50==0:
                print(json.dumps({"source":key,"page":pn}),flush=True)
        item["rasterNamedRows"]=sum(p["remunerationInkBandCount"] for p in item["pages"])
        item["namedPageCountDistribution"]=dict(collections.Counter(str(p["remunerationInkBandCount"]) for p in item["pages"]))
        item["geometryReviewRows"]=sum(r["needsSourceGeometryReview"] for p in item["pages"] for r in p["rows"])
        result["sources"].append(item)
        doc.close()
        print(json.dumps({"source":key,"rows":item["rasterNamedRows"],
                          "distribution":item["namedPageCountDistribution"],
                          "geometryReviewRows":item["geometryReviewRows"]}),flush=True)
    assert not out.exists(),"Immutable independent ledger already exists"
    out.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,separators=(",",":")).encode(),mtime=0))
    print(json.dumps({"path":str(out),"sha256":sha(out.read_bytes())}),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--primary",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--source",action="append")
    args=parser.parse_args()
    run(args.primary.resolve(),args.out.resolve(),args.source)
