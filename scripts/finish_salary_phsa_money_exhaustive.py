#!/usr/bin/env python3
"""Replay the exact, exhaustive 84/99/99 monetary peer union for FY2019 batch016.

No value is inferred from an engine or a control total.  The complete 633-field
author transcript, its 282 money-only canonical reread, explicit secondary
corrections, and each distinct peer schema are joined by physical field tuple.
The one printed expense dash is returned separately from positive confirmations.
"""
import re


SOURCE = ('phsa-2019-20',
          '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02',
          'phsa-2019-20-016')
BASE = 'research/salaries/queue-completion-2026-11-01/reviews/'
# These original schemas predate the frozen boolean / complete header convention.
# The exceptions name exact immutable documents, not a permissive schema default.
LEGACY = {
    'independent-phsa-schools-peer-held-2019-20-016-eightyfour-money-image-first.json':
        '357da534fa5c13b7d316f74915ad77983eb429ddabba97e4648f8a4e923435e0',
    'independent-phsa-schools-peer-held-2019-20-016-eightyfour-money-final-comparison.json':
        '45e446fe49a58fdd0bf564b8565f8959c28a792657daee1d7f525d7ffb7e74df',
    'independent-phsa-schools-peer-held-2019-20-016-eightyfour-money-source-pixel-verification.json':
        '172b09877b609f92a08d8a25d1db0d96a3f5df0dc7c0e6b6a12fe05b2e27e92d',
    'independent-phsa-schools-peer-held-2019-20-016-postcomparison-own-three-money-corrections.json':
        '484ed55d7d7f51467867692aa13cffbf801c41cd90fed32170b526ddd3c63b37',
    'independent-phsa-schools-peer-held-2019-20-016-first-working-before-source-rechecks.json':
        'cf3875caa4dcd748635e024189dcc39792a6f23ae251438ceb02b593818c220d',
    'independent-phsa-municipal-peer-held-2019-20-016-last99-money-source-pixels.json':
        'e8f987e697a985f9567badd0b53cd6552214b97f4547544178b5417808e0dd58',
}


def _require(condition, reason):
    if not condition:
        raise ValueError('Exhaustive batch016 money: ' + reason)


def _legacy(reference, name):
    return reference == {'path': BASE + name, 'sha256': LEGACY[name]}


def _money(value, field):
    _require(type(value) is int and value > 0 or value is None and field == 'expenses',
             'money must be a positive literal integer or the explicit expense dash')
    return value


def _literal(text, value):
    if value is None:
        _require(text == '-', 'null requires the literal printed dash')
    else:
        _require(isinstance(text, str) and re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', text)
                 and int(text.replace(',', '')) == value, 'literal text and integer differ')


def _counts(actual, expected):
    _require(isinstance(actual, dict) and set(actual) == set(expected)
             and all(type(actual[k]) is int and actual[k] == v for k, v in expected.items()),
             'declared scope / correction counts differ')


def _pairs(rows):
    result = {(r['sequence'], r['field']): r for r in rows}
    _require(len(result) == len(rows), 'duplicate sequence/field')
    return result


def independent_peer_raws(review, read):
    """Name the three actual peer raws; there is no independent 282-field raw."""
    references = review['exactDisjointPeerPartition']
    _require(len(references) == 3, 'expected exactly three distinct peer raw inputs')
    fields = ('peerImageFirstRaw', 'freshPeerSourceFirst', 'imageFirstTranscript')
    result = [read(reference)[field] for reference, field in zip(references, fields)]
    _require(len({pin['path'] for pin in result}) == 3, 'duplicate independent peer raw transcript')
    return result


def replay(review, overlay, source, read, image_check, unique, key):
    """Return facts, separate_nulls, author_raw_pin, author_errors, peer_errors.

    peer_errors counts changes from the three frozen peer transcripts (four).
    The school peer's earlier nine numeric mistakes and two unread digits remain
    checked as a separate, explicitly pre-choice working stage.
    """
    _require(source == SOURCE, 'this adapter is bounded to the one concrete source/batch')

    def load(reference, *, missing=(), frozen=True, legacy_name=None):
        doc = read(reference)
        exact = legacy_name is not None and _legacy(reference, legacy_name)
        _require(not missing or exact, 'header exception needs the exact legacy pin')
        for field, expected in zip(('sourceId', 'sourceSha256', 'batch'), source):
            if field in missing:
                _require(field not in doc, 'legacy header shape changed')
            else:
                _require(doc.get(field) == expected, 'source/PDF/batch identity differs')
        _require('frozen' not in doc or doc['frozen'] is True, 'explicitly unfrozen document')
        if frozen:
            _require(doc.get('frozen') is True or exact and 'frozen' not in doc,
                     'document is not explicitly frozen or the exact legacy document')
        return doc

    _require((review.get('sourceId'), review.get('sourceSha256'), review.get('batch')) == source
             and review.get('frozen') is True, 'aggregate financial receipt identity / closure differs')
    current_ref = review['own282SourceReread']
    current = load(current_ref)
    raw_ref = current['originalSourceFirst']
    raw = load(raw_ref)
    packet = load(current['sourceOnlyPacket'])
    views = load(raw['sourceOnlyTargetViews'])
    # The ordinary resolution schema has no frozen flag; the immutable overlay
    # byte pin and its exact complete author-raw link provide this identity.
    author_review = load(overlay['reviewInput'], frozen=False)
    _require({'path': author_review['rawTranscriptPath'],
              'sha256': author_review['rawTranscriptSha256']} == raw_ref
             and author_review['imageFirstTranscriptFreeze'] == raw_ref
             and overlay['frozenBatch']['sha256'] == views['fullBatchSha256']
             and raw['fullCandidateSha256StillClosed'] == views['fullBatchSha256']
             and author_review['additionalNativeFieldViewManifest'] == raw['sourceOnlyTargetViews']
             and author_review['unresolvedRows'] == []
             and read(author_review['completeFinancialSourceClosure']) == review,
             'effective author review / batch is not tied to its complete frozen raw')
    _require(raw['fullCandidateOrCorrespondingOcrOpenedBeforeFreeze'] is False
             and current['correspondingFreshPeerValuesOpened'] is False
             and packet['sourceValuesOrCandidateAlternativesIncluded'] is False,
             'author source-first chronology or source-only packet differs')
    original = unique(raw['rows'])
    view_fields = {}
    for row in views['rows']:
        _require(type(row['sequence']) is int and row['sequence'] > 0
                 and len(row['reviewTargetFields']) == len(set(row['reviewTargetFields'])),
                 'invalid native source target row')
        native = {v['field']: v for v in row['sourceNativeTargetViews']}
        _require(set(native) == set(row['reviewTargetFields'])
                 and len(native) == len(row['sourceNativeTargetViews']), 'native source field map differs')
        for field in row['reviewTargetFields']:
            identity = (row['physicalPage'], row['sourceRowOnPage'], field)
            _require(identity not in view_fields, 'repeated native field target')
            view_fields[identity] = (row, native[field])
    _require(len(views['rows']) == 400 and len(original) == 633
             and set(original) == set(view_fields), 'complete 633-field author coverage differs')
    targets, rereads, finals = map(unique, (packet['rows'], current['rows'], review['rows']))
    expected_money = {identity for identity in original if identity[2] in ('remuneration', 'expenses')}
    _require(len(targets) == 282 and set(targets) == expected_money
             and set(rereads) == set(targets) == set(finals), 'complete 282 money scope differs')
    _counts(raw['counts'], {'sourceRows': 400, 'requestedFields': 633, 'names': 351,
                           'remuneration': 198, 'expenses': 84, 'printedDashNulls': 1,
                           'positiveMoney': 281, 'explicitZeros': 0, 'negativeMoney': 0})

    corrections = {}
    correction_refs = review['additiveOwnSourceCorrections']
    _require(len(correction_refs) == 3, 'expected the three explicit secondary-correction receipts')
    for ref in correction_refs:
        doc = load(ref)
        _require(doc['priorFrozenCurrent'] == current_ref, 'secondary correction loses its prior reread')
        for correction in doc.get('rows', [doc]):
            identity = key(correction)
            _require(identity in targets and identity not in corrections
                     and correction['uncertainty'] is None, 'duplicate / out-of-scope secondary correction')
            corrections[identity] = correction
            for image_field in ('nativeOriginal300SourceView', 'actualWholePage600SourceView'):
                if image_field in correction:
                    _require(correction[image_field] == targets[identity][image_field],
                             'secondary correction changes its actual source image')
                    image_check(correction[image_field])
            for image in correction.get('sourceProof', []):
                _require(any(image['sha256'] == targets[identity][f]['sha256']
                             for f in ('nativeOriginal300SourceView', 'actualWholePage600SourceView')),
                         'secondary correction source proof is unrelated')
                image_check(image)
    _require({(r['sequence'], r['field']) for r in corrections.values()} ==
             {(139, 'expenses'), (174, 'expenses'), (203, 'remuneration'), (214, 'expenses')},
             'the exact four secondary corrections differ')
    author_changes = intermediate_changes = cold_pay = cold_expenses = 0
    for identity, target in targets.items():
        first, middle, final = original[identity], rereads[identity], finals[identity]
        locator, native = view_fields[identity]
        for record in (target, first, middle, final):
            _require(record['sequence'] == locator['sequence']
                     and record['cropSha256'] == locator['cropSha256'], 'sequence or original row crop moved')
        before = _money(first['literalSourceValue'], identity[2])
        second = _money(middle['currentLiteral'], identity[2])
        _require((before is None) == (identity == (119, 42, 'expenses'))
                 and (second is None) == (identity == (119, 42, 'expenses')),
                 'original / secondary monetary null scope differs from the one printed dash')
        after = corrections[identity]['correctedCurrentLiteral'] if identity in corrections else second
        _money(after, identity[2])
        _require(middle['firstFrozenLiteral'] == before
                 and middle['ownColdReadingCorrection'] is (before != second)
                 and middle['uncertainty'] is None
                 and target['nativeOriginal300SourceView'] == native
                 and middle['nativeOriginal300SourceView'] == native
                 and middle['actualWholePage600SourceView'] == target['actualWholePage600SourceView']
                 and final['sourceNative300'] == native
                 and final['sourceWhole600'] == target['actualWholePage600SourceView']
                 and final['originalColdLiteral'] == before
                 and final['ownIntermediateWhole600Literal'] == second
                 and final['finalSourceLiteral'] == after
                 and final['ownColdToFinalCorrection'] is (before != after)
                 and final['ownSecondaryToFinalCorrection'] is (second != after)
                 and final['literalPrintedDashNull'] is (after is None),
                 'actual author cold / secondary / final / source maps differ')
        if identity in corrections:
            correction = corrections[identity]
            _require(correction['sequence'] == target['sequence']
                     and correction['cropSha256'] == target['cropSha256']
                     and correction['coldFirstLiteral'] == before
                     and correction['ownIncorrectSecondaryWhole600Reading'] == second
                     and second != after, 'secondary correction hides its first or intermediate value')
        image_check(native)
        image_check(target['actualWholePage600SourceView'])
        author_changes += before != after
        intermediate_changes += before != second
        cold_pay += identity[2] == 'remuneration' and before != after
        cold_expenses += identity[2] == 'expenses' and before != after
    _counts(current['counts'], {'fields': 282, 'pay': 198, 'expenses': 84, 'positive': 281,
                               'literalDashNull': 1, 'zero': 0, 'negative': 0, 'unresolved': 0,
                               'ownColdCorrections': intermediate_changes,
                               'ownColdPayCorrections': 37, 'ownColdExpenseCorrections': 10})

    peer_references = review['exactDisjointPeerPartition']
    _require(len(peer_references) == 3 and len({r['path'] for r in peer_references}) == 3,
             'three distinct peer partitions are required')
    covered = set()
    facts, nulls = [], []
    peer_changes = 0
    for partition, reference in enumerate(peer_references):
        school, education = partition == 0, partition == 1
        peer = load(reference, legacy_name=(
            'independent-phsa-schools-peer-held-2019-20-016-eightyfour-money-final-comparison.json'
            if school else None))
        if school:
            raw_peer_ref, choice_ref, proof_ref = (peer['peerImageFirstRaw'], peer['scopedAuthorChoices'],
                                                  peer['sourcePixelVerification'])
        elif education:
            raw_peer_ref, choice_ref, proof_ref = (peer['freshPeerSourceFirst'], peer['authorOnlyScoped99Choices'],
                                                  peer['peerActualWhole600AndNative300PixelProof'])
        else:
            raw_peer_ref, choice_ref, proof_ref = (peer['imageFirstTranscript'], peer['authorScopedProposals'],
                                                  peer['pixelVerification'])
        own_peer = load(raw_peer_ref, legacy_name=(
            'independent-phsa-schools-peer-held-2019-20-016-eightyfour-money-image-first.json' if school else None))
        choice = load(choice_ref)
        proof = load(proof_ref, missing=(('batch',) if school else ('sourceId',) if not education else ()),
                     legacy_name=(
                         'independent-phsa-schools-peer-held-2019-20-016-eightyfour-money-source-pixel-verification.json'
                         if school else
                         'independent-phsa-municipal-peer-held-2019-20-016-last99-money-source-pixels.json'
                         if not education else None))
        _require(choice['peerRawFrozenBeforeTheseChoices'] == raw_peer_ref,
                 'author choice release is not tied to this peer frozen raw')
        if school:
            packet_ref = choice['sourceOnlyPacket']
            _require(choice['ownFull282CurrentFrozenBeforeAnyCorrespondingPeerLiterals'] == current_ref
                     and own_peer['authorChoicesUnopenedAtFreeze'] is True
                     and own_peer['candidateUnopenedAtFreeze'] is True
                     and own_peer['unresolvedFields'] == [] and peer['unresolvedFields'] == []
                     and own_peer['pixelVerification'] == proof_ref
                     and own_peer['sourceOnlyPackets'] == proof['sourceOnlyPackets']
                     and packet_ref in own_peer['sourceOnlyPackets'], 'school peer source-first / proof history differs')
            _require(len(own_peer['sourceOnlyPackets']) == 2
                     and own_peer['sourceOnlyPackets'][1] == packet_ref,
                     'school original/companion source-only packet pair differs')
        else:
            packet_ref = own_peer['input'] if education else own_peer['sourceOnlyPacket']
            _require(choice['ownFull282CurrentFrozenBeforeCorrespondingPeerValues'] == current_ref,
                     'peer choices do not preserve the author whole282 reread')
            if education:
                _require(own_peer['blindness']['correspondingAuthorOrOcrChoicesOpened'] is False
                         and own_peer['blindness']['priorCorrespondingExpectedValuesSupplied'] is False
                         and own_peer['uncertainFields'] == [] and proof['sourceOnlyInput'] == packet_ref,
                         'education source-first / proof history differs')
            else:
                _require(own_peer['sourceValuesOrAuthorChoicesOpenedBeforeFreeze'] is False
                         and own_peer['firstPassCorrections'] == [] and own_peer['unresolved'] == []
                         and peer['unresolvedFields'] == [] and proof['sourceOnlyPacket'] == packet_ref
                         and peer['sourceOnlyPacket'] == packet_ref and proof['rawImageFirstTranscript'] == raw_peer_ref
                         and proof['sourceOnlyFieldManifest'] == raw['sourceOnlyTargetViews']
                         and proof['sourceOriginalHashVerified'] is True, 'municipal source-first / proof history differs')
        peer_packet = load(packet_ref)
        peer_targets, first_peers, peer_rows, choices = map(unique, (
            peer_packet['rows'], own_peer['rows'], peer['rows'], choice['rows']))
        pixels = unique(proof['fields'] if school or education else proof['rows'])
        size = 84 if school else 99
        _require(len(peer_targets) == size and set(peer_targets) <= set(targets)
                 and not covered.intersection(peer_targets)
                 and all(set(mapping) == set(peer_targets) for mapping in (first_peers, peer_rows, choices, pixels)),
                 'overlapping / missing / extra peer tuple scope')
        covered.update(peer_targets)
        for identity, target in peer_targets.items():
            _require(target == targets[identity], 'partition changes the exact canonical source target')
        peer_amendments = {}
        if school:
            prior_packet = load(own_peer['sourceOnlyPackets'][0])
            prior_targets = unique(prior_packet['rows'])
            _require(set(prior_targets) == set(peer_targets), 'school original1200 target scope differs')
            for identity, target in peer_targets.items():
                _require(prior_targets[identity] == target['priorIndependentActual1200SourceView'],
                         'school prior1200 source map differs from its canonical companion')
            _require(own_peer['fieldCount'] == size and peer['fieldCount'] == size
                     and peer['matchedCurrentFields'] == size and proof['fieldCount'] == size
                     and own_peer['fieldCounts'] == {'remuneration': 55, 'expenses': 29}
                     and peer['peerFrozenRawMatchesFinal'] == 81
                     and peer['peerPrecomparisonNumericCorrections'] == 9
                     and peer['peerPrecomparisonUnclearTerminalDigitsResolved'] == 2
                     and peer['peerPostChoiceNumericCorrections'] == 3
                     and peer['authorPostPeerSecondaryNumericCorrections'] == 2
                     and peer['authorFirstVsFinalDifferencesInThisExact84Scope'] == 43,
                     'school source / correction counters differ')
            change_doc = load(peer['ownPostComparisonCorrectionReceipt'], legacy_name=
                              'independent-phsa-schools-peer-held-2019-20-016-postcomparison-own-three-money-corrections.json')
            _require(change_doc['peerRaw'] == raw_peer_ref and change_doc['scopedAuthorChoices'] == choice_ref
                     and change_doc['authorChoicesAlreadyOpened'] is True,
                     'school post-choice correction history differs')
            observations = unique(change_doc['fields'])
            _require(set(observations) <= set(peer_targets), 'school amendment widens scope')
            peer_amendments = {k: v for k, v in observations.items() if v['ownPeerCorrection'] is True}
            _require(len(peer_amendments) == 3 and len(observations) == 5
                     and change_doc['ownCorrectionCount'] == 3
                     and peer['authorPostPeerSecondaryCorrectionReceipt'] in correction_refs,
                     'school correction scope / source history differs')
            working_ref = own_peer['firstWorkingSnapshot']
            _require(_legacy(working_ref, 'independent-phsa-schools-peer-held-2019-20-016-first-working-before-source-rechecks.json'),
                     'school headerless first-working exception requires its exact immutable pin')
            working = read(working_ref)
            _require(working['sourceOnly'] == own_peer['sourceOnlyPackets'][0]['path'],
                     'school first-working snapshot identifies a different source-only packet')
            old_work = _pairs(working['readings'])
            prechanges = _pairs(own_peer['ownCorrections'])
            _require(set(old_work) == {(r['sequence'], r['field']) for r in peer_targets.values()}
                     and len(prechanges) == 11, 'school complete working snapshot / correction scope differs')
            numeric_changes = unread = 0
            for identity, first_peer in first_peers.items():
                pair = (first_peer['sequence'], identity[2]); old = old_work[pair]
                if old['value'] is None:
                    _require(pair in {(64, 'remuneration'), (109, 'remuneration')}
                             and old['needsSourceReread'] is True,
                             'school working-stage unread scope differs')
                else:
                    _money(old['value'], identity[2])
                    _literal(old['literal'], old['value'])
                if pair in prechanges:
                    correction = prechanges[pair]
                    _require(correction['firstWorkingValue'] == old['value']
                             and correction['firstWorkingLiteral'] == old['literal']
                             and correction['currentValue'] == first_peer['value']
                             and correction['currentLiteral'] == first_peer['literalSourceAmount']
                             and correction['authorChoicesSeen'] is False
                             and old['value'] != first_peer['value'], 'school pre-choice correction loses its first reading')
                    numeric_changes += old['value'] is not None
                    unread += old['value'] is None
                else:
                    _require(old['value'] == first_peer['value'], 'unrecorded school working-to-frozen change')
            _require(numeric_changes == 9 and unread == 2
                     and own_peer['preComparisonNumericCorrections'] == 9
                     and own_peer['preComparisonUnreadResolved'] == 2,
                     'school pre-choice numeric / unread history totals differ')
        elif not education:
            amendment = load(peer['ownPostcomparisonSourceCorrection'])
            _require(amendment['ownRawImageFirstTranscript'] == raw_peer_ref
                     and amendment['authorScopedChoicesOpenedOnlyAfterRawFreeze'] == choice_ref
                     and amendment['unresolved'] is False, 'municipal correction loses its raw or choices')
            peer_amendments = {key(amendment): amendment}
            _require(set(peer_amendments) <= set(peer_targets), 'municipal correction widens scope')
            _require(peer['fieldCount'] == 99 and peer['exactFinalMatches'] == 99
                     and peer['numericPositiveConfirmationCount'] == 98
                     and peer['separateLiteralDashNullEvidenceCount'] == 1
                     and proof['fieldCount'] == 99, 'municipal peer / proof counters differ')
        else:
            _counts(peer['counts'], {'fields': 99, 'remuneration': 69, 'expenses': 30,
                                    'effectiveExactMatches': 99, 'initialCurrentMatches': 98,
                                    'initialAuthorColdMatches': 99, 'peerSourceReadingCorrections': 0,
                                    'authorSecondaryErrorRestorations': 1, 'unresolvedFields': 0,
                                    'monetaryQualifications': 0})
            _counts(proof['counts'], {'pages': 5, 'requestedFields': 99,
                                     'actualWhole600RgbExact': 99, 'native300RgbExact': 99})

        partition_changes = 0
        for identity, target in peer_targets.items():
            initial, decision, proposal, pixel = (m[identity] for m in (first_peers, peer_rows, choices, pixels))
            author_first = original[identity]['literalSourceValue']
            author_middle = rereads[identity]['currentLiteral']; final = finals[identity]['finalSourceLiteral']
            native = target['nativeOriginal300SourceView']; image = target['actualWholePage600SourceView']
            for row in (initial, decision, proposal, pixel):
                _require(row['sequence'] == target['sequence'] and row['cropSha256'] == target['cropSha256'],
                         'peer/proof/choice sequence or row crop moved')
            _require(proposal == rereads[identity] and finals[identity]['independentSourcePeer'] == reference,
                     'scoped author choices / chosen peer authority differ')
            if school:
                peer_first = _money(initial['value'], identity[2])
                _literal(initial['literalSourceAmount'], peer_first)
                peer_final = (peer_amendments[identity]['currentPersonalSourceValue']
                              if identity in peer_amendments else peer_first)
                _require(initial['uncertainty'] is None and decision['uncertainty'] is None
                         and initial['nativeOriginal300SourceView'] == native
                         and initial['actualWholePage600SourceView'] == image
                         and pixel['native300'] == native and pixel['actualWhole600'] == image
                         and pixel['prior1200'] == target['priorIndependentActual1200SourceView']
                         and pixel['native300PixelExact'] is True and pixel['whole600PixelExact'] is True
                         and pixel['prior1200WhiteBoundaryPixelExact'] is True
                         and decision['peerFrozenRawValue'] == peer_first
                         and decision['currentValue'] == peer_final and decision['authorCurrentValue'] == final
                         and decision['authorFirstValue'] == author_first
                         and decision['authorScopedProvisionalValue'] == author_middle
                         and decision['peerPostChoiceCorrection'] is (peer_first != peer_final)
                         and decision['authorPostPeerSecondaryCorrection'] is (author_middle != final)
                         and decision['match'] is True, 'school source / first / final / pixel facts differ')
                _literal(decision['literalSourceAmount'], peer_final)
                image_check(pixel['prior1200'])
            elif education:
                peer_first = _money(initial['value'], identity[2]); peer_final = peer_first
                _literal(initial['literalPrinted'], peer_first)
                _require(initial['uncertain'] is False and initial['source600'] == image and initial['native300'] == native
                         and pixel['actualWholepage600'] == image and pixel['native300'] == native
                         and pixel['actualWhole600RgbExact'] is True and pixel['native300RgbExact'] is True
                         and decision['peerFirstLiteral'] == peer_first
                         and decision['authorColdFirstLiteral'] == author_first
                         and decision['authorEarlierWhole600SecondaryLiteral'] == author_middle
                         and decision['authorEffectiveCurrentLiteral'] == final
                         and decision['matchesEffectiveCurrent'] is True and decision['peerCorrection'] is False
                         and decision['authorSecondaryRestoration'] is (author_middle != final),
                         'education source / first / final / pixel facts differ')
            else:
                peer_first = _money(initial['imageFirstValue'], identity[2])
                peer_final = (peer_amendments[identity]['correctedLiteralSourceValue']
                              if identity in peer_amendments else peer_first)
                _require(initial['actualWholePage600SourceView'] == image
                         and initial['nativeOriginal300SourceView'] == native
                         and decision['sourceNativeField'] == native
                         and decision['actualWholePage600SourceField'] == pixel['actual600IndependentCrop']
                         and decision['actualWholePage600SourceField']['sha256'] == image['sha256']
                         and pixel['actual600RGBExact'] is True and pixel['native300FieldRGBExact'] is True
                         and pixel['fullRow300RGBExact'] is True
                         and decision['peerFirstSourceValue'] == peer_first and decision['value'] == peer_final
                         and decision['uncertainty'] is None and decision['authorFirstFrozenValue'] == author_first
                         and decision['authorScopedSecondaryValue'] == author_middle
                         and decision['authorEffectiveSourceValue'] == final and decision['exactMatch'] is True
                         and decision['literalPrintedDashEvidence'] is (final is None),
                         'municipal source / first / final / pixel facts differ')
                _literal(decision['literalSourceAmount'], peer_final)
                image_check(pixel['actual600IndependentCrop'])
            _money(peer_final, identity[2])
            _require(peer_final == final, 'independent literal amount disagrees with final author source')
            if identity in peer_amendments:
                change = peer_amendments[identity]
                _require(change['sequence'] == target['sequence'] and change['cropSha256'] == target['cropSha256'],
                         'peer amendment changes source locator / crop')
                if school:
                    _require(change['peerRawValue'] == peer_first
                             and change['independentlyReproducedSourcePixelsExact'] is True,
                             'school amendment hides peer first / source pixels')
                    image_check(change['sourceImage'])
                else:
                    _require(change['ownFirstFrozenValue'] == peer_first
                             and change['actual600Source'] == pixel['actual600IndependentCrop']
                             and change['native300Source'] == native, 'municipal amendment hides peer first / source image')
                    image_check(change['actual600Source']); image_check(change['native300Source'])
            partition_changes += peer_first != peer_final
            item = (target, final, image, target['cropSha256'])
            if final is None:
                _require(not school and not education and target['sequence'] == 372
                         and identity == (119, 42, 'expenses'), 'only the exact printed expense dash may be null')
                nulls.append(item)
            else:
                facts.append(item)
        _require(partition_changes == (3 if school else 0 if education else 1),
                 'frozen peer-to-final correction count differs')
        peer_changes += partition_changes
    _require(covered == set(targets) and len(facts) == 281 and len(nulls) == 1,
             'exhaustive disjoint peer union is incomplete')
    _counts(review['counts'], {'requestedMoneyFields': 282, 'pay': 198, 'expenses': 84,
                              'positiveLiteralAmounts': 281, 'explicitPrintedDashNull': 1,
                              'explicitZero': 0, 'negative': 0, 'unresolved': 0, 'overlappingPeerFields': 0,
                              'ownColdToFinalCorrections': author_changes, 'ownColdPayCorrections': cold_pay,
                              'ownColdExpenseCorrections': cold_expenses, 'ownRejectedSecondaryReadings': 4})
    _require(author_changes == 44 and cold_pay == 37 and cold_expenses == 7 and peer_changes == 4,
             'concrete final first-reading error history differs')
    overlay_fields = {}
    for row in overlay['overlays']:
        for field in row['reviewedFields']:
            identity = (row['physicalPage'], row['sourceRowOnPage'], field)
            _require(identity not in overlay_fields, 'effective overlay repeats a source field')
            overlay_fields[identity] = row
    _require(set(overlay_fields) == set(original), 'effective overlay is not the exact complete author target scope')
    for target, value, image, crop in facts + nulls:
        row = overlay_fields[key(target)]
        index = 3 if target['field'] == 'remuneration' else 4
        _require(row['resolvedRow'][index] == value and row['cropSha256'] == crop,
                 'effective overlay disagrees with an exhaustive source amount')
    return facts, nulls, raw_ref, author_changes, peer_changes
