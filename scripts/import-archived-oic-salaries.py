#!/usr/bin/env python3
"""Recover 2006/07–2017/18 OIC salary schedules from original Public Accounts PDFs.

Run from the repository root:
  python3 scripts/import-archived-oic-salaries.py --cache /tmp/pofbc-oic-processing --offline

Requires Poppler (pdftotext) and PyMuPDF. Each original PDF is pinned by hash,
page boundaries, row counts and published monetary controls. Poppler's raw text
and independently grouped MuPDF coordinates must agree on every source row.
Only enumerated review decisions may exclude a blank-payment or overlapping
deputy row. No salary threshold, approximate-name deduplication, or travel join
is applied to the recovered OIC data. All validation finishes before writes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "research/salaries/public-accounts-oic/reviewed-inputs.json"
MONEY_TOKEN = r"\(?-?(?:\d{1,3}(?:,\d{3})+|\d+)\)?|Nil"
MONEY = re.compile(r"(?<!\S)(" + MONEY_TOKEN + r")$", re.I)
FULL_MONEY = re.compile(MONEY_TOKEN, re.I)
TITLE = "Order–In–Council, Other Appointees and"
CONTINUED = "OIC and Other Appointees"
VISUAL_PAGES = {
    "2006-07": [15], "2007-08": [7, 22], "2008-09": [15],
    "2009-10": [29], "2010-11": [18], "2011-12": [13, 17, 28, 29],
    "2012-13": [15], "2013-14": [7, 15, 17, 19, 23, 24],
    "2014-15": [25], "2015-16": [12, 22], "2016-17": [12],
    "2017-18": [12, 14, 26],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def name_key(name: str) -> tuple[str, ...]:
    # Comparison only: preserve the published spelling in every output record.
    return tuple("".join(c for c in unicodedata.normalize("NFKC", part).casefold()
                         if c.isalnum()) for part in name.split(",", 1))


def amount(token: str) -> int | None:
    if not FULL_MONEY.fullmatch(token):
        raise ValueError(f"Invalid source amount: {token!r}")
    if token.casefold() == "nil":
        return None
    if token.startswith("(") != token.endswith(")"):
        raise ValueError(f"Unbalanced negative amount: {token!r}")
    if token.startswith("(-"):
        raise ValueError(f"Mixed negative amount syntax: {token!r}")
    if token.startswith("("):
        return -int(token[1:-1].replace(",", ""))
    return int(token.replace(",", ""))


def check_name(name: str) -> None:
    if "," not in name or not name.strip() or name != name.upper():
        raise ValueError(f"Unexpected published name layout: {name!r}")


def parse_raw_page(text: str, has_positions: bool) -> list[list]:
    """First reader: Poppler content-stream order, with strict row structure."""
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    currency_at = next((i for i, line in enumerate(lines) if line in ("$", "$ $")), None)
    if currency_at is None:
        raise ValueError("No OIC currency header")
    body = lines[currency_at + 1:]
    if has_positions:
        if len(body) % 2:
            raise ValueError("Truncated or unexpected name/position row")
        rows = []
        for name, position in zip(body[::2], body[1::2]):
            check_name(name)
            match = MONEY.search(position)
            rows.append([name, position[:match.start()].strip() if match else position,
                         amount(match[1]) if match else None])
        return rows
    rows = []
    for line in body:
        match = MONEY.search(line)
        if not match:
            raise ValueError(f"Truncated name/pay row: {line!r}")
        name = line[:match.start()].strip()
        check_name(name)
        rows.append([name, None, amount(match[1])])
    return rows


def coordinate_lines(words: list[tuple]) -> list[list[tuple]]:
    groups = []
    for word in sorted(words, key=lambda w: (round(w[1], 1), w[0])):
        if not groups or abs(word[1] - groups[-1][0][1]) > 2:
            groups.append([word])
        else:
            groups[-1].append(word)
    return [sorted(group, key=lambda w: w[0]) for group in groups]


def parse_coordinate_page(page, has_positions: bool) -> list[list]:
    """Second reader: MuPDF coordinates; pay is read only from its column.

    Alternating pages in 2015/16 and 2016/17 shift the two table columns.
    Deriving the gutter from the dollar headings avoids merging those columns.
    """
    words = page.get_text("words")
    dollars = sorted((w for w in words if w[4] == "$"), key=lambda w: w[0])
    if len(dollars) not in (1, 2):
        raise ValueError("Unexpected OIC currency-column count")
    body = [w for w in words if w[1] > max(w[3] for w in dollars) - 1]
    if not body:
        raise ValueError("Empty source table page")
    split = (min(w[0] for w in body) + dollars[1][0] - dollars[0][0] - 2
             if len(dollars) == 2 else page.rect.width)
    rows = []
    for side, dollar in enumerate(dollars):
        column = [w for w in body if (w[0] >= split) == bool(side)]
        if not column:
            continue
        lines = coordinate_lines(column)
        if has_positions and len(lines) % 2:
            raise ValueError("Positioned source has an unmatched name or title line")
        step = 2 if has_positions else 1
        for at in range(0, len(lines), step):
            label_words = lines[at]
            value_words = lines[at + 1] if has_positions else label_words
            pay_words = [w for w in value_words if w[0] >= dollar[0] - 30
                         and FULL_MONEY.fullmatch(w[4])]
            if len(pay_words) > 1 or (not has_positions and len(pay_words) != 1):
                raise ValueError("Unexpected positioned remuneration cell")
            if has_positions:
                name = " ".join(w[4] for w in label_words)
                position = " ".join(w[4] for w in value_words if w not in pay_words)
                if min(w[0] for w in value_words) <= min(w[0] for w in label_words) + 2:
                    raise ValueError("Position line does not have the source's indentation")
            else:
                name = " ".join(w[4] for w in label_words if w not in pay_words)
                position = None
            check_name(name)
            rows.append([name, position, amount(pay_words[0][4]) if pay_words else None])
    return rows


def read_pdf(control: dict, cache: Path, offline: bool) -> tuple[Path, bytes]:
    path = cache / (control["slug"] + ".pdf")
    if not path.exists():
        if offline:
            raise ValueError(f"Missing original PDF: {path}")
        request = urllib.request.Request(control["sourceUrl"], headers={
            "User-Agent": "PofBC salary-source importer"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        if not raw.startswith(b"%PDF"):
            raise ValueError(f"Source did not return a PDF: {control['sourceUrl']}")
        path.write_bytes(raw)
    raw = path.read_bytes()
    if sha256(raw) != control["sha256"] or len(raw) != control["sourceBytes"]:
        raise ValueError(f"{control['year']}: original PDF changed; review required")
    return path, raw


def verify_source(control: dict, path: Path) -> tuple[list[list], dict]:
    first, last = control["firstPhysicalPage"], control["lastPhysicalPage"]
    raw = subprocess.check_output(["pdftotext", "-raw", "-f", str(first), "-l", str(last),
                                   str(path), "-"], text=True)
    pages = raw.split("\f")
    if pages[-1].strip() == "":
        pages.pop()
    if len(pages) != last - first + 1:
        raise ValueError("Poppler returned an unexpected number of source pages")
    rows, per_page, secondary = [], {}, []
    with fitz.open(path) as doc:
        if len(doc) != control["pdfPageCount"]:
            raise ValueError("Original PDF page count changed")
        for number, text in enumerate(pages, first):
            expected_heading = TITLE if number == first else CONTINUED
            if expected_heading not in text or control["year"] not in text:
                raise ValueError(f"{control['year']} page {number}: wrong schedule or period")
            if number == first and f"March 31, {control['periodEndYear']}" not in text:
                raise ValueError("OIC fiscal-year-end heading mismatch")
            primary = parse_raw_page(text, control["hasPositions"])
            positioned = parse_coordinate_page(doc[number - 1], control["hasPositions"])
            if primary != positioned:
                raise ValueError(f"{control['year']} page {number}: independent readers disagree")
            printed = [w[4] for w in doc[number - 1].get_text("words")
                       if w[1] < 70 and w[4].isdigit()]
            if printed != [str(control["printedPageByPhysicalPage"][str(number)])]:
                raise ValueError("Printed/physical PDF page mapping changed")
            rows.extend([*row, number] for row in primary)
            secondary.extend([*row, number] for row in positioned)
            per_page[str(number)] = len(primary)
        following = [i + 1 for i in range(last, min(last + 4, len(doc)))
                     if re.search(r"Other Employees\s+Salary for the Fiscal", doc[i].get_text())]
        if not following:
            raise ValueError("Following Other Employees boundary not confirmed")
        summary = doc[control["summaryPhysicalPage"] - 1].get_text()
        if control["slug"] != "2013-14":
            expected = f"{control['summaryRemunerationThousands']:,}"
            if expected not in summary:
                raise ValueError("Published summary control changed")
        elif summary.strip():
            raise ValueError("2013/14 summary was reviewed as an image; source layout changed")
    if per_page != control["rowsPerPhysicalPage"] or len(rows) != control["publishedRowCount"]:
        raise ValueError("Published row counts changed")
    paid = [r for r in rows if r[2] is not None]
    total = sum(r[2] for r in paid)
    if len(paid) != control["publishedPaidRowCount"] or total != control["publishedRemuneration"]:
        raise ValueError("Published payment controls changed")
    nil = [dict(name=r[0], position=r[1], physicalPdfPage=r[3]) for r in rows if r[2] is None]
    if nil != control["expectedNilRows"]:
        raise ValueError("Unexpected blank payment; inspect the original printed cell")
    residual = total - control["summaryRemunerationThousands"] * 1000
    rounding_bound = 500 + len(paid) / 2
    if abs(residual) > rounding_bound:
        exception = control.get("summaryException", {})
        if not exception.get("reviewed") or exception.get("residualDollars") != residual:
            raise ValueError("Unreviewed source summary discrepancy")
    return rows, {
        "physicalPdfPages": [first, last], "printedPageByPhysicalPage": control["printedPageByPhysicalPage"],
        "rowsPerPhysicalPage": per_page, "followingOtherEmployeesPhysicalPage": following[0],
        "sourceRowCount": len(rows), "sourcePaidRowCount": len(paid),
        "sourceRemunerationSum": total,
        "independentExtraction": {"primary": "Poppler pdftotext -raw content-stream row parsing",
            "secondary": "MuPDF coordinate grouping with independent remuneration-column selection",
            "allRowsAgree": True, "comparedRows": len(rows), "pageCount": last - first + 1,
            "primaryRowsSha256": sha256(encoded(rows)), "secondaryRowsSha256": sha256(encoded(secondary))},
        "summaryControl": {"physicalPdfPage": control["summaryPhysicalPage"],
            "printedThousands": control["summaryRemunerationThousands"], "residualDollars": residual,
            "exactReconciliation": False, "simpleRoundingBoundDollars": rounding_bound,
            "withinSimpleRoundingBound": abs(residual) <= rounding_bound,
            "method": control["summaryExtraction"],
            "exception": control.get("summaryException")},
        "blankPaymentRowsExcluded": nil,
        "visualReview": {"physicalPages": VISUAL_PAGES[control["slug"]],
            "scope": "Selected headers, boundaries, column shifts, blank/negative cells and overlap evidence; every other source row is checked by the two independent PDF extraction paths."},
    }


def reviewed_rows(rows: list[list], control: dict, existing: dict) -> tuple[list[list], list[dict]]:
    """Apply only the enumerated source-level table preferences, with guards."""
    decisions = control["reviewedDuplicatePaymentExclusions"]
    by_key = {(d["name"], d["position"], d["remuneration"], d["physicalPdfPage"]): d for d in decisions}
    if len(by_key) != len(decisions):
        raise ValueError("Duplicate review decision")
    used, accepted = set(), []
    for row in rows:
        if row[2] is None:
            continue
        key = tuple(row)
        decision = by_key.get(key)
        if decision:
            expected = ["public-service", decision["retainedName"],
                        "Deputy Minister or Associate Deputy Minister", decision["retainedRemuneration"],
                        decision["retainedExpenses"]]
            if existing[decision["retainedSourceId"]].count(expected) != 1:
                raise ValueError("Reviewed retained deputy payment no longer matches")
            used.add(key)
        else:
            accepted.append(["public-service", row[0], row[1], row[2], None, row[3]])
    if used != set(by_key):
        raise ValueError("A reviewed duplicate exclusion is no longer present")
    old_pairs = {(name_key(row[1]), row[3]) for group in existing.values() for row in group}
    if any((name_key(row[1]), row[3]) in old_pairs for row in accepted):
        raise ValueError("Unreviewed cross-schedule name/pay overlap")
    return accepted, decisions


def verify_deputy_pdf(path: Path, expected: list[list]) -> dict:
    """The 2011/12 specialized deputy table corroborates all retained records."""
    with fitz.open(path) as doc:
        page = doc[12]
        if "Deputy Ministers and" not in page.get_text() or "2011/12" not in page.get_text():
            raise ValueError("Wrong specialized deputy table")
        groups = coordinate_lines([w for w in page.get_text("words") if w[0] >= 330 and 197 < w[1] < 650])
    rows = []
    for group in groups:
        names = [w[4] for w in group if w[0] < 480]
        pay = [w[4] for w in group if 480 <= w[0] < 535]
        travel = [w[4] for w in group if w[0] >= 535]
        if not pay:
            if not rows or not names or "," in " ".join(names):
                raise ValueError("Unexpected wrapped deputy name")
            rows[-1][0] += " " + " ".join(names)
        else:
            if len(pay) != 1 or len(travel) > 1:
                raise ValueError("Unexpected deputy monetary columns")
            rows.append([" ".join(names), amount(pay[0]), amount(travel[0]) if travel else None])
    observed = Counter((name_key(r[0]), r[1], r[2]) for r in rows)
    comparison = Counter((name_key(r[1]), r[3], r[4]) for r in expected)
    if observed != comparison or len(rows) != 45:
        raise ValueError("Retained 2011/12 deputy rows differ from the original PDF")
    if sum(r[1] for r in rows) != 8396127 or sum(r[2] or 0 for r in rows) != 828501:
        raise ValueError("Original deputy PDF subtotals do not reconcile")
    return {"physicalPdfPage": 13, "rowCount": len(rows), "allRetainedRowsAgree": True,
            "remunerationSubtotal": 8396127, "travelSubtotal": 828501,
            "printedSubtotalsReconcileExactly": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-oic-processing"))
    parser.add_argument("--output", type=Path, default=INPUTS.parent)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    inputs = json.loads(INPUTS.read_text())
    base = ROOT / "research/salaries/public-accounts"
    existing_manifest = json.loads((base / "sources.json").read_text())
    existing_all = {s["id"]: json.loads(gzip.decompress((base / s["file"]).read_bytes()))
                    for s in existing_manifest["sources"] if s.get("file")}
    outputs, sources, evidence = {}, [], []
    for control in inputs["sources"]:
        control = {**control, "periodEndYear": int(control["year"][:4]) + 1}
        path, raw = read_pdf(control, args.cache, args.offline)
        rows, validation = verify_source(control, path)
        existing = {key: value for key, value in existing_all.items()
                    if key.startswith("public-accounts-" + control["slug"] + "-")}
        existing_names = defaultdict(list)
        for key, group in existing.items():
            for old in group:
                existing_names[name_key(old[1])].append((key, old))
        accepted, exclusions = reviewed_rows(rows, control, existing)
        validation["reviewedDuplicatePaymentExclusions"] = exclusions
        if exclusions:
            validation["retainedDeputyPdfVerification"] = verify_deputy_pdf(
                path, existing["public-accounts-2011-12-deputy-ministers"])
        filename = control["slug"] + ".json.gzip"
        normalized = encoded(accepted)
        compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
        outputs[filename] = compressed
        notes = ["OIC/appointee salary payments, including amounts below $75,000. No $75,000 filter applies to this schedule.",
                 "Amounts may include base salary, retroactive pay, benefits from prior years and current-year vacation payouts; they are not annual salary rates.",
                 "Travel is published separately and is not attributed to these recovered OIC records. Missing expenses do not mean zero.",
                 "Source names and positions are retained as published, with whitespace collapsed. Initials are not expanded."]
        if not control["hasPositions"]:
            notes.append("This source publishes names and salary amounts without positions; no position is inferred.")
        if control["expectedNilRows"]:
            notes.append("Named appointments with a blank remuneration cell remain in the review evidence and are excluded from paid records; blank is not zero.")
        if exclusions:
            notes.append("All 45 specialized deputy-table records also appear in this year's OIC table. The explicitly reviewed OIC overlaps are excluded; the deputy compensation and directly reported travel remain once. Four published amounts differ by $1; the specialized deputy table is retained without altering either source in the evidence.")
        if control.get("summaryException"):
            notes.append(control["summaryException"]["reason"])
        if control["slug"] == "2013-14":
            notes.append("This year's OIC table has no judge-titled rows, unlike adjacent years. The published composition is retained; no workforce-comparability claim is made.")
        if any(r[3] < 0 for r in accepted):
            notes.append("Negative remuneration is preserved exactly as printed; it may represent a recovery.")
        source = {
            "id": "public-accounts-oic-" + control["slug"], "employerSlug": "public-service",
            "employerName": "Provincial government", "sector": "Government", "year": control["year"],
            "slug": control["slug"], "periodType": "fiscal", "file": filename,
            "title": f"Public Accounts {control['year']}: OIC, other appointees and employees not appointed under the Public Service Act",
            "sourceUrl": control["sourceUrl"], "originalUrl": control["originalUrl"],
            "archiveUrl": control["archiveUrl"], "sha256": sha256(raw), "sourceBytes": len(raw),
            "pdfPageCount": control["pdfPageCount"], "normalizedSha256": sha256(normalized),
            "dataSha256": sha256(compressed), "periodStart": control["year"][:4] + "-04-01",
            "periodEnd": str(control["periodEndYear"]) + "-03-31", "currency": "CAD",
            "scope": "appointee-remuneration", "category": "appointee-remuneration",
            "scopeDescription": "Order-in-Council, other appointees and employees not appointed under the Public Service Act; no $75,000 threshold",
            "threshold": None, "rowCount": len(accepted), "totalRemuneration": sum(r[3] for r in accepted),
            "totalDisclosedExpenses": 0, "expensesNote": notes[2], "status": "verified",
            "verifiedOn": inputs["verifiedOn"], "validation": validation, "notes": notes,
        }
        sources.append(source)
        evidence.append({"sourceId": source["id"], "sourceSha256": source["sha256"],
                         "publishedRowSchema": ["name", "position", "remuneration", "pdfPage"],
                         "publishedRows": rows, "acceptedRows": len(accepted),
                         "crossScheduleNameOverlaps": [
                             {"name": row[1], "pay": row[3], "existingSourceId": key,
                              "existingName": old[1], "existingPay": old[3], "existingExpenses": old[4]}
                             for row in accepted for key, old in existing_names[name_key(row[1])]],
                         "validation": validation})
        print(f"{control['year']}: {len(rows):,} source rows; {len(accepted):,} accepted payments; "
              f"{len(exclusions)} reviewed deputy overlaps", flush=True)
    registry = {"version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
                "sources": sources, "invalidatedTravelJoins": inputs["invalidatedTravelJoins"],
                "coverageNotes": [
                    "Recovers the 12 missing OIC/appointee cohorts from original reports, separately from the ordinary-employee and deputy schedules.",
                    "The erroneous DataBC OIC CSV resources remain excluded; these PDFs supply distinct original evidence.",
                    "This collection adds records to existing public-service fiscal years; it is not a replacement for the employee cohort.",
                    "The 2007/08 source table has a disclosed unexplained $1,244 residual against its thousands-rounded summary; exact reconciliation is not claimed.",
                    "Cross-schedule preferences and invalidated travel joins are explicit guarded decisions, not generic person-identity matching rules."]}
    outputs["sources.json"] = (json.dumps(registry, ensure_ascii=False, indent=2) + "\n").encode()
    outputs["review/source-extraction.json.gzip"] = gzip.compress(encoded(evidence), compresslevel=9, mtime=0)
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, data in outputs.items():
        destination = args.output / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    print(f"Validated {len(sources)} source schedules and {sum(s['rowCount'] for s in sources):,} accepted payments.")


if __name__ == "__main__":
    main()
