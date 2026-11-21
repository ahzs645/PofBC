"""Registered visual review of the local right flame shoulder, without scoring."""
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw
from analyze_tree_overlap import annotation_font

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--scope',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();scope=json.loads(args.scope.read_text())
    size=tuple(scope['canvas']);args.output_dir.mkdir(parents=True,exist_ok=True)
    images=[]
    for p in [args.reference,args.before,args.candidate]:
        im=Image.open(p).convert('RGB')
        if im.size!=size: im=im.resize(size,Image.Resampling.LANCZOS)
        images.append(im)
    f=annotation_font(18)
    for region in ['context','detail']:
        x0,y0,x1,y1=scope[region];scale=5
        w,h=(x1-x0)*scale,(y1-y0)*scale
        for grid in [False,True]:
            panel=Image.new('RGB',(3*w+80,h+92),'#f6f3e9');d=ImageDraw.Draw(panel)
            for i,(im,label) in enumerate(zip(images,['Reference','Before shoulder refinement','After shoulder refinement'])):
                x=20+i*(w+20)
                panel.paste(im.crop((x0,y0,x1,y1)).resize((w,h),Image.Resampling.NEAREST),(x,42))
                d.text((x,10),label,font=f,fill='#242332')
                if grid:
                    for gy in range(((y0+9)//10)*10,y1,10):
                        yy=42+(gy-y0)*scale;d.line((x,yy,x+w,yy),fill='#aaaaaa',width=1)
                        d.text((x+2,yy+2),str(gy),font=f,fill='white',stroke_width=1,stroke_fill='#242332')
                    for gx in range(((x0+9)//10)*10,x1,10):
                        xx=x+(gx-x0)*scale;d.line((xx,42,xx,42+h),fill='#aaaaaa',width=1)
                        d.text((xx+2,h+46),str(gx),font=f,fill='#242332')
                else:
                    d.text((x,h+50),f'Fixed crop x{x0}–{x1}, y{y0}–{y1}',font=f,fill='#4b4a4a')
            panel.save(args.output_dir/f'{region}_{"grid" if grid else "color"}.png')
        overlay=Image.new('RGB',(2*w+60,h+80),'#f6f3e9');d=ImageDraw.Draw(overlay)
        for i,(candidate,label) in enumerate(zip(images[1:],['Source + before, 50% each','Source + after, 50% each'])):
            x=20+i*(w+20)
            blend=Image.blend(images[0],candidate,.5).crop((x0,y0,x1,y1)).resize((w,h),Image.Resampling.NEAREST)
            overlay.paste(blend,(x,42));d.text((x,10),label,font=f,fill='#242332')
        overlay.save(args.output_dir/f'{region}_overlap.png')
    provenance={k:str(getattr(args,k).resolve()) for k in ['reference','before','candidate','scope']}
    provenance['scope']=scope
    (args.output_dir/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')

if __name__=='__main__':main()
