#!/usr/bin/env python3
"""Construct IUS campaign vectors from typography and intentional geometry.
No raster tracing. Masters contain editable paths and named groups only.
Requires fontTools and system URW Base35 OTF fonts. Inkscape expands outline strokes.
"""
from pathlib import Path
from xml.sax.saxutils import escape
from math import sin,cos,radians
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
import json, subprocess, re
HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'svg'; OUT.mkdir(exist_ok=True)
FONTDIR=Path('/usr/share/fonts/opentype/urw-base35')
INK='#1D1D1B'; ORANGE='#DE8D3F'; YELLOW='#EDC367'; PAPER='#F1E4C5'; LABEL_PAPER='#F0EFE1'; GRAY='#A8AA9D'; BLUE='#37647A'
_cache={}
def font(name):
 if name not in _cache:
  f=TTFont(FONTDIR/(name+'.otf')); _cache[name]=(f,f.getGlyphSet(),f.getBestCmap())
 return _cache[name]
def fmt(v): return f'{v:.4f}'.rstrip('0').rstrip('.') if abs(v)>0.00001 else '0'
def glyph_data(text,name,tracking=0):
 f,gs,cm=font(name); xpos=0; vals=[]; xmin=1e9; ymin=1e9; xmax=-1e9;ymax=-1e9
 kern={}
 if 'kern' in f:
  for k in f['kern'].kernTables:kern.update(k.kernTable)
 prev=None
 for ch in text:
  gn=cm.get(ord(ch),'space'); xpos+=kern.get((prev,gn),0) if prev else 0
  bp=BoundsPen(gs); gs[gn].draw(bp)
  if bp.bounds:
   b=bp.bounds;xmin=min(xmin,xpos+b[0]);xmax=max(xmax,xpos+b[2]);ymin=min(ymin,b[1]);ymax=max(ymax,b[3])
  vals.append((ch,gn,xpos));xpos+=f['hmtx'][gn][0]+tracking;prev=gn
 return (f,gs,vals,(xmin,ymin,xmax,ymax))
def word(text,name,x,y,w,h,color=INK,ident=None,tracking=0):
 f,gs,vals,b=glyph_data(text,name,tracking);xmin,ymin,xmax,ymax=b
 sx=w/(xmax-xmin);sy=h/(ymax-ymin)
 paths=[]
 for idx,(ch,gn,xpos) in enumerate(vals):
  if ch==' ':continue
  pen=SVGPathPen(gs,ntos=fmt);tp=TransformPen(pen,(sx,0,0,-sy,x+(xpos-xmin)*sx,y+ymax*sy));gs[gn].draw(tp)
  paths.append(f'<path id="{ident or "word"}-{idx+1}-{escape(ch)}" d="{pen.getCommands()}"/>')
 return f'<g id="{ident or "word"}" aria-label="{escape(text)}" fill="{color}">'+''.join(paths)+'</g>'
def poly(points):return 'M'+'L'.join(f'{fmt(x)} {fmt(y)}' for x,y in points)+'Z'
def circle(cx,cy,r,fill,ident):
 return f'<path id="{ident}" fill="{fill}" d="M{fmt(cx-r)} {fmt(cy)}a{fmt(r)} {fmt(r)} 0 1 0 {fmt(2*r)} 0a{fmt(r)} {fmt(r)} 0 1 0 {fmt(-2*r)} 0Z"/>'
def rect(x,y,w,h,fill,ident):return f'<path id="{ident}" fill="{fill}" d="M{fmt(x)} {fmt(y)}h{fmt(w)}v{fmt(h)}h{fmt(-w)}Z"/>'
def svg(w,h,title,description,body):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>{body}</svg>'''
def save(name,w,h,title,desc,body):
 p=OUT/(name+'.svg');p.write_text(svg(w,h,title,desc,body));return p

def northern_word():
 # Retain the fitted Bookman-derived lowercase outlines. The source N is a
 # distinct construction: thin tapered serifs, a lighter diagonal, a higher
 # cap, and a top-right cap that projects chiefly to the left of the stem.
 # Its low-resolution source is a visual guide, never an automatic trace.
 body=word('Northern','URWBookman-Demi',104,327,792,137,ident='northern-serif-word')
 n_path=('M0 3C8 3 14 0 24 0C28 0 31 4 35 9L85 65V16'
         'C85 9 80 6 68 5V1H100V98C100 101 97 102 94 99'
         'L28 28V82C28 91 32 95 46 97V101H2V97'
         'C10 95 12 92 12 83V17C12 10 8 7 0 6Z')
 # Preserve the N-o gap and shared baseline. Match N/o proportions locally;
 # do not reproduce the dome's camera-dependent warp across the whole word.
 pen=SVGPathPen(None,ntos=fmt)
 parse_path(n_path,TransformPen(pen,(1.28,0,0,135/101,96.3731,327.3179)))
 replacement='<path id="northern-serif-word-1-N-custom" d="'+pen.getCommands()+'"/>'
 return re.sub(r'<path id="northern-serif-word-1-N"[^>]*/>',lambda _:replacement,body)

def northern_button():
 body=circle(500,500,490,ORANGE,'orange-button-face')
 body+=northern_word()
 # Purpose-built U: nearly even stems, leftward top serifs and a flatter bowl.
 # The right stem ends directly in the bowl, without a lowercase exit foot.
 u_path='M0 0H125V18C115 19 112 24 112 45V184C112 222 129 240 167 240C196 240 218 227 233 209V43C233 25 224 19 202 18H190V0H320V253C285 273 240 280 178 280C94 280 33 264 33 203V43C33 24 22 19 0 18Z'
 pen=SVGPathPen(None,ntos=fmt);parse_path(u_path,TransformPen(pen,(1,0,0,1,340,507)))
 body+=f'<g id="large-U" aria-label="U" fill="{INK}"><path id="large-U-custom-bowl" d="{pen.getCommands()}"/></g>'
 save('northern-u-button',1000,1000,'Northern U campaign button','Flat vector reconstruction of the orange Northern U button shown in IMG_7955(1).jpeg. Northern combines a purpose-built capital N with fitted Bookman-derived lowercase outlines. The N has thinner tapered serifs, a lighter diagonal and a mainly leftward top-right cap; the large U is separately constructed from the observed serif, stem and bowl geometry. These are reconstruction choices, not an identified historical font. Photograph-derived colour is approximate. No physical glare or dome is included.',body)

# Geometric extended NORTHERN: deliberately built square bowls, constant bars,
# and simple diagonals. Widths and terminals fitted optically to source photo.
def northern_geometric(x,y,w,h):
 shapes={
 'N':(94,[[ (0,0),(18,0),(76,70),(76,0),(94,0),(94,100),(76,100),(18,30),(18,100),(0,100) ]]),
 'O':(102,[[(17,0),(85,0),(102,17),(102,83),(85,100),(17,100),(0,83),(0,17)],[(23,18),(18,23),(18,77),(23,82),(79,82),(84,77),(84,23),(79,18)]]),
 'R':(98,[[(0,0),(79,0),(98,17),(98,48),(79,64),(98,100),(77,100),(57,64),(18,64),(18,100),(0,100)],[(18,18),(18,46),(74,46),(80,40),(80,24),(74,18)]]),
 'T':(94,[[(0,0),(94,0),(94,19),(57,19),(57,100),(37,100),(37,19),(0,19)]]),
 'H':(96,[[(0,0),(19,0),(19,39),(77,39),(77,0),(96,0),(96,100),(77,100),(77,59),(19,59),(19,100),(0,100)]]),
 'E':(90,[[(0,0),(90,0),(90,18),(18,18),(18,41),(83,41),(83,59),(18,59),(18,82),(90,82),(90,100),(0,100)]]),
 }
 text='NORTHERN';gap=14;full=sum(shapes[c][0] for c in text)+gap*(len(text)-1);sx=w/full;sy=h/100;cur=0;items=[]
 for i,ch in enumerate(text):
  gw,pp=shapes[ch]
  rounded={
   'O':'M18 0H84C93.94 0 102 8.06 102 18V82C102 91.94 93.94 100 84 100H18C8.06 100 0 91.94 0 82V18C0 8.06 8.06 0 18 0ZM24 18C20.686 18 18 20.686 18 24V76C18 79.314 20.686 82 24 82H78C81.314 82 84 79.314 84 76V24C84 20.686 81.314 18 78 18Z',
   'R':'M0 0H78C92 0 98 7 98 20V43C98 57 91 64 78 64L98 100H77L57 64H18V100H0ZM18 18V46H74C78 46 80 44 80 38V26C80 21 78 18 73 18Z'
  }
  if ch in rounded:
   pen=SVGPathPen(None,ntos=fmt);parse_path(rounded[ch],TransformPen(pen,(sx,0,0,sy,x+cur*sx,y)));d=pen.getCommands()
  else:d=''.join(poly([(x+(xx+cur)*sx,y+yy*sy) for xx,yy in p]) for p in pp)
  items.append(f'<path id="northern-geometric-{i+1}-{ch}" fill-rule="evenodd" d="{d}"/>');cur+=gw+gap
 return '<g id="northern-geometric" fill="'+INK+'" aria-label="NORTHERN">'+''.join(items)+'</g>'

COLLEGE={
'I':(55,[[(0,0),(55,0),(55,16),(43,16),(43,84),(55,84),(55,100),(0,100),(0,84),(12,84),(12,16),(0,16)]]),
'N':(86,[[(0,0),(27,0),(60,63),(60,16),(50,16),(50,0),(86,0),(86,16),(77,16),(77,100),(56,100),(24,38),(24,84),(34,84),(34,100),(0,100),(0,84),(10,84),(10,16),(0,16)]]),
'T':(83,[[(0,0),(83,0),(83,30),(66,30),(66,17),(53,17),(53,84),(65,84),(65,100),(18,100),(18,84),(30,84),(30,17),(17,17),(17,30),(0,30)]]),
'E':(77,[[(0,0),(77,0),(77,30),(60,30),(60,17),(30,17),(30,40),(54,40),(54,31),(68,31),(68,69),(54,69),(54,60),(30,60),(30,83),(60,83),(60,70),(77,70),(77,100),(0,100),(0,84),(9,84),(9,16),(0,16)]]),
'R':(91,[[(0,0),(65,0),(81,16),(81,45),(69,57),(81,84),(91,84),(91,100),(55,100),(42,64),(30,64),(30,84),(39,84),(39,100),(0,100),(0,84),(10,84),(10,16),(0,16)],[(30,17),(57,17),(62,22),(62,40),(57,45),(30,45)]]),
'O':(81,[[(17,0),(64,0),(81,17),(81,83),(64,100),(17,100),(0,83),(0,17)],[(25,18),(55,18),(61,24),(61,76),(55,82),(25,82),(20,76),(20,24)]])}
def college(x,y,w,h):
 text='INTERIOR'; gap=10;full=sum(COLLEGE[c][0] for c in text)+gap*7;sx=w/full;sy=h/100;cur=0;items=[]
 for i,ch in enumerate(text):
  gw,pp=COLLEGE[ch]
  for j,p in enumerate(pp):
   d=poly([(x+(xx+cur)*sx,y+yy*sy) for xx,yy in p]);items.append(f'<path id="interior-college-{i+1}-{ch}-{j+1}" d="{d}"/>')
  cur+=gw+gap
 return f'<g id="interior-collegiate-outline" aria-label="INTERIOR" fill="none" stroke="{INK}" stroke-width="5.3" stroke-linejoin="miter" stroke-miterlimit="4">'+''.join(items)+'</g>'
def arc_university():
 # Each outlined character is positioned on a circular baseline individually.
 text='UNIVERSITY';fontname='NimbusRoman-Bold';f,gs,cm=font(fontname)
 adv=[f['hmtx'][cm[ord(c)]][0] for c in text];total=sum(adv);span=145;start=162.5;cursor=0;parts=[]
 for i,(ch,a) in enumerate(zip(text,adv)):
  angle=start-(cursor+a/2)/total*span;rad=radians(angle);bx=500+431*cos(rad);by=500+431*sin(rad)
  bp=BoundsPen(gs);gs[cm[ord(ch)]].draw(bp);xmin,ymin,xmax,ymax=bp.bounds
  hh=100;ww=(xmax-xmin)/(ymax-ymin)*hh*0.82
  one=word(ch,fontname,-ww/2,-hh,ww,hh,ident=f'university-arc-{i+1}-{ch}')
  parts.append(f'<g transform="translate({fmt(bx)} {fmt(by)}) rotate({fmt(angle-90)})">'+one+'</g>');cursor+=a
 return '<g id="university-bottom-arc" aria-label="UNIVERSITY">'+''.join(parts)+'</g>'
def yes_button():
 body=circle(500,500,490,INK,'outer-printed-ring')+circle(500,500,463,PAPER,'cream-button-face')
 body+=word('I','NimbusRoman-Bold',483,65,35,93,ident='top-I')
 body+=word('SAY YES TO','NimbusRoman-Bold',192.5,194,615,113,ident='say-yes-to')
 body+=northern_geometric(171,326,658,50)
 body+=college(62,401,876,137)
 body+=word('YES','NimbusRoman-Bold',346,620,308,103,ident='center-yes')
 body+=arc_university()
 p=save('say-yes-button',1000,1000,'I say yes to Northern Interior University button','Reconstructed campaign button from IMG_7950.jpeg. The collegiate INTERIOR and geometric NORTHERN are purpose-built geometry; serif lettering is fitted Nimbus Roman Bold outlines. Photographic perspective removed by rebuilding a circle. Typeface identities, exact dimensions and colours are unconfirmed.',body)
 # Expand explicit outline geometry into filled paths, keeping groups.
 subprocess.run(['inkscape',str(p),'--export-text-to-path','--export-plain-svg','--export-type=svg','--export-filename='+str(p.with_name('say-yes-button-expanded.svg')),'--actions=select-all:all;object-stroke-to-path'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 expanded=p.with_name('say-yes-button-expanded.svg')
 if expanded.exists():
  from xml.etree import ElementTree as ET
  ET.register_namespace('', 'http://www.w3.org/2000/svg')
  tree=ET.parse(expanded)
  for el in tree.iter():
   if el.get('id')=='interior-collegiate-outline':
    for key in list(el.attrib):
     if key.startswith('stroke'):el.attrib.pop(key)
    el.set('fill',INK)
  tree.write(p,encoding='utf-8',xml_declaration=True);expanded.unlink()

def bumper():
 body=rect(0,0,1400,390,YELLOW,'yellow-sticker-stock')
 body+=word('I support the','NimbusRoman-BoldItalic',58,39,720,102,ident='support-italic-intro',tracking=15)
 body+=word('INTERIOR UNIVERSITY','NimbusSansNarrow-Bold',54,174,1292,158,ident='condensed-university-line',tracking=0)
 body+=rect(54,348,1292,11,INK,'underline')
 save('i-support-interior-university-sticker',1400,390,'I support the Interior University sticker','Typographic vector reconstruction of the yellow bumper sticker in IMG_7947.jpeg and IMG_7955(1).jpeg. Fitted Nimbus Roman Bold Italic and Nimbus Sans Narrow Bold outlines approximate the historical lettering. Colour and aspect ratio are approximate.',body)

def toll_free():
 body=rect(0,0,1200,380,LABEL_PAPER,'cream-sticker-stock')
 body+=rect(48,48,1104,284,GRAY,'gray-frame')
 body+=rect(64,64,1072,252,LABEL_PAPER,'frame-inset')
 body+=rect(64,64,315,252,GRAY,'gray-label-block')
 body+=rect(379,219,757,7,GRAY,'horizontal-divider')
 for text,y in [('CALL',85),('TOLL',161),('FREE',237)]:body+=word(text,'URWBookman-Demi',84,y,274,62,color=LABEL_PAPER,ident='label-'+text.lower())
 body+=word('INTERIOR','NimbusSans-Regular',592,91,328,48,color=BLUE,ident='name-interior')
 body+=word('UNIVERSITY SOCIETY','NimbusSans-Regular',431,151,650,43,color=BLUE,ident='name-university-society')
 body+=word('1-800-663-3219','URWBookman-Demi',413,245,690,57,color=BLUE,ident='historical-phone-number')
 save('call-toll-free-sticker',1200,380,'Interior University Society historical toll-free sticker','Archival reconstruction from IMG_7952.jpeg. The printed historical number 1-800-663-3219 is reproduced as source text, not presented as an active contact. Gray frame, cream stock and blue lettering are approximate. The serif label and numerals use fitted URW Bookman Demi outlines after a multi-family comparison; the society name uses Nimbus Sans Regular. Exact original fonts are unconfirmed.',body)

def render():
 prev=HERE.parent/'png';prev.mkdir(exist_ok=True)
 for p in sorted(OUT.glob('*.svg')):
  subprocess.run(['inkscape',str(p),'--export-type=png','--export-width=1400','--export-filename='+str(prev/(p.stem+'.png'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

if __name__=='__main__':
 northern_button();yes_button();bumper();toll_free()
 assets=[
 {'file':'northern-u-button.svg','source':['IMG_7955(1).jpeg','IMG_7947.jpeg'],'construction':'Circle; purpose-built capital N with tapered serifs and a lighter diagonal; fitted Bookman-derived lowercase orthern; separately built large U with nearly even stems and a flatter bowl','font_approximation':['Custom N + fitted URWBookman-Demi for lowercase orthern; custom U'],'uncertainties':['Original typeface unconfirmed','N geometry inferred from a roughly 25-pixel-high photographed letter','Orange approximated from reflective photograph','Physical button diameter not measured'],'status':'evidence-led reconstruction'},
 {'file':'say-yes-button.svg','source':['IMG_7950.jpeg','IMG_7947.jpeg'],'construction':'Circular field and ring; explicit geometric NORTHERN with rounded O and R corners; custom slab collegiate INTERIOR with expanded outline strokes; per-letter curved UNIVERSITY baseline; serif outlines elsewhere','font_approximation':['NimbusRoman-Bold'],'uncertainties':['Typeface identities unconfirmed','Collegiate letter geometry is a clean reconstruction','Button diameter and original paper tint unconfirmed'],'status':'evidence-led reconstruction'},
 {'file':'i-support-interior-university-sticker.svg','source':['IMG_7955(1).jpeg','IMG_7947.jpeg'],'construction':'Rectangle, underline and individually outlined letters','font_approximation':['NimbusRoman-BoldItalic','NimbusSansNarrow-Bold'],'uncertainties':['True aspect ratio inferred from oblique photographs','Original typefaces unconfirmed','Yellow approximates photographed stock'],'status':'evidence-led reconstruction'},
 {'file':'call-toll-free-sticker.svg','source':['IMG_7952.jpeg','IMG_7955(1).jpeg'],'construction':'Paper and frame rectangles, divider and individually outlined letters','font_approximation':['URWBookman-Demi for label and numerals','NimbusSans-Regular for society name'],'uncertainties':['Gray and blue approximated through display glass','Original typefaces unconfirmed','Historical number is archival, not verified active'],'status':'evidence-led reconstruction'},
 ]
 (HERE/'campaign_metadata.json').write_text(json.dumps({'method':'Purpose-built vector geometry and actual typographic outlines; no image tracing and no embedded raster artwork.','palette':{'ink':INK,'northern_button_orange':ORANGE,'support_sticker_yellow':YELLOW,'yes_button_cream':PAPER,'toll_free_stock':LABEL_PAPER,'toll_free_gray':GRAY,'toll_free_blue':BLUE},'assets':assets},indent=2))
 print('Built',len(assets),'campaign SVG masters and metadata')
