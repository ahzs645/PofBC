"""Build registered visual proofs. Reference pixels occur only in these proofs.

The delivered SVGs and poster PDF are entirely vector. This comparison PDF
deliberately includes raster renderings of both artworks to display overlays.
"""
from pathlib import Path
from io import BytesIO
import json,re
from reconstruct_illustrations import render
import numpy as np
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth, registerFont
from reportlab.pdfbase.ttfonts import TTFont
# Embed the proof fonts so every PDF renderer uses the same glyph metrics.
PROOF_FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
registerFont(TTFont('ProofSans',str(PROOF_FONT_DIR/'DejaVuSans.ttf')))
registerFont(TTFont('ProofSans-Bold',str(PROOF_FONT_DIR/'DejaVuSans-Bold.ttf')))

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
TMP=ROOT/'_work'
PROOF=ROOT/'proof';PROOF.mkdir(exist_ok=True)
INK='#326c59'

def crop_normal(im,box,width=900):
    s=im.width/1000
    p=im.crop(tuple(round(v*s) for v in box))
    if p.width>width:p=p.resize((width,round(p.height*width/p.width)),Image.Resampling.LANCZOS)
    return p.convert('RGB')

def vector_crop(box,slug,source_text,width=1000,reuse=False):
    x0,y0,x1,y1=box
    match=re.search(r'<svg\b[^>]*>',source_text)
    tag=match.group(0)
    for name,value in [('viewBox',f'{x0} {y0} {x1-x0} {y1-y0}'),('width',str(x1-x0)),('height',str(y1-y0))]:
        tag=re.sub(name+r'="[^"]*"',name+'="'+value+'"',tag,count=1)
    p=TMP/'proof-region.svg'
    out=TMP/(slug+'-proof-vector.png')
    if not reuse or not out.exists():
        p.write_text(source_text[:match.start()]+tag+source_text[match.end():])
        render(p,out,width)
    im=Image.open(out).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
    return bg.convert('RGB')

def overlay(a,b):
    b=b.resize(a.size,Image.Resampling.LANCZOS)
    A=np.asarray(a.convert('RGB'),dtype=float);B=np.asarray(b.convert('RGB'),dtype=float)
    # Optical ink density, not a contour tracer. Paper is suppressed only in
    # the comparison overlay; source and vector panels remain unaltered.
    aa=np.clip((235-A[:,:,0])/175,0,1)
    bb=np.clip((235-B[:,:,0])/175,0,1)
    out=np.ones_like(A)*255
    out[:,:,0]-=180*bb;out[:,:,1]-=180*aa
    return Image.fromarray(out.astype('uint8'))

def wrapped(c,text,x,y,w,font='ProofSans',size=10,leading=14):
    c.setFont(font,size)
    line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if stringWidth(trial,font,size)>w and line:
            c.drawString(x,y,line);y-=leading;line=word
        else:line=trial
    if line:c.drawString(x,y,line);y-=leading
    return y

def fit_image(c,im,x,y,w,h):
    scale=min(w/im.width,h/im.height)
    iw,ih=im.width*scale,im.height*scale
    encoded=BytesIO()
    im.convert('RGB').save(encoded,format='JPEG',quality=94,subsampling=0,optimize=True)
    encoded.seek(0)
    c.drawImage(ImageReader(encoded),x+(w-iw)/2,y+(h-ih)/2,iw,ih,mask='auto')

def run(reuse_renders=False):
    reference=Image.open(ROOT/'reference/reference-native.jpg').convert('RGB')
    redraw=Image.open(TMP/'poster-proof-render.png').convert('RGB')
    master_text=(ROOT/'Wildlife-Trees-outlined.svg').read_text()
    # These are measured poster coordinates, with no nonrigid warping.
    pages=[
      ('Whole poster','whole-poster',(0,0,1000,2997.159090909091),
       'All six corrected animals, the source tree and portrait scenery, original wording and both PofBC identity vectors are assembled in the original page coordinates. The lettering uses a fitted substitute font.'),
      ('Red-tailed hawk','red-tailed-hawk',(248,88,488,303),
       'The original perch and supporting branch are restored around the corrected animal. Placement uses the native source-crop origin, undoing the isolated SVG crop. The faint beak outline retains its documented manual repair.'),
      ('Great horned owl','great-horned-owl',(128,389,338,600),
       'The corrected source-based facial proportions and feather marks are retained. The original cropped portrait, clean panel rule and caption are restored without stretching the isolated animal to a new bounding box.'),
      ('Northern flying squirrel','northern-flying-squirrel',(218,669,429,879),
       'The source tail, jaw, paws and gliding membrane remain in their original positions. Surrounding branches and trunk are separately editable. The short faint ear-rim repair is retained.'),
      ('Black-capped chickadee','black-capped-chickadee',(137,985,351,1200),
       'Both tail feather contours and both visible gripping feet remain aligned with the original trunk and cavity. Source scene details are separate from the corrected animal paths.'),
      ('Black bear','black-bear',(97,1265,359,1531),
       'The corrected muzzle contour and measured ear-core repair are retained. The source portrait crop is preserved. A pale horizontal scan crease in the lower neck was not retouched.'),
      ('Northwestern toad','northwestern-toad',(188,1559,414,1771),
       'The expanded source crop restores the left rear foot. The corrected foreleg outline and measured pupil are retained. The original ground and cast shadow are separate background vectors in the complete poster.'),
      ('Habitat tree: crown and nest','tree-crown',(340,130,980,730),
       'The jagged crown, real branch routes, woven nest and snapped limb are reconstructed from original pen marks. Manually measured feature regions organise the geometry; no random hatch texture is substituted.'),
      ('Habitat tree: trunk and cavities','tree-trunk',(430,700,820,1660),
       'Source bark, exposed wood, cavities, bracket fungi and branch junctions are rebuilt as fitted vector ink. Native source registration is retained across overlapping processing strips.'),
      ('Habitat tree: roots and forest floor','tree-roots',(45,1400,970,1955),
       'The original root flare, basal saplings, fallen wood, ground details and source illustrator mark are retained as editable vector groups. Source-visible detail is preserved without inventing wood hidden by the portraits.'),
      ('Identity marks from PofBC','identity-marks',(598,2752,839,2890),
       'Existing PofBC vector components are retained, including the ministry crest/wordmark and the Forest Service oval with its supplied lettering. Their placement is checked against the source; scanned edge softness will differ.'),
      ('Typesetting and layout','typesetting',(45,2000,952,2930),
       'All wording and punctuation were checked against the scan. Text is retyped and fitted to measured line boxes, using Nimbus Sans as an unverified-font substitute. The portable SVG and poster PDF have outlined lettering.'),
    ]
    p=ROOT/'Wildlife-Trees-overlay-proof.pdf'
    pdf_buffer=BytesIO();c=canvas.Canvas(pdf_buffer,pagesize=landscape(A4),pageCompression=1)
    c.setTitle('Wildlife Trees — registered overlay proof')
    c.setAuthor('Wildlife Trees vector reconstruction')
    W,H=landscape(A4);margin=29;gap=13;col=(W-2*margin-2*gap)/3
    manifest=[]
    for index,(title,slug,box,note) in enumerate(pages,1):
        a=crop_normal(reference,box,1000);b=vector_crop(box,slug,master_text,1000,reuse_renders).resize(a.size,Image.Resampling.LANCZOS);o=overlay(a,b)
        print('Proof',index,title,flush=True)
        # Portable raster diagnostics alongside the editable assets.
        o.save(PROOF/(slug+'-overlay.png'),optimize=True)
        th=330 if a.height/a.width<2 else 520
        tw=round(a.width*th/a.height)
        combined=Image.new('RGB',(tw*3+40,th+40),'white');d=ImageDraw.Draw(combined)
        for i,(im,label) in enumerate([(a,'SOURCE'),(b,'VECTOR REDRAW'),(o,'OVERLAY')]):
            combined.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(i*(tw+20),30));d.text((i*(tw+20)+2,8),label,fill=INK)
        combined.save(PROOF/(slug+'-comparison.png'),optimize=True)
        c.setFillColor(HexColor(INK));c.rect(0,H-9,W,9,fill=1,stroke=0)
        c.setFont('ProofSans-Bold',9);c.drawString(margin,H-32,'WILDLIFE TREES / RECONSTRUCTION PROOF')
        c.setFont('ProofSans',9);c.drawRightString(W-margin,H-32,f'{index:02d} / {len(pages):02d}')
        c.setFont('ProofSans-Bold',22);c.drawString(margin,H-61,title)
        c.setFillColor(HexColor('#5c6c62'));c.setFont('ProofSans',9)
        c.drawString(margin,H-79,'Original print in magenta; vector redraw in cyan. Overlap appears blue. No pixel-perfect match is claimed.')
        image_top=H-111;image_bottom=112;image_h=image_top-image_bottom
        for i,(im,label) in enumerate([(a,'SOURCE SCAN'),(b,'VECTOR REDRAW'),(o,'REGISTERED COLOR OVERLAY')]):
            x=margin+i*(col+gap)
            c.setFillColor(HexColor('#32483a'));c.setFont('ProofSans-Bold',8.5);c.drawString(x,image_top+10,label)
            c.setStrokeColor(HexColor('#d8e2db'));c.setLineWidth(.5);c.rect(x,image_bottom,col,image_h,stroke=1,fill=0)
            fit_image(c,im,x+5,image_bottom+5,col-10,image_h-10)
        c.setFillColor(HexColor('#293b30'))
        wrapped(c,note,margin,91,W-2*margin,size=10,leading=14)
        c.setFillColor(HexColor('#718176'));c.setFont('ProofSans',7.3)
        c.drawString(margin,23,'Visual comparison only. The supplied SVGs and Wildlife-Trees-vector.pdf contain the editable vector artwork.')
        c.drawRightString(W-margin,23,'Source: supplied Wildlife Trees.pdf')
        c.showPage()
        manifest.append({'section':title,'box':box,'comparison':f'proof/{slug}-comparison.png','overlay':f'proof/{slug}-overlay.png','note':note})
    c.save()
    fresh=p.with_suffix('.pdf.writing');fresh.write_bytes(pdf_buffer.getvalue());fresh.replace(p)
    (PROOF/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(p,len(pages),'pages')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-renders',action='store_true',help='Reuse existing crop PNGs when only proof typography or labels changed. Do not use after artwork or crop edits.')
    run(parser.parse_args().reuse_renders)
