"""Make registration proofs from the fixed native coordinate canvas.

No resizing, translation, homography, feature matching, or local warping is
applied before overlap. Display thumbnails are resized only after compositing.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
from scipy.ndimage import binary_dilation
import base64, json, html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
original_path=ROOT/'reference'/'original-reference.png'
if not original_path.exists(): original_path=ROOT.parent/'upload'/'Vintage Queen of Sidney Ferry Sticker(2).png'
source=Image.open(original_path).convert('RGBA')
vector=Image.open(ROOT/'qa'/'final-native.png').convert('RGBA')
assert source.size==vector.size==(1305,1206)

blend_layer=vector.copy()
blend_layer.putalpha(vector.getchannel('A').point(lambda n:round(n*.5)))
blend=Image.alpha_composite(source,blend_layer)
blend.save(OUT/'Queen-of-Sidney-overlap-50.png')

# Edges come from the visible flat vector rendering, not source-image tracing.
white=Image.new('RGBA',vector.size,'white');white.alpha_composite(vector)
arr=np.asarray(white.convert('RGB')).astype(np.int16)
alpha=np.asarray(vector.getchannel('A')).astype(np.int16)
edge=np.zeros(alpha.shape,dtype=bool)
edge[:,1:] |= np.max(np.abs(arr[:,1:]-arr[:,:-1]),axis=2)>42
edge[1:,:] |= np.max(np.abs(arr[1:,:]-arr[:-1,:]),axis=2)>42
edge[:,1:] |= np.abs(alpha[:,1:]-alpha[:,:-1])>42
edge[1:,:] |= np.abs(alpha[1:,:]-alpha[:-1,:])>42
edge=binary_dilation(edge,iterations=1)
rgba=np.zeros((*edge.shape,4),dtype=np.uint8)
rgba[:,:,:3]=[221,0,154]
rgba[:,:,3]=edge.astype(np.uint8)*225
edge_layer=Image.fromarray(rgba)
edge_layer.save(ROOT/'qa'/'vector-edges-transparent.png')
faded=Image.blend(source,Image.new('RGBA',source.size,'white'),.24)
edge_proof=Image.alpha_composite(faded,edge_layer)
edge_proof.save(OUT/'Queen-of-Sidney-edge-overlap.png')

def font(size,bold=False):
    return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',size)

def make_sheet():
    panel_w=880; panel_h=round(panel_w*1206/1305)
    pad=48; gap=32; title_h=166; label_h=66; footer_h=100
    width=pad*2+panel_w*2+gap
    height=title_h+(panel_h+label_h)*2+gap+footer_h
    sheet=Image.new('RGB',(width,height),'#f3f1eb');d=ImageDraw.Draw(sheet)
    d.text((pad,30),'QUEEN OF SIDNEY',font=font(34,True),fill='#10242b')
    d.text((pad,80),'Vector reconstruction / registered comparison',font=font(23),fill='#48565a')
    d.text((pad,116),'Same 1305 × 1206 canvas. No fitted shift, scale, rotation or warp.',font=font(19),fill='#48565a')
    entries=[('01  ORIGINAL REFERENCE',source),('02  REBUILT VECTOR',white),('03  50% VECTOR OVER ORIGINAL',blend),('04  MAGENTA REBUILT EDGES',edge_proof)]
    for i,(label,im) in enumerate(entries):
        col=i%2;row=i//2;x=pad+col*(panel_w+gap);y=title_h+row*(panel_h+label_h+gap)
        d.text((x,y+12),label,font=font(21,True),fill='#10242b')
        thumb=im.convert('RGB').resize((panel_w,panel_h),Image.Resampling.LANCZOS)
        sheet.paste(thumb,(x,y+label_h))
        d.rectangle((x,y+label_h,x+panel_w-1,y+label_h+panel_h-1),outline='#d7d7cf',width=1)
    y=height-footer_h+30
    d.text((pad,y),'Clean flat colours replace paper grain, wear and the photographed drop shadow.',font=font(19),fill='#48565a')
    d.text((pad,y+29),'Fine print details are reconstructed; this is not recovered original production artwork.',font=font(19),fill='#48565a')
    sheet.save(OUT/'Queen-of-Sidney-comparison.png')

make_sheet()

def data_uri(path,mime):
    return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()

source_uri=data_uri(original_path,'image/png')
svg_uri=data_uri(OUT/'Queen-of-Sidney-rebuilt.svg','image/svg+xml')
edge_uri=data_uri(ROOT/'qa'/'vector-edges-transparent.png','image/png')

template='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Queen of Sidney · vector comparison</title>
<style>
:root{color-scheme:light;--ink:#10242b;--muted:#526168;--line:#d9dfdc;--orange:#ff6404;--paper:#f6f5ef}
*{box-sizing:border-box}body{margin:0;background:var(--paper);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink)}
header{background:var(--ink);color:white;padding:28px max(24px,calc((100% - 1420px)/2));border-bottom:5px solid var(--orange)}
.eyebrow{margin:0 0 6px;font-size:12px;font-weight:750;letter-spacing:.16em;color:#ffae7a}h1{font-size:clamp(24px,3vw,36px);margin:0;font-weight:760;letter-spacing:-.035em}header p{margin:8px 0 0;color:#c7d4d8;max-width:820px}
main{max-width:1470px;margin:0 auto;padding:24px}.controls{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:18px}.modes{display:flex;gap:5px;flex-wrap:wrap}
button,.download{font:inherit;border:1px solid #bcc7c9;border-radius:7px;padding:9px 14px;background:white;color:var(--ink);cursor:pointer;text-decoration:none;font-size:14px;font-weight:650}button[aria-pressed="true"]{background:var(--ink);color:white;border-color:var(--ink)}button:hover,.download:hover{border-color:var(--orange)}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #ffab70;outline-offset:3px}
.download{margin-left:auto}.rangebox{display:flex;gap:12px;align-items:center;min-width:300px;flex:1}.rangebox label{font-size:13px;min-width:150px;font-weight:650}input[type=range]{width:min(100%,300px);accent-color:var(--orange)}
.subcontrols{display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin:0 0 16px}.zoom{display:flex;gap:12px;align-items:center;font-size:13px}.zoom input{width:150px}.caption{font-size:13px;color:var(--muted);margin:0}
.viewport{height:min(76vh,1040px);min-height:390px;overflow:auto;background:#e6e9e6;border:1px solid #cbd2ce;border-radius:10px;box-shadow:0 2px 9px #10242b0a}.stage{position:relative;width:100%;aspect-ratio:1305 / 1206;margin:0 auto;background-color:#f9faf9;background-image:linear-gradient(45deg,#e3e6e3 25%,transparent 25%),linear-gradient(-45deg,#e3e6e3 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e3e6e3 75%),linear-gradient(-45deg,transparent 75%,#e3e6e3 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}
.stage img{position:absolute;inset:0;display:block;width:100%;height:100%;pointer-events:none}.divider{position:absolute;top:0;bottom:0;width:2px;background:#e0009a;display:none;pointer-events:none}.divider:before{content:'↔';position:absolute;left:-16px;top:45%;width:34px;height:34px;display:grid;place-items:center;background:#10242b;color:white;border:2px solid white;border-radius:50%;font-weight:bold}
.info{display:grid;grid-template-columns:1fr 1fr;gap:32px;padding-top:23px;font-size:14px;color:var(--muted)}.info h2{font-size:14px;color:var(--ink);margin:0 0 6px}.info p{margin:0 0 8px}.chip{display:inline-block;border:1px solid #cfd6d1;border-radius:30px;padding:3px 10px;font-size:12px;margin:0 4px 5px 0;color:var(--ink)}
@media(max-width:700px){main{padding:16px}.download{margin-left:0}.rangebox{min-width:100%}.controls{gap:12px}.info{grid-template-columns:1fr;gap:14px}.viewport{height:64vh}.rangebox label{min-width:138px}button{padding:8px 10px}}
</style></head><body>
<header><p class="eyebrow">RECONSTRUCTED VECTOR ARTWORK</p><h1>Queen of Sidney</h1><p>Inspect the full redraw against the supplied sticker. Every view uses the original coordinate canvas, with no alignment adjustment.</p></header>
<main>
<div class="controls"><div class="modes" aria-label="Comparison mode">
<button data-mode="blend" aria-pressed="true">Overlap</button><button data-mode="wipe" aria-pressed="false">Wipe</button><button data-mode="edges" aria-pressed="false">Vector edges</button><button data-mode="source" aria-pressed="false">Original</button><button data-mode="vector" aria-pressed="false">Rebuilt</button>
</div><a class="download" download="Queen-of-Sidney-rebuilt.svg" href="__SVG__">Download SVG</a></div>
<div class="subcontrols"><div class="rangebox" id="rangebox"><label for="amount" id="amountLabel">Vector opacity · 50%</label><input type="range" id="amount" min="0" max="100" value="50" aria-label="Vector opacity"></div><div class="zoom"><label for="zoom">Zoom</label><input type="range" id="zoom" min="100" max="300" step="25" value="100"><output id="zoomLabel">100%</output><button id="reset">Reset view</button></div></div>
<div class="viewport" id="viewport"><div class="stage" id="stage">
<img id="original" src="__SOURCE__" alt="Original photographed Queen of Sidney sticker"><img id="rebuilt" src="__SVG__" alt="Reconstructed Queen of Sidney vector" style="opacity:.5"><img id="edges" src="__EDGES__" alt="Magenta outlines of the reconstructed artwork" style="display:none"><div id="divider" class="divider"></div>
</div></div>
<div class="info"><section><h2>Reading the comparison</h2><p id="modeCaption">Both versions share the same coordinate canvas. Move the opacity slider to reveal shifts in outlines and details.</p><span class="chip">1305 × 1206 source canvas</span><span class="chip">Identity registration</span><span class="chip">No warp or fitted transform</span></section><section><h2>Reconstruction choices</h2><p>The ferry, flowers, flag, wheel, landscape, water, ribbon and lettering are editable vector objects. Lettering is outlined; the SVG contains no embedded image.</p><p>Paper texture, wear, lighting variation and the photographed drop shadow were removed. Fine printed details and the lower lettering were redrawn from the available reference.</p></section></div>
</main><script>
const $=id=>document.getElementById(id);let mode='blend';
const captions={blend:'Both versions share the same coordinate canvas. Move the opacity slider to reveal shifts in outlines and details.',wipe:'The rebuilt vector appears to the left of the divider; the original appears to the right. Move the slider to inspect any region.',edges:'Magenta marks the visible boundaries of the rebuilt vector over the original. The original is slightly faded for legibility.',source:'The unmodified supplied image, displayed on its original 1305 × 1206 coordinate canvas.',vector:'The completed SVG artwork. The checkerboard outside the white sticker indicates transparency.'};
function render(){const value=Number($('amount').value);const v=$('rebuilt'),s=$('original'),e=$('edges'),d=$('divider');s.style.display=mode==='vector'?'none':'block';s.style.opacity=mode==='edges'?'.76':'1';v.style.display=['source','edges'].includes(mode)?'none':'block';v.style.opacity=mode==='blend'?String(value/100):'1';v.style.clipPath=mode==='wipe'?`inset(0 ${100-value}% 0 0)`:'none';e.style.display=mode==='edges'?'block':'none';e.style.opacity=String(value/100);d.style.display=mode==='wipe'?'block':'none';d.style.left=value+'%';$('rangebox').style.visibility=['source','vector'].includes(mode)?'hidden':'visible';const label=mode==='wipe'?'Vector portion':mode==='edges'?'Edge opacity':'Vector opacity';$('amountLabel').textContent=label+' · '+value+'%';$('amount').setAttribute('aria-label',label);$('modeCaption').textContent=captions[mode];document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));}
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.mode;$('amount').value=mode==='edges'?'100':'50';render();}));
$('amount').addEventListener('input',render);function fit(){const vp=$('viewport');const width=Math.min(vp.clientWidth,vp.clientHeight*1305/1206);$('stage').style.width=(width*Number($('zoom').value)/100)+'px';$('zoomLabel').textContent=$('zoom').value+'%';} $('zoom').addEventListener('input',fit);window.addEventListener('resize',fit);$('reset').addEventListener('click',()=>{$('zoom').value=100;fit();$('viewport').scrollTo(0,0);$('amount').value=mode==='edges'?100:50;render();});render();fit();
</script></body></html>'''
page=template.replace('__SOURCE__',source_uri).replace('__SVG__',svg_uri).replace('__EDGES__',edge_uri)
(OUT/'Queen-of-Sidney-comparison.html').write_text(page)
print(json.dumps({'proofs':[p.name for p in OUT.iterdir() if 'overlap' in p.name or 'comparison' in p.name],'registration':'identity','native_canvas':list(source.size)},indent=2))
