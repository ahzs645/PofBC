"""Model of the EXPO 86 1986 wordmark (shared by fit and SVG writer)."""
from prims import annulus, capsule
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
