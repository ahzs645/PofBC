#!/usr/bin/env python3
"""Import UNBC's final 2024/25 employee remuneration schedule.

Requires Poppler pdftotext and pdfplumber. The PDF fingerprint, complete schedule,
every monetary cell, and printed subtotals are checked before any output is
written. A one-cent source remuneration residual is explicitly retained.
The normal salary build consumes the checked-in data and needs no PDF tools.
"""
import argparse
from collections import defaultdict
from datetime import date
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.unbc.ca/sites/default/files/sections/finance/unbc-sofi-2025-final-submission-be-uploaded-website.pdf"
INDEX_URL = "https://www.unbc.ca/finance/financial-statements"
REVIEWED_SHA256 = "9f51790f023f8f817af5574e92eccc87dd84b4c9a0bca5a72e66967931c702de"
EMPLOYER = "university-of-northern-bc"
PAGES = list(range(31, 38))
PAGE_COUNTS = [67, 68, 68, 68, 68, 68, 50]
AMOUNT = r"[\d,]+\.\d{2}"
ROW = re.compile(rf"^\s*(.+?,.+?)\s{{2,}}(.+?)\s{{2,}}({AMOUNT})\s+({AMOUNT}|-)\s*$")
SUMMARY = re.compile(rf"^\s*(Total remuneration [<>] \$75,000|Grand total remuneration)\s+({AMOUNT})\s+({AMOUNT})\s*$")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cents(value):
    amount = Decimal(value.replace(",", "")) * 100
    if amount != amount.to_integral_value():
        raise ValueError(f"More than cent precision: {value}")
    return int(amount)


def parse(text):
    pages = text.split("\f")
    if not re.search(r"Year Ended,?\s*March 31,\s*2025", pages[0], re.I):
        raise ValueError("Final report cover does not establish the reviewed fiscal year")
    rows, found_pages, page_counts, summaries, cells_by_page = [], [], [], {}, {}
    for pdf_page, page in enumerate(pages, 1):
        if "SCHEDULE OF EMPLOYEE REMUNERATION" not in page:
            continue
        if "FOR THE YEAR ENDED MARCH 31, 2025" not in page:
            raise ValueError(f"Employee schedule year mismatch on PDF page {pdf_page}")
        if page.strip().splitlines()[-1].strip() != str(pdf_page - 2):
            raise ValueError(f"Printed page number mismatch on PDF page {pdf_page}")
        found_pages.append(pdf_page)
        page_rows, monetary_cells = [], []
        for line in page.splitlines():
            summary = SUMMARY.match(line)
            if summary:
                label, pay, expenses = summary.groups()
                if label in summaries:
                    raise ValueError(f"Repeated printed summary: {label}")
                summaries[label] = [cents(pay), cents(expenses)]
                monetary_cells.append([pay, expenses])
                continue
            match = ROW.match(line)
            if match:
                name, position, pay, expenses = match.groups()
                name, position = name.strip(), position.strip()
                pay_cents = cents(pay)
                if name.startswith(("Total", "Grand")) or not position or pay_cents <= 7_500_000:
                    raise ValueError(f"Invalid named employee row on PDF page {pdf_page}: {line}")
                page_rows.append([EMPLOYER, name, position, pay_cents / 100,
                                  None if expenses == "-" else cents(expenses) / 100, pdf_page])
                monetary_cells.append([pay, expenses])
            elif re.search(AMOUNT, line):
                raise ValueError(f"Unparsed monetary line on PDF page {pdf_page}: {line!r}")
        rows.extend(page_rows)
        page_counts.append(len(page_rows))
        cells_by_page[pdf_page] = monetary_cells
    if found_pages != PAGES or page_counts != PAGE_COUNTS or len(rows) != 457:
        raise ValueError(f"Incomplete or changed employee schedule: {found_pages}, {page_counts}")
    if len({row[1] for row in rows}) != len(rows):
        raise ValueError("Unexpected repeated disclosed name; review the original schedule")
    expected_summaries = {
        "Total remuneration > $75,000": [5_534_567_931, 258_841_601],
        "Total remuneration < $75,000": [3_007_540_610, 27_566_411],
        "Grand total remuneration": [8_542_108_541, 286_408_012],
    }
    if summaries != expected_summaries:
        raise ValueError(f"Printed source summaries changed: {summaries}")
    pay_sum = sum(cents(str(row[3])) for row in rows)
    expenses_sum = sum(cents(str(row[4])) for row in rows if row[4] is not None)
    # The displayed row values sum one cent above the printed named subtotal.
    # The independent coordinate extraction below must agree with every cell.
    if (pay_sum, expenses_sum) != (5_534_567_932, 258_841_601):
        raise ValueError(f"Displayed row sums changed: {pay_sum}, {expenses_sum}")
    if pay_sum - summaries["Total remuneration > $75,000"][0] != 1:
        raise ValueError("Unexpected remuneration reconciliation residual")
    return rows, cells_by_page, summaries


def verify_coordinates(pdf_path, expected):
    """Independently compare every monetary cell using PDF character coordinates.

    The locked final PDF aligns remuneration left of x=440 and expenses right of
    it. Character grouping avoids pdfplumber word extraction dropping a leading
    digit where the PDF also places overlapping whitespace characters.
    """
    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) != 45:
            raise ValueError("Unexpected source PDF page count")
        for pdf_page in PAGES:
            by_line = defaultdict(list)
            for char in pdf.pages[pdf_page - 1].chars:
                if 380 <= char["x0"] < 505 and char["text"].strip():
                    by_line[round(char["top"], 2)].append(char)
            actual = []
            for _, chars in sorted(by_line.items()):
                chars.sort(key=lambda char: char["x0"])
                pay = "".join(char["text"] for char in chars if char["x0"] < 440)
                expenses = "".join(char["text"] for char in chars if char["x0"] >= 440)
                if re.fullmatch(AMOUNT, pay):
                    actual.append([pay, expenses])
            if actual != expected[pdf_page]:
                raise ValueError(f"Independent monetary-cell extraction disagrees on PDF page {pdf_page}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-salary-sources"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/unbc")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    pdf = args.cache / "unbc-2024-25.pdf"
    if not pdf.exists():
        if args.offline:
            raise ValueError(f"Missing reviewed PDF: {pdf}")
        request = urllib.request.Request(URL, headers={"User-Agent": "PofBC salary source importer"})
        with urllib.request.urlopen(request, timeout=60) as response:
            downloaded = response.read()
        if sha(downloaded) != REVIEWED_SHA256:
            raise ValueError("Official PDF changed; review before importing")
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(downloaded)
    raw = pdf.read_bytes()
    if sha(raw) != REVIEWED_SHA256:
        raise ValueError("Official PDF changed; review before importing")
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    rows, cells, summaries = parse(text)
    verify_coordinates(pdf, cells)
    normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
    source = {
        "id": "unbc-sofi-2024-25-employees", "employerSlug": EMPLOYER,
        "employerName": "University of Northern British Columbia", "sector": "Universities and colleges",
        "year": "2024/25", "slug": "2024-25", "file": "2024-25.json.gzip",
        "title": "UNBC Statement of Financial Information 2024/25: employee remuneration",
        "sourceUrl": URL, "sourceIndexUrl": INDEX_URL, "sha256": REVIEWED_SHA256,
        "dataSha256": sha(compressed), "normalizedSha256": sha(normalized),
        "periodStart": "2024-04-01", "periodEnd": "2025-03-31",
        "category": "employee-remuneration", "scope": "employee-remuneration",
        "scopeDescription": "Named employees with remuneration over $75,000; board payments and aggregate rows excluded",
        "threshold": 75000, "thresholdRule": "over", "currency": "CAD", "amountPrecision": "cents",
        "nameDisclosure": "published-full-name", "positionDisclosure": "published",
        "rowCount": len(rows), "totalRemuneration": 55345679.32, "totalExpenses": 2588416.01,
        "totalDisclosedExpenses": 2588416.01, "pages": PAGES, "printedPages": list(range(29, 36)),
        "status": "verified", "verifiedOn": args.verified_on,
        "validation": {
            "sourceFingerprintLocked": True, "completeEmployeeSchedule": True,
            "rowCountsByPdfPage": dict(zip(PAGES, PAGE_COUNTS)),
            "allMonetaryCellsIndependentlyVerified": True,
            "independentMethod": "pdftotext layout rows compared cell-for-cell to pdfplumber character-coordinate extraction",
            "summaryTotalReconciled": False, "remunerationSubtotalExact": False, "expensesSubtotalExact": True,
            "publishedNamedRemuneration": 55345679.31, "sumOfDisplayedNamedRemuneration": 55345679.32,
            "remunerationResidual": 0.01, "publishedNamedExpenses": 2588416.01,
            "expensesResidual": 0, "unparsedMonetaryLines": 0,
            "expenseDashesRetainedAsMissing": sum(row[4] is None for row in rows),
            "visualReviewPdfPages": [31, 36, 37],
            "visualReview": "Verified the first employee page, long name/position boundaries, final employee rows, all printed subtotals and the remuneration definition. No row values were changed."
        },
        "excludedAggregates": {
            "belowThresholdRemuneration": 30075406.10, "belowThresholdExpenses": 275664.11,
            "grandTotalRemuneration": 85421085.41, "grandTotalExpenses": 2864080.12,
            "boardSchedulePdfPage": 30
        },
        "notes": [
            "The complete named employee schedule on printed pages 29-35 is imported with positions and original cents. Board payments, below-threshold aggregates and grand totals are not employee rows.",
            "Displayed employee remuneration totals $55,345,679.32, one cent above the printed $55,345,679.31 subtotal. Independent extraction agrees with every displayed monetary cell. The report does not explain the residual; published row values are preserved without adjustment.",
            "Disclosed expenses sum exactly to the printed named subtotal of $2,588,416.01. The 99 dash expense cells are retained as missing rather than assumed zero.",
            "The source excludes employer payments for non-taxable benefits, CPP, EI and WCB, and excludes payments under severance agreements; accounting-basis differences also affect comparisons with financial-statement salary and benefit totals."
        ]
    }
    registry = {"version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"], "sources": [source]}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / source["file"]).write_bytes(compressed)
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print("UNBC 2024/25: 457 employee rows; $55,345,679.32 displayed remuneration (+$0.01 source residual), $2,588,416.01 expenses (exact).")


if __name__ == "__main__":
    main()
