#!/usr/bin/env python3
"""Make a comparison proof from the completed SVG render and supplied reference.

This only measures rasterized silhouettes and assembles the proof; it does not
generate or modify the logo contours. The logo is authored in build_ofc.py.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy import ndimage
import json
import argparse
import xml.etree.ElementTree as ET

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--aligned',type=Path)
args=parser.parse_args()
OUT=args.package.resolve()
REF=OUT/'reference'/'OFC_CIPO_official_747x341.png'
ALIGNED=args.aligned or OUT/'verification'/'OFC_source_aligned_4x.png'
reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(size,b=False): return ImageFont.truetype(bold if b else reg,size)

ref_im=Image.open(REF).convert('L')
render=Image.open(ALIGNED).convert('RGBA')
small=render.resize(ref_im.size,Image.Resampling.LANCZOS)
ref=np.asarray(ref_im)<128
vec=np.asarray(small)[:,:,3]>127
intersection=int((ref&vec).sum())
union=int((ref|vec).sum())
source_only=int((ref&~vec).sum())
vector_only=int((vec&~ref).sum())
overlap=intersection/union

overlay=np.full((ref.shape[0],ref.shape[1],3),255,dtype=np.uint8)
overlay[ref&vec]=[38,43,51]
overlay[ref&~vec]=[234,45,107]
overlay[vec&~ref]=[0,162,208]
over_im=Image.fromarray(overlay)
over_im.save(OUT/'verification'/'OFC_overlay_native.png')

def bounds(mask):
    ys,xs=np.where(mask)
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]

ns={'svg':'http://www.w3.org/2000/svg'}
tree=ET.parse(OUT/'Ocean_Falls_OFC.svg')
paths=tree.findall('.//svg:path',ns)
for forbidden in ['image','text','filter','mask','clipPath','use']:
    assert not tree.findall('.//svg:'+forbidden,ns), forbidden
assert len(paths)==3
assert len(ndimage.find_objects(ndimage.label(vec)[0]))==3
assert not vec[160,220]  # Inside the O counter: transparent, not a white cover.

metrics={
    'method':'Binary silhouette intersection over union; CIPO reference held fixed',
    'reference_size_px':list(ref_im.size),'render_size_px':list(render.size),
    'downsample':'4x SVG render downsampled to source dimensions with Pillow Lanczos',
    'reference_threshold':'grayscale < 128','vector_threshold':'alpha > 127',
    'registration':'none; shared 747 x 341 source coordinate canvas',
    'intersection_px':intersection,'union_px':union,
    'intersection_over_union':overlap,'source_only_px':source_only,'vector_only_px':vector_only,
    'reference_ink_area_px':int(ref.sum()),'vector_ink_area_px':int(vec.sum()),
    'source_bounds_xyxy_exclusive':bounds(ref),'vector_bounds_xyxy_exclusive':bounds(vec),
    'vector_path_count':len(paths),'embedded_images':0,'live_text':0,
    'interpretation':'A comparison to the supplied raster, not a percentage of historical design accuracy. Smooth curves intentionally omit pixel stair-stepping.',
}
(OUT/'verification'/'comparison_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')

W,H=1800,1500
sheet=Image.new('RGB',(W,H),'#F5F4EF')
d=ImageDraw.Draw(sheet)
ink='#182B35'; muted='#59646A'
d.text((70,52),'OCEAN FALLS CORPORATION',font=font(23,True),fill=muted)
d.text((70,94),'OFC vector reconstruction',font=font(52,True),fill=ink)
d.text((70,166),'Three manually constructed letterforms, checked against the supplied reference.',font=font(25),fill=muted)
d.line((70,214,1730,214),fill='#CFD5D4',width=2)

for x,label,sub in [(70,'01  Official CIPO reproduction','Supplied raster reproduction'),(920,'02  Reconstructed vector','Custom paths; smooth editable geometry')]:
    d.rounded_rectangle((x,248,x+810,672),radius=14,fill='white')
    d.text((x+28,273),label,font=font(27,True),fill=ink)
    d.text((x+28,313),sub,font=font(22),fill=muted)

source_preview=ref_im.convert('RGB').resize((710,324),Image.Resampling.NEAREST)
vector_preview=Image.alpha_composite(Image.new('RGBA',render.size,'white'),render).convert('RGB').resize((710,324),Image.Resampling.LANCZOS)
sheet.paste(source_preview,(120,346))
sheet.paste(vector_preview,(970,346))

d.text((70,719),'03  Registered overlay',font=font(32,True),fill=ink)
metric=f'{overlap*100:.2f}% silhouette overlap (intersection / union)'
d.text((70,765),metric,font=font(25),fill=muted)
legend=[('#262B33','Overlap'),('#EA2D6B','Reference only'),('#00A2D0','Vector only')]
lx=1000
for color,label in legend:
    d.rectangle((lx,735,lx+20,755),fill=color)
    d.text((lx+30,730),label,font=font(22),fill=ink)
    lx+=235 if label=='Reference only' else 185

d.rounded_rectangle((70,821,1730,1368),radius=14,fill='white')
# Native comparison pixels are intentionally shown with nearest-neighbour
# enlargement; resampling would hide the one-pixel edge differences.
overlay_large=over_im.resize((1195,546),Image.Resampling.NEAREST)
sheet.paste(overlay_large,(302,822))
d.text((70,1400),'Comparison at 747 x 341 px with no registration warp. Colour appears only where the silhouettes differ.',font=font(23),fill=muted)
d.text((70,1437),'This is a new reconstruction of the supplied mark; the original master geometry has not been recovered.',font=font(22),fill=muted)
sheet.save(OUT/'OFC_overlay_comparison.png')

# A simple presentation preview. The PNG is derived from the final SVG.
logo=Image.open(OUT/'Ocean_Falls_OFC_transparent.png').convert('RGBA')
logo.thumbnail((1580,630),Image.Resampling.LANCZOS)
preview=Image.new('RGBA',(1700,720),'white')
preview.alpha_composite(logo,((1700-logo.width)//2,(720-logo.height)//2))
preview.convert('RGB').save(OUT/'OFC_preview.png')

print(json.dumps(metrics,indent=2))

