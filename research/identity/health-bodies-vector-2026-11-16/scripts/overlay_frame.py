"""Overlay for reconstructions drawn in the raster's own pixel coordinates (no refitting).
usage: python -I overlay_frame.py raster vector.svg out.webp [threshold] [scale]
Writes source | vector | overlay(source ink red, vector cyan, both dark) at `scale`x."""
import sys, re, subprocess, tempfile, os
import numpy as np
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
ras, vec, out = sys.argv[1:4]
thr = int(sys.argv[4]) if len(sys.argv) > 4 else 160
K = int(sys.argv[5]) if len(sys.argv) > 5 else 4
src = Image.open(ras)
if src.mode in ("P", "LA", "RGBA", "PA"):
    src = src.convert("RGBA"); b = Image.new("RGBA", src.size, (255, 255, 255, 255)); b.alpha_composite(src); src = b
src = src.convert("RGB").resize((src.width * K, src.height * K), Image.LANCZOS)
W, H = src.size
body = open(vec).read()
body = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W//K} {H//K}" width="{W}" height="{H}">', body, count=1)
with tempfile.TemporaryDirectory() as t:
    sv = os.path.join(t, "f.svg"); open(sv, "w").write(body); p = os.path.join(t, "v.png")
    subprocess.run(["node", os.path.join(here, "render.cjs"), sv, p, str(W)], check=True)
    v = Image.open(p).convert("RGBA")
m = np.asarray(src.convert("L")) < thr
vm = np.asarray(v)[..., 3] > 128
iou = (m & vm).sum() / max(1, (m | vm).sum())
ov = np.full(m.shape + (3,), 255, np.uint8)
ov[m & ~vm] = (230, 40, 40); ov[vm & ~m] = (0, 190, 220); ov[m & vm] = (60, 60, 60)
vr = Image.new("RGB", (W, H), "white"); vr.paste(v, (0, 0), v)
sheet = Image.new("RGB", (W * 3 + 20, H), (200, 200, 200))
sheet.paste(src, (0, 0)); sheet.paste(vr, (W + 10, 0)); sheet.paste(Image.fromarray(ov), (2 * W + 20, 0))
if sheet.width > 2400: sheet = sheet.resize((2400, round(sheet.height * 2400 / sheet.width)))
sheet.save(out, quality=82)
print(f"IoU={iou:.3f}")
