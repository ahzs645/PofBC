#!/usr/bin/env python3
"""Reproduce the bounded historical-arms comparison from pinned local inputs.

Requires Python 3, Pillow, NumPy and PyMuPDF. Does not fetch remote data.
An optional --museum-pdf checks the original PDF and extracted JPEG as well.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import fitz
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path, expected):
    actual = sha(path)
    if actual != expected:
        raise ValueError(f"Checksum mismatch: {path.name}: {actual}")


def raster_svg(data, scale=1, alpha=True):
    doc = fitz.open(stream=data.encode(), filetype="svg")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=alpha)
    return Image.frombytes("RGBA" if alpha else "RGB", [pix.width, pix.height], pix.samples)


def png_uri(image):
    out = io.BytesIO()
    image.save(out, format="PNG")
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def image_tag(image, x=0, y=0, width=None, height=None):
    width = width or image.width
    height = height or image.height
    return f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="{png_uri(image)}"/>'


def bbox(mask):
    yy, xx = np.where(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]


def size(box):
    return [box[2] - box[0], box[3] - box[1]]


def text(x, y, content, font_size=18, fill="#273b50", weight="normal"):
    return f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{font_size}" font-weight="{weight}" fill="{fill}">{escape(content)}</text>'


def svg_doc(width, height, body, title):
    return (f'<svg xmlns="{SVG_NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<title>{escape(title)}</title><rect width="{width}" height="{height}" fill="#f5f4ef"/>{body}</svg>')


def write_visual(name, data):
    (ROOT / f"{name}.svg").write_text(data)
    raster_svg(data, alpha=False).save(ROOT / f"{name}.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--museum-pdf", type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "registration.json").read_text())
    target = manifest["target"]
    candidate = manifest["candidate"]

    verify(ROOT / target["nativePageImage"], target["nativePageImageSha256"])
    verify(ROOT / target["crop"], target["cropSha256"])
    verify(ROOT / candidate["file"], candidate["sha256"])
    page_image = Image.open(ROOT / target["nativePageImage"])
    reference = Image.open(ROOT / target["crop"]).convert("RGB")
    reproduced_crop = page_image.crop(target["nativeCropBoxHalfOpen"]).convert("RGB")
    if not np.array_equal(np.asarray(reference), np.asarray(reproduced_crop)):
        raise ValueError("Target crop is not an exact native-pixel crop of the retained cover")

    if args.museum_pdf:
        verify(args.museum_pdf, target["sourcePdfSha256"])
        doc = fitz.open(args.museum_pdf)
        original = doc.extract_image(target["pdfImageXref"])["image"]
        if hashlib.sha256(original).hexdigest() != target["nativePageImageSha256"]:
            raise ValueError("The retained cover differs from the original PDF JPEG")

    compared = []
    comparison_images = []
    for spec in manifest["comparisonSources"]:
        verify(ROOT / spec["crop"], spec["cropSha256"])
        pdf = ROOT / spec["sourcePdf"]
        verify(pdf, spec["sourcePdfSha256"])
        doc = fitz.open(pdf)
        page = doc[spec["page"] - 1]
        original = Image.open(io.BytesIO(doc.extract_image(page.get_images()[0][0])["image"]))
        held = Image.open(ROOT / spec["crop"])
        if not np.array_equal(np.asarray(original.crop(spec["nativeCropBoxHalfOpen"])), np.asarray(held)):
            raise ValueError(f"Native crop does not reproduce: {spec['id']}")
        box = bbox(np.asarray(held.convert("L")) < spec["measurementLuminanceThreshold"])
        compared.append({"id": spec["id"], "cropDimensionsPx": list(held.size), "inkBoxHalfOpen": box,
                         "inkDimensionsPx": size(box), "luminanceThreshold": spec["measurementLuminanceThreshold"]})
        comparison_images.append(held.convert("RGB"))

    grayscale = np.asarray(reference.convert("L"))
    reference_box = bbox(grayscale < manifest["registration"]["referenceInkLuminanceThreshold"])
    reference_size = size(reference_box)
    candidate_svg = (ROOT / candidate["file"]).read_text()
    render_scale = manifest["registration"]["candidateRasterScale"]
    rendered = raster_svg(candidate_svg, render_scale)
    box_raster = bbox(np.asarray(rendered)[:, :, 3] > manifest["registration"]["candidateAlphaThreshold"])
    candidate_box = [v / render_scale for v in box_raster]
    candidate_size = size(candidate_box)
    scale = reference_size[1] / candidate_size[1]
    offset_x = (reference_box[0] + reference_box[2]) / 2 - scale * (candidate_box[0] + candidate_box[2]) / 2
    offset_y = reference_box[1] - scale * candidate_box[1]
    mapped_box = [candidate_box[0] * scale + offset_x, candidate_box[1] * scale + offset_y,
                  candidate_box[2] * scale + offset_x, candidate_box[3] * scale + offset_y]
    relative_width = candidate_size[0] * scale / reference_size[0]
    sensitivity = []
    for threshold in manifest["registration"]["thresholdSensitivity"]:
        rb = bbox(grayscale < threshold)
        rw, rh = size(rb)
        ratio = candidate_size[0] * (rh / candidate_size[1]) / rw
        sensitivity.append({"threshold": threshold, "referenceInkBoxHalfOpen": rb,
                            "candidateWidthFractionAtEqualHeight": ratio})

    # Tint is explicitly analytical. The unmodified original crop appears beside it.
    tint = np.zeros((reference.height, reference.width, 4), dtype=np.uint8)
    tint[:, :, :3] = [0, 124, 145]
    tint[:, :, 3] = (np.clip((245 - grayscale.astype(float)) / 160, 0, 1) * 255).astype(np.uint8)
    tinted = Image.fromarray(tint)
    candidate_root = ET.fromstring(candidate_svg)
    arms = next(c for c in candidate_root if c.attrib.get("data-part") == "arms")
    exact_body = ET.tostring(arms, encoding="unicode")
    magenta_body = exact_body.replace('fill="#000000"', 'fill="#b3296d"')
    matrix = f"translate({offset_x:.9f} {offset_y:.9f}) scale({scale:.12f})"
    current_panel = f'<g transform="{matrix}">{exact_body}</g>'
    overlay_panel = image_tag(tinted) + f'<g transform="{matrix}" opacity="0.66">{magenta_body}</g>'
    standalone = (f'<svg xmlns="{SVG_NS}" viewBox="0 0 230 205">'
                  '<title>1960 specimen and provisional master, uniform-height overlay</title>'
                  '<desc>Cyan is the analytical tint of the retained native scan; magenta is the frozen candidate. Uniform scale and translation only. This is not an artwork master.</desc>'
                  '<rect width="230" height="205" fill="white"/>' + overlay_panel + '</svg>')
    (ROOT / "aligned-overlay.svg").write_text(standalone)
    raster_svg(standalone, 4, alpha=False).save(ROOT / "aligned-overlay.png")

    body = text(30, 47, "Historic arms: measured comparison", 33, weight="bold")
    body += text(30, 79, "Museum report 1960 (printed 1961), cover / PDF page 1", 21)
    body += text(30, 110, "Uniform ink-height alignment. No stretching, warping or invented source detail.", 19)
    panels = [("Documented specimen", image_tag(reference)), ("Current provisional master", current_panel), ("Scale-matched overlay", overlay_panel)]
    for index, (label, content) in enumerate(panels):
        x = 30 + index * 495
        body += text(x, 157, label, 22, weight="bold")
        body += f'<rect x="{x}" y="175" width="450" height="410" rx="8" fill="white" stroke="#d4d8db"/>'
        body += f'<g transform="translate({x + 12},190) scale(1.85)">{content}</g>'
    body += text(30, 617, f"Source ink: {reference_size[0]} x {reference_size[1]} native pixels", 19)
    body += text(525, 617, f"Matched ink: {candidate_size[0] * scale:.1f} x {reference_size[1]} pixels", 19)
    body += text(1020, 617, "Cyan: source  |  Magenta: current", 19)
    body += text(30, 679, f"At equal height, the current master is about {round((1 - relative_width) * 100)}% narrower overall.", 26, weight="bold")
    body += text(30, 713, "This is a proportion comparison between different drawings; it is not an accuracy percentage.", 20)
    observations = [
        (30, "Scroll structure", ["The source has long forked ribbon tails.", "The current master has short curled ends.", "This accounts for much of the width gap."]),
        (525, "Crest and crown", ["The lion occupies a different footprint.", "The main crown has different arches,", "band spacing and proportions."]),
        (1020, "Evidence limit", ["Only about 200 pixels span the source.", "Animal features, hatching and lettering", "cannot be recovered line for line."])
    ]
    for x, heading, lines in observations:
        body += text(x, 769, heading, 23, weight="bold")
        for n, line in enumerate(lines):
            body += text(x, 802 + n * 29, line, 19)
    body += text(30, 923, "Sources, hashes, transformations and threshold sensitivity: registration.json and measurements.json", 17)
    write_visual("overlay-review", svg_doc(1500, 950, body, "Historical-arms uniform-height comparison"))

    native_body = text(30, 47, "Native scan comparison", 33, weight="bold")
    native_body += text(30, 82, "All three native crops enlarged by the same 1.8x factor; no sharpening or added detail.", 21)
    native_specs = [("1960 Museum cover", reference, reference_size, "Printed 1961. Selected for proportions."),
                    ("1954 mining cover", comparison_images[0], compared[0]["inkDimensionsPx"], "Separate broader drawing; keep distinct."),
                    ("1954 mining title page", comparison_images[1], compared[1]["inkDimensionsPx"], "Smaller, darker. Same block not established.")]
    for index, (label, img, dims, note) in enumerate(native_specs):
        x = 30 + index * 495
        native_body += text(x, 135, label, 23, weight="bold")
        native_body += f'<rect x="{x}" y="153" width="450" height="405" rx="8" fill="white" stroke="#d4d8db"/>'
        native_body += image_tag(img, x + (450 - img.width * 1.8) / 2, 168 + (375 - img.height * 1.8) / 2, img.width * 1.8, img.height * 1.8)
        native_body += text(x, 591, f"Measured ink: about {dims[0]} x {dims[1]} pixels", 19)
        native_body += text(x, 622, note, 18)
    native_body += text(30, 669, "Different paper and ink require different measurement thresholds; raw crop pixels are unchanged.", 18)
    write_visual("native-source-comparison", svg_doc(1500, 700, native_body, "Native scan resolution comparison"))

    structure_svg = (ROOT / manifest["structuralStudy"]["file"]).read_text()
    structure_root = ET.fromstring(structure_svg)
    structure_body = "".join(ET.tostring(c, encoding="unicode") for c in structure_root if c.tag == f"{{{SVG_NS}}}g")
    study = text(30, 47, "A bounded start on the 1960 specimen", 31, weight="bold")
    study += text(30, 81, "Manually constructed structure only. Animals, heraldic detail, hatching and type remain unresolved.", 19)
    for index, (label, content) in enumerate([("Editable structural curves", structure_body), ("Structure over the unchanged source", image_tag(reference) + structure_body)]):
        x = 30 + index * 535
        study += text(x, 130, label, 22, weight="bold")
        study += f'<rect x="{x}" y="149" width="495" height="440" rx="8" fill="white" stroke="#d4d8db"/>'
        study += f'<g transform="translate({x + 18},164) scale(2)">{content}</g>'
    study += text(30, 632, "The crown envelope, visible shield sides and forked scroll structure can be placed from this scan.", 20)
    study += text(30, 666, "These approximate contours are a scaffold for a better source, not a finished or authenticated coat of arms.", 19)
    write_visual("structure-review", svg_doc(1100, 700, study, "Partial structural reconstruction of the 1960 specimen"))

    measurements = {
        "candidateCommit": candidate["commit"], "targetId": target["id"],
        "coordinateUnits": "Native reference crop pixels, except unscaled candidate bounds in SVG units",
        "referenceInkBoxHalfOpen": reference_box, "referenceInkDimensionsPx": reference_size,
        "candidateInkBoxSvgUnitsHalfOpen": candidate_box, "candidateInkDimensionsSvgUnits": candidate_size,
        "uniformScale": scale, "translation": [offset_x, offset_y], "rotationDegrees": 0,
        "candidateMappedInkBoxHalfOpen": mapped_box, "candidateMappedInkDimensionsPx": size(mapped_box),
        "candidateWidthFractionAtEqualHeight": relative_width,
        "thresholdSensitivity": sensitivity, "nativeComparisons": compared,
        "interpretation": "Difference in full drawing proportions, including scroll tails; not an authenticity score or a claim that these are the same engraving.",
        "software": {"PyMuPDF": fitz.VersionBind, "Pillow": Image.__version__, "NumPy": np.__version__},
        "inputChecks": ["Frozen candidate hash", "Native cover hash", "Target crop hash and exact pixel reproduction", "Both 1954 PDF hashes", "Both 1954 crop hashes and exact pixel reproduction"]
    }
    (ROOT / "measurements.json").write_text(json.dumps(measurements, indent=2) + "\n")
    print(json.dumps({"referenceInkPx": reference_size, "candidateWidthFraction": relative_width,
                      "uniformScale": scale, "sourceCropPixelChecks": 3, "figures": 4,
                      "originalMuseumPdfVerified": bool(args.museum_pdf)}, indent=2))


if __name__ == "__main__":
    main()
