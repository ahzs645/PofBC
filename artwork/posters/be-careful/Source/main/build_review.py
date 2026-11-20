"""Compare rendered vector artwork to the supplied scan; never derive paths."""
from pathlib import Path
import base64, json, html, xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage as nd
from PIL import Image, ImageDraw, ImageFont
from build_package import R,E,BASE,NS,TAG,render,root_svg,write

SOURCE=next(p for p in [
 R.parent/'upload/B2-02_be_careful_decal_1960(1).png',
 R.parent/'Reference/Original_scan.png'] if p.exists())

def uri(p,mime='image/png'):
 return 'data:'+mime+';base64,'+base64.b64encode(Path(p).read_bytes()).decode()

def font(size,bold=False):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)

def iou(a,b):
 return float(np.count_nonzero(a&b)/np.count_nonzero(a|b))

def analysis():
 source=np.array(Image.open(SOURCE).convert('RGB'))
 vector=np.array(Image.open(R/'analysis/master_1234.png').convert('RGB'))
 sg=source.mean(axis=2);vg=vector.mean(axis=2)
 s=sg<180;v=vg<180
 metrics={'method':{'alignment':'Original 1234 x 909 coordinates; no registration transform or warping',
  'threshold':'Unweighted mean RGB below 180 of 255 is ink; all outputs rendered at original resolution',
  'iou':'Intersection area divided by union area of two binary masks',
  'limitation':'Whole ink overlap is dominated by solid fill; glyph scores and boundary distances are reported separately. '
  'These measures assess this scan, not historical font identification or authentic print colour.'},
  'whole_ink_iou':iou(s,v),'source_ink_pixels':int(s.sum()),'vector_ink_pixels':int(v.sum()),
  'different_pixels':int(np.count_nonzero(s^v))}
 edge_s=s^nd.binary_erosion(s);edge_v=v^nd.binary_erosion(v)
 distances=np.r_[nd.distance_transform_edt(~edge_s)[edge_v],nd.distance_transform_edt(~edge_v)[edge_s]]
 metrics['boundary_distance_pixels']={
  'median':float(np.median(distances)),'95th_percentile':float(np.percentile(distances,95)),
  'within_2_pixels_fraction':float(np.mean(distances<=2))}
 metrics['threshold_sensitivity']={str(t):iou(sg<t,vg<t) for t in [160,170,180,190,200]}
 # C is an isolated white component in both source and render, so the internal
 # AREFUL lettering is excluded without modifying either outline.
 sl,_=nd.label(~s);vl,_=nd.label(~v)
 metrics['large_C_white_shape_iou']=iou(sl==sl[490,650],vl==vl[490,650])
 regions={'large_B_region':(162,266,540,675),
  'slogan_white_lettering':(48,706,1060,826),'service_signature_white_lettering':(190,825,890,875),
  'small_E':(540,422,593,529),'AREFUL':(698,426,1013,540)}
 metrics['white_regions']={}
 for name,(x0,y0,x1,y1) in regions.items():
  metrics['white_regions'][name]={'box':[x0,y0,x1,y1],
   'iou':iou(~s[y0:y1,x0:x1],~v[y0:y1,x0:x1])}
 metrics['artwork']={'paths':43,'editable_layers':5,'external_fonts':0,'embedded_raster_images':0,
  'scan_sampled_ink':'#525850','physical_original_dimensions':'Unknown'}
 (E/'Reconstruction_measurements.json').write_text(json.dumps(metrics,indent=2))
 # A three-colour geometric difference map. It is a review image only.
 diff=np.full((*s.shape,3),255,dtype=np.uint8)
 diff[s&v]=(67,73,69);diff[s&~v]=(0,153,181);diff[v&~s]=(224,36,113)
 Image.fromarray(diff).save(R/'analysis/difference_final.png')
 board=Image.new('RGB',(1500,1290),'white');d=ImageDraw.Draw(board)
 d.text((48,32),'Reconstruction / overlap check',font=font(36,True),fill='#17261d')
 d.text((48,82),'Original coordinates  |  Cyan: scan only  |  Magenta: vector only  |  Dark: agreement',font=font(20),fill='#525d55')
 d.text((48,117),f"Ink overlap: {metrics['whole_ink_iou']*100:.2f}%  |  95% of boundary samples within {np.percentile(distances,95):.1f} source pixels",font=font(20),fill='#525d55')
 im=Image.fromarray(diff);im.thumbnail((1404,1040),Image.Resampling.LANCZOS);board.paste(im,((1500-im.width)//2,174))
 d.text((48,1238),'Thin coloured edges show remaining geometric differences; scan texture is deliberately removed.',font=font(20),fill='#525d55')
 board.save(E/f'{BASE}_Overlap.png')
 return metrics

def review_html(m):
 pct=lambda f:f'{100*f:.2f}%'
 template='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BC Forest Service / 1960 vector reconstruction</title>
<style>
:root{color-scheme:light;--ink:#17261d;--muted:#5e6b62;--line:#dce1da;--paper:#f5f6f1;--cyan:#0099b5;--pink:#e02471}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,-apple-system,sans-serif}
main{max-width:1180px;margin:0 auto;padding:48px 24px 70px}.eyebrow{letter-spacing:.14em;text-transform:uppercase;font-size:12px;font-weight:700;color:var(--muted)}
h1{font-size:clamp(30px,4.5vw,54px);line-height:1.12;letter-spacing:-.04em;margin:12px 0 18px;max-width:880px}
h2{font-size:25px;letter-spacing:-.02em;margin:36px 0 12px}p{max-width:920px}a{color:#2c6545}header p{color:var(--muted);font-size:18px}
.facts{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0}.fact{border:1px solid var(--line);background:white;padding:16px 20px;border-radius:10px}.fact strong{display:block;font-size:28px}.fact span{color:var(--muted);font-size:13px}
.panel{border:1px solid var(--line);border-radius:12px;background:white;overflow:hidden}.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:16px;border-bottom:1px solid var(--line)}
button,select{font:inherit;border:1px solid #c9d2c9;border-radius:6px;background:white;color:var(--ink);padding:8px 12px;cursor:pointer}button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:white}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #0099b5;outline-offset:3px}
label.region{margin-left:auto;font-size:14px}.stage{width:100%;display:block;background:white;max-height:860px}.slider{display:flex;align-items:center;gap:16px;padding:15px 20px;background:#fafbf8;font-size:14px}input[type=range]{width:100%;accent-color:#31523c}output{min-width:45px;font-variant-numeric:tabular-nums}.caption{color:var(--muted);font-size:14px;margin:12px 0 0}.legend{display:flex;gap:24px;flex-wrap:wrap;font-size:14px}.swatch{display:inline-block;width:13px;height:13px;border-radius:3px;margin-right:7px}
table{border-collapse:collapse;width:100%;margin-top:16px;background:white;border:1px solid var(--line)}td,th{text-align:left;padding:13px 16px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}td:last-child{font-variant-numeric:tabular-nums}.two{display:grid;grid-template-columns:1fr 1fr;gap:36px}.note{padding:18px 22px;border-left:3px solid #8ca28f;background:#edf1e8}footer{font-size:13px;color:var(--muted);border-top:1px solid var(--line);margin-top:40px;padding-top:20px}li{margin:8px 0}@media(max-width:650px){main{padding:28px 14px}.facts{grid-template-columns:1fr}.fact strong{font-size:25px}.two{grid-template-columns:1fr;gap:0}.toolbar{gap:6px;padding:10px}button{font-size:13px;padding:7px 9px}label.region{margin-left:0;width:100%}td,th{padding:10px;font-size:14px}}
@media print{main{padding:0}.toolbar,.slider{display:none}.panel{break-inside:avoid}h2{break-after:avoid}.facts{grid-template-columns:repeat(3,1fr)}a{color:inherit}.stage{max-height:640px}}
</style></head><body><main>
<header><div class="eyebrow">BC Forest Service · Historical artwork</div><h1>“Be Careful”<br>Vector reconstruction, 1960</h1><p>Rebuilt as deliberate Bézier geometry and individually constructed lettering. The original asymmetry, tree skyline, flame forks and word spacing are retained, while scan grain and worn print edges are removed.</p></header>
<div class="facts"><div class="fact"><strong>43 paths</strong><span>Five named, editable SVG layers</span></div><div class="fact"><strong>@@OVERLAP@@</strong><span>Thresholded foreground overlap</span></div><div class="fact"><strong>No font dependency</strong><span>All 42 letters are outlined shapes</span></div></div>
<h2>Inspect the original and reconstruction</h2><p>Move the slider: vector on the left, original scan on the right. Choose a detail to examine the geometry at a larger scale.</p>
<div class="panel"><div class="toolbar"><button data-mode="wipe" aria-pressed="true">Compare</button><button data-mode="vector" aria-pressed="false">Vector</button><button data-mode="original" aria-pressed="false">Original</button><button data-mode="difference" aria-pressed="false">Difference</button><label class="region">Detail <select id="region"><option value="full">Full decal</option><option value="B">Large B</option><option value="C">Large C</option><option value="slogan">Slogan</option><option value="signature">Service signature</option><option value="flames">Flame tips</option><option value="trees">Forest skyline</option></select></label></div>
<svg id="stage" class="stage" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1234 909" role="img" aria-label="Interactive comparison of the original decal and reconstructed vector">
<defs><clipPath id="wipe"><rect id="clipRect" x="0" y="0" width="617" height="909"/></clipPath></defs>
<rect x="0" y="0" width="1234" height="909" fill="white"/><image id="original" width="1234" height="909" href="@@SOURCE@@"/>
<g id="vectorLayer" clip-path="url(#wipe)"><rect width="1234" height="909" fill="white"/><image width="1234" height="909" href="@@VECTOR@@"/></g>
<image id="difference" width="1234" height="909" href="@@DIFF@@" visibility="hidden"/>
<line id="divider" x1="617" x2="617" y1="0" y2="909" stroke="#e02471" stroke-width="2" vector-effect="non-scaling-stroke"/>
</svg><div class="slider"><label for="range">Vector</label><input id="range" type="range" min="0" max="100" value="50" aria-label="Percentage of reconstruction visible"><output id="percent">50%</output><span>Original</span></div></div>
<p class="caption">The interactive vector is the same outlined artwork as the downloadable SVG. The scan and difference map are raster reference images only; they are not embedded in the SVG deliverables.</p>
<p class="legend"><span><i class="swatch" style="background:#434945"></i>Agreement</span><span><i class="swatch" style="background:#0099b5"></i>Scan only</span><span><i class="swatch" style="background:#e02471"></i>Vector only</span></p>
<h2>How closely does it align?</h2><table><thead><tr><th>Measurement</th><th>Result</th><th>Scope</th></tr></thead><tbody>
<tr><td>Complete ink shape</td><td>@@OVERLAP@@</td><td>All dark artwork, intersection over union</td></tr>
<tr><td>Large B region</td><td>@@B@@</td><td>White lettering within its original bounding region</td></tr>
<tr><td>Large C</td><td>@@C@@</td><td>Isolated white C; excludes AREFUL</td></tr>
<tr><td>PREVENT FOREST FIRES</td><td>@@SLOGAN@@</td><td>White slogan lettering</td></tr>
<tr><td>BC Forest Service</td><td>@@FOOTER@@</td><td>Small signature lettering</td></tr>
<tr><td>95th percentile boundary distance</td><td>@@DISTANCE@@ px</td><td>Distances in both directions at original resolution</td></tr>
</tbody></table>
<p class="caption">Measured at 1234 × 909 pixels, with mean RGB &lt; 180/255 classified as ink. No alignment warp is applied. The complete ink score is strongly influenced by solid areas; the lettering results expose smaller differences. Thin letterforms are sensitive to a one-pixel edge change. This is a reconstruction of the supplied scan, not a claim of an exact original printer’s master.</p>
<div class="two"><section><h2>Lettering decisions</h2><p><strong>Large initials:</strong> custom B and C with Albertus-like inscriptional structure. The scan does not confirm an exact named font, and the proportions are intentionally reconstructed individually.</p><p><strong>Condensed capitals:</strong> a reusable custom glyph set, retaining the bowed R leg, tiny A counter, narrow O, rounded corners and optical width differences. Alternate Gothic is a family-level comparison, not an identification.</p><p><strong>Small signature:</strong> individually drawn humanist forms, with asymmetric e/r/t details and the original baseline drift.</p></section>
<section><h2>Editing and production</h2><p><strong>Master SVG:</strong> forest/flames, large initials, upper small lettering, slogan and service signature are five named layers. Letters are editable as paths, not live text.</p><p><strong>Knockout SVG:</strong> one compound path, with genuinely transparent lettering and counters. Black and white variants and an EPS version are included in the package.</p><p><strong>Colour:</strong> #525850 is sampled from the scan. The original physical size and original ink specification are unknown; resize the vector for the intended use.</p></section></div>
<div class="note"><strong>Historical confirmation.</strong> The same forest/flame decal appears on printed page 5 of the BC Forest Service <em>Protection Bulletin</em>, No. 3, 1960, under “New Protection Decals.” It describes decals for vehicle windows and hard hats.</div>
<h2>Sources and construction record</h2><ul>
<li>The image you supplied: <em>B2-02_be_careful_decal_1960(1).png</em>, 1234 × 909 pixels.</li>
<li><a href="https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=21448">BC Forest Service Protection Bulletin, No. 3, 1960, p. 5</a> — historical identification.</li>
<li><a href="https://www.monotype.com/fonts/albertus-nova">Monotype: Albertus Nova / Albertus lineage</a> — font-family comparison.</li>
<li><a href="https://www.monotype.com/fonts/alternate-gothic">Monotype: Alternate Gothic</a> — condensed-lettering comparison.</li>
</ul><footer>Prepared 20 November 2026. The package includes source geometry, construction scripts, original scan, vector variants and measurement data. All visual reconstruction choices are explicit; no bitmap contour extraction or auto-trace stage is used.</footer>
</main><script>
const boxes={full:[0,0,1234,909],B:[150,250,400,435],C:[620,265,425,450],slogan:[40,695,1030,140],signature:[185,820,715,62],flames:[730,0,504,565],trees:[80,12,750,285]};
let mode='wipe';const $=s=>document.getElementById(s);
function update(){const b=boxes[$('region').value],t=+$('range').value/100,x=b[0]+b[2]*t;$('stage').setAttribute('viewBox',b.join(' '));$('stage').style.aspectRatio=b[2]+'/'+b[3];
const c=$('clipRect');c.setAttribute('x',mode==='vector'?0:b[0]);c.setAttribute('y',0);c.setAttribute('width',mode==='vector'?1234:b[2]*t);c.setAttribute('height',909);
$('vectorLayer').setAttribute('visibility',['wipe','vector'].includes(mode)?'visible':'hidden');$('difference').setAttribute('visibility',mode==='difference'?'visible':'hidden');
$('divider').setAttribute('visibility',mode==='wipe'?'visible':'hidden');$('divider').setAttribute('x1',x);$('divider').setAttribute('x2',x);$('divider').setAttribute('y1',b[1]);$('divider').setAttribute('y2',b[1]+b[3]);$('percent').value=Math.round(t*100)+'%';$('range').disabled=mode!=='wipe';}
document.querySelectorAll('button[data-mode]').forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.mode;document.querySelectorAll('button[data-mode]').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));update()}));
$('range').addEventListener('input',update);$('region').addEventListener('change',update);update();
</script></body></html>'''
 replacements={'@@OVERLAP@@':pct(m['whole_ink_iou']),'@@B@@':pct(m['white_regions']['large_B_region']['iou']),
  '@@C@@':pct(m['large_C_white_shape_iou']),'@@SLOGAN@@':pct(m['white_regions']['slogan_white_lettering']['iou']),
  '@@FOOTER@@':pct(m['white_regions']['service_signature_white_lettering']['iou']),
  '@@DISTANCE@@':f"{m['boundary_distance_pixels']['95th_percentile']:.2f}",
  '@@SOURCE@@':uri(SOURCE),'@@VECTOR@@':uri(E/f'{BASE}_Master.svg','image/svg+xml'),
  '@@DIFF@@':uri(R/'analysis/difference_final.png')}
 for key,value in replacements.items():template=template.replace(key,value)
 (E/f'{BASE}_Review.html').write_text(template)

def notes(m):
 text=f'''# BC Forest Service - Be Careful - 1960

## What this is

A deliberately reconstructed vector edition of the supplied decal. Geometry is manually authored from design landmarks, using line, quadratic and cubic Bezier segments. The lettering is constructed from reusable custom glyph masters and optical variants. No auto-trace, bitmap contour extraction or raster embedding is used in any SVG, PDF or EPS artwork.

## Files

- `{BASE}_Master.svg`: primary editable artwork. 43 paths in five named layers; white lettering over a scan-sampled green-grey silhouette; transparent outside the artwork.
- `{BASE}_Knockout.svg`: single-colour compound path with genuinely transparent lettering. This is useful when the substrate should show through.
- `{BASE}_Black.svg` and `{BASE}_White.svg`: knockout variants.
- `{BASE}_Print.pdf`: vector PDF. No embedded raster images. The page follows the SVG's 1234 x 909 canvas at the conventional 96 CSS pixels per inch; this is not a claim about the original decal's dimensions. Choose the intended print size.
- `{BASE}_Black.eps`: monochrome vector EPS.
- `{BASE}_Preview.png`: 2468-pixel-wide white-background preview.
- `{BASE}_Transparent.png`: 4096-pixel-wide transparent PNG of the knockout artwork.
- `{BASE}_Review.html`: self-contained, offline comparison with a wipe slider, detail views and a coloured difference map.
- `{BASE}_Overlap.png`: annotated overview of the geometric comparison.
- `Reconstruction_measurements.json`: exact measurement method and results.
- `Source/`: component SVGs and editable Python construction scripts.
- `Reference/Original_scan.png`: the supplied image, unchanged.

## Editable structure

1. Forest and flames
2. Large B and C
3. Be Careful small lettering
4. Prevent Forest Fires
5. BC Forest Service

Letters are outlined editable vector paths, not live text fields. No font installation is required. The construction scripts preserve the glyph masters, width/height placement, and semantically named silhouette sections for later refinement.

## Typography and reconstruction decisions

The large B and C have an Albertus-like inscriptional structure, but the scan does not establish a specific font, cut, weight or original setting. They are custom masters here. The narrow uppercase lettering is comparable to the Alternate Gothic / condensed sign-lettering tradition; its unusual R leg, A counter and individual widths are deliberately retained. The footer is reconstructed as small humanist lettering. No commercial font files or commercial font outlines are included.

The forest's irregular heights and branch rhythm, the transition into flames, the deep flame valleys, the angled base and the uneven lettering baseline are retained. Print grain, scratches and tiny scan-edge defects are deliberately omitted. The small signature remains the least securely determined portion because of its low source resolution.

Ink colour #525850 is the median sampled inside dark regions of the supplied scan, not a verified original ink or spot-colour specification. Original physical dimensions are unknown.

## Alignment checks

The comparison uses the original 1234 x 909 coordinate system with no affine or projective alignment, rescaling or local warping. Source and rendered artwork are classified as ink when unweighted mean RGB is below 180/255.

- Full ink-shape intersection over union: {m['whole_ink_iou']*100:.2f}%.
- Large B white region: {m['white_regions']['large_B_region']['iou']*100:.2f}%.
- Isolated large C white shape: {m['large_C_white_shape_iou']*100:.2f}%.
- Slogan white lettering: {m['white_regions']['slogan_white_lettering']['iou']*100:.2f}%.
- Small service signature white lettering: {m['white_regions']['service_signature_white_lettering']['iou']*100:.2f}%.
- Symmetric boundary distance, 95th percentile: {m['boundary_distance_pixels']['95th_percentile']:.2f} source pixels.

The full-shape score is dominated by solid areas and should not be read as a percentage of historical authenticity. Lettering metrics expose finer differences. A one-pixel edge change has a large effect on very small letters. Differences include intentional smoothing, original print irregularities and residual manual reconstruction differences.

## Historical and type references

- User-supplied scan: B2-02_be_careful_decal_1960(1).png.
- BC Forest Service, Protection Bulletin, No. 3 (1960), printed p. 5, New Protection Decals. The same design is pictured and the text describes decals for vehicle windows and hard hats: https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=21448
- Monotype, Albertus Nova / Albertus lineage, used as a family-level comparison: https://www.monotype.com/fonts/albertus-nova
- Monotype, Alternate Gothic, used as a condensed-lettering comparison: https://www.monotype.com/fonts/alternate-gothic

## Regenerating geometry

Python 3 is sufficient for the main lettering geometry. Inkscape is used to render and to calculate a vector-only Boolean difference for the knockout edition. Full export/review also uses FontTools, NumPy, SciPy, Pillow and Poppler. Fonts used for comparison-page labels are separate from the reconstructed artwork.

From the package directory:

```sh
python3 Source/silhouette/build_silhouette.py
python3 Source/lettering/build_lettering.py
python3 Source/main/draw_initials_footer.py
python3 Source/main/build_package.py
python3 Source/main/build_review.py
```

Rebuilt exports appear under `Source/exports/`. The scripts never use a raster image to generate an SVG path. The original scan is read only by the review/measurement script.

Prepared 20 November 2026.
'''
 (E/'README.md').write_text(text)

if __name__=='__main__':
 m=analysis();review_html(m);notes(m)
 print(json.dumps(m,indent=2))
