#!/usr/bin/env python3
"""Replay early001's complete55 peer scope and the original sparse616 fields."""
import csv
import re
import finish_salary_phsa_ledger as ledger


def replay(review,source,read,image_check,unique,key):
    rawref=review['rootSourceFirstTranscript'];raw=read(rawref);packet=read(review['sourceOnlyPacket'])
    author=read(review['onlyMatchingFiftyfiveComparisonAfterBothFreezes'])
    current=read(review['independentCurrentActualSourceRereadBeforeRootChoices'])
    original=read(author['originalSelected001Review']);freeze=read(author['originalSparseTranscriptFreezeReceipt'])
    amendments=read(author['originalPostcomparisonSourceAmendments'])
    batchpath=ledger.AREA/'batches'/f'{source[2][:-4]}-batch-{source[2][-3:]}.json'
    batch=read({'path':str(batchpath.relative_to(ledger.ROOT)),'sha256':original['frozenBatchSha256']})
    for document in [review,raw,packet,author,current,original,freeze,amendments,batch]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Sparse current source/first/review identity differs')
    if (review['frozen']is not True or review['accepted']is not True or review['closed']is not True or review['unresolved']
            or raw['frozen']is not True or packet['frozen']is not True or author['frozen']is not True or current['frozen']is not True
            or raw['authorOrCandidateChoicesOpenedAtFreeze']is not False or raw['correspondingIndependentCurrentRereadOpenedAtFreeze']is not False
            or current['rootCorrespondingFreshFiftyFiveChoicesOpened']is not False or author['rootCorrespondingFreshFiftyFiveChoicesOpened']is not False
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']or author['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or current['sourceOnlyPacket']!=review['sourceOnlyPacket']or author['currentOwnCanonicalSourceReread']!=review['independentCurrentActualSourceRereadBeforeRootChoices']
            or freeze['fullCandidateAndRawOcrAlternativesNotOpenedBeforeThisFreeze']is not True
            or freeze['allRequestedFieldsPersonallyReadFromActualPdfSourceImages']is not True
            or freeze['rawTranscriptPath']!=author['originalSparseImageFirstTranscript']['path']
            or freeze['rawTranscriptSha256']!=author['originalSparseImageFirstTranscript']['sha256']
            or original['rawTranscriptPath']!=freeze['rawTranscriptPath']or original['rawTranscriptSha256']!=freeze['rawTranscriptSha256']):
        raise ValueError('Sparse current source-first chronology/raw byte scope differs')
    path=(ledger.ROOT/author['originalSparseImageFirstTranscript']['path']).resolve()
    if not path.is_relative_to(ledger.ROOT)or ledger.sha(path.read_bytes())!=author['originalSparseImageFirstTranscript']['sha256']:
        raise ValueError('Original sparse616 source transcript changed')
    events={};columns={'nameLiteral':'name','remunerationLiteral':'remuneration','expensesLiteral':'expenses'}
    with path.open()as handle:
        for event in csv.DictReader(handle,delimiter='\t'):
            for column,field in columns.items():
                if event[column]=='':continue
                identity=int(event['sequence']),field
                if identity in events:raise ValueError('Duplicate nonempty sparse source field')
                events[identity]=event[column]
    expected={(r['sequence'],field)for r in batch['rows']for field in r['reviewTargetFields']}
    if set(events)!=expected or len(expected)!=freeze['requestedFieldCount']or len(expected)!=616:
        raise ValueError('Sparse source transcript does not cover its complete original616 fields')
    targets,first,peers,authors,latest=map(unique,[packet['rows'],raw['rows'],review['rows'],author['rows'],current['rows']])
    pixels={(r['physicalPage'],r['sourceRowOnPage'],r['field']):r for r in raw['sourcePixelReproduction']}
    if (len(targets)!=55 or any(set(v)!=set(targets)for v in [first,peers,authors,latest,pixels])
            or len(pixels)!=len(raw['sourcePixelReproduction'])):
        raise ValueError('Sparse current peer/raw/image/full field scopes differ')
    if (packet['sourceOnly']is not True or packet['expectedAuthorOrEngineValuesIncluded']is not False
            or packet['originalSourcePdfSha256']!=source[1]or packet['fieldCount']!=55
            or packet['fieldCounts']!={'remuneration':26,'expenses':29}
            or raw['counts']!={'fields':55,'remuneration':26,'expenses':29,'strictPositiveIntegers':55,
                              'unresolvedSourceQuestions':0,'rootOwnBeforeChoiceValueCorrections':0,'sourceViewsRgbExact':165}
            or current['counts']!={'fields':55,'remuneration':26,'expenses':29,'unresolved':0,'actualSourceRgbComparisons':110}
            or author['counts']!={'fields':55,'earliestFirstVersusCurrentDifferences':3,'oldSelected001VersusCurrentDifferences':3,'unresolved':0}):
        raise ValueError('Sparse current full target/first/current source counters differ')
    original_rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in original['resolutions']}
    batchrows={r['sequence']:r for r in batch['rows']};facts=[];author_count=peer_count=0
    changes=unique(review['oldSelectedSourceValueCorrections'])
    for identity,target in targets.items():
        seq=target['sequence'];field=identity[2];o,p,a,h,v=first[identity],peers[identity],authors[identity],latest[identity],pixels[identity]
        text=events[seq,field]
        if not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',text):raise ValueError('Sparse current target is not a positive whole-dollar first literal')
        before=int(text.replace(',',''));old=original_rows[identity[:2]]['resolvedValues'][field];value=h['literalImageValue'];rootfirst=o['literalImageValue']
        if (field not in ['remuneration','expenses']or any(type(x)is not int or x<=0 for x in [before,old,value,rootfirst,p['literalImageValue']])
                or any(r['sequence']!=seq for r in [o,p,a,h,v])or any(r['cropSha256']!=target['cropSha256']for r in [o,p,a,h])
                or a['originalSparseFirstLiteralText']!=text or a['originalSparseFirstValue']!=before or before!=old
                or a['earlierPostcomparisonSourceCorrection']is not None or a['oldSelected001SourceValue']!=old
                or a['currentPersonalWhole600AndNative300Value']!=value or a['currentSourceUncertainty']is not None
                or a['currentDiffersFromOldSelected001']!=(old!=value)or h['sourceUncertainty']is not None or o['sourceUncertainty']is not None
                or p['rootFirstLiteralImageValue']!=rootfirst or p['literalImageValue']!=value or p['sourceUncertainty']is not None
                or o['firstWhole600LiteralImageValue']!=rootfirst or not o['native300ContextRefinementBeforeMatchingChoices']
                or o['personallyReadWhole600Field']is not True or o['personallyReadNative300Context']is not True
                or p['oldSelected001SourceValue']!=old or p['currentMatchesIndependentSourceRereadExactly']is not True
                or p['earlierSelectedSourceValueCorrectionRequired']!=(old!=value)or p['rootOwnFirstReadCorrection']!=(rootfirst!=value)
                or batchrows[seq]['cropSha256']!=target['cropSha256']or field not in batchrows[seq]['reviewTargetFields']
                or (batchrows[seq]['physicalPage'],batchrows[seq]['sourceRowOnPage'])!=identity[:2]
                or (o['sourceId'],o['sourceSha256'])!=source[:2]or (p['sourceId'],p['sourceSha256'])!=source[:2]
                or o['allThreeSourceViewsIndependentlyRgbExact']is not True or p['allThreeSourceViewsIndependentlyRgbExact']is not True
                or {r['view']:r['rgbPixelExact']for r in v['views']}!={'native300Field':True,'wholePage600Field':True,'native300Context':True}):
            raise ValueError('Sparse current original/old-selected/new-independent/source facts differ')
        if rootfirst!=value and not p['rootPostcomparisonOriginalSourceReread']:
            raise ValueError('Root current literal correction lacks an explicit source reread')
        if (old!=value)!=(identity in changes):raise ValueError('Old selected source errors are not exactly declared')
        if identity in changes and changes[identity]!={'sequence':seq,'physicalPage':identity[0],'sourceRowOnPage':identity[1],
                                                     'field':field,'oldValue':old,'currentLiteralValue':value}:
            raise ValueError('Declared original source correction differs from frozen first/current values')
        for name in ['native300Field','wholePage600Field','native300Context']:
            ref=target[name]
            if o[name]!=ref or p[name]!=ref:raise ValueError('Root sparse current source image identity differs')
            if name!='native300Context'and(a[name]!=ref or h[name]!=ref):raise ValueError('Author current source view identity differs')
            image_check(ref)
        author_count+=before!=value;peer_count+=rootfirst!=value
        facts.append((target,value,target['wholePage600Field'],target['cropSha256']))
    if (review['counts']!={'fields':55,'positiveLiteralFields':55,'remuneration':26,'expenses':29,
                           'rootFirstValuesMatchingCurrentSource':55-peer_count,'rootOwnFirstValueErrorsCorrectedAfterActualSourceReread':peer_count,
                           'earlierSelectedMonetaryCellsRequiringSourceCorrection':author_count,'currentExactIndependentMatches':55,'unresolved':0}
            or author_count!=3 or peer_count!=1 or len(changes)!=3):
        raise ValueError('Sparse current complete source scope/correction counts differ')
    return facts,rawref,author_count,peer_count


def validate_financial_review(review):
    import finish_salary_phsa_money_peer as money
    import finish_salary_phsa_resolutions as resolutions
    spec=review['canonicalCurrentFinancialSourceRevision'];before=ledger.pinned(spec['previousFrozenSourceReview'])
    peer=ledger.pinned(spec['freshCurrentSourcePeer']);source=tuple(review[k]for k in ['sourceId','sourceSha256','batch'])
    facts,_,_,_=replay(peer,source,ledger.pinned,money.source_image_check,money.unique,money.key)
    current={money.key(row):value for row,value,_,_ in facts};oldrows=before['resolutions'];newrows=review['resolutions']
    if (spec['exactSourceCorrections']!=peer['oldSelectedSourceValueCorrections']
            or spec['unchangedNamesQualificationsAndAllOtherValues']is not True
            or spec['originalFirstPassAndIntermediateErrorsRemainFrozen']is not True
            or tuple(before[k]for k in ['sourceId','sourceSha256','batch'])!=source or len(oldrows)!=len(newrows)
            or review['sourceTypographyQualifications']!=before['sourceTypographyQualifications']
            or review.get('canonicalCurrentSourceNameRevision')!=before.get('canonicalCurrentSourceNameRevision')
            or review.get('closedSourceNameQualificationLedgers')!=before.get('closedSourceNameQualificationLedgers')):
        raise ValueError('Financial source revision changed original name authority/source scope')
    changes=0
    for old,new in zip(oldrows,newrows):
        if any(old[k]!=new[k]for k in ['physicalPage','sourceRowOnPage','reviewTargetFields','cropSha256','status']):
            raise ValueError('Financial source revision changed a name/status/field/source crop')
        if set(old['resolvedValues'])!=set(new['resolvedValues']):
            raise ValueError('Financial source revision changed resolved field membership')
        for field,value in new['resolvedValues'].items():
            key=new['physicalPage'],new['sourceRowOnPage'],field
            if field=='name'or key not in current:
                if value!=old['resolvedValues'][field]:raise ValueError('Financial source revision changed an unreviewed value')
            else:
                if type(value)is not int or value!=current[key]:raise ValueError('Financial source revision differs from two current source readers')
                changes+=value!=old['resolvedValues'][field]
    if changes!=3:raise ValueError('Financial source revision must correct exactly three source cells')
