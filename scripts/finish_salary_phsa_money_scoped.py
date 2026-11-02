#!/usr/bin/env python3
"""Replay a complete mixed-field image peer and its bounded fresh adjudication."""
import re


def literal(value,field):
    if field=='name':return value
    if not isinstance(value,str)or not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',value):
        raise ValueError('Scoped author money is not a literal positive integer')
    return int(value.replace(',',''))


def replay(review,overlay,source,read,image_check,unique,key):
    rawref=review['originalPeerImageFirstTranscript'];raw=read(rawref);packet=read(review['sourceOnlyPacket'])
    scoped=read(review['scopedSchool88AuthorChoices']);pixels=read(review['sourcePixelProof'])
    archive=read(review['exactSourceViewArchive']);author_review=read(overlay['reviewInput'])
    author_ref={'path':author_review['rawTranscriptPath'],'sha256':author_review['rawTranscriptSha256']};author=read(author_ref)
    for document in [review,raw,packet,scoped,pixels,archive,author_review,author]:
        if (document['sourceId'],document['sourceSha256'])!=source[:2]or ('batch'in document and document['batch']!=source[2]):
            raise ValueError('Scoped field source/header differs')
    if (raw['frozen']is not True or raw['supplementalAuthorChoicesOrOcrAlternativesOpenedBeforeFreeze']is not False
            or raw['personallyReadAll88Actual1200OriginalFields']is not True
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']or raw['sourcePixelProof']!=review['sourcePixelProof']
            or author['fullCandidateUnopenedAtFreeze']is not True or scoped['authorOriginalRawSha256']!=author_ref['sha256']
            or review['counts']['unresolved']!=0):
        raise ValueError('Scoped field first-reading order/source raw differs')
    target={}
    for row in packet['rows']:
        for field in row['reviewTargetFields']:
            entry={**row,'field':field};identity=key(entry)
            if identity in target:raise ValueError('Duplicate scoped source field')
            entry['image']=next(v for v in row['actualOriginal1200Renders']if v['field']==field);target[identity]=entry
    first=unique(raw['rows']);final=unique(review['rows']);proof=unique(pixels['rows']);copies=unique(archive['rows'])
    if any(set(v)!=set(target)for v in [first,final,proof])or not set(target)<=set(copies):
        raise ValueError('Scoped original field/first/final/pixel set incomplete')
    authors={r['sequence']:r for r in author['rows']};choices={r['sequence']:r for r in scoped['rows']}
    if len(authors)!=len(author['rows'])or len(choices)!=len(scoped['rows']):raise ValueError('Duplicate scoped author row')
    current={k:r['literalSourceValueFirstPass']for k,r in first.items()}
    for reference in review['peerSourceRereadHistory']:
        amendment=read(reference)
        if (amendment['sourceId'],amendment['sourceSha256'],amendment['batch'])!=source:
            raise ValueError('Scoped amendment belongs to another source/batch')
        changes=unique(amendment['changes'])
        if not set(changes)<=set(target):raise ValueError('Scoped amendment widens field coverage')
        for identity,change in changes.items():
            original=first[identity]['literalSourceValueFirstPass']
            for field in ['literalSourceValueFirstPass','firstHealthSourceReading','originalBlindHealthReading']:
                if field in change and change[field]!=original:raise ValueError('Scoped amendment hides original first literal')
            for field in ['previousHealthSecondaryReading','rejectedHealthSecondaryReading']:
                if field in change and change[field]!=current[identity]:raise ValueError('Scoped amendment hides intermediate literal')
            current[identity]=change['currentLiteralSourceReading']
    chronology=read(review['finalTwoNameObservationTimingClarification'])
    if (chronology['sourceId'],chronology['sourceSha256'],chronology['batch'])!=source:
        raise ValueError('Scoped source observation chronology belongs to another source')
    third=read(review['freshThird24Adjudication']);third_raw_ref=third['ownIndependentSourceFirstBeforeChoices']
    third_raw=read(third_raw_ref);third_changes=read(third['ownPostcomparisonActualSourceRereadAddendum'])
    third_first=unique(third_raw['entries']);third_final=unique(third['rows']);third_second=unique(third_changes['entries'])
    third_packet=read(third_raw['sourceOnlyPacket']);third_target=set()
    for document in [third,third_raw,third_changes,third_packet]:
        if (document['sourceId'],document['sourceSha256'])!=source[:2]or ('batch'in document and document['batch']!=source[2]):
            raise ValueError('Fresh scoped adjudication source/header differs')
    for row in third_packet['rows']:
        third_target.update((row['physicalPage'],row['sourceRowOnPage'],f)for f in row['reviewTargetFields'])
    if (third_raw['correspondingAuthorSchoolOcrValuesNotOpenedBeforeFreeze']is not True
            or third_changes['rawBeforeCorrespondingChoices']!=third_raw_ref
            or set(third_first)!=third_target or set(third_final)!=third_target or set(third_second)!=third_target
            or not third_target<=set(target)or (third['sourceId'],third['sourceSha256'],third['batch'])!=source):
        raise ValueError('Fresh scoped adjudication first/current/target history differs')
    third_money_changes=0
    for identity,entry in third_final.items():
        if identity[2]=='name':continue
        original=third_first[identity]['literalSourceValue'];second=third_second[identity]
        image=target[identity]['image']
        if (entry['ownIndependentColdLiteral']!=original or second['ownOriginalColdLiteral']!=original
                or any(r['sequence']!=target[identity]['sequence']for r in [third_first[identity],entry,second])
                or second['ownCurrentLiteral']!=entry['currentLiteralSourceValue']
                or second['ownPostComparisonCorrection']!=(original!=entry['currentLiteralSourceValue'])
                or second['realUncertainty']is not None or entry['currentLiteralSourceValue']!=current[identity]
                or entry['cropSha256']!=target[identity]['cropSha256']
                or third_first[identity]['cropSha256']!=target[identity]['cropSha256']
                or image not in third_first[identity]['actualOriginal1200Renders']
                or image not in entry['actualOriginal1200SourceViews']):
            raise ValueError('Fresh scoped monetary adjudication differs from original/reread')
        third_money_changes+=original!=entry['currentLiteralSourceValue']
    if third_money_changes!=third['counts']['ownColdMoneyCorrections']or third['counts']['unresolvedMoney']!=0:
        raise ValueError('Fresh scoped monetary uncertainty/correction counts differ')
    facts=[];own={};author_total=author_money=0
    for identity,entry in target.items():
        seq=entry['sequence'];field=identity[2];o,p,v,c=first[identity],final[identity],proof[identity],copies[identity]
        original_author=authors[seq];choice=choices[seq]
        first_author=literal(original_author['sourceImageReadings'][field],field)
        if first_author!=literal(choice['originalFrozenRawReadings'][field],field):
            raise ValueError('Scoped author choices hide original frozen first value')
        value=current[identity];image=entry['image'];crop=entry['cropSha256'];copy=v['archivedExactBytes']
        if ((original_author['physicalPage'],original_author['sourceRowOnPage'])!=identity[:2]
                or field not in original_author['reviewTargetFields']or original_author['cropSha256']!=crop
                or o['originalFullRowCropSha256']!=crop or p['originalFullRowCropSha256']!=crop
                or o['originalActual1200SourceView']!=image or p['actualOriginal1200SourceView']!=image
                or v['actual1200SourceView']!=image or v['actualOriginal1200PixelsIndependentlyReproducedExactly']is not True
                or copy['sha256']!=image['sha256']or c['originalReference']!=image or c['archivedExactBytes']!=copy
                or p['firstPeerSourceValue']!=o['literalSourceValueFirstPass']or p['finalPeerSourceValue']!=value
                or p['firstFrozenSchoolSourceValue']!=first_author or p['finalSchoolSourceValue']!=value
                or p['matchesCurrentSchoolSourceExactly']is not True):
            raise ValueError('Scoped original/final/source-view/crop proof differs')
        if field!='name':
            if (type(value)is not int or value<=0 or value!=literal(choice['currentAuthorSourceReadings'][field],field)
                    or p['status']!='resolved-from-original-image'):
                raise ValueError('Scoped positive money has uncertainty or differs from independently read author')
            if value!=o['literalSourceValueFirstPass']and identity not in third_target:
                raise ValueError('Changed fresh-peer money requires bounded independent adjudication')
            author_money+=first_author!=value
        image_check(copy);facts.append((entry,value,copy,crop));own[field]=own.get(field,0)+(o['literalSourceValueFirstPass']!=value);author_total+=first_author!=value
    counts=review['counts']
    if (len(facts)!=counts['sourceFields']or sum(r[0]['field']!='name'for r in facts)!=counts['positiveMoney']
            or author_total!=counts['authorOriginalFirstFieldsDifferentFromFinal']
            or own['name']!=counts['ownFirstPeerNameCorrections']or own['remuneration']!=counts['ownFirstPeerPayCorrections']
            or own['expenses']!=counts['ownFirstPeerExpenseCorrections']):
        raise ValueError('Scoped source/first-reading correction counts differ')
    return facts,rawref,author_money,own['remuneration']+own['expenses']
