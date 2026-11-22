from pathlib import Path
import json,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2];W=ROOT/'branding_rebuild';OUT=W/'collection'
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
geometry=json.loads((W/'root/layout_geometry.json').read_text());G={(a['year'],a['page']):a for a in geometry}
manifest=json.loads((OUT/'manifest.json').read_text());results=[]
review=OUT/'review/report_dividers';review.mkdir(parents=True,exist_ok=True)
for r in manifest['assets']:
 if r['group']!='report_dividers':continue
 yr=r['source_report'];pg=r['source_pdf_page'];geo=G[(yr,pg)];fr=geo['frame_bbox_native'];x0,y0,x1,y1=fr
 src=np.array(Image.open(W/'root'/f'{yr}_pdf{pg:03d}_native.png').convert('L'))
 M=np.array([[1000/(x1-x0),0,-x0*1000/(x1-x0)],[0,1000/(y1-y0),-y0*1000/(y1-y0)]],dtype='float32')
 a=cv2.warpAffine(src,M,(1000,1045),flags=cv2.INTER_LINEAR,borderValue=255)
 vector=np.array(Image.open(OUT/r['preview']).convert('L'));b=vector
 primary=b<120;sa=a<128
 # Exclude screened pale emblems from numeric comparison: a bilevel scan
 # stores them as scattered black dots, whereas the reconstruction is flat tint.
 mask=np.ones((1045,1000),bool)
 key=r['id'].split('_')[1]
 for branch,(xx,yy,ww,hh) in zip(['fishwildlife','parks','museum','fisheries'],[(725,35,245,230),(735,270,230,235),(735,505,230,235),(730,735,240,235)]):
  if branch!=key:mask[yy:yy+hh,xx:xx+ww]=False
 # Original scan may carry unrelated dust and staple damage. These are
 # intentionally excluded only outside the actual artwork region.
 valid=mask
 intersection=np.logical_and(sa,primary)&valid;union=np.logical_or(sa,primary)&valid
 iou=intersection.sum()/max(1,union.sum())
 rec={'id':r['id'],'primary_ink_IoU':round(float(iou),4),'source_report':yr,'source_page':pg,'registration':'One global rectangle-normalizing affine transform; no local warp. Screened non-active emblems omitted from metric. Pixel overlap is not a historical accuracy percentage.'}
 # Composite all visible artwork as a visual check. Use source density so
 # screened and solid inks are both legible without inventing details.
 sr=1-a/255;vr=1-b/255
 rgb=np.stack([1-sr*.76,1-vr*.84,1-np.maximum(sr,vr)*.38],axis=-1)
 over=Image.fromarray(np.uint8(np.clip(rgb,0,1)*255))
 panel=Image.new('RGB',(3060,1130),'#f5f2e9');d=ImageDraw.Draw(panel)
 d.text((20,15),r['title']+f' / primary-ink overlap {iou:.3f}',fill='#163c36',font=F)
 ims=[Image.fromarray(a).convert('RGB'),Image.open(OUT/r['preview']).convert('RGB'),over]
 for j,(im,label) in enumerate(zip(ims,['Original source / registered','Reconstructed vector','Overlay / source cyan, reconstruction pink'])):
  d.text((20+j*1020,48),label,fill='#52675e',font=F);panel.paste(im,(20+j*1020,80))
 path=review/f'{r["id"]}_overlay.png';panel.save(path)
 rec['overlay']=str(path.relative_to(OUT));results.append(rec)
(review/'metrics.json').write_text(json.dumps(results,indent=2))
thumbs=Image.new('RGB',(1600,math_h:=len(results)*280+60),'#f5f2e9');dd=ImageDraw.Draw(thumbs)
for i,r in enumerate(results):
 im=Image.open(OUT/r['overlay']);im.thumbnail((1560,250));thumbs.paste(im,(20,60+i*280));dd.text((20,35+i*280),r['id'],font=F,fill='#163c36')
thumbs.save(review/'All_Divider_Overlays.jpg',quality=90)
print(json.dumps(results,indent=2))
