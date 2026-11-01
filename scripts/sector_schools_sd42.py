#!/usr/bin/env python3
"""Rebuild pinned SD42 employee/trustee disclosures from original district PDFs.

The reviewed manifest pins every original fingerprint, cohort count, component sum,
and exact source-control residual. Source layout exceptions are explicit. Poppler
rows are corroborated against independently grouped PyMuPDF word coordinates.
This script never edits compiled data, aliases, registries, or application output.
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
import urllib.request
from decimal import Decimal
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "research/salaries/sector-schools"
SLUG = "maple-ridge-pitt-meadows-school-district"
EMPLOYER = "School District No. 42 (Maple Ridge - Pitt Meadows)"
REVIEWED_ON = "2026-10-31"

amount=r'(?:[0-9][0-9,]*(?:\.[0-9]{2})?|-)'
pat=re.compile(r'(?<!\S)(?:\$\s*)?([0-9][0-9,]*(?:\.[0-9]{2})?)(?:\s+\$?\s*(\(?[0-9][0-9,]*(?:\.[0-9]{2})?\)?|-))?\s*([*]*)\s*$')
def num(x):return None if not x or x.strip()=='-' else str(Decimal(x.replace(',','').replace('$','').replace('(','-').replace(')','').strip()))
def parse(y, cache_dir):
 raw=(cache_dir / f'sd42-{y}.pdf').read_bytes();txt=subprocess.check_output(['pdftotext','-layout',str(cache_dir / f'sd42-{y}.pdf'),'-']).decode();pages=txt.split('\f');mode=None;rows=[];errors=[];controls={};controlpending=False
 for p,text in enumerate(pages,1):
  for l in text.splitlines():
   s=l.strip();u=s.upper()
   if re.fullmatch(r'(A\. )?(LIST OF )?ELECTED OFFICIALS',u):mode='school-trustees';continue
   if re.match(r'(B\. )?EMPLOYEES.*WHOSE REMUNERATION EXCEEDS|DETAILED EMPLOYEES EXCEEDING',u):mode='employee-remuneration';continue
   if mode and (u.startswith('TOTAL') or u.startswith('WHOSE REMUNERATION EXCEEDS')):
    vals=re.findall(r'[0-9][0-9,]*(?:\.[0-9]{2})?',s)
    if mode=='employee-remuneration' and ('EXCEED' in u or controlpending):
     if '75,000' in vals: vals.remove('75,000')
     if len(vals)==2:controls[mode]=vals;mode=None;controlpending=False;continue
     controlpending=True;continue
    if mode=='school-trustees' and 'ELECTED' in u:
     if len(vals)==2:controls[mode]=vals;mode=None;continue
   if mode:
    m=pat.search(l)
    parts=re.split(r'\s{2,}', l[:m.start()].strip()) if m else []
    if m and len(parts)==1 and y in [2014,2015,2016,2017]: parts.append(None)
    if m and len(parts)==1 and y>=2025:
     manual={'DO COITO ANTUNES MAFRA, DULCE TEACHER':('DO COITO ANTUNES MAFRA, DULCE','TEACHER'),'DOS LIMA LLOYD, GABRIEL LUIS * MANAGER, MARKETING & RECRUITMENT, INTERNATIONAL EDUCATION':('DOS LIMA LLOYD, GABRIEL LUIS *','MANAGER, MARKETING & RECRUITMENT, INTERNATIONAL EDUCATION'),'DOS LIMA LLOYD, GABRIEL LUIS * MANAGER, MARKETING & RECRUITMENT, INTERNATIONAL ED.':('DOS LIMA LLOYD, GABRIEL LUIS *','MANAGER, MARKETING & RECRUITMENT, INTERNATIONAL ED.'),'ESKANDARI ALOUGHREH, SUSAN TEACHER':('ESKANDARI ALOUGHREH, SUSAN','TEACHER'),'FISCHER NORMAN, HEATHER A. TEACHER':('FISCHER NORMAN, HEATHER A.','TEACHER'),'PENACERRADA, CARLO GATCHALITEACHER':('PENACERRADA, CARLO GATCHALI','TEACHER'),'PERALEDA, JAVIER FRANCISCO TEACHER':('PERALEDA, JAVIER FRANCISCO','TEACHER'),'ROWLEDGE-TOSCANI, SHERALYN TEACHER':('ROWLEDGE-TOSCANI, SHERALYN','TEACHER')}
     parts=list(manual.get(parts[0],parts))
    if m and len(parts)==2:
     name,pos=parts; pay,exp,annotations=m.groups()
     if not (',' in name and (pos is None or re.search('[A-Z]',pos))):
      continue
     rows.append({'name':name.strip(),'position':pos.strip() if pos else None,'raw':[pay.strip(),exp or ''],'remuneration':num(pay),'expenses':num(exp),'page':p,'category':mode,'sourceLine':l,'annotations':annotations})
    elif ',' in s and re.search(r'\d',s) and not re.search(r'EXCEED|75,000|SCHOOL|District|YEAR ENDED|\* Includes|\*\*',s,re.I):errors.append({'page':p,'text':s})
 out={'year':y,'sourceSha256':hashlib.sha256(raw).hexdigest(),'rows':rows,'errors':errors,'controls':controls}
 for cat in ['employee-remuneration','school-trustees']:
  rs=[r for r in rows if r['category']==cat];comp=[sum(Decimal(r[k] or '0') for r in rs) for k in ['remuneration','expenses']];ct=controls.get(cat)
  out[cat]={'rowCount':len(rs),'totals':[str(x) for x in comp],'residuals':[str(x-Decimal(c.replace(',',''))) for x,c in zip(comp,ct)] if ct else None,'pages':sorted(set(r['page'] for r in rs))}
 return out

def canonical_text(value):
    return re.sub(r"[\s$]", "", value)


def corroborate_rows(parsed, pdf_path):
    """Compare complete source row text and multiplicity using PDF word geometry."""
    doc = fitz.open(pdf_path)
    grouped = {}
    for physical_page in sorted({row["page"] for row in parsed["rows"]}):
        lines = []
        for word in sorted(doc[physical_page - 1].get_text("words"), key=lambda w: ((w[1] + w[3]) / 2, w[0])):
            center = (word[1] + word[3]) / 2
            line = next((entry for entry in reversed(lines[-3:]) if abs(entry[0] - center) < 2.2), None)
            if line:
                line[1].append(word)
            else:
                lines.append([center, [word]])
        grouped[physical_page] = [
            (center, " ".join(word[4] for word in sorted(words, key=lambda word: word[0])))
            for center, words in lines
        ]
    used = set()
    previous_position = (0, 0)
    for row in parsed["rows"]:
        matches = [(index, center) for index, (center, text) in enumerate(grouped[row["page"]])
                   if canonical_text(text) == canonical_text(row["sourceLine"])]
        if len(matches) != 1 or (row["page"], matches[0][0]) in used:
            raise ValueError(f"Independent PDF row mismatch: {parsed['year']} p{row['page']}: {row['sourceLine']}")
        used.add((row["page"], matches[0][0]))
        row["pdfWordY"] = matches[0][1]
        current_position = (row["page"], row["pdfWordY"])
        if current_position <= previous_position:
            raise ValueError("Source row order differs between PDF readers")
        previous_position = current_position
        page_text = " ".join(doc[row["page"] - 1].get_text().split())
        if not re.search(r"JUNE\s+30,?\s*" + str(parsed["year"]), page_text, re.I):
            raise ValueError(f"Reporting-year heading missing on salary page {row['page']}")
    doc.close()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def write_gzip(path, value):
    raw = json_bytes(value)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    path.write_bytes(compressed)
    return hashlib.sha256(compressed).hexdigest(), hashlib.sha256(raw).hexdigest()


def dollars(value):
    if value is None:
        return None
    number = Decimal(value)
    return int(number) if number == number.to_integral() else float(number)


def build(cache_dir, output_dir, download=False):
    manifest = json.loads((COLLECTION / "reviewed-inputs.json").read_text())
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    validations = []
    for item in manifest["inputs"]:
        if item["status"] != "accepted-native-text":
            continue
        year = item["endingYear"]
        pdf = cache_dir / item["cacheFile"]
        if not pdf.exists() and download:
            request = urllib.request.Request(item["retrievedUrl"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                pdf.write_bytes(response.read())
        if not pdf.exists():
            raise FileNotFoundError(f"Missing {pdf}; use --download to retrieve the pinned original")
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Original PDF fingerprint changed: {year}")
        parsed = parse(year, cache_dir)
        if parsed["errors"]:
            raise ValueError(f"Unparsed table text: {year}: {parsed['errors']}")
        for category, expected in item["expectedCohorts"].items():
            if parsed[category] != expected:
                raise ValueError(f"Reviewed cohort controls changed: {year} {category}")
        if parsed["controls"] != item["expectedPrintedControls"]:
            raise ValueError(f"Printed controls changed: {year}")
        corroborate_rows(parsed, pdf)
        fiscal_year = f"{year - 1}/{str(year)[2:]}"
        for category in ["employee-remuneration", "school-trustees"]:
            selected = [row for row in parsed["rows"] if row["category"] == category]
            suffix = "employees" if category == "employee-remuneration" else "trustees"
            file_stem = f"sd42-{year}-{suffix}"
            rows = []
            for row in selected:
                # Asterisks are source footnote markers, preserved in raw evidence.
                name = re.sub(r"^\*+\s*|\s*\*+$", "", row["name"]).strip()
                rows.append([SLUG, name, row["position"], dollars(row["remuneration"]), dollars(row["expenses"]), row["page"]])
            data_hash, normalized_hash = write_gzip(output_dir / f"{file_stem}.json.gzip", rows)
            evidence = {
                "sourceKey": f"sd42-{year}", "originalSha256": item["sha256"],
                "componentColumns": ["remuneration", "expenses"], "rows": selected,
                "printedNamedControls": parsed["controls"][category],
                "exactControlResiduals": parsed[category]["residuals"],
            }
            provenance_hash, _ = write_gzip(output_dir / f"{file_stem}-evidence.json.gzip", evidence)
            control = parsed[category]
            residuals = [dollars(value) for value in control["residuals"]]
            notes = [
                "Fiscal reporting period is July 1 to June 30, confirmed from the original salary-schedule headings. Upload dates and calendar labels are not used as the reporting period.",
                "These are published payments, including disclosed taxable benefits and other compensation; they are not annual base salary rates or a complete employee roster. Expenses remain separate from remuneration.",
                "Published names, initials, titles and negative amounts are retained. Dashes and blank expenses remain null; explicit zero remains zero. Footnote asterisks are retained in row evidence and excluded from display names.",
                "Named employee and elected trustee schedules are separate cohorts. Under-threshold aggregate payroll, employer premiums, suppliers and financial-statement totals are not individual records.",
                "Every complete source row, amount and physical PDF page agrees between Poppler layout text and independently grouped PyMuPDF word coordinates. Original table layouts and the explicit joined-name/title exceptions were visually reviewed.",
            ]
            if category == "employee-remuneration" and year in [2014, 2015, 2016, 2017]:
                notes.append("This employee schedule does not publish job titles; positions remain null.")
            if year in [2006, 2010]:
                notes.append("Some disclosed name cells contain trailing numeric tokens (for example 23 or 11). Those published tokens are retained verbatim; no unproved identity correction has been made.")
            if year >= 2025:
                notes.append("The source prints whole dollars. Row-minus-printed-control residuals in remuneration and expenses are " + str(residuals) + " CAD. Individual values are retained without adjustment; no cause for these differences is asserted.")
                if category == "employee-remuneration":
                    notes.append("Long names and titles sometimes touch or overlap in the rendered table. Reviewed name/title boundaries are explicit in the importer; the published clipped name 'PENACERRADA, CARLO GATCHALI' in 2025 is retained without expanding its ending.")
            source = {
                "id": f"schools-{file_stem}", "inputKey": f"sd42-{year}",
                "employerSlug": SLUG, "employerName": EMPLOYER, "sector": "School districts",
                "year": fiscal_year, "slug": fiscal_year.replace("/", "-"),
                "periodType": "fiscal", "periodStart": f"{year - 1}-07-01", "periodEnd": f"{year}-06-30",
                "title": f"{EMPLOYER}, year ended June 30, {year}: {suffix}",
                "sourceUrl": item["sourceUrl"], "sourceIndexUrl": item["sourceIndexUrl"], "sha256": item["sha256"],
                "file": f"{file_stem}.json.gzip", "dataSha256": data_hash, "normalizedSha256": normalized_hash,
                "provenanceFile": f"{file_stem}-evidence.json.gzip", "provenanceSha256": provenance_hash,
                "category": category, "scope": "named-employees-over-threshold" if suffix == "employees" else "school-trustees",
                "scopeDescription": "Published employees with remuneration over $75,000" if suffix == "employees" else "Published elected trustees; no employee threshold is applied",
                "threshold": 75000 if suffix == "employees" else None, "thresholdRule": "over" if suffix == "employees" else None,
                "currency": "CAD", "amountUnit": "dollars", "amountPrecision": "whole-dollars" if year >= 2025 else "cents",
                "nameDisclosure": "published-name-as-disclosed", "positionDisclosure": "published-where-present",
                "rowCount": len(rows), "totalRemuneration": dollars(control["totals"][0]), "totalExpenses": dollars(control["totals"][1]),
                "pages": control["pages"], "status": "verified", "sourceKind": "official-pdf", "verifiedOn": REVIEWED_ON,
                "notes": notes,
                "publicWarning": (f"Sum of published row amounts minus the printed named-cohort subtotal: remuneration {residuals[0]:+g} CAD; expenses {residuals[1]:+g} CAD. Values are retained as printed; the cause is unconfirmed.") if any(residuals) else None,
                "validation": {
                    "originalFingerprintVerified": True, "reportingPeriodVerifiedOnEverySalaryPage": True,
                    "rowsByPhysicalPage": dict(sorted(collections.Counter(row[5] for row in rows).items())),
                    "independentReaders": ["Poppler layout text", "PyMuPDF independently grouped PDF word coordinates"],
                    "completeRowTextAmountsOrderAndMultiplicityAgree": True, "rowsIndependentlyChecked": len(rows),
                    "unparsedInterRowText": 0, "componentColumns": ["remuneration", "expenses"],
                    "printedControlTotals": parsed["controls"][category], "computedComponentTotals": control["totals"],
                    "controlResiduals": residuals, "allComponentSubtotalsExact": not any(residuals),
                    "missingExpenses": sum(row[4] is None for row in rows), "negativeExpenses": sum(row[4] is not None and row[4] < 0 for row in rows),
                    "publishedThresholdExceptions": sum(row[3] <= 75000 for row in rows) if suffix == "employees" else None,
                },
            }
            sources.append(source)
            validations.append({key: source[key] for key in ["id", "rowCount", "totalRemuneration", "totalExpenses", "validation"]})
    output = {
        "version": 1, "reviewed": REVIEWED_ON,
        "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses", "pdfPage"],
        "coverageNotes": ["SD42 original fiscal employee and trustee schedules. Compiled data are untouched; no alias or duplicate replacement decision is encoded here."],
        "sources": sources,
        "unparsedSources": [dict(item, nextAction="OCR all original salary pages; independently verify every name, amount, reporting period and complete cohort controls before acceptance") for item in manifest["inputs"] if item["status"] == "ocr-needed"],
    }
    (output_dir / "sources.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    (output_dir / "validation.json").write_text(json.dumps({"reviewed": REVIEWED_ON, "recordCount": sum(source["rowCount"] for source in sources), "sources": validations}, indent=2) + "\n")
    print(f"Verified {len(sources)} cohorts and {sum(source['rowCount'] for source in sources):,} source records.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".cache/sector-schools")
    parser.add_argument("--output-dir", type=Path, default=COLLECTION)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    build(args.cache_dir, args.output_dir, args.download)


if __name__ == "__main__":
    main()
