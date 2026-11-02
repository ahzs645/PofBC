#!/usr/bin/env python3
"""Independent replay of four frozen tuple-money peer formats for v7.

No producer/replay modules are imported. The public input is an ORIGINAL
confirmation member plus its exact confirmationLedger pin. Rebases belong to
the caller. Values come from frozen first reads and explicit amendments;
source flags alone never establish a value or an image correspondence.
"""
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path

SOURCE = 'phsa-2019-20'
PDF_SHA = '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02'
BASE = 'research/salaries/queue-completion-2026-11-01/phsa/triangulation/'
SPECS = {
    'deba98fe20ef290dcfb90de021123c8ee2b36134fd85382ec9e33fe8b3422c31': ('009', '009', 51, 50, 7, 5),
    'f21bb7b9d9d4e8016ff503562594667f32534047668db119da43168af198c572': ('013', '011', 44, 44, 2, 1),
    'c090f1011cc772ddd01604ba4dcb1d48e6cf2bd0aa8849e26012568096edca0d': ('015', '010', 41, 41, 4, 0),
    '94405abc9cb349a597854d1fa6b50d95dd30655996894d2d71e4484b55900ee0': ('018', '013', 40, 40, 5, 0),
}
_CACHE = {}
_AUDIT = {}


def _fail(message):
    raise ValueError('Tuple-money replay: ' + message)


def _require(condition, message):
    if not condition:
        _fail(message)


def _integer(value):
    return type(value) is int and value > 0


def _money(value, null_allowed=False):
    if value is None and null_allowed:
        return None
    _require(_integer(value), 'amount must be a literal positive integer, never bool/float/string/null/zero')
    return value


def _pin(reference):
    _require(isinstance(reference, dict), 'missing byte pin')
    path, sha = reference.get('path'), reference.get('sha256')
    _require(isinstance(path, str) and path and '\\' not in path and '..' not in Path(path).parts,
             'invalid pinned path')
    _require(isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha) is not None, 'invalid SHA256')
    return {'path': path, 'sha256': sha}


def _bytes(reference, load):
    ref = _pin(reference)
    value = load(ref, False)
    _require(isinstance(value, bytes), 'loader must return exact bytes')
    _require(hashlib.sha256(value).hexdigest() == ref['sha256'], 'referenced bytes changed: ' + ref['path'])
    return value


def _no_duplicate_json(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'duplicate JSON member')
        result[key] = value
    return result


def _document(reference, load):
    value = json.loads(_bytes(reference, load), object_pairs_hook=_no_duplicate_json)
    _require(isinstance(value, dict), 'receipt must be a JSON object')
    return value


def _same(left, right):
    return json.dumps(left, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(
        right, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _identity(doc, batch):
    _require(doc.get('sourceId') == SOURCE and doc.get('sourceSha256') == PDF_SHA,
             'foreign source identity')
    _require(doc.get('batch') == batch, 'foreign original batch')


def _key(row):
    p, r, f = row.get('physicalPage'), row.get('sourceRowOnPage'), row.get('field')
    _require(_integer(p) and _integer(r) and f in ('remuneration', 'expenses'), 'invalid physical money tuple')
    return p, r, f


def _rows(rows):
    _require(isinstance(rows, list) and rows, 'missing exact row scope')
    result = {}
    sequences = set()
    for row in rows:
        _require(isinstance(row, dict), 'row must be an object')
        key = _key(row)
        sequence = row.get('sequence')
        _require(_integer(sequence), 'invalid original sequence')
        _require(key not in result and (sequence, key[2]) not in sequences, 'duplicate physical/sequence field tuple')
        result[key] = row
        sequences.add((sequence, key[2]))
    return result


def _scope(left, right, label):
    _require(set(left) == set(right), label + ' does not cover the exact frozen tuple set')
    for key in left:
        _require(left[key]['sequence'] == right[key]['sequence'], label + ' changes original sequence')


def _crop(row):
    if 'originalFullRowCrop' in row:
        return _pin(row['originalFullRowCrop'])['sha256']
    value = row.get('originalFullRowCropSha256', row.get('cropSha256'))
    _require(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None,
             'missing original full-row crop hash')
    return value


def _empty(value):
    return value == [] or (type(value) is int and value == 0)


def _raw_author(raw_ref, batch, targets, view_rows, review, load, mode):
    data = _bytes(raw_ref, load)
    result = {}
    wanted = {(row['sequence'], key[2]): key for key, row in targets.items()}
    if mode == '015':
        reader = csv.DictReader(io.StringIO(data.decode('utf-8')), delimiter='\t')
        _require(reader.fieldnames == ['sequence', 'nameLiteral', 'remunerationLiteral', 'expensesLiteral'],
                 'unexpected sparse TSV schema')
        for row in reader:
            _require(set(row) == set(reader.fieldnames) and all(value is not None for value in row.values()),
                     'malformed sparse TSV event')
            seq_text = row['sequence']
            _require(re.fullmatch('[1-9][0-9]*', seq_text or '') is not None, 'invalid TSV sequence')
            seq = int(seq_text)
            for field, column in [('remuneration', 'remunerationLiteral'), ('expenses', 'expensesLiteral')]:
                text = row[column]
                if text == '' or (seq, field) not in wanted:
                    continue
                key = wanted[(seq, field)]
                _require(key not in result, 'duplicate sparse TSV target event')
                _require(re.fullmatch('[1-9][0-9]*', text) is not None, 'nonliteral target TSV amount')
                result[key] = int(text)
        freeze = _document(review['imageFirstTranscriptFreeze'], load)
        _identity(freeze, batch)
        _require(freeze.get('frozen') is True and freeze.get('fullCandidateAndEngineAlternativesNotOpenedBeforeFreeze') is True,
                 'TSV source-first freeze is not explicit')
        _require(_pin(freeze['imageFirstRawTranscript']) == _pin(raw_ref), 'TSV freeze pins another raw')
    else:
        raw = json.loads(data, object_pairs_hook=_no_duplicate_json)
        if mode == '013':
            # This exact frozen raw predates a batch header. Its byte pin,
            # source identity and exact native target-manifest SHA bind the
            # original batch; do not invent a missing batch value.
            _require(raw.get('sourceId') == SOURCE and raw.get('sourceSha256') == PDF_SHA
                     and 'batch' not in raw
                     and raw.get('sourceOnlyTargetViewsSha256') == review['nativeFieldViewManifest']['sha256'],
                     'legacy author raw source/target-manifest binding differs')
        else:
            _identity(raw, batch)
        _require(raw.get('frozen') is True, 'author raw is not frozen')
        blind_key = 'fullBatchCandidateOpened' if mode == '013' else 'candidateOpenedBeforeFreeze'
        _require(raw.get(blind_key) is False, 'author raw precomparison timing is not explicit')
        if mode == '013':
            readings = raw['readings']
            _require(isinstance(readings, dict), 'author readings map is missing')
            for (seq, field), key in wanted.items():
                _require(str(seq) in readings and field in readings[str(seq)], 'missing author first field')
                result[key] = _money(readings[str(seq)][field])
        else:
            values_name = 'literalValues' if mode == '009' else 'imageFirstValues'
            entries_name = 'transcript' if mode == '009' else 'rows'
            seen = set()
            for row in raw[entries_name]:
                seq = row['sequence']
                _require(_integer(seq), 'invalid raw source sequence')
                for field, value in row[values_name].items():
                    if (seq, field) not in wanted:
                        continue
                    key = wanted[(seq, field)]
                    _require(key not in seen, 'duplicate author first tuple')
                    seen.add(key)
                    _require((row['physicalPage'], row['sourceRowOnPage']) == key[:2], 'author raw physical tuple changed')
                    _require(field in row['reviewTargetFields'] and len(row['reviewTargetFields']) == len(set(row['reviewTargetFields'])),
                             'raw field not explicitly requested')
                    crop = row.get('cropSha256', row.get('sourceCropSha256'))
                    _require(crop == view_rows[key[:2]]['cropSha256'], 'raw author crop differs')
                    result[key] = _money(value, key == (61, 41, 'expenses') and mode == '009')
    _require(set(result) == set(targets), 'author raw missing/extra target tuple')
    return result


def _amend_peer(raw_values, amendment, raw_ref, targets, batch, load):
    _identity(amendment, batch)
    _require(_pin(amendment['originalFrozenImageFirstTranscript']) == _pin(raw_ref), 'peer patch pins another first raw')
    changes = _rows(amendment['changes'])
    values = dict(raw_values)
    for key, change in changes.items():
        _require(key in targets and change['sequence'] == targets[key]['sequence'], 'peer correction widens tuple scope')
        _require(_same(change['firstPeerSourceValue'], raw_values[key]), 'peer patch first value does not equal frozen raw')
        value = _money(change['finalSourceValue'])
        _require(value != raw_values[key], 'peer patch is not an actual correction')
        _require(isinstance(change.get('basis'), str) and change['basis'], 'peer correction lacks source basis')
        values[key] = value
        for item in change.values():
            if isinstance(item, dict) and 'path' in item and 'sha256' in item:
                _bytes(item, load)
    if 'ownFirstReadingCorrections' in amendment:
        _require(type(amendment['ownFirstReadingCorrections']) is int and amendment['ownFirstReadingCorrections'] == len(changes),
                 'peer correction count differs')
    if 'numericUncertaintyQualified' in amendment:
        _require(amendment['numericUncertaintyQualified'] is False, 'numeric uncertainty is not permitted')
    return values, changes


def _image(ref, load):
    from PIL import Image
    with Image.open(io.BytesIO(_bytes(ref, load))) as image:
        if image.mode == 'RGB':
            return image.copy()
        # Compare the visible paper-background image, never unpainted RGB
        # channels hidden underneath an alpha mask.
        rgba = image.convert('RGBA')
        paper = Image.new('RGBA', rgba.size, (255, 255, 255, 255))
        return Image.alpha_composite(paper, rgba).convert('RGB')


def _box(value):
    _require(isinstance(value, list) and len(value) == 4 and all(type(v) is int and v >= 0 for v in value),
             'invalid original integer-pixel crop')
    _require(value[0] < value[2] and value[1] < value[3], 'empty source crop')
    return value


def _pixels(targets, fresh_refs, native_rows, image_rows, load):
    """Reproduce all native300 fields/full rows and declared fresh renders.

    Fresh fields can be partial PDF renders. A passing partial-render check is
    never called a whole-page crop match; byte pins and RGB parity are distinct.
    """
    import fitz
    from PIL import Image
    source = Path('/tmp/queue-completion-phsa/originals') / (SOURCE + '.pdf')
    data = source.read_bytes()
    _require(hashlib.sha256(data).hexdigest() == PDF_SHA, 'original PDF bytes changed')
    doc = fitz.open(stream=data, filetype='pdf')
    current_page = None
    page300 = page600 = None
    counts = {'native300RgbExact': 0, 'oldFullRow300RgbExact': 0,
              'freshWhole600RgbExact': 0, 'freshDeclaredClipRgbExact': 0}
    try:
        for key in sorted(targets):
            pn, rn, field = key
            _require(pn <= len(doc), 'physical PDF page outside original')
            if current_page != pn:
                page300 = page600 = None
                pix = doc[pn - 1].get_pixmap(dpi=300, colorspace=fitz.csRGB, alpha=False)
                page300 = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                current_page = pn
            native = native_rows[key]
            box = _box(native['originalPdf300DpiPixelBox'])
            actual = page300.crop(box)
            supplied = _image(native, load)
            _require(actual.size == supplied.size and actual.tobytes() == supplied.tobytes(), 'actual native300 field differs')
            counts['native300RgbExact'] += 1
            old = image_rows[key[:2]]
            old_box = _box(old['cropRectOriginal300DpiPixels'])
            actual = page300.crop(old_box)
            supplied = _image({'path': old['cropPath'], 'sha256': old['cropSha256']}, load)
            _require(actual.size == supplied.size and actual.tobytes() == supplied.tobytes(), 'actual original full-row crop differs')
            counts['oldFullRow300RgbExact'] += 1
            fresh, dpi, point_clip = fresh_refs[key]
            supplied = _image(fresh, load)
            matched = False
            if dpi == 600:
                if page600 is None:
                    pix = doc[pn - 1].get_pixmap(dpi=600, colorspace=fitz.csRGB, alpha=False)
                    page600 = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                actual = page600.crop([v * 2 for v in box])
                if actual.size == supplied.size and actual.tobytes() == supplied.tobytes():
                    matched = True
                    counts['freshWhole600RgbExact'] += 1
            if not matched:
                clip = point_clip if point_clip is not None else [v * 72 / 300 for v in box]
                _require(len(clip) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in clip), 'invalid PDF clip geometry')
                pix = doc[pn - 1].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, clip=fitz.Rect(*clip))
                actual = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                _require(actual.size == supplied.size and actual.tobytes() == supplied.tobytes(),
                         'declared fresh PDF render does not reproduce exact RGB')
                counts['freshDeclaredClipRgbExact'] += 1
    finally:
        doc.close()
    return counts


def _reconstruct(spec, ledger_ref, load):
    mode, batch_number, target_count, positive_count, peer_count, author_count = spec
    batch = SOURCE + '-' + batch_number
    ledger = _document(ledger_ref, load)
    schema = ('image-first-literal-tuple-peer-with-additive-source-rereads-v1' if mode == '018'
              else 'two-independent-source-money-readers-with-additive-rereads-v1')
    _require(ledger.get('frozen') is True and ledger.get('adapter') == 'count-independent-source-money-peer-v1'
             and ledger.get('sourceReceiptSchema') == schema, 'unknown frozen ledger format')
    inputs = ledger['peerInputs']
    _require(isinstance(inputs, list) and inputs and len({_pin(r)['path'] for r in inputs}) == len(inputs), 'duplicate/missing exact peer input')
    # Independently verify every producer-declared input byte pin; derive the
    # financial matrix below from raw records, never from these confirmations.
    for ref in inputs:
        _bytes(ref, load)
    final_ref = _pin(inputs[0])
    final = _document(final_ref, load)
    _identity(final, batch)
    _require(final.get('receiptSchema') == schema and final.get('allFinalSourceValuesMatchExactly') is True
             and final.get('unresolvedFields') == [], 'final peer has an open/foreign format')
    source_ref = final['sourceOnlyPacket']
    source = _document(source_ref, load)
    _identity(source, batch)
    targets = _rows(source['rows'])
    _require(len(targets) == target_count and source.get('frozen') is True, 'frozen target scope differs')
    for row in targets.values():
        _require(not any(k in row for k in ('literalSourceValue', 'literalImageValue', 'confirmedValue', 'ownFrozenLiteral')),
                 'source-only packet contains choices')
    peer_ref = final['independentImageFirstTranscript']
    peer = _document(peer_ref, load)
    _identity(peer, batch)
    _require(_pin(peer['sourceOnlyPacket']) == _pin(source_ref), 'peer raw pins another target packet')
    if mode == '009':
        _require(peer.get('authorChoicesOpened') is False and peer.get('readFromActualOriginal1200DpiViewsBeforeAnyAuthorOrMachineChoices') is True,
                 'peer source-first timing not explicit')
    elif mode == '018':
        _require(peer.get('correspondingChoicesOpened') is False, 'peer choices were opened before raw freeze')
    else:
        _require(peer.get('frozenBeforeAuthorOrOcrChoices') is True and peer.get('fullBatchCandidateOpened') is False,
                 'peer source-first timing not explicit')
    first_rows = _rows(peer['rows'])
    _scope(first_rows, targets, 'peer frozen raw')
    first_values = {}
    for key, row in first_rows.items():
        _require(_crop(row) == _crop(targets[key]), 'peer raw crop differs from target')
        uncertainty = row.get('realUncertainty', row.get('sourceUncertainty'))
        _require(uncertainty is None, 'unresolved numeric source uncertainty')
        value = row['literalImageValue'] if mode == '018' else row['literalSourceValue']
        nullable = mode == '009' and key == (61, 41, 'expenses')
        first_values[key] = _money(value, nullable)
        if mode == '009':
            _require(row.get('literalDash') is (value is None), 'source dash/null route differs')
    amendment_ref = final['peerOwnAdditiveSourceCorrections']
    amendment = _document(amendment_ref, load)
    peer_values, peer_changes = _amend_peer(first_values, amendment, peer_ref, targets, batch, load)
    _require(len(peer_changes) == peer_count, 'wrong exact number of peer source amendments')
    # The original author overlay is a separate byte-pinned scope/value witness.
    confirmations = ledger['confirmations']
    _require(isinstance(confirmations, list) and len(confirmations) == positive_count, 'ledger positive count differs')
    refs = [_pin(row['effectiveAuthorOverlay']) for row in confirmations]
    _require(all(ref == refs[0] for ref in refs), 'ledger mixes original author overlays')
    overlay_ref = refs[0]
    overlay = _document(overlay_ref, load)
    _identity(overlay, batch)
    review = _document(overlay['reviewInput'], load)
    _identity(review, batch)
    _require(_empty(review.get('unresolvedRows')), 'author review remains unresolved')
    author_ref = final['authorOriginalFrozenTranscript']
    _require({'path': review['rawTranscriptPath'], 'sha256': review['rawTranscriptSha256']} == _pin(author_ref),
             'overlay review pins a different author first raw')
    image_manifest = _document(overlay['imageManifest'], load)
    _identity(image_manifest, batch)
    image_rows = {}
    for row in image_manifest['rows']:
        key = row['physicalPage'], row['sourceRowOnPage']
        _require(all(_integer(v) for v in key) and key not in image_rows, 'duplicate original image row')
        image_rows[key] = row
    view_key = {'009': 'nativeFieldCompanion', '013': 'nativeFieldViewManifest',
                '015': 'additionalNativeFieldViewManifest', '018': 'nativeFieldCompanion'}[mode]
    views = _document(review[view_key], load)
    _identity(views, batch)
    _require(_pin(views['originalImageManifest']) == _pin(overlay['imageManifest']), 'native manifest binds another image scope')
    view_rows = {}
    native_rows = {}
    for row in views['rows']:
        key = row['physicalPage'], row['sourceRowOnPage']
        _require(key not in view_rows, 'duplicate native source row')
        view_rows[key] = row
        for field in row['sourceNativeTargetViews']:
            if field['field'] in ('remuneration', 'expenses'):
                fk = key + (field['field'],)
                _require(fk not in native_rows, 'duplicate native field')
                native_rows[fk] = field
    for key, row in targets.items():
        _require(key[:2] in image_rows and key in native_rows, 'target absent from original image scope')
        original = image_rows[key[:2]]
        _require(row['sequence'] == original['sequence'] == view_rows[key[:2]]['sequence'], 'target original sequence changed')
        _require(key[2] in original['reviewTargetFields'] and _crop(row) == original['cropSha256'] == view_rows[key[:2]]['cropSha256'],
                 'target requested field or crop differs')
    initial_author = _raw_author(author_ref, batch, targets, view_rows, review, load, mode)
    choices_ref = final['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze']
    choices = _document(choices_ref, load)
    # Mode009 historical author scope predates the sourceId header but carries
    # the exact source SHA and original batch. No missing-value default is used.
    _require(choices.get('sourceSha256') == PDF_SHA and choices.get('batch') == batch,
             'scoped author choices identify another source')
    if 'sourceId' in choices:
        _require(choices['sourceId'] == SOURCE, 'foreign scoped author source')
    choice_rows = _rows(choices['rows'])
    _scope(choice_rows, targets, 'scoped author choices')
    if mode == '009':
        _require(_pin(choices['originalFirstTranscript']) == _pin(author_ref),
                 'author reread pins another first transcript')
    elif mode == '013':
        _require(choices.get('originalChoicesFrozenBeforePeerRead') is True
                 and choices.get('peerRawValuesNotOpenedBeforeThisAggregate') is True
                 and _pin(choices['original624SourceFirstTranscript']) == _pin(author_ref)
                 and _pin(choices['sourceOnlyPacket']) == _pin(source_ref),
                 'scoped author pre-peer timing/source pins differ')
    elif mode == '015':
        _require(choices.get('peerValuesNotOpenedBeforeThisFreeze') is True
                 and _pin(choices['ownImageFirstRaw']) == _pin(author_ref)
                 and _pin(choices['sourceOnlyPacket']) == _pin(source_ref),
                 'scoped TSV author source-first pins differ')
    else:
        _require(_pin(choices['freshSourceFirstRaw']) == _pin(peer_ref),
                 'scoped author choices do not follow the exact peer freeze')
    intermediate = {}
    for key, row in choice_rows.items():
        _require(_crop(row) == _crop(targets[key]), 'author choices crop changed')
        if mode == '009':
            first, now = row['initialImageFirstValue'], row['currentActual1200SourceReading']
        elif mode == '013':
            first, now = row['initialImageFirstValue'], row['finalAuthorSourceValue']
        elif mode == '015':
            first = now = row['ownFrozenLiteral']
            _require(row.get('sameAsImageFirstRaw') is True, 'author TSV relation is not explicit')
        else:
            first, now = row['firstFrozenLiteralAmount'], row['currentLiteralSourceAmount']
        _require(_same(first, initial_author[key]), 'scoped author first differs from raw')
        intermediate[key] = _money(now, mode == '009' and key == (61, 41, 'expenses'))
    author_values = dict(intermediate)
    if mode == '009':
        amendment_author = _document(final['authorRejectedSecondarySourceReading'], load)
        _identity(amendment_author, batch)
        key = _key(amendment_author)
        _require(key in targets and amendment_author['sequence'] == targets[key]['sequence'], 'author restoration widens scope')
        _require(_same(amendment_author['originalBlindFirstReading'], initial_author[key])
                 and _same(amendment_author['intermediateOwnSecondSourceReading'], intermediate[key]), 'restoration history does not replay')
        _require(_pin(amendment_author['originalFirstTranscript']) == _pin(author_ref)
                 and _pin(amendment_author['ownIntermediateSourceReread']) == _pin(choices_ref)
                 and _pin(amendment_author['freshPeerSourceFirstBeforeChoices']) == _pin(peer_ref),
                 'restoration pins another history')
        author_values[key] = _money(amendment_author['finalCurrentOriginalSourceReading'])
        _require(author_values[key] == initial_author[key] and author_values[key] != intermediate[key]
                 and amendment_author.get('originalDataValueUnchanged') is True, 'rejected secondary did not restore raw')
    elif mode == '013':
        amendment_author = _document(final['authorOwnAdditiveSourceCorrections'], load)
        _identity(amendment_author, batch)
        key = _key(amendment_author)
        _require(key in targets and amendment_author['sequence'] == targets[key]['sequence'], 'author correction widens scope')
        _require(amendment_author['cropSha256'] == _crop(targets[key]), 'author correction crop differs')
        _require(_same(amendment_author['firstRootImageReading'], initial_author[key])
                 and _pin(amendment_author['original624ImageFirstRaw']) == _pin(author_ref)
                 and _pin(amendment_author['originalScoped44AuthorChoices']) == _pin(choices_ref)
                 and _pin(amendment_author['independentFresh44FirstSourcePeer']) == _pin(peer_ref),
                 'author correction history differs')
        author_values[key] = _money(amendment_author['finalLiteralSourceReading'])
        _require(author_values[key] != initial_author[key], 'author amendment is not a correction')
    elif mode == '018':
        earlier = _document(choices['ownEarlierFrozenFortySourceRereads'], load)
        _identity(earlier, batch)
        _require(earlier.get('beforeFreshPeerChoicesOpened') is True, 'author reread timing differs')
        _require(_pin(earlier['rawImageFirstTranscript']) == _pin(author_ref)
                 and _pin(earlier['sourceOnlyPacket']) == _pin(source_ref),
                 'earlier author source reread pins differ')
        earlier_rows = _rows(earlier['rows'])
        _scope(earlier_rows, targets, 'author earlier source reread')
        for key, row in earlier_rows.items():
            _require(_same(row['firstFrozenValue'], initial_author[key])
                     and _same(row['currentOriginal1200LiteralValue'], author_values[key]), 'author earlier reread value differs')
    _require(sum(not _same(author_values[k], initial_author[k]) for k in targets) == author_count,
             'author first-to-final source correction count differs')
    rejected_secondary = 1 if mode == '009' else 0
    if mode != '018':
        _require(type(final.get('authorRejectedSecondaryReadings')) is int
                 and final['authorRejectedSecondaryReadings'] == rejected_secondary,
                 'rejected author-secondary history count differs')
    final_rows = _rows(final['rows'])
    _scope(final_rows, targets, 'final human peer')
    overlay_rows = {}
    for row in overlay['overlays']:
        key = row['physicalPage'], row['sourceRowOnPage']
        _require(key not in overlay_rows, 'duplicate author overlay row')
        overlay_rows[key] = row
    fresh_refs = {}
    expected = {}
    nulls = []
    image_fields = {'009': ('actual1200SourceField', 'actual1200OriginalField', 1200),
                    '013': ('actual600SourceField', 'actual600SourceField', 600),
                    '015': ('actual600OriginalField', 'actual600OriginalField', 600),
                    '018': ('actual1200SourceField', 'actual1200OriginalField', 1200)}
    target_image_key, final_image_key, dpi = image_fields[mode]
    for key, row in targets.items():
        peer_row = final_rows[key]
        _require(_crop(peer_row) == _crop(row), 'final peer crop differs')
        for field, value in [('firstPeerSourceValue', first_values[key]), ('finalPeerSourceValue', peer_values[key]),
                             ('initialAuthorSourceValue', initial_author[key]), ('intermediateAuthorSourceValue', intermediate[key]),
                             ('finalAuthorSourceValue', author_values[key])]:
            _require(_same(peer_row[field], value), 'final human history is not independently replayable: ' + field)
        _require(_same(peer_values[key], author_values[key]) and peer_row.get('finalIndependentSourceValuesMatchExactly') is True,
                 'independent final source values disagree')
        value = author_values[key]
        overlay_row = overlay_rows.get(key[:2])
        _require(overlay_row is not None and key[2] in overlay_row['reviewedFields']
                 and overlay_row['cropSha256'] == _crop(row), 'author overlay tuple/crop scope differs')
        resolved = overlay_row['resolvedRow']
        _require(len(resolved) == 6 and type(resolved[5]) is int and resolved[5] == key[0]
                 and _same(resolved[3 if key[2] == 'remuneration' else 4], value), 'author effective overlay literal differs')
        fresh = row[target_image_key]
        _require(_same(peer_row[final_image_key], fresh), 'final peer uses another target image')
        raw_image_key = {'009': 'actualSource1200OriginalView', '013': 'actual600OriginalField',
                         '015': 'actual600OriginalField', '018': 'actual1200SourceField'}[mode]
        _require(_same(first_rows[key][raw_image_key], fresh), 'frozen peer first read uses another source image')
        native_key = {'009': 'nativeSourceField', '013': 'sourceNative300',
                      '018': 'native300SourceField'}.get(mode)
        if native_key is not None:
            _require(_same(row[native_key], native_rows[key]), 'target native image/geometry differs from original field')
        # A native300 exact crop is independently reconstructed for every tuple.
        fresh_refs[key] = (fresh, dpi, row.get('actual600PdfClip'))
        if value is None:
            _require(mode == '009' and key == (61, 41, 'expenses') and peer_row.get('literalDashNullConfirmed') is True
                     and peer_row.get('eligibleForPositiveMoneyConfirmation') is False, 'null is not the separately declared printed dash')
            nulls.append({'physicalPage': key[0], 'sourceRowOnPage': key[1], 'field': key[2], 'value': None,
                          'freshSourceImage': fresh, 'originalFullRowCropSha256': _crop(row),
                          'route': 'Separately image-confirmed explicit source dash; excluded from positive-money confirmations.'})
            continue
        _money(value)
        _require(peer_row.get('eligibleForPositiveMoneyConfirmation') is True and peer_row.get('literalDashNullConfirmed') is False,
                 'positive confirmation eligibility contradicts literal type')
        expected[key] = {'sourceId': SOURCE, 'sourceSha256': PDF_SHA, 'physicalPage': key[0], 'sourceRowOnPage': key[1],
                         'field': key[2], 'confirmedValue': value, 'effectiveAuthorOverlay': overlay_ref,
                         'peerComparison': final_ref, 'freshSourceImage': fresh, 'imageFirstTranscript': _pin(peer_ref)}
    _require(len(expected) == positive_count, 'reconstructed positive scope differs')
    for row in confirmations:
        _require(_key(row) in targets, 'confirmation adds an unrequested source tuple')
    actual = _rows([{**row, 'sequence': targets[_key(row)]['sequence']} for row in confirmations])
    _require(set(actual) == set(expected), 'confirmation ledger omits/widens source tuples')
    for key, row in actual.items():
        row = dict(row); row.pop('sequence')
        _require(_same(row, expected[key]), 'producer confirmation differs from independently reconstructed source history')
    for doc, fields in [(final, {'fieldsPersonallyReadBeforeAuthorChoices': target_count,
                                 'positiveMonetaryFieldsConfirmed': positive_count, 'literalDashNullFieldsConfirmedSeparately': len(nulls),
                                 'peerOwnFirstReadingCorrections': peer_count, 'authorOwnFirstReadingCorrections': author_count}),
                        (ledger, {'completeFrozenSourceTargetFields': target_count, 'confirmedMonetaryFields': positive_count,
                                  'originalPeerOwnSourceCorrections': peer_count, 'originalAuthorOwnSourceCorrections': author_count})]:
        for field, value in fields.items():
            _require(type(doc.get(field)) is int and doc[field] == value, 'literal count differs: ' + field)
    _require(_same(ledger.get('literalSourceDashFieldsConfirmedSeparately', []), nulls), 'separate dash ledger differs')
    proof = _document(final['independentSourcePixelProof'], load)
    _identity(proof, batch)
    _require(_pin(proof['sourceOnlyPacket']) == _pin(source_ref), 'pixel proof binds another source packet')
    if 'authorValuesOpened' in proof:
        _require(proof['authorValuesOpened'] is False, 'source fidelity preceded an inconsistent author-choice state')
    _scope(_rows(proof['rows']), targets, 'independent image proof')
    required_inputs = [final_ref, peer_ref, source_ref, final['independentSourcePixelProof'],
                       amendment_ref, choices_ref, author_ref]
    if mode == '009':
        required_inputs.append(final['authorRejectedSecondarySourceReading'])
    elif mode == '013':
        required_inputs.extend([review['nativeFieldViewManifest'], final['authorOwnAdditiveSourceCorrections']])
    elif mode == '018':
        required_inputs.append(choices['ownEarlierFrozenFortySourceRereads'])
    as_pair = lambda ref: (_pin(ref)['path'], _pin(ref)['sha256'])
    _require({as_pair(ref) for ref in inputs} == {as_pair(ref) for ref in required_inputs},
             'declared peer inputs do not equal the exact reconstructed dependency set')
    pixels = _pixels(targets, fresh_refs, native_rows, image_rows, load)
    audit = {'sourceTargets': target_count, 'positiveFields': positive_count, 'dashFields': len(nulls),
             'peerCorrections': peer_count, 'authorFirstCorrections': author_count,
             'authorRejectedSecondaryReadings': rejected_secondary, **pixels}
    return {key: json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
            for key, value in expected.items()}, audit


def verify(confirmation, source_id, source_sha, load):
    """Verify one flat ORIGINAL confirmation plus confirmationLedger pin.

    The entire fixed ledger is independently reconstructed once per SHA. Every
    call still enforces the supplied exact source identity, tuple, literal type
    and complete original confirmation member, including image and overlay pins.
    """
    _require(isinstance(confirmation, dict), 'confirmation must be an object')
    ledger = _pin(confirmation.get('confirmationLedger'))
    _require(set(confirmation['confirmationLedger']) == {'path', 'sha256'}, 'ledger pin has extra metadata')
    _require(ledger['sha256'] in SPECS, 'unknown confirmation ledger SHA')
    spec = SPECS[ledger['sha256']]
    _require(ledger['path'] == BASE + 'money-peer-confirmations-' + spec[0] + '.json', 'ledger path does not match sealed SHA')
    _require(source_id == SOURCE and source_sha == PDF_SHA and confirmation.get('sourceId') == source_id
             and confirmation.get('sourceSha256') == source_sha, 'caller/entry original source differs')
    key = _key(confirmation)
    _money(confirmation.get('confirmedValue'))
    if ledger['sha256'] not in _CACHE:
        matrix, audit = _reconstruct(spec, ledger, load)
        _CACHE[ledger['sha256']] = matrix
        _AUDIT[ledger['sha256']] = audit
    entry = {key: value for key, value in confirmation.items() if key != 'confirmationLedger'}
    actual = json.dumps(entry, sort_keys=True, separators=(',', ':'), allow_nan=False)
    _require(key in _CACHE[ledger['sha256']] and actual == _CACHE[ledger['sha256']][key],
             'supplied entry is not the exact independently reconstructed original member')
    return None
