"""Assemble the reviewed historic identity reconstructions and visual evidence."""
from pathlib import Path
import copy, json, shutil, re, html
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, distance_transform_edt
import cairosvg
from lxml import etree

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
PKG=OUT/'package'
NS='http://www.w3.org/2000/svg'
INK='#213D34'
PAPER='#F4F2E8'
ITEMS=[
 dict(key='department',file='01_Department_Recreation_Conservation',name='Recreation and Conservation',lines=['Department of Recreation','and Conservation'],svg='components/core/department.svg',ref='components/core/department_reference.png',source='1973 report, PDF 144 / AA143'),
 dict(key='fishwildlife',file='02_Fish_and_Wildlife',name='Fish and Wildlife',lines=['Fish and Wildlife','Branch'],svg='components/fishwildlife/fishwildlife.svg',ref='components/fishwildlife/reference.png',source='1971 report, PDF 16 / DD15'),
 dict(key='parks',file='03_Provincial_Parks',name='Provincial Parks',lines=['Provincial Parks','Branch'],svg='components/core/parks.svg',ref='components/core/parks_reference.png',source='1971 report, PDF 64 / DD63'),
 dict(key='museum',file='04_BC_Provincial_Museum',name='British Columbia Provincial Museum',lines=['British Columbia','Provincial Museum'],svg='components/museum/museum.svg',ref='components/museum/source_crop.png',source='1971 report, PDF 98 / DD97'),
 dict(key='fisheries',file='05_Commercial_Fisheries_Marine_Resources',name='Commercial Fisheries / Marine Resources',lines=['Commercial Fisheries','later Marine Resources'],svg='components/core/fisheries.svg',ref='components/core/fisheries_reference.png',source='1973 report, PDF 144 / AA143'),
]

def inner_svg(path,prefix='',color=None):
    tree=etree.parse(str(path));root=tree.getroot()
    id_map={e.get('id'):prefix+e.get('id') for e in root.iter() if e.get('id')}
    for e in root.iter():
        if e.get('id'):e.set('id',id_map[e.get('id')])
        for a,v in list(e.attrib.items()):
            if v.startswith('#') and v[1:] in id_map:e.set(a,'#'+id_map[v[1:]])
            elif 'url(#' in v:
                for old,new in id_map.items():v=v.replace('url(#'+old+')','url(#'+new+')')
                e.set(a,v)
            elif color and a in ('fill','stroke') and v.lower() in ('black','#000000','#000'):e.set(a,color)
    return ''.join(etree.tostring(e,encoding='unicode') for e in root if etree.QName(e).localname not in ('title','desc','metadata'))

def root_svg(width,height,body,title):
    return f'<svg xmlns="{NS}" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{html.escape(title)}</title>{body}</svg>'

def text(x,y,s,size=28,color=INK,weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>'

def make_overview():
    body=f'<rect width="2400" height="930" fill="{PAPER}"/>'
    body+=text(85,73,'BRITISH COLUMBIA  /  HISTORICAL IDENTITY STUDY',22,weight=600)
    body+=text(80,167,'Recreation & Conservation',76,weight=600)
    body+=text(85,222,'Five reconstructed symbols • Family documented in the 1971 report, printed in 1972',28)
    body+='<path d="M85 266H2315" stroke="#B7C0B3" stroke-width="2"/>'
    for i,item in enumerate(ITEMS):
        x=85+i*455
        body+=text(x,321,f'0{i+1}',20,color='#758271')
        body+=f'<g transform="translate({x+32} 362) scale(.355)">{inner_svg(ROOT/item["svg"],item["key"]+"-",INK)}</g>'
        for j,line in enumerate(item['lines']):body+=text(x+210,777+j*36,line,28,weight=600,anchor='middle')
    body+='<path d="M85 861H2315" stroke="#B7C0B3" stroke-width="2"/>'
    body+=text(85,900,'Editable SVG geometry • Source comparisons and historical notes included',22)
    body+=text(2315,900,'RECONSTRUCTIONS / 2026',19,anchor='end',color='#758271')
    s=root_svg(2400,930,body,'Recreation and Conservation: five reconstructed identities')
    (OUT/'BC_Recreation_Conservation_Five_Logos.svg').write_text(s)
    cairosvg.svg2png(bytestring=s.encode(),write_to=str(OUT/'BC_Recreation_Conservation_Five_Logos.png'))
    # Original stack proportions: four smaller branches and a larger department device.
    body=''
    for j,item in enumerate(ITEMS[1:]):
        body+=f'<g id="stack-{item["key"]}" transform="translate(0 {j*680}) scale(.6)">{inner_svg(ROOT/item["svg"],"stack-"+item["key"]+"-")}</g>'
    body+=f'<g id="stack-department" transform="translate(0 2740)">{inner_svg(ROOT/ITEMS[0]["svg"],"stack-department-")}</g>'
    s=root_svg(1000,3740,body,'Four branch marks above the Department of Recreation and Conservation symbol')
    (OUT/'BC_Recreation_Conservation_Family_Stack.svg').write_text(s)
    cairosvg.svg2pdf(bytestring=s.encode(),write_to=str(PKG/'pdf'/'Family_Stack.pdf'))

def comparisons():
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    board=Image.new('RGB',(1800,3310),PAPER);d=ImageDraw.Draw(board)
    d.text((58,30),'SOURCE / RECONSTRUCTION / REGISTERED OVERLAY',font=font,fill=INK)
    d.text((58,73),'Pink: source ink only   Blue: vector ink only   Dark: shared ink',font=small,fill=INK)
    metrics={}
    for i,item in enumerate(ITEMS):
        key=item['key'];source=Image.open(ROOT/item['ref']).convert('L').resize((1000,1000))
        a=np.array(source);src=gaussian_filter((255-a)/255,.8)>.5
        vecim=Image.open(PKG/'png'/(item['file']+'.png')).convert('RGBA')
        tgt=np.array(vecim)[:,:,3]>.5*255
        valid=np.ones(src.shape,bool)
        if key=='fishwildlife':valid[485:502,80:940]=False
        # Exclude the reproduction rule through the deer/fish, and only that rule.
        overlay=np.full((1000,1000,3),255,np.uint8)
        overlay[src&valid]=[235,74,114]
        overlay[tgt&valid]=[50,160,207]
        overlay[src&tgt&valid]=[39,49,59]
        overlay[~valid]=[232,230,219]
        im=Image.fromarray(overlay);im.save(PKG/'review'/f'{key}_overlay.png')
        source.save(PKG/'review'/f'{key}_reference.png')
        srcv=src&valid;tgtv=tgt&valid
        interior=np.zeros_like(valid);interior[100:900,100:900]=True;interior&=valid
        metrics[key]={'whole_ink_IoU':round(float((srcv&tgtv).sum()/(srcv|tgtv).sum()),4),
                      'interior_ink_IoU':round(float((src&tgt&interior).sum()/((src|tgt)&interior).sum()),4),
                      'source':item['source'],
                      'note':'Ink overlap to a small printed scan, not a percentage of historical accuracy. Whole score includes frame.',
                      'registration':'Tight bounding boxes independently scaled to1000-square; no local warp.',
                      'scan_rule_excluded':key=='fishwildlife'}
        y=138+i*630;d.text((58,y),f'{i+1:02d}  {item["name"]}',font=font,fill=INK)
        d.text((58,y+38),item['source'],font=small,fill='#657366')
        white=Image.alpha_composite(Image.new('RGBA',(1000,1000),'white'),vecim).convert('RGB')
        for j,img in enumerate([source.convert('RGB'),white,im]):board.paste(img.resize((490,490)),(58+j*585,y+82))
        if key=='fishwildlife':d.text((58,y+580),'Pale band in overlay: excluded reproduction rule; the reconstructed linework remains continuous.',font=small,fill='#657366')
    board.save(OUT/'BC_Recreation_Conservation_Overlay_Review.png')
    (PKG/'review'/'comparison_metrics.json').write_text(json.dumps(metrics,indent=2))
    return metrics

def main():
    OUT.mkdir(exist_ok=True)
    for sub in ('svg','svg/reversed','pdf','png','review','research','construction/core','construction/museum','construction/fishwildlife'):(PKG/sub).mkdir(parents=True,exist_ok=True)
    for item in ITEMS:
        raw=(ROOT/item['svg']).read_text();target=PKG/'svg'/(item['file']+'.svg');target.write_text(raw)
        # Convenient copies outside the package are the individually linked files.
        (OUT/(item['file']+'.svg')).write_text(raw)
        rev=raw.replace('#000000','#FFFFFF')
        (PKG/'svg'/'reversed'/(item['file']+'_White.svg')).write_text(rev)
        cairosvg.svg2pdf(bytestring=raw.encode(),write_to=str(PKG/'pdf'/(item['file']+'.pdf')))
        cairosvg.svg2png(bytestring=raw.encode(),write_to=str(PKG/'png'/(item['file']+'.png')),output_width=1000,output_height=1000)
    make_overview();metrics=comparisons()
    for f in ('BC_Recreation_Conservation_Five_Logos.svg','BC_Recreation_Conservation_Five_Logos.png','BC_Recreation_Conservation_Family_Stack.svg','BC_Recreation_Conservation_Overlay_Review.png'):shutil.copy(OUT/f,PKG/f)
    shutil.copy(ROOT/'research/history.md',PKG/'research'/'Historical_Findings.md')
    shutil.copy(ROOT/'research/Related_Report_Graphics_Source_Sheet.png',OUT/'Related_Report_Graphics_Source_Sheet.png')
    for f in ('Related_Report_Graphics_Source_Sheet.png','1971_proposed_park_symbols_crop.png','1973_parks_shield_crop.png','1973_fw_replacement_crop.png'):shutil.copy(ROOT/'research'/f,PKG/'research'/f)
    for folder,files in {'core':['build_core.py','reference_meta.json','metrics_v1.json'], 'museum':['build_museum.py','NOTES.md','metrics.json'], 'fishwildlife':['build_fishwildlife.py','compare_fishwildlife.py','README.md','metrics.json']}.items():
        for f in files:shutil.copy(ROOT/'components'/folder/f,PKG/'construction'/folder/f)
    # Preserve the reference files expected by construction scripts.
    for f in (ROOT/'components/core').glob('*_reference*.png'):shutil.copy(f,PKG/'construction/core'/f.name)
    for f in ['source_crop.png','source_forgov_1971_native.png']:shutil.copy(ROOT/'components/museum'/f,PKG/'construction/museum'/f)
    for f in ['reference.png','report_reference.png']:shutil.copy(ROOT/'components/fishwildlife'/f,PKG/'construction/fishwildlife'/f)
    manifest={'title':'British Columbia Department of Recreation and Conservation identity family','created':'2026-11-21','status':'historical geometric reconstructions, not recovered original artwork','symbols':ITEMS,'metrics':metrics}
    (PKG/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
