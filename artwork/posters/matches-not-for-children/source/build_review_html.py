#!/usr/bin/env python3
"""Self-contained photo/vector review with fixed-mask paint and local ink overlays."""
from pathlib import Path
import base64, html, json
ROOT=Path(__file__).resolve().parent.parent
REV=ROOT/'review'
OUT=ROOT
DIAG=ROOT/'review/diagnostics/revision4'
def url(p,mime):return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
def main():
 metrics=json.loads((DIAG/'Paint_Measurements.json').read_text())
 joint=json.loads((DIAG/'joint-metrics.json').read_text())
 assets={
 'photo':url(ROOT/'review/Reference_Perspective_Normalized.png','image/png'),
 'previous':url(ROOT/'review/history/revision3/BCFS_Matches_Reconstructed.svg','image/svg+xml'),
 'revised':url(OUT/'BCFS_Matches_Reconstructed.svg','image/svg+xml'),
 'clean':url(OUT/'BCFS_Matches_Clean.svg','image/svg+xml'),
 'paint_previous':url(DIAG/'paint-overlay-previous.png','image/png'),
 'paint_revised':url(DIAG/'paint-overlay-revised.png','image/png'),
 'ink_previous':url(DIAG/'ink-overlay-previous.png','image/png'),
 'ink_revised':url(DIAG/'ink-overlay-revised.png','image/png'),
 }
 rows=[]
 for name,vals in metrics['regions'].items():
  a,b=vals['previous'],vals['revised']
  f=lambda v:'—' if v is None else f'{v:.1%}'
  rows.append(f'<tr><th>{html.escape(name)}</th><td>{a["mean_absolute_rgb_error"]:.2f}</td><td>{b["mean_absolute_rgb_error"]:.2f}</td><td>{f(a["broad_orange_iou"])}</td><td>{f(b["broad_orange_iou"])}</td></tr>')
 a=metrics['regions']['All eligible paint']['previous'];b=metrics['regions']['All eligible paint']['revised']
 j=joint['thresholds']['125']['fracture_and_splinters']
 tokens={
 '@@ASSETS@@':json.dumps({k:v for k,v in assets.items() if k not in ['photo','revised']},separators=(',',':')),
 '@@PHOTO@@':assets['photo'],'@@REVISED@@':assets['revised'],
 '@@METRICS@@':json.dumps({'paint':metrics,'joint':joint},separators=(',',':')),
 '@@ROWS@@':'\n'.join(rows),
 '@@PAINT@@':f'{a["broad_orange_iou"]:.1%} → {b["broad_orange_iou"]:.1%}',
 '@@RGB@@':f'{a["mean_absolute_rgb_error"]:.2f} → {b["mean_absolute_rgb_error"]:.2f}',
 '@@CRACK@@':f'{j["v3"]["mean_symmetric_edge_distance"]:.2f} → {j["v4"]["mean_symmetric_edge_distance"]:.2f} px',
 }
 page=TEMPLATE
 for key,value in tokens.items():page=page.replace(key,value)
 assert '@@' not in page
 (OUT/'BCFS_Interactive_Review.html').write_text(page)
 print('Built offline Revision 4 review:',len(page),'characters')

TEMPLATE=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BC Forest Service · Revision 4 overlay review</title>
<style>
:root{--ink:#202a2b;--muted:#5c6966;--line:#d4dcd3;--accent:#225d56;--paper:#fafbf7;--teal:#00b6be;--magenta:#db228e;color-scheme:light}*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0;background:#edf0e8;color:var(--ink);font:16px/1.55 system-ui,sans-serif}main{max-width:1340px;margin:auto;padding:32px 28px 60px}h1,h2,h3,p{margin-top:0}h1{font-size:clamp(1.8rem,3vw,2.7rem);line-height:1.15;letter-spacing:-.035em;margin-bottom:14px}h2{font-size:1.3rem}h3{font-size:1rem;margin-bottom:7px}.eyebrow{font-size:.73rem;font-weight:800;letter-spacing:.14em;color:var(--accent);text-transform:uppercase;margin-bottom:10px}.intro{max-width:930px;color:var(--muted)}.card{background:var(--paper);border:1px solid var(--line);border-radius:15px;overflow:hidden;margin-bottom:24px}.controls{padding:18px 20px;border-bottom:1px solid var(--line)}.row{display:flex;align-items:end;gap:15px;flex-wrap:wrap}.field{display:flex;flex-direction:column;gap:6px}.field label,.group-label{font-size:.78rem;font-weight:750;color:var(--muted)}.group-label{display:block;margin-bottom:6px}.buttons{display:flex;gap:5px;flex-wrap:wrap}button,select{font:inherit;font-size:.87rem;background:white;color:var(--ink);padding:8px 12px;border:1px solid #bac6bd;border-radius:7px;min-height:39px}button{cursor:pointer}button:hover{background:#e5ede6}button[aria-pressed="true"]{background:var(--accent);color:white;border-color:var(--accent)}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #c28a14;outline-offset:3px}.slider{flex:1;min-width:250px}.slider-head{display:flex;justify-content:space-between;gap:14px;font-size:.82rem}input[type="range"]{width:100%;accent-color:var(--accent)}input:disabled{opacity:.4}.range-row{margin-top:17px;align-items:center}.focus{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:12px}.focus button{font-size:.78rem;min-height:32px;padding:5px 9px}.small{font-size:.82rem;color:var(--muted)}.legend{padding:11px 20px;background:white;border-bottom:1px solid var(--line);font-size:.83rem;display:flex;gap:12px 22px;flex-wrap:wrap}.swatch{display:inline-block;width:13px;height:13px;margin-right:7px;border-radius:3px;vertical-align:-2px}.teal{background:var(--teal)}.magenta{background:var(--magenta)}.viewport{height:76vh;min-height:420px;max-height:1050px;overflow:auto;background:#d5d9d0;overscroll-behavior:contain}.space{width:max-content;min-width:100%;min-height:100%;padding:20px;display:flex;align-items:center;justify-content:center}.stage{position:relative;flex:0 0 auto;width:min(500px,70vw);aspect-ratio:5/7;isolation:isolate;box-shadow:0 3px 18px #1e252530;background:#e7f3f2}.stage img{position:absolute;display:block;inset:0;width:100%;height:100%;user-select:none;max-width:none}.vector{clip-path:inset(0 0 0 50%)}.diagnostic{z-index:3}.divider{position:absolute;left:50%;top:0;bottom:0;width:2px;background:white;box-shadow:0 0 0 1px #253d3e50;z-index:4;pointer-events:none}.divider:after{content:"↔";position:absolute;top:50%;left:-15px;width:32px;height:32px;text-align:center;line-height:29px;background:white;color:#202a2b;border:1px solid #7c8d85;border-radius:50%;font-size:20px}.tag{position:absolute;top:10px;padding:3px 7px;border-radius:4px;color:white;background:#142e2cbd;font-size:11px;z-index:5;pointer-events:none}.tag-left{left:10px}.tag-right{right:10px}.viewer-footer{padding:12px 20px;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted);display:flex;gap:14px;justify-content:space-between;flex-wrap:wrap}#status{font-weight:700;color:var(--ink)}.section{padding:24px 26px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:20px 0}.stat{background:#edf3ec;border:1px solid #d5e2d2;border-radius:10px;padding:16px}.stat strong{display:block;font-size:1.4rem;color:#234d45}.stat span{font-size:.8rem}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:9px;margin-top:18px}table{width:100%;min-width:690px;border-collapse:collapse;text-align:left;font-size:.85rem}caption{text-align:left;padding:12px 14px;font-weight:700;background:#edf2eb}th,td{padding:10px 14px;border-top:1px solid var(--line)}thead th{font-size:.76rem;color:var(--muted);background:#f2f5ee}tbody th{font-weight:500}td{font-variant-numeric:tabular-nums}tbody tr:first-child{background:#edf3ec}.notes{display:grid;grid-template-columns:1fr 1fr;gap:28px}.notes p{font-size:.9rem}details{font-size:.84rem;color:var(--muted);margin-top:18px}summary{font-weight:700;cursor:pointer;color:var(--ink)}details p{margin:10px 0 0}noscript p{background:#fff5d7;padding:14px;border:1px solid #d9be6c;border-radius:8px}@media(max-width:700px){main{padding:20px 12px 40px}.controls,.section{padding:16px}.stats,.notes{grid-template-columns:1fr}.stats{gap:8px}.stat{padding:12px}.viewport{height:70vh;min-height:360px}.space{padding:12px}.viewer-footer,.legend{padding:12px 16px}}@media print{.controls,.legend,.viewer-footer{display:none!important}.viewport{height:auto;max-height:none;overflow:visible;min-height:0}.space{padding:0;width:100%;display:block}.stage{width:100%!important;max-width:700px;margin:auto}.card{break-inside:avoid}.section{padding:12px}main{padding:0}}
</style></head><body><main>
<header><p class="eyebrow">British Columbia Forest Service · Revision 4</p><h1>Paint &amp; broken-match overlay review</h1><p class="intro">Compare the registered photograph with the previous and revised vectors. Inspect the large paint fields, the texture beneath the legs, and the small split where the child’s legs meet. The overlays use the same registration and fixed masks for both revisions.</p></header>
<noscript><p>The static comparison shows the photograph on the left and Revision 4 on the right. Enable JavaScript to use the wipe, blend, diagnostic and zoom controls. All images and measurements are embedded.</p></noscript>
<section class="card" aria-label="Interactive overlay comparison"><div class="controls"><div class="row">
<div class="field"><label for="edition">Artwork</label><select id="edition"><option value="revised">Revision 4 · textured</option><option value="previous">Revision 3</option><option value="clean">Revision 4 · clean paint</option></select></div>
<div><span id="mode-label" class="group-label">Comparison</span><div class="buttons" role="group" aria-labelledby="mode-label"><button type="button" data-mode="wipe" aria-pressed="true">Wipe</button><button type="button" data-mode="blend" aria-pressed="false">Blend</button><button type="button" data-mode="paint" aria-pressed="false">Paint overlay</button><button type="button" data-mode="ink" aria-pressed="false">Crack overlay</button></div></div>
<div class="field"><label for="zoom">Zoom</label><select id="zoom"><option value="1">Fit poster</option><option value="2">200% of fit</option><option value="3">300% of fit</option><option value="4">400% of fit</option><option value="6">600% of fit</option><option value="8">800% of fit</option><option value="12">1200% of fit</option></select></div></div>
<div class="row range-row"><div class="slider"><div class="slider-head"><label for="amount" id="range-label">Wipe position</label><output id="range-value" for="amount">Photo 50% · vector 50%</output></div><input id="amount" type="range" min="0" max="100" step="1" value="50"></div><div class="buttons" role="group" aria-label="View one source"><button type="button" data-mode="photo" aria-pressed="false">Photo only</button><button type="button" data-mode="vector" aria-pressed="false">Vector only</button></div></div>
<div class="focus"><span class="small">Inspect:</span><button type="button" data-focus="crack">Crack / splinters</button><button type="button" data-focus="central">Central orange column</button><button type="button" data-focus="lower">Paint beneath legs</button><button type="button" data-focus="right">Right yellow field</button><button type="button" data-focus="triangle">Upper triangle</button><button type="button" data-focus="full">Full poster</button><span class="small">Scroll to move around when enlarged.</span></div></div>
<div class="legend" id="legend" hidden><span><i class="swatch teal"></i><span id="missing-label">Photo only</span></span><span><i class="swatch magenta"></i><span id="excess-label">Vector only</span></span><span id="diagnostic-label"></span></div>
<div id="viewport" class="viewport" tabindex="0" aria-label="Scrollable photo and vector comparison"><div class="space"><div class="stage" id="stage"><img id="photo" src="@@PHOTO@@" alt="Registered original poster photograph" width="1000" height="1400" draggable="false"><img id="vector" class="vector" src="@@REVISED@@" alt="Revision 4 editable vector artwork" width="1000" height="1400" draggable="false"><img id="diagnostic" class="diagnostic" alt="Fixed-mask diagnostic overlay" width="1000" height="1400" draggable="false" hidden><div class="divider" id="divider"></div><span class="tag tag-left" id="left-tag">Photograph</span><span class="tag tag-right" id="right-tag">Revision 4</span></div></div></div>
<div class="viewer-footer"><span id="status" role="status" aria-live="polite">Revision 4 · wipe comparison</span><span>1000 × 1400 reference plane · all assets included · no network required</span></div></section>
<section class="card section"><h2>What the overlay measures</h2><div class="stats"><div class="stat"><strong>@@PAINT@@</strong><span>Broad orange-field overlap · higher is closer</span></div><div class="stat"><strong>@@RGB@@</strong><span>Mean RGB fit residual · lower is closer</span></div><div class="stat"><strong>@@CRACK@@</strong><span>Crack / splinter mean edge distance · lower is closer</span></div></div>
<p class="small">Paint measurements use the same 698,156 eligible pixels as the earlier analysis. The crack metric uses the same small box and dark-ink threshold for both versions. These are fit residuals against this photograph, not historical-authenticity percentages or scores for the entire poster.</p>
<div class="table-wrap"><table><caption>Paint comparison · Revision 3 versus Revision 4</caption><thead><tr><th>Region</th><th>V3 RGB residual</th><th>V4 RGB residual</th><th>V3 orange overlap</th><th>V4 orange overlap</th></tr></thead><tbody>@@ROWS@@</tbody></table></div>
<p class="small"><strong>Mixed regional result:</strong> lower-scumble and right-band orange placement regress despite improved average RGB appearance. The lower belt still needs finer source-located deposits; the strongest orange marks on the right remain misplaced or underrepresented. The short broken red spur above the central block is also simplified. These are the next paint targets.</p>
<details><summary>Registration, mask and threshold details</summary><p>The photograph uses the established estimated perspective transformation to 1000 × 1400 pixels. The paint mask uses R &gt; 135, B &lt; 105 and RGB range &gt; 75, with an eight-pixel interior margin and fixed caption, footer, headline and seal exclusions. It is unchanged from Revision 2. Orange-field classification smooths G / max(R,1) at sigma 6 pixels, then uses a threshold of 0.50. The paint overlay displays only areas where that broad classification disagrees.</p><p>The local crack diagnostic classifies dark ink with max(R,G,B) &lt; 125 in the box x307–372, y758–826. The reported crack/splinter metric uses x325–345, y766–799; the complete report also retains wider joint and context boxes and sensitivity checks at thresholds 90, 110 and 140. Teal marks photo ink missing from the vector; magenta marks excess vector ink. Photograph blur, print wear and estimated registration limit precision.</p><p>The clean edition shares the revised drawing. Its diagnostic buttons show the textured Revision 4 paint and the common revised crack, as stated in the legend. Artwork masks are evaluation aids only: photograph contours do not generate the delivered SVG geometry.</p></details></section>
<section class="card section"><h2>What changed, and what still needs judgment</h2><div class="notes"><div><h3>Broken match at the hips</h3><p>The broad internal divider and short star-like lines are replaced by a small torn shoulder, an irregular narrow split and tapered splinters. The paper-coloured spaces between them are part of the construction. The repair is local and preserves the long leg shafts and surrounding white paint edge.</p><h3>Paint placement and material</h3><p>The paint revision addresses the central orange column, the overly regular horizontal marks beneath the legs, and the warm mottling in the yellow fields. Large colour shapes and small paint marks remain separately editable native vector geometry.</p></div><div><h3>Remaining fidelity limits</h3><p>Fine grain, translucent deposits, wear and paint hidden by lettering are still interpreted. Some small paint marks remain different from the photograph even where broad fields align well. Close-up visual comparison matters alongside the numerical residuals.</p><p>The 5:7 artboard and original print dimensions remain unverified. Colours are fitted to the photograph rather than calibrated physical inks. Small seal details, the historical typeface and the apparent signature attribution remain approximate. The white reserve, headline and seal retain their prior construction.</p></div></div><p class="small">The HTML contains the exact delivered SVG artwork plus reference and diagnostic PNGs. JavaScript syntax and embedded asset identity are checked; browser interaction was not exercised in this environment. The static review boards provide the comparison independently.</p></section>
</main><script id="assets" type="application/json">@@ASSETS@@</script><script id="measurements" type="application/json">@@METRICS@@</script>
<script>
'use strict';
(() => {
 const id=x=>document.getElementById(x), assets=JSON.parse(id('assets').textContent);
 assets.photo=id('photo').getAttribute('src');assets.revised=id('vector').getAttribute('src');
 const state={mode:'wipe',edition:'revised',amount:50};
 const names={previous:'Revision 3',revised:'Revision 4 textured',clean:'Revision 4 clean'};
 const viewport=id('viewport'),stage=id('stage'),vector=id('vector'),photo=id('photo'),diagnostic=id('diagnostic'),zoom=id('zoom');
 let active='revised';
 function update(){
  const {mode,edition,amount:n}=state,isDiag=['paint','ink'].includes(mode);
  if(active!==edition){vector.src=assets[edition];active=edition;}
  vector.alt=names[edition];vector.hidden=mode==='photo'||isDiag;photo.hidden=mode==='vector';diagnostic.hidden=!isDiag;
  id('legend').hidden=!isDiag;id('divider').hidden=mode!=='wipe';id('left-tag').hidden=mode!=='wipe'||n<13;id('right-tag').hidden=mode!=='wipe'||n>82;
  id('right-tag').textContent=names[edition];vector.style.clipPath=mode==='wipe'?`inset(0 0 0 ${n}%)`:'none';vector.style.opacity=mode==='blend'?String(n/100):'1';id('divider').style.left=`${n}%`;
  id('amount').disabled=!['wipe','blend'].includes(mode);id('range-label').textContent=mode==='blend'?'Vector opacity':mode==='wipe'?'Wipe position':'Comparison slider';id('range-value').textContent=mode==='wipe'?`Photo ${n}% · vector ${100-n}%`:mode==='blend'?`${n}% vector`:'Select Wipe or Blend to adjust';
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  if(isDiag){const version=edition==='previous'?'previous':'revised',source=assets[`${mode}_${version}`];if(diagnostic.getAttribute('src')!==source)diagnostic.src=source;
   id('missing-label').textContent=mode==='paint'?'Orange field in photo only':'Ink in photo only';id('excess-label').textContent=mode==='paint'?'Orange field in vector only':'Ink in vector only';
   id('diagnostic-label').textContent=(version==='previous'?'Revision 3':'Revision 4')+(mode==='paint'?' textured paint · fixed interior mask':' local crack · threshold 125')+(edition==='clean'?' · common revised diagnostic':'');
   diagnostic.alt=id('diagnostic-label').textContent+'; teal is photo only, magenta is vector only';}
  id('status').textContent=`${names[edition]} · ${mode==='ink'?'local crack overlay':mode==='paint'?'broad paint overlay':mode+' comparison'}`;
 }
 function fit(center){
  const factor=Number(zoom.value),padding=innerWidth<700?24:40;
  const base=Math.max(180,Math.min(viewport.clientWidth-padding,(viewport.clientHeight-padding)/1.4));
  stage.style.width=`${base*factor}px`;
  requestAnimationFrame(()=>{if(center){const sr=stage.getBoundingClientRect(),vr=viewport.getBoundingClientRect();viewport.scrollLeft+=sr.left-vr.left+stage.clientWidth*center[0]-viewport.clientWidth/2;viewport.scrollTop+=sr.top-vr.top+stage.clientHeight*center[1]-viewport.clientHeight/2;}});
 }
 const points={crack:[.335,.562,'12'],central:[.61,.49,'3'],lower:[.32,.665,'4'],right:[.92,.58,'4'],triangle:[.73,.19,'6'],full:[.5,.5,'1']};
 document.querySelectorAll('[data-focus]').forEach(b=>b.addEventListener('click',()=>{const p=points[b.dataset.focus];zoom.value=p[2];fit(p);}));
 document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>{state.mode=b.dataset.mode;update();}));
 id('edition').addEventListener('change',e=>{state.edition=e.target.value;update();});id('amount').addEventListener('input',e=>{state.amount=Number(e.target.value);update();});
 zoom.addEventListener('change',()=>fit([.5,.5]));window.addEventListener('resize',()=>fit());fit([.5,.5]);update();
})();
</script></body></html>'''
if __name__=='__main__':main()
