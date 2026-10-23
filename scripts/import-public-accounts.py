#!/usr/bin/env python3
"""Import the Province's published salary CSV schedules, with their source evidence.

Run from the repository root:
  python scripts/import-public-accounts.py --cache /tmp/pofbc-salary-sources

Only the source importer uses the network. The salary build consumes the checked-in,
deterministic JSON gzip files. No approximate person matching is used for expenses.
All tables are validated before any normalized output is written.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import unicodedata
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = "https://catalogue.data.gov.bc.ca/api/3/action/package_show?id="
DATASETS = {
    "employees": "e8a3fc19-6016-4c90-a5c0-eb35233d708e",
    "deputy-ministers": "c5df3a4d-2520-4dcb-8445-0cff5107bb92",
    "appointees": "d7a034ac-c316-4c57-beda-587de041b833",
    "travel": "0b67c6d7-bd13-442e-a80f-7e646a173b73",
}
TITLES = {
    "employees": "Other employees with a gross salary of $75,000 or more",
    "deputy-ministers": "Deputy Ministers and Associate Deputy Ministers",
    "appointees": "Order-in-Council, other appointees and employees not appointed under the Public Service Act",
}
CATEGORIES = {
    "employees": "employee-remuneration",
    "deputy-ministers": "deputy-minister-remuneration",
    "appointees": "appointee-remuneration",
}
OIC_2019_PDF = (
    "https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/"
    "government-finances/public-accounts/2018-19/"
    "pa-2018-19-crf-detailed-schedules-of-payments.pdf"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str, path: Path, offline: bool) -> bytes:
    if path.exists():
        return path.read_bytes()
    if offline:
        raise ValueError(f"Missing cached source: {path}")
    request = urllib.request.Request(url, headers={"User-Agent": "PofBC salary source importer"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def text_rows(raw: bytes) -> tuple[list[list[str]], str]:
    try:
        text = raw.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
        encoding = "cp1252"
    if "\ufffd" in text:
        raise ValueError("Source contains replacement characters; inspect its encoding")
    # csv.reader retains quoted punctuation and embedded line breaks. Wholly empty
    # records are discarded, including >1m empty records in the FYE2025 travel CSV.
    return [row for row in csv.reader(io.StringIO(text, newline="")) if any(x.strip() for x in row)], encoding


def normalized_text(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())


def name_key(value: str) -> tuple[str, ...]:
    """Preserve the disclosed surname/given boundary; never expand initials."""
    return tuple(normalized_text(part) for part in value.split(",", 1))


def amount(value: str) -> int | float | None:
    value = value.strip().replace(",", "").replace("$", "")
    value = value.replace("\u2212", "-").replace("\u2013", "-")
    if value in ("", "-", "\u2014"):
        return None
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"Invalid amount: {value!r}") from error
    if not number.is_finite():
        raise ValueError(f"Non-finite amount: {value!r}")
    return int(number) if number == number.to_integral_value() else float(number)


def parse_table(raw: bytes, kind: str, year: int) -> tuple[list[list], dict]:
    records, encoding = text_rows(raw)
    header_at = next((i for i, row in enumerate(records) if any(
        "salary and" in cell.lower() and "compensation" in cell.lower() for cell in row
    ) or row[0].strip().lower() in ("name", "names")), None)
    if header_at is None:
        raise ValueError(f"{kind} FYE{year}: expected table header not found")
    header = [cell.strip().lower() for cell in records[header_at]]
    pay_at = next((i for i, cell in enumerate(header) if cell in ("amount", "rounded")
                   or ("salary and" in cell and "compensation" in cell)), None)
    if pay_at is None:
        raise ValueError(f"{kind} FYE{year}: salary column not found")
    title_at = next((i for i, cell in enumerate(header) if cell in ("position title", "title")), None)
    travel_at = next((i for i, cell in enumerate(header) if cell == "travel"), None)
    internal_years = sorted(set(int(y) for y in re.findall(
        r"March\s+31,?\s+(20\d{2})", " ".join(" ".join(r) for r in records[:header_at]), re.I
    )))
    if internal_years and internal_years != [year] and not (kind == "appointees" and year == 2019 and internal_years == [2018]):
        raise ValueError(f"{kind} FYE{year}: source heading says {internal_years}")

    rows, nil_rows, summary_rows = [], [], []
    for row in records[header_at + 1:]:
        if not row[0].strip() or row[0].strip().lower() in ("total", "grand total"):
            summary_rows.append(row)
            continue
        if len(row) <= pay_at:
            raise ValueError(f"{kind} FYE{year}: truncated source row {row!r}")
        pay = amount(row[pay_at])
        if pay is None:
            # Nil-paid OIC appointments can refer to people paid in the deputy
            # schedule; do not invent a second payment or an employee record.
            nil_rows.append(row[0].strip())
            continue
        if kind == "employees" and pay < 75000:
            raise ValueError(f"{kind} FYE{year}: pay below declared threshold: {row!r}")
        if title_at is not None:
            position = row[title_at].strip() or None
        elif kind == "deputy-ministers":
            position = "Deputy Minister or Associate Deputy Minister"
        else:
            position = None
        expenses = amount(row[travel_at]) if travel_at is not None else None
        rows.append(["public-service", row[0].strip(), position, pay, expenses])

    if not rows:
        raise ValueError(f"{kind} FYE{year}: empty salary schedule")
    total = sum(Decimal(str(row[3])) for row in rows)
    reconciled_totals = 0
    for summary in summary_rows:
        if len(summary) > pay_at and amount(summary[pay_at]) is not None:
            if Decimal(str(amount(summary[pay_at]))) != total:
                raise ValueError(f"{kind} FYE{year}: source total does not reconcile")
            reconciled_totals += 1
    return rows, {
        "encoding": encoding,
        "header": records[header_at],
        "internalFiscalYearEnd": internal_years[0] if internal_years else None,
        "excludedNilPayRows": len(nil_rows),
        "excludedNilPayNames": nil_rows,
        "summaryRowsExcluded": len(summary_rows),
        "summaryTotalReconciled": reconciled_totals > 0,
        "repeatedNameAndPayRows": sum(n - 1 for n in Counter((name_key(row[1]), row[3]) for row in rows).values() if n > 1),
        "negativeRemunerationRows": sum(row[3] < 0 for row in rows),
    }


def parse_travel(raw: bytes, year: int) -> tuple[dict[tuple[str, ...], list[int | float]], dict]:
    records, encoding = text_rows(raw)
    header_at = next(i for i, row in enumerate(records) if row[0].strip().lower() == "name")
    internal_years = sorted(set(int(y) for y in re.findall(
        r"March\s+31,?\s+(20\d{2})", " ".join(" ".join(r) for r in records[:header_at]), re.I
    )))
    if internal_years and internal_years != [year]:
        raise ValueError(f"Travel FYE{year}: source heading says {internal_years}")
    header = [value.strip().lower() for value in records[header_at]]
    at = next(i for i, value in enumerate(header) if value in ("amount", "rounded"))
    by_name = defaultdict(list)
    count = 0
    disclosed_zero = 0
    for row in records[header_at + 1:]:
        if not row[0].strip() or row[0].strip().lower() in ("total", "grand total"):
            continue
        value = amount(row[at])
        if value is None:
            continue
        if value == 0:
            disclosed_zero += 1
        elif value < 5000:
            raise ValueError(f"Travel FYE{year}: below the disclosed $5,000 threshold")
        by_name[name_key(row[0])].append(value)
        count += 1
    return by_name, {"rowCount": count, "encoding": encoding, "threshold": 5000,
                     "internalFiscalYearEnd": internal_years[0] if internal_years else None,
                     "explicitlyDisclosedZeroRows": disclosed_zero,
                     "ambiguousNames": sum(len(values) > 1 for values in by_name.values())}


def corroborate_oic_2019(raw: bytes, rows: list[list], cache: Path, offline: bool) -> dict:
    pdf = cache / "public-accounts-2019.pdf"
    pdf_bytes = download(OIC_2019_PDF, pdf, offline)
    text = subprocess.check_output(["pdftotext", "-raw", "-f", "11", "-l", "23", str(pdf), "-"], text=True)
    plain = normalized_text(text)
    matches = sum(normalized_text(row[1] + (row[2] or "") + str(row[3])) in plain for row in rows)
    if matches != len(rows):
        raise ValueError(f"FYE2019 OIC: only {matches}/{len(rows)} rows corroborated against published PDF")
    return {"note": "CSV preamble says March 31, 2018. Every name, position and amount matches the official 2018/19 PDF, whose schedule heading says March 31, 2019.",
            "url": OIC_2019_PDF, "sha256": sha256(pdf_bytes), "pdfPages": [11, 23],
            "matchedRows": matches, "csvSha256": sha256(raw)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/pofbc-salary-sources"))
    parser.add_argument("--output", type=Path, default=ROOT / "research/salaries/public-accounts")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verified-on", default=date.today().isoformat())
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    datasets, resources, raws = {}, {}, {}
    for kind, dataset_id in DATASETS.items():
        catalogue_path = args.cache / ("public-service-catalogue.json" if kind == "employees" else dataset_id + ".json")
        catalogue_bytes = download(CATALOGUE + dataset_id, catalogue_path, args.offline)
        dataset = json.loads(catalogue_bytes)
        dataset = dataset.get("result", dataset)
        datasets[kind] = dataset
        resources[kind], raws[kind] = {}, {}
        for resource in dataset["resources"]:
            match = re.search(r"FYE (\d{4})", resource["name"])
            if not match or resource.get("format", "").upper() != "CSV":
                continue
            year = int(match.group(1))
            prefix = "public-service" if kind == "employees" else kind
            raw = download(resource["url"], args.cache / f"{prefix}-{year}.csv", args.offline)
            resources[kind][year] = resource
            raws[kind][year] = raw

    outputs, sources, excluded, all_rows = {}, [], [], defaultdict(list)
    for year in sorted(raws["employees"]):
        label = f"{year - 1}/{str(year)[-2:]}"
        slug = label.replace("/", "-")
        travel, travel_validation = parse_travel(raws["travel"][year], year)
        pending = []
        for kind in ("employees", "deputy-ministers", "appointees"):
            raw = raws[kind].get(year)
            if raw is None:
                continue
            resource = resources[kind][year]
            if kind == "appointees" and raw == raws["employees"][year]:
                excluded.append({"id": f"public-accounts-{slug}-{kind}", "year": label,
                    "sourceUrl": resource["url"], "sha256": sha256(raw), "status": "excluded-wrong-schedule",
                    "reason": "Resource labelled OIC/appointees serves the byte-identical Other Employees CSV. It is already imported once in the employee schedule.",
                    "duplicatesSourceId": f"public-accounts-{slug}-employees"})
                continue
            rows, validation = parse_table(raw, kind, year)
            if kind == "appointees" and year == 2019:
                validation["fiscalYearCorroboration"] = corroborate_oic_2019(raw, rows, args.cache, args.offline)
            source_id = f"public-accounts-{slug}-{kind}"
            pending.append((kind, source_id, rows, validation))

        if year == 2024:
            # Reviewed overlap: the OIC entry explicitly calls Arend Associate
            # Deputy Minister; it repeats the deputy schedule's same payment.
            # Keep its deputy entry, including that schedule's disclosed travel.
            deputy_rows = next(rows for kind, _, rows, _ in pending if kind == "deputy-ministers")
            if not any(name_key(row[1]) == name_key("Arend,Elenore C.G.") and row[3] == 229841 for row in deputy_rows):
                raise ValueError("Reviewed FYE2024 Arend deputy payment changed")
            for kind, _, rows, validation in pending:
                if kind != "appointees":
                    continue
                overlap = [row for row in rows if name_key(row[1]) == name_key("Arend,Elenore C.G.") and row[3] == 229841]
                if len(overlap) != 1:
                    raise ValueError("Reviewed FYE2024 Arend OIC payment changed")
                rows.remove(overlap[0])
                validation["reviewedDuplicatePaymentExclusions"] = [{
                    "name": overlap[0][1], "position": overlap[0][2], "remuneration": overlap[0][3],
                    "retainedSourceId": f"public-accounts-{slug}-deputy-ministers",
                    "reason": "The OIC entry is explicitly an Associate Deputy Minister and repeats the exact name and annual salary in the deputy schedule; retain that payment once, with its disclosed travel.",
                }]

        name_counts = Counter(name_key(row[1]) for _, _, rows, _ in pending for row in rows)
        exact_payments = defaultdict(list)
        for kind, source_id, rows, validation in pending:
            matched = 0
            for row in rows:
                exact_payments[(name_key(row[1]), row[3])].append(source_id)
                if kind != "deputy-ministers":
                    key = name_key(row[1])
                    candidates = travel.get(key, [])
                    if name_counts[key] == 1 and len(candidates) == 1:
                        row[4] = candidates[0]
                        matched += 1
            raw = raws[kind][year]
            resource = resources[kind][year]
            filename = f"{slug}-{kind}.json.gzip"
            normalized = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            compressed = gzip.compress(normalized, compresslevel=9, mtime=0)
            outputs[filename] = compressed
            source = {
                "id": source_id, "employerSlug": "public-service", "employerName": "Provincial government",
                "sector": "Government", "year": label, "slug": slug,
                "file": filename,
                "title": f"Public Accounts {label}: {TITLES[kind]}",
                "sourceUrl": resource["url"], "catalogueUrl": "https://catalogue.data.gov.bc.ca/dataset/" + DATASETS[kind],
                "sha256": sha256(raw), "normalizedSha256": sha256(normalized), "dataSha256": sha256(compressed),
                "periodStart": f"{year - 1}-04-01", "periodEnd": f"{year}-03-31",
                "category": CATEGORIES[kind], "scope": CATEGORIES[kind], "scopeDescription": TITLES[kind],
                "threshold": 75000 if kind == "employees" else None,
                "currency": "CAD", "rowCount": len(rows),
                "totalRemuneration": float(sum(Decimal(str(row[3])) for row in rows)),
                "totalDisclosedExpenses": float(sum(Decimal(str(row[4])) for row in rows if row[4] is not None)),
                "verifiedOn": args.verified_on, "status": "verified", "validation": validation,
                "expensesNote": "Travel, not all expenses. Missing means not disclosed or no unique exact full-name match; it does not mean zero.",
            }
            source["notes"] = [source["scopeDescription"], source["expensesNote"],
                "Legislative Assembly member and Premier/minister payments are separate schedules and are not included in this import."]
            if year <= 2018:
                source["notes"].append("The OIC/appointee schedule for this fiscal year is not imported: its catalogue resource incorrectly supplies the Other Employees schedule.")
            if validation["negativeRemunerationRows"]:
                source["notes"].append("A negative payment is retained exactly as reported in the source; it can represent a recovery rather than salary earned.")
            if kind != "deputy-ministers":
                source["travelSource"] = {
                    "url": resources["travel"][year]["url"], "sha256": sha256(raws["travel"][year]),
                    **travel_validation, "matchedSalaryRows": matched,
                    "matching": "Exact normalized full name, unique in both the combined annual salary schedules and travel schedule. No initials or approximate names.",
                }
                source["notes"].append("Reported travel uses the separate $5,000-threshold travel schedule, matched only on a unique exact full name: " + resources["travel"][year]["url"])
            sources.append(source)
            all_rows[year].extend(rows)
        # A published schedule can list the same disclosed name/pay under two
        # different positions. Preserve those source rows; they are not proof
        # of a duplicate person. Cross-schedule repetitions need investigation.
        overlaps = {str(key): ids for key, ids in exact_payments.items() if len(set(ids)) > 1}
        if overlaps:
            raise ValueError(f"FYE{year}: duplicate name/pay across salary rows requires review: {overlaps}")

    # Keep the proof of the compiler's one-year error next to the replacement data.
    legacy_path = ROOT / "public/salaries/employers/public-service.json.gzip"
    evidence = {}
    if legacy_path.exists():
        legacy = json.loads(gzip.decompress(legacy_path.read_bytes()))
        legacy_index_path = ROOT / "public/salaries/employers/index.json"
        legacy_years = json.loads(legacy_index_path.read_text())["years"]
        if "2020/21" in legacy_years:
            index = legacy_years.index("2020/21")
            legacy_set = {(name_key(row[0] or ""), row[2]) for row in legacy if row[4] == index}
            official_set = {(name_key(row[1]), row[3]) for row in parse_table(raws["employees"][2020], "employees", 2020)[0]}
            if legacy_set == official_set:
                evidence = {"finding": "Compiled public-service 2020/21 is the official 2019/20 Other Employees schedule.",
                    "compiledYear": "2020/21", "actualPeriod": "2019/20", "compiledRows": len(legacy_set),
                    "officialRows": len(official_set), "identicalNamePayPairs": len(legacy_set & official_set),
                    "compiledFileSha256": sha256(legacy_path.read_bytes()),
                    "officialCsvSha256": sha256(raws["employees"][2020]),
                    "actual2020_21EmployeeRows": len(parse_table(raws["employees"][2021], "employees", 2021)[0])}
    existing = args.output / "sources.json"
    if not evidence and existing.exists():
        evidence = json.loads(existing.read_text()).get("compiledYearCorrection", {})

    registry = {"version": 1, "rowSchema": ["employerSlug", "name", "position", "remuneration", "expenses"],
        "sources": sources, "excludedSources": excluded, "compiledYearCorrection": evidence,
        "coverageNotes": [
            "These schedules cover the Province's public service and separately disclosed deputy ministers and appointees. They are not an employee list for every public sector employer.",
            "Other Employees are subject to the published $75,000 threshold. Deputy and appointee schedules include payments below that threshold.",
            "The source catalogue's OIC resources for FYE2007–2018 are the wrong schedule and are excluded. Their absence is a source defect, not evidence of no appointee pay.",
            "Legislative Assembly members and Premier/minister pay are different schedules and are not included here.",
            "Named payments are annual amounts, not salary rates or proof of a full year of employment. Negative payments are retained when the source reports them.",
        ]}
    # All sources, totals, periods and overlap checks succeeded before replacing outputs.
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, data in outputs.items():
        (args.output / filename).write_bytes(data)
    (args.output / "sources.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"Imported {len(sources)} schedules, {sum(s['rowCount'] for s in sources):,} rows across {len(all_rows)} fiscal years; excluded {len(excluded)} wrong-schedule resources.")
    for year, rows in sorted(all_rows.items()):
        print(f"{year - 1}/{str(year)[-2:]}: {len(rows):,} named payment rows")


if __name__ == "__main__":
    main()
