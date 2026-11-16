"""BCeID wordmark, rebuilt as outlines (vector reconstruction).

Source image: https://www.bceid.ca/assets/images/bceid_rev@2x.png (220 x 58, white capitals, gold italic e).
Typeface: EB Garamond (SIL OFL, Google Fonts) - capitals at a fitted weight, italic e at a fitted weight.
The original typeface is described by the earlier package as Garamond; the exact cut is not verified.
Each letter is scaled to its measured height in the source and placed in its measured box.
One weight is used for all four capitals and one for the e, each chosen by best overlap (IoU)
with the source letters.

    python -I bceid.py SOURCE.png FONTDIR OUT.svg REVIEW.png
"""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fitglyphs import Font, fitted_path, render_mask, iou

src, fontdir, out, review = sys.argv[1:5]
im = np.array(Image.open(src).convert('RGBA')).astype(float)
A = im[:, :, 3] / 255.0
H, W = A.shape
# Measured ink boxes (x0, y0, x1+1, y1+1) of each letter in the 220 x 58 source.
boxes = {'B': (5, 4, 43, 54), 'C': (47, 3, 94, 55), 'e': (98, 12, 137, 55), 'I': (138, 4, 157, 54), 'D': (164, 4, 214, 54)}
WHITE, GOLD = '#ffffff', '#e3a82b'   # sampled from the source (gold = mean of the e's opaque pixels)
roman = os.path.join(fontdir, 'EBGaramond[wght].ttf'); italic = os.path.join(fontdir, 'EBGaramond-Italic[wght].ttf')
choice = {}; parts = []
def score(chars, fontfile, w):
    tot, ds = 0, {}
    f = Font(fontfile, wght=w)
    for ch in chars:
        box = boxes[ch]; d = fitted_path(f, ch, box); ds[ch] = d
        m = render_mask(f'<path d="{d}"/>', W, H)
        x0, y0, x1, y1 = box
        tot += iou(m[y0 - 2:y1 + 2, x0 - 2:x1 + 2], A[y0 - 2:y1 + 2, x0 - 2:x1 + 2])
    return tot / len(chars), ds
for chars, ff in (('BCID', roman), ('e', italic)):
    best = max((score(chars, ff, w) + (w,) for w in range(400, 801, 50)), key=lambda t: t[0])
    for ch in chars: choice[ch] = dict(wght=best[2], meanIoU=round(float(best[0]), 3))
    bests = best[1]
    for ch in chars: choice[ch]['d'] = bests[ch]
for ch in boxes:
    parts.append(f'<path fill="{GOLD if ch == "e" else WHITE}" d="{choice[ch].pop("d")}"/>')
body = ''.join(parts)
m = render_mask(body, W, H)
total = iou(m, A)
svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="4 2 211 54" width="211" height="54">'
       f'{body}</svg>\n')
open(out, 'w').write(svg)
# review: source in red, rebuild in cyan, overlap white, on dark ground, 4x
k = 4
S = np.array(Image.fromarray((A * 255).astype(np.uint8)).resize((W * k, H * k), Image.NEAREST)) / 255.0
R = render_mask(body, W, H, scale=k)
rgb = np.zeros((H * k, W * k, 3)); rgb[..., 0] = S; rgb[..., 1] = R; rgb[..., 2] = R
Image.fromarray((rgb * 255).astype(np.uint8)).save(review)
print(json.dumps(dict(choice=choice, iou=round(float(total), 3))))
