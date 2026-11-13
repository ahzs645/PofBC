#!/usr/bin/env python3
"""Author a BC Trade reconstruction from deliberately drawn vector components.

The reference pixels are not traced or converted into contours. Geometry is
defined here as compact, editable curves; the original scan supplies landmarks.
"""
from pathlib import Path
import copy
from functools import lru_cache
import json
import re
import subprocess
import xml.etree.ElementTree as ET

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
 L 609,247 L 601,309 L 722,280
 L 663,370 C 659,375 657,379 662,381
 L 701,384 L 680,405 L 664,420
 L 644,523 L 161,546 L 142,449
 L 75,396 L 118,383 C 122,382 123,377 121,372
 L 86,276 L 199,309 C 205,311 209,307 210,297
 L 217,238 L 306,325
 C 316,335 325,340 332,335 C 340,331 338,315 335,300
 L 296,145 L 344,166 C 357,173 363,171 371,161 Z"""

FLAG = """M 142,449
 C 179,433 220,421 247,425
 C 280,429 292,446 286,493
 C 338,461 404,414 449,410
 C 482,403 511,414 519,435
 C 524,448 521,462 518,471
 C 571,441 627,424 677,419
 L 634,728 L 78,728 L 120,485 Z"""

BLUE_FIELD = """M 116,487
 C 165,459 217,438 248,445
 C 276,451 261,492 264,515
 C 268,541 301,516 326,496
 C 374,463 413,440 447,434
 C 478,427 501,437 496,459
 C 492,479 481,501 493,508
 C 507,515 536,493 576,479
 C 608,457 641,446 675,439
 L 637,738 L 71,738 Z"""

# Broad white channels and coloured interiors are separate closed paths.
LEFT_UPPER_WHITE = """M 105,497
 C 166,492 221,514 246,551
 C 264,581 264,605 258,628
 C 246,602 226,580 190,569
 C 161,559 128,557 97,564 Z"""
LEFT_UPPER_RED = """M 103,516
 C 159,507 214,529 239,558
 C 250,573 254,589 250,604
 C 237,584 214,566 184,559
 C 156,551 127,551 99,555 Z"""

LEFT_LOWER = """M 84,638
 C 133,611 188,596 224,600
 C 246,602 259,611 257,629
 C 254,647 251,670 251,690
 C 249,693 246,689 241,685
 C 231,673 215,667 194,669
 C 155,671 115,684 77,699 Z"""

CENTRE_WHITE = """M 328,490
 C 356,466 396,442 424,431
 L 400,610 L 317,613 Z"""
CENTRE_RED = """M 344,488
 C 365,470 390,455 413,446
 L 391,610 L 330,610 Z"""

DIAGONAL_WHITE = """M 471,610 L 605,458
 C 627,443 653,436 677,432
 L 670,481 C 649,493 618,523 589,552
 L 506,630 C 492,639 475,635 470,628
 C 468,622 469,615 471,610 Z"""
DIAGONAL_RED = """M 474,611 L 610,467
 C 627,455 649,448 674,443
 L 672,454 C 645,470 616,496 591,522
 L 509,605 C 495,614 484,618 474,611 Z"""

RIGHT_LOWER = """M 476,662
 C 528,633 593,605 660,588
 L 650,657 C 590,672 533,698 491,714
 C 459,728 463,705 467,684
 C 470,670 469,667 476,662 Z"""

SUN = """M 244,738
 C 249,719 250,703 246,687
 C 250,674 249,661 246,648
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

@lru_cache(maxsize=1)
def paint_geometry():
    """Resolve vector overlaps so PDF clipping cannot create coloured hairlines.

    These are Boolean operations on the authored Beziers, never on image pixels.
    White channels are cut from underlying colours; strokes become filled paths.
    All source control points above remain simple and individually editable.
    """
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
    cutouts = "".join(shape(d) for d in (LEFT_UPPER_WHITE, CENTRE_WHITE, DIAGONAL_WHITE))
    cutouts += "".join(shape(d, width=w) for d,w in ((LEFT_LOWER,12),(RIGHT_LOWER,12),(SUN,8)))
    white = operation(cutouts, "white-channels", expand + "path-union")
    result = {"blue":operation(shape(BLUE_FIELD, "blue") + shape(white), "blue-field", "select-all;path-difference")}
    for name,d,w in (("left-lower",LEFT_LOWER,12),("right-lower",RIGHT_LOWER,12),("sun",SUN,8)):
        result[name] = operation(shape(d,"red",w), name + "-inset", expand + "path-difference")
    sun_extent = operation(shape(SUN, width=8), "sun-white-extent", expand + "path-union")
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
        "Manual reconstruction from the two supplied raster references. "
        "Separate maple leaf, waving flag, five red flag bands, rising sun, and outlined lettering. "
        "Original scan controls geometry; colours are approximate. No tracing or embedded raster."
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
        g.set("transform", "translate(68 744) scale(0.668 0.64)")
        letters = ET.parse(ROOT / "typography-review" / "wordmark.svg").getroot()
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
