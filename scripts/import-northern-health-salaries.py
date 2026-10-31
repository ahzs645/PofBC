#!/usr/bin/env python3
"""Import five reviewed Northern Health employee remuneration PDF schedules.

Requires Poppler's pdftotext. The build uses the checked-in normalized JSON gzip
files and has no network/PDF dependency. Every layout row is independently checked
against PDF word coordinates, including its name, pay, expense and physical page.
Changed source bytes, omitted rows or unexpected reconciliation residuals fail.
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
BASE = "https://www.northernhealth.ca/sites/northern_health/files/about-us/reports/financial-accountability/documents/"
INDEX = "https://www.northernhealth.ca/about-us/accountability/reports/financial-accountability"
# Reviewed source fingerprint, physical pages, named rows, displayed pay/expense
# sums, and the corresponding printed named-employee subtotals.
REVIEWED = {
    "2020-21": ("9d551d4fe50c52ed1a832ae324baac8a26e5e37b3cb0eedaabb133f4c6106338", 53, 2500, 251919430, 2021847, 251919403, 2021783),
    "2021-22": ("cc479e28a8a90e7f51b665a4c08dab7e759c1c08da2f999e655dc7ad6071edbd", 61, 2755, 286328458, 2673393, 286328455, 2673340),
    "2022-23": ("8fded11f668f7c1fe6cb05bd6a67903a5db62000fd1dd21614ffb1ccb68fb894", 63, 2842, 294827198, 5030248, 294827175, 5030158),
    "2023-24": ("65a05177684e0d8cdb7727dc5b82d528993bf21c2879cea872bdd17e41a9dfd8", 82, 3645, 413792773, 8219619, 413792713, 8219505),
    "2024-25": ("6d608e1715f8fb5866c80ce16283c22650e90451cfb54e5ba15ddb4a8739b81f", 103, 4379, 501013809, 13308150, 501013796, 13307919),
}
NAMES_REVIEWED = {
    "2021-22": ["Laferriere, Joanna_Estate"],
    "2023-24": ["Masocol, Liza_Estate Of", "Mason/ wiens, Kimberly", "Togi, Helen_Estate Of", "McKinnon, Niamh Grace, Marg"],
}
HEADER = re.compile(r"Employee\s+REMUNERATION\s+EXPENSES")
ROW = re.compile(r"^\s*([^0-9]+?,[^0-9]+?)\s{2,}(\d[\d,]*)\s*(.*?)\s*$")
NS = {"x": "http://www.w3.org/1999/xhtml"}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def amount(value: str) -> int | None:
    compact = re.sub(r"\s", "", value)
    if compact in ("", "-"):
        return None
    if not re.fullmatch(r"(?:-?\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))", compact):
        raise ValueError(f"Unexpected monetary token: {value!r}")
    return int(compact.replace(",", "").replace("(", "-").replace(")", ""))


def parse_row(line: str, page: int) -> list:
    match = ROW.fullmatch(line)
    if not match:
        raise ValueError(f"Unparsed employee line on page {page}: {line!r}")
    name, pay, expense = match.groups()
    salary = amount(pay)
    if salary is None or salary <= 75000:
        raise ValueError(f"Employee row below the source's >$75,000 threshold: {line!r}")
    return ["northern-health", name.strip(), None, salary, amount(expense), page]


def parse_summary(text: str, title: str) -> tuple[int, int]:
    matches = re.findall(re.escape(title) + r"\s+\$\s+([\d,]+)\s+\$\s+([\d,]+)", text)
    if len(matches) != 1:
        raise ValueError(f"Expected one printed subtotal: {title}")
    return tuple(int(v.replace(",", "")) for v in matches[0])


def parse_layout(text: str, fiscal_end: int) -> tuple[list[list], dict]:
    if "\ufffd" in text:
        raise ValueError("Replacement character in extracted source text")
    heading = re.search(r"FOR THE FISCAL YEAR ENDED MARCH 31, (\d{4})", text[:500])
    if not heading or int(heading[1]) != fiscal_end:
        raise ValueError("Northern Health fiscal period heading missing or conflicting")
    pages = text.split("\f")
    if pages[-1].strip():
        raise ValueError("Expected a terminal PDF page separator")
    pages.pop()
    rows, page_counts = [], []
    for page_number, page_text in enumerate(pages, 1):
        lines = page_text.splitlines()
        starts = [i for i, line in enumerate(lines) if HEADER.fullmatch(line.strip())]
        if len(starts) != 1:
            raise ValueError(f"Expected one employee table header on page {page_number}")
        before = len(rows)
        reached_summary = False
        for line in lines[starts[0] + 1:]:
            if line.strip().startswith("TOTAL EMPLOYEES >"):
                if page_number != len(pages):
                    raise ValueError("Named subtotal appears before the final employee page")
                reached_summary = True
                break
            if not line.strip() or re.fullmatch(r"Page \d+ of \d+", line.strip()):
                continue
            rows.append(parse_row(line, page_number))
        if page_number == len(pages) and not reached_summary:
            raise ValueError("Missing final named employee subtotal")
        if len(rows) == before:
            raise ValueError(f"No employee records on page {page_number}")
        page_counts.append(len(rows) - before)
    named = parse_summary(text, "TOTAL EMPLOYEES > $75,000")
    below = parse_summary(text, "TOTAL EMPLOYEES = OR < $75,000")
    grand = parse_summary(text, "GRAND TOTAL")
    if tuple(a + b for a, b in zip(named, below)) != grand:
        raise ValueError("Printed named and under-threshold subtotals do not equal printed grand totals")
    counts = Counter(row[1] for row in rows)
    return rows, {
        "physicalPdfPages": [1, len(pages)], "rowsPerPhysicalPage": page_counts,
        "internalFiscalYearEnd": fiscal_end, "unparsedEmployeeLines": 0,
        "printedNamedRemuneration": named[0], "printedNamedExpenses": named[1],
        "underThresholdRemunerationExcluded": below[0], "underThresholdExpensesExcluded": below[1],
        "printedAllEmployeeRemuneration": grand[0], "printedAllEmployeeExpenses": grand[1],
        "printedSubtotalsReconcileToGrandTotals": True,
        "repeatedDisclosedNames": [{"name": name, "rows": n} for name, n in counts.items() if n > 1],
        "exactDuplicateSourceRows": sum(n - 1 for n in Counter(tuple(r[:5]) for r in rows).values() if n > 1),
    }


def validate_coordinates(bbox_xml: bytes, rows: list[list]) -> int:
    """Independently compare all names/pay/expenses with positioned PDF words."""
    pages = ET.fromstring(bbox_xml).findall(".//x:page", NS)
    by_page = defaultdict(list)
    for row in rows:
        by_page[row[5]].append(row)
    if len(pages) != len(by_page):
        raise ValueError("PDF coordinates and parsed table page counts differ")
    first = [word for word in pages[0].findall("x:word", NS)
             if (word.text or "").replace(",", "") == str(rows[0][3])
             and 250 < float(word.attrib["xMax"]) < 430]
    if len(first) != 1:
        raise ValueError("Unable to identify the salary column from the first source row")
    right = float(first[0].attrib["xMax"])
    checked = 0
    for number, page in enumerate(pages, 1):
        words = page.findall("x:word", NS)
        # Summary labels use a different font baseline from their dollar values.
        # The preceding employee row is at least 14 points above this boundary.
        last_y = min([float(w.attrib["yMin"]) - 7 for w in words if w.text == "TOTAL"] + [10000.0])
        salary_words = [word for word in words
                        if re.fullmatch(r"[\d,]+", word.text or "")
                        and int(word.text.replace(",", "")) > 75000
                        and abs(float(word.attrib["xMax"]) - right) < 1
                        and float(word.attrib["yMin"]) < last_y]
        salary_words.sort(key=lambda w: float(w.attrib["yMin"]))
        expected = by_page[number]
        if len(salary_words) != len(expected):
            raise ValueError(f"Page {number}: salary coordinate row count differs from parsed rows")
        for word, row in zip(salary_words, expected):
            y = float(word.attrib["yMin"])
            line_words = sorted((w for w in words if abs(float(w.attrib["yMin"]) - y) < 1),
                                key=lambda w: float(w.attrib["xMin"]))
            name = " ".join(w.text for w in line_words if float(w.attrib["xMax"]) < float(word.attrib["xMin"]) - 5)
            expense = " ".join(w.text for w in line_words if float(w.attrib["xMin"]) > right + 1)
            observed = (name, amount(word.text), amount(expense))
            if observed != (row[1], row[3], row[4]):
                raise ValueError(f"Page {number}: PDF coordinate evidence conflicts with row {row!r}: {observed!r}")
            checked += 1
    return checked


def verify_reviewed_totals(rows: list[list], validation: dict, reviewed: tuple) -> None:
    _, pages, count, pay, expenses, printed_pay, printed_expenses = reviewed
    total_pay = sum(row[3] for row in rows)
    total_expenses = sum(row[4] for row in rows if row[4] is not None)
    observed = (validation["physicalPdfPages"][1], len(rows), total_pay, total_expenses,
                validation["printedNamedRemuneration"], validation["printedNamedExpenses"])
    if observed != (pages, count, pay, expenses, printed_pay, printed_expenses):
        raise ValueError(f"Reviewed rows or displayed/printed totals changed: {observed!r}")
    if validation["exactDuplicateSourceRows"]:
        raise ValueError("Unexpected identical source payment rows; review before importing")
    residuals = (pay - printed_pay, expenses - printed_expenses)
    # A compatibility bound, not proof of the publisher's rounding method.
    bound = (len(rows) + 1) / 2
    if any(abs(value) > bound for value in residuals):
        raise ValueError("Source subtotal residual exceeds the displayed-dollar rounding bound")
    validation.update({
        "summaryTotalReconciled": residuals == (0, 0), "sourceFingerprintLocked": True,
        "namedRemunerationSum": pay, "namedExpensesSum": expenses,
        "remunerationResidual": residuals[0], "expensesResidual": residuals[1],
        "displayedDollarRoundingCompatibilityBound": bound,
        "residualsWithinDisplayedDollarRoundingBound": True,
        "negativeExpenseRows": sum(row[4] is not None and row[4] < 0 for row in rows),
        "explicitZeroExpenseRows": sum(row[4] == 0 for row in rows),
        "missingExpenseRows": sum(row[4] is None for row in rows),
    })


def compare_compiled_baseline(rows: list[list], year: str) -> dict | None:
    path = ROOT / "research/salaries/compiled-baseline.json.gzip"
    if not path.exists():
        return None
    raw = path.read_bytes()
    baseline = json.loads(gzip.decompress(raw))
    if year not in baseline["years"]:
        return None
    employer = next(e for e in baseline["employers"] if e["slug"] == "northern-health")
    index = baseline["years"].index(year)
    legacy = [r for r in employer["rows"] if r[4] == index]
    def key(name):
        return tuple("".join(c for c in part.casefold() if c.isalnum()) for part in name.split(",", 1))
    compiled = Counter((key(r[0]), r[2]) for r in legacy)
    official = Counter((key(r[1]), r[3]) for r in rows)
    unmatched = compiled - official
    result = {
        "baselineFile": "research/salaries/compiled-baseline.json.gzip", "baselineSha256": sha256(raw),
        "compiledLabel": year, "compiledRows": len(legacy), "acceptedSourceRows": len(rows),
        "exactNamePayPairsMatched": sum((compiled & official).values()),
        "sourceNamePayPairsAbsentFromCompiled": sum((official - compiled).values()),
        "compiledNamePayPairsNotMatched": sum(unmatched.values()),
        "compiledRowsNotMatched": [{"name": r[0], "position": r[1], "remuneration": r[2], "expenses": r[3]}
                                   for r in legacy if (key(r[0]), r[2]) in unmatched],
        "matching": "Exact normalized surname/given-name tuple and remuneration; no nickname or approximate matches.",
    }
    if year == "2023/24":
        old = next((r for r in legacy if r[0] == "McKinnon, Niamh Grace" and r[2:4] == [83246, 2962]), None)
        new = next((r for r in rows if r[1] == "McKinnon, Niamh Grace, Marg" and r[3:5] == [83246, 2962]), None)
        if old and new:
            result["reviewedShortenedName"] = {
                "compiledName": old[0], "publishedName": new[1], "remuneration": new[3],
                "expenses": new[4], "physicalPdfPage": new[5],
                "decision": "Preserve the complete name as published in the SOFI; no identity merge is applied.",
            }
            result["additionalSourceRowsBeyondReviewedNameDifference"] = sum((official - compiled).values()) - 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-salary-sources"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/northern-health")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    pending, sources = {}, []
    for label, reviewed in REVIEWED.items():
        pdf = args.cache / f"northern-health-{label}.pdf"
        url = BASE + f"schedule-remuneration-expenses-{label}.pdf"
        if not pdf.exists():
            if args.offline:
                raise ValueError(f"Missing cached source: {pdf}")
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PofBC salary source importer"})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            if not raw.startswith(b"%PDF-"):
                raise ValueError("Official report request did not return a PDF")
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(raw)
        raw = pdf.read_bytes()
        if sha256(raw) != reviewed[0]:
            raise ValueError(f"Northern Health {label} PDF changed; review before importing")
        fiscal_start = int(label[:4])
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        bbox = subprocess.check_output(["pdftotext", "-bbox", str(pdf), "-"])
        rows, validation = parse_layout(text, fiscal_start + 1)
        validation["rowsCheckedAgainstPdfWordCoordinates"] = validate_coordinates(bbox, rows)
        verify_reviewed_totals(rows, validation, reviewed)
        reviewed_rows = [row for row in rows if (row[4] is not None and row[4] <= 0)
                         or row[1] in NAMES_REVIEWED.get(label, [])]
        validation["visuallyReviewedRows"] = [{"name": r[1], "remuneration": r[3], "expenses": r[4],
                                               "physicalPdfPage": r[5]} for r in reviewed_rows]
        validation["visuallyReviewedSummaryPage"] = reviewed[1]
        filename = label + ".json.gzip"
        normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
        compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
        pending[filename] = compressed
        year = f"{fiscal_start}/{label[-2:]}"
        source = {
            "id": "northern-health-sofi-" + label, "employerSlug": "northern-health",
            "employerName": "Northern Health", "sector": "Health authorities", "year": year,
            "title": f"Northern Health Statement of Financial Information {year}: employee remuneration and expenses",
            "sourceUrl": url, "indexUrl": INDEX, "sha256": sha256(raw),
            "file": filename, "dataSha256": sha256(compressed), "normalizedSha256": sha256(normalized),
            "periodStart": f"{fiscal_start}-04-01", "periodEnd": f"{fiscal_start + 1}-03-31",
            "currency": "CAD", "scope": "employee-remuneration", "category": "employee-remuneration",
            "scopeDescription": "Named employee remuneration above $75,000, including disclosed estate payments",
            "threshold": 75000, "thresholdComparison": ">", "nameDisclosure": "named",
            "rowCount": len(rows), "totalRemuneration": sum(r[3] for r in rows),
            "totalDisclosedExpenses": sum(r[4] for r in rows if r[4] is not None),
            "status": "verified", "verifiedOn": args.verified_on, "validation": validation,
            "notes": [
                "Employee schedule only; the aggregate for employees earning $75,000 or less is excluded. Job titles are not disclosed in this schedule.",
                "Remuneration includes base salary, retroactive pay, taxable benefits, vacation payouts, retiring allowances, overtime and on-call premiums as defined in the report.",
                "Expenses include travel, tuition, registration fees, relocation allowances and professional membership fees paid to or on behalf of employees.",
                "Blank and dash expense cells are retained as missing, not zero. Negative expense recoveries and the explicitly printed negative zero are retained numerically when present.",
                "Repeated disclosed names remain separate source rows; a name alone is not a unique employee identifier. Estate wording and punctuation are preserved as published.",
                f"Displayed named salary amounts sum to ${validation['remunerationResidual']:,} more than the printed named subtotal; displayed expenses sum to ${validation['expensesResidual']:,} more. These residuals are compatible with rounding to whole dollars, but the source does not explain them. Individual published amounts are preserved; exact named-subtotal reconciliation is not claimed.",
            ],
        }
        if "cash basis" in text:
            source["notes"].append("The report states that this schedule is on a cash basis and is not directly reconcilable to accrual-basis financial statements.")
        comparison = compare_compiled_baseline(rows, year)
        if comparison is not None:
            validation["compiledBaselineComparison"] = comparison
            if year == "2020/21":
                source["notes"].append("The previous compiled snapshot had six role-labelled executive rows whose name/pay pairs differ from this employee schedule. Their compensation basis has not been independently established here; the accepted amounts come from the employee SOFI, and the original compiled rows remain in the baseline.")
            if year == "2023/24" and comparison.get("additionalSourceRowsBeyondReviewedNameDifference") == 360:
                source["notes"].append("The validated employee schedule restores 360 rows absent from the compiled snapshot and preserves one name that the compilation shortened, at the same published pay and expense amounts.")
        sources.append(source)
    registry = {
        "version": 1,
        "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "sources": sources,
        "coverageNotes": ["These five reports cover FY2020/21 through FY2024/25. Every accepted row carries its physical PDF page, and its name/pay/expense values were checked against positioned PDF words."]
    }
    # Validate every report before replacing any accepted normalized outputs.
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, content in pending.items():
        (args.output / filename).write_bytes(content)
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    for source in sources:
        print(f"{source['year']}: {source['rowCount']:,} rows, ${source['totalRemuneration']:,} remuneration; all source coordinates checked.")
    print(f"Imported {len(sources)} Northern Health schedules, {sum(s['rowCount'] for s in sources):,} rows.")


if __name__ == "__main__":
    main()
