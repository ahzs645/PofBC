"""Our British Columbia (1986): measured native vector reconstruction.

Rebuilds the geometric print design, authored title curves, outlined billing,
and reusable PofBC flag component. Does not trace image contours or embed pixels.
"""
from pathlib import Path
import json, re, sys, shutil
from xml.sax.saxutils import escape
from lxml import etree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from title_lettering import title_group, our_group

ROOT=Path(__file__).resolve().parents[1]
BUNDLED=(ROOT/'assets').exists()
ASSETS=ROOT/'assets' if BUNDLED else ROOT/'research-assets'
FONTDIR=ROOT/'fonts' if BUNDLED else ROOT/'type-research'
OUT=ROOT if BUNDLED else ROOT/'output/our-british-columbia'
OUT.mkdir(parents=True,exist_ok=True)
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
COL={'paper':'#ffffff','blue':'#143799','red':'#e51d30','gold':'#ffc000','black':'#24231b'}
FONTS={'billing':FONTDIR/'SixCaps.ttf', 'fine':FONTDIR/'Oswald300.ttf'}

class Face:
    def __init__(self,p):
        self.tt=TTFont(p);self.gs=self.tt.getGlyphSet();self.cm=self.tt.getBestCmap()
        self.cap=self.bounds('H')[3]
    def bounds(self,ch):
        p=BoundsPen(self.gs);self.gs[self.cm.get(ord(ch),'.notdef')].draw(p)
        return p.bounds or (0,0,0,0)
    def run(self,txt):
        p=SVGPathPen(self.gs);x=0;bits=[];bounds=[]
        for ch in txt:
            name=self.cm.get(ord(ch),'.notdef')
            pen=SVGPathPen(self.gs);self.gs[name].draw(pen)
            d=pen.getCommands()
            if d:bits.append(f'<path d="{d}" transform="translate({x} 0)"/>')
            b=self.bounds(ch)
            if b[2]>b[0]:bounds.append((x+b[0],b[1],x+b[2],b[3]))
            x+=self.tt['hmtx'].metrics[name][0]
        b=(min(z[0] for z in bounds),min(z[1] for z in bounds),max(z[2] for z in bounds),max(z[3] for z in bounds)) if bounds else (0,0,x,self.cap)
        return ''.join(bits),b,x

faces={k:Face(v) for k,v in FONTS.items()}
credit_records=[]

def text_box(txt,x,y,w,h,face='billing',ident=None,note=None,italic=False,live=False):
    f=faces[face];paths,b,advance=f.run(txt);sx=w/(b[2]-b[0]);sy=h/(b[3]-b[1])
    tx=x-b[0]*sx;ty=y+b[3]*sy
    ident=ident or 'credit-'+str(len(credit_records)+1)
    if not live:credit_records.append(dict(id=ident,text=txt,x=x,y=y,width=w,height=h,face=face,confidence=note or 'readable'))
    metadata=f'<title>{escape(txt)}</title>'+(f'<desc>{escape(note)}</desc>' if note else '')
    if live:
        family='Six Caps' if face=='billing' else 'Oswald'
        unit=f.tt['head'].unitsPerEm
        # Keep matching absolute type scaling in source, with installed/bundled font.
        content=f'<text x="0" y="0" font-family="{family}" font-weight="{400 if face=="billing" else 300}" font-size="{unit}">{escape(txt)}</text>'
    else:content=paths
    inner=f'<g transform="matrix({sx:.8f} 0 0 {-sy:.8f} {tx:.4f} {ty:.4f})">{content}</g>' if not live else f'<g transform="matrix({sx:.8f} 0 0 {sy:.8f} {tx:.4f} {ty:.4f})">{content}</g>'
    optical_shear=f' transform="matrix(1 0 -.12 1 {.12*(y+h):.4f} 0)"' if italic else ''
    return f'<g id="{ident}" aria-label="{escape(txt)}"{optical_shear}>{metadata}{inner}</g>'

def path(ident,d,fill,**attrs):
    return f'<path id="{ident}" d="{d}" fill="{fill}" '+ ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())+'/>'

def polygon(ident,pts,fill,**attrs):
    return path(ident,'M '+' L '.join(f'{x},{y}' for x,y in pts)+' Z',fill,**attrs)

# 27 vertices; average counterpart geometry into a bilateral construction.
sunburst=[(500,544),(440,680),(420,684),(310,585),(310,728),(294,738),
      (155,682),(211,822),(200,840),(51,840),(151,948),(146,974),
      (30,1027),(30,1205),(970,1205),(970,1027),(854,974),(849,948),
      (949,840),(800,840),(789,822),(845,682),(706,738),(690,728),
      (690,585),(580,684),(560,680)]

def geometry():
    s=[f'<rect id="paper" width="1000" height="1450" fill="{COL["paper"]}"/>']
    # Full lower red field, then explicit white diagonal bands and yellow panel.
    s.append(polygon('red-lower-border',[(18,897),(982,897),(982,1221),(18,1221)],COL['red']))
    s.append(polygon('white-left-middle-ray',[(18,736),(130,840),(204,840),(204,897),(100,897),(18,897)],COL['paper']))
    s.append(polygon('white-right-middle-ray',[(982,736),(870,840),(796,840),(796,897),(900,897),(982,897)],COL['paper']))
    s.append(polygon('red-left-ray',[(18,598),(181,756),(211,822),(201,836),(128,836),(18,734)],COL['red']))
    s.append(polygon('red-right-ray',[(982,598),(819,756),(789,822),(799,836),(872,836),(982,734)],COL['red']))
    s.append(polygon('blue-left-field',[(18,0),(306.5,0),(306.5,727),(294,734),(155,682),(177,735),(18,587)],COL['blue']))
    s.append(polygon('blue-right-field',[(982,0),(693.5,0),(693.5,727),(706,734),(845,682),(823,735),(982,587)],COL['blue']))
    s.append(polygon('red-centre-field',[(430,0),(570,0),(570,682),(559,680),(500,544),(440,680),(430,682)],COL['red']))
    s.append(polygon('sunburst-panel',sunburst,COL['gold'],stroke=COL['paper'],stroke_width=7,stroke_linejoin='miter',stroke_miterlimit=5))
    return '\n'.join(s)

def include_svg(name,x,y,w,h,ident):
    p=ASSETS/name
    r=ET.fromstring(p.read_bytes());v=[float(z) for z in r.get('viewBox').split()]
    if name=='bc-pavilion-expo86-reconstructed.svg':
        for desc in r.xpath('./*[local-name()="desc"]'):
            desc.text='Reconstructed Pavilion badge: twelve native PofBC flag path geometries reused with poster colours; shared custom title letterforms; constructed frame and outlined caption typography. No embedded raster image.'
        for wordmark in r.xpath('//*[@id="bc-title-insert"]'):
            for child in list(wordmark):wordmark.remove(child)
            wordmark.append(ET.fromstring(('<svg xmlns="'+SVG+'">'+title_group('#163d8a')+'</svg>').encode())[0])
    content=''.join(ET.tostring(c,encoding='unicode') for c in r)
    # Prefix all identifiers to keep imported component namespace independent.
    ids=re.findall(r'\bid="([^"]+)"',content)
    for old in ids:
        new=ident+'-'+old
        content=content.replace(f'id="{old}"',f'id="{new}"').replace(f'url(#{old})',f'url(#{new})').replace(f'href="#{old}"',f'href="#{new}"')
    return f'<g id="{ident}" transform="translate({x} {y}) scale({w/v[2]} {h/v[3]}) translate({-v[0]} {-v[1]})">{content}</g>'

def credits(live=False):
    s=[]
    def txt(t,x,y,w,h,**kw):s.append(text_box(t,x,y,w,h,live=live,**kw))
    def dot(x,y):s.append(f'<circle cx="{x}" cy="{y}" r="1.8"/>')
    txt('THE BRITISH COLUMBIA PAVILION',77,1232,271,28,ident='presenter')
    txt('PRESENTS',350,1252,18,6,ident='presents')
    txt('OUR BRITISH COLUMBIA',372,1233,196,28,ident='film-title-credit')
    dot(578,1246)
    txt('WRITER/DIRECTOR',590,1223,37,6,ident='writer-director-role')
    txt('RICHARD JEFFERIES',590,1233,157,28,ident='richard-jefferies')
    dot(758,1246)
    txt('EDITOR',771,1223,16,6,ident='editor-role')
    txt('MARSHALL HARVEY',771,1233,160,28,ident='marshall-harvey')
    row2=[('DIRECTOR OF PHOTOGRAPHY','REED SMOOT',134,101,59),('CINEMATOGRAPHER','BRUCE INGRAM',261,125,39),('MUSIC','DAVID SPEAR',411,107,16),('WITH','THE NEW BC PHILHARMONIC ORCHESTRA',539,333,12)]
    for role,name,x,w,rw in row2:
        slug=name.lower().replace(' ','-');txt(role,x,1266,rw,6,ident=slug+'-role');txt(name,x,1275,w,28,ident=slug)
    for x in [248,399,528]:dot(x,1289)
    row3=[('PRODUCTION SUPERVISOR','GEORGE WIKTOR',154,132,58),('POST PRODUCTION SUPERVISOR','RICK GORDON',307,115,70),('ASSOCIATE PRODUCER','LYNNE CARROW',447,126,47),('PRODUCTION MANAGER','KAREN STEWART',597,128,49),('PRODUCER','BOB ROGERS',749,106,22)]
    for role,name,x,w,rw in row3:
        slug=name.lower().replace(' ','-');txt(role,x,1308,rw,6,ident=slug+'-role');txt(name,x,1317,w,28,ident=slug)
    for x in [296,434,585,738]:dot(x,1331)
    txt('For Lisa, Tyler and Jordy',462,1359,95,11,face='fine',ident='dedication',note='Jordy is the best visual reading; the final letters are partly shadowed.')
    lines=[
      ('Music Recorded at Little Mountain Sound, Vancouver · Processing by Alpha Cine Service, Vancouver · Equipment by W.F. White, Ltd., Vancouver · Video Post by Post Haste Video, Vancouver',151,1376,742,11,'processing-credit','Short connective phrase and repeated Vancouver ending reconstructed where the photograph is occluded.'),
      ('Sincere appreciation to the Motion Picture Studio Production Technicians I.A.T.S.E. 891, Vancouver, Canada, with special thanks to George Chapman; and to Dianne Neufeld and the staff of the B.C. Film Production Office',134,1396,760,11,'acknowledgements','Special thanks to and Office are editorial expansions beneath photographic holders; period terminology corroborates Office, but the printed word is not directly visible.'),
      ('Sound Track distributed by Front Row Productions, Box 4486, Vancouver, B.C. V6B 3Z8, Canada · Film, Poster and Sound Track distributed by International Media Distribution, Inc., 824 N. Victory Blvd., Burbank, CA 91502',122,1416,772,11,'distribution-credit','Track distributed and ZIP ending 02 are editorial expansions of text hidden by holders; 91502 matches the street address. Exact original ending remains unverified.')]
    for t,x,y,w,h,ident,note in lines:txt(t,x,y,w,h,face='fine',ident=ident,note=note,italic=ident in ['acknowledgements','distribution-credit'])
    txt('POSTER PRINTED IN BRITISH COLUMBIA BY MITCHELL PRESS.',450,1431,159,6,ident='printer-credit')
    txt('© 1986 International Media Distribution, Inc.',463,1441,133,4.7,face='fine',ident='copyright-credit')
    return '\n'.join(s)

def build(live=False):
    credit_records.clear()
    # Local title fit accounts for mild photographic perspective, preserving flat baselines.
    title=f'<g transform="translate(104 864) scale(.984 .981) translate(-190 -923)">{title_group(COL["black"])}</g>'
    our=f'<g transform="translate(381 759) scale(1.006 1.01) translate(-472 -820)">{our_group(COL["black"])}</g>'
    layer=lambda id,label,body:f'<g id="{id}" inkscape:groupmode="layer" inkscape:label="{label}">{body}</g>'
    s=['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="{SVG}" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1450" viewBox="0 0 1000 1450" role="img">',
       '<title>Our British Columbia — BC Pavilion Expo 86 film poster</title>',
       '<desc>Clean reconstruction from the supplied photographed poster. Native editable shapes; custom constructed title letterforms; open-font billing outlines; PofBC 12-path flag reused for the Pavilion badge. Working aspect ratio is approximate. Photography holders, curl, reflections and ageing are excluded. Some occluded fine-print words are editorial expansions documented on their individual groups and in the accompanying report.</desc>',
       '<metadata id="reconstruction-metadata">'+escape(json.dumps({'version':'1.0','date':'2026-11-21','method':'geometric reconstruction and authored Bezier lettering; no automatic raster trace','working_size':[1000,1450],'physical_dimensions':'unverified','palette':COL,'source_repository':'https://github.com/ahzs645/PofBC','reused_source':'src/assets/flagMark.js','source_commit':'bb468bc78bbc81d214477293934e0a8e3d4977d7'}))+'</metadata>',
       layer('geometry','01 — Sunburst and flag rays',geometry()),
       layer('hand-lettering','02 — Our / constructed pen strokes',our),
       layer('title-lettering','03 — British Columbia / custom letterforms',title),
       layer('billing','04 — Film credits'+(' / editable text' if live else ' / outlined'),' <g fill="'+COL['black']+'">'+credits(live)+'</g>'),
       layer('footer-logos','05 — Pavilion and production emblems',
          include_svg('industrial-showmanship-reconstructed.svg',35,1309,92,57.5,'industrial-showmanship')+
          include_svg('bob-rogers-company-reconstructed.svg',42,1381,68.5,50,'bob-rogers-company')+
          include_svg('bc-pavilion-expo86-reconstructed.svg',911,1331,74.5,113.24,'pavilion-badge')),
       '</svg>']
    return '\n'.join(s)

if __name__=='__main__':
    full=build(False)
    target=OUT/'Our_British_Columbia_1986.svg';target.write_text(full)
    work=ROOT/'source' if BUNDLED else ROOT/'work'
    if not BUNDLED:(work/'poster.svg').write_text(full)
    (OUT/'credit-transcription.json').write_text(json.dumps(credit_records,indent=2,ensure_ascii=False))
    (OUT/'Our_British_Columbia_1986_editable-text.svg').write_text(build(True))
    (work/'vector-landmarks.json').write_text(json.dumps({'yellow_boundary_white_stroke_centre':sunburst},indent=2))
    print(target)
