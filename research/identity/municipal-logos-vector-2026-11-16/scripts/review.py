"""Review image: website raster (left) beside the vector render (right), on white and on grey.
usage: review.py raster.png vector.png out.webp"""
import sys
from PIL import Image
a = Image.open(sys.argv[1]).convert('RGBA'); b = Image.open(sys.argv[2]).convert('RGBA')
H = 200
a = a.resize((max(1, round(a.width * H / a.height)), H), Image.LANCZOS)
b = b.resize((max(1, round(b.width * H / b.height)), H), Image.LANCZOS)
W = a.width + b.width + 60
sheet = Image.new('RGB', (W, 2 * H + 60), (255, 255, 255))
grey = Image.new('RGB', (W, H + 30), (110, 110, 110)); sheet.paste(grey, (0, H + 30))
for y in (15, H + 45):
    sheet.paste(a, (20, y), a); sheet.paste(b, (a.width + 40, y), b)
sheet.save(sys.argv[3], quality=80)
