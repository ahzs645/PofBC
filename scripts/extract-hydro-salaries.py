#!/usr/bin/env python3
"""Extract verified employee remuneration from BC Hydro's official FIA returns.

Run from any directory:
  python scripts/extract-hydro-salaries.py --cache-dir /tmp/pofbc-hydro-research
  python scripts/extract-hydro-salaries.py --self-test

Requires Poppler's pdftotext; all Python dependencies are in the standard library.
Public source PDFs are cached outside the repository. The committed, deterministic
JSON/gzip files preserve the printed dollar values, employee initials, expenses and
one-based PDF page. They do not infer positions or expand initials into identities.

Only employee schedules for BC Hydro, Powerex and Powertech are selected. Board,
supplier, severance, aggregate and other subsidiary rows cannot enter the output.
An employer/year is withheld when its named rows do not reconcile to the printed
total less the consolidated under-threshold amount within the maximum possible
whole-dollar rounding error. Review-only rows remain separate from published input.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "salaries" / "hydro"
BASE = "https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/accountability-reports/"
SOURCE_INDEX = "https://www.bchydro.com/about/accountability_reports/financial_reports.html"
SOURCES = {
    2013: "openness-accountability/financial-information-act-return-march-31-2013.pdf",
    2014: "openness-accountability/financial-information-act-return-20140331.pdf",
    2015: "openness-accountability/financial-information-act-return-march-31-2015.pdf",
    2016: "openness-accountability/financial-information-act-return-march-31-2016.pdf",
    2017: "financial-reports/annual-reports/BC-Hydro-FIA-F17.pdf",
    2018: "financial-reports/annual-reports/bch-fia-f18.pdf",
    2019: "financial-reports/annual-reports/bch-fia-f19.pdf",
    2020: "financial-reports/annual-reports/BCHydro-FIA-F20.pdf",
    2021: "financial-reports/annual-reports/BCHydro-FIA-F21.pdf",
    2022: "financial-reports/annual-reports/bch-fia-f22.pdf",
    2023: "financial-reports/annual-reports/bch-fia-f23.pdf",
    2024: "financial-reports/annual-reports/bch-fia-f24.pdf",
    2025: "financial-reports/annual-reports/f2025-financial-information-act-return.pdf",
}
EMPLOYERS = {
    "BRITISH COLUMBIA HYDRO AND POWER AUTHORITY": ("bc-hydro", "BC Hydro"),
    "POWEREX CORP.": ("sub-powerex", "Powerex"),
    "POWERTECH LABS INC.": ("sub-powertech-labs", "Powertech Labs"),
}
MONEY = r"-?\d[\d,]*(?:\.\d{2})?"
# Old reports can abut a long surname and its amount; FY2025 has mixed/lowercase
# initials, one-space separators, and a Unicode hyphen for zero expenses.
ROW = re.compile(
    rf"(?:^|\s{{2,}})((?!(?i:total)\b)[A-Za-z]{{1,5}})\s+"
    rf"([^\d\s][^\d]*?)\s*({MONEY})\s+({MONEY}|[\u2010\u2013\u2014-])(?=\s|$)"
)
TAIL_AMOUNTS = re.compile(rf"\s({MONEY})\s+({MONEY})\s*$")
EMPLOYEE_HEADER = re.compile(
    r"on Behalf of Employees During the Year Ended March 31, (\d{4})", re.I
)
PAGE_SEQUENCE = re.compile(r"\bPage(?:\s+No:)?\s*(\d+)\s+of\s+(\d+)")


def dollars(value: str) -> int | float:
    if value in ("-", "\u2010", "\u2013", "\u2014"):
        return 0
    amount = Decimal(value.replace(",", ""))
    return int(amount) if amount == amount.to_integral_value() else float(amount)


def exact_sum(values) -> int | float:
    total = sum((Decimal(str(x)) for x in values), Decimal(0))
    return int(total) if total == total.to_integral_value() else float(total)


def parse_rows(line: str, employer: str, page: int):
    matches = list(ROW.finditer(line))
    rows = []
    for match in matches:
        initials, surname, pay, expenses = match.groups()
        name = re.sub(r"\s+", " ", surname.strip())
        pay, expenses = dollars(pay), dollars(expenses)
        if pay < 75000:
            raise ValueError(f"Below-threshold employee match at page {page}: {line!r}")
        if not any(c.isalpha() for c in name):
            raise ValueError(f"Invalid employee name at page {page}: {line!r}")
        rows.append([employer, f"{name}, {initials.upper()}", None, pay, expenses, page])
    residue = line
    for match in reversed(matches):
        residue = residue[:match.start()] + residue[match.end():]
    return rows, residue


def parse_report(text: str, year: int):
    pages = text.split("\f")
    cover = re.sub(r"\s+", " ", pages[0])
    if not re.search(rf"Year Ended March 31, {year}\b", cover, re.I):
        raise ValueError(f"Cover does not identify the expected fiscal year {year}")
    rows_by_employer = defaultdict(list)
    metadata = {}
    ignored_employers = set()
    for page_number, page in enumerate(pages, 1):
        header = EMPLOYEE_HEADER.search(page)
        if not header:
            continue
        title = page.strip().split("\n")[0].strip()
        if title not in EMPLOYERS:
            ignored_employers.add(title)
            continue
        if int(header[1]) != year:
            raise ValueError(f"Wrong fiscal year in employee section at PDF page {page_number}")
        slug, name = EMPLOYERS[title]
        item = metadata.setdefault(slug, {
            "slug": slug, "name": name, "sourceName": title, "pages": [],
            "sectionPages": [], "reportedTotal": None, "reportedUnderThreshold": None,
        })
        item["pages"].append(page_number)
        sequence = PAGE_SEQUENCE.search(page)
        if not sequence:
            raise ValueError(f"Missing section page count at PDF page {page_number}")
        item["sectionPages"].append([int(sequence[1]), int(sequence[2])])
        table_started = False
        is_summary_page = "Consolidated total of other" in page
        for line in page.splitlines():
            upper = line.upper()
            if "REMUNERATION" in upper and "EXPENSES" in upper and "SCHEDULE" not in upper:
                table_started = True
                continue
            if not table_started:
                continue
            # FY2025 wraps the under-threshold label and places the summary beside
            # named rows; anchor amounts at the right edge of the physical line.
            amounts = TAIL_AMOUNTS.search(line)
            if amounts and ("Total " in line or "total " in line or "employees with remuneration" in line):
                amounts = [dollars(x) for x in amounts.groups()]
                key = "reportedTotal" if re.search(r"\bTotal\b", line) else "reportedUnderThreshold"
                if item[key] is not None:
                    raise ValueError(f"Multiple {key} rows for {slug}/{year}")
                item[key] = amounts
            rows, residue = parse_rows(line, slug, page_number)
            rows_by_employer[slug].extend(rows)
            # Monetary leftovers on an ordinary employee page indicate a skipped
            # or broken row. Summary pages also contain aggregate-only amounts;
            # these are checked independently by the reconciliation below.
            if not is_summary_page and re.search(r"\d,\d{3}", residue):
                raise ValueError(f"Unparsed money at PDF page {page_number}: {residue!r}")

    if set(metadata) != {x[0] for x in EMPLOYERS.values()}:
        raise ValueError(f"Expected all three employee sections for {year}; found {list(metadata)}")
    accepted_rows, deferred_rows = [], []
    accepted, deferred = [], []
    for slug, item in metadata.items():
        rows = rows_by_employer[slug]
        if not rows or item["reportedTotal"] is None or item["reportedUnderThreshold"] is None:
            raise ValueError(f"Incomplete employee section or missing summary for {slug}/{year}")
        section_pages = item.pop("sectionPages")
        expected_pages = section_pages[0][1]
        if section_pages != [[i, expected_pages] for i in range(1, expected_pages + 1)]:
            raise ValueError(f"Missing/repeated section pages for {slug}/{year}: {section_pages}")
        total_pay = exact_sum(row[3] for row in rows)
        total_expenses = exact_sum(row[4] for row in rows)
        expected = [a - b for a, b in zip(item["reportedTotal"], item["reportedUnderThreshold"])]
        variances = [total_pay - expected[0], total_expenses - expected[1]]
        # Each named printed amount and both printed aggregate amounts can differ
        # from its unrounded original by at most $0.50. This is an upper bound,
        # not a claim that a non-zero difference has been proved to be rounding.
        rounding_bound = (len(rows) + 2) / 2
        reconciles = all(abs(delta) <= rounding_bound for delta in variances)
        duplicate_names = Counter(row[1] for row in rows)
        item.update({
            "status": "verified" if reconciles else "deferred-aggregate-mismatch",
            "rowCount": len(rows), "totalRemuneration": total_pay,
            "totalExpenses": total_expenses,
            "expectedNamedRemuneration": expected[0], "expectedNamedExpenses": expected[1],
            "remunerationVariance": variances[0], "expensesVariance": variances[1],
            "maxWholeDollarRoundingDifference": rounding_bound,
            "reconciliation": "within-rounding-bound" if reconciles else "outside-rounding-bound",
            "duplicateInitialNameCount": sum(n - 1 for n in duplicate_names.values() if n > 1),
            "positionDisclosure": "not-published", "nameDisclosure": "surname-and-initials",
        })
        if not reconciles:
            item["reason"] = (
                "Printed named rows do not reconcile to the printed total less the under-threshold "
                "aggregate within the maximum whole-dollar rounding bound. These rows are kept "
                "for review and excluded from the verified import. No values have been inferred."
            )
            deferred.append(item)
            deferred_rows.extend(rows)
        else:
            accepted.append(item)
            accepted_rows.extend(rows)
    return accepted_rows, accepted, deferred_rows, deferred, sorted(ignored_employers)


def write_rows(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def self_test():
    def check(line, name, pay, expenses):
        rows, residue = parse_rows(line, "sub-powerex", 1)
        assert rows == [["sub-powerex", name, None, pay, expenses, 1]], rows
        assert not residue.strip(), residue
    check("BL    Mo                     122,528               704", "Mo, BL", 122528, 704)
    check("S     Motamedi Mohammadian143,869                1,956", "Motamedi Mohammadian, S", 143869, 1956)
    check("jg   stilwell          204,132        5,342", "stilwell, JG", 204132, 5342)
    check("J    Zhao                 100,237          \u2010", "Zhao, J", 100237, 0)
    check("A      Sukhija               97,329             -304", "Sukhija, A", 97329, -304)
    check("BL    Mo                     122,528.25           704.02", "Mo, BL", 122528.25, 704.02)
    assert not parse_rows("Total                      31,964,758          81,873", "sub-powerex", 1)[0]
    both, residue = parse_rows(
        "BL    Mo                     122,528               704            P      Sung                  91,751                0",
        "sub-powerex", 189,
    )
    assert len(both) == 2 and not residue.strip()
    assert exact_sum([122528.25, 704.02]) == 123232.27
    print("Hydro extraction regression checks passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/pofbc-hydro-research"))
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--refresh", action="store_true", help="Download the source PDFs again")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "version": 1, "publisher": "BC Hydro", "verifiedAt": "2026-10-22",
        "sourceIndexUrl": SOURCE_INDEX,
        "columns": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "currency": "CAD", "amountUnit": "dollars", "sources": [],
        "unparsedSources": [
            {
                "id": "bchydro-fia-2011-ocr-backlog", "year": "2010/11", "slug": "2010-11",
                "sourceUrl": BASE + "openness-accountability/financial-information-act-return-2011.pdf",
                "sha256": "7e7901ae68991cede2c063af9d08675506e7272d9dc3678a0f8d2e7ea72d7e36",
                "periodStart": "2010-04-01", "periodEnd": "2011-03-31",
                "status": "requires-ocr", "category": "employee-remuneration",
                "reason": "Employee tables are scanned images without extractable text; OCR and row/aggregate verification are needed.",
                "notes": "Cover and rendered employee schedule on PDF page 47 say March 31, 2011; the contents page incorrectly says 2010. Cover says updated January 2013.",
            },
            {
                "id": "bchydro-fia-2012-ocr-backlog", "year": "2011/12", "slug": "2011-12",
                "sourceUrl": BASE + "openness-accountability/financial-information-act-return-2012.pdf",
                "sha256": "aef1ea379eedad356a9b6b635ab649d41e50e3150c0e0b40a04c044188655270",
                "periodStart": "2011-04-01", "periodEnd": "2012-03-31",
                "status": "requires-ocr", "category": "employee-remuneration",
                "reason": "Employee tables are scanned images without extractable text; OCR and row/aggregate verification are needed.",
                "notes": "Rendered employee schedule on PDF page 47 says March 31, 2012. General notes say this return includes 27 pay periods rather than the usual 26; cover says updated January 2013.",
            },
        ],
        "notes": [
            "Fiscal year labels refer to April 1 through March 31; e.g. FY2021 is 2020/21.",
            "Amounts are gross remuneration as printed, not base salary. Expenses remain separate.",
            "Named disclosure threshold is $75,000; these are not complete employee rosters or total payrolls.",
            "Initial-only names are not expanded or treated as unique identities; repeated initials remain separate rows.",
            "A variance within the theoretical rounding bound is a reconciliation check, not proof of exact equality.",
            "FY2025 Hydro expense and Powerex remuneration mismatches were independently reproduced using PDF word coordinates.",
        ],
    }
    for year, relative_url in SOURCES.items():
        url = BASE + relative_url
        pdf = args.cache_dir / f"hydro-{year}.pdf"
        if args.refresh or not pdf.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "PofBC-public-disclosure-research/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                content = response.read()
            if not content.startswith(b"%PDF-"):
                raise ValueError(f"Expected a PDF from {url}")
            pdf.write_bytes(content)
        text_file = pdf.with_suffix(".txt")
        subprocess.run(["pdftotext", "-layout", str(pdf), str(text_file)], check=True)
        text = text_file.read_text()
        rows, employers, review_rows, deferred, ignored = parse_report(text, year)
        slug = f"{year - 1}-{str(year)[2:]}"
        filename = f"{slug}.json.gzip"
        row_hash = write_rows(args.output_dir / filename, rows)
        source = {
            "id": f"bchydro-fia-{year}", "year": f"{year - 1}/{str(year)[2:]}", "slug": slug,
            "file": filename, "sourceUrl": url, "sourceIndexUrl": SOURCE_INDEX,
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "dataSha256": row_hash,
            "sourceTitle": f"BC Hydro Financial Information Act Return, year ended March 31, {year}",
            "periodStart": f"{year - 1}-04-01", "periodEnd": f"{year}-03-31",
            "category": "employee-remuneration", "threshold": 75000,
            "thresholdRule": "over", "currency": "CAD", "amountUnit": "dollars",
            "amountPrecision": "whole-dollar", "coverage": "named-employees-over-threshold",
            "scope": "named-employees-over-threshold",
            "nameDisclosure": "surname-and-initials", "positionDisclosure": "not-published",
            "rowCount": len(rows), "totalRemuneration": exact_sum(row[3] for row in rows),
            "totalExpenses": exact_sum(row[4] for row in rows), "employers": employers,
            "validation": {
                "method": "named-row-sums-versus-total-minus-under-threshold",
                "employeeSectionPagesComplete": True,
                "importedEmployerSumsWithinWholeDollarRoundingBound": True,
                "publishedAmountPrecision": "whole-dollar",
            },
            "notes": [
                "Official employee schedules; gross remuneration and expenses are separate. Positions are not published.",
                "Names are surnames and initials, not resolved personal identities. Duplicate initial-name rows are retained.",
                "Named rows are reconciled with the printed total less the under-threshold aggregate; minor variances are retained, not adjusted.",
            ],
        }
        if ignored:
            source["otherEmployeeSchedulesNotImported"] = ignored
        if deferred:
            source["deferredEmployers"] = deferred
            source["deferredFile"] = f"review/{slug}.json.gzip"
            source["deferredDataSha256"] = write_rows(args.output_dir / source["deferredFile"], review_rows)
            source["notes"].append(
                "BC Hydro and Powerex are withheld for this fiscal year because aggregate discrepancies "
                "exceed possible whole-dollar rounding; only verified Powertech rows enter the import."
            )
        result["sources"].append(source)
        counts = ", ".join(f"{e['slug']} {e['rowCount']}" for e in employers)
        print(f"{source['year']}: {len(rows):,} verified rows ({counts}); {len(deferred)} employer-years deferred")
    manifest = args.output_dir / "sources.json"
    manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {manifest}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, AssertionError, subprocess.CalledProcessError) as exc:
        print(f"Hydro extraction failed: {exc}", file=sys.stderr)
        sys.exit(1)
