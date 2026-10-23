#!/usr/bin/env python3
"""Recover BC Transit's image-only FY2020/21 named employee disclosure.

Requires PyMuPDF and Tesseract. The reviewed PDF is pinned by SHA-256. Two
different renderings are OCR'd and reconciled using explicit, image-reviewed
corrections. Every employee page, name/pay/expense row, and printed subtotal is
checked before publishing normalized rows. Nothing is adjusted to balance sums.

Run normally to download/render/OCR the source again. --reviewed-ocr replays the
durable, hash-checked OCR evidence instead, while still checking the source PDF,
all parsing, both passes, completeness, expected output hash, and subtotals.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/salaries/bc-transit"
REVIEW = OUT / "review/2020-21-ocr-review.json"
URL = "https://www.bctransit.com/wp-content/uploads/9/159/2021-07-30-FY2021-Statement-of-Financial-Information-Final-with-FS-Image.pdf"
INDEX_URL = "https://www.bctransit.com/about/corporate-reports/financial/"
PDF_SHA256 = "f9d752695330689e2f2e20d37f13a16be9473c0ccf5c6c77d576765cf4279409"
NORMALIZED_SHA256 = "adb2ef47ff18f885f004a1d93a6319c6e033de6939fd5f2ce54cd307a0407682"
PAGES = list(range(6, 14))
ROW = re.compile(r"(.+?, .+?) (\d{2,3},\d{3}) ([\d,]+|-)")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def render_and_ocr(pdf, cache):
    import fitz

    document = fitz.open(pdf)
    if len(document) != 52:
        raise ValueError("Unexpected PDF page count")
    jobs = []
    for dpi, colorspace in [(300, fitz.csRGB), (400, fitz.csGRAY)]:
        for page in PAGES:
            image = cache / f"transit-{page:02d}-{dpi}.png"
            document[page - 1].get_pixmap(
                matrix=fitz.Matrix(dpi / 72, dpi / 72), colorspace=colorspace
            ).save(image)
            jobs.append((str(dpi), str(page), image))
    env = dict(os.environ, OMP_THREAD_LIMIT="1")

    def run(job):
        dpi, page, image = job
        result = subprocess.check_output(
            ["tesseract", str(image), "stdout", "--psm", "6"],
            text=True, stderr=subprocess.DEVNULL, env=env,
        )
        return dpi, page, result

    raw = {"300": {}, "400": {}}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for dpi, page, text in pool.map(run, jobs):
            raw[dpi][page] = text
    return raw


def parse_pass(raw, pass_id, review):
    if set(raw) != {str(page) for page in PAGES}:
        raise ValueError("Incomplete OCR page set")
    corrections = {
        (item["pdfPage"], item["ocrLine"]): item["verifiedLine"]
        for item in review["reviewedCorrections"][pass_id]
    }
    rows = []
    for expected in review["pages"]:
        page = expected["pdfPage"]
        text = raw[str(page)]
        if page == 6:
            for required in ["Expenses over $75,000", "For the Year Ended March 31, 2021"]:
                if required not in text:
                    raise ValueError(f"Missing threshold or period on employee schedule: {required}")
        active, found_header, page_rows = False, False, []
        for original in text.splitlines():
            line = " ".join(original.replace("$", "").split())
            line = corrections.get((page, line), line)
            if line.startswith("EMPLOYEE NAME"):
                active = found_header = True
                continue
            if line.startswith("Over 75,000 Remuneration"):
                active = False
            if not active or not line or line == str(page):
                continue
            match = ROW.fullmatch(line)
            if not match:
                raise ValueError(f"Unparsed employee schedule line, pass {pass_id}, page {page}: {line}")
            name, pay, expenses = match.groups()
            pay = int(pay.replace(",", ""))
            expenses = 0 if expenses == "-" else int(expenses.replace(",", ""))
            if pay <= 75000 or not name.strip():
                raise ValueError(f"Unexpected employee row: {line}")
            page_rows.append(["bc-transit", name, None, pay, expenses, page])
        if not found_header or not page_rows:
            raise ValueError(f"Missing employee header or rows on page {page}")
        actual = {
            "rowCount": len(page_rows), "firstName": page_rows[0][1],
            "lastName": page_rows[-1][1],
            "remunerationSum": sum(row[3] for row in page_rows),
            "expensesSum": sum(row[4] for row in page_rows),
        }
        if any(value != expected[key] for key, value in actual.items()):
            raise ValueError(f"Employee page differs from reviewed transcription: {page}, {actual}")
        rows.extend(page_rows)
    if len(rows) != 385 or len({row[1] for row in rows}) != 385:
        raise ValueError("Unexpected named employee count or duplicate name")
    if "27-pay period cycle (2020 - 26 pay periods)" not in raw["13"]:
        raise ValueError("Missing pay-period comparability note")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/pofbc-transit-research"))
    parser.add_argument("--pdf", type=Path, help="Already downloaded reviewed official PDF")
    parser.add_argument("--reviewed-ocr", action="store_true", help="Replay hash-checked saved OCR evidence")
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    pdf = args.pdf or args.cache_dir / "bc-transit-2020-21.pdf"
    if not pdf.exists():
        with urllib.request.urlopen(URL, timeout=120) as response:
            pdf.write_bytes(response.read())
    if sha(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError("Official PDF changed; review the new source before changing its accepted hash")
    review_bytes = REVIEW.read_bytes()
    review = json.loads(review_bytes)
    if review["sourceSha256"] != PDF_SHA256 or review["normalizedSha256"] != NORMALIZED_SHA256:
        raise ValueError("Review evidence does not match the reviewed source and output")
    if args.reviewed_ocr:
        evidence = (REVIEW.parent / review["rawOcrFile"]).read_bytes()
        if sha(evidence) != review["rawOcrSha256"]:
            raise ValueError("Saved OCR evidence hash mismatch")
        raw = json.loads(gzip.decompress(evidence))
    else:
        raw = render_and_ocr(pdf, args.cache_dir)
    rows = parse_pass(raw["300"], "300", review)
    if rows != parse_pass(raw["400"], "400", review):
        raise ValueError("Reviewed OCR passes disagree")
    normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    if sha(normalized) != NORMALIZED_SHA256:
        raise ValueError("Rows differ from the complete, image-reviewed transcription")
    sums = {"remuneration": sum(row[3] for row in rows), "expenses": sum(row[4] for row in rows)}
    printed = review["publishedNamedSubtotals"]
    difference = {column: sums[column] - printed[column] for column in sums}
    rounding_bound = (len(rows) + 1) / 2
    if sums != review["namedRowSums"] or difference != review["differenceRowsMinusPrinted"]:
        raise ValueError("Unexpected printed-subtotal variance")
    if any(abs(value) > rounding_bound for value in difference.values()):
        raise ValueError("Named subtotal exceeds the whole-dollar rounding bound")
    summary = review["summaryAlsoReviewed"]
    for column in ["Remuneration", "Expenses"]:
        if printed[column.lower()] + summary["belowThreshold" + column] != summary["allEmployees" + column]:
            raise ValueError("Printed named and below-threshold totals do not reconcile to grand total")
    compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
    source = {
        "id": "bc-transit-sofi-2021", "employerSlug": "bc-transit", "employerName": "BC Transit",
        "sector": "Crown corporations", "year": "2020/21", "slug": "2020-21", "file": "2020-21.json.gzip",
        "title": "British Columbia Transit Statement of Financial Information, year ended March 31, 2021",
        "sourceUrl": URL, "sourceIndexUrl": INDEX_URL, "sha256": PDF_SHA256,
        "dataSha256": sha(compressed), "normalizedSha256": sha(normalized),
        "periodStart": "2020-04-01", "periodEnd": "2021-03-31",
        "category": "employee-remuneration", "scope": "named-employees-over-threshold",
        "threshold": 75000, "thresholdRule": "over", "currency": "CAD", "amountUnit": "dollars",
        "nameDisclosure": "published-full-name", "positionDisclosure": "not-published",
        "rowCount": len(rows), "totalRemuneration": sums["remuneration"], "totalExpenses": sums["expenses"],
        "pages": PAGES, "status": "verified", "verifiedOn": "2026-10-22",
        "validation": {
            "method": "Two OCR renderings, explicit image-reviewed corrections, complete page review and printed-subtotal reconciliation",
            "fullEmployeePagesReviewed": PAGES, "ocrPassesAgreeAfterReviewedCorrections": True,
            "printedRemunerationSubtotal": printed["remuneration"], "printedExpensesSubtotal": printed["expenses"],
            "remunerationDifference": difference["remuneration"], "expensesDifference": difference["expenses"],
            "remunerationSubtotalExact": False, "expensesSubtotalExact": False,
            "wholeDollarRoundingUpperBound": rounding_bound, "withinWholeDollarRoundingBound": True,
            "printedNamedPlusBelowEqualsGrandTotals": True,
            "reviewFile": "review/2020-21-ocr-review.json", "reviewSha256": sha(review_bytes),
        },
        "notes": [
            "Recovered 385 named employees from the official image-only 2020/21 employee schedule, PDF pages 6–13. Board payments, below-threshold aggregates and suppliers are excluded.",
            "Named row sums are $36,243,255 remuneration and $320,215 expenses. Printed named subtotals are $36,243,253 and $320,208. The +$2 and +$7 variances are within whole-dollar rounding bounds; source row values are preserved without balancing adjustments.",
            "The report states that 2021 remuneration covers 27 pay periods, compared with 26 in 2020, and includes gross pay, taxable benefits and banked-time payouts. Year-to-year changes therefore are not simply changes in salary rates.",
            "The source publishes names and amounts but no employee positions. Dashes in the expense column are recorded as zero; position is null.",
        ],
    }
    # All verification completes before accepted artifacts are written.
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / source["file"]).write_bytes(compressed)
    (OUT / "sources.json").write_text(json.dumps({"version": 1,
        "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "sources": [source]}, indent=2) + "\n")
    print("BC Transit 2020/21: 385 named rows; pay $36,243,255, expenses $320,215; printed-subtotal variances +$2 / +$7.")


if __name__ == "__main__":
    main()
