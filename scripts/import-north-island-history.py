#!/usr/bin/env python3
"""Recover five reviewed North Island College employee remuneration schedules.

Poppler layout text is checked against every positioned name/title/payment cell
from PyMuPDF. Source fingerprints, period headings, complete page counts and
printed controls are locked. The salary build itself only needs the committed
normalized data. No SunshineLists data is copied by this importer.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
EMPLOYER = "north-island-college"
INDEX_URL = "https://www.nic.bc.ca/about/leadership-and-governance/institutional-reporting.html"
BASE_URL = "https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-"
SCHEMA = ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"]
REVIEWED = {
    "2018-19": {
        "sha256": "8042d90554896de2c310d93bde9f4247757f092213b6038398e1a365257711b0",
        "pdfPages": 42, "pages": [7, 8, 9, 10, 11], "pageCounts": [18, 37, 36, 34, 8],
        "sums": [12415381, 578000], "controls": [12415391, 577995],
        "board": [20355, 18576], "below": [14923244, 436452], "grand": [27358990, 1033023],
        "positionBoundary": 200, "boundaryCorrections": 0,
        "approvalPage": 2, "approvalDate": "2019-09-27", "visualPages": [2, 3, 7, 11],
    },
    "2021-22": {
        "sha256": "90fedb56a99c010064a67db18370578ecd6e33326bac04998b2d5458a3740afd",
        "pdfPages": 17, "pages": [7, 8, 9, 10, 11], "pageCounts": [19, 38, 38, 38, 5],
        "sums": [13907610, 154386], "controls": [13907610, 154386],
        "board": [16748, 5655], "below": [15358062, 370499], "grand": [29282420, 530540],
        "positionBoundary": 212, "boundaryCorrections": 1,
        "approvalPage": 3, "approvalDate": "2022-10-06", "visualPages": [3, 7, 10, 11],
    },
    "2022-23": {
        "sha256": "08b65aa51ae42b99125ffcbd5d59d27331ab775d989795051032197ea12bbcff",
        "pdfPages": 41, "pages": [7, 8, 9, 10, 11], "pageCounts": [20, 39, 38, 39, 20],
        "sums": [16201622, 567333], "controls": [16201622, 567333],
        "board": [24625, 10414], "below": [16331780, 376056], "grand": [32558027, 953803],
        "positionBoundary": 200, "boundaryCorrections": 1,
        "approvalPage": 3, "approvalDate": "2023-09-28", "visualPages": [3, 7, 10, 11],
    },
    "2023-24": {
        "sha256": "598caa417c3963e40a48af17d05ab860c02ae75cc901727ad092fa5ca98e762a",
        "pdfPages": 20, "pages": [8, 9, 10, 11, 12, 13], "pageCounts": [18, 37, 36, 37, 37, 16],
        "sums": [20146497, 760596], "controls": [20146497, 760596],
        "board": [21691, 30135], "below": [16696027, 607319], "grand": [36864215, 1398050],
        "positionBoundary": 212, "boundaryCorrections": 1,
        "approvalPage": 3, "approvalDate": "2024-10-03", "visualPages": [3, 8, 11, 13],
    },
    "2024-25": {
        "sha256": "13ba3ce3742b8487ffedb14a945f340eaf09f27d9f94bbe084d9162546445b8e",
        "pdfPages": 17, "pages": [6, 7, 8, 9, 10, 11], "pageCounts": [22, 40, 40, 40, 40, 18],
        "sums": [22139569, 923737], "controls": [22139569, 923737],
        "board": [22500, 13072], "below": [16716932, 607319], "grand": [38879001, 1544128],
        "positionBoundary": None, "boundaryCorrections": 0,
        "approvalPage": 3, "approvalDate": "2025-10-02", "visualPages": [3, 6, 11],
    },
}
MONEY = r"(?:\d{1,3}(?:,\d{3})*|0)"
ROW = re.compile(rf"^\s*(.+?)\s{{2,}}({MONEY})\s+({MONEY}|-)\s*$")
PAIR = re.compile(rf"^\s*({MONEY})\s+({MONEY})\s*$")
ABUTTING = "Paquet-Combe, Marie-FranceInst, Health Care Assistant"
SPLIT_NAME = "Paquet-Combe, Marie-France"
SPLIT_POSITION = "Inst, Health Care Assistant"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def amount(value: str) -> int | None:
    if value == "-":
        return None
    if not re.fullmatch(MONEY, value):
        raise ValueError(f"Unexpected monetary token: {value!r}")
    return int(value.replace(",", ""))


def parse_employee(line: str, page: int, period: str) -> tuple[list, bool]:
    match = ROW.fullmatch(line)
    if not match:
        raise ValueError(f"Unparsed employee line on PDF page {page}: {line!r}")
    label, pay, expense = match.groups()
    corrected = ABUTTING in label
    if corrected:
        if period not in ("2021-22", "2022-23", "2023-24") or label != ABUTTING:
            raise ValueError("Unreviewed name/position boundary")
        label = SPLIT_NAME + "  " + SPLIT_POSITION
    fields = re.split(r"\s{2,}", label.strip())
    expected = 1 if REVIEWED[period]["positionBoundary"] is None else 2
    if len(fields) != expected or "," not in fields[0]:
        raise ValueError(f"Unexpected name/position columns on page {page}: {fields!r}")
    remuneration = amount(pay)
    if remuneration is None or remuneration <= 75000:
        raise ValueError("Employee remuneration fails the source's >$75,000 threshold")
    return [EMPLOYER, fields[0], fields[1] if expected == 2 else None,
            remuneration, amount(expense), page], corrected


def parse_layout(text: str, period: str) -> tuple[list, dict]:
    reviewed = REVIEWED[period]
    fiscal_end = int(period[:4]) + 1
    pages = text.split("\f")
    if pages[-1].strip() or len(pages) - 1 != reviewed["pdfPages"] or "\ufffd" in text:
        raise ValueError("Changed/incomplete PDF text or page boundaries")
    rows, found_pages, page_counts, controls, board_controls = [], [], [], [], []
    corrections, below, grand = [], [], []
    for number, page in enumerate(pages[:-1], 1):
        if "SCHEDULE OF EMPLOYEE REMUNERATION AND EXPENSES" not in page or not re.search(r"B\.\s+Other Employees", page):
            continue
        if not re.search(rf"FOR (?:THE )?YEAR ENDED MARCH 31, {fiscal_end}\b", page):
            raise ValueError(f"Conflicting employee reporting period on PDF page {number}")
        found_pages.append(number)
        before = len(rows)
        active = False
        closed = False
        for line in page.splitlines():
            stripped = line.strip()
            if re.match(r"B\.\s+Other Employees > \$75,000", stripped):
                if active or closed:
                    raise ValueError("Duplicate employee section marker")
                active = True
                continue
            if re.match(r"C\.\s+Other Employees < \$75,000", stripped):
                active, closed = False, True
                continue
            pair = PAIR.fullmatch(line)
            if not active:
                if pair and not closed:
                    board_controls.append([amount(v) for v in pair.groups()])
                if closed and "Consolidated Remuneration / Expenses < $75,000" in line:
                    tokens = line.split()
                    below.append([amount(v) for v in tokens[-2:]])
                if closed and (stripped.startswith("TOTAL ") or (pair and period == "2018-19")):
                    tokens = line.replace("$", "").split()
                    grand.append([amount(v) for v in tokens[-2:]])
                continue
            if (not stripped or stripped.startswith("Name ") or
                    "Schedule of Employee Remuneration and Expenses - FIR" in line or
                    re.fullmatch(r"Page \d+ of \d+", stripped)):
                continue
            if pair:
                controls.append([amount(v) for v in pair.groups()])
                continue
            row, corrected = parse_employee(line, number, period)
            rows.append(row)
            if corrected:
                corrections.append({"pdfPage": number, "name": SPLIT_NAME,
                    "position": SPLIT_POSITION,
                    "reason": "Rendered source shows the adjacent name/title columns touching. Only the column boundary is restored; no source letters or amounts changed."})
        page_counts.append(len(rows) - before)
    sums = [sum(r[3] for r in rows), sum(r[4] for r in rows if r[4] is not None)]
    if found_pages != reviewed["pages"] or page_counts != reviewed["pageCounts"]:
        raise ValueError(f"Changed/incomplete employee section: {found_pages}, {page_counts}")
    if controls != [reviewed["controls"]] or sums != reviewed["sums"]:
        raise ValueError(f"Changed named rows or printed controls: {sums}, {controls}")
    if board_controls != [reviewed["board"]] or below != [reviewed["below"]] or grand != [reviewed["grand"]]:
        raise ValueError(f"Changed excluded aggregate controls: {board_controls}, {below}, {grand}")
    if [sum(v[i] for v in (board_controls[0], controls[0], below[0])) for i in (0, 1)] != grand[0]:
        raise ValueError("Printed board, named and under-threshold controls do not reconcile")
    if len(corrections) != reviewed["boundaryCorrections"]:
        raise ValueError("Unexpected reviewed layout-boundary correction count")
    if len(set(tuple(r[:5]) for r in rows)) != len(rows):
        raise ValueError("Unexpected duplicate employee observations require review")
    residuals = [sums[i] - controls[0][i] for i in (0, 1)]
    return rows, {
        "sourceFingerprintLocked": True, "completeEmployeeSchedule": True,
        "internalFiscalYearEnd": fiscal_end,
        "rowCountsByPdfPage": dict(zip(found_pages, page_counts)),
        "physicalPdfPages": [found_pages[0], found_pages[-1]],
        "namedRemunerationSum": sums[0], "namedExpensesSum": sums[1],
        "publishedNamedRemuneration": controls[0][0], "publishedNamedExpenses": controls[0][1],
        "remunerationResidual": residuals[0], "expensesResidual": residuals[1],
        "summaryTotalReconciled": residuals == [0, 0], "residualCause": None,
        "printedSubtotalsReconcileToGrandTotal": True,
        "expenseDashesRetainedAsMissing": sum(r[4] is None for r in rows),
        "explicitZeroExpenseRows": sum(r[4] == 0 for r in rows),
        "layoutCorrections": corrections, "unparsedEmployeeLines": 0,
    }


def independent_coordinate_check(pdf_path: Path, rows: list, period: str) -> int:
    """Read every original field with an independent PDF engine and column geometry."""
    import fitz

    reviewed = REVIEWED[period]
    checked = 0
    with fitz.open(pdf_path) as document:
        if len(document) != reviewed["pdfPages"]:
            raise ValueError("Independent PDF page count differs")
        for number in reviewed["pages"]:
            page = document[number - 1]
            words = page.get_text("words")
            begin = [w[1] for w in words if w[4] == "B." and w[0] < 100]
            if not begin:
                raise ValueError("Independent employee-section marker missing")
            begin.sort()
            end = min((w[1] for w in words if w[4] == "C." and w[0] < 100 and w[1] > begin[0]), default=10000)
            if any(y < end for y in begin[1:]):
                raise ValueError("Independent employee-section marker ambiguous")
            anchors = sorted((w for w in words if w[0] > 390 and w[2] < 480 and
                re.fullmatch(MONEY, w[4]) and 75000 < int(w[4].replace(",", "")) < 1000000
                and begin[0] < w[1] < end), key=lambda w: w[1])
            expected = [r for r in rows if r[5] == number]
            if len(anchors) != len(expected):
                raise ValueError(f"Independent employee count differs on PDF page {number}")
            for anchor, row in zip(anchors, expected):
                line = sorted((w for w in words if abs(w[1] - anchor[1]) < 3), key=lambda w: w[0])
                left = [w for w in line if w[2] < anchor[0] - 3]
                expense = [w[4] for w in line if w[0] > anchor[2] + 2]
                boundary = reviewed["positionBoundary"]
                if len(expense) != 1:
                    raise ValueError(f"Independent expense cell ambiguous on PDF page {number}")
                if row[1] == SPLIT_NAME and reviewed["boundaryCorrections"]:
                    label = " ".join(w[4] for w in left)
                    if label != ABUTTING or row[2] != SPLIT_POSITION:
                        raise ValueError("Independent reader conflicts at the reviewed touching columns")
                    name, position = SPLIT_NAME, SPLIT_POSITION
                else:
                    name = " ".join(w[4] for w in left if boundary is None or w[0] < boundary)
                    position = " ".join(w[4] for w in left if boundary is not None and w[0] >= boundary) or None
                actual = [EMPLOYER, name, position, amount(anchor[4]), amount(expense[0]), number]
                if actual != row:
                    raise ValueError(f"Independent field conflict on PDF page {number}: {actual!r} != {row!r}")
                checked += 1
            # The named subtotal lies below the last employee and above section C.
            if number == reviewed["pages"][-1]:
                candidates = [w for w in words if w[0] > 390 and re.fullmatch(MONEY, w[4])
                              and anchors[-1][1] + 3 < w[1] < end]
                if [amount(w[4]) for w in sorted(candidates, key=lambda w: w[0])] != reviewed["controls"]:
                    raise ValueError("Independent printed named controls differ")
    if checked != len(rows):
        raise ValueError("Independent reader did not cover every employee")
    return checked


def build_source(period: str, rows: list, validation: dict, pdf_bytes: bytes, verified_on: str) -> tuple[dict, bytes]:
    reviewed = REVIEWED[period]
    normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
    start = int(period[:4])
    validation.update({
        "allNamesTitlesAndMonetaryCellsIndependentlyVerified": True,
        "independentMethod": "Poppler pdftotext -layout rows compared with every PyMuPDF positioned name/title/remuneration/expense cell and the named subtotal. Three touching-column boundaries were separately rendered and reviewed.",
        "approvalPdfPages": [reviewed["approvalPage"]], "signedApprovalDate": reviewed["approvalDate"],
        "approvalVisuallyVerified": True, "visualReviewPdfPages": reviewed["visualPages"],
        "visualReview": "Rendered approval, first/final employee pages and the three touching-column cases reviewed. All employee cells checked independently by two PDF engines.",
    })
    source = {
        "id": f"north-island-college-sofi-{period}-employees", "employerSlug": EMPLOYER,
        "employerName": "North Island College", "sector": "Colleges",
        "year": period.replace("-", "/"), "slug": period, "file": f"{period}.json.gzip",
        "title": f"North Island College Statement of Financial Information {period.replace('-', '/')}: employee remuneration and expenses",
        "sourceUrl": BASE_URL + period + ".pdf", "sourceIndexUrl": INDEX_URL,
        "sourceKind": "official-pdf", "periodType": "fiscal",
        "sha256": sha256(pdf_bytes), "dataSha256": sha256(compressed), "normalizedSha256": sha256(normalized),
        "periodStart": f"{start}-04-01", "periodEnd": f"{start + 1}-03-31",
        "category": "employee-remuneration", "scope": "named-employees-over-threshold",
        "scopeDescription": "Complete named employee schedule above $75,000; board, supplier and aggregate schedules excluded.",
        "threshold": 75000, "thresholdRule": "over", "currency": "CAD", "amountPrecision": "whole-dollars",
        "nameDisclosure": "published-full-name", "positionDisclosure": "not-published" if reviewed["positionBoundary"] is None else "published",
        "rowCount": len(rows), "totalRemuneration": reviewed["sums"][0],
        "totalExpenses": reviewed["sums"][1], "totalDisclosedExpenses": reviewed["sums"][1],
        "pages": reviewed["pages"], "status": "verified", "verifiedOn": verified_on,
        "validation": validation,
        "excludedAggregates": {
            "boardRemuneration": reviewed["board"][0], "boardExpenses": reviewed["board"][1],
            "belowThresholdRemuneration": reviewed["below"][0], "belowThresholdExpenses": reviewed["below"][1],
            "grandTotalRemuneration": reviewed["grand"][0], "grandTotalExpenses": reviewed["grand"][1],
        },
        "notes": [
            "Only the complete section B named-employee schedule is imported. Board, suppliers and below-threshold aggregates do not become employee observations.",
            "Published dash expense cells remain missing, distinct from explicit numeric zero. Full names and any disclosed job titles are observations, not verified cross-year identities.",
            "Fiscal dates come from the actual employee schedule. The public website incorrectly sends its 2020/21 link to the 2019/20 scan; this collection does not reimport the separately accepted 2020/21 source.",
            "The 2024/25 employee section does not publish job titles; titles from earlier years or board rows are not substituted.",
        ],
    }
    if period == "2018-19":
        source["publicWarning"] = "The published 133 employee rows total $12,415,381 remuneration and $578,000 expenses: $10 below and $5 above the printed named subtotals, respectively. Both PDF readers agree on every displayed cell. The cause is unconfirmed; no amount has been adjusted to force agreement."
        source["notes"].append(source["publicWarning"])
    return source, compressed


def baseline_comparison(rows: list) -> dict:
    baseline_path = ROOT / "research/salaries/compiled-baseline.json.gzip"
    raw = baseline_path.read_bytes()
    baseline = json.loads(gzip.decompress(raw))
    employer = next(e for e in baseline["employers"] if e["slug"] == EMPLOYER)
    old = [r for r in employer["rows"] if baseline["years"][r[4]] == "2023/24"]
    norm = lambda name: "".join(c for c in name.casefold() if c.isalnum())
    # The comparison treats compiled zero versus a source dash as equivalent only
    # for overlap evidence. Accepted source data retains each dash as null.
    old_keys = Counter((norm(r[0]), r[2], r[3] or 0) for r in old)
    new_keys = Counter((norm(r[1]), r[3], r[4] or 0) for r in rows)
    by_payment = {}
    for r in rows:
        by_payment.setdefault((r[3], r[4] or 0), []).append(r)
    mismatches = []
    for row in old:
        if (norm(row[0]), row[2], row[3] or 0) not in new_keys:
            matches = by_payment.get((row[2], row[3] or 0), [])
            mismatches.append({"compiledName": row[0], "compiledPosition": row[1],
                "remuneration": row[2], "compiledExpenses": row[3],
                "samePaymentSourceCandidates": [{"name": r[1], "position": r[2], "expenses": r[4], "pdfPage": r[5]} for r in matches]})
    old_payments = Counter((r[2], r[3] or 0) for r in old)
    new_payments = Counter((r[3], r[4] or 0) for r in rows)
    if len(old) != 181 or old_payments != new_payments:
        raise ValueError("Reviewed compiled-period payment comparison changed")
    return {"baselineFile": str(baseline_path.relative_to(ROOT)), "baselineSha256": sha256(raw),
        "employerSlug": EMPLOYER, "compiledLabel": "2023/24", "officialPeriod": "2023/24",
        "compiledRows": len(old), "officialRows": len(rows),
        "exactNormalizedNamePayExpenseMatches": sum((old_keys & new_keys).values()),
        "paymentMultisetMatches": True, "unmatchedCompiledNameRows": mismatches,
        "decision": "Replace the complete same-period compiled employee partition with the complete verified official schedule under the existing builder rules. No cross-period or approximate person matching is used.",
        "comparisonLimitations": ["Payment-only equality does not establish person identity. Names/title boundaries are taken from the official source.",
            "Compiled zero versus official dash is equated only for this overlap comparison; official expenses remain null where disclosed as a dash."]}


def existing_publication(rows: list, source: dict) -> dict:
    """Keep the independently identical 2024/25 cohort published by PR #34 once."""
    collection = "continuation-education/supplemental"
    folder = ROOT / "research/salaries" / collection
    manifest = json.loads((folder / "sources.json").read_text())
    existing = next(s for s in manifest["sources"] if s["id"] == "north-island-sofi-2024-25-employees")
    raw = (folder / existing["file"]).read_bytes()
    if sha256(raw) != existing["dataSha256"] or existing["sha256"] != source["sha256"]:
        raise ValueError("Previously published NIC source fingerprint changed")
    payload = json.loads(gzip.decompress(raw))
    published = payload if isinstance(payload, list) else payload["rows"]
    if Counter(map(tuple, rows)) != Counter(map(tuple, published)):
        raise ValueError("Previously published NIC cohort differs; review before adding overlapping rows")
    return {**source, "publication": "verification-only-already-published",
            "publishedCollection": collection, "publishedSourceId": existing["id"],
            "publishedDataSha256": existing["dataSha256"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/pofbc-nic-history"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/north-island-history")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verify", action="store_true", help="Compare reproduced data/manifests without writing")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    date.fromisoformat(args.verified_on)
    sources, verification_only, files, by_period = [], [], {}, {}
    # Finish every extraction and independent check before writing any output.
    for period, reviewed in REVIEWED.items():
        path = args.cache_dir / f"nic-{period}.pdf"
        if not path.exists():
            if args.offline:
                raise ValueError(f"Missing cached original: {path}")
            request = urllib.request.Request(BASE_URL + period + ".pdf", headers={"User-Agent": "PofBC official salary source verification"})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            if not data.startswith(b"%PDF-") or sha256(data) != reviewed["sha256"]:
                raise ValueError(f"Original changed or is not a PDF: {period}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        data = path.read_bytes()
        if sha256(data) != reviewed["sha256"]:
            raise ValueError(f"Original fingerprint changed; review before importing: {period}")
        text = subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True)
        rows, validation = parse_layout(text, period)
        independent_coordinate_check(path, rows, period)
        source, compressed = build_source(period, rows, validation, data, args.verified_on)
        if period == "2024-25":
            verification_only.append(existing_publication(rows, source))
        else:
            sources.append(source)
        files[source["file"]] = compressed
        by_period[period] = rows
    manifest = {"version": 1, "rowSchema": SCHEMA, "sources": sources,
        "verificationOnlySources": verification_only,
        "unparsedSources": [{
            "id": "north-island-college-sofi-2019-20-ocr-lead", "employerSlug": EMPLOYER,
            "employerName": "North Island College", "year": "2019/20",
            "title": "North Island College Statement of Financial Information, year ended March 31, 2020: scanned original awaiting extraction",
            "sourceUrl": BASE_URL + "2019-20.pdf", "sourceIndexUrl": INDEX_URL, "indexUrl": INDEX_URL,
            "status": "requires-ocr", "scope": "employee-remuneration",
            "sha256": "43fd43a1d642fd6ad49efa92b8428d8663a4a410eec74d2d615b30fecb7e661d",
            "physicalPdfPageCount": 9, "checkedOn": args.verified_on,
            "reason": "The retrieved original has no native text. Its rendered cover confirms year ended March 31, 2020, but no employee rows or controls have been accepted.",
            "nextAction": "OCR the complete original, verify the employee-section period/scope and every row against rendered pages, then reconcile printed controls before accepting any observations.",
            "notes": [
                "The official archive's 2019-20 and 2020-21 labels both target https://www.nic.bc.ca/_resources/pdf/statement-of-financial-information-2019-20.pdf. The rendered cover confirms this target is FY2019/20; do not reclassify it as FY2020/21 from the second link label.",
                "The genuine FY2020/21 report is independently accepted in the separate north-island collection. This unparsed lead contributes zero salary observations.",
                "Cover-period verification is not complete employee-schedule, row or subtotal verification.",
            ],
            "discoveryEvidence": {"indexUrl": INDEX_URL,
                "indexLabels": ["2019-20 Statement of Financial Information", "2020-21 Statement of Financial Information"],
                "observedTargetUrl": BASE_URL + "2019-20.pdf", "renderedCoverPhysicalPage": 1,
                "renderedCoverFiscalYearEnd": "2020-03-31", "employeeScheduleAccepted": False},
        }],
        "coverageNotes": ["Five complete official employee cohorts (808 observations) independently verified. Four cohorts add 608 official observations; FY2023/24 replaces 181 compiled rows for 427 net additions. The 200 FY2024/25 observations are already published by PR #34 and remain verification-only here, with exact source and row-multiset agreement.",
            "FY2019/20 remains a scanned-source/OCR gap. FY2020/21 is already accepted in the separate north-island collection. This is not a claim of complete college history."]}
    files["sources.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    files["compiled-period-comparison.json"] = (json.dumps(baseline_comparison(by_period["2023-24"]), ensure_ascii=False, indent=2) + "\n").encode()
    if args.verify:
        for filename, expected in files.items():
            if (args.output / filename).read_bytes() != expected:
                raise ValueError(f"Checked-in normalized output differs: {filename}")
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            (args.output / filename).write_bytes(content)
    print(json.dumps({"verified": args.verify, "sources": len(sources), "officialRows": sum(s["rowCount"] for s in sources),
        "alreadyPublishedRowsVerified": sum(s["rowCount"] for s in verification_only),
        "replacedCompiledRows": 181, "netAdditionalRows": 427,
        "periods": [{"year": s["year"], "rows": s["rowCount"], "payResidual": s["validation"]["remunerationResidual"],
                     "expenseResidual": s["validation"]["expensesResidual"]} for s in sources]}, indent=2))


if __name__ == "__main__":
    main()
