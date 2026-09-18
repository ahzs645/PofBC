"""Extracts the current BC ministry marks from the official guideline PDF.

The Province publishes its ministry marks as a PDF of finished artwork, and says plainly that they
must be used exactly as provided rather than recreated. So this does not reconstruct them: it lifts
the drawn vectors out, unchanged, and packages them for the app to serve.

Every mark is built the same way — the BC mark (sun, mountains, wordmark), a hairline gold rule,
then the ministry name. The BC mark is identical across all of them, so it is stored once per
language exactly as the crest is; a ministry contributes only its own name.

The ministry names are outlines, not text. That is what makes this approach work at all: the serif
they are set in is not one we have, and we never need it.

Run: npm run build:current-marks
"""

import json
import re
import pathlib
import sys

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "artwork/current/ministry-marks.pdf"
TARGET = ROOT / "public/current-marks"

# The gold rule that separates the mark from the name. Finding it is how each lockup is split.
GOLD = (0.99, 0.72, 0.07)
COLOUR_TOLERANCE = 0.08

# Coordinates are rounded to this many decimals. The artwork is ~40pt wide, so a hundredth of a
# point is already far finer than anything these are reproduced at.
PRECISION = 2


def close(a, b, tolerance=COLOUR_TOLERANCE):
    return all(abs(x - y) <= tolerance for x, y in zip(a, b))


def is_rule(drawing):
    """A thin, tall, gold shape: the divider."""
    rect = drawing["rect"]
    fill = drawing.get("fill")
    return bool(fill) and close(fill, GOLD) and rect.height > rect.width * 5


def fmt(value):
    text = f"{round(value, PRECISION):.{PRECISION}f}".rstrip("0").rstrip(".")
    return text if text not in ("-0", "") else "0"


def path_data(drawing, origin):
    """PyMuPDF's drawing items as SVG path data, moved to `origin`."""
    ox, oy = origin
    out = []
    current = None

    def point(p):
        return f"{fmt(p.x - ox)} {fmt(p.y - oy)}"

    for item in drawing["items"]:
        kind = item[0]

        if kind == "l":
            start, end = item[1], item[2]
            if current != start:
                out.append(f"M{point(start)}")
            out.append(f"L{point(end)}")
            current = end
        elif kind == "c":
            start, c1, c2, end = item[1], item[2], item[3], item[4]
            if current != start:
                out.append(f"M{point(start)}")
            out.append(f"C{point(c1)} {point(c2)} {point(end)}")
            current = end
        elif kind == "re":
            rect = item[1]
            out.append(
                f"M{fmt(rect.x0 - ox)} {fmt(rect.y0 - oy)}"
                f"H{fmt(rect.x1 - ox)}V{fmt(rect.y1 - oy)}H{fmt(rect.x0 - ox)}Z"
            )
            current = None
        elif kind == "qu":
            quad = item[1]
            corners = [quad.ul, quad.ur, quad.lr, quad.ll]
            out.append("M" + point(corners[0]) + "".join("L" + point(c) for c in corners[1:]) + "Z")
            current = None
        else:
            raise SystemExit(f"Unhandled drawing item {kind!r} — the PDF uses something new.")

    if drawing.get("closePath"):
        out.append("Z")

    return "".join(out)


def hex_of(fill):
    return "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in fill)


NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def shape_key(shape, scale=1.0):
    """A position-and-size signature for a shape, used to pair shapes up between lockups.

    The PDF does not draw the sub-paths of the mark in a consistent order from row to row, so two
    copies of the same artwork cannot be compared index by index. Pairing them by where each one
    sits sidesteps that entirely.
    """
    values = [float(v) for v in NUMBER.findall(shape["d"])]
    xs = [v * scale for v in values[0::2]]
    ys = [v * scale for v in values[1::2]]
    return (
        shape["fill"],
        bool(shape.get("evenOdd")),
        len(values),
        round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1),
    )


def same_shapes(a, b, scale=1.0, tolerance=0.02):
    """Whether two shape lists are the same drawing, allowing for a difference in size.

    Compared numerically rather than as text, because the PDF places each lockup at its own spot on
    the page and the same artwork rounds differently from one to the next. `scale` additionally
    allows for the handful of rows the source draws fractionally larger — the same drawing at a
    different size is still the same drawing.
    """
    if len(a) != len(b):
        return False

    left_sorted = sorted(a, key=lambda shape: shape_key(shape, scale))
    right_sorted = sorted(b, key=shape_key)

    for one, two in zip(left_sorted, right_sorted):
        if one["fill"] != two["fill"] or bool(one.get("evenOdd")) != bool(two.get("evenOdd")):
            return False
        left = [float(v) for v in NUMBER.findall(one["d"])]
        right = [float(v) for v in NUMBER.findall(two["d"])]
        if len(left) != len(right):
            return False
        if any(abs(x * scale - y) > tolerance for x, y in zip(left, right)):
            return False

    return True


def shapes(drawings, origin):
    """Drawings as `{d, fill, evenOdd}`, in source order so overlaps still stack correctly."""
    out = []
    for drawing in drawings:
        fill = drawing.get("fill")
        if not fill:
            continue
        out.append(
            {
                "d": path_data(drawing, origin),
                "fill": hex_of(fill),
                **({"evenOdd": True} if drawing.get("even_odd") else {}),
            }
        )
    return out


def shape_markup(shape):
    rule = ' fill-rule="evenodd"' if shape.get("evenOdd") else ""
    return f'<path fill="{shape["fill"]}"{rule} d="{shape["d"]}"/>'


def bounds(drawings):
    rect = pymupdf.Rect(drawings[0]["rect"])
    for drawing in drawings[1:]:
        rect |= drawing["rect"]
    return rect


def lockups_on(page):
    """Every mark on a page, as `(rule, mark_drawings, name_drawings)` left to right."""
    drawings = [d for d in page.get_drawings() if d.get("fill")]

    # The source draws one row's rule twice, in the same place. Deduplicating by position keeps
    # that row from being extracted as two separate ministries.
    seen = set()
    rules = []
    for drawing in sorted((d for d in drawings if is_rule(d)), key=lambda d: (round(d["rect"].y0), d["rect"].x0)):
        key = (round(drawing["rect"].x0, 1), round(drawing["rect"].y0, 1))
        if key in seen:
            continue
        seen.add(key)
        rules.append(drawing)

    found = []
    for index, rule in enumerate(rules):
        band = rule["rect"]

        # Each row carries two lockups, English then French, so a name runs from its own rule up to
        # wherever the next lockup on that row begins — not simply "everything to the right", which
        # would swallow the neighbour, and not a fixed width, which would cut a long name short.
        following = next(
            (
                other["rect"].x0
                for other in rules[index + 1 :]
                if abs(other["rect"].y0 - band.y0) < 6 and other["rect"].x0 > band.x1
            ),
            page.rect.x1,
        )
        # The next lockup's own mark sits to the left of its rule; stop short of that too.
        right_limit = following - 60 if following < page.rect.x1 else page.rect.x1

        # A row's vertical band is the rule's, widened enough for accents and descenders, which
        # reach past it in the French names.
        row = [
            d
            for d in drawings
            if not is_rule(d)
            and d["rect"].y0 >= band.y0 - 6
            and d["rect"].y1 <= band.y1 + 6
            and d["rect"].width < 300
        ]

        mark = [d for d in row if d["rect"].x1 <= band.x0 + 0.5]
        name = [d for d in row if band.x1 - 0.5 <= d["rect"].x0 and d["rect"].x1 <= right_limit]

        # The mark sits immediately left of its own rule; anything further left is the neighbour's.
        if mark:
            cutoff = max(d["rect"].x1 for d in mark) - 60
            mark = [d for d in mark if d["rect"].x0 >= cutoff]

        if mark and name:
            found.append((rule, mark, name))

    return found


def row_labels(page):
    """The ministry names printed down the left of the table, with the y band of each."""
    labels = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            x0, y0, x1, y1 = line["bbox"]
            if text and x0 < 200 and line["spans"][0]["font"].endswith("SemiCnIt"):
                labels.append({"text": text, "y0": y0, "y1": y1})
    return labels


def label_for(rule, labels):
    """The table label whose lines sit alongside a given lockup."""
    band = rule["rect"]
    near = [entry for entry in labels if entry["y0"] > band.y0 - 24 and entry["y1"] < band.y1 + 24]
    # A ministry name wraps over several lines, and the last is the abbreviation in brackets.
    parts = [entry["text"] for entry in near if not entry["text"].startswith("(")]
    code = next((entry["text"].strip("()") for entry in near if entry["text"].startswith("(")), None)
    return " ".join(parts).strip(), code


def main():
    if not SOURCE.exists():
        sys.exit(
            f"Missing {SOURCE.relative_to(ROOT)}.\n"
            "The current-era marks are extracted from the Province's published ministry-marks PDF.\n"
            "Place it there and run this again."
        )

    document = pymupdf.open(SOURCE)
    marks = {}
    shared = {}

    for page in document:
        labels = row_labels(page)
        for rule, mark_drawings, name_drawings in lockups_on(page):
            name_text, code = label_for(rule, labels)
            if not code:
                continue

            # English is the left-hand column, French the right.
            language = "en" if rule["rect"].x0 < page.rect.width / 2 else "fr"

            lockup = bounds(mark_drawings) | bounds(name_drawings) | rule["rect"]
            mark_box = bounds(mark_drawings)
            name_box = bounds(name_drawings)

            # Each piece is normalised to its own box rather than the lockup's. The lockup's box
            # depends on how many lines the ministry name runs to, so measuring the mark against it
            # would make the same artwork come out different for every ministry.
            mark_shapes = shapes(mark_drawings, (mark_box.x0, mark_box.y0))

            # Nearly every lockup embeds the same drawing, so it is stored once and referenced.
            # A couple of rows in the source carry a different vector export of the same logo —
            # different point counts, not merely a different size — so those are kept as their own
            # variant rather than being forced to match or quietly normalised away.
            mark_width = round(mark_box.x1 - mark_box.x0, PRECISION)
            variants = shared.setdefault(language, [])

            # Matched by tolerance rather than by exact equality: the same artwork rounds
            # differently at each position on the page, and a few rows are drawn fractionally
            # larger, so `scale` lets those pair up with the drawing they are a copy of.
            variant = next(
                (
                    candidate
                    for candidate in variants
                    if same_shapes(candidate["shapes"], mark_shapes, mark_width / candidate["width"])
                ),
                None,
            )

            if variant is None:
                variant = {
                    "id": f"{language}{len(variants) + 1}",
                    "shapes": mark_shapes,
                    "width": mark_width,
                    "height": round(mark_box.y1 - mark_box.y0, PRECISION),
                    "used": 0,
                }
                variants.append(variant)

            variant["used"] += 1

            origin = (lockup.x0, lockup.y0)
            entry = marks.setdefault(code, {"code": code, "name": name_text})
            entry[language] = {
                # Where each piece sits inside the lockup, so the shared mark can be placed without
                # the caller having to know anything about how the artwork was drawn.
                "mark": {
                    "id": variant["id"],
                    "x": round(mark_box.x0 - origin[0], PRECISION),
                    "y": round(mark_box.y0 - origin[1], PRECISION),
                    # Drawn at the variant's own size unless this row uses it larger.
                    **(
                        {"scale": round(mark_width / variant["width"], 4)}
                        if abs(mark_width - variant["width"]) > 0.01
                        else {}
                    ),
                },
                "name": {
                    "x": round(name_box.x0 - origin[0], PRECISION),
                    "y": round(name_box.y0 - origin[1], PRECISION),
                    "shapes": shapes(name_drawings, (name_box.x0, name_box.y0)),
                },
                "rule": {
                    "x": round(rule["rect"].x0 - origin[0], PRECISION),
                    "y": round(rule["rect"].y0 - origin[1], PRECISION),
                    "width": round(rule["rect"].width, PRECISION),
                    "height": round(rule["rect"].height, PRECISION),
                    "fill": hex_of(rule["fill"]),
                },
                "width": round(lockup.x1 - lockup.x0, PRECISION),
                "height": round(lockup.y1 - lockup.y0, PRECISION),
            }

    complete = {code: entry for code, entry in marks.items() if "en" in entry and "fr" in entry}
    if len(complete) != len(marks):
        missing = sorted(set(marks) - set(complete))
        print(f"  warning: no French counterpart for {', '.join(missing)}", file=sys.stderr)

    ordered = sorted(complete.values(), key=lambda entry: entry["name"])

    # Flatten the variant tables, most-used first, and drop the signatures used to group them.
    marks = {}
    for language, variants in shared.items():
        for variant in sorted(variants, key=lambda v: -v["used"]):
            marks[variant["id"]] = {
                "language": language,
                "width": variant["width"],
                "height": variant["height"],
                "shapes": variant["shapes"],
            }

    TARGET.mkdir(parents=True, exist_ok=True)
    for existing in TARGET.glob("*.svg"):
        existing.unlink()

    def render(entry, language):
        """One ministry mark as a complete, standalone SVG."""
        lockup = entry[language]
        variant = marks[lockup["mark"]["id"]]
        placement = lockup["mark"]
        scale = placement.get("scale", 1)

        mark_transform = f'translate({placement["x"]} {placement["y"]})'
        if scale != 1:
            mark_transform += f" scale({scale})"

        rule = lockup["rule"]
        parts = [
            f'<g transform="{mark_transform}">',
            *(shape_markup(shape) for shape in variant["shapes"]),
            "</g>",
            f'<rect x="{rule["x"]}" y="{rule["y"]}" width="{rule["width"]}" '
            f'height="{rule["height"]}" fill="{rule["fill"]}"/>',
            f'<g transform="translate({lockup["name"]["x"]} {lockup["name"]["y"]})">',
            *(shape_markup(shape) for shape in lockup["name"]["shapes"]),
            "</g>",
        ]

        title = f'{entry["name"]} — {"English" if language == "en" else "French"}'
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {lockup["width"]} {lockup["height"]}">'
            f"<title>{title}</title>" + "".join(parts) + "</svg>"
        )

    catalogue = []
    total = 0
    for entry in ordered:
        languages = {}
        for language in ("en", "fr"):
            svg = render(entry, language)
            name = f'{entry["code"].lower()}-{language}.svg'
            (TARGET / name).write_text(svg)
            total += len(svg)
            languages[language] = {
                "file": name,
                "width": entry[language]["width"],
                "height": entry[language]["height"],
                "bytes": len(svg),
            }
        catalogue.append({"code": entry["code"], "name": entry["name"], **languages})

    index = {
        "source": "The Province of British Columbia's published ministry marks.",
        "note": (
            "Official artwork, lifted from the published PDF unchanged. The guidelines require "
            "these be used exactly as provided rather than recreated, so the ministry names are "
            "the original outlines and nothing here is typeset."
        ),
        "units": "PDF points",
        "colours": {
            "mark": "#053673",
            "sun": "#fdb913",
            "rule": "#fdb913",
            "note": (
                "As drawn in the print artwork. The Province's colour-accessibility guidance "
                "specifies #234075 and #e3a82b for screen; the generator recolours to those."
            ),
        },
        "ministries": catalogue,
    }
    (TARGET / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    print(
        f"  current marks     {len(ordered)} ministries x 2 languages, {len(ordered) * 2} SVG files, "
        f"BC mark {', '.join(f'{lang}: {len(v)}' for lang, v in sorted(shared.items()))} variants"
    )
    print(f"  → {TARGET.relative_to(ROOT)}/ ({total / 1024:.0f} KB total, {total / (len(ordered) * 2) / 1024:.0f} KB each)")


if __name__ == "__main__":
    main()
