#!/usr/bin/env python3
"""Independent readers for only the original 007 and 020 financial ledgers.

No producer, finalizer, dispatcher or v7 implementation is imported. Human
interpretations remain the original source records; this reader independently
joins their fields, histories, original-PDF geometry and exact ledger members.
"""
import csv
import hashlib
import io
from pathlib import Path
import re

import fitz
from PIL import Image


SOURCE = 'phsa-2019-20'
PDF_SHA = '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02'
MODES = {
    'f84faa0afa911828578812ab01bb664f79f7aac4b09593f0daebf7797cb9e1de':
        ('sparse-author-events-and-fresh-source-money-v1', 43, '005'),
    'dfc426bb2a520aeae5f973288eb85e332cec9bf6b2224098adc595e741a8aa70':
        ('historical-phsa-scoped-source-fields-with-additive-rereads-v1', 67, '006'),
}
_CACHE = {}
_PDF = None


def _ok(condition, reason):
    if not condition:
        raise ValueError('Independent 007/020 money replay: ' + reason)


def _key(row):
    page, number, field = row['physicalPage'], row['sourceRowOnPage'], row['field']
    _ok(type(page) is int and type(number) is int and page > 0 and number > 0
        and field in {'name', 'remuneration', 'expenses'}, 'invalid physical field identity')
    if 'sourceId' in row:
        _ok(row['sourceId'] == SOURCE, 'row has another source')
    if 'sourceSha256' in row:
        _ok(row['sourceSha256'] == PDF_SHA, 'row has another original PDF')
    return page, number, field


def _index(rows, key=_key):
    result = {key(row): row for row in rows}
    _ok(len(result) == len(rows), 'duplicate physical field / sequence')
    return result


def _positive(value):
    _ok(type(value) is int and value > 0, 'positive source amount is not an integer')
    return value


def _literal(text):
    _ok(isinstance(text, str) and re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', text),
        'unparsed / absent / signed / fractional source money')
    return _positive(int(text.replace(',', '')))


def _bytes(reference, load):
    data = load(reference, False)
    _ok(isinstance(data, bytes) and hashlib.sha256(data).hexdigest() == reference['sha256'],
        'source image / sparse transcript bytes changed')
    return data


def _source(document, batch, *, optional_batch=False, frozen=False):
    _ok((document.get('sourceId'), document.get('sourceSha256')) == (SOURCE, PDF_SHA),
        'document source identity differs')
    _ok(document.get('batch') == batch or optional_batch and 'batch' not in document,
        'document batch identity differs')
    _ok('frozen' not in document or document['frozen'] is True, 'explicitly unfrozen document')
    if frozen:
        _ok(document.get('frozen') is True, 'source transcript is not frozen')


def _document(reference, load, batch, **kwargs):
    result = load(reference)
    _source(result, batch, **kwargs)
    return result


def _pdf():
    global _PDF
    if _PDF is None:
        path = Path('/tmp/queue-completion-phsa/originals') / (SOURCE + '.pdf')
        data = path.read_bytes()
        _ok(hashlib.sha256(data).hexdigest() == PDF_SHA, 'independent original PDF differs')
        _PDF = fitz.open(stream=data, filetype='pdf')
    return _PDF


def _pixels(image_reference, archive_reference, page, dpi, point_box, load):
    """Reproduce the actual declared partial-source paint, without reinterpretation.

    These two historic schemas explicitly used partial600/1200 views. This is
    their byte/source check, not a claim they were whole-page canonical views.
    """
    _ok(image_reference['sha256'] == archive_reference['sha256'], 'archive image hash differs')
    data = _bytes(archive_reference, load)
    supplied = Image.open(io.BytesIO(data)).convert('RGB')
    pix = _pdf()[page - 1].get_pixmap(dpi=dpi, alpha=False, clip=fitz.Rect(point_box))
    _ok(supplied.size == (pix.width, pix.height) and supplied.tobytes() == pix.samples,
        'declared original-PDF source crop pixels differ')


def _sparse_events(data):
    events = {}
    stream = csv.DictReader(io.StringIO(data.decode('utf-8')), delimiter='\t')
    _ok(stream.fieldnames == ['sequence', 'nameLiteral', 'remunerationLiteral', 'expensesLiteral'],
        'sparse author transcript columns differ')
    for row in stream:
        _ok(re.fullmatch('[1-9][0-9]*', row['sequence']) is not None, 'invalid sparse sequence')
        for column, field in [('nameLiteral', 'name'), ('remunerationLiteral', 'remuneration'),
                              ('expensesLiteral', 'expenses')]:
            text = row[column]
            if text == '':
                continue
            identity = int(row['sequence']), field
            _ok(identity not in events, 'duplicate NONEMPTY sparse author field event')
            events[identity] = text
    return events


def _overlay(ledger, load, batch):
    rows = ledger['confirmations']
    refs = {tuple(sorted(row['effectiveAuthorOverlay'].items())) for row in rows}
    _ok(len(refs) == 1, 'original ledger covers more than its one original overlay')
    reference = rows[0]['effectiveAuthorOverlay']
    overlay = _document(reference, load, batch, frozen=True)
    physical = _index(overlay['overlays'], lambda row: (row['physicalPage'], row['sourceRowOnPage']))
    author_review = _document(overlay['reviewInput'], load, batch)
    batch_doc = _document(overlay['frozenBatch'], load, batch, frozen=True)
    targets = _index(batch_doc['rows'], lambda row: row['sequence'])
    _ok(len(targets) == 400, 'complete original author batch is not 400 unique rows')
    return reference, overlay, physical, author_review, targets


def _verify_007(ledger, load, batch):
    review_ref = ledger['peerInputs'][0]
    review = _document(review_ref, load, batch, frozen=True)
    raw_ref = review['independentImageFirstTranscript']
    raw = _document(raw_ref, load, batch, frozen=True)
    packet = _document(review['sourceOnlyPacket'], load, batch)
    choices = _document(review['authorChoicesOpenedAfterPeerRawFreeze'], load, batch)
    proof = _document(review['independentSourcePixelProof'], load, batch, frozen=True)
    amend = _document(review['peerOwnSourceRereadAmendments'], load, batch, frozen=True)
    overlay_ref, overlay, overlay_rows, author_review, batch_rows = _overlay(ledger, load, batch)
    sparse_ref = choices['originalRawImageFirstTranscript']
    freeze = _document(author_review['imageFirstTranscriptFreeze'], load, batch)
    _ok(raw['sourceOnlyPacket'] == review['sourceOnlyPacket'] == choices['sourceOnlyPacket'] == proof['sourceOnlyPacket']
        and raw['independentSourcePixelProof'] == review['independentSourcePixelProof']
        and amend['originalFrozenPeerTranscript'] == raw_ref
        and choices['freshPeerFullLiteralChoicesNotOpenedBeforeThisReceipt'] is True
        and choices['ownActual600RereadAll43ConfirmedFirstPass'] is True
        and raw['readFromActualOriginal600DpiViewsBeforeAnyAuthorOrMachineChoices'] is True
        and raw['authorManualValuesAndCorrectionsUnopened'] is True
        and raw['unresolvedFields'] == [] and review['unresolvedFields'] == []
        and review['allFinalLiteralSourceValuesMatchFrozenAuthor'] is True
        and amend['unresolvedFields'] == [] and amend['authorChoicesOpenedBeforeThisAddendum'] is True
        and freeze['fullCandidateChoicesNeverOpenedBeforeFreeze'] is True
        and freeze['frozenBatchSha256'] == overlay['frozenBatch']['sha256']
        and {'path': freeze['rawTranscriptPath'], 'sha256': freeze['rawTranscriptSha256']} == sparse_ref
        and {'path': author_review['rawTranscriptPath'], 'sha256': author_review['rawTranscriptSha256']} == sparse_ref
        and ledger['authorSparseRawTranscript'] == sparse_ref, '007 first-reading chronology differs')
    events = _sparse_events(_bytes(sparse_ref, load))
    requested = {(seq, field) for seq, row in batch_rows.items() for field in row['reviewTargetFields']}
    _ok(set(events) == requested and len(events) == 639 and freeze['fields'] == 639,
        'complete sparse639 field coverage differs (blank events are not nulls)')
    target, first, authors, finals, pixels = map(_index, [packet['rows'], raw['rows'], choices['rows'], review['rows'], proof['rows']])
    changes = _index(amend['changes'])
    _ok(len(target) == 43 and all(set(mapping) == set(target) for mapping in [first, authors, finals, pixels])
        and set(changes) <= set(target) and len(changes) == 1, '007 exact43 scope differs')
    expected = {}
    for identity, row in target.items():
        seq, field = row['sequence'], identity[2]
        _ok(field != 'name', '007 financial target contains name')
        batch_row = batch_rows[seq]
        _ok((batch_row['physicalPage'], batch_row['sourceRowOnPage']) == identity[:2]
            and field in batch_row['reviewTargetFields']
            and batch_row['cropSha256'] == row['originalFullRowCropSha256'], '007 source target moved')
        original = _literal(events[seq, field])
        before = _positive(first[identity]['literalSourceValue'])
        value = _positive(changes[identity]['finalSourceValue']) if identity in changes else before
        image, crop = row['actual600FieldImage'], row['originalFullRowCropSha256']
        a, p, pixel = authors[identity], finals[identity], pixels[identity]
        for record in [first[identity], a, p, pixel]:
            _ok(record['sequence'] == seq, '007 sequence differs')
        _ok(a['ownLiteralValue'] == original == value and a['valueUnchangedFromFrozenImageFirstTranscript'] is True
            and a['actual600FieldImage'] == image and a['originalFullRowCropSha256'] == crop
            and first[identity]['actualSource600OriginalView'] == image
            and first[identity]['originalFullRowCropSha256'] == crop
            and p['firstPeerSourceValue'] == before and p['finalPeerSourceValue'] == value
            and p['frozenAuthorSourceValue'] == original and p['matchesFrozenAuthorSourceValue'] is True
            and p['originalFullRowCropSha256'] == crop and p['actualSource600OriginalView'] == image
            and p['archivedExactOriginal600View'] == pixel['archivedExactBytes']
            and pixel['originalReference'] == image and pixel['sourcePixelsIndependentlyReproducedExactly'] is True,
            '007 source / original / corrected field differs')
        box = [coordinate * 72 / 300 for coordinate in image['original300DpiPixelBox']]
        _ok(pixel['actual600PdfClip'] == box, '007 declared source geometry differs')
        _pixels(image, pixel['archivedExactBytes'], identity[0], 600, box, load)
        if identity in changes:
            change = changes[identity]
            _ok(change['firstPeerSourceValue'] == before and before != value, '007 amendment hides its first error')
            _bytes(change['actualOriginal1200SourceView'], load)
        expected[identity] = (value, pixel['archivedExactBytes'], crop)
    _ok(review['reviewerOwnFirstPassCorrections'] == 1 and review['authorCurrentValueCorrectionsRequired'] == 0,
        '007 correction counters differ')
    return expected, overlay_ref, overlay_rows, raw_ref, review_ref


def _expand(packet):
    expanded = []
    for row in packet['rows']:
        fields = row['reviewTargetFields']
        _ok(len(fields) == len(set(fields)), 'duplicate fields inside a scoped target row')
        images = {v['field']: v for v in row['actualOriginal1200Renders']}
        _ok(len(images) == len(row['actualOriginal1200Renders']) and set(images) == set(fields),
            'scoped source images do not match requested fields')
        for field in fields:
            expanded.append({**row, 'field': field, 'image': images[field]})
    return _index(expanded)


def _verify_020(ledger, load, batch):
    review_ref = ledger['peerInputs'][0]
    review = _document(review_ref, load, batch, frozen=True)
    raw_ref = review['originalPeerImageFirstTranscript']
    raw = _document(raw_ref, load, batch, frozen=True)
    packet = _document(review['sourceOnlyPacket'], load, batch, optional_batch=True)
    choices = _document(review['scopedSchool88AuthorChoices'], load, batch)
    proof = _document(review['sourcePixelProof'], load, batch, frozen=True)
    archive = _document(review['exactSourceViewArchive'], load, batch, optional_batch=True, frozen=True)
    overlay_ref, overlay, overlay_rows, author_review, batch_rows = _overlay(ledger, load, batch)
    author_ref = {'path': author_review['rawTranscriptPath'], 'sha256': author_review['rawTranscriptSha256']}
    author = _document(author_ref, load, batch)
    _ok(raw['sourceOnlyPacket'] == review['sourceOnlyPacket'] == proof['sourceOnlyPacket']
        and raw['sourcePixelProof'] == review['sourcePixelProof']
        and raw['smallReviewedSourceAssetsArchived'] == review['exactSourceViewArchive']
        and raw['supplementalAuthorChoicesOrOcrAlternativesOpenedBeforeFreeze'] is False
        and raw['personallyReadAll88Actual1200OriginalFields'] is True
        and choices['independent88RawSha256'] == raw_ref['sha256']
        and choices['sourceOnlyPacketSha256'] == review['sourceOnlyPacket']['sha256']
        and choices['authorOriginalRawSha256'] == author_ref['sha256']
        and author['fullCandidateUnopenedAtFreeze'] is True and review['counts']['unresolved'] == 0,
        '020 source-first chronology differs')
    targets = _expand(packet)
    first, finals, pixels, copies = map(_index, [raw['rows'], review['rows'], proof['rows'], archive['rows']])
    _ok(len(targets) == 88 and all(set(mapping) == set(targets) for mapping in [first, finals, pixels])
        and set(targets) <= set(copies), '020 complete88 target scope differs')
    authors = _index(author['rows'], lambda r: r['sequence'])
    scoped = _index(choices['rows'], lambda r: r['sequence'])
    _ok(set(authors) == set(batch_rows) and len(authors) == 400 and author['fieldCount'] == 635,
        '020 complete author400/635 row scope differs')
    requested = {(seq, field) for seq, row in batch_rows.items() for field in row['reviewTargetFields']}
    actual = {(seq, field) for seq, row in authors.items() for field in row['sourceImageReadings']}
    _ok(requested == actual and len(actual) == 635, '020 original author635 field scope differs')
    state = {k: row['literalSourceValueFirstPass'] for k, row in first.items()}
    for reference in review['peerSourceRereadHistory']:
        amendment = _document(reference, load, batch, frozen=True)
        changed = _index(amendment['changes'])
        _ok(set(changed) <= set(targets), '020 source amendment widens scope')
        for identity, change in changed.items():
            for field in ['literalSourceValueFirstPass', 'firstHealthSourceReading', 'originalBlindHealthReading']:
                if field in change:
                    _ok(change[field] == first[identity]['literalSourceValueFirstPass'], '020 first peer value hidden')
            for field in ['previousHealthSecondaryReading', 'rejectedHealthSecondaryReading']:
                if field in change:
                    _ok(change[field] == state[identity], '020 intermediate peer value hidden')
            state[identity] = change['currentLiteralSourceReading']
    third = _document(review['freshThird24Adjudication'], load, batch, frozen=True)
    third_ref = third['ownIndependentSourceFirstBeforeChoices']
    third_raw = _document(third_ref, load, batch, frozen=True)
    third_changes = _document(third['ownPostcomparisonActualSourceRereadAddendum'], load, batch,
                              optional_batch=True, frozen=True)
    third_packet = _document(third_raw['sourceOnlyPacket'], load, batch, optional_batch=True)
    third_targets = _expand(third_packet)
    third_first, third_final, third_current = map(_index, [third_raw['entries'], third['rows'], third_changes['entries']])
    _ok(len(third_targets) == 24 and set(third_targets) <= set(targets)
        and all(set(mapping) == set(third_targets) for mapping in [third_first, third_final, third_current])
        and third_raw['correspondingAuthorSchoolOcrValuesNotOpenedBeforeFreeze'] is True
        and third_changes['rawBeforeCorrespondingChoices'] == third_ref
        and third['counts']['unresolvedMoney'] == 0, '020 fresh24 adjudication scope / timing differs')
    third_money_errors = 0
    for identity, target in third_targets.items():
        if identity[2] == 'name':
            continue  # No name ambiguity authority is granted by this financial reader.
        a, b, c = third_first[identity], third_final[identity], third_current[identity]
        old, value = _positive(a['literalSourceValue']), _positive(b['currentLiteralSourceValue'])
        _ok(b['ownIndependentColdLiteral'] == old == c['ownOriginalColdLiteral']
            and c['ownCurrentLiteral'] == value == state[identity]
            and c['ownPostComparisonCorrection'] is (old != value) and c['realUncertainty'] is None
            and targets[identity]['image'] in a['actualOriginal1200Renders']
            and targets[identity]['image'] in b['actualOriginal1200SourceViews']
            and a['cropSha256'] == b['cropSha256'] == target['cropSha256'] == targets[identity]['cropSha256'],
            '020 fresh adjudication does not bind its cold / current / crop')
        third_money_errors += old != value
    _ok(third_money_errors == 3 == third['counts']['ownColdMoneyCorrections'], '020 fresh third corrections differ')
    expected, peer_errors, author_errors = {}, 0, 0
    all_peer_counts = {'name': 0, 'remuneration': 0, 'expenses': 0}
    for identity, target in targets.items():
        seq, field = target['sequence'], identity[2]
        original_author, scoped_author = authors[seq], scoped[seq]
        _ok((original_author['physicalPage'], original_author['sourceRowOnPage']) == identity[:2]
            and original_author['cropSha256'] == target['cropSha256'] == batch_rows[seq]['cropSha256']
            and field in original_author['reviewTargetFields'], '020 original author source row differs')
        initial_author = original_author['sourceImageReadings'][field]
        _ok(initial_author == scoped_author['originalFrozenRawReadings'][field], '020 scoped author hides first literal')
        value, original_peer = state[identity], first[identity]['literalSourceValueFirstPass']
        p, pixel, copied = finals[identity], pixels[identity], copies[identity]
        image, crop = target['image'], target['cropSha256']
        _ok(first[identity]['originalActual1200SourceView'] == image == p['actualOriginal1200SourceView']
            and image == pixel['actual1200SourceView'] == copied['originalReference']
            and copied['archivedExactBytes'] == pixel['archivedExactBytes']
            and first[identity]['originalFullRowCropSha256'] == p['originalFullRowCropSha256'] == crop
            and p['firstPeerSourceValue'] == original_peer and p['finalPeerSourceValue'] == value
            and p['firstFrozenSchoolSourceValue'] == (_literal(initial_author) if field != 'name' else initial_author)
            and p['finalSchoolSourceValue'] == value and p['matchesCurrentSchoolSourceExactly'] is True
            and pixel['actualOriginal1200PixelsIndependentlyReproducedExactly'] is True,
            '020 full peer/source/pixel history differs')
        _pixels(image, copied['archivedExactBytes'], identity[0], 1200, image['actualPdfPointClip'], load)
        all_peer_counts[field] += original_peer != value
        if field == 'name':
            continue
        _positive(value)
        before = _literal(initial_author)
        _ok(value == _literal(scoped_author['currentAuthorSourceReadings'][field])
            and p['status'] == 'resolved-from-original-image'
            and (original_peer == value or identity in third_targets), '020 unresolved / unadjudicated positive money')
        peer_errors += original_peer != value
        author_errors += before != value
        expected[identity] = (value, copied['archivedExactBytes'], crop)
    _ok(len(expected) == 67 and peer_errors == 9 and author_errors == 7
        and all_peer_counts == {'name': 14, 'remuneration': 6, 'expenses': 3}
        and review['counts']['positiveMoney'] == 67 and review['counts']['sourceFields'] == 88,
        '020 financial totals / first-reading correction history differs')
    return expected, overlay_ref, overlay_rows, raw_ref, review_ref


def verify(confirmation, source_id, source_sha, load):
    """Verify one exact original ledger member, reconstructing each fixed ledger once."""
    _ok((source_id, source_sha) == (SOURCE, PDF_SHA), 'unsupported source')
    reference = confirmation['confirmationLedger']
    _ok(reference['sha256'] in MODES, 'unknown independent money mode/hash remains held')
    mode, amount_count, suffix = MODES[reference['sha256']]
    cache_key = reference['sha256'], id(load)
    if cache_key not in _CACHE:
        ledger = load(reference)
        _ok(ledger['frozen'] is True and ledger['adapter'] == 'count-independent-source-money-peer-v1'
            and ledger['sourceReceiptSchema'] == mode and ledger['confirmedMonetaryFields'] == amount_count,
            'original fixed ledger schema/count differs')
        counters = {'completeFrozenSourceTargetFields': 43 if suffix == '005' else 88,
                    'confirmedMonetaryFields': amount_count,
                    'originalAuthorOwnSourceCorrections': 0 if suffix == '005' else 7,
                    'originalPeerOwnSourceCorrections': 1 if suffix == '005' else 9}
        _ok(all(type(ledger[name]) is int and ledger[name] == value
                for name, value in counters.items()), 'original ledger source/correction counters differ')
        batch = SOURCE + '-' + suffix
        reconstruct = _verify_007 if suffix == '005' else _verify_020
        expected, overlay_ref, overlay_rows, raw_ref, peer_ref = reconstruct(ledger, load, batch)
        members = _index(ledger['confirmations'])
        _ok(set(members) == set(expected) and len(members) == amount_count,
            'original ledger omits/duplicates a complete positive field')
        for identity, (value, image, crop) in expected.items():
            member, row = members[identity], overlay_rows[identity[:2]]
            _ok((member['sourceId'], member['sourceSha256']) == (SOURCE, PDF_SHA)
                and _positive(member['confirmedValue']) == value
                and member['effectiveAuthorOverlay'] == overlay_ref and member['freshSourceImage'] == image
                and member['peerComparison'] == peer_ref and member['imageFirstTranscript'] == raw_ref
                and identity[2] in row['reviewedFields'] and row['cropSha256'] == crop
                and row['resolvedRow'][3 if identity[2] == 'remuneration' else 4] == value,
                'original financial confirmation differs from independently reconstructed source facts')
        _CACHE[cache_key] = members
    identity = _key(confirmation)
    members = _CACHE[cache_key]
    _ok(identity in members and confirmation == {**members[identity], 'confirmationLedger': reference},
        'requested confirmation is not the exact original fixed-ledger member')
