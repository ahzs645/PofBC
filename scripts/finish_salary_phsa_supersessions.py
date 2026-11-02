#!/usr/bin/env python3
"""Explicit immutable selection of revised overlays, retaining every old byte."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def load(reference):
    path=ROOT/reference['path']
    if not path.resolve().is_relative_to(ROOT) or sha(path.read_bytes())!=reference['sha256']:
        raise ValueError('Revised overlay selection input changed')
    return path,json.loads(path.read_text())


def scope(overlay):
    return [(r['physicalPage'],r['sourceRowOnPage'],r['reviewedFields'],r['rawCandidateRow'],
             r['pageEvidencePath'],r['pageEvidenceSha256'],r['cropSha256']) for r in overlay['overlays']]


def validate(sidecar):
    old_path,old=load(sidecar['supersededOverlay']);new_path,new=load(sidecar['effectiveOverlay'])
    if old_path==new_path:raise ValueError('Revision requires a new immutable file')
    if sidecar.get('selectionKind')=='canonical-supplement-name-metadata-selection':
        from finish_salary_phsa_canonical_supplements import validate_selection
        validate_selection(sidecar,old,new)
        if scope(old)!=scope(new):raise ValueError('Canonical supplement reviewed field scope changed')
        return old_path,new_path
    for key in ['sourceId','sourceSha256','batch','resolvedRows','frozenBatch','imageManifest']:
        if old[key]!=new[key]:raise ValueError('Overlay revision cannot change source/batch/row scope')
    if scope(old)!=scope(new):raise ValueError('Overlay revision cannot add/remove/reorder/widen reviewed fields')
    if (sidecar['sourceId'],sidecar['sourceSha256'],sidecar['batch'])!=(old['sourceId'],old['sourceSha256'],old['batch']):
        raise ValueError('Revision sidecar identity differs')
    if not sidecar.get('reason') or sidecar.get('oldFrozenFilesRemainUnchanged') is not True:
        raise ValueError('Revision reason and immutable archival status required')
    return old_path,new_path


def selected(paths):
    candidates=set(paths);edges={};incoming=set();pins=[]
    for path in sorted((AREA/'overlay-supersessions').glob('*.json')):
        sidecar=json.loads(path.read_text());old,new=validate(sidecar)
        if old not in candidates or new not in candidates:raise ValueError('Selection references an absent overlay')
        if old in edges or new in incoming:raise ValueError('Conflicting overlay revisions')
        edges[old]=new;incoming.add(new);pins.append(pin(path))
    for start in edges:
        seen=set();current=start
        while current in edges:
            if current in seen:raise ValueError('Cyclic overlay revision selection')
            seen.add(current);current=edges[current]
    return sorted(candidates-set(edges)),pins


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--old',required=True);p.add_argument('--new',required=True);p.add_argument('--out',required=True);p.add_argument('--reason',required=True);a=p.parse_args()
    old_path,old=load({'path':a.old,'sha256':sha((ROOT/a.old).read_bytes())})
    value={'frozen':True,'sourceId':old['sourceId'],'sourceSha256':old['sourceSha256'],'batch':old['batch'],
           'supersededOverlay':pin(old_path),'effectiveOverlay':pin(ROOT/a.new),
           'reason':a.reason,'oldFrozenFilesRemainUnchanged':True,'onlyExactPreviouslyRequestedFieldsMayChange':True}
    validate(value);out=ROOT/a.out
    if out.exists():raise ValueError('Never replace a frozen revision selection')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(pin(out)))
