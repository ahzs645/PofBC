"""Overlay check: fit the SVG's rendering to the raster's ink box, and write source | vector | overlay.
Overlay: source ink red, vector ink cyan, agreement dark. Prints IoU of ink masks.
usage: python -I overlay.py raster.png vector.svg out.webp [threshold] [--dark]"""
import sys, subprocess, tempfile, os
import numpy as np
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
ras, vec, out = sys.argv[1:4]
thr = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 160
dark = "--dark" in sys.argv
src = Image.open(ras)
if src.mode in ("P", "LA", "RGBA", "PA"):
    src = src.convert("RGBA"); bgc = (40, 40, 40) if dark else (255, 255, 255)
    b = Image.new("RGBA", src.size, bgc + (255,)); b.alpha_composite(src); src = b
src = src.convert("RGB")
g = np.asarray(src.convert("L")).astype(int)
m = (g > 255 - thr) if dark else (g < thr)
ys, xs = np.where(m); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
W = (box[2] - box[0]) * 4
with tempfile.TemporaryDirectory() as t:
    p = os.path.join(t, "v.png")
    subprocess.run(["node", os.path.join(here, "render.cjs"), vec, p, str(W)], check=True)
    v = Image.open(p).convert("RGBA")
a = np.asarray(v)[..., 3] > 128
vy, vx = np.where(a); v = v.crop((vx.min(), vy.min(), vx.max() + 1, vy.max() + 1))
v = v.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
vm = np.zeros(m.shape, bool); vm[box[1]:box[3], box[0]:box[2]] = np.asarray(v)[..., 3] > 128
iou = (m & vm).sum() / max(1, (m | vm).sum())
ov = np.full(m.shape + (3,), 255, np.uint8)
ov[m & ~vm] = (230, 40, 40); ov[vm & ~m] = (0, 190, 220); ov[m & vm] = (40, 40, 40)
vr = Image.new("RGB", src.size, (40, 40, 40) if dark else (255, 255, 255)); vv = Image.new("RGBA", src.size); vv.paste(v, box[:2]); vr.paste(vv, (0, 0), vv)
H = src.height; sheet = Image.new("RGB", (src.width * 3 + 20, H), (200, 200, 200))
sheet.paste(src, (0, 0)); sheet.paste(vr, (src.width + 10, 0)); sheet.paste(Image.fromarray(ov), (2 * src.width + 20, 0))
if sheet.width > 1500: sheet = sheet.resize((1500, round(sheet.height * 1500 / sheet.width)))
sheet.save(out, quality=80)
print(f"IoU={iou:.3f} box={box}")
