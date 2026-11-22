"""Write the BCRC website-wordmark SVG from a fit result (font outlines, per-letter translation)."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from fontpaths import *
fits = json.load(open(sys.argv[1])); res = fits[int(sys.argv[2])]
out = sys.argv[3]
RED, BLUE = sys.argv[4], sys.argv[5]
font = load_font(res['fontPath'], res['axes']); upm = font['head'].unitsPerEm
lines = [(0, 7), (7, 15), (15, 22), (22, 29)]
paths = []; allpts = []
for k, L in enumerate(res['letters']):
    rec, adv = glyph_record(font, L['ch'])
    T = Affine.translate(L['dx'], L['dy']) @ glyph_T(res['size'], upm, 0, 0, res['addedSlant'], res['xscale'])
    paths.append((k, L['ch'], T, rec))
    for pl in record_to_polys(rec, T, 16): allpts += pl
import numpy as np
P = np.array(allpts); x0, y0 = P.min(0) - 1; x1, y1 = P.max(0) + 1
sh = Affine.translate(-x0, -y0)
initials = {0, 7, 15, 22}
g = []
for li, (a, b) in enumerate(lines):
    red = [paths[a]]; blue = paths[a + 1:b]
    g.append('<g id="line%d">' % (li + 1))
    g.append('<path fill="%s" d="%s"/>' % (RED, record_to_svg(red[0][3], sh @ red[0][2])))
    g.append('<path fill="%s" d="%s"/>' % (BLUE, ''.join(record_to_svg(p[3], sh @ p[2]) for p in blue)))
    g.append('</g>')
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" width="%.2f" height="%.2f">' % (x1 - x0, y1 - y0, x1 - x0, y1 - y0)
       + '<title>British Columbia Railway Company</title>' + ''.join(g) + '</svg>\n')
open(out, 'w').write(svg)
print(out, 'offset', round(x0, 2), round(y0, 2), 'size', round(x1 - x0, 2), round(y1 - y0, 2))
