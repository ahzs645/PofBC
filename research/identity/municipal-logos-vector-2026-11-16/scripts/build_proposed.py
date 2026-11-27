"""Write proposed-assets.json from the extracted SVGs and the facts recorded below.

    python3 -I build_proposed.py

sha256, bytes and viewBox are read from the SVG files themselves.
"""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[2]
SEARCH = PKG.name
OBSERVED = "2026-11-16"
PDF_FIDELITY = ("Every shape is a path the PDF itself draws, kept in the PDF’s own colours (as MuPDF converts them to RGB) "
                "and the PDF’s own geometry. Only the logo’s paths are kept. No tracing, redrawing or recolouring.")

A = [
    dict(target="source-municipal-abbotsford-website-logo", body="municipality-abbotsford", id="municipal-abbotsford-annual-report-2025",
         label="Abbotsford — Logo, 2025 Annual Report", file="abbotsford/annual-report-2025-logo.svg", publisher="City of Abbotsford",
         sourcePage="https://www.abbotsford.ca",
         sourceUrl="https://www.abbotsford.ca/sites/default/files/2026-06/2025%20Annual%20Report_FINAL%20for%20WEB.pdf",
         locator="PDF page 140 (back cover)", sourceDate="2025 Annual Report; PDF created 2 June 2026",
         notes="The same design and colours as the website logo, drawn as vector paths on the report’s back cover."),
    dict(target="source-municipal-burns-lake-website-logo", body="municipality-burns-lake", id="municipal-burns-lake-housing-needs-report-2024",
         label="Burns Lake — Logo, 2024 Interim Housing Needs Report", file="burns-lake/housing-needs-report-2024-logo.svg",
         publisher="The Corporation of the Village of Burns Lake", sourcePage="https://www.burnslake.ca",
         sourceUrl="https://www.burnslake.ca/media/file/burns-lake-housing-needs-report-v4-dec-6th-2024-final",
         locator="PDF page 1 (cover)", sourceDate="2024 Interim Housing Needs Report, draft version 3.0, 6 December 2024",
         notes="The same design and colours as the website logo, drawn as vector paths on the report’s cover."),
    dict(target="source-municipal-chilliwack-website-logo", body="municipality-chilliwack", id="municipal-chilliwack-climate-action-plan-2022",
         label="Chilliwack — Logo, horizontal, Corporate Climate Action Plan 2022", file="chilliwack/climate-action-plan-2022-logo.svg",
         publisher="City of Chilliwack", sourcePage="https://www.chilliwack.com",
         sourceUrl="https://www.chilliwack.com/main/attachments/Files/2024/City%20of%20Chilliwack%20Corporate%20Climate%20Action%20Plan_FINAL.pdf",
         locator="PDF page 1 (cover)", sourceDate="Corporate Climate Action Plan, 16 August 2022",
         notes="The horizontal lockup the website uses. In this printing “City of” is dark green rather than the website’s light green, and the snowcaps are open (no white fill), so the cover shows through them."),
    dict(target="source-municipal-chilliwack-website-logo", body="municipality-chilliwack", id="municipal-chilliwack-climate-actions-summary-stacked",
         label="Chilliwack — Logo, stacked, City Climate Actions summary", file="chilliwack/climate-actions-summary-logo-stacked.svg",
         publisher="City of Chilliwack", sourcePage="https://www.chilliwack.com",
         sourceUrl="https://www.chilliwack.com/main/attachments/Files/2876/City%20Climate%20Actions%20%2D%20Summary%2Epdf",
         locator="PDF page 1", sourceDate="City Climate Actions summary; PDF created 28 March 2022",
         notes="The stacked lockup, with the white ground under the mountains and the light-green “City of” the website logo shows. The website uses the horizontal lockup.",
         variantOf="municipal-chilliwack-climate-action-plan-2022"),
    dict(target="source-municipal-coquitlam-website-logo", body="municipality-coquitlam", id="municipal-coquitlam-treasury-report-2025-white",
         label="Coquitlam — Logo, white, 2025 Treasury Report", file="coquitlam/treasury-report-2025-logo-white.svg", publisher="City of Coquitlam",
         sourcePage="https://www.coquitlam.ca", sourceUrl="https://coquitlam.ca/DocumentCenter/View/19383/2025_Treasury_Report",
         locator="PDF page 1 (cover)", sourceDate="2025 Treasury Report (year ended 31 December 2025)",
         notes="The white version, as on the website’s dark masthead, drawn as vector paths on the report’s cover. The website file adds a drop shadow; this does not.",
         dark=True),
    dict(target="source-municipal-coquitlam-website-logo", body="municipality-coquitlam", id="municipal-coquitlam-treasury-report-2025",
         label="Coquitlam — Logo, blue, 2025 Treasury Report", file="coquitlam/treasury-report-2025-logo.svg", publisher="City of Coquitlam",
         sourcePage="https://www.coquitlam.ca", sourceUrl="https://coquitlam.ca/DocumentCenter/View/19383/2025_Treasury_Report",
         locator="PDF page 12 (back page)", sourceDate="2025 Treasury Report (year ended 31 December 2025)",
         notes="The blue version, from the same report’s back page.", variantOf="municipal-coquitlam-treasury-report-2025-white"),
    dict(target="source-municipal-dawson-creek-website-logo", body="municipality-dawson-creek", id="municipal-dawson-creek-community-profile-2024",
         label="Dawson Creek — Logo, 2024 Community Profile", file="dawson-creek/community-profile-2024-logo.svg",
         publisher="The Corporation of the City of Dawson Creek", sourcePage="https://www.dawsoncreek.ca",
         sourceUrl="https://www.dawsoncreek.ca/media/nr4fvuix/community-profile-2024.pdf",
         locator="PDF page 40 (back cover)", sourceDate="Community Profile & Investment Guide 2024; PDF created 17 May 2024",
         notes="The same design and colours as the website logo. This drawing differs slightly at the foot of the building, where white steps cut into the blue; its white parts are kept as drawn."),
    dict(target="source-municipal-fort-st-john-website-logo", body="municipality-fort-st-john", id="municipal-fort-st-john-ocp-2025-stacked",
         label="Fort St. John — Logo, stacked, Official Community Plan 2025", file="fort-st-john/ocp-2025-logo-stacked.svg",
         publisher="City of Fort St John", sourcePage="https://www.fortstjohn.ca/ocp",
         sourceUrl="https://www.fortstjohn.ca/media/file/official-community-plan-bylaw",
         locator="PDF page 1 (cover)", sourceDate="Official Community Plan bylaw; PDF created 17 December 2025",
         specimenDate="2025",
         notes="The stacked colour signature places the arc symbol above the name and tagline. It shares the city identity shown in the horizontal website logo and in the black signature in the 2012 travel guide.",
         extraction={"pdfPage": 1, "pdfBounds": [476, 668, 587, 744],
                     "method": "Isolated the logo’s native PDF paths with PyMuPDF."}),
    dict(target="source-municipal-kamloops-website-logo", body="municipality-kamloops", id="municipal-kamloops-annual-report-2025",
         label="Kamloops — Logo, 2025 Annual Report", file="kamloops/annual-report-2025-logo.svg", publisher="City of Kamloops",
         sourcePage="https://www.kamloops.ca/city-hall/governance-finance/annual-reports",
         sourceUrl="https://www.kamloops.ca/sites/default/files/CityofKamloops_AnnualReport2025_11x8-5_May2026_FINAL-WEB.pdf",
         locator="PDF page 142 (back cover)", sourceDate="Annual Report 2025; PDF created 3 June 2026",
         notes="The same logo as the website, with “Canada’s Tournament Capital” in white for a dark ground, as on the website.",
         fidelity=("Replayed from the logo’s own marked-content block in the page’s content stream: every path and clip is the PDF’s own, "
                   "and each of the 26 colour ramps is the PDF’s own axial shading written as an SVG linear gradient with the shading’s own axis "
                   "and its 64 sampled colours as stops. CMYK converted to RGB by MuPDF. No tracing, redrawing or recolouring."),
         dark=True, script="kamloops_shading.py"),
    dict(target="source-municipal-mackenzie-website-logo", body="municipality-mackenzie", id="municipal-mackenzie-brand-book-2018",
         label="Mackenzie — Logo, Brand Book 2018", file="mackenzie/brand-book-2018-logo.svg", publisher="District of Mackenzie",
         sourcePage="https://districtofmackenzie.ca/business-development/branding/",
         sourceUrl="https://districtofmackenzie.ca/wp-content/uploads/2019/02/Brand-Book-V2.pdf",
         locator="PDF page 2", sourceDate="Brand Book, version 2, November 2018",
         notes="The primary logo from the District’s published brand book; the same design and colours as the website logo."),
    dict(target="source-municipal-nanaimo-website-logo", body="municipality-nanaimo", id="municipal-nanaimo-annual-report-2025",
         label="Nanaimo — Logo, 2025 Annual Report", file="nanaimo/annual-report-2025-logo.svg", publisher="City of Nanaimo",
         sourcePage="https://www.nanaimo.ca/your-government/budget-finance/annual-financial-reports",
         sourceUrl="https://www.nanaimo.ca/docs/your-government/budget-and-finance/2025-annual-report-web.pdf",
         locator="PDF page 1 (cover)", sourceDate="2025 Annual Report; PDF created 23 June 2026",
         notes="The same design as the website logo. The print colours are brighter process blues than the website file’s, and the waves carry thin black keylines, as printed."),
    dict(target="source-municipal-prince-rupert-website-logo", body="municipality-prince-rupert", id="municipal-prince-rupert-community-assessment-2024",
         label="Prince Rupert — Logo, Complete Community Assessment 2024", file="prince-rupert/community-assessment-2024-logo.svg",
         publisher="City of Prince Rupert", sourcePage="https://www.princerupert.ca",
         sourceUrl="https://princerupert.ca/sites/7/files/2024-12/PR%20Complete%20Community%20Assessment%20%26%20Plan.pdf",
         locator="PDF page 1 (cover)", sourceDate="Complete Community Assessment & Plan; PDF created 25 October 2024",
         notes="The city adopted the red arch above “The City of Prince Rupert” in 2022. Its standalone website wordmark has a separate gallery entry."),
    dict(target="source-municipal-quesnel-website-logo", body="municipality-quesnel", id="municipal-quesnel-brand-guidelines-2016",
         label="Quesnel — Logo, Brand Guidelines 2016", file="quesnel/brand-guidelines-2017-logo.svg", publisher="City of Quesnel",
         sourcePage="https://www.quesnel.ca", sourceUrl="https://www.quesnel.ca/media/file/city-quesnel-guidelines-v3-size-edits",
         locator="PDF page 7", sourceDate="Brand Guidelines, version 02, 13 December 2016; PDF created 17 January 2017",
         notes="The “City of Quesnel” lockup from the City’s brand guidelines. The website file is the same design but its wordmark and wave are drawn taller relative to “City of”."),
    dict(target="source-municipal-quesnel-website-logo-compact", body="municipality-quesnel", id="municipal-quesnel-brand-guidelines-2016-compact",
         label="Quesnel — Logo, compact, Brand Guidelines 2016", file="quesnel/brand-guidelines-2017-logo-compact.svg", publisher="City of Quesnel",
         sourcePage="https://www.quesnel.ca", sourceUrl="https://www.quesnel.ca/media/file/city-quesnel-guidelines-v3-size-edits",
         locator="PDF page 7", sourceDate="Brand Guidelines, version 02, 13 December 2016; PDF created 17 January 2017",
         notes="The “Quesnel” lockup without “City of”, from the same page of the brand guidelines.",
         variantOf="municipal-quesnel-brand-guidelines-2016"),
    dict(target="source-municipal-richmond-website-logo", body="municipality-richmond", id="municipal-richmond-strategic-plan-highlights",
         label="Richmond — Logo, Council Strategic Plan term highlights", file="richmond/strategic-plan-highlights-logo.svg", publisher="City of Richmond",
         sourcePage="https://www.richmond.ca", sourceUrl="https://www.richmond.ca/__shared/assets/overview2022-2026stratplan79453.pdf",
         locator="PDF page 1", sourceDate="Council Strategic Plan 2022–2026, Term Highlights at a Glance; PDF created 6 July 2026",
         notes="The heron logo; the same design and colours as the website logo."),
    dict(target="source-municipal-smithers-website-logo", body="municipality-smithers", id="municipal-smithers-new-residents-guide-2026",
         label="Smithers — Logo, New Resident Guide 2026", file="smithers/new-residents-guide-2026-logo.svg", publisher="Town of Smithers",
         sourcePage="https://www.smithers.ca", sourceUrl="https://www.smithers.ca/sites/default/files/2026-03/TownofSmithers_New%20Residents%20Guide_2026_Web.pdf",
         locator="PDF page 2", sourceDate="New Resident Guide 2026; PDF created 4 March 2026",
         notes="The stacked logo with the name in slate, without the tagline. The website file is the same stacked logo with a white name and “A Town For All Seasons”."),
    dict(target="source-municipal-smithers-website-logo", body="municipality-smithers", id="municipal-smithers-new-residents-guide-2026-tagline-white",
         label="Smithers — Logo with tagline, white, New Resident Guide 2026", file="smithers/new-residents-guide-2026-logo-tagline-white.svg",
         publisher="Town of Smithers", sourcePage="https://www.smithers.ca",
         sourceUrl="https://www.smithers.ca/sites/default/files/2026-03/TownofSmithers_New%20Residents%20Guide_2026_Web.pdf",
         locator="PDF page 1 (cover)", sourceDate="New Resident Guide 2026; PDF created 4 March 2026",
         notes="The horizontal lockup with a white name and the tagline “A Town For All Seasons”, for a dark ground.",
         dark=True, variantOf="municipal-smithers-new-residents-guide-2026"),
    dict(target="source-municipal-victoria-website-logo", body="municipality-victoria", id="municipal-victoria-property-tax-sheet-2025",
         label="Victoria — Logo, 2025 property tax information sheet", file="victoria/property-tax-sheet-2025-logo.svg",
         publisher="The Corporation of the City of Victoria", sourcePage="https://www.victoria.ca",
         sourceUrl="https://www.victoria.ca/media/file/2025-property-tax-info-sheet",
         locator="PDF page 4", sourceDate="2025 property tax information sheet; PDF created 29 April 2025",
         notes="The same design as the website logo. In this printing the blue is slightly lighter and the lettering pure black."),
]

records = []
for a in A:
    path = ROOT / "public/identity-municipal" / a["file"]
    data = path.read_bytes()
    vb = re.search(rb'viewBox="([^"]+)"', data).group(1).decode()
    assert b"<image" not in data and b"<text" not in data
    asset = {
        "id": a["id"], "label": a["label"], "file": "identity-municipal/" + a["file"], "format": "svg", "isVector": True,
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        "sourcePage": a["sourcePage"], "sourceUrl": a["sourceUrl"], "resolvedSourceUrl": a["sourceUrl"],
        "dimensions": {"viewBox": vb}, "contentType": "image/svg+xml",
        "supplied": False, "reconstruction": False, "publisher": a["publisher"],
        "sourceLocator": a["locator"], "sourceFile": None, "sourceDate": a["sourceDate"],
        "dateNote": "Publication date, not an adoption date.", "observedDate": OBSERVED,
        "evidenceType": "native-pdf-vector-extraction", "notes": a["notes"],
        "fidelityNote": a.get("fidelity", PDF_FIDELITY), "darkBackground": a.get("dark", False),
    }
    if a.get("variantOf"):
        asset["variantOf"] = a["variantOf"]
    if a.get("specimenDate"):
        asset["specimenDate"] = a["specimenDate"]
    if a.get("extraction"):
        asset["extraction"] = a["extraction"]
    asset["search"] = SEARCH
    records.append({"targetAssetId": a["target"], "dataFile": "municipalIdentityData.js", "bodyId": a["body"], "asset": asset})

(PKG / "proposed-assets.json").write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n")
print(len(records), "records")
