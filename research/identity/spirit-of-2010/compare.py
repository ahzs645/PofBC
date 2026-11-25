"""Compare the editable SVG with the two held, native-resolution print specimens.

Run with Python 3, Pillow, PyMuPDF, numpy and scipy. The figure uses DejaVu Sans.
"""
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

ART = Path(__file__).resolve().parents[3] / "public/initiatives/spirit-of-2010"


def render_svg():
    with pymupdf.open(ART / "spirit-of-2010.svg") as source:
        with pymupdf.open("pdf", source.convert_to_pdf()) as pdf:
            page = pdf[0]
            pix = page.get_pixmap(matrix=pymupdf.Matrix(800 / page.rect.width, 804 / page.rect.height))
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return image.resize((200, 201), Image.Resampling.LANCZOS)


def ink(image, threshold=0.5):
    return 1 - np.asarray(image.convert("RGB"), dtype=float).min(axis=2) / 255 > threshold


def iou(observed, reconstructed):
    return np.logical_and(observed, reconstructed).sum() / np.logical_or(observed, reconstructed).sum()


def overlay(observed, reconstructed):
    rgb = np.full((*observed.shape, 3), 255, dtype=np.uint8)
    rgb[observed] = (210, 79, 38)
    rgb[reconstructed] = (0, 125, 147)
    rgb[observed & reconstructed] = (43, 43, 44)
    return Image.fromarray(rgb)


def main():
    colour = Image.open(ART / "resort-strategy-2004.jpg")
    mono = Image.open(ART / "playmaker-2006.png")
    vector = render_svg()

    # Map from the independent scan’s native pixel coordinates into the SVG.
    # Only the published frame is used to register the 2006 scan.
    sx = (198.73 - 1.60) / (199 - 2)
    sy = (198.60 - 2.43) / (196 - 2)
    registered = vector.transform(mono.size, Image.Transform.AFFINE,
                                  (sx, 0, 1.60 - 2 * sx, 0, sy, 2.43 - 2 * sy),
                                  resample=Image.Resampling.BILINEAR, fillcolor="white")
    c, v = ink(colour), ink(vector)
    s, p = ink(mono), ink(registered)
    for threshold in [0.4, 0.5, 0.6]:
        print(f"2004, threshold {threshold:.2f}: {iou(ink(colour, threshold), ink(vector, threshold)):.4f}")
    for name, row, col in [("capitals", slice(26, 67), slice(17, 184)),
                           ("of and rules", slice(70, 106), slice(17, 184)),
                           ("numerals", slice(108, 176), slice(17, 184))]:
        print(f"2004, {name}: {iou(c[row, col], v[row, col]):.4f}")
    print(f"2006, raw pixels: {iou(s, p):.4f}")
    for threshold in [0.18, 0.25, 0.32]:
        smoothed = gaussian_filter(s.astype(float), 0.85) > threshold
        expected = gaussian_filter(p.astype(float), 0.85) > threshold
        print(f"2006, screen-density threshold {threshold:.2f}: {iou(smoothed, expected):.4f}")

    sheet = Image.new("RGB", (1330, 1195), "#ffffff")
    draw = ImageDraw.Draw(sheet)
    heading = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    subheading = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    caption = ImageFont.truetype("DejaVuSans.ttf", 20)
    draw.text((44, 28), "Spirit of 2010", font=heading, fill="#172e42")
    draw.text((44, 87), "2004  ·  Resort Strategy and Action Plan", font=subheading, fill="#172e42")
    draw.text((44, 588), "2006  ·  A Playmaker’s Guide", font=subheading, fill="#172e42")
    rows = [(134, colour, vector, c, v, "Original colour JPEG"),
            (635, mono, registered, s, p, "Original screened printing")]
    for top, observed, fitted, ref, fit, source_label in rows:
        for index, (label, img) in enumerate([
            (source_label, observed), ("Registered reconstruction", fitted),
            (f"Raw-mask overlap  {iou(ref, fit):.1%}", overlay(ref, fit))
        ]):
            x = 44 + index * 431
            enlarged = img.convert("RGB").resize((img.width * 2, img.height * 2), Image.Resampling.NEAREST)
            sheet.paste(enlarged, (x, top))
            draw.text((x, top + 413), label, font=caption, fill="#172e42")
    for x, label, colour_code in [(44, "Both", "#2b2b2c"), (239, "Source only", "#d24f26"),
                                  (494, "Reconstruction only", "#007d93")]:
        draw.rectangle((x, 1113, x + 22, 1135), fill=colour_code)
        draw.text((x + 34, 1111), label, font=caption, fill="#172e42")
    draw.text((44, 1150), "The 2006 halftone leaves white gaps inside printed strokes. Raw overlap counts those gaps.", font=caption, fill="#374650")
    sheet.save(ART / "overlay.png")


if __name__ == "__main__":
    main()
