"""Recover native logo paths from the publications listed in sources.json.

Requires PyMuPDF 1.26.6. Source PDFs stay outside the repository. --download
fetches missing public sources and verifies their fixed hashes. --check compares
the SVGs and source register byte for byte without changing them.
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
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def recover(spec, source_dir):
    data = (source_dir / spec["sourceFile"]).read_bytes()
    if digest(data) != spec["sourceSha256"]:
        raise ValueError(f"Source checksum differs: {spec['sourceFile']}")
    doc = fitz.open(stream=data, filetype="pdf")
    page = doc[spec["sourcePdfPage"] - 1]
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
    # MuPDF emits separate fill and stroke nodes for a PDF 'fs' drawing.
    # Validate those paired nodes before mapping the source drawing indices.
    mapping = []
    cursor = 0
    for drawing in drawings:
        count = 2 if drawing["type"] == "fs" else 1
        nodes = leaves[cursor:cursor + count]
        if count == 2:
            if len(nodes) != 2 or any(nodes[0].get(k) != nodes[1].get(k) for k in ("d", "transform")):
                raise ValueError("PDF fill/stroke pair no longer maps to identical SVG geometry")
            if nodes[0].get("fill") == "none" or nodes[1].get("fill") != "none" or not nodes[1].get("stroke"):
                raise ValueError("Unexpected SVG fill/stroke ordering")
        mapping.append(list(range(cursor, cursor + count)))
        cursor += count
    if cursor != len(leaves):
        raise ValueError("PDF drawing order no longer matches SVG painted-path order")
    selected_indices = spec["selectedDrawingIndices"]
    svg_indices = [at for index in selected_indices for at in mapping[index]]
    keep = {id(leaves[index]) for index in svg_indices}

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
    bounds = fitz.Rect(drawings[selected_indices[0]]["rect"])
    for index in selected_indices[1:]:
        bounds |= drawings[index]["rect"]
    # Two BCLC covers place complete native logo paths above a page photograph.
    # Only explicitly reviewed image indices from the fixed-hash source may be
    # excluded. Every other intersecting image remains a hard failure.
    approved_backgrounds = spec.get("excludedSourceBackgroundImageIndices", [])
    if len(set(approved_backgrounds)) != len(approved_backgrounds):
        raise ValueError("Duplicate source-background image exclusion")
    excluded_backgrounds = []
    for index, picture in enumerate(page.get_image_info(hashes=True, xrefs=True)):
        if (bounds & fitz.Rect(picture["bbox"])).get_area() > 0:
            if index not in approved_backgrounds:
                raise ValueError("An unreviewed source raster image intersects the selected logo")
            excluded_backgrounds.append({
                "imageIndex": index, "xref": picture["xref"],
                "bbox": list(picture["bbox"]), "width": picture["width"],
                "height": picture["height"], "digestMd5": picture["digest"].hex(),
            })
    if sorted(approved_backgrounds) != sorted(item["imageIndex"] for item in excluded_backgrounds):
        raise ValueError("Reviewed source-background image no longer intersects the logo")
    if excluded_backgrounds and not spec.get("sourceBackgroundExclusionReason"):
        raise ValueError("Source-background exclusion needs a documented visual assessment")
    blank_blocks = 0
    for block in page.get_text("blocks"):
        if (bounds & fitz.Rect(block[:4])).get_area() > 0:
            if str(block[4]).strip():
                raise ValueError("Live source text intersects the selected logo")
            blank_blocks += 1
    # Drawings/text use unrotated coordinates, whereas SVG and rendered-page clips
    # use the displayed page orientation. Preserve the publication's orientation.
    displayed_bounds = bounds * page.rotation_matrix
    crop = displayed_bounds + (-0.6, -0.6, 0.6, 0.6)
    output.set("viewBox", " ".join(f"{v:.6f}" for v in (crop.x0, crop.y0, crop.width, crop.height)))
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
    title.text = f"{spec['organization']} - {spec['label']}"
    description = ET.Element(f"{{{NS}}}desc")
    description.text = f"Original outlined paths from {spec['sourceUrl']}, PDF page {spec['sourcePdfPage']}. No tracing or substituted type. Source dates identify specimens, not adoption."
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
    path = f"identity-collected/{spec['bodyId']}/{spec['id']}.svg"
    record = {key: value for key, value in spec.items() if key not in ("sourceFile", "proofBackground")}
    record.update({
        "file": path, "bytes": len(svg), "sha256": digest(svg),
        "format": "svg", "genuineVectorVerified": True, "sourceBytesUnchanged": False,
        "retrievedDate": "2026-11-08",
        "method": "PyMuPDF 1.26.6 PDF-to-SVG conversion preserving selected original path nodes, ancestor transforms, paint order and referenced clipping definitions. All lettering was already outlined. Unrelated page artwork and unused definitions excluded. No tracing, type recreation or manual recolouring; PDF print colours converted to sRGB by MuPDF. Original page rotation preserved. Intrinsic width is 780px with proportional height; source geometry remains unchanged.",
        "sourceBoundsUnrotated": list(bounds), "sourcePageRotation": page.rotation,
        "sourceBounds": list(displayed_bounds), "sourceCrop": list(crop),
        "selectedSvgPaintedPathIndices": svg_indices,
        "validation": {
            "xmlElementCounts": counts, "sourceDrawingCount": len(selected_indices),
            "paintedPaths": len(svg_indices), "embeddedImages": 0, "textElements": 0,
            "externalResources": [], "intersectingSourceImages": len(excluded_backgrounds),
            "excludedSourceBackgroundImages": excluded_backgrounds,
            "intersectingVisibleSourceText": 0, "ignoredWhitespaceOnlyTextBlocks": blank_blocks,
            "sha256Verified": True,
        },
    })
    return ROOT / "public" / path, svg, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if fitz.VersionBind != "1.26.6":
        raise SystemExit(f"Use PyMuPDF 1.26.6, found {fitz.VersionBind}")
    specs = json.loads((HERE / "sources.json").read_text())
    outputs, records = [], []
    for spec in specs:
        source = args.source_dir / spec["sourceFile"]
        if args.download and not source.exists():
            with urllib.request.urlopen(spec["sourceUrl"], timeout=60) as response:
                data = response.read()
            if digest(data) != spec["sourceSha256"]:
                raise ValueError(f"Downloaded source checksum differs: {spec['sourceFile']}")
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(data)
        path, svg, record = recover(spec, args.source_dir)
        outputs.append((path, svg))
        records.append(record)
    register = {
        "title": "Original vector logo follow-up", "researchDate": "2026-11-08",
        "timeZone": "America/Vancouver",
        "repositorySnapshot": "658a83af56e4b6ebaf38bb1a69812d6052ce4cc1",
        "datePolicy": "Publication/reporting dates establish specimens, not adoption or first use.",
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
