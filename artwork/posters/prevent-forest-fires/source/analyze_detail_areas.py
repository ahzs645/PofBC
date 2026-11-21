"""Fixed local review areas for the remaining constructed tree details.

Areas are rectangles chosen before revision-4 edits. They may overlap, so their
counts are diagnostic and must not be summed. They never create SVG geometry.
"""
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw
from analyze_tree_overlap import load_image,ink_mask,metrics,overlap_image,annotation_font

ROOT=Path(__file__).resolve().parent.parent
DEFAULT_WORK=ROOT/'work'
REGIONS={
 'upper_left':{'name':'Left canopy and trunk tip','box':[0,0,265,425],'exclusions':[]},
 'upper_second':{'name':'Second crown and hanging boughs','box':[210,0,415,280],'exclusions':[]},
 'upper_centre':{'name':'Central tree and its boughs','box':[410,0,735,290],'exclusions':[]},
 'upper_right':{'name':'Right canopy and outer branches','box':[740,0,1000,380],'exclusions':[]},
 'leaning_trunk':{'name':'Leaning trunk and root area','box':[25,780,270,1145],'exclusions':[[125,780,270,880]]},
 'main_log':{'name':'Fallen-log middle span','box':[285,885,650,1015],'exclusions':[]},
 'rear_branches':{'name':'Rear branches and right-stump area','box':[535,1005,875,1095],'exclusions':[]},
 'ground_right':{'name':'Right-hand ground openings','box':[745,1075,1000,1145],'exclusions':[]},
}

def run(reference,candidate,label,outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    ref=load_image(reference);vec=load_image(candidate)
    a=ink_mask(ref);b=ink_mask(vec)
    results={'label':label,'reference':str(reference),'candidate':str(candidate),
             'method':'Fixed rectangular diagnostic areas; raw maxRGB <140; same registration as primary analysis; areas may overlap.',
             'regions':{}}
    for key,region in REGIONS.items():
        results['regions'][key]={'definition':region,'raw':metrics(a,b,region,False)}
        box=tuple(region['box']);width=box[2]-box[0];height=box[3]-box[1]
        scale=3
        board=Image.new('RGB',(3*width*scale+80,height*scale+105),'#F6F3E9');draw=ImageDraw.Draw(board)
        draw.text((20,10),region['name']+f'  ·  x={box[0]}–{box[2]}, y={box[1]}–{box[3]}',font=annotation_font(19),fill='#262F3D')
        panels=[('Reference',ref.crop(box)),('Vector · '+label,vec.crop(box)),('Shared / missing / extra',overlap_image(a,b,region))]
        for i,(title,im) in enumerate(panels):
            x=20+i*(width*scale+20)
            draw.text((x,42),title,font=annotation_font(18),fill='#262F3D')
            board.paste(im.resize((width*scale,height*scale),Image.Resampling.NEAREST if i==2 else Image.Resampling.LANCZOS),(x,75))
        board.save(outdir/f'{label}_{key}_detail.png')
    (outdir/f'{label}_detail_metrics.json').write_text(json.dumps(results,indent=2))
    for key,entry in results['regions'].items():
        m=entry['raw'];print(key,round(100*m['iou'],2),'missing',m['missing_px'],'extra',m['extra_px'])

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',default=str(DEFAULT_WORK/'reference-rectified.png'))
    ap.add_argument('--candidate',required=True)
    ap.add_argument('--label',required=True)
    ap.add_argument('--output-dir',default=str(DEFAULT_WORK/'overlap_v4/details'))
    args=ap.parse_args()
    run(args.reference,args.candidate,args.label,args.output_dir)
