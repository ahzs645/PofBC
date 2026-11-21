"""Fixed local colour and edge diagnostics; never used to generate artwork paths."""
from pathlib import Path
import argparse,json
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageDraw,ImageFont

def font(size=18):
    try:return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    except OSError:return ImageFont.load_default()

def classify(im,name,scope):
    a=np.asarray(im,dtype=float);r,g,b=a[...,0],a[...,1],a[...,2];c=scope['classifiers'][name]
    if name=='orange':return (r>c['red_min'])&(g>c['green_min'])&(g<r*c['green_red_ratio_max'])&(b<r*c['blue_red_ratio_max'])
    return (r>c['red_min'])&(g>c['green_min'])&(b>c['blue_min'])&((r-g)<c['red_green_delta_max'])&((g-b)<c['green_blue_delta_max'])

def analyze(ref,cand,scope):
    out={}
    for key,region in scope['regions'].items():
        x0,y0,x1,y1=region['box'];a=classify(ref,region['class'],scope);b=classify(cand,region['class'],scope)
        valid=np.zeros(a.shape,bool);valid[y0:y1,x0:x1]=True
        inter=int((a&b&valid).sum());missing=int((a&~b&valid).sum());extra=int((~a&b&valid).sum())
        eroded=ndi.binary_erosion(valid,iterations=2)
        ea=(a^ndi.binary_erosion(a))&eroded;eb=(b^ndi.binary_erosion(b))&eroded
        da=ndi.distance_transform_edt(~ea)[eb];db=ndi.distance_transform_edt(~eb)[ea]
        out[key]={'definition':region,'intersection':inter,'missing':missing,'extra':extra,'iou':inter/(inter+missing+extra) if inter+missing+extra else 1,
          'mean_symmetric_edge_px':float((da.mean()+db.mean())/2) if len(da) and len(db) else None}
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ['reference','candidate','scope','output_dir']:p.add_argument('--'+field.replace('_','-'),type=Path,required=True)
    p.add_argument('--label',default='Candidate');p.add_argument('--baseline',type=Path)
    args=p.parse_args();scope=json.loads(args.scope.read_text());size=tuple(scope['canvas'])
    ref=Image.open(args.reference).convert('RGB');assert ref.size==size
    cand=Image.open(args.candidate).convert('RGB');cand=cand.resize(size,Image.Resampling.LANCZOS) if cand.size!=size else cand
    args.output_dir.mkdir(parents=True,exist_ok=True)
    result={'scope':scope,'reference':str(args.reference.resolve()),'candidate':str(args.candidate.resolve()),'label':args.label,'regions':analyze(ref,cand,scope)}
    (args.output_dir/'metrics.json').write_text(json.dumps(result,indent=2))
    baseline=Image.open(args.baseline).convert('RGB').resize(size,Image.Resampling.LANCZOS) if args.baseline else None
    for key,region in scope['regions'].items():
        box=tuple(region['box']);x0,y0,x1,y1=box;w=x1-x0;h=y1-y0
        sources=[('Reference',ref),(args.label,cand)] if baseline is None else [('Reference',ref),('Revision 5',baseline),(args.label,cand)]
        scale=min(3,590/w,720/h) if len(sources)==2 else min(3,390/w,700/h)
        cw,ch=round(w*scale),round(h*scale)
        for grid in [False,True]:
            board=Image.new('RGB',(len(sources)*(cw+20)+20,ch+100),'#f4f1e8');d=ImageDraw.Draw(board)
            for i,(name,im) in enumerate(sources):
                ox=20+i*(cw+20);oy=45;board.paste(im.crop(box).resize((cw,ch),Image.Resampling.NEAREST),(ox,oy));d.text((ox,12),name,font=font(),fill='#242332')
                if grid:
                    step=25
                    for gx in range(((x0+step-1)//step)*step,x1,step):
                        xx=ox+round((gx-x0)*scale);d.line((xx,oy,xx,oy+ch),fill='#FFFFFF',width=1);d.text((xx+1,oy+2),str(gx),font=font(12),fill='white',stroke_width=1,stroke_fill='#242332')
                    for gy in range(((y0+step-1)//step)*step,y1,step):
                        yy=oy+round((gy-y0)*scale);d.line((ox,yy,ox+cw,yy),fill='#FFFFFF',width=1);d.text((ox+2,yy+1),str(gy),font=font(12),fill='white',stroke_width=1,stroke_fill='#242332')
            m=result['regions'][key];d.text((20,ch+58),f'{region["name"]}: IoU {100*m["iou"]:.2f}% · mean edge {m["mean_symmetric_edge_px"]:.2f}px',font=font(),fill='#242332')
            board.save(args.output_dir/(key+('_grid.png' if grid else '_color.png')))
        a=classify(ref,region['class'],scope)[y0:y1,x0:x1];b=classify(cand,region['class'],scope)[y0:y1,x0:x1]
        diff=np.full((h,w,3),(246,241,227),dtype=np.uint8);diff[a&b]=(48,47,58);diff[a&~b]=(0,170,198);diff[~a&b]=(220,43,127)
        Image.fromarray(diff).resize((cw,ch),Image.Resampling.NEAREST).save(args.output_dir/(key+'_difference.png'))
    print(json.dumps({k:{'iou':round(v['iou']*100,3),'edge':round(v['mean_symmetric_edge_px'],3),'missing':v['missing'],'extra':v['extra']} for k,v in result['regions'].items()},indent=2))

if __name__=='__main__':main()
