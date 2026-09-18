"""Rasterises the generated/original SVG pairs and writes a side-by-side difference sheet.

Called by scripts/compare-artwork.mjs; not intended to be run directly.
"""
import json
import sys
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageDraw

out = Path(sys.argv[1])
width = int(sys.argv[2])

cases = json.loads((out / "cases.json").read_text())
panels = []

for case in cases:
    layout = case["layout"]
    height = max(1, round(width * case["height"] / case["width"]))

    rendered = {}
    for kind in ("generated", "original"):
        png = out / f"{layout}-{kind}.png"
        cairosvg.svg2png(
            url=str(out / f"{layout}-{kind}.svg"),
            write_to=str(png),
            output_width=width,
            output_height=height,
        )
        rendered[kind] = Image.open(png).convert("RGB")

    # Anything that lines up cancels to black; whatever glows is where the reconstruction and the
    # original artwork disagree.
    difference = ImageChops.difference(rendered["generated"], rendered["original"])
    box = difference.convert("L").point(lambda v: 255 if v > 40 else 0).getbbox()
    pixels = sum(1 for v in difference.convert("L").getdata() if v > 40)
    total = difference.width * difference.height
    print(f"  {layout:<11} differing pixels: {pixels:>7} / {total} ({100 * pixels / total:.2f}%)"
          + (f"  worst region {box}" if box else "  (clean)"))

    panels.append((layout, rendered["original"], rendered["generated"], difference))

# One tall sheet: original, reconstruction, and the difference, for each lockup.
pad = 24
label = 34
sheet_width = width * 3 + pad * 4
sheet_height = sum(p[1].height + label + pad for p in panels) + pad
sheet = Image.new("RGB", (sheet_width, sheet_height), "#14181c")
draw = ImageDraw.Draw(sheet)

y = pad
for layout, original, generated, difference in panels:
    draw.text((pad, y), f"{layout}  —  original / generated / difference", fill="#e8eef4")
    y += label
    for index, image in enumerate((original, generated, difference)):
        sheet.paste(image, (pad + index * (width + pad), y))
    y += original.height + pad

sheet.save(out / "comparison.png")
print(f"\n  → {out / 'comparison.png'}")
