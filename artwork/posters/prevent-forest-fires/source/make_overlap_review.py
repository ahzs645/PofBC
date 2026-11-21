"""Assemble measured overlap review artifacts, separately from vector artwork."""
from pathlib import Path
import base64, csv, io, json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work' if (ROOT/'work/reference-rectified.png').exists() else ROOT/'analysis'
DATA=WORK/'overlap_v6' if (WORK/'overlap_v6/before_metrics.json').exists() else WORK
ARTWORK=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'artwork'
OUT=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'review'
FP='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PAPER='#F6F3E9'
INK='#262F3D'
GRAY='#626A73'
CYAN='#00A0C3'
MAGENTA='#D43679'

def font(size,bold=False):
    for candidate in [FB if bold else FP,'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf','/System/Library/Fonts/Helvetica.ttc','C:/Windows/Fonts/arial.ttf']:
        try:return ImageFont.truetype(candidate,size)
        except OSError:pass
    try:return ImageFont.load_default(size=size)
    except TypeError:return ImageFont.load_default()
def pct(x):return f'{100*x:.1f}%'
def pp(x):return f'{100*x:+.1f} pp'
def read(label):return json.loads((DATA/f'{label}_metrics.json').read_text())
def dataurl(im):
    buf=io.BytesIO();im.save(buf,format='PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')

def sheet(before,after):
    canvas=Image.new('RGB',(2120,1420),PAPER);d=ImageDraw.Draw(canvas)
    d.text((40,26),'TREE OVERLAP · BEFORE / REVISED',font=font(37,True),fill=INK)
    d.text((40,80),'Fixed photograph registration · 1000 × 1440 analysis canvas · dark-ink masks, threshold 140',font=font(23),fill=GRAY)
    legend=[(40,INK,'Ink shared by photograph and vector'),(665,CYAN,'Reference only: missing ink'),(1165,MAGENTA,'Vector only: extra ink'),(1620,'#DFE1E3','Excluded lettering')]
    for x,c,label in legend:
        d.rectangle((x,126,x+22,148),fill=c)
        d.text((x+33,122),label,font=font(21),fill=INK)
    for x,label,metrics in [(40,'BEFORE · REVISION 5',before),(1080,'REVISED · REVISION 6',after)]:
        d.text((x,175),label,font=font(27,True),fill=INK)
        v=metrics['regions']['upper']['raw']
        d.text((x,217),f'Upper trees  |  ink overlap {pct(v["iou"])}',font=font(23),fill=INK)
        im=Image.open(DATA/f'{metrics["label"]}_upper_raw.png').convert('RGB')
        canvas.paste(im,(x,254))
        v=metrics['regions']['lower']['raw']
        d.text((x,718),f'Lower woodland  |  ink overlap {pct(v["iou"])}',font=font(23),fill=INK)
        im=Image.open(DATA/f'{metrics["label"]}_lower_raw.png').convert('RGB')
        canvas.paste(im,(x,755))
    d.line((40,1200,2080,1200),fill='#CCD0D2',width=2)
    rows=[('lower_structure','Lower trunks and logs, excluding dense ground'),('lower_ground','Roots and dense ground, measured separately')]
    for j,(key,label) in enumerate(rows):
        b=before['regions'][key]['raw']['iou'];a=after['regions'][key]['raw']['iou']
        d.text((40,1224+j*43),f'{label}:  {pct(b)} → {pct(a)}  ({pp(a-b)})',font=font(24),fill=INK)
    d.text((40,1320),'Overlap = shared dark-ink area ÷ total dark-ink area present in either image.',font=font(23),fill=GRAY)
    d.text((40,1356),'The masks measure this photograph at one fixed alignment; they are not a percentage of historical accuracy.',font=font(22),fill=GRAY)
    canvas.save(OUT/'BC_Forest_Service_Tree_Overlap.png')

def blend_sheet(before,after):
    canvas=Image.new('RGB',(2120,1150),PAPER);d=ImageDraw.Draw(canvas)
    d.text((40,24),'REFERENCE / VECTOR · 50% OVERLAYS',font=font(34,True),fill=INK)
    d.text((40,72),'Same coordinates, scale and crop in every panel. Double edges reveal placement differences.',font=font(22),fill=GRAY)
    for x,label,metrics in [(40,'Before · revision 5',before),(1080,'Revised · revision 6',after)]:
        d.text((x,116),label,font=font(26,True),fill=INK)
        for key,y in [('upper',158),('lower',642)]:
            im=Image.open(DATA/f'{metrics["label"]}_{key}_blend.png').convert('RGB')
            canvas.paste(im,(x,y))
    d.text((40,601),'UPPER TREES',font=font(22,True),fill=INK)
    d.text((40,1070),'LOWER WOODLAND',font=font(22,True),fill=INK)
    d.text((40,1109),'Colour blends are visual inspection aids. The overlap scores use the separate dark-ink masks.',font=font(20),fill=GRAY)
    canvas.save(OUT/'BC_Forest_Service_Tree_Blend.png')

def viewer(before,after):
    ref=Image.open(WORK/'reference-rectified.png').convert('RGB')
    before_path=Path(before['candidate'])
    if not before_path.exists():
        before_path=WORK/'baseline_v5/BC_Forest_Service_Preview.png' if (WORK/'baseline_v5/BC_Forest_Service_Preview.png').exists() else WORK/'before_preview.png'
    after_path=Path(after['candidate'])
    if not after_path.exists():after_path=ARTWORK/'BC_Forest_Service_Preview.png'
    candidates={
      'before':Image.open(before_path).convert('RGB').resize((1000,1440),Image.Resampling.LANCZOS),
      'after':Image.open(after_path).convert('RGB').resize((1000,1440),Image.Resampling.LANCZOS)}
    images={}
    for key,box in [('upper',(0,0,1000,425)),('lower',(0,735,1000,1145))]:
        images[key]={'reference':dataurl(ref.crop(box)),'height':box[3]-box[1]}
        for label,im in candidates.items():
            images[key][label]={'vector':dataurl(im.crop(box))}
            for mode in ['raw','structural']:
                images[key][label][mode]=dataurl(Image.open(DATA/f'{label}_{key}_{mode}.png').convert('RGB'))
    stats={label:{key:{k:v for k,v in run['regions'][key]['raw'].items() if k in ['iou','precision','recall','missing_px','extra_px']}
                  for key in ['upper','lower']} for label,run in [('before',before),('after',after)]}
    template='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Forest Service poster · tree overlap review</title>
<style>
:root{color-scheme:light;--paper:#f6f3e9;--ink:#262f3d;--muted:#626a73;--line:#d5d9da;--cyan:#00a0c3;--magenta:#d43679}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,sans-serif;line-height:1.5}
main{max-width:1460px;margin:auto;padding:28px 24px 48px}h1{margin:0;font-size:clamp(24px,3vw,38px);letter-spacing:-.025em}h2{font-size:20px;margin:26px 0 12px}p{margin:8px 0 16px}.muted{color:var(--muted)}
.controls{display:flex;flex-wrap:wrap;gap:18px 28px;margin:24px 0 16px;align-items:end}.control{display:flex;flex-direction:column;gap:6px}label{font-size:14px;font-weight:650}select,button{border:1px solid #b8bec2;border-radius:6px;color:var(--ink);background:#fff;padding:9px 12px;font:inherit;min-height:42px}select:focus-visible,input:focus-visible{outline:3px solid var(--cyan);outline-offset:2px}input[type=range]{width:220px;accent-color:#3f566c}
.stats{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}.stat{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 18px;min-width:160px}.stat strong{display:block;font-size:25px;line-height:1.2}.stat span{font-size:13px;color:var(--muted)}
.stagewrap{border:1px solid #bdc4c7;border-radius:8px;overflow:auto;background:var(--paper)}.stage{position:relative;width:100%;min-width:650px;aspect-ratio:1000/425}.stage img{position:absolute;width:100%;height:100%;inset:0;object-fit:fill}.stage #mask{display:none}.exclusion{position:absolute;left:12.5%;top:0;width:70.5%;height:35.36585%;background:#dfe1e3;color:#6a7076;display:none;padding:8px 12px;font-size:14px}
.legend{display:flex;flex-wrap:wrap;gap:12px 25px;margin-top:12px;font-size:14px}.legend span{display:flex;align-items:center;gap:8px}.swatch{display:inline-block;width:14px;height:14px;border-radius:2px}.note{max-width:1000px;font-size:15px}.hint{font-size:13px;margin-top:5px}
table{border-collapse:collapse;background:#fff;width:100%;font-size:15px}td,th{padding:10px 14px;border-bottom:1px solid var(--line);text-align:left}th{font-size:13px;color:var(--muted)}.tablewrap{overflow-x:auto}details{margin-top:24px;border-top:1px solid var(--line);padding-top:16px}summary{cursor:pointer;font-weight:650}code{font-family:ui-monospace,monospace}
@media(max-width:700px){main{padding:20px 14px}.stat{flex:1;min-width:135px}.controls{gap:12px}.control{flex:1}select{width:100%}}
</style></head><body><main>
<h1>Tree overlap review</h1>
<p class="muted">British Columbia Forest Service poster · fixed photograph registration · revision 5 → revision 6</p>
<div class="controls">
<div class="control"><label for="region">Artwork region</label><select id="region"><option value="upper">Upper trees</option><option value="lower">Lower woodland</option></select></div>
<div class="control"><label for="revision">Vector version</label><select id="revision"><option value="after">Revised · revision 6</option><option value="before">Before · revision 5</option></select></div>
<div class="control"><label for="mode">Inspection view</label><select id="mode"><option value="raw">Dark-ink differences</option><option value="blend">Reference + vector overlay</option><option value="structural">Differences with light cleanup</option></select></div>
<div class="control" id="opacityControl"><label for="opacity">Vector opacity: <output id="opacityText">50%</output></label><input id="opacity" type="range" min="0" max="100" value="50"></div>
</div>
<div class="stats" aria-live="polite"><div class="stat"><strong id="iou"></strong><span>Raw dark-ink overlap (IoU)</span></div><div class="stat"><strong id="recall"></strong><span>Reference ink covered</span></div><div class="stat"><strong id="precision"></strong><span>Vector ink supported</span></div><div class="stat"><strong id="change"></strong><span>Overlap gain over revision 5</span></div></div>
<p class="hint muted">Scores always use the raw ink masks, including when the lightly cleaned map is displayed.</p>
<div class="stagewrap"><div class="stage" id="stage"><img id="reference" alt="Perspective-corrected reference photograph"><img id="vector" alt="Constructed vector rendering"><img id="mask" alt="Dark-ink difference map"><div class="exclusion" id="exclusion">Lettering excluded</div></div></div>
<p class="hint muted">On a small screen, scroll the image horizontally to inspect the entire width. The overlay slider runs from the photograph (0%) to the vector (100%).</p>
<div class="legend"><span><i class="swatch" style="background:#262f3d"></i>Shared ink</span><span><i class="swatch" style="background:#00a0c3"></i>Reference only · missing ink</span><span><i class="swatch" style="background:#d43679"></i>Vector only · extra ink</span><span><i class="swatch" style="background:#dfe1e3"></i>Lettering excluded</span></div>
<h2>Before and after under the same measurement</h2>
<div class="tablewrap">__TABLE__</div>
<p class="note muted">Ink overlap is the intersection divided by the union of the two dark-ink masks. It is a measure of agreement with this photographed print, not a percentage of historical accuracy. A yellow wood face and an orange background are both outside the dark-ink mask, so use the colour overlay to judge the material shapes too.</p>
<details><summary>Measurement method and limitations</summary>
<p class="note">The supplied photograph is rectified once to 1000 × 1440 pixels. The same coordinates are used for both vector versions. No per-tree alignment, local warping, or movement of the comparison crops is used. Candidate previews are downsampled once from 3000 × 4320 pixels.</p>
<p class="note">Dark ink uses <code>max(R,G,B) &lt; 140</code> in both images. Thresholds 120 and 160 are also recorded in the analysis report. The primary scores above are raw. The optional cleaned map applies the same radius-one cross closing and fills only enclosed holes of nine pixels or less in both images; it does not replace the raw scores.</p>
<p class="note">Upper crop: x=0–1000, y=0–425. Lower crop: x=0–1000, y=735–1145, with the FIRES lettering area x=125–830, y=735–880 excluded. Dense roots and ground (y=1075–1145) are also reported separately because their solid ink area can make the overall lower score look better than the trunks and logs alone.</p>
<p class="note">Paper distortion, approximate corner selection, JPEG blur, print wear, and the deliberately interpreted woodcut details contribute to the remaining differences. The diagnostic masks are used to assess authored vector shapes; they are not traced into artwork paths.</p>
</details></main>
<script>
const images=__IMAGES__;
const stats=__STATS__;
const $=id=>document.getElementById(id);
const percent=x=>(100*x).toFixed(1)+'%';
function update(){
 const region=$('region').value,revision=$('revision').value,mode=$('mode').value;
 const data=images[region],current=data[revision],s=stats[revision][region];
 $('stage').style.aspectRatio='1000 / '+data.height;
 $('reference').src=data.reference;$('vector').src=current.vector;
 const blend=mode==='blend';$('mask').style.display=blend?'none':'block';
 if(!blend)$('mask').src=current[mode];
 $('vector').style.opacity=$('opacity').value/100;
 $('opacityControl').style.visibility=blend?'visible':'hidden';
 $('opacityText').textContent=$('opacity').value+'%';
 $('exclusion').style.display=(blend&&region==='lower')?'block':'none';
 $('iou').textContent=percent(s.iou);$('recall').textContent=percent(s.recall);$('precision').textContent=percent(s.precision);
 const gain=100*(s.iou-stats.before[region].iou);$('change').textContent=(gain>=0?'+':'')+gain.toFixed(1)+' pp';
}
for(const id of ['region','revision','mode','opacity'])$(id).addEventListener('input',update);
update();
</script></body></html>'''
    rows=[]
    for key in ['upper','lower','lower_structure','lower_ground']:
        b=before['regions'][key]['raw']['iou'];a=after['regions'][key]['raw']['iou']
        rows.append(f'<tr><td>{after["regions"][key]["definition"]["name"]}</td><td>{pct(b)}</td><td>{pct(a)}</td><td>{pp(a-b)}</td></tr>')
    table='<table><thead><tr><th>Region</th><th>Before</th><th>Revised</th><th>Change</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
    html=template.replace('__TABLE__',table).replace('__IMAGES__',json.dumps(images,separators=(',',':'))).replace('__STATS__',json.dumps(stats,separators=(',',':')))
    (OUT/'BC_Forest_Service_Overlap_Viewer.html').write_text(html)

def report(before,after):
    lines=['# Tree overlap analysis — revision 5 to revision 6','',
           'The upper conifers and lower burnt woodland were compared with the supplied photograph using a fixed registration. The differences then guided changes to manually authored tree, log, bark, and root shapes. The image masks did not generate artwork contours.','',
           '## Primary result: raw dark-ink overlap','',
           '| Region | Before (revision 5) | Revised (revision 6) | Change |',
           '|---|---:|---:|---:|']
    for key in ['upper','lower','lower_structure','lower_ground']:
        b=before['regions'][key]['raw']['iou'];a=after['regions'][key]['raw']['iou']
        lines.append(f'| {after["regions"][key]["definition"]["name"]} | {pct(b)} | {pct(a)} | {pp(a-b)} |')
    lines+=['','**Definition:** ink overlap is intersection-over-union (IoU): the dark-ink pixels shared by both images divided by all pixels dark in either image. Shared background does not count. A higher number indicates closer ink occupancy at this alignment; it is not a percentage of historical or artistic accuracy.','',
            'The lower trunks/logs and the dense roots/ground are reported separately. Otherwise the large dark ground field would conceal some of the remaining differences in the individual structures. The combined lower-woodland row includes both.','',
            '## How to read the overlays','',
            '- Dark gray: dark ink shared by the reference and vector.',
            '- Cyan: dark ink in the reference that is missing from the vector.',
            '- Magenta: extra dark ink in the vector.',
            '- Light gray rectangle: the excluded FIRES lettering area.','',
            '`BC_Forest_Service_Tree_Overlap.png` shows the raw maps before and after. `BC_Forest_Service_Tree_Blend.png` shows 50/50 colour blends. `BC_Forest_Service_Overlap_Viewer.html` is a self-contained interactive viewer with upper/lower selection, before/revised selection, colour overlay opacity, raw difference maps, and lightly cleaned maps.','',
            'Colour overlays remain necessary: both yellow exposed wood and orange background are outside the dark-ink mask. A better ink overlap score alone cannot determine whether the material shape is correct.','',
            '## Ink coverage and excess','',
            'Reference ink covered (recall) asks how much source ink appears in the vector. Vector ink supported (precision) asks how much vector ink is also present in the source. Both are reported so that adding dark mass everywhere cannot look like an unqualified improvement.','',
            '| Region | Reference covered, before → revised | Vector supported, before → revised | Missing ink pixels, before → revised | Extra ink pixels, before → revised |',
            '|---|---:|---:|---:|---:|']
    for key in ['upper','lower','lower_structure','lower_ground']:
        b=before['regions'][key]['raw'];a=after['regions'][key]['raw'];name=after['regions'][key]['definition']['name']
        lines.append(f'| {name} | {pct(b["recall"])} → {pct(a["recall"])} | {pct(b["precision"])} → {pct(a["precision"])} | {b["missing_px"]:,} → {a["missing_px"]:,} | {b["extra_px"]:,} → {a["extra_px"]:,} |')
    lines+=['','## Threshold sensitivity','',
            'The same RGB classifier is applied to the reference and each vector render. The primary threshold is 140, with 120 and 160 checked as sensitivity bounds. Requiring every RGB channel to be below the threshold avoids classifying the orange and yellow fields as dark ink. These are diagnostic thresholds, not estimated historical ink colours.','',
            '| Region | Threshold 120, before → revised | Threshold 140, before → revised | Threshold 160, before → revised |',
            '|---|---:|---:|---:|']
    for key in ['upper','lower','lower_structure','lower_ground']:
        name=after['regions'][key]['definition']['name'];vals=[]
        for t in ['120','140','160']:
            b=before['regions'][key]['sensitivity'][t]['iou'];a=after['regions'][key]['sensitivity'][t]['iou']
            vals.append(f'{pct(b)} → {pct(a)}')
        lines.append('| '+name+' | '+' | '.join(vals)+' |')
    lines+=['','## Secondary check: light cleanup','',
            'An identical radius-one cross closing is applied to each binary mask, followed by filling only enclosed holes of nine pixels or fewer. This reduces some small print and bark interruptions. There is no opening that would erase thin twigs, and larger holes and background gaps remain. The result is still an ink mask with internal details, not a pure outer-silhouette measurement. The raw scores above remain the primary comparison.','',
            '| Region | Light-cleanup overlap, before | Light-cleanup overlap, revised | Change |','|---|---:|---:|---:|']
    for key in ['upper','lower','lower_structure','lower_ground']:
        b=before['regions'][key]['structural']['iou'];a=after['regions'][key]['structural']['iou']
        lines.append(f'| {after["regions"][key]["definition"]["name"]} | {pct(b)} | {pct(a)} | {pp(a-b)} |')
    lines+=['','## Secondary check: ink-edge distances','',
            'Edges are computed on the full images before applying the region masks, with a two-pixel guard inside crop and exclusion boundaries. Query and target edges both remain inside that guarded region. A matching edge outside the region is therefore unavailable, which can inflate distances near crop splits; the same restriction is used before and after. The mean distance equally weights the reference-to-vector and vector-to-reference directions. These are all dark-ink edges, including internal grain and print-wear edges; they should not be described as only the exterior tree contour. More mismatched fine details can change these distances even when the main shape improves.','',
            '| Region | Mean symmetric distance, before → revised | Edge F1 within 2 px, before → revised | Edge F1 within 4 px, before → revised |','|---|---:|---:|---:|']
    for key in ['upper','lower','lower_structure','lower_ground']:
        b=before['regions'][key]['raw']['ink_boundary'];a=after['regions'][key]['raw']['ink_boundary'];name=after['regions'][key]['definition']['name']
        lines.append(f'| {name} | {b["mean_symmetric_px"]:.2f} → {a["mean_symmetric_px"]:.2f} px | {pct(b["f1_2px"])} → {pct(a["f1_2px"])} | {pct(b["f1_4px"])} → {pct(a["f1_4px"])} |')
    lines+=['','Directional 95th-percentile distances, exact pixel counts, and component hotspot bounds are included in the JSON files. The CSV includes raw and cleaned counts, scores, and edge metrics for every region.','',
            '## Fixed geometry and exclusions','',
            '- Reference canvas: 1000 × 1440 pixels.',
            '- Photograph corner registration, clockwise from upper left: (248, 27), (1183, 29), (1207, 1423), (216, 1427).',
            '- Upper trees: x=[0, 1000), y=[0, 425).',
            '- Lower woodland: x=[0, 1000), y=[735, 1145).',
            '- Excluded lower lettering rectangle: x=[125, 830), y=[735, 880).',
            '- Lower trunks and logs: the lower region above y=1075.',
            '- Roots and ground: x=[0, 1000), y=[1075, 1145).',
            '- Both vector previews are 3000 × 4320 pixels and are reduced once with Lanczos resampling to the reference canvas.',
            '- No independent alignment of individual trees, no local warping, and no score-optimizing crop changes.','',
            'The corners are visually selected from a photograph. Perspective rectification cannot remove paper curvature, all lens effects, lighting variation, blur, print wear, or JPEG compression. This limits how literally a few-pixel residual should be interpreted. The broad missing and extra ink regions are more reliable guides than isolated speckles.','',
            '## What this does and does not establish','',
            'The method provides a repeatable comparison of the visible dark printing in the supplied image. The final SVG remains constructed from editable vector objects. Fine needles, small torn edges, and individual engraved marks remain interpreted, and the work should not be represented as a pixel-identical archival facsimile.','',
            '## Reproduce the analysis','',
            'Python 3 with Pillow, NumPy, and SciPy is required for the analysis; the artwork generator itself uses the standard library. From the unpacked package root:','',
            '```bash',
            'python3 source/analyze_tree_overlap.py --reference analysis/reference-rectified.png --candidate analysis/before_preview.png --label before --output-dir analysis',
            'python3 source/analyze_tree_overlap.py --reference analysis/reference-rectified.png --candidate artwork/BC_Forest_Service_Preview.png --label after --output-dir analysis',
            '```','',
            'The diagnostic PNGs and JSON metrics can be regenerated without the original image attachment. The fixed rectified reference is supplied in the analysis folder. It is never embedded in the artwork SVG or print PDF.','']
    (OUT/'BC_Forest_Service_Overlap_Analysis.md').write_text('\n'.join(lines))
    combined={'before':before,'after':after}
    (OUT/'BC_Forest_Service_Overlap_Metrics.json').write_text(json.dumps(combined,indent=2))
    with (OUT/'BC_Forest_Service_Overlap_Metrics.csv').open('w',newline='') as handle:
        records=[]
        for label,run in combined.items():
            for key,region in run['regions'].items():
                for kind in ['raw','structural']:
                    m=region[kind];r={'version':label,'region':key,'mask':kind}
                    r.update({k:v for k,v in m.items() if k!='ink_boundary'});r.update(m['ink_boundary']);records.append(r)
        writer=csv.DictWriter(handle,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    before=read('before');after=read('after')
    sheet(before,after);blend_sheet(before,after);viewer(before,after);report(before,after)
    print('Overlap sheet, blend sheet, interactive viewer, report, JSON and CSV written.')

if __name__=='__main__':main()
