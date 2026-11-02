#!/usr/bin/env python3
"""Independent replay of four frozen ordered monetary peer receipt schemas.

Only the exact 002/003/008/010 confirmation ledgers below are supported. This
reader imports neither the producer's interpretation code nor the v7 caller.
``load(ref, parse=True)`` is the caller's hash-checking evidence reader. Source
interpretations remain those of the frozen humans; this module makes no new
visual reading or numeric qualification.
"""
import collections
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re


SOURCE = 'phsa-2019-20'
SOURCE_SHA = '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02'
PREFIX = 'research/salaries/queue-completion-2026-11-01/'
CONFIG = {
    '1d0b4d5d43fe9c950fc043d48deaf22e0d9db3e6c68b1aead68e4085524b3a99':
        ('002', '002', 12, None, 1, 0, '405c169f16a0b3e223b7a8d50f15d4eb33d9c3e11fa58815e0710131c21259ab'),
    '1c33c726f92ca493f2eb0a75d26c4431c64191a27446704800ba83d8304a4e44':
        ('003', '003', 38, 'separate-frozen-source-readers-v1', 1, 1,
         '53b8c2190bde3f6fd02d72776566f81f1277363a1ce062703b7878f9d5fe10de'),
    'd169d7d6e0d9a767742ad1e82d8bca992db986553f5c942bde58a11f9ffac5d3':
        ('008', '008', 14, 'ordered-peer-and-explicit-post-choice-money-source-amendment-v1', 2, 0,
         '2d53fdb8e8c95c0581722f771f75d7f7262c893ff9b18fff819abad86820bd81'),
    '53ddc8db3f1d26e36a0efbade0e871348bdfacb71d9045c6eb47c057a1b2b102':
        ('010', '007', 52, 'ordered-root-peer-with-exact-tuple-author-joins-v1', 7, 0,
         '8ad6a4fd148bfab30e75621caefe0560fba2b58b69e7291cb65c61e7e940be15'),
}
_CACHE = {}
_PIXELS = set()
_PIXEL_MODES = {}
#These three old direct-clip PNGs have reproducible renderer phase differences
#from whole600 paint. Their independently reconstructed whole300 native PNG SHA
#must still match; only the exact old600 image/hash/geometry below gets a direct
#clip replay. No general fallback or new source interpretation is authorized.
HISTORICAL_PARTIAL_600 = {
    (132, 16, 30, 'remuneration'): 'ecc06a79e9ae56c7c5920ef193d0ee769fd56879ef515b829b7ee20469f2d87e',
    (275, 19, 23, 'remuneration'): '87ee71f9cf14a3e3b4acf23226e3f55ae1522d45b659396bbd8eecb5ef0fb1bb',
    (294, 19, 51, 'remuneration'): 'ed17eeeadd6e11ca41b39bd36a380c05190401b486c3dc9c7ccda6fd6fff0c91',
}
_MONEY = {'remuneration': 3, 'expenses': 4}


def _need(condition, message):
    if not condition:
        raise ValueError(message)


def _positive(value):
    return type(value) is int and value > 0


def _amount(value):
    _need(_positive(value), 'Ordered peer money must be a literal positive integer, never bool/null')
    return value


def _count(doc, key, expected):
    _need(type(doc.get(key)) is int and doc[key] == expected, 'Declared field/error count differs: ' + key)


def _reference(ref, *, image=False):
    _need(isinstance(ref, dict), 'Missing exact evidence reference')
    path, digest = ref.get('path'), ref.get('sha256')
    _need(isinstance(path, str) and path and '\\' not in path,
          'Invalid evidence path')
    _need(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest) is not None,
          'Invalid evidence SHA256')
    if not image:
        p = PurePosixPath(path)
        _need(not p.is_absolute() and '..' not in p.parts and str(p) == path,
              'Parsed evidence must be repository relative')
    return {'path': path, 'sha256': digest}


def _header(doc, batch, *, required=True):
    _need(isinstance(doc, dict), 'Receipt must be a JSON object')
    for name, value in [('sourceId', SOURCE), ('sourceSha256', SOURCE_SHA), ('batch', batch)]:
        if required or name in doc:
            _need(doc.get(name) == value, 'Receipt source/year/batch differs')


def _empty(doc, name):
    value = doc[name]
    _need((type(value) is list and value == []) or (type(value) is int and value == 0),
          'Source receipt retains unresolved fields')


def _key(row):
    _need(isinstance(row, dict), 'Source field row must be an object')
    numbers = tuple(row.get(k) for k in ['sequence', 'physicalPage', 'sourceRowOnPage'])
    _need(all(_positive(n) for n in numbers) and row.get('field') in _MONEY,
          'Invalid exact monetary field identity')
    for name, value in [('sourceId', SOURCE), ('sourceSha256', SOURCE_SHA)]:
        if name in row:
            _need(row[name] == value, 'Field identifies another original source')
    return numbers + (row['field'],)


def _unique(rows):
    _need(isinstance(rows, list), 'Expected an explicit source field list')
    result = {}
    locations = set()
    for row in rows:
        k = _key(row)
        _need(k not in result and k[1:] not in locations, 'Repeated source monetary field')
        result[k] = row
        locations.add(k[1:])
    return result


def _row_index(rows):
    _need(isinstance(rows, list), 'Expected original row list')
    result = {}
    for row in rows:
        k = tuple(row.get(n) for n in ['sequence', 'physicalPage', 'sourceRowOnPage'])
        _need(all(_positive(n) for n in k) and k not in result, 'Invalid/repeated original row')
        result[k] = row
    return result


def _fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _literal(text, value):
    _amount(value)
    _need(isinstance(text, str) and re.fullmatch(r'(?:[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', text)
          and int(text.replace(',', '')) == value, 'Printed integer differs from frozen literal')


def _source_pixels(targets, natives, originals, load):
    """Whole-page source RGB, not producer pixel flags or interpretation code."""
    import fitz
    from PIL import Image

    pdf = Path('/tmp/queue-completion-phsa/originals') / (SOURCE + '.pdf')
    _need(hashlib.sha256(pdf.read_bytes()).hexdigest() == SOURCE_SHA, 'Original PDF hash differs')
    pending = collections.defaultdict(list)
    for k, target in targets.items():
        native = natives[k]
        image = _reference(target['actual600SourceField'], image=True)
        box = native['originalPdf300DpiPixelBox']
        _need(isinstance(box, list) and len(box) == 4 and all(type(n) is int and n >= 0 for n in box)
              and box[0] < box[2] and box[1] < box[3], 'Invalid native source pixel box')
        if 'actual600PdfClip' in target:
            expected = [Decimal(n) * Decimal(72) / Decimal(300) for n in box]
            clip = target['actual600PdfClip']
            _need(isinstance(clip, list) and len(clip) == 4 and
                  all(type(v) in (int, float) and Decimal(str(v)) == n
                      for v, n in zip(clip, expected)), 'PDF clip disagrees with native geometry')
        cache = (SOURCE_SHA, k, tuple(box), _fingerprint(native), _fingerprint(image))
        if cache not in _PIXELS:
            pending[k[1]].append((k, target, native, image, box, cache))
    if not pending:
        return
    with fitz.open(pdf) as doc:
        for page, items in sorted(pending.items()):
            rendered = {}
            for dpi in [300, 600]:
                pix = doc[page - 1].get_pixmap(dpi=dpi, alpha=False)
                rendered[dpi] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            for k, target, native, image, box, cache in items:
                _need(box[2] <= rendered[300].width and box[3] <= rendered[300].height,
                      'Source geometry is outside original page')
                cropped = rendered[300].crop(box)
                # These immutable native PNGs were encoded as direct RGB PIL crops.
                # Reproduce their actual byte SHA without unpinned /tmp image reads.
                encoded = io.BytesIO()
                cropped.save(encoded, format='PNG')
                _need(hashlib.sha256(encoded.getvalue()).hexdigest() == native['sha256'],
                      'Original whole300 native field PNG hash differs')
                data = load(image, False)
                _need(isinstance(data, bytes) and hashlib.sha256(data).hexdigest() == image['sha256'],
                      'Frozen source image bytes differ')
                archived = Image.open(io.BytesIO(data)).convert('RGB')
                actual = rendered[600].crop(tuple(n * 2 for n in box))
                mode = 'whole-page600-integer-crop-rgb-exact'
                if actual.size != archived.size or actual.tobytes() != archived.tobytes():
                    _need(HISTORICAL_PARTIAL_600.get(k) == image['sha256'] and 'actual600PdfClip' in target,
                          'Unlisted whole600 source field RGB difference')
                    pix = doc[page - 1].get_pixmap(dpi=600, alpha=False,
                                                clip=fitz.Rect(target['actual600PdfClip']))
                    historical = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                    _need(historical.size == archived.size and historical.tobytes() == archived.tobytes(),
                          'Exact historical partial600 source PNG differs')
                    mode = 'exact-listed-historical-partial600-rgb-plus-canonical-whole300-png-sha'
                _PIXEL_MODES[k] = mode
                _PIXELS.add(cache)


def _replay(ledger, profile, load):
    number, batch_number, count, schema, author_errors, peer_errors, overlay_sha = profile
    batch = SOURCE + '-' + batch_number
    inputs = ledger['peerInputs']
    _need(ledger.get('frozen') is True and isinstance(inputs, list), 'Unfrozen financial ledger')
    _need(len(inputs) == {'002': 4, '003': 8, '008': 9, '010': 7}[number], 'Peer input scope differs')
    _need(len({_fingerprint(_reference(r)) for r in inputs}) == len(inputs), 'Repeated peer input')
    docs = {}

    def get(ref):
        ref = _reference(ref)
        k = (ref['path'], ref['sha256'])
        if k not in docs:
            docs[k] = load(ref)
        _need(isinstance(docs[k], dict), 'Pinned JSON receipt is not an object')
        return docs[k]

    def image_bytes(ref):
        ref = _reference(ref, image=True)
        data = load(ref, False)
        _need(isinstance(data, bytes) and hashlib.sha256(data).hexdigest() == ref['sha256'],
              'Pinned monetary evidence image changed')

    all_inputs = [get(r) for r in inputs]
    comparison, peer = all_inputs[:2]
    if number == '003':
        author, packet = all_inputs[2:4]
        packet_ref = inputs[3]
        author_ref = inputs[2]
    else:
        packet, author = all_inputs[2:4]
        packet_ref, author_ref = inputs[2:4]
    _header(packet, batch)
    _header(peer, batch)
    _header(author, batch, required=number != '002')
    _header(comparison, batch, required=number in ['002', '003'])
    if number != '002':
        _need(ledger['adapter'] == 'count-independent-source-money-peer-v1'
              and ledger['sourceReceiptSchema'] == schema, 'Unknown ordered monetary schema')
        _need(ledger['completeFrozenSourceTargetFields'] == count
              and type(ledger['completeFrozenSourceTargetFields']) is int
              and ledger['confirmedMonetaryFields'] == count
              and type(ledger['confirmedMonetaryFields']) is int, 'Declared financial counts differ')
    else:
        _need('adapter' not in ledger and 'sourceReceiptSchema' not in ledger,
              'Legacy002 cannot be relabelled as a different adapter')
    _need(comparison.get('independentImageFirstTranscript', comparison.get('freshOriginalImageFirstTranscript')) == inputs[1],
          'Comparison borrows another peer transcript')
    author_link = 'authorChoicesFrozenBeforePeerValuesOpened' if number == '003' else 'authorChoicesOpenedAfterTranscriptFreeze'
    _need(comparison[author_link] == author_ref, 'Comparison author choice pin differs')
    if number == '003':
        _need(peer['sourceOnlyPacketSha256'] == packet_ref['sha256'], 'Ordered source packet hash differs')
    else:
        _need(comparison['sourceOnlyPacket'] == peer.get('sourceOnlyPacket', packet_ref) == packet_ref,
              'Peer source-only scope differs')
    targets = _unique(packet['rows'])
    compared = _unique(comparison['rows'])
    authors = _unique(author['rows'])
    _need(len(targets) == count and set(targets) == set(compared) == set(authors),
          'Financial source/author/peer exact field partitions differ')
    _need(list(compared) == list(targets), 'Comparison packet order shifted')
    literal_fields = {
        '002': ['literalSourceValue', 'authorFrozenValue'],
        '003': ['firstRootSourceReading', 'finalRootSourceReading', 'initialAuthorSourceReading', 'finalAuthorSourceReading'],
        '008': ['literalSourceValue', 'firstRootImageReading', 'firstAuthorImageReading', 'frozenAuthorChoicesValue', 'finalAuthorSourceValue'],
        '010': ['literalSourceValue', 'firstRootImageReading', 'firstAuthorImageReading', 'finalAuthorSourceValue'],
    }[number]
    for row in compared.values():
        for field in literal_fields:
            _amount(row[field])
        _need(not row.get('visibleAlternatives') and row.get('realUncertainty') is None
              and row.get('uncertainty') is None and row.get('numericQualification') is None,
              'A monetary field has an unresolved/qualified numeric interpretation')
    if number == '010':
        _need(list(authors) != list(targets) and comparison['authorArrayOrderDiffersFromSourceOnlyPacketOrder'] is True,
              'Actual010 author permutation must be joined by tuple, not position')
        _need(comparison['authorOwnCorrectionsFrozenBeforeRootFirstReading'] == inputs[5],
              'Original author correction history pin differs')
    raw_ref = author.get('authorImageFirstTranscript', author.get('independentOriginalImageFirstTranscript'))
    _need(raw_ref is not None and raw_ref != inputs[1], 'Author raw cannot be the independent peer raw')
    raw = get(raw_ref)
    _header(raw, batch)
    if number == '003':
        _need(raw_ref == inputs[6] and author['authorOwnPostComparisonSourceReread'] == inputs[7],
              'Separate reader original inputs differ')
    elif number == '008':
        _need(raw_ref == inputs[4] and author['authorOwnPostComparisonSourceReread'] == inputs[5],
              'Post-choice source input history differs')
    elif number == '010':
        _need(raw_ref == inputs[6] and author['authorOwnPostComparisonSourceReread'] == inputs[5],
              'Tuple-joined author source input history differs')
    if number == '002':
        _need(raw['frozen'] is True and raw['candidateOpenedBeforeFreeze'] is False
              and peer['readOriginal600DpiFieldsBeforeOpeningAuthorOrOcrChoices'] is True,
              'Legacy source-first role/timing differs')
        view_ref = raw['targetViewManifest']
        _need(comparison['sourceOnlyTargetViews'] == view_ref, 'Legacy native field manifest differs')
        _empty(peer, 'unresolvedFields')
        _need(peer['frozen'] is True, 'Peer first transcript is unfrozen')
        first_peer_rows = _unique(peer['rows'])
        _need(list(first_peer_rows) == list(targets), 'Legacy peer transcript field order differs')
        first_peer = {k: _amount(v['literalSourceValue']) for k, v in first_peer_rows.items()}
    else:
        _need(author['sourceOnlyPacket'] == packet_ref and author['peerValuesOpened'] is False,
              'Author/peer role chronology differs')
        if number == '008':
            view_ref = raw['imageFirstSourceOnlyViews']
            _need(raw['frozenBeforeCandidateOpening'] is True, 'Author raw opened candidates first')
        else:
            view_ref = raw['sourceOnlyTargetViews']
            _need(raw['frozenBeforeOpeningFullCandidate'] is True, 'Author raw opened candidates first')
        _need(raw['fullCandidateOpened'] is False and peer['frozen'] is True
              and peer['authorOrOcrChoicesOpened'] is False, 'Source-first role/timing differs')
        values = peer['readingsInPacketOrder']
        _need(isinstance(values, list) and len(values) == count, 'Ordered raw reading partition differs')
        first_peer = dict(zip(targets, map(_amount, values)))
        _empty(peer, 'genuineUnresolvedMonetaryFields' if number == '003' else 'unresolvedFields')
    views = get(view_ref)
    _header(views, batch)
    if number != '002':
        proof_ref = comparison['independentSourcePixels'] if number == '003' else comparison['sourcePixelProof']
        _need(proof_ref == inputs[{'003': 4, '008': 8, '010': 4}[number]], 'Source pixel proof pin differs')
        proof = get(proof_ref)
        _header(proof, batch, required=False)
        _need(proof['sourceOnlyPacketSha256'] == packet_ref['sha256'], 'Pixel proof uses another target packet')
        if number == '003':
            _need(peer['sourcePixelProof'] == proof_ref and proof['frozen'] is True
                  and proof['noFieldValuesRetypedOrResampled'] is True, 'Separate source pixel history differs')
            _count(proof, 'actualOriginal600DpiFieldsIndependentlyReproducedPixelExact', count)
        else:
            pixel_rows = _unique(proof['rows'])
            _need(set(pixel_rows) == set(targets) and proof['frozen'] is True,
                  'Pixel proof exact field partition differs')
            flag = ('all14Actual600SourceViewsReproducedPixelExact' if number == '008'
                    else 'all52ActualOriginal600ViewsReproducedPixelExact')
            _need(proof[flag] is True, 'Pixel proof declares an incomplete source scope')
            for row in pixel_rows.values():
                flag = ('actual600OriginalPixelsReproducedExactly' if number == '008'
                        else 'actual600SourcePixelsReproducedExactly')
                _need(row[flag] is True, 'Pixel proof declares a source mismatch')
                if number == '008':
                    _need(row['actual600PngSha256Matches'] is True, 'Pixel proof declares a different image SHA')
    view_rows = _row_index(views['rows'])
    raw_rows = _row_index(raw['rows'])
    _need(set(raw_rows) == set(view_rows), 'Author complete first transcript source scope differs')
    natives, first_author = {}, {}
    for k, target in targets.items():
        row = view_rows[k[:3]]
        initial = raw_rows[k[:3]]
        fields = row['reviewTargetFields']
        _need(isinstance(fields, list) and len(fields) == len(set(fields))
              and k[3] in fields and initial['reviewTargetFields'] == fields,
              'Requested source field scope differs')
        native_rows = row['sourceNativeTargetViews']
        native = {v['field']: v for v in native_rows}
        _need(len(native) == len(native_rows) and set(native) == set(fields), 'Native source field partition differs')
        natives[k] = native[k[3]]
        _need(native[k[3]]['noResamplingOrGlyphAlteration'] is True, 'Native source claims changed glyphs')
        if 'sourceNative300' in target:
            _need(target['sourceNative300'] == native[k[3]], 'Borrowed native source view')
        crop = target['originalFullRowCropSha256']
        _need(re.fullmatch('[0-9a-f]{64}', crop) is not None
              and crop == row['cropSha256'] == initial.get('cropSha256', initial.get('originalFullRowCropSha256')),
              'Original source crop differs')
        if 'originalFullRowCropSha256' in authors[k]:
            _need(authors[k]['originalFullRowCropSha256'] == crop, 'Author source crop differs')
        _need(authors[k]['actual600SourceField'] == target['actual600SourceField'], 'Author borrows another field image')
        first_author[k] = _amount(initial['literalSourceValuesFirstPass'][k[3]])
    #The exact old overlay is provenance input only; no producer interpreter import.
    expected_overlay = {'path': PREFIX + f'phsa/overlays/{SOURCE}-manual-overlay-{batch_number}.json', 'sha256': overlay_sha}
    overlay = get(expected_overlay)
    _header(overlay, batch)
    _need(overlay['frozen'] is True, 'Unfrozen effective overlay')
    manifest = get(overlay['imageManifest'])
    _header(manifest, batch)
    originals = _row_index(manifest['rows'])
    _need(set(originals) == set(raw_rows), 'Overlay/source original row scope differs')
    selected = {}
    for row in overlay['overlays']:
        loc = row['physicalPage'], row['sourceRowOnPage']
        _need(all(_positive(v) for v in loc) and loc not in selected, 'Duplicate/invalid overlay source row')
        selected[loc] = row
    _need(set(selected) == {k[1:] for k in originals}, 'Effective overlay scope differs')
    review = get(overlay['reviewInput'])
    _header(review, batch)
    _empty(review, 'unresolvedRows')
    _need({'path': review['rawTranscriptPath'], 'sha256': review['rawTranscriptSha256']} == raw_ref,
          'Overlay review borrows another author first transcript')
    _need(review['imageManifestSha256'] == overlay['imageManifest']['sha256']
          and review['frozenBatchSha256'] == overlay['frozenBatch']['sha256'] == views['fullBatchSha256'],
          'Overlay frozen source inputs differ')
    resolutions = {}
    for row in review['resolutions']:
        loc = row['physicalPage'], row['sourceRowOnPage']
        _need(all(_positive(v) for v in loc) and loc not in resolutions,
              'Invalid/repeated author resolution row')
        resolutions[loc] = row
    _need(set(resolutions) == set(selected), 'Author review/overlay scope differs')
    final = {}
    for k, target in targets.items():
        original, chosen, resolved = originals[k[:3]], selected[k[1:3]], resolutions[k[1:3]]
        _need(original['cropSha256'] == chosen['cropSha256'] == resolved['cropSha256'] == target['originalFullRowCropSha256'],
              'Effective overlay crop guard differs')
        _need(chosen['reviewedFields'] == resolved['reviewTargetFields'] == original['reviewTargetFields']
              and set(resolved['resolvedValues']) == set(original['reviewTargetFields']),
              'Overlay requested field scope differs')
        _need(len(chosen['resolvedRow']) == 6 and _positive(chosen['resolvedRow'][5])
              and chosen['resolvedRow'][5] == k[1], 'Invalid selected physical source row')
        final[k] = _amount(chosen['resolvedRow'][_MONEY[k[3]]])
        _need(final[k] == _amount(resolved['resolvedValues'][k[3]]), 'Review and overlay monetary literal differ')

    #Reconstruct author and peer amendments as an exact partition of actual errors.
    author_amendments, peer_amendments = {}, {}
    if number == '002':
        _need(packet['separateAuthorChoices'] == author_ref, 'Legacy author choices reference differs')
        amend = get(review['ownPostcomparisonSourceCorrection'])
        _header(amend, batch)
        _need(amend['originalFirstPass'] == raw_ref and amend['sourcePeerComparison'] == inputs[0],
              'Legacy correction does not preserve original histories')
        _need(amend['frozen'] is True and amend['noBalanceOrOtherFieldChange'] is True,
              'Legacy post-choice correction scope differs')
        k = _key(amend)
        author_amendments[k] = (_amount(amend['firstPassValue']), _amount(amend['actualSourceConfirmedValue']))
        _need(amend['actual600SourceField'] == targets[k]['actual600SourceField'], 'Legacy correction borrows source image')
        third_ref = amend['thirdFreshSourceFirst']
        third = get(third_ref)
        _header(third, batch)
        _need(_key(third) == k and third['frozenBeforeRootAuthorOrOcrChoices'] is True
              and third['realAmbiguity'] is None
              and _amount(third['literalSourceInteger']) == final[k], 'Independent third source reading differs')
        expected_correction = {'sequence': k[0], 'sourceId': SOURCE, 'physicalPage': k[1], 'sourceRowOnPage': k[2],
                               'field': k[3], 'authorFrozenValue': first_author[k],
                               'independentlyConfirmedSourceValue': final[k], 'freshThirdSourceImagePeer': third_ref}
        _need(ledger['originalAuthorSourceCorrectionsRequired'] == comparison['sourceBasedAuthorCorrectionsRequired']
              == [expected_correction], 'Legacy correction history differs')
    else:
        amend_ref = author['authorOwnPostComparisonSourceReread']
        amend = get(amend_ref)
        _header(amend, batch)
        _need(amend['originalFrozenFirstPass'] == raw_ref, 'Author amendment borrows another first transcript')
        source_changes = amend['ownCorrections'] if number == '010' else [amend['ownCorrection']]
        for row in source_changes:
            k = _key(row)
            _need(k not in author_amendments and k in targets, 'Author correction scope differs')
            author_amendments[k] = (_amount(row['initialReading']), _amount(row['literalSourceReread']))
            _need(row['actual600SourceField'] == targets[k]['actual600SourceField'], 'Author correction source image differs')
        if number == '003':
            _need(comparison['rootOwnSourceRereadAmendment'] == inputs[5], 'Peer own amendment reference differs')
            own = get(inputs[5])
            _header(own, batch, required=False)
            _need(own['imageFirstPeerTranscript'] == inputs[1] and own['rawTranscriptUnchanged'] is True,
                  'Peer error history relabelled as unchanged first agreement')
            peer_amendments[_key(own)] = (_amount(own['firstRootReading']), _amount(own['literalSourceReread']))
            image_bytes(own['actualOriginal1200DpiReread'])
        elif number == '008':
            _need(comparison['authorOwnCorrectionAlreadyFrozenBeforeRootFirstReading'] == amend_ref,
                  'Pre-peer money52 source correction chronology differs')
            extra_ref = comparison['authorMoney89AdditiveCorrection']
            extra = get(extra_ref)
            _header(extra, batch)
            _need(extra_ref == inputs[6] and extra['originalFirstPass'] == raw_ref
                  and extra['priorActual600RereadAmendment'] == amend_ref
                  and extra['afterRootPeerDisagreementRevealed'] is True
                  and extra['oldRawAndChoiceFilesUnchanged'] is True,
                  'Post-choice money89 chronology differs')
            k = _key(extra)
            _need(k == (89, 53, 41, 'expenses') and k not in author_amendments, 'Money89 correction scope differs')
            before = _amount(extra['originalOwnFirstReading'])
            _need(extra['earlierOwn600RereadAlsoWrong'] == before, 'Rejected secondary reading was hidden')
            author_amendments[k] = before, _amount(extra['currentLiteral1200SourceReading'])
            third_ref = comparison['independentThird89SourceOnlyReading']
            _need(third_ref == inputs[7], 'Money89 independent third input differs')
            third = get(third_ref)
            _header(third, batch, required=False)
            _need(third['batch'] == batch and third['sourceSha256'] == SOURCE_SHA and third['frozen'] is True
                  and third['uncertain'] is False
                  and set(third['blindness']) == {'rootChoiceOpened', 'authorChoiceOpened',
                                                   'ocrCandidateOpened', 'expectedAmountSupplied'}
                  and all(v is False for v in third['blindness'].values()),
                  'Money89 source-first uncertainty/role differs')
            _literal(third['literalPrinted'], third['literalInteger'])
            _need(third['literalInteger'] == final[k]
                  and _reference(third['sourceImage'], image=True) == extra['actualOriginal1200Source'],
                  'Money89 independent literal or source image differs')
            image_bytes(extra['actualOriginal1200Source'])
        else:
            _empty(amend, 'unresolvedMoneyFields')
            _need(amend['sourceOnlyPacket'] == packet_ref and amend['noNumericQualification'] is True,
                  'Exact tuple author correction source scope differs')

    actual_author_errors = {k for k in targets if first_author[k] != final[k]}
    actual_peer_errors = {k for k in targets if first_peer[k] != final[k]}
    _need(set(author_amendments) == actual_author_errors and len(actual_author_errors) == author_errors,
          'Original author correction partition is not exact')
    _need(set(peer_amendments) == actual_peer_errors and len(actual_peer_errors) == peer_errors,
          'Original peer correction partition is not exact')
    for amendments, originals_first in [(author_amendments, first_author), (peer_amendments, first_peer)]:
        for k, pair in amendments.items():
            _need(pair == (originals_first[k], final[k]), 'Source amendment first/current literals differ')
    expected_entries = []
    for order, (k, target) in enumerate(targets.items(), 1):
        row, a = compared[k], authors[k]
        value = final[k]
        if number == '002':
            _need(_amount(a['authorSourceValue']) == first_author[k]
                  and row['literalSourceValue'] == first_peer[k] == value
                  and row['authorFrozenValue'] == first_author[k]
                  and row['matchesFrozenAuthorValue'] is (value == first_author[k])
                  and row['actual600SourceField'] == target['actual600SourceField']
                  and row['originalFullRowCropSha256'] == target['originalFullRowCropSha256']
                  and row['actual600DpiSourcePixelsIndependentlyReproducedExactly'] is True,
                  'Legacy exact source/first/current comparison differs')
        else:
            _need(_amount(a['initialImageFirstValue']) == first_author[k], 'Author first amount differs from full raw')
            intermediate = author_amendments[k][1] if k in author_amendments else first_author[k]
            if number == '008' and k == (89, 53, 41, 'expenses'):
                intermediate = first_author[k]
            _need(_amount(a['finalAuthorSourceValue']) == intermediate, 'Frozen author intermediate history differs')
            if number == '003':
                _need(row['firstRootSourceReading'] == first_peer[k]
                      and row['finalRootSourceReading'] == row['finalAuthorSourceReading'] == value
                      and row['initialAuthorSourceReading'] == first_author[k]
                      and row['finalIndependentSourceReadingsMatch'] is True
                      and row['sourceImageCropSha256'] == target['originalFullRowCropSha256'],
                      'Separate frozen-reader error history differs')
            else:
                _need(row['literalSourceValue'] == row['firstRootImageReading'] == first_peer[k] == value
                      and row['firstAuthorImageReading'] == first_author[k]
                      and row['finalAuthorSourceValue'] == value
                      and row['matchesFrozenFinalAuthorValue'] is True
                      and row['actual600SourceImage'] == target['actual600SourceField'],
                      'Ordered exact-tuple first/current comparison differs')
                if number == '008':
                    _need(row['frozenAuthorChoicesValue'] == intermediate, 'Post-choice intermediate value differs')
                else:
                    _need(row['rootSourceOnlyPacketIndex'] == order, 'Ordered peer tuple index shifted')
        expected_entries.append({'sourceId': SOURCE, 'sourceSha256': SOURCE_SHA, 'physicalPage': k[1],
            'sourceRowOnPage': k[2], 'field': k[3], 'confirmedValue': value,
            'effectiveAuthorOverlay': expected_overlay, 'peerComparison': inputs[0],
            'freshSourceImage': target['actual600SourceField'], 'imageFirstTranscript': inputs[1]})
    if number == '002':
        _empty(comparison, 'unresolvedFields')
        _need(comparison['all12SourceFieldsIndependentlyConfirmed'] is True
              and comparison['personallyReadSourceMoneyFields'] == count
              and comparison['authorFirstReadMatches'] == ledger['originalAuthorFirstReadMatches'] == count - author_errors
              and comparison['rootReadingsUnchanged'] is True and comparison['rootReadingCorrections'] == 0
              and comparison['candidateChangesMadeByPeer'] == 0
              and ledger['notClaimingUnanimityForOriginalAuthorReadings'] is True,
              'Legacy financial totals/role declarations differ')
        for key, value in [('personallyReadSourceMoneyFields', count), ('authorFirstReadMatches', count - author_errors),
                           ('rootReadingCorrections', 0), ('candidateChangesMadeByPeer', 0)]:
            _count(comparison, key, value)
        _count(ledger, 'originalAuthorFirstReadMatches', count - author_errors)
        _need(comparison['all12Actual600DpiFieldImagesIndependentlyReproducedExactly'] is True,
              'Legacy source image proof declaration differs')
    else:
        _need(ledger['originalAuthorOwnSourceCorrections'] == author_errors
              and type(ledger['originalAuthorOwnSourceCorrections']) is int
              and ledger['originalPeerOwnSourceCorrections'] == peer_errors
              and type(ledger['originalPeerOwnSourceCorrections']) is int, 'Declared first-reading error counts differ')
        if number == '003':
            _need(comparison['all38FinalSourceValuesConfirmed'] is True
                  and comparison['authorOwnFirstReadingCorrections'] == author_errors
                  and comparison['rootOwnFirstReadingCorrections'] == peer_errors
                  and peer['personallySourceReadFields'] == count
                  and peer['allRequestedFieldsReadBeforeAuthorOrOcrChoices'] is True,
                  'Separate-reader scope declarations differ')
            _count(comparison, 'authorOwnFirstReadingCorrections', author_errors)
            _count(comparison, 'rootOwnFirstReadingCorrections', peer_errors)
            _count(peer, 'personallySourceReadFields', count)
        else:
            _empty(comparison, 'unresolvedFields')
            _need(comparison[f'all{count}FinalLiteralValuesMatch'] is True
                  and comparison['rootOwnCorrections'] == peer_errors
                  and comparison['authorOwnCorrectionCount'] == author_errors,
                  'Ordered comparison coverage/error declarations differ')
            _count(comparison, 'rootOwnCorrections', peer_errors)
            _count(comparison, 'authorOwnCorrectionCount', author_errors)
            if number == '008':
                _need(peer['all14PersonallyReadFromActual600SourceViews'] is True,
                      'Ordered peer personal source scope differs')
            else:
                _count(peer, 'personallyReadActual600SourceMoneyFields', count)
    for entry in ledger['confirmations']:
        _entry_shape(entry)
    _need(ledger['confirmations'] == expected_entries, 'Whole confirmation ledger differs from independent source replay')
    _source_pixels(targets, natives, originals, load)
    return expected_entries


def _entry_shape(expected):
    _need(isinstance(expected, dict) and set(expected) == {'sourceId', 'sourceSha256', 'physicalPage', 'sourceRowOnPage', 'field',
                           'confirmedValue', 'effectiveAuthorOverlay', 'peerComparison',
                           'freshSourceImage', 'imageFirstTranscript'}, 'Unexpected confirmation authority/fields')
    _need((expected['sourceId'], expected['sourceSha256']) == (SOURCE, SOURCE_SHA)
          and _positive(expected['physicalPage']) and _positive(expected['sourceRowOnPage'])
          and expected['field'] in _MONEY, 'Confirmation source field identity differs')
    _amount(expected['confirmedValue'])
    for key in ['effectiveAuthorOverlay', 'peerComparison', 'imageFirstTranscript']:
        _reference(expected[key])
    _reference(expected['freshSourceImage'], image=True)


def verify(confirmation, source_id, source_sha, load):
    """Check one flat confirmation and its entire supported original ledger."""
    _need((source_id, source_sha) == (SOURCE, SOURCE_SHA), 'Unsupported ordered monetary original')
    _need(isinstance(confirmation, dict) and 'confirmationLedger' in confirmation,
          'Expected flat confirmation plus confirmationLedger')
    ref = _reference(confirmation['confirmationLedger'])
    _need(ref['sha256'] in CONFIG, 'Unknown frozen ordered-peer ledger SHA')
    profile = CONFIG[ref['sha256']]
    _need(ref['path'] == PREFIX + f'phsa/triangulation/money-peer-confirmations-{profile[0]}.json',
          'Ordered ledger path/hash scope differs')
    expected = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
    _entry_shape(expected)
    ledger = load(ref)
    signature = _fingerprint(ledger)
    cached = _CACHE.get(ref['sha256'])
    if cached is None or cached[0] is not load:
        entries = _replay(ledger, profile, load)
        _CACHE[ref['sha256']] = (load, signature, entries)
    else:
        _need(cached[1] == signature, 'Previously checked immutable ledger changed')
        entries = cached[2]
    _need(entries.count(expected) == 1, 'Supplied confirmation is not one exact independently replayed field')
