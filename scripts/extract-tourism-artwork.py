#!/usr/bin/env python3
"""Extract documented Tourism BC specimens without tracing or redrawing artwork.

Usage:
  python scripts/extract-tourism-artwork.py --order /path/m0068_2013.pdf \
    --standards /path/bcgraphicstandards.pdf --gazette-assets /path/downloaded-gifs

Requires PyMuPDF, Pillow, lxml and svgpathtools. The order is the 89-page Ministerial Order M068/2013.
The standards input is the 10-page December 2005 excerpt preserved at
https://skitops.com/membership/profile/pdf/bcgraphicstandards.pdf.

Raster specimens remain source crops. Vector specimens preserve the manual's
native SVG paths and transforms, discarding only elements outside the selected
specimen. Manual safety keylines and display backgrounds extend outside the
selected bounds and are deliberately excluded. No PDF path rewriting is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageStat
from lxml import etree
from svgpathtools import parse_path


REPO = Path(__file__).resolve().parents[1]
ASSET_DIR = REPO / "public/tourism/marks"
MANIFEST = REPO / "research/identity/tourism-asset-transfer-2013/artwork-manifest.json"

# Coordinates are PDF points (72 per inch), origin at top left. PDF page numbers
# are one-based. Bounds avoid adjacent labels. Where a source table rule meets
# the source graphic, that scan artifact is retained rather than painted out.
ORDER_CROPS = [
    ("bc-magazine-masthead-tagline", "British Columbia Magazine masthead with tagline", 70, [282, 176, 376, 212], "TMA620,822"),
    ("visitor-centre-icon", "Visitor Centre information symbol", 70, [313, 246, 347, 295], "TMA750,057"),
    ("visitor-centre-horizontal-colour", "Visitor Centre horizontal colour-design specimen, reproduced in monochrome", 70, [298, 344, 369, 389], "TMA750,052"),
    ("super-natural-oval-symbol", "Sun, Sea and Mountain Oval Design", 70, [278, 436, 380, 477], "TMA632,575"),
    ("superhost", "SuperHost figure and wordmark", 70, [298, 492, 356, 557], "TMA672,366"),
    ("super-natural-stacked-earlier", "Super, Natural British Columbia stacked non-oval specimen", 70, [309, 598, 357, 629], "TMA578,341"),
    ("super-natural-stacked-oval", "Super, Natural British Columbia stacked oval specimen", 70, [297, 639, 372, 677], "TMA793,324"),
    ("tourism-bc-corporate", "Tourism British Columbia corporate lockup", 71, [294, 196, 354.5, 263], "TMA588,974"),
    ("worldhost", "WorldHost wordmark and ring design", 71, [292, 272, 361, 309], "TMA789,655"),
    ("super-natural-hellobc-horizontal", "Super, Natural British Columbia with HelloBC.com, horizontal", 71, [281, 320, 375, 338], None),
    ("super-natural-hellobc-stacked", "Super, Natural British Columbia with HelloBC.com, stacked", 71, [308, 349, 354, 385], None),
    ("bermuda-superhost", "Bermuda SuperHost international adaptation", 72, [306, 468, 364, 537], "V65685BM"),
    ("bc-magazine-masthead", "British Columbia Magazine masthead official-mark specimen", 86, [296, 164, 369, 193], "920549"),
    ("canadas-west-marketplace", "Canada's West Marketplace Alberta & British Columbia", 86, [297, 211, 367, 236], "920547"),
    ("visitor-centre-horizontal-bw", "Visitor Centre horizontal black-and-white official-mark specimen", 86, [298.5, 255, 364.5, 298.5], "920552"),
    ("visitor-centre-stacked", "Visitor Centre stacked official-mark specimen", 86, [297, 353.5, 358, 408.5], "920555"),
    ("super-natural-landscape-symbol", "Sun, Mountains & Sea Design, without oval", 86, [303, 416, 360, 446], "920600"),
    ("super-natural-horizontal", "Super, Natural British Columbia horizontal official-mark specimen", 86, [294, 475.5, 373, 489], "920550"),
    ("super-natural-horizontal-short", "Super, Natural British Columbia horizontal-short official-mark specimen", 86, [301, 498.5, 365, 511], "920556"),
    ("approved-accommodation", "Tourism British Columbia Canada Approved Accommodation", 86, [292.5, 574, 357, 636], "920558"),
]

GAZETTE_IMAGES = {
    "bc-magazine-masthead-tagline": "BCMag",
    "visitor-centre-icon": "Idesign",
    "visitor-centre-horizontal-colour": "IvisitorH",
    "super-natural-oval-symbol": "SunMtnSeaO",
    "superhost": "SuperHost",
    "super-natural-stacked-earlier": "SuperNatS",
    "super-natural-stacked-oval": "SuperNatO",
    "tourism-bc-corporate": "TourismBC",
    "worldhost": "WorldHost",
    "super-natural-hellobc-horizontal": "SuperNatHelloH",
    "super-natural-hellobc-stacked": "SuperNatHelloS",
    "bermuda-superhost": "SuperHost_Bermuda",
    "bc-magazine-masthead": "Appendix7_1",
    "canadas-west-marketplace": "Appendix7_2",
    "visitor-centre-horizontal-bw": "Appendix7_3",
    "visitor-centre-stacked": "Appendix7_5",
    "super-natural-landscape-symbol": "Appendix7_6",
    "super-natural-horizontal": "Appendix7_7",
    "super-natural-horizontal-short": "Appendix7_8",
    "approved-accommodation": "Appendix7_10",
}

# Five actually illustrated treatments for each layout: the reverse colour
# specimen represents both spot and process filenames in the manual, so it is
# extracted once rather than counted as two different designs.
VECTOR_CROPS = [
    ("stacked-spot", "Stacked with Canada, spot colour", 5, 15, [58, 225, 178, 306], ["2.1_SNBC_Stack_CDN_5spot.eps"], False),
    ("stacked-process", "Stacked with Canada, process colour", 5, 15, [58, 365, 178, 448], ["2.2_SNBC_Stack_CDN_cmyk.eps"], False),
    ("stacked-grayscale", "Stacked with Canada, grayscale", 5, 15, [416, 225, 536, 306], ["2.3_SNBC_Stack_CDN_gs.eps"], False),
    ("stacked-reverse", "Stacked with Canada, reverse colour", 6, 16, [58, 146, 178, 228], ["2.4_SNBC_Stack_CDN_REV_5spot.eps", "2.5_SNBC_Stack_CDN_REV_cmyk.eps"], True),
    ("stacked-reverse-grayscale", "Stacked with Canada, reverse grayscale", 6, 16, [417, 146, 537, 228], ["2.6_SNBC_Stack_CDN_REV_gs.eps"], True),
    ("horizontal-a-spot", "Horizontal A with Canada, spot colour", 7, 17, [59, 220, 274, 270], ["2.1A_SNBC_Horiz_CDN_5spot.eps"], False),
    ("horizontal-a-process", "Horizontal A with Canada, process colour", 7, 17, [59, 323, 274, 373], ["2.2A_SNBC_Horiz_CDN_cmyk.eps"], False),
    ("horizontal-a-grayscale", "Horizontal A with Canada, grayscale", 7, 17, [59, 420, 274, 470], ["2.3A_SNBC_Horiz_CDN_gs.eps"], False),
    ("horizontal-a-reverse", "Horizontal A with Canada, reverse colour", 8, 18, [59, 144, 274, 193], ["2.4A_SNBC_Horiz_CDN_REV_5spot.eps", "2.5A_SNBC_Horiz_CDN_REV_cmyk.eps"], True),
    ("horizontal-a-reverse-grayscale", "Horizontal A with Canada, reverse grayscale", 8, 18, [59, 352, 274, 402], ["2.6A_SNBC_Horiz_CDN_REV_gs.eps"], True),
    ("horizontal-b-spot", "Horizontal B with Canada, spot colour", 9, 19, [59, 201, 354, 239], ["2.1B_SNBC_Horiz_CDN_5spot.eps"], False),
    ("horizontal-b-process", "Horizontal B with Canada, process colour", 9, 19, [59, 299, 354, 336], ["2.2B_SNBC_Horiz_CDN_cmyk.eps"], False),
    ("horizontal-b-grayscale", "Horizontal B with Canada, grayscale", 9, 19, [59, 395, 354, 433], ["2.3B_SNBC_Horiz_CDN_gs.eps"], False),
    ("horizontal-b-reverse", "Horizontal B with Canada, reverse colour", 10, 20, [59, 148, 354, 183], ["2.4B_SNBC_Horiz_CDN_REV_5spot.eps", "2.5B_SNBC_Horiz_CDN_REV_cmyk.eps"], True),
    ("horizontal-b-reverse-grayscale", "Horizontal B with Canada, reverse grayscale", 10, 20, [59, 356, 354, 392], ["2.6B_SNBC_Horiz_CDN_REV_gs.eps"], True),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pil_image(pix: fitz.Pixmap) -> Image.Image:
    return Image.frombytes("RGBA" if pix.alpha else "RGB", [pix.width, pix.height], pix.samples)


def svg_element_inside(element, definitions: dict, width: float, height: float) -> bool:
    """Measure an unchanged SVG element; retain only complete specimen paths."""
    tag = etree.QName(element).localname
    geometry = element
    if tag == "use":
        reference = element.get("{http://www.w3.org/1999/xlink}href", element.get("href", ""))
        geometry = definitions.get(reference.lstrip("#"))
        if geometry is None:
            return False
    data = geometry.get("d", "")
    if not data:
        return False
    path = parse_path(data)
    if not len(path):
        return False
    xmin, xmax, ymin, ymax = path.bbox()
    transform = element.get("transform", "")
    if transform:
        match = re.fullmatch(r"matrix\(([^)]+)\)", transform)
        if not match:
            raise ValueError(f"Unexpected source transform: {transform}")
        a, b, c, d, e, f = [float(v) for v in re.split(r"[ ,]+", match[1].strip())]
    else:
        a, b, c, d, e, f = 1, 0, 0, 1, 0, 0
    if any(parent.get("transform") for parent in element.iterancestors()):
        raise ValueError("Unexpected ancestor transform in source SVG")
    points = [(a * x + c * y + e, b * x + d * y + f) for x in (xmin, xmax) for y in (ymin, ymax)]
    return all(-0.05 <= x <= width + 0.05 and -0.05 <= y <= height + 0.05 for x, y in points)


def retain_specimen_svg(svg: str, width: float, height: float) -> str:
    root = etree.fromstring(svg.encode())
    namespaces = {"svg": "http://www.w3.org/2000/svg"}
    definitions = {node.get("id"): node for node in root.xpath(".//svg:defs//*[@id]", namespaces=namespaces)}
    candidates = root.xpath(".//svg:path[not(ancestor::svg:defs)] | .//svg:use[not(ancestor::svg:defs)]", namespaces=namespaces)
    for element in candidates:
        if not svg_element_inside(element, definitions, width, height):
            element.getparent().remove(element)
    # Keep original group clipping and transforms; remove empty groups and only
    # definitions no longer referenced by the retained specimen.
    for group in reversed(root.xpath(".//svg:g", namespaces=namespaces)):
        if len(group) == 0:
            group.getparent().remove(group)
    defs = root.find("{http://www.w3.org/2000/svg}defs")
    if defs is not None:
        ids_needed = set()
        def references(node):
            for child in node.iter():
                for key, value in child.attrib.items():
                    for reference in re.findall(r"url\(#([^)]+)\)", value):
                        yield reference
                    if key.endswith("href") and value.startswith("#"):
                        yield value[1:]
        for child in root:
            if child is not defs:
                ids_needed.update(references(child))
        queue = list(ids_needed)
        while queue:
            definition = definitions.get(queue.pop())
            if definition is not None:
                for reference in references(definition):
                    if reference not in ids_needed:
                        ids_needed.add(reference)
                        queue.append(reference)
        for definition in list(defs):
            if definition.get("id") not in ids_needed:
                defs.remove(definition)
        if len(defs) == 0:
            root.remove(defs)
    return etree.tostring(root, encoding="unicode") + "\n"


def extract_vector(source: fitz.Document, page_no: int, bounds: list[int], target: Path, reverse: bool) -> dict:
    page = source[page_no - 1]
    clip = fitz.Rect(bounds)
    original_box = page.cropbox
    page.set_cropbox(clip)
    svg = retain_specimen_svg(page.get_svg_image(text_as_path=True), clip.width, clip.height)
    page.set_cropbox(original_box)
    if "<image" in svg or "<text" in svg or not re.search(r"<path\b", svg):
        raise ValueError(f"Expected native outlined vector content: {target.name}")
    target.write_text(svg, encoding="utf-8")

    # Compare the retained shapes with the source specimen at the same scale.
    # Reverse artwork is composited over the manual's actual display backdrop.
    original = pil_image(source[page_no - 1].get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip))
    backdrop = max(original.getcolors(original.width * original.height), key=lambda item: item[0])[1]
    # Render the actual saved SVG over the source's comparison backdrop. This
    # detects missing glyphs and changes in native strokes or anisotropic scales.
    svg_doc = fitz.open(stream=svg.encode(), filetype="svg")
    comparison = fitz.open(stream=svg_doc.convert_to_pdf(), filetype="pdf")
    result_page = comparison[0]
    result_page.draw_rect(result_page.rect, color=None, fill=tuple(channel / 255 for channel in backdrop), overlay=False)
    retained = pil_image(result_page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False))
    diff = ImageChops.difference(original.convert("RGB"), retained.convert("RGB"))
    mean_difference = sum(ImageStat.Stat(diff).mean) / 3
    if original.size != retained.size or mean_difference > 2.0:
        raise ValueError(f"Unexpected change inside source specimen {target.name}: mean difference {mean_difference}")
    return {
        "width": round(clip.width, 3), "height": round(clip.height, 3),
        "dimensionUnit": "svg-user-unit",
        "nativePathCount": len(re.findall(r"<path\b", svg)),
        "containsRasterImage": False,
        "sourceComparison": {"renderScale": 3, "meanAbsoluteRgbDifference": round(mean_difference, 6)},
        "displayBackground": "dark" if reverse else "white",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", required=True, type=Path)
    parser.add_argument("--standards", required=True, type=Path)
    parser.add_argument("--gazette-assets", required=True, type=Path, help="Directory containing the 20 unmodified GIFs linked by the official Gazette page")
    args = parser.parse_args()
    order = fitz.open(args.order)
    standards = fitz.open(args.standards)
    if len(order) != 89 or len(standards) != 10:
        raise ValueError("Unexpected source edition or page count")
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    assets = []

    for slug, title, page_no, bounds, reference in ORDER_CROPS:
        filename = f"{slug}-order-2013.png"
        target = ASSET_DIR / filename
        pix = order[page_no - 1].get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72), clip=fitz.Rect(bounds), alpha=False)
        pix.save(target)
        assets.append({
            "id": f"{slug}-order-2013", "title": title,
            "path": f"public/tourism/marks/{filename}", "format": "png", "kind": "source-crop",
            "sourceId": "mo-68-2013", "sourcePage": page_no, "printedPage": page_no,
            "sourceBoundsPoints": bounds, "reference": reference,
            "sha256": sha256(target), "width": pix.width, "height": pix.height, "dimensionUnit": "pixel",
            "renderDpi": 200, "colourEvidence": "Monochrome scan; no original colours inferred.",
            "extractionNotes": "Bounded crop of the supplied source page; no tracing, redrawing, sharpening, or invented detail. A table-rule fragment is retained where it meets artwork in the original scan.",
            "displayBackground": "white",
        })

    for slug, title, page_no, _bounds, reference in ORDER_CROPS:
        source_filename = f"135_2013_{GAZETTE_IMAGES[slug]}.gif"
        source_file = args.gazette_assets / source_filename
        filename = f"{slug}-gazette-2013.gif"
        target = ASSET_DIR / filename
        shutil.copyfile(source_file, target)
        with Image.open(target) as image:
            width, height = image.size
        source_url = f"https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/{source_filename}"
        assets.append({
            "id": f"{slug}-gazette-2013", "title": title.replace(", reproduced in monochrome", ""),
            "path": f"public/tourism/marks/{filename}", "format": "gif", "kind": "source-image",
            "evidenceType": "original-published-image", "sourceId": "gazette-135-2013",
            "sourceImageUrl": source_url, "sourceImageSha256": sha256(source_file),
            "sourcePdfPage": page_no, "sourcePdfId": "mo-68-2013", "reference": reference,
            "sha256": sha256(target), "width": width, "height": height, "dimensionUnit": "pixel",
            "extractionNotes": "Unmodified image bytes linked by the official BC Gazette HTML. No conversion, resizing, sharpening, redrawing, or inferred colours. PDF page is a cross-reference to the corresponding transfer-schedule row.",
            "displayBackground": "white",
        })

    for slug, title, page_no, printed_page, bounds, filenames, reverse in VECTOR_CROPS:
        filename = f"super-natural-canada-{slug}-2005.svg"
        target = ASSET_DIR / filename
        details = extract_vector(standards, page_no, bounds, target, reverse)
        assets.append({
            "id": f"super-natural-canada-{slug}-2005", "title": f"Super, Natural British Columbia — {title}",
            "path": f"public/tourism/marks/{filename}", "format": "svg", "kind": "source-vector-extraction",
            "sourceId": "tourism-bc-standards-2005", "sourcePage": page_no, "printedPage": printed_page,
            "sourceBoundsPoints": bounds, "sourceArtworkFilenames": filenames,
            "sha256": sha256(target), **details,
            "extractionNotes": "Native vector paths from the manual, with outlined lettering. Surrounding explanatory text, safety keyline, and non-printing backdrop removed; artwork geometry preserved. SVG colours are the PDF renderer's display conversion, not a new RGB specification.",
        })

    manifest = {
        "schemaVersion": 1,
        "title": "Tourism BC source artwork from the 2013 asset-transfer order and December 2005 standards",
        "sources": [
            {"id": "mo-68-2013", "title": "Ministerial Order M068/2013: Transfer to Destination BC Corp. Regulation", "sourceFilename": args.order.name, "pageCount": 89, "sha256": sha256(args.order), "relatedWebUrl": "https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v56n05_135-2013", "sourceType": "User-supplied official PDF", "date": "2013-03-21"},
            {"id": "gazette-135-2013", "title": "BC Gazette Part II, Volume 56 Number 5, B.C. Reg. 135/2013", "url": "https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v56n05_135-2013", "sourceType": "Official Gazette HTML and linked original image files", "date": "2013", "notes": "The GIFs are preserved without byte changes. Source-image URLs were obtained from the official HTML img elements."},
            {"id": "tourism-bc-standards-2005", "title": "Tourism British Columbia Graphic Standards Manual, December 2005 (10-page excerpt)", "sourceFilename": args.standards.name, "pageCount": 10, "sha256": sha256(args.standards), "url": "https://skitops.com/membership/profile/pdf/bcgraphicstandards.pdf", "sourceType": "Tourism BC manual preserved by a third-party industry host", "date": "2005-12", "printedPagesPresent": ["cover", "1", "2", "3", "15", "16", "17", "18", "19", "20"]},
        ],
        "notes": [
            "The 2013 order documents listed assets and specimens; it does not establish each design's creation date.",
            "Canadian trademark rows and official-mark rows can describe the same design. Registration references are transcribed historical evidence, not a current legal-status check.",
            "The 2005 manual identifies Thesis Sans and specifies PMS Black, 130, 347, 349 and 285 for the illustrated colour variants.",
            "Original rights remain with the relevant owners; provenance in a transfer schedule does not establish an open reuse licence.",
        ],
        "assets": assets,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"assets": len(assets), "sourceCrops": len(ORDER_CROPS), "officialImages": len(GAZETTE_IMAGES), "nativeVectors": len(VECTOR_CROPS), "manifest": str(MANIFEST)}, indent=2))


if __name__ == "__main__":
    main()
