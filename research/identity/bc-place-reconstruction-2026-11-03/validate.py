#!/usr/bin/env python3
"""Render the SVGs, check their structure and reproduce the source overlay.

Dependencies: PyMuPDF, Pillow, numpy, scipy. Geometry is authored separately by
scripts/build-bc-place-reconstruction.py; this script does not generate paths.
"""
import hashlib
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / 'evidence'
QA = HERE / 'qa'
NS = '{http://www.w3.org/2000/svg}'


def render(data, scale=1, canvas=None, alpha=False):
    if canvas:
        doc = ET.fromstring(data)
        doc.set('viewBox', f'0 0 {canvas[0]} {canvas[1]}')
        doc.set('width', str(canvas[0])); doc.set('height', str(canvas[1]))
        data = ET.tostring(doc)
    with fitz.open(stream=data, filetype='svg') as doc:
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=alpha)
        return Image.frombytes('RGBA' if alpha else 'RGB', (pix.width,pix.height), pix.samples)


def source_mask(source, threshold=130, blue_red_threshold=117):
    a = np.asarray(source).astype(float)
    # R=117 is halfway between the median local paper R=234 and sampled ink R=0.
    # Require the blue hue as well, so grey paper/noise is not classified as ink.
    blue = ((a[:,:,2]-a[:,:,0]>50) & (a[:,:,1]-a[:,:,0]>35)
            & (a[:,:,0]<blue_red_threshold))
    blue[:,240:] = False
    black = a.max(2)<threshold
    black[:,:250] = False
    mask = blue | black
    components, _ = ndimage.label(mask)
    sizes = np.bincount(components.ravel())
    # Remove only tiny isolated ink/scan specks from the comparison mask.
    # The archived colour source crop itself remains unchanged.
    return mask & (sizes[components]>12)


def comparison(a,b):
    ae = a & ~ndimage.binary_erosion(a)
    be = b & ~ndimage.binary_erosion(b)
    distances = np.r_[ndimage.distance_transform_edt(~ae)[be],
                      ndimage.distance_transform_edt(~be)[ae]]
    return {
        'intersectionOverUnion':float((a&b).sum()/(a|b).sum()),
        'sourceInkPixels':int(a.sum()), 'reconstructionInkPixels':int(b.sum()),
        'symmetricBoundaryMedianPixels':float(np.median(distances)),
        'symmetricBoundary95thPercentilePixels':float(np.percentile(distances,95)),
    }


def font(size,bold=False):
    base=Path(os.environ.get('POFBC_QA_FONT_DIR','/usr/share/fonts/truetype/dejavu'))
    if not (base/'DejaVuSans.ttf').is_file() or not (base/'DejaVuSans-Bold.ttf').is_file():
        raise FileNotFoundError('Install DejaVu Sans or set POFBC_QA_FONT_DIR to the directory containing DejaVuSans.ttf and DejaVuSans-Bold.ttf. These fonts label the comparison board only; the logo has no font dependency.')
    return ImageFont.truetype(str(base/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)


def board(source, vector, overlay):
    page=Image.new('RGB',(1960,1240),'#f2f0e9'); draw=ImageDraw.Draw(page)
    draw.text((40,28),'British Columbia Place | a researched vector reconstruction',font=font(33,True),fill='#182636')
    draw.text((40,77),'Early-1980s corporate identity  /  Source comparison  /  3 November 2026',font=font(20),fill='#52616b')
    original=Image.open(ROOT/'public/identity-collected/bc-place-ltd/bc-place-1983-logo.png').convert('RGB')
    panels=[
        (40,125,'A  Collected 1983 annual-report scan','Original gallery file retained unchanged.',original),
        (1000,125,'B  Museum opening programme, 19 June 1983','Primary colour specimen, page 4; original printed details.',source),
        (40,660,'C  Hand-built vector reconstruction','Explicit arcs and custom glyphs; blue sampled from the scan.',vector),
        (1000,660,'D  Overlay against the museum specimen','Cyan: source only  |  Magenta: redraw only  |  Dark: shared ink',overlay),
    ]
    for x,y,title,note,im in panels:
        draw.rounded_rectangle((x,y,x+920,y+515),radius=12,fill='white')
        draw.text((x+20,y+16),title,font=font(22,True),fill='#182636')
        draw.text((x+20,y+48),note,font=font(16),fill='#52616b')
        scale=min(884/im.width,422/im.height)
        fit=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
        page.paste(fit,(x+(920-fit.width)//2,y+79+(420-fit.height)//2))
    draw.text((40,1197),'Reconstruction, not an original vector master. Exact designer, historical typeface and production colour remain unconfirmed.',font=font(18),fill='#43515a')
    page.save(QA/'comparison-board.png')


def main():
    QA.mkdir(exist_ok=True)
    register=json.loads((HERE/'source-register.json').read_text())
    results=[]
    for asset in register['assets']:
        path=ROOT/'public'/asset['file']; data=path.read_bytes(); doc=ET.fromstring(data)
        tags=[element.tag.split('}')[-1] for element in doc.iter()]
        forbidden=[tag for tag in tags if tag in {'image','text','foreignObject','script','filter'}]
        external=[value for element in doc.iter() for key,value in element.attrib.items()
                  if key.split('}')[-1] in {'href','src'} or 'url(' in value]
        assert not forbidden and not external,(path,forbidden,external)
        assert tags.count('path')>0,path
        assert hashlib.sha256(data).hexdigest()==asset['sha256'],path
        image=render(data,scale=3,alpha=True)
        alpha=np.asarray(image)[:,:,3]
        ys,xs=np.where(alpha>0)
        assert xs.min()>0 and ys.min()>0 and xs.max()<image.width-1 and ys.max()<image.height-1,path
        results.append({'file':asset['file'],'sha256':asset['sha256'],'bytes':len(data),
                        'pathCount':tags.count('path'),'imageElements':tags.count('image'),
                        'textElements':tags.count('text'),'externalResources':external,
                        'renderedSize':[image.width,image.height],'unclipped':True})
        if asset['id']=='reconstruction-bc-place-1982-lockup-colour':
            image.save(QA/'colour-reconstruction-preview.png')
            colour=render(data,scale=2,canvas=(760,385))
        elif asset['id']=='reconstruction-bc-place-1982-lockup':
            image.save(QA/'monochrome-reconstruction-preview.png')
            monochrome=data
    source=Image.open(EVIDENCE/'1983-programme-logo.png').convert('RGB')
    vector=render(monochrome,canvas=source.size)
    ink=np.asarray(vector)[:,:,0]<128
    mask=source_mask(source)
    overlay=np.full((*mask.shape,3),255,np.uint8)
    overlay[mask]=[0,172,218]; overlay[ink]=[236,61,139]; overlay[mask&ink]=[44,47,54]
    overlay=Image.fromarray(overlay); overlay.save(QA/'programme-overlay.png')
    stats={'whole':comparison(mask,ink),
           'monogram':comparison(mask[32:360,20:240],ink[32:360,20:240]),
           'lettering':comparison(mask[80:310,250:710],ink[80:310,250:710])}
    sensitivity={f'black={t},blueRed={b}':comparison(source_mask(source,t,b),ink)['intersectionOverUnion']
                 for t,b in [(100,97),(130,117),(160,137)]}
    report={'date':'2026-11-03','vectorValidation':results,'comparison':stats,
            'method':{'reference':'evidence/1983-programme-logo.png','referenceSize':list(source.size),
                      'registration':'None; common source-coordinate canvas. No affine fit or local warping.',
                      'sourceMask':'Black: maximum RGB < 130 for x>=250; blue: R<117 (halfway between sampled ink R=0 and paper R=234), B-R>50 and G-R>35 for x<240; connected components <=12 pixels excluded.',
                      'vectorMask':'PyMuPDF rendering at the reference resolution; red channel <128.',
                      'thresholdSensitivityIoU':sensitivity,
                      'interpretation':'Overlap is a comparison against one imperfect scan, not a percentage of historical authenticity. Printing, scanning, threshold choice and hand reconstruction all contribute to differences.'}}
    (QA/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    board(source,colour,overlay)
    print(json.dumps({'assets':len(results),'comparison':stats,'thresholdSensitivityIoU':sensitivity},indent=2))


if __name__=='__main__':
    main()
