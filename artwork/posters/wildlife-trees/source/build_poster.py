"""Assemble layered poster, with live type and portable outlined-type edition.

All drawings remain independent editable vector groups. Text is manually
proofread against the supplied scan and fitted to measured line boxes. The
original faces are unverified; Nimbus Sans is a documented replacement.
"""
from pathlib import Path
import json, copy, re
from lxml import etree as E
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
INK='#326c59'
NS='http://www.w3.org/2000/svg'
INKSCAPE='http://www.inkscape.org/namespaces/inkscape'
XLINK='http://www.w3.org/1999/xlink'
HEIGHT=2997.159090909091
COPY=json.loads((ROOT/'source/poster-copy.json').read_text())

def node(tag,**attrs):
    return E.Element('{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def layer(parent,ident,label):
    g=node('g',id=ident)
    g.set('{'+INKSCAPE+'}groupmode','layer');g.set('{'+INKSCAPE+'}label',label)
    parent.append(g);return g

fonts={}
for style,f in [('regular','NimbusSans-Regular.otf'),('bold','NimbusSans-Bold.otf')]:
    path=Path('/usr/share/fonts/opentype/urw-base35')/f
    tt=TTFont(path);fonts[style]={'tt':tt,'glyphs':tt.getGlyphSet(),'cmap':tt.getBestCmap(),'hmtx':tt['hmtx'].metrics,'upem':tt['head'].unitsPerEm}

def glyph_info(char,style):
    f=fonts[style];name=f['cmap'].get(ord(char),f['cmap'][ord('?')]);g=f['glyphs'][name]
    pen=BoundsPen(f['glyphs']);g.draw(pen)
    p=SVGPathPen(f['glyphs']);g.draw(p)
    return f['hmtx'][name][0]/f['upem']*1000, tuple(v/f['upem']*1000 for v in pen.bounds) if pen.bounds else None,p.getCommands(),f['upem']

def prepare_text(row):
    seq=[];advance=0;bounds=[]
    for i,c in enumerate(row['text']):
        style='bold' if row.get('bold') or i<len(row.get('bold_prefix','')) else 'regular'
        a,b,d,u=glyph_info(c,style)
        seq.append((c,style,advance,a,b,d,u));advance+=a
        if b:bounds.append((seq[-1][2]+b[0],b[1],seq[-1][2]+b[2],b[3]))
    b=(min(v[0] for v in bounds),min(v[1] for v in bounds),max(v[2] for v in bounds),max(v[3] for v in bounds))
    return seq,b

def text_line(parent,defs,row,ident,outlined=False):
    x,y,w,h=row['box'];seq,b=prepare_text(row)
    sx=w/(b[2]-b[0]);sy=h/(b[3]-b[1])
    tx=x-b[0]*sx;ty=y+b[3]*sy
    g=node('g',id=ident,fill=row.get('fill',INK),aria_label=row['text'])
    title=node('title');title.text=row['text'];g.append(title)
    if outlined:
        g.set('transform',f'translate({tx:.6f} {ty:.6f}) scale({sx:.8f} {-sy:.8f})')
        for char,style,advance,a,gb,d,upem in seq:
            if not d:continue
            gid=f'glyph-{style}-{ord(char):04x}'
            if gid not in known:
                glyph=node('path',id=gid,d=d)
                if upem!=1000:glyph.set('transform',f'scale({1000/upem:.8f})')
                defs.append(glyph);known.add(gid)
            use=node('use',transform=f'translate({advance:.4f} 0)')
            use.set('{'+XLINK+'}href','#'+gid);g.append(use)
    else:
        # Each character has a measured x to ensure consistency with the outlined
        # edition; the whole line remains selectable/retypable SVG text.
        g.set('transform',f'translate({tx:.6f} {ty:.6f}) scale({sx:.8f} {sy:.8f})')
        t=node('text',font_family='Nimbus Sans, Arial, sans-serif',font_size=1000)
        for char,style,advance,a,gb,d,upem in seq:
            sp=node('tspan',x=f'{advance:.4f}',y=0,font_weight=700 if style=='bold' else 400)
            sp.text=char;t.append(sp)
        g.append(t)
    parent.append(g)

def import_svg(parent,name,ident,transform=None,restore_source_registration=False):
    original=E.parse(str(ASSETS/name)).getroot()
    if restore_source_registration:
        registration=original.xpath('//*[@id="source-registration"]')[0]
        registration.attrib.pop('transform',None)
    wrapper=node('g',id=ident)
    if transform:wrapper.set('transform',transform)
    idmap={n.get('id'):ident+'-'+n.get('id') for n in original.iter() if n.get('id')}
    for child in original:
        c=copy.deepcopy(child)
        for n in c.iter():
            for key,value in list(n.attrib.items()):
                if key=='id':n.set(key,idmap[value]);continue
                value=re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+idmap.get(m.group(1),m.group(1))+')',value)
                if value.startswith('#') and value[1:] in idmap:value='#'+idmap[value[1:]]
                n.set(key,value)
        wrapper.append(c)
    parent.append(wrapper)
    return wrapper

def fitted_logo(parent,name,x,y,w,h,ident):
    original=E.parse(str(ASSETS/name)).getroot();v=list(map(float,original.get('viewBox').split()))
    transform=f'translate({x} {y}) scale({w/v[2]:.10f} {h/v[3]:.10f}) translate({-v[0]} {-v[1]})'
    return import_svg(parent,name,ident,transform)

def build(outlined):
    global known
    known=set()
    registration=json.loads((ROOT/'source/source-registration.json').read_text())
    layout=json.loads((ROOT/'source/panel-layout.json').read_text())
    panels={x['key']:x for x in layout['panels']}
    r=E.Element('{'+NS+'}svg',nsmap={None:NS,'inkscape':INKSCAPE,'xlink':XLINK})
    r.attrib.update({'version':'1.1','viewBox':f'0 0 1000 {HEIGHT}','width':'290.576mm','height':'870.9025mm'})
    title=node('title');title.text='Wildlife Trees — rebuilt vector poster';r.append(title)
    desc=node('desc');desc.text='Full vector reconstruction of the supplied poster, using the corrected individually rebuilt animals, original tree and panel penwork reconstructed as editable Bezier paths, retyped lettering and existing PofBC identity vectors. Anatomical and tree-feature masks were measured manually; source-supported small feature repairs are documented. Original typeface remains unverified and is approximated by fitted Nimbus Sans.';r.append(desc)
    defs=node('defs');r.append(defs)
    g=layer(r,'paper','Paper');g.append(node('rect',width=1000,height=HEIGHT,fill='white'))
    g=layer(r,'habitat-tree','01 · Original habitat tree, nest, branches, fungi, roots and ground')
    import_svg(g,'wildlife-habitat-tree.svg','habitat')
    for index,reg in enumerate(registration['portraits']):
        key=reg['key'];slug=reg['slug'];panel=panels[key]
        g=layer(r,slug,f'{index+2:02d} · '+slug.replace('-',' ').title())
        bg=layer(g,key+'-background','Original panel background — removable')
        bg.append(node('path',d=panel['frame_path'],fill='white'))
        a=E.parse(str(ASSETS/(slug+'.svg'))).getroot();meta=json.loads(a.find('{'+NS+'}metadata').text)
        vw,vh=meta['source_viewBox'][2:];x0,y0,x1,y1=reg['poster_bbox']
        tr=f'translate({x0:.10f} {y0:.10f}) scale({(x1-x0)/vw:.12f} {(y1-y0)/vh:.12f})'
        import_svg(bg,slug+'-context.svg',key+'-context-art',tr)
        bg.append(node('path',d=panel['frame_path'],fill='none',stroke=INK,stroke_width=panel.get('frame_stroke_width',.65)))
        fg=layer(g,key+'-foreground','Corrected animal — independently editable')
        import_svg(fg,slug+'.svg',key+'-animal-art',tr,True)
    g=layer(r,'portrait-captions','08 · Portrait captions')
    for i,row in enumerate(COPY['captions']):
        x,y,w,h=layout['panels'][i]['caption_whiteplate_rect'];g.append(node('rect',x=x,y=y,width=w,height=h,fill='white'))
        text_line(g,defs,row,'caption-'+str(i),outlined)
    g=layer(r,'poster-heading','09 · Title and definition')
    tx,ty,tw,th=layout['title_background'];g.append(node('rect',x=tx,y=ty,width=tw,height=th,fill=INK))
    for i,row in enumerate(COPY['title']+COPY['intro']):text_line(g,defs,row,'heading-line-'+str(i),outlined)
    g=layer(r,'educational-copy','10 · Educational text')
    g.append(node('path',d=layout['divider_path'],stroke=INK,stroke_width=layout['divider_stroke_width'],fill='none'))
    for side in ['left-copy','right-copy']:
        sg=node('g',id=side);g.append(sg)
        for i,row in enumerate(COPY[side]):text_line(sg,defs,row,side+'-'+str(i),outlined)
    g=layer(r,'identity-marks','11 · PofBC ministry and Forest Service marks')
    for logo in layout['logo_placements']:
        x,y,w,h=logo['box'];fitted_logo(g,logo['file'],x,y,w,h,logo['key'])
    metadata=node('metadata');metadata.text=json.dumps({'source':'Wildlife Trees.pdf supplied by user','physical_mm':[290.576,870.9025],'native_source_pixels':registration['source_pixels'],'animal_registration':'Native crop origins and dimensions; tight SVG crops undone before placement. No bounding-box refit.','logo_source':'ahzs645/PofBC, revision 6d635f76208153909ad4a8322cd5167c15d28bbe','typeface':'Nimbus Sans fitted to source line boxes; original font unverified.'});r.append(metadata)
    name='Wildlife-Trees-outlined.svg' if outlined else 'Wildlife-Trees-editable.svg'
    out=ROOT/name;fresh=out.with_suffix('.svg.writing');fresh.write_bytes(E.tostring(r,encoding='UTF-8',xml_declaration=True));fresh.replace(out)
    print(name,'layers',len(r),'glyph definitions',len(defs),flush=True)

if __name__=='__main__':
    build(False)
    build(True)
