"""Build a colour review of the five side ribbons, outside the vector artwork."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from analyze_tree_overlap import load_image,annotation_font

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work' if (ROOT/'work/reference-rectified.png').exists() else ROOT/'analysis'
DATA=WORK/'overlap_v6' if (WORK/'overlap_v6/before_metrics.json').exists() else WORK
OUT=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'review'
ART=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'artwork'

def number(value):return f'{value:.1f}%'

def main():
    flame=DATA/'flames'
    before=json.loads((flame/'before/metrics.json').read_text())
    after=json.loads((flame/'after/metrics.json').read_text())
    scope=json.loads((flame/'regions_before_edits.json').read_text())
    shoulder_path=flame/'shoulder/scope_before_edit.json'
    shoulder=json.loads(shoulder_path.read_text()) if shoulder_path.exists() else None
    tree_before=json.loads((DATA/'before_metrics.json').read_text())
    old_path=Path(tree_before['candidate'])
    if not old_path.exists():old_path=WORK/'before_preview.png'
    images=[load_image(WORK/'reference-rectified.png'),load_image(old_path),
            load_image(ART/'BC_Forest_Service_Preview.png')]
    row_heights={'left_long':300,'left_mid':235,'left_low':235,'right_oblique':255,'right_low':235}
    width=1400;height=160+sum(row_heights[k]+62 for k in scope['regions'])+60
    if shoulder:height+=362
    board=Image.new('RGB',(width,height),'#F6F3E9');draw=ImageDraw.Draw(board)
    draw.text((30,22),'FLAME-LINE CHECK · REVISION 5 TO 6',font=annotation_font(29),fill='#262F3D')
    draw.text((30,65),'Retained side ribbons and a shoulder check; matching crops and scale within each row.',font=annotation_font(20),fill='#626A73')
    xs=[30,490,950]
    for x,title in zip(xs,['Reference photograph','Before · revision 5','Revised · revision 6']):
        draw.text((x,111),title,font=annotation_font(23),fill='#262F3D')
    y=160
    for key,region in scope['regions'].items():
        old=before['regions'][key]['iou_percent'];new=after['regions'][key]['iou_percent']
        draw.line((30,y-5,1370,y-5),fill='#CDD1D3',width=1)
        draw.text((30,y+7),region['name']+f'  ·  yellow overlap {number(old)} → {number(new)}',font=annotation_font(21),fill='#262F3D')
        box=tuple(region['context']);h=row_heights[key]
        scale=min(420/(box[2]-box[0]),h/(box[3]-box[1]))
        size=(round((box[2]-box[0])*scale),round((box[3]-box[1])*scale))
        for x,im in zip(xs,images):
            board.paste(im.crop(box).resize(size,Image.Resampling.LANCZOS),
                        (x+(420-size[0])//2,y+45+(h-size[1])//2))
        y+=h+62
    if shoulder:
        draw.line((30,y-5,1370,y-5),fill='#CDD1D3',width=1)
        draw.text((30,y+7),'Right shoulder — curved fork and narrow orange tongue · visual comparison',font=annotation_font(21),fill='#262F3D')
        box=tuple(shoulder['detail']);h=300
        scale=min(420/(box[2]-box[0]),h/(box[3]-box[1]))
        size=(round((box[2]-box[0])*scale),round((box[3]-box[1])*scale))
        for x,im in zip(xs,images):
            board.paste(im.crop(box).resize(size,Image.Resampling.LANCZOS),
                        (x+(420-size[0])//2,y+45+(h-size[1])//2))
        y+=362
    draw.text((30,height-40),'Scores use the fixed measurement areas and exclusions; colour crops provide wider context.',font=annotation_font(19),fill='#626A73')
    OUT.mkdir(exist_ok=True,parents=True)
    board.save(OUT/'BC_Forest_Service_Flame_Details.png')
    combined={'scope':scope,'before':before,'after':after}
    if shoulder:combined['shoulder_visual_scope']=shoulder
    (OUT/'BC_Forest_Service_Flame_Overlap_Metrics.json').write_text(json.dumps(combined,indent=2))
    lines=['# Flame-line overlap analysis — revision 5 to revision 6','',
           'Five yellow side ribbons were checked separately from the dark-ink tree analysis. Their path geometry is retained from revision 5; revision 6 concentrates its flame changes on the upper crest and narrow folds. Nearby crest or lettering changes can still affect a local colour mask. The rectified source photograph remains fixed at 1000 × 1440 pixels, and each vector preview is reduced once from 3000 × 4320 using Lanczos resampling. The large orange field is not included in a single overall score.','',
           '## Local yellow overlap','',
           '| Fixed review area | Before | Revised | Change |','|---|---:|---:|---:|']
    for key,region in scope['regions'].items():
        b=before['regions'][key];a=after['regions'][key]
        lines.append(f'| {region["name"]} | {number(b["iou_percent"])} | {number(a["iou_percent"])} | {a["iou_percent"]-b["iou_percent"]:+.1f} percentage points |')
    lines+=['','The percentages are intersection-over-union of the locally classified yellow areas. They describe agreement at this fixed registration, with the stated colour rule. They do not establish exact historical ink colour or distinguish every feature of photographed print wear. The boxes can overlap; their counts are not added or presented as an overall flame score.','',
            '## Classifier and fixed scope','',
            'The same classifier, measurement boxes and exclusions are applied to both revisions. Scope and exclusions were settled before the first revision-5 flame-geometry edit. The exact definitions below are retained in `analysis/flames/regions_before_edits.json`.','',
            '```json',json.dumps(scope,indent=2),'```','',
            'The wider colour crops show visual context. Measurement boxes may cover only a useful section of a ribbon; for example, the left long vein is assessed on its lower shaft. The difference images show shared yellow in dark gray, reference-only yellow in cyan, candidate-only yellow in magenta, and excluded areas in light gray.','',
            '## Coverage and excess','',
            '| Area | Reference covered, before → revised | Vector supported, before → revised | Missing pixels, before → revised | Extra pixels, before → revised |','|---|---:|---:|---:|---:|']
    for key,region in scope['regions'].items():
        b=before['regions'][key];a=after['regions'][key]
        lines.append(f'| {region["name"]} | {number(b["recall_percent"])} → {number(a["recall_percent"])} | {number(b["precision_percent"])} → {number(a["precision_percent"])} | {b["missing_pixels"]:,} → {a["missing_pixels"]:,} | {b["extra_pixels"]:,} → {a["extra_pixels"]:,} |')
    ratios=scope['sensitivity_green_red_ratio']
    lines+=['','## Colour-threshold sensitivity','',
            '| Area | '+' | '.join('G/R ≥ '+str(v) for v in ratios)+' |',
            '|---|'+'---:|'*len(ratios)]
    for key,region in scope['regions'].items():
        b=before['regions'][key];a=after['regions'][key]
        values=[number(b['sensitivity'][str(r)]['iou_percent'])+' → '+number(a['sensitivity'][str(r)]['iou_percent']) for r in ratios]
        lines.append('| '+region['name']+' | '+' | '.join(values)+' |')
    if shoulder:
        lines+=['','## Local right shoulder','',
                'The curved fork and narrow orange tongue introduced in revision 5 are retained. Revision 6 changes the adjacent orange neck and several other crest peaks, while keeping all five detached side-ribbon paths and `right-inside-shoulder` unchanged.','',
                'The shoulder is reviewed with fixed colour crops, grid crops and 50% overlays. No separate numerical yellow score is claimed because the canopy and surrounding yellow field interact in this crop. Both the scoped comparison and overview sheet use the delivered revision-5 render and final revision 6.','',
                'The scope, previous-delivery render and comparison images are in `analysis/flames/shoulder/`. The additional orange-field and script measurements are documented in the iteration review; those colour regions are not isolated-flame scores.','']
    lines+=['','## Reproduce','',
            'Run from the unpacked package root with Python 3, Pillow, NumPy and SciPy:','',
            '```bash',
            'python3 source/analyze_flame_edges.py --candidate analysis/before_preview.png --reference analysis/reference-rectified.png --scope analysis/flames/regions_before_edits.json --label before --output-dir analysis/flames/before',
            'python3 source/analyze_flame_edges.py --candidate artwork/BC_Forest_Service_Preview.png --reference analysis/reference-rectified.png --scope analysis/flames/regions_before_edits.json --label after --output-dir analysis/flames/after',
            'python3 source/make_flame_review.py','```','',
            'The artwork paths are authored independently in `source/flames_v2.py`. The diagnostic masks never create or trace vector contours.','']
    if shoulder:
        lines+=['The scoped shoulder comparison can be reproduced independently:','',
                '```bash',
                'python3 source/make_shoulder_review.py --reference analysis/reference-rectified.png --before analysis/flames/shoulder/before_preview.png --candidate artwork/BC_Forest_Service_Preview.png --scope analysis/flames/shoulder/scope_before_edit.json --output-dir analysis/flames/shoulder/review','```','']
    (OUT/'BC_Forest_Service_Flame_Overlap_Analysis.md').write_text('\n'.join(lines))
    report=OUT/'BC_Forest_Service_Overlap_Analysis.md'
    marker='\n## Separate flame-line review'
    body=report.read_text().split(marker)[0]
    body+=marker+'\n\nThe five side ribbons are assessed with fixed local yellow masks, separately from the dark-ink tree regions. Full scope, exclusions, colour-threshold sensitivity, counts and reproduction commands are in `BC_Forest_Service_Flame_Overlap_Analysis.md`; `BC_Forest_Service_Flame_Details.png` provides matching colour crops.\n\n'
    body+='| Flame area | Before | Revised |\n|---|---:|---:|\n'
    for key,region in scope['regions'].items():
        body+='| '+region['name']+' | '+number(before['regions'][key]['iou_percent'])+' | '+number(after['regions'][key]['iou_percent'])+' |\n'
    report.write_text(body)
    print('Flame colour review, report and metrics written.')

if __name__=='__main__':main()
