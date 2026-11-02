#!/usr/bin/env python3
"""Read-only independent replay of PHSA holdout keys, provenance and pixels.

Does not open holdout candidate files or output names or monetary values.
Selection is reimplemented from the frozen policy/config and original evidence.
"""
import collections
import gzip
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "research/salaries/queue-completion-2026-11-01/phsa"
EVIDENCE = ROOT / "research/salaries/queue-completion-phsa/evidence"
FIELDS = {"name": 1, "remuneration": 3, "expenses": 4}
CONFIDENCE = {
    "name": {"tesseract-name-confidence-below-85", "rapid-name-confidence-below-0.98"},
    "remuneration": {"tesseract-pay-confidence-below-90", "rapid-pay-confidence-below-0.98"},
    "expenses": {"tesseract-expense-confidence-below-90", "rapid-expense-confidence-below-0.98"},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == ".gzip" else path.read_bytes())


def checked_pin(value):
    p = ROOT / value["path"]
    assert sha(p) == value["sha256"], str(p)
    return p


def normalized_name(value):
    return re.sub(r"\s*,\s*", ",", re.sub(r"\s+", " ", value).strip())


def guarded_name(value):
    punctuation = set(" ,.'-\u2018\u2019\u02bc\u2010\u2011\u2013\u2014")
    return (bool(re.search(r"(?:^|[\W_])I", value))
            or bool(re.search(r"I[Il]|lI|\bMc[Il]{1,2}", value))
            or any(not (c.isalpha() or c.isspace() or unicodedata.category(c).startswith("M")
                        or c in punctuation) for c in value))


def row_assessment(row, page, source, anchors):
    anchor = anchors[(source["id"], page["physicalPage"])]
    i = row["sourceRowOnPage"] - 1
    valid = (page["sourceSha256"] == source["sourceSha256"]
             and anchor[0] == source["sourceSha256"]
             and page["sourceImageSha256"] == anchor[1]["actualRenderedPngSha256FromPrimary"]
             and len(page["rows"]) == anchor[1]["remunerationInkBandCount"]
             and not page["dateTitleNeedsReview"] and not page["pageGeometryNeedsReview"]
             and 0 <= i < len(anchor[1]["rows"]))
    if valid:
        ar = anchor[1]["rows"][i]
        valid = (not ar["needsSourceGeometryReview"] and ar["nameInkPixels"] > 0
                 and ar["nameRowBox"][1] <= row["sourceNameBand"]["center"] < ar["nameRowBox"][3])
    t, r = row["tesseract"], row["rapidocr"]
    guarded = guarded_name(row["candidateRow"][1])
    corroborated, confidence_only, manual = [], [], []
    for field, index in FIELDS.items():
        flags = row["fieldConflicts"].get(field, [])
        hard = set(flags) - CONFIDENCE[field]
        agree = False
        if t is not None and r is not None:
            if field == "name":
                left, right = normalized_name(t["name"]), normalized_name(r["name"])
                agree = bool(left) and left == right == row["candidateRow"][index] and not guarded
            else:
                token = "pay" if field == "remuneration" else "expense"
                a, b, c = t[token], r[token], row["candidateRow"][index]
                agree = (a["kind"] == b["kind"] == "number"
                         and all(type(v) is int and v > 0 for v in (a["value"], b["value"], c))
                         and a["value"] == b["value"] == c)
                if field == "expenses":
                    glyph = row["expenseOriginalImage"]
                    agree = agree and not glyph["blank"] and not glyph["matchesSourceCalibratedDashGeometry"]
        good = valid and agree and not hard
        if good:
            corroborated.append(field)
            if flags:
                confidence_only.append(field)
        glyph = row["expenseOriginalImage"]
        legacy_source_dash = (field == "expenses" and valid and not flags
                              and not glyph["blank"] and glyph["matchesSourceCalibratedDashGeometry"]
                              and row["candidateRow"][4] is None
                              and not any(engine is not None and engine["expense"]["kind"] == "number"
                                          for engine in (t, r)))
        if not good and not legacy_source_dash:
            manual.append(field)
    return corroborated, confidence_only, manual


def run():
    config_path = AREA / "holdout-selection-config-001.json"
    config = read(config_path)
    inventory_path = checked_pin(config["sourceInventory"])
    inventory = read(inventory_path)["sources"]
    policy_path = checked_pin(config["policy"])
    policy = read(policy_path)
    index_path = checked_pin(policy["processingProfiles"])
    profiles = {p["sourceId"]: p for p in read(index_path)["sourceProfiles"]}
    raster_path = ROOT / "research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-history-all-pages-raster-pay-anchors.json.gzip"
    anchors = {}
    for s in read(raster_path)["sources"]:
        for p in s["pages"]:
            anchors[(s["sourceId"], p["physicalPage"])] = (s["sourceSha256"], p)
    reserved_rows = set()
    reservation_pins = []
    for p in sorted((AREA / "batches").glob("*.json")):
        if not re.fullmatch(r"phsa-\d{4}-\d{2}-batch-\d{3}\.json", p.name):
            continue
        batch = read(p)
        reservation_pins.append(pin(p))
        for row in batch["rows"]:
            reserved_rows.add((batch["sourceId"], row["physicalPage"], row["sourceRowOnPage"]))
    for p in sorted((AREA / "overlays").glob("*-first-table-image-overlay.json")):
        fixture = read(p)
        reservation_pins.append(pin(p))
        for row in fixture["overlays"]:
            reserved_rows.add((fixture["sourceId"], row["physicalPage"], row["sourceRowOnPage"]))
    for p in sorted(AREA.glob("supplemental-field-reservation-*.json")):
        reservation_pins.append(pin(p))
        for row in read(p)["reservations"]:
            reserved_rows.add((row["sourceId"], row["physicalPage"], row["sourceRowOnPage"]))
    results = []
    for source in inventory:
        packet_path = AREA / "holdouts" / (source["id"] + "-source-only.json")
        if not packet_path.exists():
            continue
        packet = read(packet_path)
        profile_path = checked_pin(profiles[source["id"]])
        profile = read(profile_path)
        assert source["sourceSha256"] == profile["sourceSha256"] == packet["sourceSha256"]
        assert sha(Path(source["cachePath"])) == source["sourceSha256"]
        assert packet["selectionConfiguration"] == pin(config_path)
        assert packet["fieldPolicy"] == pin(policy_path)
        paths = sorted(EVIDENCE.glob(source["id"] + "-rows-p*.json.gzip"))
        pages = [read(p) for p in paths]
        page_keys = [p["physicalPage"] for p in pages]
        assert len(page_keys) == len(set(page_keys)) == source["pdfPages"]
        assert set(page_keys) == set(range(1, source["pdfPages"] + 1))
        start = profile["firstSalaryPhysicalPage"]
        count = source["pdfPages"] - start + 1
        buckets = collections.defaultdict(list)
        by_key = {}
        for path, page in zip(paths, pages):
            assert page["sourceId"] == source["id"]
            assert [r["sourceRowOnPage"] for r in page["rows"]] == list(range(1, len(page["rows"]) + 1))
            for row in page["rows"]:
                key = (page["physicalPage"], row["sourceRowOnPage"])
                assert key not in by_key
                assert row["physicalPage"] == page["physicalPage"] == row["candidateRow"][5]
                by_key[key] = (path, page, row)
                if page["physicalPage"] == start or (source["id"], *key) in reserved_rows:
                    continue
                fields, confidence, manual = row_assessment(row, page, source, anchors)
                if manual or not fields:
                    continue
                third = min(2, (key[0] - start) * 3 // count)
                rank = hashlib.sha256(json.dumps([config["seed"], source["sourceSha256"], *key],
                                                  ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
                buckets[third].append((not bool(confidence), rank, key, fields))
        expected = []
        for third, number in enumerate((3, 4, 3)):
            expected.extend((third, item) for item in sorted(buckets[third])[:number])
        assert len(expected) == len(packet["rows"]) == 10
        actual_keys = [(r["physicalPage"], r["sourceRowOnPage"]) for r in packet["rows"]]
        assert len(set(actual_keys)) == 10
        assert actual_keys == [item[2] for _, item in expected]
        crop_count = 0
        for entry, (third, item) in zip(packet["rows"], expected):
            unflagged, rank, key, fields = item
            assert entry["reviewTargetFields"] == fields
            assert entry["selectionRankSha256"] == rank
            assert entry["salaryPageThird"] == ("early", "middle", "late")[third]
            assert entry["selectionClass"] == ("otherwise-unflagged-paired-row" if unflagged else "unreserved-confidence-only-paired-row")
            path, page, row = by_key[key]
            assert entry["pageEvidence"] == pin(path)
            checked_pin(entry["rawPageEvidence"])
            original = Path(entry["actualSourceImagePath"])
            assert sha(original) == entry["actualSourceImageSha256"] == page["sourceImageSha256"]
            image = Image.open(original).convert("RGB")
            context = Path(entry["fullRowContextPath"])
            assert sha(context) == entry["fullRowContextSha256"]
            assert ImageChops.difference(image.crop(entry["fullRowOriginalPixelBox"]), Image.open(context).convert("RGB")).getbbox() is None
            for view in entry["sourceNativeFieldViews"]:
                cp = checked_pin(view)
                assert view["field"] in fields
                expected_crop = image.crop(view["originalPdf300DpiPixelBox"])
                actual_crop = Image.open(cp).convert("RGB")
                assert actual_crop.size == expected_crop.size
                assert ImageChops.difference(expected_crop, actual_crop).getbbox() is None
                crop_count += 1
        results.append({"sourceId": source["id"], "packet": pin(packet_path),
                        "sourceSha256": source["sourceSha256"], "sourcePages": len(pages),
                        "sourceRows": sum(len(p["rows"]) for p in pages), "selectedRowKeys": actual_keys,
                        "holdoutRows": 10, "sourceThirdAllocation": [3, 4, 3],
                        "requestedFieldsAndExactSourcePixelCrops": crop_count,
                        "selectionClassCounts": dict(collections.Counter(r["selectionClass"] for r in packet["rows"])),
                        "allSelectionReservationProvenanceAndPixelAssertionsPass": True})
    return {"reviewer": "/root/recovery_review", "script": pin(Path(__file__).resolve()),
            "method": "Independently reimplemented source-only eligibility/rank selection; exact raw evidence/source/raster/crop provenance and pixel replay. No candidate holdout files opened or literal names/pay/expenses emitted.",
            "policy": pin(policy_path), "selectionConfig": pin(config_path), "inventory": pin(inventory_path),
            "processingProfileIndex": pin(index_path), "independentRasterLedger": pin(raster_path),
            "reservationInputPins": reservation_pins, "sources": results,
            "holdoutSourcesChecked": len(results), "holdoutRowsChecked": 10 * len(results),
            "allNineSourcesAvailable": len(results) == 9,
            "limits": ["This validates selection/provenance/pixels, not the literal source transcription of the requested fields.",
                       "Root's blind source transcription and exact comparison of all ninety rows remain mandatory before acceptance.",
                       "Final source control/field closure and qualified source cases are separate gates."],
            "sourceAcceptanceClaim": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
