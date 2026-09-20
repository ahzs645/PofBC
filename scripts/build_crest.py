"""Lifts the coat of arms and the BRITISH COLUMBIA wordmark out of a page extraction.

This identity — the crest with the wordmark, and a ministry set against it — came after the flag
one. Most files it survives in carry the arms as an embedded PNG, which is no use. One does not: it
holds the arms as vector and the wordmark as outlines rather than as text, so neither needs a font.

The source splits both across compound paths for reasons of its own — the wordmark arrives as "R",
then "ITISH OLUMBI", then "B C A" — so this works in contours and regroups them by where they sit.
What it must not do is emit each contour as its own path: a letter's counter is a contour wound
against its outline, and separating the two fills the hole in.

It is Python rather than Node because the source uses relative arcs, and this project's own path
reader does not implement them.

Run: npm run build:crest
"""

import os
import re
import sys
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(os.environ.get("CREST_SOURCE", ROOT / "artwork/crest/wordmark-source.svg"))


def contours(data):
    """A path as a list of contours, each a list of absolute drawing commands."""
    pen = RecordingPen()
    parse_path(data, pen)

    out, current = [], []
    for op, args in pen.value:
        if op == "moveTo" and current:
            out.append(current)
            current = []
        current.append((op, args))
    if current:
        out.append(current)
    return out


def bounds(contour):
    xs = [p[0] for _, args in contour for p in args if p]
    ys = [p[1] for _, args in contour for p in args if p]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def render(contour, dx, dy):
    """Absolute M/L/C/Q/Z, shifted. Curves keep their degree; nothing is flattened."""
    out = []
    for op, args in contour:
        points = [(round(x + dx, 3), round(y + dy, 3)) for x, y in args if x is not None]
        flat = " ".join(f"{x:g} {y:g}" for x, y in points)
        if op == "moveTo":
            out.append(f"M{flat}")
        elif op == "lineTo":
            out.append(f"L{flat}")
        elif op == "curveTo":
            out.append(f"C{flat}")
        elif op == "qCurveTo":
            out.append(f"Q{flat}")
        elif op == "closePath":
            out.append("Z")
    return "".join(out)


def main():
    if not SOURCE.exists():
        sys.exit(f"\nCould not find the crest artwork at {SOURCE}.\n"
                 "Point CREST_SOURCE at the SVG:\n\n"
                 "    CREST_SOURCE=/path/to/page.svg npm run build:crest\n")

    source = SOURCE.read_text()
    box = re.search(r'viewBox="([^"]+)"', source)
    page_w, page_h = (float(v) for v in box.group(1).split()[2:4])

    pieces = []
    for match in re.finditer(r'<path([^>]*?)\sd="([^"]+)"', source):
        attrs, d = match.groups()
        fill = re.search(r'fill="([^"]*)"', attrs)
        fill = fill.group(1) if fill else None
        if fill == "none":
            continue

        parts = contours(d)
        whole = [b for b in (bounds(c) for c in parts) if b]
        if not whole:
            continue
        # Judge the whole path, not its pieces. The page's clip shapes are as large as the page and
        # draw nothing, but their individual contours are small enough to pass one at a time.
        span_x = max(b[2] for b in whole) - min(b[0] for b in whole)
        span_y = max(b[3] for b in whole) - min(b[1] for b in whole)
        if span_x >= page_w or span_y >= page_h:
            continue

        for contour in parts:
            b = bounds(contour)
            if b:
                pieces.append({"contour": contour, "box": b, "fill": fill})

    if not pieces:
        sys.exit("\nNo artwork found in the source.\n")

    # Two clusters, split on the widest horizontal gap between them: the arms on the left, the
    # wordmark on the right. Found rather than written down, so a differently cropped page works.
    ordered = sorted(pieces, key=lambda p: p["box"][0])
    split, widest, reach = 0, 0, ordered[0]["box"][2]
    for piece in ordered[1:]:
        gap = piece["box"][0] - reach
        if gap > widest:
            widest, split = gap, piece["box"][0] - gap / 2
        reach = max(reach, piece["box"][2])

    def centre(piece):
        return (piece["box"][0] + piece["box"][2]) / 2

    groups = {
        "ARMS": [p for p in pieces if centre(p) < split],
        "WORDMARK": [p for p in pieces if centre(p) >= split],
    }

    out = {}
    for name, group in groups.items():
        x0 = min(p["box"][0] for p in group)
        y0 = min(p["box"][1] for p in group)
        x1 = max(p["box"][2] for p in group)
        y1 = max(p["box"][3] for p in group)

        # One path per fill, holding every contour that shares it — which is what keeps a letter's
        # counter with the letter it belongs to.
        by_fill = {}
        for piece in group:
            by_fill.setdefault(piece["fill"], []).append(render(piece["contour"], -x0, -y0))

        out[name] = {
            "width": round(x1 - x0, 3),
            "height": round(y1 - y0, 3),
            "contours": len(group),
            "shapes": [
                {**({"fill": fill} if fill else {}), "d": "".join(parts)}
                for fill, parts in by_fill.items()
            ],
        }

    import json
    body = "\n\n".join(
        f"export const {name} = " + json.dumps(
            {k: v for k, v in data.items() if k != "contours"}, indent=2)
        for name, data in out.items())

    (ROOT / "src/assets/crestMark.js").write_text(
        "// Generated by scripts/build_crest.py — do not edit.\n"
        "//\n"
        "// The Province's coat of arms and its BRITISH COLUMBIA wordmark, lifted from a page\n"
        "// extraction and moved onto their own ink boxes. The wordmark is outlines rather than\n"
        "// text, so it needs no font and cannot be set in the wrong one.\n"
        "//\n"
        "// Coordinates are the source page's points, each drawing starting at 0,0 and exactly as\n"
        "// large as what it draws.\n\n"
        + body + "\n")

    for name, data in out.items():
        size = len(json.dumps(data)) / 1024
        print(f"  {name.lower():10} {data['contours']:3} contours in {len(data['shapes'])} path(s)   "
              f"{data['width']} x {data['height']}   {size:.1f} KB")
    print(f"  split at x={split:.2f}, the widest gap between them ({widest:.2f} units)")
    print("  -> src/assets/crestMark.js")


if __name__ == "__main__":
    main()
