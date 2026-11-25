"""Register the source page and measure the first and current Fire Day SVGs."""
import argparse
import io
import subprocess
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[3]
DRAWING = 'src/signs/forest-service/fire-day.svg'
FIRST_VERSION = '08b8d632570ccf3dc20eb3df0c8548c53deb7ce5'
SIZE = (550, 424)
# Bounds of the print lines in the registered view (left, top, right, bottom).
REGIONS = {
    'Headline': [(13, 22, 534, 74)],
    'Warning columns': [
        (22, 93, 164, 129), (381, 94, 538, 129), (22, 130, 164, 166), (380, 130, 538, 165),
        (22, 168, 164, 205), (381, 168, 538, 205), (22, 207, 164, 242), (381, 207, 538, 242),
    ],
    'Lower notice': [(25, 262, 529, 291), (80, 292, 172, 321), (360, 292, 465, 320),
                     (25, 320, 529, 346), (25, 346, 529, 374)],
    'INFLAMMABLE': [(177, 292, 355, 312)],
    'Issuer': [(107, 376, 442, 395)],
}
RENDER = """
const { Resvg } = require('@resvg/resvg-js')
const svg = require('node:fs').readFileSync(0)
process.stdout.write(new Resvg(svg, { fitTo: { mode: 'zoom', value: 3 } }).render().asPng())
"""


def registered_page(pdf):
    with pymupdf.open(pdf) as archive:
        page = archive[122]
        scale = pymupdf.Matrix(827 / page.rect.width, 1241 / page.rect.height)
        pix = page.get_pixmap(matrix=scale)
        scan = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L')
    # Clockwise from the upper-left corner of the photographed board.
    scan_points = [(142, 551), (690, 554), (685, 968), (145, 974)]
    sign_points = [(0, 0), (550, 0), (550, 424), (0, 424)]
    matrix, target = [], []
    for (x, y), (u, v) in zip(sign_points, scan_points):
        matrix.extend([[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]])
        target.extend([u, v])
    inverse_map = np.linalg.solve(matrix, target)
    return scan.transform(SIZE, Image.Transform.PERSPECTIVE, inverse_map, Image.Resampling.BICUBIC)


def rendered_ink(svg):
    data = subprocess.check_output(['node', '-e', RENDER], input=svg, cwd=ROOT)
    rgb = Image.open(io.BytesIO(data)).convert('RGB').resize(SIZE, Image.Resampling.LANCZOS)
    return np.asarray(rgb)[:, :, 0] < 142


def compare(pdf):
    scan = registered_page(pdf)
    reference = Image.open(ROOT / 'src/signs/forest-service/fire-day.reference.png')
    if not np.array_equal(np.asarray(scan), np.asarray(reference)):
        raise ValueError('The registered page differs from the published overlay reference.')
    gray = np.asarray(scan, dtype=float)
    background = gaussian_filter(gray, 7)
    first = subprocess.check_output(['git', 'show', f'{FIRST_VERSION}:{DRAWING}'], cwd=ROOT)
    trials = [rendered_ink(first), rendered_ink((ROOT / DRAWING).read_bytes())]
    masks = {}
    for name, boxes in REGIONS.items():
        region = np.zeros(gray.shape, dtype=bool)
        for x, y, right, bottom in boxes:
            region[y:bottom, x:right] = True
        masks[name] = region
    masks['All lettering'] = np.logical_or.reduce(list(masks.values()))
    for delta in (28, 36, 44):
        ink = (gray < background - delta) & (gray < 202 - delta)
        for name, mask in masks.items():
            overlaps = [np.sum(ink & draw & mask) / np.sum((ink | draw) & mask) for draw in trials]
            print(f'{delta:2d}  {name:<18s}  {overlaps[0]:6.2%}  {overlaps[1]:6.2%}')


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('museum_pdf', type=Path)
    compare(cli.parse_args().museum_pdf)
