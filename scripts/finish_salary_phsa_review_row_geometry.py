#!/usr/bin/env python3
"""Compare staged PHSA row locators with independent original ink anchors.

Candidate names and monetary values are intentionally never read or emitted.
The independent ledger was derived from original painted pages without OCR.
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
        raise SystemExit("Output exists; use a new additive review receipt.")
    independent = Path(
        "research/salaries/queue-completion-2026-11-01/reviews/"
        "independent-phsa-history-all-pages-raster-pay-anchors.json.gzip"
    )
    with gzip.open(independent, "rt") as stream:
        ledger = json.load(stream)
    evidence = Path("research/salaries/queue-completion-phsa/evidence")
    sources = []
    exceptions = []
    for source in ledger["sources"]:
        source_id = source["sourceId"]
        pages = {row["physicalPage"]: row for row in source["pages"]}
        checked = []
        for path in sorted(evidence.glob(f"{source_id}-rows-p*.json.gzip")):
            with gzip.open(path, "rt") as stream:
                staged = json.load(stream)
            page = staged["physicalPage"]
            assert staged["sourceId"] == source_id
            assert staged["sourceSha256"] == source["sourceSha256"]
            if page not in pages:
                assert staged["role"] != "employee-salary-table"
                assert not staged["rows"]
                continue
            original = pages[page]
            assert staged["sourceImageSha256"] == original["actualRenderedPngSha256FromPrimary"]
            assert staged["role"] == "employee-salary-table"
            rows = staged["rows"]
            original_rows = original["rows"]
            if len(rows) != len(original_rows):
                exceptions.append({
                    "sourceId": source_id, "physicalPage": page,
                    "kind": "row-count-difference", "stagedRows": len(rows),
                    "independentRasterRows": len(original_rows),
                })
            for row, original_row in zip(rows, original_rows):
                index = row["sourceRowOnPage"]
                assert index == original_row["sourceRowOnPage"]
                assert row["physicalPage"] == page
                top, bottom = original_row["nameRowBox"][1::2]
                center = row["sourceNameBand"]["center"]
                if not top <= center < bottom:
                    exceptions.append({
                        "sourceId": source_id, "physicalPage": page,
                        "sourceRowOnPage": index,
                        "kind": "name-band-outside-independent-original-row",
                        "sourceNameBandCenter": center,
                        "independentRowVerticalBounds": [top, bottom],
                    })
            if staged["pageGeometryNeedsReview"] or staged["dateTitleNeedsReview"] or staged["pageIssues"]:
                exceptions.append({
                    "sourceId": source_id, "physicalPage": page,
                    "kind": "staged-page-needs-review",
                    "pageGeometryNeedsReview": staged["pageGeometryNeedsReview"],
                    "dateTitleNeedsReview": staged["dateTitleNeedsReview"],
                    "pageIssues": staged["pageIssues"],
                })
            checked.append({
                "physicalPage": page, "stagedPageEvidencePath": str(path),
                "stagedPageEvidenceSha256": digest(path),
                "sourceImageSha256": staged["sourceImageSha256"],
                "stagedRows": len(rows),
                "independentOriginalRasterRows": len(original_rows),
            })
        captured = {row["physicalPage"] for row in checked}
        missing = sorted(set(pages) - captured)
        sources.append({
            "sourceId": source_id, "sourceSha256": source["sourceSha256"],
            "expectedNamedRows": source["rasterNamedRows"],
            "checkedNamedRows": sum(row["stagedRows"] for row in checked),
            "checkedSalaryPages": len(checked), "missingSalaryPages": missing,
            "completeSourceGeometryCoverage": not missing,
            "pageComparisons": checked,
        })
    result = {
        "reviewer": "/root/held_health_review", "version": 1,
        "scriptSha256": digest(__file__),
        "independentAllSourceRasterPayAnchorLedger": {
            "path": str(independent), "sha256": digest(independent)
        },
        "checkedSalaryPages": sum(row["checkedSalaryPages"] for row in sources),
        "checkedNamedRows": sum(row["checkedNamedRows"] for row in sources),
        "expectedSalaryPages": 1474, "expectedNamedRows": 64912,
        "sources": sources, "exceptions": exceptions,
        "exceptionCount": len(exceptions),
        "limits": [
            "Every available staged row count and name-band location is compared with independent painted-source ink anchors.",
            "Candidate names, pay, expenses and OCR alternatives are intentionally not accessed.",
            "Missing later staged pages remain explicit and are not deemed reviewed.",
            "Geometry agreement is separate from semantic field, period, control and source-acceptance review.",
        ],
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "path": str(output), "sha256": digest(output),
        "checkedSalaryPages": result["checkedSalaryPages"],
        "checkedNamedRows": result["checkedNamedRows"],
        "exceptionCount": len(exceptions),
    }))


if __name__ == "__main__":
    main()
