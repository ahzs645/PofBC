import sys,json; sys.path.insert(0,'.')
from fittext import *
FONT='../fonts/Yesteryear-Regular.ttf'
img=np.array(Image.open('/home/user/PofBC/public/identity-collected/south-fraser-health-region/south-fraser-health-region-horizontal-1998.png').convert('L')).astype(float)
T=np.clip((200-img)/140,0,1); T[:323,:]=0; H,W=T.shape
Tb=blurred(T,2.0)
words=[('Working',16,282),('together',303,568),('for',578,686),('a',702,734),('healthy',753,1006),('future',1016,1218)]
S=0.925; TY=403.5
out={}
for w,x0,x1 in words:
    d0,wid=text_d(FONT,w,100)
    a=render(f'<g transform="translate(10 120)"><path d="{d0}"/></g>',int(wid+40),200)
    gx0,_,gx1,_=bbox_of_mask(ink(a)>0.5)
    tr0=((x1-x0)/S-(gx1-gx0))/max(1,len(w)-1)
    tx0=x0-(gx0-10)*S
    cx0,cx1=max(0,x0-6),min(W,x1+6)
    def body(p):
        tx,tr,ty=p; d,_=text_d(FONT,w,100,tr); return f'<g transform="matrix({S} 0 0 {S} {tx} {ty})"><path d="{d}"/></g>'
    def loss(p):
        R=blurred(ink(render(body(p),W,H)),2.0); return ((R[323:,cx0:cx1]-Tb[323:,cx0:cx1])**2).sum()
    r=minimize(loss,[tx0,tr0,TY],method='Nelder-Mead',options={'maxiter':300,'initial_simplex':[[tx0,tr0,TY],[tx0+3,tr0,TY],[tx0,tr0+1.5,TY],[tx0,tr0,TY+3]]})
    out[w]={'s':S,'tx':r.x[0],'tracking':r.x[1],'ty':r.x[2],'loss':float(r.fun)}
    print(w,[round(v,2) for v in r.x],round(r.fun),flush=True)
json.dump(out,open('fit_h98tag.json','w'),indent=1)
