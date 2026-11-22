import sys, numpy as np, cv2
from PIL import Image
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from measure import *
g, b = load(sys.argv[1])
H, W = b.shape
# centre: fit outer silhouette circle (largest component's outer contour)
cs, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float) + 0.5
cc = fit_circle(c); print('outer silhouette circle', cc.round(2))
angs = np.radians(np.arange(0, 360, 1.0))
rs = np.arange(0, cc[2] + 6, 0.5)
prof = []
for a in angs:
    xs = (cc[0] + rs * np.cos(a)).astype(int).clip(0, W - 1); ys = (cc[1] + rs * np.sin(a)).astype(int).clip(0, H - 1)
    prof.append(b[ys, xs])
prof = np.array(prof)
med = prof.mean(0)
for r, v in zip(rs[::2], med[::2]):
    if r > cc[2] * 0.55: print('%6.1f %s' % (r, '#' * int(v * 40)))
