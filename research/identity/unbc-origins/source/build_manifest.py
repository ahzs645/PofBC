"""Refresh asset metadata from the generated source records and SVG masters."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];NS='{http://www.w3.org/2000/svg}'
target=ROOT/'asset-manifest.json'
data=json.loads(target.read_text()) if target.exists() else {}
byid={a['id']:a for a in data.get('assets',[])}
for name in ['core_manifest.json','application_manifest.json','campaign_metadata.json','forms_metadata.json','illustration_metadata.json','sweatshirt_metadata.json']:
    path=ROOT/'source'/name
    if not path.exists():continue
    obj=json.loads(path.read_text())
    if isinstance(obj,list):entries=obj
    elif 'assets' in obj:entries=obj['assets']
    elif 'id' in obj or 'file' in obj:entries=[obj]
    elif name=='illustration_metadata.json':entries=[dict(obj,id='ius-graduates-interpretive')]
    else:entries=[]
    for item in entries:
        if not isinstance(item,dict):continue
        ident=item.get('id') or item.get('asset') or Path(item.get('file','')).stem
        if ident:
            update=dict(item,id=ident)
            if 'source' in update:
                update['sources']=update['source'] if isinstance(update['source'],list) else [update['source']]
            byid.setdefault(ident,{}).update(update)
assets=[]
for path in sorted((ROOT/'svg').glob('*.svg')):
    r=ET.parse(path).getroot();entry=byid.get(path.stem,{'id':path.stem})
    entry.update(id=path.stem,title=r.findtext(NS+'title'),description=r.findtext(NS+'desc'),viewBox=r.get('viewBox'),
                 files={e:f'{e}/{path.stem}.{e}' for e in ['svg','pdf','eps','png']},
                 sha256_svg=hashlib.sha256(path.read_bytes()).hexdigest())
    assets.append(entry)
data.update(title='Interior University Society Vector Brand Kit',version='1.2',asset_count=len(assets),
            method='Outlined typography, manually constructed geometry, and deliberately drawn curves. No bitmap tracing or embedded images in production masters.',
            font_review='IUS_Font_Review.pdf',font_schedule='FONT_NOTES.md',assets=assets)
target.write_text(json.dumps(data,indent=2))
print('Updated manifest:',len(assets),'assets, version 1.2')
