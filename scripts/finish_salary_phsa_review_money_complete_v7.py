"""Independent verification of the two complete-author monetary receipts 011/012.

This reader imports no producer, adapter, dispatcher or other review interpreter.
The two immutable receipt sets partition 51 fields from the same 400-row author
transcript. Their first, secondary and amended readings are reconstructed before
either peer is given authority. Partial high-dpi views are byte-pinned historical
evidence; original-PDF whole-page 300-dpi crops provide the pixel binding.
"""
from collections import Counter
from io import BytesIO
import hashlib
import json
import re


BASE = 'research/salaries/queue-completion-2026-11-01/'
SOURCE = 'phsa-2019-20'
SOURCE_SHA = '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02'
BATCH = 'phsa-2019-20-004'
SCHEMA = 'separate-complete-source-peer-with-author-first-and-secondary-history-v1'
LEDGERS = (
    {'path': BASE + 'phsa/triangulation/money-peer-confirmations-011.json',
     'sha256': 'af8a9fa14b37d7cf567c781b71741a1285ad82c4bedae4c3c3f13c1afeefb069'},
    {'path': BASE + 'phsa/triangulation/money-peer-confirmations-012.json',
     'sha256': '9ff9fc7127ee2820689dfafe96780b904d7cf149d9efe007389d92c4d70d5bce'},
)
MONEY_INDEX = {'remuneration': 3, 'expenses': 4}
_CACHE = {}


def _need(test, message):
    if not test:
        raise ValueError('complete-author monetary evidence: ' + message)


def _positive(value):
    _need(type(value) is int and value > 0, 'literal amount must be a strict positive integer, not bool/zero/null')
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _ref_equal(a, b):
    return _canonical(a) == _canonical(b)


class _Pinned:
    def __init__(self, load):
        self.load = load
        self.cache = {}

    def raw(self, ref):
        _need(isinstance(ref, dict) and isinstance(ref.get('path'), str)
              and isinstance(ref.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', ref['sha256']),
              'malformed immutable reference')
        key = (ref['path'], ref['sha256'])
        if key not in self.cache:
            data = self.load({'path': ref['path'], 'sha256': ref['sha256']}, False)
            _need(isinstance(data, bytes), 'raw loader must return exact bytes')
            _need(hashlib.sha256(data).hexdigest() == ref['sha256'], 'input byte hash differs: ' + ref['path'])
            self.cache[key] = data
        return self.cache[key]

    def json(self, ref):
        return json.loads(self.raw(ref))

    def walk(self, value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
                self.raw(value)
            for item in value.values():
                self.walk(item)
        elif isinstance(value, list):
            for item in value:
                self.walk(item)


def _identity(doc, source_id=True):
    _need(doc.get('sourceSha256') == SOURCE_SHA and doc.get('batch') == BATCH, 'wrong source hash/batch')
    if source_id:
        _need(doc.get('sourceId') == SOURCE, 'wrong source identifier')


def _rows(rows, label, route=None):
    _need(isinstance(rows, list), label + ' rows must be a list')
    result = {}
    for row in rows:
        seq = row.get('sequence')
        _need(type(seq) is int and seq > 0, label + ' sequence must be a positive integer')
        field = row.get('field')
        _need(field in MONEY_INDEX, label + ' scope includes a nonmonetary field')
        key = (seq, field)
        _need(key not in result, label + ' duplicate source field')
        if route is not None:
            _need(seq in route and field in route[seq]['reviewTargetFields'], label + ' field outside original scope')
            original = route[seq]
            for coord in ['physicalPage', 'sourceRowOnPage']:
                if coord in row:
                    _need(type(row[coord]) is int and row[coord] == original[coord], label + ' source coordinates differ')
        result[key] = row
    return result


def _map(rows, value_key, label, route):
    fields = _rows(rows, label, route)
    return {key: _positive(row.get(value_key)) for key, row in fields.items()}


def _source_pixels(read, manifest, targets, keys):
    """Check native field/full-row RGB against independently rendered whole pages."""
    import fitz
    from PIL import Image

    pdf_ref = {'path': manifest['originalPdfCachePath'], 'sha256': SOURCE_SHA}
    data = read.raw(pdf_ref)
    route = {r['sequence']: r for r in manifest['rows']}
    fields = {r['sequence']: r for r in targets['rows']}
    pages = {}

    def same(ref, image):
        with Image.open(BytesIO(read.raw(ref))) as supplied:
            actual = supplied.convert('RGB')
            _need(actual.size == image.size and actual.tobytes() == image.tobytes(),
                  'native300/full-row pixels differ from original PDF')

    with fitz.open(stream=data, filetype='pdf') as document:
        for seq, field in sorted(keys):
            row = route[seq]
            page = row['physicalPage']
            if page not in pages:
                pix = document[page - 1].get_pixmap(dpi=300, alpha=False)
                pages[page] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            image = pages[page]
            row_box = row['cropRectOriginal300DpiPixels']
            _need(len(row_box) == 4 and all(type(x) is int for x in row_box), 'noninteger full-row pixel geometry')
            same({'path': row['cropPath'], 'sha256': row['cropSha256']}, image.crop(row_box))
            matches = [v for v in fields[seq]['sourceNativeTargetViews'] if v['field'] == field]
            _need(len(matches) == 1, 'native field missing/duplicate')
            view = matches[0]
            box = view['originalPdf300DpiPixelBox']
            _need(len(box) == 4 and all(type(x) is int for x in box), 'noninteger native field geometry')
            _need(row_box[0] <= box[0] < box[2] <= row_box[2]
                  and row_box[1] == box[1] < box[3] == row_box[3], 'native field outside source row')
            same(view, image.crop(box))


def _build(read, pixel_check):
    """Reconstruct both immutable concrete schemas without trusting their flags."""
    ledgers = [read.json(ref) for ref in LEDGERS]
    for ledger, count in zip(ledgers, [4, 47]):
        _need(ledger.get('frozen') is True and ledger.get('sourceReceiptSchema') == SCHEMA, 'unknown receipt schema')
        _need(ledger.get('adapter') == 'count-independent-source-money-peer-v1', 'unknown adapter')
        _need(ledger.get('completeFrozenSourceTargetFields') == count
              and ledger.get('confirmedMonetaryFields') == count, 'ledger count differs')
        _need(type(ledger.get('originalAuthorOwnSourceCorrections')) is int
              and ledger['originalAuthorOwnSourceCorrections'] == (3 if count == 4 else 1), 'author correction count differs')
        _need(type(ledger.get('originalPeerOwnSourceCorrections')) is int
              and ledger['originalPeerOwnSourceCorrections'] == 0, 'peer corrections not supported by this schema')
        for ref in ledger['peerInputs']:
            read.walk(read.json(ref))

    four = read.json(ledgers[0]['peerInputs'][0])
    fortyseven = read.json(ledgers[1]['peerInputs'][0])
    for doc in [four, fortyseven]:
        _identity(doc)
    author = read.json(four['authorOriginalImageFirstRaw'])
    secondary = read.json(four['authorOwnSecondarySourceRereads'])
    changes = read.json(four['authorFinalSourceCorrections'])
    late = read.json(fortyseven['authorOnlyPostPeerSourceCorrection'])
    for doc in [author, secondary, changes, late]:
        _identity(doc)
    _need(author.get('frozen') is True and author.get('candidateOpenedBeforeFreeze') is False
          and author.get('authorCandidateAlternativesSeenBeforeFreeze') is False, 'author first-reading chronology missing')
    _need(author.get('all400AssignedRowFieldSetsTranscribed') is True, 'complete-author scope not declared')
    _need(_ref_equal(secondary['rawSourceFirstTranscript'], four['authorOriginalImageFirstRaw'])
          and _ref_equal(changes['original628FieldBlindTranscript'], four['authorOriginalImageFirstRaw'])
          and _ref_equal(changes['ownSecond51FieldMoneyReread'], four['authorOwnSecondarySourceRereads']),
          'first/secondary history references differ')
    manifest = read.json(author['sourceOnlyManifest'])
    targets = read.json(author['nativeFieldViews'])
    _identity(manifest)
    _identity(targets)
    _need(_ref_equal(targets['originalImageManifest'], author['sourceOnlyManifest']), 'native target manifest differs')
    route = {r['sequence']: r for r in manifest['rows']}
    _need(len(route) == len(manifest['rows']) == 400 and set(route) == set(range(1, 401)), 'complete 400-row source routing missing/duplicate')
    _need(len(author['rows']) == 400, 'complete author transcript is not 400 rows')
    raw_route = {r['sequence']: r for r in author['rows']}
    target_route = {r['sequence']: r for r in targets['rows']}
    _need(len(raw_route) == len(target_route) == 400 and set(raw_route) == set(target_route) == set(route),
          'complete source/author/target rows differ')
    counts = Counter()
    first = {}
    for seq, original in route.items():
        raw = raw_route[seq]
        target = target_route[seq]
        _need(type(seq) is int and all(type(original.get(c)) is int and original[c] > 0 for c in ['physicalPage', 'sourceRowOnPage']), 'invalid source row locator')
        scope = original['reviewTargetFields']
        _need(isinstance(scope, list) and len(scope) == len(set(scope)) and set(scope) <= {'name', *MONEY_INDEX}, 'invalid original requested field scope')
        for other in [raw, target]:
            _need(other['physicalPage'] == original['physicalPage'] and other['sourceRowOnPage'] == original['sourceRowOnPage']
                  and other['reviewTargetFields'] == scope, 'author/native source row scope differs')
        _need(raw['sourceCropSha256'] == original['cropSha256'] == target['cropSha256'], 'complete author row crop differs')
        _need(set(raw['imageFirstValues']) == set(scope), 'complete author first fields missing/extra')
        _need({v['field'] for v in target['sourceNativeTargetViews']} == set(scope)
              and len(target['sourceNativeTargetViews']) == len(scope), 'native field set missing/duplicate')
        counts.update(scope)
        for field in scope:
            if field in MONEY_INDEX:
                first[(seq, field)] = _positive(raw['imageFirstValues'][field])
    _need(dict(counts) == author['requestedFieldCounts'] == {'name': 344, 'expenses': 86, 'remuneration': 198}, 'complete author field counts differ')
    second = _map(secondary['rows'], 'secondSourceReading', 'secondary', route)
    baseline = _map(changes['all51FinalMoneyReadings'], 'finalOriginalSourceValue', 'author final51', route)
    _need(len(second) == len(baseline) == 51 and set(second) == set(baseline) <= set(first), 'secondary/final51 scope differs')
    secondary_rows = _rows(secondary['rows'], 'secondary source proof', route)
    for key, row in secondary_rows.items():
        seq, field = key
        proof = row['sourceProof']
        _need(proof['sequence'] == seq and proof['field'] == field
              and proof['physicalPage'] == route[seq]['physicalPage'] and proof['sourceRowOnPage'] == route[seq]['sourceRowOnPage'], 'secondary source proof locator differs')
        native = next(v for v in target_route[seq]['sourceNativeTargetViews'] if v['field'] == field)
        _need(proof['originalRowCropSha256'] == route[seq]['cropSha256']
              and proof['originalFieldViewSha256'] == native['sha256'], 'secondary source proof crop differs')
        _need(proof['actual1200NameOrMoney']['original300DpiPixelBox'] == native['originalPdf300DpiPixelBox'], 'secondary field geometry differs')
        historical = row.get('finiteVisibleAlternatives')
        if historical is not None:
            _need(row.get('provisionalPendingFreshSourcePeer') is True
                  and isinstance(historical, list) and len(historical) == len(set(historical))
                  and all(type(v) is int and v > 0 for v in historical)
                  and set(historical) == {first[key], second[key], baseline[key]},
                  'historical provisional monetary alternatives lack exact first/secondary/final history')

    primary_changes = _rows(changes['ownMonetaryDataCorrections'], 'first-reading source corrections', route)
    secondary_changes = _rows(changes['ownSecondaryProvisionalReadingCorrection'], 'secondary source correction', route)
    _need(len(primary_changes) == 3 and len(secondary_changes) == 1, 'declared correction history differs')
    _need(set(primary_changes) == {k for k in baseline if first[k] != baseline[k]}, 'first-reading disagreements not exactly explained')
    for key, row in primary_changes.items():
        _need(_positive(row['initialBlindValue']) == first[key]
              and _positive(row['finalOriginalSourceValue']) == baseline[key], 'first-reading correction before/after differs')
    _need(set(secondary_changes) == {k for k in baseline if second[k] != baseline[k]}, 'secondary disagreements not exactly explained')
    for key, row in secondary_changes.items():
        _need(_positive(row['firstBlindOriginalValue']) == first[key] == baseline[key]
              and _positive(row['intermediateOwnSecondReadProvisionalValue']) == second[key]
              and _positive(row['finalOriginalSourceValue']) == baseline[key]
              and row.get('originalBlindDataValueUnchanged') is True, 'secondary-only restoration history differs')
        proof = row['sourceProof']
        # This older schema stores a path/hash pair in separately named keys.
        # It is still an input pin, although the final pixel authority is the
        # independent whole-page native300 replay below.
        read.raw({'path': proof['actual2400Path'], 'sha256': proof['actual2400Sha256']})
    _need(changes.get('unresolvedMonetaryFields') == [] and changes.get('moneyQualificationOrImputationAccepted') is False
          and changes.get('noControlsUsedToSelectValues') is True, 'unresolved/qualified monetary evidence')
    late_key = (late['sequence'], late['field'])
    _need(late_key == (310, 'expenses') and late_key in baseline, 'unexpected additional correction scope')
    _need(_positive(late['originalBlindAndPriorOwnRereadValue']) == first[late_key] == second[late_key] == baseline[late_key], 'additional correction prior history differs')
    _need(late.get('ownDataReadingCorrection') is True
          and late['sourceEvidence']['originalFullRowCropSha256'] == route[310]['cropSha256'], 'additional source correction crop differs')
    current = dict(baseline)
    current[late_key] = _positive(late['finalCurrentOriginalSourceValue'])
    expected_all_money = dict(first)
    expected_all_money.update(current)

    raw_peers = [read.json(four['independentImageFirstRaw']), read.json(fortyseven['imageFirstTranscript'])]
    packets = [read.json(raw_peers[0]['sourceOnlyPacket']), read.json(fortyseven['sourceOnlyPacket'])]
    _need(raw_peers[0].get('frozenBeforeAuthorProposalsOrCandidateMoneyValues') is True
          and raw_peers[0].get('candidateOrAuthorValuesOpened') is False, 'four-field peer first chronology differs')
    _need(raw_peers[1].get('authorChoicesUnopenedAtFreeze') is True
          and raw_peers[1].get('candidateUnopenedAtFreeze') is True, '47-field peer first chronology differs')
    _need(_ref_equal(changes['freshFourMoneyPeerSourceFirstRaw'], four['independentImageFirstRaw'])
          and _ref_equal(late['freshIndependent47RawBeforeChoices'], fortyseven['imageFirstTranscript']), 'source correction peer chronology link differs')
    for doc in raw_peers + packets:
        _identity(doc)
    packet_maps = [_rows(p['rows'], 'source-only packet', route) for p in packets]
    raw_peer_maps = [_rows(p['rows'], 'fresh peer raw', route) for p in raw_peers]
    final_peer_maps = [_rows(p['rows'], 'fresh peer comparison', route) for p in [four, fortyseven]]
    scopes = [set(m) for m in packet_maps]
    _need(len(scopes[0]) == 4 and len(scopes[1]) == 47 and not scopes[0] & scopes[1]
          and scopes[0] | scopes[1] == set(current), 'fresh peer scopes do not exactly partition 51 fields')
    open_fields = _rows(secondary['openFieldKeys'], 'secondary open scope', route)
    _need(set(open_fields) == scopes[0], 'four-field peer scope does not match declared open readings')
    for scope, raw_map, final_map in zip(scopes, raw_peer_maps, final_peer_maps):
        _need(scope == set(raw_map) == set(final_map), 'peer source/final field scopes differ')

    overlay_refs = [c['effectiveAuthorOverlay'] for ledger in ledgers for c in ledger['confirmations']]
    _need(overlay_refs and all(_ref_equal(r, overlay_refs[0]) for r in overlay_refs), 'monetary entries use different overlays')
    overlay_ref = overlay_refs[0]
    overlay = read.json(overlay_ref)
    _identity(overlay)
    _need(_ref_equal(overlay['imageManifest'], author['sourceOnlyManifest']), 'overlay original manifest differs')
    overlay_rows = {(r['physicalPage'], r['sourceRowOnPage']): r for r in overlay['overlays']}
    _need(len(overlay_rows) == len(overlay['overlays']) == 400 and overlay['resolvedRows'] == 400, 'overlay complete scope differs')
    for seq, original in route.items():
        key = (original['physicalPage'], original['sourceRowOnPage'])
        _need(key in overlay_rows, 'overlay source row omitted')
        row = overlay_rows[key]
        _need(row['cropSha256'] == original['cropSha256'] and row['reviewedFields'] == original['reviewTargetFields'], 'overlay crop/field scope differs')
        _need(len(row['resolvedRow']) == len(row['rawCandidateRow']) == 6
              and type(row['resolvedRow'][5]) is int and row['resolvedRow'][5] == key[0], 'overlay row shape/page differs')
        for field, index in MONEY_INDEX.items():
            if field in original['reviewTargetFields']:
                _need(_positive(row['resolvedRow'][index]) == expected_all_money[(seq, field)], 'overlay monetary value does not follow complete source correction history')
            else:
                _need(_canonical(row['resolvedRow'][index]) == _canonical(row['rawCandidateRow'][index]), 'unrequested monetary field changed')

    proposals = read.json(fortyseven['authorScopedProposals'])
    _identity(proposals, source_id=False)
    _need(_ref_equal(proposals['releasedOnlyAfterFresh47Raw'], fortyseven['imageFirstTranscript']), 'scoped proposals not linked to frozen first peer')
    proposal_map = _map(proposals['rows'], 'finalOriginalSourceValue', '47-only author proposals', route)
    _need(set(proposal_map) == scopes[1] and all(proposal_map[k] == baseline[k] for k in scopes[1]), '47 scoped author proposals differ from original final51')
    _need({k for k in scopes[1] if proposal_map[k] != current[k]} == {late_key}, 'additional source correction does not exactly explain proposal difference')

    rebuilt = {}
    for i, (ledger, packet_map, raw_map, final_map) in enumerate(zip(ledgers, packet_maps, raw_peer_maps, final_peer_maps)):
        values = []
        for key, packet in packet_map.items():
            seq, field = key
            peer_raw, peer_final = raw_map[key], final_map[key]
            native = next(v for v in target_route[seq]['sourceNativeTargetViews'] if v['field'] == field)
            field_ref = packet.get('original300FieldView', packet.get('nativeSourceField'))
            _need(_ref_equal(field_ref, native), 'source-only native field differs from original target')
            crop = packet['originalFullRowCrop']
            _need(crop['sha256'] == route[seq]['cropSha256'] and crop['original300DpiPixelBox'] == route[seq]['cropRectOriginal300DpiPixels'], 'source-only full-row crop differs')
            _need(packet['actual1200SourceField']['original300DpiPixelBox'] == native['originalPdf300DpiPixelBox'], 'historical partial view geometry differs')
            for row in [peer_raw, peer_final]:
                _need(_ref_equal(row['actual1200SourceField'], packet['actual1200SourceField']), 'peer historical source-image pin differs')
            if i == 0:
                _need(_positive(peer_raw['literalSourceValue']) == current[key]
                      and peer_raw.get('genuineUnresolvedGlyphs') == [], 'four-field peer literal differs/unresolved')
                _need(_positive(peer_final['originalAuthorFirstReading']) == first[key]
                      and _positive(peer_final['freshIndependentFirstSourceReading']) == current[key]
                      and _positive(peer_final['finalLiteralSourceValue']) == current[key]
                      and peer_final['originalAuthorFirstAndFinalMatch'] is (first[key] == current[key]), 'four-field first/current comparison history differs')
                _need(peer_raw['originalFullRowCrop']['sha256'] == route[seq]['cropSha256'], 'four-field raw source crop differs')
            else:
                for row in [peer_raw, peer_final]:
                    literal = row.get('literalSourceAmount')
                    _need(isinstance(literal, str) and re.fullmatch(r'(?:[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', literal), 'source literal has unsupported money separators/digits')
                    _need(int(literal.replace(',', '')) == _positive(row.get('value')) == current[key]
                          and row.get('uncertainty') is None and row['cropSha256'] == route[seq]['cropSha256'], '47-field literal/current/crop differs')
                    _need(_ref_equal(row['sourceNativeField'], native), '47-field native source pin differs')
                _need(_positive(peer_final['authorEffectiveSourceValue']) == current[key]
                      and peer_final.get('exactMatch') is True, '47-field final comparison does not match source')
            values.append({'sourceId': SOURCE, 'sourceSha256': SOURCE_SHA,
                           'physicalPage': route[seq]['physicalPage'], 'sourceRowOnPage': route[seq]['sourceRowOnPage'],
                           'field': field, 'confirmedValue': current[key], 'effectiveAuthorOverlay': overlay_ref,
                           'peerComparison': ledger['peerInputs'][0], 'freshSourceImage': packet['actual1200SourceField'],
                           'imageFirstTranscript': four['independentImageFirstRaw'] if i == 0 else fortyseven['imageFirstTranscript']})
        _need(len(values) == len(ledger['confirmations']), 'ledger confirmation count differs from reconstructed tuples')
        _need(sorted(map(_canonical, values)) == sorted(map(_canonical, ledger['confirmations'])), 'ledger entries differ from exact independently reconstructed peer tuples')
        _need(len(set(map(_canonical, values))) == len(values), 'duplicate ledger confirmation')
        rebuilt[LEDGERS[i]['sha256']] = tuple(values)
    _need(four.get('independentReviewerOwnCorrections') == 0 and four.get('unresolvedFields') == 0
          and four.get('originalAuthorFirstReadingsMatchingFinal') == 1 and four.get('originalAuthorFirstReadingsSourceCorrected') == 3,
          'four-field correction summary differs')
    _need(fortyseven.get('peerCorrections') == [] and fortyseven.get('unresolvedFields') == []
          and fortyseven.get('authorCorrectionCount') == 1 and raw_peers[1].get('ownCorrections') == [], '47-field correction summary differs')
    read.walk(author)
    read.walk(secondary)
    read.walk(changes)
    read.walk(late)
    for packet in packets:
        read.walk(packet)
    pixel_check(read, manifest, targets, set(current))
    return rebuilt


def verify(confirmation, source_id, source_sha, load):
    """Verify one exact original-ledger member, rebuilding the full bundle once."""
    _need(source_id == SOURCE and source_sha == SOURCE_SHA, 'unsupported source identity/hash')
    _need(isinstance(confirmation, dict), 'confirmation must be an object')
    reference = confirmation.get('confirmationLedger')
    _need(any(_ref_equal(reference, allowed) for allowed in LEDGERS), 'unknown ledger hash/path')
    member = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
    _need(member.get('sourceId') == source_id and member.get('sourceSha256') == source_sha, 'entry source identity/hash differs')
    _positive(member.get('confirmedValue'))
    reader = _Pinned(load)
    ledger = reader.json(reference)  # Recheck exact ledger bytes on every call.
    _need(sum(_canonical(member) == _canonical(row) for row in ledger['confirmations']) == 1, 'entry is not one exact immutable ledger member')
    cache_key = tuple(ref['sha256'] for ref in LEDGERS)
    if cache_key not in _CACHE:
        _CACHE[cache_key] = _build(reader, _source_pixels)
    expected = _CACHE[cache_key][reference['sha256']]
    _need(sum(_canonical(member) == _canonical(row) for row in expected) == 1, 'entry is not one reconstructed source-confirmed tuple')
