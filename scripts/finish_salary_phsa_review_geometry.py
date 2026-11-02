#!/usr/bin/env python3
"""Independent actual-source render and raster row-band ledger; never OCR or accept data.

The nine body-top cuts were calibrated from personally viewed original first,
middle and final tables, separately for each source. This is a fourth-CPU,
single-process source check and does not start any OCR engine.
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

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "research/salaries/queue-completion-2026-11-01"
CACHE = Path("/tmp/queue-completion-phsa")
TOPS = {
    "phsa-2015-16": 870, "phsa-2016-17": 885, "phsa-2017-18": 800,
    "phsa-2018-19": 700, "phsa-2019-20": 675, "phsa-2020-21": 680,
    "phsa-2021-22": 755, "phsa-2022-23": 740, "phsa-2023-24": 740,
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def runs(ys, maximum_delta):
    result = []
    for y in ys:
        y = int(y)
        if not result or y - result[-1][-1] > maximum_delta:
            result.append([y])
        else:
            result[-1].append(y)
    return [[r[0], r[-1]] for r in result]


def geometry(rgb, source_id):
    # Standard PIL RGB-to-L luminance, calibrated on each source's actual pages.
    gray = np.asarray(Image.fromarray(rgb).convert("L"))
    top, bottom = TOPS[source_id], 3070
    strong = np.where((gray[:, 200:2300] < 128).sum(axis=1) > 1600)[0]
    rules = [r for r in runs(strong, 1)
             if r[1] - r[0] + 1 >= 3 and top <= r[0] < bottom]
    if rules:
        bottom = min(r[0] for r in rules)
    ys = np.where((gray[:, 190:1450] < 128).sum(axis=1) > 10)[0]
    # At most ten empty rows bridge diacritics/dots to the body of the same row.
    # Source sample pitches range40–62px; no fixed named-row count is enforced.
    bands = runs([y for y in ys if top <= y < bottom], 11)
    return {"bodyTop": top, "bodyBottom": bottom, "longRules": rules,
            "namedInkBands": bands, "namedInkBandCount": len(bands)}


def run(out, only=None, sample=False):
    inventory = AREA / "phsa/source-inventory.json"
    sources = json.loads(inventory.read_text())["sources"]
    ledger = {"reviewer": "held_health_review", "version": 1,
              "scriptSha256": sha(Path(__file__).read_bytes()),
              "sourceInventorySha256": sha(inventory.read_bytes()),
              "method": "Independent original PDF actual RGB300dpi render and raster name-column ink bands. No OCR engines or inferred names/money.",
              "renderer": {"engine": "PyMuPDF", "version": fitz.VersionBind,
                           "invocation": "page.get_pixmap(dpi=300,alpha=False)"},
              "geometry": {"inkThreshold": 128, "nameXRange": [190,1450],
                           "minimumInkPixelsPerNameRow": 11,
                           "maximumVerticalInkDelta": 11,
                           "defaultBodyBottomExclusive": 3070,
                           "finalControlRuleXRange": [200,2300],
                           "minimumRuleDarkPixels": 1601,
                           "minimumRuleConsecutiveRows": 3,
                           "sourceBodyTopCuts": TOPS},
              "limits": ["Raster bands verify geometric row coverage, not semantic field accuracy.",
                         "Narrative pages are rendered and identified but excluded from named scope.",
                         "Every raster/reader row mismatch must be source-reviewed before final closure.",
                         "Available author image hashes are compared; later raw pages require a separate full replay."],
              "sources": []}
    for source in sources:
        key = source["id"]
        if only and key not in only:
            continue
        pdf = Path(source["cachePath"])
        assert sha(pdf.read_bytes()) == source["sourceSha256"], key
        doc = fitz.open(pdf)
        assert len(doc) == source["pdfPages"]
        first_salary = 2 if int(source["year"][:4]) <= 2020 else 1
        item = {"sourceId": key, "sourceSha256": source["sourceSha256"],
                "firstSalaryPhysicalPage": first_salary, "pdfPages": len(doc),
                "pages": []}
        pages = sorted({1, first_salary, len(doc)//2, len(doc)}) if sample else range(1,len(doc)+1)
        for pn in pages:
            page = doc[pn-1]
            native = page.get_text()
            assert not native.strip(), (key,pn,"unexpected native text")
            pix = page.get_pixmap(dpi=300,alpha=False)
            assert [pix.width,pix.height,pix.n] == [2550,3300,3], (key,pn)
            digest = sha(pix.tobytes("png"))
            result = {"physicalPage": pn, "actualRenderedPngSha256": digest,
                      "dimensions": [pix.width,pix.height], "nativeTextChars": len(native),
                      "scope": "narrative-context" if pn<first_salary else "named-employees"}
            if pn >= first_salary:
                rgb = np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
                result.update(geometry(rgb,key))
            raw = CACHE/key/"raw"/f"p{pn:03d}.json.gzip"
            if raw.exists():
                evidence = json.loads(gzip.decompress(raw.read_bytes()))
                assert evidence["sourceSha256"] == source["sourceSha256"]
                assert evidence["physicalPage"] == pn
                assert evidence["sourceImageSha256"] == digest, (key,pn,"render mismatch")
                result["availableRawPageEvidenceSha256"] = sha(raw.read_bytes())
                result["authorActualRenderHashMatches"] = True
            item["pages"].append(result)
            if pn % 25 == 0:
                print(json.dumps({"source":key,"renderedPhysicalPage":pn}),flush=True)
        item["namedInkBandTotal"] = sum(p.get("namedInkBandCount",0) for p in item["pages"])
        item["namedPageCountDistribution"] = dict(collections.Counter(
            str(p["namedInkBandCount"]) for p in item["pages"] if "namedInkBandCount" in p))
        ledger["sources"].append(item)
        doc.close()
        print(json.dumps({"source":key,"rendered":len(item["pages"]),
                          "bands":item["namedInkBandTotal"],
                          "distribution":item["namedPageCountDistribution"]}),flush=True)
    ledger["renderedPhysicalPages"] = sum(len(s["pages"]) for s in ledger["sources"])
    ledger["comparedAvailableRawPages"] = sum("availableRawPageEvidenceSha256" in p
        for s in ledger["sources"] for p in s["pages"])
    assert not out.exists(), "Immutable independent ledger already exists"
    out.parent.mkdir(parents=True,exist_ok=True)
    encoded = json.dumps(ledger,ensure_ascii=False,separators=(",",":")).encode()
    out.write_bytes(gzip.compress(encoded,mtime=0))
    print(json.dumps({"path":str(out),"sha256":sha(out.read_bytes()),
                      "rendered":ledger["renderedPhysicalPages"]}),flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--source",action="append")
    parser.add_argument("--sample",action="store_true")
    args = parser.parse_args()
    run(args.out,args.source,args.sample)
