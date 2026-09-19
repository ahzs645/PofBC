"""Recovers the wording of the Province's ministry marks from their outlines.

The published marks carry their ministry name as vector outlines, not text, so
the wording cannot simply be read out. This identifies every glyph by matching
its outline against Adobe Garamond Pro — the serif the B.C. Visual Identity
Program specifies — and reassembles the line and word breaks from the glyph
positions.

Two things come out of it:

  * the wording of all 46 marks, English and French, which is what lets the
    generator typeset a name instead of storing a picture of one;
  * a measure of how exactly Garamond reproduces the published artwork, which is
    the evidence for being allowed to stop storing it.

Run: npm run recover:current-names
"""

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parent.parent
MARKS = ROOT / "public" / "current-marks"
# Stated, never guessed: see scripts/build-current-extras.mjs for why.
DEFAULT_FONT = os.environ.get("GARAMOND_SOURCE")

# Every character the marks can contain. The uppercase accents and the
# f-ligatures are not optional: Adobe Garamond substitutes ff/fi/fl
# automatically, so "Affairs" is drawn with four outlines, not six, and the
# French names carry É.
CHARSET = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    ",.'’-–"
    "éèêàâçôûîïüœ"
    "ÉÈÊÀÂÇÔÛÎÏŒ"
    "ﬀﬁﬂﬃﬄ"
)

LIGATURES = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
}

FLATNESS = 12
RES = 72

_gx, _gy = np.meshgrid(np.linspace(0, 1, RES), np.linspace(0, 1, RES))
GRID = np.column_stack([_gx.ravel(), _gy.ravel()])


def flatten(recording):
    """A pen recording as a list of polygons."""
    contours, current, start, cursor = [], [], None, None

    def bezier(p0, points):
        out = []
        for i in range(1, FLATNESS + 1):
            t = i / FLATNESS
            u = 1 - t
            if len(points) == 2:
                (x1, y1), (x2, y2) = points
                out.append((u * u * p0[0] + 2 * u * t * x1 + t * t * x2,
                            u * u * p0[1] + 2 * u * t * y1 + t * t * y2))
            else:
                (x1, y1), (x2, y2), (x3, y3) = points
                out.append((u ** 3 * p0[0] + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
                            u ** 3 * p0[1] + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3))
        return out

    for op, args in recording:
        if op == "moveTo":
            if current:
                contours.append(current)
            cursor = start = args[0]
            current = [cursor]
        elif op == "lineTo":
            cursor = args[0]
            current.append(cursor)
        elif op in ("curveTo", "qCurveTo"):
            points = list(args)
            if op == "qCurveTo" and points and points[-1] is None:
                points = points[:-1] + [start]
            if op == "qCurveTo" and len(points) > 2:
                for i in range(len(points) - 1):
                    control = points[i]
                    following = (points[i + 1] if i == len(points) - 2 else
                                 ((points[i][0] + points[i + 1][0]) / 2,
                                  (points[i][1] + points[i + 1][1]) / 2))
                    current.extend(bezier(cursor, [control, following]))
                    cursor = following
            else:
                current.extend(bezier(cursor, points))
                cursor = points[-1]
        elif op == "closePath":
            if current:
                contours.append(current)
                current = []
    if current:
        contours.append(current)
    return [c for c in contours if len(c) > 2]


def fill(contours):
    """Rasterise, normalised so the ink bounding box maps onto the unit square.

    Normalising away position and size is what makes a 5-point outline lifted
    from a PDF comparable with a 1000-unit glyph from the font file.
    """
    points = [p for c in contours for p in c]
    x0 = min(p[0] for p in points)
    x1 = max(p[0] for p in points)
    y0 = min(p[1] for p in points)
    y1 = max(p[1] for p in points)
    width, height = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    mask = np.zeros(GRID.shape[0], dtype=bool)
    for contour in contours:
        scaled = [((px - x0) / width, (py - y0) / height) for px, py in contour]
        mask ^= MplPath(np.asarray(scaled), closed=True).contains_points(GRID)
    return mask, width, height


def build_library(font_path):
    font = TTFont(font_path)
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    library = {}
    for character in CHARSET:
        name = cmap.get(ord(character))
        if not name:
            continue
        pen = RecordingPen()
        glyphs[name].draw(pen)
        contours = flatten(pen.value)
        if not contours:
            continue
        mask, width, height = fill(contours)
        library[character] = (mask, width, height)
    return font, library


def name_glyphs(svg):
    """Every glyph of the ministry name, as (x0, x1, y0, y1, contours)."""
    source = svg.read_text()
    group = re.search(
        r'<g transform="translate\(([-\d.]+) ([-\d.]+)\)">'
        r'((?:(?!</g>).)*?data-role="name".*?)</g>', source, re.S)
    if not group:
        return []
    tx, ty = float(group.group(1)), float(group.group(2))
    out = []
    for d in re.findall(r'\sd="([^"]+)"', group.group(3)):
        pen = RecordingPen()
        parse_path(d, pen)
        # SVG measures y downward and fonts measure it up from the baseline.
        contours = [[(x + tx, -(y + ty)) for x, y in c] for c in flatten(pen.value)]
        points = [p for c in contours for p in c]
        out.append((min(p[0] for p in points), max(p[0] for p in points),
                    min(p[1] for p in points), max(p[1] for p in points), contours))
    return out


def assign_lines(glyphs, leading):
    """Group glyphs into lines by snapping each one to a baseline grid.

    Clustering on a single extreme does not survive real wording: a comma's head
    sits barely above the baseline, so heads merge adjacent lines, while an
    apostrophe's foot floats near the ascender, so feet merge them the other way.
    Both behave once there is a grid to snap to — and the leading is a constant
    across all 46 marks, so a grid is available.

    Most letters are flat-bottomed and sit exactly on their baseline, so the feet
    pile up into tight clusters. The highest such cluster anchors the grid.
    """
    feet = sorted(glyph[2] for glyph in glyphs)
    clusters = []
    for foot in feet:
        if clusters and foot - clusters[-1][-1] < 0.2:
            clusters[-1].append(foot)
        else:
            clusters.append([foot])
    anchored = [sum(c) / len(c) for c in clusters if len(c) >= 2] or \
               [sum(c) / len(c) for c in clusters]
    top = max(anchored)

    rows = {}
    for glyph in glyphs:
        rows.setdefault(round((top - glyph[2]) / leading), []).append(glyph)
    return [rows[key] for key in sorted(rows)]


def recover(svg, library, leading):
    """The mark's wording, plus the worst glyph disagreement seen recovering it."""
    glyphs = name_glyphs(svg)
    if not glyphs:
        return None

    lines = assign_lines(glyphs, leading)

    worst, scales, text_lines = 0.0, [], []
    for line in lines:
        line = sorted(line, key=lambda g: g[0])
        pieces, previous_right = [], None
        for x0, x1, y0, y1, contours in line:
            mask, width, height = fill(contours)
            error, character, glyph_height = min(
                ((np.count_nonzero(mask ^ other) / max(np.count_nonzero(mask | other), 1), ch, h)
                 for ch, (other, _, h) in library.items()),
                key=lambda t: t[0])
            worst = max(worst, error)
            scales.append(height / glyph_height)
            # A word break is a gap far wider than the letter-fitting inside one.
            if previous_right is not None and x0 - previous_right > 0.9:
                pieces.append(" ")
            pieces.append(LIGATURES.get(character, character))
            previous_right = x1
        text_lines.append("".join(pieces))

    return dict(lines=text_lines, worst=worst,
                scale=float(np.median(scales)), scale_sd=float(np.std(scales)))


def main():
    font_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_FONT or '')
    if not DEFAULT_FONT and len(sys.argv) <= 1 or not font_path.exists():
        sys.exit(
            f"\nCould not find Adobe Garamond Pro at {font_path}.\n"
            "The B.C. Visual Identity Program specifies it for the ministry marks. Point this\n"
            "script at a licensed copy:\n\n"
            "    npm run recover:current-names -- /path/to/AGaramondPro-Regular.otf\n")

    font, library = build_library(font_path)
    print(f"matching against {font['name'].getDebugName(4)}, {len(library)} glyphs\n")

    index = json.loads((MARKS / "index.json").read_text())
    english = {m["code"].lower(): m["name"] for m in index["ministries"]}

    leading = 8.10  # measured across all 46 marks
    results, worst_overall, mismatched = {}, 0.0, []

    for ministry in index["ministries"]:
        code = ministry["code"].lower()
        for language in ("en", "fr"):
            svg = MARKS / f"{code}-{language}.svg"
            if not svg.exists():
                continue
            found = recover(svg, library, leading)
            if not found:
                continue
            worst_overall = max(worst_overall, found["worst"])
            text = " ".join(found["lines"])
            results[f"{code}-{language}"] = found

            # The stored English name is known independently, so it is a free
            # check on the whole method — and on the extraction that produced
            # these files in the first place.
            if language == "en":
                expected = f"Ministry of {english[code]}"
                if text != expected:
                    mismatched.append((f"{code}-en", expected, text))

            flag = " " if found["worst"] < 0.10 else "!"
            print(f"{flag} {code}-{language:2}  {text}")

    print(f"\nworst single-glyph disagreement across all marks: {100 * worst_overall:.1f}%")
    scales = [r["scale"] for r in results.values()]
    print(f"type size: median {1000 * float(np.median(scales)):.2f} pt, "
          f"range {1000 * min(scales):.2f}..{1000 * max(scales):.2f} pt")

    if mismatched:
        print(f"\n{len(mismatched)} mark(s) whose artwork does not match the catalogue:")
        for code, expected, found in mismatched:
            print(f"  {code}\n      catalogue: {expected}\n      artwork  : {found}")

    out = ROOT / "scripts" / "current-names.json"
    out.write_text(json.dumps(
        {k: {"lines": v["lines"], "size": round(1000 * v["scale"], 3)}
         for k, v in sorted(results.items())}, ensure_ascii=False, indent=2) + "\n")
    print(f"\n→ {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
