"""Writes ../proposed-assets.json (sha256 and bytes read from the files in public/)."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
PKG = "health-bodies-vector-2026-11-16"
IHPDF = "https://www.interiorhealth.ca/sites/default/files/PDFS/"
recs = [
 dict(t="source-interior-health-interior-health-symbol-jpg", df="collectedData.js", b="interior-health", id="interior-health-symbol-2024-pdf",
      label="Interior Health — Symbol, 2024 strategic direction", file="identity-collected/interior-health/interior-health-symbol-2024-strategic-direction.svg",
      rec=False, pub="Interior Health", page=IHPDF + "strategic-priorities.pdf", url=IHPDF + "strategic-priorities.pdf", loc="PDF page 1, top centre",
      sf="Our Strategic Direction 2024-2027", sd="2024-01-24", dn="The document's date, not an adoption date.", ev="native-pdf-vector-extraction",
      notes="The figure, head and swoosh on their own, in the blue the PDF gives them.",
      fid="The PDF's own three paths and colour, extracted with PyMuPDF (research/identity/health-bodies-vector-2026-11-16/scripts/interior_health.py); no tracing or redrawing. The PDF's blue converts to #005ba2, brighter than the website JPG's #2f5088; IH's 2024 wayfinding guideline lists Pantone 653 C as both hex 005AA2 and RGB 47/79/136."),
 dict(t="source-interior-health-interior-health-stacked-jpg", df="collectedData.js", b="interior-health", id="interior-health-stacked-rebuilt",
      label="Interior Health — Stacked (vector reconstruction)", file="identity-collected/interior-health/interior-health-stacked-rebuilt.svg",
      rec=True, pub="Interior Health", page="https://www.interiorhealth.ca/about-ih/media-centre-and-alerts", url=IHPDF + "deciding-to-move-into-long-term-care.pdf",
      loc="Layout: the stacked JPG on the media centre page. Parts: the horizontal logo on PDF page 1 of Deciding to Move into Long-Term Care (IH #810281)",
      sf="Deciding to Move into Long-Term Care, access guide (IH #810281)", sd=None, dn="The JPG is undated; the parts' PDF was created 26 March 2024. Neither is an adoption date.",
      ev="vector-reconstruction", notes="The symbol over “Interior Health”, in IH Blue.",
      fid="A reconstruction of the stacked layout, not original stacked artwork: no stacked vector was found. The symbol (3 paths) and the wordmark (14 glyph outlines) are the long-term-care guide's own paths, each scaled uniformly and placed on the boxes they occupy in the official stacked JPG; their fitted heights agree with the JPG within 1%, and an aligned overlay matches closely. Filled #2f4f88, IH Blue as RGB 47/79/136 in IH's wayfinding guideline, which is also the JPG's colour."),
 dict(t="source-first-nations-health-authority-fnha-white-png", df="collectedData.js", b="first-nations-health-authority", id="fnha-white-stacked-2026-pdf",
      label="First Nations Health Authority — White, stacked and centred, 2026 brochure", file="identity-collected/first-nations-health-authority/fnha-white-stacked-2026-pdf.svg",
      rec=False, pub="First Nations Health Authority", page="https://fnha.ca/", url="https://fnha.ca/wp-content/uploads/FNHA-Indigenous-End-of-Life-Guide-Brochure.pdf",
      loc="PDF page 1, front panel, top", sf="Indigenous End-of-Life Guide (brochure, version August 2026)", sd="2026-08", dn="The brochure's version date, not an adoption date.",
      ev="native-pdf-vector-extraction", notes="The thunderbird-and-sun symbol over the centred name and “Health through wellness”, all in white, for a dark ground.",
      fid="The PDF's own 55 white fills and 2 hairline strokes, extracted with PyMuPDF (scripts/fnha.py); the two strokes have zero width in the PDF and are written at 0.35 pt, their width in another FNHA PDF. No tracing or recolouring.", dark=True),
 dict(t="source-first-nations-health-authority-fnha-horizontal-png", df="collectedData.js", b="first-nations-health-authority", id="fnha-horizontal-colour-rebuilt",
      label="First Nations Health Authority — Full colour, horizontal (vector reconstruction)", file="identity-collected/first-nations-health-authority/fnha-horizontal-colour-rebuilt.svg",
      rec=True, pub="First Nations Health Authority", page="https://fnha.ca/", url="https://fnha.ca/wp-content/uploads/FNHA-Caregiving-An-Important-Part-of-Community-Medicine-3.pdf",
      loc="Layout and lettering: white horizontal logo, PDF page 1 (foot). Symbol: stacked colour logo, PDF page 1 of https://fnha.ca/wp-content/uploads/migrated/Documents/FNHA-Daily-Movement-Guide.pdf",
      sf="Caregiving: An Important Part of Community Medicine; Connect to Change, Movement is Medicine (Daily Movement Guide)", sd=None, dn="Undated handout; the Daily Movement Guide PDF was created 25 May 2026. Not adoption dates.",
      ev="vector-reconstruction", notes="The full-colour symbol beside “First Nations Health Authority” and “Health through wellness” in navy.",
      fid="Assembled from original FNHA PDF parts, not a found full-colour horizontal file: the lettering is the white horizontal logo's own 48 glyph outlines, filled navy #091631 as in FNHA's colour logos; the symbol is the 30 full-colour paths of the stacked logo in the Daily Movement Guide, scaled uniformly onto the white logo's symbol box (the two boxes have the same proportions to 0.01%). Colours are the PDFs' own as converted by MuPDF."),
 dict(t="source-expanded-sub-bc-centre-for-disease-control-website-logo", df="expandedIdentityData.js", b="sub-bc-centre-for-disease-control", id="bccdc-2021-research-report",
      label="BC Centre for Disease Control — CDC symbol and name, 2020/2021 research report", file="identity-expanded/sub-bc-centre-for-disease-control/bccdc-2021-research-report.svg",
      rec=False, pub="BC Centre for Disease Control", page="https://www.bccdc.ca/about/accountability/annual-reports", url="https://www.bccdc.ca/Our-Research-Site/Documents/BCCDC%20Annual%20Research%20Report%202021.pdf",
      loc="PDF page 1 (cover), lower right", sf="BCCDC Annual Research Report 2020/2021", sd="2021", dn="The report's year, not an adoption date.",
      ev="native-pdf-vector-extraction", notes="The interlocking CDC letters over “BC Centre for Disease Control”, in blue.",
      fid="The PDF's own 2 symbol paths and 25 glyph outlines, extracted with PyMuPDF (scripts/bccdc.py); no tracing or recolouring. The cover adds an endorsement line, “Provincial Health Services Authority”, under the name; it is left out, as on the website logo. The PDF's blue converts to #0065a4, lighter than the website PNG."),
 dict(t="source-expanded-bc-emergency-health-services-website-logo", df="expandedIdentityData.js", b="bc-emergency-health-services", id="bcehs-2024-progress-report-endorsed",
      label="BC Emergency Health Services — Logo with PHSA line, 2023/24 progress report", file="identity-expanded/bc-emergency-health-services/bcehs-2024-progress-report-endorsed.svg",
      rec=False, pub="BC Emergency Health Services", page="https://www.bcehs.ca/about/accountability/reports", url="https://www.bcehs.ca/about-site/Documents/bcehs_progress_report_2023-24.pdf",
      loc="PDF page 1 (cover), top right", sf="BCEHS 2023/2024 Progress Report", sd="2023/24", dn="The report's year, not an adoption date.",
      ev="native-pdf-vector-extraction", notes="BCEHS in blue and red with the red rule and the name, over “Provincial Health Services Authority”. The endorsed version: its name is larger beside the letters than on the website logo.",
      fid="The PDF's own 65 paths and colours, extracted with PyMuPDF (scripts/bcehs.py); no tracing or recolouring. A related version of the website logo, not the same artwork: it carries the PHSA line and different proportions."),
 dict(t="source-expanded-bc-emergency-health-services-website-logo", df="expandedIdentityData.js", b="bc-emergency-health-services", id="bcehs-website-layout-rebuilt",
      label="BC Emergency Health Services — Logo (vector reconstruction)", file="identity-expanded/bc-emergency-health-services/bcehs-website-layout-rebuilt.svg",
      rec=True, pub="BC Emergency Health Services", page="https://www.bcehs.ca/", url="https://www.bcehs.ca/about-site/Documents/bcehs_progress_report_2023-24.pdf",
      loc="Layout: the website logo PNG. Parts: the logo on PDF page 1 of the 2023/24 progress report", sf="BCEHS 2023/2024 Progress Report", sd=None,
      dn="The website PNG is undated; the parts come from the 2023/24 report. Not adoption dates.", ev="vector-reconstruction",
      notes="BCEHS in blue and red, a red rule and “BC Emergency Health Services” on two lines, as on the website.",
      fid="A reconstruction of the website layout from original parts: the BCEHS letters (5 paths), the rule (2) and the name (25 glyph outlines) are the progress report's own paths, each scaled uniformly and placed on the box it occupies in the website PNG (fitted heights within 2% of the PNG). Colours are the PDF's own (#004b8d, #c42032); the website PNG's red is brighter."),
 dict(t="source-expanded-sub-bc-womens-hospital-website-logo", df="expandedIdentityData.js", b="sub-bc-womens-hospital", id="bc-womens-2024-foundation-impact-report",
      label="BC Women's Hospital + Health Centre — Logo, 2024 foundation impact report", file="identity-expanded/sub-bc-womens-hospital/bc-womens-2024-foundation-impact-report.svg",
      rec=False, pub="BC Women's Health Foundation (report); logo of BC Women's Hospital + Health Centre", page="https://bcwomensfoundation.org/wp-content/uploads/2024/08/BCWHF-Impact-Report-2024-Single-Pages.pdf",
      url="https://bcwomensfoundation.org/wp-content/uploads/2024/08/BCWHF-Impact-Report-2024-Single-Pages.pdf", loc="PDF page 4, top left",
      sf="BC Women's Health Foundation Impact Report 2024 (single pages)", sd="2024-08", dn="The report's date, not an adoption date.",
      ev="native-pdf-vector-extraction-with-converted-gradients", notes="The name in teal and grey beside the folded-ribbon W in grey and teal gradients.",
      fid="The lettering (30 glyph outlines) and the W's 11 clipping shapes are the PDF's own paths and colours (scripts/bc_womens.py). The PDF fills those shapes with about 800 thin strips, a gradient broken into bands, and paints the three folds with small (34 × 43 px) images that vary only from top to bottom; here each shape is filled with an SVG linear gradient through those strips' or image rows' own colours, at their own heights. No tracing."),
 dict(t="source-central-vancouver-island-health-region-central-vancouver-island-health-region-1999-grayscale-emblem-png", df="collectedData.js", b="central-vancouver-island-health-region",
      id="central-vancouver-island-health-region-1999-emblem-rebuilt", label="Mountain and wave emblem (vector reconstruction)",
      file="identity-collected/central-vancouver-island-health-region/central-vancouver-island-health-region-1999-emblem-rebuilt.svg",
      rec=True, pub="Central Vancouver Island Health Region; reproduced in The World Without Linen Bags", page="https://www.hcergo.org/wp-content/uploads/2018/04/The-world-without-linen-bags.pdf",
      url="https://www.hcergo.org/wp-content/uploads/2018/04/The-world-without-linen-bags.pdf", loc="PDF page 85 (1-based), the grayscale emblem on a page dated May 1, 1999",
      sf="The World Without Linen Bags (March 2002)", sd="1999-05-01", dn="The date on the source page, a sighting, not an adoption date.", ev="vector-reconstruction",
      notes="Four peaks, the front one lighter, standing in a wave with two streamers at each end, in greys.",
      fid="A hand-fitted reconstruction of the 232 × 112 px grayscale emblem, not original artwork. The four peaks are triangles with 45-degree sides (every apex and edge on the scan fits that slope), cut off along the wave's top edge; the wave is one path through hand-picked points, smoothed as Catmull-Rom curves. No bitmap tracing. The greys (#383838–#5b5b5b) are averages measured on a halftoned photocopy; the original colours are not known. The PDF's vector letterhead (page 58) has only a solid black outline of this emblem, so it could not supply the peaks."),
]
out = []
for r in recs:
    p = ROOT / "public" / r["file"]; data = p.read_bytes()
    out.append({"targetAssetId": r["t"], "dataFile": r["df"], "bodyId": r["b"], "asset": {
        "id": r["id"], "label": r["label"], "file": r["file"], "format": "svg", "isVector": True,
        "supplied": False, "reconstruction": r["rec"], "publisher": r["pub"], "sourcePage": r["page"], "sourceUrl": r["url"],
        "sourceLocator": r["loc"], "sourceFile": r["sf"], "sourceDate": r["sd"], "observedDate": "2026-11-16", "dateNote": r["dn"],
        "evidenceType": r["ev"], "notes": r["notes"], "fidelityNote": r["fid"],
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "darkBackground": r.get("dark", False), "search": PKG}})
(Path(__file__).resolve().parents[1] / "proposed-assets.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(len(out), "records")
