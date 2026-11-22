"""Extract native vector paths from a PDF page region into a clean SVG.

python -I extract.py PDF PAGE X0 Y0 X1 Y1 [--out OUT.svg] [--skip i,j] [--list] [--title T] [--margin M]

Keeps every filled/stroked drawing whose bbox lies inside (or, with --intersect, intersects) the
clip rectangle, in the PDF's own colours and fill rule. No tracing, no recolouring.
Reports any text or images inside the rectangle (they are NOT converted).
"""
import sys, argparse, hashlib, pymupdf
ap=argparse.ArgumentParser()
ap.add_argument('pdf');ap.add_argument('page',type=int)
ap.add_argument('box',type=float,nargs=4)
ap.add_argument('--out');ap.add_argument('--skip',default='');ap.add_argument('--list',action='store_true')
ap.add_argument('--intersect',action='store_true');ap.add_argument('--title',default='')
ap.add_argument('--margin',type=float,default=0.5);ap.add_argument('--skipwhite',action='store_true')
ap.add_argument('--maxw',type=float,default=1e9)
a=ap.parse_args()
doc=pymupdf.open(a.pdf);page=doc[a.page-1];clip=pymupdf.Rect(*a.box)
hexof=lambda rgb:"#%02x%02x%02x"%tuple(round(v*255) for v in rgb)
num=lambda v:f"{v:.3f}".rstrip("0").rstrip(".")
def path_of(items, close):
    d,at=[],None
    for item in items:
        kind,*pts=item
        if kind=="re":
            r=pts[0];d.append(f"M{num(r.x0)} {num(r.y0)}H{num(r.x1)}V{num(r.y1)}H{num(r.x0)}Z");at=None;continue
        if kind=="qu":
            q=pts[0];d.append("M"+" L".join(f"{num(p.x)} {num(p.y)}" for p in (q.ul,q.ur,q.lr,q.ll))+"Z");at=None;continue
        s=pts[0]
        if at is None or abs(at.x-s.x)>1e-3 or abs(at.y-s.y)>1e-3:
            d.append(f"M{num(s.x)} {num(s.y)}")
        if kind=="l": d.append(f"L{num(pts[1].x)} {num(pts[1].y)}")
        elif kind=="c": d.append("C"+" ".join(f"{num(p.x)} {num(p.y)}" for p in pts[1:]))
        at=pts[-1]
    out="".join(d)
    if close: out=out.replace("M","ZM")[1:]+"Z" if out.startswith("M") else out
    return out
skip={int(x) for x in a.skip.split(',') if x}
dr=page.get_drawings()
txt=[b for b in page.get_text('dict',clip=clip)['blocks']]
imgs=[i for i in page.get_image_info() if pymupdf.Rect(i['bbox']).intersects(clip)]
if txt: print('WARNING text in box:',[ ''.join(s['text'] for l in b.get('lines',[]) for s in l['spans'])[:60] for b in txt])
if imgs: print('WARNING images in box:',[(i['bbox'],i['width'],i['height']) for i in imgs])
shapes=[];box=None;n=0
for i,d in enumerate(dr):
    r=d['rect']
    ok = r.intersects(clip) if a.intersect else (clip.contains(r) or (r.is_empty and clip.contains(r.tl)))
    if not ok or r.width>a.maxw: continue
    if a.list: print(i,d['type'],[round(v,1) for v in r],d.get('fill') and hexof(d['fill']),d.get('color') and hexof(d['color']),d.get('width'),d.get('even_odd'),d.get('fill_opacity'),len(d['items']))
    if i in skip: continue
    if a.skipwhite and d.get('fill') and min(d['fill'])>0.99 and d['type']=='f': continue
    attrs=[]
    t=d['type']
    if 'f' in t and d.get('fill') is not None:
        attrs.append(f'fill="{hexof(d["fill"])}"')
        if d.get('even_odd'): attrs.append('fill-rule="evenodd"')
        if d.get('fill_opacity') not in (None,1,1.0): attrs.append(f'fill-opacity="{num(d["fill_opacity"])}"')
    else: attrs.append('fill="none"')
    if 's' in t and d.get('color') is not None:
        attrs.append(f'stroke="{hexof(d["color"])}" stroke-width="{num(d.get("width") or 1)}"')
        lc=d.get('lineCap'); 
        if lc and max(lc)==1: attrs.append('stroke-linecap="round"')
        if lc and max(lc)==2: attrs.append('stroke-linecap="square"')
        lj=d.get('lineJoin')
        if lj==1: attrs.append('stroke-linejoin="round"')
        if lj==2: attrs.append('stroke-linejoin="bevel"')
    close=bool(d.get('closePath')) or 'f' in t
    shapes.append(f'<path d="{path_of(d["items"],close)}" {" ".join(attrs)}/>')
    w=(d.get('width') or 0)/2 if 's' in t else 0
    rr=pymupdf.Rect(r.x0-w,r.y0-w,r.x1+w,r.y1+w)
    box=rr if box is None else box|rr; n+=1
print('kept',n,'shapes; bbox',box)
if a.out and box:
    m=a.margin;vb=(box.x0-m,box.y0-m,box.width+2*m,box.height+2*m)
    title=f'<title>{a.title}</title>' if a.title else ''
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(num(v) for v in vb)}" width="{num(vb[2]*4)}" height="{num(vb[3]*4)}">{title}'+"".join(shapes)+"</svg>\n"
    open(a.out,'w').write(svg); print(a.out,len(svg),'bytes sha256',hashlib.sha256(svg.encode()).hexdigest())
