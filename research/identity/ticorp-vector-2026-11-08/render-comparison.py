"""Render a review sheet of official PDF crops beside the extracted SVGs.

Requires PyMuPDF 1.26.6 and Pillow. Run after extract.py, supplying the same
--source-dir. The sheet is evidence only, not a replacement logo asset.
"""

import argparse
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def raster(page, clip=None):
    pix = page.get_pixmap(matrix=fitz.Matrix(6, 6), clip=clip, alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)


def place(sheet, picture, box, background):
    x, y, width, height = box
    plate = Image.new("RGBA", (width, height), background)
    picture.thumbnail((width - 32, height - 32), Image.Resampling.LANCZOS)
    plate.alpha_composite(picture, ((width - picture.width) // 2, (height - picture.height) // 2))
    sheet.paste(plate.convert("RGB"), (x, y))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    args = parser.parse_args()
    register = json.loads((HERE / "source-register.json").read_text())
    sheet = Image.new("RGB", (1500, 810), "#edf1f5")
    draw = ImageDraw.Draw(sheet)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    heading = ImageFont.truetype(font_path, 32)
    label = ImageFont.truetype(font_path, 23)
    small = ImageFont.truetype(font_path, 18)
    draw.text((36, 26), "TI Corp: original vectors recovered from official publications", font=heading, fill="#172f4b")
    draw.text((36, 78), "Source PDF crop", font=label, fill="#43576c")
    draw.text((768, 78), "Extracted SVG", font=label, fill="#43576c")
    for index, asset in enumerate(register["assets"]):
        filename = "pbr-project2025.pdf" if index == 0 else "pbr-project2020.pdf"
        with fitz.open(args.source_dir / filename) as pdf:
            source = raster(pdf[asset["sourcePdfPage"] - 1], fitz.Rect(asset["sourceCrop"]))
        with fitz.open(ROOT / "public" / asset["file"]) as svg:
            # The SVG is already 780px wide; a lower render scale is sufficient here.
            pix = svg[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=True)
            extracted = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
        y = 120 + index * 300
        background = "#166b98" if asset["darkBackgroundRecommended"] else "#ffffff"
        place(sheet, source, (36, y, 696, 220), background)
        place(sheet, extracted, (768, y, 696, 220), background)
        draw.text((36, y + 234), f"{asset['sourceDate']} publication · PDF page {asset['sourcePdfPage']}", font=label, fill="#172f4b")
        draw.text((768, y + 234), f"{asset['validation']['paintedPaths']} original painted paths · outlined lettering", font=label, fill="#172f4b")
    draw.text((36, 744), "Review sheet only. Both SVG downloads have transparent backgrounds; white artwork needs a dark ground.", font=small, fill="#43576c")
    draw.text((36, 773), "Publication dates identify these specimens and do not establish adoption dates.", font=small, fill="#43576c")
    target = HERE / "source-comparison.png"
    sheet.save(target, optimize=True)
    print(target)


if __name__ == "__main__":
    main()
