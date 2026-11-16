import re, numpy as np, pymupdf
from PIL import Image
SRC='/home/user/PofBC/public/identity-collected/south-fraser-health-region/south-fraser-health-region-stacked-tagline-2001.svg'
def load_paths():
    s=open(SRC).read()
    out=[]
    for p in re.findall(r'<path ([^>]*)/>',s):
        d=re.search(r'\bd="([^"]*)"',p).group(1)
        out.append({'d':d,'raw':p})
    return out
P=load_paths()
GROUPS={'symbol':list(range(0,4)),'line1':list(range(4,15)),'line2':list(range(15,27)),
        'tag1':list(range(27,45)),'tag2':list(range(45,63)),'rule':[63]}
def bbox(idx):
    xs=[];ys=[]
    for i in idx:
        nums=list(map(float,re.findall(r'-?[\d.]+',P[i]['d']))); xs+=nums[0::2]; ys+=nums[1::2]
    return min(xs),min(ys),max(xs),max(ys)
def group_svg(idx, fill='#000', keep_stroke=True):
    parts=[]
    for i in idx:
        raw=P[i]['raw']
        if 'fill="none"' in raw:
            sw=re.search(r'stroke-width="([^"]*)"',raw).group(1)
            parts.append(f'<path d="{P[i]["d"]}" fill="none" stroke="{fill}" stroke-width="{sw}"/>')
        elif 'stroke=' in raw and keep_stroke:
            sw=re.search(r'stroke-width="([^"]*)"',raw).group(1)
            lj=re.search(r'stroke-linejoin="([^"]*)"',raw)
            lj=f' stroke-linejoin="{lj.group(1)}"' if lj else ''
            parts.append(f'<path d="{P[i]["d"]}" fill="{fill}" stroke="{fill}" stroke-width="{sw}"{lj}/>')
        else:
            parts.append(f'<path d="{P[i]["d"]}" fill="{fill}"/>')
    return '\n'.join(parts)
def render(svg_body, W, H, scale=1):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>{svg_body}</svg>'
    doc=pymupdf.open(stream=svg.encode(),filetype='svg')
    pix=doc[0].get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False)
    a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.h,pix.w,pix.n)[:,:,:3]
    return a
def ink(a): return 1-a.astype(float).mean(2)/255
