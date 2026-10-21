"""Append the narrow G2 FOIPPA verification without rebuilding earlier research."""
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).parent


def save(name, data):
    (BASE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def source(sid, title, doc, paths, pinpoint, newness, source_type="original_enacted_statute", **extra):
    item = dict(id=sid, title=title, url=doc, source_type=source_type,
                retrieved_on="2026-10-21", local_files=paths, pinpoint=pinpoint,
                newness=newness, retrieval_status="retrieved", **extra)
    item["sha256"] = hashlib.sha256((BASE / paths[0]).read_bytes()).hexdigest()
    return item


new_sources = [
    source("R4H-015", "Miscellaneous Statutes Amendment Act (No. 3), 1995, SBC 1995 c.53",
           "https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/71594662",
           ["foi-followup/misc1995c53.pdf", "foi-followup/misc1995c53.txt",
            "foi-followup/misc1995c53-p1.png", "foi-followup/misc1995c53-p4.png",
            "foi-followup/misc1995c53-p22.png"],
           "PDF pp.1,4,22 / printed pp.925,928,946; assent, s.14 and s.55",
           "New exact legislative date: s.14 adds regional health boards and community health councils to FOIPPA health care bodies; not delayed by s.55.",
           web_refs=["turn863view0", "turn863search1"], visually_verified=True),
    source("R4H-016", "Freedom of Information and Protection of Privacy Act, RSBC 1996 c.165, original Supplement",
           "https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1337117255",
           ["foi-followup/foippa1996supp.pdf", "foi-followup/foippa1996supp.txt",
            "foi-followup/foippa1996supp-p1.png"],
           "PDF p.1, s.1(h)",
           "Identity guard: Supplement s.1(h) changes Medical Appeal Board to Hospital Appeal Board in Schedule 2; unrelated to the regional-board/council classes in Schedule 1.",
           web_refs=["turn868view2"], visually_verified=True),
    source("R4H-017", "Health Authorities Act, SBC 1993 c.47, original enactment",
           "https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/206203074",
           ["foi-followup/haa1993.pdf", "foi-followup/haa1993.txt"],
           "Entire ten-page Act; PDF p.10 / printed p.426, ss.18–19",
           "Closes one incorrect statutory route: its sole consequential amendment is to the Property Transfer Tax Act, not FOIPPA.",
           web_refs=["turn854view0"]),
    source("R4H-018", "Freedom of Information and Protection of Privacy Act, RSBC 1996 c.165, original revision",
           "https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/794520916",
           ["foi-followup/foippa1996original.pdf", "foi-followup/foippa1996original.txt"],
           "PDF/printed p.37, Schedule 1 health care body; PDF p.55 / historical-table p.ii",
           "Corroborates the regional-board and council definitions and the historical citation 1995-53-14; the 1996 revision is not their original inclusion date."),
    source("R4H-019", "Order in Council 1321/1995: FOIPPA Amendment Act 1993 ss.30 and 32 commencement",
           "https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1321_1995",
           ["foi-followup/oic451-route/1321_1995.pdf", "foi-followup/oic451-route/1321_1995.txt",
            "foi-followup/oic1321-date.png"],
           "Single-page order, approval stamp and operative clause",
           "New original instrument supporting root R4RC-112; approval 2 November 1995, expressly effective 6 November 1995. It enacts professional Schedule 3 through s.30, alongside the Legal Profession Act amendment in s.32.",
           source_type="original_order_in_council", made_date="1995-11-02",
           effective_date="1995-11-06", visually_verified=True,
           web_retrieval_note="Search-service open failed; direct public urllib retrieval succeeded. The complete original and date crop are held locally."),
    source("R4H-020", "Table of Legislative Changes — 31 December 1998",
           "https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/638385389",
           ["foi-followup/table1998.pdf", "foi-followup/table1998.txt", "foi-followup/table1998-p32.png"],
           "PDF p.32 / printed p.27, FOIPPA Schedule 2, Supplement s.1(h)",
           "Official compilation proves the 21 April 1997 retrospective date superseding BC Reg 135/97, with citation 1998-19-8(2). It applies to the Hospital Appeal Board name, not regional health classes.",
           source_type="official_legislative_history_table", visually_verified=True,
           web_retrieval_note="Search-service open failed; direct public urllib retrieval succeeded.")
]

new_claims = [
    dict(id="R4HC-007", work_item=["G2"],
         claim="Regional health boards designated under Health Authorities Act s.4(1) and community health councils designated under s.6(1) were added as FOIPPA health care bodies on 13 July 1995 by SBC 1995 c.53 s.14.",
         source_ids=["R4H-015", "R4H-018", "R4R-081"],
         pinpoint="R4H-015 PDF pp.1,4,22 (assent, s.14, s.55); R4R-081 PDF pp.1,80 / printed pp.1165,1244; R4H-018 PDF pp.37,55",
         new_in_round4=True, claim_type="statutory_scrutiny_class_start", confidence="high",
         made_date="1995-07-13", effective_date="1995-07-13", date_precision="day",
         date_basis="Royal Assent: s.14 is excluded from s.55 deferred provisions; the 1995 official table records 1995 c.53 without another effective date, and its introduction explains that unqualified entries commenced on Royal Assent.",
         relationship_type="subject_to_foippa", atlas_import=True,
         covered_classes=["regional health board designated under Health Authorities Act s.4(1)",
                          "community health council designated under Health Authorities Act s.6(1)"],
         import_rule="A body's class-based coverage begins no earlier than both 13 July 1995 and its own legal designation. Keep this scrutiny edge separate from ministry accountability, ownership, service delivery and incorporation. Do not apply it to the distinct community health services societies without their separate coverage authority.",
         guard="The 3 November 1994 hospital/regional-hospital-district class commencement does not establish the start for these two additional classes. Neither date is an individual body's creation date."),
    dict(id="R4HC-008", work_item=["G2"],
         claim="FOIPPA RS1996 Supplement s.1(h) changes the Schedule 2 name Medical Appeal Board (Hospital Act) to Hospital Appeal Board (Hospital Act); its initially ordered 15 April 1997 date was superseded by a retrospective 21 April 1997 commencement under SBC 1998 c.19 s.8(2), as recorded in the official 1998 legislative table.",
         source_ids=["R4H-016", "R4H-020", "R4R-086"],
         pinpoint="R4H-016 p.1 s.1(h); R4R-086 p.1; R4H-020 PDF p.32 / printed p.27",
         new_in_round4=True, claim_type="identity_and_commencement_guard", confidence="high",
         made_date=None, originally_ordered_effective_date="1997-04-15",
         effective_date="1997-04-21", correction_assent_date="1998-06-30", date_precision="day",
         date_basis="Original OIC414/1997 and original Supplement identify the provision; official 1998 table records BC Reg135/97 superseded by 1998-19-8(2), retroactive from 30 June 1998.",
         atlas_import="guard_and_schedule_name_history_only",
         import_rule="Do not use either April 1997 date for regional health board or community health council FOIPPA inclusion. Do not infer the tribunal's legal creation or general rename date from this FOIPPA Schedule 2 amendment alone.",
         limitation="The catalogue's retrieved SBC1998c19 PDF contains only its first page, not s.8. The retrospective date here is supported by the official enacted-law compilation, not a claim that the complete original s.8 page was retrieved."),
    dict(id="R4HC-009", work_item=["G2"],
         claim="OIC1321/1995, approved 2 November 1995, expressly brings FOIPPA Amendment Act1993 c.46 ss.30 and32 into force on 6 November 1995. Section30 adds Schedule3 governing bodies of professions or occupations; section32 makes the Legal Profession Act consequential amendment.",
         source_ids=["R4H-019", "R4R-072", "R4R-081"],
         pinpoint="R4H-019 p.1; R4R-072 PDF pp.10–11 / printed pp.414–415; R4R-081 PDF p.80 / printed p.1244",
         new_in_round4=True, claim_type="primary_instrument_corroboration", confidence="high",
         made_date="1995-11-02", effective_date="1995-11-06", date_precision="day",
         atlas_import="strengthen_existing_root_claim_R4RC-112",
         import_rule="Use for the Schedule3 statutory commencement, with the list and any intervening amendments checked for each particular body. Do not treat this as an all-professions or all-health-bodies blanket date.",
         counting_policy="The date was already recorded by root from the official 1995 table. Count this as recovery of the original commencement instrument, not a second new class-date discovery."),
    dict(id="R4HC-010", work_item=["G2"],
         claim="The original Health Authorities Act1993 c.47 contains no FOIPPA consequential amendment; its only consequential amendment, s.18, concerns the Property Transfer Tax Act.",
         source_ids=["R4H-017"], pinpoint="Entire Act, especially PDF p.10 / printed p.426, s.18",
         new_in_round4=True, claim_type="bounded_statutory_route_exclusion", confidence="high",
         made_date=None, effective_date=None, atlas_import=False,
         import_rule="Research guard only. Use the separate 1995 c.53 s.14 amendment for regional-board and council FOIPPA inclusion.")
]

sources = [s for s in json.loads((BASE / "sources.json").read_text()) if s["id"] not in {s["id"] for s in new_sources}]
claims = [c for c in json.loads((BASE / "claims.json").read_text()) if c["id"] not in {c["id"] for c in new_claims}]
save("sources.json", sources + new_sources)
save("claims.json", claims + new_claims)
coverage = [c for c in json.loads((BASE / "coverage.json").read_text()) if c["work_item"] != "G2_health_and_professional_foippa"]
coverage.append(dict(
    work_item="G2_health_and_professional_foippa", status="regional_class_date_closed_and_two_guards",
    new_findings="Regional health boards and community health councils enter FOIPPA health care body definition on 13 July 1995; original OIC 1321/1995 corroborates professional Schedule 3 commencement on 6 November 1995; RS1996 Supplement s.1(h) is an unrelated Hospital Appeal Board name correction.",
    claim_ids=[c["id"] for c in new_claims], source_ids=[s["id"] for s in new_sources],
    root_source_dependencies=["R4R-072", "R4R-081", "R4R-086"],
    remaining="Individual-body coverage requires matching the class to its designation and any separate exceptions or Schedule2 listing. Full original 1998 correction Act s8 page not retrieved; official 1998 table provides the retrospective legal date.",
    negative_route="HAA1993c47 has no FOIPPA amendment; Supplement1h cannot date regional-board/council entry.",
    search_scope="Both web search engines; original1993/1995/1996 enactments; official1995/1998 tables; first-page text screen of 71 OIC PDFs numbered1270–1340/1995 to find original professional commencement."
))
save("coverage.json", coverage)

report_path = BASE / "report.md"
report = report_path.read_text()
report = report.replace(
    "The strongest new result is a specific archival route for the missing transfer paperwork:",
    "The final follow-up establishes a new exact scrutiny date: **regional health boards and community health councils entered FOIPPA’s health-care-body class on 13 July 1995**. It also recovers the original professional-body commencement order and resolves a misleading 1997 appeal-board-name lead (section 7). The health-transaction work identifies a specific archival route for the missing transfer paperwork:")
old_counts = "This module has six claim records: one archive-series finding and five PORT/Society historical or relationship observations. Three are directly useful dated relationship observations; one is an attributed program-origin year; one preserves the minister’s historical account without changing the Society’s legal registration date. The source register has 14 records, including catalogues and unsuccessful source leads; that is not a count of 14 substantive discoveries."
new_counts = "This module has **10 claim records and 20 source records**. The six earlier health-transaction/PORT records are supplemented by one new FOIPPA class-date finding, one recovered original commencement instrument corroborating a root finding, and two statutory identity/route guards. Catalogues, supplementary leads, negative findings and corroboration are labelled; 20 source records do not mean 20 substantive discoveries. The separate hospital-improvement-district verification appendix checks root-owned sources and does not add another set of duplicate sources or health claims."
report = report.replace(old_counts, new_counts)

section = """## 7. G2: regional health boards and councils entered FOIPPA on 13 July 1995

The decisive enactment is **Miscellaneous Statutes Amendment Act (No.3), 1995, SBC 1995 c.53, s.14**. It adds two paragraphs to the Schedule 1 definition of *health care body*: regional health boards designated under Health Authorities Act s.4(1), and community health councils designated under s.6(1). The original Act records assent on **13 July 1995**; s.55 defers a specific list of provisions but does not include s.14. [R4H-015, PDF pp.1,4,22 / printed pp.925,928,946](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/71594662).

The official **1995 Table of Statutes**, root source **R4R-081**, independently records the Schedule 1 amendment by 1995 c.53 without a deferred date; its introductory explanation says such entries commenced on Royal Assent. See PDF p.80 / printed p.1244 and PDF p.1 / printed p.1165. The original RS1996 FOIPPA text preserves both classes and its historical table cites **1995-53-14**. [R4H-018, PDF pp.37,55](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/794520916).

This is a **class coverage date**, not a creation date. For an individual board or council, the class-based relationship starts no earlier than both 13 July 1995 and that body’s legal designation. It must be kept distinct from the **3 November 1994 hospital/regional-hospital-district class commencement**, and from the bodies’ ministry accountability. The separate community health services societies need their own listing or coverage evidence; the new board/council paragraphs do not automatically include them.

### The 1997 dates belong to the Hospital Appeal Board name

The original FOIPPA **RS1996 Supplement s.1(h)** changes **Medical Appeal Board (Hospital Act)** to **Hospital Appeal Board (Hospital Act)** in **Schedule 2**. It does not add the regional-board or council classes. [R4H-016, p.1](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1337117255).

Root **R4R-086**, OIC414/1997, approved 3 April 1997, initially orders this Supplement provision effective **15 April 1997**. The official **1998 Table of Legislative Changes** records its legally corrected date as **21 April 1997**, identifying BC Reg135/97 as superseded by **1998-19-8(2)**, retrospectively from the Act’s assent on **30 June 1998**. [R4H-020, PDF p.32 / printed p.27](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/638385389). The critical table row was visually checked. The catalogue’s original 1998 c.19 PDF supplied only its first page, so this module does not claim to have recovered the original s.8 page. The official enacted-law table supports the corrected date. Neither April date can be used for regional health board/council inclusion or, by itself, the tribunal’s creation date.

The original **Health Authorities Act1993 c.47** also closes an incorrect route: its only consequential amendment is s.18 concerning the Property Transfer Tax Act. There is no FOIPPA amendment in that Act. [R4H-017, PDF p.10 / printed p.426](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/206203074).

### Original professional-body commencement recovered

**OIC1321/1995**, approved **2 November 1995**, expressly brings FOIPPA Amendment Act1993 c.46 **ss.30 and32** into force **6 November 1995**. Section30 adds Schedule3 governing bodies of professions or occupations; section32 makes the Legal Profession Act consequential amendment. [R4H-019, original order](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1321_1995); root **R4R-072**, PDF pp.10–11 / printed pp.414–415. The order’s stamp and operative clause were visually checked. Root had already established the date from its official 1995 table; this is a stronger original-instrument source for **R4RC-112**, not another independent class-date discovery.

The order was found by a bounded first-page text screen of **71 original order PDFs, 1270–1340/1995**. The screen ledger is `foi-followup/oic451-route/screen-manifest.json`; the full order is retained. Unrelated first-page keyword hits were not treated as relevant legal evidence. Supplement, Act and table pages, extracts, and visual-check images are in `foi-followup/`.

"""
if "## 7. G2:" not in report:
    report = report.replace("## Files\n", section + "## Files\n")
report = report.replace("`sources.json`: 14 source, catalogue and lead records", "`sources.json`: 20 source, catalogue and lead records")
report = report.replace("`claims.json`: six new records", "`claims.json`: ten records")
report = report.replace("`coverage.json`: ten work-item statuses", "`coverage.json`: eleven work-item statuses")
report = report.replace("- `raw/`: retrieved originals, extracts and evidence images.", "- `raw/` and `foi-followup/`: retrieved originals, extracts and evidence images.\n- `hid-verification.json` and `hid-verification.md`: independent checks of root-owned hospital-improvement-district evidence; no duplicate source/claim count.")
report_path.write_text(report)

ledger = BASE / "search_ledger.md"
text = ledger.read_text()
if "## Final G2 follow-up" not in text:
    text += """
## Final G2 follow-up

- Original Health Authorities Act1993c47 inspected; no FOIPPA consequential amendment. Its s18 amends Property Transfer Tax Act.
- Original RS1996 FOIPPA Supplement s1(h) retrieved and visually checked: it renames Medical Appeal Board to Hospital Appeal Board in Schedule2. It is unrelated to Schedule1 health-authority classes.
- Both search engines used to trace the original class amendment. Miscellaneous Statutes Amendment Act(No.3),1995 c53 s14 recovered. Assent13July1995; s55 excludes s14 from deferred provisions. Official1995table R4R081 corroborates assent commencement; originalRS1996historicaltable cites1995-53-14.
- Official1998TableLegislativeChanges retrieved, PDF32/printed27 visually checked: Supplement1h date21April1997 under1998c19s8(2), supersedingBCReg135/97. Catalogue original1998c19PDF contains onlyp1; originalenacteds8page not recovered. The official table supports the retrospective correction; bill text was not treated as proof of enactment.
- Direct public PDF retrieval succeeded where search-service open returned inaccessible. These are retrieval-route differences, not missing-source conclusions.
- Professional commencement: exact-number/regulation web queries did not identify the order. Four date-sampling covers were read (1300,1360,1400,1421/1995); a subsequent bounded first-page text screen covered orders1270–1340/1995 inclusive. OIC1321/1995 states ss30and32of1993c46 effective6November1995; approval2November1995 visually checked. Detailed71-order ledger in foi-followup/oic451-route/screen-manifest.json. Do not infer that every page of all71orders was manually reviewed.
"""
    ledger.write_text(text)

manifest = []
for p in sorted(BASE.rglob("*")):
    if p.is_file() and p.name != "sha256_manifest.json" and "__pycache__" not in p.parts:
        data = p.read_bytes()
        manifest.append(dict(path=str(p.relative_to(BASE)), bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
save("sha256_manifest.json", dict(prepared_on="2026-10-21", files=manifest))
print(json.dumps(dict(sources=len(sources)+len(new_sources), claims=len(claims)+len(new_claims),
                      coverage=len(coverage), manifest_files=len(manifest)), indent=2))
