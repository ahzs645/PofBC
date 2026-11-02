#!/usr/bin/env python3
"""Read-only confidence diagnostics against frozen independent image labels.

This does not accept rows, remove flags, change names, or run OCR. The separate
source typography policy remains necessary for indistinguishable I/l glyphs.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "research/salaries/queue-completion-2026-11-01"
REVIEWS = AREA / "reviews"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path, expected=None):
    digest = sha(path)
    if expected is not None and digest != expected:
        raise ValueError(f"Frozen input changed: {path}")
    return json.loads(path.read_text()), {
        "path": str(path.relative_to(ROOT)), "sha256": digest
    }


def normalized_spacing(value):
    # Comparison only; never write a replacement source name.
    return re.sub(r"\s*,\s*", ",", re.sub(r"\s+", " ", value).strip())


def confidence_curve(labels, thresholds):
    result = []
    for threshold in thresholds:
        flagged = [x for x in labels if x["confidence"] < threshold]
        unflagged = [x for x in labels if x["confidence"] >= threshold]
        result.append({
            "threshold": threshold,
            "labels": len(labels),
            "belowThreshold": len(flagged),
            "literalMismatchesBelowThreshold": sum(x["mismatch"] for x in flagged),
            "literalMismatchesAtOrAboveThreshold": sum(x["mismatch"] for x in unflagged),
            "matchingReadingsBelowThreshold": sum(not x["mismatch"] for x in flagged),
        })
    return result


def build():
    inputs = []
    fixture_index, pin = read(
        REVIEWS / "independent-phsa-history-batches-benchmark-index.json",
        "3d3de244f7fcf1eff6db7aaf5776117c817ead58f338624ecb23063dc7c9d753",
    )
    inputs.append(pin)
    trials, pin = read(AREA / "phsa/first-table-ocr-benchmark-trials-003.json")
    inputs.append(pin)
    profiles, pin = read(AREA / "phsa/processing-profile-index-001.json")
    inputs.append(pin)
    fixture_by_hash = {x["transcript"]["sha256"]: x for x in fixture_index["fixtures"]}
    sources = []
    for profile_pin in profiles["sourceProfiles"]:
        profile, pin = read(ROOT / profile_pin["path"], profile_pin["sha256"])
        inputs.append(pin)
        selected = next(x for x in trials["results"]
                        if x["sourceId"] == profile["sourceId"]
                        and x["configuration"] == profile["chosenRapidConfiguration"])
        fixture = fixture_by_hash[selected["fixtureSha256"]]
        fixture_path = ROOT / fixture["transcript"]["path"]
        if sha(fixture_path) != selected["fixtureSha256"]:
            raise ValueError("Independent literal fixture changed")
        labels = []
        mismatches = []
        for row in selected["perRowComparison"]:
            mismatch = not row["rapidNameMatch"]
            labels.append({"confidence": row["rapidNameConfidence"], "mismatch": mismatch})
            if mismatch or not row["tesseractNameMatch"]:
                mismatches.append({
                    "sourceRowOnPage": row["sourceRowOnPage"],
                    "independentLiteral": row["literalFixtureName"],
                    "rapidName": row["rapidName"],
                    "tesseractName": row["tesseractName"],
                    "rapidNameConfidence": row["rapidNameConfidence"],
                })
        if len(labels) != fixture["namedRows"]:
            raise ValueError("Complete first-table coverage differs")
        sources.append({
            "sourceId": profile["sourceId"],
            "sourceSha256": profile["sourceSha256"],
            "selectedRapidConfiguration": selected["configuration"],
            "fixture": fixture["transcript"],
            "fixtureRows": len(labels),
            "rapidLiteralNameMismatches": sum(x["mismatch"] for x in labels),
            "tesseractLiteralNameMismatches": selected["fixtureRows"] - selected["tesseractNameMatches"],
            "rapidNameConfidenceDiagnostic": confidence_curve(labels, [.90, .95, .98, .99]),
            "sourceImageRecheckCandidates": mismatches,
        })

    raw, pin = read(
        REVIEWS / "independent-phsa-history-batches-2015-16-002-original-transcript.json",
        "1b2a9a8068a3166ddfaa9c15f0c5678f67f21ccf478e248a2b9710396bd89fc5",
    )
    inputs.append(pin)
    batch, pin = read(
        AREA / "phsa/batches/phsa-2015-16-batch-002.json",
        "e96ae4c71c65d0c055c7f80fb8281612053726e04c5104de0ae952a9512da13c",
    )
    inputs.append(pin)
    counters = collections.Counter()
    reasons = collections.Counter()
    money_labels = []
    name_labels = {"tesseract": [], "paddle": []}
    for image, machine in zip(raw["rows"], batch["rows"]):
        if (image["physicalPage"], image["sourceRowOnPage"]) != (
            machine["physicalPage"], machine["sourceRowOnPage"]
        ):
            raise ValueError("Image/engine row identity differs")
        for values in machine["fieldConflicts"].values():
            reasons.update(values)
        for field, literal in image["initialTargetReadings"].items():
            counters[field] += 1
            engine_values = []
            for engine, key in [("tesseract", "rawTesseractRow"), ("paddle", "rawRapidRow")]:
                row = machine[key]
                if field == "name":
                    value = normalized_spacing(row["name"])
                    confidence = row["nameConfidence"]
                    name_labels[engine].append({"confidence": confidence, "mismatch": value != literal})
                else:
                    value = row["pay" if field == "remuneration" else "expense"]["value"]
                    confidence = row["payConfidence" if field == "remuneration" else "expenseConfidence"]
                    if value != literal:
                        raise ValueError("This bounded money diagnostic requires the reviewed exact matches")
                engine_values.append(value)
            if field != "name":
                money_labels.append({"field": field, "bothEnginesMatchImage": True})
    if len(money_labels) != 200 or len(raw["rows"]) != 400:
        raise ValueError("Frozen bounded diagnostic coverage differs")
    return {
        "reviewedOn": "2026-11-01",
        "reviewer": "/root/recovery_review",
        "kind": "independent-image-label-confidence-diagnostic",
        "inputs": inputs,
        "sourceFirstTableFixtures": sources,
        "firstTableImageLabeledRows": sum(x["fixtureRows"] for x in sources),
        "firstTableLiteralMoneyFieldsAvailable": 810,
        "additional2015BatchDiagnostic": {
            "batch": raw["batch"], "imageReadRows": 400,
            "requestedFieldCounts": dict(counters),
            "bothEngineMoneyMatches": len(money_labels),
            "definiteMoneyMismatches": 0,
            "recordedFlagReasons": dict(reasons),
            "tesseractNameDiagnostic": confidence_curve(name_labels["tesseract"], [50, 70, 80, 85, 90]),
            "paddleNameDiagnostic": confidence_curve(name_labels["paddle"], [.90, .95, .98, .99]),
            "nameMismatchInterpretation": "Six differences per engine concern contextual I/l typography choices, not pixel-proved glyph errors. Exact qualified ledger and peer/root adoption apply separately.",
        },
        "methodLimits": [
            "The400-row batch is selected from low-confidence/name-quality flags after disagreement-priority allocation. It is not an unbiased source error-rate estimate or proof that unreviewed rows are correct.",
            "Literal fixture mismatches are source-image recheck candidates; a manual fixture can also contain reviewer error. Frozen fixtures must not be rewritten in response to machine output.",
            "Matching numeric values in155tesseract-pay-below90 and39tesseract-expense-below90 targets demonstrate many confidence-only flags in this bounded sample. They do not waive missing detections, reader disagreement, source glyph ambiguity or geometry/period controls.",
            "First-table source-specific font/density fixtures and this independently image-read held-out batch can inform future field-specific confidence calibration. Any calibration change needs a new versioned profile and retained original outputs/flags; this script changes none.",
            "High-confidence agreed-name I/l, pipes and spacing checks remain necessary. No generic uppercase or name-dictionary replacement is performed.",
        ],
        "acceptedEmployeeRows": 0,
        "mutatedSourceRowsOrFlags": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    payload = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
    output = REVIEWS / "independent-phsa-history-batches-confidence-diagnostic-001.json"
    if args.check:
        if output.read_bytes() != payload:
            raise ValueError("Frozen confidence diagnostic replay differs")
    else:
        with output.open("xb") as file:
            file.write(payload)
    print(json.dumps({"path": str(output.relative_to(ROOT)), "sha256": sha(output)}))


if __name__ == "__main__":
    main()
