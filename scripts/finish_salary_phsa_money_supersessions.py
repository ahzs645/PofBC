#!/usr/bin/env python3
"""Select immutable confirmation revisions only for unchanged monetary fields."""
import copy
import json
from pathlib import Path
import finish_salary_phsa_supersessions as ordinary
ROOT=ordinary.ROOT
AREA=ordinary.AREA
pin=ordinary.pin
load=ordinary.load

def identity(row):return row['sourceId'],row['physicalPage'],row['sourceRowOnPage'],row['field']

def rebase(previous_reference,overlay_selector_reference,read_previous=None,preserve_unrelated_provenance=False):
    """Keep an exact peer proof while rebinding unchanged money to a name revision."""
    if read_previous is None:
        from finish_salary_phsa_triangulation import verified_confirmation
        read_previous=verified_confirmation
    previous=read_previous(previous_reference)
    if previous.get('adapter')=='unchanged-money-overlay-revision-v2'and not preserve_unrelated_provenance:
        raise ValueError('An existing per-field provenance chain must retain unrelated pointers')
    _,selector=load(overlay_selector_reference)
    old_path,new_path=ordinary.validate(selector)
    old_reference,new_reference=pin(old_path),pin(new_path)
    old_overlay=json.loads(old_path.read_text());new_overlay=json.loads(new_path.read_text())
    old_rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in old_overlay['overlays']}
    new_rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in new_overlay['overlays']}
    value=copy.deepcopy(previous);changed=0
    for row in value['confirmations']:
        if row['effectiveAuthorOverlay']!=old_reference:continue
        field=row['field'];index={'remuneration':3,'expenses':4}.get(field)
        if (index is None or type(row['confirmedValue'])is not int or row['confirmedValue']<=0
                or (row['sourceId'],row['sourceSha256'])!=(selector['sourceId'],selector['sourceSha256'])):
            raise ValueError('Money rebasing source or positive field type differs')
        for overlay_rows in [old_rows,new_rows]:
            entry=overlay_rows[(row['physicalPage'],row['sourceRowOnPage'])]
            if field not in entry['reviewedFields']or type(entry['resolvedRow'][index])is not int or entry['resolvedRow'][index]!=row['confirmedValue']:
                raise ValueError('Fresh-confirmed money changed in the revised ordinary overlay')
        row['effectiveAuthorOverlay']=new_reference;changed+=1
    if not changed:raise ValueError('Money revision does not cover any field in the selected overlay')
    value['supersededAdapter']=previous.get('adapter')
    value['adapter']='unchanged-money-overlay-revision-v2'if preserve_unrelated_provenance else 'unchanged-money-overlay-revision-v1'
    value['previousConfirmationLedger']=previous_reference
    value['ordinaryOverlaySupersession']=overlay_selector_reference
    value['unchangedFreshMoneyFieldsRebound']=changed
    value['peerInputs']=previous['peerInputs']+[previous_reference,overlay_selector_reference]
    if preserve_unrelated_provenance:
        inherited={identity(r):r for r in previous.get('preservedUnchangedFieldProvenance',[])}
        if len(inherited)!=len(previous.get('preservedUnchangedFieldProvenance',[])):
            raise ValueError('Duplicate inherited unchanged field provenance')
        incoming=[]
        for path in sorted((AREA/'triangulation/confirmation-supersessions').glob('*.json')):
            sidecar=json.loads(path.read_text())
            if sidecar['effectiveConfirmation']==previous_reference:incoming.append(pin(path))
        if len(incoming)>1:raise ValueError('Conflicting original confirmation provenance')
        preserved=[]
        for row in previous['confirmations']:
            if row['effectiveAuthorOverlay']==old_reference:continue
            k=identity(row)
            record=inherited.get(k)
            if record is None:
                record={k:row[k]for k in ['sourceId','physicalPage','sourceRowOnPage','field']}
                record['confirmationLedger']=previous_reference
                if incoming:record['confirmationSupersession']=incoming[0]
            preserved.append(copy.deepcopy(record))
        value['preservedUnchangedFieldProvenance']=preserved
    return value

def validate(sidecar):
    old_path,old=load(sidecar['supersededConfirmation']);new_path,new=load(sidecar['effectiveConfirmation'])
    if old_path==new_path:raise ValueError('Confirmation revision must retain a distinct old file')
    if sidecar.get('selectionKind')=='source-first-provenance-correction-selection':
        from finish_salary_phsa_money_provenance import build
        if (new!=build(sidecar['supersededConfirmation'],lambda reference:old)
                or not sidecar.get('reason')or sidecar.get('oldFrozenFilesRemainUnchanged')is not True):
            raise ValueError('Source-first metadata correction differs from its exact frozen scope')
        return old_path,new_path
    overlay_path,overlay_selector=load(sidecar['ordinaryOverlaySupersession'])
    old_overlay_path,new_overlay_path=ordinary.validate(overlay_selector)
    old_overlay_ref,new_overlay_ref=pin(old_overlay_path),pin(new_overlay_path)
    def without_overlay(document):
        value=copy.deepcopy(document)
        for row in value['confirmations']:row.pop('effectiveAuthorOverlay')
        return value
    rebased=new.get('adapter')in ['unchanged-money-overlay-revision-v1','unchanged-money-overlay-revision-v2']
    if rebased:
        expected=rebase(sidecar['supersededConfirmation'],sidecar['ordinaryOverlaySupersession'],lambda reference:old,
                        preserve_unrelated_provenance=new['adapter']=='unchanged-money-overlay-revision-v2')
        if new!=expected:raise ValueError('Rebased confirmation differs from unchanged source proof and exact ordinary revision')
    elif without_overlay(old)!=without_overlay(new):raise ValueError('Confirmation revision may not change source evidence, values, scope or reading history')
    a={identity(r):r for r in old['confirmations']};b={identity(r):r for r in new['confirmations']}
    if not a or len(a)!=len(old['confirmations'])or set(a)!=set(b)or len(b)!=len(new['confirmations']):
        raise ValueError('Confirmation revision requires the exact distinct original field set')
    old_overlay=json.loads(old_overlay_path.read_text());new_overlay=json.loads(new_overlay_path.read_text())
    old_rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in old_overlay['overlays']}
    new_rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in new_overlay['overlays']}
    for key,before in a.items():
        after=b[key];source,pn,rn,field=key;index={'remuneration':3,'expenses':4}.get(field)
        if rebased and before['effectiveAuthorOverlay']!=old_overlay_ref:
            if before!=after:raise ValueError('Unrelated fresh confirmation changed during rebasing')
            continue
        if (index is None or type(before['confirmedValue'])is not int or before['confirmedValue']<=0
                or before['effectiveAuthorOverlay']!=old_overlay_ref or after['effectiveAuthorOverlay']!=new_overlay_ref
                or source!=overlay_selector['sourceId']or before['sourceSha256']!=overlay_selector['sourceSha256']):
            raise ValueError('Confirmation revision must bind exactly the selected original/effective overlay')
        for rows in [old_rows,new_rows]:
            row=rows[(pn,rn)]
            if field not in row['reviewedFields']or row['resolvedRow'][index]!=before['confirmedValue']:
                raise ValueError('Previously fresh-confirmed source money changed or left its authorized scope')
    if sidecar.get('oldFrozenFilesRemainUnchanged')is not True or not sidecar.get('reason'):
        raise ValueError('Confirmation revision reason and immutable history required')
    return old_path,new_path

def selected(paths):
    candidates=set(paths);edges={};incoming=set();proofs={}
    for path in sorted((AREA/'triangulation/confirmation-supersessions').glob('*.json')):
        sidecar=json.loads(path.read_text());old,new=validate(sidecar)
        if old not in candidates or new not in candidates or old in edges or new in incoming:
            raise ValueError('Absent or conflicting monetary confirmation revision')
        edges[old]=new;incoming.add(new);proofs[new]=pin(path)
    for start in edges:
        seen=set();current=start
        while current in edges:
            if current in seen:raise ValueError('Cyclic monetary confirmation revision')
            seen.add(current);current=edges[current]
    return sorted(candidates-set(edges)),proofs
