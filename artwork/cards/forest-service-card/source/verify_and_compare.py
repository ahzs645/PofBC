#!/usr/bin/env python3
"""Render the vector card, inspect export structure, and make comparison proofs."""
from pathlib import Path
import json, hashlib, copy
from collections import Counter
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import cairosvg
import fitz
from PIL import Image, ImageDraw, ImageFont

BASE=Path(__file__).resolve().parent.parent
ART=BASE/'artwork'
REV=BASE/'review'
SRC=BASE/'source'
REV.mkdir(exist_ok=True)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def font(size,bold=False):
    return ImageFont.truetype(bold_path if bold else font_path,size)

def tags(path):
    root=ET.parse(path).getroot()
    counts=Counter(e.tag.rsplit('}',1)[-1] for e in root.iter())
    ids=[e.get('id') for e in root.iter() if e.get('id')]
    return root,dict(counts),len(ids)==len(set(ids))

def validate():
    out={'vector_files':{},'pdf_files':{},'source_logo_sha256':hashlib.sha256((SRC/'website-logo.svg').read_bytes()).hexdigest()}
    original=ET.parse(SRC/'website-logo.svg').getroot()
    source_paths=Counter(e.get('d') for e in original.iter() if e.tag.endswith('}path'))
    for p in ART.glob('*.svg'):
        root,count,unique=tags(p)
        all_paths=Counter(e.get('d') for e in root.iter() if e.tag.endswith('}path'))
        preserve=not bool(source_paths-all_paths)
        checks={'elements':count,'unique_ids':unique,'all_source_logo_paths_preserved':preserve,
                'embedded_raster_images':count.get('image',0),'live_text_objects':count.get('text',0),
                'external_references':[v for e in root.iter() for k,v in e.attrib.items() if k.endswith('href') and not v.startswith('#')]}
        assert unique and preserve and checks['embedded_raster_images']==0 and checks['live_text_objects']==0 and not checks['external_references'],checks
        out['vector_files'][p.name]=checks
    for p in ART.glob('*.pdf'):
        d=fitz.open(p)
        page=d[0]
        checks={'pages':len(d),'images':len(page.get_images(full=True)),'fonts':len(page.get_fonts(full=True)),
                'page_size_mm':[round(page.rect.width*25.4/72,4),round(page.rect.height*25.4/72,4)]}
        assert checks['images']==0 and checks['fonts']==0 and len(d)==1,checks
        out['pdf_files'][p.name]=checks
        # Independent PDF rasterization; production files remain entirely vector.
        page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(REV/(p.stem+'-pdf-proof.png'))
    return out

def comparisons(validation):
    ref=Image.open(REV/'reference-rectified.png').convert('RGB')
    for stem in ['forest-service-card','forest-service-card-original-logo']:
        cairosvg.svg2png(url=str(ART/(stem+'-white.svg')),write_to=str(REV/(stem+'-white-native.png')),output_width=1050,output_height=500)
    clean=Image.open(ART/'forest-service-card-preview.png').convert('RGB').resize((1050,500),Image.Resampling.LANCZOS)
    exact=Image.open(ART/'forest-service-card-original-logo-preview.png').convert('RGB').resize((1050,500),Image.Resampling.LANCZOS)
    vector_gray=np.asarray(Image.open(REV/'forest-service-card-white-native.png').convert('L'))
    vec=vector_gray<190
    a=np.asarray(ref)
    gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY).astype('float32')
    background=cv2.morphologyEx(gray,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31)))
    contrast=(background-gray)/np.maximum(background,1)
    observed=contrast>.16
    rois={'logo':[270,22,785,285],'line_1':[150,303,903,353],'line_2':[260,363,785,406],
          'frame_and_ink':[85,24,965,460]}
    m=np.zeros(observed.shape,dtype=bool)
    m[22:460,85:965]=True
    observed &= m
    vec &= m
    diagnostic=np.full((500,1050,3),255,dtype='uint8')
    diagnostic[observed&vec]=[28,35,42]
    diagnostic[observed&~vec]=[205,36,115]
    diagnostic[vec&~observed]=[0,149,194]
    overlay=Image.fromarray(diagnostic)
    overlay.save(REV/'forest-service-card-ink-overlay.png')
    metrics={}
    for name,(x0,y0,x1,y1) in rois.items():
        v=vec[y0:y1,x0:x1];o=observed[y0:y1,x0:x1]
        metrics[name]={'roi':[x0,y0,x1,y1],'intersection_over_union':float((v&o).sum()/max((v|o).sum(),1)),
                       'reference_ink_pixels':int(o.sum()),'vector_ink_pixels':int(v.sum())}
    sensitivity={}
    for threshold in [.12,.16,.20]:
        o=(contrast>threshold)&m
        sensitivity[str(threshold)]={}
        for name,(x0,y0,x1,y1) in rois.items():
            rr=o[y0:y1,x0:x1];vv=vec[y0:y1,x0:x1]
            sensitivity[str(threshold)][name]=float((rr&vv).sum()/max((rr|vv).sum(),1))
    validation['diagnostic_overlap']={'method':'Reference rectified from measured printed frame. Reference ink = relative dark contrast >0.16 against a paper field estimated by 31 px elliptical morphological closing. Vector ink = grayscale <190 at 1050x500. No per-region re-registration after assembly. Paper damage outside artwork excluded. These values are threshold-sensitive diagnostics, not authenticity or fidelity percentages.',
                                      'regions':metrics,
                                      'reference_threshold_sensitivity':sensitivity,
                                      'caveats':['Source emblem is a different reconstruction; its component geometry does not perfectly match the photograph.',
                                                 'Clean reconstructed text restores ink absent in the worn photograph.',
                                                 'Photography, thresholding, resampling and the approximate typeface affect the overlay.']}
    # Four equally scaled panels so the exact-logo variant can be compared fairly.
    proof=Image.new('RGB',(2220,1310),'#F5F3EC')
    d=ImageDraw.Draw(proof)
    d.text((40,26),'FOREST SERVICE CARD / VECTOR RECONSTRUCTION',font=font(32,True),fill='#202923')
    d.text((40,75),'Same 1050 x 500 artboard throughout. The supplied photograph is corrected using the printed frame.',font=font(22),fill='#566156')
    panels=[(40,160,ref,'01 / PHOTOGRAPH, PERSPECTIVE CORRECTED'),
            (1130,160,clean,'02 / VECTOR, BOUGHS FITTED TO CARD'),
            (40,755,overlay,'03 / INK OVERLAP, FITTED VECTOR'),
            (1130,755,exact,'04 / VECTOR, ORIGINAL LOGO PROPORTIONS')]
    for x,y,im,title in panels:
        d.text((x,y-40),title,font=font(22,True),fill='#202923')
        proof.paste(im,(x,y));d.rectangle((x,y,x+1049,y+499),outline='#D3CEBF',width=1)
    d.text((40,677),'Type: rebuilt C059 Bold outlines, condensed and fitted; original typeface unconfirmed.',font=font(20),fill='#566156')
    d.text((1130,677),'The central seal is preserved; existing bough groups are repositioned and scaled.',font=font(20),fill='#566156')
    d.text((40,1275),'Ink overlay: dark = shared; magenta = photograph only; cyan = vector only. Wear and ink weight create expected differences.',font=font(20),fill='#566156')
    proof.save(REV/'forest-service-card-comparison.png')

if __name__=='__main__':
    v=validate();comparisons(v)
    (REV/'verification.json').write_text(json.dumps(v,indent=2))
    print(json.dumps(v,indent=2))
