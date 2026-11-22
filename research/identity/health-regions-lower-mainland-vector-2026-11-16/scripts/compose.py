import sys,re,json; sys.path.insert(0,'.')
from sfcommon import *
def shift_d(d,dx,dy,s=1.0,ox=0,oy=0):
    toks=d.split()
    out=[];isx=True
    for t in toks:
        if re.fullmatch(r'[A-Za-z]',t): out.append(t); isx=True; continue
        v=float(t)
        if isx: v=(v-ox)*s+ox+dx
        else: v=(v-oy)*s+oy+dy
        out.append(f'{v:.4f}'.rstrip('0').rstrip('.')); isx=not isx
    return ' '.join(out)
def placed_paths(group, dx, dy, fill, s=1.0, ox=0, oy=0):
    out=[]
    for i in GROUPS[group]:
        raw=P[i]['raw']; d=shift_d(P[i]['d'],dx,dy,s,ox,oy)
        if 'fill="none"' in raw:
            sw=float(re.search(r'stroke-width="([^"]*)"',raw).group(1))
            out.append(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{sw:.3f}"/>')
        elif 'stroke=' in raw:
            sw=float(re.search(r'stroke-width="([^"]*)"',raw).group(1))
            lj=re.search(r'stroke-linejoin="([^"]*)"',raw).group(1)
            out.append(f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="{sw:.3f}" stroke-linejoin="{lj}"/>')
        else:
            out.append(f'<path d="{d}" fill="{fill}"/>')
    return out
def tight_bbox(body, approx, scale=20):
    x0,y0,x1,y1=approx
    W=x1-x0+4; H=y1-y0+4
    a=render(f'<g transform="translate({-x0+2} {-y0+2})">{body}</g>',W,H,scale)
    m=ink(a)>0.02
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
    return (x0-2+xs.min()/scale, y0-2+ys.min()/scale, x0-2+(xs.max()+1)/scale, y0-2+(ys.max()+1)/scale)
def svg_doc(body, vb, title, desc):
    x0,y0,x1,y1=vb
    w=x1-x0;h=y1-y0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}" width="{w:.2f}" height="{h:.2f}">\n'
            f'  <title>{title}</title>\n  <desc>{desc}</desc>\n'+body+'\n</svg>\n')
