"""Show the concrete details left after revision 5 at matching crop scales."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from analyze_tree_overlap import load_image,annotation_font

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work' if (ROOT/'work/reference-rectified.png').exists() else ROOT/'analysis'
DATA=WORK/'overlap_v6' if (WORK/'overlap_v6/before_metrics.json').exists() else WORK
OUT=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'review'
ART=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'artwork'

FEATURES=[
 ('Left canopy — branch shoulders and lower spray',(40,145,205,322),245),
 ('Right conifer — staggered boughs and open spaces',(755,50,880,315),245),
 ('Leaning trunk — shaft width and root flare',(35,765,265,1115),260),
 ('Main fallen log — exposed face and lower edge',(220,880,790,1010),200),
 ('Under the crossing — ground gaps and exposed end face',(70,1055,640,1125),200),
 ('Right stump and rear arch — connected wood face',(665,1005,835,1125),230),
 ('Right snag — broken top and outer edge',(840,770,935,1075),280),
]

def pct(v):return f'{100*v:.1f}%'

def main():
    before=json.loads((DATA/'before_metrics.json').read_text())
    after=json.loads((DATA/'after_metrics.json').read_text())
    before_path=Path(before['candidate'])
    if not before_path.exists():before_path=WORK/'before_preview.png'
    after_path=Path(after['candidate'])
    if not after_path.exists():after_path=ART/'BC_Forest_Service_Preview.png'
    images=[load_image(WORK/'reference-rectified.png'),load_image(before_path),load_image(after_path)]
    width=1380;height=150+sum(h+58 for _,_,h in FEATURES)+60
    board=Image.new('RGB',(width,height),'#F6F3E9');d=ImageDraw.Draw(board)
    d.text((30,20),'REMAINING DETAILS · RECONSTRUCTION FOLLOW-UP',font=annotation_font(28),fill='#262F3D')
    d.text((30,65),'Source, previous vector and revised vector at matching scale within each row.',font=annotation_font(20),fill='#626A73')
    xs=[30,480,930]
    for x,label in zip(xs,['Reference photograph','Before · revision 5','Revised · revision 6']):
        d.text((x,109),label,font=annotation_font(23),fill='#262F3D')
    y=150
    for title,box,h in FEATURES:
        d.line((30,y-4,1350,y-4),fill='#CDD1D3',width=1)
        d.text((30,y+8),title,font=annotation_font(22),fill='#262F3D')
        w0=box[2]-box[0];h0=box[3]-box[1]
        scale=min(420/w0,h/h0)
        size=(round(w0*scale),round(h0*scale))
        for x,im in zip(xs,images):
            px=x+(420-size[0])//2;py=y+45+(h-size[1])//2
            board.paste(im.crop(box).resize(size,Image.Resampling.LANCZOS),(px,py))
        y+=h+58
    d.text((30,height-40),'The shapes are constructed vectors. The photograph is present only in this review material.',font=annotation_font(19),fill='#626A73')
    board.save(OUT/'BC_Forest_Service_Remaining_Details.png')
    b=json.loads((DATA/'details/before_detail_metrics.json').read_text())
    a=json.loads((DATA/'details/after_detail_metrics.json').read_text())
    combined={'before':b,'after':a}
    (OUT/'BC_Forest_Service_Detail_Metrics.json').write_text(json.dumps(combined,indent=2))
    lines=['','## Follow-up on the details left after revision 5','',
      'The local measurement areas below were fixed before revision 5 and remain unchanged for revision 6. They may overlap, so their counts cannot be added. Some contain adjacent branches or stumps; they are area diagnostics, not isolated-object scores. Lettering is excluded in the leaning-trunk area.','',
      '| Fixed local review area | Before | Revised | Change |','|---|---:|---:|---:|']
    for key in b['regions']:
        rb=b['regions'][key]['raw'];ra=a['regions'][key]['raw']
        lines.append(f'| {a["regions"][key]["definition"]["name"]} | {pct(rb["iou"])} | {pct(ra["iou"])} | {100*(ra["iou"]-rb["iou"]):+.1f} percentage points |')
    lines+=['','`BC_Forest_Service_Remaining_Details.png` shows source shapes alongside revisions 5 and 6: left branch shoulders, staggered right boughs, the leaning trunk/root flare, main fallen log, ground junctions, right rear arch and tall broken snag. These qualitative view windows are selected to show the work and differ from the fixed measurement rectangles above.','',
      'The supplementary JSON records the exact fixed measurement rectangles, exclusions and pixel counts. These local diagnostics use the same raw dark-ink classifier as the primary analysis. A colour crop must still be checked to distinguish exposed pale-gold wood from orange background.','',
      'The local crops and metrics can be regenerated using `source/analyze_detail_areas.py` with `--reference`, `--candidate`, `--label` and `--output-dir`; use the same reference and candidate files as the primary reproduction commands, and set the output directory to `analysis/details`. Run once for label `before` and once for label `after`.','']
    report=OUT/'BC_Forest_Service_Overlap_Analysis.md'
    body=report.read_text()
    marker='\n## Follow-up on the details left after revision 5'
    tail=''
    if marker in body:
        body,_,old_section=body.partition(marker)
        next_section=old_section.find('\n## ')
        if next_section!=-1:
            tail=old_section[next_section:]
    report.write_text(body+'\n'.join(lines)+tail)
    print('Remaining-detail review and fixed local-area results written.')

if __name__=='__main__':main()
