"""Curate compact evidence and a separate bounded-search audit inventory.

Original evidence is read only. Extracts preserve whole source PDF pages; no
annotations, retyping, cropping, resampling or changes to original files occur.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import fitz

BASE = Path(__file__).parent.resolve()
SELECTION = BASE / "evidence-selection"
SELECTION.mkdir(exist_ok=True)
TODAY = "2026-10-21"


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def info(path, **extra):
    p = BASE / path
    data = p.read_bytes()
    out = dict(path=str(p.relative_to(BASE)), absolute_path=str(p),
               bytes=len(data), sha256=sha(data), **extra)
    if p.suffix.lower() == ".pdf":
        with fitz.open(p) as doc:
            out["pdf_pages"] = len(doc)
    return out


def extract(sid, original, pages, labels):
    src_path = BASE / original
    original_hash = sha(src_path.read_bytes())
    original_doc = fitz.open(src_path)
    dest = fitz.open()
    for p in pages:
        dest.insert_pdf(original_doc, from_page=p - 1, to_page=p - 1)
    rel = f"evidence-selection/{sid}-cited-pages.pdf"
    target = BASE / rel
    # Deterministic overwrite of derived selection only; source is never changed.
    if target.exists():
        target.unlink()
    dest.save(target, garbage=4, deflate=True)
    dest.close()
    check = fitz.open(target)
    mapping = []
    extracts = []
    for i, n in enumerate(pages):
        original_page, copied_page = original_doc[n - 1], check[i]
        original_text = original_page.get_text()
        copied_text = copied_page.get_text()
        original_render = original_page.get_pixmap(matrix=fitz.Matrix(1, 1),
                                                  colorspace=fitz.csRGB, alpha=False)
        copied_render = copied_page.get_pixmap(matrix=fitz.Matrix(1, 1),
                                              colorspace=fitz.csRGB, alpha=False)
        assert original_text == copied_text, (sid, n, "text differs")
        assert original_render.samples == copied_render.samples, (sid, n, "render differs")
        assert original_page.rect == copied_page.rect, (sid, n, "page size differs")
        mapping.append(dict(extract_pdf_page=i + 1, original_pdf_page=n,
                            original_printed_page=labels[i],
                            page_text_sha256=sha(original_text.encode()),
                            rendered_rgb_72dpi_sha256=sha(original_render.samples),
                            render_width=original_render.width,
                            render_height=original_render.height,
                            source_and_extract_render_identical=True,
                            source_and_extract_text_identical=True))
        extracts.append(f"=== EXTRACT PAGE {i + 1}; ORIGINAL PDF PAGE {n}; PRINTED {labels[i]} ===\n" + original_text)
    text_rel = f"evidence-selection/{sid}-cited-pages.txt"
    (BASE / text_rel).write_text("\n\n".join(extracts))
    original_doc.close()
    check.close()
    assert sha(src_path.read_bytes()) == original_hash
    return [info(rel, representation="faithful_whole_page_pdf_extract",
                 source_ids=[sid], original_path=original,
                 original_sha256=original_hash, page_map=mapping),
            info(text_rel, representation="searchable_text_of_selected_pages",
                 source_ids=[sid], derived_from_path=rel,
                 warning="Search aid only; the PDF pages are the visual legal evidence.")]


catalogue = json.loads((BASE / "sources.json").read_text())
claims = json.loads((BASE / "claims.json").read_text())
# Two previously web-only catalogue/guidance pages were preserved at their exact
# cited URLs while preparing this manifest. This changes metadata, not claims.
retrievals = json.loads((BASE / "evidence-original-retrievals.json").read_text())
for row in retrievals:
    if row.get("path"):
        s = next(s for s in catalogue if s["id"] == row["source_id"])
        s["local_files"] = [row["path"]]
        s["retrieval_status"] = "retrieved; exact cited page preserved for evidence-manifest preparation"
        s["sha256"] = row["sha256"]
dump(BASE / "sources.json", catalogue)

classes = {
    "used_positive_or_corroboration": [2, 3, 4, 5, 9, 15, 18, 19, 20],
    "archival_lead_or_guard": [1, 6, 12, 16, 17],
    "screened_or_index": [7, 8, 10, 13, 14],
    "not_retrieved": [11],
}
class_by_id = {f"R4H-{n:03d}": c for c, nums in classes.items() for n in nums}

# Selected pages retain full page dimensions and contents. The medical article
# selection contains the affiliation page relevant to this governance research.
specs = {
    "R4H-001": ("raw/health-authority-performance.pdf", [33, 51, 56, 57],
                 ["section 1 p.7", "section 1 p.25", "section 1 p.30", "section 1 p.31"]),
    "R4H-005": ("raw/buchan1991.pdf", [1], ["1382"]),
    "R4H-015": ("foi-followup/misc1995c53.pdf", [1, 4, 22], ["925", "928", "946"]),
    "R4H-018": ("foi-followup/foippa1996original.pdf", [37, 38, 39, 55, 56],
                 ["37", "38", "39", "historical table ii", "historical table iii"]),
    "R4H-020": ("foi-followup/table1998.pdf", [1, 32, 33], ["i", "27", "28"]),
}
original_files = {
    "R4H-001": "raw/health-authority-performance.pdf",
    "R4H-002": "raw/hansard_1987_04_27.html",
    "R4H-003": "raw/hansard_1988_04_27.html",
    "R4H-004": "raw/hansard_1988_06_09.html",
    "R4H-005": "raw/buchan1991.pdf",
    "R4H-006": "raw/gazette_part2_catalogue.html",
    "R4H-007": "raw/mo_index_2001.xml",
    "R4H-008": "raw/mo_index_2002.xml",
    "R4H-009": "raw/bccdc_2016.pdf",
    "R4H-010": "raw/hstats1978-index.html",
    "R4H-012": "raw/bcarchives-government-records.html",
    "R4H-013": "raw/c2_route_2",
    "R4H-014": "raw/year-1979.xml",
    "R4H-015": "foi-followup/misc1995c53.pdf",
    "R4H-016": "foi-followup/foippa1996supp.pdf",
    "R4H-017": "foi-followup/haa1993.pdf",
    "R4H-018": "foi-followup/foippa1996original.pdf",
    "R4H-019": "foi-followup/oic451-route/1321_1995.pdf",
    "R4H-020": "foi-followup/table1998.pdf",
}
text_mates = {
    "R4H-002": "raw/hansard_1987_04_27.txt",
    "R4H-003": "raw/hansard_1988_04_27.txt",
    "R4H-004": "raw/hansard_1988_06_09.txt",
    "R4H-009": "raw/bccdc_2016.txt",
    "R4H-016": "foi-followup/foippa1996supp.txt",
    "R4H-017": "foi-followup/haa1993.txt",
    "R4H-019": "foi-followup/oic451-route/1321_1995.txt",
}
source_rows, compact_files, index_files = [], [], []
for s in catalogue:
    sid = s["id"]
    classification = class_by_id[sid]
    claim_ids = [c["id"] for c in claims if sid in c.get("source_ids", [])]
    original = original_files.get(sid)
    originals = [info(original, representation="complete_retrieved_original", source_ids=[sid])] if original else []
    if sid in specs:
        selected = extract(sid, *specs[sid])
    elif original:
        selected = list(originals)
        if sid in text_mates:
            selected.append(info(text_mates[sid], representation="searchable_text_of_original",
                                 source_ids=[sid], derived_from_path=original))
    else:
        selected = []
    package_group = "audit_index" if classification == "screened_or_index" else (
        "unretrieved_lead_record_only" if classification == "not_retrieved" else "compact_claim_or_lead_evidence")
    row = dict(source_id=sid, title=s["title"], url=s["url"], classification=classification,
               package_group=package_group, claim_ids=claim_ids,
               use=s.get("newness"), pinpoint=s.get("pinpoint"),
               original_files=originals, selected_files=selected,
               retrieval_status="complete_original_retrieved" if original else "full_source_not_retrieved")
    if sid == "R4H-011":
        row["retrieval_limit"] = s["retrieval_status"]
        row["accepted_for_commencement_claim"] = False
    if sid == "R4H-009":
        row["evidential_limit"] = "Narrative corroboration only; no BCCDC participant certificate or numbered-society mapping supplied."
    if sid == "R4H-001":
        row["evidential_limit"] = "The record schedule is retrieved, but the described three binders and individual agreements are not."
    if sid == "R4H-020":
        row["evidential_limit"] = "Official enacted-law table supports the retrospective date; the original enacted 1998 c.19 s.8 page was not retrieved."
    source_rows.append(row)
    if package_group == "audit_index":
        index_files.extend(selected)
    else:
        compact_files.extend(selected)

mo = json.loads((BASE / "order_scan_manifest.json").read_text())
mo_records = []
for r in mo["records"]:
    stem = r["id"]
    pdf = f"raw/orders/{stem}.pdf"
    txt = r["text"]
    mo_records.append(dict(instrument_id=stem, url=r["url"], retrieval_status=r["status"],
                           pages_screened=list(range(1, r["pages_inspected"] + 1)),
                           scope="First two PDF pages, or all pages if shorter; text/OCR keyword screen, not all-page visual inspection.",
                           files=[info(pdf, representation="original_audit_pdf"),
                                  info(txt, representation="screened_page_text_or_ocr")]))
oic = json.loads((BASE / "foi-followup/oic451-route/screen-manifest.json").read_text())
oic_records = []
for r in oic:
    n = r["order"]
    base = f"foi-followup/oic451-route/{n:04d}_1995"
    oic_records.append(dict(instrument_id=f"{n:04d}_1995", url=r["url"],
                            pages_screened=[1], total_pdf_pages=r.get("pages"),
                            scope="First PDF page embedded text keyword screen; no assertion of all-page review.",
                            keyword_hit=r.get("hit", False),
                            relevant_positive_source_id="R4H-019" if n == 1321 else None,
                            files=[info(base + ".pdf", representation="original_audit_pdf"),
                                   info(base + ".txt", representation="first_page_embedded_text")]))
audit_controls = [
    "order_scan_manifest.json", "early2001_order_scan.json", "restructuring_order_scan.json",
    "foi-followup/oic451-route/screen-manifest.json", "scan_early2001_orders.py",
    "scan_restructuring_orders.py", "search_ledger.md", "financial_retrievals.json",
    "evidence-original-retrievals.json",
]
audit_records = dict(
    schema_version="1.0", prepared_on=TODAY, path_base=str(BASE),
    purpose="Audit files are screening/search documentation, not additional accepted findings.",
    groups=[
        dict(group_id="ministerial_orders_2001_and_early2002", instrument_count=len(mo_records),
             pages_screened=mo["pages_screened"], ranges=mo["scope"], method=mo["method"],
             result=mo["finding"], instruments=mo_records),
        dict(group_id="oic_1270_to_1340_1995", instrument_count=len(oic_records), pages_screened=71,
             ranges=[dict(year=1995, first_order=1270, last_order=1340, count=71)],
             method="Screened first-page embedded text for freedom/privacy/451 terms. Visually checked the relevant OIC1321 approval stamp and operative text. No all-page manual audit.",
             result="OIC1321/1995 is accepted as R4H-019. Keyword hits1292 and1299 do not establish the target commencement.",
             instruments=oic_records),
    ],
    index_and_catalogue_files=index_files,
    audit_control_files=[info(p, representation="audit_control_or_search_ledger") for p in audit_controls],
    overlap_with_compact_evidence=["foi-followup/oic451-route/1321_1995.pdf", "foi-followup/oic451-route/1321_1995.txt"],
    packaging_note="Deduplicate overlaps if including both the compact evidence and full audit sets. Bulk audit PDFs are not required to verify the positive claims.",
)
dump(BASE / "evidence_audit_files.json", audit_records)

external = []
for sid, pages, purpose in [
    ("R4R-072", [7, 8, 10, 11], "1993 FOIPPA definitions, original professional Schedule3 and consequential amendment"),
    ("R4R-081", [1, 80], "Royal-Assent commencement explanation and1995 FOIPPA history"),
    ("R4R-086", [1], "Originally ordered 15 April 1997 date for RS1996 Supplement s.1(h)"),
    ("R4R-080", [1, 90, 266], "Report-only1977 proclamation corroboration and narrower retrieval target; root-owned")]:
    p = BASE.parent / "root" / "raw" / (sid + ".pdf")
    data = p.read_bytes()
    external.append(dict(source_id=sid, path=str(p.relative_to(BASE.parent)), absolute_path=str(p),
                         bytes=len(data), sha256=sha(data), required_original_pdf_pages=pages,
                         purpose=purpose, owner="root", included_in_health_compact_file_count=False))

control_files = [info(p, representation="research_handback") for p in [
    "report.md", "sources.json", "claims.json", "coverage.json", "records_request_targets.md",
    "unresolved_transaction_targets.json", "hid-verification.json", "hid-verification.md",
    "root-report-review.md",
]]
audit_unique = {f["path"]: f for g in audit_records["groups"] for r in g["instruments"] for f in r["files"]}
for f in index_files + audit_records["audit_control_files"]:
    audit_unique[f["path"]] = f
counts = dict(
    source_catalogue_records=len(source_rows),
    source_classification_counts=dict(Counter(x["classification"] for x in source_rows)),
    claim_records=len(claims), claim_type_counts=dict(Counter(c["claim_type"] for c in claims)),
    complete_originals_preserved=19, full_source_not_retrieved=1,
    compact_evidence_source_records=sum(1 for s in source_rows if s["package_group"] == "compact_claim_or_lead_evidence"),
    compact_evidence_files=len(compact_files), compact_evidence_bytes=sum(f["bytes"] for f in compact_files),
    whole_page_extracts=len(specs), extracted_pdf_pages=sum(len(x[1]) for x in specs.values()),
    ministerial_order_audit_instruments=len(mo_records), oic_audit_instruments=len(oic_records),
    audit_unique_files=len(audit_unique), audit_bytes=sum(f["bytes"] for f in audit_unique.values()),
    handback_control_files=len(control_files),
)
manifest = dict(
    schema_version="1.0", prepared_on=TODAY, module="health_round4", path_base=str(BASE),
    counting_rule="20 catalogue records are not20 accepted findings. Nine records are positive/corroborating sources; five are archival leads or guards; five are indexes/search records; one full source was not retrieved. The10 claim records include an archive target, attributed historical observations, corroboration and negative/identity guards. Count by claim type, not by file or source total.",
    counts=counts,
    classification_definitions={
        "used_positive_or_corroboration": "Supports a dated factual statement or corroborates a reported event; not necessarily a new conclusion.",
        "archival_lead_or_guard": "Locates a record series/holding/access route or prevents identity/chronology conflation; no invented missing transaction.",
        "screened_or_index": "Catalogue or bounded search documentation; not positive proof of a missing event.",
        "not_retrieved": "Full source absent; indexed lead not promoted into an accepted factual claim.",
    },
    extraction_policy="Selected PDF pages are copied losslessly as whole pages into separate derived PDFs; originals are untouched. Each page map records the original1-based PDF page, printed label, text hash and72dpiRGB render hash, and equality checks against the source. Complete small originals are retained for the single-page orders/supplement, full10-page Act, small audited statements and HTML sources. The research-article selection is only its relevant affiliation page.",
    sources=source_rows,
    compact_claim_evidence_files=compact_files,
    handback_control_files=control_files,
    audit_file_list=info("evidence_audit_files.json", representation="separate_audit_inventory"),
    audit_inventory_summary=dict(instruments=513, ministerial_orders=442, oic_orders=71,
                                 screened_pages=577, uninspected_later_pages_not_implied_reviewed=True,
                                 audit_unique_files=len(audit_unique), audit_bytes=sum(f["bytes"] for f in audit_unique.values())),
    external_root_dependencies=external,
    hid_dependency_note="The HID verification appendix references root-owned originals. Those originals are packaged by root; the appendix does not allocate duplicate R4H sources or duplicate A8 claims.",
    verification=dict(all_original_files_exist=True, source_id_count_matches_catalogue=True,
                      extracts_render_and_text_match=True, original_hashes_unchanged=True,
                      failed_retrieval_not_in_compact_evidence=True),
)
dump(BASE / "evidence_manifest.json", manifest)

# Refresh the comprehensive integrity index after adding derived files/metadata.
full = []
for p in sorted(BASE.rglob("*")):
    if p.is_file() and p.name != "sha256_manifest.json" and "__pycache__" not in p.parts:
        data = p.read_bytes()
        full.append(dict(path=str(p.relative_to(BASE)), bytes=len(data), sha256=sha(data)))
dump(BASE / "sha256_manifest.json", dict(prepared_on=TODAY, files=full))
print(json.dumps(dict(counts=counts, integrity_manifest_files=len(full)), indent=2))
