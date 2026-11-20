"""Fixed-layout in-sample overlap diagnostics; no contour tracing or local fitting."""
from pathlib import Path
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess
import numpy as np
from scipy.ndimage import label,find_objects,binary_erosion,distance_transform_edt
from PIL import Image
from lxml import etree as ET

PACKAGE=Path(__file__).resolve().parent.parent
HERE=PACKAGE/'references'
ROOT=PACKAGE/'svg'
OUT=PACKAGE/'analysis'/'metrics'
OUT.mkdir(exist_ok=True)
SVG='http://www.w3.org/2000/svg'
parser=argparse.ArgumentParser()
parser.add_argument('--include-closed-panel',action='store_true')
parser.add_argument('--shared-masters',action='store_true',help='Compare the one-alphabet alternative, preserving the same letter placement and x/y scaling.')
args=parser.parse_args()
if args.shared_masters:
    OUT=PACKAGE/'analysis'/'metrics-shared-masters'
    OUT.mkdir(exist_ok=True)
SUFFIX='-shared-masters' if args.shared_masters else ''
registration=json.loads((PACKAGE/'analysis'/'registration.json').read_text())
measurements=json.loads((PACKAGE/'analysis'/'source-measurements.json').read_text())
MAIN=('FOREST','CLOSURE','BOUNDARY','ZONE','3')
ID={'FOREST':'word-forest','CLOSURE':'word-closure','BOUNDARY':'word-boundary','ZONE':'word-zone','3':'word-zone-number'}
COLORS={'source_only':[0,174,201],'vector_only':[218,43,145],'overlap':[25,35,44],'background':[255,255,255]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def otsu(gray):
    histogram=np.bincount(gray.ravel(),minlength=256).astype(float)
    probability=histogram/histogram.sum()
    cumulative=np.cumsum(probability)
    moment=np.cumsum(np.arange(256)*probability)
    variance=(moment[-1]*cumulative-moment)**2/(cumulative*(1-cumulative)+1e-15)
    return int(np.argmax(variance))


def matrix_svg(matrix):
    return 'matrix('+','.join(f'{v:.12g}' for v in [matrix[0,0],matrix[1,0],matrix[0,1],matrix[1,1],matrix[0,2],matrix[1,2]])+')'


def render_fragment(name,path,group_id,size,inverse=None):
    parsed=ET.parse(str(path))
    found=parsed.xpath('//*[@id=$name]',name=group_id)
    if len(found)!=1:
        raise RuntimeError(f'{path.name}: expected one {group_id}, found {len(found)}')
    fragment=deepcopy(found[0])
    root=ET.Element(f'{{{SVG}}}svg',nsmap={None:SVG},viewBox=f'0 0 {size[0]} {size[1]}',width=str(size[0]),height=str(size[1]))
    group=ET.SubElement(root,f'{{{SVG}}}g',fill='#000')
    if inverse is not None:
        group.set('transform',matrix_svg(inverse))
    group.append(fragment)
    # Colour is irrelevant: these are transparent foreground masks, so use alpha.
    fragment_path=OUT/f'{name}_vector_fragment.svg'
    ET.ElementTree(root).write(str(fragment_path),encoding='utf-8',xml_declaration=True)
    png=OUT/f'{name}_vector_4x.png'
    subprocess.run(['inkscape',str(fragment_path),'--export-area-page',f'--export-filename={png}',f'--export-width={size[0]*4}',f'--export-height={size[1]*4}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    alpha=Image.open(png).convert('RGBA').getchannel('A').resize(tuple(size),Image.Resampling.LANCZOS)
    alpha.save(OUT/f'{name}_vector_alpha.png')
    mask=np.asarray(alpha)>=128
    Image.fromarray((mask*255).astype('uint8')).save(OUT/f'{name}_vector_mask.png')
    return mask


def source_mask(gray,roi,threshold,light=False):
    x0,y0,x1,y1=roi
    mask=np.zeros(gray.shape,bool)
    part=gray[y0:y1,x0:x1]
    mask[y0:y1,x0:x1]=part>=threshold if light else part<=threshold
    components,count=label(mask)
    result=np.zeros_like(mask)
    for index,obj in enumerate(find_objects(components)):
        if obj is None:continue
        yy,xx=obj
        region=components[obj]==index+1
        if region.sum()<60 or xx.stop-xx.start<5 or yy.stop-yy.start<20:continue
        result[components==index+1]=True
    return result


def scores(source,vector):
    intersection=int((source&vector).sum());union=int((source|vector).sum())
    source_count=int(source.sum());vector_count=int(vector.sum())
    sb=source&~binary_erosion(source,structure=np.ones((3,3)),border_value=0)
    vb=vector&~binary_erosion(vector,structure=np.ones((3,3)),border_value=0)
    ds=distance_transform_edt(~sb);dv=distance_transform_edt(~vb)
    precision=float(np.mean(ds[vb]<=2)) if vb.any() else 0.
    recall=float(np.mean(dv[sb]<=2)) if sb.any() else 0.
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.
    return {'iou':intersection/union,'dice':2*intersection/(source_count+vector_count),'boundary_precision_2px':precision,'boundary_recall_2px':recall,'boundary_f1_2px':f1,'source_ink_pixels':source_count,'vector_ink_pixels':vector_count,'intersection_pixels':intersection,'union_pixels':union,'source_boundary_pixels':int(sb.sum()),'vector_boundary_pixels':int(vb.sum())}


def output_images(name,source,vector):
    difference=np.full((*source.shape,3),255,dtype='uint8')
    difference[source&~vector]=COLORS['source_only']
    difference[vector&~source]=COLORS['vector_only']
    difference[source&vector]=COLORS['overlap']
    Image.fromarray(difference).save(OUT/f'{name}_difference.png')
    Image.fromarray((source*255).astype('uint8')).save(OUT/f'{name}_source_mask.png')
    for kind,mask,color in [('source',source,COLORS['source_only']),('vector',vector,COLORS['vector_only'])]:
        transparent=np.empty((*mask.shape,4),dtype='uint8')
        transparent[:,:,:3]=color
        transparent[:,:,3]=mask*255
        Image.fromarray(transparent).save(OUT/f'{name}_{kind}_ink.png')


jobs=[]
for word in MAIN:
    frame=np.array(measurements['photos']['open'][word]['local_to_main'])
    filename=f'open_{word}_upright.png' if word in ('FOREST','CLOSURE') else f'open_{word}_crop.png'
    size=Image.open(HERE/filename).size
    jobs.append((word,ROOT/'main-ink-analysis.svg',ID[word],size,np.linalg.inv(frame)))
jobs.append(('OPEN_PANEL',ROOT/f'forest-closure-open{SUFFIX}.svg','open-panel-lettering',tuple(registration['photos']['open']['panel_size']),None))
if args.include_closed_panel:
    jobs.append(('CLOSED_PANEL',ROOT/f'forest-closure-closed{SUFFIX}.svg','closed-panel-lettering',tuple(registration['photos']['closed']['panel_size']),None))
with ThreadPoolExecutor(max_workers=3) as pool:
    masks=dict(zip([job[0] for job in jobs],pool.map(lambda job:render_fragment(*job),jobs)))

results={
    'generated_utc':datetime.now(timezone.utc).isoformat(),
    'classification':'in-sample reconstruction fit, not font identification or independent validation accuracy',
    'artwork_variant':'One shared alphabet with width/height scaling' if args.shared_masters else 'Photograph-fitted local glyph variants',
    'coordinate_system':'Canonical width 1000. Main plate registered by fixed homography; sloping words use fixed rigid coordinate frames. Both status faces share a 1000 by 130 panel convention and have independent photograph homographies. CLOSED uses the revised physical-board boundary, not the photograph bottom edge.',
    'alignment':'The vector was reconstructed using these photographs. No additional per-letter or per-word alignment is performed by this analysis.',
    'foreground':'Main lettering only; triangle, oval, board/background and supports excluded. OPEN panel included. CLOSED panel optional.',
    'source_threshold':'Otsu separately within each fixed photographic text ROI; discard isolated components smaller than 60 pixels or narrower than 5 / shorter than 20 pixels. Threshold sensitivity at Otsu -12, Otsu, Otsu +12.',
    'vector_threshold':'SVG exported by Inkscape at 4x; alpha downsampled with Lanczos, foreground alpha >= 128.',
    'boundary_metric':'8-neighbour inner boundaries (mask minus 3x3 erosion). Precision is fraction of vector boundary within 2 canonical pixels of source boundary, recall reverses roles, F1 is harmonic mean.',
    'difference_colors_rgb':COLORS,
    'inputs_sha256':{p.name:sha(p) for p in [ROOT/'main-ink-analysis.svg',ROOT/f'forest-closure-open{SUFFIX}.svg',ROOT/f'forest-closure-closed{SUFFIX}.svg',PACKAGE/'analysis'/'registration.json']},
    'photos':{}
}

for photo in ('open','closed'):
    photo_result={}
    targets=list(MAIN)+(['OPEN_PANEL'] if photo=='open' else ['CLOSED_PANEL'] if args.include_closed_panel else [])
    for word in targets:
        if word=='OPEN_PANEL':
            path=HERE/'open_panel_rectified.png';roi=(235,7,755,123);light=False
        elif word=='CLOSED_PANEL':
            path=HERE/'closed_panel_rectified.png';roi=(8,18,995,118);light=True
        elif word in ('FOREST','CLOSURE'):
            path=HERE/f'{photo}_{word}_upright.png'
            roi=(60,32,610,142) if word=='FOREST' else (35,20,620,125)
            light=False
        else:
            path=HERE/f'{photo}_{word}_crop.png'
            size=Image.open(path).size
            roi=(4,4,247,91) if word=='ZONE' else (0,0,*size)
            light=False
        gray=np.asarray(Image.open(path).convert('L'))
        x0,y0,x1,y1=roi
        threshold=otsu(gray[y0:y1,x0:x1])
        sensitivity=[]
        for offset in (-12,0,12):
            t=max(0,min(255,threshold+offset))
            source=source_mask(gray,roi,t,light)
            scored=scores(source,masks[word])
            sensitivity.append({'threshold_offset':offset,'threshold':t,**scored})
            if offset==0:
                nominal=scored
                output_images(f'{photo}_{word}',source,masks[word])
        photo_result[word]={'source_filename':path.name,'threshold':threshold,'roi':roi,'nominal':nominal,'threshold_sensitivity':sensitivity,'sensitivity_range':{metric:[min(s[metric] for s in sensitivity),max(s[metric] for s in sensitivity)] for metric in ['iou','dice','boundary_f1_2px']}}
        print(photo,word, 'IoU',f"{nominal['iou']*100:.2f}",'Dice',f"{nominal['dice']*100:.2f}",'boundary F1',f"{nominal['boundary_f1_2px']*100:.2f}",'threshold',threshold)
    results['photos'][photo]=photo_result

results['main_pooled_by_photo']={}
for photo in ('open','closed'):
    records=[results['photos'][photo][word]['nominal'] for word in MAIN]
    source_pixels=sum(r['source_ink_pixels'] for r in records)
    vector_pixels=sum(r['vector_ink_pixels'] for r in records)
    intersection=sum(r['intersection_pixels'] for r in records)
    union=sum(r['union_pixels'] for r in records)
    precision=sum(r['boundary_precision_2px']*r['vector_boundary_pixels'] for r in records)/sum(r['vector_boundary_pixels'] for r in records)
    recall=sum(r['boundary_recall_2px']*r['source_boundary_pixels'] for r in records)/sum(r['source_boundary_pixels'] for r in records)
    results['main_pooled_by_photo'][photo]={'iou':intersection/union,'dice':2*intersection/(source_pixels+vector_pixels),'boundary_f1_2px':2*precision*recall/(precision+recall),'interpretation':'Pooled foreground counts across five main word/number regions; in-sample fit only.'}
(OUT/'quantitative.json').write_text(json.dumps(results,indent=2))
(OUT/'README.md').write_text('''# Fixed-layout overlap diagnostics

These are in-sample fit diagnostics: the same two photographs informed the reconstruction. They do not identify a typeface and are not independent validation accuracy.

quantitative.json records all scores, exact method, thresholds, threshold sensitivity, SVG file hashes and fixed registration assumptions. No local letter or word alignment occurs in this analysis. Each artwork group keeps its published position; only the fixed measurement coordinate frame is inverted to make the sloping word readable.

Difference images: cyan is photographic ink only; magenta is vector ink only; dark is overlap; white is background. Each source and vector bitmap mask is also saved separately. The coloured *_ink.png files have transparency for interactive overlays.

The area measures (IoU and Dice) compare binary ink coverage. Boundary F1 compares both directions of the inner ink boundary within two canonical pixels, after 3x3 binary erosion defines the boundary. Values depend on the photograph threshold, soft print edges, the inferred equilateral layout and camera registration.

Re-run: python3 source/measure_overlap.py
Include revised CLOSED notice: python3 source/measure_overlap.py --include-closed-panel
''')
