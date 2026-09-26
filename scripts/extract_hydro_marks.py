"""Lifts BC Hydro's later marks out of the artwork they were supplied in.

Two identities, both kept as drawn — every shape comes out of the source file unchanged and is
labelled with the part it plays, so the gallery can colour it:

  1990–2016   "BC hydro" beside the square symbol, from artwork/hydro/bc-hydro-1990.ai (an
              Illustrator file, which is a PDF underneath). "BC" in green, "hydro" in blue, the
              symbol green over blue with the stylized H cut out between its halves.

  2016–now    The circular symbol, "BC Hydro" and the "Power smart" tagline, from the logo pages of
              BC Hydro's February 2020 brand guidelines (artwork/hydro/brand-guidelines-2020-logo.pdf,
              pages 14 and 15 of that document, kept without its photographs). The guidelines forbid
              reconstructing the logo, so it is taken from their own artwork and only ever drawn in
              the colourways they give. The black and reverse versions on the page are the same
              shapes as the colour one; this checks that rather than assuming it.

Writes src/assets/hydroMarks.js. Committed, as the other lifted artwork is.

Run: npm run extract:hydro-marks
"""

import json
import pathlib
import sys

import pymupdf

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from extract_current_marks import fmt, hex_of, path_data  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_1990 = ROOT / "artwork/hydro/bc-hydro-1990.ai"
SOURCE_2016 = ROOT / "artwork/hydro/brand-guidelines-2020-logo.pdf"
TARGET = ROOT / "src/assets/hydroMarks.js"

GRASS = (0.311, 0.721, 0.282)
SEA = (0.0, 0.708, 0.875)
WHITE = (1.0, 1.0, 1.0)


def close(a, b, tolerance=0.03):
    return a is not None and all(abs(x - y) <= tolerance for x, y in zip(a, b))


def inside(rect, box):
    x0, y0, x1, y1 = box
    return rect.x0 >= x0 and rect.y0 >= y0 and rect.x1 <= x1 and rect.y1 <= y1


def mark(drawings, role_of, source, note):
    """Shapes moved to the origin of their joint bounds, each with its part and fill rule."""
    x0 = min(d["rect"].x0 for d in drawings)
    y0 = min(d["rect"].y0 for d in drawings)
    x1 = max(d["rect"].x1 for d in drawings)
    y1 = max(d["rect"].y1 for d in drawings)
    shapes = []
    for drawing in drawings:
        r = drawing["rect"]
        shape = {
            "role": role_of(drawing),
            "d": path_data(drawing, (x0, y0)),
            "box": [float(fmt(v)) for v in (r.x0 - x0, r.y0 - y0, r.x1 - x0, r.y1 - y0)],
        }
        if drawing.get("even_odd"):
            shape["evenOdd"] = True
        shapes.append(shape)
    return {
        "source": source,
        "note": note,
        "width": float(fmt(x1 - x0)),
        "height": float(fmt(y1 - y0)),
        "printed": {},
        "shapes": shapes,
    }


def signature(drawings):
    """Sizes and item counts in drawing order — enough to tell whether two copies are one drawing."""
    return [(round(d["rect"].width, 1), round(d["rect"].height, 1), len(d["items"])) for d in drawings]


def filled(page):
    return [d for d in page.get_drawings() if d.get("fill") is not None]


def the_1990_mark():
    page = pymupdf.open(SOURCE_1990)[0]
    drawings = sorted(filled(page), key=lambda d: d["rect"].x0)
    symbol_left = max(d["rect"].x0 for d in drawings)
    # The symbol is the two rightmost shapes; the letters run left to right before it.
    letters = [d for d in drawings if d["rect"].x0 < symbol_left - 1]
    if len(letters) != 7:
        raise SystemExit(f"expected the seven letters of BChydro, found {len(letters)}")
    symbol_top = min(d["rect"].y0 for d in drawings if d["rect"].x0 >= symbol_left - 1)

    def role_of(drawing):
        if drawing["rect"].x0 >= symbol_left - 1:
            return "upper" if drawing["rect"].y0 <= symbol_top + 1 else "lower"
        return "bc" if letters.index(drawing) < 2 else "hydro"

    result = mark(drawings, role_of, "artwork/hydro/bc-hydro-1990.ai",
                  "“BC hydro” with the square symbol to its right, as supplied.")
    for drawing in drawings:
        result["printed"].setdefault(role_of(drawing), hex_of(drawing["fill"]))
    return result


def the_current_marks():
    document = pymupdf.open(SOURCE_2016)
    variations, symbols = document[0], document[1]

    # The four variations sit in a two-by-two grid; the colour logo is top left.
    colour = [d for d in filled(variations) if inside(d["rect"], (300, 160, 500, 230))]
    black = [d for d in filled(variations) if inside(d["rect"], (540, 160, 740, 230))]
    reverse = [d for d in filled(variations) if inside(d["rect"], (300, 330, 500, 400))]
    untagged = [d for d in filled(variations) if inside(d["rect"], (540, 330, 740, 400))]
    if len(colour) != 19:
        raise SystemExit(f"expected the colour logo’s 19 shapes — two halves, “BC Hydro”, “Power smart”, found {len(colour)}")
    if signature(black) != signature(colour) or signature(reverse) != signature(colour):
        raise SystemExit("the black or reverse logo is not the colour logo's drawing")
    if signature(untagged) != signature(colour)[:9]:
        raise SystemExit("the logo without its tagline is not the colour logo less the tagline")

    # By where a letter's top sits, not its bottom: the y of Hydro descends past the symbol.
    symbol_bottom = max(d["rect"].y1 for d in colour if close(d["fill"], SEA))

    def logo_role(drawing):
        if close(drawing["fill"], GRASS):
            return "upper"
        if close(drawing["fill"], SEA):
            return "lower"
        return "wordmark" if drawing["rect"].y0 < symbol_bottom else "tagline"

    counts = [logo_role(d) for d in colour]
    if counts.count("wordmark") != 7 or counts.count("tagline") != 10:
        raise SystemExit("expected the seven letters of “BC Hydro” and the ten of “Power smart”")

    logo = mark(colour, logo_role, "artwork/hydro/brand-guidelines-2020-logo.pdf, page 1 (guidelines page 14)",
                "The colour logo with its tagline. The black, reverse and untagged versions are this drawing.")
    for drawing in colour:
        logo["printed"].setdefault(logo_role(drawing), hex_of(drawing["fill"]))

    def symbol_role(drawing):
        if close(drawing["fill"], WHITE):
            return "border"
        return "upper" if close(drawing["fill"], GRASS) else "lower"

    plain = [d for d in filled(symbols) if inside(d["rect"], (360, 160, 430, 220))]
    bordered = [d for d in filled(symbols) if inside(d["rect"], (590, 160, 670, 225))]
    if len(plain) != 2 or len(bordered) != 3:
        raise SystemExit(f"expected the symbol's two halves and a bordered copy; found {len(plain)} and {len(bordered)}")

    source = "artwork/hydro/brand-guidelines-2020-logo.pdf, page 2 (guidelines page 15)"
    symbol = mark(plain, symbol_role, source, "The symbol alone.")
    with_border = mark(bordered, symbol_role, source, "The symbol with its white border, for coloured or busy backgrounds.")
    for result, drawings in ((symbol, plain), (with_border, bordered)):
        for drawing in drawings:
            result["printed"].setdefault(symbol_role(drawing), hex_of(drawing["fill"]))

    return {"bc-hydro-2016": logo, "bc-hydro-2016-symbol": symbol, "bc-hydro-2016-symbol-border": with_border}


def main():
    marks = {"bc-hydro-1990": the_1990_mark(), **the_current_marks()}
    body = ",\n".join(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}" for key, value in marks.items())
    TARGET.write_text(
        "// Generated by scripts/extract_hydro_marks.py — do not edit.\n"
        "//\n"
        "// BC Hydro's 1990 and current marks, lifted from the supplied artwork unchanged. Coordinates are\n"
        "// the source's points, moved to the origin; each shape carries the part it plays, its box, and\n"
        "// its fill rule where that is even-odd.\n\n"
        f"export const HYDRO_MARKS = {{\n{body}\n}}\n"
    )
    for key, value in marks.items():
        roles = sorted({shape["role"] for shape in value["shapes"]})
        print(f"  {key:30} {len(value['shapes']):2} shapes  {value['width']} × {value['height']}  {', '.join(roles)}")


if __name__ == "__main__":
    main()
