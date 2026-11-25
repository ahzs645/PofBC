"""Screen public specimen images against the 1979 print, using the same fit for every face."""
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage, signal

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / 'public/identity-collected/bc-resources-investment-corporation'
REFERENCE = ART / 'bcric-1979-brochure-wordmark-raster.png'
ORIGINAL_SVG = ART / 'bcric-1979-wordmark-rebuilt.svg'
LETTERS = 'BCRIC'
# The two fitted print impressions have different margins. The divisions separate adjoining
# letters only for registration. Final overlap counts the union on one canvas before scoring.
P6_EDGES = [20, 151, 259, 376, 423, 550]
P3_EDGES = [87, 211, 315, 430, 474, 594]
SCALE = 0.5
BASE = 'https://e-daylight.jp/fonts/type/'
# Half-open boxes for the ordinary B/C/R/I capitals; swash alternates are excluded.
SHEETS = {
    'Caslon Black': ('c/img/caslon-black.gif', [(63,23,104,69),(104,23,141,69),(186,82,228,127),(345,23,370,69)]),
    'ITC Garamond Ultra': ('g/img/itc-garamond-ultra-bold.gif', [(78,28,134,81),(134,27,184,81),(218,109,280,162),(453,29,489,81)]),
    'ITC Garamond Ultra Condensed': ('g/img/itc-garamond-ultra-bold-cond.gif', [(61,24,104,78),(104,24,143,79),(181,108,231,161),(353,25,379,78)]),
    'ITC Tiffany Heavy': ('t/img/tiffany-heavy.gif', [(284,24,336,72),(336,23,380,72),(52,161,110,207),(74,95,104,142)]),
    'ITC Tiffany Demi': ('t/img/tiffany-demi.gif', [(218,23,263,69),(263,20,305,70),(32,157,87,202),(625,23,653,69)]),
    'ITC Benguiat Bold': ('b/img/benguiat-bold.gif', [(115,21,163,70),(164,20,213,70),(272,81,321,131),(462,21,486,70)]),
}
TIFFANY_ALTERNATES = {
    'ITC Tiffany Heavy': [(111,161,169,208),(170,161,247,226)],
    'ITC Tiffany Demi': [(87,157,143,203),(143,157,217,219)],
}
DOC_URL = 'https://sacda.ufv.ca/sites/default/files/2026-09/2021_03_01_03_003.pdf'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cached(url, directory):
    path = directory / url.rsplit('/', 1)[1]
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            path.write_bytes(response.read())
    return path


def trim(mask):
    ys, xs = np.where(mask)
    return mask[ys.min():ys.max()+1, xs.min():xs.max()+1]


def silhouette(image, sigma=1.0, threshold=42):
    rgb = np.asarray(image.convert('RGB'), dtype=float)
    green = ndimage.gaussian_filter(rgb[:, :, 1] - rgb[:, :, 0], sigma)
    small = Image.fromarray(green.astype('float32')).resize(
        (round(image.width*SCALE), round(image.height*SCALE)), Image.Resampling.BILINEAR)
    return np.asarray(small) > threshold


def specimen_glyph(image, box):
    ink = np.asarray(image.crop(box))
    # A neighbouring serif can enter a letter box. Every selected capital is connected
    # at this light threshold, including the fine curves in Tiffany.
    parts, _ = ndimage.label(ink < 230, structure=np.ones((3, 3)))
    largest = np.bincount(parts.ravel())[1:].argmax() + 1
    return trim((parts == largest) & (ink < 128))


def resize(mask, width, height):
    size = (max(1, round(width)), max(1, round(height)))
    return np.asarray(Image.fromarray(mask.astype('uint8')*255).resize(size, Image.Resampling.LANCZOS)) >= 128


def svg_ink(root, scale):
    with pymupdf.open(stream=ET.tostring(root), filetype='svg') as doc:
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=True)
    return np.asarray(Image.frombytes('RGBA', (pix.width, pix.height), pix.samples))[:, :, 3] > 127


def gelasio():
    # One compound path with 3 contours for B, 1 for C, 2 for R, 1 for I, 1 for C.
    root = ET.parse(ORIGINAL_SVG).getroot()
    path = next(root.iter('{http://www.w3.org/2000/svg}path'))
    parts = re.findall('M[^M]+', path.get('d'))
    assert len(parts) == 8
    root.set('viewBox', '0 0 567 187')
    root.set('width', '567')
    root.set('height', '187')
    as_shipped = svg_ink(root, 2)
    masks = []
    for letters in [parts[:3], parts[3:4], parts[4:6], parts[6:7]]:
        path.set('d', ''.join(letters))
        masks.append(trim(svg_ink(root, 2)))
    return masks, as_shipped


def register(mask, target):
    """Maximize ink intersection for integer shifts within ±4 analysis pixels of box-centre alignment."""
    h, w = mask.shape
    ys, xs = target.nonzero()
    center_y = (ys.min() + ys.max()) / 2
    center_x = (xs.min() + xs.max()) / 2
    y, x = round(center_y-(h-1)/2), round(center_x-(w-1)/2)
    # Correlate against only the possible target window to evaluate all 81 placements.
    padded = np.pad(target, 100)
    window = padded[100+y-4:100+y+h+4,100+x-4:100+x+w+4]
    overlap = np.rint(signal.correlate(window.astype(float), mask.astype(float), mode='valid', method='fft')).astype(int)
    dy, dx = np.unravel_index(overlap.argmax(), overlap.shape)
    inter = int(overlap[dy, dx])
    return inter, int(mask.sum() + target.sum() - inter), y-4+dy, x-4+dx


def fit(glyphs, target, edges, cap):
    """Share both scale factors across the five placements, including the two impressions of C."""
    edges = [round(x*SCALE) for x in edges]
    cells = [target[:, left:right] for left, right in zip(edges, edges[1:])]
    # Preserve each font's natural width ratios. The width range is centred on the specimen's
    # total natural width, so condensed and normal faces get the same opportunity to fit.
    indexes = [0,1,2,3,1]
    base_y = cap / glyphs[0].shape[0]
    base_x = sum(trim(c).shape[1] for c in cells)/sum(glyphs[i].shape[1] for i in indexes)
    best = (-1, None, None)
    cache = {}
    pad = 30  # Keep ink outside the scan crop in the union, including long swashes.
    padded_target = np.pad(target, pad)
    def evaluate(xscale, yscale):
        nonlocal best
        placements, work = [], np.zeros_like(padded_target)
        for k, (glyph, cell) in enumerate(zip(indexes, cells)):
            mh, mw = glyphs[glyph].shape
            w, h = round(mw*xscale), round(mh*yscale)
            key = (k, w, h)
            if key not in cache:
                mask = resize(glyphs[glyph], w, h)
                cache[key] = mask, register(mask, cell)
            mask, (inter, union, y, x) = cache[key]
            placements.append((inter, union))
            x += edges[k] + pad
            y += pad
            h, w = mask.shape
            assert y >= 0 and x >= 0 and y+h <= work.shape[0] and x+w <= work.shape[1]
            work[y:y+h, x:x+w] |= mask
        inter = np.count_nonzero(work & padded_target)
        union = np.count_nonzero(work | padded_target)
        if inter / union > best[0]:
            best = (inter/union, (xscale, yscale),
                    (work[pad:-pad, pad:-pad], [round(i/u, 4) for i,u in placements]))
    for ax in np.linspace(.83,1.17,12):
        for ay in np.linspace(.90,1.10,9):
            evaluate(base_x*ax, base_y*ay)
    bx, by = best[1]
    for ax in np.linspace(.98,1.02,9):
        for ay in np.linspace(.982,1.018,7):
            evaluate(bx*ax, by*ay)
    score, scales, (work, per_glyph) = best
    return {'iou': round(score,4), 'B_C1_R_I_C2': per_glyph, 'horizontal_to_vertical_scale': round(scales[0]/scales[1],4)}, work


def overlay(target, candidate):
    pixels = np.full((*target.shape,3), [249,248,244], dtype='uint8')
    pixels[target] = [46,134,99]
    pixels[candidate] = [192,97,57]
    pixels[target & candidate] = [29,43,48]
    return Image.fromarray(pixels)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', required=True, type=Path, help='Directory for downloaded public sources')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ink-threshold', type=int, default=42, help='Minimum smoothed green minus red (8-bit levels)')
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    sources = {}
    control, as_shipped = gelasio()
    faces = {'Gelasio Bold (existing SVG)': control}
    alternates = {}
    for name, (url, boxes) in SHEETS.items():
        path = cached(BASE+url, args.cache)
        with Image.open(path) as sheet:
            gray = sheet.convert('L')
            faces[name] = [specimen_glyph(gray, box) for box in boxes]
            for n, r_box in enumerate(TIFFANY_ALTERNATES.get(name, []), start=2):
                alt = faces[name].copy()
                alt[2] = specimen_glyph(gray, r_box)
                alternates[f'{name}, R {n} on sheet'] = alt
        sources[name] = {'url':BASE+url, 'sha256':digest(path)}
    pdf = cached(DOC_URL, args.cache)
    with pymupdf.open(pdf) as doc:
        pix = doc[2].get_pixmap(matrix=pymupdf.Matrix(2,2), clip=pymupdf.Rect(25,65,355,190))
    p3 = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    results = {'inkThreshold':args.ink_threshold, 'referenceSha256':digest(REFERENCE), 'archivalPdfSha256':digest(pdf), 'specimens':sources, 'fits':{}}
    results['tiffanyAlternateFits'] = {}
    for page, image, edges in [('page6',Image.open(REFERENCE),P6_EDGES),('page3',p3,P3_EDGES)]:
        target = silhouette(image, threshold=args.ink_threshold)
        # The broad top and bottom strokes of B establish a nominal cap height in each impression.
        cap = trim(target[:,round(edges[0]*SCALE):round(edges[1]*SCALE)]).shape[0]
        fits = {}
        registered = {}
        for name, glyphs in faces.items():
            fits[name], fitted = fit(glyphs, target, edges, cap)
            registered[name] = fitted
        if page == 'page6':
            fixed = resize(as_shipped, target.shape[1], target.shape[0])
            results['asShippedPage6IoU'] = round(np.count_nonzero(target & fixed) / np.count_nonzero(target | fixed), 4)
            best = max(SHEETS, key=lambda name: fits[name]['iou'])
            for name, filename in [('Gelasio Bold (existing SVG)', 'gelasio-overlay.png'), (best, 'best-candidate-overlay.png')]:
                overlay(target, registered[name]).resize(image.size, Image.Resampling.NEAREST).save(args.output/filename)
        results['fits'][page] = fits
        results['tiffanyAlternateFits'][page] = {name:fit(glyphs, target, edges, cap)[0] for name,glyphs in alternates.items()}
    (args.output/'scores.json').write_text(json.dumps(results, indent=2)+'\n')


if __name__ == '__main__':
    main()
