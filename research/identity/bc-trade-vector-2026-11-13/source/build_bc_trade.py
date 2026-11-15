#!/usr/bin/env python3
"""Author a BC Trade reconstruction from deliberately drawn vector components.

The reference pixels are not traced or converted into contours. Geometry is
defined here as compact, editable curves; the original scan supplies landmarks.
"""
from pathlib import Path
import copy
from functools import lru_cache
import json
import math
import re
import subprocess
import xml.etree.ElementTree as ET
from svgpathtools import CubicBezier, Path as BezierPath, parse_path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "bc-trade"
OUT.mkdir(parents=True, exist_ok=True)
SVG = "http://www.w3.org/2000/svg"
INK = "http://www.inkscape.org/namespaces/inkscape"
ET.register_namespace("", SVG)
ET.register_namespace("inkscape", INK)

PALETTES = {
    "colour": {"red": "#B22C20", "blue": "#17447F", "gold": "#EDC445", "white": "#FFFFFF", "black": "#111111"},
    "scan-tones": {"red": "#B3614E", "blue": "#46698A", "gold": "#DDC679", "white": "#FFFFFF", "black": "#242A28"},
}

MAPLE = """M 446,52
 L 465,151 C 468,165 473,172 483,170
 C 501,166 534,152 559,145
 L 478,288 C 468,306 461,329 469,335
 C 477,342 490,334 502,324
 L 609,247 L 601,309 L 722,288
 L 663,370 C 659,375 657,379 662,381
 L 704,391 L 680,409 L 664,420
 L 644,523 L 161,546 L 142,440
 L 75,390 L 118,383 C 122,382 123,377 121,372
 L 86,276 L 199,309 C 205,311 209,307 210,297
 L 217,238 L 306,325
 C 316,335 325,340 332,335 C 340,331 338,315 335,300
 L 296,145 L 344,166 C 357,173 363,171 371,161 Z"""

FLAG = """M 142,440
 C 179,433 220,421 247,425
 C 282,428 301,445 296,482
 C 295,489 295,493 301,489
 C 351,459 405,414 449,410
 C 483,404 512,414 521,435
 C 525,445 526,451 525,458
 C 524,464 524,467 530,464
 C 579,438 629,423 677,419
 L 632.5,718.5 Q 632,722 628.5,722
 L 81.5,722 Q 78,722 78.6,718.5 L 120,485 Z"""

BLUE_FIELD = """M 116,480
 C 165,459 217,438 248,445
 C 276,451 261,492 264,515
 C 268,541 301,516 326,496
 C 374,463 413,440 447,434
 C 478,427 501,437 496,459
 C 492,479 481,497 493,503
 C 507,510 536,490 576,477
 C 608,457 641,446 671,439
 L 633,738 L 71,738 Z"""

# Broad white channels and coloured interiors are separate closed paths.
LEFT_UPPER_WHITE = """M 105,497
 C 166,492 221,514 246,551
 C 264,581 264,605 258,628
 C 246,602 226,580 190,569
 C 161,559 128,557 97,564 Z"""
LEFT_UPPER_RED = """M 103,516
 C 159,507 214,529 239,558
 C 248,571 253,584 251,595
 C 250,601 249,602 246,597
 C 234,580 214,566 184,559
 C 156,551 127,551 99,555 Z"""

# The lower white channels are intentionally wider above the red than below it.
# A uniform stroked inset made the blue wedges too deep in the first version.
LEFT_LOWER_WHITE = """M 88,615
 C 133,595 182,584 218,586
 C 246,588 263,604 263,628
 C 261,653 256,675 257,697
 C 246,695 240,687 233,681
 C 221,671 206,672 194,675
 C 151,679 111,692 75,707 Z"""
LEFT_LOWER = """M 89,641
 C 132,619 178,605 212,605
 C 235,605 254,611 251,628
 C 249,645 245,666 244,680
 C 232,668 215,661 194,663
 C 155,666 119,678 84,690 Z"""

CENTRE_WHITE = """M 328,490
 C 356,466 400,442 431,430
 L 407,610 L 317,613 Z"""
CENTRE_RED = """M 344,488
 C 365,470 390,455 413,446
 L 391,610 L 330,610 Z"""

DIAGONAL_WHITE = """M 454,598
 C 515,540 565,446 677,432
 L 670,481 C 649,493 618,523 589,552
 C 559,588 537,612 506,630 C 492,639 475,635 470,628
 C 462,621 450,605 454,598 Z"""
DIAGONAL_RED = """M 470,604
 C 522,542 586,459 667,445
 C 672,444 674,443 673,448
 L 672,454 C 645,470 616,496 591,522
 L 505,602 C 491,611 480,614 470,604 Z"""

RIGHT_LOWER_WHITE = """M 470,644
 C 523,611 591,581 658,565
 L 650,661 C 590,677 532,703 490,721
 C 459,735 455,713 462,682
 C 464,661 465,650 470,644 Z"""
RIGHT_LOWER = """M 479,667
 C 529,639 590,613 653,596
 L 645,652 C 585,668 529,693 489,709
 C 471,717 468,711 472,691
 C 475,673 474,671 479,667 Z"""

SUN = """M 234,738
 C 239,719 238,703 238,688
 C 238,674 242,661 242,648
 C 255,652 263,657 267,646
 L 272,602 C 279,609 288,620 294,608
 L 318,566 C 326,582 334,591 342,575
 L 368,544 C 370,541 372,541 374,546
 L 386,559 C 393,575 401,562 412,550
 C 416,544 419,544 422,552
 L 433,572 C 440,587 447,577 455,571
 L 468,564 C 474,560 473,570 471,582
 L 470,614 C 468,623 484,626 492,620
 L 472,660 C 461,647 451,650 437,654
 C 394,665 331,693 279,728 L 264,738 Z"""

def clean_path(s):
    # All displayed coordinates are deliberate control points, not sampled edges.
    return re.sub(r"\s+", " ", s).strip()

def el(tag, attrs=None, parent=None):
    e = ET.Element(f"{{{SVG}}}{tag}", attrs or {})
    if parent is not None:
        parent.append(e)
    return e

def layer(root, name, label):
    return el("g", {"id":name, f"{{{INK}}}groupmode":"layer", f"{{{INK}}}label":label}, root)

def path(parent, name, d, colour, **attrs):
    return el("path", {"id":name, "d":clean_path(d), "fill":colour, **attrs}, parent)


# These small, named regions contain accidental acute joins in the flag's blue
# areas. They do not include maple tips, sun rays, or the straight lower edge.
# Distances are along the authored vector curves (four units per source pixel).
BLUE_CAPS = [
    ("upper-blue-terminal", (530, 455, 610, 495), 10),
    ("blue-terminal-beside-sun", (463, 550, 493, 604), 6),
    ("right-blue-terminal", (520, 582, 565, 625), 10),
    ("left-blue-terminal", (206, 570, 242, 609), 6),
]
CAP_REVIEW = []


def round_selected_joins(d, regions):
    """Replace selected acute vector joins with tangent-aligned cubic caps.

    This acts on the authored/Boolean vector, never on reference pixels. Only
    joins inside the named regions and below 65 degrees are eligible. The cap
    shares the actual endpoint tangent of each retained neighbouring curve.
    """
    output = []
    for subpath in parse_path(d).continuous_subpaths():
        starts, ends = [0.0] * len(subpath), [1.0] * len(subpath)
        selected = {}
        for i, previous in enumerate(subpath):
            following = subpath[(i + 1) % len(subpath)]
            vertex = previous.end
            if abs(vertex - following.start) > 1e-6:
                continue
            into, away = previous.derivative(1), following.derivative(0)
            if abs(into) < 1e-8 or abs(away) < 1e-8:
                continue
            dot = ((-into).real * away.real + (-into).imag * away.imag) / abs(into) / abs(away)
            angle = math.degrees(math.acos(max(-1, min(1, dot))))
            if angle >= 65:
                continue
            for name, (left, top, right, bottom), amount in regions:
                if not (left < vertex.real < right and top < vertex.imag < bottom):
                    continue
                before_length, after_length = previous.length(), following.length()
                distance = min(amount, before_length * .8, after_length * .8)
                if distance < 1:
                    continue
                ends[i] = previous.ilength(before_length - distance)
                starts[(i + 1) % len(subpath)] = following.ilength(distance)
                selected[i] = (name, vertex, angle, distance)
                break
        trimmed = []
        for i, segment in enumerate(subpath):
            if starts[i] == 0 and ends[i] == 1:
                trimmed.append(segment)
                continue
            piece = segment.cropped(starts[i], ends[i])
            # Preserve exact shared endpoints. Round-off from de Casteljau
            # subdivision must not serialize as a new SVG M / closed triangle.
            if starts[i] == 0:
                piece.start = segment.start
            if ends[i] == 1:
                piece.end = segment.end
            trimmed.append(piece)
        parts = []
        for i, segment in enumerate(trimmed):
            parts.append(segment)
            if i not in selected:
                continue
            next_segment = trimmed[(i + 1) % len(trimmed)]
            start, end = segment.end, next_segment.start
            tangent_in, tangent_out = segment.unit_tangent(1), next_segment.unit_tangent(0)
            dot = tangent_in.real * tangent_out.real + tangent_in.imag * tangent_out.imag
            turn = math.acos(max(-1, min(1, dot)))
            radius = abs(end - start) / max(2 * math.sin(turn / 2), 1e-8)
            handle = 4 / 3 * math.tan(turn / 4) * radius
            cap = CubicBezier(start, start + tangent_in * handle,
                              end - tangent_out * handle, end)
            parts.append(cap)
            name, vertex, angle, distance = selected[i]
            CAP_REVIEW.append({"id": name, "joinBeforeCap": [round(vertex.real, 3), round(vertex.imag, 3)],
                               "internalAngleBeforeCapDegrees": round(angle, 2),
                               "trimDistance": round(distance, 3),
                               "capStart": [round(start.real, 3), round(start.imag, 3)],
                               "capEnd": [round(end.real, 3), round(end.imag, 3)],
                               "tangentAligned": True})
        contour = BezierPath(*parts)
        if not contour.iscontinuous() or not contour.isclosed():
            raise ValueError("A flag corner cap disconnected its closed contour")
        output.append(contour.d() + " Z")
    return " ".join(output)

@lru_cache(maxsize=1)
def paint_geometry():
    """Resolve vector overlaps so PDF clipping cannot create coloured hairlines.

    These are Boolean operations on the authored Beziers, never on image pixels.
    White channels are cut from underlying colours; strokes become filled paths.
    All source control points above remain simple and individually editable.
    """
    CAP_REVIEW.clear()
    temp = ROOT / "tmp" / "vector-build"
    temp.mkdir(parents=True, exist_ok=True)
    head = '<svg xmlns="http://www.w3.org/2000/svg" width="784" height="872" viewBox="0 0 784 872">'

    def shape(d, fill="white", width=None):
        attrs = f' stroke="white" stroke-width="{width}" stroke-linejoin="round"' if width else ""
        return f'<path fill="{fill}"{attrs} d="{clean_path(d)}"/>'

    def operation(body, name, actions):
        src, dest = temp / (name + "-input.svg"), temp / (name + ".svg")
        src.write_text(head + body + "</svg>")
        result = subprocess.run([
            "inkscape", str(src), "--batch-process", "--actions=" + actions +
            ";export-type:svg;export-plain-svg;export-filename:" + str(dest) + ";export-do"
        ], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)
        paths = ET.parse(dest).getroot().findall(f".//{{{SVG}}}path")
        if len(paths) != 1 or paths[0].get("transform"):
            raise ValueError(f"Unexpected Boolean geometry for {name}")
        return paths[0].get("d")

    expand = "select-all;object-stroke-to-path;select-all;selection-ungroup;select-all;"
    cutouts = "".join(shape(d) for d in (LEFT_UPPER_WHITE, LEFT_LOWER_WHITE,
                                      CENTRE_WHITE, DIAGONAL_WHITE, RIGHT_LOWER_WHITE))
    cutouts += shape(SUN, width=6)
    white = operation(cutouts, "white-channels", expand + "path-union")
    result = {"blue":operation(shape(BLUE_FIELD, "blue") + shape(white), "blue-field", "select-all;path-difference")}
    result["blue"] = round_selected_joins(result["blue"], BLUE_CAPS)
    if sorted(item["id"] for item in CAP_REVIEW) != sorted(item[0] for item in BLUE_CAPS):
        raise ValueError("Expected one tangent cap in each named blue-tip region")
    result["left-lower"] = clean_path(LEFT_LOWER)
    result["right-lower"] = clean_path(RIGHT_LOWER)
    result["sun"] = operation(shape(SUN,"gold",6), "sun-inset", expand + "path-difference")
    sun_extent = operation(shape(SUN, width=6), "sun-white-extent", expand + "path-union")
    for name,d in (("left-upper",LEFT_UPPER_RED),("left-lower",result["left-lower"]),
                   ("centre",CENTRE_RED),("diagonal",DIAGONAL_RED),("right-lower",result["right-lower"])):
        result[name] = operation(shape(d,"red")+shape(sun_extent), name+"-sun-clearance", "select-all;path-difference")
    return result

def build(palette_name="colour", symbol_only=False):
    p = PALETTES[palette_name]
    geo = paint_geometry()
    root = el("svg", {"version":"1.1", "width":"784", "height":"872", "viewBox":"0 0 784 872", "role":"img", "aria-labelledby":"title description"})
    el("title", parent=root).text = "BC TRADE — reconstructed vector artwork"
    el("desc", {"id":"description"}, root).text = (
        "Manual reconstruction from the 1991 printed colour scan, checked against the 1989 newspaper example. "
        "Separate maple leaf, waving flag, five red flag bands, rising sun, and outlined lettering. "
        "Original scan controls geometry; colours are approximate. "
        "TRADE retains the open letter separations visible in both printed examples. No automatic tracing or embedded raster."
    )
    root.find(f"{{{SVG}}}title").set("id", "title")
    defs = el("defs", parent=root)
    clip = el("clipPath", {"id":"flag-boundary", "clipPathUnits":"userSpaceOnUse"}, defs)
    path(clip, "flag-boundary-path", FLAG, p["white"])

    g = layer(root, "maple-leaf", "01 · Maple leaf")
    path(g, "maple-canopy", MAPLE, p["red"])
    g = layer(root, "flag", "02 · Waving flag")
    path(g, "white-flag-field", FLAG, p["white"])
    clipped = el("g", {"id":"flag-colour-shapes", "clip-path":"url(#flag-boundary)"}, g)
    path(clipped, "blue-flag-field", geo["blue"], p["blue"])
    bands = el("g", {"id":"flag-red-bands"}, clipped)
    path(bands, "upper-left-white-channel", LEFT_UPPER_WHITE, p["white"])
    path(bands, "upper-left-red-wave", geo["left-upper"], p["red"])
    path(bands, "lower-left-red-wave", geo["left-lower"], p["red"])
    path(bands, "central-white-channel", CENTRE_WHITE, p["white"])
    path(bands, "central-red-stripe", geo["centre"], p["red"])
    path(bands, "diagonal-white-channel", DIAGONAL_WHITE, p["white"])
    path(bands, "diagonal-red-stripe", geo["diagonal"], p["red"])
    path(bands, "lower-right-red-wave", geo["right-lower"], p["red"])
    sun = el("g", {"id":"sun-and-rays"}, clipped)
    path(sun, "gold-rising-sun", geo["sun"], p["gold"])
    if not symbol_only:
        g = layer(root, "wordmark", "03 · BC TRADE outlined lettering")
        letters = ET.parse(ROOT / "typography-review" / "wordmark.svg").getroot().find(f"{{{SVG}}}g")
        g.set("transform", letters.get("transform"))
        g.set("fill-rule", "evenodd")
        for group in letters.findall(f"{{{SVG}}}g"):
            group = copy.deepcopy(group)
            for elem in group.iter():
                if elem.tag == f"{{{SVG}}}path":
                    elem.set("fill",p["black"])
                    # Normalize decimal precision while preserving deliberate curves.
                    elem.set("d", re.sub(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", lambda m: f"{float(m.group()):.3f}".rstrip("0").rstrip(".") if "." in m.group() or "e" in m.group() else m.group(), elem.get("d")))
            g.append(group)
    else:
        root.set("viewBox","52 28 696 724")
        root.set("width","696")
        root.set("height","724")
    ET.indent(root)
    filename = "BC-Trade-symbol.svg" if symbol_only else ("BC-Trade-recreated.svg" if palette_name=="colour" else "BC-Trade-scan-tones.svg")
    dest = OUT/filename
    ET.ElementTree(root).write(dest, encoding="utf-8", xml_declaration=True)
    return dest

if __name__ == "__main__":
    for f in [build(), build("scan-tones"), build(symbol_only=True)]:
        print(f)
    (OUT/"palette.json").write_text(json.dumps(PALETTES,indent=2)+"\n")
    (OUT/"flag-corner-review.json").write_text(json.dumps(CAP_REVIEW, indent=2)+"\n")
