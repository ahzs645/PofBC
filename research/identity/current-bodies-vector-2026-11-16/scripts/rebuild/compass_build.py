"""Build the two Compass needle SVGs from the fitted geometry (compass_fit.py) and check them.

    python -I compass_build.py needle-symbol.png website-logo.png OUTDIR REVIEWDIR

needle-symbol: blue needle (#0099cc) with a white C, as the 561 x 561 TransLink PNG.
website-logo:  white needle with a blue C (#009ddc), as the compasscard.ca sprite crop (81 x 80).
Both use the same geometry (source-pixel units of the 561 px image); only the fills differ.
"""
import sys, os, math, json, subprocess, tempfile
import numpy as np
from PIL import Image
RENDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'render.cjs')
N = dict(cx=268.482, cy=292.474, R=269.206, px=557.497, py=3.947, rc=4.11)
C = dict(ux=270.939, uy=299.251, r1=204.47, r2=116.447, yt=253.8, yb=348.6)
f = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')


def needle_d():
    cx, cy, R, px, py, rc = (N[k] for k in ('cx', 'cy', 'R', 'px', 'py', 'rc'))
    d = math.hypot(px - cx, py - cy); ang = math.atan2(py - cy, px - cx); beta = math.acos((R - rc) / d)
    t1, t2 = ang + beta, ang - beta
    B1 = (cx + R * math.cos(t1), cy + R * math.sin(t1)); S1 = (px + rc * math.cos(t1), py + rc * math.sin(t1))
    B2 = (cx + R * math.cos(t2), cy + R * math.sin(t2)); S2 = (px + rc * math.cos(t2), py + rc * math.sin(t2))
    return (f'M{f(B1[0])} {f(B1[1])}L{f(S1[0])} {f(S1[1])}A{f(rc)} {f(rc)} 0 0 0 {f(S2[0])} {f(S2[1])}'
            f'L{f(B2[0])} {f(B2[1])}A{f(R)} {f(R)} 0 1 0 {f(B1[0])} {f(B1[1])}Z')


def c_d():
    ux, uy, r1, r2, yt, yb = (C[k] for k in ('ux', 'uy', 'r1', 'r2', 'yt', 'yb'))
    xo = lambda r, y: ux + math.sqrt(r * r - (y - uy) ** 2)
    Uo, Ui, Lo, Li = (xo(r1, yt), yt), (xo(r2, yt), yt), (xo(r1, yb), yb), (xo(r2, yb), yb)
    return (f'M{f(Uo[0])} {f(Uo[1])}A{f(r1)} {f(r1)} 0 1 0 {f(Lo[0])} {f(Lo[1])}L{f(Li[0])} {f(Li[1])}'
            f'A{f(r2)} {f(r2)} 0 1 1 {f(Ui[0])} {f(Ui[1])}Z')


VB = '-1 -0.5 563.5 563'
def svg(needle_fill, c_fill):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB}" width="563.5" height="563">'
            f'<path fill="{needle_fill}" d="{needle_d()}"/><path fill="{c_fill}" d="{c_d()}"/></svg>\n')


def render(svgtext, w, h, vb):
    tmp = tempfile.mkdtemp(); s = svgtext.replace(f'viewBox="{VB}" width="563.5" height="563"', f'viewBox="{vb}" width="{w}" height="{h}" preserveAspectRatio="none"')
    open(f'{tmp}/a.svg', 'w').write(s)
    subprocess.run(['node', RENDER, f'{tmp}/a.svg', f'{tmp}/a.png', str(w)], check=True)
    return np.array(Image.open(f'{tmp}/a.png').convert('RGBA')).astype(float) / 255


needle_png, web_png, outdir, revdir = sys.argv[1:5]
os.makedirs(outdir, exist_ok=True); os.makedirs(revdir, exist_ok=True)
outs = {'needle-symbol-rebuilt.svg': svg('#0099cc', '#ffffff'), 'c-symbol-rebuilt.svg': svg('#ffffff', '#009ddc')}
for n, s in outs.items(): open(os.path.join(outdir, n), 'w').write(s)
report = {}
for n, src, vbx in (('needle-symbol-rebuilt.svg', needle_png, '0 0 561 561'), ('c-symbol-rebuilt.svg', web_png, None)):
    T = np.array(Image.open(src).convert('RGBA')).astype(float) / 255
    h, w = T.shape[:2]
    if vbx is None:  # website crop: fit the needle's extent to the sprite's alpha extent
        ys, xs = np.where(T[..., 3] > 0.5)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        kx = 562.3 / (x1 - x0); ky = 561.9 / (y1 - y0)
        vbx = f'{-0.72 - x0 * kx:.3f} {-0.16 - y0 * ky:.3f} {w * kx:.3f} {h * ky:.3f}'
    Rr = render(outs[n], w, h, vbx)
    a_t, a_r = T[..., 3], Rr[..., 3]
    shape_iou = np.minimum(a_t, a_r).sum() / np.maximum(a_t, a_r).sum()
    wt = a_t * T[..., 0]; wr = a_r * Rr[..., 0]     # white share (both blues have R = 0)
    white_iou = np.minimum(wt, wr).sum() / np.maximum(wt, wr).sum()
    report[n] = dict(source=os.path.basename(src), size=[w, h], viewBoxUsed=vbx, shapeIoU=round(float(shape_iou), 4), whiteIoU=round(float(white_iou), 4))
    k = max(1, 600 // w)
    big = lambda m: np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((w * k, h * k), Image.NEAREST)) / 255
    rgb = np.stack([big(wt), big(wr), big(wr)], -1)
    Image.fromarray((rgb * 255).astype(np.uint8)).save(os.path.join(revdir, n.replace('.svg', '-overlay.png')))
print(json.dumps(report, indent=1))
