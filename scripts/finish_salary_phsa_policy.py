#!/usr/bin/env python3
"""Root-approved provisional paired-reader policy; never rewrite original flags.

Source acceptance additionally requires the independent implementation assessment
and all ninety blind source holdout rows. Confidence scores are not probabilities.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path

import finish_salary_phsa_rows as readers
from finish_salary_phsa_calibration import extra_name_guard
from finish_salary_phsa_stage import suspicious_name

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
COLLECTION=ROOT/'research/salaries/queue-completion-phsa'
POLICY=AREA/'paired-reader-field-policy-002.json'
POLICY_SHA='0fafb3763ea5a1ebf8f2d7310e748cb4d24247428f544056e1427d2e6ecc77fe'
ANCHORS=ROOT/'research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-history-all-pages-raster-pay-anchors.json.gzip'
ANCHORS_SHA='76e604b4d14031c2361e2fbf01ff15a547d677822c09472c28519aa008253c79'
FIELD_INDEX={'name':1,'remuneration':3,'expenses':4}
CONFIDENCE_FLAGS={
    'name':{'tesseract-name-confidence-below-85','rapid-name-confidence-below-0.98'},
    'remuneration':{'tesseract-pay-confidence-below-90','rapid-pay-confidence-below-0.98'},
    'expenses':{'tesseract-expense-confidence-below-90','rapid-expense-confidence-below-0.98'}}
RASTER=None


def sha(raw):return hashlib.sha256(raw).hexdigest()


def raster_pages():
    global RASTER
    if RASTER is None:
        if sha(POLICY.read_bytes())!=POLICY_SHA or sha(ANCHORS.read_bytes())!=ANCHORS_SHA:
            raise ValueError('Approved field policy or independent source-raster evidence changed')
        ledger=json.loads(gzip.decompress(ANCHORS.read_bytes()));RASTER={}
        for source in ledger['sources']:
            for page in source['pages']:
                RASTER[(source['sourceId'],page['physicalPage'])]=(source['sourceSha256'],page)
    return RASTER


def classify(row,page):
    source=page['sourceId'];pn=page['physicalPage'];key=(source,pn)
    entry=raster_pages().get(key)
    valid=entry is not None and entry[0]==page['sourceSha256']
    if valid:
        anchor=entry[1]
        valid=(anchor['actualRenderedPngSha256FromPrimary']==page['sourceImageSha256']
               and anchor['remunerationInkBandCount']==len(page['rows'])
               and not page['dateTitleNeedsReview'] and not page['pageGeometryNeedsReview'])
        if valid:
            index=row['sourceRowOnPage']-1
            valid=(0<=index<len(anchor['rows']) and not anchor['rows'][index]['needsSourceGeometryReview'])
            if valid:
                box=anchor['rows'][index]['nameRowBox'];y=row['sourceNameBand']['center']
                valid=box[1]<=y<box[3] and anchor['rows'][index]['nameInkPixels']>0
    t=row['tesseract'];r=row['rapidocr'];result={}
    extra=list(dict.fromkeys(suspicious_name(row['candidateRow'][1])+extra_name_guard(row['candidateRow'][1])))
    for field,index in FIELD_INDEX.items():
        flags=row['fieldConflicts'].get(field,[])
        hard=[reason for reason in flags if reason not in CONFIDENCE_FLAGS[field]]
        agreement=False;value=None;exclusions=list(hard)
        if t is None or r is None:exclusions.append('independent-reader-missing-or-ambiguous')
        elif field=='name':
            left=readers.name_comparison(t['name']);right=readers.name_comparison(r['name'])
            agreement=bool(left) and left==right;value=left
            exclusions+=extra
        else:
            token='pay' if field=='remuneration' else 'expense'
            left=t[token];right=r[token]
            agreement=left['kind']=='number' and right['kind']=='number' and left['value']==right['value']
            value=left['value'] if left['kind']=='number' else None
            values=[left['value'],right['value'],row['candidateRow'][index]]
            if any(type(v) is not int or v<=0 for v in values):
                exclusions.append('zero-negative-noninteger-blank-dash-or-unparsed-not-eligible')
            if field=='expenses':
                glyph=row['expenseOriginalImage']
                if glyph['blank'] or glyph['matchesSourceCalibratedDashGeometry']:
                    exclusions.append('not-an-unambiguous-positive-numeric-source-expense-region')
        if not agreement:exclusions.append('no-exact-independent-parsed-field-agreement')
        if value!=row['candidateRow'][index]:exclusions.append('candidate-does-not-already-equal-both-independent-readers')
        if not valid:exclusions.append('source-raster-date-or-row-geometry-gate-not-satisfied')
        corroborated=agreement and not exclusions
        result[field]={'field':field,'originalFlags':flags,'originalConfidenceOnly':bool(flags) and not hard,
                       'exactIndependentAgreement':agreement,'value':value,'allSourceGeometryGatesPass':valid,
                       'exclusions':exclusions,'corroborated':corroborated,
                       'eligibleToResolveUnreservedConfidenceOnly':corroborated and bool(flags) and not hard,
                       'additionalManualNameGuard':extra if field=='name' else []}
    manual=[]
    for field in FIELD_INDEX:
        glyph=row['expenseOriginalImage']
        # This is the separately validated ORIGINAL dash route, not a new paired
        # policy inference from two missing values or from detector absence.
        legacy_explicit_dash=(field=='expenses' and valid and not row['fieldConflicts'].get(field)
                              and not glyph['blank'] and glyph['matchesSourceCalibratedDashGeometry']
                              and row['candidateRow'][4] is None
                              and not any(reader is not None and reader['expense']['kind']=='number' for reader in [t,r]))
        if not result[field]['corroborated'] and not legacy_explicit_dash:manual.append(field)
    return {'fields':result,'manualFieldsBeforeExistingReviewCoverage':manual,
            'policy':{'path':str(POLICY.relative_to(ROOT)),'sha256':POLICY_SHA},
            'independentRasterProof':{'path':str(ANCHORS.relative_to(ROOT)),'sha256':ANCHORS_SHA}}


def reserved_fields():
    """Exclude immutable packet fields, including ones not yet reviewed."""
    import finish_salary_phsa_batches as batches
    fields=set();rows=set()
    for path in batches.full_batch_paths(AREA/'batches'):
        batch=json.loads(path.read_text());source=batch['sourceId']
        for row in batch['rows']:
            key=(source,row['physicalPage'],row['sourceRowOnPage']);rows.add(key)
            fields.update((*key,field) for field in row['reviewTargetFields'])
    for path in (AREA/'overlays').glob('*-first-table-image-overlay.json'):
        overlay=json.loads(path.read_text());source=overlay['sourceId']
        for row in overlay['overlays']:
            key=(source,row['physicalPage'],row['sourceRowOnPage']);rows.add(key)
            fields.update((*key,field) for field in row['reviewedFields'])
    for path in AREA.glob('supplemental-field-reservation-*.json'):
        reservation=json.loads(path.read_text())
        for row in reservation['reservations']:
            key=(row['sourceId'],row['physicalPage'],row['sourceRowOnPage']);rows.add(key)
            fields.update((*key,field) for field in row['reviewTargetFields'])
    return fields,rows


def preview():
    reserved,_=reserved_fields();counts=collections.defaultdict(collections.Counter)
    for path in sorted((COLLECTION/'evidence').glob('phsa-*-rows-p*.json.gzip')):
        page=json.loads(gzip.decompress(path.read_bytes()));source=page['sourceId']
        for row in page['rows']:
            classified=classify(row,page);counts[source]['rows']+=1
            manual=[]
            for field,item in classified['fields'].items():
                key=(source,page['physicalPage'],row['sourceRowOnPage'],field)
                if key in reserved:
                    counts[source]['reservedOrBenchmarkFields']+=1
                elif item['eligibleToResolveUnreservedConfidenceOnly']:
                    counts[source]['provisionalCorroboratedConfidenceOnlyFields']+=1
                elif field in classified['manualFieldsBeforeExistingReviewCoverage']:
                    counts[source]['unreservedManualFields']+=1;manual.append(field)
            if manual:counts[source]['unreservedManualRows']+=1
    out={source:dict(stats) for source,stats in counts.items()}
    print(json.dumps(out))
    return out


if __name__=='__main__':preview()
