import sys,json; sys.path.insert(0,'.')
from fit import *
img=np.array(Image.open('/home/user/PofBC/public/identity-collected/south-fraser-health-region/south-fraser-health-region-stacked-1998.png').convert('L')).astype(float)
mask=np.clip((200-img)/140,0,1)
r=fit_groups(mask,{'symbol':(115,23,220,122)},blur=1.5)
json.dump(r,open('fit_s1998.json','w'),indent=1)
s,tx,ty=r['symbol']
H,W=img.shape
a=render(f'<g transform="matrix({s} 0 0 {s} {tx} {ty})">{group_svg(GROUPS["symbol"])}</g>',W,H,4)
v=ink(a); ri=1-np.array(Image.fromarray(img.astype('uint8')).resize((W*4,H*4),Image.LANCZOS)).astype(float)/255
o=np.ones((H*4,W*4,3))*255; o[...,0]-=v*255; o[...,2]-=v*255; o[...,1]-=ri*255
Image.fromarray(np.clip(o,0,255).astype('uint8')).crop((440,60,900,500)).save('ov-s1998-sym.png')
