#!/usr/bin/env python3
"""Replace North Island College's duplicated compiled 2020/21 disclosure.

Uses the official PDF's employee schedule, not deduplicated compiler rows.
Requires Python standard library and Poppler pdftotext. All row, year, threshold,
subtotal and baseline-comparison checks finish before normalized data is written.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = "https://nic.bc.ca/_resources/pdf/statement-of-financial-information-2020-21.pdf"
INDEX_URL = "https://nic.bc.ca/about/leadership-and-governance/institutional-reporting.html"
REVIEWED_SHA256 = "e6f8d92e4ea6b821e63494f27bf46d755e83a088f7248c831d1e683427f8d513"
ROW = re.compile(r"^\s+(\S.+?)\s{2,}(\S.+?)\s{2,}([\d,]+)\s+([\d,]+|-)\s*$")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(text):
    if "FOR THE YEAR ENDED MARCH 31, 2021" not in text.split("\f")[0]:
        raise ValueError("Unexpected cover fiscal year")
    rows, pages, subtotals, layout_corrections = [], [], [], []
    for number, page in enumerate(text.split("\f"), 1):
        if "SCHEDULE OF EMPLOYEE REMUNERATION AND EXPENSES" not in page:
            continue
        if "FOR THE YEAR ENDED MARCH 31, 2021" not in page:
            raise ValueError(f"Unexpected employee schedule year on PDF page {number}")
        pages.append(number)
        active = False
        for line in page.splitlines():
            if re.match(r"B\.\s+Other Employees > \$75,000", line):
                active = True
                continue
            if re.match(r"C\.\s+Other Employees", line):
                active = False
            if not active:
                continue
            # The long name physically reaches the position column in the PDF.
            # This exact column boundary was verified on rendered PDF page 11.
            abutting = "Paquet-Combe, Marie-FranceInst, Health Care Assistant"
            if abutting in line:
                line = line.replace(abutting, "Paquet-Combe, Marie-France  Inst, Health Care Assistant")
                layout_corrections.append({"pdfPage": number, "name": "Paquet-Combe, Marie-France",
                    "position": "Inst, Health Care Assistant",
                    "reason": "Inserted the rendered name/position column boundary; no source letters or monetary values changed."})
            match = ROW.match(line)
            if match:
                name, position, pay, expenses = match.groups()
                pay = int(pay.replace(",", ""))
                expenses = 0 if expenses == "-" else int(expenses.replace(",", ""))
                if "," not in name or pay <= 75000:
                    raise ValueError(f"Unexpected employee row at PDF page {number}: {line}")
                rows.append(["north-island-college", name.strip(), position.strip(), pay, expenses, number])
            elif re.fullmatch(r"\s+[\d,]+\s+[\d,]+\s*", line):
                subtotals.append([int(x.replace(",", "")) for x in line.split()])
            elif re.search(r"\d{2},\d{3}", line):
                raise ValueError(f"Unparsed monetary row at PDF page {number}: {line}")
    if pages != [8, 9, 10, 11, 12] or len(rows) != 145:
        raise ValueError(f"Unexpected employee section completeness: {pages}, {len(rows)} rows")
    sums = [sum(row[i] for row in rows) for i in [3, 4]]
    if subtotals != [[14487889, 149323]] or sums != subtotals[0]:
        raise ValueError(f"Named employee sums do not equal printed subtotals: {sums}, {subtotals}")
    if len({row[1] for row in rows}) != len(rows) or len(layout_corrections) != 1:
        raise ValueError("Unexpected name duplication or layout correction count")
    return rows, layout_corrections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/pofbc-nic-research"))
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    pdf = args.cache_dir / "nic-2020-21.pdf"
    if not pdf.exists():
        with urllib.request.urlopen(URL, timeout=60) as response:
            pdf.write_bytes(response.read())
    pdf_bytes = pdf.read_bytes()
    if sha(pdf_bytes) != REVIEWED_SHA256:
        raise ValueError("Official PDF changed; review the source and layout before updating its accepted hash")
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    rows, layout_corrections = parse(text)
    baseline_path = ROOT / "research/salaries/compiled-baseline.json.gzip"
    baseline_bytes = baseline_path.read_bytes()
    baseline = json.loads(gzip.decompress(baseline_bytes))
    employer = next(x for x in baseline["employers"] if x["slug"] == "north-island-college")
    year_index = baseline["years"].index("2020/21")
    compiled = [row for row in employer["rows"] if row[4] == year_index]
    multiplicities = Counter(tuple(row[:4]) for row in compiled)
    if len(compiled) != 290 or len(multiplicities) != 145 or set(multiplicities.values()) != {2}:
        raise ValueError("The reviewed compiler duplication has changed")
    key = lambda name: "".join(c for c in name.lower() if c.isalnum())
    reviewed_names = {"Naugler, Diane Dean": "Naugler, Diane", "Petteplace, Lindsa": "Petteplace, Lindsay"}
    compiled_keys = Counter((key(reviewed_names.get(r[0], r[0])), r[2], r[3]) for r in multiplicities)
    primary_keys = Counter((key(r[1]), r[3], r[4]) for r in rows)
    if compiled_keys != primary_keys:
        raise ValueError("Primary and unique compiled name/pay/expense records do not match the reviewed comparison")
    normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
    source = {
        "id": "north-island-college-sofi-2021", "employerSlug": "north-island-college",
        "employerName": "North Island College", "sector": "Colleges",
        "year": "2020/21", "slug": "2020-21", "file": "2020-21.json.gzip",
        "title": "North Island College Statement of Financial Information, year ended March 31, 2021",
        "sourceUrl": URL, "sourceIndexUrl": INDEX_URL, "sha256": sha(pdf_bytes),
        "dataSha256": sha(compressed), "normalizedSha256": sha(normalized),
        "periodStart": "2020-04-01", "periodEnd": "2021-03-31",
        "category": "employee-remuneration", "scope": "named-employees-over-threshold",
        "threshold": 75000, "thresholdRule": "over", "currency": "CAD", "amountUnit": "dollars",
        "nameDisclosure": "published-full-name", "positionDisclosure": "published",
        "rowCount": 145, "totalRemuneration": 14487889, "totalExpenses": 149323,
        "pages": [8, 9, 10, 11, 12], "status": "verified", "verifiedOn": "2026-10-22",
        "validation": {"remunerationSubtotalExact": True, "expensesSubtotalExact": True,
            "publishedRemunerationSubtotal": 14487889, "publishedExpensesSubtotal": 149323,
            "layoutCorrections": layout_corrections},
        "compiledDuplicationEvidence": {"baselineSha256": sha(baseline_bytes),
            "compiledRows": 290, "uniqueCompiledRows": 145, "copiesOfEveryRecord": 2,
            "verifiedPrimaryRows": 145, "matchedNamePayExpenseRecords": 145,
            "reviewedCompilerNameCorrections": reviewed_names,
            "sourceYearIsCorrect": True},
        "notes": [
            "Official employee schedule replaces 290 compiled rows with 145 verified rows; every compiled record appeared twice.",
            "Both remuneration and expense sums exactly equal the source's named-employee subtotals. Board and under-threshold aggregate rows are excluded.",
            "The institution's reporting page incorrectly sends its 2020-21 link to the 2019-20 PDF. This import uses the separately accessible actual 2020-21 report, whose cover and employee pages state March 31, 2021.",
            "Primary-source names repair two compiler field errors: Naugler, Diane Dean becomes Naugler, Diane with Dean in the position; Petteplace, Lindsa becomes Petteplace, Lindsay.",
        ],
    }
    out = ROOT / "research/salaries/north-island"
    out.mkdir(parents=True, exist_ok=True)
    (out / source["file"]).write_bytes(compressed)
    (out / "sources.json").write_text(json.dumps({"version": 1,
        "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "sources": [source]}, indent=2) + "\n")
    print("North Island College 2020/21: 145 source rows, $14,487,889 remuneration, $149,323 expenses; both subtotals reconcile exactly.")


if __name__ == "__main__":
    main()
