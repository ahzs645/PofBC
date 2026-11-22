import sys,json; sys.path.insert(0,'.')
from fit import fit_groups
from fittext import *
from compose import *
FONT='../fonts2/Enriqueta-SemiBold.ttf'
img=np.array(Image.open('../sf/st98-native.png').convert('L')).astype(float)
T=np.clip((200-img)/140,0,1); H,W=T.shape
sym=fit_groups(T,{'symbol':(148,31,282,157)},blur=1.5)['symbol']
lines={}
for text,reg in (('South Fraser',(30,170,400,226)),('Health Region',(10,227,420,297))):
    r=fit_text(T,reg,FONT,text,blur=1.5); r.pop('body'); lines[text]=r
json.dump({'symbol':sym,'lines':lines},open('fit_st98.json','w'),indent=1)
S,stx,sty=sym
body=[]
for i in range(4):
    GROUPS['_p']=[i]; body+=placed_paths('_p',stx/S,sty/S,'#000')
for text,r in lines.items():
    k=r['s']/S
    d,_=text_d(FONT,text,100*k,r['tracking']*k,r['tx']/S,r['ty']/S)
    body.append(f'<path d="{d}" fill="#000"/>')
B='\n'.join('  '+x for x in body)
vb=tight_bbox(B,(0,0,W/S,H/S))
vb=(vb[0]-0.1,vb[1]-0.1,vb[2]+0.1,vb[3]+0.1)
title='South Fraser Health Region — stacked logo, 1998 (vector reconstruction)'
desc=('Reconstruction of the stacked symbol and name from the February 1998 Board Reference Manual. Symbol: the original 2001 vector outlines of the same emblem. '
      'Name: set in Enriqueta SemiBold (SIL OFL) and converted to outlines as a stand-in for the unverified original serif.')
open(sys.argv[1],'w').write(svg_doc(B,vb,title,desc)); print(S,vb)
