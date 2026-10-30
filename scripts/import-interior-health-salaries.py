#!/usr/bin/env python3
"""Import the eleven reviewed Interior Health employee schedules, FY2014/15–2024/25.

Poppler layout extraction is compared with a complete independent PyMuPDF word-
coordinate reconstruction. All pages, rows, fiscal headings, footers, aggregate
controls and source fingerprints are checked before any accepted file is written.
The offline salary build consumes the deterministic normalized gzip files.
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

import fitz

ROOT = Path(__file__).resolve().parents[1]
INDEX = "https://www.interiorhealth.ca/about-ih/accountability/financial-reporting"
BASE = "https://www.interiorhealth.ca/sites/default/files/PDFS/"
SLUG = "interior-health"
HEADER = re.compile(r"EMPLOYEE NAME\s+REMUNERATION\s+EXPENSES")
ROW = re.compile(r"(.+?)\s{2,}\$?\s*(\d{1,3}(?:,\d{3})*)\s{2,}\$?\s*([,\d()\-*\s]+)")
TOTAL_LABELS = ("Total Greater than $75,000", "Total Less than or equal to $75,000", "Grand Total")
# Source SHA-256, pages, rows, displayed remuneration/expense sums, printed named subtotals.
REVIEWED = {
    2015: ("1a855bf7c2709ebc8f27f86638b1ca99f75f0e978c77d262166c34d18a446532", 65, 3408, 311631916, 4023715, 311631876, 4023665),
    2016: ("a2862553ce057d07d633300c354e3b69413ee909835f9fd6c8ad8c36b65e12ad", 78, 3538, 324074781, 3159511, 324074756, 3159455),
    2017: ("b2800e35e50f13b7d89de746fe1e6a4bf20dfddbc66b373df5135b5474616706", 93, 4233, 398638133, 4346681, 398638075, 4346602),
    2018: ("2c99b878151b8617a349caa732f6b9ee1f1b20a8950fde4603aa686ac2896c59", 90, 4084, 380402777, 4721409, 380402778, 4721330),
    2019: ("d7df21b3b35ed7bfd8df940f62b6c6b8bc5c49c65bb581baca56b58a28fce2b5", 98, 4447, 416996644, 5162058, 416996613, 5161932),
    2020: ("2dd2005c9d69553ec9db35a0ca9f54176d3f06e0f2d3640f41b5ae239feef840", 112, 5125, 485458710, 5188138, 485458701, 5188018),
    2021: ("950ad48c1f618ae12e5bca865733b9b0fd6e246c5aa6c137a8fafc606255ceeb", 138, 6320, 616614075, 2878715, 616614060, 2878538),
    2022: ("dca0f5e1d47e2c6456fd3d49c87dd62b9d17b8f09f1bb3363cbdcad2c3a3389f", 145, 6611, 655762847, 3892164, 655762830, 3892046),
    2023: ("bb31af4b09978ae13738f036221da93e604c719fdea67f30e614c348b4f3feb8", 158, 7222, 722913933, 5766902, 722913871, 5766700),
    2024: ("5f05258e6b0d5a523f4cb4be126ed629e552d274ffcc88d5ce96c094fe6f9990", 208, 9540, 1044940648, 9971502, 1044940593, 9971261),
    2025: ("6d32e3fbbf601db59db549ca983852efbcc77507dc945606f2202f807c6d1661", 236, 10836, 1209331334, 13856783, 1209331297, 13857050),
}
# This exact printed row was visually verified. The source still labels its
# cohort >$75,000; do not change the cohort to >= or invent undisclosed cents.
BOUNDARY_ROWS = {2021: [[SLUG, "BAXTER,LOUISE M", None, 75000, None, 8]]}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def amount(token: str) -> int | None:
    value = "".join(token.split())
    if value == "-":
        return None
    if not re.fullmatch(r"(?:-?\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))\*?", value):
        raise ValueError(f"Unexpected monetary cell: {token!r}")
    value = value.rstrip("*")
    if value.startswith("("):
        value = "-" + value[1:-1]
    return int(value.replace(",", ""))


def parse_row(line: str, page: int, fiscal_end: int) -> list:
    match = ROW.fullmatch(line.strip())
    if not match:
        raise ValueError(f"Unparsed employee line on physical page {page}: {line!r}")
    name, pay, expenses = match.groups()
    if "," not in name or any(c.isdigit() for c in name):
        raise ValueError(f"Unreviewed employee-name structure: {name!r}")
    row = [SLUG, name, None, amount(pay), amount(expenses), page]
    if row[3] <= 75000 and row not in BOUNDARY_ROWS.get(fiscal_end, []):
        raise ValueError(f"Unexpected row at/below the published >$75,000 threshold: {row!r}")
    return row


def parse_summary(text: str, title: str) -> tuple[int, int]:
    matches = re.findall(re.escape(title) + r"\s*\$?\s*([\d,]+)\s*\$?\s*([\d,]+)", text)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one printed subtotal: {title}")
    return tuple(amount(value) for value in matches[0])


def parse_layout(text: str, fiscal_end: int) -> tuple[list[list], dict]:
    if "\ufffd" in text:
        raise ValueError("Replacement character in extracted PDF text")
    pages = text.split("\f")
    if pages[-1].strip():
        raise ValueError("Missing terminal PDF page separator")
    pages.pop()
    if not pages:
        raise ValueError("No PDF pages")
    headings = re.findall(r"For the Year Ending March 31, (\d{4})", text)
    if headings != [str(fiscal_end)] or "Schedule of Employee Remuneration and Expenses" not in pages[0]:
        raise ValueError("Missing or conflicting fiscal period or schedule heading")
    rows, page_counts = [], []
    for number, page in enumerate(pages, 1):
        lines = [line for line in page.splitlines() if line.strip()]
        if not lines or lines[-1].strip() != f"Page {number} of {len(pages)}":
            raise ValueError(f"Missing or nonsequential footer on physical page {number}")
        headers = [at for at, line in enumerate(lines) if HEADER.fullmatch(line.strip())]
        if len(headers) != 1:
            raise ValueError(f"Expected one employee table header on physical page {number}")
        before = len(rows)
        summary_started = False
        for line in lines[headers[0] + 1:-1]:
            if line.strip().startswith("Total"):
                if number != len(pages):
                    raise ValueError("Aggregate section appears before the final employee page")
                summary_started = True
                break
            rows.append(parse_row(line, number, fiscal_end))
        if number == len(pages) and not summary_started:
            raise ValueError("Final employee page has no named subtotal")
        if len(rows) == before:
            raise ValueError(f"Employee page {number} has no parsed employee rows")
        page_counts.append(len(rows) - before)
    named, below, grand = (parse_summary(text, label) for label in TOTAL_LABELS)
    residuals = tuple(a + b - c for a, b, c in zip(named, below, grand))
    if any(abs(value) > 1.5 for value in residuals):
        raise ValueError("Printed subtotals differ from grand totals beyond the three-cell whole-dollar rounding bound")
    counts = Counter(row[1] for row in rows)
    return rows, {
        "physicalPdfPages": [1, len(pages)], "rowsPerPhysicalPage": page_counts,
        "internalFiscalYearEnd": fiscal_end, "allPageFootersSequential": True,
        "unparsedEmployeeLines": 0, "summaryPhysicalPdfPages": [len(pages)],
        "printedNamedRemuneration": named[0], "printedNamedExpenses": named[1],
        "underThresholdRemunerationExcluded": below[0], "underThresholdExpensesExcluded": below[1],
        "printedAllEmployeeRemuneration": grand[0], "printedAllEmployeeExpenses": grand[1],
        "printedSubtotalRemunerationResidual": residuals[0], "printedSubtotalExpenseResidual": residuals[1],
        "printedSubtotalsReconcileExactly": residuals == (0, 0),
        "printedSubtotalRoundingCompatibilityBound": 1.5,
        "repeatedDisclosedNames": [{"name": name, "rows": count} for name, count in counts.items() if count > 1],
        "exactDuplicateSourceRows": sum(count - 1 for count in Counter(tuple(row[:5]) for row in rows).values() if count > 1),
    }


def validate_coordinates(pdf: Path, rows: list[list], expected_pages: int) -> int:
    """Use an independent PDF engine and spatial row reconstruction for every cell."""
    def center(word):
        return (word[1] + word[3]) / 2
    by_page = defaultdict(list)
    for row in rows:
        by_page[row[5]].append(row)
    checked = 0
    with fitz.open(pdf) as document:
        if len(document) != expected_pages:
            raise ValueError("PDF engines disagree on page count")
        for number, page in enumerate(document, 1):
            words = page.get_text("words")
            pay_headers = [word for word in words if word[4] == "REMUNERATION"]
            expense_headers = [word for word in words if word[4] == "EXPENSES"]
            if len(pay_headers) != 1 or len(expense_headers) != 1:
                raise ValueError(f"Coordinate table headings are missing or repeated on physical page {number}")
            ph, eh = pay_headers[0], expense_headers[0]
            bottom = min([center(word) - 3 for word in words if word[4] in ("Total", "Page") and center(word) > center(ph)]
                         + [page.rect.height - 25])
            salaries = sorted([word for word in words if re.fullmatch(r"\d{1,3}(?:,\d{3})*", word[4])
                               and ph[0] - 30 <= word[0] and word[2] < eh[0] - 1
                               and center(ph) + 2 < center(word) < bottom], key=center)
            observed = []
            for pay in salaries:
                line = sorted([word for word in words if abs(center(word) - center(pay)) < 2], key=lambda word: word[0])
                name = " ".join(word[4] for word in line if word[2] < pay[0] - 1 and word[4] != "$")
                expense = " ".join(word[4] for word in line if word[0] > pay[2] + 1 and word[4] != "$")
                observed.append([SLUG, name, None, amount(pay[4]), amount(expense), number])
            if observed != by_page[number]:
                mismatch = next(((a, b) for a, b in zip(observed, by_page[number]) if a != b), None)
                raise ValueError(f"PyMuPDF row mismatch on physical page {number}: {len(observed)} vs {len(by_page[number])}; {mismatch!r}")
            checked += len(observed)
    return checked


def validate_totals(rows: list[list], validation: dict, reviewed: tuple, end: int) -> None:
    _, pages, count, pay, expense, named_pay, named_expense = reviewed
    sums = sum(row[3] for row in rows), sum(row[4] for row in rows if row[4] is not None)
    observed = (validation["physicalPdfPages"][1], len(rows), *sums,
                validation["printedNamedRemuneration"], validation["printedNamedExpenses"])
    if observed != (pages, count, pay, expense, named_pay, named_expense):
        raise ValueError(f"Reviewed page/row counts or monetary controls changed: {observed!r}")
    if validation["exactDuplicateSourceRows"]:
        raise ValueError("Unexpected identical employee rows require separate review")
    boundary = [row for row in rows if row[3] <= 75000]
    if boundary != BOUNDARY_ROWS.get(end, []):
        raise ValueError("Reviewed displayed-threshold exception changed")
    residuals = pay - named_pay, expense - named_expense
    bound = (len(rows) + 1) / 2
    if any(abs(value) > bound for value in residuals):
        raise ValueError("Named subtotal residual exceeds displayed-dollar rounding compatibility bound")
    validation.update({
        "sourceFingerprintLocked": True, "namedRemunerationSum": pay, "namedExpensesSum": expense,
        "remunerationResidual": residuals[0], "expensesResidual": residuals[1],
        "summaryTotalReconciled": residuals == (0, 0),
        "displayedDollarRoundingCompatibilityBound": bound, "residualsWithinDisplayedDollarRoundingBound": True,
        "negativeExpenseRows": sum(row[4] is not None and row[4] < 0 for row in rows),
        "explicitZeroExpenseRows": sum(row[4] == 0 for row in rows),
        "missingExpenseRows": sum(row[4] is None for row in rows),
        "visuallyReviewedHeaderPhysicalPages": [1], "visuallyReviewedSummaryPhysicalPages": [pages],
        "visuallyReviewedNegativeExpenseRows": [
            {"name": row[1], "remuneration": row[3], "expenses": row[4], "physicalPdfPage": row[5]}
            for row in rows if row[4] is not None and row[4] < 0
        ],
        "reviewedDisplayedThresholdExceptions": [
            {"name": row[1], "remuneration": row[3], "expenses": row[4], "physicalPdfPage": row[5],
             "reason": "The original PDF prints 75,000 in its >75,000 named schedule. Retained exactly; underlying unrounded amount is unknown."}
            for row in boundary
        ],
    })


def compare_compiled_baseline(all_rows: dict[int, list[list]]) -> dict:
    path = ROOT / "research/salaries/compiled-baseline.json.gzip"
    raw = path.read_bytes()
    baseline = json.loads(gzip.decompress(raw))
    employer = next(entry for entry in baseline["employers"] if entry["slug"] == SLUG)
    def name_key(name):
        return tuple("".join(c for c in part.casefold() if c.isalnum()) for part in name.split(",", 1))
    results = []
    for index, label in enumerate(baseline["years"]):
        old = [row for row in employer["rows"] if row[4] == index]
        compiled = Counter((name_key(row[0]), row[2]) for row in old)
        candidates = []
        for end, rows in all_rows.items():
            official = Counter((name_key(row[1]), row[3]) for row in rows)
            candidates.append({
                "sourcePeriod": f"{end - 1}/{end % 100:02d}", "officialRows": len(rows),
                "normalizedNamePayMatches": sum((compiled & official).values()),
                "compiledUnmatched": sum((compiled - official).values()),
                "sourceUnmatched": sum((official - compiled).values()),
            })
        result = {"compiledLabel": label, "compiledRows": len(old), "sourcePeriodComparisons": candidates}
        end = int(label[:4]) + 1
        official = Counter((name_key(row[1]), row[3]) for row in all_rows[end])
        unmatched = compiled - official
        result["compiledRowsUnmatchedInSameFiscalPeriod"] = [
            {"name": row[0], "position": row[1], "remuneration": row[2], "expenses": row[3]}
            for row in old if (name_key(row[0]), row[2]) in unmatched
        ]
        if label == "2017/18":
            # Diagnostic only: the compiler substituted digit zero for hyphens.
            repaired = Counter((name_key(row[0].replace("0", "-")), row[2]) for row in old)
            result["diagnosticAfterReplacingLegacyNameZeroWithHyphen"] = {
                "matches": sum((repaired & official).values()),
                "compiledUnmatched": sum((repaired - official).values()),
                "note": "Comparison only. All accepted names come unchanged from the original PDF; no person-identity matching or baseline mutation.",
            }
        results.append(result)
    return {
        "baselineFile": str(path.relative_to(ROOT)), "baselineSha256": sha256(raw),
        "method": "Multiset name/pay comparison across every recovered source year. Name keys remove case, whitespace and punctuation while retaining the surname/given-name boundary. No fuzzy or identity matching; amounts are unchanged.",
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-additional-sources"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/interior-health")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    pending, sources, all_rows = {}, [], {}
    for end, reviewed in REVIEWED.items():
        name = ("schedule-of-employee-remuneration-and-expenses-" if end == 2020 else "schedule-of-remuneration-and-expenses-") + str(end) + ".pdf"
        url = BASE + name
        pdf = args.cache / f"interior-health-{end}.pdf"
        if not pdf.exists():
            if args.offline:
                raise ValueError(f"Missing source PDF: {pdf}")
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PofBC salary source importer"})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            if not raw.startswith(b"%PDF-"):
                raise ValueError(f"Not a PDF: {url}")
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(raw)
        raw = pdf.read_bytes()
        if sha256(raw) != reviewed[0]:
            raise ValueError(f"Interior Health {end} PDF bytes changed; review before importing")
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        rows, validation = parse_layout(text, end)
        validation["rowsCheckedWithIndependentPdfEngine"] = validate_coordinates(pdf, rows, reviewed[1])
        validation["independentPdfEngine"] = "PyMuPDF word coordinates; primary extraction uses Poppler layout text"
        validate_totals(rows, validation, reviewed, end)
        label = f"{end - 1}-{end % 100:02d}"
        year = label.replace("-", "/")
        filename = label + ".json.gzip"
        normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
        compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
        pending[filename] = compressed
        all_rows[end] = rows
        notes = [
            "Named employee remuneration only. The report labels this cohort greater than $75,000; under-threshold aggregate totals are excluded. No job titles are published in these schedules.",
            "Published names, punctuation, initials and separate repeated-name records are preserved. A disclosed name does not prove unique identity.",
            "Dash expense cells remain missing, not explicit zero. Separated minus signs and parenthesized negative expenses remain negative; footnote markers are metadata, not monetary digits.",
            f"Displayed named remuneration minus the printed subtotal is ${validation['remunerationResidual']:,}; expenses differ by ${validation['expensesResidual']:,}. These fit the recorded whole-dollar rounding compatibility bound, but their cause is not established. No values are adjusted; exact reconciliation is not claimed.",
        ]
        if end >= 2020:
            notes.append("The source states that this is a cash-basis report and negative expenses may result from timing of third-party reimbursements.")
        if end == 2021:
            notes.append("One reviewed source row, BAXTER,LOUISE M on physical page 8, prints exactly $75,000 despite the >$75,000 cohort label. The source value is retained; no undisclosed cents or different threshold are inferred.")
        sources.append({
            "id": "interior-health-sofi-" + label, "employerSlug": SLUG, "employerName": "Interior Health",
            "sector": "Health authorities", "year": year,
            "title": f"Interior Health Schedule of Employee Remuneration and Expenses {year}",
            "sourceUrl": url, "indexUrl": INDEX, "sha256": sha256(raw), "pdfBytes": len(raw),
            "file": filename, "dataSha256": sha256(compressed), "normalizedSha256": sha256(normalized),
            "periodStart": f"{end - 1}-04-01", "periodEnd": f"{end}-03-31", "periodType": "fiscal", "currency": "CAD",
            "scope": "employee-remuneration", "category": "employee-remuneration",
            "scopeDescription": "Named employees in the source's greater-than-$75,000 schedule; published boundary values retained",
            "threshold": 75000, "thresholdComparison": ">", "nameDisclosure": "named",
            "rowCount": len(rows), "totalRemuneration": validation["namedRemunerationSum"],
            "totalDisclosedExpenses": validation["namedExpensesSum"], "status": "verified",
            "verifiedOn": args.verified_on, "validation": validation, "notes": notes,
        })
        print(f"Validated {year}: {len(rows):,} rows; all {reviewed[1]} pages checked with two PDF engines.", flush=True)
    comparison = compare_compiled_baseline(all_rows)
    registry = {
        "version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "sources": sources,
        "coverageNotes": ["Eleven original employee schedules cover every fiscal year from 2014/15 through 2024/25. Source-reported remuneration is not necessarily annual base salary or a workforce census.",
                          "The three compiled periods best match the same fiscal-period PDFs, with incomplete rows and transcription/scope differences. See compiled-comparison.json; no global municipal-style period relabelling is applied."],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, raw in pending.items():
        (args.output / filename).write_bytes(raw)
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    (args.output / "compiled-comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n")
    print(f"Validated {len(sources)} Interior Health schedules, {sum(source['rowCount'] for source in sources):,} rows.")


if __name__ == "__main__":
    main()
