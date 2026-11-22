import sys,re,json; sys.path.insert(0,'.')
from sfcommon import *
def svg_body(path):
    s=open(path).read()
    return s[s.find('</desc>')+7:s.rfind('</svg>')]
def overlay(raster_path, svg_path, S, ox, oy, out, invert=False, up=2, label=''):
    rimg=Image.open(raster_path).convert('RGB'); W,H=rimg.size
    body=svg_body(svg_path)
    a=render(f'<g transform="matrix({S} 0 0 {S} {ox} {oy})">{body}</g>',W,H,up)
    vec=Image.fromarray(a).convert('RGB')
    r=np.array(rimg.resize((W*up,H*up),Image.LANCZOS).convert('L')).astype(float)
    v=np.array(vec.convert('L')).astype(float)
    ri=1-r/255; vi=1-v/255
    if invert: ri=r/255  # reversed raster: light = ink
    # overlay: raster ink in magenta, vector ink in green; agreement dark grey
    o=np.ones((H*up,W*up,3))*255
    o[...,0]-=vi*255; o[...,2]-=vi*255   # vector -> green
    o[...,1]-=ri*255                      # raster -> magenta
    o=np.clip(o,0,255).astype('uint8')
    side=Image.new('RGB',(W*up,H*up*3+20),'white')
    side.paste(rimg.resize((W*up,H*up),Image.LANCZOS),(0,0)); side.paste(vec,(0,H*up+10)); side.paste(Image.fromarray(o),(0,2*H*up+20))
    side.save(out,quality=82)
    iou=((ri>0.5)&(vi>0.5)).sum()/max(1,((ri>0.5)|(vi>0.5)).sum())
    return iou
if __name__=='__main__':
    print(overlay(sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),sys.argv[6],len(sys.argv)>7 and sys.argv[7]=='inv'))
