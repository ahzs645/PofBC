"""Render source/SVG review pairs and an overview; requires PyMuPDF and Pillow."""

import argparse
import json
import math
from pathlib import Path
import textwrap

import fitz
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size):
    return ImageFont.truetype(FONT, size)


def place(sheet, picture, box, background):
    x, y, width, height = box
    plate = Image.new("RGBA", (width, height), background)
    picture = picture.copy()
    picture.thumbnail((width - 32, height - 32), Image.Resampling.LANCZOS)
    plate.alpha_composite(picture.convert("RGBA"), ((width - picture.width) // 2, (height - picture.height) // 2))
    sheet.paste(plate.convert("RGB"), (x, y))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    args = parser.parse_args()
    specs = json.loads((HERE / "sources.json").read_text())
    assets = json.loads((HERE / "source-register.json").read_text())["assets"]
    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    overview = Image.new("RGB", (1500, 125 + 310 * math.ceil(len(assets) / 3)), "#edf1f5")
    title = ImageDraw.Draw(overview)
    title.text((28, 24), "Recovered original vector logos", font=font(34), fill="#172f4b")
    title.text((28, 76), "Official or attributable publication specimens - source dates are not adoption dates", font=font(20), fill="#43576c")
    for index, (spec, asset) in enumerate(zip(specs, assets)):
        if spec["id"] != asset["id"]:
            raise ValueError("Source order differs from register")
        with fitz.open(args.source_dir / spec["sourceFile"]) as pdf:
            crop = fitz.Rect(asset["sourceCrop"])
            scale = max(5, min(1400 / crop.width, 460 / crop.height))
            pix = pdf[asset["sourcePdfPage"] - 1].get_pixmap(matrix=fitz.Matrix(scale, scale), clip=crop, alpha=False)
            source = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        with fitz.open(ROOT / "public" / asset["file"]) as svg:
            pix = svg[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=True)
            extracted = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
        # The padded corner lies outside the logo, revealing its published ground.
        background = spec.get("proofBackground", source.getpixel((0, 0)))
        sheet = Image.new("RGB", (1500, 480), "#edf1f5")
        draw = ImageDraw.Draw(sheet)
        draw.text((28, 22), asset["organization"], font=font(27), fill="#172f4b")
        draw.text((28, 62), asset["label"], font=font(20), fill="#43576c")
        draw.text((28, 106), f"Source PDF - page {asset['sourcePdfPage']}", font=font(21), fill="#43576c")
        draw.text((764, 106), "Extracted SVG - original geometry", font=font(21), fill="#43576c")
        place(sheet, source, (28, 144, 708, 230), background)
        place(sheet, extracted, (764, 144, 708, 230), background)
        draw.text((28, 395), f"{asset['validation']['sourceDrawingCount']} source drawings / {asset['validation']['paintedPaths']} SVG paint paths. SVG: no bitmap, live text or substituted type.", font=font(19), fill="#43576c")
        if asset["validation"]["excludedSourceBackgroundImages"]:
            draw.text((28, 432), "Published page background excluded; transparent logo shown on a dark preview plate.", font=font(19), fill="#43576c")
        sheet.save(evidence / f"{asset['id']}-comparison.png", optimize=True)
        x, y = 20 + (index % 3) * 500, 120 + (index // 3) * 310
        place(overview, extracted, (x, y, 460, 195), background)
        draw = ImageDraw.Draw(overview)
        for line, text in enumerate(textwrap.wrap(asset["organization"], width=41)):
            draw.text((x, y + 205 + line * 24), text, font=font(20), fill="#172f4b")
        detail = f"{asset['sourceDate']} / page {asset['sourcePdfPage']}"
        for line, text in enumerate(textwrap.wrap(detail, width=45)):
            draw.text((x, y + 256 + line * 21), text, font=font(17), fill="#43576c")
    overview.save(HERE / "recovered-logos.png", optimize=True)
    print(f"Rendered {len(assets)} comparison sheets and recovered-logos.png")


if __name__ == "__main__":
    main()
