#!/usr/bin/env python3
"""Select an explicitly root-revised name adoption without changing old bytes."""
import json
from pathlib import Path
import hashlib
import re

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
LEGACY14=AREA.parent/'reviews/root-phsa-history-2015-16-batch-001-typography-adoption.json'
LEGACY14_SHA='41410273e366a0cee07268d8d2af077fa95daef4edd9a5bfef9c00be35b3448c'
LEGACY_HYPHEN=AREA.parent/'reviews/root-phsa-history-2015-16-hyphen-i-typography-adoption.json'
LEGACY_HYPHEN_SHA='defef093e74632947d378f96df12877039071dfab3e037f28c0e2058724ee2bc'
HYPHEN_SELECTION_BATCH='phsa-2015-16-hyphen-supplement'


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def load(reference):
    path=ROOT/reference['path']
    if not path.resolve().is_relative_to(ROOT) or pin(path)!=reference:
        raise ValueError('Pinned root name-adoption selection input changed')
    return path,json.loads(path.read_text())


def exact_legacy14(path,adoption):
    return (path==LEGACY14 and pin(path)['sha256']==LEGACY14_SHA
            and json.dumps(adoption,sort_keys=True)==json.dumps(json.loads(path.read_text()),sort_keys=True)
            and adoption.get('decision')=='Adopt exactly14 qualified contextual source-glyph readings; no pixel-proved casing claim.'
            and type(adoption.get('qualifiedNameCases'))is int and adoption['qualifiedNameCases']==14
            and len(adoption.get('cases',[]))==14)


def accepted(path,adoption):
    if path==LEGACY14:return exact_legacy14(path,adoption)
    if path==LEGACY_HYPHEN:return exact_legacy_hyphen(path,adoption)
    return adoption.get('acceptedQualifiedCases')is True


def exact_legacy_hyphen(path,adoption):
    return (path==LEGACY_HYPHEN and pin(path)['sha256']==LEGACY_HYPHEN_SHA
            and json.dumps(adoption,sort_keys=True)==json.dumps(json.loads(path.read_text()),sort_keys=True)
            and adoption.get('acceptedQualifiedCases')is True and adoption.get('qualifiedCases')==1
            and len(adoption.get('exactCases',[]))==1
            and adoption['exactCases'][0]['chosenContextualTranscription']=='Gfeller-Ingledew,Paris-Ann PA')


def source_identity(path,adoption):
    if exact_legacy_hyphen(path,adoption):
        return adoption['sourceId'],adoption['sourceSha256'],HYPHEN_SELECTION_BATCH
    return tuple(adoption[k]for k in ['sourceId','sourceSha256','batch'])


def case_ledger(path,adoption):
    if exact_legacy_hyphen(path,adoption):return pin(path)
    if exact_legacy14(path,adoption):
        filename=adoption['caseLedgerFile']
        if Path(filename).name!=filename:raise ValueError('Exact legacy case ledger must remain in original reviews directory')
        return {'path':str((LEGACY14.parent/filename).relative_to(ROOT)),'sha256':adoption['caseLedgerSha256']}
    return adoption['exactCaseLedger']


def cases(adoption,path=None):
    if path is not None and exact_legacy_hyphen(path,adoption):
        value=adoption['exactCases']
    elif path is not None and exact_legacy14(path,adoption):
        load(case_ledger(path,adoption))
        value=adoption['cases']
    else:
        _,document=load(adoption['exactCaseLedger'])
        mixed=isinstance(adoption.get('cases'),list)and isinstance(adoption.get('closedCases'),list)
        declared=(adoption['cases']+adoption['closedCases'])if mixed else adoption.get('exactCases',adoption.get('closedCases'))
        if isinstance(declared,list):
            if mixed:candidates=document.get('qualifications',document.get('cases',document.get('sourceTypographyQualifications')))
            else:candidates=document.get('sourceNameSegmentationExceptions',document.get('separateClosedRrMExceptionsAwaitingExactRootAdoption',document.get('qualifications',document.get('cases',document.get('sourceTypographyQualifications')))))
            if not isinstance(candidates,list):raise ValueError('Scoped exact adoption has no pinned source case list')
            selected={(r['physicalPage'],r['sourceRowOnPage']):r for r in candidates}
            explicit={(r['physicalPage'],r['sourceRowOnPage']):r for r in declared}
            if len(selected)!=len(candidates)or len(explicit)!=len(declared)or not set(explicit)<=set(selected):
                raise ValueError('Scoped exact adoption case set is missing/duplicated')
            value=[]
            for key,root_case in explicit.items():
                original=selected[key]
                if primary(root_case)!=primary(original)or set(family(root_case))!=set(family(original))or crop(root_case)!=crop(original):
                    raise ValueError('Scoped exact adoption differs from its pinned full source case')
                value.append(original)
        else:
            value=document.get('qualifications',document.get('cases',document.get('sourceTypographyQualifications',document.get('sourceNameSegmentationExceptions'))))
    if not isinstance(value,list):raise ValueError('Root name-adoption ledger needs an exact case list')
    result={(r['physicalPage'],r['sourceRowOnPage']):r for r in value}
    if len(result)!=len(value):raise ValueError('Duplicate source name-adoption case')
    return result


def primary(case):
    for field in ['chosenContextualTranscription','resolvedContextualName','proposedName','chosenName','primaryName','primary']:
        if field in case:return case[field]
    raise ValueError('Missing exact source-name case primary')


def family(case):
    if 'visibleAlternatives'in case:return case['visibleAlternatives']
    if isinstance(case.get('visibleIOrLowerLAlternatives'),list):
        return [primary(case)]+case['visibleIOrLowerLAlternatives']
    if isinstance(case.get('typographicallyPossibleAlternative'),str)and case['typographicallyPossibleAlternative']:
        return [primary(case),case['typographicallyPossibleAlternative']]
    if isinstance(case.get('alternative'),str)and case['alternative']:
        return [primary(case),case['alternative']]
    raise ValueError('Missing exact source-name finite family')


def crop(case):
    value=case.get('cropSha256',case.get('originalFullRowCropSha256',case.get('actualSourceEvidence',{}).get('originalFullRowCropSha256')))
    if not isinstance(value,str) or re.fullmatch('[0-9a-f]{64}',value)is None:
        raise ValueError('Missing exact original full-row crop hash')
    return value


def validate(sidecar):
    old_path,old=load(sidecar['supersededRootAdoption']);new_path,new=load(sidecar['effectiveRootAdoption'])
    identity=tuple(sidecar[k]for k in ['sourceId','sourceSha256','batch'])
    if (old_path==new_path or source_identity(old_path,old)!=identity
            or tuple(new[k]for k in ['sourceId','sourceSha256','batch'])!=identity
            or not accepted(old_path,old) or new.get('acceptedQualifiedCases') is not True
            or new.get('supersededRootAdoption')!=sidecar['supersededRootAdoption']
            or case_ledger(old_path,old)!=sidecar['supersededCaseLedger']
            or new['exactCaseLedger']!=sidecar['effectiveCaseLedger']
            or sidecar['oldFrozenFilesRemainUnchanged'] is not True or not sidecar['reason']):
        raise ValueError('Root replacement authority/source/case-ledger scope differs')
    before,after=cases(old,old_path),cases(new,new_path)
    from finish_salary_phsa_retirements import validate as validate_retirements
    retired=validate_retirements(sidecar,old,new,before)
    allowed={(r['physicalPage'],r['sourceRowOnPage']):r for r in sidecar['authorizedChangedNameCases']}
    if (set(before)-set(retired)!=set(after) or len(allowed)!=len(sidecar['authorizedChangedNameCases'])
            or not(allowed or retired)or not set(allowed).issubset(after)):
        raise ValueError('Root name-adoption revision widens/removes case scope')
    changed=set()
    for key,previous in before.items():
        if key in retired:continue
        revised=after[key]
        if previous==revised:continue
        changed.add(key)
        if key not in allowed:raise ValueError('Unlisted source-name adoption changed')
        authority=allowed[key]
        if (authority['allowedFields']!=['name'] or primary(previous)!=authority['oldPrimary']
                or primary(revised)!=authority['newPrimary']
                or family(previous)!=authority['oldVisibleAlternatives']
                or family(revised)!=authority['newVisibleAlternatives']
                or crop(previous)!=authority['originalFullRowCropSha256']
                or crop(revised)!=authority['originalFullRowCropSha256']
                or revised.get('caseProvenByPixels') is not False):
            raise ValueError('Root revision differs from the exact name-only finite source case')
    if changed!=set(allowed):raise ValueError('Root source-name revision case list is not exact')
    return old_path,new_path


def selected(paths,include_closed=False):
    import finish_salary_phsa_resolutions as reviews
    closed=set()
    for policy_path,digest in reviews.CLOSED_CASE_POLICIES:
        policy=reviews.pinned(policy_path,digest)
        for case in policy['approvedCases']:
            path,adoption=load(case['rootAdoption'])
            if not(isinstance(adoption.get('cases'),list)and isinstance(adoption.get('closedCases'),list)):
                closed.add(path)
    candidates=set(paths);edges={};incoming=set();selection={}
    for path in sorted((AREA/'adoption-supersessions').glob('*.json')):
        sidecar=json.loads(path.read_text());old,new=validate(sidecar)
        if old not in candidates:
            if old in closed:candidates.add(old)
            else:raise ValueError('Superseded root adoption was not an original selected input')
        if old in edges or new in incoming:raise ValueError('Conflicting root name-adoption revisions')
        candidates.add(new);edges[old]=new;incoming.add(new);selection[new]=pin(path)
        if old in closed:closed.add(new)
    for start in edges:
        visited=set();current=start
        while current in edges:
            if current in visited:raise ValueError('Cyclic root name-adoption selection')
            visited.add(current);current=edges[current]
    return sorted(candidates-set(edges)-(set()if include_closed else closed)),selection
