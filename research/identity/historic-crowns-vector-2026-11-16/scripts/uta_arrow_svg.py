import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from uta_arrow import model
from svgout import write, poly_d
p = json.load(open(sys.argv[1])); ink = sys.argv[3] if len(sys.argv) > 3 else '#000000'
polys = model(p)
xs = [x for q in polys for x, y in q]; ys = [y for q in polys for x, y in q]
print(write(sys.argv[2], [(poly_d(q), ink) for q in polys], (min(xs), min(ys), max(xs), max(ys)), sys.argv[4] if len(sys.argv) > 4 else 'Urban Transit Authority double-arrow (reconstruction)'))
