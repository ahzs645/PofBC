#!/usr/bin/env python3
"""Recover reviewed BC Transit annual named employee disclosures.

Requires PyMuPDF and Tesseract. The reviewed PDF is pinned by SHA-256. Two
different renderings are OCR'd and reconciled using explicit, image-reviewed
corrections. Every employee page, name/pay/expense row, and printed subtotal is
checked before publishing normalized rows. Nothing is adjusted to balance sums.

Run normally to download/render/OCR the source again. --reviewed-ocr replays the
durable, hash-checked OCR evidence instead, while still checking the source PDF,
all parsing, both passes, completeness, expected output hash, and subtotals.

Use --year YYYY-YY for another reviewed annual source or --all-reviewed to
rebuild every accepted period. Native-text sources additionally compare every
row with an independent extraction from positioned PDF words. Adding a year
requires a dated employee schedule, complete page review, pinned source hash,
and review evidence; a successful OCR run alone does not accept a new year.
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
ANNUAL_ROW = re.compile(r"(.+?) (\d{2,3},\d{3}) ([\d,]+|-)")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_source(source, compressed):
    """Update one accepted period without erasing the other reviewed years."""
    path = OUT / "sources.json"
    manifest = json.loads(path.read_text()) if path.exists() else {
        "version": 1,
        "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "sources": [],
    }
    if any(s["slug"] == source["slug"] and s["id"] != source["id"] for s in manifest["sources"]):
        raise ValueError("Another source already owns this employer/year")
    manifest["sources"] = sorted(
        [s for s in manifest["sources"] if s["id"] != source["id"]] + [source],
        key=lambda s: s["slug"],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / source["file"]).write_bytes(compressed)
    path.write_text(json.dumps(manifest, indent=2) + "\n")


def parse_annual_pages(raw, review, pass_id=None):
    expected_pages = [p["pdfPage"] for p in review["pages"]]
    if sorted(map(int, raw)) != expected_pages:
        raise ValueError("Incomplete annual employee page set")
    end_year = int(review["slug"][:4]) + 1
    first = " ".join(raw[str(expected_pages[0])].split())
    for required in ["Expenses over $75,000", f"For the Year Ended March 31, {end_year}"]:
        if required not in first:
            raise ValueError(f"Missing employee threshold or period: {required}")
    corrections = {
        (x["pdfPage"], x["ocrLine"]): x["verifiedLine"]
        for x in review.get("reviewedCorrections", {}).get(pass_id, [])
    }
    used_corrections = set()
    rows = []
    corrected_pages = {}
    for expected in review["pages"]:
        page = expected["pdfPage"]
        found_years = re.findall(r"For the Year Ended March 31, (\d{4})", raw[str(page)])
        if any(int(year) != end_year for year in found_years):
            raise ValueError(f"Wrong employee schedule year on page {page}")
        active = found_header = False
        page_rows = []
        corrected_lines = []
        for original in raw[str(page)].splitlines():
            line = " ".join(original.replace("$", "").split())
            key = (page, line)
            if key in corrections:
                used_corrections.add(key)
                line = corrections[key]
            corrected_lines.append(line)
            if line.startswith("EMPLOYEE NAME"):
                if found_header:
                    raise ValueError(f"Repeated employee header on page {page}")
                active = found_header = True
                continue
            if line.startswith("Over 75,000 Remuneration"):
                active = False
            if not active or not line or line == str(page):
                continue
            match = ANNUAL_ROW.fullmatch(line)
            if not match:
                raise ValueError(f"Unparsed employee line on page {page}: {line}")
            name, pay, expense = match.groups()
            if ", " not in name and name not in review.get("namesWithoutComma", []):
                raise ValueError(f"Unreviewed name structure on page {page}: {name}")
            pay = int(pay.replace(",", ""))
            expense = 0 if expense == "-" else int(expense.replace(",", ""))
            if pay <= 75000:
                raise ValueError(f"Unexpected below-threshold employee: {line}")
            page_rows.append(["bc-transit", name, None, pay, expense, page])
        if not found_header or not page_rows:
            raise ValueError(f"Missing employee header or rows on page {page}")
        actual = {"rowCount": len(page_rows), "firstName": page_rows[0][1],
                  "lastName": page_rows[-1][1],
                  "remunerationSum": sum(r[3] for r in page_rows),
                  "expensesSum": sum(r[4] for r in page_rows)}
        if any(expected[k] != v for k, v in actual.items()):
            raise ValueError(f"Employee page differs from reviewed evidence: {page}: {actual}")
        rows.extend(page_rows)
        corrected_pages[page] = " ".join(corrected_lines)
    if used_corrections != set(corrections):
        raise ValueError("Reviewed OCR correction was not used; the extraction has changed")
    if len(rows) != review["rowCount"]:
        raise ValueError("Unexpected annual employee row count")
    summary = corrected_pages[expected_pages[-1]]
    for label, key in [("Over 75,000 Remuneration", "publishedNamedSubtotals"),
                       ("Less than 75,000 Remuneration", "belowThresholdSubtotals"),
                       ("Grand Total Employees", "allEmployeeTotals")]:
        match = re.search(re.escape(label) + r"\s+([\d,]+)\s+([\d,]+)", summary)
        if not match or [int(v.replace(",", "")) for v in match.groups()] != list(review[key].values()):
            raise ValueError(f"Printed {label} differs from reviewed evidence")
    if review["payPeriodNote"] not in summary:
        raise ValueError("Missing or changed pay-period comparability note")
    return rows


def native_coordinate_rows(pdf, pages):
    """Read complete table rows using their physical baselines and columns."""
    import fitz

    result = []
    with fitz.open(pdf) as document:
        found_pages = [i + 1 for i, page in enumerate(document)
                       if re.search(r"EMPLOYEE\s+NAME", page.get_text())]
        if found_pages != pages:
            raise ValueError("Native PDF contains a missing or unexpected employee page")
        for number in pages:
            words = document[number - 1].get_text("words")
            header = next(w for w in words if w[4] == "EMPLOYEE")
            bottom = min((w[1] for w in words if w[4] == "Over" and w[1] > header[1]), default=740)
            pay_x = next(w[0] for w in words if "REMUNERATION" in w[4]) - 5
            expense_x = next(w[0] for w in words if w[4] == "TOTAL") - 5
            baselines = []
            for word in sorted(words, key=lambda w: (w[1], w[0])):
                if not header[1] + 5 < word[1] < bottom - 1:
                    continue
                if not baselines or abs(baselines[-1][0][1] - word[1]) > 1:
                    baselines.append([])
                baselines[-1].append(word)
            for line in baselines:
                columns = [[], [], []]
                for word in sorted(line, key=lambda w: w[0]):
                    columns[0 if word[0] < pay_x else 1 if word[0] < expense_x else 2].append(word[4])
                name, pay, expense = [" ".join(c) for c in columns]
                if not re.fullmatch(r".+?, .+", name) or not re.fullmatch(r"\d{2,3},\d{3}", pay) or not re.fullmatch(r"[\d,]+|-", expense):
                    raise ValueError(f"Unparsed coordinate row on page {number}: {columns}")
                result.append(["bc-transit", name, None, int(pay.replace(",", "")),
                               0 if expense == "-" else int(expense.replace(",", "")), number])
    return result


def extract_annual(review, args):
    import fitz

    slug = review["slug"]
    pdf = args.pdf or args.cache_dir / f"bc-transit-{slug}.pdf"
    if not pdf.exists():
        with urllib.request.urlopen(review["sourceUrl"], timeout=120) as response:
            pdf.write_bytes(response.read())
    if sha(pdf.read_bytes()) != review["sourceSha256"]:
        raise ValueError("Official PDF changed; review it before changing its accepted hash")
    with fitz.open(pdf) as document:
        if len(document) != review["pdfPageCount"]:
            raise ValueError("Unexpected annual PDF page count")
    pages = [p["pdfPage"] for p in review["pages"]]
    if review["method"] == "native-text":
        full_text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True).split("\f")
        rows = parse_annual_pages({str(p): full_text[p - 1] for p in pages}, review)
        if rows != native_coordinate_rows(pdf, pages):
            raise ValueError("Layout text and positioned-word extraction disagree")
    else:
        if args.reviewed_ocr:
            evidence = (OUT / "review" / review["rawOcrFile"]).read_bytes()
            if sha(evidence) != review["rawOcrSha256"]:
                raise ValueError("Saved annual OCR evidence hash mismatch")
            raw = json.loads(gzip.decompress(evidence))
        else:
            raw = render_annual_ocr(pdf, args.cache_dir, slug, pages)
        rows = parse_annual_pages(raw["300"], review, "300")
        if rows != parse_annual_pages(raw["400"], review, "400"):
            raise ValueError("Reviewed annual OCR passes disagree")
    normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    if sha(normalized) != review["normalizedSha256"]:
        raise ValueError("Annual rows differ from the reviewed transcription")
    sums = {"remuneration": sum(r[3] for r in rows), "expenses": sum(r[4] for r in rows)}
    if sums != review["namedRowSums"]:
        raise ValueError("Unexpected annual row sums")
    printed = review["publishedNamedSubtotals"]
    difference = {c: sums[c] - printed[c] for c in sums}
    bound = (len(rows) + 1) / 2
    if any(abs(v) > bound for v in difference.values()):
        raise ValueError("Printed subtotal differs by more than whole-dollar rounding permits")
    for column in sums:
        if printed[column] + review["belowThresholdSubtotals"][column] != review["allEmployeeTotals"][column]:
            raise ValueError("Printed named and below-threshold totals do not add to grand total")
    end_year = int(slug[:4]) + 1
    compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
    native = review["method"] == "native-text"
    source = {
        "id": f"bc-transit-sofi-{end_year}", "employerSlug": "bc-transit", "employerName": "BC Transit",
        "sector": "Crown corporations", "year": slug.replace("-", "/"), "slug": slug,
        "file": f"{slug}.json.gzip",
        "title": f"British Columbia Transit Statement of Financial Information, year ended March 31, {end_year}",
        "sourceUrl": review["sourceUrl"], "sourceIndexUrl": INDEX_URL,
        "sha256": review["sourceSha256"], "dataSha256": sha(compressed), "normalizedSha256": sha(normalized),
        "periodStart": f"{end_year - 1}-04-01", "periodEnd": f"{end_year}-03-31",
        "category": "employee-remuneration", "scope": "named-employees-over-threshold",
        "threshold": 75000, "thresholdRule": "over", "currency": "CAD", "amountUnit": "dollars",
        "nameDisclosure": "published-full-name", "positionDisclosure": "not-published",
        "rowCount": len(rows), "totalRemuneration": sums["remuneration"], "totalExpenses": sums["expenses"],
        "pages": pages, "status": "verified", "verifiedOn": "2026-10-23",
        "validation": {
            "method": "Layout text plus every row independently checked with positioned PDF words" if native else "Two OCR renderings, image-reviewed disagreements, complete page review and printed-subtotal reconciliation",
            "allRowsCheckedAgainstPdfCoordinates": native,
            "ocrPassesAgreeAfterReviewedCorrections": not native,
            "visuallyReviewedPages": review["visuallyReviewedPages"],
            "printedRemunerationSubtotal": printed["remuneration"], "printedExpensesSubtotal": printed["expenses"],
            "remunerationDifference": difference["remuneration"], "expensesDifference": difference["expenses"],
            "remunerationSubtotalExact": difference["remuneration"] == 0,
            "expensesSubtotalExact": difference["expenses"] == 0,
            "wholeDollarRoundingUpperBound": bound, "withinWholeDollarRoundingBound": True,
            "printedNamedPlusBelowEqualsGrandTotals": True,
            "reviewFile": "review/annual-reviews.json",
            "reviewEntrySha256": sha(json.dumps(review, sort_keys=True, separators=(",", ":")).encode()),
        },
        "notes": [
            f"Accepted {len(rows)} named employees from the complete official employee schedule, physical PDF pages {pages[0]}-{pages[-1]}. Board members, suppliers and aggregate rows are excluded.",
            f"Named remuneration is ${sums['remuneration']:,}; expenses are ${sums['expenses']:,}. Rows minus printed named subtotals: remuneration {difference['remuneration']:+,}, expenses {difference['expenses']:+,}. Residuals are within the independent whole-dollar rounding bound; individual values are unchanged and the source does not establish the cause.",
            f"The remuneration note states {review['payPeriodNote']}. Pay includes gross pay, taxable benefits and banked-time payouts; it is not an annual salary rate.",
            "The employee schedule publishes names and amounts but no positions. Expense dashes are recorded as zero; missing positions remain null.",
        ],
    }
    if review.get("namesWithoutComma"):
        source["notes"].append(
            "The source prints these names without a surname/given-name separator: "
            + "; ".join(review["namesWithoutComma"])
            + ". Their printed order is retained without inventing a surname boundary."
        )
    write_source(source, compressed)
    print(f"BC Transit {source['year']}: {len(rows)} rows; remuneration {sums['remuneration']:,}, expenses {sums['expenses']:,}; residuals {difference}")


def render_annual_ocr(pdf, cache, slug, pages):
    import fitz

    jobs = []
    with fitz.open(pdf) as document:
        for dpi, colorspace in [(300, fitz.csRGB), (400, fitz.csGRAY)]:
            for page in pages:
                image = cache / f"full-{slug}-{page:02d}-{dpi}.png"
                document[page - 1].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), colorspace=colorspace).save(image)
                jobs.append((str(dpi), str(page), image))

    def run(job):
        dpi, page, image = job
        output = subprocess.check_output(["tesseract", str(image), "stdout", "--psm", "6"],
                                         text=True, stderr=subprocess.DEVNULL,
                                         env=dict(os.environ, OMP_THREAD_LIMIT="1"))
        return dpi, page, output

    raw = {"300": {}, "400": {}}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for dpi, page, text in pool.map(run, jobs):
            raw[dpi][page] = text
    return raw


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
    parser.add_argument("--year", default="2020-21", help="Reviewed period, e.g. 2016-17 (default 2020-21)")
    parser.add_argument("--all-reviewed", action="store_true", help="Rebuild all reviewed annual sources")
    args = parser.parse_args()
    args.year = args.year.replace("/", "-")
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    if args.all_reviewed and args.pdf:
        parser.error("--pdf identifies one source and cannot be used with --all-reviewed")
    if args.all_reviewed or args.year != "2020-21":
        annual = json.loads((OUT / "review/annual-reviews.json").read_text())["sources"]
        selected = annual if args.all_reviewed else [r for r in annual if r["slug"] == args.year.replace("/", "-")]
        if not selected:
            parser.error(f"No reviewed source for {args.year}; review the source before accepting it")
        for review in selected:
            extract_annual(review, args)
        if not args.all_reviewed:
            return
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
    write_source(source, compressed)
    print("BC Transit 2020/21: 385 named rows; pay $36,243,255, expenses $320,215; printed-subtotal variances +$2 / +$7.")


if __name__ == "__main__":
    main()
