from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import json, re, hashlib, shutil, zipfile
import fitz

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
NS={'s':'http://www.w3.org/2000/svg'}
master=ET.parse(OUT/'BC_Super_Natural_Welcome_Sign.svg').getroot()
rawflag=(ROOT/'../../../../src/assets/flagMark.js').read_text()
expected_flags=re.findall(r'\{"d":"([^"]+)","fill":"([^"]+)"\}',rawflag)
flag=master.find(".//s:g[@id='existing-spirit-of-bc-flag']",NS)
actual_flags=[(el.get('d'),el.get('fill')) for el in flag.findall('s:path',NS)]
assert expected_flags==actual_flags and len(actual_flags)==12
assert not master.findall('.//s:image',NS)
assert not master.findall('.//s:text',NS)
assert not master.findall('.//s:foreignObject',NS)
for e in master.iter():
    assert not any(k.endswith('href') for k in e.attrib)
    if e.tag.endswith('path'): assert e.get('d','').strip()
rows=master.findall(".//s:g[@data-text]",NS)
assert [r.get('data-text') for r in rows]==['Super, Natural','British Columbia','welcomes you']
glyph_table=json.loads(re.search(r'export const GLYPHS = (\{.*?\})\s*\n\}',(ROOT/'../../../../src/hydro/serif.js').read_text(),re.S).group(1)+'\n}')
letter_count=0
for row in rows:
    for g in row.findall('s:g',NS):
        ch=g.get('data-letter'); assert ch in glyph_table
        for p in g.findall('.//s:path',NS): assert p.get('d')==glyph_table[ch]['d']
        letter_count+=1
assert letter_count==39
pdf=fitz.open(OUT/'BC_Super_Natural_Welcome_Sign.pdf')
assert len(pdf)==1
assert not pdf[0].get_images(full=True)
assert not pdf[0].get_fonts(full=True)
drawings=len(pdf[0].get_drawings())
assert drawings>20
pdf[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(ROOT/'pdf-check.png')

preview=Image.open(OUT/'BC_Super_Natural_Welcome_Sign.png').convert('RGBA')
canvas=Image.new('RGBA',(1360,1380),'#e6e9eb')
canvas.alpha_composite(preview,(80,90))
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
draw.text((80,1282),'Rebuilt with the existing PofBC flag and serif outlines',font=font,fill='#233b50')
draw.text((80,1315),'Editable vector · layout reconstructed from the supplied photo',font=font,fill='#596a77')
canvas.convert('RGB').save(OUT/'BC_Super_Natural_Preview.png')

sources={
 'artwork/flag/spirit-of-bc-flag.svg':'7bc5c089eb91458a0c8827dae56212552361434b',
 'src/assets/flagMark.js':'50be0e64651e66809102f48e5491fecf7ea0cd3d',
 'src/hydro/serif.js':'c2bc9ab467b0d2ff9e72489f817eaff2dd865184',
 'src/hydro/hydroType.js':'607c4b7f1c0065375df140821567cbd3fbd1f532'
}
checks=[]
for name,expected in sources.items():
    data=(ROOT/'../../../..'/name).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert blob==expected,(name,blob,expected)
    checks.append({'path':name,'git_blob_sha1':blob,'source_bytes_unchanged':True})
validation={
 'status':'passed',
 'source_commit':'620294eec90dba2e69d94b4dde8551108f61fe37',
 'unchanged_flag_paths':12,
 'letter_instances':letter_count,
 'all_letter_path_data_matches_committed_glyphs':True,
 'lettering_adjustments':'Per-row condensation and scale; 16 source-unit vector stroke; clipped descender scaling p=0.5 comma=0.7 y=0.65. Source path d strings unchanged.',
 'svg_has_raster_images':False,
 'svg_has_live_text':False,
 'svg_has_external_dependencies':False,
 'pdf_pages':len(pdf),
 'pdf_embedded_raster_images':0,
 'pdf_font_dependencies':0,
 'pdf_vector_drawing_count':drawings,
 'sources':checks,
 'comparison':'Master projected onto four photo board corners for visual review. No tracing or raster-vectorization was used to construct the artwork.',
 'limits':['Original sign typeface not identified','Source-palette colours retained, not a verified sign paint specification','White flag-backing cut contour interpreted','No measured real-world dimensions; normalized 1200 by 1150 drawing units']
}
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps(validation,indent=2))
