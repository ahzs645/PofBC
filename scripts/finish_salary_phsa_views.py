#!/usr/bin/env python3
"""Add source-native field views without modifying any frozen review batch."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
CACHE=Path('/tmp/queue-completion-phsa')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def views(manifest_path):
    from PIL import Image,ImageDraw,ImageFont
    original=json.loads(manifest_path.read_text());key=original['sourceId'];batch=original['batch']
    profile=json.loads((AREA/(key+'-processing-profile-001.json')).read_text())
    out=manifest_path.with_name(manifest_path.name.replace('-images.json','-target-views.json'))
    if out.exists():raise ValueError('Target-view evidence is already frozen')
    folder=CACHE/key/'review-images'/(batch+'-target-views');folder.mkdir(parents=True,exist_ok=True)
    crops={field:[] for field in ['name','remuneration','expenses']};rows=[]
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
    except OSError:font=ImageFont.load_default()
    for r in original['rows']:
        full=Path(r['cropPath'])
        if sha(full.read_bytes())!=r['cropSha256']:raise ValueError('Frozen full-row source context changed')
        image=Image.open(full).convert('RGB');x0,y0,x1,y1=r['cropRectOriginal300DpiPixels'];target=[]
        for field in r['reviewTargetFields']:
            if field=='name':left,right=x0,min(x1,profile['namePayBoundary'])
            elif field=='remuneration':left,right=max(x0,profile['namePayBoundary']-8),min(x1,profile['payExpenseBoundary']+8)
            elif field=='expenses':left,right=max(x0,profile['payExpenseBoundary']-8),x1
            else:raise ValueError('Unknown source field view')
            rect=[left-x0,0,right-x0,image.height];crop=image.crop(rect)
            path=folder/f'{r["sequence"]:04d}-{field}.png';crop.save(path)
            view={'field':field,'path':str(path),'sha256':sha(path.read_bytes()),
                  'originalPdf300DpiPixelBox':[left,y0,right,y1],'noResamplingOrGlyphAlteration':True}
            target.append(view);crops[field].append((r['sequence'],r['physicalPage'],r['sourceRowOnPage'],crop))
        rows.append({**r,'sourceNativeTargetViews':target,
                     'fullRowContextRemainsAuthoritativeCropSha256':r['cropSha256']})
    sheets=[]
    for field,entries in crops.items():
        for offset in range(0,len(entries),10):
            group=entries[offset:offset+10];width=max(im.width for _,_,_,im in group)
            height=sum(im.height+38 for _,_,_,im in group);sheet=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(sheet);y=0
            for sequence,pn,rn,crop in group:
                draw.text((0,y+3),f'{sequence:04d} | p{pn} row {rn} | {field}',fill='black',font=font)
                sheet.paste(crop,(0,y+38));y+=crop.height+38
            path=folder/f'{field}-sheet-{offset//10+1:03d}.png';sheet.save(path)
            sheets.append({'field':field,'path':str(path),'sha256':sha(path.read_bytes()),
                           'sequences':[x[0] for x in group],'noSourcePixelsResampled':True})
    packet={'frozen':True,'date':'2026-11-01','sourceId':key,'sourceSha256':original['sourceSha256'],
            'batch':batch,'assignedReviewer':original['assignedReviewer'],'rowsToReview':len(rows),
            'originalImageManifest':{'path':str(manifest_path.relative_to(ROOT)),'sha256':sha(manifest_path.read_bytes())},
            'fullBatchPath':original['fullBatchPath'],'fullBatchSha256':original['fullBatchSha256'],
            'sourceNativeFieldViews':'Name-only source columns and separate monetary columns, without resampling, retyping or hidden candidate values. Original full-row/PDF hash/context retained.',
            'instructions':original['instructions']+[
                'Use these narrower native-pixel field sheets for the requested fields. Original individual full-row crops or the actual PDF remain available for context.',
                'Only requested fields need transcription. literalImageName may be null on a money-only resolution; do not widen its field scope.',
                'The ordinary seven-key resolution cropSha256 remains the ORIGINAL full-row crop hash in each row, not an optional display-view hash. Pin this additional target-view manifest separately.',
                'Root source-typography policy addendum permits explicitly qualified I/l cases with visible alternatives/context; exact case peer/root adoption and source publicWarning remain required.'
            ],'rows':rows,'contactSheets':sheets,'originalFrozenBatchAndCropsUnchanged':True}
    out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'targetViewManifest':str(out.relative_to(ROOT)),'sha256':sha(out.read_bytes()),'rows':len(rows),'contactSheets':len(sheets)}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--images',required=True);views(ROOT/p.parse_args().images)
