#!/usr/bin/env python3
"""Apply hash-pinned original-image reviews as separate immutable OCR overlays."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'research/salaries/held-resolution-2026-11-01/health'
FIELDS={'name':1,'remuneration':3,'expenses':4}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def apply_verified_values(candidate, fields, values):
    if set(values)!=set(fields) or not set(values)<=set(FIELDS):
        raise ValueError('Reviewer field coverage differs from frozen request')
    resolved=list(candidate)
    for field,value in values.items():
        if field=='name' and (not isinstance(value,str) or not value.strip()):
            raise ValueError('Empty literal source name')
        if field=='remuneration' and type(value) not in (int,float):
            raise ValueError('Missing remuneration must remain held')
        if field=='expenses' and value is not None and type(value) not in (int,float):
            raise ValueError('Invalid literal expense')
        resolved[FIELDS[field]]=value
    return resolved


def build(review_paths,originals=False):
    batches={sha(p.read_bytes()):p for p in AUDIT.glob('review-batch-*.json')
             if not p.name.endswith('-images.json')}
    overlays=[];inputs=[];keys=set()
    for path,expected in review_paths:
        raw=path.read_bytes()
        if sha(raw)!=expected:
            raise ValueError('Reviewer receipt fingerprint differs')
        review=json.loads(raw)
        batch_sha=review['frozenBatchSha256']
        batch_path=batches[batch_sha];batch=json.loads(batch_path.read_text())
        if review['sourceSha256']!=batch['sourceSha256']:
            raise ValueError('Reviewed original differs')
        source_rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in batch['rows']}
        for resolution in review['resolutions']:
            key=(resolution['physicalPage'],resolution['sourceRowOnPage'])
            if key in keys:
                raise ValueError('Overlapping reviewer rows need explicit reconciliation')
            if resolution['status']!='resolved-from-original-image':
                continue
            row=source_rows[key]
            if resolution['cropSha256']!=row['cropSha256']:
                raise ValueError('Reviewed original-image pixels differ')
            if originals and sha(Path(row['cropPath']).read_bytes())!=row['cropSha256']:
                raise ValueError('Cached reviewed original-image pixels differ')
            evidence=ROOT/'research/salaries/held-resolution-health/evidence'/f'phsa-fy2024-25-ocr-p{key[0]:03d}.json.gzip'
            if not evidence.exists():
                evidence=Path(row['completePageEvidencePath'])
            if sha(evidence.read_bytes())!=row['completePageEvidenceSha256']:
                raise ValueError('Original raw OCR evidence differs')
            e=json.loads(gzip.decompress(evidence.read_bytes()))
            original=next(r for r in e['rowEvidence'] if r['sourceRowOnPage']==key[1])
            if original['candidateRow']!=row['candidateRow']:
                raise ValueError('Frozen candidate row differs from original evidence')
            values=resolution['resolvedValues']
            resolved=apply_verified_values(original['candidateRow'],row['reviewTargetFields'],values)
            overlays.append({'physicalPage':key[0],'sourceRowOnPage':key[1],
                             'rawCandidateRow':original['candidateRow'],'resolvedRow':resolved,
                             'reviewedFields':sorted(values),'originalConflicts':original['conflicts'],
                             'changedFields':[f for f in values if original['candidateRow'][FIELDS[f]]!=values[f]],
                             'reviewer':review['reviewer'],'reviewReceiptPath':str(path.relative_to(ROOT)),
                             'reviewReceiptSha256':expected,'batchSha256':batch_sha,
                             'cropSha256':row['cropSha256'],'rawPageEvidenceSha256':row['completePageEvidenceSha256'],
                             'acceptedEmployeeRows':0})
            keys.add(key)
        inputs.append({'path':str(path.relative_to(ROOT)),'sha256':expected,
                       'batchPath':str(batch_path.relative_to(ROOT)),'batchSha256':batch_sha})
    return {'frozen':True,'date':'2026-11-01','sourceSha256':'809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c',
            'reviewInputs':inputs,'resolvedRows':len(overlays),'changedRows':sum(bool(x['changedFields']) for x in overlays),
            'acceptedEmployeeRows':0,'rawOcrOrFrozenBatchRewritten':False,'overlays':overlays,
            'scope':'Original-image corrections for a staged complete-source workflow. This overlay does not accept a partial page or cohort and does not alter raw OCR or source pixels.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--review',action='append',required=True,help='repository-relative receipt path=sha256')
    p.add_argument('--out',required=True,help='new output filename under held health audit folder')
    p.add_argument('--check',action='store_true')
    p.add_argument('--originals',action='store_true',help='also recheck cached original row-image bytes')
    args=p.parse_args()
    paths=[]
    for value in args.review:
        path,digest=value.rsplit('=',1);paths.append((ROOT/path,digest))
    result=build(paths,args.originals);raw=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode();out=AUDIT/args.out
    if out.parent!=AUDIT:
        raise ValueError('Output must remain in the assigned audit directory')
    if args.check:
        if out.read_bytes()!=raw:
            raise ValueError('Frozen manual overlay differs')
    else:
        if out.exists():
            raise ValueError('Use a new immutable overlay filename')
        out.write_bytes(raw)
    print(json.dumps({'file':str(out.relative_to(ROOT)),'sha256':sha(raw),
                      'resolvedRows':result['resolvedRows'],'changedRows':result['changedRows'],'acceptedEmployeeRows':0}))


if __name__=='__main__':
    main()
