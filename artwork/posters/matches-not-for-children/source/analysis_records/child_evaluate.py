#!/usr/bin/env python3
"""Fixed-mask QA for the two revised child/thread reserve paths."""
from pathlib import Path
import importlib.util
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from lxml import etree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location('child', HERE/'child_reserves.py')
CHILD = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(CHILD)
SPEC = importlib.util.spec_from_file_location('qa', ROOT/'work/revision2/analyze_revision.py')
QA = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(QA)

def main():
    (HERE/'child_reserves.svg').write_text(CHILD.svg())
    tree = etree.parse(str(HERE/'prior/BCFS_Matches_Reconstructed.svg'))
    for key, value in CHILD.RESERVES.items():
        tree.xpath('//*[@id="'+key+'"]')[0].set('d', value)
    tree.write(str(HERE/'child-candidate-master.svg'), encoding='UTF-8', xml_declaration=True)
    ns='http://www.w3.org/2000/svg'
    root=etree.Element('{'+ns+'}svg', width='1000',height='1400',viewBox='0 0 1000 1400')
    root.append(tree.xpath('//*[@id="paper-reserves"]')[0])
    etree.ElementTree(root).write(str(HERE/'child-candidate-reserves.svg'),encoding='UTF-8',xml_declaration=True)
    for name in ['child-candidate-master','child-candidate-reserves']:
        subprocess.run(['inkscape',str(HERE/(name+'.svg')),'--export-type=png',
          '--export-filename='+str(HERE/(name+'.png')),'--export-width=1000'],
          check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    ref=np.asarray(Image.open(ROOT/'work/revision2/reference-reserve-mask-root.png'))>127
    old=np.asarray(Image.open(ROOT/'work/revision2/revised-reserve-mask.png'))>127
    new=np.asarray(Image.open(HERE/'child-candidate-reserves.png').convert('RGBA'))[:,:,3]>127
    yy,xx=np.indices(ref.shape)
    valid=((xx-914.5)/74)**2+((yy-1217.5)/90)**2>1
    valid&=(yy<1250)&(xx>140)&(xx<925)&(yy>30)
    regions={
      'Hanging thread and upper knot':[295,65,410,480],
      'Child head and neck':[280,470,395,610],
      'Child arms, body and legs':[155,570,540,925],
    }
    results={key:{'bounds':box,'revision2':QA.measures(ref,old,valid,box),
      'revision3':QA.measures(ref,new,valid,box)} for key,box in regions.items()}
    report={
      'scope':'Only suspension-thread-reserve and child-figure-reserve were replaced; other V2 paths unchanged.',
      'reference':'Unchanged work/revision2/reference-reserve-mask-root.png, 1000 x 1400',
      'method':'Same V2 evaluator and common valid domain. Alpha threshold >127. Symmetric pooled nearest-boundary distance in normalized pixels. The fixed photographic mask is used for QA only, never SVG contour construction.',
      'regions':results,
    }
    (HERE/'child_metrics.json').write_text(json.dumps(report,indent=2))
    photo=Image.open(ROOT/'work/reference-rectified.png').convert('RGB')
    before=Image.open(HERE/'prior/BCFS_Matches_Preview.png').convert('RGB').resize((1000,1400),Image.Resampling.LANCZOS)
    after=Image.open(HERE/'child-candidate-master.png').convert('RGB')
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    for name,box,scale in [
      ('child',(170,475,540,912),2),
      ('leg_detail',(240,755,540,910),3),
      ('arm_detail',(170,565,475,705),3),
      ('head_detail',(287,470,381,605),4),
      ('thread_detail',(302,180,374,490),3),
    ]:
        width=(box[2]-box[0])*scale; height=(box[3]-box[1])*scale
        board=Image.new('RGB',(width*3+60,height+70),'#f5f3ec');draw=ImageDraw.Draw(board)
        for i,(label,im) in enumerate(zip(['PHOTOGRAPH','REVISION 2','REVISION 3'],[photo,before,after])):
            x=15+i*(width+15);draw.text((x,15),label,fill='#26302f',font=font)
            board.paste(im.crop(box).resize((width,height),Image.Resampling.BICUBIC),(x,50))
        board.save(HERE/(name+'-comparison.png'))
    over_old=QA.overlay(ref,old,np.asarray(photo),valid)
    over_new=QA.overlay(ref,new,np.asarray(photo),valid)
    box=(170,475,540,912);w=740;h=874
    board=Image.new('RGB',(w*2+60,h+145),'#f5f3ec');draw=ImageDraw.Draw(board)
    for i,(label,im) in enumerate(zip(['REVISION 2 AGAINST FIXED PHOTO MASK','REVISION 3 AGAINST FIXED PHOTO MASK'],[over_old,over_new])):
        x=15+i*(w+15);draw.text((x,15),label,fill='#26302f',font=font)
        board.paste(im.crop(box).resize((w,h),Image.Resampling.NEAREST),(x,50))
    draw.rectangle((15,h+75,35,h+95),fill='#00899d')
    draw.text((45,h+72),'Teal: missing pale reserve',fill='#26302f',font=font)
    draw.rectangle((600,h+75,620,h+95),fill='#cd2785')
    draw.text((630,h+72),'Magenta: excess pale reserve',fill='#26302f',font=font)
    draw.text((15,h+110),'Same registration and target mask. These pixels measure photo fit, not historical authenticity.',fill='#54615f',font=font)
    board.save(HERE/'child-overlay-comparison.png')
    Image.fromarray((new*255).astype('uint8')).save(HERE/'child-candidate-reserve-mask.png')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
