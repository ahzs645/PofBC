#!/usr/bin/env python3
"""Render the authored master, its printed reference and a supplied earlier SVG.

Pixel overlap is a fixed-registration diagnostic, not historical authentication.
No reference pixels are converted to SVG contours by this review or the builder.
Requires Inkscape, Pillow, numpy and PyMuPDF; optional --font is a local TTF.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent
REPO = ROOT.parents[3]
MASTER = REPO / "public/identity-collected/bc-trade/bc-trade-1991-rebuilt.svg"
REFERENCE = REPO / "public/identity-collected/bc-trade/bc-trade-1991-scan.png"
SVG = "{http://www.w3.org/2000/svg}"


def render(source, destination):
    subprocess.run(["inkscape", str(source), "--export-filename=" + str(destination)],
                   check=True, capture_output=True, text=True)


def on_white(image):
    image = image.convert("RGBA")
    white = Image.new("RGBA", image.size, "white")
    white.alpha_composite(image)
    return white.convert("RGB")


def colour_masks(image):
    rgb = np.asarray(image.convert("RGB"), dtype=float)
    red, green, blue = rgb.transpose(2, 0, 1)
    y, x = np.indices(rgb.shape[:2])
    return {
        "red": (red > 1.2 * green) & (red > 1.15 * blue) & (red < 235),
        "blue": (blue > 1.17 * red) & (green > 1.04 * red) & (blue > green),
        # Limit gold to the sun: blurred red/white boundaries can appear yellow.
        "gold": ((red > 1.1 * blue) & (green > 1.15 * blue) & (red > green)
                 & (red < 240) & (green > 130) & (x > 55) & (x < 130)
                 & (y > 130) & (y < 184)),
        "wordmark": (red + green + blue < 420) & (y >= 185),
    }


def overlap(reference, drawing):
    expected = colour_masks(reference)
    actual = colour_masks(on_white(drawing).resize(reference.size, Image.Resampling.LANCZOS))
    return {name: round(float((expected[name] & actual[name]).sum()
                             / (expected[name] | actual[name]).sum()), 4)
            for name in expected}


def comparison(reference, before, after, font_path):
    def font(size):
        return ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default(size=size)
    sheet = Image.new("RGB", (1800, 1060), "#F2F1EC")
    draw = ImageDraw.Draw(sheet)
    draw.text((60, 36), "BC TRADE", font=font(42), fill="#162A49")
    draw.text((62, 96), "Printed evidence and reconstructed artwork | 14 November 2026",
              font=font(21), fill="#45525C")
    panels = [
        ("1991 printed reference", reference.resize((784, 872), Image.Resampling.LANCZOS),
         "Native 196 x 218 px scan, enlarged."),
        ("Previous gallery vector", on_white(before), "Solid letters; uniform lower separators."),
        ("Revised vector", on_white(after), "Open letter details; revised flag shapes."),
    ]
    for index, (title, picture, caption) in enumerate(panels):
        x = 60 + index * 570
        draw.rounded_rectangle((x, 150, x + 540, 950), radius=8, fill="white", outline="#D7DAD8", width=2)
        draw.text((x + 24, 177), title, font=font(26), fill="#162A49")
        sheet.paste(picture.resize((470, 523), Image.Resampling.LANCZOS), (x + 35, 223))
        draw.text((x + 28, 770), "LETTERING DETAIL", font=font(15), fill="#6A747A")
        detail = picture.crop((55, 740, 640, 832))
        sheet.paste(detail.resize((470, 74), Image.Resampling.LANCZOS), (x + 35, 802))
        draw.text((x + 25, 904), caption, font=font(18), fill="#45525C")
    draw.text((62, 984), "Geometry follows printed evidence. Exact typeface and official ink colours remain unverified.",
              font=font(20), fill="#45525C")
    review = PACKAGE / "review"
    review.mkdir(exist_ok=True)
    sheet.save(review / "comparison.webp", quality=94, method=6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path, help="Earlier master SVG for comparison")
    parser.add_argument("--font", type=str, default=None, help="Optional local TTF for review labels")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        render(MASTER, work / "after.png")
        render(args.before, work / "before.png")
        render(MASTER, work / "after.pdf")
        before = Image.open(work / "before.png").convert("RGBA")
        after = Image.open(work / "after.png").convert("RGBA")
        reference = Image.open(REFERENCE).convert("RGB")
        comparison(reference, before, after, args.font)
        root = ET.parse(MASTER).getroot()
        paths = root.findall(".//" + SVG + "path")
        groups = root.findall(".//" + SVG + "g")
        with fitz.open(work / "after.pdf") as pdf:
            page = pdf[0]
            pdf_report = {"pages": len(pdf), "raster_images": len(page.get_images()),
                          "font_objects": len(page.get_fonts()),
                          "vector_drawing_objects": len(page.get_drawings()),
                          "page_dimensions_points": list(page.rect)}
        report = {
            "reviewDate": "2026-11-14",
            "masterSha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
            "svg": {"paths": len(paths), "image_elements": len(root.findall(".//" + SVG + "image")),
                    "live_text_elements": len(root.findall(".//" + SVG + "text")),
                    "letter_groups": sum(g.get("id", "").startswith("letter-") for g in groups),
                    "all_paths_closed": all(p.get("d", "").strip().lower().endswith("z") for p in paths),
                    "stroke_attributes": sum("stroke" in p.attrib for p in paths),
                    "file_bytes": MASTER.stat().st_size},
            "pdf": pdf_report,
            "png": {"dimensions": list(after.size),
                    "transparent_corners": all(after.getpixel(point)[3] == 0 for point in
                                               [(0, 0), (after.width-1, 0), (0, after.height-1),
                                                (after.width-1, after.height-1)])},
            "sourceComparison": {
                "sourceDimensions": list(reference.size),
                "registration": "Fixed 4x scan coordinates; no independent fit or warp of either candidate.",
                "metric": "Intersection over union of fixed colour masks after 196 x 218 downsampling; thresholds in source/review_bc_trade.py.",
                "limitation": "Diagnostics only, not an accuracy percentage. Scan blur, paper and approximate RGB colours affect masks; gold is restricted to the sun region.",
                "beforeSha256": hashlib.sha256(args.before.read_bytes()).hexdigest(),
                "before": overlap(reference, before), "after": overlap(reference, after),
            },
        }
        (PACKAGE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
