#!/usr/bin/env python3
"""Import ten reviewed Fraser Health employee-remuneration schedules, FY2015/16–2024/25.

Requires Poppler's pdftotext. Every employee row is independently reconstructed
from positioned PDF words and compared with the layout-text extraction. Source
hashes, fiscal headings, sequential page footers, monetary totals and published
subtotals are checked before any accepted output is replaced. The offline salary
build consumes the normalized gzip files and does not need this extractor.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
INDEX = "https://www.fraserhealth.ca/about-us/accountability/financial-reporting"
BASE = "https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/"
# Exact links from the employer's reporting index; filename capitalization varies.
FILES = {
    2016: "2016/2016EmployeeRenumeration.pdf",
    2017: "2017/20171030_employee_remuneration.pdf",
    2018: "2018/20181031_EE_Remuneration_Schedule.pdf",
    2019: "2019/2019_11_Summary_of_Remuneration_and_Expenses.pdf",
    2020: "2020/Employee-remuneration.pdf",
    2021: "2021/Employee-remuneration.pdf",
    2022: "2022/Employee_remuneration.pdf",
    2023: "2023/Employee-remuneration.pdf",
    2024: "2024/Employee-remuneration.pdf",
    2025: "2025/Employee_Remuneration.pdf",
}
# Reviewed PDF hash, page count, row count, displayed remuneration and expenses,
# and printed named-employee remuneration and expense subtotals.
REVIEWED = {
    2016: ("e6564e341b0dfc576cdf6bcc7a3aa8ff2809d4d3e29a1e4139a71858fc2b1575", 149, 6219, 575856593, 4542045, 575856515, 4542036),
    2017: ("44536e19f38d708ed2cba456269f80a2fbb65cf2b199f6fa835f6ede51ac1ea4", 158, 6606, 622509766, 4606903, 622509617, 4606740),
    2018: ("0125b00e4c76b8de69d8d1f7835260b4074bc23aae6f938b920a72f445de10d9", 170, 6938, 656117414, 5070506, 656117309, 5070457),
    2019: ("b78ab4ed653bf0682e3e96385046558ff4a950967031fbfd38eddc2cee0135e4", 154, 7527, 721267111, 4973596, 721267029, 4973546),
    2020: ("13621a601da6cc412ede2bb39b95024510a897caa6351c9eb81602a2ec0868b0", 166, 8080, 793671551, 5089367, 793671441, 5089309),
    2021: ("e6265fac988bea5034b257f9e057c95845c314a40b578b928e7124e5e374a9bf", 206, 10072, 1022135521, 5243498, 1022135501, 5243504),
    2022: ("65897bdbaadd4ec5ebf56303d757432364a3c1f83ba041b850a288dd6bce2af9", 221, 10782, 1114704375, 5726328, 1114704344, 5726268),
    2023: ("5b8a991c3ff69c6176489418c2d1f5ba29a3b5991d840050344a0a03300940cb", 231, 11289, 1174137118, 6165257, 1174136879, 6165243),
    2024: ("4aa5874dce2f261f1f0224c296ea30d1534e9984020a69f16bd99292008bb0f2", 305, 14921, 1715733845, 21092362, 1715733801, 21091937),
    2025: ("b5d0435cfd67f3f327a2dcb6f2947d637b03aa0c6653ca72054f0ab06c595465", 353, 17278, 2009600438, 19619483, 2009600126, 19620205),
}
# These edge cases were checked against rendered PDF pages. Every other row is
# still checked by both text algorithms; these are the targeted visual checks.
VISUAL_EXPENSE_REVIEWS = {
    2018: [("CANOSA,SANDEE", 81287, -459, 22)],
    2019: [("JEONG,JANELLE", 82030, -47, 64)],
    2020: [("CHOHAN,GURMANGAL", 97525, -85, 27), ("MCNEIL,ROSEMARY", 100621, -99, 99)],
    2022: [("BRAR,RAMAN", 126803, 0, 24)],
}
VISUAL_SUMMARY_REVIEWS = {2018: [169, 170], 2025: [353]}
HEADER = re.compile(r"EMPLOYEE NAME\s+REMUNERATION\s+EXPENSES")
ROW = re.compile(r"(.+?)\s{2,}([\d,]+)\s{2,}([\d,()\-‐\s]+)")
TOTAL_LABELS = (
    "Total payments equal to or greater than $75,000",
    "Total payments less than $75,000",
    "Total payments to all Fraser Health employees",
)
NS = {"x": "http://www.w3.org/1999/xhtml"}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def amount(token: str) -> int | None:
    value = "".join(token.split()).replace("‐", "-")
    if value in ("", "-"):
        return None
    if re.fullmatch(r"\(\d{1,3}(?:,\d{3})*\)", value):
        value = "-" + value[1:-1]
    if not re.fullmatch(r"-?\d{1,3}(?:,\d{3})*", value):
        raise ValueError(f"Unexpected monetary token: {token!r}")
    return int(value.replace(",", ""))


def parse_row(line: str, page: int) -> list:
    match = ROW.fullmatch(line.strip())
    if not match:
        raise ValueError(f"Unparsed employee line on page {page}: {line!r}")
    name, pay, expenses = match.groups()
    if "," not in name:
        raise ValueError(f"Unreviewed name ordering on page {page}: {name!r}")
    remuneration = amount(pay)
    if remuneration is None or remuneration < 75000:
        raise ValueError(f"Employee remuneration below the source's inclusive $75,000 threshold: {line!r}")
    return ["fraser-health", name, None, remuneration, amount(expenses), page]


def parse_summary(text: str, label: str) -> tuple[int, int]:
    matches = re.findall(re.escape(label) + r"\s+([\d,]+)\s+([\d,]+)", text)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one printed subtotal: {label}")
    return tuple(amount(token) for token in matches[0])


def parse_layout(text: str, fiscal_end: int) -> tuple[list[list], dict]:
    if "\ufffd" in text:
        raise ValueError("Replacement character in source text")
    pages = text.split("\f")
    if pages[-1].strip():
        raise ValueError("Expected terminal PDF page separator")
    pages.pop()
    if not pages:
        raise ValueError("No PDF pages")
    rows, page_counts, summary_pages = [], [], []
    summary_started = False
    for number, page in enumerate(pages, 1):
        lines = [line for line in page.splitlines() if line.strip()]
        if not lines or lines[-1].strip() != str(number):
            raise ValueError(f"Missing or out-of-order printed page footer on physical page {number}")
        if "FRASER HEALTH AUTHORITY" not in page:
            raise ValueError(f"Employer heading missing on page {number}")
        dates = re.findall(r"FOR THE FISCAL YEAR ENDED MARCH 31, (\d{4})", page)
        if dates != [str(fiscal_end)]:
            raise ValueError(f"Wrong or missing fiscal year on page {number}")
        starts = [at for at, line in enumerate(lines) if HEADER.fullmatch(line.strip())]
        if len(starts) != 1:
            raise ValueError(f"Expected one employee table header on page {number}")
        before = len(rows)
        for line in lines[starts[0] + 1:-1]:
            if line.strip().startswith("Total payments"):
                summary_started = True
                summary_pages.append(number)
                break
            if summary_started:
                raise ValueError(f"Employee text after aggregate section began, page {number}")
            rows.append(parse_row(line, number))
        page_counts.append(len(rows) - before)
        if page_counts[-1] == 0 and number not in summary_pages:
            raise ValueError(f"Empty employee page without an aggregate schedule: {number}")
    named, below, grand = (parse_summary(text, label) for label in TOTAL_LABELS)
    aggregate_residuals = tuple(a + b - c for a, b, c in zip(named, below, grand))
    # Three independently rounded whole-dollar aggregates have a $1.50 bound.
    if any(abs(value) > 1.5 for value in aggregate_residuals):
        raise ValueError("Printed subtotals and grand totals differ beyond whole-dollar rounding")
    repeated = Counter(row[1] for row in rows)
    return rows, {
        "physicalPdfPages": [1, len(pages)], "rowsPerPhysicalPage": page_counts,
        "summaryPhysicalPdfPages": summary_pages, "internalFiscalYearEnd": fiscal_end,
        "allFiscalHeadersChecked": True, "allPageFootersSequential": True,
        "unparsedEmployeeLines": 0,
        "printedNamedRemuneration": named[0], "printedNamedExpenses": named[1],
        "underThresholdRemunerationExcluded": below[0], "underThresholdExpensesExcluded": below[1],
        "printedAllEmployeeRemuneration": grand[0], "printedAllEmployeeExpenses": grand[1],
        "printedSubtotalRemunerationResidual": aggregate_residuals[0],
        "printedSubtotalExpenseResidual": aggregate_residuals[1],
        "printedSubtotalsReconcileExactly": aggregate_residuals == (0, 0),
        "printedSubtotalRoundingCompatibilityBound": 1.5,
        "repeatedDisclosedNames": [{"name": name, "rows": count} for name, count in repeated.items() if count > 1],
        "exactDuplicateSourceRows": sum(count - 1 for count in Counter(tuple(row[:5]) for row in rows).values() if count > 1),
    }


def validate_coordinates(bbox_xml: bytes, rows: list[list], physical_pages: int) -> int:
    """Reconstruct every table row from PDF coordinates independently of layout spacing."""
    pages = ET.fromstring(bbox_xml).findall(".//x:page", NS)
    if len(pages) != physical_pages:
        raise ValueError("Layout and coordinate PDF page counts differ")
    by_page = defaultdict(list)
    for row in rows:
        by_page[row[5]].append(row)
    checked = 0
    for number, page in enumerate(pages, 1):
        words = page.findall("x:word", NS)
        headings = [word for word in words if word.text == "EMPLOYEE"]
        if len(headings) != 1:
            raise ValueError(f"Coordinate employee header missing or repeated on page {number}")
        header_y = float(headings[0].attrib["yMin"])
        salary_header = [word for word in words if word.text == "REMUNERATION" and abs(float(word.attrib["yMin"]) - header_y) < 1]
        expense_header = [word for word in words if word.text == "EXPENSES" and abs(float(word.attrib["yMin"]) - header_y) < 1]
        if len(salary_header) != 1 or len(expense_header) != 1:
            raise ValueError(f"Coordinate remuneration header missing on page {number}")
        # Earlier schedules center headings above right-aligned values. Bound
        # the numeric column by both headings, rather than assuming their right edges agree.
        salary_left = float(salary_header[0].attrib["xMin"]) - 30
        salary_right = float(expense_header[0].attrib["xMin"]) - 1
        summary_y = min([float(word.attrib["yMin"]) for word in words if word.text == "Total" and float(word.attrib["yMin"]) > header_y] + [10000])
        salaries = [word for word in words if re.fullmatch(r"\d{1,3}(?:,\d{3})*", word.text or "")
                    and amount(word.text) >= 75000
                    and float(word.attrib["xMin"]) >= salary_left
                    and float(word.attrib["xMax"]) <= salary_right
                    and header_y + 2 < float(word.attrib["yMin"]) < summary_y - 1]
        salaries.sort(key=lambda word: float(word.attrib["yMin"]))
        observed = []
        for salary in salaries:
            y = float(salary.attrib["yMin"])
            right = float(salary.attrib["xMax"])
            line = sorted([word for word in words if abs(float(word.attrib["yMin"]) - y) < 1], key=lambda word: float(word.attrib["xMin"]))
            name = " ".join(word.text for word in line if float(word.attrib["xMax"]) < float(salary.attrib["xMin"]) - 2)
            expense = " ".join(word.text for word in line if float(word.attrib["xMin"]) > right + 1)
            observed.append(["fraser-health", name, None, amount(salary.text), amount(expense), number])
        if observed != by_page[number]:
            mismatch = next(((a, b) for a, b in zip(observed, by_page[number]) if a != b), None)
            raise ValueError(f"Page {number}: coordinate rows differ ({len(observed)} vs {len(by_page[number])}); first mismatch {mismatch!r}")
        checked += len(observed)
    return checked


def validate_totals(rows: list[list], validation: dict, reviewed: tuple) -> None:
    _, pages, count, pay, expenses, named_pay, named_expenses = reviewed
    observed = (validation["physicalPdfPages"][1], len(rows), sum(row[3] for row in rows),
                sum(row[4] for row in rows if row[4] is not None),
                validation["printedNamedRemuneration"], validation["printedNamedExpenses"])
    if observed != (pages, count, pay, expenses, named_pay, named_expenses):
        raise ValueError(f"Reviewed page/row counts or monetary totals changed: {observed!r}")
    residuals = pay - named_pay, expenses - named_expenses
    bound = (len(rows) + 1) / 2
    if any(abs(value) > bound for value in residuals):
        raise ValueError("Named subtotal residual exceeds displayed-dollar rounding bound")
    # Duplicates are kept, but an unexpected identical record requires an explicit review.
    if validation["exactDuplicateSourceRows"]:
        raise ValueError("Unexpected exact duplicate source rows; review before accepting")
    validation.update({
        "sourceFingerprintLocked": True, "namedRemunerationSum": pay, "namedExpensesSum": expenses,
        "remunerationResidual": residuals[0], "expensesResidual": residuals[1],
        "summaryTotalReconciled": residuals == (0, 0),
        "displayedDollarRoundingCompatibilityBound": bound,
        "residualsWithinDisplayedDollarRoundingBound": True,
        "negativeExpenseRows": sum(row[4] is not None and row[4] < 0 for row in rows),
        "explicitZeroExpenseRows": sum(row[4] == 0 for row in rows),
        "missingExpenseRows": sum(row[4] is None for row in rows),
        "thresholdComparison": ">=",
    })


def compare_compiled_baseline(rows: list[list], year: str) -> dict | None:
    path = ROOT / "research/salaries/compiled-baseline.json.gzip"
    if not path.exists():
        return None
    raw = path.read_bytes()
    baseline = json.loads(gzip.decompress(raw))
    if year not in baseline["years"]:
        return None
    employer = next(entry for entry in baseline["employers"] if entry["slug"] == "fraser-health")
    at = baseline["years"].index(year)
    old = [row for row in employer["rows"] if row[4] == at]
    def name_key(name):
        return tuple("".join(c for c in part.casefold() if c.isalnum()) for part in name.split(",", 1))
    compiled = Counter((name_key(row[0]), row[2]) for row in old)
    official = Counter((name_key(row[1]), row[3]) for row in rows)
    return {
        "baselineFile": "research/salaries/compiled-baseline.json.gzip", "baselineSha256": sha256(raw),
        "compiledLabel": year, "compiledRows": len(old), "officialRows": len(rows),
        "exactNormalizedNamePayMatches": sum((compiled & official).values()),
        "compiledNamePayPairsNotInOfficialSchedule": sum((compiled - official).values()),
        "officialNamePayPairsNotInCompiledSnapshot": sum((official - compiled).values()),
        "method": "Multiplicity-preserving name/pay comparison after removing name case, spacing and punctuation; no fuzzy, nickname or identity matching.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-fraser"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/fraser-health")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    pending, sources = {}, []
    for end, reviewed in REVIEWED.items():
        url = BASE + FILES[end]
        pdf = args.cache / f"{end}.pdf"
        if not pdf.exists():
            if args.offline:
                raise ValueError(f"Missing cached PDF: {pdf}")
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PofBC salary source importer"})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            if not raw.startswith(b"%PDF-"):
                raise ValueError(f"Source is not a PDF: {url}")
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(raw)
        raw = pdf.read_bytes()
        if sha256(raw) != reviewed[0]:
            raise ValueError(f"Fraser Health {end} source bytes changed; review before importing")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        bbox = subprocess.check_output(["pdftotext", "-bbox", str(pdf), "-"])
        rows, validation = parse_layout(text, end)
        validation["rowsCheckedAgainstPdfWordCoordinates"] = validate_coordinates(bbox, rows, reviewed[1])
        validate_totals(rows, validation, reviewed)
        visual_rows = VISUAL_EXPENSE_REVIEWS.get(end, [])
        for name, pay, expenses, page in visual_rows:
            if ["fraser-health", name, None, pay, expenses, page] not in rows:
                raise ValueError(f"Visually reviewed expense row changed: {end} page {page} {name}")
        if visual_rows:
            validation["visuallyReviewedExpenseRows"] = [
                {"name": name, "remuneration": pay, "expenses": expenses, "physicalPdfPage": page}
                for name, pay, expenses, page in visual_rows
            ]
        if end in VISUAL_SUMMARY_REVIEWS:
            validation["visuallyReviewedSummaryPages"] = VISUAL_SUMMARY_REVIEWS[end]
        label = f"{end - 1}-{end % 100:02d}"
        year = label.replace("-", "/")
        filename = label + ".json.gzip"
        normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
        compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
        pending[filename] = compressed
        source = {
            "id": "fraser-health-sofi-" + label, "employerSlug": "fraser-health",
            "employerName": "Fraser Health", "sector": "Health authorities", "year": year,
            "title": f"Fraser Health Statement of Financial Information {year}: employee remuneration and expenses",
            "sourceUrl": url, "indexUrl": INDEX, "sha256": sha256(raw),
            "file": filename, "dataSha256": sha256(compressed), "normalizedSha256": sha256(normalized),
            "periodStart": f"{end - 1}-04-01", "periodEnd": f"{end}-03-31", "currency": "CAD",
            "scope": "employee-remuneration", "category": "employee-remuneration",
            "scopeDescription": "Named employee payments equal to or greater than $75,000; employee schedule only",
            "threshold": 75000, "thresholdComparison": ">=", "nameDisclosure": "named",
            "rowCount": len(rows), "totalRemuneration": validation["namedRemunerationSum"],
            "totalDisclosedExpenses": validation["namedExpensesSum"], "status": "verified",
            "verifiedOn": args.verified_on, "validation": validation,
            "notes": [
                "Employee schedule only. The published threshold is inclusive: payments equal to or greater than $75,000. Under-threshold aggregates are excluded; job titles are not supplied.",
                "The source states that the schedule is on a cash basis and is not directly reconcilable to accrual-basis financial statements. Employer benefit costs, contracted labour and physician fees are excluded from this schedule.",
                "Names, including initials and punctuation, are retained as printed. Repeated names remain separate rows and do not establish a unique person.",
                "Dash expense cells remain missing, not zero; printed negative recoveries and explicit zero amounts are preserved.",
                f"Displayed named remuneration minus its printed subtotal is ${validation['remunerationResidual']:,}; the corresponding expense difference is ${validation['expensesResidual']:,}. Both fit the recorded independent whole-dollar rounding bound; the cause is not established, no amount is adjusted and exact reconciliation is not claimed.",
            ],
        }
        comparison = compare_compiled_baseline(rows, year)
        if comparison is not None:
            validation["compiledBaselineComparison"] = comparison
        sources.append(source)
        print(f"Validated {year}: {len(rows):,} rows, all physical pages and row coordinates checked.", flush=True)
    registry = {
        "version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "sources": sources,
        "coverageNotes": ["Ten original employee schedules cover FY2015/16 through FY2024/25. FY2025/26 employee remuneration was not linked from the issuer's financial-reporting index when checked; executive and board reports are separate cohorts."],
    }
    # No output changes until all ten sources have passed.
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, raw in pending.items():
        (args.output / filename).write_bytes(raw)
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"Imported {len(sources)} Fraser Health schedules, {sum(source['rowCount'] for source in sources):,} records.")


if __name__ == "__main__":
    main()
