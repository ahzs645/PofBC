import sys,json; sys.path.insert(0,'.')
from compose import *
r=json.load(open('fit_colour2001.json'))
S=float(np.median([r[g][0] for g in ['symbol','line1','line2','tag1','tag2']]))
# colours: dither-averaged from the 2001 raster under the fitted masks (see README)
COL={0:'#1D6A79',1:'#004D5F',2:'#68ACB2',3:'#006878'}
TEXT='#004A5A'
body=[];ab=[]
place={}
for g in ['symbol','line1','line2','rule','tag1','tag2']:
    s,tx,ty=r[g]
    bx0,by0,bx1,by1=bbox(GROUPS[g]); cx=(bx0+bx1)/2; cy=(by0+by1)/2
    # where the group's centre lands in the raster, expressed in source units at the common scale
    dx=(s*cx+tx)/S-cx; dy=(s*cy+ty)/S-cy
    place[g]=(dx,dy)
    if g=='symbol':
        for i in range(4):
            GROUPS['_p']=[i]
            body+=placed_paths('_p',dx,dy,COL[i])
    elif g=='rule':
        # keep the fitted rule length (scale about its own centre)
        body+=[re.sub(r'stroke-width="[^"]*"','stroke-width="0.42"',x) for x in placed_paths(g,dx,dy,TEXT,s=s/S,ox=cx,oy=cy)]  # rule weight measured from the raster (~2.9 px at 6.79 px/pt)
    else:
        body+=placed_paths(g,dx,dy,TEXT)
    ab.append((bx0+dx,by0+dy,bx1+dx,by1+dy))
approx=(min(a[0] for a in ab),min(a[1] for a in ab),max(a[2] for a in ab),max(a[3] for a in ab))
B='\n'.join('  '+x for x in body)
vb=tight_bbox(B,approx)
vb=(vb[0]-0.1,vb[1]-0.1,vb[2]+0.1,vb[3]+0.1)
title='South Fraser Health Region — horizontal colour logo with Healthy Individuals / Healthy Communities (vector reconstruction)'
desc=('Reconstruction of the July 2001 horizontal colour lockup. Symbol, lettering, rule and tagline are the original vector outlines '
      'from the April–May 2001 South Fraser Health Region newsletter (PDF page 1), repositioned unchanged to the horizontal arrangement of the 2001 raster. '
      'Colours are approximations averaged from that dithered raster.')
open(sys.argv[1],'w').write(svg_doc(B,vb,title,desc))
json.dump({'S':S,'place':place,'viewBox':vb},open('build_colour2001.json','w'),indent=1)
print(S,vb)
