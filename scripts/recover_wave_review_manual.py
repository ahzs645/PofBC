#!/usr/bin/env python3
"""Replay immutable independent manual-review fingerprints and six-field rows.

The manual images were read before author payloads. This replay preserves that
evidence; it does not claim a second automated OCR engine or new visual review.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "research/salaries/recovery-wave-2026-11-01/reviews"


def read_json(path: Path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gzip" else raw)


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reviewed(path: Path, expected: str) -> None:
    assert fingerprint(path) == expected, f"Fingerprint changed: {path}"


def main() -> None:
    handoff = read_json(REVIEWS / "independent-manual-review-handoff.json")
    for receipt in handoff["receipts"]:
        reviewed(ROOT / receipt["path"], receipt["sha256"])

    municipal = read_json(REVIEWS / "independent-manual-mcbride-normalized-payloads.json")
    raw = read_json(ROOT / municipal["independentRawTranscript"]["path"])
    count = 0
    for page, comp in zip(raw["pages"][:7], municipal["comparisons"]):
        path = ROOT / comp["file"]
        reviewed(path, comp["dataSha256"])
        reviewed(ROOT / comp["evidenceFile"], comp["evidenceSha256"])
        expected = [["village-of-mcbride", *row[:4], page["pdfPage"]] for row in page["rows"]]
        assert read_json(path) == expected, comp["sourceId"]
        count += len(expected)
    assert count == 35

    schools = read_json(REVIEWS / "independent-manual-schools-normalized-payloads.json")
    for comp in schools["comparisons"]:
        path = ROOT / comp["normalizedFile"]
        reviewed(path, comp["dataSha256"])
        reviewed(ROOT / comp["provenanceFile"], comp["provenanceSha256"])
        with (ROOT / comp["independentRawTranscript"]).open() as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        if "sd19" in comp["sourceId"]:
            rows[54]["position"] = "Speech language Patholoigist"
        if "sd49" in comp["sourceId"]:
            rows[16]["name"] = "FAIRFUL, BEVERLY"
        category = "school-trustees" if comp["sourceId"].endswith("trustees") else "employee-remuneration"
        actual = read_json(path)
        expected = []
        for row in rows:
            if row["scope"] != category:
                continue
            expense = row.get("expensesToken", row.get("expenses"))
            expected.append([
                actual[0][0], row["name"], row["position"] or None,
                int(row["remuneration"]),
                None if expense in ("", "-", "BLANK") else int(expense),
                int(row["pdfPage"]),
            ])
        assert actual == expected, comp["sourceId"]
        count += len(expected)

    health = read_json(REVIEWS / "independent-manual-interior-board-comparison.json")
    raw = read_json(ROOT / health["independentRawTranscript"]["path"])
    raw["pages"][3]["rows"][0][0] = "Beddow, Joyce"
    for page, comp in zip(raw["pages"], health["originalComparisons"]):
        path = ROOT / comp["normalizedFile"]
        reviewed(path, comp["dataSha256"])
        actual = read_json(path)
        expected = [["interior-health", *row, page["pdfPage"]] for row in page["rows"]]
        assert actual == expected, comp["sourceId"]
        count += len(expected)
    assert count == handoff["acceptedNamedRows"] == 202
    print(f"PASS: {len(handoff['receipts'])} immutable receipts; {count} independently transcribed normalized rows")


if __name__ == "__main__":
    main()
