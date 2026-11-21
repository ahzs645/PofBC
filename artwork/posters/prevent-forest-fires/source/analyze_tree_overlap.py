"""Fixed-registration diagnostics; never generates or traces SVG geometry.

Compares visible dark ink in the supplied rectified photograph and SVG renders.
The source photograph is fixed at 1000 x 1440. Candidate renders are downsampled
once. No per-tree alignment, elastic warping, or score-optimizing registration.
"""
from pathlib import Path
import argparse, json
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work'
OUT=WORK/'overlap'
SHAPE=(1440,1000)
INK=(38,47,61)
MISSING=(0,160,195)
EXTRA=(212,54,121)
PAPER=(246,243,233)
EXCLUDED=(223,225,227)
FP='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def annotation_font(size):
    for candidate in [FP,'DejaVuSans.ttf','/System/Library/Fonts/Helvetica.ttc','C:/Windows/Fonts/arial.ttf']:
        try:return ImageFont.truetype(candidate,size)
        except OSError:pass
    try:return ImageFont.load_default(size=size)
    except TypeError:return ImageFont.load_default()

REGIONS={
 'upper': {'name':'Upper trees', 'box':[0,0,1000,425], 'exclusions':[]},
 'lower': {'name':'Lower woodland', 'box':[0,735,1000,1145], 'exclusions':[[125,735,830,880]]},
 'lower_structure': {'name':'Lower trunks and logs', 'box':[0,735,1000,1075], 'exclusions':[[125,735,830,880]]},
 'lower_ground': {'name':'Roots and ground', 'box':[0,1075,1000,1145], 'exclusions':[]},
}

def load_image(path):
    im=Image.open(path).convert('RGB')
    if im.size!=(1000,1440): im=im.resize((1000,1440),Image.Resampling.LANCZOS)
    return im

def ink_mask(im,threshold=140):
    # Requiring every colour channel to be dark excludes the orange/yellow
    # flames despite their lower luminance. Ivory lettering is also excluded.
    return np.asarray(im).max(axis=2)<threshold

def structural_mask(mask):
    # Radius-one closing, identically applied, plus filling only enclosed
    # islands <=9 pixels. Fine twigs are not removed by an opening operation.
    disk=np.array([[0,1,0],[1,1,1],[0,1,0]],bool)
    padded=np.pad(mask,2,mode='edge')
    result=ndi.binary_closing(padded,structure=disk)[2:-2,2:-2]
    holes=ndi.binary_fill_holes(result)&~result
    lab,n=ndi.label(holes)
    counts=np.bincount(lab.ravel()); keep=counts<=9
    keep[0]=False
    return result|keep[lab]

def roi_mask(region):
    m=np.zeros(SHAPE,bool)
    x0,y0,x1,y1=region['box'];m[y0:y1,x0:x1]=True
    for a,b,c,d in region['exclusions']:m[b:d,a:c]=False
    return m

def boundary_metrics(a,b,roi):
    # Compute ink edges on the full image, then suppress artificial ROI edges.
    inside=ndi.binary_erosion(roi,iterations=2,border_value=0)
    ea=(a&~ndi.binary_erosion(a,border_value=1))&inside
    eb=(b&~ndi.binary_erosion(b,border_value=1))&inside
    if not ea.any() or not eb.any():return None
    da=ndi.distance_transform_edt(~ea)
    db=ndi.distance_transform_edt(~eb)
    atob=db[ea];btoa=da[eb]
    result={'mean_symmetric_px':float((atob.mean()+btoa.mean())/2),
            'source_to_vector_p95_px':float(np.percentile(atob,95)),
            'vector_to_source_p95_px':float(np.percentile(btoa,95))}
    for tol in [2,4]:
        recall=float((atob<=tol).mean());precision=float((btoa<=tol).mean())
        result[f'f1_{tol}px']=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return result

def metrics(a,b,region,with_boundary=True):
    roi=roi_mask(region); aa=a&roi;bb=b&roi
    common=int((aa&bb).sum());missing=int((aa&~bb).sum());extra=int((bb&~aa).sum())
    union=common+missing+extra
    r={'valid_roi_px':int(roi.sum()),'reference_ink_px':int(aa.sum()),'vector_ink_px':int(bb.sum()),
       'shared_px':common,'missing_px':missing,'extra_px':extra,
       'iou':common/union if union else 1.0,
       'precision':common/(common+extra) if common+extra else 1.0,
       'recall':common/(common+missing) if common+missing else 1.0}
    if with_boundary:r['ink_boundary']=boundary_metrics(a,b,roi)
    return r

def largest_regions(mask,roi,limit=10):
    # Diagnostic connected areas only. These coordinates are not used to draw
    # SVG paths; an illustrator decides how authored structural objects change.
    labels,n=ndi.label(mask&roi)
    counts=np.bincount(labels.ravel());counts[0]=0
    objects=ndi.find_objects(labels)
    items=[]
    for k in np.argsort(counts)[-limit:][::-1]:
        if not k or counts[k]<20:continue
        yy,xx=objects[k-1]
        items.append({'pixels':int(counts[k]),'box':[xx.start,yy.start,xx.stop,yy.stop]})
    return items

def overlap_image(a,b,region):
    roi=roi_mask(region)
    arr=np.empty((*SHAPE,3),np.uint8);arr[:]=PAPER
    arr[a&b]=INK;arr[a&~b]=MISSING;arr[b&~a]=EXTRA
    arr[~roi]=EXCLUDED
    x0,y0,x1,y1=region['box']
    im=Image.fromarray(arr).crop((x0,y0,x1,y1))
    d=ImageDraw.Draw(im)
    for ax,ay,bx,by in region['exclusions']:
        d.text((ax-x0+12,ay-y0+10),'Lettering excluded',font=annotation_font(18),fill=(106,112,118))
    return im

def write_run(candidate,label,reference=None,outdir=None):
    reference=Path(reference) if reference else WORK/'reference-rectified.png'
    outdir=Path(outdir) if outdir else OUT
    outdir.mkdir(parents=True,exist_ok=True)
    ref=load_image(reference);vec=load_image(candidate)
    a=ink_mask(ref);b=ink_mask(vec)
    ac=structural_mask(a);bc=structural_mask(b)
    data={'label':label,'reference':str(reference.resolve()),'candidate':str(Path(candidate).resolve()),
          'registration':{'canvas':[1000,1440],
              'source_photo_corners':[[248,27],[1183,29],[1207,1423],[216,1427]],
              'independent_tree_alignment':False},
          'method':{'ink_classifier':'max(R,G,B) < threshold','primary_threshold':140,
                    'threshold_sensitivity':[120,140,160],
                    'structural_cleanup':'radius-1 cross closing; fill enclosed holes <=9 pixels; both images identically',
                    'boundary_crop_guard_px':2},
          'regions':{}}
    for key,reg in REGIONS.items():
        roi=roi_mask(reg)
        entry={'definition':reg,'raw':metrics(a,b,reg),'structural':metrics(ac,bc,reg),
               'sensitivity':{},'missing_hotspots':largest_regions(ac&~bc,roi),
               'extra_hotspots':largest_regions(bc&~ac,roi)}
        for threshold in [120,140,160]:
            entry['sensitivity'][str(threshold)]=metrics(ink_mask(ref,threshold),ink_mask(vec,threshold),reg,False)
        data['regions'][key]=entry
        overlap_image(a,b,reg).save(outdir/f'{label}_{key}_raw.png')
        overlap_image(ac,bc,reg).save(outdir/f'{label}_{key}_structural.png')
        if key in ['upper','lower']:
            x0,y0,x1,y1=reg['box']
            Image.blend(ref,vec,.5).crop((x0,y0,x1,y1)).save(outdir/f'{label}_{key}_blend.png')
    (outdir/f'{label}_metrics.json').write_text(json.dumps(data,indent=2))
    # Region mask is shown in its entirety, making the exclusions reviewable.
    np.savez_compressed(outdir/f'{label}_masks.npz',reference=a,vector=b,reference_structural=ac,vector_structural=bc)
    return data

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',required=True)
    ap.add_argument('--label',required=True)
    ap.add_argument('--reference',default=str(WORK/'reference-rectified.png'))
    ap.add_argument('--output-dir',default=str(OUT))
    args=ap.parse_args()
    data=write_run(args.candidate,args.label,args.reference,args.output_dir)
    for key,v in data['regions'].items():
        raw=v['raw'];st=v['structural']
        print(key, 'raw IoU',round(raw['iou'],4),'structural IoU',round(st['iou'],4),
              'precision',round(raw['precision'],4),'recall',round(raw['recall'],4),
              'missing',raw['missing_px'],'extra',raw['extra_px'])
    print(Path(args.output_dir)/f'{args.label}_metrics.json')

if __name__=='__main__':main()
