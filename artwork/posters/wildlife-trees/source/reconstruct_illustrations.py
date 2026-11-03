"""Source-guided vector rebuilding for the habitat tree and portrait context.

Major contours, feature partitions and exclusion areas are authored against the
reference. Actual penwork is reconstructed as fitted, measured-width Bezier
stroke envelopes. No procedural hatch pattern or bitmap is embedded in assets.
"""
from pathlib import Path
from collections import defaultdict
import json,copy,subprocess,sys,math,time
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from lxml import etree as E
from penwork import thin,paths_from_skeleton,stroke_envelope,measure_ink,NS,INK

ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'_work';TMP.mkdir(exist_ok=True,parents=True)
ASSETS=ROOT/'assets'
INKSCAPE='http://www.inkscape.org/namespaces/inkscape'
NSMAP={None:NS,'inkscape':INKSCAPE}
REG=json.loads((ROOT/'source/source-registration.json').read_text())
SCALE=REG['native_pixels_per_poster_unit']
PIX_TO_POSTER=1/SCALE
SOURCE=ROOT/'reference/reference-native.jpg'

def node(tag,**attrs):return E.Element('{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def add(parent,tag,**attrs):n=node(tag,**attrs);parent.append(n);return n

def write_xml(r,path):
    q=path.with_suffix(path.suffix+'.writing');q.write_bytes(E.tostring(r,encoding='utf-8',xml_declaration=True));q.replace(path)

def render(svg,png,width,height=None):
    fresh=png.with_name(png.stem+'-rendering.png')
    if fresh.exists():fresh.unlink()
    cmd=['inkscape',str(svg),'--export-type=png','--export-filename='+str(fresh),'--export-width='+str(width)]
    if height:cmd+=['--export-height='+str(height)]
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with Image.open(fresh) as im:im.load()
    fresh.replace(png)

def render_shape(d,viewbox,pixels,name,stroke=None,stroke_width=None):
    r=E.Element('{'+NS+'}svg',nsmap={None:NS},viewBox=' '.join(map(str,viewbox)))
    attrs={'d':d,'fill':'white' if stroke is None else 'none'}
    if stroke is not None:attrs.update(stroke='white',stroke_width=stroke_width)
    add(r,'path',**attrs)
    p=TMP/(name+'.svg');write_xml(r,p);render(p,p.with_suffix('.png'),*pixels)
    return np.asarray(Image.open(p.with_suffix('.png')).convert('RGBA'))[:,:,3]>127

def render_regions(regions,viewbox,pixels,name):
    r=E.Element('{'+NS+'}svg',nsmap={None:NS},viewBox=' '.join(map(str,viewbox)))
    step=max(1,int(245/(len(regions)+1)))
    for i in reversed(range(len(regions))):add(r,'path',d=regions[i]['path'],fill=f'rgb({(i+1)*step},0,255)')
    p=TMP/(name+'-regions.svg');write_xml(r,p);render(p,p.with_suffix('.png'),*pixels)
    ar=np.asarray(Image.open(p.with_suffix('.png')).convert('RGBA'))
    labels=np.clip(np.rint(ar[:,:,0]/step),0,len(regions)).astype(np.int16);labels[ar[:,:,3]<128]=0
    return labels

def split_regions(chain,labels):
    ix=np.clip(chain[:,0].astype(int),0,labels.shape[1]-1);iy=np.clip(chain[:,1].astype(int),0,labels.shape[0]-1)
    ids=labels[iy,ix];changes=np.flatnonzero(ids[1:]!=ids[:-1])+1
    for st,en in zip(np.r_[0,changes],np.r_[changes,len(chain)]):yield int(ids[st]),chain[max(0,st-1):min(len(chain),en+1)]

def fitted_paths(plate,labels,region_ids,sx,sy):
    dist=ndi.distance_transform_edt(plate);sk=thin(plate);chains=paths_from_skeleton(sk);result=defaultdict(list)
    for ch in chains:
        for rid,part in split_regions(ch,labels):
            ix=np.clip(part[:,0].astype(int),0,plate.shape[1]-1);iy=np.clip(part[:,1].astype(int),0,plate.shape[0]-1)
            radii=np.maximum(.48,dist[iy,ix]+.05)
            result[region_ids[rid-1] if rid else 'other-original-ink'].append(stroke_envelope(part,radii,sx,sy))
    return result,{'source_ink_pixels':int(plate.sum()),'medial_samples':int(sk.sum()),'stroke_chains':len(chains),'vector_paths':sum(len(x) for x in result.values())}

def captions():
    layout=json.loads((ROOT/'source/panel-layout.json').read_text())
    return layout['caption_exclusions']

def mask_rect(mask,global_box,tile_box):
    x0,y0,x1,y1=map(round,global_box);tx,ty,tx1,ty1=tile_box
    xx0=max(x0,tx)-tx;xx1=min(x1,tx1)-tx;yy0=max(y0,ty)-ty;yy1=min(y1,ty1)-ty
    if xx1>xx0 and yy1>yy0:mask[yy0:yy1,xx0:xx1]=False

def tree_regions():
    regs=[];whites=[];notes=[]
    for part in ['upper','lower']:
        p=ROOT/'source'/f'tree-{part}-regions.json'
        if p.exists():
            d=json.loads(p.read_text());regs+=d['regions'];whites+=d.get('white_base_paths',[]);notes+=d.get('notes',[])
    return regs,whites,notes

def tree():
    source=Image.open(SOURCE).convert('RGB')
    regions,whites,notes=tree_regions();assert regions,'Measured feature regions required before tree build'
    # Native-pixel boundaries ensure exact source registration.
    bounds=[round(v*SCALE) for v in [40,130,975,1970]]
    x0,y0,x1,y1=bounds;core_height=900;halo=64
    root=E.Element('{'+NS+'}svg',nsmap=NSMAP,viewBox='0 0 1000 1985',width='1000',height='1985',version='1.1')
    add(root,'title').text='Wildlife habitat tree — reconstructed original penwork'
    add(root,'desc').text='Manually partitioned original crown, branches, nest, broken limbs, cavities, fungi, roots and forest floor, rebuilt as editable fitted Bezier ink paths. Source-visible parts retained; no hidden branches invented.'
    defs=add(root,'defs')
    white=add(root,'g',id='solid-wood-white',fill='white');white.set('{'+INKSCAPE+'}groupmode','layer');white.set('{'+INKSCAPE+'}label','Solid wood white — removable')
    for i,p in enumerate(whites):add(white,'path',id=p.get('id','wood-white-'+str(i)),d=p.get('path',p.get('d')))
    # All ink is already isolated. Named groups make large tree features editable.
    named={};order=[x['id'] for x in regions]+['other-original-ink']
    for rid in order:
        if rid in named:continue
        g=add(root,'g',id=rid,fill=INK);g.set('{'+INKSCAPE+'}groupmode','layer');g.set('{'+INKSCAPE+'}label',rid.replace('-',' ').capitalize());named[rid]=g
    stats=[];exclusions=[p['native_bbox'] for p in REG['portraits']]+[[v*SCALE for v in c['bbox']] for c in captions()]
    total=math.ceil((y1-y0)/core_height)
    for tile,core_y0 in enumerate(range(y0,y1,core_height)):
        core_y1=min(y1,core_y0+core_height);ty0=max(y0,core_y0-halo);ty1=min(y1,core_y1+halo)
        box=[x0,ty0,x1,ty1];im=source.crop(box);ink,density=measure_ink(im);allowed=np.ones(ink.shape,bool)
        for b in exclusions:mask_rect(allowed,b,box)
        plate=ink&allowed
        vb=[x0/SCALE,ty0/SCALE,(x1-x0)/SCALE,(ty1-ty0)/SCALE]
        labels=render_regions(regions,vb,im.size,'tree-'+str(tile))
        paths,st=fitted_paths(plate,labels,[r['id'] for r in regions],PIX_TO_POSTER,PIX_TO_POSTER)
        clip=add(defs,'clipPath',id='tree-tile-'+str(tile),clipPathUnits='userSpaceOnUse')
        add(clip,'rect',x=x0/SCALE,y=core_y0/SCALE,width=(x1-x0)/SCALE,height=(core_y1-core_y0)/SCALE)
        for rid,ds in paths.items():
            g=add(named[rid],'g',id=rid+'-tile-'+str(tile),clip_path=f'url(#tree-tile-{tile})')
            inner=add(g,'g',transform=f'translate({x0/SCALE:.9f} {ty0/SCALE:.9f})')
            for j,d in enumerate(ds):add(inner,'path',id=f'{rid}-{tile}-{j}',d=d)
        st.update({'tile':tile,'core_native_bbox':[x0,core_y0,x1,core_y1],'halo_native_pixels':halo});stats.append(st)
        print('TREE',tile+1,'/',total,st,flush=True)
    for rid,g in list(named.items()):
        if not len(g):root.remove(g)
    meta={'source':'Wildlife Trees.pdf supplied by user','source_pixels':REG['source_pixels'],'native_pixels_per_poster_unit':SCALE,'method':'Manually measured structural regions and source-guided, variable-width Bezier reconstruction of the original penwork. No procedural hatching. Native-pixel tiles with 64-pixel overlaps and vector clipping.','notes':notes,'tiles':stats,'source_exclusions':exclusions,'regions':[r['id'] for r in regions]}
    add(root,'metadata').text=json.dumps(meta)
    out=ASSETS/'wildlife-habitat-tree.svg';write_xml(root,out);render(out,ASSETS/'wildlife-habitat-tree.png',1600)
    (ROOT/'source/tree-vector-manifest.json').write_text(json.dumps(meta,indent=2));print('Tree SVG complete.',flush=True)

def panel_context(key):
    reg=next(x for x in REG['portraits'] if x['key']==key);source=Image.open(SOURCE).convert('RGB').crop(reg['native_bbox'])
    animal=E.parse(str(ASSETS/(reg['slug']+'.svg'))).getroot();meta=json.loads(animal.find('{'+NS+'}metadata').text)
    vw,vh=meta['source_viewBox'][2:];d=animal.xpath('//*[@id="visible-animal-contour"]/*')[0].get('d')
    animal_mask=render_shape(d,[0,0,vw,vh],source.size,key+'-animal-visible')
    ink,density=measure_ink(source);plate=ink&~animal_mask
    # Measured frame rule is removed from the ink plate and redrawn as geometry
    # during poster assembly. Other original scene marks are preserved.
    layout_path=ROOT/'source/panel-layout.json'
    if layout_path.exists():
        layout=json.loads(layout_path.read_text());rows=layout.get('panels',layout.get('portraits',[]));panel=next((p for p in rows if p.get('key')==key),None)
        if panel:
            fp=panel.get('frame_path')
            if fp:
                bx,by,bx1,by1=reg['poster_bbox'];fmask=render_shape(fp,[bx,by,bx1-bx,by1-by],source.size,key+'-frame-rule',stroke='white',stroke_width=panel.get('frame_removal_width',1.05))
                plate&=~fmask
    label=np.ones(plate.shape,np.int16)
    paths,stats=fitted_paths(plate,label,['original-panel-context'],vw/source.width,vh/source.height)
    root=E.Element('{'+NS+'}svg',nsmap=NSMAP,viewBox=f'0 0 {vw} {vh}',width=str(vw),height=str(vh),version='1.1')
    add(root,'title').text=reg['slug']+' — original surrounding illustration'
    add(root,'desc').text='Original branches, trunk, cavity or ground surrounding the isolated animal, rebuilt as editable vector ink. The animal and clean frame are separate in the assembled poster.'
    g=add(root,'g',id='original-context',fill=INK)
    for rid,ds in paths.items():
        for j,d in enumerate(ds):add(g,'path',id=key+'-context-'+str(j),d=d)
    add(root,'metadata').text=json.dumps({'key':key,'source_viewBox':[0,0,vw,vh],'native_bbox':reg['native_bbox'],'poster_bbox':reg['poster_bbox'],'counts':stats})
    out=ASSETS/(reg['slug']+'-context.svg');write_xml(root,out);render(out,TMP/(key+'-context.png'),source.width,source.height)
    print('CONTEXT',key,stats,flush=True)

if __name__=='__main__':
    if sys.argv[1:] and sys.argv[1]=='tree':tree()
    else:
        for key in sys.argv[1:] or ['hawk','owl','squirrel','chickadee','bear','toad']:panel_context(key)
