import sys,json; sys.path.insert(0,'.')
from fittext import *
from compose import tight_bbox, svg_doc
from cg_strokes import strokes, smooth_bezier
SRC='../sf/cg/embedded.png'
FONT='../fonts3/inst-Gelasio-Italic-w700.ttf'
TEAL='#00948C'; BAR='#A2C4C4'
CX,CY,R=146.29,123.25,120.5
BARS=[125.1,146.23,167.43,186.43,209.71,230.84]; BH=6.4; BX0,BX1=7.6,282.5
img=np.array(Image.open(SRC).convert('L')).astype(float)
T=np.clip((200-img)/150,0,1); T[:,:285]=0
lines={}
for text,reg in [('Coast',(290,10,765,85)),('Garibaldi',(290,85,765,165)),('Health',(290,165,765,246))]:
    r=fit_text(T,reg,FONT,text,blur=1.5); r.pop('body'); lines[text]=r
runs,sw=strokes(SRC,CX,CY,R)
f=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
body=[]
body.append(f'<path d="M {f(CX-R)} {f(CY)} A {f(R)} {f(R)} 0 1 1 {f(CX+R)} {f(CY)} A {f(R)} {f(R)} 0 1 1 {f(CX-R)} {f(CY)} Z" fill="{TEAL}"/>')
body.append(f'<clipPath id="cg-disc"><path d="M {f(CX-R)} {f(CY)} A {f(R)} {f(R)} 0 1 1 {f(CX+R)} {f(CY)} A {f(R)} {f(R)} 0 1 1 {f(CX-R)} {f(CY)} Z"/></clipPath>')
ext={'left_ridge':(8,6),'upper_ridge':(0,8),'sun':(0,0),'right_ridge':(8,6)}
g=[]
for k,P in runs.items():
    g.append(f'<path d="{smooth_bezier(P,10,*ext[k])}"/>')
body.append(f'<g clip-path="url(#cg-disc)" fill="none" stroke="#FFFFFF" stroke-width="{sw:.2f}" stroke-linecap="round" stroke-linejoin="round">'+''.join(g)+'</g>')
for y in BARS:
    body.append(f'<path d="M {f(BX0)} {f(y-BH/2)} L {f(BX1)} {f(y-BH/2)} L {f(BX1)} {f(y+BH/2)} L {f(BX0)} {f(y+BH/2)} Z" fill="{BAR}"/>')
for text,r in lines.items():
    d,_=text_d(FONT,text,100*r['s'],r['tracking']*r['s'],r['tx'],r['ty'])
    body.append(f'<path d="{d}" fill="{TEAL}"/>')
B='\n'.join('  '+x for x in body)
vb=tight_bbox(B,(0,0,765,246),scale=4)
vb=(vb[0]-0.5,vb[1]-0.5,vb[2]+0.5,vb[3]+0.5)
title='Coast Garibaldi Health — symbol and wordmark (vector reconstruction)'
desc=('Reconstruction of the Coast Garibaldi Community Health Services Society logo. Disc, bars and ridge/sun lines are geometry fitted to the 765 x 246 px bitmap in the June 2000 Word header '
      'preserved on cghealth.org; the name is set in Gelasio Bold Italic (SIL OFL) and converted to outlines as a stand-in for the unverified original typeface. Colours approximated from the 2001 website GIF.')
open(sys.argv[1],'w').write(svg_doc(B,vb,title,desc))
json.dump({'lines':lines,'stroke_width':sw,'disc':[CX,CY,R],'bars':BARS},open('fit_cg.json','w'),indent=1,default=float)
print(vb,sw)
