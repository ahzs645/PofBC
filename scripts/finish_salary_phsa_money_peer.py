#!/usr/bin/env python3
"""Replay count-independent, field-limited fresh human money confirmations.

The two supported receipt schemas retain the original independent transcripts,
source-only target set and subsequent transparent reader amendments. This module
does not infer a value from agreement or a control total.
"""
import json
import csv
import re
from pathlib import Path

import finish_salary_phsa_ledger as ledger


def key(row):
    pn, rn, field = row['physicalPage'], row['sourceRowOnPage'], row['field']
    if type(pn) is not int or type(rn) is not int or min(pn, rn) < 1:
        raise ValueError('Invalid original source money locator')
    return pn, rn, field


def unique(rows):
    result = {key(row): row for row in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate fresh source field')
    return result


def positive(value):
    if type(value) is not int or value <= 0:
        raise ValueError('Fresh positive money must be a literal integer')
    return value


def source_image_check(reference):
    path=Path(reference['path'])
    if not path.is_absolute():path=ledger.ROOT/path
    if not path.exists():
        matches=[]
        for index in sorted((ledger.AREA/'triangulation').glob('archived-source-money-views-*.json')):
            archive=json.loads(index.read_text())
            matches.extend(r['archivedExactBytes']for r in archive['rows']if r['originalReference']==reference)
        if len(matches)!=1 or matches[0]['sha256']!=reference['sha256']:
            raise ValueError('Missing unique archived original source view')
        path=ledger.ROOT/matches[0]['path']
    if ledger.sha(path.read_bytes())!=reference['sha256']:
        raise ValueError('Pinned original source-money image changed')


def build(peer_reference, overlay_reference):
    review = ledger.pinned(peer_reference)
    overlay = ledger.pinned(overlay_reference)
    source = (overlay['sourceId'], overlay['sourceSha256'], overlay['batch'])
    if 'sourceId' in review:
        if source[:2]!=(review['sourceId'],review['sourceSha256']):raise ValueError('Source-money peer and overlay identities differ')
        if 'batch'in review:
            if review['batch']!=source[2]:raise ValueError('Source-money peer batch differs')
        elif not ('peerRawSourceFirst'in review and 'authorScopedChoicesOpenedAfterRaw'in review):
            raise ValueError('Missing source-money peer batch header')
    inputs = [peer_reference]
    sparse_reference=None
    independent_raws=None

    def read(reference):
        value = ledger.pinned(reference)
        inputs.append(reference)
        return value

    def image_check(reference):
        # Retain exact original temporary references; unique archived leaf bytes
        # permit clean-CI replay after the reviewer workspace is gone.
        source_image_check(reference)

    separate_nulls=[]
    if 'onlyMatchingFiftyfiveComparisonAfterBothFreezes'in review:
        from finish_salary_phsa_money_sparse_current import replay
        schema='sparse-author-source-events-and-current-wholepage-independent-peer-v1'
        facts,raw_reference,author_corrections,peer_corrections=replay(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=read(review['sourceOnlyPacket'])
        choices=read(review['onlyMatchingFiftyfiveComparisonAfterBothFreezes']);sparse_reference=choices['originalSparseImageFirstTranscript'];inputs.append(sparse_reference)
    elif 'authorAll42CanonicalFinal'in review and 'root264AdditiveRestoration'in review:
        from finish_salary_phsa_money_canonical import root_canonical_table
        schema='complete-root-canonical-money-table-with-first-secondary-and-fresh-third-history-v1'
        facts,raw_reference,author_corrections,peer_corrections=root_canonical_table(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif 'exactDisjointPeerPartition'in review and 'own282SourceReread'in review:
        from finish_salary_phsa_money_exhaustive import replay,independent_peer_raws
        schema='exhaustive-canonical-money-union-with-three-distinct-source-first-peers-v1'
        facts,separate_nulls,raw_reference,author_corrections,peer_corrections=replay(review,overlay,source,read,image_check,unique,key)
        independent_raws=independent_peer_raws(review,read)
        raw=ledger.pinned(raw_reference);own=read(review['own282SourceReread']);packet=read(own['sourceOnlyPacket'])
    elif review.get('receiptSchema')=='canonical-wholepage-literal-tuple-money-peer-v1':
        from finish_salary_phsa_money_canonical import wholepage_literal_peer
        schema=review['receiptSchema']
        facts,raw_reference,author_corrections,peer_corrections=wholepage_literal_peer(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif 'supersedesCurrentAuthorityOfOnly394InPriorReceipt'in review:
        from finish_salary_phsa_money_canonical import root_positive_canonical
        schema='complete-root-positive-table-with-one-independent-canonical-correction-v1'
        facts,raw_reference,author_corrections,peer_corrections=root_positive_canonical(review,overlay,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif 'peerOwnPostcomparisonCorrections'in review and 'source107Limit'in review:
        from finish_salary_phsa_money_canonical import mixed_wholepage_peer
        schema='canonical-mixed-source-peer-with-unchanged-positive-money-v1'
        facts,raw_reference,author_corrections,peer_corrections=mixed_wholepage_peer(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif review.get('receiptSchema')=='historical-phsa-scoped-source-fields-with-additive-rereads-v1':
        from finish_salary_phsa_money_scoped import replay
        schema=review['receiptSchema']
        facts,raw_reference,author_corrections,peer_corrections=replay(review,overlay,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif review.get('receiptSchema')=='image-first-literal-tuple-peer-with-additive-source-rereads-v1':
        from finish_salary_phsa_money_standard import literal_tuple_peer
        schema=review['receiptSchema']
        facts,raw_reference,author_corrections,peer_corrections=literal_tuple_peer(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif review.get('receiptSchema')=='two-independent-source-money-readers-with-additive-rereads-v1':
        from finish_salary_phsa_money_standard import replay
        schema=review['receiptSchema']
        facts,separate_nulls,raw_reference,author_corrections,peer_corrections=replay(
            review,source,read,image_check,unique,key,ledger.ROOT)
        packet=ledger.pinned(review['sourceOnlyPacket']);raw=ledger.pinned(raw_reference)
        if review['authorOriginalFrozenTranscript']not in inputs:inputs.append(review['authorOriginalFrozenTranscript'])
    elif 'scopedAuthor53OnlyChoices'in review:
        from finish_salary_phsa_money_standard import root_positive_table
        schema='count-bounded-root-positive-money-with-additive-source-rereads-v1'
        facts,raw_reference,author_corrections,peer_corrections=root_positive_table(review,overlay,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
    elif 'scopedAuthorOneChoice'in review:
        from finish_salary_phsa_money_standard import one_root_peer
        schema='one-exact-root-source-field-with-unchanged-author-first-v1'
        facts,raw_reference=one_root_peer(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
        author_corrections=peer_corrections=0
    elif 'authorFinalSourceCorrections'in review or 'authorOnlyPostPeerSourceCorrection'in review:
        from finish_salary_phsa_money_municipal import replay
        schema='separate-complete-source-peer-with-author-first-and-secondary-history-v1'
        facts,raw_reference,author_corrections=replay(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
        peer_corrections=0
    elif 'peerRawSourceFirst'in review and 'authorScopedChoicesOpenedAfterRaw'in review:
        from finish_salary_phsa_money_standard import unchanged_overlay_peer
        schema='unchanged-source-table-with-exact-author-raw-and-overlay-v1'
        facts,raw_reference=unchanged_overlay_peer(review,source,read,image_check,unique,key)
        raw=ledger.pinned(raw_reference);packet=ledger.pinned(raw['sourceOnlyPacket'])
        author_corrections=peer_corrections=0
    elif 'all52FinalLiteralValuesMatch' in review:
        from finish_salary_phsa_money_standard import ordered_peer
        schema='ordered-root-peer-with-exact-tuple-author-joins-v1'
        facts,raw_reference,author_corrections=ordered_peer(review,source,read,image_check,unique,key)
        packet=ledger.pinned(review['sourceOnlyPacket']);raw=ledger.pinned(raw_reference)
        peer_corrections=0
    elif 'freshOriginalImageFirstTranscript' in review:
        schema = 'separate-frozen-source-readers-v1'
        raw_reference = review['freshOriginalImageFirstTranscript']
        raw = read(raw_reference)
        choices = read(review['authorChoicesFrozenBeforePeerValuesOpened'])
        packet_reference = choices['sourceOnlyPacket']
        packet = read(packet_reference)
        proof = read(review['independentSourcePixels'])
        amendment = read(review['rootOwnSourceRereadAmendment'])
        author_raw = read(choices['independentOriginalImageFirstTranscript'])
        author_amendment = read(choices['authorOwnPostComparisonSourceReread'])
        if (raw['authorOrOcrChoicesOpened'] is not False or choices['peerValuesOpened'] is not False
                or raw['allRequestedFieldsReadBeforeAuthorOrOcrChoices'] is not True
                or raw['genuineUnresolvedMonetaryFields']
                or raw['sourceOnlyPacketSha256'] != packet_reference['sha256']
                or proof['sourceOnlyPacketSha256'] != packet_reference['sha256']
                or proof['actualOriginal600DpiFieldsIndependentlyReproducedPixelExact'] != len(packet['rows'])
                or len(raw['readingsInPacketOrder']) != len(packet['rows'])):
            raise ValueError('Fresh independent source-first or source-pixel gate failed')
        target, authors, peers = unique(packet['rows']), unique(choices['rows']), unique(review['rows'])
        if set(target) != set(authors) or set(target) != set(peers):
            raise ValueError('Fresh source peer must cover exactly the frozen target set')
        peer_changes=unique(amendment['changes'] if 'changes' in amendment else [amendment])
        if amendment['imageFirstPeerTranscript'] != raw_reference or not set(peer_changes).issubset(target):
            raise ValueError('Source-reread amendment is outside its frozen transcript')
        for change in peer_changes.values():image_check(change['actualOriginal1200DpiReread'])
        original_author_rows = {(r['physicalPage'],r['sourceRowOnPage']):r for r in author_raw['rows']}
        author_changes=unique(author_amendment['ownCorrections'] if 'ownCorrections' in author_amendment else [author_amendment['ownCorrection']])
        first_frozen=(author_raw.get('frozenBeforeOpeningFullCandidate') is True or author_raw.get('frozenBeforeCandidateOpening') is True)
        if (not first_frozen or author_raw['fullCandidateOpened'] is not False
                or author_amendment['originalFrozenFirstPass'] != choices['independentOriginalImageFirstTranscript']
                or not set(author_changes).issubset(target)):
            raise ValueError('Author source-first correction history is not pinned to the actual field')
        for identity,change in author_changes.items():
            if (change['initialReading'] != original_author_rows[identity[:2]]['literalSourceValuesFirstPass'][identity[2]]
                    or change['actual600SourceField'] != target[identity]['actual600SourceField']):
                raise ValueError('Author amendment changes its frozen first value or original source view')
        for identity,change in peer_changes.items():
            amended_index=next(i for i,r in enumerate(packet['rows']) if key(r)==identity)
            if change['firstRootReading'] != raw['readingsInPacketOrder'][amended_index]:
                raise ValueError('Peer amendment hides its actual first-pass source reading')
        for document in [choices, author_raw, author_amendment]:
            if (document['sourceId'],document['sourceSha256'],document['batch']) != source:
                raise ValueError('Author raw source identity differs')
        facts = []
        for i, source_row in enumerate(packet['rows']):
            identity = key(source_row)
            author, peer = authors[identity], peers[identity]
            first = raw['readingsInPacketOrder'][i]
            final_peer = peer_changes[identity]['literalSourceReread'] if identity in peer_changes else first
            author_first = original_author_rows[identity[:2]]['literalSourceValuesFirstPass'][identity[2]]
            author_final = author_changes[identity]['literalSourceReread'] if identity in author_changes else author_first
            if (peer['firstRootSourceReading'] != first or peer['finalRootSourceReading'] != final_peer
                    or author['initialImageFirstValue'] != author_first
                    or author['finalAuthorSourceValue'] != author_final
                    or peer['initialAuthorSourceReading'] != author['initialImageFirstValue']
                    or peer['finalAuthorSourceReading'] != author['finalAuthorSourceValue']
                    or peer['finalIndependentSourceReadingsMatch'] is not True
                    or final_peer != author['finalAuthorSourceValue']
                    or peer['sourceImageCropSha256'] != source_row['originalFullRowCropSha256']
                    or author['actual600SourceField'] != source_row['actual600SourceField']
                    or author['originalFullRowCropSha256'] != source_row['originalFullRowCropSha256']):
                raise ValueError('Fresh source-reader facts differ from pinned raw/adjudication evidence')
            facts.append((source_row, final_peer, source_row['actual600SourceField'],
                          source_row['originalFullRowCropSha256']))
        peer_corrections = sum(r['firstRootSourceReading'] != r['finalRootSourceReading'] for r in peers.values())
        author_corrections = sum(r['initialAuthorSourceReading'] != r['finalAuthorSourceReading'] for r in peers.values())
        if (peer_corrections != review['rootOwnFirstReadingCorrections']
                or author_corrections != review['authorOwnFirstReadingCorrections']):
            raise ValueError('Source-reader correction counts differ')
    elif 'authorMoney89AdditiveCorrection' in review:
        schema='ordered-peer-and-explicit-post-choice-money-source-amendment-v1'
        raw_reference=review['independentImageFirstTranscript'];raw=read(raw_reference)
        packet=read(review['sourceOnlyPacket']);choices=read(review['authorChoicesOpenedAfterTranscriptFreeze'])
        author_raw=read(choices['independentOriginalImageFirstTranscript'])
        before=read(review['authorOwnCorrectionAlreadyFrozenBeforeRootFirstReading'])
        post=read(review['authorMoney89AdditiveCorrection']);third=read(review['independentThird89SourceOnlyReading'])
        proof=read(review['sourcePixelProof'])
        if (raw['authorOrOcrChoicesOpened'] is not False or raw['unresolvedFields'] or review['unresolvedFields']
                or author_raw.get('frozenBeforeCandidateOpening') is not True
                or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']
                or choices['sourceOnlyPacket']!=review['sourceOnlyPacket']
                or choices['peerValuesOpened'] is not False
                or choices['authorOwnPostComparisonSourceReread']!=review['authorOwnCorrectionAlreadyFrozenBeforeRootFirstReading']
                or before['originalFrozenFirstPass']!=choices['independentOriginalImageFirstTranscript']
                or post['originalFirstPass']!=choices['independentOriginalImageFirstTranscript']
                or proof['sourceOnlyPacketSha256']!=review['sourceOnlyPacket']['sha256']
                or proof['sourceSha256']!=source[1] or len(raw['readingsInPacketOrder'])!=len(packet['rows'])):
            raise ValueError('Post-choice source amendment does not preserve exact blinded histories')
        targets,authors,peers,pixels=unique(packet['rows']),unique(choices['rows']),unique(review['rows']),unique(proof['rows'])
        if set(targets)!=set(authors) or set(targets)!=set(peers) or set(targets)!=set(pixels):
            raise ValueError('Post-choice monetary confirmation widens or omits a source field')
        original={(r['physicalPage'],r['sourceRowOnPage']):r for r in author_raw['rows']}
        early=before['ownCorrection'];early_key=key(early);post_key=key(post)
        if early_key not in targets or post_key not in targets or early_key==post_key:
            raise ValueError('Source correction tuples are outside distinct frozen fields')
        image_check(review['actualOriginal1200Money89'])
        if (post['actualOriginal1200Source']!=review['actualOriginal1200Money89']
                or post['actual1200PixelsIndependentlyReproducedExactly'] is not True
                or third['sourceSha256']!=source[1] or third['batch']!=source[2]
                or any(third['blindness'].values()) or third['uncertain'] is not False
                or third['literalInteger']!=post['currentLiteral1200SourceReading']
                or {k:third['sourceImage'][k]for k in ['path','sha256']}!=review['actualOriginal1200Money89']):
            raise ValueError('Post-choice correction lacks exact fresh-third original-source corroboration')
        facts=[];author_corrections=0
        for i,source_row in enumerate(packet['rows']):
            identity=key(source_row);choice,peer,checked=authors[identity],peers[identity],pixels[identity]
            first=original[identity[:2]]['literalSourceValuesFirstPass'][identity[2]]
            frozen_final=early['literalSourceReread'] if identity==early_key else first
            final=post['currentLiteral1200SourceReading'] if identity==post_key else frozen_final
            value=raw['readingsInPacketOrder'][i]
            if (choice['initialImageFirstValue']!=first or choice['finalAuthorSourceValue']!=frozen_final
                    or (peer['sourceId'],peer['sourceSha256'])!=source[:2]
                    or peer['firstAuthorImageReading']!=first or peer['frozenAuthorChoicesValue']!=frozen_final
                    or peer['finalAuthorSourceValue']!=final or peer['literalSourceValue']!=value or value!=final
                    or peer['firstRootImageReading']!=value or peer['matchesFrozenFinalAuthorValue'] is not True
                    or peer['actual600SourceImage']!=source_row['actual600SourceField']
                    or checked['actual600OriginalPixelsReproducedExactly'] is not True
                    or checked['actual600PngSha256Matches'] is not True):
                raise ValueError('Post-choice source first/frozen/final values or original pixels differ')
            if identity==early_key and early['initialReading']!=first:raise ValueError('Early correction hides source first reading')
            if identity==post_key and post['originalOwnFirstReading']!=first:raise ValueError('Late correction hides source first reading')
            author_corrections+=first!=final
            facts.append((source_row,final,source_row['actual600SourceField'],source_row['originalFullRowCropSha256']))
        peer_corrections=0
        if review['rootOwnCorrections']!=0 or review['authorOwnCorrectionCount']!=author_corrections:
            raise ValueError('Post-choice source correction counts differ')
    elif review.get('receiptSchema')=='two-frozen-source-reader-money-v1':
        schema='sparse-author-events-and-fresh-source-money-v1'
        raw_reference=review['independentImageFirstTranscript'];raw=read(raw_reference)
        packet=read(review['sourceOnlyPacket'])
        choices=read(review['authorChoicesOpenedAfterPeerRawFreeze'])
        proof=read(review['independentSourcePixelProof'])
        amendments=read(review['peerOwnSourceRereadAmendments'])
        sparse_reference=choices['originalRawImageFirstTranscript']
        sparse_path=ledger.ROOT/sparse_reference['path']
        if ledger.sha(sparse_path.read_bytes())!=sparse_reference['sha256']:
            raise ValueError('Frozen sparse source transcript changed')
        events={};columns={'nameLiteral':'name','remunerationLiteral':'remuneration','expensesLiteral':'expenses'}
        with sparse_path.open() as handle:
            for event in csv.DictReader(handle,delimiter='\t'):
                for column,field in columns.items():
                    if event[column]=='':continue  # blank event is never source-null
                    event_key=(int(event['sequence']),field)
                    if event_key in events:raise ValueError('Duplicate nonempty sparse source-field event')
                    events[event_key]=event[column]
        target,authors,peers=unique(packet['rows']),unique(choices['rows']),unique(review['rows'])
        first=unique(raw['rows']);checked=unique(proof['rows']);changes=unique(amendments['changes'])
        if (set(target)!=set(authors) or set(target)!=set(peers) or set(target)!=set(first)
                or set(target)!=set(checked) or not set(changes).issubset(target)
                or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']
                or choices['sourceOnlyPacket']!=review['sourceOnlyPacket']
                or raw['readFromActualOriginal600DpiViewsBeforeAnyAuthorOrMachineChoices'] is not True
                or choices['freshPeerFullLiteralChoicesNotOpenedBeforeThisReceipt'] is not True
                or raw['unresolvedFields'] or review['unresolvedFields']):
            raise ValueError('Sparse/fresh source money scope or blind-freeze gate differs')
        batch_path=ledger.AREA/'batches'/(source[0]+'-batch-'+source[2].rsplit('-',1)[1]+'.json')
        batch=ledger.pinned({'path':str(batch_path.relative_to(ledger.ROOT)),'sha256':packet['frozenBatchSha256']})
        batch_rows={r['sequence']:r for r in batch['rows']}
        for document in [choices,proof,amendments]:
            if (document['sourceId'],document['sourceSha256'],document['batch'])!=source:
                raise ValueError('Sparse source proof belongs to a different original/batch')
        facts=[]
        for identity,source_row in target.items():
            author,peer,original,check=authors[identity],peers[identity],first[identity],checked[identity]
            literal=events[(source_row['sequence'],source_row['field'])]
            batch_row=batch_rows[source_row['sequence']]
            if (identity[:2]!=(batch_row['physicalPage'],batch_row['sourceRowOnPage'])
                    or identity[2] not in batch_row['reviewTargetFields']
                    or source_row['originalFullRowCropSha256']!=batch_row['cropSha256']):
                raise ValueError('Sparse source target widens/moves a frozen requested field')
            if not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',literal):
                raise ValueError('Sparse author money is not a literal positive whole-dollar value')
            author_value=int(literal.replace(',',''));peer_first=original['literalSourceValue']
            peer_final=changes[identity]['finalSourceValue'] if identity in changes else peer_first
            if identity in changes:
                change=changes[identity]
                if change['firstPeerSourceValue']!=peer_first:raise ValueError('Fresh peer amendment hides its first value')
                image_check(change['actualOriginal1200SourceView'])
            if (peer['firstPeerSourceValue']!=peer_first or peer['finalPeerSourceValue']!=peer_final
                    or peer['frozenAuthorSourceValue']!=author_value or author['ownLiteralValue']!=author_value
                    or author['valueUnchangedFromFrozenImageFirstTranscript'] is not True
                    or peer['matchesFrozenAuthorSourceValue'] is not True or peer_final!=author_value
                    or peer['actualSource600OriginalView']!=source_row['actual600FieldImage']
                    or original['actualSource600OriginalView']!=source_row['actual600FieldImage']
                    or check['originalReference']!=source_row['actual600FieldImage']
                    or peer['archivedExactOriginal600View']!=check['archivedExactBytes']
                    or check['sourcePixelsIndependentlyReproducedExactly'] is not True
                    or peer['originalFullRowCropSha256']!=source_row['originalFullRowCropSha256']):
                raise ValueError('Sparse source first/final/crop/pixel facts differ from frozen evidence')
            if check['archivedExactBytes']['sha256']!=source_row['actual600FieldImage']['sha256']:
                raise ValueError('Archived reviewed source pixels differ from original source-only view')
            facts.append((source_row,peer_final,check['archivedExactBytes'],source_row['originalFullRowCropSha256']))
        peer_corrections=sum(first[k]['literalSourceValue']!=peers[k]['finalPeerSourceValue'] for k in peers)
        author_corrections=0
        if peer_corrections!=review['reviewerOwnFirstPassCorrections'] or review['authorCurrentValueCorrectionsRequired']!=0:
            raise ValueError('Sparse source peer reading-correction history differs')
    elif 'independentImageFirstTranscript' in review and 'originalRootTranscript' in review:
        schema = 'mixed-source-fields-with-independent-reader-v1'
        raw_reference = review['independentImageFirstTranscript']
        raw = read(raw_reference)
        packet_reference = raw['sourceOnlyPacket']
        packet = read(packet_reference)
        author = read(review['originalRootTranscript'])
        amendments = read(review['additiveOwnCorrections'])
        if (raw['frozenBeforeRootAuthorOrOcrChoices'] is not True
                or raw['fullBatchCandidateOpened'] is not False
                or author['frozenBeforeCandidateOpening'] is not True
                or amendments['originalImageFirstTranscript'] != review['originalRootTranscript']
                or amendments['independentBlindedTwelveFieldSourcePeer'] != raw_reference):
            raise ValueError('Fresh independent source-first order is not pinned')
        target, peers = unique(packet['rows']), unique(review['rows'])
        entries = {(e['sequence'], e['field']): e for e in raw['entries']}
        if (set(target) != set(peers) or len(entries) != len(raw['entries'])
                or set(entries) != {(r['sequence'], r['field']) for r in packet['rows']}):
            raise ValueError('Mixed source peer must cover exactly the frozen target set')
        changes = unique(amendments['changes'])
        if not set(changes).issubset(target):
            raise ValueError('Source amendment widens the frozen peer scope')
        facts = []
        for source_row in packet['rows']:
            identity = key(source_row)
            peer, entry = peers[identity], entries[(source_row['sequence'], source_row['field'])]
            first = author['readings'][str(source_row['sequence'])][source_row['field']]
            final = changes[identity]['confirmedSourceReading'] if identity in changes else first
            if (peer['firstRootReading'] != first or peer['confirmedSourceReading'] != final
                    or peer['rootFirstAndPeerMatch'] != (first == entry['literalSourceValue'])
                    or entry['literalSourceValue'] != final
                    or peer['rootOriginal600DpiReread'] != source_row['actual600DpiSourceView']):
                raise ValueError('Mixed source peer differs from actual frozen source readings')
            facts.append((source_row, final, source_row['actual600DpiSourceView'], source_row['originalCropSha256']))
        author_corrections = len(changes)
        peer_corrections = None  # peer's own precomparison corrections remain in its original receipt
        if author_corrections != review['firstRootCorrections']:
            raise ValueError('Mixed source reader correction count differs')
    else:
        raise ValueError('Unsupported versioned source-money receipt schema')

    for document in [packet, raw]:
        if (document['sourceId'], document['sourceSha256']) != source[:2]:
            raise ValueError('Source-only transcript identity differs')
        if 'batch'in document:
            if document['batch']!=source[2]:raise ValueError('Source-only transcript batch differs')
        elif not (schema=='historical-phsa-scoped-source-fields-with-additive-rereads-v1'and document is packet):
            raise ValueError('Missing source-only transcript batch header')
    overlay_rows = {(r['physicalPage'], r['sourceRowOnPage']): r for r in overlay['overlays']}
    for source_row,value,image,crop in separate_nulls:
        pn,rn,field=key(source_row);row=overlay_rows[(pn,rn)]
        if field!='expenses' or field not in row['reviewedFields'] or row['resolvedRow'][ledger.FIELDS[field]]is not None or row['cropSha256']!=crop:
            raise ValueError('Separately confirmed literal dash differs from effective source overlay')
    confirmed = []
    for source_row, value, image, crop in facts:
        pn, rn, field = key(source_row)
        if field not in ['remuneration', 'expenses']:
            continue
        positive(value)
        row = overlay_rows[(pn, rn)]
        if (field not in row['reviewedFields'] or row['resolvedRow'][ledger.FIELDS[field]] != value
                or row['cropSha256'] != crop):
            raise ValueError('Effective source overlay differs from the fresh peer money/crop')
        image_check(image)
        confirmed.append({'sourceId':source[0], 'sourceSha256':source[1], 'physicalPage':pn,
                          'sourceRowOnPage':rn, 'field':field, 'confirmedValue':value,
                          'effectiveAuthorOverlay':overlay_reference, 'peerComparison':peer_reference,
                          'freshSourceImage':image, 'imageFirstTranscript':raw_reference})
    if not confirmed:
        raise ValueError('Fresh source confirmation has no monetary fields')
    result={'frozen':True, 'adapter':'count-independent-source-money-peer-v1', 'sourceReceiptSchema':schema,
            'peerInputs':inputs, 'confirmations':confirmed, 'completeFrozenSourceTargetFields':len(facts)+len(separate_nulls),
            'confirmedMonetaryFields':len(confirmed), 'originalAuthorOwnSourceCorrections':author_corrections,
            'originalPeerOwnSourceCorrections':peer_corrections,
            'scope':'Exact source-money fields only. Original first-pass disagreements/corrections are retained; no balancing, name or unrelated field authority.'}
    if sparse_reference:result['authorSparseRawTranscript']=sparse_reference
    if independent_raws is not None:
        result['authorImageFirstTranscript']=raw_reference
        result['independentPeerImageFirstTranscripts']=independent_raws
        result['imageFirstTranscriptRole']='Per-confirmation imageFirstTranscript is the author complete633-field raw; the three independent peer raws and each final source peer are separately explicit.'
        peer_rows=unique(review['rows'])
        for row in confirmed:row['independentSourcePeer']=peer_rows[key(row)]['independentSourcePeer']
    if separate_nulls:result['literalSourceDashFieldsConfirmedSeparately']=[{
        'physicalPage':key(row)[0],'sourceRowOnPage':key(row)[1],'field':key(row)[2],
        'value':None,'freshSourceImage':image,'originalFullRowCropSha256':crop,
        'route':'Separately image-confirmed explicit source dash; excluded from positive-money confirmations.'}
        for row,value,image,crop in separate_nulls]
    return result


def emit(peer_reference, overlay_reference, out):
    result = build(peer_reference, overlay_reference)
    if out.exists():
        raise ValueError('Never replace frozen source-money confirmations')
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return ledger.pin(out)
