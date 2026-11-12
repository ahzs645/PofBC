from pathlib import Path
from PIL import Image
import numpy as np
import json
from scipy import ndimage as nd
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/gazette'
OUT.mkdir(parents=True,exist_ok=True)
# Use alpha to avoid interpreting the transparent background as black.
im=Image.open(ROOT/'verification/OFC_source_aligned_4x.png').convert('RGBA')
im=Image.alpha_composite(Image.new('RGBA',im.size,'white'),im).convert('L').resize((747,341),Image.Resampling.LANCZOS)
model=np.asarray(im)<128
src=np.asarray(Image.open(ROOT/'reference/OFC_1977_Gazette_logo_890x310.png').convert('L'))
raw=src<128
smooth=nd.gaussian_filter(src.astype(float),0.8)<128
l,n=nd.label(smooth)
counts=np.bincount(l.ravel());counts[0]=0
keep=np.argsort(counts)[-3:]
clean=np.isin(l,keep)
# Fill only tiny white print speckles; keep the proper O counter and C opening.
l,n=nd.label(~clean)
counts=np.bincount(l.ravel());counts[0]=0
small=np.where(counts<20)[0]
clean |= np.isin(l,small)

def bbox(a):
 y,x=np.where(a);return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
mb=bbox(model); sb=bbox(clean)
sx=(sb[2]-sb[0])/(mb[2]-mb[0]);sy=(sb[3]-sb[1])/(mb[3]-mb[1])
start=np.array([sx,0.,sb[0]-sx*mb[0],0.,sy,sb[1]-sy*mb[1]])
def edge(a):
 y,x=np.where(a&~nd.binary_erosion(a));return np.c_[x+0.5,y+0.5]
me=edge(model);se=edge(clean)
msdf=nd.distance_transform_edt(~model)-nd.distance_transform_edt(model)
ssdf=nd.distance_transform_edt(~clean)-nd.distance_transform_edt(clean)
def aff(p):return np.array([[p[0],p[1]],[p[3],p[4]]]),np.array([p[2],p[5]])
def residual(p):
 m,t=aff(p)
 q=me@m.T+t
 rr=nd.map_coordinates(ssdf,[q[:,1]-.5,q[:,0]-.5],order=1,mode='constant',cval=30)
 qi=(se-t)@np.linalg.inv(m).T
 rr2=nd.map_coordinates(msdf,[qi[:,1]-.5,qi[:,0]-.5],order=1,mode='constant',cval=30)*1.2
 return np.r_[rr,rr2]
fit=least_squares(residual,start,bounds=([1.05,-.15,-60,-.05,1.0,-90],[1.4,.15,50,.05,1.4,10]),loss='soft_l1',f_scale=2.,x_scale='jac',diff_step=1e-4,max_nfev=150)
p=fit.x;m,t=aff(p)
y,x=np.indices(src.shape)
q=(np.c_[x.ravel()+.5,y.ravel()+.5]-t)@np.linalg.inv(m).T
warped=nd.map_coordinates(model.astype(float),[q[:,1]-.5,q[:,0]-.5],order=1,mode='constant').reshape(src.shape)>.5

def iou(a,b):return float((a&b).sum()/(a|b).sum())
res=residual(p)
report={'model_path':'verification/OFC_source_aligned_4x.png','source_path':'reference/OFC_1977_Gazette_logo_890x310.png',
 'model_source_canvas':[747,341],'gazette_canvas':[890,310],
 'method':'one global six-parameter affine, fitted symmetrically to source and model edges with robust least-squares; no per-letter alignment or deformation',
 'source_preprocessing_for_fit':'Gaussian sigma 0.8 px, threshold128, keep three main black components, fill white speckles smaller than20px; raw source retained for separate IoU',
 'model_bbox':mb,'gazette_clean_bbox':sb,'initial_bbox_affine':start.tolist(),
 'affine_model_to_gazette':[[float(p[0]),float(p[1]),float(p[2])],[float(p[3]),float(p[4]),float(p[5])],[0,0,1]],
 'iou_raw_threshold128':iou(warped,raw),'iou_denoised_threshold128':iou(warped,clean),
 'edge_abs_median_px':float(np.median(abs(res))),'edge_abs_mean_px':float(np.mean(abs(res))),'edge_abs_p95_px':float(np.percentile(abs(res),95)),
 'optimization_success':bool(fit.success),'nfev':fit.nfev}
for tag,a in [('model',warped),('gazette',clean)]:
 l,n=nd.label(a);counts=np.bincount(l.ravel());counts[0]=0
 comps=[]
 for j in np.argsort(counts)[-3:]:
  b=bbox(l==j);comps.append((b,j))
 comps.sort(key=lambda z:z[0][0])
 report[tag+'_component_bounds_O_F_C']=[b for b,j in comps]

# Source is not edited or redefined: this diagnostic color-codes binary overlap.
can=np.full((*src.shape,3),255,np.uint8)
can[raw&warped]=[37,42,49]
can[raw&~warped]=[215,48,100]
can[warped&~raw]=[0,161,196]
Image.fromarray(can).resize((1780,620),Image.Resampling.NEAREST).save(OUT/'gazette_global_affine_overlay.png')
Image.fromarray((~warped*255).astype(np.uint8)).save(OUT/'model_aligned_to_gazette.png')
(OUT/'gazette_check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
