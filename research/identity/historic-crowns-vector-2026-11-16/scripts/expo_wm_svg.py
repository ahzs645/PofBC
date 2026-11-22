"""Write the fitted EXPO 86 wordmark as SVG with true arcs (white, as knocked out of the leaflet's red)."""
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
import prims
from svgout import write
p = json.load(open(sys.argv[1])); ink = sys.argv[3] if len(sys.argv) > 3 else '#ffffff'
calls = []
import expo_wm_model
# re-run the model with recording primitives
rec = []
def cap(*a): rec.append(('c', a)); return prims.capsule(*a)
def ann(*a): rec.append(('a', a)); return prims.annulus(*a)
expo_wm_model.capsule = cap; expo_wm_model.annulus = ann
polys = expo_wm_model.model(p)
sh = []
for kind, a in rec:
    if kind == 'c': sh.append((prims.d_capsule(*a), ink))
    else: sh.append((prims.d_annulus(*a), ink, 'fill-rule="evenodd"'))
xs = [x for o, h in polys for x, y in o]; ys = [y for o, h in polys for x, y in o]
print(write(sys.argv[2], sh, (min(xs), min(ys), max(xs), max(ys)), 'EXPO 86 wordmark, 1986 (reconstruction)', scale=2))
