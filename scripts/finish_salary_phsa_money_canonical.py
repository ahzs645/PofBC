#!/usr/bin/env python3
"""Replay bounded canonical whole-page source-money peers without letter waivers."""

import re


def root_canonical_table(review,source,read,image_check,unique,key):
    rawref=review['rootFirstRaw'];raw=read(rawref);packet=read(raw['sourceOnlyPacket'])
    middle=read(review['rootActual600SecondaryAssessment']);restore=read(review['root264AdditiveRestoration'])
    author=read(review['authorAll42CanonicalFinal']);original=read(author['originalFrozen497FirstTranscript'])
    prior=read(author['prior42Partial1200SourceRereadHistory'])
    planref=author['ownCanonicalWholePage600AndNative300Plan']
    plan=read({'path':'research/salaries/queue-completion-2026-11-01/phsa/triangulation/archived-source-money-inputs/'+planref['sha256']+'.json','sha256':planref['sha256']})
    third=read(review['independentThird13Final']);third_inputs=[read(ref)for ref in third['inputs']];thirdraw=third_inputs[0]
    # This transitive packet is already pinned by the immutable third raw and
    # scoped choice receipt. Checking it adds no new reading or derived fact.
    import finish_salary_phsa_ledger as ledger
    thirdpacket=ledger.pinned(thirdraw['imageOnlyPacket']);thirdchoices=third_inputs[1]
    for document in [review,raw,packet,middle,restore,author,original,prior,third,thirdpacket]+third_inputs:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Root canonical table first/secondary/current source differs')
    if (review['accepted']is not True or raw['frozen']is not True or raw['candidateOrAuthorValuesOpened']is not False
            or original['candidateOpened']is not False or original['correspondingChoicesOpened']is not False
            or packet['noCorrespondingAuthorChoicesIncluded']is not True or middle['rootFirst42Raw']!=rawref
            or author['sourceOnlyPacket']!=raw['sourceOnlyPacket']or prior['sourceOnlyPacket']!=raw['sourceOnlyPacket']
            or prior['originalFrozenFirstTranscript']!=author['originalFrozen497FirstTranscript']
            or restore['originalFirst42Raw']!=rawref or restore['intermediate42Actual600Assessment']!=review['rootActual600SecondaryAssessment']
            or restore['independentThird13ColdRaw']!=third['inputs'][0]
            or thirdraw['frozen']is not True or third['frozen']is not True
            or thirdpacket['frozen']is not True or thirdchoices['frozen']is not True
            or thirdpacket['correspondingAuthorAndRootValuesMustStayClosedUntilRawFreeze']is not True
            or thirdchoices['sourceOnlyPacket']!=thirdraw['imageOnlyPacket']
            or thirdchoices['thirdColdRawBeforeTheseChoices']!=third['inputs'][0]
            or review['numericQualificationAllowed']is not False or review['unresolvedMoneyFields']!=0
            or author['numericQualificationAllowed']is not False or author['oldAll497And42RawBytesUnchanged']is not True
            or (plan['sourceId'],plan['sourceSha256'])!=source[:2]):
        raise ValueError('Root canonical table chronology/source-only authority differs')
    targets,first,secondary,peers,current,previous,planned=map(unique,[packet['rows'],raw['rows'],middle['rows'],review['rows'],author['rows'],prior['rows'],plan['rows']])
    thirds,thirdfirst,thirdtargets,thirdscoped=map(unique,[third['rows'],thirdraw['rows'],thirdpacket['rows'],thirdchoices['rows']]);originals={(r['physicalPage'],r['sourceRowOnPage']):r for r in original['rows']}
    changes=unique(author['ownFirstToFinalMoneyCorrections'])
    if (any(set(v)!=set(targets)for v in [first,secondary,peers,current,previous,planned])
            or any(set(v)!=set(thirdtargets)for v in [thirds,thirdfirst,thirdscoped])or not set(thirds)<=set(targets)
            or len(originals)!=len(original['rows'])or not set(changes)<=set(targets)or key(restore)not in thirds):
        raise ValueError('Root canonical table target/first/secondary/current scope differs')
    third_corrections={(r['sequence'],r['field']):r for r in thirdraw['sourceOnlyOwnCorrections']}
    if (len(third_corrections)!=len(thirdraw['sourceOnlyOwnCorrections'])
            or set(third_corrections)!={(r['sequence'],r['field'])for r in thirdfirst.values()if r['firstActual600VisualValue']!=r['literalValue']}):
        raise ValueError('Fresh third prechoice source-reading corrections are incomplete')
    facts=[];author_count=peer_count=0;secondary_count=restored_count=0
    rejected={(r['sequence'],r['field']):r for r in author['rejectedOwnPartial1200SecondaryReadings']}
    if len(rejected)!=len(author['rejectedOwnPartial1200SecondaryReadings']):raise ValueError('Duplicate canonical rejected secondary history')
    rejected_seen=set()
    for identity,entry in targets.items():
        o,m,p,a,b,planrow=first[identity],secondary[identity],peers[identity],current[identity],previous[identity],planned[identity]
        field=identity[2];original_row=originals[identity[:2]];before=original_row['imageFirstValues'][field]
        peer_first=o['rootFirstImageReading'];intermediate=m['rootCurrent600SourceReading']
        peer_final=restore['rootFinalRestoredSourceReading']if identity==key(restore)else intermediate
        value=a['currentCanonicalSourceValue'];crop=entry['cropSha256'];image=a['sourceEvidence'];native=entry['native300SourceField']
        if (field not in ['remuneration','expenses']or any(type(v)is not int or v<=0 for v in [before,peer_first,intermediate,peer_final,value,b['currentOriginal1200SourceValue']])
                or any(r['sequence']!=entry['sequence']for r in [o,m,p,a,b,planrow])
                or any(r['cropSha256']!=crop for r in [o,m,p,b,planrow])or a['originalFullRowCropSha256']!=crop
                or original_row['cropSha256']!=crop or field not in original_row['reviewTargetFields']
                or o['actual1200SourceField']!=entry['actual1200SourceField']or o['native300SourceField']!=native
                or b['initialImageFirstValue']!=before or b['firstReadingChanged']!=(before!=b['currentOriginal1200SourceValue'])
                or a['initialImageFirstValue']!=before or a['priorPartial1200SecondaryReading']!=b['currentOriginal1200SourceValue']
                or a['finalAuthorSourceValue']!=value or a['firstReadingChanged']!=(before!=value)
                or a['secondaryReadingChanged']!=(b['currentOriginal1200SourceValue']!=value)
                or a['native300SourceField']!=native or image!=planrow['whole600Source']or planrow['native300SourceField']!=native
                or m['rootFirst1200ImageReading']!=peer_first or m['actual600RgbExactlyReproducedFromOriginal']is not True
                or p['rootFirstImageValue']!=peer_first or p['rootFinalSourceValue']!=peer_final
                or p['authorCanonicalFinalSourceValue']!=value or value!=peer_final or p['exactCurrentAgreement']is not True
                or p['rootOwnFirstReadingChanged']!=(peer_first!=peer_final)
                or p['rootIntermediateWrongValueRestored']!=(identity==key(restore))):
            raise ValueError('Root canonical table first/secondary/final/source facts differ')
        if identity==key(restore):
            if (restore['rootFirst1200SourceReading']!=peer_first or restore['rootWrongSecondary600Reading']!=intermediate
                    or restore['cropSha256']!=crop or restore['source1200RgbExact']is not True):
                raise ValueError('Root canonical secondary restoration hides original first/source')
            image_check(restore['actualOriginal1200SourceField'])
        if identity in thirds:
            t,f,tt,tc=thirds[identity],thirdfirst[identity],thirdtargets[identity],thirdscoped[identity]
            if (t['literalValue']!=peer_final or f['literalValue']!=peer_final or t['firstActual600VisualValue']!=f['firstActual600VisualValue']
                    or any(r['sequence']!=entry['sequence']for r in [t,f,tt,tc])or tt['cropSha256']!=crop or tc['cropSha256']!=crop
                    or t['cropSha256']!=crop or f['cropSha256']!=crop or t['uncertainty']is not None
                    or t['rootFirst1200ImageReading']!=peer_first or t['rootIntermediate600SourceReading']!=intermediate
                    or t['rootFinalSourceValue']!=peer_final or t['sourceAgreementWithRootFinal']is not True
                    or t['actualOriginal600']!=m['actualOriginal600']or f['actualOriginal600']!=m['actualOriginal600']
                    or tt['actualOriginal600']!=m['actualOriginal600']or tc['source600']!=m['actualOriginal600']
                    or t['native300SourceField']!=native or f['native300SourceField']!=native or tt['native300SourceField']!=native
                    or tt['actual600RgbExactlyReproducedFromOriginal']is not True
                    or f['independentActual600RgbReproduction']is not True or f['independentNative300AndFullRowPixelReproduction']is not True
                    or t['independentActual600RgbReproduction']is not True or t['independentNative300AndFullRowPixelReproduction']is not True):
                raise ValueError('Root canonical fresh-third source/first/final facts differ')
            if (entry['sequence'],field)in third_corrections:
                c=third_corrections[(entry['sequence'],field)]
                if c['firstVisualValue']!=f['firstActual600VisualValue']or c['correctedLiteralValue']!=f['literalValue']:
                    raise ValueError('Fresh third source-only correction hides its first value')
        if before!=value:
            if identity not in changes:raise ValueError('Canonical author first error is not explicitly amended')
            c=changes[identity]
            if c['first']!=before or c['final']!=value or c['intermediate']!=b['currentOriginal1200SourceValue']or c['actualCanonicalWhole600']!=image:
                raise ValueError('Canonical author first-value correction hides history')
        if b['currentOriginal1200SourceValue']!=value:
            pair=(entry['sequence'],field);c=rejected.get(pair)
            if not c or c['first']!=before or c['rejectedSecondary']!=b['currentOriginal1200SourceValue']or c['final']!=value or c['restoresOriginalFirstValue']!=(before==value):
                raise ValueError('Canonical rejected secondary source reading is not preserved')
            rejected_seen.add(pair);secondary_count+=1;restored_count+=before==value
        for ref in [image,native,m['actualOriginal600']]:image_check(ref)
        facts.append((entry,value,image,crop));author_count+=before!=value;peer_count+=peer_first!=peer_final
    if (len(facts)!=review['scope']['positiveMoneyFields']or peer_count!=review['rootOwnFirstErrors']
            or len(changes)!=author_count or set(rejected)!=rejected_seen
            or third['counts']['fields']!=len(thirdtargets)or third['counts']['rootFinalMatch']!=len(thirdtargets)
            or third['counts']['thirdSourceOnlyOwnPrechoiceCorrection']!=len(third_corrections)
            or third['counts']['thirdPostchoiceAmountCorrections']!=0 or third['counts']['unresolvedSourceAmounts']!=0
            or author['counts']!={'sourceFieldsPersonallyReadCanonically':len(facts),'positiveIntegerFields':len(facts),
                                 'trueOwnOriginalFirstMoneyErrors':author_count,'ownIncorrectSecondaryReadings':secondary_count,
                                 'originalFirstValuesRestoredAfterWrongSecondary':restored_count,'unresolved':0}):
        raise ValueError('Root canonical complete table or correction counts differ')
    return facts,rawref,author_count,peer_count


def wholepage_literal_peer(review,source,read,image_check,unique,key):
    rawref=review['independentImageFirstTranscript'];raw=read(rawref);packet=read(review['sourceOnlyPacket'])
    proof=read(review['independentSourcePixelProof']);resolution=read(review['peerPrechoiceUncertaintyResolution'])
    choices=read(review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze']);author=read(review['authorOriginalFrozenTranscript'])
    correction=read(review['authorPostPeerAdditiveCorrection'])
    for document in [review,raw,packet,choices,author,correction]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Whole-page literal source/author identity differs')
    for document in [proof,resolution]:
        if (document['sourceId'],document['sourceSha256'])!=source[:2]:raise ValueError('Whole-page proof/resolution source differs')
    # The actual frozen first transcript records its chronology in its method,
    # with no later invented boolean. Permit that historic shape only at this pin.
    if (rawref['sha256']!='007af5b9d98cd06cefef7e882b1358889686ddce3e17b0e8f6dfbadd86048ff4'
            or raw['frozen']is not True or 'No corresponding author first/current/engine values opened.'not in raw['method']
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']or packet['sourceValuesOrCandidateAlternativesIncluded']is not False
            or choices['freshPeerChoicesOpened']is not False or author['candidateOpenedBeforeFreeze']is not False
            or choices['rawImageFirstTranscript']!=review['authorOriginalFrozenTranscript']
            or choices['sourceOnlyFreshMoneyPacket']!=review['sourceOnlyPacket']
            or proof['sourceOnlyPacket']!=review['sourceOnlyPacket']or resolution['originalSourceFirstRaw']!=rawref
            or resolution['firstFrozenBytesUnchanged']is not True or resolution['numericQualification']is not False
            or correction['ownPrevious36SourceRereads']!=review['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze']
            or correction['fresh36PeerRawFrozenBeforeOwnChoicesReleased']!=rawref
            or review['peerOwnAdditiveSourceCorrections']is not None or review['unresolvedFields']
            or review['allFinalSourceValuesMatchExactly']is not True):
        raise ValueError('Whole-page literal source-first chronology differs')
    targets,first,peers,authors,pixels,resolved=map(unique,[packet['rows'],raw['rows'],review['rows'],choices['rows'],proof['rows'],resolution['rows']])
    originals={(r['physicalPage'],r['sourceRowOnPage']):r for r in author['rows']}
    if (any(set(x)!=set(targets)for x in [first,peers,authors,pixels])or not set(resolved)<=set(targets)
            or len(originals)!=len(author['rows'])or key(correction)not in targets
            or set(resolved)!={k for k,o in first.items()if o['sourceUncertainty']is not None}):
        raise ValueError('Whole-page literal raw/proof/choice/resolution scope differs')
    facts=[];author_count=0
    for identity,entry in targets.items():
        o,p,a,v=first[identity],peers[identity],authors[identity],pixels[identity];original=originals[identity[:2]]
        field=identity[2];before=original['imageFirstValues'][field];intermediate=a['currentSourceLiteral']
        value=correction['correctedLiteralSourceValue']if identity==key(correction)else intermediate
        image=entry['actualWholePage600SourceView'];native=entry['nativeOriginal300SourceView'];context=entry['native300Context'];crop=entry['cropSha256']
        if (field not in ['remuneration','expenses']or any(type(x)is not int or x<=0 for x in [before,intermediate,value,o['literalImageValue']])
                or any(r['sequence']!=entry['sequence']for r in [o,p,a,v])
                or field not in original['reviewTargetFields']or original['sourceCropSha256']!=crop
                or a['firstFrozenLiteral']!=before or a['ownSourceCorrection']!=(before!=intermediate)
                or a['sourceEvidence']!=entry or o['cropSha256']!=crop or v['cropSha256']!=crop
                or o['wholePage600SourceView']!=image or o['native300SourceView']!=native or o['native300Context']!=context
                or p['actual600OriginalField']!=image or p['native300OriginalField']!=native or p['native300Context']!=context
                or v['checks']!={'native300':True,'whole600':True,'context300':True}
                or p['firstPeerSourceValue']!=o['literalImageValue']or p['finalPeerSourceValue']!=o['literalImageValue']
                or p['initialAuthorSourceValue']!=before or p['intermediateAuthorSourceValue']!=intermediate
                or p['finalAuthorSourceValue']!=value or value!=o['literalImageValue']
                or p['originalFullRowCropSha256']!=crop or p['finalIndependentSourceValuesMatchExactly']is not True
                or p['eligibleForPositiveMoneyConfirmation']is not True or p['literalDashNullConfirmed']is not False):
            raise ValueError('Whole-page literal source/first/current/pixel facts differ')
        if identity in resolved:
            c=resolved[identity]
            if c['firstFrozenLiteral']!=value or c['currentSourceLiteral']!=value or c['wholePage600SourceView']!=image or c['native300Context']!=context:
                raise ValueError('Whole-page prechoice uncertainty resolution changes a first literal')
        if identity==key(correction):
            if (correction['ownFirstFrozenAndSecondSourceRereadValue']!=before or intermediate!=before
                    or correction['cropSha256']!=crop or correction['actualCurrentOriginalSourceEvidence']!=entry):
                raise ValueError('Whole-page author correction hides first/intermediate source evidence')
        for ref in [image,native,context]:image_check(ref)
        facts.append((entry,value,image,crop));author_count+=before!=value
    if (len(facts)!=review['fieldsPersonallyReadBeforeAuthorChoices']or len(facts)!=review['positiveMonetaryFieldsConfirmed']
            or author_count!=review['authorOwnFirstReadingCorrections']or review['peerOwnFirstReadingCorrections']!=0
            or review['literalDashNullFieldsConfirmedSeparately']!=0 or proof['counts']['fields']!=len(facts)):
        raise ValueError('Whole-page literal complete scope/correction counters differ')
    return facts,rawref,author_count,0


def root_positive_canonical(review,overlay,source,read,image_check,unique,key):
    """Retain the original53 history; independently replace only its exposed394 error."""
    from finish_salary_phsa_money_standard import root_positive_table
    previous_ref=review['supersedesCurrentAuthorityOfOnly394InPriorReceipt'];previous=read(previous_ref)
    facts,rawref,author_count,peer_count=root_positive_table(previous,overlay,source,read,image_check,unique,key)
    canonical=read(review['authorAll53CanonicalWhole600Reread']);change=read(review['authorOne394Correction'])
    freshref=review['freshColdIndependent394'];fresh=read(freshref);packet=read(fresh['sourceOnlyPacket'])
    # This later complete pixel proof is itself immutable, and explicitly names
    # this cold field and the source-only packet. It does not refreeze a reading.
    finalref={'path':'research/salaries/queue-completion-2026-11-01/reviews/author-phsa-history-schools-2019-20-012-money394-final-source-comparison.json',
              'sha256':'47f64934dfc7fcdc780c29b48dea03ef83d7d4b9689b55c09bb3fc93f610384c'}
    final=read(finalref);proof=read(final['sourcePixelProof'])
    for document in [review,canonical,change,fresh,packet,final,proof]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Canonical394 source/first/proof identity differs')
    if (review['accepted']is not True or review['preservesAllOriginalRawAndOther52Values']is not True
            or fresh['frozen']is not True or final['frozen']is not True or proof['frozen']is not True
            or review['originalRootFirstRaw']!=rawref or canonical['priorRootFinal53']!=previous_ref
            or canonical['priorAuthor53']!=previous['scopedAuthor53OnlyChoices']
            or canonical['fieldCount']!=53 or canonical['unchangedCount']!=52 or canonical['changedCount']!=1
            or fresh['correspondingAuthorOrPeerAmountsOpened']is not False or fresh['fullBatchCandidateOpened']is not False
            or final['originalSourceFirst']!=freshref or final['scopedAuthorOwnCorrection']!=review['authorOne394Correction']
            or final['root53AdditiveCurrentClosure']!= {'path':'research/salaries/queue-completion-2026-11-01/reviews/root-phsa-history-2019-20-batch-012-fiftythree-money-final-source-comparison-v2.json','sha256':'3b66fbc847ceb77368066ebcb5e5de66a1874fe13623108750af9cdedda42ef9'}
            or review['currentExactValuesAgree']!=53 or review['unresolvedMoneyFields']!=0 or review['numericQualificationAllowed']is not False):
        raise ValueError('Canonical394 additive correction hides its original order or scope')
    targets=unique([f[0]for f in facts]);peers=unique(review['rows']);old=unique(previous['rows']);current=unique(canonical['fields'])
    cold=unique(fresh['rows']);finalrows=unique(final['rows']);source_rows=unique(packet['rows'])
    changed_key=key(change)
    if (set(targets)!=set(peers)or set(targets)!=set(current)or set(cold)!={changed_key}
            or set(finalrows)!={changed_key}or set(source_rows)!={changed_key}or changed_key!=(88,13,'remuneration')):
        raise ValueError('Canonical394 complete53/single-correction scope differs')
    output=[]
    for entry,old_value,old_image,crop in facts:
        identity=key(entry);p,c=peers[identity],current[identity]
        if (p['sequence']!=entry['sequence']or c['sequence']!=entry['sequence']or p['cropSha256']!=crop or c['cropSha256']!=crop
                or p['rootFirstImageReading']!=old[identity]['rootFirstImageReading']
                or p['authorFirstSourceReading']!=old[identity]['authorFirstSourceReading']
                or c['oldScopedSourceValue']!=old_value or c['whole600PixelsExact']is not True
                or p['positiveLiteralValuesAgree']is not True):
            raise ValueError('Canonical53 first/source/whole-page facts differ')
        value=c['currentPersonalWhole600Value']
        literal=p['authorCurrentSourceReading']
        if (type(value)is not int or value<=0 or type(p['rootCurrentSourceReading'])is not int
                or p['rootCurrentSourceReading']!=value or not isinstance(literal,str)
                or re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',literal)is None
                or int(literal.replace(',',''))!=value):
            raise ValueError('Canonical53 final literal positive value differs')
        image={'path':c['whole600CellPath'],'sha256':c['whole600CellSha256']};image_check(image);image_check(c['sourceNativeField'])
        if identity!=changed_key:
            if p!=old[identity]or value!=old_value or c['changed']is not False:
                raise ValueError('Canonical394 revision changed an unrelated one of52 values/history')
        else:
            o=next(iter(cold.values()));s=source_rows[identity];v=finalrows[identity]
            if (change['oldAuthorAndRootValue']!=old_value or change['currentPersonalSourceValue']!=value
                    or o['literalImageValue']!=value or not re.fullmatch(r'[0-9]{1,3}(?:,[0-9]{3})*',o['literalImageText'])
                    or int(o['literalImageText'].replace(',',''))!=value or o['uncertainty']is not None
                    or o['cropSha256']!=crop or s['cropSha256']!=crop or v['cropSha256']!=crop
                    or p['priorRootAndAuthorCurrentSourceReading']!=old_value or c['changed']is not True
                    or p['freshIndependentWholePageSourceFirstValue']!=value
                    or p['rootOwnFirstReadingErrorCorrectedAfterCanonicalSourceExpectedExposure']is not True
                    or v['peerFirstSourceValue']!=value or v['peerCurrentSourceValue']!=value
                    or v['authorFirstSourceValue']!=old_value or v['authorCurrentSourceValue']!=value):
                raise ValueError('Canonical394 fresh cold reading/source/old error facts differ')
            for field in ['nativeOriginal300Field','whole600Field','whole1200Focus']:
                if o[field]!=s[field]or v[field]!=s[field]:raise ValueError('Canonical394 source view identity differs')
                image_check(s[field])
            checked=[r for r in proof['rows']if key(r)==identity]
            if len(checked)!=3 or {r['dpi']for r in checked}!={300,600,1200}or any(r['rgbPixelsExactlyReproducedFromWholeOriginalPage']is not True for r in checked):
                raise ValueError('Canonical394 original whole-page pixel proof incomplete')
            if {r['sourceView']['sha256']for r in checked}!={o[k]['sha256']for k in ['nativeOriginal300Field','whole600Field','whole1200Focus']}:
                raise ValueError('Canonical394 proof covers a different original source image')
            author_count+=1;peer_count+=1
        output.append((entry,value,image,crop))
    return output,freshref,author_count,peer_count


def mixed_wholepage_peer(review,source,read,image_check,unique,key):
    rawref=review['independentImageFirstTranscript'];raw=read(rawref)
    packet=read(review['sourceOnlyPacket']);choices=read(review['authorScopedChoicesOpenedOnlyAfterPeerFreeze'])
    author=read(choices['originalRaw']);changes=read(review['peerOwnPostcomparisonCorrections'])
    for document in [review,raw,packet,choices,author,changes]:
        if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
            raise ValueError('Canonical mixed source/first/choice identity differs')
    if (raw['frozen']is not True or raw['correspondingAuthorChoicesOpened']is not False
            or raw['fullCandidateOpened']is not False or packet['sourceOnly']is not True
            or packet['expectedValuesWithheld']is not True or choices['freshPeerChoicesOpened']is not False
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']or choices['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or changes['originalSourceFirst']!=rawref or author['fullCandidateOpened']is not False
            or author['frozenBeforeOpeningFullCandidate']is not True):
        raise ValueError('Canonical mixed source-first chronology differs')
    targets,first,peers,authors,amended=map(unique,[packet['rows'],raw['rows'],review['rows'],choices['rows'],changes['rows']])
    pixels={(r['sequence'],r['field']):r for r in raw['pixelProofRows']}
    originals={r['sequence']:r for r in author['rows']}
    if (any(set(r)!=set(targets)for r in [first,peers,authors])or not set(amended)<=set(targets)
            or len(pixels)!=len(raw['pixelProofRows'])or set(pixels)!={(r['sequence'],r['field'])for r in targets.values()}
            or len(originals)!=len(author['rows'])):
        raise ValueError('Canonical mixed source/first/proof field scope differs')
    facts=[];names=money=0
    for identity,entry in targets.items():
        o,p,a=first[identity],peers[identity],authors[identity];seq=entry['sequence'];field=identity[2]
        original=originals[seq];before=original['literalSourceValuesFirstPass'][field]
        final=amended[identity]['correctedCurrentSourceLiteral']if identity in amended else o['literalPreferred']
        if (any(r['sequence']!=seq for r in [o,p,a])or any(r['cropSha256']!=entry['cropSha256']for r in [o,p,a])
                or (original['physicalPage'],original['sourceRowOnPage'])!=identity[:2]
                or original['cropSha256']!=entry['cropSha256']or field not in original['reviewTargetFields']
                or (entry['sourceId'],entry['sourceSha256'])!=source[:2]
                or a['firstAuthorSourceReading']!=before or p['authorFirstSourceValue']!=before
                or p['authorCurrentSourceValue']!=a['currentAuthorSourceReading']
                or p['firstPeerWhole600VisualValue']!=o['firstWhole600VisualValue']
                or p['peerPrechoiceContextLiteral']!=o['literalPreferred']or p['peerCurrentPreferredLiteral']!=final
                or p['literalSourceValue']!=final or p['ownPostchoiceLiteralCorrection']!=(identity in amended)
                or p['actualSourceOriginalWhole600AndNative300PixelExact']is not True
                or pixels[(seq,field)]['physicalPage']!=identity[0]
                or pixels[(seq,field)]['allOriginal600FieldAnd300NativeContextRgbExact']is not True):
            raise ValueError('Canonical mixed raw/first/current/source facts differ')
        if identity in amended:
            change=amended[identity]
            if (field!='name'or change['firstWhole600VisualValue']!=o['firstWhole600VisualValue']
                    or change['prechoiceContextValue']!=o['literalPreferred']or change['cropSha256']!=entry['cropSha256']):
                raise ValueError('Canonical mixed amendment hides its original source reading')
        for peer_key,target_key in [('sourceWhole600','actualWholePage600Field'),('sourceNative300','actualNative300Field'),('sourceContext300','actualNative300Context')]:
            ref=entry[target_key]
            if o[peer_key]!=ref or p[peer_key]!=ref or a[target_key]!=ref:
                raise ValueError('Canonical mixed source image/crop map differs')
            image_check(ref)
        if field=='name':names+=1
        elif field in ['remuneration','expenses']:
            money+=1
            if (any(type(v)is not int or v<=0 for v in [before,final,o['firstWhole600VisualValue'],a['currentAuthorSourceReading']])
                    or any(v!=final for v in [before,o['firstWhole600VisualValue'],a['currentAuthorSourceReading']])
                    or o['uncertain']is not False or p['numericalUncertainty']is not None
                    or p['sourceTypographyQualificationProposed']is not False or p['peerAndAuthorCurrentPreferredMatch']is not True):
                raise ValueError('Canonical mixed positive money lacks unchanged independent first readings')
        else:raise ValueError('Unknown canonical mixed source field')
        facts.append((entry,final,entry['actualWholePage600Field'],entry['cropSha256']))
    if (review['counts']['fields']!=len(targets)or review['counts']['names']!=names or review['counts']['money']!=money
            or review['counts']['literalMoneyUnresolved']!=0 or raw['counts']['positiveMoneyFields']!=money
            or review['counts']['peerPostchoiceLiteralCorrections']!=len(amended)
            or review['counts']['allSixMoneyFirstValuesMatchAuthorCurrentExactly']is not True):
        raise ValueError('Canonical mixed scope/correction counters differ')
    return facts,rawref,0,0
