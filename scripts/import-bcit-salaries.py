#!/usr/bin/env python3
"""Import the reviewed BCIT 2017/18 employee schedule from its official SOFI PDF.

Requires pdftotext (Poppler). The build itself uses the deterministic checked-in
JSON gzip, so it does not download or extract PDFs. A changed source must be
reviewed before updating the fingerprint and row/total assertions below.
"""
import argparse
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.bcit.ca/files/financialservices/pdf/financial-information-2018.pdf"
SOURCE_SHA256 = "31f9f6cf0f6faaab8d3953ccc064b8335e65b8aca87156e9b2ec14386ffaacc3"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def number(value):
    if value == "-":
        return None
    return int(value.replace(",", "").replace("(", "-").replace(")", ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-salary-sources"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/bcit")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    path = args.cache / "bcit-financial-2018.pdf"
    if not path.exists():
        if args.offline:
            raise ValueError(f"Missing source: {path}")
        request = urllib.request.Request(URL, headers={"User-Agent": "PofBC salary source importer"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise ValueError("The official BCIT PDF has changed; review before importing")
    text = subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True)
    if "FOR THE YEAR ENDED MARCH 31, 2018" not in text[:300]:
        raise ValueError("BCIT fiscal year heading missing or changed")
    start = text.index("Abdel-Hai, Mahmoud")
    stop = text.index("STATEMENT OF BOARD OF GOVERNORS, REMUNERATION AND EXPENSES", start)
    section = text[start:stop]
    pattern = re.compile(r"^\s*(.+?,.+?)\s{2,}([\d,]+)\s+(\([\d,]+\)|[\d,]+|-)\s*$")
    rows = []
    for line in section.splitlines():
        match = pattern.match(line)
        if match:
            name, pay, expenses = match.groups()
            rows.append(["bcit", name.strip(), None, number(pay), number(expenses)])
        elif re.search(r"\d", line) and not any(part in line for part in (
            "Page", "Salaries under", "172,147,371", "*Salary may include"
        )):
            raise ValueError(f"Unparsed numeric line in employee schedule: {line!r}")
    if len(rows) != 970 or min(row[3] for row in rows) < 75000:
        raise ValueError("BCIT employee row count or threshold changed")
    total_pay = sum(row[3] for row in rows)
    total_expenses = sum(row[4] for row in rows if row[4] is not None)
    if (total_pay, total_expenses) != (96590156, 3409363):
        raise ValueError("BCIT displayed employee row totals changed")
    if not re.search(r"ZZ --- Salaries under \$75000\s+75,557,234\s+-", section):
        raise ValueError("BCIT under-threshold aggregate changed")
    if not re.search(r"172,147,371\s+3,409,360", section):
        raise ValueError("BCIT printed grand totals changed")
    filename = "2017-18-employees.json.gzip"
    normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
    source = {
        "id": "bcit-sofi-2017-18-employees", "employerSlug": "bcit",
        "employerName": "British Columbia Institute of Technology", "sector": "Education",
        "year": "2017/18", "title": "BCIT Financial Information Act Return 2017/18: Exhibit B",
        "sourceUrl": URL, "sha256": SOURCE_SHA256, "dataSha256": digest(compressed),
        "normalizedSha256": digest(normalized), "file": filename,
        "periodStart": "2017-04-01", "periodEnd": "2018-03-31", "currency": "CAD",
        "category": "employee-remuneration", "scope": "employee-remuneration",
        "scopeDescription": "Named employees earning $75,000 or more, Exhibit B",
        "threshold": 75000, "rowCount": len(rows), "totalRemuneration": total_pay,
        "totalDisclosedExpenses": total_expenses, "status": "verified", "verifiedOn": args.verified_on,
        "notes": [
            "Exhibit B lists employees. Board of Governors payments and the aggregate below $75,000 are excluded.",
            "Salary may include overtime, allowances, part-time and termination settlement, as stated in the source.",
            "Dash expenses are retained as missing, and one reported expense recovery of -$443 is retained.",
            "The sum of displayed named salaries plus the below-threshold aggregate exceeds the printed total by $19; displayed expenses exceed the printed total by $3. These small residuals are compatible with dollar rounding, but the PDF does not explain them. Individual published values are preserved."
        ],
        "validation": {
            "physicalPdfPages": [36, 57], "printedPages": [6, 27],
            "internalFiscalYearEnd": 2018, "rowCountChecked": True,
            "sourceFingerprintLocked": True, "summaryTotalReconciled": False,
            "namedRemunerationSum": total_pay, "underThresholdAggregateExcluded": 75557234,
            "printedAllEmployeeRemuneration": 172147371, "remunerationResidual": 19,
            "namedExpensesSum": total_expenses, "printedAllEmployeeExpenses": 3409360,
            "expensesResidual": 3, "negativeExpenseRows": sum(row[4] is not None and row[4] < 0 for row in rows),
            "unparsedNumericLines": 0
        }
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / filename).write_bytes(compressed)
    registry = {"version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses"], "sources": [source]}
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"Imported BCIT 2017/18: {len(rows)} named employees; ${total_pay:,} displayed remuneration.")


if __name__ == "__main__":
    main()
