#!/usr/bin/env python3
"""Exact current-source retirement of explicitly named wrong glyph families."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
POLICIES=[(AREA/'source-name-exact-retirement-policy-001.json','07b1657c0fc70ce2f654dde478fdc2749ace31bebff70db8df9df3f3c19dfb73'),
          (AREA/'source-name-exact-retirement-policy-002.json','34aeabd2a62d30f28a64bc5bb4821ed209664b7dc422cb1b55346bf4a94e47a3')]


def validate(sidecar,old,new,before):
    import finish_salary_phsa_adoption_supersessions as a
    declared=sidecar.get('authorizedRetiredNameCases',[])
    if not declared:return {}
    allowed={}
    for path,digest in POLICIES:
        _,policy=a.load({'path':str(path.relative_to(ROOT)),'sha256':digest})
        for case in policy['approvedRetirements']:
            key=case['sourceId'],case['physicalPage'],case['sourceRowOnPage']
            if key in allowed:raise ValueError('Duplicate exact source-name retirement authority')
            allowed[key]=(case,{'path':str(path.relative_to(ROOT)),'sha256':digest})
    if new.get('acceptedCaseRetirements')!=declared:
        raise ValueError('Root has not accepted the exact current-source case retirements')
    result={}
    for case in declared:
        key=case['sourceId'],case['physicalPage'],case['sourceRowOnPage'];rowkey=key[1:]
        if key not in allowed or allowed[key][0]!=case:raise ValueError('Unknown or altered source-name retirement')
        _,policyref=allowed[key]
        if (sidecar.get('retirementImplementationPolicy')!=policyref or new.get('retirementImplementationPolicy')!=policyref
                or case['originalRootAdoption']!=sidecar['supersededRootAdoption']
                or case['originalCaseLedger']!=sidecar['supersededCaseLedger']
                or (case['sourceId'],case['sourceSha256'],case['batch'])!=(old['sourceId'],old['sourceSha256'],old['batch'])
                or case['allowedFields']!=['name']or case['requiresDirectLiteral']is not True or rowkey not in before
                or a.primary(before[rowkey])!=case['oldPrimary']or a.crop(before[rowkey])!=case['originalFullRowCropSha256']
                or set(a.family(before[rowkey]))!=set(case['oldVisibleAlternatives'])or rowkey in result):
            raise ValueError('Retired source-name case differs from its original exact root authority/crop')
        for reference in [case['currentSourceDecision'],case['independentSourcePeer']]:
            _,document=a.load(reference)
            if (document['sourceId'],document['sourceSha256'])!=(case['sourceId'],case['sourceSha256']):
                raise ValueError('Retirement source decision belongs to a different original')
            matches=[r for r in document['rows']if(r['physicalPage'],r['sourceRowOnPage'])==rowkey]
            if len(matches)!=1:raise ValueError('Retirement current-source human row is missing/duplicated')
            row=matches[0]
            value=row.get('currentAcceptedSourceLiteral',row.get('literalCurrentSourceName',row.get('educationFirstAndCurrentLiteral',row.get('canonicalPreferredLiteral'))))
            family=row.get('currentCompleteVisibleAlternatives',row.get('visibleAlternatives'))
            status=row.get('currentSourceStatus',row.get('sourceStatus'))
            if (status is None and 'canonicalPreferredLiteral'in row and row.get('sourceSpans')==[]
                    and row.get('sourceUncertainty')is None and family==[value]):status='direct'
            if row['field']!='name'or value!=case['currentDirectLiteral']or family!=[value]or status!='direct':
                raise ValueError('Retirement lacks exact direct literal current source agreement')
        result[rowkey]=case
    return result


def records():
    import finish_salary_phsa_adoption_supersessions as a
    result=[]
    for path in sorted((AREA/'adoption-supersessions').glob('*.json')):
        sidecar=json.loads(path.read_text())
        if not sidecar.get('authorizedRetiredNameCases'):continue
        a.validate(sidecar)
        for case in sidecar['authorizedRetiredNameCases']:
            result.append({**case,'rootAdoptionSupersession':a.pin(path),'effectiveRootAdoption':sidecar['effectiveRootAdoption']})
    return result
