"""Recover TI Corp's published vector paths, without tracing or replacing lettering.

Requires PyMuPDF 1.26.6 for byte-reproducible PDF-to-SVG conversion. Run from any
directory; the source PDFs remain in the supplied scratch directory. --download
retrieves the two public official publications and verifies their fixed hashes.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET

import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BODY = "transportation-investment-corporation"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

SOURCES = [
    {
        "id": "ticorp-2025-colour-source-vector",
        "filename": "pbr-project2025.pdf",
        "url": "https://www.pattullobridgereplacement.ca/app/uploads/sites/637/2025/06/Summer-2025-Project-Update.pdf",
        "sha256": "08c8621c9f4e361bc930d71fbc762ee94ffb668e8770f31cda061062c8ee6d09",
        "page": 1,
        "indices": list(range(56)),
        "date": "Summer 2025",
        "label": "Full colour, Summer 2025 project update",
        "dark": False,
        "notes": "Full-colour TI Corp lockup recovered from the official Pattullo Bridge Replacement Project Summer 2025 Project Update, page 1. The emblem, divider and all lettering are original vector paths. The website PNG remains available as a separate specimen. PDF print colours are converted to sRGB; this is an extraction from a publication, not a separately published SVG master.",
    },
    {
        "id": "ticorp-2020-reversed-source-vector",
        "filename": "pbr-project2020.pdf",
        "url": "https://www.pattullobridgereplacement.ca/app/uploads/sites/637/2020/10/Project-Overview-May-2020.pdf",
        "sha256": "39c640ca29bcc45da2502a1614b216f8d84dce9cd8bd41660b20657a09c3d28c",
        "page": 19,
        "indices": list(range(1, 55)),
        "date": "Spring 2020",
        "label": "White, Spring 2020 project overview",
        "dark": True,
        "notes": "Original white TI Corp lockup recovered from the back cover (PDF page 19) of the official Pattullo Bridge Replacement Project Spring 2020 Project Overview. The source's blue page background is excluded; the SVG has a transparent background and needs a dark ground. This is the publication's own reverse artwork, not a recolouring of the full-colour specimen.",
    },
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extract(spec, source_dir):
    data = (source_dir / spec["filename"]).read_bytes()
    if digest(data) != spec["sha256"]:
        raise ValueError(f"Source checksum differs: {spec['filename']}")
    doc = fitz.open(stream=data, filetype="pdf")
    page = doc[spec["page"] - 1]
    drawings = page.get_drawings()
    original = ET.fromstring(page.get_svg_image(text_as_path=True))
    leaves = []

    def walk(node):
        for child in node:
            if child.tag == f"{{{NS}}}defs":
                continue
            if child.tag == f"{{{NS}}}path":
                leaves.append(child)
            walk(child)

    walk(original)
    if len(leaves) != len(drawings):
        raise ValueError("PDF drawing order no longer matches SVG painted-path order")
    keep = {id(leaves[index]) for index in spec["indices"]}

    def selected(node):
        if node.tag == f"{{{NS}}}path":
            return copy.deepcopy(node) if id(node) in keep else None
        if node.tag not in (f"{{{NS}}}g", f"{{{NS}}}svg"):
            return None
        new = ET.Element(node.tag, node.attrib)
        for child in node:
            chosen = selected(child)
            if chosen is not None:
                new.append(chosen)
        return new if len(new) else None

    output = selected(original)
    bounds = fitz.Rect(drawings[spec["indices"][0]]["rect"])
    for index in spec["indices"][1:]:
        bounds |= drawings[index]["rect"]
    for image in page.get_image_info():
        if (bounds & fitz.Rect(image["bbox"])).get_area() > 0:
            raise ValueError("A raster image intersects the selected logo")
    for block in page.get_text("blocks"):
        if (bounds & fitz.Rect(block[:4])).get_area() > 0:
            raise ValueError("Live text intersects the selected logo")
    crop = bounds + (-0.6, -0.6, 0.6, 0.6)
    output.set("viewBox", " ".join(f"{v:.6f}" for v in (crop.x0, crop.y0, crop.width, crop.height)))
    # A useful intrinsic size for the gallery's responsive <img>; the PDF-coordinate
    # viewBox, paths and transforms are unchanged by this display-only scaling.
    output.set("width", "780")
    output.set("height", f"{780 * crop.height / crop.width:.6f}")
    refs = set(re.findall(r"url\(#([^\)]+)\)", ET.tostring(output, encoding="unicode")))
    definitions = {
        el.get("id"): el
        for defs in original.findall(f"{{{NS}}}defs")
        for el in defs if el.get("id")
    }
    added = set()
    needed = ET.Element(f"{{{NS}}}defs")
    while refs - added:
        key = sorted(refs - added)[0]
        node = copy.deepcopy(definitions[key])
        needed.append(node)
        added.add(key)
        refs.update(re.findall(r"url\(#([^\)]+)\)", ET.tostring(node, encoding="unicode")))
    if len(needed):
        output.insert(0, needed)
    title = ET.Element(f"{{{NS}}}title")
    title.text = f"Transportation Investment Corporation - {spec['label']}"
    description = ET.Element(f"{{{NS}}}desc")
    description.text = f"Original outlined paths extracted from {spec['url']}, PDF page {spec['page']}. No tracing or substituted type. Publication date is a sighting, not an adoption date."
    output.insert(0, description)
    output.insert(0, title)
    counts = {}
    for el in output.iter():
        tag = el.tag.split("}")[-1]
        counts[tag] = counts.get(tag, 0) + 1
    if set(counts) - {"svg", "g", "defs", "clipPath", "path", "title", "desc"}:
        raise ValueError(f"Unexpected SVG content: {counts}")
    svg = ET.tostring(output, encoding="utf-8", xml_declaration=True) + b"\n"
    if re.search(rb"\bon[a-z]+\s*=|(?:href|src)\s*=", svg, re.I):
        raise ValueError("Active or external SVG content")
    path = f"identity-collected/{BODY}/{spec['id']}.svg"
    record = {
        "id": spec["id"], "bodyId": BODY,
        "organization": "Transportation Investment Corporation",
        "category": "current-crown", "label": spec["label"],
        "file": path, "bytes": len(svg), "sha256": digest(svg),
        "format": "svg", "genuineVectorVerified": True,
        "provenance": "Official publication, original native vector paths extracted; not a supplied standalone master.",
        "sourceBytesUnchanged": False,
        "sourceUrl": spec["url"], "sourcePageUrl": spec["url"],
        "sourcePdfPage": spec["page"], "sourceSha256": spec["sha256"],
        "sourceDate": spec["date"],
        "dateMeaning": "Date printed on the source publication, not an adoption or first-use date.",
        "retrievedDate": "2026-11-08", "darkBackgroundRecommended": spec["dark"],
        "notes": spec["notes"],
        "method": "PyMuPDF 1.26.6 PDF-to-SVG conversion, preserving selected source path nodes, ancestor transforms and referenced clipping definitions. Unrelated artwork, page backgrounds, raster images and unused definitions excluded. All lettering was already outlined in the PDF. No tracing, type recreation or recolouring; PDF print colours converted to sRGB by MuPDF. Intrinsic width is 780px with proportional height for display; the PDF-coordinate viewBox and geometry are retained.",
        "sourceBounds": list(bounds), "sourceCrop": list(crop),
        "selectedDrawingIndices": spec["indices"],
        "validation": {
            "xmlElementCounts": counts, "paintedPaths": len(spec["indices"]),
            "embeddedImages": 0, "textElements": 0, "externalResources": [],
            "intersectingSourceImages": 0, "intersectingSourceText": 0,
            "sha256Verified": True,
        },
    }
    return ROOT / "public" / path, svg, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--check", action="store_true", help="Compare outputs without changing them")
    args = parser.parse_args()
    if fitz.VersionBind != "1.26.6":
        raise SystemExit(f"Use PyMuPDF 1.26.6 for byte-reproducible output, found {fitz.VersionBind}")
    args.source_dir.mkdir(parents=True, exist_ok=True)
    records = []
    outputs = []
    for spec in SOURCES:
        source = args.source_dir / spec["filename"]
        if args.download and not source.exists():
            with urllib.request.urlopen(spec["url"], timeout=60) as response:
                data = response.read()
            if digest(data) != spec["sha256"]:
                raise ValueError(f"Downloaded source checksum differs: {spec['filename']}")
            source.write_bytes(data)
        path, svg, record = extract(spec, args.source_dir)
        outputs.append((path, svg))
        records.append(record)
    register = {
        "title": "TI Corp original vector recovery",
        "researchDate": "2026-11-08",
        "repositorySnapshot": "280b5015ddd2a092acf26b242b3aec2dd220b690",
        "previousResearch": "../vector-search-2026-10-30/research/current_crown_findings.json",
        "datePolicy": "Publication dates establish dated specimens, not adoption or first use.",
        "assets": records,
    }
    outputs.append((HERE / "source-register.json", (json.dumps(register, indent=2) + "\n").encode()))
    for path, content in outputs:
        if args.check:
            if path.read_bytes() != content:
                raise ValueError(f"Generated output differs: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        print(f"{'Verified' if args.check else 'Wrote'} {path.relative_to(ROOT)} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
