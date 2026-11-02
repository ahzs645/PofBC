#!/usr/bin/env python3
"""Strict replay of complete source-money peers with additive reading histories."""
import csv
import json
import re


def root_positive_table(review,overlay,source,read,image_check,unique,key):
    choice_keys=[k for k in review if re.fullmatch(r'scopedAuthor[0-9]+OnlyChoices',k)]
    if len(choice_keys)!=1:raise ValueError('Exactly one count-bounded root monetary choice set is required')
    count=int(re.search(r'[0-9]+',choice_keys[0]).group())
    rawref=review['rootImageFirstRaw'];raw=read(rawref);packet=read(raw['sourceOnlyPacket'])
    choices=read(review[choice_keys[0]]);proof=read(review['sourcePixelProof'])
    author_review=read(overlay['reviewInput']);author=read({'path':author_review['rawTranscriptPath'],'sha256':author_review['rawTranscriptSha256']})
    for document in [review,raw,packet,choices,proof,author_review,author]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Count-bounded root/source/author identity differs')
    if (raw['frozen']is not True or raw['candidateOrAuthorValuesOpened']is not False
            or author['fullCandidateUnopenedAtFreeze']is not True
            or choices['rootFrozen53RawSha256']!=review['rootImageFirstRaw']['sha256']
            or proof['sourceOnlyPacket']!=raw['sourceOnlyPacket']or review['rawBytesChanged']is not False):
        raise ValueError('Count-bounded root source-first order differs')
    targets,first,peers,authors,pixels=map(unique,[packet['rows'],raw['rows'],review['rows'],choices['rows'],proof['rows']])
    changes=unique(review['ownAdditiveSourceCorrections']);originals={r['sequence']:r for r in author['rows']}
    if count!=len(targets)or any(set(v)!=set(targets)for v in [first,peers,authors,pixels])or not set(changes)<=set(targets):
        raise ValueError('Count-bounded root monetary field scope differs')
    def amount(value):
        if not isinstance(value,str)or not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',value):
            raise ValueError('Count-bounded author first/current money is not a literal whole-dollar string')
        return int(value.replace(',',''))
    facts=[];author_count=peer_count=0
    for identity,entry in targets.items():
        seq=entry['sequence'];field=identity[2];original=originals[seq];o,p,a,v=first[identity],peers[identity],authors[identity],pixels[identity]
        before=amount(original['sourceImageReadings'][field]);current=amount(a['currentSourceReading'])
        peer_first=o['rootFirstImageReading'];peer_final=changes[identity]['rootCurrentSourceReading']if identity in changes else peer_first
        image=entry['actualOriginal1200SourceField'];crop=entry['cropSha256']
        if (field not in ['remuneration','expenses']or any(type(x)is not int or x<=0 for x in [before,current,peer_first,peer_final])
                or field not in original['reviewTargetFields']or original['cropSha256']!=crop
                or (original['physicalPage'],original['sourceRowOnPage'])!=identity[:2]
                or any(row['sequence']!=seq for row in [o,p,a,v])or any(row['cropSha256']!=crop for row in [o,p,a])
                or amount(a['originalFrozenRawReading'])!=before or a['changedFromFrozenRaw']!=(before!=current)
                or o['actualOriginal1200SourceField']!=image or v['source1200FileSha256']!=image['sha256']
                or v['actual1200RgbExact']is not True or v['native300FieldRgbExact']is not True
                or p['rootFirstImageReading']!=peer_first or p['rootCurrentSourceReading']!=peer_final
                or amount(p['authorFirstSourceReading'])!=before or amount(p['authorCurrentSourceReading'])!=current
                or peer_final!=current or p['positiveLiteralValuesAgree']is not True):
            raise ValueError('Count-bounded root raw/author/current/pixel facts differ')
        if identity in changes:
            change=changes[identity]
            if (change['rootFirstImageReading']!=peer_first or change['cropSha256']!=crop
                    or change['source2400RgbExact']is not True):
                raise ValueError('Root own reread hides original first value/source pixels')
            image_check(change['actualCurrentOriginal2400'])
        image_check(image);facts.append((entry,current,image,crop));author_count+=before!=current;peer_count+=peer_first!=peer_final
    expected={'positiveFields':count,'firstRootCurrentMatches':count-peer_count,'rootOwnFirstDigitCorrections':peer_count,
              'authorOwnFirstDigitCorrections':author_count,'allCurrentLiteralFieldsAgree':count,'unresolved':0,'qualifiedMonetaryFields':0}
    if review['counts']!=expected or len(changes)!=peer_count:raise ValueError('Root source/correction totals differ')
    return facts,rawref,author_count,peer_count


def one_root_peer(review,source,read,image_check,unique,key):
    rawref=review['rootImageFirstRaw'];raw=read(rawref);packet=read(raw['sourceOnlyPacket'])
    choice=read(review['scopedAuthorOneChoice']);author=read(choice['sourceFirstTranscript'])
    for document in [raw,packet,choice,author]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('One-cell source/author identity differs')
    if (raw['frozen']is not True or raw['candidateOrAuthorValuesOpened']is not False
            or author['candidateOpened']is not False or author['correspondingPeerChoicesOpened']is not False
            or review['rootOwnCorrections']!=0 or review['authorOwnCorrections']!=0
            or review['source1200RgbReproducedExactly']is not True or choice['ownCorrection']is not False):
        raise ValueError('One-cell source-first/no-change gate differs')
    if packet['sourceOnly']is not True:raise ValueError('One-cell source packet contains choices')
    targets,first,peers=map(unique,[[packet['field']],raw['rows'],review['rows']]);originals=unique(author['readings'])
    if len(targets)!=1 or set(targets)!=set(first)or set(targets)!=set(peers)or key(choice)not in targets:
        raise ValueError('One-cell source/first/final scope differs')
    identity=key(choice);entry,original,peer=targets[identity],first[identity],peers[identity]
    author_first=originals[identity];value=original['rootFirstImageReading'];image=original['actualOriginal1200SourceField'];crop=entry['cropSha256']
    if (identity[2]not in ['remuneration','expenses']or type(value)is not int or value<=0
            or any(type(v)is not int for v in [choice['firstSourceReading'],choice['currentSourceReading'],author_first['value']])
            or choice['firstSourceReading']!=value or choice['currentSourceReading']!=value or author_first['value']!=value
            or int(choice['literalPrinted'].replace(',',''))!=value or author_first['uncertain']is not False
            or original['uncertain']is not False or original['source1200RgbExact']is not True
            or original['actualSourceField']!=entry['actualSourceField']or image['sha256']!=entry['actualSourceField']['sha256']
            or any(r['cropSha256']!=crop for r in [original,peer,choice,author_first])
            or any(r['sequence']!=entry['sequence']for r in [original,peer,choice,author_first])
            or any(peer[k]!=value for k in ['rootFirstSourceReading','rootCurrentSourceReading','authorFirstSourceReading','authorCurrentSourceReading'])
            or peer['allPositiveLiteralValuesMatch']is not True):
        raise ValueError('One-cell source/raw first/current/pixel facts differ')
    image_check(image)
    return [(entry,value,image,crop)],rawref


def literal_tuple_peer(review,source,read,image_check,unique,key):
    """Source-first literalImageValue rows with explicit author reread tuples."""
    rawref=review['independentImageFirstTranscript'];raw=read(rawref);packet=read(review['sourceOnlyPacket'])
    proof=read(review['independentSourcePixelProof']);choices=read(review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze'])
    author=read(review['authorOriginalFrozenTranscript'])
    reread=read(choices['ownEarlierFrozenFortySourceRereads'])if 'ownEarlierFrozenFortySourceRereads'in choices else choices
    amendments=read(review['peerOwnAdditiveSourceCorrections'])if review['peerOwnAdditiveSourceCorrections']else None
    for document in [raw,packet,proof,choices,author,reread]+([amendments]if amendments else[]):
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Literal tuple source/raw identity differs')
    if (raw['frozen']is not True or raw['correspondingChoicesOpened']is not False
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']or review['unresolvedFields']
            or review['allFinalSourceValuesMatchExactly']is not True
            or author['candidateOpenedBeforeFreeze']is not False
            or reread['rawImageFirstTranscript']!=review['authorOriginalFrozenTranscript']
            or reread.get('sourceOnlyPeerPacket',reread.get('sourceOnlyPacket'))!=review['sourceOnlyPacket']
            or reread['beforeFreshPeerChoicesOpened']is not True):
        raise ValueError('Literal tuple source-first chronology differs')
    if 'freshSourceFirstRaw'in choices and choices['freshSourceFirstRaw']!=rawref:
        raise ValueError('Scoped author choices pin a different first source transcript')
    if 'sourceOnlyPacket'in proof and proof['sourceOnlyPacket']!=review['sourceOnlyPacket']:
        raise ValueError('Literal tuple source proof pins a different target set')
    if amendments and amendments['originalFrozenImageFirstTranscript']!=rawref:
        raise ValueError('Literal tuple peer amendment does not preserve its raw')
    targets,first,peers,authors,pixels=map(unique,[packet['rows'],raw['rows'],review['rows'],reread['rows'],proof.get('rows',proof.get('checks',[]))])
    scoped=unique(choices['rows']);originals={(r['physicalPage'],r['sourceRowOnPage']):r for r in author['rows']}
    changes=unique(amendments['changes'])if amendments else{}
    if (any(set(x)!=set(targets)for x in [first,peers,authors,pixels,scoped])or not set(changes)<=set(targets)
            or len(originals)!=len(author['rows'])):
        raise ValueError('Literal tuple first/proof/choice scope differs')
    facts=[];author_count=peer_count=0
    for identity,entry in targets.items():
        o,p,a,v,s=first[identity],peers[identity],authors[identity],pixels[identity],scoped[identity]
        original=originals[identity[:2]];field=identity[2];before=original['imageFirstValues'][field]
        current=a['currentOriginal1200LiteralValue'];peer_first=o['literalImageValue']
        peer_final=changes[identity]['finalSourceValue']if identity in changes else peer_first
        image=entry['actual1200SourceField'];crop=entry['originalFullRowCrop']['sha256']
        if (field not in ['remuneration','expenses']or any(type(x)is not int or x<=0 for x in [before,current,peer_first,peer_final])
                or o.get('sourceUncertainty',o.get('uncertainty'))is not None
                or any(row['sequence']!=entry['sequence']for row in [o,p,a,v,s])
                or field not in original['reviewTargetFields']or original['sourceCropSha256']!=crop
                or a['firstFrozenValue']!=before
                or ('firstLiteralChanged'in a and a['firstLiteralChanged']!=(before!=current))
                or ('firstLiteralChanged'not in a and reread.get('all40FirstLiteralAmountsRetained')is not True)
                or (reread.get('all40FirstLiteralAmountsRetained')is True and before!=current)
                or a['sourceEvidence']['actual1200SourceField']!=image or a['sourceEvidence']['originalFullRowCrop']['sha256']!=crop
                or o['actual1200SourceField']!=image or p['actual1200OriginalField']!=image
                or v.get('originalReference',v.get('actual1200SourceField'))!=image
                or v['actual1200PixelsMatch']is not True or v['actual300FullRowAndNativeFieldPixelsMatch']is not True
                or p['firstPeerSourceValue']!=peer_first or p['finalPeerSourceValue']!=peer_final
                or p['initialAuthorSourceValue']!=before or p['intermediateAuthorSourceValue']!=current
                or p['finalAuthorSourceValue']!=current or current!=peer_final
                or p['originalFullRowCropSha256']!=crop or p['finalIndependentSourceValuesMatchExactly']is not True
                or p['eligibleForPositiveMoneyConfirmation']is not True or p['literalDashNullConfirmed']is not False):
            raise ValueError('Literal tuple first/current/source/pixel facts differ')
        if 'firstFrozenLiteralAmount'in s:
            if s['firstFrozenLiteralAmount']!=before or s['currentLiteralSourceAmount']!=current or s['cropSha256']!=crop:
                raise ValueError('Thin scoped money choices differ from actual first/reread')
        if identity in changes:
            c=changes[identity]
            if c['firstPeerSourceValue']!=peer_first:raise ValueError('Literal tuple amendment hides first source value')
            image_check(c['actual2400OriginalSource'])
        image_check(image);facts.append((entry,current,image,crop));author_count+=before!=current;peer_count+=peer_first!=peer_final
    if (len(facts)!=review['fieldsPersonallyReadBeforeAuthorChoices']or len(facts)!=review['positiveMonetaryFieldsConfirmed']
            or review['literalDashNullFieldsConfirmedSeparately']!=0 or author_count!=review['authorOwnFirstReadingCorrections']
            or peer_count!=review['peerOwnFirstReadingCorrections']):
        raise ValueError('Literal tuple source/scope/correction counters differ')
    return facts,rawref,author_count,peer_count


def unchanged_overlay_peer(review,source,read,image_check,unique,key):
    """Complete unchanged field table with a separately supplied effective overlay."""
    rawref=review['peerRawSourceFirst'];raw=read(rawref);packet=read(review['sourceOnlyPacket'])
    choices=read(review['authorScopedChoicesOpenedAfterRaw']);author=read(choices['rawImageFirst'])
    for document in [raw,packet,choices,author]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Unchanged source-table raw identity differs')
    if (raw['frozen']is not True or raw['correspondingChoicesOpened']is not False
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or choices['sourceOnlyPacket']!=review['sourceOnlyPacket']or choices['peerValuesNotYetOpened']is not True
            or author['fullCandidateOrCorrespondingOcrOpenedBeforeFreeze']is not False or author['frozen']is not True):
        raise ValueError('Unchanged source-table first-reading chronology differs')
    targets,first,peers,authors=map(unique,[packet['rows'],raw['rows'],review['rows'],choices['rows']])
    original=unique(author['rows'])
    if (not targets or any(set(r)!=set(targets)for r in [first,peers,authors])or not set(targets)<=set(original)
            or any(type(v)is not int for v in review['counts'].values())
            or review['counts']!={'sourceFields':len(targets),'positiveIntegerFields':len(targets),
                                  'firstValuesMatchingAuthor':len(targets),'ownSourceCorrections':0,'unresolved':0}):
        raise ValueError('Unchanged source-table target set/counts differ')
    facts=[]
    for identity,entry in targets.items():
        before,peer,choice,author_first=first[identity],peers[identity],authors[identity],original[identity]
        value=before['literalImageValue'];image=entry['actual1200Source'];crop=entry['cropSha256']
        if (identity[2]not in ['remuneration','expenses']or type(value)is not int or value<=0
                or any(type(v)is not int for v in [choice['ownOriginalFrozenLiteral'],choice['ownCurrentLiteral'],author_first['literalSourceValue'],
                                                  peer['peerInitialImageFirstValue'],peer['peerFinalValue'],peer['authorFinalValue']])
                or value!=choice['ownCurrentLiteral']or value!=choice['ownOriginalFrozenLiteral']or value!=author_first['literalSourceValue']
                or choice['ownLiteralCorrection']is not False or choice['realUncertainty']is not None
                or before['uncertainty']is not None or int(before['literalImageText'].replace(',',''))!=value
                or any(r['sequence']!=entry['sequence']for r in [before,peer,choice,author_first])
                or any(r['cropSha256']!=crop for r in [before,choice,author_first])
                or before['actual1200Source']!=image or choice['sourceProof']['actual1200Source']!=image
                or peer['sourceImage']!=image or peer['peerInitialImageFirstValue']!=value or peer['peerFinalValue']!=value
                or peer['authorFinalValue']!=value or peer['independentActualPdfPixelsMatch']is not True
                or peer['status']!='confirmed-exact-from-original-image'):
            raise ValueError('Unchanged source-table literal/raw/source proof differs')
        image_check(image);facts.append((entry,value,image,crop))
    return facts,rawref


def ordered_peer(review,source,read,image_check,unique,key):
    """Legacy root52 packet: raw is ordered, all later arrays join by tuples."""
    rawref=review['independentImageFirstTranscript'];raw=read(rawref)
    packet=read(review['sourceOnlyPacket']);choices=read(review['authorChoicesOpenedAfterTranscriptFreeze'])
    proof=read(review['sourcePixelProof']);amend=read(review['authorOwnCorrectionsFrozenBeforeRootFirstReading'])
    authorref=choices['independentOriginalImageFirstTranscript'];author=read(authorref)
    targets,authors,peers,pixels=map(unique,[packet['rows'],choices['rows'],review['rows'],proof['rows']])
    changes=unique(amend['ownCorrections']);rereads=unique(amend['personallyRecheckedActual1200MoneyFields'])
    if (any(set(x)!=set(targets)for x in [authors,peers,pixels,rereads])or not set(changes)<=set(targets)
            or raw['authorOrOcrChoicesOpened']is not False or raw['frozen']is not True or raw['unresolvedFields']
            or author['frozenBeforeOpeningFullCandidate']is not True or author['fullCandidateOpened']is not False
            or choices['peerValuesOpened']is not False or choices['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or choices['authorOwnPostComparisonSourceReread']!=review['authorOwnCorrectionsFrozenBeforeRootFirstReading']
            or amend['originalFrozenFirstPass']!=authorref or amend['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or proof['sourceOnlyPacketSha256']!=review['sourceOnlyPacket']['sha256']or proof['sourceSha256']!=source[1]
            or review['all52FinalLiteralValuesMatch']is not True or len(targets)!=52
            or review['rootOwnCorrections']!=0 or review['unresolvedFields']
            or len(raw['readingsInPacketOrder'])!=len(targets)):
        raise ValueError('Ordered fresh source-money history/scope gate differs')
    for document in [raw,packet,choices,amend,author]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Ordered source-money evidence identity differs')
    originals={(r['physicalPage'],r['sourceRowOnPage']):r for r in author['rows']}
    if len(originals)!=len(author['rows']):raise ValueError('Duplicate original author source row')
    facts=[];count=0
    for i,entry in enumerate(packet['rows']):
        identity=key(entry);choice,peer,pixel,reread=authors[identity],peers[identity],pixels[identity],rereads[identity]
        field=identity[2];first=originals[identity[:2]]['literalSourceValuesFirstPass'][field]
        final=changes[identity]['literalSourceReread']if identity in changes else first
        value=raw['readingsInPacketOrder'][i];image=entry['actual600SourceField'];crop=entry['originalFullRowCropSha256']
        if field not in ['remuneration','expenses']or any(type(v)is not int or v<=0 for v in [first,final,value]):
            raise ValueError('Ordered source money must retain literal positive integer types')
        if (any(r['sequence']!=entry['sequence']for r in [choice,peer,pixel,reread])
                or choice['initialImageFirstValue']!=first or choice['finalAuthorSourceValue']!=final
                or choice['actual600SourceField']!=image or choice['originalFullRowCropSha256']!=crop
                or reread['initialReading']!=first or reread['literalSourceReread']!=final
                or reread['actual600SourceField']!=image or reread['originalFullRowCropSha256']!=crop
                or peer['firstRootImageReading']!=value or peer['literalSourceValue']!=value
                or peer['rootSourceOnlyPacketIndex']!=i+1 or peer['firstAuthorImageReading']!=first
                or peer['finalAuthorSourceValue']!=final or value!=final
                or peer['matchesFrozenFinalAuthorValue']is not True or peer['actual600SourceImage']!=image
                or pixel['actual600SourcePixelsReproducedExactly']is not True):
            raise ValueError('Ordered raw source reading or tuple-joined author facts differ')
        if identity in changes:
            change=changes[identity]
            if any(change[k]!=reread[k]for k in ['initialReading','literalSourceReread','actual600SourceField','actual1200SourceField','originalFullRowCropSha256']):
                raise ValueError('Author correction differs from its independently frozen source reread')
            image_check(change['actual1200SourceField'])
        count+=first!=final
        facts.append((entry,value,image,crop))
    if count!=len(changes)or count!=review['authorOwnCorrectionCount']:
        raise ValueError('Ordered source-money first correction count differs')
    return facts,rawref,count


def replay(review, source, read, image_check, unique, key, root):
    rawref=review['independentImageFirstTranscript']
    raw=read(rawref);packet=read(review['sourceOnlyPacket'])
    proof=read(review['independentSourcePixelProof'])
    changes=read(review['peerOwnAdditiveSourceCorrections'])
    choices=read(review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze'])
    firstref=review['authorOriginalFrozenTranscript'];firstpath=root/firstref['path']
    # TSV sparse events and JSON row transcripts have different physical shapes.
    # Both retain exactly one nonempty literal per requested tuple.
    from finish_salary_phsa_ledger import sha
    if sha(firstpath.read_bytes())!=firstref['sha256']:
        raise ValueError('Actual author first transcript changed')
    first={}
    if firstpath.suffix=='.tsv':
        with firstpath.open() as handle:
            for row in csv.DictReader(handle,delimiter='\t'):
                for field,column in [('remuneration','remunerationLiteral'),('expenses','expensesLiteral')]:
                    if row[column]=='':continue
                    value=row[column]
                    if not value.replace(',','').isdigit():raise ValueError('Sparse author amount unparsed')
                    identity=(int(row['sequence']),field)
                    if identity in first:raise ValueError('Duplicate nonempty sparse source field')
                    first[identity]=int(value.replace(',',''))
        if (choices['ownImageFirstRaw']!=firstref or choices['sourceOnlyPacket']!=review['sourceOnlyPacket']
                or choices['peerValuesNotOpenedBeforeThisFreeze']is not True):
            raise ValueError('Sparse author first/choices order is not pinned')
    elif 'original624SourceFirstTranscript'in choices:
        author=read(firstref)
        if (author['fullBatchCandidateOpened']is not False
                or choices['original624SourceFirstTranscript']!=firstref
                or choices['originalChoicesFrozenBeforePeerRead']is not True
                or choices['peerRawValuesNotOpenedBeforeThisAggregate']is not True
                or author['sourceId']!=source[0]or author['sourceSha256']!=source[1]
                or ('batch'in author and author['batch']!=source[2])):
            raise ValueError('Sequence-indexed author source-first history differs')
        from finish_salary_phsa_ledger import AREA,pin
        image_path=AREA/'batches'/(source[0]+'-batch-'+source[2].rsplit('-',1)[1]+'-target-views.json')
        image_reference=pin(image_path)
        if image_reference['sha256']!=author['sourceOnlyTargetViewsSha256']:
            raise ValueError('Author original source-field map changed')
        image_packet=read(image_reference)
        if (image_packet['sourceId'],image_packet['sourceSha256'],image_packet['batch'])!=source:
            raise ValueError('Author original field map belongs to another source/batch')
        for seq,fields in author['readings'].items():
            for field,value in fields.items():
                identity=(int(seq),field)
                if identity in first:raise ValueError('Duplicate sequence-indexed author source field')
                first[identity]=value
        if (set(first)!={(r['sequence'],f)for r in image_packet['rows']for f in r['reviewTargetFields']}
                or len(first)!=author['personallyReadRequestedFields']):
            raise ValueError('Author original source transcript lacks complete field coverage')
    else:
        author=read(firstref)
        if (author['candidateOpenedBeforeFreeze']is not False or choices['originalFirstTranscript']!=firstref
                or (author['sourceId'],author['sourceSha256'],author['batch'])!=source):
            raise ValueError('Author source-first history is not pinned')
        for row in author['transcript']:
            for field,value in row['literalValues'].items():
                identity=(row['sequence'],field)
                if identity in first:raise ValueError('Duplicate author original source field')
                first[identity]=value
    rejected=read(review['authorRejectedSecondarySourceReading'])if review['authorRejectedSecondarySourceReading']else None
    author_change=read(review['authorOwnAdditiveSourceCorrections'])if review.get('authorOwnAdditiveSourceCorrections')else None
    if (raw['sourceOnlyPacket']!=review['sourceOnlyPacket'] or proof['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or raw['sourcePixelProof']!=review['independentSourcePixelProof']
            or changes['originalFrozenImageFirstTranscript']!=rawref
            or raw['unresolvedFields']or review['unresolvedFields']
            or review['allFinalSourceValuesMatchExactly']is not True):
        raise ValueError('Complete source-money peer history differs')
    blind=((raw.get('authorChoicesOpened')is False and raw.get('readFromActualOriginal1200DpiViewsBeforeAnyAuthorOrMachineChoices')is True)
           or(raw.get('frozenBeforeAuthorOrOcrChoices')is True and raw.get('fullBatchCandidateOpened')is False))
    if not blind:raise ValueError('Fresh source peer was not frozen before choices')
    for document in [raw,packet,proof,changes,choices]:
        if document.get('sourceId',source[0])!=source[0]or document['sourceSha256']!=source[1]or document['batch']!=source[2]:
            raise ValueError('Source-money evidence belongs to another original/batch')
    target,peers,original,pixels,authors=map(unique,[packet['rows'],review['rows'],raw['rows'],proof['rows'],choices['rows']])
    amendment=unique(changes['changes'])
    if any(set(x)!=set(target)for x in [peers,original,pixels,authors])or not set(amendment)<=set(target):
        raise ValueError('Source-money peer must cover exactly all source-only tuples')
    if rejected:
        if (rejected['originalFirstTranscript']!=firstref
                or rejected['ownIntermediateSourceReread']!=review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze']
                or rejected['freshPeerSourceFirstBeforeChoices']!=rawref or key(rejected)not in target):
            raise ValueError('Rejected secondary source reading lacks its exact history')
        if (rejected['sourceId'],rejected['sourceSha256'],rejected['batch'])!=source:
            raise ValueError('Rejected author reading belongs to another source/batch')
        image_check(rejected['sourceEvidence'])
    if author_change:
        if (rejected or author_change['original624ImageFirstRaw']!=firstref
                or author_change['originalScoped44AuthorChoices']!=review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze']
                or author_change['independentFresh44FirstSourcePeer']!=rawref
                or key(author_change)not in target or author_change['unresolved']is not False):
            raise ValueError('Author additive source correction does not retain exact source history')
        if (author_change['sourceId'],author_change['sourceSha256'],author_change['batch'])!=source:
            raise ValueError('Author additive correction belongs to another source/batch')
        image_check(author_change['actualCurrentOriginal1200View'])
    facts=[];nulls=[];author_count=peer_count=0
    for identity,entry in target.items():
        p,o,v,a=peers[identity],original[identity],pixels[identity],authors[identity]
        seq=entry['sequence'];field=identity[2]
        if any(row['sequence']!=seq for row in [p,o,v,a]):raise ValueError('Source sequence moved')
        image=entry.get('actual1200SourceField',entry.get('actual600OriginalField',entry.get('actual600SourceField')))
        crop=entry.get('originalFullRowCropSha256',entry.get('cropSha256',entry.get('originalFullRowCrop',{}).get('sha256')))
        expected_first=first[(seq,field)]
        intermediate=a.get('currentActual1200SourceReading',a.get('ownFrozenLiteral',a.get('finalAuthorSourceValue')))
        final=intermediate
        if rejected and identity==key(rejected):
            if (rejected['originalBlindFirstReading']!=expected_first
                    or rejected['intermediateOwnSecondSourceReading']!=intermediate):
                raise ValueError('Rejected author reading hides its first/intermediate value')
            final=rejected['finalCurrentOriginalSourceReading']
        if author_change and identity==key(author_change):
            if (author_change['sequence']!=seq or author_change['firstRootImageReading']!=expected_first
                    or author_change['cropSha256']!=crop or intermediate!=expected_first):
                raise ValueError('Author additive correction hides original source value/crop')
            final=author_change['finalLiteralSourceReading']
        if 'initialImageFirstValue'in a and a['initialImageFirstValue']!=expected_first:
            raise ValueError('Author source choice hides actual first literal')
        peer_first=o['literalSourceValue'];peer_final=peer_first
        if identity in amendment:
            change=amendment[identity]
            if change['firstPeerSourceValue']!=peer_first:raise ValueError('Peer amendment hides first literal')
            peer_final=change['finalSourceValue']
        if field not in ['remuneration','expenses']or any(
                not (value is None and field=='expenses')and(type(value)is not int or value<=0)
                for value in [expected_first,intermediate,final,peer_first,peer_final]):
            raise ValueError('Source-money first/final values have invalid literal types')
        actual=p.get('actual1200OriginalField',p.get('actual600OriginalField',p.get('actual600SourceField')))
        raw_image=o.get('actualSource1200OriginalView',o.get('actual600OriginalField'))
        pixel_image=v.get('originalReference',v.get('actual600OriginalField'))
        author_image=a.get('sourceEvidence',a.get('actual600OriginalField',a.get('actual600SourceField')))
        author_crop=a.get('originalFullRowCropSha256',a.get('cropSha256'))
        pixel_pass=(v.get('actual1200PixelsMatch')is True and v.get('actual300FullRowAndNativeFieldPixelsMatch')is True
                    or v.get('independentActual600PixelsExactlyMatchSupplied')is True)
        if (actual!=image or raw_image!=image or pixel_image!=image or author_image!=image or author_crop!=crop or not pixel_pass
                or p['originalFullRowCropSha256']!=crop or o['originalFullRowCropSha256']!=crop
                or p['firstPeerSourceValue']!=peer_first or p['finalPeerSourceValue']!=peer_final
                or p['initialAuthorSourceValue']!=expected_first or p['intermediateAuthorSourceValue']!=intermediate
                or p['finalAuthorSourceValue']!=final or peer_final!=final or o.get('realUncertainty')is not None
                or p['finalIndependentSourceValuesMatchExactly']is not True):
            raise ValueError('Money first/intermediate/final/source/pixel evidence differs')
        image_check(image)
        peer_count+=peer_first!=peer_final;author_count+=expected_first!=final
        if final is None:
            if (field!='expenses'or o.get('literalDash')is not True or p['literalDashNullConfirmed']is not True
                    or p['eligibleForPositiveMoneyConfirmation']is not False):
                raise ValueError('Only an explicit independently read expense dash is null')
            nulls.append((entry,None,image,crop))
        else:
            if type(final)is not int or final<=0 or p['eligibleForPositiveMoneyConfirmation']is not True or p['literalDashNullConfirmed']is not False:
                raise ValueError('Positive source-money confirmation has invalid type/value')
            facts.append((entry,final,image,crop))
    if (peer_count!=review['peerOwnFirstReadingCorrections']or author_count!=review['authorOwnFirstReadingCorrections']
            or len(facts)!=review['positiveMonetaryFieldsConfirmed']or len(nulls)!=review['literalDashNullFieldsConfirmedSeparately']
            or len(target)!=review['fieldsPersonallyReadBeforeAuthorChoices']
            or int(rejected is not None)!=review['authorRejectedSecondaryReadings']):
        raise ValueError('Source-money correction and scope counters differ')
    return facts,nulls,rawref,author_count,peer_count
