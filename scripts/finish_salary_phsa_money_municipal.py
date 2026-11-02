#!/usr/bin/env python3
"""Replay the disjoint four/47 fresh-money readers for historical PHSA batch004."""


def pairs(rows):
    result={(r['sequence'],r['field']):r for r in rows}
    if len(result)!=len(rows):raise ValueError('Duplicate sequence/source field')
    return result


def replay(review,source,read,image_check,unique,key):
    four='authorFinalSourceCorrections'in review
    if four:
        rawref=review['independentImageFirstRaw'];raw=read(rawref)
        correction=read(review['authorFinalSourceCorrections'])
        authorref=review['authorOriginalImageFirstRaw'];author=read(authorref)
        secondaryref=review['authorOwnSecondarySourceRereads'];secondary=read(secondaryref)
        packetref=raw['sourceOnlyPacket'];packet=read(packetref)
        if (raw['frozenBeforeAuthorProposalsOrCandidateMoneyValues']is not True
                or raw['candidateOrAuthorValuesOpened']is not False
                or raw['unresolvedFields']or review['unresolvedFields']
                or review['independentReviewerOwnCorrections']!=0):
            raise ValueError('Four-field peer was not complete and blind')
        proof=None;late=None;choices=None
    else:
        rawref=review['imageFirstTranscript'];raw=read(rawref)
        packetref=review['sourceOnlyPacket'];packet=read(packetref)
        proof=read(review['pixelVerification']);choices=read(review['authorScopedProposals'])
        correction=read(choices['sourceOfOwnEffectiveValues'])
        authorref=correction['original628FieldBlindTranscript'];author=read(authorref)
        secondaryref=correction['ownSecond51FieldMoneyReread'];secondary=read(secondaryref)
        late=read(review['authorOnlyPostPeerSourceCorrection'])
        if (raw['authorChoicesUnopenedAtFreeze']is not True or raw['candidateUnopenedAtFreeze']is not True
                or raw['sourceOnlyPacket']!=packetref or raw['pixelVerification']!=review['pixelVerification']
                or choices['releasedOnlyAfterFresh47Raw']!=rawref
                or late['freshIndependent47RawBeforeChoices']!=rawref
                or late['ownEarlierFrozen51FinalReads']!=choices['sourceOfOwnEffectiveValues']
                or raw['unresolvedFields']or review['unresolvedFields']or review['peerCorrections']
                or late['ownDataReadingCorrection']is not True):
            raise ValueError('47-field source-first history differs')
        image_check(late['sourceEvidence'])
    for document in [raw,packet,author,secondary,correction]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Municipal source-money proof belongs to another original/batch')
    if (author['candidateOpenedBeforeFreeze']is not False
            or correction['original628FieldBlindTranscript']!=authorref
            or correction['ownSecond51FieldMoneyReread']!=secondaryref
            or secondary['rawSourceFirstTranscript']!=authorref
            or correction['unresolvedMonetaryFields']):
        raise ValueError('Actual complete author first/secondary/correction history differs')
    originals={r['sequence']:r for r in author['rows']}
    if len(originals)!=len(author['rows']):raise ValueError('Duplicate original author row')
    secondary_rows=pairs(secondary['rows']);finals=pairs(correction['all51FinalMoneyReadings'])
    data_changes=pairs(correction['ownMonetaryDataCorrections'])
    secondary_changes=pairs(correction['ownSecondaryProvisionalReadingCorrection'])
    if set(secondary_rows)!=set(finals)or not set(data_changes)<=set(finals)or not set(secondary_changes)<=set(finals):
        raise ValueError('Complete51 author source reread history incomplete')
    for identity,entry in finals.items():
        seq,field=identity;first=originals[seq]['imageFirstValues'][field]
        expected=data_changes[identity]['finalOriginalSourceValue']if identity in data_changes else first
        if entry['finalOriginalSourceValue']!=expected:raise ValueError('Unrecorded author source-value drift')
        if identity in data_changes and data_changes[identity]['initialBlindValue']!=first:
            raise ValueError('Author source correction hides actual first value')
        second=secondary_rows[identity]['secondSourceReading']
        if identity in secondary_changes:
            c=secondary_changes[identity]
            if (c['firstBlindOriginalValue']!=first or c['intermediateOwnSecondReadProvisionalValue']!=second
                    or c['finalOriginalSourceValue']!=expected):
                raise ValueError('Rejected secondary author reading history changed')
        elif second!=expected:raise ValueError('Source reread lacks its explicit correction')
    if late:
        identity=(late['sequence'],late['field'])
        if identity not in finals or finals[identity]['finalOriginalSourceValue']!=late['originalBlindAndPriorOwnRereadValue']:
            raise ValueError('Additional source correction does not preserve its prior value')
    targets,peers,blind=map(unique,[packet['rows'],review['rows'],raw['rows']])
    if set(targets)!=set(peers)or set(targets)!=set(blind):raise ValueError('Money peer must cover exact source-only tuple set')
    if four:
        if len(targets)!=review['reviewedMoneyFields']or len(targets)!=4:raise ValueError('Four-source scope differs')
    else:
        pixels=unique(proof['checks']);proposals=pairs(choices['rows'])
        if set(pixels)!=set(targets)or set(proposals)!={(r['sequence'],r['field'])for r in packet['rows']}:
            raise ValueError('47-source proof/choice target set differs')
        if proof['sourceOnlyPacket']!=packetref:raise ValueError('Pixel proof pins a different source target')
    facts=[];author_changes=0
    for identity,entry in targets.items():
        seq,field=entry['sequence'],identity[2];pair=(seq,field);peer,original=peers[identity],blind[identity]
        own=originals[seq];first=own['imageFirstValues'][field];second=secondary_rows[pair]
        final=late['finalCurrentOriginalSourceValue']if late and identity==key(late)else finals[pair]['finalOriginalSourceValue']
        image=entry['actual1200SourceField'];crop=entry['originalFullRowCrop']['sha256']
        if ((own['physicalPage'],own['sourceRowOnPage'])!=identity[:2]or field not in own['reviewTargetFields']
                or own['sourceCropSha256']!=crop or second['sourceProof']['actual1200NameOrMoney']!=image
                or second['sourceProof']['originalRowCropSha256']!=crop
                or original['actual1200SourceField']!=image or peer['actual1200SourceField']!=image):
            raise ValueError('Fresh money original source/crop/row mapping differs')
        if four:
            value=original['literalSourceValue']
            if (original['genuineUnresolvedGlyphs']or original['actual1200OriginalSourcePixelsIndependentlyReproducedExactly']is not True
                    or peer['actual1200SourcePixelsIndependentlyReproducedExactly']is not True
                    or peer['originalAuthorFirstReading']!=first or peer['freshIndependentFirstSourceReading']!=value
                    or peer['finalLiteralSourceValue']!=final or peer['originalFullRowCrop']!=entry['originalFullRowCrop']
                    or original['originalFullRowCrop']!=entry['originalFullRowCrop']):
                raise ValueError('Four-source first/final/pixel proof differs')
        else:
            value=original['value'];pixel=pixels[identity];proposal=proposals[pair]
            if (original['uncertainty']is not None or peer['uncertainty']is not None
                    or peer['value']!=value or peer['authorEffectiveSourceValue']!=final or peer['exactMatch']is not True
                    or proposal['finalOriginalSourceValue']!=finals[pair]['finalOriginalSourceValue']
                    or pixel['allThreeOriginalImageMappingsPixelExact']is not True or pixel['ownActual1200Sha256']!=image['sha256']
                    or original['cropSha256']!=crop or peer['cropSha256']!=crop):
                raise ValueError('47-source first/final/pixel proof differs')
        if any(type(v)is not int or v<=0 for v in [first,second['secondSourceReading'],final,value])or value!=final:
            raise ValueError('Fresh literal money is unresolved/invalid')
        image_check(image);facts.append((entry,value,image,crop));author_changes+=first!=final
    if four:
        if (review['originalAuthorFirstReadingsSourceCorrected']!=author_changes
                or review['originalAuthorFirstReadingsMatchingFinal']!=len(facts)-author_changes):
            raise ValueError('Four-field author correction history count differs')
    elif review['fieldCount']!=len(facts)or review['exactFinalMatches']!=len(facts)or review['authorCorrectionCount']!=author_changes:
        raise ValueError('47-field source/correction counts differ')
    return facts,rawref,author_changes
