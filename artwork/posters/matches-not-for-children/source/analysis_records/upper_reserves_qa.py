"""Fixed-registration diagnostic of manually constructed upper white reserves."""
from pathlib import Path
import json, subprocess
from xml.etree import ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd
from upper_reserves import RESERVES

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'upper-analysis'
OUT.mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'
PHOTO=ROOT/'work/reference-rectified.png'
FIXED=ROOT/'work/revision2/reference-reserve-mask-root.png'
PREVIOUS=ROOT/'work/revision3/prior/BCFS_Matches_Reconstructed.svg'

def raster(tree,name):
    svg=OUT/(name+'.svg'); png=OUT/(name+'.png')
    tree.write(svg,encoding='utf-8',xml_declaration=True)
    subprocess.run(['inkscape',str(svg),'--export-filename='+str(png),'--export-width=1000'],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return Image.open(png).convert('RGBA')

def build_master(revised):
    tree=ET.parse(PREVIOUS)
    if revised:
        for e in tree.iter():
            if e.get('id') in RESERVES:
                e.set('d',RESERVES[e.get('id')]);e.set('fill-rule','nonzero')
    return tree

def reserve_tree(tree):
    layer=tree.find('.//{'+NS+'}g[@id="paper-reserves"]')
    assert layer is not None
    root=ET.Element('{'+NS+'}svg',width='1000',height='1400',viewBox='0 0 1000 1400')
    root.append(layer)
    return ET.ElementTree(root)

before_master=build_master(False);after_master=build_master(True)
before=raster(reserve_tree(before_master),'v2-reserve')
after=raster(reserve_tree(after_master),'v3-upper-reserve')
before=np.asarray(before)[:,:,3]>127;after=np.asarray(after)[:,:,3]>127
photo=Image.open(PHOTO).convert('RGB')
target=np.asarray(Image.open(FIXED))>127
v2=raster(build_master(False),'v2-master').convert('RGB')
v3=raster(build_master(True),'v3-upper-master').convert('RGB')

def edge(a):return a&~nd.binary_erosion(a)
def metrics(mask,box):
    x0,y0,x1,y1=box;scope=np.zeros_like(target);scope[y0:y1,x0:x1]=True
    a=mask&scope;b=target&scope
    re=edge(target);ce=edge(mask)
    d=np.r_[nd.distance_transform_edt(~re)[ce&scope],nd.distance_transform_edt(~ce)[re&scope]]
    return {'intersection_over_union':float((a&b).sum()/(a|b).sum()),
            'mean_symmetric_edge_distance':float(d.mean()),
            'edge_distance_p95':float(np.quantile(d,.95)),
            'extra_white_pixels':int((a&~b).sum()),'missing_white_pixels':int((b&~a).sum())}

regions={'upper_beam_and_brace':[220,38,905,515],
         'top_beam':[220,38,905,182],
         'triangle_opening':[580,145,795,340],
         'brace_lower_edge':[495,180,795,475]}
report={'reference_mask':str(FIXED.relative_to(ROOT)),
        'construction':'Manually selected landmarks and authored Bezier curves. No masks or image contours generate the paths.',
        'comparison':'Exact fixed V2 target mask and original 1000 x 1400 perspective registration. All three other reserve components unchanged. Distances in normalized pixels.',
        'limitations':'The photographic edge includes print grain, camera blur and colour fringe. Scores describe photo fit, not physical dimensions or authenticity.',
        'regions':{name:{'bounds':box,'v2':metrics(before,box),'v3_upper_only':metrics(after,box)} for name,box in regions.items()}}
(OUT/'upper-reserve-metrics.json').write_text(json.dumps(report,indent=2))

font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,bold=False):return ImageFont.truetype(bold_path if bold else font_path,n)
def overlay(mask):
    rgb=np.asarray(photo);base=(rgb*.36+np.array([246,246,238])*.64).astype(np.uint8)
    base[target&~mask]=[0,137,157];base[mask&~target]=[205,39,133]
    return Image.fromarray(base)

ov2=overlay(before);ov3=overlay(after)
ov2.save(OUT/'v2-upper-overlay.png');ov3.save(OUT/'v3-upper-overlay.png')
for name,box in [('beam',(220,38,905,205)),('triangle',(575,140,805,337)),('diagonal',(485,170,805,480))]:
    x0,y0,x1,y1=box
    scale=2.0 if name=='beam' else 2.6
    w=round((x1-x0)*scale);h=round((y1-y0)*scale);gap=24;pad=28
    board=Image.new('RGB',(w*3+gap*2+pad*2,h+130),'#f5f3ec');d=ImageDraw.Draw(board)
    d.text((pad,18),'UPPER WHITE RESERVES / '+name.upper(),font=font(22,True),fill='#1d2424')
    for n,(im,label) in enumerate([(photo,'PHOTOGRAPH'),(v2,'REVISION 2'),(v3,'REVISION 3 UPPER CONTOURS')]):
        x=pad+n*(w+gap);d.text((x,59),label,font=font(17,True),fill='#4d625d')
        board.paste(im.crop(box).resize((w,h),Image.Resampling.LANCZOS),(x,88))
    board.save(OUT/(name+'-photo-v2-v3.png'))
    ov=Image.new('RGB',(w*2+gap+pad*2,h+135),'#f5f3ec');d=ImageDraw.Draw(ov)
    d.text((pad,15),'FIXED PHOTO MASK / '+name.upper(),font=font(22,True),fill='#1d2424')
    d.text((pad,46),'Teal: missing white   Magenta: excess white',font=font(16),fill='#4d625d')
    for n,(im,label) in enumerate([(ov2,'REVISION 2'),(ov3,'REVISION 3 UPPER CONTOURS')]):
        x=pad+n*(w+gap);d.text((x,77),label,font=font(16,True),fill='#4d625d')
        ov.paste(im.crop(box).resize((w,h),Image.Resampling.LANCZOS),(x,106))
    ov.save(OUT/(name+'-overlay-v2-v3.png'))
print(json.dumps(report,indent=2))
