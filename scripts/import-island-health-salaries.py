#!/usr/bin/env python3
"""Verify ten Island Health employee PDFs; accept eight and retain two held years.

Every row is reconstructed with independent PDF engines (Poppler layout text and
PyMuPDF coordinates). Source fingerprints, exact decimals, all employee pages,
printed controls and reviewed glyph transcriptions are required. Two unresolved
source inconsistencies stay in staging and never acquire accepted manifest paths.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "research/salaries/island-health"
INDEX = "https://www.islandhealth.ca/about-us/plans-reports-and-policies/financial-reports"
SLUG = "island-health"
NUMBER = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?"
ROW = re.compile(r"(.+?)\s{2,}\$?\s*(" + NUMBER + r")\s+\$?\s*([,\d.()\-‐\s]+)")
SUMMARY_START = re.compile(r"(?:Total payments|TOTAL PAYMENTS|Sub(?:t)?otal:)", re.I)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def amount(token: str) -> Decimal | None:
    value = "".join(token.split()).replace("‐", "-")
    if value == "-":
        return None
    if not re.fullmatch(r"(?:-?" + NUMBER + r"|\(" + NUMBER + r"\))", value):
        raise ValueError(f"Unexpected monetary cell: {token!r}")
    if value.startswith("("):
        value = "-" + value[1:-1]
    return Decimal(value.replace(",", ""))


def json_number(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(f"Unsupported JSON type: {type(value)}")


def reviewed_expense_token(token: str, year: str, page: int, name: str) -> str:
    # The exact source cell was visually read on physical page 295. Do not apply
    # a global Unicode-to-digit mapping to names or other cells.
    if (year, page, name, token.strip()) == ("2024/25", 295, "MACNEIL,KATHRYN E", "1ϯ,ϭϭϳ"):
        return "13,117"
    return token


def normalize_reviewed_row(line: str, year: str, page: int) -> str:
    if year == "2024/25" and page == 295 and line.strip().startswith("MACNEIL,KATHRYN E"):
        if line.count("1ϯ,ϭϭϳ") != 1:
            raise ValueError("Reviewed misencoded employee cell changed")
        return line.replace("1ϯ,ϭϭϳ", "13,117")
    return line


def parse_row(line: str, page: int, year: str) -> list:
    match = ROW.fullmatch(normalize_reviewed_row(line, year, page).strip())
    if not match:
        raise ValueError(f"Unparsed employee line: {year} physical page {page}: {line!r}")
    name, pay, expenses = match.groups()
    if "," not in name or any(c.isdigit() for c in name):
        raise ValueError(f"Unexpected employee name: {name!r}")
    row = [SLUG, name, None, amount(pay), amount(expenses), page]
    if row[3] <= 75000:
        raise ValueError("Unexpected employee row at or below $75,000; requires fresh review")
    return row


def allowed_headers(year: str) -> set[str]:
    start = int(year[:4]); end = start + 1
    return {
        "vancouver island health authority",
        f"financial information act - {year} report",
        f"financial information act - {start}/{end} report",
        "schedule of remuneration and expenses",
        "for employees receiving remuneration exceeding $75,000",
        "name remuneration travel & expenses", "employee name remuneration expenses", "name remuneration expenses",
        "schedule showing remuneration and expenses paid to or on behalf of each employee",
        f"for the fiscal year ended march 31, {end} (unaudited)",
    }


def parse_controls(page: str, reviewed: dict) -> list | None:
    expected = reviewed["printedControls"]
    if expected is None:
        if SUMMARY_START.search(page):
            raise ValueError("Unexpected printed controls in a previously unsummarized source")
        return None
    text = page
    if reviewed["year"] == "2024/25":
        text = text.replace("\x03", " ")
        for raw, visual in (("17,0Ϭϱ,ϬϴϮ", "17,005,082"), ("27,5ϴϳ,ϵϯϬ", "27,587,930")):
            if text.count(raw) != 1:
                raise ValueError("Reviewed control-total glyph transcription changed")
            text = text.replace(raw, visual)
    if int(reviewed["year"][:4]) < 2022:
        labels = ("Total payments equal to or greater than $75,000", "Total payments less than $75,000", "Total payments to all Island Health employees")
        found = []
        for label in labels:
            matches = re.findall(re.escape(label) + r"\s*\$?\s*([\d,]+)\s*\$?\s*([\d,]+)", text, re.I)
            if len(matches) != 1:
                raise ValueError(f"Missing or ambiguous printed subtotal: {label}")
            found.append([amount(token) for token in matches[0]])
    else:
        patterns = (
            r"Sub(?:t)?otal:.*?remuneration exceeding \$75,000\s+([\d,]+)\s+([\d,]+)",
            r"Consolidated total:.*?remuneration less than \$75,000\s+([\d,]+)\s+([\d,]+)",
            r"Total: Remuneration to all Island Health Employees\s+\$\s*([\d,]+)\s*\$\s*([\d,]+)",
        )
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.S)
            if len(matches) != 1:
                raise ValueError(f"Missing or ambiguous SOFI subtotal: {pattern}")
            found.append([amount(token) for token in matches[0]])
    if found != expected:
        raise ValueError(f"Printed controls differ from visual review: {found!r}")
    return found


def parse_layout(text: str, reviewed: dict) -> tuple[list[list], dict]:
    pages = text.split("\f")
    if pages[-1].strip():
        raise ValueError("Missing terminal PDF page separator")
    pages.pop()
    if len(pages) != reviewed["pdfPages"]:
        raise ValueError("Reviewed physical PDF page count changed")
    year = reviewed["year"]; start, last = reviewed["employeePages"]
    end_year = int(year[:4]) + 1
    rows, page_counts = [], []
    headings = allowed_headers(year)
    for number in range(start, last + 1):
        page = pages[number - 1]
        if "\ufffd" in page:
            raise ValueError(f"Replacement character in employee page {number}")
        lines = [line for line in page.splitlines() if line.strip()]
        if end_year == 2016:
            footer = f"Page {number} of {last}"
        elif 2020 <= end_year <= 2022 and number > 1:
            footer = f"Page {number}"
        elif end_year >= 2023:
            footer = str(number - 1)
        else:
            footer = None
        if footer and lines[-1].strip() != footer:
            raise ValueError(f"Nonsequential printed footer: {year} page {number}")
        if end_year >= 2023:
            if f"For the Fiscal Year Ended March 31, {end_year}" not in page or "Each Employee" not in page:
                raise ValueError("Employee section boundary/period mismatch in full SOFI")
        elif number == 1 or end_year in (2016, 2017, 2020, 2021, 2022):
            observed = re.findall(r"Financial Information Act\s*-\s*(\d{4}/\d{2,4}) Report", page, re.I)
            if observed not in ([year], [f"{end_year - 1}/{end_year}"]):
                raise ValueError(f"Missing fiscal heading on employee page {number}")
        before = len(rows); summary = False; began = False
        for line in lines:
            value = line.strip()
            if footer and value == footer:
                continue
            if SUMMARY_START.match(value):
                if number != last or reviewed["printedControls"] is None:
                    raise ValueError("Unexpected aggregate boundary inside employee table")
                summary = True
                break
            normalized_header = " ".join(value.lower().split())
            if not began and normalized_header in headings:
                continue
            rows.append(parse_row(line, number, year)); began = True
        if number == last and reviewed["printedControls"] is not None and not summary:
            raise ValueError("Missing final employee subtotals")
        if len(rows) == before:
            raise ValueError(f"Empty employee page {number}")
        page_counts.append(len(rows) - before)
    controls = parse_controls(pages[last - 1], reviewed)
    declared = reviewed["declaredNamedCount"]
    if declared is not None:
        narrative = pages[start - 2]
        pattern = r"(?:there were|there were\s+)\s*([\d,]+) employees who earned in excess of \$75,000"
        counts = re.findall(pattern, narrative)
        if len(counts) != 1 or int(counts[0].replace(",", "")) != declared:
            raise ValueError("Declared employee count does not match reviewed scope page")
        if "does not include amounts paid under severance agreements" not in narrative:
            raise ValueError("Reviewed employee remuneration scope changed")
    return rows, {
        "pdfPages": len(pages), "physicalPdfPages": [start, last], "rowsPerPhysicalPage": page_counts,
        "unparsedEmployeeLines": 0, "sourceFiscalYearEnd": end_year,
        "printedFooterValidation": "Sequential on every employee page where the source prints a footer; physical pages counted independently for sources without footers",
        "printedNamedRemuneration": controls[0][0] if controls else None,
        "printedNamedExpenses": controls[0][1] if controls else None,
        "underThresholdRemunerationExcluded": controls[1][0] if controls else None,
        "underThresholdExpensesExcluded": controls[1][1] if controls else None,
        "printedAllEmployeeRemuneration": controls[2][0] if controls else None,
        "printedAllEmployeeExpenses": controls[2][1] if controls else None,
        "printedControlsAvailable": controls is not None, "sourceDeclaredNamedCount": declared,
        "scopeDefinitionPhysicalPage": start - 1 if start > 1 else None,
    }


def validate_coordinates(pdf: Path, rows: list[list], reviewed: dict) -> int:
    def center(word):
        return (word[1] + word[3]) / 2
    by_page = defaultdict(list)
    for row in rows:
        by_page[row[5]].append(row)
    start, last = reviewed["employeePages"]; end = int(reviewed["year"][:4]) + 1
    checked = 0
    with fitz.open(pdf) as document:
        if len(document) != reviewed["pdfPages"]:
            raise ValueError("Independent PDF engine page count differs")
        first = document[start - 1].get_text("words")
        ph = next(word for word in first if word[4].lower() == "remuneration" and word[0] > 300)
        eh = next(word for word in first if word[4].lower() == "expenses" and word[0] > 450)
        for number in range(start, last + 1):
            page = document[number - 1]; words = page.get_text("words")
            bottom = min([center(word) - 3 for word in words if word[4] in ("Total", "TOTAL", "Subtotal:", "Subotal:", "Page")]
                         + [page.rect.height - 20])
            if number == start:
                top = center(ph) + 2
            elif end <= 2017 or end >= 2023:
                top = max(center(word) for word in words if word[4] == "Name") + 2
            elif end in (2018, 2019):
                top = 0
            else:
                top = 70
            salaries = sorted([word for word in words if re.fullmatch(NUMBER, word[4])
                               and ph[0] - 30 < word[0] and word[2] < eh[0] - 3
                               and top < center(word) < bottom], key=center)
            observed = []
            for pay in salaries:
                line = sorted([word for word in words if abs(center(word) - center(pay)) < 2], key=lambda word: word[0])
                name = " ".join(word[4] for word in line if word[2] < pay[0] - 1 and word[4] != "$")
                expense = " ".join(word[4] for word in line if word[0] > pay[2] + 1 and word[4] != "$")
                expense = reviewed_expense_token(expense, reviewed["year"], number, name)
                observed.append([SLUG, name, None, amount(pay[4]), amount(expense), number])
            if observed != by_page[number]:
                mismatch = next(((a, b) for a, b in zip(observed, by_page[number]) if a != b), None)
                raise ValueError(f"Independent PDF reconstruction differs on physical page {number}: {len(observed)} vs {len(by_page[number])}; {mismatch!r}")
            checked += len(observed)
    return checked


def validate_controls(rows: list[list], validation: dict, reviewed: dict) -> None:
    pay = sum(row[3] for row in rows)
    expenses = sum(row[4] for row in rows if row[4] is not None)
    if (len(rows), pay, expenses) != (reviewed["rowCount"], Decimal(reviewed["remunerationSum"]), Decimal(reviewed["expenseSum"])):
        raise ValueError("Reviewed row count or exact monetary sums changed")
    duplicated = sum(count - 1 for count in Counter(tuple(row[:5]) for row in rows).values() if count > 1)
    if duplicated:
        raise ValueError("Unexpected identical source rows require review")
    negatives = [[row[1], str(row[3]), str(row[4]), row[5]] for row in rows if row[4] is not None and row[4] < 0]
    if negatives != reviewed["negativeRows"]:
        raise ValueError("Visually reviewed negative rows changed")
    counts = Counter(row[1] for row in rows)
    validation.update({
        "sourceFingerprintLocked": True, "namedRemunerationSum": pay, "namedExpensesSum": expenses,
        "exactDuplicateSourceRows": duplicated,
        "repeatedDisclosedNames": [{"name": name, "rows": count} for name, count in counts.items() if count > 1],
        "missingExpenseRows": sum(row[4] is None for row in rows),
        "explicitZeroExpenseRows": sum(row[4] == 0 for row in rows),
        "negativeExpenseRows": len(negatives),
        "allNegativeExpenseRowsVisuallyReviewed": True,
        "visuallyReviewedHeaderPhysicalPages": [reviewed["employeePages"][0]],
        "visuallyReviewedEndAndControlPhysicalPages": [reviewed["employeePages"][1]],
        "sourceDeclaredCountResidual": len(rows) - reviewed["declaredNamedCount"] if reviewed["declaredNamedCount"] is not None else None,
    })
    if reviewed["printedControls"] is not None:
        named, below, grand = reviewed["printedControls"]
        residuals = pay - named[0], expenses - named[1]
        bound = Decimal(len(rows) + 1) / 2
        compatible = all(abs(value) <= bound for value in residuals)
        validation.update({
            "remunerationResidual": residuals[0], "expensesResidual": residuals[1],
            "summaryTotalReconciled": residuals == (0, 0),
            "displayedDollarRoundingCompatibilityBound": bound,
            "residualsWithinDisplayedDollarRoundingBound": compatible,
            "printedSubtotalRemunerationResidual": named[0] + below[0] - grand[0],
            "printedSubtotalExpenseResidual": named[1] + below[1] - grand[1],
        })
        if not reviewed["heldReason"] and not compatible:
            raise ValueError("Accepted source monetary controls do not reconcile within rounding bounds")
    else:
        validation.update({"summaryTotalReconciled": None,
                           "controlLimitation": "The complete standalone employee PDF publishes neither named subtotals nor an independent declared row count. All source pages and rows were independently reconstructed; no exact total reconciliation is claimed."})
    if not reviewed["heldReason"] and validation["sourceDeclaredCountResidual"] not in (None, 0):
        raise ValueError("Accepted source has an unresolved declared employee count discrepancy")


def compiled_comparison(rows_by_year: dict) -> dict:
    path = ROOT / "research/salaries/compiled-baseline.json.gzip"; raw = path.read_bytes()
    base = json.loads(gzip.decompress(raw)); employer = next(entry for entry in base["employers"] if entry["slug"] == SLUG)
    def key(name):
        return tuple("".join(c for c in part.casefold() if c.isalnum()) for part in name.split(",", 1))
    result = []
    for index, year in enumerate(base["years"]):
        old = [row for row in employer["rows"] if row[4] == index]
        compiled = Counter((key(row[0]), Decimal(str(row[2]))) for row in old)
        candidates = []
        for period, rows in rows_by_year.items():
            official = Counter((key(row[1]), row[3]) for row in rows)
            rounded = Counter((key(row[1]), row[3].quantize(Decimal(1), rounding=ROUND_HALF_EVEN)) for row in rows)
            half_up = Counter((key(row[1]), row[3].quantize(Decimal(1), rounding=ROUND_HALF_UP)) for row in rows)
            candidates.append({"sourcePeriod": period, "sourceRows": len(rows),
                               "exactNormalizedNamePayMatches": sum((compiled & official).values()),
                               "matchesAfterSourceWholeDollarRoundingForComparisonOnly": sum((compiled & rounded).values()),
                               "matchesAfterSourceWholeDollarHalfUpForComparisonOnly": sum((compiled & half_up).values())})
        result.append({"compiledLabel": year, "compiledRows": len(old), "sourcePeriodComparisons": candidates})
    return {"baselineFile": str(path.relative_to(ROOT)), "baselineSha256": sha256(raw),
            "method": "Multiset comparison across all ten source periods. Name keys normalize case, punctuation and whitespace, preserving the surname/given-name boundary. Whole-dollar ROUND_HALF_EVEN and ROUND_HALF_UP are comparison-only diagnostics; accepted source cents are never rounded. No fuzzy name or identity inference.",
            "results": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc_health_sources"))
    parser.add_argument("--output", type=Path, default=COLLECTION)
    parser.add_argument("--reviewed-inputs", type=Path, default=COLLECTION / "reviewed-inputs.json")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    review = json.loads(args.reviewed_inputs.read_text())
    pending, sources, rows_by_year = {}, [], {}
    for reviewed in review["sources"]:
        year = reviewed["year"]; label = year.replace("/", "-"); end = int(year[:4]) + 1
        pdf = args.cache / ("island-" + label + ".pdf")
        if not pdf.exists():
            if args.offline:
                raise ValueError(f"Missing source PDF: {pdf}")
            request = urllib.request.Request(reviewed["sourceUrl"], headers={"User-Agent": "Mozilla/5.0 PofBC salary source importer"})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            if not raw.startswith(b"%PDF-"):
                raise ValueError("Downloaded content is not a PDF")
            pdf.parent.mkdir(parents=True, exist_ok=True); pdf.write_bytes(raw)
        raw = pdf.read_bytes()
        if sha256(raw) != reviewed["sha256"]:
            raise ValueError(f"Source bytes changed for {year}; fresh review required")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        rows, validation = parse_layout(text, reviewed)
        validation["rowsCheckedWithIndependentPdfEngine"] = validate_coordinates(pdf, rows, reviewed)
        validation["independentPdfEngine"] = "PyMuPDF word coordinates; primary extraction uses Poppler layout text"
        validate_controls(rows, validation, reviewed)
        rows_by_year[year] = rows
        normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":"), default=json_number).encode()
        compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
        held = reviewed["heldReason"] is not None
        filename = ("staging/" if held else "") + label + ".json.gzip"
        pending[filename] = compressed
        conflict = 2020 <= end <= 2022
        notes = [
            "Employee schedule only; board remuneration, supplier payments, severance schedules and financial-statement aggregates are excluded. No job titles are supplied in the employee table.",
            "Source names, separate repeated-name records, exact displayed cents, negative expenses and missing dash cells are retained. A disclosed name is not a verified unique identity.",
        ]
        if conflict:
            notes.append("The same report uses conflicting threshold wording: its cover says remuneration exceeding $75,000, while its named subtotal says equal to or greater than $75,000. All disclosed named rows actually exceed $75,000; no threshold rule is inferred from the contradiction.")
        if reviewed["printedControls"]:
            notes.append(f"Displayed named remuneration differs from the printed subtotal by ${validation['remunerationResidual']:,}; expenses differ by ${validation['expensesResidual']:,}. Individual amounts remain unchanged and exact reconciliation is not claimed.")
        else:
            notes.append("This standalone list publishes no named monetary subtotal or independent named employee count. Every physical page and row was reconstructed with two PDF engines; no unpublished reconciliation control is invented.")
        if 2020 <= end <= 2022:
            notes.append("The source describes cash-basis payments, excludes employer benefit costs, contracted labour and physician fees, and warns that it does not directly reconcile to accrual financial statements.")
        if end >= 2023:
            notes.append("The scope page includes salaries, wages, retroactive pay, vacation payouts, taxable benefits and retiring allowances; amounts paid under severance agreements are explicitly excluded.")
        if year == "2015/16":
            notes.append("The source mixes whole-dollar values with four rows containing cent-valued cells. Those exceptional printed values were visually checked and retained without rounding.")
        if year == "2017/18":
            notes.append("The source reports remuneration and numeric expenses to cents. The normalized data retains that precision; compiler whole-dollar matching is diagnostic only.")
        transcriptions = [entry for entry in review["glyphTranscriptions"] if entry["year"] == year]
        if transcriptions:
            validation["reviewedGlyphTranscriptions"] = transcriptions
            notes.append("Three narrowly identified misencoded PDF monetary cells were visually transcribed: one employee expense on physical page 295 and two aggregate expense totals on page 426. No global glyph repair is applied.")
        source = {
            "id": "island-health-sofi-" + label, "employerSlug": SLUG, "employerName": "Island Health",
            "sector": "Health authorities", "year": year, "title": f"Island Health employee remuneration and expenses {year}",
            "sourceUrl": reviewed["sourceUrl"], "indexUrl": INDEX, "sha256": sha256(raw), "pdfBytes": len(raw),
            "periodStart": f"{end - 1}-04-01", "periodEnd": f"{end}-03-31", "periodType": "fiscal", "currency": "CAD",
            "scope": "employee-remuneration", "category": "employee-remuneration",
            "scopeDescription": "Named employee schedule; cover says >$75,000, subtotal says >=$75,000" if conflict else "Named employee remuneration exceeding $75,000",
            "threshold": 75000, "thresholdComparison": "reported-conflict" if conflict else ">", "nameDisclosure": "named",
            "rowCount": len(rows), "totalRemuneration": validation["namedRemunerationSum"], "totalDisclosedExpenses": validation["namedExpensesSum"],
            "status": "held-for-review" if held else "verified", "verifiedOn": args.verified_on,
            "validation": validation, "notes": notes,
        }
        if held:
            source.update({"candidateFile": filename, "candidateDataSha256": sha256(compressed), "candidateNormalizedSha256": sha256(normalized),
                           "reason": reviewed["heldReason"], "nextAction": reviewed["heldReason"], "accepted": False})
        else:
            source.update({"file": filename, "dataSha256": sha256(compressed), "normalizedSha256": sha256(normalized)})
        sources.append(source)
        print(f"{'Held' if held else 'Validated'} {year}: {len(rows):,} rows; both PDF engines agree.", flush=True)
    registry = {"version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
                "sources": sources, "coverageNotes": ["Eight source years accepted; FY2022/23 and FY2023/24 retained only as held candidate schedules because unresolved source controls conflict. Held files have candidateFile paths only and cannot replace compiled rows."]}
    comparison = compiled_comparison(rows_by_year)
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, raw in pending.items():
        target = args.output / filename; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2, default=json_number) + "\n")
    (args.output / "compiled-comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n")
    print(f"Accepted {sum(s['rowCount'] for s in sources if s['status'] == 'verified'):,} rows; held {sum(s['rowCount'] for s in sources if s['status'] != 'verified'):,} candidate rows.")


if __name__ == "__main__":
    main()
