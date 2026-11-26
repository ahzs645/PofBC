"""Rebuild the outlined sign with: uv run --with fonttools scripts/build_cheakamus_sign.py"""
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artwork/signs/cheakamus/polished.svg"
EMBLEM = ROOT / "public/identity-recreation-conservation/drc-fw-oval-1973.svg"
OUTPUT = ROOT / "src/signs/fish-wildlife/cheakamus.svg"
SVG = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", SVG[1:-1])
source = ET.parse(SOURCE).getroot()
drawing = ET.Element(SVG + "svg", {**source.attrib, "aria-labelledby": "ck-title ck-desc"})
ET.SubElement(drawing, SVG + "title", id="ck-title").text = "Notice to Anglers, Cheakamus River"
ET.SubElement(drawing, SVG + "desc", id="ck-desc").text = (
    "Reconstruction of an undated Fish and Wildlife Branch sign. The notice describes a closure "
    "from the sign upstream to the British Columbia Railway bridge (mile 56.6), April 1 to June 30. "
    "Some wording is inferred from the photograph."
)


def original(layer):
    return source.find(f"./*[@id='{layer}']")


for layer in ("board", "fw-emblem", "red-header"):
    element = original(layer)
    element.set("id", "ck-" + layer)
    drawing.append(element)


# Fit the gallery master to the existing gold backing, using the sign's original dark ink.
emblem = drawing.find("./*[@id='ck-fw-emblem']")
backing = emblem.find(SVG + "rect")
old_outline = emblem.find(SVG + "path")
master_paths = ET.parse(EMBLEM).getroot().findall(".//" + SVG + "path")
bounds = BoundsPen(None)
for path in master_paths:
    parse_path(path.get("d"), bounds)
left, top, right, bottom = bounds.bounds
scale_x = float(backing.get("width")) / (right - left)
scale_y = float(backing.get("height")) / (bottom - top)
emblem.remove(old_outline)
outline = ET.SubElement(emblem, SVG + "g", {
    "fill": old_outline.get("fill"),
    "transform": (
        f"translate({backing.get('x')} {backing.get('y')}) "
        f"scale({scale_x:.9g} {scale_y:.9g}) translate({-left:g} {-top:g})"
    ),
})
for path in master_paths:
    ET.SubElement(outline, SVG + "path", {"d": path.get("d"), "fill-rule": path.get("fill-rule")})


def line(layer, x, baseline, sx, sy, fill, words):
    """One placement per line and one outlined path per word, labelled in reading order."""
    group = ET.SubElement(drawing, SVG + "g", {
        "id": "ck-" + layer, "aria-label": " ".join(word for word, _ in words),
        "fill": fill, "transform": f"translate({x:g} {baseline:g}) scale({sx:.7f} {-sy:.7f})",
    })
    for word, path in words:
        ET.SubElement(group, SVG + "path", {"aria-label": word, "d": path})


def display_line(layer, center, baseline, width, cap_height, font_cap, gap, space):
    """Use the supplied letter shapes, with common scale, tracking and word spaces."""
    group = original(layer)
    letters = iter(group)
    words = []
    cursor = 0
    for word in group.get("aria-label").split():
        pen = SVGPathPen(None)
        for char in word:
            glyph = next(letters)
            assert glyph.get("aria-label") == char
            path = glyph if glyph.tag == SVG + "path" else glyph.find(SVG + "path")
            outline = path.get("d")
            bounds = BoundsPen(None)
            parse_path(outline, bounds)
            left, bottom, right, top = bounds.bounds
            # The custom barred J was drawn upright in board units. All other outlines use font units.
            # The river name also borrows an I drawn in a larger font coordinate system.
            rescale = glyph is path or (layer == "river-name" and char == "I")
            scale = font_cap / (top - bottom) if rescale else 1
            matrix = (scale, 0, 0, -scale if glyph is path else scale,
                      cursor - scale * left, scale * top if glyph is path else 0)
            parse_path(outline, TransformPen(pen, matrix))
            cursor += (right - left) * scale + gap
        words.append((word, pen.getCommands()))
        cursor += space - gap
    line(layer, center - width / 2, baseline, width / (cursor - space), cap_height / font_cap,
         group[0].get("fill"), words)


# The display lettering retains the reconstructed headline, river name, two inserts and credit.
display_line("notice-heading", 584, 178, 710, 47, 1384, 55, 620)
display_line("river-name", 530, 325, 704, 49, 714, 66, 300)

# All four notice lines use the same font metrics, left margin and 54-unit baseline spacing.
font = TTFont(ROOT / "src/fonts/stand-in/texgyreheros-regular.ttf")
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
body_scale = 35 / font["OS/2"].sCapHeight


def body_line(layer, x, baseline):
    words = []
    cursor = 0
    for word in original(layer).get("aria-label").split():
        pen = SVGPathPen(glyphs)
        for char in word:
            glyph = glyphs[cmap[ord(char)]]
            glyph.draw(TransformPen(pen, (1, 0, 0, 1, cursor, 0)))
            cursor += glyph.width + 16
        words.append((word, pen.getCommands()))
        cursor += glyphs[cmap[32]].width
    line(layer, x, baseline, body_scale * 0.925, body_scale, "#282923", words)

body_line("closed-line", 70, 382)
body_line("upstream-line", 70, 436)
body_line("railway-line", 70, 490)
display_line("mile-number", 603, 490, 258, 35, 739, 55, 310)
body_line("from-line", 784, 490)
body_line("start-date", 70, 544)
display_line("end-date", 510, 544, 220, 34, 1413, 145, 560)
display_line("branch-credit", 530, 607, 860, 18, 722, 65, 350)

ET.indent(drawing, space="  ")
OUTPUT.write_text(ET.tostring(drawing, encoding="unicode") + "\n")
