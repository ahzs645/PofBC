"""EXPO 86 horizontal wordmark (1986 leaflet): heavy round-ended monoline letters rebuilt from capsules
and elliptical rings, fitted by overlap to the white lettering of the leaflet crop."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import numpy as np
from PIL import Image
from fitlib import fit_prims, raster_prims, iou, overlay_sheet
from prims import annulus, capsule
SRC = '/home/user/PofBC/public/identity-collected/expo-86-corporation/expo86-original-1986-wordmark.png'
a = np.array(Image.open(SRC).convert('RGB')).astype(int)
m = a.min(2) > 170; m[:, 704:] = False; m[172:, :] = False   # white letters; TM and below excluded
H, W = m.shape
def model(p):
    s = p['s']; yt = p['top'] + s/2; yb = p['bot'] - s/2; ym = (p['top'] + p['bot'])/2 + p['emo']
    ex = p['ex'] + s/2
    out = [capsule(ex, yt, ex, yb, s), capsule(ex, yt, p['ex2'] - s/2, yt, s), capsule(ex, ym, p['emr'] - s/2, ym, s), capsule(ex, yb, p['ex2'] - s/2, yb, s)]
    w = s*p['xk']
    out += [capsule(p['xl'] + w/2, yt, p['xr'] - w/2, yb, w), capsule(p['xr'] - w/2, yt, p['xl'] + w/2, yb, w)]
    px = p['px'] + s/2
    out += [capsule(px, yt, px, yb, s), annulus(p['pcx'], p['pcy'], p['prx'], p['pry'], s*p['pk']), capsule(px, p['pcy'] - p['pry'] + s/2, p['pcx'], p['pcy'] - p['pry'] + s/2, s), capsule(px, p['pcy'] + p['pry'] - s/2, p['pcx'], p['pcy'] + p['pry'] - s/2, s)]
    out += [annulus(p['ox'], (p['top'] + p['bot'])/2, p['orx'], (p['bot'] - p['top'])/2, s*p['ok'])]
    out += [annulus(p['e1x'], p['e1y'], p['e1rx'], p['e1ry'], s*p['e1k']), annulus(p['e2x'], p['e2y'], p['e2rx'], p['e2ry'], s*p['e2k'])]
    out += [annulus(p['sx'], p['sy'], p['srx'], p['sry'], s*p['sk']), capsule(p['a1x'], p['a1y'], p['a2x'], p['a2y'], s*p['ak'])]
    return out
p0 = dict(s=40, top=34, bot=170, emo=0, ex=42, ex2=133, emr=128, xl=137, xr=262, xk=1.05, px=262, pcx=315, pcy=78, prx=48, pry=45, pk=1.0,
          ox=420, orx=68, ok=1.0, e1x=550, e1y=72, e1rx=40, e1ry=38, e1k=0.95, e2x=550, e2y=128, e2rx=45, e2ry=43, e2k=1.0,
          sx=652, sy=124, srx=50, sry=47, sk=1.0, a1x=625, a1y=110, a2x=675, a2y=50, ak=1.0)
st = {k: (0.04 if k.endswith('k') else 2) for k in p0}
b, s = fit_prims(model, p0, st, m, rounds=5)
print('IoU', round(s, 4), {k: round(v, 2) for k, v in b.items()})
json.dump(b, open(sys.argv[1], 'w'), indent=0)
fm = raster_prims(model(b), (W, H))
# overlay: letters are white on red, so feed inverted image
inv = Image.fromarray((255 - np.array(Image.open(SRC).convert('L'))).astype(np.uint8)); inv.save('/tmp/claude-0/-home-user-PofBC/bed6bc9b-d326-5a8f-9df1-5262b2af0a39/scratchpad/crowns/work/expo-wm-inv.png')
mm = m.copy()
ov = np.full((H, W, 3), 255, np.uint8); ov[mm & fm] = (70, 70, 70); ov[mm & ~fm] = (40, 120, 235); ov[~mm & fm] = (230, 40, 160)
A = Image.open(SRC).convert('RGB'); B = Image.fromarray(ov); sc = 200 / H
A = A.resize((round(W*sc), 200)); B = B.resize((round(W*sc), 200))
sh = Image.new('RGB', (A.width*2 + 12, 200), (235, 235, 235)); sh.paste(A, (0, 0)); sh.paste(B, (A.width + 12, 0)); sh.save(sys.argv[2], quality=82)
