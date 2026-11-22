"""review.py SOURCE.png RENDER.png OUT.webp [--overlay]
Side by side: source raster | vector render (scaled to same height) [| overlay if same aspect]."""
import sys
from PIL import Image, ImageChops, ImageOps
src=Image.open(sys.argv[1]).convert('RGBA'); ren=Image.open(sys.argv[2]).convert('RGBA')
def flat(im,bg=(255,255,255)):
    b=Image.new('RGBA',im.size,bg+(255,)); b.alpha_composite(im); return b.convert('RGB')
src=flat(src); ren=flat(ren)
H=240
src=src.resize((max(1,round(src.width*H/src.height)),H),Image.LANCZOS)
ren=ren.resize((max(1,round(ren.width*H/ren.height)),H),Image.LANCZOS)
tiles=[src,ren]
if '--overlay' in sys.argv:
    r=ren.resize(src.size,Image.LANCZOS)
    a=ImageOps.grayscale(src).point(lambda v:255 if v<128 else 0)
    b=ImageOps.grayscale(r).point(lambda v:255 if v<200 else 0)
    ov=Image.new('RGB',src.size,'white')
    px=ov.load();A=a.load();B=b.load()
    for y in range(src.height):
        for x in range(src.width):
            if A[x,y] and B[x,y]: px[x,y]=(60,60,60)
            elif A[x,y]: px[x,y]=(30,110,230)
            elif B[x,y]: px[x,y]=(230,40,160)
    tiles.append(ov)
W=sum(t.width for t in tiles)+12*(len(tiles)-1)
s=Image.new('RGB',(W,H),(235,235,235)); x=0
for t in tiles: s.paste(t,(x,0)); x+=t.width+12
s.save(sys.argv[3],quality=82)
