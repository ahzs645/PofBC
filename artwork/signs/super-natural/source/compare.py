from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
cfg=json.loads((ROOT/'design.json').read_text())
photo=Image.open(ROOT/'reference'/'Bennett-06.jpg').convert('RGB')
master=Image.open(OUT/'BC_Super_Natural_Welcome_Sign.png').convert('RGBA')
src=np.array([[0,190],[1200,190],[1200,1150],[0,1150]],float)
dst=np.array(cfg['photo']['boardCorners'],float)
A=[]; b=[]
for (x,y),(u,v) in zip(src,dst):
    A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
    b.extend([u,v])
H=np.r_[np.linalg.solve(A,b),1].reshape(3,3)
Hi=np.linalg.inv(H); Hi/=Hi[2,2]
# Compare by projecting the finished geometry into the supplied camera view.
# This transform is confined to verification; it is never applied to the SVG.
S=4
Hd=H.copy(); Hd[:2,:]*=S
Hdi=np.linalg.inv(Hd); Hdi/=Hdi[2,2]
placed=master.transform((photo.width*S,photo.height*S),Image.Transform.PERSPECTIVE,Hdi.flatten()[:8],resample=Image.Resampling.BICUBIC)
placed=placed.resize(photo.size,Image.Resampling.LANCZOS)
placed.save(ROOT/'projected.png')
mask=placed.getchannel('A')
clean=Image.new('RGBA',photo.size,'#dbe5e6')
clean.alpha_composite(placed)
overlay=Image.blend(photo.convert('RGBA'),Image.alpha_composite(photo.convert('RGBA'),placed),0.45)
box=(108,5,247,138)
tiles=[photo.crop(box),clean.convert('RGB').crop(box),overlay.convert('RGB').crop(box)]
scale=4
tw,th=tiles[0].width*scale,tiles[0].height*scale
W=tw*3+96; Hh=th+198
sheet=Image.new('RGB',(W,Hh),'#f5f3ee')
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
draw.text((24,20),'SUPER, NATURAL BC — GEOMETRY COMPARISON',font=font,fill='#183149')
labels=['SUPPLIED PHOTOGRAPH','VECTOR IN THE SAME VIEW','45% VECTOR OVERLAY']
for i,(tile,label) in enumerate(zip(tiles,labels)):
    x=24+i*(tw+24)
    draw.text((x,65),label,font=small,fill='#183149')
    sheet.paste(tile.resize((tw,th),Image.Resampling.LANCZOS),(x,98))
draw.text((24,th+120),'Board corners align the views. The original is 364 × 161 px; enlarging does not add detail.',font=small,fill='#485967')
draw.text((24,th+150),'Flag and serif outlines are reused from PofBC. Panel cut edge, font identity and paint colours remain interpretations.',font=small,fill='#485967')
sheet.save(OUT/'BC_Super_Natural_Comparison.png')
(ROOT/'projection.json').write_text(json.dumps({'matrix_master_to_photo':H.tolist(),'board_corners':dst.tolist(),'method':'four board corners; comparison only'},indent=2)+'\n')
print(OUT/'BC_Super_Natural_Comparison.png')
