"""Build outlined and editable sign lettering editions from the 2000 manual plates."""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[3]
SOURCES = ROOT / 'src/signs/entering-bc'
OUTPUT = ROOT / 'public/sign-reconstructions/entering-bc'
SYSTEM_FONTS = Path('/System/Library/Fonts/Supplemental')
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)


def element(parent, tag, attrs=None, text=None):
    node = ET.SubElement(parent, f'{{{SVG}}}{tag}', attrs or {})
    node.text = text
    return node


def number(value):
    return f'{value:.6f}'.rstrip('0').rstrip('.')


def matrix(scale_x, scale_y, x=0, y=0):
    return 'matrix(' + ' '.join(map(number, (scale_x, 0, 0, scale_y, x, y))) + ')'


class Face:
    def __init__(self, file, family, weight=400, italic=False):
        self.family = family
        self.weight = weight
        self.italic = italic
        font = TTFont(file)
        self.upem = font['head'].unitsPerEm
        self.cmap = font.getBestCmap()
        self.names = font.getGlyphOrder()
        location = {'wght': weight} if 'fvar' in font else {}
        self.glyphs = font.getGlyphSet(location=location)
        self.hb_font = hb.Font(hb.Face(Path(file).read_bytes()))
        self.hb_font.set_variations(location)
        self.hb_font.scale = (self.upem, self.upem)

    def shape(self, text, tracking):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.hb_font, buffer, {'liga': not tracking, 'clig': not tracking})
        x = 0
        positions = []
        for glyph, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
            positions.append((self.names[glyph.codepoint], x + pos.x_offset, pos.y_offset, glyph.cluster))
            x += pos.x_advance + tracking
        return positions

    def text_attributes(self, size, fill):
        return {
            'font-family': self.family, 'font-size': number(size), 'font-weight': str(self.weight),
            'font-style': 'italic' if self.italic else 'normal', 'fill': fill,
        }


def outline(parent, face, name, transform, fill):
    pen = SVGPathPen(face.glyphs, ntos=number)
    face.glyphs[name].draw(TransformPen(pen, transform))
    if path := pen.getCommands():
        element(parent, 'path', {'d': path, 'fill': fill})


def fit_text(parent, face, label, bounds, editable, *, fill='#000000', tracking=0, accent=None):
    """Fit the shaped ink to the measured manual bounds. Tracking is a fraction of an em."""
    left, top, right, bottom = bounds
    tracking *= face.upem
    positions = face.shape(label, tracking)
    pen = BoundsPen(face.glyphs)
    for name, x, y, _ in positions:
        face.glyphs[name].draw(TransformPen(pen, (1, 0, 0, 1, x, y)))
    x_min, y_min, x_max, y_max = pen.bounds
    sx, sy = (right - left) / (x_max - x_min), (bottom - top) / (y_max - y_min)
    tx, ty = left - sx * x_min, top + sy * y_max

    if editable:
        attrs = face.text_attributes(face.upem, fill)
        attrs.update({
            'transform': matrix(sx, sy, tx, ty), 'letter-spacing': number(tracking),
            'font-variant-ligatures': 'none' if tracking else 'normal',
        })
        if accent:
            start, end, colour = accent
            node = element(parent, 'text', attrs, label[:start])
            element(node, 'tspan', {'fill': colour}, label[start:end]).tail = label[end:]
        else:
            element(parent, 'text', attrs, label)
        return

    for name, x, y, index in positions:
        colour = accent[2] if accent and accent[0] <= index < accent[1] else fill
        outline(parent, face, name, (sx, 0, 0, -sy, tx + sx * x, ty - sy * y), colour)


def greeting_from_pdf(parent, face, label, size, scale_x, editable):
    """Re-set the two Times greetings using the native PDF glyph origins held in the SVG."""
    glyph_positions = [
        tuple(map(float, re.fullmatch(r'translate\(([\d.]+) ([\d.]+)\)', path.attrib['transform']).groups()))
        for group in parent for path in group
    ]
    assert len(glyph_positions) == len(label.replace(' ', ''))
    for group in list(parent):
        parent.remove(group)
    fill = '#6666ff'
    if editable:
        visible = iter(glyph_positions)
        positions = []
        for char in label:
            positions.append(next(visible)[0] if char != ' ' else positions[-1] + size / 3)
        attrs = face.text_attributes(size, fill)
        attrs.update({
            'transform': matrix(scale_x, 1),
            'x': ' '.join(number(x / scale_x) for x in positions),
            'y': number(glyph_positions[0][1]), 'font-kerning': 'none',
            '{http://www.w3.org/XML/1998/namespace}space': 'preserve',
        })
        element(parent, 'text', attrs, label)
        return
    sx, sy = scale_x * size / face.upem, size / face.upem
    for char, (x, y) in zip(label.replace(' ', ''), glyph_positions, strict=True):
        outline(parent, face, face.cmap[ord(char)], (sx, 0, 0, -sy, x, y), fill)


def reset(group):
    for child in list(group):
        group.remove(child)


def rebuild(sign, faces, editable):
    root = ET.parse(SOURCES / f'{sign}.svg').getroot()
    title = root.find(f'{{{SVG}}}title')
    title.text += ' · editable lettering' if editable else ' · lettering reconstruction'
    desc = root.find(f'{{{SVG}}}desc')
    desc.text = 'Lettering edition based on the B.C. Ministry of Transportation and Highways manual, September 2000, printed page 6.12. Panel and symbol paths come from the published illustrations.'

    def group(name):
        return root.find(f".//*[@id='{sign}-{name}']")

    if sign == 'i-180':
        desc.text += ' Lobster Regular approximates the unidentified square-sign script. The Tourism BC wordmark retains its published outlines.'
        greeting = group('greeting')
        reset(greeting)
        fit_text(greeting, faces['lobster'], 'Welcomes You!', (81.36, 121.56, 127.56, 128.16), editable, fill='#ffffff')
    elif sign in WIDE_GREETINGS:
        desc.text += ' Times New Roman Bold Italic is named in the PDF. The Tourism BC wordmark retains its published outlines.'
        greeting_from_pdf(group('greeting'), faces['times'], *WIDE_GREETINGS[sign], editable)
    elif sign == 'i-181':
        desc.text += ' Arial Narrow Bold approximates the unidentified condensed lettering.'
        message = group('message')
        reset(message)
        for line, bounds, tracking in SEAT_BELT_LINES:
            fit_text(message, faces['narrow'], line, bounds, editable, tracking=tracking)
    else:
        desc.text += ' Overpass and Arial Bold approximate the unidentified Thinkmetric lettering.'
        headline = group('headline')
        reset(headline)
        fit_text(headline, faces['overpass800'], 'Thinkmetric', (60.72, 509.64, 170.64, 521.4),
                 editable, fill='#ffffff', tracking=.125, accent=(4, 6, '#ffd93d'))
        examples = group('examples')
        for index, path in enumerate(list(examples)):
            if index not in SPEED_PANEL_PATHS:
                examples.remove(path)
        for line, face, bounds, tracking, fill in SPEED_LINES:
            fit_text(examples, faces[face], line, bounds, editable, tracking=tracking, fill=fill)

    ET.indent(root, space='  ')
    suffix = 'editable' if editable else 'reconstruction'
    (OUTPUT / f'{sign}-{suffix}.svg').write_text(ET.tostring(root, encoding='unicode') + '\n')


WIDE_GREETINGS = {
    'i-180x': ('Welcomes You!', 9.8151, 1.0009),
    'i-180b': ('Welcomes You!  /   Bienvenue!', 13.3566, .9929),
}
SEAT_BELT_LINES = [
    ('USE OF', (96.72, 402.96, 119.28, 408.96), .1),
    ('SEAT BELTS', (96.72, 412.8, 132, 418.8), .05),
    ('COMPULSORY IN', (96.72, 422.4, 145.92, 428.64), .125),
    ('BRITISH COLUMBIA', (96.72, 432.24, 154.08, 438.24), .075),
]
# White faces and their outlines, followed by the inner black rules.
SPEED_PANEL_PATHS = {0, 1, 2, 3, 29, 30, 31, 44, 45, 46, 47}
SPEED_LINES = [
    ('WAS', 'overpass900', (102.24, 542.52, 129.12, 551.16), .15, '#ffffff'),
    ('MAXIMUM', 'overpass900', (68.64, 529.8, 94.56, 534.12), .025, '#000000'),
    ('90', 'overpass800', (68.64, 537.96, 94.08, 556.2), 0, '#000000'),
    ('km/h', 'arial', (71.28, 558.84, 91.68, 564.6), .075, '#000000'),
    ('MAXIMUM', 'overpass900', (137.04, 529.8, 162.96, 534.12), .025, '#000000'),
    ('55', 'overpass900', (137.76, 538.2, 162.24, 556.2), -.025, '#000000'),
    ('MPH', 'arial', (138.48, 558.84, 161.52, 564.6), .325, '#000000'),
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lobster', required=True, type=Path, help='Lobster-Regular.ttf')
    parser.add_argument('--overpass', required=True, type=Path, help='Overpass[wght].ttf')
    parser.add_argument('--system-fonts', default=SYSTEM_FONTS, type=Path, help='Directory containing the Times New Roman and Arial TTFs')
    args = parser.parse_args()
    faces = {
        'lobster': Face(args.lobster, 'Lobster'),
        'overpass800': Face(args.overpass, 'Overpass', 800),
        'overpass900': Face(args.overpass, 'Overpass', 900),
        'times': Face(args.system_fonts / 'Times New Roman Bold Italic.ttf', 'Times New Roman', 700, True),
        'narrow': Face(args.system_fonts / 'Arial Narrow Bold.ttf', 'Arial Narrow', 700),
        'arial': Face(args.system_fonts / 'Arial Bold.ttf', 'Arial', 700),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for sign in ('i-180', 'i-180x', 'i-180b', 'i-181', 'i-182'):
        for editable in (False, True):
            rebuild(sign, faces, editable)
