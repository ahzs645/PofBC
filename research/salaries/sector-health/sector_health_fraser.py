#!/usr/bin/env python3
"""Verify two recovered Fraser Health employee originals (FY2013/14–2014/15).

Poppler layout extraction is checked row-for-row using independent PyMuPDF
coordinates. No printed amount is changed to force the source's totals to agree.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

import fitz

BASE = "https://www.fraserhealth.ca/-/media/Project/FraserHealth/FraserHealth/About-Us/Accountability/Financial-reporting/"
INDEX = "https://www.fraserhealth.ca/about-us/accountability/financial-reporting"
REVIEWED = {
    2014: {"sha256": "dc651f21a4d8f7e143865c3e6e723a32189c271b90d251511f40e93c94e87f28", "pages": 118, "offset": 1, "totals": (5569, 514447540, 4561219, 514447500, 4561185)},
    2015: {"sha256": "dd902ea484f17717eff18ce0faa9876831d2a513cf34f1e3ac9642e87e4971c0", "pages": 149, "offset": 0, "totals": (5925, 544066029, 4513454, 544065925, 4513431)},
}
HEADER = re.compile(r"EMPLOYEE NAME\s+(?:REMUNERATION|RENUMERATION)\s+EXPENSES")
ROW = re.compile(r"(.+?)\s{2,}([\d,]+)\s{2,}([\d,()\-‐\s]+)")
LABELS = ["Total Payments Equal to or Greater than $75,000", "Total Payments Less than $75,000", "Total Payments to All Fraser Health Employees"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def amount(text):
    value = "".join(text.split()).replace("‐", "-")
    if value in ("", "-"):
        return None
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    if not re.fullmatch(r"-?\d{1,3}(?:,\d{3})*", value):
        raise ValueError("Unrecognized monetary cell: " + repr(text))
    return int(value.replace(",", ""))


def parse_layout(text, end):
    pages = text.split("\f")
    assert not pages.pop().strip(), "Missing terminal page separator"
    cfg = REVIEWED[end]
    assert len(pages) == cfg["pages"], "Page count changed"
    assert "\ufffd" not in text, "Replacement character in extracted text"
    rows, counts = [], []
    for physical, page in enumerate(pages, 1):
        lines = [line for line in page.splitlines() if line.strip()]
        assert "FRASER HEALTH AUTHORITY" in page
        if physical <= cfg["offset"]:
            assert end == 2014 and "CONTRACT TOTALS" in page
            assert "FOR THE YEAR ENDED MARCH 31, 2014" in page
            assert re.search(r"3,853\s+780\s+20\s+916\s+5,569", page)
            counts.append(0)
            continue
        assert lines[-1].strip() == str(physical - cfg["offset"]), (physical, "Footer changed")
        assert re.findall(r"FOR THE FISCAL YEAR ENDED MARCH 31, (\d{4})", page) == [str(end)]
        heads = [i for i, line in enumerate(lines) if HEADER.fullmatch(line.strip())]
        assert len(heads) == 1, (physical, "Table header changed")
        before = len(rows)
        for line in lines[heads[0] + 1:-1]:
            if line.strip().lower().startswith("total payments"):
                assert physical == len(pages), "Summary before final page"
                break
            match = ROW.fullmatch(line.strip())
            assert match, (physical, "Unparsed employee line", line)
            name, pay, expense = match.groups()
            assert "," in name and amount(pay) >= 75000
            rows.append(["fraser-health", name, None, amount(pay), amount(expense), physical])
        counts.append(len(rows) - before)
    totals = []
    for label in LABELS:
        match = re.findall(re.escape(label) + r"\s+([\d,]+)\s+([\d,]+)", text, re.I)
        assert len(match) == 1, (label, "Missing/duplicate summary")
        totals.append([amount(x) for x in match[0]])
    repeated = Counter(row[1] for row in rows)
    return rows, {
        "pdfPages": len(pages), "physicalPdfPages": [cfg["offset"] + 1, len(pages)],
        "rowsPerPhysicalPage": counts, "summaryPhysicalPdfPages": [len(pages)],
        "internalFiscalYearEnd": end, "allFiscalHeadersChecked": True,
        "allPageFootersSequential": True, "unparsedEmployeeLines": 0,
        "printedNamedRemuneration": totals[0][0], "printedNamedExpenses": totals[0][1],
        "underThresholdRemunerationExcluded": totals[1][0], "underThresholdExpensesExcluded": totals[1][1],
        "printedAllEmployeeRemuneration": totals[2][0], "printedAllEmployeeExpenses": totals[2][1],
        "printedSubtotalRemunerationResidual": totals[0][0] + totals[1][0] - totals[2][0],
        "printedSubtotalExpenseResidual": totals[0][1] + totals[1][1] - totals[2][1],
        "sourceDeclaredNamedCount": 5569 if end == 2014 else None,
        "sourceDeclaredNamedCountPhysicalPage": 1 if end == 2014 else None,
        "repeatedDisclosedNames": [{"name": n, "rows": c} for n, c in repeated.items() if c > 1],
        "exactDuplicateSourceRows": sum(c-1 for c in Counter(tuple(row[:5]) for row in rows).values() if c > 1),
    }


def independent_rows(pdf, end):
    """Reconstruct rows using MuPDF glyph decoding and positions, without layout text."""
    doc = fitz.open(pdf)
    rows = []
    offset = REVIEWED[end]["offset"]
    for physical, page in enumerate(doc, 1):
        if physical <= offset:
            continue
        words = page.get_text("words")
        heads = [w for w in words if w[4] == "EMPLOYEE"]
        assert len(heads) == 1, (physical, "Independent employee header")
        hy = heads[0][1]
        payhead = [w for w in words if w[4] in ("REMUNERATION", "RENUMERATION") and abs(w[1] - hy) < 1]
        expensehead = [w for w in words if w[4] == "EXPENSES" and abs(w[1] - hy) < 1]
        assert len(payhead) == len(expensehead) == 1
        cutoff = min([w[1] for w in words if w[4] == "Total" and w[1] > hy] + [10000])
        # Group all table words by baseline before interpreting any monetary cell.
        lines = defaultdict(list)
        for word in words:
            if hy + 2 < word[1] < cutoff - 1 and word[1] < page.rect.height - 55:
                lines[round(word[1], 0)].append(word)
        for y in sorted(lines):
            line = sorted(lines[y], key=lambda w: w[0])
            name = " ".join(w[4] for w in line if w[2] < payhead[0][0] - 10)
            pay = " ".join(w[4] for w in line if w[0] >= payhead[0][0] - 10 and w[2] < expensehead[0][0] - 1)
            expense = " ".join(w[4] for w in line if w[0] >= expensehead[0][0] - 1)
            assert "," in name and amount(pay) >= 75000, (physical, line)
            rows.append(["fraser-health", name, None, amount(pay), amount(expense), physical])
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/sector-health"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    sources, outputs = [], {}
    for end, cfg in REVIEWED.items():
        url = BASE + f"{end}/{end}EmployeeRemuneration.pdf"
        pdf = args.cache / f"fraser-{end}.pdf"
        if not pdf.exists():
            assert not args.offline, "Source missing in offline cache"
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read()
            assert data.startswith(b"%PDF-"), "Download is not a PDF"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(data)
        raw = pdf.read_bytes()
        assert digest(raw) == cfg["sha256"], "Source hash changed; fresh review required"
        text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
        rows, val = parse_layout(text, end)
        other = independent_rows(pdf, end)
        assert rows == other, next(((a,b) for a,b in zip(rows,other) if a != b), (len(rows),len(other)))
        assert not val["exactDuplicateSourceRows"], "Unexpected exact duplicates require review"
        if val["sourceDeclaredNamedCount"]:
            assert len(rows) == val["sourceDeclaredNamedCount"]
        pay, expense = sum(r[3] for r in rows), sum(r[4] for r in rows if r[4] is not None)
        assert (len(rows), pay, expense, val["printedNamedRemuneration"], val["printedNamedExpenses"]) == cfg["totals"], "Reviewed count or monetary control changed"
        assert [r for r in rows if r[4] is not None and r[4] < 0] == ([["fraser-health", "LUCKEN,BRENDA A", None, 91313, -5, 64]] if end == 2014 else []), "Reviewed negative amounts changed"
        val.update({"rowsCheckedWithIndependentPdfEngine": len(rows), "independentPdfEngine": "PyMuPDF word coordinates; primary extraction uses Poppler layout text", "sourceFingerprintLocked": True,
            "namedRemunerationSum": pay, "namedExpensesSum": expense,
            "remunerationResidual": pay-val["printedNamedRemuneration"], "expensesResidual": expense-val["printedNamedExpenses"],
            "summaryTotalReconciled": pay == val["printedNamedRemuneration"] and expense == val["printedNamedExpenses"],
            "missingExpenseRows": sum(r[4] is None for r in rows), "explicitZeroExpenseRows": sum(r[4] == 0 for r in rows),
            "negativeExpenseRows": sum(r[4] is not None and r[4] < 0 for r in rows),
            "negativeExpenseRowDetails": [dict(name=r[1], remuneration=r[3], expenses=r[4], physicalPdfPage=r[5]) for r in rows if r[4] is not None and r[4] < 0],
            "visuallyReviewedHeaderPhysicalPages": [1, 2] if end == 2014 else [1],
            "visuallyReviewedSummaryPhysicalPages": [cfg["pages"]],
            "allNegativeExpenseRowsVisuallyReviewed": True,
            "compiledBaselineComparison": {"baselineFile": "research/salaries/compiled-baseline.json.gzip", "compiledLabel": f"{end-1}/{end%100:02d}", "compiledRows": 0, "method": "The preserved baseline contains Fraser Health rows only for fiscal labels 2017/18, 2020/21 and 2023/24; these earlier periods add records without replacing compiled rows."},
        })
        label = f"{end-1}-{end%100:02d}"
        year = label.replace("-", "/")
        normalized = json.dumps(rows,ensure_ascii=False,separators=(",", ":")).encode()
        compressed = gzip.compress(normalized,compresslevel=9,mtime=0)
        filename = f"{label}.json.gzip"
        outputs[filename] = compressed
        source = dict(id=f"fraser-health-sofi-{label}", employerSlug="fraser-health", employerName="Fraser Health", sector="Health authorities", year=year,
            title=f"Fraser Health Statement of Financial Information {year}: employee remuneration and expenses", sourceUrl=url, indexUrl=INDEX, sourceIndexUrl=INDEX,
            sha256=digest(raw), pdfBytes=len(raw), file=filename, dataSha256=digest(compressed), normalizedSha256=digest(normalized),
            periodStart=f"{end-1}-04-01", periodEnd=f"{end}-03-31", periodType="fiscal", currency="CAD", scope="employee-remuneration", category="employee-remuneration",
            scopeDescription="Named employee payments equal to or greater than $75,000; employee schedule only", threshold=75000, thresholdComparison=">=", nameDisclosure="named",
            rowCount=len(rows), totalRemuneration=pay, totalDisclosedExpenses=expense, status="verified", verifiedOn="2026-10-31", validation=val,
            publicWarning=f"Displayed employee rows exceed the printed named remuneration subtotal by ${val['remunerationResidual']:,} and the expense subtotal by ${val['expensesResidual']:,}. The cause is unresolved; all published cells are retained unchanged.",
            notes=["Recovered directly from the issuer's official media storage; this historical schedule is not linked from its current reporting index.",
                "Cash-basis employee remuneration; employer benefit costs, contracted labour and physician fees are excluded. These are payment disclosures, not complete employee rosters or salary rates.",
                "Job titles are not published. Dash expenses remain missing; printed zero and negative amounts are retained. Names, initials, punctuation and repeated names remain as published.",
                f"The sum of displayed remuneration differs from the printed named subtotal by ${val['remunerationResidual']:+,}; expenses differ by ${val['expensesResidual']:+,}. The cause is unresolved. Every employee row agrees between two PDF engines; no amount was adjusted and exact monetary reconciliation is not claimed.",
            ])
        sources.append(source)
        print(json.dumps({"year":year,"rows":len(rows),"pay":pay,"expenses":expense,"validation":val},ensure_ascii=False))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, raw in outputs.items():
        (args.output/name).write_bytes(raw)
    (args.output/"sources.json").write_text(json.dumps(dict(version=1,rowSchema=["employerSlug","name","position","remuneration","expenses","pdfPage"],sources=sources),ensure_ascii=False,indent=2)+"\n")


if __name__ == "__main__":
    main()
