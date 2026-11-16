"""Build a PGE caribou badge reconstruction from a JSON config.

Geometry (circles / ellipses) comes from edge fits recorded in the config; ring lettering
is set letter by letter in the configured typeface (outlines, see ringtext.py); the caribou
illustration inside the centre is an automatic potrace outline of the published
illustration (disclosed). Coordinates are source pixels of the registered crop.

usage: build_badge.py config.json out.svg meta.json
"""
import sys, json, math
import numpy as np, cv2
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from measure import *
from ringtext import *
from trace import upsampled_mask, trace_to_path
from fontscan_ring import get_runs

cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; meta_out = sys.argv[3]
g, b, c, lab, runs = get_runs(cfg)
H, W = b.shape
parts = []
meta = dict(config=cfg, runs=[])


def shape(s):
    kind = s['kind']
    if kind == 'disc':
        return '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>' % (*s['c'], s['r'], s['fill'])
    if kind == 'ring':  # annulus between r0 < r1 as a stroked circle
        r0, r1 = s['r']
        return '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" stroke-width="%.2f"/>' % (*s['c'], (r0 + r1) / 2, s['stroke'], r1 - r0)
    if kind == 'ellipse':
        return '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s"/>' % (*s['c'], s['rx'], s['ry'], s['fill'])
    if kind == 'ellipse-ring':
        (rx0, ry0), (rx1, ry1) = s['r']
        return ('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="none" stroke="%s" stroke-width="%.2f"/>'
                % (*s['c'], (rx0 + rx1) / 2, (ry0 + ry1) / 2, s['stroke'], ((rx1 - rx0) + (ry1 - ry0)) / 2))
    raise ValueError(kind)


for s in cfg['shapes']:
    parts.append(shape(s))

# caribou trace (before lettering so letters sit on top; regions do not overlap anyway)
tr = cfg['trace']
yy, xx = np.mgrid[0:H, 0:W]
if tr['region'][0] == 'circle':
    _, cx, cy, rr = tr['region']
    region = np.hypot(xx + .5 - cx, yy + .5 - cy) < rr
else:
    _, cx, cy, rx, ry = tr['region']
    region = ((xx + .5 - cx) / rx) ** 2 + ((yy + .5 - cy) / ry) ** 2 < 1
up = 4
gg = g.astype(np.float32)
if tr['polarity'] == 'neg':
    gg = 255 - gg  # trace the light parts
m = upsampled_mask(gg, region, up=up, thr=tr.get('thr', 128))
path, n = trace_to_path(m, up=up, turdsize=tr.get('turdsize', 60), alphamax=1.0, opttolerance=0.2)
parts.append('<path fill="%s" fill-rule="evenodd" d="%s"/>' % (tr['fill'], path))
meta['trace'] = dict(tool='potracer 0.0.4', upsample=up, threshold=tr.get('thr', 128), turdsize=tr.get('turdsize', 60), alphamax=1.0, opttolerance=0.2, contours=n)

# lettering
for (run, sel), lr in zip(runs, cfg['lettering']):
    font = load_font(lr['font'], lr.get('axes'))
    pl = fit_run(font, run['text'], sel, lab, c, lr['size'], lr['xs'], run['outward_up'], axes=cfg.get('normalAxes'))
    parts.append(run_svg(pl, lr['fill']))
    meta['runs'].append(dict(text=run['text'], font=lr['font'].rsplit('/', 1)[-1], axes=lr.get('axes'), size=lr['size'], xs=lr['xs'],
                             meanIoU=round(float(np.mean([p['iou'] for p in pl])), 4),
                             letters=[dict(ch=p['ch'], iou=round(p['iou'], 3), rotation=round(p['rot'], 2)) for p in pl]))

x0, y0, x1, y1 = cfg['viewBox']
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.2f %.2f %.2f %.2f" width="%.2f" height="%.2f">'
       '<title>%s</title>%s</svg>\n' % (x0, y0, x1 - x0, y1 - y0, x1 - x0, y1 - y0, cfg['title'], ''.join(parts)))
open(out, 'w').write(svg)
json.dump(meta, open(meta_out, 'w'), indent=1)
print(json.dumps({'runs': [(r['text'], r['meanIoU']) for r in meta['runs']], 'traceContours': n, 'bytes': len(svg)}))
