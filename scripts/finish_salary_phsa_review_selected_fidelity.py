#!/usr/bin/env python3
"""Independently check captured PHSA page provenance against painted renders.

This reads only metadata from OCR captures. It does not inspect OCR readings,
accept a source, amend a source, or change any frozen evidence.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise SystemExit("Output exists; frozen review receipts cannot be replaced.")

    independent = Path(
        "research/salaries/queue-completion-2026-11-01/reviews/"
        "independent-phsa-history-all-pages-raster-ledger.json.gzip"
    )
    with gzip.open(independent, "rt") as stream:
        ledger = json.load(stream)
    sources = []
    for source in ledger["sources"]:
        source_id = source["sourceId"]
        pages = {row["physicalPage"]: row for row in source["pages"]}
        captures = []
        cache = Path("/tmp/queue-completion-phsa") / source_id / "raw-selected"
        for path in sorted(cache.glob("p*.json.gzip")):
            with gzip.open(path, "rt") as stream:
                raw = json.load(stream)
            page = raw["physicalPage"]
            assert path.name == f"p{page:03}.json.gzip"
            assert raw["sourceId"] == source_id
            assert raw["sourceSha256"] == source["sourceSha256"]
            assert raw["physicalPdfPages"] == source["pdfPages"]
            assert raw["sourceImageSha256"] == pages[page]["actualRenderedPngSha256"]
            assert digest(raw["sourceImagePath"]) == raw["sourceImageSha256"]
            renderer = raw["renderer"]
            assert renderer["engine"] == "PyMuPDF"
            assert renderer["actualPdfPaintedRendering"] is True
            assert renderer["dpi"] == 300
            assert renderer["imageDimensions"] == [2550, 3300]
            profile = raw["sourceSpecificProfile"]
            assert profile["sourceId"] == source_id
            assert digest(profile["path"]) == profile["sha256"]
            captures.append({
                "physicalPage": page,
                "rawCapturePath": str(path),
                "rawCaptureSha256": digest(path),
                "actualSourceImageSha256": raw["sourceImageSha256"],
                "sourceSpecificProfile": profile,
            })
        captured_pages = {row["physicalPage"] for row in captures}
        assert len(captured_pages) == len(captures)
        missing = sorted(set(pages) - captured_pages)
        sources.append({
            "sourceId": source_id,
            "sourceSha256": source["sourceSha256"],
            "physicalPages": source["pdfPages"],
            "capturedPagesChecked": len(captures),
            "missingPhysicalPages": missing,
            "completeSourcePaintedRenderCoverage": not missing,
            "captureMetadataChecks": captures,
        })
    receipt = {
        "reviewer": "/root/held_health_review",
        "version": 1,
        "scriptSha256": digest(__file__),
        "independentWholeSourcePaintedRenderLedger": {
            "path": str(independent), "sha256": digest(independent)
        },
        "capturedPhysicalPagesChecked": sum(x["capturedPagesChecked"] for x in sources),
        "completePhysicalPagesExpected": 1480,
        "allAvailableCaptureImageHashesExact": True,
        "allCaptureSourceAndProfileHashesExact": True,
        "sources": sources,
        "limits": [
            "This gate checks the exact PDF-painted source view and capture provenance.",
            "OCR text and candidate name/money alternatives are not examined by this check.",
            "Missing later captures remain explicitly listed; their source fidelity is not yet asserted.",
            "No semantic row review, monetary control closure or source acceptance follows from this receipt.",
        ],
    }
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "path": str(output), "sha256": digest(output),
        "capturedPhysicalPagesChecked": receipt["capturedPhysicalPagesChecked"],
        "completeSources": [x["sourceId"] for x in sources if x["completeSourcePaintedRenderCoverage"]],
    }))


if __name__ == "__main__":
    main()
