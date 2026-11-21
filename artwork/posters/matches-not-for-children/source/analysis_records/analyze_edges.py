#!/usr/bin/env python3
"""Review constructed edges against a fixed photo mask; never author contours."""
from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
REV=ROOT/'work/revision3'
OUT=ROOT/'output/BC_Forest_Service_Matches'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

def font(n,b=False):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',n)

def raster_reserve():
    master=ET.parse(OUT/'BCFS_Matches_Reconstructed.svg').getroot()
    # Evaluate geometric coverage, excluding local coloured pigment deposits.
    g=master.find('.//{'+NS+'}g[@id="white-reserves-v3"]')
    root=ET.Element('{'+NS+'}svg',{'width':'1000','height':'1400','viewBox':'0 0 1000 1400'})
    root.append(g)
    s=REV/'revised-reserve.svg';p=REV/'revised-reserve.png'
    ET.ElementTree(root).write(s,encoding='utf-8',xml_declaration=True)
    subprocess.run(['inkscape',str(s),'--export-type=png','--export-filename='+str(p),'--export-width=1000'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return np.array(Image.open(p).convert('RGBA'))[:,:,3]>127

def edge(a):return a&~nd.binary_erosion(a)

def measures(ref,can,valid,box):
    x0,y0,x1,y1=box;scope=np.zeros_like(valid);scope[y0:y1,x0:x1]=True;scope&=valid
    r=ref&scope;c=can&scope;re=edge(ref)&valid;ce=edge(can)&valid
    dr=nd.distance_transform_edt(~re);dc=nd.distance_transform_edt(~ce)
    d1=dr[ce&scope];d2=dc[re&scope];dd=np.r_[d1,d2]
    m={'intersection_over_union':float((r&c).sum()/(r|c).sum()),
       'extra_white_pixels':int((c&~r).sum()),'missing_white_pixels':int((r&~c).sum()),
       'reference_area_pixels':int(r.sum()),'candidate_area_pixels':int(c.sum()),
       'mean_symmetric_edge_distance_pixels':float(dd.mean()),'edge_distance_p95_pixels':float(np.quantile(dd,.95))}
    for t in [1,2,3]:
        p=float(np.mean(d1<=t));rec=float(np.mean(d2<=t))
        m[f'boundary_within_{t}px']={'precision':p,'recall':rec,'f1':2*p*rec/(p+rec)}
    return m

def overlay(ref,can,photo,valid):
    a=(photo*.35+np.array([245,245,238])*.65).astype('uint8')
    a[(ref&~can)&valid]=[0,137,157];a[(can&~ref)&valid]=[205,39,133]
    ink=(photo.max(2)<125)&(photo[:,:,2]>12);i=ink&(ref|can)&valid
    a[i]=(photo[i]*.4+np.array([37,41,46])*.6).astype('uint8')
    return Image.fromarray(a)

def triptych(images,rows,title,subtitle,path):
    width=1720;col=520;xs=[40,600,1160];y=150
    heights=[round(min(col/(b[2]-b[0]),530/(b[3]-b[1]))*(b[3]-b[1])) for _,b in rows]
    board=Image.new('RGB',(width,150+sum(h+85 for h in heights)+68),'#f5f3ec');d=ImageDraw.Draw(board)
    d.text((40,25),title,font=font(31,True),fill='#1d2424')
    d.text((40,73),subtitle,font=font(20),fill='#53615f')
    for x,label in zip(xs,['PHOTOGRAPH','REVISION 2','REVISION 3']):d.text((x,116),label,font=font(17,True),fill='#435b57')
    for (label,box),h in zip(rows,heights):
        d.text((40,y),label,font=font(16,True),fill='#53615f');y+=29
        scale=min(col/(box[2]-box[0]),530/(box[3]-box[1]))
        size=(round((box[2]-box[0])*scale),h)
        for x,im in zip(xs,images):board.paste(im.crop(box).resize(size,Image.Resampling.BICUBIC),(x,y))
        y+=h+56
    d.text((40,y-4),'Identical registration and crop in each column. The photograph retains printing wear and camera blur.',font=font(18),fill='#53615f')
    board.save(path)

def main():
    prior=REV/'prior'; photo=np.array(Image.open(prior/'review/Reference_Perspective_Normalized.png').convert('RGB'))
    ref=np.array(Image.open(prior/'review/diagnostics/reference-reserve-mask-root.png'))>127
    old=np.array(Image.open(prior/'review/diagnostics/revised-reserve-mask.png'))>127
    current=raster_reserve();yy,xx=np.indices(ref.shape)
    valid=(((xx-914.5)/74)**2+((yy-1217.5)/90)**2>1)&(yy<1250)&(xx>140)&(xx<925)&(yy>30)
    baseline=json.loads((prior/'review/White_Edge_Measurements.json').read_text())
    results={name:{'bounds':r['bounds'],'previous':measures(ref,old,valid,r['bounds']),'revised':measures(ref,current,valid,r['bounds'])} for name,r in baseline['regions'].items()}
    report={'revision':3,'previous_revision':2,'registration':baseline['registration'],'method':baseline['method'],'regions':results}
    report['method']['boundary_tolerance']='For tolerances 1,2,3 normalized pixels, precision is the fraction of candidate boundary within tolerance of the reference; recall is the converse; F1 is their harmonic mean. The same fixed photographic mask is used for both versions.'
    report['method']['construction']='Manually authored Bezier contours and deliberately placed brush-edge detail; the mask is used only for review.'
    report['method']['artwork_masks']='Alpha coverage of the reserve geometry alone, excluding the optional coloured pigment deposits, rendered at1000x1400 and threshold127/255. V2 has the same geometric coverage in its paper-reserve layer.'
    for p in [REV/'White_Edge_Measurements.json',OUT/'review/White_Edge_Measurements.json']:p.write_text(json.dumps(report,indent=2))
    Image.fromarray((current*255).astype('uint8')).save(REV/'revised-reserve-mask.png')
    a=overlay(ref,old,photo,valid);b=overlay(ref,current,photo,valid)
    a.save(REV/'old-white-overlay.png');b.save(REV/'new-white-overlay.png')
    a.save(OUT/'review/White_Edge_Overlay_previous.png');b.save(OUT/'review/White_Edge_Overlay_revised.png')
    images=[Image.fromarray(photo),Image.open(prior/'BCFS_Matches_Preview.png').convert('RGB').resize((1000,1400),Image.Resampling.LANCZOS),Image.open(OUT/'BCFS_Matches_Preview.png').convert('RGB').resize((1000,1400),Image.Resampling.LANCZOS)]
    triptych(images,[('UPPER TIE AND THREAD',(286,62,421,222)),('CHILD HEAD AND NECK',(278,470,403,630))],
             'WHITE EDGES · CONTINUED REFINEMENT','The original screenshot areas, compared directly with Revision 2.',OUT/'BCFS_White_Edge_Details.png')
    triptych(images,[('DIAGONAL OPENING AND BRACE',(555,145,802,372)),('CHILD LEGS',(238,742,540,914)),('UPRIGHT SHOULDER AND BROKEN TAPER',(750,585,884,765))],
             'EDGE CONTOURS · REVISION 2 TO REVISION 3','Curved brush lobes and small recesses replace the remaining facets and steps.',OUT/'BCFS_Contour_Refinement.png')
    board=Image.new('RGB',(1560,1555),'#f5f3ec');d=ImageDraw.Draw(board)
    d.text((45,28),'WHITE EDGE OVERLAY · REVISION 2 / REVISION 3',font=font(29,True),fill='#1d2424')
    for x,c,label in [(45,'#00899d','White missing from the reconstruction'),(765,'#cd2785','White extending beyond the photo mask')]:
        d.rectangle((x,85,x+22,107),fill=c);d.text((x+34,82),label,font=font(18),fill='#1d2424')
    for x,label,im in [(45,'REVISION 2',a),(800,'REVISION 3',b)]:
        d.text((x,128),label,font=font(17,True),fill='#53615f');board.paste(im.resize((710,994),Image.Resampling.LANCZOS),(x,165))
    d.text((45,1192),'Closer boundary placement on the same photographic reference',font=font(23,True),fill='#1d2424')
    for x,label in [(45,'Region'),(850,'V2 mean edge distance'),(1170,'V3 mean edge distance')]:d.text((x,1232),label,font=font(17,True),fill='#53615f')
    for i,name in enumerate(['All visible illustration reserve','Upper beam and diagonal brace','Child arms, body and legs','Upright support']):
        y=1270+i*43;r=results[name];d.text((45,y),name,font=font(18),fill='#1d2424')
        for x,key in [(850,'previous'),(1170,'revised')]:d.text((x,y),f'{r[key]["mean_symmetric_edge_distance_pixels"]:.2f} px',font=font(18),fill='#1d2424')
    d.text((45,1470),'Pixels refer to the 1000 × 1400 comparison plane. Hidden reserve beneath the seal is excluded.',font=font(17),fill='#53615f')
    board.save(OUT/'BCFS_White_Edge_Overlay.png')
    for name,r in results.items():print(name, json.dumps({k:{a:round(v,5) for a,v in r[k].items() if isinstance(v,float)} for k in ['previous','revised']}))

if __name__=='__main__':main()
