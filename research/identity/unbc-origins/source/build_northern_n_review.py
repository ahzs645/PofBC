"""Render the original / v1.1 / v1.2 capital-N comparison from saved evidence.

Photographic pixels appear only in this labelled proof, never in the SVG master.
No threshold boundary or photo contour is used to generate the custom N.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/font-audit/northern-n'
REF.mkdir(parents=True,exist_ok=True)
NS='{http://www.w3.org/2000/svg}'
PAPER='#F7F5EF'; INK='#1D1D1B'; MUTED='#625F58'; ORANGE='#DE8D3F'
FONT=Path('/usr/share/fonts/truetype/open-sans')
def face(size,bold=False):
    return ImageFont.truetype(str(FONT/('OpenSans-Bold.ttf' if bold else 'OpenSans-Regular.ttf')),size)

def preview(path,letter=False):
    root=ET.parse(path).getroot()
    group=next(e for e in root.iter() if e.get('id')=='northern-serif-word')
    if letter:
        element=deepcopy(next(e for e in group if e.get('id','').startswith('northern-serif-word-1-N')))
        element.set('fill',INK)
        b=BoundsPen(None);parse_path(element.get('d'),b)
        x0,y0,x1,y1=b.bounds
        view=(x0,y0,x1-x0,y1-y0)
        width=round((x1-x0)/(y1-y0)*270)
    else:
        element=deepcopy(group);view=(92,322,808,147);width=404
    wrapper=ET.Element(NS+'svg',{'viewBox':' '.join(map(str,view))})
    wrapper.append(element)
    with TemporaryDirectory() as temp:
        src=Path(temp)/'detail.svg';dst=Path(temp)/'detail.png'
        ET.ElementTree(wrapper).write(src,encoding='utf-8',xml_declaration=True)
        subprocess.run(['inkscape',str(src),'--export-type=png','--export-width='+str(width),
                        '--export-filename='+str(dst)],check=True,capture_output=True)
        return Image.open(dst).convert('RGBA').copy()

photo=Image.open(ROOT/'reference/supplied/IMG_7955(1).jpeg').convert('RGB')
source_n=photo.crop((702,497,728,523))
source_n.save(REF/'N-source-native-26x26.png')
source_word=photo.crop((698,486,865,530))
previous=REF/'northern-u-button-v1_1.svg'
current=ROOT/'svg/northern-u-button.svg'
im=Image.new('RGB',(1400,850),PAPER);d=ImageDraw.Draw(im)
d.rectangle((40,34,81,39),fill='#D17A42')
d.text((98,22),'NORTHERN U  /  CAPITAL N DETAIL',font=face(20,True),fill=MUTED)
d.text((40,64),'The N, rebuilt from the original button.',font=face(37,True),fill=INK)
d.text((40,122),'Photo evidence, previous substitute and corrected vector geometry.',font=face(22),fill=MUTED)

cols=[(40,'ORIGINAL PHOTOGRAPH'),(500,'PREVIOUS VECTOR / v1.1'),(960,'CORRECTED VECTOR / v1.2')]
for x,label in cols:
    d.line((x,175,x+400,175),fill='#CFC8BB',width=2)
    d.text((x,192),label,font=face(18,True),fill=INK)
    d.rectangle((x,238,x+400,555),fill=ORANGE)

# Original is shown without sharpening, retouching or guessed edge restoration.
large=source_n.resize((292,292),Image.Resampling.BICUBIC)
im.paste(large,(94,250))
for path,x in [(previous,500),(current,960)]:
    letter=preview(path,True)
    im.paste(letter,(x+(400-letter.width)//2,260),letter)

d.text((40,578),'As photographed; enlarged from 26 × 26 pixels.',font=face(15),fill=MUTED)
d.text((500,578),'Bookman-derived N with heavy slab serifs.',font=face(15),fill=MUTED)
d.text((960,578),'Custom path with lighter, tapered details.',font=face(15),fill=MUTED)

source_word=source_word.resize((400,105),Image.Resampling.BICUBIC)
im.paste(source_word,(40,620))
for path,x in [(previous,500),(current,960)]:
    d.rectangle((x,620,x+400,725),fill=ORANGE)
    word=preview(path)
    im.paste(word,(x-2,620+(105-word.height)//2),word)

d.line((40,758,1360,758),fill='#CFC8BB',width=2)
d.text((40,778),'Revised: thinner diagonal · tapered serifs · mainly leftward top-right serif · adjusted cap height',font=face(20),fill=INK)
d.text((40,814),'Exact historical font unconfirmed. The master is editable vector geometry; the source photograph is evidence only.',font=face(16),fill=MUTED)
im.save(REF/'Northern_N_Detail.png')
im.save(ROOT/'IUS_Font_Review_Preview.png')
print('Built Northern capital-N detail proof')
