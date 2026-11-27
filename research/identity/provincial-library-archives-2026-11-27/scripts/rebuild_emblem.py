"""Reconstruct a faithful two-ink, path-only SVG from the supplied engraving.

Prepares transparent support and black engraving independently, fits cubic curves,
and separates original lettering into named editable layers. The final SVG contains
no linked or embedded raster image and requires no installed fonts.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
from lxml import etree as ET
from vector_engine import trace,lib

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'reference'/'source-reference.png'
if not SOURCE.exists():
    SOURCE=ROOT/'upload'/'Historic Provincial Library & Archives Emblem(1).png'
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'

TEXT_ZONES=[
 ('provincial','PROVINCIAL',[(194,128),(285,91),(386,67),(480,58),(552,66),(611,100),(621,156),(547,145),(459,143),(351,158),(264,186),(198,221)]),
 ('library','LIBRARY',[(650,137),(722,106),(810,78),(910,72),(962,77),(964,147),(897,149),(811,166),(727,190),(654,220)]),
 ('archives','& ARCHIVES',[(364,256),(438,268),(539,272),(650,266),(774,246),(780,325),(681,339),(573,345),(458,344),(364,324)]),
 ('victoria','VICTORIA',[(179,412),(256,432),(331,425),(433,411),(435,485),(354,503),(254,505),(187,485)]),
 ('bc','B.C.',[(744,404),(815,402),(894,412),(893,470),(817,471),(744,465)]),
 ('splendor','SPLENDOR',[(257,1274),(321,1258),(390,1232),(455,1210),(508,1212),(516,1274),(454,1283),(371,1311),(287,1331),(257,1324)]),
 ('sine','SINE',[(546,1265),(649,1263),(653,1319),(545,1318)]),
 ('occasu','OCCASU.',[(688,1212),(743,1215),(822,1247),(914,1272),(915,1330),(848,1318),(776,1297),(694,1277)])
]

def remove_small(mask,minimum,connectivity=2):
    lab,count=ndi.label(mask,structure=ndi.generate_binary_structure(2,connectivity))
    sizes=np.bincount(lab.ravel())
    keep=sizes>=minimum
    keep[0]=False
    return keep[lab],int(np.count_nonzero((sizes[1:]<minimum))),int(sizes[1:][sizes[1:]<minimum].sum())

def layer(parent,ident,label):
    return ET.SubElement(parent,'{'+SVG+'}g',id=ident,attrib={'{'+INK+'}groupmode':'layer','{'+INK+'}label':label})

def path(parent,item,ident,fill='#000000'):
    return ET.SubElement(parent,'{'+SVG+'}path',id=ident,d=item['d'],fill=fill,attrib={'fill-rule':'nonzero'})

def point_in_polygon(x,y,polygon):
    inside=False
    for i in range(len(polygon)):
        x1,y1=polygon[i];x2,y2=polygon[(i+1)%len(polygon)]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:inside=not inside
    return inside

def classify(item):
    x1,y1,x2,y2=item['bbox'];x=(x1+x2)/2;y=(y1+y2)/2
    if x2-x1<120 and y2-y1<170:
        for ident,label,polygon in TEXT_ZONES:
            if point_in_polygon(x,y,polygon):return 'text-'+ident
    if x2-x1>450 or y2-y1>400:return 'framework'
    if 450<x<700 and 370<y<730:return 'lion-and-crown'
    if x<355 and 505<y<740:return 'stag-details'
    if x<450 and 730<y<1240:return 'stag-details'
    if x>790 and 540<y<1240:return 'ram-details'
    if 398<x<752 and 725<y<1190:return 'shield-details'
    if y>1188:return 'motto-details'
    if y<522:return 'scroll-details'
    return 'cord-and-staff-details'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--name',default='provincial-library-archives')
    parser.add_argument('--threshold',type=float,default=140)
    parser.add_argument('--blur',type=float,default=.26)
    parser.add_argument('--hole-area',type=float,default=.18)
    parser.add_argument('--speck-area',type=float,default=.2)
    parser.add_argument('--tolerance',type=float,default=.14)
    parser.add_argument('--scale',type=int,default=3)
    parser.add_argument('--shading-threshold',type=float,default=108)
    parser.add_argument('--clean-lettering',action=argparse.BooleanOptionalAction,default=True)
    args=parser.parse_args()
    (ROOT/'work').mkdir(exist_ok=True)
    im=Image.open(SOURCE).convert('RGBA');w,h=im.size;s=args.scale
    arr=np.asarray(im)
    # Filter premultiplied coverage to avoid growing RGB=0 transparent pixels into ink.
    matte=np.asarray(Image.alpha_composite(Image.new('RGBA',im.size,'white'),im).convert('L'))
    lum=Image.fromarray(matte).filter(ImageFilter.GaussianBlur(args.blur)).resize((w*s,h*s),Image.Resampling.LANCZOS)
    aa=im.getchannel('A').filter(ImageFilter.GaussianBlur(.22)).resize((w*s,h*s),Image.Resampling.LANCZOS)
    coverage=np.asarray(aa)>127
    coverage,exterior_specks,exterior_pixels=remove_small(coverage,3*s*s)
    # Preserve the tone of engraved fills independently of the heavier outlines.
    # Flat middle-tone fields are identified inside the shield; the narrow zone
    # beside each boundary stays on the structural threshold.
    threshold_map=np.full((h*s,w*s),args.threshold,dtype=np.float32)
    shade=np.zeros((h,w),dtype=bool)
    if args.shading_threshold is not None:
        values=matte.astype(float)
        tone=ndi.gaussian_filter(values,1.4)
        variance=ndi.uniform_filter(tone*tone,5)-ndi.uniform_filter(tone,5)**2
        stable=(np.sqrt(np.maximum(variance,0))<18)&(tone>55)&(tone<160)
        zone=np.zeros((h,w),dtype=bool)
        zone[730:922,400:751]=True
        zone[948:1128,400:751]=True
        yy,xx=np.ogrid[:h,:w]
        zone &= ~((yy>928)&((xx-575)**2+(yy-1137)**2<86**2))
        core=ndi.binary_opening(stable&zone,iterations=1)
        core,_,_=remove_small(core,12)
        shade=ndi.binary_dilation(core,iterations=2)&(tone<175)&zone
        field=ndi.gaussian_filter(shade.astype(float),.45)
        field=np.asarray(Image.fromarray(field.astype('float32'),mode='F').resize((w*s,h*s),Image.Resampling.BICUBIC))
        field=np.clip(field,0,1)
        threshold_map-=field*(args.threshold-args.shading_threshold)
    ink=(np.asarray(lum)<threshold_map)&coverage
    ink,black_specks,black_pixels=remove_small(ink,args.speck_area*s*s)
    # Fine fill texture and facial highlights are exempt from pinhole cleanup.
    lab,n=ndi.label(~ink,structure=ndi.generate_binary_structure(2,1))
    areas=np.bincount(lab.ravel())
    limits=np.full(areas.shape,args.hole_area*s*s)
    if args.shading_threshold is not None:
        keep_texture=np.asarray(Image.fromarray(shade).resize((w*s,h*s),Image.Resampling.NEAREST))
        protected=np.unique(lab[keep_texture]);limits[protected]=0
    if args.clean_lettering:
        lettering=Image.new('1',(w*s,h*s));ld=ImageDraw.Draw(lettering)
        for _,_,polygon in TEXT_ZONES:ld.polygon([(int(x*s),int(y*s)) for x,y in polygon],fill=1)
        text_labels=np.unique(lab[np.asarray(lettering)])
        limits[text_labels]=max(args.hole_area,3.2)*s*s
    fill=areas<limits;fill[0]=False
    n_holes=int(fill.sum());hole_pixels=int(areas[fill].sum())
    ink=(ink|fill[lab])&coverage
    white_paths=trace(coverage,scale=s,alpha=1.0,tolerance=args.tolerance)
    black_paths=trace(ink,scale=s,alpha=1.0,tolerance=args.tolerance)
    root=ET.Element('{'+SVG+'}svg',nsmap={None:SVG,'inkscape':INK},width='1116',height='1410',viewBox='0 0 1116 1410',version='1.1')
    ET.SubElement(root,'{'+SVG+'}title').text='Historic Provincial Library & Archives emblem - Victoria, B.C.'
    ET.SubElement(root,'{'+SVG+'}desc').text='Faithful cleaned vector reconstruction from the supplied raster engraving. Original ornamental lettering is retained as editable outlines. Transparent exterior, opaque white interiors, and black engraving. Cubic Bezier paths only; no embedded images, raster effects, or font dependencies. Automatic contour fitting with selective grain cleanup and visual verification; not an assertion of original master artwork.'
    meta=ET.SubElement(root,'{'+SVG+'}metadata')
    meta.text=json.dumps({'source':SOURCE.name,'sourceSize':[w,h],'method':'subpixel contour reconstruction with cubic Bezier fitting, separate opaque support and ink, and original outlined lettering','parameters':vars(args),'engine':lib.potrace_version().decode()},indent=2)
    restore=ROOT/'work'/'crown-backings.json'
    if not restore.exists():restore=Path(__file__).resolve().parent/'crown-backings.json'
    if restore.exists():
        restoration=layer(root,'crown-cap-backing','00 - Restored opaque crown-cap interiors')
        for i,d in enumerate(json.loads(restore.read_text())['paths']):
            ET.SubElement(restoration,'{'+SVG+'}path',id=f'crown-cap-backing-{i+1}',d=d,fill='#ffffff')
    backing=layer(root,'white-interiors','01 - White interiors and transparent cutouts')
    for i,item in enumerate(white_paths):path(backing,item,f'white-support-{i+1:04d}','#ffffff')
    groups={}
    names=[('framework','02 - Connected engraved framework'),('scroll-details','03 - Upper scroll engraving'),('cord-and-staff-details','04 - Cords and staffs'),('stag-details','05 - Stag engraving details'),('ram-details','06 - Ram engraving details'),('lion-and-crown','07 - Lion and crown engraving details'),('shield-details','08 - Shield engraving details'),('motto-details','09 - Motto scroll engraving')]
    for ident,label in names:groups[ident]=layer(root,ident,label)
    typ=layer(root,'original-lettering','10 - Original lettering as outlines')
    for ident,label,_ in TEXT_ZONES:groups['text-'+ident]=ET.SubElement(typ,'{'+SVG+'}g',id='text-'+ident,attrib={'{'+INK+'}label':label})
    counts={k:0 for k in groups}
    for i,item in enumerate(black_paths):
        group=classify(item);counts[group]+=1
        path(groups[group],item,f'{group}-{counts[group]:04d}')
    for g in list(groups.values()):
        if len(g)==0:g.getparent().remove(g)
    dest=ROOT/'output';dest.mkdir(exist_ok=True)
    target=dest/(args.name+'.svg')
    ET.ElementTree(root).write(target,xml_declaration=True,encoding='UTF-8',pretty_print=True)
    metrics={'source':[w,h],'parameters':vars(args),'paths':len(root.xpath('//*[local-name()="path"]')),'fitted_curve_segments':sum(x['segments'] for x in white_paths+black_paths),'groups':counts,'removed_black_specks':black_specks,'removed_black_area_source_px':black_pixels/s**2,'filled_white_pinholes':n_holes,'filled_white_area_source_px':hole_pixels/s**2,'removed_alpha_specks':exterior_specks,'svg_bytes':target.stat().st_size}
    (ROOT/'work'/(args.name+'-metrics.json')).write_text(json.dumps(metrics,indent=2))
    # These binary masks are QA intermediates only and are never embedded.
    Image.fromarray((ink*255).astype('uint8')).save(ROOT/'work'/(args.name+'-ink-mask.png'))
    Image.fromarray((coverage*255).astype('uint8')).save(ROOT/'work'/(args.name+'-coverage-mask.png'))
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
