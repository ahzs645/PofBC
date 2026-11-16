"""Montage page thumbnails. usage: montage.py out.png img1 img2 ..."""
import sys
from PIL import Image, ImageDraw
out, files = sys.argv[1], sys.argv[2:]
ims = [Image.open(f).convert('RGB') for f in files]
for im in ims: im.thumbnail((260, 260))
cols = 5; rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * 270, rows * 280), (200, 200, 200))
d = ImageDraw.Draw(sheet)
for i, (im, f) in enumerate(zip(ims, files)):
    x, y = (i % cols) * 270 + 5, (i // cols) * 280 + 15
    sheet.paste(im, (x, y)); d.text((x, y - 12), f.split('-')[-1], fill=(0, 0, 0))
sheet.save(out)
