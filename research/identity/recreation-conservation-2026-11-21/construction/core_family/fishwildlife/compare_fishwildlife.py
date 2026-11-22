from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,cairosvg
P=Path(__file__).parent
r=np.array(Image.open(P/'reference.png').convert('L'))<128
rows=[]
for stem in ['iteration_01','iteration_02','fishwildlife']:
 svg=P/(stem+'.svg')
 cairosvg.svg2png(url=str(svg),write_to=str(P/(stem+'.png')),output_width=1000,output_height=1000)
 v=np.array(Image.open(P/(stem+'.png')).convert('RGBA'))[:,:,3]>127
 # Both masks use tight framing and independently normalized x/y extents.
 # Printed registration line at y~493 is excluded from the interior score.
 eligible=np.ones((1000,1000),bool);eligible[485:502,:]=False
 interior=eligible.copy();interior[:80,:]=False;interior[920:,:]=False;interior[:,:80]=False;interior[:,920:]=False
 def metric(m):return {'intersection_over_union':float((v&r&m).sum()/((v|r)&m).sum()),'source_ink_pixels':int((r&m).sum()),'vector_ink_pixels':int((v&m).sum())}
 metrics={'whole_mark':metric(eligible),'interior':metric(interior)}
 o=np.ones((1000,1000,3),np.uint8)*255;o[r]=[0,160,210];o[v]=[239,93,65];o[r&v]=[40,53,61]
 Image.fromarray(o).save(P/(stem+'_overlay.png'))
 white=Image.new('RGBA',(1000,1000),'white');white.alpha_composite(Image.open(P/(stem+'.png')).convert('RGBA'));white.convert('RGB').save(P/(stem+'_white.png'))
 rows.append({'iteration':stem,'metrics':metrics})
(P/'metrics.json').write_text(json.dumps(rows,indent=2))
# Clean side-by-side reviewer board at native source-pixel information, upscaled for legibility.
canvas=Image.new('RGB',(1860,755),'#f5f4ef');d=ImageDraw.Draw(canvas)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for j,(name,f) in enumerate([('1971 report specimen','reference.png'),('Geometric SVG reconstruction','fishwildlife_white.png'),('Registered comparison','fishwildlife_overlay.png')]):
 x=30+j*610;d.text((x,22),name,font=font,fill='#263c36');canvas.paste(Image.open(P/f).convert('RGB').resize((580,580)),(x,65))
d.text((30,673),'Cyan: scanned ink only     Orange: vector only     Charcoal: overlap',font=small,fill='#263c36')
d.text((30,708),'B.C. Department of Recreation and Conservation, 1971 report, printed DD15 / PDF page 16.',font=small,fill='#263c36')
canvas.save(P/'comparison.png')
print(json.dumps(rows))
