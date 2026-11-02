#!/usr/bin/env python3
"""Replay the three expressly reserved hyphen-I source-name checks.

Only the three name fields are covered. The FY2015 case remains explicitly
qualified and requires the separately pinned root adoption in final closure.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import finish_salary_phsa_resolutions as reviews

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
REVIEW=ROOT/'research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-history-batches-hyphen-i-supplement-001-comparison.json'
REVIEW_SHA='249fb4812ea8fe79b87b795ae655b7d087d9a42705828863d4024c9333b24147'
KEYS={('phsa-2015-16',40,15),('phsa-2017-18',43,14),('phsa-2017-18',122,16)}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def build():
    review=reviews.pinned(REVIEW,REVIEW_SHA)
    transcript=reviews.pinned(ROOT/review['sourceOnlyTranscript']['path'],review['sourceOnlyTranscript']['sha256'])
    readings={(r['sourceId'],r['physicalPage'],r['sourceRowOnPage']):r for r in transcript['readings']}
    resolved={(r['sourceId'],r['physicalPage'],r['sourceRowOnPage']):r for r in review['resolutions']}
    if set(readings)!=KEYS or set(resolved)!=KEYS or len(review['resolutions'])!=3:
        raise ValueError('Do not widen the three reserved source-name fields')
    grouped={}
    for key in sorted(KEYS):
        source,pn,rn=key;reading=readings[key];resolution=resolved[key]
        if reading['reviewTargetFields']!=['name'] or resolution['reviewTargetFields']!=['name']:
            raise ValueError('Supplement is expressly name-only')
        if reading['resolvedValues']!=resolution['resolvedValues'] or reading['cropSha256']!=resolution['cropSha256']:
            raise ValueError('Blind source reading and final comparison differ')
        proof=ROOT/reading['pageEvidencePath']
        page=reviews.pinned_gzip(proof,reading['pageEvidenceSha256'])
        if (page['sourceId'],page['sourceSha256'],page['sourceImageSha256'])!=(source,reading['sourceSha256'],reading['actualSourceImageSha256']):
            raise ValueError('Supplement no longer binds the exact painted original')
        original=page['rows'][rn-1]
        if original['sourceRowOnPage']!=rn:raise ValueError('Wrong original source row')
        before=original['candidateRow'];after=reviews.apply_values(before,['name'],resolution['resolvedValues'])
        q=None
        if resolution['status'] in reviews.QUALIFIED:
            case=resolution['caseQualification'];alternatives=[a for a in case['visibleAlternatives'] if a!=after[1]]
            if not alternatives or case['caseProvenByPixels']:raise ValueError('Retain visible case uncertainty')
            q={'originalCaseEvidence':case,'chosenName':after[1],'visibleAlternatives':alternatives,
               'characterPositionsZeroBased':case['characterPositionsZeroBased'],
               'assumptionBasis':case['assumptionBasis'],'caseProvenByPixels':False,
               'requiresExactPeerAndRootCaseAdoption':True,'sourceCaseLedger':None}
        elif resolution['status']!=reviews.EXACT:raise ValueError('Unresolved source name')
        # Preserve a small source-native view alongside the existing receipts;
        # the full PDF and whole-page cache remain outside the repository.
        asset=AREA/'supplement-assets'/f'{source}-hyphen-p{pn:03d}-r{rn:02d}.png'
        crop=(asset if asset.exists() else Path(reading['cropPath'])).read_bytes()
        if sha(crop)!=reading['cropSha256']:raise ValueError('Reviewed original name context changed')
        if asset.exists() and asset.read_bytes()!=crop:raise ValueError('Never replace a frozen source view')
        asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(crop)
        overlay={'physicalPage':pn,'sourceRowOnPage':rn,'rawCandidateRow':before,'resolvedRow':after,
                 'reviewedFields':['name'],'changedFields':['name'] if after[1]!=before[1] else [],
                 'resolutionStatus':resolution['status'],'nameTypographyQualification':q,
                 'pageEvidencePath':reading['pageEvidencePath'],'pageEvidenceSha256':reading['pageEvidenceSha256'],
                 'rawPageEvidence':reading['rawPageEvidence'],'cropSha256':reading['cropSha256'],
                 'retainedOriginalContext':{'path':str(asset.relative_to(ROOT)),'sha256':sha(crop)},
                 'reviewInput':{'path':str(REVIEW.relative_to(ROOT)),'sha256':REVIEW_SHA}}
        grouped.setdefault(source,[]).append(overlay)
    return {source:{'frozen':True,'sourceId':source,'sourceSha256':readings[(source,rows[0]['physicalPage'],rows[0]['sourceRowOnPage'])]['sourceSha256'],
                    'kind':'expressly-reserved-three-case-hyphen-source-name-supplement',
                    'reviewInput':{'path':str(REVIEW.relative_to(ROOT)),'sha256':REVIEW_SHA},
                    'sourceOnlyTranscript':review['sourceOnlyTranscript'],'resolvedRows':len(rows),
                    'reviewedFieldCounts':{'name':len(rows)},'overlays':rows,
                    'rawOcrAndFrozenBatchesUnchanged':True,'noMoneyFieldsReviewedOrChanged':True}
            for source,rows in grouped.items()}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    for source,result in build().items():
        reviews.write(result,AREA/'overlays'/(source+'-hyphen-name-supplement-001.json'),a.check)
