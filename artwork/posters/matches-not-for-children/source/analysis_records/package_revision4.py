#!/usr/bin/env python3
"""Package the completed Revision 4 assembly, diagnostics and reproducible sources."""
from pathlib import Path
from xml.etree import ElementTree as ET
import ast, base64, copy, hashlib, json, re, shutil, subprocess, zipfile
import fitz

ROOT=Path(__file__).resolve().parents[2]
REV=ROOT/'work/revision4'
OUT=ROOT/'output/BC_Forest_Service_Matches'
PRIOR=REV/'prior'
REVIEW=OUT/'review'
SOURCE=OUT/'source'
HISTORY=REVIEW/'history/revision3'
DIAG=REVIEW/'diagnostics/revision4'
NS='http://www.w3.org/2000/svg'

def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)

def canon(e):
 return (e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(canon(c) for c in e))

def group(root,id):
 e=root.find('.//{'+NS+'}g[@id="'+id+'"]')
 if e is None:raise ValueError('Missing group '+id)
 return e

def no_joint(e):
 e=copy.deepcopy(e)
 for parent in e.iter():
  for c in list(parent):
   if c.get('id')=='child-cracked-junction-v4' or c.get('d','').startswith('M330 779 L342 796'):parent.remove(c)
 return e

def validate():
 checks={}
 for p in sorted(OUT.glob('*.svg')):
  tree=ET.parse(p);root=tree.getroot();counts={}
  bad=[];ids=[]
  for e in root.iter():
   kind=e.tag.rsplit('}',1)[-1];counts[kind]=counts.get(kind,0)+1
   if kind in ['image','text','filter','foreignObject']:bad.append(kind)
   if e.get('id'):ids.append(e.get('id'))
   for k,v in e.attrib.items():
    if k.rsplit('}',1)[-1]=='href' and not v.startswith('#'):bad.append('external href')
    if 'url(' in v and re.search(r'url\([\s\"\']*(?!#)',v):bad.append('external url')
  # Fill and clip references must resolve within each standalone file.
  for e in root.iter():
   for v in e.attrib.values():
    for target in re.findall(r'url\(#([^)]*)\)',v):
     if target not in ids:bad.append('missing local id '+target)
  assert not bad,(p,bad)
  assert len(ids)==len(set(ids)),(p,'duplicate ids')
  checks[p.name]={'elements':counts,'embedded_raster_images':0,'live_text':0,'filters':0,'external_references':0,'all_local_references_resolve':True}
 current=ET.parse(OUT/'BCFS_Matches_Reconstructed.svg').getroot()
 prior=ET.parse(PRIOR/'BCFS_Matches_Reconstructed.svg').getroot()
 unchanged={}
 for id in ['paper-reserves','headline-lettering','forest-service-oval','footer-lettering','centennial-caption','publication-marks']:
  unchanged[id]=canon(group(current,id))==canon(group(prior,id));assert unchanged[id],id+' unexpectedly changed'
 original_figures=canon(no_joint(group(prior,'matchstick-illustration')))
 current_figures=canon(no_joint(group(current,'matchstick-illustration')))
 assert original_figures==current_figures,'Unexpected illustration changes outside local joint component'
 pdf=fitz.open(OUT/'BCFS_Matches_Reconstructed.pdf')
 pdf_result={'pages':len(pdf),'embedded_bitmap_images':sum(len(p.get_images(full=True)) for p in pdf),'page_size_points':list(pdf[0].rect)[2:]}
 assert pdf_result['pages']==1 and pdf_result['embedded_bitmap_images']==0
 pdf.close()
 page=(OUT/'BCFS_Interactive_Review.html').read_text()
 assets=json.loads(re.search(r'<script id="assets" type="application/json">(.*?)</script>',page,re.S).group(1))
 assets['revised']=re.search(r'<img id="vector"[^>]*\bsrc="([^"]+)"',page).group(1)
 embedded_metrics=json.loads(re.search(r'<script id="measurements" type="application/json">(.*?)</script>',page,re.S).group(1))
 current_paint=json.loads((REV/'root-analysis/Paint_Measurements.json').read_text())
 current_joint=json.loads((REV/'root-analysis/joint-metrics.json').read_text())
 assert embedded_metrics=={'paint':current_paint,'joint':current_joint},'Stale measurements in HTML'
 assert current_paint['evaluated_paint_sha256']['v4']==hashlib.sha256((OUT/'BCFS_Paint_Background.svg').read_bytes()).hexdigest(),'Paint changed after analysis'
 assert current_joint['evaluated_master_sha256']['v4']==hashlib.sha256((OUT/'BCFS_Matches_Reconstructed.svg').read_bytes()).hexdigest(),'Master changed after joint analysis'
 for key,p in [('previous',PRIOR/'BCFS_Matches_Reconstructed.svg'),('revised',OUT/'BCFS_Matches_Reconstructed.svg'),('clean',OUT/'BCFS_Matches_Clean.svg')]:
  assert base64.b64decode(assets[key].split(',',1)[1])==p.read_bytes(),key+' stale in HTML'
 scripts=re.findall(r'<script>(.*?)</script>',page,re.S);assert len(scripts)==1
 js=REV/'review_script_syntax.js';js.write_text(scripts[0]);subprocess.run(['node','--check',str(js)],check=True,capture_output=True)
 return {'revision':4,'svg_checks':checks,'unchanged_layers_vs_v3':unchanged,'other_illustration_geometry_unchanged':True,
         'pdf':pdf_result,'html':{'embedded_master_bytes_match_deliverables':True,'embedded_measurements_match_final_analysis':True,'javascript_syntax_checked':True,'browser_interaction_exercised':False}}

def portable_analysis():
 s=(REV/'analyze_revision4.py').read_text()
 edits={"ROOT = Path(__file__).resolve().parents[2]":"ROOT = Path(__file__).resolve().parent.parent",
        "REV = ROOT / 'work/revision4'":"REV = ROOT / 'review'",
        "OUT = ROOT / 'output/BC_Forest_Service_Matches'":"OUT = ROOT",
        "REF = ROOT / 'work/reference-rectified.png'":"REF = ROOT / 'review/Reference_Perspective_Normalized.png'",
        "MASK = ROOT / 'work/revision2/background-evaluation-mask.png'":"MASK = ROOT / 'review/diagnostics/revision4/fixed-paint-mask.png'",
        "PREV = REV / 'prior'":"PREV = ROOT / 'review/history/revision3'",
        "DIAG = REV / 'root-analysis'":"DIAG = ROOT / 'review/diagnostics/revision4'"}
 for a,b in edits.items():
  assert a in s,a;s=s.replace(a,b)
 ast.parse(s);return s

def portable_review():
 s=(REV/'build_review_html.py').read_text()
 edits={"ROOT=Path(__file__).resolve().parents[2]":"ROOT=Path(__file__).resolve().parent.parent",
        "REV=ROOT/'work/revision4'":"REV=ROOT/'review'",
        "OUT=ROOT/'output/BC_Forest_Service_Matches'":"OUT=ROOT",
        "DIAG=REV/'root-analysis'":"DIAG=ROOT/'review/diagnostics/revision4'",
        "ROOT/'work/reference-rectified.png'":"ROOT/'review/Reference_Perspective_Normalized.png'",
        "REV/'prior/BCFS_Matches_Reconstructed.svg'":"ROOT/'review/history/revision3/BCFS_Matches_Reconstructed.svg'"}
 for a,b in edits.items():assert a in s,a;s=s.replace(a,b)
 ast.parse(s);return s

def report(paint,joint):
 a=paint['regions']['All eligible paint']['previous'];b=paint['regions']['All eligible paint']['revised']
 j=joint['thresholds']['125'];f=j['fracture_and_splinters'];loc=j['local_joint']
 rows=[]
 for name,v in paint['regions'].items():
  old,new=v['previous'],v['revised']
  pct=lambda n:'—' if n is None else f'{n:.2%}'
  rows.append(f'| {name} | {old["mean_absolute_rgb_error"]:.2f} | {new["mean_absolute_rgb_error"]:.2f} | {pct(old["broad_orange_iou"])} | {pct(new["broad_orange_iou"])} |')
 sensitivity=[]
 for th,v in joint['thresholds'].items():
  x,y=v['fracture_and_splinters']['v3'],v['fracture_and_splinters']['v4']
  sensitivity.append(f'| {th} | {x["iou"]:.2%} | {y["iou"]:.2%} | {x["mean_symmetric_edge_distance"]:.2f} | {y["mean_symmetric_edge_distance"]:.2f} |')
 return f'''# BC Forest Service poster — Revision 4

## Outcome

This revision addresses the two places raised in the latest review: the paint background and the broken match where the child’s legs meet. The broad paint fields have been recomposed and their texture revised. The joint now has a torn shoulder, a thin irregular split and tapered splinters, replacing the previous thick divider and short star-like strokes.

The final artwork remains native vector geometry. The poster SVG and PDF contain no embedded raster image, live text or raster filters. The photograph and rendered PNGs are comparison evidence outside the vector artwork. The white reserve, headline, seal, footer, centennial captions and publication marks retain their Revision 3 construction. Only the paint layer and the small broken joint change.

## What the overlay revealed

### 1. The crack was a structural drawing problem

The previous figure joined the torso to the legs with a thick diagonal divider from roughly (345.5,776) to (337,792). A few fine strokes were placed over it. In the source photograph, that area is an irregular break: a short shoulder projects from the right-hand rail, a narrow curving seam passes into the lower junction, and small pointed splinters rise from the crotch. Pale negative spaces separate the pieces.

The correction removes the local divider and reconstructs those three features as independently editable ink shapes. A small paper-coloured cutout opens the gap. The long shafts retain their existing coordinates. The first development patch used clipped replacement rails; close inspection found hairline antialias seams, so that method was discarded. The final component has no clipping and changes only the local internal junction.

At the principal dark-ink threshold, the small fracture/splinter region’s mean symmetric edge distance changes from **{f['v3']['mean_symmetric_edge_distance']:.2f} to {f['v4']['mean_symmetric_edge_distance']:.2f} normalized pixels**. Its ink-area overlap changes from **{f['v3']['iou']:.2%} to {f['v4']['iou']:.2%}**. In the wider local-joint box, overlap changes from **{loc['v3']['iou']:.2%} to {loc['v4']['iou']:.2%}**. These measurements support the observed improvement but do not turn a blurred photograph into certain original contours.

### 2. The paint needed its large shapes corrected

The central orange field was not simply missing grain. Its middle-right edge withdrew too far inward, by around 20–40 normalized pixels at several diagnostic rows. The lower spine extended too far left by roughly 25–40 pixels, creating an overly broad, lumpy column. Moving the whole field would have displaced its relatively stable right edge; the useful correction was to reshape it locally.

The upper-left orange block was reasonably placed, but its lower stepped continuation was too narrow. The right yellow band also had too little broad warm coverage. These spatial differences remain visible after smoothing and therefore cannot be explained only by camera blur or tiny print grain. The initial independent audit, coordinates and diagnostic images are retained in `review/paint_audit/`.

### 3. Texture direction mattered more than adding more speckles

The previous paint beneath the legs contained repeated, high-contrast horizontal fragments. The photographed area has irregular upright remnants, overlapping deposits, quiet gaps and a smaller number of transverse scrapes. Along the right edge, narrow aligned rails similarly made the texture look generated.

The new material pass replaces those repeated motifs with authored paint pulls, irregular residual deposits and localized dragged or rubbed marks. Yellow-field marks are distributed regionally, rather than changing every yellow pixel to a warmer colour. The first structure-and-colour draft improved numerical fit but looked too flat; it was revised after visual review. The final paint remains a reconstruction of material appearance, with fine grain and some small deposits still interpreted.

## Fixed-reference paint measurements

Both versions use the same photograph registration and the same **698,156 eligible paint pixels**. The mask is retained from Revision 2, including its interior margin and exclusions. The raw RGB residual changes from **{a['mean_absolute_rgb_error']:.2f} to {b['mean_absolute_rgb_error']:.2f} levels per channel**. Broad orange-field overlap changes from **{a['broad_orange_iou']:.2%} to {b['broad_orange_iou']:.2%}**.

| Region | V3 RGB residual | V4 RGB residual | V3 orange overlap | V4 orange overlap |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Lower RGB residual indicates closer average appearance under this fixed comparison; higher orange overlap indicates closer broad field placement. The quiet-yellow region may contain very little orange, so its orange-overlap value is a poor general texture measure. Regional boxes overlap; their sample counts must not be added.

**The regional outcome is mixed.** In the lower paint/scumble box, orange-field overlap changes from {paint['regions']['Lower paint / scumbles']['previous']['broad_orange_iou']:.2%} to {paint['regions']['Lower paint / scumbles']['revised']['broad_orange_iou']:.2%}, despite a lower RGB residual. In the right band, orange overlap changes from {paint['regions']['Right paint band']['previous']['broad_orange_iou']:.2%} to {paint['regions']['Right paint band']['revised']['broad_orange_iou']:.2%}; the very low values concern the strongest orange deposits, which occupy only a small part of that predominantly yellow/amber region. Improved average warmth and removal of repeated motifs have not solved the exact placement of those stronger marks. The tables retain these regressions explicitly.

The next useful paint corrections are therefore specific: the lower belt needs finer, less upright remnants at the photographed locations; the right band needs its strongest orange gestures better placed; the broken red spur above the central block, roughly x485–535/y250–325, remains too simplified. The upper-left shoulder and some sparse yellow-field scrapes also remain interpreted. These are visible construction differences, beyond the unavoidable uncertainty in microscopic grain.

The additional masked, smoothed RGB residuals are **{a['masked_smooth_rgb_error_sigma_8']:.2f} → {b['masked_smooth_rgb_error_sigma_8']:.2f}** at sigma 8 pixels and **{a['masked_smooth_rgb_error_sigma_24']:.2f} → {b['masked_smooth_rgb_error_sigma_24']:.2f}** at sigma 24 pixels. These help inspect broad colour/placement separately from high-frequency grain. The full regional values are in `review/Paint_Measurements.json`.

The photograph is used for both visual design fitting and evaluation, so these are **fit residuals**, not held-out validation. No value is a whole-poster accuracy percentage or a calibrated pigment measurement. A numerically improved paint field can still look too regular; the enlarged comparisons and final visual audit remain essential evidence.

## Overlay method

The established perspective transform maps the supplied photograph to an estimated 1000 × 1400 reference plane. The source corners and transformation are preserved in the package. Neither registration nor paint-mask selection was changed to improve this revision’s scores.

For paint, the fixed mask begins with photo pixels having R > 135, B < 105 and RGB range > 75. It applies an eight-pixel interior margin and fixed exclusions for the top captions, footer, main headline and seal. Broad orange classification uses a Gaussian-smoothed ratio G / max(R,1), sigma 6 pixels, with a threshold of 0.50. In `BCFS_Paint_Overlay.png`, **teal marks orange present in the photograph only**, and **magenta marks orange present in the vector only**. Greyed areas either agree under that classification or are excluded; the overlay does not rate their fine texture.

For smoothed RGB residuals, normalized convolution uses only the eligible paint mask before smoothing. This avoids spreading the photograph’s white reserve and black lettering into the paint comparison. Sigma 8 and 24 are diagnostic scales in the normalized plane.

For the crack, dark ink is classified using max(R,G,B) < 125. The context box is x307–372, y758–826; the local-joint box is x320–354, y763–804; the fracture/splinter box is x325–345, y766–799. Identical boxes and thresholds are used for both versions. The joint overlay uses **teal for missing ink** and **magenta for excess ink**. Its pixels are deliberately enlarged without smoothing so the diagnostic cells remain visible.

### Crack threshold sensitivity

| Dark-ink threshold | V3 fracture IoU | V4 fracture IoU | V3 mean edge distance | V4 mean edge distance |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(sensitivity)}

The same direction of improvement across these fixed thresholds is more persuasive than choosing a single favourable threshold. Remaining tiny differences can reflect wear, camera softness, compression, resampling, registration or imperfect reconstruction. Geometry in the final artwork is manually authored; photographic masks and contours do not generate its paths.

## Review and editing

Start with `BCFS_Child_Crack_Details.png` to inspect the structural repair, and `BCFS_Child_Crack_Overlay.png` for its local ink diagnostic. The paint overview is `BCFS_Paint_Overlay.png`; `BCFS_Paint_Details.png` provides matching enlarged paint crops. `BCFS_Reconstruction_Comparison.png` shows the full photograph, V3 and V4 side by side.

`BCFS_Interactive_Review.html` is self-contained. It includes V3, V4 textured and V4 clean artwork, wipe/blend, paint and crack diagnostics, photo/vector-only views, and focus controls with up to 1200% of fit zoom. The clean edition shares the revised drawing; its diagnostic modes explicitly show the textured V4 paint and the common crack. Embedded SVG identity and JavaScript syntax were checked. Browser interaction was not exercised in this environment, so the static boards remain the directly inspected comparison.

The final artwork has separate layers for paint, white reserve, matchstick illustration, headline, seal, footer, centennial captions and publication marks. `BCFS_Child_Crack.svg` is the local repair component: it includes the paper-coloured cutout and belongs above the base figure with its obsolete hip-star stroke removed. The full master already applies it correctly. Paint, white reserve and lettering remain independently editable.

## Remaining priorities and limits

1. **Specific paint deposits and gestures:** the lower belt's orange placement and the right band's strongest orange marks still need work, as the regional regressions above show. The upper-central broken red spur and upper-left shoulder remain simplified. Irregular dry edges, small translucent deposits and worn pigment also differ. Further refinement should target recognizable medium-scale strokes and quiet gaps.
2. **Source limitations:** the supplied image includes photographic softness, wear, compression and a partly cropped paper edge. An exact physical print boundary, ink palette and concealed paint cannot be established from it.
3. **Small historical details:** the seal uses fitted URW Bookman Demi outlines as a visual substitute; the historical typeface is unverified. Fine emblem details and the apparent “J.J. ANDRE” signature reading and attribution remain approximate.
4. **Print preparation:** the 5:7 artboard is an estimated comparison plane. The PDF is scalable vector artwork; it has no printer-specific colour profile or bleed specification. Original physical dimensions and calibrated colours are unverified.

The earlier white-edge work is retained, not rescored as a new improvement in this revision. Its reports and fixed-mask measurements remain available in the historical review folders.

## Reproducibility and validation

`source/rebuild_poster.py` assembles the final components without reading a photograph or mask. `source/crack_joint.py` regenerates the local manually authored break. `source/paint-source/` contains the paint construction code; its synthetic deposition fields originate from authored geometry rather than extracted photo contours. Final component SVGs are supplied so ordinary vector editing requires no Python.

`source/analyze_revision4.py` is the portable fixed-reference analysis entry point. `source/build_review_html.py` rebuilds the offline viewer from those diagnostics. Historical analysis scripts are retained separately for provenance.

`review/Vector_Validation.json` records native-vector checks, unchanged-layer checks, the one-page PDF’s lack of bitmap images, and viewer asset/syntax checks. `review/Source_Rebuild_Check.json` records an isolated regeneration from the packaged final components. Review PNGs and the supplied photograph are raster evidence; they are not embedded in the vector master or PDF.
'''

def readme(paint,joint):
 a=paint['regions']['All eligible paint']['previous'];b=paint['regions']['All eligible paint']['revised']
 return f'''# BC Forest Service — MATCHES ARE NOT FOR CHILDREN!!

## Revision 4: paint and broken match

The paint background has been recomposed and the child’s broken hip junction reconstructed. The central orange column, lower paint remnants and warm yellow-field marks receive this pass; the crack now has a torn shoulder, irregular thin split and tapered splinters. White reserve, headline, seal and supporting lettering retain their earlier construction.

The SVG and PDF remain native vector artwork with no embedded bitmap, live text or raster filter. The geometry is deliberately constructed; the photograph is used for visual reference and diagnostic masks, not automatic contour tracing.

## Start here

| File | Purpose |
| --- | --- |
| `BCFS_Matches_Reconstructed.svg` | Complete current textured poster; named editable layers |
| `BCFS_Matches_Clean.svg` | Same drawing and white reserve with simplified paint fields |
| `BCFS_Matches_Reconstructed.pdf` | One-page scalable vector PDF |
| `BCFS_Matches_Preview.png` | 2000 × 2800 raster preview |
| `BCFS_Interactive_Review.html` | Offline V3/V4 wipe, blend, paint/crack overlays and zoom |
| `BCFS_Reconstruction_Comparison.png` | Photograph, V3 and V4 full-poster comparison |
| `BCFS_Paint_Overlay.png` | Broad orange-field placement diagnostic |
| `BCFS_Paint_Details.png` | Matching enlarged paint crops |
| `BCFS_Child_Crack_Details.png` | Photo / V3 / V4 broken-joint comparison |
| `BCFS_Child_Crack_Overlay.png` | Local ink mismatch overlay |
| `BCFS_Paint_Background.svg` | Separately editable revised paint |
| `BCFS_Child_Crack.svg` | Local broken-joint component with paper-coloured cutout |
| `BCFS_Matchstick_Illustration.svg` | Complete updated matchstick drawing |
| `BCFS_White_Reserve.svg` | Retained Revision 3 pale reserve |
| `BCFS_White_Edge_Residue.svg` | Retained sparse pigment deposits inside reserve |
| `BCFS_Headline.svg`, `BCFS_Forest_Service_Oval.svg` | Separate existing lettering and emblem |
| `review/Revision_4_Report.md` | Findings, method, measurements and remaining limits |
| `review/Paint_Measurements.json`, `review/Joint_Measurements.json` | Current fixed-reference numerical evidence |
| `review/history/` | Historical reports, vectors and comparison boards |
| `source/` | Current assembly, editable construction sources and supplied photograph |

## How to read the diagnostics

Paint analysis retains the earlier mask of 698,156 eligible pixels. Broad orange-field overlap changes from {a['broad_orange_iou']:.2%} to {b['broad_orange_iou']:.2%}; raw RGB fit residual changes from {a['mean_absolute_rgb_error']:.2f} to {b['mean_absolute_rgb_error']:.2f} levels per channel. These are photo-fitting diagnostics, not whole-poster accuracy or authenticity scores. Paint grain is reviewed visually as well.

The regional result is mixed: the lower scumble and right-band orange-placement scores regress even while average RGB residuals improve. The exact placement of those stronger deposits, the upper-central broken red spur and some thin scrapes remain refinement targets. The report keeps those limitations explicit.

Teal means a classified orange/ink area exists in the photograph only; magenta means it exists in the vector only. Paint and ink overlays use different explicit masks. The crack overlay is limited to its small context box. The report contains fixed threshold sensitivity and wider joint context results.

The comparison plane is estimated at 1000 × 1400 pixels. Original physical dimensions, calibrated inks, the historical seal typeface and signature attribution remain unverified. The PDF canvas has no bleed or printer-specific profile. Fine grain, transparent pigment and concealed details are still interpreted.

## Rebuild the delivered master

The finished SVG needs no fonts or Python to open. To regenerate it from the included final components:

```bash
python3 -m pip install -r source/requirements.txt
python3 source/crack_joint.py
python3 source/rebuild_poster.py
```

The builder reads `paint_v4.svg`, `paint_v4_clean.svg`, the retained `reserves_v3.svg`, `edge_residue.svg`, `emblem_v2.svg`, `signature_v2.svg` and the custom headline construction. It does not read the photograph. DejaVu Sans Bold and DejaVu Serif Bold are used to outline tiny supporting captions; their paths are declared in the builder. Save direct SVG edits before regeneration, which overwrites the master files.

The more expensive paint construction is in `source/paint-source/`; final component files are already supplied. The local cracked-junction component is applied after the base figure and replaces the removed old hip-star strokes. Existing reserve construction sources remain available for editing.

To export and reproduce the current analysis:

```bash
inkscape BCFS_Matches_Reconstructed.svg --export-type=png --export-width=2000 --export-filename=BCFS_Matches_Preview.png
inkscape BCFS_Matches_Reconstructed.svg --export-type=pdf --export-filename=BCFS_Matches_Reconstructed.pdf
python3 source/analyze_revision4.py
python3 source/build_review_html.py
```

Analysis reads the retained reference photograph, unchanged fixed paint mask and immutable V3 artwork from this package. The HTML includes every image and SVG asset; download it and open it locally. Embedded asset identity and JavaScript syntax were checked, but browser interaction was not exercised in this environment.

Current checks are recorded in `review/Vector_Validation.json` and `review/Source_Rebuild_Check.json`. Earlier white-edge reports are historical; no new white-contour improvement is claimed by Revision 4.
'''

def main():
 required=[OUT/'BCFS_Matches_Reconstructed.svg',OUT/'BCFS_Matches_Clean.svg',OUT/'BCFS_Matches_Reconstructed.pdf',OUT/'BCFS_Matches_Preview.png',
           OUT/'BCFS_Interactive_Review.html',REV/'root-analysis/Paint_Measurements.json',REV/'root-analysis/joint-metrics.json',REV/'paint_v4.svg',REV/'paint_v4_clean.svg',REV/'crack_joint.py',REV/'crack_joint.svg']
 for p in required:assert p.is_file(),p
 paint=json.loads((REV/'root-analysis/Paint_Measurements.json').read_text());joint=json.loads((REV/'root-analysis/joint-metrics.json').read_text())
 # Export derivatives from the current master here, eliminating stale V3 PDF
 # or preview files as possible packaging inputs.
 subprocess.run(['inkscape',str(OUT/'BCFS_Matches_Reconstructed.svg'),'--export-type=png','--export-width=2000','--export-filename='+str(OUT/'BCFS_Matches_Preview.png')],check=True,capture_output=True)
 subprocess.run(['inkscape',str(OUT/'BCFS_Matches_Reconstructed.svg'),'--export-type=pdf','--export-filename='+str(OUT/'BCFS_Matches_Reconstructed.pdf')],check=True,capture_output=True)
 for d in [REVIEW,SOURCE,HISTORY,DIAG]:d.mkdir(parents=True,exist_ok=True)
 for name in ['README.md','BCFS_Matches_Reconstructed.svg','BCFS_Matches_Clean.svg','BCFS_Matches_Preview.png','BCFS_Paint_Background.svg','BCFS_Matchstick_Illustration.svg','BCFS_White_Edge_Details.png','BCFS_White_Edge_Overlay.png','BCFS_Contour_Refinement.png']:
  cp(PRIOR/name,HISTORY/name)
 for name in ['Revision_3_Report.md','White_Edge_Measurements.json','Vector_Validation.json','Source_Rebuild_Check.json','Main_Contour_Sensitivity.json']:
  p=PRIOR/'review'/name
  if p.exists():cp(p,HISTORY/name)
 # Stale contour-only boards are retained in history, rather than displayed
 # beside current full-poster paint proof as if they were new Revision 4 views.
 for name in ['BCFS_White_Edge_Details.png','BCFS_White_Edge_Overlay.png','BCFS_Contour_Refinement.png']:
  p=OUT/name
  if p.exists():p.unlink()
 cp(REV/'root-analysis/Paint_Measurements.json',REVIEW/'Paint_Measurements.json')
 cp(REV/'root-analysis/joint-metrics.json',REVIEW/'Joint_Measurements.json')
 cp(OUT/'BCFS_Paint_Overlay.png',REVIEW/'BCFS_Alignment_Review.png')
 cp(ROOT/'work/reference-rectified.png',REVIEW/'Reference_Perspective_Normalized.png')
 cp(ROOT/'work/rectification.json',REVIEW/'Reference_Registration.json')
 for p in (REV/'root-analysis').glob('*'):
  if p.suffix in ['.json','.png'] and not p.name.endswith('-final-proof.png'):cp(p,DIAG/p.name)
 packaged_joint_notes='''> Package location note: the inventory and worktree paths below describe the isolated joint development. Its listed PNG proofs and reference mask are preserved in `review/joint_review/`, and its QA script is `source/analysis_records/crack_joint_qa.py`. The current paint-integrated proofs are `BCFS_Child_Crack_Details.png` and `BCFS_Child_Crack_Overlay.png` at the package root. Final-master measurements are in `review/Joint_Measurements.json`; `source/analyze_revision4.py` is their portable regeneration entry point. The normalized photo is `review/Reference_Perspective_Normalized.png`, and the supplied detail crop is `source/Crack_Reference_Crop.png`.

'''+(REV/'crack_joint_notes.md').read_text()
 (REVIEW/'joint_review').mkdir(exist_ok=True)
 (REVIEW/'joint_review/crack_joint_notes.md').write_text(packaged_joint_notes)
 for p in (REV/'joint-analysis').glob('*'):
  if p.suffix in ['.md','.json','.png']:cp(p,REVIEW/'joint_review'/p.name)
 for dirname,subdir in [('paint-audit','paint_audit'),('paint-analysis','paint_review')]:
  for p in (REV/dirname).glob('*'):
   current_evidence=(dirname=='paint-audit' and not re.match(r'0[4-9]-draft',p.name)) or p.name.startswith('final-') or p.name=='baseline-roi-colours.json'
   if p.is_file() and p.suffix in ['.md','.json','.png'] and current_evidence:cp(p,REVIEW/subdir/p.name)
 for p in REV.glob('paint_v4*'):
  if p.suffix in ['.md','.json']:cp(p,REVIEW/'paint_review'/p.name)
 cp(ROOT/'work/rebuild_poster.py',SOURCE/'rebuild_poster.py')
 for name in ['paint_v4.svg','paint_v4_clean.svg','crack_joint.py','crack_joint.svg']:
  cp(REV/name,SOURCE/name)
 (SOURCE/'crack_joint_notes.md').write_text(packaged_joint_notes)
 crop=ROOT/'upload'/'Screenshot 2026-11-20 at 6.26.59\u202fPM.png'
 if crop.exists():cp(crop,SOURCE/'Crack_Reference_Crop.png')
 for p in (REV/'paint-source').rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:
   if p.name.startswith('analyze_'):cp(p,SOURCE/'analysis_records/paint'/p.name)
   else:cp(p,SOURCE/'paint-source'/p.relative_to(REV/'paint-source'))
 for name in ['crack_joint_qa.py','package_revision4.py']:
  cp(REV/name,SOURCE/'analysis_records'/name)
 # Keep the previous white-edge analyzer as provenance; it is not the current
 # entry point and its outputs refer to the earlier V2/V3 comparison.
 if (SOURCE/'analyze_white_edges.py').exists():cp(SOURCE/'analyze_white_edges.py',SOURCE/'analysis_records/analyze_white_edges_revision3.py');(SOURCE/'analyze_white_edges.py').unlink()
 (SOURCE/'analyze_revision4.py').write_text(portable_analysis())
 (SOURCE/'build_review_html.py').write_text(portable_review())
 (OUT/'README.md').write_text(readme(paint,joint))
 (REVIEW/'Revision_4_Report.md').write_text(report(paint,joint))
 validation=validate();(REVIEW/'Vector_Validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 # The assembly is rebuilt from a separate copy, without its original work tree.
 repro=REV/'source-rebuild-check'
 if repro.exists():shutil.rmtree(repro)
 shutil.copytree(SOURCE,repro/'source',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 subprocess.run(['python3',str(repro/'source/crack_joint.py')],check=True,capture_output=True)
 subprocess.run(['python3',str(repro/'source/rebuild_poster.py')],check=True,capture_output=True)
 hashes={}
 for name in ['BCFS_Matches_Reconstructed.svg','BCFS_Matches_Clean.svg','BCFS_Paint_Background.svg','BCFS_Matchstick_Illustration.svg','BCFS_White_Reserve.svg','BCFS_White_Edge_Residue.svg','BCFS_Child_Crack.svg']:
  x=(OUT/name).read_bytes();y=(repro/name).read_bytes();assert x==y,'Rebuild differs: '+name
  hashes[name]=hashlib.sha256(x).hexdigest()
 (REVIEW/'Source_Rebuild_Check.json').write_text(json.dumps({'revision':4,'isolated_final_component_assembly':'byte-identical','files_sha256':hashes,'paint_synthesis_regenerated_in_this_check':False},indent=2)+'\n')
 # A single new archive replaces the logical current package after completion.
 final_zip=ROOT/'output/BCFS_Vector_Reconstruction.zip';staging=ROOT/'output/BCFS_Vector_Reconstruction.building.zip'
 with zipfile.ZipFile(staging,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('.') and p.suffix!='.pyc':z.write(p,'BC_Forest_Service_Matches/'+str(p.relative_to(OUT)))
 with zipfile.ZipFile(staging) as z:assert z.testzip() is None;count=len(z.infolist())
 staging.replace(final_zip)
 print(json.dumps({'archive':str(final_zip),'archive_bytes':final_zip.stat().st_size,'files':count,'native_vector_validated':True,'source_assembly_byte_identical':True},indent=2))

if __name__=='__main__':main()
