#!/usr/bin/env python3
"""Build a portable offline SVG/reference overlay review.

Usage:
  python source/build_review.py
  python source/build_review.py --master PATH --reference PATH --boxes PATH --output PATH

All image data and UI code are embedded. No network resources are loaded.
The original scan's native aspect ratio is retained for registration.
"""
from pathlib import Path
import argparse, base64, io, json, re
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parents[1]

def data_uri(data, mime):
    return 'data:'+mime+';base64,'+base64.b64encode(data).decode('ascii')

def build(master,reference,boxes_path,output):
    raw=master.read_bytes()
    tree=ET.fromstring(raw)
    vb=[float(x) for x in re.split(r'[\s,]+',tree.attrib.get('viewBox','0 0 1000 2997.26').strip())]
    if len(vb)!=4 or vb[0]!=0 or vb[1]!=0:
        raise ValueError('Review expects an SVG viewBox beginning at 0 0.')
    width,height=vb[2],vb[3]
    image=Image.open(reference).convert('RGB')
    native_width,native_height=image.size
    if image.width>2000:
        image=image.resize((2000,round(image.height*2000/image.width)),Image.Resampling.LANCZOS)
    encoded=io.BytesIO()
    image.save(encoded,format='JPEG',quality=94,subsampling=0,optimize=True)
    boxes=json.loads(boxes_path.read_text())
    names=[('whole','Whole poster'),('hawk','Red-tailed hawk'),('owl','Great horned owl'),('squirrel','Northern flying squirrel'),('chickadee','Black-capped chickadee'),('bear','Black bear'),('toad','Northwestern toad'),('tree-top','Habitat tree · upper branches'),('tree-middle','Habitat tree · trunk'),('tree-base','Habitat tree · roots'),('footer','Title and information panel'),('logos','Ministry and Forest Service marks')]
    presets=[]
    for key,label in names:
        box=[0,0,width,height] if key=='whole' else ([598,2735,845,2896] if key=='logos' else boxes[key])
        presets.append({'id':key,'label':label,'box':box})
    paths=sum(1 for e in tree.iter() if e.tag.rsplit('}',1)[-1]=='path')
    rasters=sum(1 for e in tree.iter() if e.tag.rsplit('}',1)[-1]=='image')
    metadata={
      'width':width,'height':height,
      'sourceWidth':native_width,'sourceHeight':native_height,
      'sourceLogicalHeight':width*native_height/native_width,
      'presets':presets,'pathCount':paths,'embeddedRasterCount':rasters,
      'reference':data_uri(encoded.getvalue(),'image/jpeg'),
      'vector':data_uri((ROOT/'_work/poster-proof-render.png').read_bytes(),'image/png'),
      'masterFilename':master.name,
    }
    html=TEMPLATE.replace('/*__EMBEDDED_DATA__*/',json.dumps(metadata,separators=(',',':')))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(html,encoding='utf-8')
    print(json.dumps({'output':str(output.resolve()),'bytes':output.stat().st_size,'master_viewBox':vb,'source_pixels':[native_width,native_height],'paths':paths,'embedded_rasters':rasters,'focus_presets':len(presets)}))

TEMPLATE=r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>Wildlife Trees · Overlay review</title>
<style>
:root{font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#203b31;background:#edf1ed;--forest:#326c59;--line:#ced9d1;--muted:#52695d;--panel:#fbfcf9}
*{box-sizing:border-box}body{margin:0}button,select,input{font:inherit}button,select{border:1px solid var(--line);background:#fff;color:inherit;border-radius:7px;min-height:38px}button{padding:7px 12px;cursor:pointer}button:hover{background:#edf4ed}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #bc800e;outline-offset:3px}button:disabled{opacity:.45;cursor:wait}header{padding:23px 28px 18px;background:var(--panel);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:24px}.eyebrow{font-size:10px;font-weight:750;letter-spacing:.15em;color:var(--forest);margin-bottom:5px}h1{font-family:Georgia,"Times New Roman",serif;font-size:29px;font-weight:normal;line-height:1.08;letter-spacing:-.02em;margin:0}header p{font-size:13px;color:var(--muted);margin:7px 0 0}.header-actions{display:flex;align-items:center;gap:10px}.download{background:var(--forest);border-color:var(--forest);color:white;font-size:12px;white-space:nowrap}.download:hover{background:#25503f}.badge{font-size:11px;color:var(--muted);white-space:nowrap;border:1px solid var(--line);border-radius:20px;padding:6px 9px}.controls{background:var(--panel);padding:14px 28px;display:flex;flex-wrap:wrap;gap:14px 24px;align-items:end;border-bottom:1px solid var(--line)}.control{display:flex;flex-direction:column;gap:5px;min-width:125px}.control>label,.control-title{font-size:10px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}.modes{display:flex;gap:3px;background:#e8eee8;border:1px solid var(--line);border-radius:9px;padding:3px}.modes button{min-height:31px;border:0;background:transparent;border-radius:5px;font-size:12px;padding:6px 10px;white-space:nowrap}.modes button[aria-pressed="true"]{background:#fff;box-shadow:0 1px 3px #16332620;color:#204e3b;font-weight:700}select{min-width:215px;max-width:300px;padding:6px 30px 6px 10px;font-size:12px}.range-row{height:38px;display:flex;align-items:center;gap:8px}.range-row input{width:135px;accent-color:var(--forest)}output{font-size:12px;font-variant-numeric:tabular-nums;min-width:37px;text-align:right}.zoom-buttons{display:flex;gap:6px}.zoom-buttons button{font-size:12px;padding:6px 9px}.slider-panel{transition:opacity .15s}.slider-panel.inactive{opacity:.40}.workbench-wrap{padding:15px 24px 0}.view-meta{display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:28px;font-size:12px;color:var(--muted);padding:0 2px 10px}.focus-name{font-weight:650;color:#244436}.legend{display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:11px}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}.ref-dot{background:#b52f80}.vec-dot{background:#1197b3}.legend[hidden]{display:none}.workbench{height:calc(100vh - 291px);min-height:355px;overflow:auto;position:relative;background-color:#e2e8e2;background-image:linear-gradient(45deg,#dbe3da 25%,transparent 25%),linear-gradient(-45deg,#dbe3da 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#dbe3da 75%),linear-gradient(-45deg,transparent 75%,#dbe3da 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0;border:1px solid #c6d1c7;border-radius:10px;scrollbar-color:#98ad9b #e6ebe5;overscroll-behavior:contain;cursor:grab}.workbench.dragging{cursor:grabbing}.canvas-box{position:relative;min-width:100%;min-height:100%}.stage{position:absolute;isolation:isolate;background:white;box-shadow:0 3px 20px #1937281f;user-select:none}.stage img{position:absolute;left:0;top:0;width:100%;max-width:none;display:block;pointer-events:none;user-select:none}.vector{height:100%}.reference{opacity:1}.stage.reference-only .vector{display:none}.stage.vector-only .reference{display:none}.stage.vector-only .vector{opacity:1!important;clip-path:none!important}.stage.blend .vector{clip-path:none!important}.stage.wipe .vector{opacity:1!important}.stage.color .reference{filter:url(#magenta-ink)}.stage.color .vector{filter:url(#cyan-ink);mix-blend-mode:multiply;opacity:1!important;clip-path:none!important}.wipe-line{position:absolute;top:0;bottom:0;border-left:1.5px solid #d69212;pointer-events:none;display:none;z-index:2}.stage.wipe .wipe-line{display:block}.wipe-tab{position:absolute;top:15px;left:-13px;width:26px;height:26px;border-radius:20px;background:#fff7e2;border:1px solid #bd820d;display:grid;place-items:center;color:#815900;font-size:14px;box-shadow:0 1px 4px #0002}.status{font-size:12px;color:var(--muted)}.status.error{color:#9c3924}.bottom-bar{padding:11px 26px 15px;display:flex;align-items:start;justify-content:space-between;gap:16px;font-size:11px;color:var(--muted);line-height:1.5}.bottom-bar p{margin:0}details{max-width:620px;text-align:right}summary{cursor:pointer;text-decoration:underline;text-underline-offset:3px}details p{margin-top:7px!important}kbd{font:10px ui-monospace,monospace;border:1px solid var(--line);border-radius:3px;padding:1px 4px;background:#fff}.filter-defs{position:absolute;width:0;height:0;overflow:hidden}.loading{position:absolute;inset:0;display:grid;place-items:center;z-index:4;background:#eaf0e8e8;color:#294e3d;font-size:14px;pointer-events:none}.loading[hidden]{display:none}
@media(max-width:1050px){.controls{gap:10px 16px;padding:12px 20px}.control{min-width:110px}.range-row input{width:105px}.workbench{height:calc(100vh - 329px)}.header-actions .badge{display:none}.modes button{padding:6px 8px}}
@media(max-width:700px){header{padding:17px 16px 14px;align-items:start;gap:12px}h1{font-size:25px}header p{max-width:280px;line-height:1.4;font-size:12px}.download{font-size:11px;padding:7px 9px}.controls{padding:11px 13px;gap:10px 13px}.mode-control{width:100%}.modes{width:100%;justify-content:space-between}.modes button{flex:1;font-size:11px;padding:6px 5px}.focus-control{flex:1}.focus-control select{width:100%;max-width:none;min-width:175px}.zoom-control{min-width:104px}.zoom-control input{width:70px}.slider-panel input{width:95px}.slider-panel{min-width:135px}.zoom-buttons{margin-left:auto}.workbench-wrap{padding:11px 10px 0}.workbench{height:calc(100vh - 393px);min-height:365px}.view-meta{font-size:11px;gap:8px;align-items:start}.legend{font-size:10px;gap:8px}.bottom-bar{padding:9px 13px 14px;display:block}.bottom-bar details{text-align:left;margin-top:7px}.keyboard-hint{display:none}}
@media print{header,.controls,.bottom-bar,.view-meta{display:none}.workbench-wrap{padding:0}.workbench{border:0;height:auto;overflow:visible;background:white}.canvas-box{width:100%!important;height:auto!important}.stage{position:relative;left:0!important;top:0!important;width:100%!important;height:auto!important;aspect-ratio:1000/2997.26;box-shadow:none}.stage .reference{display:none}.stage .vector{display:block;filter:none!important;opacity:1!important;clip-path:none!important;mix-blend-mode:normal!important}.wipe-line{display:none!important}}
</style>
</head>
<body>
<svg class="filter-defs" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs>
<filter id="magenta-ink" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope="1.45" intercept="-.45"/><feFuncG type="linear" slope="1.45" intercept="-.45"/><feFuncB type="linear" slope="1.45" intercept="-.45"/></feComponentTransfer><feColorMatrix type="matrix" values=".14 0 0 0 .86  0 .89 0 0 .11  0 0 .47 0 .53  0 0 0 1 0"/></filter>
<filter id="cyan-ink" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope="1.45" intercept="-.45"/><feFuncG type="linear" slope="1.45" intercept="-.45"/><feFuncB type="linear" slope="1.45" intercept="-.45"/></feComponentTransfer><feColorMatrix type="matrix" values="1 0 0 0 0  0 .45 0 0 .55  0 0 .25 0 .75  0 0 0 1 0"/></filter>
</defs></svg>
<header>
  <div><div class="eyebrow">ARTWORK REVIEW</div><h1>Wildlife Trees</h1><p>Compare the rebuilt poster with the original scan at the same positions.</p></div>
  <div class="header-actions"><span class="badge">Works offline</span></div>
</header>
<section class="controls" aria-label="Comparison controls">
  <div class="control mode-control"><span class="control-title">Comparison</span><div class="modes" role="group" aria-label="Comparison mode">
    <button type="button" data-mode="reference-only" aria-pressed="false">Reference</button><button type="button" data-mode="vector-only" aria-pressed="false">Redraw</button><button type="button" data-mode="blend" aria-pressed="true">Blend</button><button type="button" data-mode="wipe" aria-pressed="false">Wipe</button><button type="button" data-mode="color" aria-pressed="false">Color overlay</button>
  </div></div>
  <div class="control focus-control"><label for="focus">Focus</label><select id="focus"></select></div>
  <div class="control slider-panel" id="opacity-panel"><label for="opacity">Vector opacity</label><div class="range-row"><input type="range" id="opacity" min="0" max="100" step="1" value="50"><output id="opacity-value" for="opacity">50%</output></div></div>
  <div class="control slider-panel inactive" id="wipe-panel"><label for="wipe">Wipe position</label><div class="range-row"><input type="range" id="wipe" min="0" max="100" step="1" value="50" disabled><output id="wipe-value" for="wipe">50%</output></div></div>
  <div class="control zoom-control"><label for="zoom">Zoom</label><div class="range-row"><input type="range" id="zoom" min="0.10" max="5" step="0.01" value="0.20"><output id="zoom-value" for="zoom">20%</output></div></div>
  <div class="zoom-buttons"><button type="button" id="fit">Fit selection</button><button type="button" id="width-fit">Fit width</button></div>
</section>
<main class="workbench-wrap">
  <div class="view-meta"><span id="focus-name" class="focus-name">Whole poster</span><span class="legend" id="legend" hidden><span><i class="dot ref-dot"></i>Reference</span><span><i class="dot vec-dot"></i>Vector</span><span>Overlap appears darker</span></span><span id="status" class="status" role="status">Preparing artwork…</span></div>
  <div class="workbench" id="viewport" tabindex="0" aria-label="Artwork comparison. Drag to pan or use the scrollbars.">
    <div class="canvas-box" id="canvas-box"><div class="stage blend" id="stage"><img id="reference" class="reference" alt="Original scanned Wildlife Trees poster"><img id="vector" class="vector" alt="Reconstructed vector Wildlife Trees poster"><div class="wipe-line" id="wipe-line"><span class="wipe-tab">↔</span></div></div></div>
    <div class="loading" id="loading">Preparing the embedded artwork…</div>
  </div>
</main>
<footer class="bottom-bar"><p>Drag to pan. Choose a portrait or tree section to inspect details. <span class="keyboard-hint"><kbd>+</kbd> / <kbd>−</kbd> zoom · <kbd>F</kbd> fit selection</span></p><details><summary>About this comparison</summary><p>The scan and vector share the same poster coordinates. The reference keeps its original aspect ratio. The colored overlay shows the scan in magenta and the redraw in cyan; aligned ink appears darker. Smoothing, scan grain and the fitted replacement typeface can create colored fringes. The comparison uses a rendered vector preview; the editable SVG and vector PDF are supplied separately.</p><p id="registration"></p></details></footer>
<script>
'use strict';
const DATA=/*__EMBEDDED_DATA__*/;
const el=id=>document.getElementById(id);
const viewport=el('viewport'),stage=el('stage'),canvasBox=el('canvas-box');
const reference=el('reference'),vector=el('vector');
const focusSelect=el('focus'),zoom=el('zoom'),opacity=el('opacity'),wipe=el('wipe');
let scale=.2,mode='blend',ready=false,stageLeft=24,stageTop=24;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function preset(){return DATA.presets.find(p=>p.id===focusSelect.value)||DATA.presets[0];}
function layout(){
  const w=DATA.width*scale,h=DATA.height*scale;
  const viewW=viewport.clientWidth,viewH=viewport.clientHeight;
  stageLeft=Math.max(24,(viewW-w)/2);stageTop=Math.max(24,(viewH-h)/2);
  stage.style.width=w+'px';stage.style.height=h+'px';
  stage.style.left=stageLeft+'px';stage.style.top=stageTop+'px';
  canvasBox.style.width=Math.max(viewW,w+48)+'px';
  canvasBox.style.height=Math.max(viewH,h+48)+'px';
  reference.style.height=(DATA.sourceLogicalHeight/DATA.height*100)+'%';
  zoom.value=scale;el('zoom-value').textContent=Math.round(scale*100)+'%';
  updateComparison();
}
function centerOn(x,y){viewport.scrollLeft=stageLeft+x*scale-viewport.clientWidth/2;viewport.scrollTop=stageTop+y*scale-viewport.clientHeight/2;}
function setScale(next,center){
  const x=center?center[0]:(viewport.scrollLeft+viewport.clientWidth/2-stageLeft)/scale;
  const y=center?center[1]:(viewport.scrollTop+viewport.clientHeight/2-stageTop)/scale;
  scale=clamp(next,.1,5);layout();centerOn(x,y);
}
function fitSelection(widthOnly=false){
  const b=preset().box,pad=preset().id==='whole'?0:12;
  const availableW=Math.max(150,viewport.clientWidth-48),availableH=Math.max(150,viewport.clientHeight-48);
  const next=widthOnly?availableW/(b[2]-b[0]+pad*2):Math.min(availableW/(b[2]-b[0]+pad*2),availableH/(b[3]-b[1]+pad*2));
  setScale(next,[(b[0]+b[2])/2,(b[1]+b[3])/2]);
}
function updateComparison(){
  stage.className='stage '+mode;
  vector.style.opacity=Number(opacity.value)/100;
  const b=preset().box;
  const cut=b[0]+(b[2]-b[0])*Number(wipe.value)/100;
  const right=100-clamp(cut/DATA.width*100,0,100);
  vector.style.clipPath='inset(0 '+right+'% 0 0)';
  el('wipe-line').style.left=(cut/DATA.width*100)+'%';
  el('opacity-value').textContent=opacity.value+'%';el('wipe-value').textContent=wipe.value+'%';
  opacity.disabled=mode!=='blend';wipe.disabled=mode!=='wipe';
  el('opacity-panel').classList.toggle('inactive',mode!=='blend');el('wipe-panel').classList.toggle('inactive',mode!=='wipe');
  el('legend').hidden=mode!=='color';
  for(const button of document.querySelectorAll('[data-mode]'))button.setAttribute('aria-pressed',String(button.dataset.mode===mode));
  if(ready){el('status').textContent=mode==='wipe'?'Redraw left · reference right':mode==='color'?'':mode==='blend'?'Reference + redraw':mode==='vector-only'?'Vector artwork':'Original scan';}
}
for(const p of DATA.presets){const o=document.createElement('option');o.value=p.id;o.textContent=p.label;focusSelect.append(o);}
focusSelect.addEventListener('change',()=>{el('focus-name').textContent=preset().label;fitSelection();});
for(const button of document.querySelectorAll('[data-mode]'))button.addEventListener('click',()=>{mode=button.dataset.mode;updateComparison();});
opacity.addEventListener('input',updateComparison);wipe.addEventListener('input',updateComparison);
zoom.addEventListener('input',()=>setScale(Number(zoom.value)));
el('fit').addEventListener('click',()=>fitSelection());el('width-fit').addEventListener('click',()=>fitSelection(true));

let drag=null;
viewport.addEventListener('pointerdown',e=>{
  if(e.pointerType!=='mouse'||e.button!==0||!ready)return;
  drag={x:e.clientX,y:e.clientY,left:viewport.scrollLeft,top:viewport.scrollTop,id:e.pointerId};
  viewport.setPointerCapture(e.pointerId);viewport.classList.add('dragging');e.preventDefault();
});
viewport.addEventListener('pointermove',e=>{if(!drag)return;viewport.scrollLeft=drag.left-(e.clientX-drag.x);viewport.scrollTop=drag.top-(e.clientY-drag.y);});
function endDrag(){drag=null;viewport.classList.remove('dragging');}
viewport.addEventListener('pointerup',endDrag);viewport.addEventListener('pointercancel',endDrag);
viewport.addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey){e.preventDefault();setScale(scale*(e.deltaY<0?1.12:1/1.12));}},{passive:false});
document.addEventListener('keydown',e=>{
  if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement.tagName))return;
  if(e.key==='+'||e.key==='='){e.preventDefault();setScale(scale*1.2);}
  else if(e.key==='-'||e.key==='_'){e.preventDefault();setScale(scale/1.2);}
  else if(e.key.toLowerCase()==='f'){e.preventDefault();fitSelection();}
});
let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>fitSelection(),120);});
el('registration').textContent='Reference: '+DATA.sourceWidth+' × '+DATA.sourceHeight+' pixels. Master viewBox: '+DATA.width+' × '+DATA.height+'. Master artwork: '+DATA.pathCount.toLocaleString()+' vector paths'+(DATA.embeddedRasterCount?', '+DATA.embeddedRasterCount+' embedded raster images.':', no embedded raster images.');
function imageReady(image){return new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('An embedded image could not be displayed.'));});}
const loading=Promise.all([imageReady(reference),imageReady(vector)]);
reference.src=DATA.reference;vector.src=DATA.vector;layout();
loading.then(()=>{ready=true;el('loading').hidden=true;fitSelection();updateComparison();}).catch(err=>{el('loading').hidden=true;el('status').classList.add('error');el('status').textContent=err.message;});
</script>
</body>
</html>'''

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--master',type=Path,default=ROOT/'Wildlife-Trees-outlined.svg')
    parser.add_argument('--reference',type=Path,default=ROOT/'reference/reference-native.jpg')
    parser.add_argument('--boxes',type=Path,default=ROOT/'source/reference-regions.json')
    parser.add_argument('--output',type=Path,default=ROOT/'Wildlife-Trees-overlay-review.html')
    args=parser.parse_args();build(args.master,args.reference,args.boxes,args.output)
