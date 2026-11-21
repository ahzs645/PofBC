"""Diagnostic only: compare the joint reconstruction at one fixed registration."""
from pathlib import Path
import json,subprocess
from xml.etree import ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
from crack_joint import joint_group,PATCH

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'joint-analysis';OUT.mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'
MASTER=HERE/'prior/BCFS_Matches_Reconstructed.svg'
REFERENCE=ROOT/'work/reference-rectified.png'

def build(revised=False):
    tree=ET.parse(MASTER)
    if revised:
        threads=tree.find('.//{'+NS+'}g[@id="thread-and-ties"]')
        removed=0
        for e in list(threads):
            if e.get('d','').startswith('M330 779 L342 796'):
                threads.remove(e);removed+=1
        assert removed==1,'Expected exactly one obsolete hip star path'
        g=tree.find('.//{'+NS+'}g[@id="matchstick-illustration"]')
        assert g is not None
        component=ET.fromstring('<svg xmlns="'+NS+'">'+joint_group()+'</svg>')
        for e in component:g.append(e)
    return tree

def render(tree,name,box=None,scale=1):
    root=tree.getroot()
    if box:
        x0,y0,x1,y1=box
        root.set('viewBox',f'{x0} {y0} {x1-x0} {y1-y0}')
        root.set('width',str((x1-x0)*scale));root.set('height',str((y1-y0)*scale))
    p=OUT/(name+'.svg');png=OUT/(name+'.png')
    tree.write(p,encoding='utf-8',xml_declaration=True)
    subprocess.run(['inkscape',str(p),'--export-filename='+str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return Image.open(png).convert('RGB')

photo=Image.open(REFERENCE).convert('RGB')
before=render(build(),'joint-v3-full')
after=render(build(True),'joint-v4-full')
P=np.asarray(photo);B=np.asarray(before);A=np.asarray(after)
regions={'local_joint':[320,763,354,804],
         'fracture_and_splinters':[325,766,345,799],
         'context':[307,758,372,826]}

def edge(a):return a&~nd.binary_erosion(a)
def measure(ref,can,box):
    x0,y0,x1,y1=box;scope=np.zeros_like(ref);scope[y0:y1,x0:x1]=True
    r=ref&scope;c=can&scope
    re=edge(ref);ce=edge(can)
    ds=np.r_[nd.distance_transform_edt(~re)[ce&scope],nd.distance_transform_edt(~ce)[re&scope]]
    return {'iou':float((r&c).sum()/(r|c).sum()),
            'dice':float(2*(r&c).sum()/(r.sum()+c.sum())),
            'mean_symmetric_edge_distance':float(ds.mean()),
            'edge_distance_p95':float(np.quantile(ds,.95)),
            'excess_ink_pixels':int((c&~r).sum()),'missing_ink_pixels':int((r&~c).sum())}

results={}
for threshold in [90,110,125,140]:
    r=P.max(2)<threshold;b=B.max(2)<threshold;a=A.max(2)<threshold
    results[str(threshold)]={name:{'bounds':box,'v3':measure(r,b,box),'v4':measure(r,a,box)} for name,box in regions.items()}
    if threshold==125:
        Image.fromarray((r*255).astype('uint8')).save(OUT/'reference-ink-mask-125.png')
        target,old,new=r,b,a

report={'registration':'Existing 1000 x 1400 perspective-normalized photograph, unchanged for both versions.',
        'mask':'Dark ink classified by max(R,G,B) < threshold. Main threshold 125; 90/110/140 are fixed sensitivity checks. Masks are QA only, not construction data.',
        'units':'Normalized source pixels. These measurements do not establish physical print size or authenticity.',
        'thresholds':results}
(OUT/'joint-metrics.json').write_text(json.dumps(report,indent=2))

font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(bold if b else font_path,n)
box=(307,758,372,826);scale=9;cw=(box[2]-box[0])*scale;ch=(box[3]-box[1])*scale
orig=photo.crop(box).resize((cw,ch),Image.Resampling.BICUBIC)
bc=render(build(),'joint-v3-detail',box,scale)
ac=render(build(True),'joint-v4-detail',box,scale)
board=Image.new('RGB',(cw*3+96,ch+152),'#f5f3ec');d=ImageDraw.Draw(board)
d.text((24,17),'BROKEN MATCH JUNCTION / STRUCTURAL RECONSTRUCTION',font=font(24,True),fill='#1d2424')
for i,(im,label) in enumerate([(orig,'PHOTOGRAPH'),(bc,'REVISION 3'),(ac,'REVISION 4')]):
    x=24+i*(cw+24);d.text((x,58),label,font=font(18,True),fill='#52635c');board.paste(im,(x,90))
d.text((24,ch+112),'Same registration and crop; vector geometry is rendered directly at enlarged scale.',font=font(18),fill='#52635c')
board.save(OUT/'joint-photo-v3-v4.png')

def overlay(can):
    rgb=(P*.35+np.array([245,245,238])*.65).astype(np.uint8)
    rgb[target&~can]=[0,137,157];rgb[can&~target]=[205,39,133]
    rgb[target&can]=[35,48,49]
    return Image.fromarray(rgb).crop(box).resize((cw,ch),Image.Resampling.NEAREST)
ov=Image.new('RGB',(cw*2+72,ch+160),'#f5f3ec');d=ImageDraw.Draw(ov)
d.text((24,16),'FIXED SOURCE INK OVERLAY / JOINT',font=font(24,True),fill='#1d2424')
d.text((24,51),'Teal = missing ink   Magenta = excess ink   Dark = shared ink',font=font(17),fill='#52635c')
for i,(can,label) in enumerate([(old,'REVISION 3'),(new,'REVISION 4')]):
    x=24+i*(cw+24);d.text((x,80),label,font=font(18,True),fill='#52635c');ov.paste(overlay(can),(x,110))
ov.save(OUT/'joint-overlay-v3-v4.png')
print(json.dumps(results['125'],indent=2))
