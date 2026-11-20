"""Builds the evergreen emblem with "British Columbia Forest Service" set around it.

A photograph of the emblem printed on a glass shows the badge ringed by its name in spaced,
bold grotesque capitals: FOREST up the left side and BRITISH across the top, reading clockwise
with the letters' tops outward, then COLUMBIA along the foot and SERVICE up the right side,
reading left to right with their tops inward. The words follow a rounded square around the badge,
not a circle.

This script measures that ring from the photograph and sets the words on it:

- The ring is a superellipse fitted to the centres of the 28 letters, read off the photograph.
- Each word runs from its first letter's position to its last letter's, as photographed, with its
  letters spaced by their own widths in between.
- The letters are outlined from TeX Gyre Heros Bold (src/fonts/stand-in, GUST Font License), the
  free Helvetica clone the site already ships. The photograph does not identify the typeface; it is
  a bold grotesque of that kind, and Heros stands in for it.

The badge, map and tree are the existing reconstruction (src/internal/forest-service-emblem.svg),
copied unchanged; only the viewBox grows to take the ring.

Run: python3 scripts/build_forest_emblem_lettered.py   (Python 3 with fontTools, NumPy, SciPy)
Writes src/internal/forest-service-emblem-lettered.svg.
"""

import math
import re
from pathlib import Path

import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / 'src/internal/forest-service-emblem.svg'
FONT = ROOT / 'src/fonts/stand-in/texgyreheros-bold.ttf'
OUT = ROOT / 'src/internal/forest-service-emblem-lettered.svg'
INK = '#1A1A1A'

# ── What the photograph shows (pixels of a 4× enlargement of the 245 × 247 image) ───────────────

# The badge's edges, which tie the photograph to the reconstruction's coordinates.
PHOTO_BADGE = {'left': 233, 'right': 697, 'top': 303, 'bottom': 772}
# Each letter's centre, in reading order. `out`: tops face away from the badge.
WORDS = [
    {'text': 'FOREST', 'out': True, 'centres': [(185, 752), (180, 690), (180, 610), (183, 520), (188, 440), (195, 360)]},
    {'text': 'BRITISH', 'out': True, 'centres': [(255, 282), (325, 262), (390, 250), (450, 247), (515, 247), (585, 252), (655, 262)]},
    {'text': 'COLUMBIA', 'out': False, 'centres': [(252, 825), (305, 835), (368, 840), (425, 843), (495, 840), (560, 830), (610, 815), (660, 800)]},
    {'text': 'SERVICE', 'out': False, 'centres': [(722, 718), (730, 655), (738, 590), (740, 515), (740, 455), (735, 395), (725, 335)]},
]
PHOTO_CAP_HEIGHT = 35

# The reconstruction's badge: x 183–1065, y 173–1059.
SVG_BADGE = {'left': 183, 'right': 1065, 'top': 173, 'bottom': 1059}


def photo_to_svg():
    sx = (SVG_BADGE['right'] - SVG_BADGE['left']) / (PHOTO_BADGE['right'] - PHOTO_BADGE['left'])
    sy = (SVG_BADGE['bottom'] - SVG_BADGE['top']) / (PHOTO_BADGE['bottom'] - PHOTO_BADGE['top'])
    scale = (sx + sy) / 2
    pcx = (PHOTO_BADGE['left'] + PHOTO_BADGE['right']) / 2
    pcy = (PHOTO_BADGE['top'] + PHOTO_BADGE['bottom']) / 2
    scx = (SVG_BADGE['left'] + SVG_BADGE['right']) / 2
    scy = (SVG_BADGE['top'] + SVG_BADGE['bottom']) / 2
    return scale, lambda x, y: (scx + (x - pcx) * scale, scy + (y - pcy) * scale)


# ── The ring ─────────────────────────────────────────────────────────────────────────────────────

def fit_ring(points):
    """A superellipse |x/a|^n + |y/b|^n = 1 about (cx, cy) through the letter centres."""
    pts = np.array(points)

    def residuals(p):
        cx, cy, a, b, n = p
        x, y = np.abs(pts[:, 0] - cx) / a, np.abs(pts[:, 1] - cy) / b
        return (x ** n + y ** n) ** (1 / n) - 1

    c = pts.mean(axis=0)
    start = [c[0], c[1], np.ptp(pts[:, 0]) / 2, np.ptp(pts[:, 1]) / 2, 3.0]
    return least_squares(residuals, start, bounds=([-np.inf, -np.inf, 1, 1, 2], [np.inf, np.inf, np.inf, np.inf, 8])).x


def ring_samples(ring, count=20000):
    cx, cy, a, b, n = ring
    t = np.linspace(0, 2 * np.pi, count, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    x = cx + a * np.sign(c) * np.abs(c) ** (2 / n)
    y = cy + b * np.sign(s) * np.abs(s) ** (2 / n)
    seg = np.hypot(np.diff(x, append=x[0]), np.diff(y, append=y[0]))
    arc = np.concatenate([[0], np.cumsum(seg)[:-1]])
    return x, y, arc, seg.sum()


def nearest_arc(samples, point):
    x, y, arc, _ = samples
    return arc[np.argmin((x - point[0]) ** 2 + (y - point[1]) ** 2)]


def at_arc(samples, s):
    """The point at arc length s and the clockwise tangent's angle there."""
    x, y, arc, total = samples
    s %= total
    i = int(np.searchsorted(arc, s, side='right') - 1)
    j = (i + 1) % len(x)
    span = (arc[j] if j else total) - arc[i]
    f = (s - arc[i]) / span if span else 0
    px, py = x[i] + (x[j] - x[i]) * f, y[i] + (y[j] - y[i]) * f
    return px, py, math.atan2(y[j] - y[i], x[j] - x[i])


# ── Setting the words ────────────────────────────────────────────────────────────────────────────

def glyph_path(font, glyph_set, char, transform):
    name = font.getBestCmap()[ord(char)]
    pen = SVGPathPen(glyph_set, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
    glyph_set[name].draw(TransformPen(pen, transform))
    return pen.getCommands()


def set_word(word, samples, font, glyph_set, cap_target, to_svg):
    cmap, hmtx = font.getBestCmap(), font['hmtx']
    cap = font['OS/2'].sCapHeight
    k = cap_target / cap
    total = samples[3]
    widths = [hmtx[cmap[ord(ch)]][0] * k for ch in word['text']]
    # Centres of the letters along the word if set solid, then stretched to the photograph's ends.
    solid = np.cumsum([0] + [(widths[i] + widths[i + 1]) / 2 for i in range(len(widths) - 1)])
    first = nearest_arc(samples, to_svg(*word['centres'][0]))
    last = nearest_arc(samples, to_svg(*word['centres'][-1]))
    # Outward words travel clockwise (arc increasing); inward words counter-clockwise.
    run = (last - first) % total if word['out'] else -((first - last) % total)
    paths = []
    for ch, offset in zip(word['text'], solid):
        s = first + run * (offset / solid[-1])
        px, py, tangent = at_arc(samples, s)
        angle = tangent if word['out'] else tangent + math.pi
        name = cmap[ord(ch)]
        # Centre each letter on the ring: its advance's middle along it, half its cap height across.
        cx, cy = hmtx[name][0] / 2, cap / 2
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        # font units (y up) → letter-centred, scaled, y down → rotated → placed
        a, b = k * cos_a, k * sin_a
        c, d = k * sin_a, -k * cos_a
        e = px - (a * cx + c * cy)
        f = py - (b * cx + d * cy)
        paths.append(f'<path d="{glyph_path(font, glyph_set, ch, (a, b, c, d, e, f))}"/>')
    return paths


def main():
    scale, to_svg = photo_to_svg()
    centres = [to_svg(*p) for word in WORDS for p in word['centres']]
    ring = fit_ring(centres)
    samples = ring_samples(ring)
    font = TTFont(FONT)
    glyph_set = font.getGlyphSet()
    cap_target = PHOTO_CAP_HEIGHT * scale

    groups = []
    for word in WORDS:
        body = '\n      '.join(set_word(word, samples, font, glyph_set, cap_target, to_svg))
        groups.append(f'    <g id="ring-{word["text"].lower()}" inkscape:label="{word["text"]}">\n      {body}\n    </g>')

    master = MASTER.read_text(encoding='utf-8')
    cx, cy, a, b, n = ring
    reach = max(a, b) * 2 ** 0.5 * 2 ** (-1 / n) + cap_target * 0.75
    half = math.ceil(max(a + cap_target, b + cap_target, reach) / 10) * 10 + 20
    ox, oy = round(cx - half), round(cy - half)
    size = 2 * half
    svg = re.sub(r'width="922" height="922" viewBox="163 155 922 922"',
                 f'width="{size}" height="{size}" viewBox="{ox} {oy} {size} {size}"', master)
    svg = svg.replace('British Columbia evergreen emblem: vector reconstruction',
                      'British Columbia Forest Service evergreen emblem with its name around it: vector reconstruction')
    svg = re.sub(r'<desc id="logo-description">[^<]*</desc>',
                 '<desc id="logo-description">The evergreen emblem reconstruction with “British Columbia Forest Service” '
                 'set around it in outlined bold grotesque capitals, after a photograph of the emblem printed on a glass. '
                 'The lettering is TeX Gyre Heros Bold standing in for an unidentified typeface; the ring is fitted to '
                 'the photographed letter positions. Not an official master.</desc>', svg)
    ring_layer = (f'  <g inkscape:groupmode="layer" inkscape:label="04 · Name around the badge" id="ring-layer" fill="{INK}">\n'
                  + '\n'.join(groups) + '\n  </g>\n</svg>')
    svg = svg.replace('</svg>', ring_layer)
    OUT.write_text(svg, encoding='utf-8')
    print(f'ring: centre ({cx:.1f}, {cy:.1f}), semi-axes {a:.1f} × {b:.1f}, exponent {n:.2f}; '
          f'cap height {cap_target:.1f}; viewBox {ox} {oy} {size} {size}')


if __name__ == '__main__':
    main()
