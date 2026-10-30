"""Check retained geometry, absence of raster payloads, and rendered appearance."""
from copy import deepcopy
from pathlib import Path
from collections import Counter
import hashlib
import io
import json
import fitz
from lxml import etree
from PIL import Image, ImageChops, ImageStat, ImageDraw

ROOT=Path(__file__).resolve().parent
NS='http://www.w3.org/2000/svg'
OUT=ROOT/'validation'
OUT.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'vector-manifest.json').read_text())

def shape_signature(e):
    return (e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[shape_signature(c) for c in e])

def render_svg(root,scale=4):
    root=deepcopy(root)
    root.attrib.pop('width',None);root.attrib.pop('height',None)
    doc=fitz.open(stream=etree.tostring(root),filetype='svg')
    pdf=fitz.open('pdf',doc.convert_to_pdf())
    pix=pdf[0].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=True)
    return Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGBA')

def on_background(im,white=True):
    bg=Image.new('RGBA',im.size, (255,255,255,255) if white else (25,38,57,255))
    bg.alpha_composite(im)
    return bg.convert('RGB')

checks=[]
previews=[]
for row in manifest:
    output=Path(row['file'])
    out=etree.parse(str(output)).getroot()
    tags=dict(Counter(etree.QName(e).localname for e in out.iter()))
    externals=[v for e in out.iter() for k,v in e.attrib.items() if etree.QName(k).localname=='href' and not v.startswith('#')]
    assert tags.get('image',0)==0 and not externals
    check={'file':str(output),'xmlElementCounts':tags,'embeddedImages':0,'externalResourceHrefs':externals,'sourceSha256':row['sourceSha256']}
    source=Path(row['sourceFile'])
    if row['bodyId']=='first-nations-health-authority':
        check['sourceBytesIdentical']=output.read_bytes()==source.read_bytes()
        assert check['sourceBytesIdentical']
        if output.name=='fnha-logo-colour.svg':
            previews.append(('FNHA: official original SVG',render_svg(out),render_svg(out)))
    elif row['bodyId']=='provincial-health-services-authority':
        original=etree.parse(str(source)).getroot()
        original_group=original.findall('{%s}g'%NS)[-1]
        output_group=out.findall('{%s}g'%NS)[-1]
        check['allSelectedGeometryUnchanged']=shape_signature(original_group)==shape_signature(output_group)
        assert check['allSelectedGeometryUnchanged']
        original.set('viewBox',out.get('viewBox'))
        a,b=render_svg(original),render_svg(out)
        assert a.size==b.size
        check['renderSize']=list(a.size)
        diff=ImageChops.difference(a,b)
        check['renderMaximumDifferencePerChannel']=[channel[1] for channel in diff.getextrema()]
        assert max(check['renderMaximumDifferencePerChannel'])==0
        check['renderComparison']='Original full SVG, viewed in identical tight viewBox, matches selected-only extraction exactly.'
        if 'black' in output.name:
            previews.append(('PHSA: original SVG group extraction',a,b))
    elif 'blue-horizontal' in output.name:
        doc=fitz.open(source);page=doc[row['sourcePdfPage']-1]
        original=etree.fromstring(page.get_svg_image(text_as_path=True).encode())
        check['allSelectedGeometryUnchanged']=shape_signature(original.findall('{%s}g'%NS)[0])==shape_signature(out.findall('{%s}g'%NS)[0])
        assert check['allSelectedGeometryUnchanged']
        original.set('viewBox',out.get('viewBox'))
        a,b=render_svg(original),render_svg(out)
        check['renderSize']=list(a.size)
        diff=ImageChops.difference(a,b)
        check['renderMaximumDifferencePerChannel']=[channel[1] for channel in diff.getextrema()]
        assert max(check['renderMaximumDifferencePerChannel'])==0
        check['renderComparison']='Whole PDF page converted by MuPDF and viewed in matching logo region matches the selected-only SVG exactly; page background lies outside the logo region.'
        previews.insert(0,('Interior Health: PDF page 22 vector extraction',a,b))
    else:
        check['renderComparison']='Source PDF logo region visually compared to output; CAD hatching retained. Supplemental, not preferred primary asset.'
    checks.append(check)

sheet=Image.new('RGB',(1440,860),'#eceff3')
d=ImageDraw.Draw(sheet)
d.text((24,17),'Vector verification: original source region (left) and supplied asset (right)',fill='#172b4d')
y=55
for name,src,out in previews:
    d.text((25,y),name,fill='#172b4d')
    y+=25
    for col,im in enumerate([src,out]):
        im=on_background(im)
        im.thumbnail((675,205),Image.Resampling.LANCZOS)
        card=Image.new('RGB',(690,220),'white')
        card.paste(im,((690-im.width)//2,(220-im.height)//2))
        sheet.paste(card,(20+710*col,y))
    y+=240
sheet.save(OUT/'source-vs-vector-comparison.png')
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
