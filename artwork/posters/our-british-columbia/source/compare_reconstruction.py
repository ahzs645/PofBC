#!/usr/bin/env python3
"""Create labelled, reproducible visual comparisons without fitting the artwork.

Usage:
 python3 compare_reconstruction.py ../work/poster-preview.png
 python3 compare_reconstruction.py ../work/poster-preview.png --landmarks ../work/vector-landmarks.json

The raster inputs must both use the registered 1000 x 1450 artboard. No affine,
projective, local, or nonlinear optimization is performed by this script.
"""
from pathlib import Path
import argparse, base64, io, json, math, html, hashlib
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parents[1]/'review'
CYAN=(0,125,160); MAGENTA=(190,37,101); OVERLAP=(53,41,65)

def font(size,bold=False):
    name='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+name,size)

def rgb(path):
    im=Image.open(path).convert('RGBA')
    bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
    return bg.convert('RGB')

def edge(mask):
    return mask & ~ndimage.binary_erosion(mask,structure=np.ones((3,3),bool))

def colour_shapes(im):
    a=np.asarray(im).astype(float);r,g,b=a[...,0],a[...,1],a[...,2]
    blue=(b>r*1.35)&(b>g*1.1)&(b>45)
    red=(r>g*2.0)&(r>b*1.5)&(r>90)
    yellow=(r>125)&(g>70)&(r>g*.75)&(r<g*2.1)&(b<g*.80)
    masks=[]
    for m in [blue,red,yellow]:
        m[1218:,:]=False
        # Fill enclosed lettering/holder holes; do not reconstruct the boundary.
        m=ndimage.binary_fill_holes(m)
        masks.append(m)
    return masks

def source_valid_mask(reg,include_glare=False):
    mask=Image.new('L',(1000,1450),255);d=ImageDraw.Draw(mask)
    H=np.asarray(reg['source_to_rectified_homography'])
    for key,poly in reg['artifact_masks_source'].items():
        if not include_glare and 'glare' in key: continue
        a=np.c_[np.asarray(poly),np.ones(len(poly))] @ H.T
        pts=a[:,:2]/a[:,2,None]
        d.polygon([tuple(p) for p in pts],fill=0)
    return np.asarray(mask)>0

def edge_composite(source_edges,vector_edges,valid):
    out=np.full((1450,1000,3),255,dtype=np.uint8)
    # Excluded areas have no comparison meaning for either image.
    yy,xx=np.indices(valid.shape)
    out[~valid]=(242,241,239)
    hatch=(~valid)&((xx+yy)%14<2);out[hatch]=(224,223,221)
    a=source_edges&valid;b=vector_edges&valid
    out[a]=CYAN;out[b]=MAGENTA;out[a&b]=OVERLAP
    return Image.fromarray(out)

def labelled(im,title,subtitle):
    canvas=Image.new('RGB',(im.width,im.height+116),'#f7f6f2');d=ImageDraw.Draw(canvas)
    d.text((24,16),title,font=font(25,True),fill='#19293b')
    d.text((24,52),subtitle,font=font(15),fill='#46525c')
    canvas.paste(im,(0,86))
    d.text((24,canvas.height-23),'Approximate photo registration; curl, glare and hidden details limit correspondence.',font=font(12),fill='#59636c')
    return canvas

def png_data(im):
    b=io.BytesIO();im.save(b,format='PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()

def write_review_html(photo,vector,geometry,lettering,out):
    p,v,g,l=map(png_data,[photo,vector,geometry,lettering])
    doc='''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Our British Columbia — reconstruction review</title>
<style>
:root{color-scheme:light;--ink:#172b44;--paper:#f6f4ef;--muted:#53606a}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}header{max-width:1120px;margin:auto;padding:28px 24px 18px}h1{font-size:28px;line-height:1.15;margin:0 0 10px}p{margin:7px 0;color:var(--muted)}.controls{position:sticky;top:0;z-index:5;background:#fffefbea;border-block:1px solid #d8d9d6;padding:13px 24px;backdrop-filter:blur(12px)}.control-inner{max-width:1072px;margin:auto;display:flex;align-items:center;flex-wrap:wrap;gap:12px 20px}label{display:flex;gap:8px;align-items:center;font-size:14px}select,button{font:inherit;padding:7px 10px;border:1px solid #c6ccc9;border-radius:6px;background:white;color:var(--ink)}input[type=range]{width:140px;accent-color:#315f76}button{cursor:pointer}button:hover{background:#edf3f4}.viewer{margin:20px auto;max-width:1120px;padding:0 24px;overflow:auto;max-height:78vh;border-bottom:1px solid #d8d9d6}.stage{position:relative;margin:auto;width:700px;max-width:none;aspect-ratio:1000/1450;background:white;box-shadow:0 4px 22px #14293b17}.stage img{display:block;position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.top{opacity:.5}.rule{position:absolute;top:0;bottom:0;left:50%;width:2px;background:#fff;box-shadow:0 0 0 1px #172b4480;display:none;pointer-events:none}.legend{display:flex;gap:20px;flex-wrap:wrap}.legend span:before{content:"";display:inline-block;width:18px;height:3px;margin-right:6px;vertical-align:middle}.cyan:before{background:#007da0}.magenta:before{background:#be2565}.dark:before{background:#352941}footer{max-width:1120px;margin:0 auto;padding:0 24px 28px;font-size:13px}output{min-width:36px;font-variant-numeric:tabular-nums}.status{font-size:13px;color:var(--muted)}@media(max-width:700px){header{padding-top:20px}h1{font-size:23px}.controls{padding:10px 14px}.viewer{padding:0 10px}.stage{width:100%}input[type=range]{width:100px}.control-inner{gap:9px 13px}}
</style>
<header><h1>Our British Columbia — reconstruction review</h1><p>Compare the reconstructed vector with the supplied photograph after approximate perspective correction.</p><p>Working frame: 1000 × 1450. Original physical size and print colours are unverified.</p></header>
<section class="controls" aria-label="Comparison controls"><div class="control-inner">
<label>View <select id="mode"><option value="blend">Opacity overlay</option><option value="wipe">Vertical wipe</option><option value="photo">Corrected photograph</option><option value="vector">Reconstruction</option><option value="geometry">Colour-shape edges</option><option value="lettering">Lettering edges</option></select></label>
<label id="mixlabel">Amount <input id="amount" type="range" min="0" max="100" value="50"><output id="amountout">50%</output></label>
<label>Size <input id="zoom" type="range" min="450" max="1600" value="700" step="50"><output id="zoomout">700</output></label>
<button id="full" type="button">Whole poster</button><button id="title" type="button">Title</button><button id="footer" type="button">Credits</button>
<span id="status" class="status">Photograph beneath; reconstruction at 50% opacity.</span>
</div></section>
<div class="viewer" id="viewer"><div class="stage" id="stage"><img id="base" alt="Perspective-corrected reference photograph"><img id="top" class="top" alt="Vector reconstruction overlay"><div class="rule" id="rule"></div></div></div>
<footer><div class="legend"><span class="cyan">Photograph edge</span><span class="magenta">Reconstructed edge</span><span class="dark">Coincident raster edge</span></div><p>Edge views are inspection aids, not fidelity scores. Colour regions are isolated from lettering; enclosed holes are filled for the colour-shape view. The lettering view uses dark pixels in the title and credits. Hatched areas exclude physical holders and magnets from both edge layers. Reflected or faint lettering is retained for inspection, so its extracted edge is less reliable.</p><p>One projective transform cannot remove local paper curl. No automatic alignment or optimization is performed by this viewer. The clean vector intentionally straightens the printed borders and uses a single colour per ink.</p></footer>
<script>
const assets={photo:'__P__',vector:'__V__',geometry:'__G__',lettering:'__L__'};
const mode=document.getElementById('mode'),amount=document.getElementById('amount'),zoom=document.getElementById('zoom'),base=document.getElementById('base'),topImage=document.getElementById('top'),rule=document.getElementById('rule'),stage=document.getElementById('stage'),viewer=document.getElementById('viewer');
function update(){const m=mode.value,a=Number(amount.value);document.getElementById('amountout').textContent=a+'%';document.getElementById('mixlabel').style.display=['blend','wipe'].includes(m)?'flex':'none';base.src=assets.photo;topImage.src=assets.vector;topImage.style.display='block';topImage.style.opacity='1';topImage.style.clipPath='none';rule.style.display='none';let s='';if(m==='blend'){topImage.style.opacity=a/100;s='Photograph beneath; reconstruction at '+a+'% opacity.';}else if(m==='wipe'){topImage.style.clipPath='inset(0 '+(100-a)+'% 0 0)';rule.style.display='block';rule.style.left=a+'%';s='Reconstruction on the left; photograph on the right.';}else{base.src=assets[m];topImage.style.display='none';s={photo:'Supplied photograph, approximately corrected.',vector:'Reconstructed artwork, clean flat colours.',geometry:'Colour boundaries; lettering holes removed from each colour region.',lettering:'Dark lettering edges; physical holders excluded; glare remains uncertain.'}[m];}document.getElementById('status').textContent=s;}
mode.addEventListener('change',update);amount.addEventListener('input',update);zoom.addEventListener('input',()=>{stage.style.width=zoom.value+'px';document.getElementById('zoomout').textContent=zoom.value;});
document.getElementById('full').onclick=()=>{zoom.value=Math.max(450,Math.min(700,viewer.clientWidth-48));zoom.dispatchEvent(new Event('input'));viewer.scrollTop=0;};
function region(y){zoom.value=1000;zoom.dispatchEvent(new Event('input'));viewer.scrollTop=y;}
document.getElementById('title').onclick=()=>region(720);document.getElementById('footer').onclick=()=>region(1200);update();
</script></html>'''
    for key,data in [('__P__',p),('__V__',v),('__G__',g),('__L__',l)]:doc=doc.replace(key,data)
    out.write_text(doc)

def main():
    p=argparse.ArgumentParser();p.add_argument('rendered_png',type=Path);p.add_argument('--landmarks',type=Path);p.add_argument('--out',type=Path,default=HERE);a=p.parse_args()
    a.out.mkdir(exist_ok=True,parents=True)
    photo=rgb(HERE/'reference_rectified.png');vector=rgb(a.rendered_png)
    if vector.size!=(1000,1450):raise SystemExit(f'Expected 1000x1450 render, received {vector.size}; no silent resizing is allowed.')
    reg=json.loads((HERE/'registration.json').read_text())
    valid_geometry=source_valid_mask(reg,False);valid_lettering=source_valid_mask(reg,False)
    p_shapes=colour_shapes(photo);v_shapes=colour_shapes(vector)
    pe=np.any(np.array([edge(x) for x in p_shapes]),axis=0);ve=np.any(np.array([edge(x) for x in v_shapes]),axis=0)
    geometry=edge_composite(pe,ve,valid_geometry)
    pa=np.asarray(photo).astype(float);va=np.asarray(vector).astype(float)
    # Threshold only in the title and footer domains, never in the blue field.
    title=np.zeros((1450,1000),bool);title[750:1178,85:920]=True
    footer=np.zeros((1450,1000),bool);footer[1223:,:]=True
    domain=title|footer
    pdark=((pa[...,0]<190)&(pa[...,1]<175)&(pa[...,2]<175)&title&ndimage.binary_erosion(v_shapes[2],iterations=12))|((pa[...,0]<175)&(pa[...,1]<175)&(pa[...,2]<175)&footer)
    vdark=((va[...,0]<190)&(va[...,1]<175)&(va[...,2]<175)&title&ndimage.binary_erosion(v_shapes[2],iterations=3))|((va[...,0]<175)&(va[...,1]<175)&(va[...,2]<175)&footer)
    lettering=edge_composite(edge(pdark),edge(vdark),valid_lettering)
    # Keep a title-only edge view available at full resolution.
    geometry.save(a.out/'geometry-edges.png');lettering.save(a.out/'lettering-edges.png')
    blend=Image.blend(photo,vector,.5)
    labelled(blend,'50% overlay','Corrected photograph + reconstructed vector; no local fitting.').save(a.out/'overlay-50.png')
    labelled(geometry,'Colour-shape edge comparison','Cyan: photograph | Magenta: reconstruction | Dark: coincident edges').save(a.out/'geometry-edge-review.png')
    labelled(lettering.crop((75,730,930,1185)),'Title-lettering edge comparison','Cyan: photograph | Magenta: reconstruction | Dark: coincident edges').save(a.out/'title-edge-review.png')
    # Compact three-panel plate suitable for visual review in chat or a report.
    scale=.6;pw,ph=600,870;sheet=Image.new('RGB',(pw*3+80,ph+170),'#f7f6f2');d=ImageDraw.Draw(sheet)
    d.text((20,15),'OUR BRITISH COLUMBIA — RECONSTRUCTION COMPARISON',font=font(26,True),fill='#172b44')
    d.text((20,53),'Approximate perspective registration • 1000 × 1450 working artboard • Uncalibrated photograph',font=font(17),fill='#53606a')
    for i,(im,title) in enumerate([(photo,'Corrected photograph'),(vector,'Reconstructed vector'),(blend,'50% overlay')]):
        x=20+i*(pw+20);d.text((x,91),title,font=font(19,True),fill='#172b44');sheet.paste(im.resize((pw,ph),Image.Resampling.LANCZOS),(x,124))
    d.text((20,ph+137),'Paper curl, magnets, glare, unknown original dimensions and tiny obscured credits limit exact comparison.',font=font(16),fill='#53606a')
    sheet.save(a.out/'comparison-overview.png')
    write_review_html(photo,vector,geometry,lettering,a.out/'interactive-review.html')
    report={'source':str(HERE/'reference_rectified.png'),'reconstruction':str(a.rendered_png.resolve()),'render_sha256':hashlib.sha256(a.rendered_png.read_bytes()).hexdigest(),'artboard':[1000,1450],'automatic_fitting':False,'numeric_fidelity_score':None,'method':'Manually registered photo; separate colour-shape and dark-lettering edge views. No artwork optimization.', 'limitations':reg['cautions']}
    if a.landmarks:
        v=json.loads(a.landmarks.read_text())
        if 'rectified_landmarks' in v:v=v['rectified_landmarks']
        key='yellow_boundary_white_stroke_centre';src=np.asarray(reg['rectified_landmarks'][key]);dst=np.asarray(v[key])
        if src.shape!=dst.shape:raise SystemExit(f'Anchor shapes differ {src.shape} vs {dst.shape}; no inferred correspondence.')
        residual=dst-src;dist=np.sqrt((residual**2).sum(axis=1))
        report['selected_anchor_residuals']={'definition':'Vector centreline vertex minus manually selected photo centreline vertex, in the 1000x1450 frame. Includes perspective/curl/measurement uncertainty.','count':len(dist),'median_distance_units':round(float(np.median(dist)),3),'maximum_distance_units':round(float(np.max(dist)),3),'vertices':[{'index':i,'photo':s.tolist(),'vector':d.tolist(),'dx':round(float(r[0]),3),'dy':round(float(r[1]),3),'distance':round(float(n),3)} for i,(s,d,r,n) in enumerate(zip(src,dst,residual,dist))]}
    (a.out/'comparison-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'outputs':[str(a.out/x) for x in ['comparison-overview.png','overlay-50.png','geometry-edge-review.png','title-edge-review.png','interactive-review.html','comparison-report.json']],'anchor_residuals':report.get('selected_anchor_residuals',{}).get('median_distance_units')},indent=2))

if __name__=='__main__':main()
