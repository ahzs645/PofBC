from pathlib import Path
import json, shutil, zipfile, hashlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy import ndimage as ndi
from lxml import etree as ET
import fitz
from vector_utils import ROOT, clean_mask

out=ROOT/'output'
src=Image.open(ROOT/'upload'/'Ornate historical coat of arms.png').convert('RGBA')
vec=Image.open(ROOT/'tmp'/'final-native.png').convert('RGBA')
paper='#f4f0e7'
preview=Image.new('RGBA',vec.size,paper);preview.alpha_composite(vec)
preview.convert('RGB').save(out/'historical-bc-coat-of-arms-preview.png')

# Reference and reconstruction share the same canvas and placement.
plate=Image.new('RGB',(2522,1390),paper)
draw=ImageDraw.Draw(plate)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
header=ImageFont.truetype(font,28)
small=ImageFont.truetype(font,20)
for i,(im,label) in enumerate([(src,'SUPPLIED REFERENCE'),(vec,'VECTOR RECONSTRUCTION')]):
    bg=Image.new('RGBA',im.size,paper);bg.alpha_composite(im)
    plate.paste(bg.convert('RGB'),(i*1261,86))
    draw.text((i*1261+36,26),label,font=header,fill='#252422')
draw.text((36,1351),'Same scale and registration. Printed dots and stray pixels are intentionally omitted from the reconstruction.',font=small,fill='#58544c')
plate.save(out/'historical-bc-coat-of-arms-comparison.png')

# Registered closeups make the corrections directly reviewable.
baseline_path=ROOT/'reference'/'first-vector.png'
if not baseline_path.exists():
    baseline_path.parent.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'tmp'/'revision-baseline'/'tmp'/'final-native.png',baseline_path)
before=Image.open(baseline_path).convert('RGBA')
details=[
    ('Antlers: narrow interiors and branch crossings',(0,278,313,447)),
    ('Scrolls: rounded curls and the central band',(498,1001,840,1220)),
    ('Shield: inset diagonal tips and the crown underside',(432,518,913,741)),
    ('Crest: restored toe tips and corrected jewel proportions',(487,270,839,535))]
col_w=580;gap=20;margin=30;top=115
detail_width=3*col_w+2*gap+2*margin
row_heights=[round((b[3]-b[1])*(col_w-16)/(b[2]-b[0]))+64 for _,b in details]
review=Image.new('RGB',(detail_width,top+sum(row_heights)+45),paper)
rd=ImageDraw.Draw(review)
rd.text((margin,20),'COAT OF ARMS - DETAIL REVIEW',font=ImageFont.truetype(font,31),fill='#252422')
for i,label in enumerate(['SUPPLIED REFERENCE','FIRST VECTOR','REVISED VECTOR']):
    rd.text((margin+i*(col_w+gap),75),label,font=ImageFont.truetype(font,22),fill='#58544c')
y=top
for (title,box),row_h in zip(details,row_heights):
    rd.text((margin,y+8),title,font=ImageFont.truetype(font,23),fill='#252422')
    w,h=box[2]-box[0],box[3]-box[1]
    size=(col_w-16,round(h*(col_w-16)/w))
    for i,im in enumerate([src,before,vec]):
        crop=im.crop(box);bg=Image.new('RGBA',crop.size,paper);bg.alpha_composite(crop)
        review.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),(margin+i*(col_w+gap)+8,y+43))
    y+=row_h
rd.text((margin,y+8),'Aligned crops at the same scale. Printed dots are intentionally omitted from the vector.',font=ImageFont.truetype(font,18),fill='#58544c')
review.save(out/'historical-bc-coat-of-arms-detail-review.png')

# This diagnostic compares silhouette only, not internal accuracy.
s=clean_mask(np.array(src)[:,:,3]>180,sigma=.45,min_size=30,hole_size=10)
v=np.array(vec)[:,:,3]>180
se=s^ndi.binary_erosion(s,iterations=2)
ve=v^ndi.binary_erosion(v,iterations=2)
pixels=np.full((*s.shape,3),248,dtype=np.uint8)
pixels[s&v]=[226,228,227];pixels[se]=[0,137,179];pixels[ve]=[216,45,106];pixels[se&ve]=[30,30,30]
overlay=Image.new('RGB',(1261,1340),'#f8f8f8');overlay.paste(Image.fromarray(pixels),(0,80))
d=ImageDraw.Draw(overlay)
d.text((28,15),'OUTER SILHOUETTE CHECK',font=header,fill='#252422')
d.text((28,52),'Reference: cyan   Vector: magenta   Coincident edges: dark',font=small,fill='#58544c')
overlay.save(out/'historical-bc-coat-of-arms-silhouette-overlay.png')

# Validate delivered vector formats, including the PDF independently.
tree=ET.parse(str(out/'historical-bc-coat-of-arms.svg'))
tags=[ET.QName(el).localname for el in tree.getroot().iter()]
pdf=fitz.open(out/'historical-bc-coat-of-arms.pdf')
ids=[el.get('id') for el in tree.getroot().iter() if el.get('id')]
checks={'revision':2,'svg_paths':tags.count('path'),'svg_ellipses':tags.count('ellipse'),'svg_circles':tags.count('circle'),'svg_embedded_images':tags.count('image'),'svg_live_text_elements':tags.count('text'),'svg_duplicate_ids':len(ids)-len(set(ids)),'pdf_pages':len(pdf),'pdf_images':sum(len(p.get_images(full=True)) for p in pdf),'pdf_vector_drawing_objects':sum(len(p.get_drawings()) for p in pdf),'transparent_png_size':list(Image.open(out/'historical-bc-coat-of-arms-4000px.png').size)}
assert checks['svg_embedded_images']==0 and checks['svg_live_text_elements']==0
assert checks['svg_duplicate_ids']==0
assert checks['pdf_images']==0 and checks['pdf_vector_drawing_objects']>0
for el in tree.getroot().iter():
    for name,value in el.attrib.items():
        if ET.QName(name).localname in ['href','src']:
            assert value.startswith('#'),(name,value)
pdf[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(ROOT/'tmp'/'pdf-final-check.png')
pdf.close()
(out/'vector-validation.json').write_text(json.dumps(checks,indent=2)+'\n')

readme='''# Historical coat of arms: vector reconstruction

This package rebuilds the supplied “Ornate historical coat of arms.png” as scalable, editable vector artwork. It is a reconstruction of that specific supplied drawing, not an authenticated official vector master.

## Main files

- `historical-bc-coat-of-arms.svg`: main editable artwork, on the source's 1261 × 1247 coordinate system, with a transparent outer background.
- `historical-bc-coat-of-arms.pdf`: one-page vector export. No raster images are embedded.
- `historical-bc-coat-of-arms-4000px.png`: transparent raster export, 4000 pixels wide, for convenient use in applications that do not accept SVG.
- `previews/historical-bc-coat-of-arms-preview.png`: the finished artwork on a warm neutral background.
- `previews/historical-bc-coat-of-arms-comparison.png`: reference and reconstruction at the same scale and registration.
- `previews/historical-bc-coat-of-arms-detail-review.png`: aligned reference / first vector / revised vector closeups for the antlers, inner scrolls, shield, and crown.
- `previews/historical-bc-coat-of-arms-silhouette-overlay.png`: cyan reference boundaries and magenta vector boundaries. This checks external contours only; it does not measure the accuracy of internal details.

## Reconstruction decisions

The lion, stag, and ram retain source-guided outlines and engraving-like details. Printed halftone dots were removed before curves were fitted and cleaned. Contact points, hooves, and stray colour fragments were inspected separately.

The shield, flag geometry, waves, sun rays, small crown, ribbon curves, large-crown jewels, and pearl beads were selectively redrawn or regularised. The clean result deliberately differs from the coarse printed texture.

## Revision 2: detail corrections

- Antlers: restored narrowed ivory runs and excessive black weight at branch crossings. The outer silhouette, number of tines, and spacing between branches are unchanged. The thin upper-left twig interior was rebuilt as a tapered curve.
- Scrolls: recovered the rounded inner curls, continuous edge into the SINE panel, original bowl depth, and outer roll seams. Removed the first version's triangular fold closures and duplicate edges below the hooves. The 18 outlined letters are unchanged.
- Shield: reconstructed the inset, rounded red diagonal tips and open white junctions; corrected the small crown's oval underside and the chief's dividing line. Refitted the sun-ray curves against the source while keeping the visible ray tips anchored.
- Crest: repaired the small crown's disconnected gold arch and the overlap that hid the lion's toe tips. Preserved more mane detail, restored the shoulder incision, and corrected crown gem interiors separately from their borders.

These changes followed enlarged, registered comparisons. The very small cross lobes and fine printed mane edges remain interpretations of the supplied raster.

The motto is outlined vector lettering, preserving the original letter widths, positions, and curved baseline without substituting a font. The visible break in the N of SINE was repaired. The text reads SPLENDOR SINE OCCASU.

The palette is normalised to ink #171513, warm ivory #FFF5DF, gold #FFC928, red #EE3429, blue #168FC1, ribbon outline #CD365A, and the flag's narrow red edge #AE3343. This is a visual reconstruction palette, not a claim about official colour specifications.

## Editing

Open the SVG in Inkscape, Illustrator, Affinity Designer, or another vector editor. Named groups separate the shield, crowns, lion, stag, ram, ribbon, and motto. All visible SVG content is vector geometry, including the lettering. There are no bitmap images or external font dependencies in the SVG. The supporters contain compound paths; their internal contours can be edited with a node tool.

The PDF is also vector. The PNG files are preview/convenience exports and are not editable vector artwork.

## Rebuilding

The `rebuild` directory includes the source raster, component SVGs, and the Python source used to make the artwork. Requirements: Python 3, NumPy, SciPy, Pillow, lxml, the system libpotrace library, and Inkscape for export.

From the `rebuild` directory:

```sh
python build_artwork.py
inkscape output/historical-bc-coat-of-arms.svg --export-type=pdf --export-filename=output/historical-bc-coat-of-arms.pdf
```

The main build script rebuilds all five components before assembling them. The reconstruction uses a combination of source-guided curve fitting and manually defined geometry. It should not be described as an entirely manual redraw or as untouched original artwork.

## Verification

The final SVG and PDF were rendered and visually inspected, including the faces, antlers, horns, crown, shield contacts, hooves, ribbon, and motto. The final files were checked for embedded images and live text. Machine-readable format checks are in `vector-validation.json`.
'''
(out/'README.md').write_text(readme)

archive=out/'historical-bc-coat-of-arms-vector-package.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in ['historical-bc-coat-of-arms.svg','historical-bc-coat-of-arms.pdf','historical-bc-coat-of-arms-4000px.png','README.md','vector-validation.json']:
        z.write(out/name,name)
    for name in ['historical-bc-coat-of-arms-preview.png','historical-bc-coat-of-arms-comparison.png','historical-bc-coat-of-arms-silhouette-overlay.png','historical-bc-coat-of-arms-detail-review.png']:
        z.write(out/name,'previews/'+name)
    for name in ['vector_utils.py','build_artwork.py','package_deliverables.py']:
        z.write(ROOT/name,'rebuild/'+name)
    for f in sorted((ROOT/'components').glob('*')):
        if f.is_file() and f.suffix in ['.svg','.py']:
            z.write(f,'rebuild/components/'+f.name)
    z.write(ROOT/'upload'/'Ornate historical coat of arms.png','rebuild/upload/Ornate historical coat of arms.png')
    z.write(baseline_path,'rebuild/reference/first-vector.png')
print(json.dumps(checks,indent=2))
print('ZIP',archive.stat().st_size,'bytes')
print('FILES',[(p.name,p.stat().st_size) for p in out.iterdir() if p.is_file()])
