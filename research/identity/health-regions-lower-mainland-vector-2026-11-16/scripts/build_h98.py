import sys,json; sys.path.insert(0,'.')
from compose import *
from textpath import text_d
FONT='../fonts/Yesteryear-Regular.ttf'
g=json.load(open('fit_h1998.json')); tag=json.load(open('fit_h98tag.json'))
S=g['symbol'][0]   # output unit = 1 source-PDF unit of the symbol
body=[]
# ground panel measured from the scan (50% edges)
bx0,by0,bx1,by1=11.6/S,22.4/S,1227.9/S,320.2/S
body.append(f'<path d="M {bx0:.3f} {by0:.3f} L {bx1:.3f} {by0:.3f} L {bx1:.3f} {by1:.3f} L {bx0:.3f} {by1:.3f} Z" fill="#000"/>')
for grp in ['symbol','line1','line2']:
    s,tx,ty=g[grp]; k=s/S
    if grp=='symbol':
        for i in range(4):
            GROUPS['_p']=[i]; body+=placed_paths('_p',tx/S,ty/S,'#FFF')
    else:
        body+=placed_paths(grp,tx/S,ty/S,'#FFF',s=k,ox=0,oy=0)
for w,r in tag.items():
    k=r['s']/S
    d,_=text_d(FONT,w,100*k,r['tracking']*k,r['tx']/S,r['ty']/S)
    body.append(f'<path d="{d}" fill="#000"/>')
B='\n'.join('  '+x for x in body)
vb=tight_bbox(B,(0,0,1248/S,452/S))
vb=(vb[0]-0.1,vb[1]-0.1,vb[2]+0.1,vb[3]+0.1)
title='South Fraser Health Region — reversed horizontal logo with Working together for a healthy future, 1998 (vector reconstruction)'
desc=('Reconstruction of the September 1998 reversed horizontal lockup. Symbol and name: the original 2001 vector outlines of the same artwork, reversed out of a black panel measured from the scan. '
      'Tagline: set in Yesteryear (SIL OFL) and converted to outlines as a stand-in for the unidentified original script.')
open(sys.argv[1],'w').write(svg_doc(B,vb,title,desc)); print(S,vb)
