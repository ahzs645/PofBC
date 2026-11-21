"""Revision-six comparison and audit record, separate from vector artwork."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
from analyze_tree_overlap import annotation_font, load_image

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'work' if (ROOT/'work/reference-rectified.png').exists() else ROOT/'analysis'
DATA=WORK/'overlap_v6' if (WORK/'overlap_v6/after_metrics.json').exists() else WORK
OUT=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'review'
ART=ROOT/'deliverables' if (ROOT/'deliverables').exists() else ROOT/'artwork'

def read(p):return json.loads(p.read_text())
def pct(v):return f'{100*v:.2f}%'

def main():
    manifest_path=WORK/'v6_iteration_manifest.json'
    if not manifest_path.exists():manifest_path=WORK/'iteration_manifest.json'
    manifest=read(manifest_path)
    before=read(DATA/'before_metrics.json');after=read(DATA/'after_metrics.json')
    rb=read(DATA/'constructed/before/metrics.json');ra=read(DATA/'constructed/after/metrics.json')
    headline=read(DATA/'headline/metrics.json')
    footer=read(DATA/'footer/metrics.json') if (DATA/'footer/metrics.json').exists() else None
    combined={'revision':6,'baseline_revision':5,'manifest':manifest,'tree':{'before':before,'after':after},
              'constructed_details':{'before':rb,'after':ra},'headline':headline,'footer':footer}
    (OUT/'BC_Forest_Service_Iteration_Metrics.json').write_text(json.dumps(combined,indent=2))
    old_path=Path(before['candidate'])
    if not old_path.exists():old_path=WORK/'before_preview.png'
    ims=[load_image(WORK/'reference-rectified.png'),load_image(old_path),load_image(ART/'BC_Forest_Service_Preview.png')]
    board=Image.new('RGB',(1530,880),'#F6F3E9');d=ImageDraw.Draw(board)
    d.text((25,20),'REPEATED OVERLAP REVIEW · REVISION 6',font=annotation_font(28),fill='#242332')
    d.text((25,63),'Fixed photograph alignment; equal scale in all three columns.',font=annotation_font(20),fill='#626A73')
    for i,(im,title,sub) in enumerate(zip(ims,['Reference photograph','Previous delivery · revision 5','Revised construction · revision 6'],
                                           ['Rectified for comparison','Frozen before this refinement','Editable curves and constructed glyphs'])):
        x=25+i*505
        d.text((x,106),title,font=annotation_font(21),fill='#242332')
        board.paste(im.resize((470,677),Image.Resampling.LANCZOS),(x,143))
        d.text((x,836),sub,font=annotation_font(17),fill='#626A73')
    board.save(OUT/'BC_Forest_Service_Refinement_Overview.png')
    lines=['# Recursive overlap review — revision 6','',
      'Revision 6 uses the delivered revision 5 as its frozen baseline. The work repeatedly followed the same loop: inspect a fixed colour comparison and missing/extra ink, change an authored shape, render the complete candidate, measure again, then accept or reject after visual review. Independent combined reviews supplied a final set of targeted corrections.','',
      'The aim is a closer visual reconstruction. None of the numbers below is a 0–10 artistic rating, and no overall “90% accurate” claim is made.','',
      '## Accepted changes','']
    for section in manifest['areas']:
        lines+=['### '+section['name'],'',section['summary'],'',
                '**Selected state:** '+section['selected']+'.',
                '**Review record:** '+section['record']+'.','']
    lines+=['## Final combined result versus the previous delivery','',
      'These measurements use the exact delivered PNG render, including all accepted modules together. Isolated iteration results may differ because adjacent layers can reveal or cover each other.','',
      '| Fixed dark-ink area | Revision 5 | Revision 6 | Change |','|---|---:|---:|---:|']
    for key in ['upper','lower','lower_structure','lower_ground']:
        b=before['regions'][key]['raw'];a=after['regions'][key]['raw']
        lines.append(f'| {after["regions"][key]["definition"]["name"]} | {pct(b["iou"])} | {pct(a["iou"])} | {100*(a["iou"]-b["iou"]):+.2f} percentage points |')
    lines+=['','Dark ink uses the same max-RGB < 140 rule, with the original tree regions and FIRES exclusion unchanged. The main overlap report also gives raw counts, precision, recall, sensitivity at 120/160, light cleanup, and guarded ink-edge distances. The ground has its own row so its large dark area does not conceal the remaining log and trunk differences.','',
      '### Constructed script','',
      '| Ivory script area | Revision 5 | Revision 6 | Mean edge distance, before → after |','|---|---:|---:|---:|']
    b=rb['regions']['prevent_script'];a=ra['regions']['prevent_script']
    lines.append(f'| Prevent | {pct(b["iou"])} | {pct(a["iou"])} | {b["mean_symmetric_edge_px"]:.2f} → {a["mean_symmetric_edge_px"]:.2f} px |')
    lines+=['',f'The script has {b["missing"]:,} → {a["missing"]:,} missing ivory pixels and {b["extra"]:,} → {a["extra"]:,} extra ivory pixels. Both changes are disclosed: increased brush coverage is useful only when the colour review still supports the letter form.','',
      '### Display headline: fill and outline measured separately','',
      '| Word | Dark fill, before → after | Ivory outline, before → after |','|---|---:|---:|']
    for word,v in headline['regions'].items():
        lines.append(f'| {word} | {pct(v["ink"]["baseline"]["iou"])} → {pct(v["ink"]["iou"])} | {pct(v["ivory"]["baseline"]["iou"])} → {pct(v["ivory"]["iou"])} |')
    lines+=['','The headline boxes and both classifiers were frozen before headline edits. A thin outline is especially sensitive to small position and width differences; its score must be read alongside the natural-colour review. Fill and outline scores are not averaged.','',
      '### Flame crest: local orange-field checks','',
      '| Fixed local colour area | Revision 5 | Revision 6 | Mean edge distance, before → after |','|---|---:|---:|---:|']
    for key,v in ra['regions'].items():
        if key=='prevent_script':continue
        b=rb['regions'][key]
        lines.append(f'| {v["definition"]["name"]} | {pct(b["iou"])} | {pct(v["iou"])} | {b["mean_symmetric_edge_px"]:.2f} → {v["mean_symmetric_edge_px"]:.2f} px |')
    lines+=['','These are local orange-field measurements. Their rectangles also contain some lettering or bark, so they are not isolated-flame silhouette scores. The separate five yellow side-ribbon paths are retained from revision 5 and checked using the previously frozen yellow-mask scope. Nearby crest or lettering changes can affect their local colour counts even when a ribbon path is unchanged. No combined flame rating is calculated.','',
      '## How the recursion affected the decisions','',
      '- A first redraw of the lowercase script and a later uniform shift/weight treatment both made the match worse. Those results are retained, but the delivered lowercase uses the original constructed masters with individually bounded placement and brush-weight changes.',
      '- The capital P was rebuilt as one continuous outline after the combined review exposed an angular bowl/downstroke join. A final pass narrows the bottom of its downstroke while retaining its left edge.',
      '- A left-flame experiment made a narrow finger and adjacent tongue less convincing. It was revised before acceptance; the final folds use unequal curved tongues.',
      '- The headline O experiment was corrected after its full render reduced agreement. The outline was then reviewed for visible weight independently of the dark fill.',
      '- Canopy review favoured connected twig ends over a slightly higher intermediate raw score. Remaining right-crown weight and the central flame collar were reviewed after integration.',
      '- Exposed wood received a separate pale-gold colour after the colour review showed the sky yellow made it too vivid. That colour-only stage was checked independently of geometry, so anti-aliasing changes are not described as a construction gain.','',
      '## Construction method and fixed evidence','',
      'Tree structure, flame contours, bark cuts, ground fragments and lettering are authored vector geometry. Masks never become path contours. For the script, headline and selected footer letters, bounded position, proportion and constant stroke-width parameters are fitted to already constructed letter masters, followed by exact SVG render and visual review. This is parameter calibration of editable design elements; it is not automatic bitmap tracing. Final parameter values are recorded in the source modules.','',
      'The source photograph is rectified once to 1000 × 1440 using corners (248,27), (1183,29), (1207,1423), (216,1427). Every vector is rendered at 3000 × 4320 and reduced once using Lanczos. Neither the reference nor individual trees are independently warped to improve agreement. Primary regions, exclusions and thresholds stay fixed; additional local scopes were recorded before edits in their respective areas. Qualitative detail windows may differ from measurement rectangles and are not scored as though they were frozen measurement regions.','',
      'The actual artwork contains no photograph, live text or external font dependency. The source image, masks, overlays and colour comparison boards appear only in review/analysis materials. The artwork builder itself never reads a raster reference.','',
      '## Remaining interpretation','',
      'The supplied photograph contains blur, aged ink, uneven lighting, print wear and very small broken marks. Individual needles, torn grain and tiny bark gaps remain interpreted rather than copied pixel for pixel. Some lettering contours and small spacing still differ. The separate colour/edge diagnostics and source comparison make those limits visible; the package does not claim an archival facsimile or certify a subjective 9/10.','',
      '## Files and reproducibility','',
      '`BC_Forest_Service_Refinement_Overview.png` places the fixed source, delivered revision 5 and final revision 6 side by side. Tree detail, flame detail, colour blends and missing/extra-ink maps provide larger crops. `BC_Forest_Service_Iteration_Metrics.json` contains the exact measurements used here, together with the selected source states.','',
      'The ZIP includes the editable artwork, independent vector PDF, all construction modules, final diagnostics and fixed scopes, the baseline render, source reference, per-area ledgers and source/metric checkpoints. Rejected cycles are retained as history, clearly separate from the delivered artwork. Large intermediate PNG renders are omitted where the complete source snapshot can regenerate them. Final analysis commands are in the reconstruction notes and individual reports. `SHA256SUMS.txt` records the packaged files.','']
    if footer:
        lines+=['## Footer word fitting','',
          'The footer record uses word areas and classifiers frozen before the closing edits. Only bounded transformations of existing glyphs were used. The ivory rule is recorded separately in the footer scope; these local word measurements are separate from the tree analysis.','',
          '| Word | Ivory overlap, before → after | Mean ivory edge distance, before → after |','|---|---:|---:|']
        for key,v in footer['regions'].items():
            b=v['ivory']['baseline'];a=v['ivory']['candidate']
            lines.append(f'| {v["definition"]["name"]} | {pct(b["iou"])} → {pct(a["iou"])} | {b["mean_symmetric_boundary_px"]:.2f} → {a["mean_symmetric_boundary_px"]:.2f} px |')
        lines+=['','The corresponding dark-space checks and complete pixel counts are retained in the JSON. Background agreement is not used as a substitute for ivory letter agreement.','']
    (OUT/'BC_Forest_Service_Iteration_Review.md').write_text('\n'.join(lines))
    print('Revision 6 iteration review, metrics and overview written.')

if __name__=='__main__':main()
