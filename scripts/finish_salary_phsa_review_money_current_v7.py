#!/usr/bin/env python3
"""Independent fixed-schema financial replay for PHSA ledgers022/023-v2/025/026/027.

Only source receipts/field tuples are read. No producer, finalizer or v7 imports.
"""
import hashlib
import copy
import csv
import gzip
import json
import io
import re
from pathlib import Path

SPEC = {
 '6e649bf527469dafd60ddfcaf17dd53d93a4bc49de9f55b1f7b85a6166ecd7c0': (22, 31, 6, 0, 0),
 '9e436864774cc41573ace634789b386bd1ab47824587a8e3544400c269ff4494': (23, 53, 53, 10, 7),
 '97c998ec16fb28746f76b5fd450f0d7f966b24109b432d68ef6b0db41328626c': (25, 42, 42, 7, 7),
 '90b60335597f5a791d613307a4c819440702903a0ea319abf61c575df383e525': (26, 36, 36, 3, 0),
 '6dd8ce0d759d5b07b0b5d5d28591f9e05dccfd9ae5119206d32084cf1f47523e': (27, 55, 55, 3, 1),
}
SOURCE = ('phsa-2019-20', '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02')
CACHE = {}


class Pinned:
    def __init__(self, loader):
        self.loader = loader
        self.cache = {}

    def __call__(self, reference, parse=True):
        k = reference['path'], reference['sha256']
        assert isinstance(k[0], str) and re.fullmatch('[0-9a-f]{64}', k[1])
        if k not in self.cache:
            data = self.loader({'path': k[0], 'sha256': k[1]}, False)
            assert isinstance(data, bytes) and hashlib.sha256(data).hexdigest() == k[1], 'Pinned input bytes changed'
            self.cache[k] = data
        data = self.cache[k]
        if not parse:
            return data
        return json.loads(gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data)


def key(row):
    p, r, f = row['physicalPage'], row['sourceRowOnPage'], row['field']
    assert type(p) is int and type(r) is int and min(p, r) > 0
    assert f in ['name', 'remuneration', 'expenses']
    return p, r, f


def rows(items):
    result = {key(row): row for row in items}
    assert len(result) == len(items)
    return result


def amount(value):
    if isinstance(value, str):
        assert re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', value)
        value = int(value.replace(',', ''))
    assert type(value) is int and value > 0
    return value


def integer_columns(row, names):
    for name in names:
        assert type(row[name]) is int and row[name] > 0, ('Expected strict positive source integer', name)


def same_locator(*items):
    assert all(type(row['sequence']) is int and row['sequence'] > 0 for row in items)
    assert len({(key(r), r['sequence']) for r in items}) == 1
    hashes = {r.get('cropSha256', r.get('originalFullRowCropSha256')) for r in items}
    assert len(hashes) == 1 and None not in hashes
    return next(iter(hashes))


def source_identity(doc, source_id, source_sha):
    assert doc['sourceId'] == source_id and doc['sourceSha256'] == source_sha


def same_source_documents(*documents):
    for doc in documents:
        source_identity(doc, *SOURCE)


def raw_value(document, locator):
    """The concrete complete-author JSON schemas, preserving exact tuple identity."""
    matches = []
    for row in document['rows']:
        if (row['physicalPage'], row['sourceRowOnPage']) != locator[:2]:
            continue
        if 'field' in row and row['field'] == locator[2]:
            for field in ['literalSourceValueFirstPass', 'literalSourceValue', 'firstFrozenLiteral']:
                if field in row:
                    matches.append(row[field])
                    break
        elif 'literalSourceValuesFirstPass' in row and locator[2] in row['literalSourceValuesFirstPass']:
            matches.append(row['literalSourceValuesFirstPass'][locator[2]])
        elif 'sourceImageReadings' in row and locator[2] in row['sourceImageReadings']:
            matches.append(row['sourceImageReadings'][locator[2]])
        elif 'imageFirstValues' in row and locator[2] in row['imageFirstValues']:
            matches.append(row['imageFirstValues'][locator[2]])
        elif 'resolvedValues' in row and locator[2] in row['resolvedValues']:
            matches.append(row['resolvedValues'][locator[2]])
    assert len(matches) == 1, ('Complete author raw field missing/duplicated', locator)
    return amount(matches[0])


def pixels(facts, source_id, source_sha, load):
    """Fresh original whole-page source rendering, then integer financial cuts."""
    import fitz
    from PIL import Image
    pdf = Path('/tmp/queue-completion-phsa/originals') / (source_id + '.pdf')
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == source_sha
    doc = fitz.open(pdf)
    for page in sorted({p for p, _, _, _ in facts}):
        by_dpi = {}
        for dpi in {dpi for p, _, dpi, _ in facts if p == page}:
            pix = doc[page - 1].get_pixmap(dpi=dpi, alpha=False)
            by_dpi[dpi] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        for pn, image_ref, dpi, box in facts:
            if pn != page:
                continue
            assert len(box) == 4 and all(type(n) is int for n in box)
            actual = by_dpi[dpi].crop(tuple(box))
            try:
                supplied = Image.open(io.BytesIO(load(image_ref, False)))
                assert supplied.mode == 'RGB' and supplied.format == 'PNG', 'Source fields must retain visible RGB ink, not alpha-hidden bytes'
                assert supplied.size == actual.size and supplied.tobytes() == actual.tobytes()
            except (KeyError, FileNotFoundError):
                # Some original native target PNGs are intentionally reconstructible
                # rather than archived. Reproduce their exact PNG bytes, not a guess.
                encoded = io.BytesIO()
                actual.save(encoded, format='PNG')
                assert hashlib.sha256(encoded.getvalue()).hexdigest() == image_ref['sha256']


def mode22(peer, load):
    raw_ref = peer['independentImageFirstTranscript']
    first = load(raw_ref)
    packet = load(peer['sourceOnlyPacket'])
    choices = load(peer['authorScopedChoicesOpenedOnlyAfterPeerFreeze'])
    author_original = load(choices['originalRaw'])
    same_source_documents(peer, first, packet, choices, author_original)
    assert author_original['frozen'] is True and author_original['frozenBeforeOpeningFullCandidate'] is True
    assert author_original['fullCandidateOpened'] is False and author_original['all198AssignedRowsAnd226FieldsPersonallyRead'] is True
    assert len(author_original['rows']) == 198
    assert sum(len(r['reviewTargetFields']) for r in author_original['rows']) == 226
    assert first['frozen'] is True and first['correspondingAuthorChoicesOpened'] is False
    assert first['fullCandidateOpened'] is False and first['sourceOnlyPacket'] == peer['sourceOnlyPacket']
    assert packet['sourceOnly'] is True and packet['expectedValuesWithheld'] is True
    targets, original, author, final = [rows(d['rows']) for d in [packet, first, choices, peer]]
    assert len(targets) == 31 and set(targets) == set(original) == set(author) == set(final)
    facts, images = [], []
    for k, target in targets.items():
        initial, choice, result = original[k], author[k], final[k]
        crop = same_locator(target, initial, choice, result)
        if k[2] == 'name':
            continue
        integer_columns(initial, ['literalPreferred', 'firstWhole600VisualValue'])
        integer_columns(choice, ['firstAuthorSourceReading', 'currentAuthorSourceReading'])
        integer_columns(result, ['firstPeerWhole600VisualValue', 'peerPrechoiceContextLiteral', 'peerCurrentPreferredLiteral', 'authorFirstSourceValue', 'authorCurrentSourceValue', 'literalSourceValue'])
        value = amount(initial['literalPreferred'])
        assert value == amount(initial['firstWhole600VisualValue'])
        assert value == amount(choice['firstAuthorSourceReading']) == amount(choice['currentAuthorSourceReading'])
        assert raw_value(author_original, k) == choice['firstAuthorSourceReading']
        assert value == result['firstPeerWhole600VisualValue'] == result['peerPrechoiceContextLiteral']
        assert value == result['peerCurrentPreferredLiteral'] == result['authorFirstSourceValue']
        assert value == result['authorCurrentSourceValue'] == result['literalSourceValue']
        assert result['numericalUncertainty'] is None and result['ownPostchoiceLiteralCorrection'] is False
        image = target['actualWholePage600Field']
        assert initial['sourceWhole600'] == result['sourceWhole600'] == choice['actualWholePage600Field'] == image
        native = target['actualNative300Field']
        assert initial['sourceNative300'] == result['sourceNative300'] == native
        images += [(k[0], image, 600, image['originalFullPagePixelBox']),
                   (k[0], native, 300, native['originalFullPagePixelBox'])]
        assert image['originalFullPagePixelBox'] == [n * 2 for n in native['originalFullPagePixelBox']]
        facts.append((k, value, crop, image, raw_ref))
    assert len(facts) == 6
    return facts, images, 0, 0


def mode23(peer, load):
    old = load(peer['supersedesCurrentAuthorityOfOnly394InPriorReceipt'])
    raw_ref = peer['originalRootFirstRaw']
    first = load(raw_ref)
    author = load(peer['authorAll53CanonicalWhole600Reread'])
    scoped = load(author['priorAuthor53'])
    reread = load({'path': 'research/salaries/queue-completion-2026-11-01/reviews/independent-phsa-schools-2019-20-batch-012-current-source-reread-before-fresh-peer.json',
                   'sha256': scoped['authorBroaderFreezeSha256ForHashOnly']})
    author_first = load(reread['originalFrozenRaw'])
    assert author_first['fullCandidateUnopenedAtFreeze'] is True
    assert author_first['rowCount'] == len(author_first['rows']) == 400
    prior_author = rows(scoped['rows'])
    correction = load(peer['authorOne394Correction'])
    cold = load(peer['freshColdIndependent394'])
    same_source_documents(peer, first, author, correction, cold, scoped, reread, author_first, old)
    assert first['frozen'] is True and first['candidateOrAuthorValuesOpened'] is False
    assert cold['frozen'] is True and cold['correspondingAuthorOrPeerAmountsOpened'] is False
    assert cold['fullBatchCandidateOpened'] is False and len(cold['rows']) == 1
    assert peer['accepted'] is True and peer['numericQualificationAllowed'] is False
    assert not peer['unresolvedMoneyFields']
    original, prior, secondary, final = [rows(d['rows'] if 'rows' in d else d['fields'])
                                       for d in [first, old, author, peer]]
    assert len(final) == 53 and set(final) == set(original) == set(prior) == set(secondary)
    corrected_key = key(correction)
    assert correction['sequence'] == 394 and key(cold['rows'][0]) == corrected_key
    assert amount(correction['currentPersonalSourceValue']) == amount(cold['rows'][0]['literalImageValue'])
    assert cold['rows'][0]['uncertainty'] is None
    facts, images = [], []
    author_errors = root_errors = 0
    for k, result in final.items():
        initial, earlier, current = original[k], prior[k], secondary[k]
        crop = same_locator(initial, earlier, current, result)
        assert amount(result['rootFirstImageReading']) == amount(initial['rootFirstImageReading'])
        value = amount(current['currentPersonalWhole600Value'])
        assert value == amount(result['rootCurrentSourceReading']) == amount(result['authorCurrentSourceReading'])
        assert result['positiveLiteralValuesAgree'] is True
        if k != corrected_key:
            assert result == earlier, 'Only394 may supersede the prior final53 receipt'
        else:
            assert value == amount(correction['currentPersonalSourceValue'])
            assert amount(earlier['authorCurrentSourceReading']) == amount(correction['oldAuthorAndRootValue'])
            assert value != amount(earlier['rootCurrentSourceReading'])
        assert amount(result['authorFirstSourceReading']) == amount(earlier['authorFirstSourceReading'])
        assert raw_value(author_first, k) == amount(prior_author[k]['originalFrozenRawReading']) == amount(result['authorFirstSourceReading'])
        assert amount(current['oldScopedSourceValue']) == amount(prior_author[k]['currentSourceReading'])
        author_errors += amount(result['authorFirstSourceReading']) != value
        root_errors += amount(initial['rootFirstImageReading']) != value
        image = {'path': current['whole600CellPath'], 'sha256': current['whole600CellSha256']}
        native = initial['sourceNativeField']
        box = current['actualWhole600PixelCropBox']
        native_box = initial['original300DpiFieldBox']
        assert box == [2 * native_box[0], 2 * native_box[1] - 8, 2 * native_box[2], 2 * native_box[3] + 8]
        images += [(k[0], image, 600, box),
                   (k[0], native, 300, initial['original300DpiFieldBox'])]
        facts.append((k, value, crop, image, peer['freshColdIndependent394'] if k == corrected_key else raw_ref))
    assert (author_errors, root_errors) == (10, 7)
    return facts, images, author_errors, root_errors


def mode25(peer, load):
    raw_ref = peer['rootFirstRaw']
    first = load(raw_ref)
    middle = load(peer['rootActual600SecondaryAssessment'])
    restoration = load(peer['root264AdditiveRestoration'])
    third = load(peer['independentThird13Final'])
    author = load(peer['authorAll42CanonicalFinal'])
    author_raw = load(author['originalFrozen497FirstTranscript'])
    assert third['frozen'] is True and len(third['inputs']) == 3
    third_first_ref = third['inputs'][0]
    third_first = load(third_first_ref)
    third_choices = load(third['inputs'][1])
    third_packet = load(third_first['imageOnlyPacket'])
    assert third['inputs'][2] == peer['root264AdditiveRestoration']
    assert third_first['frozen'] is True and third_choices['frozen'] is True and third_packet['frozen'] is True
    assert third_choices['thirdColdRawBeforeTheseChoices'] == third_first_ref
    assert third_choices['sourceOnlyPacket'] == third_first['imageOnlyPacket']
    assert third_packet['correspondingAuthorAndRootValuesMustStayClosedUntilRawFreeze'] is True
    same_source_documents(third, third_first, third_choices, third_packet)
    original_third, third_targets, third_opened = [rows(d['rows']) for d in [third_first, third_packet, third_choices]]
    third_prechoice = {(r['sequence'], r['field']): r for r in third_first['sourceOnlyOwnCorrections']}
    assert len(third_prechoice) == len(third_first['sourceOnlyOwnCorrections']) == 1
    same_source_documents(peer, first, middle, restoration, third, author, author_raw)
    assert author_raw['frozen'] is True and author_raw['candidateOpened'] is False and author_raw['correspondingChoicesOpened'] is False
    assert first['frozen'] is True and first['candidateOrAuthorValuesOpened'] is False
    assert peer['accepted'] is True and peer['numericQualificationAllowed'] is False and not peer['unresolvedMoneyFields']
    original, secondary, final, current, third_rows = [rows(d['rows']) for d in [first, middle, peer, author, third]]
    assert len(final) == 42 and len(third_rows) == 13
    assert set(third_rows) == set(original_third) == set(third_targets) == set(third_opened)
    assert set(final) == set(original) == set(secondary) == set(current) and set(third_rows) <= set(final)
    assert restoration['sequence'] == 264 and key(restoration) in third_rows
    facts, images = [], []
    author_errors = root_errors = 0
    for k, result in final.items():
        initial, intermediate, decision = original[k], secondary[k], current[k]
        integer_columns(initial, ['rootFirstImageReading'])
        integer_columns(intermediate, ['rootFirst1200ImageReading', 'rootCurrent600SourceReading'])
        integer_columns(decision, ['finalAuthorSourceValue', 'currentCanonicalSourceValue', 'initialImageFirstValue'])
        integer_columns(result, ['rootFirstImageValue', 'rootFinalSourceValue', 'authorCanonicalFinalSourceValue'])
        crop = same_locator(initial, intermediate, result, decision)
        before = amount(initial['rootFirstImageReading'])
        value = amount(decision['finalAuthorSourceValue'])
        assert value == decision['currentCanonicalSourceValue'] == result['rootFinalSourceValue'] == result['authorCanonicalFinalSourceValue']
        assert amount(result['rootFirstImageValue']) == amount(intermediate['rootFirst1200ImageReading']) == before
        assert result['exactCurrentAgreement'] is True and result['rootOwnFirstReadingChanged'] is (before != value)
        if k == key(restoration):
            assert value == restoration['rootFinalRestoredSourceReading'] == restoration['rootFirst1200SourceReading']
            assert intermediate['rootCurrent600SourceReading'] == restoration['rootWrongSecondary600Reading'] != value
        else:
            assert intermediate['rootCurrent600SourceReading'] == value
        if k in third_rows:
            independent = third_rows[k]
            raw_third, target_third, opened_third = original_third[k], third_targets[k], third_opened[k]
            same_locator(independent, raw_third, target_third, opened_third)
            integer_columns(independent, ['literalValue', 'rootFinalSourceValue', 'firstActual600VisualValue'])
            integer_columns(raw_third, ['literalValue', 'firstActual600VisualValue'])
            assert raw_third['literalValue'] == independent['literalValue']
            assert raw_third['firstActual600VisualValue'] == independent['firstActual600VisualValue']
            assert raw_third['uncertainty'] is None
            assert raw_third['actualOriginal600'] == independent['actualOriginal600'] == target_third['actualOriginal600']
            assert raw_third['native300SourceField'] == independent['native300SourceField'] == target_third['native300SourceField']
            load(target_third['actualOriginal600'], False)
            prechoice_key = raw_third['sequence'], k[2]
            if prechoice_key in third_prechoice:
                fix = third_prechoice[prechoice_key]
                assert fix['firstVisualValue'] == raw_third['firstActual600VisualValue']
                assert fix['correctedLiteralValue'] == raw_third['literalValue'] != fix['firstVisualValue']
                assert prechoice_key == (235, 'expenses') and fix['basis']
            else:
                assert raw_third['firstActual600VisualValue'] == raw_third['literalValue']
            assert independent['rootFirst1200ImageReading'] == opened_third['rootFirst1200ImageReading'] == before
            assert independent['rootIntermediate600SourceReading'] == opened_third['rootCurrent600SourceReading'] == intermediate['rootCurrent600SourceReading']
            assert independent['authorFirst600SourceReading'] == opened_third['authorFirst600SourceReading'] == decision['initialImageFirstValue']
            assert independent['authorIntermediate1200SourceReading'] == opened_third['authorSecondary1200SourceReading'] == decision['priorPartial1200SecondaryReading']
            assert independent['literalValue'] == independent['rootFinalSourceValue'] == value
            assert independent['uncertainty'] is None and independent['sourceAgreementWithRootFinal'] is True
        author_first = amount(decision['initialImageFirstValue'])
        assert raw_value(author_raw, k) == author_first
        author_errors += author_first != value
        root_errors += before != value
        image, native = decision['sourceEvidence'], decision['native300SourceField']
        box = image['wholePage600PixelBox']
        assert box == [n * 2 for n in native['originalPdf300DpiPixelBox']]
        images += [(k[0], image, 600, box), (k[0], native, 300, native['originalPdf300DpiPixelBox'])]
        facts.append((k, value, crop, image, raw_ref))
    assert (author_errors, root_errors) == (7, 7)
    return facts, images, author_errors, root_errors


def mode26(peer, load):
    raw_ref = peer['independentImageFirstTranscript']
    first = load(raw_ref)
    packet = load(peer['sourceOnlyPacket'])
    choices = load(peer['authorScopedSourceChoicesOpenedOnlyAfterPeerFreeze'])
    author_raw = load(peer['authorOriginalFrozenTranscript'])
    addition = load(peer['authorPostPeerAdditiveCorrection'])
    uncertainty = load(peer['peerPrechoiceUncertaintyResolution'])
    same_source_documents(peer, first, packet, choices, author_raw, addition, uncertainty)
    original, targets, scoped, final = [rows(d['rows']) for d in [first, packet, choices, peer]]
    assert len(final) == 36 and set(final) == set(original) == set(targets) == set(scoped)
    assert first['frozen'] is True and packet['sourceValuesOrCandidateAlternativesIncluded'] is False
    assert author_raw['candidateOpenedBeforeFreeze'] is False and author_raw['authorCandidateAlternativesSeenBeforeFreeze'] is False
    assert choices['freshPeerChoicesOpened'] is False and peer['allFinalSourceValuesMatchExactly'] is True
    assert not peer['unresolvedFields'] and peer['peerOwnAdditiveSourceCorrections'] is None
    resolved_uncertainty = rows(uncertainty['rows'])
    assert len(resolved_uncertainty) == 1 and uncertainty['originalSourceFirstRaw'] == raw_ref
    assert addition['sequence'] == 189 and key(addition) in scoped
    facts, images = [], []
    author_errors = peer_errors = 0
    for k, result in final.items():
        initial, target, choice = original[k], targets[k], scoped[k]
        integer_columns(initial, ['literalImageValue'])
        integer_columns(choice, ['firstFrozenLiteral', 'currentSourceLiteral'])
        integer_columns(result, ['firstPeerSourceValue', 'finalPeerSourceValue', 'initialAuthorSourceValue', 'intermediateAuthorSourceValue', 'finalAuthorSourceValue'])
        assert choice['sourceEvidence'] == target
        crop = same_locator(initial, target, {**choice, 'cropSha256': choice['sourceEvidence']['cropSha256']}, result)
        value = amount(result['finalPeerSourceValue'])
        assert value == result['finalAuthorSourceValue'] and result['finalIndependentSourceValuesMatchExactly'] is True
        assert result['eligibleForPositiveMoneyConfirmation'] is True and result['literalDashNullConfirmed'] is False
        assert amount(result['firstPeerSourceValue']) == amount(initial['literalImageValue'])
        if k in resolved_uncertainty:
            resolved = resolved_uncertainty[k]
            assert value == amount(resolved['currentSourceLiteral'])
            assert resolved['firstFrozenLiteral'] == initial['literalImageValue']
        else:
            assert initial['sourceUncertainty'] is None and value == amount(initial['literalImageValue'])
        author_first = amount(result['initialAuthorSourceValue'])
        assert raw_value(author_raw, k) == amount(choice['firstFrozenLiteral']) == author_first
        assert result['intermediateAuthorSourceValue'] == amount(choice['currentSourceLiteral'])
        if k == key(addition):
            assert value == amount(addition['correctedLiteralSourceValue'])
            assert result['intermediateAuthorSourceValue'] == addition['ownFirstFrozenAndSecondSourceRereadValue'] != value
        else:
            assert value == amount(choice['currentSourceLiteral'])
        author_errors += author_first != value
        peer_errors += amount(initial['literalImageValue']) != value
        image, native = target['actualWholePage600SourceView'], target['nativeOriginal300SourceView']
        assert image == result['actual600OriginalField'] and native == result['native300OriginalField']
        assert image['actual600PixelCropBox'] == [n * 2 for n in native['originalPdf300DpiPixelBox']]
        images += [(k[0], image, 600, image['actual600PixelCropBox']),
                   (k[0], native, 300, native['originalPdf300DpiPixelBox'])]
        facts.append((k, value, crop, image, raw_ref))
    assert (author_errors, peer_errors) == (3, 0)
    return facts, images, author_errors, peer_errors


def mode27(peer, load):
    """Late-discovered001 money coverage: preserve sparse first and three true errors."""
    raw_ref = peer['rootSourceFirstTranscript']
    first = load(raw_ref)
    packet = load(peer['sourceOnlyPacket'])
    choices = load(peer['onlyMatchingFiftyfiveComparisonAfterBothFreezes'])
    current = load(peer['independentCurrentActualSourceRereadBeforeRootChoices'])
    old_review = load(choices['originalSelected001Review'])
    old_amendments = load(choices['originalPostcomparisonSourceAmendments'])
    freeze = load(choices['originalSparseTranscriptFreezeReceipt'])
    same_source_documents(peer, first, packet, choices, current, old_review, old_amendments, freeze)
    assert peer['accepted'] is True and peer['closed'] is True and peer['unresolved'] == []
    assert current['rootCorrespondingFreshFiftyFiveChoicesOpened'] is False
    assert choices['rootCorrespondingFreshFiftyFiveChoicesOpened'] is False
    assert first['frozen'] is True and first['authorOrCandidateChoicesOpenedAtFreeze'] is False and first['correspondingIndependentCurrentRereadOpenedAtFreeze'] is False
    assert packet['sourceOnly'] is True and packet['expectedAuthorOrEngineValuesIncluded'] is False
    original, targets, author, source_current, final = [rows(d['rows']) for d in [first, packet, choices, current, peer]]
    assert len(final) == 55 and set(final) == set(original) == set(targets) == set(author) == set(source_current)
    source_manifest = load({'path': 'research/salaries/queue-completion-2026-11-01/phsa/batches/phsa-2019-20-batch-001-images.json',
                            'sha256': old_review['imageManifestSha256']})
    route = {r['sequence']: r for r in source_manifest['rows']}
    assert len(route) == len(source_manifest['rows']) == 400
    events = {}
    for event in csv.DictReader(io.StringIO(load(choices['originalSparseImageFirstTranscript'], False).decode()), delimiter='\t'):
        for f, col in [('name', 'nameLiteral'), ('remuneration', 'remunerationLiteral'), ('expenses', 'expensesLiteral')]:
            text = event[col]
            if not text:
                continue
            k = int(event['sequence']), f
            assert k not in events
            events[k] = text
    assert set(events) == {(seq, f) for seq, r in route.items() for f in r['reviewTargetFields']} and len(events) == 616
    assert freeze['rawTranscriptSha256'] == choices['originalSparseImageFirstTranscript']['sha256']
    assert freeze['fullCandidateAndRawOcrAlternativesNotOpenedBeforeThisFreeze'] is True
    old = {(r['physicalPage'], r['sourceRowOnPage']): r for r in old_review['resolutions']}
    assert len(old) == len(old_review['resolutions']) == 400
    prior_changes = {(r['sequence'], r['field']): r for r in old_amendments['reviewerFirstPassCorrections']}
    facts, images = [], []
    author_errors = peer_errors = 0
    corrections = rows(peer['oldSelectedSourceValueCorrections'])
    changed = set()
    for k, result in final.items():
        initial, target, choice, own_current = original[k], targets[k], author[k], source_current[k]
        integer_columns(initial, ['literalImageValue'])
        integer_columns(choice, ['originalSparseFirstValue', 'oldSelected001SourceValue', 'currentPersonalWhole600AndNative300Value'])
        integer_columns(own_current, ['literalImageValue'])
        integer_columns(result, ['rootFirstLiteralImageValue', 'oldSelected001SourceValue', 'literalImageValue'])
        crop = same_locator(initial, target, choice, own_current, result)
        seq = target['sequence']
        assert (route[seq]['physicalPage'], route[seq]['sourceRowOnPage']) == k[:2] and k[2] in route[seq]['reviewTargetFields']
        text = events[seq, k[2]]
        first_author = amount(text)
        old_value = amount(old[k[:2]]['resolvedValues'][k[2]])
        value = amount(own_current['literalImageValue'])
        assert first_author == amount(choice['originalSparseFirstLiteralText']) == choice['originalSparseFirstValue']
        assert choice['oldSelected001SourceValue'] == old_value == result['oldSelected001SourceValue']
        assert choice['currentPersonalWhole600AndNative300Value'] == result['literalImageValue'] == value
        assert choice['currentSourceUncertainty'] is own_current['sourceUncertainty'] is result['sourceUncertainty'] is None
        assert result['rootFirstLiteralImageValue'] == initial['literalImageValue']
        assert result['currentMatchesIndependentSourceRereadExactly'] is True
        assert result['earlierSelectedSourceValueCorrectionRequired'] is (old_value != value)
        if first_author != old_value:
            amendment = prior_changes[seq, k[2]]
            assert amount(amendment['frozenInitialReading']) == first_author
            assert amount(amendment['finalActualSourceReading']) == old_value
            assert choice['earlierPostcomparisonSourceCorrection'] == amendment
        else:
            assert choice['earlierPostcomparisonSourceCorrection'] is None
        if old_value != value:
            changed.add(k)
            assert k in corrections
            correction = corrections[k]
            integer_columns(correction, ['oldValue', 'currentLiteralValue'])
            assert correction == {'sequence': seq, 'physicalPage': k[0], 'sourceRowOnPage': k[1], 'field': k[2], 'oldValue': old_value, 'currentLiteralValue': value}
        if initial['literalImageValue'] != value:
            assert result['rootOwnFirstReadCorrection'] is True
            assert result['rootPostcomparisonOriginalSourceReread']
            assert seq == 392 and k[2] == 'expenses'
        else:
            assert result['rootOwnFirstReadCorrection'] is False
        author_errors += first_author != value
        peer_errors += initial['literalImageValue'] != value
        image, native = target['wholePage600Field'], target['native300Field']
        assert initial['wholePage600Field'] == own_current['wholePage600Field'] == result['wholePage600Field'] == image
        assert image['sourcePixelBox'] == [2*n for n in native['sourcePixelBox']]
        images += [(k[0], image, 600, image['sourcePixelBox']), (k[0], native, 300, native['sourcePixelBox'])]
        facts.append((k, value, crop, image, raw_ref))
    assert changed == set(corrections) and len(changed) == 3
    assert (author_errors, peer_errors) == (3, 1)
    return facts, images, author_errors, peer_errors


def verify(confirmation, source_id, source_sha, load):
    load = Pinned(load)
    assert type(confirmation['confirmedValue']) is int and confirmation['confirmedValue'] > 0
    ref = confirmation['confirmationLedger']
    assert ref['sha256'] in SPEC and (source_id, source_sha) == SOURCE
    document = load(ref)
    member = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
    assert document['confirmations'].count(member) == 1
    if ref['sha256'] in CACHE:
        assert member in CACHE[ref['sha256']]
        return
    mode, target_count, positive_count, author_count, peer_count = SPEC[ref['sha256']]
    assert all(type(document[name]) is int for name in ['completeFrozenSourceTargetFields', 'confirmedMonetaryFields', 'originalAuthorOwnSourceCorrections', 'originalPeerOwnSourceCorrections'])
    assert document['frozen'] is True
    assert document['adapter'] == ('source-first-provenance-correction-v1' if mode == 23 else 'count-independent-source-money-peer-v1')
    assert document['sourceReceiptSchema'] == {22: 'canonical-mixed-source-peer-with-unchanged-positive-money-v1', 23: 'complete-root-positive-table-with-one-independent-canonical-correction-v1', 25: 'complete-root-canonical-money-table-with-first-secondary-and-fresh-third-history-v1', 26: 'canonical-wholepage-literal-tuple-money-peer-v1', 27: 'sparse-author-source-events-and-current-wholepage-independent-peer-v1'}[mode]
    assert (document['completeFrozenSourceTargetFields'], document['confirmedMonetaryFields'],
            document['originalAuthorOwnSourceCorrections'], document['originalPeerOwnSourceCorrections']) == (target_count, positive_count, author_count, peer_count)
    for reference in document['peerInputs']:
        load(reference, False)
    peer_ref = document['peerInputs'][0]
    peer = load(peer_ref)
    source_identity(peer, source_id, source_sha)
    facts, images, a, b = {22: mode22, 23: mode23, 25: mode25, 26: mode26, 27: mode27}[mode](peer, load)
    if mode == 23:
        previous_ref = document['previousConfirmationLedger']
        assert previous_ref == {'path': 'research/salaries/queue-completion-2026-11-01/phsa/triangulation/money-peer-confirmations-023.json',
                                'sha256': '34fd632d9beca3d6c5c13860dfe723ac85c6c3709d8513eed667fb8696dc542c'}
        previous = load(previous_ref)
        expected_document = copy.deepcopy(previous)
        fresh = peer['freshColdIndependent394']
        changed = 0
        for row in expected_document['confirmations']:
            assert row['imageFirstTranscript'] == fresh
            if key(row) != (88, 13, 'remuneration'):
                row['imageFirstTranscript'] = peer['originalRootFirstRaw']
                changed += 1
        assert changed == 52
        expected_document.update(adapter='source-first-provenance-correction-v1', supersededAdapter=previous['adapter'],
                                 previousConfirmationLedger=previous_ref, sourceFirstPointerCorrections=52,
                                 originalRoot53FirstTranscript=peer['originalRootFirstRaw'], independentCold394FirstTranscript=fresh,
                                 peerInputs=previous['peerInputs'] + [previous_ref],
                                 provenanceCorrectionReason=document['provenanceCorrectionReason'])
        assert document['provenanceCorrectionReason'] and expected_document == document

    overlay_ref = document['confirmations'][0]['effectiveAuthorOverlay']
    overlay = load(overlay_ref)
    source_identity(overlay, source_id, source_sha)
    assert overlay['batch'] == peer['batch']
    overlay_rows = rows([{**r, 'field': f} for r in overlay['overlays'] for f in r['reviewedFields']])
    expected = []
    for locator, value, crop, image, raw_ref in facts:
        assert locator[2] in ['remuneration', 'expenses'] and type(value) is int and value > 0
        row = overlay_rows[locator]
        assert row['resolvedRow'][3 if locator[2] == 'remuneration' else 4] == value
        assert row['cropSha256'] == crop
        expected.append({'sourceId': source_id, 'sourceSha256': source_sha,
                         'physicalPage': locator[0], 'sourceRowOnPage': locator[1], 'field': locator[2],
                         'confirmedValue': value, 'effectiveAuthorOverlay': overlay_ref,
                         'peerComparison': peer_ref, 'freshSourceImage': image,
                         'imageFirstTranscript': raw_ref})
    assert expected == document['confirmations'] and len(expected) == positive_count
    pixels(images, source_id, source_sha, load)
    CACHE[ref['sha256']] = expected
