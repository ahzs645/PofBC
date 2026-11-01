#!/usr/bin/env python3
"""Reproduce reviewed municipal employee collections from pinned original PDFs.

Run --fetch to retrieve missing official PDFs into --cache, then --write to rebuild
normalized rows. With no action option, verify PDF extraction and retained files.
--check-data verifies the retained data/provenance without network or PDF originals.
New sources require a separately reviewed entry in reviewed-inputs.json; this script
never promotes a newly discovered report or adjusts records to make totals balance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

from parse_municipal_lower_mainland_layouts import key, money, parse_document

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "research/salaries/municipal-lower-mainland"
SCHEMA = ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serialize(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def compressed(value) -> bytes:
    return gzip.compress(serialize(value), mtime=0)


def number(value):
    if value is None:
        return None
    value = Decimal(value)
    return int(value) if value == value.to_integral_value() else float(value)


def normalize(rows, reviewed):
    output = []
    for row in rows:
        components = [money(cell) for cell in row["raw"]]
        selected = [components[index] for index in reviewed["remunerationColumns"]]
        if not any(value is not None for value in selected):
            raise ValueError(f"{reviewed['key']}: missing all remuneration components")
        pay = sum((value or Decimal(0) for value in selected), Decimal(0))
        output.append([reviewed["employerSlug"], row["name"], row["position"],
                       number(pay), number(components[reviewed["expensesColumn"]]), row["page"]])
    return output


def table_completeness(parsed, text):
    """Every inter-row character must belong to a disclosed record or reviewed note.

    Whitespace and printed currency glyphs are normalized, but monetary amounts,
    punctuation and textual content remain. This catches dropped records, clipped
    positions and stray supplier/control rows inside the accepted employee table.
    """
    pages = text.split("\f")
    gaps = []
    for page in sorted({row["page"] for row in parsed["rows"]}):
        canonical = key(pages[page - 1])
        cursor = 0
        first = True
        for row in (r for r in parsed["rows"] if r["page"] == page):
            offset = canonical.find(row["sourceKey"], cursor)
            if offset < 0:
                raise ValueError(f"Physical page {page}: source text missing for {row['name']}")
            if not first and offset > cursor:
                gaps.append({"page": page, "text": canonical[cursor:offset]})
            cursor = offset + len(row["sourceKey"])
            first = False
    return gaps


def parse_reviewed(reviewed, cache):
    pdf = cache / f"{reviewed['key']}.pdf"
    original = pdf.read_bytes()
    if sha256(original) != reviewed["sha256"]:
        raise ValueError(f"{reviewed['key']}: original PDF hash changed; review required")
    text_path = pdf.with_suffix(".txt")
    subprocess.run(["pdftotext", "-layout", str(pdf), str(text_path)], check=True,
                   stderr=subprocess.PIPE)
    parsed = parse_document(text_path)
    if not parsed or "rows" not in parsed:
        raise ValueError(f"{reviewed['key']}: expected source layout not found")
    if any(error[0] != "subtotal-mismatch" for error in parsed["errors"]):
        raise ValueError(f"{reviewed['key']}: unresolved row extraction error")
    expected = reviewed["expected"]
    comparisons = {
        "rowCount": parsed["n"],
        "pages": parsed["pages"],
        "componentSums": parsed["sums"],
        "printedControls": parsed["controls"],
        "controlResiduals": parsed["deltas"],
        "parserErrors": parsed["errors"],
        "parserErrorCount": parsed["errorCount"],
        "rowsByPhysicalPage": dict(Counter(str(row["page"]) for row in parsed["rows"])),
        "interRowNotes": table_completeness(parsed, text_path.read_text()),
    }
    for field, actual in comparisons.items():
        if expected[field] != actual:
            raise ValueError(f"{reviewed['key']}: {field} changed: {actual!r}")
    normalized = normalize(parsed["rows"], reviewed)
    if sha256(serialize(normalized)) != reviewed["normalizedSha256"]:
        raise ValueError(f"{reviewed['key']}: normalized records changed")
    audit = {
        "sourceKey": reviewed["key"], "originalSha256": reviewed["sha256"],
        "componentColumns": reviewed["componentColumns"], "rows": parsed["rows"],
        "printedControls": parsed["controls"], "componentSums": parsed["sums"],
        "controlResiduals": parsed["deltas"],
    }
    return normalized, audit


def fetch(reviewed, cache):
    pdf = cache / f"{reviewed['key']}.pdf"
    if pdf.exists():
        return
    request = urllib.request.Request(reviewed["sourceUrl"], headers={"User-Agent": "PofBC-source-verification/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        content = response.read()
    if not content.startswith(b"%PDF") or sha256(content) != reviewed["sha256"]:
        raise ValueError(f"{reviewed['key']}: downloaded source is not the reviewed PDF")
    pdf.write_bytes(content)


def verify_data(source, reviewed):
    blob = (COLLECTION / source["file"]).read_bytes()
    if sha256(blob) != source["dataSha256"]:
        raise ValueError(f"{source['id']}: compressed row hash mismatch")
    plain = gzip.decompress(blob)
    if sha256(plain) != reviewed["normalizedSha256"]:
        raise ValueError(f"{source['id']}: normalized row hash mismatch")
    rows = json.loads(plain)
    if len(rows) != source["rowCount"] or any(len(row) != 6 for row in rows):
        raise ValueError(f"{source['id']}: invalid row schema/count")
    if any(row[0] != source["employerSlug"] or not row[1] or not isinstance(row[5], int) for row in rows):
        raise ValueError(f"{source['id']}: invalid employer/name/page")
    for label, index in [("totalRemuneration", 3), ("totalExpenses", 4)]:
        actual = sum((Decimal(str(row[index])) for row in rows if row[index] is not None), Decimal(0))
        if actual != Decimal(str(source[label])):
            raise ValueError(f"{source['id']}: {label} mismatch")
    audit_bytes = (COLLECTION / source["provenanceFile"]).read_bytes()
    if sha256(audit_bytes) != source["provenanceSha256"]:
        raise ValueError(f"{source['id']}: source component audit hash mismatch")
    audit = json.loads(gzip.decompress(audit_bytes))
    if audit["originalSha256"] != source["sha256"] or normalize(audit["rows"], reviewed) != rows:
        raise ValueError(f"{source['id']}: source components disagree with normalized records")
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-lower"))
    parser.add_argument("--fetch", action="store_true", help="Fetch missing pinned official PDFs")
    parser.add_argument("--write", action="store_true", help="Rebuild accepted row and audit files")
    parser.add_argument("--check-data", action="store_true", help="Verify retained data without PDF downloads")
    parser.add_argument("--source", action="append", help="Limit to a reviewed report key; repeatable")
    args = parser.parse_args()
    if args.check_data and (args.fetch or args.write):
        parser.error("--check-data cannot be combined with --fetch or --write")
    inputs = json.loads((COLLECTION / "reviewed-inputs.json").read_text())["sources"]
    manifest = json.loads((COLLECTION / "sources.json").read_text())
    indexed = {source["inputKey"]: source for source in manifest["sources"]}
    if args.source:
        missing = set(args.source) - {entry["key"] for entry in inputs}
        if missing:
            parser.error(f"Unreviewed source keys: {sorted(missing)}")
        inputs = [entry for entry in inputs if entry["key"] in args.source]
    args.cache.mkdir(parents=True, exist_ok=True)
    total = 0
    for reviewed in inputs:
        source = indexed[reviewed["key"]]
        if args.fetch:
            fetch(reviewed, args.cache)
        if not args.check_data:
            rows, audit = parse_reviewed(reviewed, args.cache)
            for value, filename, digest in [(rows, source["file"], source["dataSha256"]),
                                            (audit, source["provenanceFile"], source["provenanceSha256"])]:
                generated = compressed(value)
                if sha256(generated) != digest:
                    raise ValueError(f"{reviewed['key']}: generated {filename} hash changed")
                if args.write:
                    (COLLECTION / filename).write_bytes(generated)
        total += verify_data(source, reviewed)
    print(json.dumps({"verifiedReports": len(inputs), "verifiedRows": total,
                      "originalPdfValidation": not args.check_data}))


if __name__ == "__main__":
    main()
