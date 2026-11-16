"""Compare candidate typefaces for a badge's ring lettering (mean per-letter IoU).
usage: fontscan_ring.py config.json candidates.json
config: {source, centre:[x,y], band:[r0,r1], polarity:'neg'|'pos', minw, runs:[{text, start, clockwise, outward_up}]}
"""
import sys, json, math
import numpy as np, cv2
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from measure import *
from ringtext import *


def get_runs(cfg):
    g, b = load(cfg['source'], cfg.get('thr', 128))
    H, W = b.shape; c = np.array(cfg['centre'])
    yy, xx = np.mgrid[0:H, 0:W]
    if 'ellipseBand' in cfg:  # [[ax0, by0], [ax1, by1]] inner and outer semi-axes of the lettering band
        (a0, b0), (a1, b1) = cfg['ellipseBand']
        e0 = ((xx + .5 - c[0]) / a0) ** 2 + ((yy + .5 - c[1]) / b0) ** 2
        e1 = ((xx + .5 - c[0]) / a1) ** 2 + ((yy + .5 - c[1]) / b1) ** 2
        band = (e0 > 1) & (e1 < 1)
    else:
        r = np.hypot(xx + .5 - c[0], yy + .5 - c[1])
        band = (r > cfg['band'][0]) & (r < cfg['band'][1])
    if 'bandMask' in cfg:
        band = np.load(cfg['bandMask'])
    ink = b.astype(bool)
    L = (~ink if cfg['polarity'] == 'neg' else ink) & band
    for x0, y0, x1, y1, w in cfg.get('cuts', []):  # separate letters that print merged
        t = np.zeros(L.shape, np.uint8); cv2.line(t, (int(x0), int(y0)), (int(x1), int(y1)), 1, int(w)); L = L & ~t.astype(bool)
    comps, lab = letter_components(L, cfg.get('minArea', 20))
    # drop paper slivers at the band edges: long thin and small
    def sliver(x):
        w, h, a = x[1][2], x[1][3], x[1][4]
        return (max(w, h) / max(1, min(w, h)) > 3.2 and a < cfg.get('keepArea', 150)) or min(w, h) < cfg.get('minw', 4) or a / (w * h) < 0.12
    comps = [x for x in comps if not sliver(x)]
    runs = []
    used = set()
    for run in cfg['runs']:
        lo, hi = run['range']
        sel = []
        for x in comps:
            a = math.degrees(math.atan2(x[2][1] - c[1], x[2][0] - c[0])) % 360
            if (lo <= a <= hi) if lo < hi else (a >= lo or a <= hi):
                sel.append(x)
        sel = order_run(sel, c, run['start'], run['clockwise'])
        runs.append((run, sel))
    return g, b, c, lab, runs


if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1]))
    g, b, c, lab, runs = get_runs(cfg)
    for run, sel in runs:
        print(run['text'], len(sel))
    for fp, axes, sizes, xss in json.load(open(sys.argv[2])):
        font = load_font(fp, axes)
        tot = []
        for run, sel in runs:
            text = run['text']
            if len(text) != len(sel):
                print('count mismatch', text, len(sel)); continue
            ax = cfg.get('normalAxes')
            best = search_size(font, text, sel, lab, c, run['outward_up'], sizes, xss, axes=ax)
            pl = fit_run(font, text, sel, lab, c, best[1], best[2], run['outward_up'], axes=ax)
            m = float(np.mean([p['iou'] for p in pl]))
            tot.append(m)
            print(fp.rsplit('/', 1)[-1], axes, run['text'], 'size', round(best[1], 1), 'xs', best[2], 'meanIoU', round(m, 4), ' '.join('%s%.2f' % (p['ch'], p['iou']) for p in pl), flush=True)
