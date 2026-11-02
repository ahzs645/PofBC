#!/usr/bin/env python3
"""Deterministic blind actual-source holdout, configured before row selection."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

import finish_salary_phsa_policy as policy

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
CONFIG=AREA/'holdout-selection-config-001.json'
CONFIG_SHA='fa3689b3b361f5c431707e7ed517ebdff4080499c96d1af7ec1d2aa6a46e8627'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def pinned(reference,expected_path=None):
    path=ROOT/reference['path']
    if expected_path is not None and path!=expected_path:raise ValueError('Unexpected pinned holdout input path')
    if sha(path.read_bytes())!=reference['sha256']:raise ValueError('Pinned holdout input changed')
    return json.loads(path.read_text())


def select(source,profile,config,reserved_rows):
    paths=sorted((COLLECTION/'evidence').glob(source['id']+'-rows-p*.json.gzip'))
    pages=[json.loads(gzip.decompress(p.read_bytes())) for p in paths]
    numbers=[p['physicalPage'] for p in pages]
    if len(numbers)!=len(set(numbers)):raise ValueError('Duplicate staged physical source page')
    for page in pages:
        if page['sourceId']!=source['id'] or page['sourceSha256']!=source['sourceSha256']:
            raise ValueError('Staged page belongs to a different original source')
        keys=[r['sourceRowOnPage'] for r in page['rows']]
        if any(type(n) is not int for n in keys) or keys!=list(range(1,len(keys)+1)):
            raise ValueError('Duplicate/missing/reordered source row keys in holdout input')
    if {p['physicalPage'] for p in pages}!=set(range(1,source['pdfPages']+1)):
        return None
    buckets=collections.defaultdict(list);start=profile['firstSalaryPhysicalPage'];count=source['pdfPages']-start+1
    for path,page in zip(paths,pages):
        for row in page['rows']:
            key=(source['id'],page['physicalPage'],row['sourceRowOnPage'])
            if page['physicalPage']==start or key in reserved_rows:continue
            assessment=policy.classify(row,page)
            if assessment['manualFieldsBeforeExistingReviewCoverage']:continue
            fields=[f for f,v in assessment['fields'].items() if v['corroborated']]
            if not fields:continue
            original_confidence_only=any(assessment['fields'][f]['eligibleToResolveUnreservedConfidenceOnly'] for f in fields)
            third=min(2,(page['physicalPage']-start)*3//count)
            rank=sha(json.dumps([config['seed'],source['sourceSha256'],page['physicalPage'],row['sourceRowOnPage']],
                                ensure_ascii=False,separators=(',',':')).encode())
            buckets[third].append((not original_confidence_only,rank,path,page,row,fields,assessment))
    selected=[]
    for third,number in enumerate([3,4,3]):
        bucket=sorted(buckets[third],key=lambda item:(item[0],item[1]))
        if len(bucket)<number:raise ValueError('Not enough independently corroborated unreserved holdout rows: '+source['id'])
        selected.extend((third,item) for item in bucket[:number])
    return selected


def revalidate(source,selected):
    path=AREA/'holdouts'/(source['id']+'-source-only.json');packet=json.loads(path.read_text())
    if packet['sourceSha256']!=source['sourceSha256'] or packet['selectionConfiguration']!=pin(CONFIG) or packet['fieldPolicy']!=pin(policy.POLICY):
        raise ValueError('Frozen source holdout identity/configuration changed')
    actual=[(r['physicalPage'],r['sourceRowOnPage'],r['reviewTargetFields'],r['salaryPageThird'],r['selectionRankSha256']) for r in packet['rows']]
    expected=[(item[3]['physicalPage'],item[4]['sourceRowOnPage'],item[5],['early','middle','late'][third],item[1]) for third,item in selected]
    if actual!=expected:raise ValueError('Existing holdout no longer matches final guards/reservations/seed selection')
    candidate=ROOT/packet['fullCandidate']['path']
    if sha(candidate.read_bytes())!=packet['fullCandidate']['sha256']:raise ValueError('Frozen holdout candidate bytes changed')
    for row in packet['rows']:
        for view in row['sourceNativeFieldViews']:
            if sha((ROOT/view['path']).read_bytes())!=view['sha256']:raise ValueError('Frozen native field crop changed')
    for sheet in packet['contactSheets']:
        if sha((ROOT/sheet['path']).read_bytes())!=sheet['sha256']:raise ValueError('Frozen native field sheet changed')


def emit(source,profile,selected,config):
    from PIL import Image,ImageDraw,ImageFont
    folder=AREA/'holdouts';folder.mkdir(parents=True,exist_ok=True)
    source_id=source['id'];candidate_path=folder/(source_id+'-candidate.json');blind_path=folder/(source_id+'-source-only.json')
    if candidate_path.exists() or blind_path.exists():raise ValueError('Never overwrite a frozen source holdout')
    assets=folder/'field-crops';assets.mkdir(exist_ok=True);sheets_dir=folder/'sheets';sheets_dir.mkdir(exist_ok=True)
    context_dir=Path('/tmp/queue-completion-phsa/holdout-context');context_dir.mkdir(parents=True,exist_ok=True)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
    except OSError:font=ImageFont.load_default()
    full=[];blind=[];field_crops=collections.defaultdict(list);original_page_pins=[]
    for sequence,(third,item) in enumerate(selected,1):
        unflagged,rank,path,page,row,fields,assessment=item
        original=Path(page['sourceImagePath'])
        if sha(original.read_bytes())!=page['sourceImageSha256']:raise ValueError('Actual source raster changed')
        image=Image.open(original).convert('RGB');geo=page['actualSourceGeometry'];y=row['sourceNameBand']['center'];pitch=geo['rowPitchPixels']
        rect=[max(0,geo['tableNameHeader']['box'][0]-20),max(0,round(y-pitch*.48)),
              round(image.width*.95),min(image.height,round(y+pitch*.48))]
        context=context_dir/f'{source_id}-p{page["physicalPage"]:03d}-r{row["sourceRowOnPage"]:02d}.png'
        image.crop(rect).save(context);views=[]
        for field in fields:
            if field=='name':left,right=rect[0],min(rect[2],profile['namePayBoundary'])
            elif field=='remuneration':left,right=profile['namePayBoundary']-8,profile['payExpenseBoundary']+8
            else:left,right=profile['payExpenseBoundary']-8,rect[2]
            box=[max(rect[0],left),rect[1],min(rect[2],right),rect[3]]
            crop=image.crop(box);cp=assets/f'{source_id}-{sequence:02d}-{field}.png';crop.save(cp)
            views.append({'field':field,**pin(cp),'originalPdf300DpiPixelBox':box,'noResamplingOrGlyphAlteration':True})
            field_crops[field].append((sequence,page['physicalPage'],row['sourceRowOnPage'],crop))
        base={'sequence':sequence,'sourceId':source_id,'physicalPage':page['physicalPage'],
              'sourceRowOnPage':row['sourceRowOnPage'],'salaryPageThird':['early','middle','late'][third],
              'selectionClass':'otherwise-unflagged-paired-row' if unflagged else 'unreserved-confidence-only-paired-row',
              'selectionRankSha256':rank,'reviewTargetFields':fields,'sourceNativeFieldViews':views,
              'actualSourceImagePath':str(original),'actualSourceImageSha256':page['sourceImageSha256'],
              'fullRowContextPath':str(context),'fullRowContextSha256':sha(context.read_bytes()),
              'fullRowOriginalPixelBox':rect,'pageEvidence':pin(path),'rawPageEvidence':page['rawPage']}
        blind.append(base)
        full.append({**base,'candidateRow':row['candidateRow'],
                     'expectedValues':{field:assessment['fields'][field]['value'] for field in fields},
                     'pairedFieldEvidence':{field:assessment['fields'][field] for field in fields}})
        original_page_pins.append(pin(path))
    sheets=[]
    for field,crops in field_crops.items():
        width=max(c.width for _,_,_,c in crops);height=sum(c.height+38 for _,_,_,c in crops)
        sheet=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(sheet);y=0
        for sequence,pn,rn,crop in crops:
            draw.text((0,y+3),f'{sequence:02d} | physical p{pn} row{rn} | {field}',font=font,fill='black')
            sheet.paste(crop,(0,y+38));y+=crop.height+38
        sp=sheets_dir/(source_id+'-'+field+'.png');sheet.save(sp);sheets.append({'field':field,**pin(sp)})
    core={'frozen':True,'date':'2026-11-01','sourceId':source_id,'sourceSha256':source['sourceSha256'],
          'sourceUrl':source['sourceUrl'],'originalPdfCachePath':source['cachePath'],'rows':full,
          'selectionConfiguration':pin(CONFIG),'fieldPolicy':pin(policy.POLICY),
          'completeSourcePagesAtSelection':source['pdfPages'],'sourceThirdAllocation':[3,4,3],
          'benchmarkReservedAndManualRowsExcluded':True,'holdoutRootTranscriptionMustPrecedeCandidateOpening':True}
    candidate_path.write_text(json.dumps(core,ensure_ascii=False,indent=2)+'\n')
    packet={**{k:v for k,v in core.items() if k!='rows'},'rows':blind,'contactSheets':sheets,
            'fullCandidate':pin(candidate_path),
            'instructions':['Read every requested field directly from unchanged actual-PDF native-pixel views, before opening the full candidate file.',
                            'Freeze source-only literal transcript and SHA256 first; use full source PDF/context for uncertain glyphs.',
                            'This is the deterministic source-specific policy holdout. Any true requested-field mismatch halts/revises policy acceptance; do not silently correct the holdout result to agree with the machine.',
                            'Report exact source/page/row/field and literal source value. Dashes/zero/negative/type ambiguity were excluded from paired policy eligibility, not converted into positive amounts.',
                            'FY2015/16 already has all original flagged rows reserved, so its holdout uses otherwise unflagged rows passing the same guards; this approved limitation is recorded in the selection config.']}
    blind_path.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sourceId':source_id,'sourceOnly':pin(blind_path),'candidate':pin(candidate_path),
                      'rows':len(blind),'fields':sum(len(r['reviewTargetFields']) for r in blind),
                      'selectionClasses':dict(collections.Counter(r['selectionClass'] for r in blind))}),flush=True)


def run():
    if sha(CONFIG.read_bytes())!=CONFIG_SHA:raise ValueError('Pre-selection holdout configuration changed')
    config=json.loads(CONFIG.read_text())
    if config['policy']['sha256']!=policy.POLICY_SHA:raise ValueError('Wrong root-approved policy')
    inventory=pinned(config['sourceInventory'],AREA/'source-inventory.json')['sources']
    policy_definition=pinned(config['policy'],policy.POLICY)
    profile_index=pinned(policy_definition['processingProfiles'],AREA/'processing-profile-index-001.json')
    profiles={entry['sourceId']:pinned(entry) for entry in profile_index['sourceProfiles']}
    _,reserved=policy.reserved_fields()
    for source in inventory:
        profile=profiles[source['id']]
        if (profile['sourceId'],profile['sourceSha256'],profile['year'])!=(source['id'],source['sourceSha256'],source['year']):
            raise ValueError('Pinned per-source profile identity changed')
        selected=select(source,profile,config,reserved)
        if selected is not None:
            if (AREA/'holdouts'/(source['id']+'-source-only.json')).exists():revalidate(source,selected)
            else:emit(source,profile,selected,config)
    packets=[pin(p) for p in sorted((AREA/'holdouts').glob('*-source-only.json'))]
    index={'selectionConfiguration':pin(CONFIG),'fieldPolicy':pin(policy.POLICY),'sourceOnlyPackets':packets,
           'completeNineSourceHoldout':len(packets)==9,'rowsFrozen':10*len(packets),'noCandidateValuesInThisIndex':True}
    (AREA/'holdouts'/'source-only-index.json').write_text(json.dumps(index,indent=2)+'\n')


if __name__=='__main__':run()
