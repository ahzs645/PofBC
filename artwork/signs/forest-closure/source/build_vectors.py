"""Rebuild SVG artwork from geometric glyph masters and layout measurements.

No source photograph, raster silhouette or contour-tracing program is required.
Run with Python 3 + fonttools. Inkscape is optional for PNG/PDF exports.
"""
from pathlib import Path
import json,copy,base64,subprocess,sys
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT=Path(__file__).resolve().parent.parent
SVGNS='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',SVGNS)
GLYPHS=json.loads((ROOT/'source/glyph_masters.json').read_text())
EXPANDED=json.loads((ROOT/'source/expanded_glyph_masters.json').read_text())
LAYOUT=json.loads((ROOT/'source/layout.json').read_text())

def tag(name):return '{'+SVGNS+'}'+name
def elt(parent,name,attrs=None,text=None):
    x=ET.SubElement(parent,tag(name),{k:str(v) for k,v in (attrs or {}).items()})
    if text is not None:x.text=text
    return x

def numeric(x):return f'{x:.6f}'.rstrip('0').rstrip('.')
def matrix(a):return 'matrix('+','.join(numeric(a[i][j]) for i,j in [(0,0),(1,0),(0,1),(1,1),(0,2),(1,2)])+')'

def font_glyphs(path,chars):
    f=TTFont(path);gs=f.getGlyphSet();cmap=f.getBestCmap();out={}
    for c in sorted(set(chars)):
        name=cmap[ord(c)];p=BoundsPen(gs);gs[name].draw(p);x0,y0,x1,y1=p.bounds
        sp=SVGPathPen(gs);gs[name].draw(TransformPen(sp,(1,0,0,-1000/(y1-y0),-x0,y1*1000/(y1-y0))))
        out[c]={'path':sp.getCommands(),'width':x1-x0,'cap_height':1000}
    return out

def notice_masters():
    saved=ROOT/'source/notice_glyph_masters.json'
    if saved.exists():
        data=json.loads(saved.read_text())
        return data.get('glyphs',data)
    return font_glyphs(ROOT/'fonts/LeagueSpartan-750.ttf','WOODSCLET RAV')

def letter(parent,char,box,glyphs,live=False,prefix='main',unit_box_to_panel=None):
    x0,y0,x1,y1=box;g=glyphs[char];w=g['width'];sx=(x1-x0)/w;sy=(y1-y0)/1000
    transform=f'translate({numeric(x0)} {numeric(y0)}) scale({numeric(sx)} {numeric(sy)})'
    if unit_box_to_panel:
        a=copy.deepcopy(unit_box_to_panel)
        for row in range(3):
            a[row][0]/=w
            a[row][1]/=1000
        transform=matrix(a)
    group=elt(parent,'g',{'data-character':char,'data-width-scale-relative-to-cap-height':numeric(sx/sy),'transform':transform})
    if live and prefix in ['main','expanded']:
        family='Forest Closure 1960 Expanded Reconstruction' if prefix=='expanded' else 'Forest Closure 1960 Reconstruction'
        elt(group,'text',{'x':-45,'y':1000,'font-size':1400,'font-family':family,'font-weight':900},char)
    else:elt(group,'path',{'d':g['path'],'fill-rule':'evenodd'})

def new_svg(name,w,h,live=False):
    svg=ET.Element(tag('svg'),{'viewBox':f'0 0 {numeric(w)} {numeric(h)}','width':numeric(w),'height':numeric(h),
      'version':'1.1','role':'img','aria-labelledby':'artwork-title artwork-description'})
    elt(svg,'title',{'id':'artwork-title'},name)
    elt(svg,'desc',{'id':'artwork-description'},'Constructed vector recreation of BC Forest Service Protection Bulletin 1960 no. 3, page 4. Both status faces use one 1000 by 130 unit panel convention. Lettering uses reusable masters with independent width and height scaling; local shape variants improve photographic agreement but do not establish different historical fonts. Closed notice uses a modern League Spartan proxy with manually reconstructed variants. Exact historical typefaces, colours and physical dimensions are unverified. The small oval contains simplified interpretive detail. No raster images or autotraced contours are embedded.')
    if live:
        styles=[]
        for filename,family in [('ForestClosure1960-Reconstruction.otf','Forest Closure 1960 Reconstruction'),('ForestClosure1960-Expanded.otf','Forest Closure 1960 Expanded Reconstruction')]:
            font=base64.b64encode((ROOT/'fonts'/filename).read_bytes()).decode()
            styles.append("@font-face{font-family:'"+family+"';src:url(data:font/otf;base64,"+font+") format('opentype');font-weight:900}")
        elt(svg,'style',text=''.join(styles)+'text{font-kerning:none}')
    return svg

def main_elements(svg,live=False,board=True,emblem=True):
    if board:
        b=elt(svg,'g',{'id':'main-board','data-label':'White triangular board'})
        elt(b,'path',{'d':'M 500 0 L 1000 866.025404 L 0 866.025404 Z','fill':'#fff'})
    border=elt(svg,'g',{'id':'inner-rule','data-label':'Geometric inner triangular rule','fill':'none','stroke':'#111','stroke-width':LAYOUT['border_stroke'],'stroke-linejoin':'miter'})
    pts=LAYOUT['inner_triangle']
    elt(border,'path',{'d':'M '+' L '.join(f'{numeric(x)} {numeric(y)}' for x,y in pts)+' Z'})
    text=elt(svg,'g',{'id':'main-lettering','fill':'#111'})
    for word,data in LAYOUT['words'].items():
        group=elt(text,'g',{'id':'word-'+('zone-number' if word=='3' else word.lower()),'data-label':word,'aria-label':word,'transform':matrix(data['frame'])})
        for item in data['chars']:letter(group,item['character'],item['bbox'],GLYPHS,live)
    if emblem:
        x0,y0,x1,y1=LAYOUT['emblem']['box']
        g=elt(svg,'g',{'id':'forest-service-oval','data-label':'Interpretive historical oval','transform':f'translate({x0} {y0}) scale({(x1-x0)/400} {(y1-y0)/520})','color':'#111'})
        original=ET.parse(ROOT/'svg/forest-service-oval.svg').getroot()
        for child in original:
            if child.tag in [tag('g'),tag('defs')]:g.append(copy.deepcopy(child))

def panel_elements(svg,mode,y=0,live=False,board=True,shared_masters=False):
    data=LAYOUT['panel_'+mode];w,h=data['size']
    group=elt(svg,'g',{'id':mode+'-panel','data-label':mode.upper()+' changeable panel','transform':f'translate(0 {numeric(y)})'})
    if board:elt(group,'rect',{'width':w,'height':h,'rx':2,'fill':'#111' if mode=='closed' else '#fff'})
    g=elt(group,'g',{'id':mode+'-panel-lettering','aria-label':'OPEN' if mode=='open' else 'WOODS CLOSED TO TRAVEL','fill':'#fff' if mode=='closed' else '#111'})
    masters=GLYPHS if shared_masters else EXPANDED if mode=='open' else notice_masters()
    for item in data['chars']:letter(g,item['character'],item['bbox'],masters,live,prefix='main' if shared_masters else 'expanded' if mode=='open' else 'notice',unit_box_to_panel=item.get('unit_box_to_panel'))

def save(svg,name):
    path=ROOT/'svg'/name;ET.indent(svg,space='  ');ET.ElementTree(svg).write(path,encoding='utf-8',xml_declaration=True)
    return path

def build():
    mainh=LAYOUT['main_size'][1]
    assert LAYOUT['panel_open']['size']==LAYOUT['panel_closed']['size'], 'Both status faces share the same board geometry.'
    for live in [False,True]:
        suffix='-live-type' if live else ''
        for mode in ['open','closed','main']:
            h=mainh if mode=='main' else mainh+LAYOUT['panel_gap']+LAYOUT['panel_'+mode]['size'][1]
            svg=new_svg('Forest closure zone 3 boundary - '+mode.upper(),1000,h,live)
            main_elements(svg,live)
            if mode!='main':panel_elements(svg,mode,mainh+LAYOUT['panel_gap'],live)
            save(svg,'forest-closure-'+mode+suffix+'.svg')
    for mode in ['open','closed']:
        w,h=LAYOUT['panel_'+mode]['size'];svg=new_svg(mode.upper()+' notice panel',w,h)
        panel_elements(svg,mode);save(svg,'panel-'+mode+'.svg')
        svg=new_svg('Forest closure '+mode.upper()+' - same alphabet, scaled widths',1000,mainh+LAYOUT['panel_gap']+h)
        svg.find(tag('desc')).text='Shared-alphabet alternative: all large lettering uses the same 19-glyph reconstructed master set, with independent width/height scaling and measured placement. OPEN and CLOSED share a 1000 by 130 panel convention. The subset is an original reconstruction, not an identified historical font. The small oval remains interpretive outlined artwork. No raster images or autotracing are used.'
        main_elements(svg)
        panel_elements(svg,mode,mainh+LAYOUT['panel_gap'],shared_masters=True)
        save(svg,'forest-closure-'+mode+'-shared-masters.svg')
    # Separate transparent ink plate for unambiguous raster QA, no seal in score.
    svg=new_svg('Main geometric lettering and border, no paper or oval',1000,867)
    main_elements(svg,board=False,emblem=False);save(svg,'main-ink-analysis.svg')
    for mode in ['open','closed']:
        w,h=LAYOUT['panel_'+mode]['size'];svg=new_svg('Panel lettering QA '+mode,w,h)
        panel_elements(svg,mode,board=False);save(svg,mode+'-ink-analysis.svg')
    print('Built SVG artwork from shared glyph paths and measured layout.')

if __name__=='__main__':build()
