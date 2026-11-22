import sys, json, numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from fontpaths import *
from PIL import Image
res = json.load(open(sys.argv[1]))[int(sys.argv[2])]
fonts_dir = sys.argv[4]
font = load_font(fonts_dir + '/' + res['font'] if not res['font'].startswith('DejaVu') else '/usr/share/fonts/truetype/dejavu/' + res['font'], res['axes'])
mask = np.load('src/bcrc-red.npy') | np.load('src/bcrc-blue.npy')
H, W = mask.shape; upm = font['head'].unitsPerEm
allp = []
for L in res['letters']:
    rec, adv = glyph_record(font, L['ch'])
    allp.append(record_to_polys(rec, Affine.translate(L['dx'], L['dy']) @ glyph_T(res['size'], upm, 0, 0, res['addedSlant'], res['xscale']), 8))
r = raster(allp, (H, W)).astype(bool)
img = np.full((H, W, 3), 255, np.uint8)
img[mask & ~r] = (230, 40, 40); img[r & ~mask] = (40, 90, 230); img[r & mask] = (60, 60, 60)
Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save(sys.argv[3])
