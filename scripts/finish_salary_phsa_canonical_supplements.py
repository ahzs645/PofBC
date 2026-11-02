#!/usr/bin/env python3
"""Replay only the existing FY2015 hyphen supplement's canonical I/l metadata."""
import copy
import json
import finish_salary_phsa_resolutions as reviews
import finish_salary_phsa_adoption_supersessions as adoptions

ROOT=reviews.ROOT
KIND='canonical-source-typography-metadata-supplement-revision'
ORIGINAL_KIND='expressly-reserved-three-case-hyphen-source-name-supplement'
ORIGINAL_PATH=reviews.AREA/'overlays/phsa-2015-16-hyphen-name-supplement-001.json'
ORIGINAL_SHA='74a0cdd987ffb09b309faaaf79a9e44778d22dc12c6398384c57a97dd28335fa'


def build(original_reference,adoption_selector_reference):
    path=ROOT/original_reference['path'];old=reviews.pinned(path,original_reference['sha256'])
    selector=reviews.pinned(ROOT/adoption_selector_reference['path'],adoption_selector_reference['sha256'])
    adoptions.validate(selector)
    if (path!=ORIGINAL_PATH or original_reference['sha256']!=ORIGINAL_SHA or old['kind']!=ORIGINAL_KIND
            or (old['sourceId'],old['sourceSha256'])!=(selector['sourceId'],selector['sourceSha256'])
            or selector['batch']!=adoptions.HYPHEN_SELECTION_BATCH
            or selector['supersededRootAdoption']!=adoptions.pin(adoptions.LEGACY_HYPHEN)
            or len(old['overlays'])!=1 or old['overlays'][0]['reviewedFields']!=['name']
            or (old['overlays'][0]['physicalPage'],old['overlays'][0]['sourceRowOnPage'])!=(40,15)):
        raise ValueError('Canonical supplement adapter is limited to the exact existing hyphen name field')
    normalized=reviews.typography_cases({'sourceId':old['sourceId'],'sourceSha256':old['sourceSha256'],
                    'batch':selector['batch'],'sourceTypographyQualifications':selector['effectiveCaseLedger']})
    if set(normalized)!={(40,15)}:raise ValueError('Canonical supplement root metadata widens its exact name scope')
    new=copy.deepcopy(old);row=new['overlays'][0];case=normalized[(40,15)];old_case=row['nameTypographyQualification']
    if (case['chosenName']!=row['resolvedRow'][1]or old_case['chosenName']!=case['chosenName']
            or set(old_case['visibleAlternatives'])-set(case['visibleAlternatives'])
            or case['originalCaseEvidence']['cropSha256']!=row['cropSha256']):
        raise ValueError('Canonical supplement metadata changes literal value/crop or discards an old source alternative')
    row['nameTypographyQualification']=case
    new['kind']=KIND;new['originalSpecialSupplement']=original_reference
    new['rootAdoptionSupersession']=adoption_selector_reference
    new['canonicalMetadataOnlyNoLiteralMoneyOrScopeChange']=True
    return new


def validate_selection(sidecar,old,new):
    if (sidecar.get('selectionKind')!='canonical-supplement-name-metadata-selection'
            or old.get('kind')!=ORIGINAL_KIND or new.get('kind')!=KIND
            or new.get('originalSpecialSupplement')!=sidecar['supersededOverlay']
            or new.get('canonicalMetadataOnlyNoLiteralMoneyOrScopeChange')is not True
            or (sidecar['sourceId'],sidecar['sourceSha256'])!=(old['sourceId'],old['sourceSha256'])
            or any(old[k]!=new[k]for k in ['sourceId','sourceSha256','resolvedRows','reviewedFieldCounts','reviewInput','sourceOnlyTranscript'])
            or not sidecar.get('reason')or sidecar.get('oldFrozenFilesRemainUnchanged')is not True):
        raise ValueError('Canonical supplement selection changes original source/review/field scope')
    expected=build(new['originalSpecialSupplement'],new['rootAdoptionSupersession'])
    if json.dumps(expected,sort_keys=True)!=json.dumps(new,sort_keys=True):
        raise ValueError('Canonical supplement selection does not replay exact root-only metadata')
