"""PGE mark rebuilt from deliberate geometry and hand-authored Bezier paths.

The reference is read only for comparison, never for contour extraction.
No autotracing, raster embedding, or font substitution is used in the artwork.
"""
from pathlib import Path
import json
import math
import shutil
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import fitz
from reportlab.pdfgen import canvas
from svgpathtools import parse_path, Line, CubicBezier, QuadraticBezier

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pge-vector"
ANALYSIS = ROOT / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
ANALYSIS.mkdir(parents=True, exist_ok=True)
REFERENCE = ROOT / "upload" / "Isolated vintage PGE logo on transparency(1).png"

# Design-space coordinates preserve direct comparison with the supplied image.
SOURCE_SIZE = (1312, 1199)
ARTBOARD = (135.0, 14.0, 1078.0, 1168.0)
INK = "#000000"
PAPER = "#ffffff"

BACK = "M183 46 H993 L1181 606 L977 1150 H167 L373 606 Z"

# A consistent grid replaces the slight pitch/thickness drift in the bitmap.
STRIPE_COUNT = 38
STRIPE_START = 60.0
STRIPE_PITCH = 14.55
STRIPE_HEIGHT = 5.5

def left_edge(y):
    return 183.0 + (373.0 - 183.0) * (y - 46.0) / 560.0

def right_edge(y):
    return 993.0 + (1181.0 - 993.0) * (y - 46.0) / 560.0

def stripe_path(i):
    y0 = STRIPE_START + STRIPE_PITCH * i
    y1 = y0 + STRIPE_HEIGHT
    return (f"M{left_edge(y0):.4f} {y0:.4f} "
            f"H{right_edge(y0):.4f} "
            f"L{right_edge(y1):.4f} {y1:.4f} "
            f"H{left_edge(y1):.4f} Z")

# The stylized coast is reconstructed with selected landmarks and smooth
# curves. This deliberately does not copy the bitmap's edge jitter.
MAINLAND = """
M428 104.5 H797 V354
C799 357 805 358 811 359
C813 366 817 371 821 375
L850 419
C855 426 858 431 860 436
L877 449 L891 465 L908 486
C911 492 907 497 911 502
C909 508 914 512 916 519
L921 531 L929 543 H698
L697 552
C700 557 698 560 691 560
L681 558
C676 560 668 561 663 558
C664 555 669 552 665 549
L655 545 L648 545 L643 541 L643 537
L630 530
C627 523 622 519 616 517
L616 511 L610 507 L600 501
C599 496 595 491 589 489
L589 481 L584 475 L584 467
L579 463 L577 455 L573 447 L577 442
L591 442
C594 445 592 451 596 454
C600 458 604 454 605 450
L601 445 L597 443 L597 439 L593 435
L592 424 L589 418 L583 414
L584 405 L581 402 L580 393 L575 387
L575 379 L568 372 L567 364 L562 359
L558 358 L556 351 L557 342 L553 335
L556 327 L554 321 L562 309
C559 301 560 294 560 289
C560 278 564 267 568 259
L560 256 L554 251 L550 245 L550 238
C554 234 550 229 544 224
L537 216 L535 207 L539 202 L537 198
L532 200 L528 193 L525 189 L525 183
L522 179 L525 173 L522 166 L523 160
C522 156 519 154 516 153
L509 157 L503 154 L500 153 L500 144
L497 139 L498 134
C503 132 498 128 494 126
L487 120 L483 121 L489 126 L479 126
L476 130 L478 136
L472 139 L446 139 L439 136 L437 132
L437 127 L430 123 L430 117 Z
"""

WEST_ISLAND = """
M498 300 H539
L537 310 L531 314 L528 319 L526 325
L529 332 L527 338 L530 344 L526 349
L525 357 L521 365 L523 372
L531 379 L534 386 L532 392 L528 396
L528 400 L524 400 L520 394 L520 390
L515 385 L514 380 L508 376 L508 371
L502 366 L501 361 L503 354 L501 348
L503 341 L498 334 L500 327 L497 321
L500 314 L497 306 Z
"""

# Six small coastal negative shapes, separately editable.
COAST_CUTOUTS = [
    "M609 447 L614 445 L618 448 L619 452 L615 455 L611 454 L608 451 Z",
    "M610 460 L616 459 L620 462 L622 466 L618 470 L614 470 L610 466 Z",
    "M633 474 L638 472 C642 471 645 474 647 478 L644 482 L639 484 L634 481 L631 477 Z",
    "M653 488 L659 487 L663 485 C668 485 672 487 672 492 L674 501 L680 505 C684 507 686 510 685 513 L678 514 L674 511 L667 511 C661 510 662 506 665 504 L672 503 L670 498 L662 498 L660 494 L654 494 L651 491 Z",
    "M678 517 L685 516 C690 518 690 522 687 525 L683 527 L680 525 L677 521 Z",
    "M692 530 C694 528 698 531 698 534 C698 537 695 540 692 537 C690 535 690 532 692 530 Z",
]

# Individually constructed letter outlines. P's counter is a true compound
# path; there are no live text objects and no dependency on installed fonts.
LETTER_P = """
M440 660 H577
C615 660 625 689 610 735
L553 878
C545 901 527 911 506 911
H415 L347 1098 H278 Z
M487 720 H525
C541 720 547 725 539 746
L508 826
C503 840 495 845 480 845
H441 Z
"""

LETTER_G = """
M724 660 H810
C847 660 859 682 848 719
L824 792 H759 L776 744
C782 727 774 720 760 720
H735
C722 720 716 728 710 744
L614 1008
C608 1025 615 1034 631 1034
H652
C663 1034 672 1029 678 1011
L716 912 H673 L696 849 H805
L733 1048
C721 1085 699 1098 661 1098
H581
C541 1098 530 1077 539 1036
L645 735
C663 685 687 660 724 660 Z
"""

LETTER_E = """
M927 660 H1090 L1065 721 H970
L924 848 H1022 L999 911 H902
L857 1035 H958 L935 1098 H775 Z
"""

def clean(d):
    return " ".join(d.split())

SHAPES = [("panel", INK, BACK)]
SHAPES += [(f"stripe-{i+1:02d}", PAPER, stripe_path(i)) for i in range(STRIPE_COUNT)]
SHAPES += [("bc-mainland-and-south-coast", PAPER, MAINLAND),
           ("western-island", PAPER, WEST_ISLAND)]
SHAPES += [(f"coastal-cutout-{i+1}", INK, d) for i,d in enumerate(COAST_CUTOUTS)]
SHAPES += [("letter-P", PAPER, LETTER_P), ("letter-G", PAPER, LETTER_G),
           ("letter-E", PAPER, LETTER_E)]

def make_svg(viewbox, filename):
    x,y,w,h=viewbox
    head = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="{w:g}" height="{h:g}" viewBox="{x:g} {y:g} {w:g} {h:g}"
     role="img" aria-labelledby="title desc">
  <title id="title">PGE logo - geometric vector reconstruction</title>
  <desc id="desc">Rebuilt from the supplied raster reference using a folded black panel, 38 mathematically spaced white bands, a hand-drawn stylized British Columbia silhouette, and custom outlined PGE lettering. The exterior is transparent. No embedded images, live text, filters, clipping masks, or automatic tracing.</desc>
  <metadata>Reference-based reconstruction, 2026-11-12. Not an original archival master. Stripe grid: 38 bands, pitch 14.55, height 5.5. All design elements are editable filled paths.</metadata>
'''
    groups=[("01-panel", "Black panel", SHAPES[:1]),
            ("02-stripe-grid", "38 regular horizontal bands", SHAPES[1:39]),
            ("03-british-columbia", "Stylized BC silhouette and coastal details", SHAPES[39:47]),
            ("04-pge-lettering", "Custom PGE letter outlines", SHAPES[47:])]
    lines=[head]
    for gid,label,shapes in groups:
        lines.append(f'  <g id="{gid}" data-name="{label}">')
        for sid,fill,d in shapes:
            lines.append(f'    <path id="{sid}" fill="{fill}" fill-rule="evenodd" d="{clean(d)}"/>')
        lines.append("  </g>")
    lines.append("</svg>\n")
    filename.write_text("\n".join(lines))

def add_rl_path(c, d, fill):
    parsed=parse_path(d)
    p=c.beginPath()
    for sub in parsed.continuous_subpaths():
        p.moveTo(sub.start.real,sub.start.imag)
        for seg in sub:
            if isinstance(seg,Line):
                p.lineTo(seg.end.real,seg.end.imag)
            elif isinstance(seg,CubicBezier):
                p.curveTo(seg.control1.real,seg.control1.imag,
                          seg.control2.real,seg.control2.imag,
                          seg.end.real,seg.end.imag)
            elif isinstance(seg,QuadraticBezier):
                c1=seg.start+(seg.control-seg.start)*2/3
                c2=seg.end+(seg.control-seg.end)*2/3
                p.curveTo(c1.real,c1.imag,c2.real,c2.imag,seg.end.real,seg.end.imag)
            else:
                raise ValueError(type(seg))
        if sub.isclosed():
            p.close()
    c.setFillColor(fill)
    c.drawPath(p,stroke=0,fill=1,fillMode=0)

def make_pdf():
    x,y,w,h=ARTBOARD
    out=OUT/'PGE-reconstructed-vector.pdf'
    # 270 mm tall, containing vector artwork only.
    scale=(270.0*72.0/25.4)/h
    c=canvas.Canvas(str(out),pagesize=(w*scale,h*scale),pageCompression=1)
    c.setTitle("PGE - reconstructed vector logo")
    c.setAuthor("Reference-based geometric reconstruction")
    c.setSubject("Editable path geometry; no raster images or font dependencies")
    c.scale(scale,scale)
    c.translate(-x,h+y)
    c.scale(1,-1)
    for sid,fill,d in SHAPES:
        add_rl_path(c,d,fill)
    c.showPage()
    c.save()
    # ReportLab emits an empty default text block and Helvetica resource even
    # when every visible object is a path. Remove those unused defaults so the
    # delivered PDF is literally free of font resources as well as live text.
    doc=fitz.open(out)
    page=doc[0]
    contents=page.read_contents().replace(b'BT /F1 12 Tf 14.4 TL ET',b'')
    assert b'BT' not in contents and b' Tj' not in contents
    xref=doc.get_new_xref()
    doc.update_object(xref,'<<>>')
    doc.update_stream(xref,contents)
    page.set_contents(xref)
    doc.xref_set_key(page.xref,'Resources','<</ProcSet[/PDF]>>')
    pdf_bytes=doc.tobytes(garbage=4,deflate=True)
    doc.close()
    out.write_bytes(pdf_bytes)
    return out

def render_svg(svgpath, width=None):
    doc=fitz.open(str(svgpath))
    page=doc[0]
    zoom=1 if width is None else width/page.rect.width
    pix=page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=True)
    # Pixmap has premultiplied alpha. get PNG bytes to recover ordinary RGBA.
    import io
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")

def font(size,bold=False):
    path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(path,size)

def proof(full_rebuild):
    reference=Image.open(REFERENCE).convert('RGBA')
    ref=np.asarray(reference).astype(float)/255
    vec=np.asarray(full_rebuild).astype(float)/255
    # Compare white foreground, without counting transparent exterior as white.
    rm=(ref[:,:,:3].mean(axis=2)>.65)&(ref[:,:,3]>.5)
    vm=(vec[:,:,:3].mean(axis=2)>.65)&(vec[:,:,3]>.5)
    overlay=np.empty((*rm.shape,4),dtype=np.uint8)
    overlay[:]=[242,244,246,255]
    overlay[rm&~vm]=[202,44,116,255]
    overlay[vm&~rm]=[0,153,185,255]
    overlay[vm&rm]=[32,46,65,255]
    overlay_im=Image.fromarray(overlay)
    overlay_im.save(ANALYSIS/'overlay-full.png')
    full_rebuild.save(ANALYSIS/'rebuild-full.png')

    # An aligned detail proof makes the hand-built type easy to assess.
    region=(250,640,1110,1120)
    overlay_im.crop(region).resize((1290,720),Image.Resampling.LANCZOS).save(ANALYSIS/'overlay-letters.png')

    # Three-column user-facing board: supplied source, rebuild, aligned overlay.
    W,H=2280,1240
    board=Image.new('RGB',(W,H),'#f2f4f6')
    dr=ImageDraw.Draw(board)
    dr.text((54,32),'PGE / VECTOR RECONSTRUCTION',font=font(35,True),fill='#172334')
    dr.text((54,85),'Same proportions. Deliberately rebuilt geometry.',font=font(22),fill='#586270')
    panels=[(54,'SUPPLIED REFERENCE',reference),(794,'REBUILT VECTOR',full_rebuild),(1534,'ALIGNED OVERLAY',overlay_im)]
    crop=(135,14,1213,1182)
    for x,label,im in panels:
        dr.text((x,145),label,font=font(21,True),fill='#26364a')
        # Neutral backing makes exterior transparency visible.
        tile=Image.new('RGBA',SOURCE_SIZE,'#e3e7eb')
        tile=Image.alpha_composite(tile,im).crop(crop)
        tile.thumbnail((692,750),Image.Resampling.LANCZOS)
        board.paste(tile.convert('RGB'),(x,190))
    dr.line((54,975,2226,975),fill='#c9d0d7',width=2)
    dr.text((54,1000),'CONSTRUCTION',font=font(20,True),fill='#26364a')
    dr.text((54,1037),'38 equal-pitch bands  /  custom outlined P, G and E',font=font(20),fill='#465465')
    dr.text((54,1070),'Hand-drawn map paths  /  transparent exterior',font=font(20),fill='#465465')
    dr.text((54,1103),'No embedded bitmap, live type, filters or auto-tracing.',font=font(20),fill='#465465')
    dr.text((1534,1000),'OVERLAY KEY',font=font(20,True),fill='#26364a')
    for i,(col,txt) in enumerate([('#202e41','Shared white areas'),('#ca2c74','Reference only'),('#0099b9','Reconstruction only')]):
        yy=1038+i*34
        dr.rectangle((1534,yy+3,1554,yy+23),fill=col)
        dr.text((1567,yy),txt,font=font(19),fill='#465465')
    dr.text((54,1185),'Reference-based reconstruction; not an original archival vector. Stripe regularization is visible in the overlay.',font=font(18),fill='#637080')
    board.save(OUT/'PGE-reference-comparison.png')

    letter_slice=(slice(650,1110),slice(250,1110))
    a=rm[letter_slice];b=vm[letter_slice]
    silhouette_ref=ref[:,:,3]>.5
    silhouette_vec=vec[:,:,3]>.5
    measures={
        'letter_foreground_iou':float(np.sum(a&b)/np.sum(a|b)),
        'outer_silhouette_iou':float(np.sum(silhouette_ref&silhouette_vec)/np.sum(silhouette_ref|silhouette_vec)),
        'stripe_count':STRIPE_COUNT,
        'stripe_pitch':STRIPE_PITCH,
        'stripe_height':STRIPE_HEIGHT,
        'artwork_paths':len(SHAPES),
    }
    for label,(x0,y0,x1,y1) in {'P':(270,650,620,1110),'G':(530,650,857,1110),'E':(770,650,1100,1110)}.items():
        aa=rm[y0:y1,x0:x1];bb=vm[y0:y1,x0:x1]
        measures[f'{label}_region_iou']=float(np.sum(aa&bb)/np.sum(aa|bb))
    (ANALYSIS/'validation.json').write_text(json.dumps(measures,indent=2)+'\n')
    return measures

def validate(pdf_path):
    doc=fitz.open(pdf_path)
    page=doc[0]
    images=page.get_images(full=True)
    fonts=page.get_fonts(full=True)
    assert not images,'PDF must contain no raster images'
    assert not fonts,'PDF must contain no live font resources'
    assert len(doc)==1
    pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=True)
    pix.save(ANALYSIS/'pdf-render.png')
    tree=ET.parse(OUT/'PGE-reconstructed.svg')
    ns={'svg':'http://www.w3.org/2000/svg'}
    assert not tree.findall('.//svg:image',ns)
    assert not tree.findall('.//svg:text',ns)
    paths=tree.findall('.//svg:path',ns)
    assert len(paths)==50
    print(json.dumps({'svg_paths':len(paths),'pdf_images':len(images),'pdf_fonts':len(fonts),'pdf_pages':len(doc)}))

def write_readme():
    (OUT/'README.txt').write_text('''PGE LOGO - VECTOR RECONSTRUCTION
================================

Rebuilt from the image supplied in this conversation, 12 November 2026.
This is a reference-based reconstruction, not a recovered archival master.

FILES
PGE-reconstructed.svg              Editable vector master; transparent exterior
PGE-reconstructed-vector.pdf       Vector PDF, 270 mm tall, no raster images
PGE-reconstructed-transparent.png  Transparent raster export, 2800 px wide
PGE-preview.png                    Neutral-background preview
PGE-reference-comparison.png       Source / reconstruction / aligned overlay
reconstruct_pge.py                 Reproducible construction geometry

CONSTRUCTION
The artwork is drawn from geometric primitives and explicitly authored
Bezier outlines. No automatic tracing or vectorized bitmap is used.

The SVG has four named groups: black panel, stripe grid, British Columbia
silhouette and coastal cutouts, and custom PGE lettering. All 50 artwork
objects are filled paths; the lettering is already outlined. There are no
linked fonts, embedded images, filters, masks or external dependencies.

The 38 white bands use a constant pitch of 14.55 design units and a height
of 5.5 design units. The source's slight stripe-spacing drift, image texture,
edge noise and near-opaque alpha have intentionally been regularized.
The overall layout and distinctive letter proportions have been preserved.

The black panel and white artwork are intentional parts of the design.
Only the exterior is transparent. White areas are not empty holes.

EDITING
Open the SVG in a vector editor, ungroup as needed, and edit the named paths.
P, G and E are independent objects. The narrow P counter is a compound path
using the even-odd fill rule. The small coastal cutouts are separate black
paths, making them easy to inspect or adjust.

The SVG artboard contains a 32-unit margin around the black emblem.
The PDF retains the same geometry, with a page size of approximately
249.20 x 270.00 mm. It contains vector fills only, with no live fonts.

COMPARISON
The comparison board shows the supplied reference and the reconstruction
at identical scale. In the overlay, dark navy denotes shared white areas,
magenta denotes reference-only white areas, and cyan denotes rebuilt-only
white areas. The difference around the bands is expected because the
rebuilt stripe grid is regular. The overlay is a review aid, not artwork.

REPRODUCTION
The included Python construction script uses Pillow, NumPy, svgpathtools,
ReportLab and PyMuPDF. For comparisons, place the supplied image at:
upload/Isolated vintage PGE logo on transparency(1).png
The reference is read for comparisons only; it is not used to generate paths.
''')

def main():
    make_svg(ARTBOARD,OUT/'PGE-reconstructed.svg')
    make_svg((0,0,*SOURCE_SIZE),ANALYSIS/'PGE-aligned.svg')
    pdf_path=make_pdf()
    render_svg(OUT/'PGE-reconstructed.svg',2800).save(OUT/'PGE-reconstructed-transparent.png')
    preview=render_svg(OUT/'PGE-reconstructed.svg',1000)
    Image.alpha_composite(Image.new('RGBA',preview.size,'#e8ebee'),preview).convert('RGB').save(OUT/'PGE-preview.png')
    full=render_svg(ANALYSIS/'PGE-aligned.svg')
    print(json.dumps(proof(full),indent=2))
    validate(pdf_path)
    write_readme()
    shutil.copy2(__file__,OUT/'reconstruct_pge.py')
    zpath=OUT.parent/'PGE-vector-package.zip'
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file():z.write(p,arcname='PGE-vector/'+p.name)
    print('Package:',zpath)

if __name__=='__main__':
    main()
