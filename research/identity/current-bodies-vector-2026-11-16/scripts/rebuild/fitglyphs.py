"""Fit font glyphs to letter boxes measured on a source raster and score the overlap.

Each glyph is scaled uniformly to the measured height of its letter and placed at the measured box
(optionally its width is honoured instead). Returns SVG path data for the fitted glyph and its IoU
against the source's alpha mask in that box (rendered with resvg at the source's pixel size).
"""
import os, subprocess, tempfile, sys
import numpy as np
from PIL import Image
from fontTools.pens.boundsPen import BoundsPen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from outline import Font

RENDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'render.cjs')


def glyph_bounds(font, ch):
    bp = BoundsPen(font.gs); font.gs[font.glyph(ch)].draw(bp); return bp.bounds


def fitted_path(font, ch, box, fit='height'):
    """box = (x0, y0, x1, y1) in output units (ink box). Returns path d."""
    gx0, gy0, gx1, gy1 = glyph_bounds(font, ch)
    bx0, by0, bx1, by1 = box
    k = (by1 - by0) / (gy1 - gy0) if fit == 'height' else (bx1 - bx0) / (gx1 - gx0)
    size = k * font.upm
    # glyph drawn with y flipped: ink top at y = baseline - gy1*k
    baseline = by0 + gy1 * k
    x = bx0 - gx0 * k
    if fit == 'height':  # centre horizontally in the box
        x += ((bx1 - bx0) - (gx1 - gx0) * k) / 2
    d, _ = font.path(ch, size, x, baseline)
    return d


def render_mask(svg_body, w, h, scale=1):
    tmp = tempfile.mkdtemp()
    open(f'{tmp}/a.svg', 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{svg_body}</svg>')
    subprocess.run(['node', RENDER, f'{tmp}/a.svg', f'{tmp}/a.png', str(int(w * scale))], check=True)
    return np.array(Image.open(f'{tmp}/a.png').convert('RGBA'))[:, :, 3] / 255.0


def iou(a, b):
    inter = np.minimum(a, b).sum(); uni = np.maximum(a, b).sum()
    return inter / uni if uni else 0
