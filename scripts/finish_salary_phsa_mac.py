#!/usr/bin/env python3
"""Replay the exact sixteen additive Mac-prefix name checks, offline."""
import argparse
import hashlib
import json
from pathlib import Path

import finish_salary_phsa_resolutions as r

ROOT=r.ROOT;AREA=r.AREA
REVIEW=ROOT/'research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-history-mac-I-quality-002-resolutions.json'
REVIEW_SHA='e7e9dbb35343baf591d1bc1cf968e5c12d84a998c580123d2c4acff0b6746cc3'
PEER={'path':'research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-history-batches-mac-I-quality-002-peer-comparison.json',
      'sha256':'44da96133b4f26b1f97f97c3bcf2d39b228b208f885aff0c7669cd37730b0f36'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def keep(reference,filename):
    path=AREA/'supplement-assets'/filename
    raw=(path if path.exists() else Path(reference['path'])).read_bytes()
    if sha(raw)!=reference['sha256']:raise ValueError('Source-native Mac review view changed')
    if not path.exists():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(raw)}


def build():
    review=r.pinned(REVIEW,REVIEW_SHA);r.pinned(ROOT/PEER['path'],PEER['sha256'])
    packet=r.pinned(ROOT/review['sourceOnlyPacket']['path'],review['sourceOnlyPacket']['sha256'])
    ledger=r.pinned(ROOT/review['sourceTypographyQualificationLedger']['path'],review['sourceTypographyQualificationLedger']['sha256'])
    transcript=ROOT/review['imageFirstTranscript']['path']
    if sha(transcript.read_bytes())!=review['imageFirstTranscript']['sha256']:raise ValueError('Source-only Mac transcript changed')
    if review['unresolvedRows'] or len(review['resolutions'])!=16:raise ValueError('Complete sixteen-name scope required')
    key=lambda row:(row['sourceId'],row['physicalPage'],row['sourceRowOnPage'])
    original={key(row):row for row in packet['rows']};seen=set();grouped={}
    for resolution in review['resolutions']:
        identity=key(resolution);source,pn,rn=identity
        if identity in seen or identity not in original:raise ValueError('Duplicate or unreserved Mac name field')
        seen.add(identity);view=original[identity]
        if resolution['reviewTargetFields']!=['name'] or resolution['cropSha256']!=view['originalFullRowCrop']['sha256']:
            raise ValueError('Do not widen additive name scope or replace reviewed crop')
        proof=view['pageEvidence'];page=r.pinned_gzip(ROOT/proof['path'],proof['sha256']);row=page['rows'][rn-1]
        if (page['sourceId'],page['sourceSha256'])!=(source,resolution['sourceSha256']) or row['candidateRow']!=resolution['rawCandidateRow']:
            raise ValueError('Mac supplement binds a different original observation')
        after=r.apply_values(row['candidateRow'],['name'],resolution['resolvedValues'])
        if after!=resolution['resolvedRow']:raise ValueError('Unrequested Mac fields changed')
        cases=[c for c in ledger['qualifications']if c['sourceId']==source]
        qualifications=r.typography_cases({'sourceId':source,'sourceSha256':page['sourceSha256'],'sourceTypographyQualifications':cases})
        q=qualifications.get((pn,rn))
        if q:q['sourceCaseLedger']=review['sourceTypographyQualificationLedger']
        if resolution['status']!=r.EXACT and resolution['status']not in r.QUALIFIED:
            raise ValueError('Unresolved additive Mac source name')
        if (resolution['status']in r.QUALIFIED)!=(q is not None) or (q and q['chosenName']!=after[1]):
            raise ValueError('Mac source-case status/primary differs from exact case ledger')
        retained=keep(view['nameOnlyOriginalImage'],f'mac-002-{resolution["sequence"]:03d}-name.png')
        overlay={'physicalPage':pn,'sourceRowOnPage':rn,'rawCandidateRow':row['candidateRow'],'resolvedRow':after,
                 'reviewedFields':['name'],'changedFields':['name']if after[1]!=row['candidateRow'][1]else[],
                 'resolutionStatus':resolution['status'],'nameTypographyQualification':q,
                 'pageEvidencePath':proof['path'],'pageEvidenceSha256':proof['sha256'],'rawPageEvidence':view['rawPageEvidence'],
                 'cropSha256':resolution['cropSha256'],'retainedSourceNameView':retained,
                 'reviewInput':{'path':str(REVIEW.relative_to(ROOT)),'sha256':REVIEW_SHA}}
        if q:overlay['retainedOriginalSourceContext']=keep(view['adjacentOriginalContext'],f'mac-002-{resolution["sequence"]:03d}-context.png')
        grouped.setdefault(source,[]).append(overlay)
    if seen!=set(original):raise ValueError('Missing additive Mac-name source checks')
    return {source:{'frozen':True,'sourceId':source,'sourceSha256':rows[0]['nameTypographyQualification']['originalCaseEvidence']['sourceSha256']if rows[0]['nameTypographyQualification']else next(x['sourceSha256']for x in review['resolutions']if x['sourceId']==source),
                    'kind':'complete-sixteen-case-additive-mac-prefix-name-review','reviewInput':{'path':str(REVIEW.relative_to(ROOT)),'sha256':REVIEW_SHA},
                    'sourceOnlyPacket':review['sourceOnlyPacket'],'independentFreshPeer':PEER,'resolvedRows':len(rows),
                    'reviewedFieldCounts':{'name':len(rows)},'overlays':rows,'noUnrequestedFieldsChanged':True,
                    'qualifiedCasesRequireExactPerSourceRootAdoption':any(row['nameTypographyQualification']for row in rows)}
            for source,rows in grouped.items()}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    for source,result in build().items():r.write(result,AREA/'overlays'/(source+'-mac-name-supplement-002.json'),a.check)
