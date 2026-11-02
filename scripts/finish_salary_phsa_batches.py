#!/usr/bin/env python3
"""Freeze disjoint source-specific image-first PHSA employee review batches."""
import argparse
import collections
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
CACHE=Path('/tmp/queue-completion-phsa')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def full_batch_paths(folder,source=None):
    pattern=(re.escape(source) if source else r'phsa-\d{4}-\d{2}')+r'-batch-\d{3}\.json'
    return sorted(p for p in folder.glob('*-batch-*.json') if re.fullmatch(pattern,p.name))


def registry(folder):
    result=[]
    overrides=[]
    for p in AREA.glob('review-batch-*-assignment.json'):
        e=json.loads(p.read_text());overrides.append((e,p))
    for p in full_batch_paths(folder):
        b=json.loads(p.read_text());assigned=b['assignedReviewer'];adoption=None
        for e,ap in overrides:
            if (e['sourceId'],e['batch'])==(b['sourceId'],b['batch']):
                assigned=e['actualAssignedReviewer'];adoption={'path':str(ap.relative_to(ROOT)),'sha256':sha(ap.read_bytes())}
        result.append({'sourceId':b['sourceId'],'batch':b['batch'],'reviewer':assigned,
                       'initialFrozenReviewerLabel':b['assignedReviewer'],'assignmentOverride':adoption,
                       'rows':b['rowsToReview'],'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())})
    (AREA/'review-batch-registry.json').write_text(json.dumps({'batches':result},indent=2)+'\n')
    return result


def freeze(source,count,reviewer,use_policy=False):
    from PIL import Image,ImageDraw,ImageFont
    profile_path=AREA/(source+'-processing-profile-001.json');profile=json.loads(profile_path.read_text())
    inventory=next(s for s in json.loads((AREA/'source-inventory.json').read_text())['sources'] if s['id']==source)
    folder=AREA/'batches';folder.mkdir(parents=True,exist_ok=True)
    used=set();used_fields=set();existing=[];prior_pins=[]
    for p in full_batch_paths(folder,source):
        b=json.loads(p.read_text());existing.append(b)
        used.update((r['physicalPage'],r['sourceRowOnPage']) for r in b['rows'])
        used_fields.update((r['physicalPage'],r['sourceRowOnPage'],field) for r in b['rows'] for field in r['reviewTargetFields'])
        prior_pins.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())})
    if use_policy:
        import finish_salary_phsa_policy as policy
        all_reserved,_=policy.reserved_fields()
        used_fields.update((pn,rn,field) for src,pn,rn,field in all_reserved if src==source)
        for p in sorted((AREA/'overlays').glob('*-first-table-image-overlay.json')):
            prior_pins.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())})
        for p in sorted(AREA.glob('supplemental-field-reservation-*.json')):
            prior_pins.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())})
    candidates=[]
    for p in sorted((COLLECTION/'evidence').glob(source+'-rows-p*.json.gzip')):
        page=json.loads(gzip.decompress(p.read_bytes()))
        if page['physicalPage']==profile['firstSalaryPhysicalPage']:continue
        if page['pageGeometryNeedsReview'] or page['dateTitleNeedsReview']:continue
        for r in page['rows']:
            key=(r['physicalPage'],r['sourceRowOnPage'])
            if use_policy:
                classification=policy.classify(r,page)
                wanted=[field for field in classification['manualFieldsBeforeExistingReviewCoverage'] if (*key,field) not in used_fields]
                if not wanted:continue
                r={**r,'originalRequestedFields':r['requestedFields'],'requestedFields':wanted,
                   'policyClassification':classification}
            elif not r['requestedFields'] or key in used:continue
            reasons=[reason for rs in r['fieldConflicts'].values() for reason in rs]
            priority=0 if any('disagreement' in x or 'missing-or-ambiguous' in x for x in reasons) else 1
            candidates.append((priority,key,p,page,r))
    candidates.sort(key=lambda x:(x[0],x[1]))
    if count==0:
        if not 0<len(candidates)<=500:raise ValueError('All-remaining batch requires between1and500targets')
        count=len(candidates)
    if len(candidates)<count:raise ValueError(f'Only {len(candidates)} unassigned eligible rows currently available, need {count}')
    selected=candidates[:count];batch_no=max([int(b['batch'].rsplit('-',1)[1]) for b in existing],default=0)+1;batch=f'{source}-{batch_no:03d}'
    full_path=folder/f'{source}-batch-{batch_no:03d}.json';image_manifest=folder/f'{source}-batch-{batch_no:03d}-images.json'
    if full_path.exists() or image_manifest.exists():raise ValueError('Do not overwrite a frozen review batch')
    image_dir=CACHE/source/'review-images'/f'batch-{batch_no:03d}';image_dir.mkdir(parents=True,exist_ok=True)
    blind=[];full=[];crops=[];image_cache=collections.OrderedDict()
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
    except OSError:font=ImageFont.load_default()
    for seq,(_,key,proof_path,page,row) in enumerate(selected,1):
        original=Path(page['sourceImagePath'])
        if original not in image_cache:
            digest=sha(original.read_bytes())
            image_cache[original]=(Image.open(original).convert('RGB'),digest)
            if len(image_cache)>3:image_cache.popitem(last=False)
        im,digest=image_cache[original]
        if digest!=page['sourceImageSha256']:raise ValueError('Actual source image changed')
        geo=page['actualSourceGeometry'];pitch=geo['rowPitchPixels'];y=row['sourceNameBand']['center']
        rect=[max(0,geo['tableNameHeader']['box'][0]-20),max(0,round(y-pitch*.48)),
              round(im.width*.95),min(im.height,round(y+pitch*.48))]
        crop=im.crop(rect);cp=image_dir/f'p{key[0]:03d}-r{key[1]:02d}.png'
        if cp.exists():raise ValueError('Existing row crop must remain immutable')
        crop.save(cp);crops.append((seq,crop,key,row['requestedFields']))
        base={'sequence':seq,'physicalPage':key[0],'sourceRowOnPage':key[1],
              'reviewTargetFields':row['requestedFields'],'cropPath':str(cp),'cropSha256':sha(cp.read_bytes()),
              'cropRectOriginal300DpiPixels':rect,'actualSourceImagePath':str(original),
              'actualSourceImageSha256':page['sourceImageSha256'],
              'pageEvidencePath':str(proof_path.relative_to(ROOT)),'pageEvidenceSha256':sha(proof_path.read_bytes()),
              'rawPageEvidence':page['rawPage']}
        blind.append(base)
        full.append({**base,'rawCandidateRow':row['candidateRow'],'fieldConflicts':row['fieldConflicts'],
                     'rawTesseractRow':row['tesseract'],'rawRapidRow':row['rapidocr'],
                     'expenseOriginalImage':row['expenseOriginalImage'],
                     **({'rawOriginalRequestedFields':row['originalRequestedFields'],
                         'newPolicyClassification':row['policyClassification']} if use_policy else {})})
    sheets=[]
    for offset in range(0,len(crops),10):
        group=crops[offset:offset+10];width=max(crop.width for _,crop,_,_ in group)
        height=sum(crop.height+38 for _,crop,_,_ in group);sheet=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(sheet)
        y=0
        for seq,crop,key,fields in group:
            draw.text((0,y+3),f'{seq:04d} | physical page {key[0]} | source row {key[1]} | '+', '.join(fields),fill='black',font=font)
            sheet.paste(crop,(0,y+38));y+=crop.height+38
        sp=image_dir/f'contact-sheet-{offset//10+1:03d}.png';sheet.save(sp)
        sheets.append({'path':str(sp),'sha256':sha(sp.read_bytes()),'firstSequence':offset+1,'lastSequence':offset+len(group)})
    instructions=['Read every requested literal field directly from these actual-PDF row crops before opening the full candidate file.',
                  'Freeze your raw image transcript and its SHA256 first. Record own uncertain readings honestly; recheck individual unchanged original crops or independently render the PDF for ambiguous glyphs.',
                  'Names preserve all printed letters, initials, diacritics, punctuation and word boundaries. No general casing rule or guessed expansion. Source dashes are null, explicit zero is zero; do not infer either from an OCR omission.',
                  'Only assigned fields can be amended by this ordinary receipt. Context findings outside scope need a separate supplemental source-image confirmation.',
                  'Use seven resolution keys: physicalPage,sourceRowOnPage,reviewTargetFields,resolvedValues,literalImageName,status,cropSha256. resolvedValues keys must exactly equal requested fields; status resolved-from-original-image.',
                  'Top-level receipt records sourceId/sourceSha256/batch/frozenBatchSha256/imageManifestSha256/rawTranscriptSha256/reviewer/reviewedOn/resolutions/unresolvedRows. This batch alone does not accept a whole employee source.']
    candidate={'frozen':True,'date':'2026-11-01','sourceId':source,'sourceSha256':inventory['sourceSha256'],
               'sourceUrl':inventory['sourceUrl'],'batch':batch,'assignedReviewer':reviewer,
               'rowsToReview':len(full),'rows':full,'contactSheets':sheets,'instructions':instructions,
               'firstPageBenchmarkRowsExcluded':True,'oldBatchesUnchanged':True}
    if use_policy:
        candidate['fieldPolicy']={'path':str(policy.POLICY.relative_to(ROOT)),'sha256':policy.POLICY_SHA}
        candidate['priorFieldReservationPins']=prior_pins
    full_path.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n')
    images={'frozen':True,'date':'2026-11-01','sourceId':source,'sourceSha256':inventory['sourceSha256'],
            'sourceUrl':inventory['sourceUrl'],'originalPdfCachePath':inventory['cachePath'],
            'batch':batch,'assignedReviewer':reviewer,'rowsToReview':len(blind),'rows':blind,'contactSheets':sheets,
            'instructions':instructions,'fullBatchPath':str(full_path.relative_to(ROOT)),'fullBatchSha256':sha(full_path.read_bytes())}
    image_manifest.write_text(json.dumps(images,ensure_ascii=False,indent=2)+'\n')
    if use_policy:
        from finish_salary_phsa_views import views
        views(image_manifest)
    registry(folder)
    print(json.dumps({'batch':batch,'reviewer':reviewer,'rows':len(blind),
                      'imageManifest':str(image_manifest.relative_to(ROOT)),'imageManifestSha256':sha(image_manifest.read_bytes()),
                      'fullCandidate':str(full_path.relative_to(ROOT)),'fullCandidateSha256':sha(full_path.read_bytes())}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--rows',type=int,required=True);p.add_argument('--reviewer',required=True);p.add_argument('--policy',action='store_true')
    a=p.parse_args();freeze(a.source,a.rows,a.reviewer,a.policy)
