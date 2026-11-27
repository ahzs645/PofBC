from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vector_utils import trace_mask, save_svg, polygon_mask, clean_mask
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp/stag/revision'; TMP.mkdir(exist_ok=True,parents=True)
src=Image.open(ROOT/'upload/Ornate historical coat of arms.png').convert('RGBA'); arr=np.asarray(src).astype(float)
alpha=arr[:,:,3]/255
rgb=arr[:,:,:3]
# A hand-drawn component matte follows the exposed animal and excludes the neighboring shield and scroll.
poly=[(0,270),(315,270),(320,424),(385,457),(401,535),(414,563),(440,559),(439,671),(458,677),(470,684),(477,697),(474,708),(470,717),(467,723),(463,731),(458,740),(452,750),(448,759),(443,766),(440,772),(436,778),(430,785),(421,796),(407,805),(394,812),(364,837),(365,883),(334,918),(367,939),(406,959),(439,992),(447,1033),(421,1034),(399,1027),(388,999),(363,993),(321,972),(272,952),(256,924),(263,868),(249,863),(225,922),(192,946),(157,980),(158,1022),(184,1065),(221,1102),(217,1116),(184,1115),(159,1096),(137,1079),(126,1045),(124,1006),(109,978),(115,949),(145,921),(161,896),(140,875),(105,884),(98,864),(104,828),(139,760),(207,674),(226,638),(217,589),(202,541),(189,496),(183,474),(166,458),(159,443),(116,429),(0,381)]
m=Image.new('L',src.size,0); ImageDraw.Draw(m).polygon(poly,fill=255); region=np.asarray(m)>0
# Keep the main connected ink silhouette while suppressing transparent raster fringe.
sil=ndi.gaussian_filter(alpha,0.75)>.5
sil &=region
lab,n=ndi.label(sil); sizes=np.bincount(lab.ravel()); keep=sizes>45; keep[0]=False; sil=keep[lab]
# Close tiny print pinholes, keeping the designed antler and leg openings.
inv,n=ndi.label(~sil); sz=np.bincount(inv.ravel()); holes=(sz<18); holes[0]=False;sil|=holes[inv]
# Average the orange printer's screen without retaining a stippled vector texture.
coverage=ndi.gaussian_filter(alpha,1.05)
lum=rgb@np.array([.299,.587,.114])
sm=ndi.gaussian_filter(lum*alpha,1.05)/np.maximum(coverage,1e-9)
smred=ndi.gaussian_filter(rgb[:,:,0]*alpha,1.05)/np.maximum(coverage,1e-9)
light=(sm>127)&sil
lab,n=ndi.label(light); sizes=np.bincount(lab.ravel()); keep=sizes>7; keep[0]=False; light=keep[lab]
inv,n=ndi.label(~light); sz=np.bincount(inv.ravel()); holes=(sz<20);holes[0]=False;light|=holes[inv]&sil
# Cut the small section resting on the scroll at its drawn ink boundary, excluding the paper behind it.
for x0,y0,x1,y1 in [(125,1040,225,1118),(386,979,447,1035)]:
    dark=((sm<110)&(smred<135)&(coverage>.35)&region)[y0:y1,x0:x1]
    # The top edge closes the leg, whose cream center enters the window from above.
    inds=np.where(dark[0])[0]
    if len(inds): dark[0,inds.min():inds.max()+1]=True
    dark=ndi.binary_fill_holes(dark)
    lab,n=ndi.label(dark);sz=np.bincount(lab.ravel());sz[0]=0
    dark=lab==np.argmax(sz)
    sil[y0:y1,x0:x1]=dark
    light[y0:y1,x0:x1]&=dark
# Rebuild the extreme rear hoof tip where the black ink met the coloured ribbon.
rear_clip=polygon_mask([(380,970),(413,977),(435,1002),(443,1018),(442,1027),(437,1031),(428,1028),(409,1021),(394,1010),(384,991)])
roi=np.zeros_like(sil);roi[1020:1040,400:450]=True
sil[roi]&=rear_clip[roi];light[roi]&=sil[roi]
# Exclude the narrow neighboring shield-border fragment in the open gap below the raised foreleg.
sil[632:673,433:441]=False
light[632:673,433:441]=False
# Keep a continuous ink edge wherever the source crossed a neighboring element.
light &= ndi.distance_transform_edt(sil)>1.25
# Antler revision: use a local de-screening cutoff that preserves thin ivory
# runs. The general animal-body cutoff made narrow branches appear too heavy.
antler_region=polygon_mask([(0,275),(315,275),(315,423),(275,426),(259,430),
                            (251,436),(228,435),(208,431),(184,428),(155,422),
                            (115,413),(77,399),(37,378),(0,368)])
antler_ivory=(sm>108)&sil
antler_ivory=clean_mask(antler_ivory,sigma=.42,min_size=4,hole_size=12)
antler_ivory &= ndi.distance_transform_edt(sil)>1.6
light[antler_region]=antler_ivory[antler_region]
# Preserve the large negative spaces, all original tines, and the observed
# two-antler crossing. A local explicit curve refines the thinnest upper twig.
# Shape the leftward upper twig as a tapered run rather than a blunt enclosed
# oval. The narrow pink/ivory neck is visible in the supplied screened source.
horizontal_twig_region=polygon_mask([(75,311),(105,313),(119,317),(120,325),(76,323)])
light[horizontal_twig_region]=False
antler_bridges={
'rear-horizontal-tine-interior':"""M80.2,315.7 C85.1,313.9 95.4,316.0 104.3,318.0
 C109.8,319.2 114.7,320.3 119.0,321.1 L120.1,323.5
 C112.6,322.4 106.4,321.4 100.1,320.5 C90.4,319.1 83.8,319.3 79.9,318.0
 Q77.8,317.1 80.2,315.7 Z"""
}

# The animal's outer curve crosses over the shield here; clip to the observed leg contour.
for name,mask in [('silhouette',sil),('ivory',light)]: Image.fromarray(mask.astype('uint8')*255).save(TMP/(name+'.png'))
preview=np.zeros((*alpha.shape,4),dtype='uint8');preview[sil]=[23,21,19,255];preview[light]=[255,245,223,255]
Image.fromarray(preview).save(TMP/'preview.png')
canvas=Image.new('RGBA',src.size,'white');canvas.alpha_composite(Image.fromarray(preview));canvas.crop((0,275,485,1120)).save(TMP/'preview_white.png')
print('silhouette pixels',sil.sum(),'ivory pixels',light.sum())

body='<g id="stag-supporter"><title>Stag supporter</title>'
body+='<path id="stag-ink-silhouette" fill="#171513" fill-rule="evenodd" d="'+trace_mask(sil,turdsize=20,opttolerance=.55)+'"/>'
body+='<path id="stag-ivory-engraving" fill="#fff5df" fill-rule="evenodd" d="'+trace_mask(light,turdsize=7,opttolerance=.4)+'"/>'
body+='<defs><clipPath id="stag-antler-interior-clip"><path fill-rule="evenodd" clip-rule="evenodd" d="'+trace_mask((ndi.distance_transform_edt(sil)>2.0)&antler_region,turdsize=4,opttolerance=.2)+'"/></clipPath></defs>'
body+='<g id="stag-antler-junction-refinements" fill="#fff5df" clip-path="url(#stag-antler-interior-clip)">'
for name,d in antler_bridges.items():
    body+='<path id="stag-antler-'+name+'" d="'+d+'"/>'
body+='</g></g>'
save_svg(ROOT/'components/stag.svg',body)
print('Wrote stag.svg')
