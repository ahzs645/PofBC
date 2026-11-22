import sys,pymupdf
from PIL import Image
# pages.py out.png file:page[,page] ...  -> contact sheet at small scale
out=sys.argv[1]; ims=[]
for spec in sys.argv[2:]:
    f,ps=spec.rsplit(':',1); d=pymupdf.open(f)
    for p in ps.split(','):
        pix=d[int(p)-1].get_pixmap(dpi=50); im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples); ims.append(im)
W=sum(i.width for i in ims)+5*len(ims); H=max(i.height for i in ims)
s=Image.new('RGB',(W,H),'gray'); x=0
for i in ims: s.paste(i,(x,0)); x+=i.width+5
s.save(out)
