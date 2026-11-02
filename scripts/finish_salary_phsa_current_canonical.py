#!/usr/bin/env python3
"""Validate exact current201 human decisions and name-only overlay revisions."""
import finish_salary_phsa_resolutions as r

MAP=r.AREA/'canonical-review/phsa-2019-20-current201-authorized-decisions.json'
MAP_SHA='a1b8df27b36ad2accbef599f4ebde23fd98805e1a25a4f97b45a568d2dd8b2be'


def decisions():
    document=r.pinned(MAP,MAP_SHA);result={}
    for row in document['rows']:
        key=row['physicalPage'],row['sourceRowOnPage']
        if key in result or row['field']!='name':raise ValueError('Current canonical source decision is duplicate/not a name')
        pointer=row['currentHumanDecision'];human=r.pinned(r.ROOT/pointer['receipt']['path'],pointer['receipt']['sha256'])
        target=human
        for component in pointer['rowRecordPointer'].split('/')[1:]:
            target=target[int(component)]if isinstance(target,list)else target[component.replace('~1','/').replace('~0','~')]
        value=target[pointer['valueField']];family=target[pointer['finiteField']]
        if ((human['sourceId'],human['sourceSha256'])!=(document['sourceId'],document['sourceSha256'])
                or (target['physicalPage'],target['sourceRowOnPage'])!=key or target['field']!='name'
                or value!=row['currentAcceptedSourceLiteral']or family!=row['currentCompleteVisibleAlternatives']
                or value not in family or len(family)!=len(set(family))
                or row['currentSourceStatus']!=('qualified'if len(family)>1 else'direct')):
            raise ValueError('Current canonical decision differs from exact final human row/value/family')
        result[key]=row
    if len(result)!=201 or sum(q['currentSourceStatus']=='qualified'for q in result.values())!=70:
        raise ValueError('Current canonical earlier-source scope differs')
    return document,result


def validate_review(review,qualification):
    spec=review['canonicalCurrentSourceNameRevision'];expected={'path':str(MAP.relative_to(r.ROOT)),'sha256':MAP_SHA}
    if spec['authorizedCurrent201DecisionMap']!=expected:raise ValueError('Wrong current canonical human map')
    document,rows=decisions();before=r.pinned(r.ROOT/spec['originalFrozenReview']['path'],spec['originalFrozenReview']['sha256'])
    if (tuple(review[k]for k in ['sourceId','sourceSha256','batch'])!=tuple(before[k]for k in ['sourceId','sourceSha256','batch'])
            or (review['sourceId'],review['sourceSha256'])!=(document['sourceId'],document['sourceSha256'])
            or len(before['resolutions'])!=len(review['resolutions'])):
        raise ValueError('Current canonical name revision changes original source/batch scope')
    for old,new in zip(before['resolutions'],review['resolutions']):
        key=new['physicalPage'],new['sourceRowOnPage']
        if any(old[k]!=new[k]for k in ['physicalPage','sourceRowOnPage','reviewTargetFields','cropSha256']):
            raise ValueError('Current canonical revision changes a frozen source row/field/crop')
        if set(old['resolvedValues'])!=set(new['resolvedValues'])or any(old['resolvedValues'][f]!=new['resolvedValues'][f]for f in old['resolvedValues']if f!='name'):
            raise ValueError('Current canonical revision changes a financial or unrelated field')
        if 'name'not in new['resolvedValues']:continue
        if key not in rows:
            if old['resolvedValues']['name']!=new['resolvedValues']['name']or old['status']!=new['status']:
                raise ValueError('Current canonical revision changes an unreviewed name')
            continue
        accepted=rows[key];value=accepted['currentAcceptedSourceLiteral'];q=qualification.get(key)
        family=[q['chosenName']]+q['visibleAlternatives']if q else[value]
        if (new['resolvedValues']['name']!=value or set(family)!=set(accepted['currentCompleteVisibleAlternatives'])
                or (new['status']in r.QUALIFIED)!=(accepted['currentSourceStatus']=='qualified')):
            raise ValueError('Current overlay differs from exact accepted human literal/full family/status')
