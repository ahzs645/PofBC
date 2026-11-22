"""Extract the native vector paths of a logo from one PDF page into a clean SVG.
Keeps each path's own geometry and fill/stroke colour (as MuPDF reports it); applies only the page's
/Rotate so the SVG reads upright. Usage:
  python -I extract_pdf_vector.py SRC.pdf PAGE(1-based) x0,y0,x1,y1(display pts) OUT.svg "title" "desc" [--exclude i,j]"""
import sys, pymupdf
src,pg,clip,out,title,desc=sys.argv[1:7]
excl=set()
if '--exclude' in sys.argv: excl=set(int(v) for v in sys.argv[sys.argv.index('--exclude')+1].split(','))
doc=pymupdf.open(src); page=doc[int(pg)-1]
C=pymupdf.Rect(*map(float,clip.split(',')))
M=page.rotation_matrix
num=lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
hexof=lambda c: "#%02X%02X%02X"%tuple(round(v*255) for v in c)
def P(p): q=pymupdf.Point(p)*M; return f"{num(q.x)} {num(q.y)}"
def path_of(items, close):
    d=[];at=None
    for it in items:
        k,*pts=it
        if k=='re':
            r=pts[0]; d.append("M"+" L".join(P(x) for x in (r.tl,r.tr,r.br,r.bl))+" Z"); at=None; continue
        if k=='qu':
            q=pts[0]; d.append("M"+" L".join(P(x) for x in (q.ul,q.ur,q.lr,q.ll))+" Z"); at=None; continue
        st=pts[0]
        if at is None or abs(at.x-st.x)>1e-3 or abs(at.y-st.y)>1e-3:
            if d and close: d.append("Z")
            d.append("M"+P(st))
        if k=='l': d.append("L"+P(pts[1]))
        elif k=='c': d.append("C"+" ".join(P(x) for x in pts[1:]))
        at=pts[-1]
    if close: d.append("Z")
    return " ".join(d)
els=[];used=[];bb=None
for i,dr in enumerate(page.get_drawings()):
    r=dr['rect']*M
    if not C.contains(r) or i in excl: continue
    fill=dr.get('fill'); col=dr.get('color'); t=dr['type']
    a=[]
    if fill is not None and 'f' in t: a.append(f'fill="{hexof(fill)}"' + (' fill-rule="evenodd"' if dr.get('even_odd') else ''))
    else: a.append('fill="none"')
    if col is not None and 's' in t:
        a.append(f'stroke="{hexof(col)}" stroke-width="{num(dr.get("width") or 1)}"')
        if dr.get('lineJoin') not in (None,0): a.append(f'stroke-linejoin="{["miter","round","bevel"][int(dr["lineJoin"])]}"')
    els.append(f'  <path d="{path_of(dr["items"], dr.get("closePath",True) or "f" in t)}" {" ".join(a)}/>')
    used.append(i)
    w=(dr.get('width') or 0)/2 if 's' in t else 0
    rr=pymupdf.Rect(r.x0-w,r.y0-w,r.x1+w,r.y1+w); bb=rr if bb is None else bb|rr
x0,y0=bb.x0,bb.y0; w,h=bb.width,bb.height
svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x0)} {num(y0)} {num(w)} {num(h)}" width="{num(w)}" height="{num(h)}">\n'
     f'  <title>{title}</title>\n  <desc>{desc}</desc>\n'+"\n".join(els)+"\n</svg>\n")
open(out,'w').write(svg)
print('paths',len(used),'indices',used[0],'-',used[-1],'bbox',bb)
