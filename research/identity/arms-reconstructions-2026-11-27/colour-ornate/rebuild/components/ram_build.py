from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vector_utils import *
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'tmp'/'ram').mkdir(parents=True,exist_ok=True)
A=source_array(); rgb=A[:,:,:3].astype(float); alpha=A[:,:,3]
# Isolate the supporter at the contacts with the shield and folded ribbon.
roi=polygon_mask([(950,340),(1240,340),(1240,1045),(1186,1053),(1167,1068),(1162,1087),(1146,1096),(1100,1097),(1098,1080),(1112,1057),(1127,1046),(1138,1025),(1113,1001),(1012,984),(950,1015),(935,1034),(906,1040),(890,1032),(890,1005),(940,965),(957,900),(950,865),(951,850),(977,851),(980,801),(941,770),(932,782),(949,794),(953,805),(972,811),(978,832),(974,850),(954,850),(935,835),(922,821),(905,815),(896,790),(884,760),(877,743),(876,737),(881,728),(892,719),(910,708),(928,694),(941,678),(940,655),(926,642),(914,628),(905,614),(905,574),(925,585),(943,599),(955,603),(951,550)])
base=(alpha>100)&roi
base=clean_mask(base,sigma=.7,min_size=90,hole_size=30)
# Reconstruct the two hooves across the paper ribbon.  At these contacts alpha
# alone cannot separate the painted animal from the ribbon underneath it.
Y,X=np.indices((H,W))
rgbmed=ndi.median_filter(rgb,size=(3,3,1))
dark=(rgbmed.max(axis=2)<110)&((rgbmed.max(axis=2)-rgbmed.min(axis=2))<70)&(alpha>100)
rightfoot=dark&(X>=1095)&(X<1190)&(Y>=1020)&(Y<1100)
rightfoot[1020,1152:1179]=True
rightfoot=ndi.binary_closing(rightfoot,iterations=1)
rightfoot=ndi.binary_fill_holes(rightfoot)
rightfoot=clean_mask(rightfoot,sigma=.6,min_size=60,hole_size=20)
leftfoot=clean_mask(dark&(X>890)&(X<957)&(Y>=1015)&(Y<1043),sigma=.6,min_size=60,hole_size=20)
base[(Y>=1020)&(X>1080)]=False
base|=rightfoot
base[(Y>=1015)&(X<980)]=False
base|=leftfoot
# Smooth colour at the scale of the printed dots before fitting the curves.
lightval=(rgb[:,:,0]*.32+rgb[:,:,1]*.42+rgb[:,:,2]*.26)
lightval=ndi.gaussian_filter(lightval,.9)
light=(lightval>130)&base
light=clean_mask(light,sigma=.55,min_size=20,hole_size=27)
# Avoid crossing the silhouette or turning transparent pixels into paint.
light &= base
lab,n=ndi.label(light)
sizes=np.bincount(lab.ravel()); order=np.argsort(sizes[1:])[::-1]+1
parts=[]
for i,number in enumerate(order):
    cm=lab==number
    if sizes[number]<20: continue
    yy,xx=np.where(cm)
    if sizes[number]<100 and xx.mean()<911 and 699<yy.mean()<735: continue
    parts.append('<g id="ram-ivory-region-%02d">'%i+mask_path(cm,PALETTE['ivory'],turdsize=15,opttolerance=.34)+'</g>')
body='<g id="ram-supporter" aria-label="Ram supporter"><g id="ram-black-silhouette">'+mask_path(base,PALETTE['ink'],turdsize=25,opttolerance=.42)+ '</g><g id="ram-ivory-drawing">'+''.join(parts)+'</g></g>'
save_svg(ROOT/'components/ram.svg',body)
# QA plate is temporary only.
im=Image.new('RGBA',(W,H),'white')
Image.fromarray(np.uint8(base)*255).save(ROOT/'tmp/ram/silhouette.png')
print('Wrote',ROOT/'components/ram.svg', 'pixels',base.sum(),light.sum())
