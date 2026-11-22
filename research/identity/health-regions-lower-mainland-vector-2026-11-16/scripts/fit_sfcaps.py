import sys,json; sys.path.insert(0,'.')
from fitcaps import *
img=np.array(Image.open('/home/user/PofBC/public/identity-collected/simon-fraser-health-region/simon-fraser-health-region-continuum-2001-monochrome.png').convert('L')).astype(float)
T=np.clip((200-img)/140,0,1); T[:, :1000]=0; T[800:,:]=0; H,W=T.shape
Tb=blurred(T,2.0)
boxes={'SIMON':(1034,262,1862,387),'FRASER':(1043,436,1879,561),'HEALTH':(1043,610,1864,734)}
font=sys.argv[1]
base={t:fit_caps(T,b,font,t,refine=False) for t,b in boxes.items()}
def line(t,sx):
    b=boxes[t]; r=base[t]; s=r['s']
    d,w=text_d(font,t,100)
    # natural width with horizontal scale sx: glyph bbox from base fit (tracking 0)
    a=render(f'<g transform="translate(20 150)"><path d="{d}"/></g>',int(w+60),200,4)
    gx0,_,gx1,_=[v/4 for v in bbox_of_mask(ink(a)>0.5)]; gx0-=20; gx1-=20
    tr=((b[2]-b[0])/(s*sx)-(gx1-gx0))/(len(t)-1)
    tx=b[0]-gx0*s*sx
    dd,_=text_d(font,t,100,tr)
    return f'<g transform="matrix({s*sx} 0 0 {s} {tx} {r["ty"]})"><path d="{dd}"/></g>', dict(s=s,sx=sx,tracking=tr,tx=tx,ty=r['ty'])
def loss(sx):
    body=''.join(line(t,sx)[0] for t in boxes)
    R=blurred(ink(render(body,W,H)),2.0); return ((R[240:760,1000:]-Tb[240:760,1000:])**2).sum()
best=None
for sx in np.arange(1.0,1.42,0.03):
    l=loss(sx); print(round(sx,3),round(l)); best=(l,sx) if best is None or l<best[0] else best
sx=best[1]
for sx2 in np.arange(sx-0.025,sx+0.026,0.01):
    l=loss(sx2); best=(l,sx2) if l<best[0] else best
print('best',best)
out={t:line(t,best[1])[1] for t in boxes}
json.dump(out,open(sys.argv[2],'w'),indent=1,default=float)
body=''.join(line(t,best[1])[0] for t in boxes)
v=ink(render(body,W,H)); o=np.ones((H,W,3))*255; o[...,0]-=v*255; o[...,2]-=v*255; o[...,1]-=T*255
Image.fromarray(np.clip(o,0,255).astype('uint8')).crop((1000,240,1943,760)).save(sys.argv[2]+'.png')
