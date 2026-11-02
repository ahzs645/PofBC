#!/usr/bin/env python3
"""Measure frozen OCR flags against independent image truth; adopt no new policy."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import finish_salary_phsa_rows as readers

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
REVIEWS=ROOT/'research/salaries/queue-completion-2026-11-01/reviews'
FIELD_INDEX={'name':1,'remuneration':3,'expenses':4}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def extra_name_guard(name):
    reasons=[]
    if re.search(r'(?:^|[\W_])I',name):reasons.append('word-initial-capital-I-requires-source-case-check')
    if re.search(r'I[Il]|lI|\bMc[Il]{1,2}',name):reasons.append('mixed-I-l-or-Mc-prefix-case-requires-source-check')
    allowed_punctuation=set(" ,.'-\u2018\u2019\u02bc\u2010\u2011\u2013\u2014")
    if any(not(c.isalpha() or c.isspace() or unicodedata.category(c).startswith('M') or c in allowed_punctuation) for c in name):
        reasons.append('unexplained-or-nonstandard-name-symbol-requires-source-check')
    return reasons


def field_comparison(row,field,truth,qualified=False):
    t=row['tesseract'];r=row['rapidocr'];reasons=row['fieldConflicts'].get(field,[])
    if field=='name':
        tv=readers.name_comparison(t['name']) if t else None
        rv=readers.name_comparison(r['name']) if r else None
        truth=readers.name_comparison(truth)
        tc=t['nameConfidence']/100 if t else None;rc=r['nameConfidence'] if r else None
        agree=t is not None and r is not None and bool(tv) and tv==rv
        extra=extra_name_guard(tv or '')
    else:
        key='pay' if field=='remuneration' else 'expense'
        tv=t[key]['value'] if t and t[key]['kind']=='number' else None
        rv=r[key]['value'] if r and r[key]['kind']=='number' else None
        tc=t[key+'Confidence']/100 if t and t[key+'Confidence'] is not None else None
        rc=r[key+'Confidence'] if r else None
        agree=t is not None and r is not None and t[key]['kind']=='number' and r[key]['kind']=='number' and tv==rv
        extra=[]
        if agree and (type(tv) is not int or tv<=0):extra.append('zero-negative-or-noninteger-not-calibrated-for-confidence-only-resolution')
    hard=[reason for reason in reasons if 'confidence-below' not in reason]
    confidence_only=bool(reasons) and not hard
    proposed_eligible=confidence_only and agree and not extra and not qualified
    return {'field':field,'literalImageValue':truth,'tesseractValue':tv,'rapidValue':rv,
            'tesseractConfidenceFraction':tc,'rapidConfidenceFraction':rc,
            'independentExactFieldAgreement':agree,'originalFieldFlags':reasons,
            'confidenceOnlyFlag':confidence_only,'nonConfidenceFlags':hard,
            'additionalMandatoryNameOrAmountGuards':extra,'qualifiedTypographyRequiresManualAdoption':qualified,
            'candidateValueMatchesImageTruth':(tv==truth),
            'agreedValueMatchesImageTruth':agree and tv==truth,
            'proposedNewPolicyEligible':proposed_eligible,
            'proposedNewPolicyWouldBeWrong':proposed_eligible and tv!=truth}


def histogram(values):
    edges=[0,.5,.8,.85,.9,.95,.98,.99,1.000001]
    result={f'{edges[i]:.2f}..{min(edges[i+1],1):.2f}':0 for i in range(len(edges)-1)}
    result['missing']=0
    for v in values:
        if v is None:result['missing']+=1;continue
        for i in range(len(edges)-1):
            if edges[i]<=v<edges[i+1]:result[f'{edges[i]:.2f}..{min(edges[i+1],1):.2f}']+=1;break
    return result


def summarize(records):
    result={}
    for field in FIELD_INDEX:
        rows=[r for r in records if r['field']==field]
        if not rows:continue
        result[field]={'imageTruthFields':len(rows),'originalFlaggedFields':sum(bool(r['originalFieldFlags']) for r in rows),
                       'confidenceOnlyFlags':sum(r['confidenceOnlyFlag'] for r in rows),
                       'nonConfidenceFlaggedFields':sum(bool(r['nonConfidenceFlags']) for r in rows),
                       'qualifiedTypographyFields':sum(r['qualifiedTypographyRequiresManualAdoption'] for r in rows),
                       'independentExactAgreements':sum(r['independentExactFieldAgreement'] for r in rows),
                       'agreedButDifferentFromImageReading':[r for r in rows if r['independentExactFieldAgreement'] and not r['agreedValueMatchesImageTruth']],
                       'proposedNewPolicyEligibleFields':sum(r['proposedNewPolicyEligible'] for r in rows),
                       'proposedNewPolicyWrongFields':[r for r in rows if r['proposedNewPolicyWouldBeWrong']],
                       'tesseractConfidenceHistogram':histogram([r['tesseractConfidenceFraction'] for r in rows]),
                       'rapidConfidenceHistogram':histogram([r['rapidConfidenceFraction'] for r in rows])}
    return result


def run(filename):
    inputs=[];records=[];source_stats=[]
    for p in sorted((AREA/'overlays').glob('*-first-table-image-overlay.json')):
        overlay=json.loads(p.read_text());inputs.append(pin(p));local=[]
        for reviewed in overlay['overlays']:
            proof=ROOT/reviewed['pageEvidencePath']
            if sha(proof.read_bytes())!=reviewed['pageEvidenceSha256']:raise ValueError('Frozen source evidence changed')
            page=json.loads(gzip.decompress(proof.read_bytes()));row=page['rows'][reviewed['sourceRowOnPage']-1]
            for field,index in FIELD_INDEX.items():
                record=field_comparison(row,field,reviewed['resolvedRow'][index])
                record.update(dataset='independent-complete-first-table-fixture',sourceId=overlay['sourceId'],
                              physicalPage=reviewed['physicalPage'],sourceRowOnPage=reviewed['sourceRowOnPage'],
                              pageGeometryValid=not page['pageGeometryNeedsReview'],dateTitleValid=not page['dateTitleNeedsReview'])
                if not record['pageGeometryValid'] or not record['dateTitleValid']:record['proposedNewPolicyEligible']=False
                local.append(record);records.append(record)
        source_stats.append({'sourceId':overlay['sourceId'],'firstTableRows':overlay['resolvedRows'],'fields':summarize(local)})
    batch_stats=[]
    for p in sorted((AREA/'overlays').glob('*-manual-overlay-*.json')):
        overlay=json.loads(p.read_text());inputs.append(pin(p));local=[]
        for reviewed in overlay['overlays']:
            proof=ROOT/reviewed['pageEvidencePath']
            if sha(proof.read_bytes())!=reviewed['pageEvidenceSha256']:raise ValueError('Frozen adjudicated source row changed')
            page=json.loads(gzip.decompress(proof.read_bytes()));row=page['rows'][reviewed['sourceRowOnPage']-1]
            for field in reviewed['reviewedFields']:
                record=field_comparison(row,field,reviewed['resolvedRow'][FIELD_INDEX[field]],
                                        field=='name' and reviewed['nameTypographyQualification'] is not None)
                record.update(dataset='independently-adjudicated-ordinary-review',sourceId=overlay['sourceId'],batch=overlay['batch'],
                              physicalPage=reviewed['physicalPage'],sourceRowOnPage=reviewed['sourceRowOnPage'],
                              pageGeometryValid=not page['pageGeometryNeedsReview'],dateTitleValid=not page['dateTitleNeedsReview'])
                if not record['pageGeometryValid'] or not record['dateTitleValid']:record['proposedNewPolicyEligible']=False
                local.append(record);records.append(record)
        batch_stats.append({'sourceId':overlay['sourceId'],'batch':overlay['batch'],'reviewedRows':overlay['resolvedRows'],
                            'authoritativelyAdjudicatedRequestedFields':len(local),'fields':summarize(local)})
    result={'status':'analysis-only-no-policy-adopted','date':'2026-11-01','inputPins':inputs,
            'benchmarkSources':source_stats,'completedImageReviewBatches':batch_stats,'combined':summarize(records),
            'perFieldEvidence':records,'proposedNewVersionedPolicy':{
                'scope':'Only otherwise-valid fields whose entire original uncertainty is confidence-only; exact independent literal field agreement remains necessary.',
                'requirements':['Retain every original flag and raw confidence in immutable evidence. Never alter any frozen batch, requested field or transcript.',
                                'Every actual reader disagreement, missing/unparsed value, source-shape exception, date/geometry exception and existing source-name quality flag remains an original-image target.',
                                'Add mandatory word-initial capital I, mixed I/l/Mc-prefix ambiguity and unexplained-name-artifact guards. Any explicitly qualified typography remains manual peer/root adoption with publicWarning.',
                                'No zero/negative/noninteger amount is auto-resolved by this calibration; the image benchmark supplies no such confidence-only examples.',
                                'Require source-specific benchmark coverage and independent complete actual-PDF geometry/render validation. Positive numeric source fields must be independently recognized as exactly the same integer, never detector absence or a blank.',
                                'Do not revoke already frozen packet fields, even if this analysis would classify them as corroborated. A new policy requires root assessment/adoption and a separate versioned field-resolution ledger.'],
                'actualAdjudicatedErrorsThatWouldEscape':[r for r in records if r['proposedNewPolicyWouldBeWrong']]},
            'limits':['Confidence values are engine/model scores, not calibrated probabilities. The same threshold is not an equal-error rule across source fonts or different recognition networks.',
                      'First-table benchmark truth is independently image-first transcribed; ordinary truth uses only final explicitly requested-field resolutions, not unadjudicated context fields.',
                      'This finite empirical benchmark cannot prove all later agreeing OCR fields are correct. Full source controls, every original disagreement, source-name quality audit and independent final closure remain necessary.',
                      'No adopted confidence policy or accepted source data is emitted by this analysis.']}
    out=AREA/filename
    if out.exists():raise ValueError('Calibration analysis already frozen; choose a new version')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    columns=['imageTruthFields','confidenceOnlyFlags','nonConfidenceFlaggedFields',
             'qualifiedTypographyFields','proposedNewPolicyEligibleFields','proposedNewPolicyWrongFields']
    compact={field:{key:value for key,value in values.items() if key in columns}
             for field,values in result['combined'].items()}
    print(json.dumps({'path':str(out.relative_to(ROOT)),'sha256':sha(out.read_bytes()),
                      'imageTruthFields':len(records),'combined':compact}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
