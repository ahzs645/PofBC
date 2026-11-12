#!/usr/bin/env python3
"""Rebuild the BCSC 1983 wordmark from a small, manually designed glyph model.

No image-to-path tracing, font outlines or raster embeds are used in the logo.
The reference image is read only to make the separate comparison proof.
"""
from pathlib import Path
import math, json, hashlib, shutil, zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import fitz

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
# The delivered source folder rebuilds into a sibling 'regenerated' folder.
if SCRIPT_DIR.name == 'source':
    OUT = ROOT / 'regenerated'
    REF = ROOT / 'reference' / 'BCSC_1983_Source_Scan.png'
    WORK = OUT / 'checks'
else:
    OUT = ROOT / 'output' / 'BC_Systems_Corporation_Vector'
    REF = ROOT / 'work' / 'reference' / 'bc-systems-1983-logo.png'
    WORK = ROOT / 'work'
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

# Design units: cap height 224, with a common 30 degree italic shear.
# These are reconstructed dimensions, not recovered official specifications.
CAP = 224.0
SLANT = math.tan(math.radians(30.0))
ADVANCES = [('B', 0.0), ('C', 262.0), ('S', 522.0), ('C', 782.0)]
WIDTH = 1006.0 + SLANT * CAP
MARGIN = 12.0

# Upright glyph skeletons. Q denotes a quadratic corner; all other edges are
# straight. Two C instances share this exact master, differing by translation.
B = [
 ('M',7,0),('L',187,0),('Q',194,0,194,7),('L',194,81),
 ('Q',194,87,200,91),('L',219,103),('Q',224,106,224,113),
 ('L',224,217),('Q',224,224,217,224),('L',7,224),
 ('Q',0,224,0,217),('L',0,7),('Q',0,0,7,0),('Z',),
 # Upper counter.
 ('M',86,26),('L',151,26),('Q',157,26,157,32),('L',157,83),
 ('Q',157,89,151,89),('L',86,89),('Q',80,89,80,83),
 ('L',80,32),('Q',80,26,86,26),('Z',),
 # Lower counter, offset to follow the stepped bowl/stem construction.
 ('M',122,117),('L',186,117),('Q',192,117,192,123),
 ('L',192,190),('Q',192,196,186,196),('L',122,196),
 ('Q',116,196,116,190),('L',116,123),('Q',116,117,122,117),('Z',)
]
C = [
 ('M',7,0),('L',217,0),('Q',224,0,224,7),('L',224,67),
 ('Q',224,72,219,72),('L',198,72),('Q',192,72,192,66),
 ('L',192,32),('Q',192,26,186,26),('L',86,26),
 ('Q',80,26,80,32),('L',80,80),('Q',80,87,87,92),
 ('L',110,105),('Q',116,108,116,115),('L',116,189),
 ('Q',116,196,123,196),('L',186,196),('Q',192,196,192,190),
 ('L',192,146),('Q',192,140,198,140),('L',218,140),
 ('Q',224,140,224,146),('L',224,217),('Q',224,224,217,224),
 ('L',7,224),('Q',0,224,0,217),('L',0,7),('Q',0,0,7,0),('Z',)
]
S = [
 ('M',7,0),('L',217,0),('Q',224,0,224,7),('L',224,67),
 ('Q',224,72,218,72),('L',198,72),('Q',192,72,192,66),
 ('L',192,32),('Q',192,26,186,26),('L',38,26),
 ('Q',32,26,32,32),('L',32,81),('Q',32,88,39,88),
 ('L',217,88),('Q',224,88,224,95),('L',224,217),
 ('Q',224,224,217,224),('L',7,224),('Q',0,224,0,217),
 ('L',0,146),('Q',0,140,6,140),('L',26,140),
 ('Q',32,140,32,146),('L',32,189),('Q',32,196,39,196),
 ('L',101,196),('Q',108,196,108,189),('L',108,123),
 ('Q',108,116,101,116),('L',7,116),('Q',0,116,0,109),
 ('L',0,7),('Q',0,0,7,0),('Z',)
]
GLYPHS={'B':B,'C':C,'S':S}

def number(n):
    return f'{n:.4f}'.rstrip('0').rstrip('.')

def path_d(commands, origin=0, transform=None):
    parts=[]
    for cmd in commands:
        values=[]
        for i in range(1,len(cmd),2):
            x=cmd[i]+origin+SLANT*(CAP-cmd[i+1]); y=cmd[i+1]
            if transform: x,y=transform(x,y)
            values.extend([number(x),number(y)])
        parts.append(cmd[0]+' '.join(values))
    return ' '.join(parts)

def logo_paths(fill='#000000', transform=None):
    return '\n'.join(
      f'  <path id="letter-{letter.lower()}-{i+1}" fill="{fill}" fill-rule="evenodd" d="{path_d(GLYPHS[letter],origin,transform)}"/>'
      for i,(letter,origin) in enumerate(ADVANCES))

def logo_svg(fill='#000000', background=None, viewbox=None, transform=None):
    vb=viewbox or (-MARGIN,-MARGIN,WIDTH+2*MARGIN,CAP+2*MARGIN)
    bg=(f'<rect x="{number(vb[0])}" y="{number(vb[1])}" width="{number(vb[2])}" height="{number(vb[3])}" fill="{background}"/>\n' if background else '')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{number(vb[2])}" height="{number(vb[3])}" viewBox="{' '.join(number(x) for x in vb)}" role="img" aria-labelledby="title description">
 <title id="title">BCSC - British Columbia Systems Corporation, 1983 reconstruction</title>
 <desc id="description">Geometric reconstruction of the BCSC wordmark from the 1982-83 annual report cover. Four editable filled paths; two identical C masters; reconstructed 30-degree slant. No embedded raster or fonts. This is a modern reconstruction, not an original official vector master.</desc>
 <metadata>Reference: https://projects.ahmadjalil.com/PofBC/identity-collected/bc-systems-corporation/bc-systems-1983-logo.png ; Report: https://archive.org/details/micro_IA40243510_1370 ; reconstructed 2026-11-12.</metadata>
 {bg}<g id="bcsc-wordmark">\n{logo_paths(fill,transform)}\n </g>
</svg>'''

def render_svg(svg, width, alpha=True):
    doc=fitz.open(stream=svg.encode(),filetype='svg')
    pix=doc[0].get_pixmap(matrix=fitz.Matrix(width/doc[0].rect.width,width/doc[0].rect.width),alpha=alpha)
    return Image.frombytes('RGBA' if alpha else 'RGB',(pix.width,pix.height),pix.samples)

def font(size,bold=False):
    p='/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf'
    try:
        return ImageFont.truetype(p,size)
    except OSError:
        try:
            return ImageFont.truetype('DejaVuSans.ttf',size)
        except OSError:
            return ImageFont.load_default(size=size)

def main():
    variants = {
       'BCSC_1983_Reconstructed.svg': logo_svg(),
       'BCSC_1983_White.svg': logo_svg('#ffffff'),
       'BCSC_1983_White_on_Black.svg': logo_svg('#ffffff','#000000'),
    }
    for name,svg in variants.items(): (OUT/name).write_text(svg)
    # Export the actual vector. Transparent PNGs are convenience derivatives.
    render_svg(variants['BCSC_1983_Reconstructed.svg'],4800).save(OUT/'BCSC_1983_Black_4800px.png')
    render_svg(variants['BCSC_1983_White.svg'],4800).save(OUT/'BCSC_1983_White_4800px.png')
    preview_rgba=render_svg(variants['BCSC_1983_White_on_Black.svg'],2000,True)
    preview=Image.new('RGB',preview_rgba.size,'black')
    preview.paste(preview_rgba,mask=preview_rgba.getchannel('A'))
    preview.save(OUT/'BCSC_1983_Preview.png')

    # A 2-page vector PDF, positive then reversed. Both pages retain paths.
    pdf=fitz.open()
    for name in ['BCSC_1983_Reconstructed.svg','BCSC_1983_White_on_Black.svg']:
        src=fitz.open(stream=variants[name].encode(),filetype='svg')
        srcpdf=fitz.open(stream=src.convert_to_pdf(),filetype='pdf')
        pdf.insert_pdf(srcpdf)
    pdf.set_metadata({'title':'BCSC 1983 - reconstructed vector wordmark',
                      'subject':'Positive and reversed editions of a modern geometric reconstruction',
                      'author':'Reconstructed for Ahmad Jalil'})
    pdf.save(OUT/'BCSC_1983_Vector.pdf',garbage=4,deflate=True)
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(WORK/'pdf_positive_check.png')

    # The comparison uses one global source-coordinate alignment, never local
    # per-letter warping. y shear restores the scan's measured ~0.7-degree tilt.
    scan_x=21.0; scan_y=25.3; tilt=0.0125
    transform=lambda x,y:(x+scan_x,y+scan_y+tilt*(x+scan_x))
    aligned_svg=logo_svg('#ffffff','#000000',(0,0,1168,288),transform)
    aligned=render_svg(aligned_svg,1168,False)
    source=Image.open(REF).convert('RGB')
    a=np.asarray(source.convert('L'))>140
    b=np.asarray(aligned.convert('L'))>127
    intersection=int((a&b).sum()); union=int((a|b).sum())
    from scipy.ndimage import binary_erosion, distance_transform_edt
    ae=a^binary_erosion(a); be=b^binary_erosion(b)
    distances=np.concatenate([distance_transform_edt(~be)[ae],distance_transform_edt(~ae)[be]])
    metrics={'reference_dimensions_px':[1168,288],
        'reference_threshold':140,'render_threshold':127,
        'global_alignment':{'translation_x':scan_x,'translation_y':scan_y,'scan_y_shear':tilt},
        'mask_intersection_over_union':intersection/union,
        'symmetric_boundary_median_px':float(np.median(distances)),
        'symmetric_boundary_p95_px':float(np.percentile(distances,95)),
        'note':'Agreement with the selected threshold of a damaged microfiche scan, not proof of an original master. Parameters are manually reconstructed.'}
    (WORK/'comparison_metrics.json').write_text(json.dumps(metrics,indent=2))
    overlay=np.full((*a.shape,3),18,dtype=np.uint8)
    overlay[a&b]=(221,225,229)
    overlay[a&~b]=(236,74,96)
    overlay[b&~a]=(0,178,189)
    overlay_im=Image.fromarray(overlay)
    aligned.save(WORK/'aligned_reconstruction.png')
    overlay_im.save(WORK/'overlay_detail.png')
    board=Image.new('RGB',(1800,1240),'#f4f3ee'); draw=ImageDraw.Draw(board)
    draw.text((80,45),'BCSC / 1983',font=font(48,True),fill='#17232a')
    draw.text((80,110),'Geometric reconstruction from the annual-report scan',font=font(26),fill='#5a646a')
    panels=[('01  ORIGINAL SCAN',source),('02  REBUILT VECTOR / SCAN ALIGNMENT',aligned),('03  ALIGNED COMPARISON',overlay_im)]
    for idx,(label,im) in enumerate(panels):
        top=180+idx*322
        draw.text((80,top),label,font=font(20,True),fill='#4a555b')
        # Same scaling, full source rectangle; no independent per-letter fit.
        scaled=im.resize((1168,288),Image.Resampling.LANCZOS)
        board.paste(scaled,(316,top+34))
    draw.rectangle((81,1175,96,1190),fill=(236,74,96));draw.text((106,1171),'Source only',font=font(19),fill='#39464b')
    draw.rectangle((310,1175,325,1190),fill=(0,178,189));draw.text((335,1171),'Reconstruction only',font=font(19),fill='#39464b')
    draw.text((680,1171),'Shared C master  /  30° slant  /  four vector paths',font=font(19),fill='#39464b')
    board.save(OUT/'BCSC_1983_Comparison.png')

    # Verify structural properties, not the implementation's coordinates.
    checks=[]
    for name in variants:
        root=ET.parse(OUT/name).getroot()
        paths=root.findall('.//{http://www.w3.org/2000/svg}path')
        images=root.findall('.//{http://www.w3.org/2000/svg}image')
        texts=root.findall('.//{http://www.w3.org/2000/svg}text')
        assert len(paths)==4 and not images and not texts
        checks.append({'file':name,'paths':len(paths),'embedded_rasters':len(images),'font_text_objects':len(texts)})
    assert all(len(p.get_images())==0 for p in pdf)
    metrics['structural_validation']=checks
    metrics['pdf_pages']=len(pdf);metrics['pdf_embedded_images']=0
    (OUT/'Reconstruction_QA.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
