"""Fixed dark-fill / ivory-outline diagnostics for authored headline geometry.

Measures only; source masks never create vector contours. Registration, scopes
and colour thresholds are frozen before edits. Scores are reported separately,
not combined into a subjective fidelity rating.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageDraw,ImageFont

PALETTE={'shared':(38,47,61),'missing':(0,160,195),'extra':(212,54,121),'background':(246,241,227)}

def font(size=18):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    except OSError:
        return ImageFont.load_default()

def load_image(p,canvas):
    im=Image.open(p).convert('RGB')
    return im.resize(tuple(canvas),Image.Resampling.LANCZOS) if im.size!=tuple(canvas) else im

def classify(im,name,scope):
    a=np.asarray(im,dtype=float)
    if name=='ink':return a.max(2)<scope['classifiers']['ink']['max_rgb_less_than']
    r,g,b=np.moveaxis(a,2,0);s=scope['classifiers']['ivory']
    return (r>s['red_min'])&(g>s['green_min'])&(b>s['blue_min'])&((r-g)<s['red_green_delta_max'])&((g-b)<s['green_blue_delta_max'])

def metrics(a,b):
    intersection=int((a&b).sum());missing=int((a&~b).sum());extra=int((~a&b).sum())
    ea=a^ndi.binary_erosion(a);eb=b^ndi.binary_erosion(b)
    da=ndi.distance_transform_edt(~ea)[eb];db=ndi.distance_transform_edt(~eb)[ea]
    return {'intersection':intersection,'missing':missing,'extra':extra,'source_area':int(a.sum()),'candidate_area':int(b.sum()),'iou':intersection/(intersection+missing+extra),'mean_symmetric_edge_px':float((da.mean()+db.mean())/2),'p95_symmetric_edge_px':float(np.percentile(np.r_[da,db],95))}

def diff(a,b):
    out=np.full(a.shape+(3,),PALETTE['background'],np.uint8);out[a&b]=PALETTE['shared'];out[a&~b]=PALETTE['missing'];out[~a&b]=PALETTE['extra'];return Image.fromarray(out)

def make_board(sources,box,path,grid=False,maxwidth=1086):
    x,y,xx,yy=box;w=xx-x;h=yy-y;scale=min(3,maxwidth/w);cw,ch=round(w*scale),round(h*scale)
    board=Image.new('RGB',(cw+40,len(sources)*(ch+42)+25),'#F4F1E8');d=ImageDraw.Draw(board)
    for i,(label,im) in enumerate(sources):
        ox=20;oy=48+i*(ch+42);d.text((ox,oy-28),label,font=font(),fill='#242332');board.paste(im.crop(box).resize((cw,ch),Image.Resampling.NEAREST),(ox,oy))
        if grid:
            step=10 if w<230 else 25
            for gx in range(((x+step-1)//step)*step,xx,step):
                px=ox+round((gx-x)*scale);d.line((px,oy,px,oy+ch),fill='white');d.text((px+1,oy+1),str(gx),font=font(10),fill='white',stroke_width=1,stroke_fill='#242332')
            for gy in range(((y+step-1)//step)*step,yy,step):
                py=oy+round((gy-y)*scale);d.line((ox,py,ox+cw,py),fill='white');d.text((ox+1,py+1),str(gy),font=font(10),fill='white',stroke_width=1,stroke_fill='#242332')
    board.save(path)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ['reference','candidate','baseline','scope','output_dir']:p.add_argument('--'+field.replace('_','-'),type=Path,required=True)
    p.add_argument('--label',default='Candidate');args=p.parse_args();scope=json.loads(args.scope.read_text());out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    images={name:load_image(path,scope['canvas']) for name,path in [('Reference',args.reference),('Revision 5',args.baseline),(args.label,args.candidate)]}
    masks={name:{c:classify(im,c,scope) for c in ['ink','ivory']} for name,im in images.items()}
    result={'reference':str(args.reference.resolve()),'candidate':str(args.candidate.resolve()),'baseline':str(args.baseline.resolve()),'label':args.label,'scope':str(args.scope.resolve()),'scope_sha256':hashlib.sha256(args.scope.read_bytes()).hexdigest(),'regions':{}}
    for word,box in scope['regions'].items():
        x,y,xx,yy=box;region={}
        for c in ['ink','ivory']:
            a=masks['Reference'][c][y:yy,x:xx];b=masks[args.label][c][y:yy,x:xx];before=masks['Revision 5'][c][y:yy,x:xx]
            region[c]=metrics(a,b);region[c]['baseline']=metrics(a,before)
            diff(a,b).resize((2*(xx-x),2*(yy-y)),Image.Resampling.NEAREST).save(out/(word.lower()+'_'+c+'_difference.png'))
        result['regions'][word]=region
        for grid in [False,True]:make_board(list(images.items()),box,out/(word.lower()+('_grid.png' if grid else '_color.png')),grid)
    # Focused diagnostic crops are fixed visually chosen windows, not score regions.
    details={'F':[75,450,260,645],'O':[210,450,380,645],'R':[345,450,545,645],'E':[515,455,690,645],'S':[635,455,800,645],'T':[775,455,945,645],'lower_F':[145,675,333,865],'lower_E':[520,680,695,865],'lower_S':[645,675,815,865]}
    for key,box in details.items():
        make_board([('Reference',images['Reference']),(args.label,images[args.label])],box,out/(key+'_detail.png'),False,700)
    (out/'metrics.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({word:{c:{k:round(v*100,3) if k=='iou' else round(v,3) if isinstance(v,float) else v for k,v in m.items() if k in ['iou','missing','extra','mean_symmetric_edge_px']} for c,m in region.items()} for word,region in result['regions'].items()},indent=2))
if __name__=='__main__':main()
