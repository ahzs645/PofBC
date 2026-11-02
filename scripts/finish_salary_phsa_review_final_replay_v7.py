#!/usr/bin/env python3
"""Independent raw-page/explicit-overlay replay of one complete PHSA candidate.

Does not import the author's finalizer, ledger or resolution implementation.
Writes only a new independent review receipt. No candidate/raw data mutations.
Version7 independently checks current canonical source decisions, immutable overlay/adoption selections and unchanged-money rebasing. Earlier version1–6 files remain frozen. No producer/finalizer/promotion implementation imports.
"""
import argparse
import collections
import copy
import csv
import gzip
import hashlib
import io
import importlib.util
import json
import re
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/queue-completion-2026-11-01'
COLLECTION = ROOT / 'research/salaries/queue-completion-phsa'
FIELDS = {'name': 1, 'remuneration': 3, 'expenses': 4}
CONFIDENCE = {
    'name': {'tesseract-name-confidence-below-85', 'rapid-name-confidence-below-0.98'},
    'remuneration': {'tesseract-pay-confidence-below-90', 'rapid-pay-confidence-below-0.98'},
    'expenses': {'tesseract-expense-confidence-below-90', 'rapid-expense-confidence-below-0.98'},
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)


_ARCHIVED_IMAGE_ALIASES = {}
_ORIGINAL_PDF_REFERENCES = set()

def pinned(reference, parse=True):
    path = ROOT / reference['path']
    if not path.resolve().is_relative_to(ROOT):
        assert parse is False, 'No external parsed evidence'
        identity = reference['path'], reference['sha256']
        if identity in _ORIGINAL_PDF_REFERENCES:
            data = path.read_bytes()
            assert digest(data) == reference['sha256'] and data.startswith(b'%PDF-')
            return data
        path = _ARCHIVED_IMAGE_ALIASES[identity]
    assert path.resolve().is_relative_to(ROOT)
    assert digest(path.read_bytes()) == reference['sha256'], str(path)
    return read(path) if parse else path.read_bytes()



_ADDITIONAL_MONEY_LEDGERS = {
    '1438b41ecb02f464e1af7e7f8149a86ae003aa887b3077a92cada8566389a44b': 'count-independent-source-money-peer-v1',
    'e457c434b39b590ecf922c4dc7e38ae6c0f930ce88e7850f90969434cb4db0bb': 'direct-scoped-source-peer-v1',
}
_ADDITIONAL_MONEY_CACHE = {}


def independent_additional_money_peer(confirmation, source_id, source_sha):
    """Two exact frozen FY22 schemas, independently replayed, with no imported producer."""
    reference = confirmation['confirmationLedger']
    ledger = pinned(reference)
    assert reference['sha256'] in _ADDITIONAL_MONEY_LEDGERS
    assert ledger['adapter'] == _ADDITIONAL_MONEY_LEDGERS[reference['sha256']]
    assert source_id == 'phsa-2022-23'
    expected = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
    assert ledger['confirmations'].count(expected) == 1
    if reference['sha256'] not in _ADDITIONAL_MONEY_CACHE:
        import fitz
        from PIL import Image
        assert ledger['frozen'] is True
        for entry in ledger['peerInputs']:
            pinned(entry, False)
        raw = pinned(confirmation['imageFirstTranscript'])
        assert raw['sourceId'] == source_id and raw['sourceSha256'] == source_sha
        assert raw['frozenBeforeRootAuthorOrOcrChoices'] is True and raw['fullBatchCandidateOpened'] is False
        packet = pinned(raw['sourceOnlyPacket'])
        assert raw['sourceOnlyPacket'] in ledger['peerInputs']
        assert packet['sourceId'] == source_id and packet['sourceSha256'] == source_sha
        assert raw['batch'] == packet['batch']
        targets = {(r['sequence'], r['field']): r for r in packet['rows']}
        readings = {(r['sequence'], r['field']): r for r in raw['entries']}
        assert len(targets) == len(packet['rows']) == len(readings) == len(raw['entries'])
        assert set(targets) == set(readings)
        batch = read(AREA / 'phsa' / 'batches' / (packet['batch'].rsplit('-', 1)[0] + '-batch-' + packet['batch'].rsplit('-', 1)[1] + '-images.json'))
        originals = {r['sequence']: r for r in batch['rows']}
        assert batch['sourceId'] == source_id and batch['sourceSha256'] == source_sha
        mode = ledger['adapter']
        if mode == 'count-independent-source-money-peer-v1':
            peer = pinned(confirmation['peerComparison'])
            assert peer['sourceId'] == source_id and peer['sourceSha256'] == source_sha
            assert peer['independentImageFirstTranscript'] == confirmation['imageFirstTranscript']
            assert peer['all12FinalSourceValuesConfirmed'] is True
            compared = {(r['sequence'], r['field']): r for r in peer['rows']}
            assert len(compared) == len(peer['rows']) == len(targets) == 12
            assert set(compared) == set(targets)
            for k, reading in readings.items():
                assert compared[k]['confirmedSourceReading'] == reading['literalSourceValue']
                assert compared[k]['rawTranscriptUnchanged'] is True
            assert ledger['completeFrozenSourceTargetFields'] == 12 and ledger['confirmedMonetaryFields'] == 4
            pixel_rows = None
        else:
            assert confirmation['peerComparison'] == confirmation['imageFirstTranscript']
            proof = pinned(ledger['pixelProof'])
            assert proof['sourceId'] == source_id and proof['sourceSha256'] == source_sha
            assert proof['sourcePeer'] == confirmation['imageFirstTranscript']
            assert proof['sourceOnlyPacket'] == raw['sourceOnlyPacket']
            pixel_rows = {(r['sequence'], r['field']): r for r in proof['rows']}
            assert len(pixel_rows) == len(proof['rows']) == len(targets) == 4
            assert set(pixel_rows) == set(targets)
            assert ledger['completeFrozenSourcePeerFields'] == 4 and ledger['confirmedMonetaryFields'] == 2
        original_pdf = Path('/tmp/queue-completion-phsa/originals') / (source_id + '.pdf')
        assert digest(original_pdf.read_bytes()) == source_sha
        document = fitz.open(original_pdf)
        expected_money = {}
        for k, target in targets.items():
            original = originals[target['sequence']]
            assert (target['physicalPage'], target['sourceRowOnPage']) == (original['physicalPage'], original['sourceRowOnPage'])
            assert target.get('originalCropSha256', target.get('cropSha256')) == original['cropSha256']
            assert target['field'] in original['reviewTargetFields']
            image_reference = target.get('actual600DpiSourceView', target.get('actualOriginal600DpiField'))
            image_bytes = pinned(image_reference, False)
            if pixel_rows is None:
                # The archived root FY22 batch001 pay clips use the native pay column
                # and the exact immutable row y bounds. Only these four money cells.
                if target['field'] not in ['remuneration', 'expenses']:
                    continue
                box = [1693, original['cropRectOriginal300DpiPixels'][1], 2114, original['cropRectOriginal300DpiPixels'][3]]
            else:
                pixel = pixel_rows[k]
                assert pixel['actualOriginal600DpiField'] == image_reference
                assert (pixel['physicalPage'], pixel['sourceRowOnPage']) == (target['physicalPage'], target['sourceRowOnPage'])
                assert pixel['independentlyReproducedOriginalPixelsExact'] is True
                box = pixel['original300DpiPixelBox']
            pixmap = document[target['physicalPage'] - 1].get_pixmap(dpi=600, alpha=False, clip=fitz.Rect(*[v * 72 / 300 for v in box]))
            reproduced = Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples)
            archived = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            assert reproduced.size == archived.size and reproduced.tobytes() == archived.tobytes(), ('Original money source pixels differ', k)
            if target['field'] not in ['remuneration', 'expenses']:
                continue
            reading = readings[k]
            value = reading['literalSourceValue']
            assert type(value) is int and value > 0
            assert reading.get('realUncertainty') is None and reading.get('visibleAlternatives') == []
            location = (target['physicalPage'], target['sourceRowOnPage'], target['field'])
            expected_money[location] = (value, image_reference)
        document.close()
        confirmations = {(r['physicalPage'], r['sourceRowOnPage'], r['field']): r for r in ledger['confirmations']}
        assert len(confirmations) == len(ledger['confirmations']) == len(expected_money)
        assert set(confirmations) == set(expected_money)
        for key, item in confirmations.items():
            assert item['sourceId'] == source_id and item['sourceSha256'] == source_sha
            assert item['confirmedValue'] == expected_money[key][0]
            assert item['freshSourceImage'] == expected_money[key][1]
            assert item['imageFirstTranscript'] == confirmation['imageFirstTranscript']
            assert item['peerComparison'] == confirmation['peerComparison']
        _ADDITIONAL_MONEY_CACHE[reference['sha256']] = confirmations
    return ledger


_FY21_LEDGERS = {
 '32481670b7c7d7cdba333795d41d6906a27daea9b31ad0a6508b8584874714c6': ('literal-source-table-money-peer-v1', 8, 8),
 'b2f9eb63ad0aaaa38c47adff5e18ed01e11da815727150ce9c257c21d58c51d9': ('count-independent-source-money-peer-v1', 1, 1),
 'ba7e5902ad5a8240d90fb7ef78c6a6ef539c533e1ca7ab1a0570ad88c7db3817': ('count-independent-source-money-peer-v1', 2, 2),
 '6ea7b9126af181f5572a716b1237f08cce62f63f6aad381b18c64237ca08d143': ('direct-scoped-source-peer-v2', 8, 2),
 '7512fd0d496e1f7674a1bc1bc17814b58ff838710d74d0d7c97f388e411859f1': ('count-independent-source-money-peer-v1', 4, 4),
}
_FY21_CACHE = {}

def independent_fy21_money_peer(confirmation, source_id, source_sha):
    """Replay only five known complete frozen source scopes; no producer imports."""
    import fitz
    from PIL import Image
    ref = confirmation['confirmationLedger']
    assert ref['sha256'] in _FY21_LEDGERS
    assert source_id == 'phsa-2021-22' and source_sha == '944c99fa7b7ede643cb4c426a5e9ab30aa906d8f81fda379f0206e4b0cdcd25c'
    ledger = pinned(ref)
    assert confirmation['sourceId'] == source_id and confirmation['sourceSha256'] == source_sha
    mode, target_count, money_count = _FY21_LEDGERS[ref['sha256']]
    assert ledger['frozen'] is True and ledger['adapter'] == mode
    expected = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
    assert ledger['confirmations'].count(expected) == 1
    if ref['sha256'] in _FY21_CACHE:
        return ledger
    for peer_input in ledger['peerInputs']:
        pinned(peer_input, False)
    raw = pinned(confirmation['imageFirstTranscript'])
    peer = pinned(confirmation['peerComparison'])
    assert raw['frozen'] is True and peer['frozen'] is True
    raw_rows = raw['rows']
    if ref['sha256'].startswith('6ea7'):
        assert raw['blindness']['authorScopedProposalsOpened'] is False
        assert raw['blindness']['fullCandidateOpened'] is False
        assert raw['blindness']['correspondingExpectedValuesSupplied'] is False
        assert confirmation['peerComparison'] == confirmation['imageFirstTranscript']
        packet_ref = raw['input']
    else:
        flag = 'candidateOrAuthorValuesOpened' if target_count == 1 else 'correspondingChoicesOpened'
        assert raw[flag] is False
        packet_ref = raw['sourceOnlyPacket']
        for key, item in peer.items():
            if isinstance(item, dict) and set(['path', 'sha256']) <= set(item):
                pinned(item, False)
    assert raw.get('sourceSha256', source_sha) == source_sha
    packet = pinned(packet_ref)
    assert packet_ref in ledger['peerInputs'] or mode == 'direct-scoped-source-peer-v2'
    targets = packet.get('rows', [packet.get('field')])
    assert len(targets) == len(raw_rows) == target_count
    key = lambda r: (r['sequence'], r['field'])
    target_map = {key(r): r for r in targets}
    reading_map = {key(r): r for r in raw_rows}
    peer_map = {key(r): r for r in peer['rows']}
    assert len(target_map) == len(reading_map) == len(peer_map) == target_count
    assert set(target_map) == set(reading_map) == set(peer_map)
    proof_rows = None
    if mode == 'direct-scoped-source-peer-v2':
        pixel_proof = pinned(ledger['pixelProof'])
        assert pixel_proof['sourcePeer'] == confirmation['imageFirstTranscript']
        assert pixel_proof['sourceOnlyPacket'] == packet_ref
        proof_rows = {key(r): r for r in pixel_proof['rows']}
        assert len(proof_rows) == len(pixel_proof['rows']) == target_count and set(proof_rows) == set(target_map)
    original = Path('/tmp/queue-completion-phsa/originals') / (source_id + '.pdf')
    assert digest(original.read_bytes()) == source_sha
    document = fitz.open(original)
    expected_money = {}
    for k, target in target_map.items():
        reading, compared = reading_map[k], peer_map[k]
        location = (target['physicalPage'], target['sourceRowOnPage'], target['field'])
        assert (reading['physicalPage'], reading['sourceRowOnPage'], reading['field']) == location
        assert (compared['physicalPage'], compared['sourceRowOnPage'], compared['field']) == location
        assert target.get('sourceSha256', packet.get('sourceSha256', source_sha)) == source_sha
        if mode == 'direct-scoped-source-peer-v2':
            image_ref = target['actual1200Source']
            clip, dpi, crop = target['actualPdfPointClip'], 1200, None
            pixel = proof_rows[k]
            assert pixel['actualOriginalSourceField'] == image_ref
            assert pixel['actualPdfPointClip'] == clip and pixel['dpi'] == dpi
            assert pixel['independentlyReproducedOriginalPixelsExact'] is True
            assert reading['cropSha256'] == target['originalFullRowCropSha256'] == pixel['originalFullRowCropSha256']
        elif target_count == 8:
            image_ref = target['actualPdf600View']
            clip = [x * 72 / 300 for x in target['original300DpiPixelBox']]
            dpi, crop = 600, None
            assert reading['actualPdf600View'] == image_ref
        elif target_count == 1:
            image_ref = reading['actualOriginal1200SourceField']
            geom = target['actualSourceField']
            assert image_ref['sha256'] == geom['sha256']
            clip, dpi, crop = geom['clipPoints'], geom['dpi'], geom['whiteOnlyCropBox']
            assert reading['uncertain'] is False and reading['cropSha256'] == target['cropSha256']
        elif target_count == 2:
            image_ref = target['actual1200Source']
            clip, dpi, crop = image_ref['actualPdfPointClip'], image_ref['dpi'], image_ref['whiteBoundaryCrop']
            assert reading['actual1200Source'] == image_ref
            assert reading['cropSha256'] == target['cropSha256']
        else:
            assert target_count == 4
            image_ref = target['actual1200SourceField']
            clip = [x * 72 / 300 for x in image_ref['original300DpiPixelBox']]
            dpi, crop = 1200, None
            assert reading['actual1200SourceField'] == image_ref
            assert compared['originalFullRowCropSha256'] == target['originalFullRowCrop']['sha256']
        rendered = document[target['physicalPage'] - 1].get_pixmap(dpi=dpi, alpha=False, clip=fitz.Rect(clip))
        reproduced = Image.frombytes('RGB', (rendered.width, rendered.height), rendered.samples)
        if crop is not None:
            reproduced = reproduced.crop(crop)
        archived = Image.open(io.BytesIO(pinned(image_ref, False))).convert('RGB')
        assert reproduced.size == archived.size and reproduced.tobytes() == archived.tobytes(), ('FY21 original pixels differ', k)
        if target['field'] not in ['remuneration', 'expenses']:
            continue
        staged_page = read(COLLECTION / 'evidence' / (source_id + '-rows-p%03d.json.gzip' % target['physicalPage']))
        staged_row = next(r for r in staged_page['rows'] if r['sourceRowOnPage'] == target['sourceRowOnPage'])
        assert clip[1] * 300 / 72 <= staged_row['sourceNameBand']['center'] < clip[3] * 300 / 72
        assert [round(clip[0]*300/72), round(clip[2]*300/72)] == [1775, 2140]
        if mode == 'direct-scoped-source-peer-v2':
            value = reading['value']
            assert reading['uncertain'] is False and reading['visibleAlternatives'] == [value]
            final_value = value
        elif target_count == 1:
            value, final_value = reading['rootFirstImageReading'], compared['rootCurrentSourceReading']
            assert compared['authorCurrentSourceReading'] == final_value
            assert compared['allPositiveLiteralValuesMatch'] is True
        else:
            value = reading['literalImageValue']
            assert reading['uncertainty'] is None
            final_value = compared.get('peerFinalValue', compared.get('finalPeerSourceValue'))
            assert final_value == compared.get('authorFinalValue', compared.get('finalAuthorSourceValue'))
        assert type(value) is int and value > 0 and value == final_value
        expected_money[location] = (final_value, image_ref)
    document.close()
    actual = {(r['physicalPage'], r['sourceRowOnPage'], r['field']): r for r in ledger['confirmations']}
    assert len(actual) == len(ledger['confirmations']) == len(expected_money) == money_count
    assert set(actual) == set(expected_money)
    for location, item in actual.items():
        assert item['sourceId'] == source_id and item['sourceSha256'] == source_sha
        assert item['confirmedValue'] == expected_money[location][0]
        assert item['freshSourceImage']['sha256'] == expected_money[location][1]['sha256']
        assert item['imageFirstTranscript'] == confirmation['imageFirstTranscript']
        assert item['peerComparison'] == confirmation['peerComparison']
        pinned(item['freshSourceImage'], False)
    _FY21_CACHE[ref['sha256']] = actual
    return ledger


def normalized_name(value):
    return re.sub(r'\s*,\s*', ',', re.sub(r'\s+', ' ', value.strip()))


def source_case_name(case):
    for key in ['chosenContextualTranscription', 'resolvedContextualName', 'proposedName', 'chosenName', 'primaryName', 'primary']:
        if key in case:
            return case[key]
    raise AssertionError('No explicit qualified name primary')


def independent_review_overlay(reference, source_id, source_sha):
    overlay = pinned(reference)
    assert overlay['sourceId'] == source_id and overlay['sourceSha256'] == source_sha
    if overlay.get('kind') == 'canonical-source-typography-metadata-supplement-revision':
        original_ref = overlay['originalSpecialSupplement']
        assert original_ref == {'path': str((AREA / 'phsa/overlays/phsa-2015-16-hyphen-name-supplement-001.json').relative_to(ROOT)),
                                'sha256': '74a0cdd987ffb09b309faaaf79a9e44778d22dc12c6398384c57a97dd28335fa'}
        original = pinned(original_ref)
        assert source_id == 'phsa-2015-16' and original['kind'] == 'expressly-reserved-three-case-hyphen-source-name-supplement'
        old_fields = independent_review_overlay(original_ref, source_id, source_sha)
        assert set(old_fields) == {(40, 15, 'name')} and len(overlay['overlays']) == 1
        _, adopted_ref = independent_adoption_selection(overlay['rootAdoptionSupersession'], source_id, source_sha)
        adoption = pinned(adopted_ref)
        ledger = pinned(adoption['exactCaseLedger'])
        cases = ledger.get('qualifications', ledger.get('cases'))
        assert len(cases) == 1 and (cases[0]['physicalPage'], cases[0]['sourceRowOnPage']) == (40, 15)
        current = overlay['overlays'][0]
        qualification = current['nameTypographyQualification']
        assert current['reviewedFields'] == ['name'] and current['resolvedRow'] == original['overlays'][0]['resolvedRow']
        assert qualification['chosenName'] == source_case_name(cases[0]) == current['resolvedRow'][1]
        assert set(qualification['visibleAlternatives']) | {qualification['chosenName']} == set(case_family(cases[0]))
        assert source_case_crop(cases[0]) == current['cropSha256']
        expected = copy.deepcopy(original)
        expected['overlays'][0]['nameTypographyQualification'] = qualification
        expected.update(kind='canonical-source-typography-metadata-supplement-revision',
                        originalSpecialSupplement=original_ref,
                        rootAdoptionSupersession=overlay['rootAdoptionSupersession'],
                        canonicalMetadataOnlyNoLiteralMoneyOrScopeChange=True)
        assert overlay == expected, 'Special supplement changed beyond exact name-case metadata'
        return {(40, 15, 'name'): {'value': current['resolvedRow'][1], 'row': current, 'overlay': reference}}
    review_raw = pinned(overlay['reviewInput'], False)
    kind = overlay.get('kind')
    review = None
    originals = {}
    if kind == 'complete-first-table-independent-image-benchmark-review':
        literal = list(csv.DictReader(io.StringIO(review_raw.decode()), delimiter='\t'))
        readings = {(int(r['physicalPage']), int(r['sourceRowOnPage'])): r for r in literal}
    elif overlay.get('frozenBatch'):
        batch = pinned(overlay['frozenBatch'])
        images = pinned(overlay['imageManifest'])
        assert batch['sourceId'] == source_id and images['sourceId'] == source_id
        assert batch['sourceSha256'] == images['sourceSha256'] == source_sha
        originals = {(r['physicalPage'], r['sourceRowOnPage']): r for r in batch['rows']}
        assert set(originals) == {(r['physicalPage'], r['sourceRowOnPage']) for r in images['rows']}
        review = json.loads(review_raw)
        assert review['sourceId'] == source_id and review['sourceSha256'] == source_sha
        assert review.get('unresolvedRows') in [[], 0]
        readings = {(r['physicalPage'], r['sourceRowOnPage']): r for r in review['resolutions']}
        assert len(readings) == len(review['resolutions']) == len(originals)
        if review.get('rawTranscriptPath'):
            pinned({'path': review['rawTranscriptPath'], 'sha256': review['rawTranscriptSha256']}, False)
    elif kind == 'complete-sixteen-case-additive-mac-prefix-name-review':
        review = json.loads(review_raw)
        assert review['reviewer'] == '/root/held_health_review'
        assert review.get('unresolvedRows') in [[], 0]
        packet = pinned(overlay['sourceOnlyPacket'])
        peer = pinned(overlay['independentFreshPeer'])
        assert overlay['reviewInput']['sha256'] == 'e7e9dbb35343baf591d1bc1cf968e5c12d84a998c580123d2c4acff0b6746cc3'
        assert overlay['independentFreshPeer']['sha256'] == '44da96133b4f26b1f97f97c3bcf2d39b228b208f885aff0c7669cd37730b0f36'
        readings = {(r['physicalPage'], r['sourceRowOnPage']): r for r in review['resolutions'] if r['sourceId'] == source_id}
        assert all(r['sourceSha256'] == source_sha for r in readings.values())
        assert len(readings) == overlay['resolvedRows']
    else:
        assert kind == 'expressly-reserved-three-case-hyphen-source-name-supplement'
        assert overlay['noMoneyFieldsReviewedOrChanged']
        if overlay.get('sourceOnlyTranscript'):
            pinned(overlay['sourceOnlyTranscript'], False)
        readings = None
    result = {}
    seen = set()
    for row in overlay['overlays']:
        key = row['physicalPage'], row['sourceRowOnPage']
        assert key not in seen
        seen.add(key)
        requested = row['reviewedFields']
        assert len(requested) == len(set(requested)) and set(requested) <= set(FIELDS)
        before, after = row['rawCandidateRow'], row['resolvedRow']
        assert len(before) == len(after) == 6
        assert [before[i] for i in [0, 2, 5]] == [after[i] for i in [0, 2, 5]]
        for field, index in FIELDS.items():
            if field not in requested:
                assert before[index] == after[index]
        if originals:
            original = originals[key]
            reading = readings[key]
            assert requested == original['reviewTargetFields'] == reading['reviewTargetFields']
            assert row['cropSha256'] == original['cropSha256'] == reading['cropSha256']
            assert before == original['rawCandidateRow']
            assert set(reading['resolvedValues']) == set(requested)
            assert row['resolutionStatus'] == reading['status']
            for field in requested:
                assert after[FIELDS[field]] == reading['resolvedValues'][field]
        elif kind == 'complete-first-table-independent-image-benchmark-review':
            reading = readings[key]
            assert after[1] == reading['name']
            assert after[3] == int(reading['remunerationLiteral'].replace(',', ''))
            expense = reading['expensesLiteral']
            assert after[4] == (None if expense in ['-', '–', '—'] else int(expense.replace(',', '')))
            assert set(requested) == set(FIELDS)
        elif kind == 'complete-sixteen-case-additive-mac-prefix-name-review':
            reading = readings[key]
            assert requested == reading['reviewTargetFields'] == ['name']
            assert row['cropSha256'] == reading['cropSha256']
            assert before == reading['rawCandidateRow'] and after == reading['resolvedRow']
            assert after[1] == reading['resolvedValues']['name']
            assert row['resolutionStatus'] == reading['status']
            pinned(row['retainedSourceNameView'], False)
            if row.get('retainedOriginalSourceContext'):
                pinned(row['retainedOriginalSourceContext'], False)
            else:
                # Serif exact cases have a retained name asset and reconstructible
                # context in the immutable source-only packet, without a redundant asset.
                from PIL import Image
                packet_rows = [r for r in packet['rows'] if r['sourceId'] == source_id and (r['physicalPage'], r['sourceRowOnPage']) == key]
                assert len(packet_rows) == 1
                packet_row = packet_rows[0]
                image_path = Path(packet_row['actualSourceImagePath'])
                assert digest(image_path.read_bytes()) == packet_row['actualSourceImageSha256']
                staged_page = pinned(packet_row['pageEvidence'])
                assert staged_page['sourceId'] == source_id and staged_page['sourceSha256'] == source_sha
                assert staged_page['sourceImageSha256'] == packet_row['actualSourceImageSha256']
                context_ref = packet_row['adjacentOriginalContext']
                context_png = io.BytesIO()
                Image.open(image_path).crop(tuple(context_ref['original300DpiPixelBox'])).save(context_png, format='PNG')
                assert digest(context_png.getvalue()) == context_ref['sha256']
        else:
            assert requested == ['name']
        for field in requested:
            result[(*key, field)] = {'value': after[FIELDS[field]], 'row': row, 'overlay': reference}
    assert len(seen) == overlay['resolvedRows']
    if originals:
        assert seen == set(originals)
    return result


def exact_reference(reference):
    assert isinstance(reference, dict) and set(reference) == {'path', 'sha256'}
    path, sha = reference['path'], reference['sha256']
    assert isinstance(path, str) and path and not Path(path).is_absolute()
    assert '..' not in Path(path).parts and '\\' not in path
    assert isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha)
    return path, sha


def unique_rows(rows, key):
    assert isinstance(rows, list)
    result = {key(row): row for row in rows}
    assert len(result) == len(rows), 'Repeated source field/case'
    return result


def independent_ordinary_selection(reference, source_id, source_sha, load=pinned):
    """Check one exact old/new edge without reading a mutable selector directory."""
    exact_reference(reference)
    selector = load(reference)
    assert selector['sourceId'] == source_id and selector['sourceSha256'] == source_sha
    assert selector['oldFrozenFilesRemainUnchanged'] is True and selector['reason']
    before_ref, after_ref = selector['supersededOverlay'], selector['effectiveOverlay']
    assert exact_reference(before_ref) != exact_reference(after_ref)
    before, after = load(before_ref), load(after_ref)
    if selector.get('selectionKind') == 'canonical-supplement-name-metadata-selection':
        assert before_ref['sha256'] == '74a0cdd987ffb09b309faaaf79a9e44778d22dc12c6398384c57a97dd28335fa'
        assert before['kind'] == 'expressly-reserved-three-case-hyphen-source-name-supplement'
        assert after['kind'] == 'canonical-source-typography-metadata-supplement-revision'
        assert after['originalSpecialSupplement'] == before_ref
        independent_review_overlay(after_ref, source_id, source_sha)
        return before_ref, after_ref, before, after
    for field in ['sourceId', 'sourceSha256', 'batch', 'resolvedRows', 'frozenBatch', 'imageManifest']:
        assert before[field] == after[field]
    assert (before['sourceId'], before['sourceSha256'], before['batch']) == (source_id, source_sha, selector['batch'])
    assert len(before['overlays']) == len(after['overlays']) == before['resolvedRows']
    seen = set()
    for a, b in zip(before['overlays'], after['overlays']):
        key = a['physicalPage'], a['sourceRowOnPage']
        assert key not in seen
        seen.add(key)
        for field in ['physicalPage', 'sourceRowOnPage', 'reviewedFields', 'rawCandidateRow',
                      'pageEvidencePath', 'pageEvidenceSha256', 'cropSha256']:
            assert a[field] == b[field], 'Ordinary revision widened original review scope'
        for index in [0, 2, 5]:
            assert a['resolvedRow'][index] == b['resolvedRow'][index]
        for field, index in FIELDS.items():
            if field not in a['reviewedFields']:
                assert a['resolvedRow'][index] == b['resolvedRow'][index]
    return before_ref, after_ref, before, after


def independent_ordinary_selections(provenance, source_id, source_sha):
    selected = {exact_reference(ref) for ref in provenance['manualOverlayInputs']}
    assert len(selected) == len(provenance['manualOverlayInputs'])
    edges, incoming = {}, set()
    for ref in provenance.get('manualOverlaySupersessions', []):
        a, b, _, _ = independent_ordinary_selection(ref, source_id, source_sha)
        old, new = exact_reference(a), exact_reference(b)
        assert old not in edges and new not in incoming, 'Conflicting ordinary selection'
        edges[old] = new
        incoming.add(new)
    for start in edges:
        trail, current = set(), start
        while current in edges:
            assert current not in trail, 'Cyclic ordinary selection'
            trail.add(current)
            current = edges[current]
        assert current in selected and not selected.intersection(trail)
    return len(edges)


def case_family(case):
    if 'visibleAlternatives' in case:
        value = case['visibleAlternatives']
    elif 'visibleIOrLowerLAlternatives' in case:
        value = [source_case_name(case)] + case['visibleIOrLowerLAlternatives']
    elif 'typographicallyPossibleAlternative' in case:
        value = [source_case_name(case), case['typographicallyPossibleAlternative']]
    else:
        value = [source_case_name(case), case['alternative']]
    assert isinstance(value, list) and value and all(isinstance(v, str) and v for v in value)
    assert len(set(value)) == len(value)
    return value


def source_case_crop(case):
    value = case.get('cropSha256', case.get('originalFullRowCropSha256',
                                         case.get('actualSourceEvidence', {}).get('originalFullRowCropSha256')))
    assert isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)
    return value


def independent_scoped_adoption_cases(adoption, document):
    """Select only exact root-declared cases from a pinned mixed source ledger."""
    if isinstance(adoption.get('cases'), list) and isinstance(adoption.get('closedCases'), list):
        declared = adoption['cases'] + adoption['closedCases']
    else:
        declared = adoption.get('exactCases', adoption.get('closedCases'))
    candidates = []
    for name in ['qualifications', 'cases', 'sourceTypographyQualifications', 'sourceNameSegmentationExceptions',
                 'separateClosedRrMExceptionsAwaitingExactRootAdoption']:
        if isinstance(document.get(name), list):
            part = unique_rows(document[name], lambda c: (c['physicalPage'], c['sourceRowOnPage']))
            candidates.extend(part.values())
    all_cases = {}
    for case in candidates:
        k = case['physicalPage'], case['sourceRowOnPage']
        assert k not in all_cases or all_cases[k] == case, 'Conflicting source case aliases'
        all_cases[k] = case
    if not adoption:
        return list(all_cases.values())
    if not isinstance(declared, list):
        for name in ['qualifications', 'cases', 'sourceTypographyQualifications', 'sourceNameSegmentationExceptions']:
            if isinstance(document.get(name), list):
                return document[name]
        raise AssertionError('No source case category for exact adoption')
    selected = unique_rows(declared, lambda c: (c['physicalPage'], c['sourceRowOnPage']))
    assert set(selected) <= set(all_cases)
    for k, root_case in selected.items():
        original = all_cases[k]
        assert source_case_name(root_case) == source_case_name(original)
        assert set(case_family(root_case)) == set(case_family(original))
        assert source_case_crop(root_case) == source_case_crop(original)
    return [all_cases[k] for k in selected]


def independent_exact_retirements(selector, before_adoption, after_adoption, before_cases, load=pinned):
    """No general deletion rule: three immutable source/root/crop-bound cases only."""
    declared = selector.get('authorizedRetiredNameCases', [])
    if not declared:
        return {}
    allowed = {}
    for number, sha in [(1, '07b1657c0fc70ce2f654dde478fdc2749ace31bebff70db8df9df3f3c19dfb73'),
                        (2, '34aeabd2a62d30f28a64bc5bb4821ed209664b7dc422cb1b55346bf4a94e47a3')]:
        ref = {'path': str((AREA / f'phsa/source-name-exact-retirement-policy-{number:03d}.json').relative_to(ROOT)), 'sha256': sha}
        policy = load(ref)
        assert policy['frozen'] is True and policy['noGenericCaseDeletion'] is True
        assert policy['noFinancialOrOtherFieldAuthority'] is True
        for case in policy['approvedRetirements']:
            k = case['sourceId'], case['physicalPage'], case['sourceRowOnPage']
            assert k not in allowed
            allowed[k] = case, ref
    assert after_adoption['acceptedCaseRetirements'] == declared
    result = {}
    for case in declared:
        k = case['physicalPage'], case['sourceRowOnPage']
        expected, policy_ref = allowed[(case['sourceId'], *k)]
        assert case == expected and k not in result
        assert selector['retirementImplementationPolicy'] == after_adoption['retirementImplementationPolicy'] == policy_ref
        assert case['originalRootAdoption'] == selector['supersededRootAdoption']
        assert case['originalCaseLedger'] == selector['supersededCaseLedger']
        assert case['allowedFields'] == ['name'] and case['requiresDirectLiteral'] is True
        assert tuple(case[n] for n in ['sourceId', 'sourceSha256', 'batch']) == tuple(before_adoption[n] for n in ['sourceId', 'sourceSha256', 'batch'])
        old = before_cases[k]
        assert source_case_name(old) == case['oldPrimary'] and case_family(old) == case['oldVisibleAlternatives']
        assert source_case_crop(old) == case['originalFullRowCropSha256']
        for ref in [case['currentSourceDecision'], case['independentSourcePeer']]:
            document = load(ref)
            assert (document['sourceId'], document['sourceSha256']) == (case['sourceId'], case['sourceSha256'])
            matches = [row for row in document['rows'] if (row['physicalPage'], row['sourceRowOnPage']) == k]
            assert len(matches) == 1
            row = matches[0]
            value = next((row[name] for name in ['currentAcceptedSourceLiteral', 'literalCurrentSourceName', 'educationFirstAndCurrentLiteral', 'canonicalPreferredLiteral'] if name in row), None)
            family = row.get('currentCompleteVisibleAlternatives', row.get('visibleAlternatives'))
            status = row.get('currentSourceStatus', row.get('sourceStatus'))
            if status is None and 'canonicalPreferredLiteral' in row:
                assert row.get('sourceSpans') == [] and row.get('sourceUncertainty') is None
                status = 'direct'
            assert row['field'] == 'name' and status == 'direct'
            assert value == case['currentDirectLiteral'] and family == [value]
        result[k] = case
    return result


def independent_adoption_selection(reference, source_id, source_sha, load=pinned):
    exact_reference(reference)
    selector = load(reference)
    before_ref, after_ref = selector['supersededRootAdoption'], selector['effectiveRootAdoption']
    assert exact_reference(before_ref) != exact_reference(after_ref)
    before, after = load(before_ref), load(after_ref)
    expected_identity = source_id, source_sha, selector['batch']
    before_document = None
    legacy_hyphen = before_ref == {'path': str((AREA / 'reviews/root-phsa-history-2015-16-hyphen-i-typography-adoption.json').relative_to(ROOT)),
                                  'sha256': 'defef093e74632947d378f96df12877039071dfab3e037f28c0e2058724ee2bc'}
    assert tuple(after[k] for k in ['sourceId', 'sourceSha256', 'batch']) == expected_identity
    if legacy_hyphen:
        assert expected_identity == (source_id, source_sha, 'phsa-2015-16-hyphen-supplement')
        assert source_id == 'phsa-2015-16' and (before['sourceId'], before['sourceSha256']) == (source_id, source_sha)
        assert before['acceptedQualifiedCases'] is True and before['qualifiedCases'] == 1
        assert before_ref == selector['supersededCaseLedger']
        old_cases = before['exactCases']
        assert len(old_cases) == 1 and source_case_name(old_cases[0]) == 'Gfeller-Ingledew,Paris-Ann PA'
    elif before.get('acceptedQualifiedCases') is not True:
        assert tuple(before[k] for k in ['sourceId', 'sourceSha256', 'batch']) == expected_identity
        assert before_ref['sha256'] == '41410273e366a0cee07268d8d2af077fa95daef4edd9a5bfef9c00be35b3448c'
        assert before['decision'] == 'Adopt exactly14 qualified contextual source-glyph readings; no pixel-proved casing claim.'
        assert before['qualifiedNameCases'] == 14 and len(before['cases']) == 14
        original_ledger = {'path': str((AREA / 'reviews' / before['caseLedgerFile']).relative_to(ROOT)),
                           'sha256': before['caseLedgerSha256']}
        assert original_ledger == selector['supersededCaseLedger']
        load(original_ledger)
        old_cases = before['cases']
    else:
        assert tuple(before[k] for k in ['sourceId', 'sourceSha256', 'batch']) == expected_identity
        assert before['exactCaseLedger'] == selector['supersededCaseLedger']
        doc = load(before['exactCaseLedger'])
        before_document = doc
        old_cases = independent_scoped_adoption_cases(before, doc)
    assert after['acceptedQualifiedCases'] is True
    assert after['supersededRootAdoption'] == before_ref
    assert after['exactCaseLedger'] == selector['effectiveCaseLedger']
    doc = load(after['exactCaseLedger'])
    new_cases = independent_scoped_adoption_cases(after, doc)
    key = lambda c: (c['physicalPage'], c['sourceRowOnPage'])
    old, new = unique_rows(old_cases, key), unique_rows(new_cases, key)
    allowed = unique_rows(selector['authorizedChangedNameCases'], key)
    retired = independent_exact_retirements(selector, before, after, old, load)
    if before_document is not None:
        full_before = unique_rows(independent_scoped_adoption_cases({}, before_document), key)
        full_after = unique_rows(independent_scoped_adoption_cases({}, doc), key)
        assert set(full_before) - set(retired) == set(full_after), 'Unlisted source-case scope changed'
        for k in set(full_after) - set(allowed):
            assert full_before[k] == full_after[k], 'Unlisted source-case dictionary changed'
    assert old and set(old) - set(retired) == set(new) and (allowed or retired) and set(allowed) <= set(new)
    assert selector['oldFrozenFilesRemainUnchanged'] is True and selector['reason']
    changed = {k for k in new if old[k] != new[k]}
    assert changed == set(allowed), 'Changed root case list is not exact'
    for k in changed:
        a, b, authority = old[k], new[k], allowed[k]
        assert authority['allowedFields'] == ['name']
        assert source_case_name(a) == authority['oldPrimary']
        assert source_case_name(b) == authority['newPrimary']
        assert case_family(a) == authority['oldVisibleAlternatives']
        assert case_family(b) == authority['newVisibleAlternatives']
        assert source_case_crop(a) == source_case_crop(b) == authority['originalFullRowCropSha256']
        assert b['caseProvenByPixels'] is False
    return before_ref, after_ref


_CLOSED_POLICY_SELECTION_CACHE = {}


def independent_closed_policy_selections(policy_ref, item, source_id, source_sha, load=pinned, trail=None):
    """Closed routes embed their exact adoption selector in the matching policy case."""
    cache_key = source_id, source_sha, exact_reference(policy_ref), item['physicalPage'], item['sourceRowOnPage'], exact_reference(item['rootAdoption'])
    if load is pinned and cache_key in _CLOSED_POLICY_SELECTION_CACHE:
        return _CLOSED_POLICY_SELECTION_CACHE[cache_key]
    trail = set() if trail is None else set(trail)
    assert cache_key not in trail, 'Cyclic exact closed policy history'
    trail.add(cache_key)
    policy = load(policy_ref)
    assert policy['frozen'] is True
    key = item['physicalPage'], item['sourceRowOnPage']
    cases = [case for case in policy['approvedCases'] if (case['sourceId'], case['physicalPage'], case['sourceRowOnPage']) == (source_id, *key)]
    assert len(cases) == 1
    case = cases[0]
    assert case['sourceSha256'] == source_sha and case['rootAdoption'] == item['rootAdoption']
    assert case['primary'] == item['chosenName']
    assert case['originalFullRowCropSha256'] == source_case_crop(item['originalCaseEvidence'])
    assert set(case['completeVisibleAlternatives']) == set(case_family(item['originalCaseEvidence']))
    adoption = load(case['rootAdoption'])
    assert adoption['exactCaseLedger'] == case['exactCaseLedger']
    results = []
    predecessor = case.get('supersedesExactClosedAuthority')
    if predecessor is not None:
        previous_policy = load(predecessor['policy'])
        previous_cases = [row for row in previous_policy['approvedCases'] if (row['sourceId'], row['physicalPage'], row['sourceRowOnPage']) == (source_id, *key)]
        assert len(previous_cases) == 1
        before = previous_cases[0]
        assert before['rootAdoption'] == predecessor['rootAdoption'] and before['exactCaseLedger'] == predecessor['exactCaseLedger']
        assert before['originalFullRowCropSha256'] == case['originalFullRowCropSha256']
        previous_item = {'physicalPage': key[0], 'sourceRowOnPage': key[1], 'rootAdoption': before['rootAdoption'],
                         'chosenName': before['primary'], 'originalCaseEvidence': {'proposedName': before['primary'],
                         'cropSha256': before['originalFullRowCropSha256'], 'visibleAlternatives': before['completeVisibleAlternatives']}}
        results.extend(independent_closed_policy_selections(predecessor['policy'], previous_item, source_id, source_sha, load, trail))
    revision = case.get('canonicalAuthorityRevision')
    if revision is not None:
        selector_ref = revision['rootAdoptionSupersession']
        before_ref, after_ref = independent_adoption_selection(selector_ref, source_id, source_sha, load)
        assert after_ref == case['rootAdoption']
        if predecessor is not None:
            assert before_ref == predecessor['rootAdoption']
        results.append((selector_ref, after_ref))
    if load is pinned:
        _CLOSED_POLICY_SELECTION_CACHE[cache_key] = results
    return results


def positive_integer(value):
    return type(value) is int and value > 0


def independent_metadata_identity(metadata, inventory_source, source_id):
    parts = source_id.split('-')
    assert len(parts) == 3 and parts[0] == 'phsa' and re.fullmatch('[0-9]{4}', parts[1])
    assert parts[2] == str(int(parts[1]) + 1)[-2:]
    expected_year = parts[1] + '/' + parts[2]
    assert metadata['year'] == inventory_source['year'] == expected_year
    assert metadata['id'] == 'queue-completion-' + source_id + '-employees'
    assert metadata['employerSlug'] == 'provincial-health-services-authority'
    assert metadata['sourceKind'] == 'official' and metadata['sector'] == 'Health authorities'
    assert metadata['sha256'] == inventory_source['sourceSha256']
    assert metadata['sourceUrl'] == inventory_source['sourceUrl']
    assert metadata['sourceIndexUrl'] == inventory_source['sourceIndexUrl']
    assert type(metadata['pdfBytes']) is int and metadata['pdfBytes'] == inventory_source['pdfBytes']
    assert metadata['periodType'] == 'fiscal'
    assert metadata['periodStart'] == parts[1] + '-04-01'
    assert metadata['periodEnd'] == str(int(parts[1]) + 1) + '-03-31'
    assert metadata['scope'] == metadata['category'] == 'employee-remuneration'
    assert metadata['threshold'] == 75000 and type(metadata['threshold']) is int
    assert metadata['thresholdComparison'] == '>' and metadata['currency'] == 'CAD'
    assert metadata['retainCompiledPartition'] is True and inventory_source['retainCompiledPartition'] is True


def canonical_field_key(row, source_id, source_sha, default_name=False):
    assert isinstance(row, dict)
    for k, expected in [('sourceId', source_id), ('sourceSha256', source_sha)]:
        if k in row:
            assert row[k] == expected
    page, number = row.get('physicalPage'), row.get('sourceRowOnPage')
    field = row.get('field', 'name' if default_name else None)
    assert positive_integer(page) and positive_integer(number) and field in FIELDS
    return page, number, field


def whole_name_family(primary, alternatives):
    assert isinstance(primary, str) and primary
    assert isinstance(alternatives, list) and alternatives
    assert all(isinstance(s, str) and s for s in alternatives)
    assert len(set(alternatives)) == len(alternatives) and primary in alternatives
    return frozenset(alternatives)


def human_record_at(document, pointer):
    assert isinstance(pointer, str) and (pointer == '' or pointer.startswith('/'))
    current = document
    for token in pointer.split('/')[1:] if pointer else []:
        assert re.search(r'~(?![01])', token) is None
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(current, list):
            assert re.fullmatch(r'0|[1-9][0-9]*', token)
            current = current[int(token)]
        else:
            assert isinstance(current, dict) and token in current
            current = current[token]
    assert isinstance(current, dict)
    return current


def independent_canonical_source(reference, source_id, source_sha, source, load=pinned, staged=None):
    """Independently bind every canonical outcome to an exact human row and payload field."""
    exact_reference(reference)
    closure = load(reference)
    assert closure['schema'] == 'phsa-canonical-source-closure-v1'
    assert (closure['sourceId'], closure['sourceSha256']) == (source_id, source_sha)
    assert closure['accepted'] is True and closure['closed'] is True and closure['unresolved'] == []
    assert source['sourceId'] == source_id and source['sourceSha256'] == source_sha
    assert source['completePhysicalSource'] is True
    assert isinstance(source['pendingFields'], list) and source['pendingFields'] == []
    selected = unique_rows(source['rows'], lambda r: (r['row'][5], r['sourceRowOnPage']))
    packets = closure['targetPackets']
    packet_pins = [exact_reference(ref) for ref in packets]
    assert packets and len(set(packet_pins)) == len(packets)
    prior = source_id != 'phsa-2019-20'
    if prior:
        expected = {str((AREA / 'phsa/canonical-review' / (source_id + '-' + kind + '-source-only.json')).relative_to(ROOT))
                    for kind in ['qualified-name', 'direct-neither-name', 'positive-neither-money']}
        assert {p for p, _ in packet_pins} == expected
        assert closure['scopeKind'] == 'prior-eight-three-packets'
    else:
        assert closure['scopeKind'] == 'phsa-2019-20-bounded-packets'
    targets = set()
    for ref in packets:
        packet = load(ref)
        assert (packet['sourceId'], packet['sourceSha256']) == (source_id, source_sha)
        assert any(packet.get(flag) is True for flag in ['sourceOnly', 'candidateValuesWithheld', 'expectedValuesWithheld'])
        rows = packet['rows']
        local = [canonical_field_key(row, source_id, source_sha, prior) for row in rows]
        assert len(set(local)) == len(rows) and not targets.intersection(local), 'Overlapping canonical target packets'
        if prior:
            money = ref['path'].endswith('-positive-neither-money-source-only.json')
            assert all((k[2] != 'name') == money for k in local)
        for field in ['rowCount', 'fieldCount', 'qualifiedNameFields', 'directManualNeitherNameFields', 'positiveMonetaryFields']:
            if field in packet:
                assert type(packet[field]) is int and packet[field] == len(rows)
        targets.update(local)
    if prior and staged is not None:
        # Recompute the current risk coverage from the original reader streams.
        # Punctuation/spacing alone do not create a new canonical name family;
        # every letter/digit and its case remains significant.
        letters = lambda text: ''.join(c for c in text if c.isalpha() or c.isdigit())
        required_current_fields = set()
        for (page, number), entry in selected.items():
            original = staged[page, number]
            for field, proof in entry['fields'].items():
                if not proof['status'].startswith('manual-'):
                    continue
                value = entry['row'][FIELDS[field]]
                readers = [r for r in [original['tesseract'], original['rapidocr']] if r is not None]
                if field == 'name':
                    value = letters(value)
                    alternatives = [letters(r['name']) for r in readers]
                else:
                    if not positive_integer(value):
                        continue
                    token = 'pay' if field == 'remuneration' else 'expense'
                    alternatives = [r[token]['value'] for r in readers
                                    if r[token]['kind'] == 'number' and type(r[token]['value']) is int]
                if value not in alternatives:
                    required_current_fields.add((page, number, field))
        assert required_current_fields <= targets, 'Canonical packets omit a current manual field outside both reader families'
    human_refs = closure['humanReviewReceipts']
    assert human_refs
    humans = {}
    for ref in human_refs:
        key = exact_reference(ref)
        assert key not in humans and key[0] not in {k[0] for k in humans}
        human = load(ref)
        has_identity = 'sourceId' in human or 'sourceSha256' in human
        if has_identity:
            assert (human.get('sourceId'), human.get('sourceSha256')) == (source_id, source_sha)
        for flag in ['accepted', 'closed']:
            if flag in human:
                assert human[flag] is True
        for flag in ['unresolved', 'unresolvedFields', 'unresolvedMoneyFields']:
            if flag in human:
                assert human[flag] == [] or type(human[flag]) is int and human[flag] == 0
        humans[key] = human, has_identity
    outcomes = unique_rows(closure['outcomes'], lambda r: canonical_field_key(r, source_id, source_sha))
    assert set(outcomes) == targets
    used = set()
    qualified = 0
    for key, outcome in outcomes.items():
        page, number, field = key
        entry = selected[page, number]
        assert len(entry['row']) == 6
        value, status = outcome['value'], outcome['status']
        assert value == entry['row'][FIELDS[field]] and type(value) is type(entry['row'][FIELDS[field]])
        if field == 'name':
            family = whole_name_family(value, outcome['visibleAlternatives'])
            resolution = entry['fields']['name']
            evidence = resolution.get('evidence', {}).get('nameTypographyQualification')
            if resolution['status'] == 'manual-qualified-source-typography':
                assert status == 'qualified' and len(family) > 1
                assert evidence['caseProvenByPixels'] is False
                assert evidence.get('chosenName', value) == value
                assert family == frozenset(evidence['visibleAlternatives']) | {value}
                qualified += 1
            else:
                assert status == 'direct' and family == {value} and evidence is None
        else:
            assert positive_integer(value) and status == 'direct' and 'visibleAlternatives' not in outcome
            family = None
        record = outcome['decisionRecord']
        assert set(record) == {'receipt', 'rowRecordPointer', 'valueField', 'finiteField'}
        human_key = exact_reference(record['receipt'])
        human, has_identity = humans[human_key]
        decision = human_record_at(human, record['rowRecordPointer'])
        if not has_identity:
            assert (decision.get('sourceId'), decision.get('sourceSha256')) == (source_id, source_sha)
        assert canonical_field_key(decision, source_id, source_sha, field == 'name') == key
        value_key = record['valueField']
        assert isinstance(value_key, str) and decision[value_key] == value and type(decision[value_key]) is type(value)
        finite_key = record['finiteField']
        if finite_key is None:
            assert status == 'direct'
        else:
            assert field == 'name' and isinstance(finite_key, str)
            assert whole_name_family(value, decision[finite_key]) == family
        used.add(human_key)
    if targets:
        assert used == set(humans)
    else:
        assert all(has_identity for _, has_identity in humans.values())
    if prior:
        all_qualified = {(p, n, 'name') for (p, n), entry in selected.items()
                         if entry['fields']['name']['status'] == 'manual-qualified-source-typography'}
        assert all_qualified <= targets
    counts = {'targets': len(targets), 'nameTargets': sum(k[2] == 'name' for k in targets),
              'positiveMoneyTargets': sum(k[2] != 'name' for k in targets), 'qualifiedNameTargets': qualified}
    assert closure['counts'] == counts and all(type(n) is int for n in closure['counts'].values())
    return {'closure': reference, 'scopeKind': closure['scopeKind'], **counts}


_EXHAUSTIVE_016_SHA = '9c6f4c3bd80ff422eb923e660ca722468c5146da259bc818315c17f8988dcacf'
_EXHAUSTIVE_016_CACHE = {}

_INDEPENDENT_MONEY_HELPERS = {
    '1d0b4d5d43fe9c950fc043d48deaf22e0d9db3e6c68b1aead68e4085524b3a99': 'ordered',
    '1c33c726f92ca493f2eb0a75d26c4431c64191a27446704800ba83d8304a4e44': 'ordered',
    'd169d7d6e0d9a767742ad1e82d8bca992db986553f5c942bde58a11f9ffac5d3': 'ordered',
    '53ddc8db3f1d26e36a0efbade0e871348bdfacb71d9045c6eb47c057a1b2b102': 'ordered',
    'deba98fe20ef290dcfb90de021123c8ee2b36134fd85382ec9e33fe8b3422c31': 'tuple',
    'f21bb7b9d9d4e8016ff503562594667f32534047668db119da43168af198c572': 'tuple',
    'c090f1011cc772ddd01604ba4dcb1d48e6cf2bd0aa8849e26012568096edca0d': 'tuple',
    '94405abc9cb349a597854d1fa6b50d95dd30655996894d2d71e4484b55900ee0': 'tuple',
    'af8a9fa14b37d7cf567c781b71741a1285ad82c4bedae4c3c3f13c1afeefb069': 'complete',
    '9ff9fc7127ee2820689dfafe96780b904d7cf149d9efe007389d92c4d70d5bce': 'complete',
    'f84faa0afa911828578812ab01bb664f79f7aac4b09593f0daebf7797cb9e1de': 'scoped',
    'dfc426bb2a520aeae5f973288eb85e332cec9bf6b2224098adc595e741a8aa70': 'scoped',
    '6e649bf527469dafd60ddfcaf17dd53d93a4bc49de9f55b1f7b85a6166ecd7c0': 'current',
    '9e436864774cc41573ace634789b386bd1ab47824587a8e3544400c269ff4494': 'current',
    '97c998ec16fb28746f76b5fd450f0d7f966b24109b432d68ef6b0db41328626c': 'current',
    '90b60335597f5a791d613307a4c819440702903a0ea319abf61c575df383e525': 'current',
    '6dd8ce0d759d5b07b0b5d5d28591f9e05dccfd9ae5119206d32084cf1f47523e': 'current',
}
_MONEY_HELPER_MODULES = {}
_MONEY_HELPER_PINS = {}


def independent_external_money_helper(confirmation, source_id, source_sha):
    kind = _INDEPENDENT_MONEY_HELPERS[confirmation['confirmationLedger']['sha256']]
    path = ROOT / 'scripts' / ('finish_salary_phsa_review_money_' + kind + '_v7.py')
    current_pin = pin(path)
    if kind not in _MONEY_HELPER_MODULES:
        spec = importlib.util.spec_from_file_location('independent_phsa_money_' + kind + '_v7', path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _MONEY_HELPER_MODULES[kind] = module
        _MONEY_HELPER_PINS[kind] = current_pin
    assert current_pin == _MONEY_HELPER_PINS[kind], 'Independent helper changed during replay'
    _MONEY_HELPER_MODULES[kind].verify(confirmation, source_id, source_sha, pinned)


def financial_literal(text, value):
    if value is None:
        assert text == '-'
    else:
        assert positive_integer(value) and isinstance(text, str)
        assert re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)', text)
        assert int(text.replace(',', '')) == value


def independent_exhaustive_016(confirmation, source_id, source_sha):
    """Reconstruct the actual 84/99/99 source union; never import its producer."""
    ref = confirmation['confirmationLedger']
    assert ref['sha256'] == _EXHAUSTIVE_016_SHA
    assert (source_id, source_sha) == ('phsa-2019-20', '0e31ac2054f0c2d4ef78797185dddd96cc0cdf2eab94bd6841fa24e1c38e7d02')
    ledger = pinned(ref)
    expected_entry = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
    assert ledger['confirmations'].count(expected_entry) == 1
    if ref['sha256'] in _EXHAUSTIVE_016_CACHE:
        assert expected_entry in _EXHAUSTIVE_016_CACHE[ref['sha256']]
        return
    assert ledger['frozen'] is True and ledger['adapter'] == 'count-independent-source-money-peer-v1'
    assert ledger['sourceReceiptSchema'] == 'exhaustive-canonical-money-union-with-three-distinct-source-first-peers-v1'
    assert (ledger['completeFrozenSourceTargetFields'], ledger['confirmedMonetaryFields'],
            ledger['originalAuthorOwnSourceCorrections'], ledger['originalPeerOwnSourceCorrections']) == (282, 281, 44, 4)
    for item in ledger['peerInputs']:
        pinned(item, False)
    review_ref = ledger['peerInputs'][0]
    assert review_ref['sha256'] == 'b59c4f4a3e18dc04797d2971445dcd023accb3c1b6a49a2c1b4250bd971ad825'
    review = pinned(review_ref)
    current = pinned(review['own282SourceReread'])
    raw_ref = current['originalSourceFirst']
    raw = pinned(raw_ref)
    packet = pinned(current['sourceOnlyPacket'])
    views = pinned(raw['sourceOnlyTargetViews'])
    batch = 'phsa-2019-20-016'
    for doc in [review, current, raw, packet, views]:
        assert (doc['sourceId'], doc['sourceSha256'], doc['batch']) == (source_id, source_sha, batch)
    assert raw['frozen'] is True and raw['fullCandidateOrCorrespondingOcrOpenedBeforeFreeze'] is False
    assert current['frozen'] is True and current['correspondingFreshPeerValuesOpened'] is False
    assert packet['sourceValuesOrCandidateAlternativesIncluded'] is False
    key = lambda r: (r['physicalPage'], r['sourceRowOnPage'], r['field'])
    original = unique_rows(raw['rows'], key)
    targets = unique_rows(packet['rows'], key)
    secondary = unique_rows(current['rows'], key)
    finals = unique_rows(review['rows'], key)
    assert len(original) == 633 and len(views['rows']) == 400
    assert set(targets) == {k for k in original if k[2] in ['remuneration', 'expenses']}
    assert len(targets) == 282 and set(targets) == set(secondary) == set(finals)
    view_fields = {}
    for row in views['rows']:
        native = {entry['field']: entry for entry in row['sourceNativeTargetViews']}
        assert len(native) == len(row['sourceNativeTargetViews']) == len(row['reviewTargetFields'])
        assert set(native) == set(row['reviewTargetFields'])
        for field in native:
            k = row['physicalPage'], row['sourceRowOnPage'], field
            assert k not in view_fields
            view_fields[k] = row, native[field]
    assert set(view_fields) == set(original)
    amendments = {}
    for amendment_ref in review['additiveOwnSourceCorrections']:
        doc = pinned(amendment_ref)
        assert doc['priorFrozenCurrent'] == review['own282SourceReread']
        for row in doc.get('rows', [doc]):
            k = key(row)
            assert k not in amendments and k in targets and row['uncertainty'] is None
            amendments[k] = row
    assert {(r['sequence'], r['field']) for r in amendments.values()} == {
        (139, 'expenses'), (174, 'expenses'), (203, 'remuneration'), (214, 'expenses')}
    overlay_ref = ledger['confirmations'][0]['effectiveAuthorOverlay']
    overlay = pinned(overlay_ref)
    assert (overlay['sourceId'], overlay['sourceSha256'], overlay['batch']) == (source_id, source_sha, batch)
    selected_fields = independent_review_overlay(overlay_ref, source_id, source_sha)
    assert set(selected_fields) == set(original)
    author_review = pinned(overlay['reviewInput'])
    assert author_review['imageFirstTranscriptFreeze'] == raw_ref
    assert {'path': author_review['rawTranscriptPath'], 'sha256': author_review['rawTranscriptSha256']} == raw_ref
    assert author_review['completeFinancialSourceClosure'] == review_ref
    assert overlay['frozenBatch']['sha256'] == views['fullBatchSha256'] == raw['fullCandidateSha256StillClosed']
    author_errors = collections.Counter()
    for k, target in targets.items():
        first, middle, final = original[k], secondary[k], finals[k]
        locator, native = view_fields[k]
        for record in [target, first, middle, final]:
            assert record['sequence'] == locator['sequence'] and record['cropSha256'] == locator['cropSha256']
        value = amendments[k]['correctedCurrentLiteral'] if k in amendments else middle['currentLiteral']
        assert positive_integer(value) or value is None and k == (119, 42, 'expenses')
        assert first['literalSourceValue'] == middle['firstFrozenLiteral'] == final['originalColdLiteral']
        assert middle['currentLiteral'] == final['ownIntermediateWhole600Literal']
        assert value == final['finalSourceLiteral'] == selected_fields[k]['value']
        assert middle['uncertainty'] is None and middle['ownColdReadingCorrection'] is (first['literalSourceValue'] != middle['currentLiteral'])
        assert final['ownColdToFinalCorrection'] is (first['literalSourceValue'] != value)
        assert final['ownSecondaryToFinalCorrection'] is (middle['currentLiteral'] != value)
        assert final['literalPrintedDashNull'] is (value is None)
        assert final['sourceNative300'] == middle['nativeOriginal300SourceView'] == native
        assert final['sourceWhole600'] == middle['actualWholePage600SourceView'] == target['actualWholePage600SourceView']
        if k in amendments:
            amend = amendments[k]
            assert amend['coldFirstLiteral'] == first['literalSourceValue']
            assert amend['ownIncorrectSecondaryWhole600Reading'] == middle['currentLiteral'] != value
        if first['literalSourceValue'] != value:
            author_errors[k[2]] += 1
    assert dict(author_errors) == {'remuneration': 37, 'expenses': 7}
    raw_peer_fields = ['peerImageFirstRaw', 'freshPeerSourceFirst', 'imageFirstTranscript']
    value_fields = ['currentValue', 'authorEffectiveCurrentLiteral', 'value']
    initial_fields = ['value', 'value', 'imageFirstValue']
    peer_refs = review['exactDisjointPeerPartition']
    expected_peer_hashes = ['45e446fe49a58fdd0bf564b8565f8959c28a792657daee1d7f525d7ffb7e74df',
                            'ad76511527a1aece7c1f113838780515c7fe157c6fdb0dbff210e64c5889b15f',
                            'c068e164e42240c31ee218abe36bbc0427f4d65bf0d6dd223550e7336b3a77b7']
    assert [ref['sha256'] for ref in peer_refs] == expected_peer_hashes
    expected_confirmations, covered, independent_raws = [], set(), []
    for index, peer_ref in enumerate(peer_refs):
        peer = pinned(peer_ref)
        raw_peer_ref = peer[raw_peer_fields[index]]
        independent_raws.append(raw_peer_ref)
        first_peer = pinned(raw_peer_ref)
        peers = unique_rows(peer['rows'], key)
        first_peers = unique_rows(first_peer['rows'], key)
        assert set(peers) == set(first_peers) and len(peers) == [84, 99, 99][index]
        assert not covered.intersection(peers) and set(peers) <= set(targets)
        covered.update(peers)
        if index == 0:
            assert raw_peer_ref['sha256'] == '357da534fa5c13b7d316f74915ad77983eb429ddabba97e4648f8a4e923435e0'
            assert first_peer['authorChoicesUnopenedAtFreeze'] is True and first_peer['candidateUnopenedAtFreeze'] is True
            assert not first_peer['unresolvedFields'] and not peer['unresolvedFields']
            amendment = pinned(peer['ownPostComparisonCorrectionReceipt'])
            peer_changes = {key(r): r for r in amendment['fields'] if r['ownPeerCorrection'] is True}
            assert len(peer_changes) == 3
            proof = pinned(peer['sourcePixelVerification'])
            pixels = unique_rows(proof['fields'], key)
        elif index == 1:
            assert first_peer['frozen'] is True and first_peer['blindness']['correspondingAuthorOrOcrChoicesOpened'] is False
            assert first_peer['blindness']['priorCorrespondingExpectedValuesSupplied'] is False and not first_peer['uncertainFields']
            peer_changes = {}
            proof = pinned(peer['peerActualWhole600AndNative300PixelProof'])
            pixels = unique_rows(proof['fields'], key)
        else:
            assert first_peer['frozen'] is True and first_peer['sourceValuesOrAuthorChoicesOpenedBeforeFreeze'] is False
            assert not first_peer['unresolved'] and not peer['unresolvedFields']
            amendment = pinned(peer['ownPostcomparisonSourceCorrection'])
            peer_changes = {key(amendment): amendment}
            proof = pinned(peer['pixelVerification'])
            pixels = unique_rows(proof['rows'], key)
        assert set(pixels) == set(peers)
        changed = 0
        for k, row in peers.items():
            first, target, final = first_peers[k], targets[k], finals[k]
            value = final['finalSourceLiteral']
            before = first[initial_fields[index]]
            if k in peer_changes:
                amended = peer_changes[k]
                assert amended['cropSha256'] == target['cropSha256']
                assert amended['peerRawValue' if index == 0 else 'ownFirstFrozenValue'] == before
                peer_value = amended['currentPersonalSourceValue' if index == 0 else 'correctedLiteralSourceValue']
            else:
                peer_value = before
            assert peer_value == row[value_fields[index]] == value
            assert row['cropSha256'] == first['cropSha256'] == pixels[k]['cropSha256'] == target['cropSha256']
            assert row['sequence'] == first['sequence'] == pixels[k]['sequence'] == target['sequence']
            assert final['independentSourcePeer'] == peer_ref
            changed += before != value
            if index == 0:
                financial_literal(first['literalSourceAmount'], before)
                financial_literal(row['literalSourceAmount'], value)
                assert row['peerFrozenRawValue'] == before and row['authorCurrentValue'] == value
                assert row['peerPostChoiceCorrection'] is (before != value) and row['uncertainty'] is None
                assert first['actualWholePage600SourceView'] == pixels[k]['actualWhole600'] == final['sourceWhole600']
                assert pixels[k]['native300PixelExact'] is pixels[k]['whole600PixelExact'] is True
            elif index == 1:
                financial_literal(first['literalPrinted'], before)
                assert first['uncertain'] is False and row['peerFirstLiteral'] == before
                assert row['matchesEffectiveCurrent'] is True and row['peerCorrection'] is False
                assert first['source600'] == pixels[k]['actualWholepage600'] == final['sourceWhole600']
                assert pixels[k]['actualWhole600RgbExact'] is pixels[k]['native300RgbExact'] is True
            else:
                financial_literal(row['literalSourceAmount'], value)
                assert row['peerFirstSourceValue'] == before and row['uncertainty'] is None and row['exactMatch'] is True
                assert pixels[k]['actual600RGBExact'] is pixels[k]['native300FieldRGBExact'] is True
                assert pixels[k]['fullRow300RGBExact'] is True
            if value is not None:
                expected_confirmations.append({'sourceId': source_id, 'sourceSha256': source_sha,
                    'physicalPage': k[0], 'sourceRowOnPage': k[1], 'field': k[2], 'confirmedValue': value,
                    'effectiveAuthorOverlay': overlay_ref, 'peerComparison': review_ref,
                    'freshSourceImage': final['sourceWhole600'], 'imageFirstTranscript': raw_ref,
                    'independentSourcePeer': peer_ref})
        assert changed == [3, 0, 1][index]
    assert covered == set(targets) and len(expected_confirmations) == 281
    assert ledger['confirmations'] == expected_confirmations
    assert ledger['authorImageFirstTranscript'] == raw_ref
    assert ledger['independentPeerImageFirstTranscripts'] == independent_raws
    assert len({exact_reference(r) for r in independent_raws}) == 3 and raw_ref not in independent_raws
    nulls = [r for r in finals.values() if r['finalSourceLiteral'] is None]
    assert len(nulls) == 1 and key(nulls[0]) == (119, 42, 'expenses') and nulls[0]['sequence'] == 372
    declared_nulls = ledger['literalSourceDashFieldsConfirmedSeparately']
    assert len(declared_nulls) == 1 and declared_nulls[0]['value'] is None
    assert key(declared_nulls[0]) == key(nulls[0])
    assert declared_nulls[0]['freshSourceImage'] == nulls[0]['sourceWhole600']
    assert declared_nulls[0]['originalFullRowCropSha256'] == nulls[0]['cropSha256']
    # Independently replay actual whole-page pixels for all 282 native/600 fields.
    import fitz
    from PIL import Image
    pdf = Path('/tmp/queue-completion-phsa/originals/phsa-2019-20.pdf')
    assert digest(pdf.read_bytes()) == source_sha
    doc = fitz.open(pdf)
    for page in sorted({k[0] for k in finals}):
        rendered = {}
        for dpi in [300, 600]:
            pix = doc[page - 1].get_pixmap(dpi=dpi, alpha=False)
            rendered[dpi] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        for k, final in finals.items():
            if k[0] != page:
                continue
            for dpi, image_ref, box_field in [(300, final['sourceNative300'], 'originalPdf300DpiPixelBox'),
                                              (600, final['sourceWhole600'], 'actual600PixelCropBox')]:
                supplied = Image.open(io.BytesIO(pinned(image_ref, False))).convert('RGB')
                actual = rendered[dpi].crop(tuple(image_ref[box_field]))
                assert supplied.size == actual.size and supplied.tobytes() == actual.tobytes()
    _EXHAUSTIVE_016_CACHE[ref['sha256']] = expected_confirmations


def independent_base_money_peer(confirmation, source_id, source_sha):
    reference = confirmation['confirmationLedger']
    ledger = pinned(reference)
    if reference['sha256'] in _INDEPENDENT_MONEY_HELPERS:
        independent_external_money_helper(confirmation, source_id, source_sha)
    elif reference['sha256'] == _EXHAUSTIVE_016_SHA:
        independent_exhaustive_016(confirmation, source_id, source_sha)
    elif reference['sha256'] in _FY21_LEDGERS:
        independent_fy21_money_peer(confirmation, source_id, source_sha)
    elif reference['sha256'] in _ADDITIONAL_MONEY_LEDGERS:
        independent_additional_money_peer(confirmation, source_id, source_sha)
    else:
        legacy = {
            'b83bc5c079cc0611537cb8f1a15d4721df1eb3ee66bdfa131d44339fba35cba5': ('money-peer-confirmations-001.json', 15),
            '40ad0f19416db7d14819aca689c9e3aa6c1ad155c783617fd40a7c17efe3fa44': ('money-peer-confirmations-005.json', 109),
        }
        assert reference['sha256'] in legacy, 'Unknown source-money schema remains held'
        filename, count = legacy[reference['sha256']]
        assert reference['path'] == str((AREA / 'phsa/triangulation' / filename).relative_to(ROOT))
        assert len(ledger['confirmations']) == count
        assert ledger.get('noSalaryValuesChanged') is True
        expected = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
        assert ledger['confirmations'].count(expected) == 1
        peer = pinned(confirmation['peerComparison'])
        assert not peer['candidateChanges'] and not peer['unresolvedFields']
        key = confirmation['physicalPage'], confirmation['sourceRowOnPage'], confirmation['field']
        rows = [r for r in peer['rows'] if r['sourceId'] == source_id and
                (r['physicalPage'], r['sourceRowOnPage'], r['field']) == key]
        assert len(rows) == 1 and rows[0]['literalSourceValue'] == confirmation['confirmedValue']
        assert rows[0]['actualSource600DpiPixelsIndependentlyReproducedExactly'] is True


def independent_preserved_money_records(previous, previous_ref, superseded_overlay_ref, current, load=pinned):
    """Unrelated mixed-source fields retain their own exact earlier proof pointers."""
    field_key = lambda row: (row['sourceId'], row['physicalPage'], row['sourceRowOnPage'], row['field'])
    before = unique_rows(previous['confirmations'], field_key)
    after = unique_rows(current['confirmations'], field_key)
    inherited = unique_rows(previous.get('preservedUnchangedFieldProvenance', []), field_key)
    supplied = unique_rows(current['preservedUnchangedFieldProvenance'], field_key)
    wanted = [row for row in previous['confirmations'] if row['effectiveAuthorOverlay'] != superseded_overlay_ref]
    assert set(supplied) == {field_key(row) for row in wanted}, 'Unrelated proof pointer scope changed'
    result = []
    for row in wanted:
        k = field_key(row)
        record = supplied[k]
        assert row == after[k], 'Unrelated money row changed'
        if k in inherited:
            assert record == inherited[k], 'Inherited unrelated proof pointer changed'
        else:
            expected = {name: row[name] for name in ['sourceId', 'physicalPage', 'sourceRowOnPage', 'field']}
            expected['confirmationLedger'] = previous_ref
            selector_ref = record.get('confirmationSupersession')
            if selector_ref is not None:
                exact_reference(selector_ref)
                selector = load(selector_ref)
                assert selector['effectiveConfirmation'] == previous_ref
                assert selector['oldFrozenFilesRemainUnchanged'] is True and selector['reason']
                expected['confirmationSupersession'] = selector_ref
            else:
                assert previous.get('adapter') not in ['unchanged-money-overlay-revision-v1', 'unchanged-money-overlay-revision-v2']
            assert record == expected, 'Preserved field does not retain the immediately previous proof'
        proof = load(record['confirmationLedger'])
        proof_rows = unique_rows(proof['confirmations'], field_key)
        assert proof_rows[k] == row, 'Preserved source proof does not describe the unchanged field'
        result.append(record)
    assert result == current['preservedUnchangedFieldProvenance'], 'Preserved proof order changed'
    return result


def independent_current_money_peer(confirmation, source_id, source_sha, seen=None, historical=False):
    """Replay immutable old evidence before permitting only its overlay-pointer rebase."""
    seen = set() if seen is None else set(seen)
    ref = confirmation['confirmationLedger']
    identity = exact_reference(ref)
    assert identity not in seen, 'Cyclic money proof derivation'
    seen.add(identity)
    ledger = pinned(ref)
    assert confirmation['sourceId'] == source_id and confirmation['sourceSha256'] == source_sha
    own_entry = {k: v for k, v in confirmation.items()
                 if k not in ['confirmationLedger', 'confirmationSupersession']}
    assert ledger['confirmations'].count(own_entry) == 1
    selection_ref = confirmation.get('confirmationSupersession')
    if ledger.get('adapter') == 'source-first-provenance-correction-v1':
        assert ref['sha256'] == '9e436864774cc41573ace634789b386bd1ab47824587a8e3544400c269ff4494'
        assert selection_ref is not None
        exact_reference(selection_ref)
        assert selection_ref['sha256'] == '9b5af42eaeee7b6eb461fb0ae3f899bf1706df8bb22a702265a327c7953ec0e5'
        selection = pinned(selection_ref)
        assert selection['selectionKind'] == 'source-first-provenance-correction-selection'
        assert selection['effectiveConfirmation'] == ref
        assert selection['supersededConfirmation'] == ledger['previousConfirmationLedger']
        assert selection['oldFrozenFilesRemainUnchanged'] is True and selection['frozen'] is True and selection['reason']
        return independent_external_money_helper({**own_entry, 'confirmationLedger': ref}, source_id, source_sha)
    rebased = ledger.get('adapter') in ['unchanged-money-overlay-revision-v1', 'unchanged-money-overlay-revision-v2']
    if selection_ref is None:
        if not rebased:
            return independent_base_money_peer(confirmation, source_id, source_sha)
        assert historical, 'A currently selected rebased ledger needs its exact immutable sidecar'
        previous_ref = ledger['previousConfirmationLedger']
        overlay_selector_ref = ledger['ordinaryOverlaySupersession']
    else:
        exact_reference(selection_ref)
        selection = pinned(selection_ref)
        assert selection['oldFrozenFilesRemainUnchanged'] is True and selection['reason']
        assert selection['effectiveConfirmation'] == ref
        previous_ref = selection['supersededConfirmation']
        overlay_selector_ref = selection['ordinaryOverlaySupersession']
    assert exact_reference(previous_ref) != identity
    previous = pinned(previous_ref)
    overlay_selector = pinned(overlay_selector_ref)
    edge_source, edge_sha = overlay_selector['sourceId'], overlay_selector['sourceSha256']
    old_ref, new_ref, old_overlay, new_overlay = independent_ordinary_selection(
        overlay_selector_ref, edge_source, edge_sha)
    old_rows = unique_rows(old_overlay['overlays'], lambda r: (r['physicalPage'], r['sourceRowOnPage']))
    new_rows = unique_rows(new_overlay['overlays'], lambda r: (r['physicalPage'], r['sourceRowOnPage']))
    key = lambda r: (r['sourceId'], r['physicalPage'], r['sourceRowOnPage'], r['field'])
    before = unique_rows(previous['confirmations'], key)
    after = unique_rows(ledger['confirmations'], key)
    assert before and set(before) == set(after)
    expected = copy.deepcopy(previous)
    changed = 0
    for row in expected['confirmations']:
        k = key(row)
        assert row['field'] in ['remuneration', 'expenses'] and positive_integer(row['confirmedValue'])
        if row['effectiveAuthorOverlay'] == old_ref:
            assert row['sourceId'] == edge_source and row['sourceSha256'] == edge_sha
            for overlay_rows in [old_rows, new_rows]:
                entry = overlay_rows[k[1:3]]
                assert row['field'] in entry['reviewedFields']
                value = entry['resolvedRow'][FIELDS[row['field']]]
                assert type(value) is int and value == row['confirmedValue'], 'Fresh-confirmed money changed'
            row['effectiveAuthorOverlay'] = new_ref
            changed += 1
        assert row == after[k], 'Source-money value/evidence/history/scope changed during rebase'
    assert changed > 0
    if rebased:
        expected['supersededAdapter'] = previous.get('adapter')
        expected['adapter'] = ledger['adapter']
        expected['previousConfirmationLedger'] = previous_ref
        expected['ordinaryOverlaySupersession'] = overlay_selector_ref
        expected['unchangedFreshMoneyFieldsRebound'] = changed
        expected['peerInputs'] = previous['peerInputs'] + [previous_ref, overlay_selector_ref]
        if ledger['adapter'] == 'unchanged-money-overlay-revision-v2':
            expected['preservedUnchangedFieldProvenance'] = independent_preserved_money_records(
                previous, previous_ref, old_ref, ledger)
        else:
            assert previous.get('adapter') != 'unchanged-money-overlay-revision-v2', 'Per-field provenance cannot be discarded'
    assert ledger == expected, 'Money ledger changed beyond exact unchanged-value overlay pointers'
    original = dict(before[key(own_entry)])
    original['confirmationLedger'] = previous_ref
    # Earlier derivations carry their own byte-pinned predecessor and ordinary
    # selector. Replay every edge recursively; only the present selected ledger
    # requires the separately pinned current confirmation-selection sidecar.
    independent_current_money_peer(original, source_id, source_sha, seen, historical=True)
    return {'supersession': selection_ref, 'unchangedReboundFields': changed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', help='New immutable receipt; omitted for --check-only schema probes')
    parser.add_argument('--check-only', action='store_true', help='Run all checks without writing or freezing a review receipt')
    parser.add_argument('--metadata', required=True, help='Explicit selected v3/v4 candidate metadata path')
    parser.add_argument('--canonical-closure', required=True, help='Exact root normalized canonical source closure')
    args = parser.parse_args()
    assert args.check_only or args.output
    out = ROOT / args.output if args.output else None
    assert out is None or not out.exists(), 'Never overwrite a frozen independent review'
    source_id = args.source
    metadata_path = ROOT / args.metadata
    assert metadata_path.name in [source_id + '-source-v3.json', source_id + '-source-v4.json']
    metadata = read(metadata_path)
    revision = metadata_path.stem.rsplit('-v', 1)[1]
    assert metadata['file'] == source_id + '-employees-v' + revision + '.json.gzip'
    data_path = COLLECTION / metadata['file']
    assert digest(data_path.read_bytes()) == metadata['dataSha256']
    payload = read(data_path)
    provenance_path = COLLECTION / metadata['provenanceFile']
    assert digest(provenance_path.read_bytes()) == metadata['provenanceSha256']
    provenance = read(provenance_path)
    supplementary_archive_refs = []
    if source_id == 'phsa-2019-20':
        # This exact shared historical53-peer archive was omitted from the
        # immutable author's source-specific list; retain its explicit independent
        # receipt dependency rather than editing any final v4 artifact.
        supplementary_archive_refs = [{'path': str((AREA / 'phsa/triangulation/archived-source-money-views-003.json').relative_to(ROOT)),
                                       'sha256': '5d1dd4210cc7a5f0a41dcd263e771200b8491fb58e39dafa61f95d9c6a110414'}]
    for archive_ref in provenance.get('archivedExactSourceMoneyViews', []) + supplementary_archive_refs:
        archive = pinned(archive_ref)
        assert archive['frozen'] is True
        for source_peer in ([archive['sourcePeer']] if 'sourcePeer' in archive else archive['peerComparisons']):
            pinned(source_peer, False)
        for entry in archive['rows']:
            original_ref, stored = entry['originalReference'], entry['archivedExactBytes']
            assert original_ref['sha256'] == stored['sha256']
            pinned(stored, False)
            alias_key = (original_ref['path'], original_ref['sha256'])
            if alias_key in _ARCHIVED_IMAGE_ALIASES:
                assert _ARCHIVED_IMAGE_ALIASES[alias_key].read_bytes() == (ROOT / stored['path']).read_bytes(), 'Conflicting archived bytes for one source-view alias'
            else:
                _ARCHIVED_IMAGE_ALIASES[alias_key] = ROOT / stored['path']
    source = provenance['originalRowsAndPerFieldResolution']
    assert source['sourceId'] == source_id and source['sourceSha256'] == metadata['sha256']
    assert provenance['dataSha256'] == metadata['dataSha256']
    assert source['completePhysicalSource'] and not source['pendingFields']
    ordinary_selection_count = independent_ordinary_selections(provenance, source_id, metadata['sha256'])
    inventory = pinned(provenance['sourceInventory'])
    inv = next(s for s in inventory['sources'] if s['id'] == source_id)
    assert inv['sourceSha256'] == metadata['sha256']
    independent_metadata_identity(metadata, inv, source_id)
    original_pdf_bytes = Path(inv['cachePath']).read_bytes()
    assert len(original_pdf_bytes) == inv['pdfBytes'] and digest(original_pdf_bytes) == metadata['sha256']
    _ORIGINAL_PDF_REFERENCES.add((inv['cachePath'], metadata['sha256']))
    profiles = pinned(provenance['processingProfiles'])
    for reference in profiles['sourceProfiles']:
        pinned(reference)
    pinned(provenance['fieldPolicy'])
    contexts = pinned(provenance['sourceContextControls'])
    context = next(s for s in contexts['sources'] if s['sourceId'] == source_id)
    anchors = pinned(provenance['independentOriginalRowGeometry'])
    anchor = next(s for s in anchors['sources'] if s['sourceId'] == source_id)
    assert anchor['sourceSha256'] == metadata['sha256']
    geometry = {p['physicalPage']: p for p in anchor['pages']}
    staged, pages = {}, {}
    for reference in source['physicalPages']:
        page = pinned(reference)
        pn = page['physicalPage']
        assert pn not in pages and page['sourceId'] == source_id
        assert page['sourceSha256'] == metadata['sha256']
        pinned(page['rawPage'])
        assert not page['pageGeometryNeedsReview'] and not page['dateTitleNeedsReview']
        pages[pn] = page
        if pn in geometry:
            original = geometry[pn]
            assert len(page['rows']) == len(original['rows'])
            assert page['sourceImageSha256'] == original['actualRenderedPngSha256FromPrimary']
            for row, expected in zip(page['rows'], original['rows']):
                assert row['sourceRowOnPage'] == expected['sourceRowOnPage']
                assert expected['nameRowBox'][1] <= row['sourceNameBand']['center'] < expected['nameRowBox'][3]
        else:
            assert not page['rows']
        for row in page['rows']:
            key = pn, row['sourceRowOnPage']
            assert key not in staged
            staged[key] = row
    assert set(pages) == set(range(1, inv['pdfPages'] + 1))
    assert len(staged) == source['rowCount'] == len(payload) == anchor['rasterNamedRows']
    manual = {}
    for reference in provenance['manualOverlayInputs']:
        scope = independent_review_overlay(reference, source_id, metadata['sha256'])
        assert not set(manual) & set(scope), 'Duplicate manual field'
        manual.update(scope)
    assert provenance['allNineSourceHoldoutsPassed'] is True
    all_holdout_pins = []
    all_holdout_fields = 0
    all_holdout_sources = set()
    for holdout_source in sorted(s['id'] for s in inventory['sources']):
        hp = AREA / 'reviews' / ('root-phsa-history-' + holdout_source.removeprefix('phsa-') + '-holdout-source-comparison.json')
        hr = read(hp)
        assert hr['sourceId'] not in all_holdout_sources
        all_holdout_sources.add(hr['sourceId'])
        assert hr['allRequestedFieldsMatchExactly'] and not hr['candidateChanges'] and not hr['unresolvedFields']
        hc = pinned(hr['candidate'])
        assert len(hc['rows']) == 10 and hc['sourceId'] == hr['sourceId']
        pinned(hr['sourceOnlyPacket'])
        pinned(hr['imageFirstTranscript'], False)
        all_holdout_fields += sum(len(r['reviewTargetFields']) for r in hc['rows'])
        all_holdout_pins.append(pin(hp))
    assert all_holdout_sources == {s['id'] for s in inventory['sources']}
    assert len(all_holdout_pins) == 9 and all_holdout_fields == 222
    assert len(provenance['rootHoldoutComparisons']) == 1
    holdouts = {}
    for reference in provenance['rootHoldoutComparisons']:
        receipt = pinned(reference)
        assert receipt['sourceId'] == source_id
        assert receipt['allRequestedFieldsMatchExactly'] and not receipt['candidateChanges'] and not receipt['unresolvedFields']
        candidate = pinned(receipt['candidate'])
        pinned(receipt['sourceOnlyPacket'])
        pinned(receipt['imageFirstTranscript'], False)
        for row in candidate['rows']:
            for field in row['reviewTargetFields']:
                key = row['physicalPage'], row['sourceRowOnPage'], field
                assert key not in holdouts and key not in manual
                holdouts[key] = row['expectedValues'][field]
    qualified = {}
    adoption_selections = set()
    retirement_records = []
    def record_adoption_selector(selector_ref, expected_adoption):
        old_ref, new_ref = independent_adoption_selection(selector_ref, source_id, metadata['sha256'])
        assert new_ref == expected_adoption
        selector_identity = exact_reference(selector_ref)
        if selector_identity not in adoption_selections:
            selector = pinned(selector_ref)
            for retired in selector.get('authorizedRetiredNameCases', []):
                retirement_records.append({**retired, 'rootAdoptionSupersession': selector_ref, 'effectiveRootAdoption': new_ref})
        adoption_selections.add(selector_identity)
    for item in source['rootAdoptedQualifiedNameCases']:
        key = item['physicalPage'], item['sourceRowOnPage']
        assert key not in qualified and item['sourceSha256'] == metadata['sha256']
        adoption = pinned(item['rootAdoption'])
        if item.get('rootAdoptionSupersession'):
            record_adoption_selector(item['rootAdoptionSupersession'], item['rootAdoption'])
        if item.get('closedCasePolicy'):
            for selector_ref, adopted_ref in independent_closed_policy_selections(item['closedCasePolicy'], item, source_id, metadata['sha256']):
                record_adoption_selector(selector_ref, adopted_ref)
        assert adoption['sourceSha256'] == metadata['sha256']
        for adoption_key, adoption_value in adoption.items():
            if isinstance(adoption_value, dict) and set(['path', 'sha256']) <= set(adoption_value):
                pinned(adoption_value, False)
            elif isinstance(adoption_value, list) and 'peer' in adoption_key.lower():
                for peer_reference in adoption_value:
                    if isinstance(peer_reference, dict) and set(['path', 'sha256']) <= set(peer_reference):
                        pinned(peer_reference, False)
        if adoption.get('acceptedQualifiedCases') is not True:
            assert item['rootAdoption']['sha256'] == '41410273e366a0cee07268d8d2af077fa95daef4edd9a5bfef9c00be35b3448c'
            assert adoption['decision'] == 'Adopt exactly14 qualified contextual source-glyph readings; no pixel-proved casing claim.'
            assert adoption['qualifiedNameCases'] == 14 and len(adoption['cases']) == 14
            assert adoption['mandatoryPublicWarning']
        adopted_cases = adoption.get('cases', adoption.get('exactCases', adoption.get('closedCases')))
        ledger_cases = []
        if adoption.get('exactCaseLedger'):
            exact_ledger = pinned(adoption['exactCaseLedger'])
            for list_key in ['qualifications', 'cases', 'sourceTypographyQualifications', 'sourceNameSegmentationExceptions', 'separateClosedRrMExceptionsAwaitingExactRootAdoption']:
                if isinstance(exact_ledger.get(list_key), list):
                    ledger_cases.extend(exact_ledger[list_key])
            adopted_cases = independent_scoped_adoption_cases(adoption, exact_ledger)
        if adoption.get('caseLedgerFile'):
            legacy_ledger = pinned({'path': str((AREA / 'reviews' / adoption['caseLedgerFile']).relative_to(ROOT)), 'sha256': adoption['caseLedgerSha256']})
            for list_key in ['qualifications', 'cases', 'sourceTypographyQualifications']:
                if isinstance(legacy_ledger.get(list_key), list):
                    ledger_cases.extend(legacy_ledger[list_key])
        if adoption.get('independentPeer'):
            pinned(adoption['independentPeer'])
        if adoption.get('independentPeerFile'):
            pinned({'path': str((AREA / 'reviews' / adoption['independentPeerFile']).relative_to(ROOT)), 'sha256': adoption['independentPeerSha256']})
        assert isinstance(adopted_cases, list)
        matching = [c for c in adopted_cases if (c['physicalPage'], c['sourceRowOnPage']) == key]
        assert len(matching) == 1
        assert source_case_name(matching[0]) == item['chosenName']
        original_case = item['originalCaseEvidence']
        assert original_case in adopted_cases or original_case in ledger_cases
        if adoption.get('requireClosedExactCaseBoundConsumerException'):
            assert adoption.get('publicSourceWarningRequired', adoption.get('publicWarningRequired')) is True
            assert adoption['noOtherNameOrMonetaryFieldAuthority'] is True
            # A closed singleton receipt may carry its primary and full finite set
            # at top level; array receipts bind exactly the matching row.
            authority = adoption if 'primary' in adoption else matching[0]
            assert (authority['physicalPage'], authority['sourceRowOnPage']) == key
            assert source_case_name(authority) == item['chosenName']
            if item['rootAdoption']['sha256'] == 'b0e0b7f4f0627b91d708d2a9b14cd6f28b6618bfda16db90688d67482cff42cd':
                # This exact older singleton pins the name-only600 view rather
                # than duplicating its source ledger's full-row300 hash.
                assert source_id == 'phsa-2019-20' and key == (7, 7)
                assert adoption['exactCaseLedger']['sha256'] == 'f781f5c14be0a38a56a8888f7c73d26bfbef68eae63190ddbdd38a61427c1e2c'
                original_view = original_case['actualSourceEvidence']
                assert authority['rootViewedActualSourceCropSha256'] == original_view['nameOnlyActual600DpiCropSha256']
                assert source_case_crop(original_case) == 'b033f7ff9b3241968092a610ca3305984d9e8aa15847e4a032b4bb416095bbaf'
            else:
                assert source_case_crop(authority) == source_case_crop(original_case)
            assert set(case_family(authority)) == set(case_family(original_case))
        assert item['completeAdoptionEvidence'] == adoption
        assert item['caseProvenByPixels'] is False and item['sourcePublicWarningRequired']
        qualified[key] = item
    current_root_refs = {exact_reference(item['rootAdoption']): item['rootAdoption'] for item in qualified.values()}
    for retired in source.get('rootAcceptedQualifiedNameRetirements', []):
        selector_ref = retired['rootAdoptionSupersession']
        effective_ref = retired['effectiveRootAdoption']
        reachable = False
        for live_ref in current_root_refs.values():
            ref, history = live_ref, set()
            while ref is not None:
                identity = exact_reference(ref)
                assert identity not in history, 'Cyclic current root-adoption history'
                history.add(identity)
                if ref == effective_ref:
                    reachable = True
                    break
                ref = pinned(ref).get('supersededRootAdoption')
            if reachable:
                break
        assert reachable, 'Retirement authority is not on an explicitly selected current root history'
        record_adoption_selector(selector_ref, effective_ref)
    retirement_key = lambda case: (case['sourceId'], case['physicalPage'], case['sourceRowOnPage'])
    expected_retirements = unique_rows(retirement_records, retirement_key)
    actual_retirements = unique_rows(source.get('rootAcceptedQualifiedNameRetirements', []), retirement_key)
    assert actual_retirements == expected_retirements, 'Exact source-name retirement provenance differs'
    expected_rows, route_counts, changes = [], collections.Counter(), collections.Counter()
    recorded = {(entry['row'][5], entry['sourceRowOnPage']): entry for entry in source['rows']}
    assert len(recorded) == len(source['rows']) == len(staged)
    for retired in retirement_records:
        k = retired['physicalPage'], retired['sourceRowOnPage']
        assert k not in qualified
        row = recorded[k]
        assert row['row'][1] == retired['currentDirectLiteral']
        assert row['fields']['name']['status'] == 'manual-original-image'
        assert row['fields']['name']['evidence'].get('nameTypographyQualification') is None
    seen_manual = set()
    monetary_confirmations = {}
    for key in sorted(staged):
        raw = staged[key]
        entry = recorded[key]
        assert set(entry['fields']) == set(FIELDS), 'Unexpected or missing salary field evidence route'
        assert entry['rawCandidateRow'] == raw['candidateRow']
        final = list(raw['candidateRow'])
        assert entry['originalRawFieldFlags'] == raw['fieldConflicts']
        for field, index in FIELDS.items():
            fk = (*key, field)
            proof = entry['fields'][field]
            route = proof['status']
            route_counts[(field, route)] += 1
            assert proof['originalRawFlags'] == raw['fieldConflicts'].get(field, [])
            if fk in manual:
                own = manual[fk]
                assert own['row']['rawCandidateRow'] == raw['candidateRow']
                assert proof['evidence']['overlay'] == own['overlay']
                final[index] = own['value']
                seen_manual.add(fk)
                if key in qualified and field == 'name':
                    assert route == 'manual-qualified-source-typography'
                    assert final[1] == qualified[key]['chosenName']
                    assert own['row']['nameTypographyQualification'] is not None
                else:
                    assert route == 'manual-original-image'
                    assert field != 'name' or own['row']['nameTypographyQualification'] is None
            elif fk in holdouts:
                assert route == 'manual-blind-source-holdout'
                assert final[index] == holdouts[fk]
            elif route == 'original-source-explicit-dash-geometry':
                glyph = raw['expenseOriginalImage']
                assert field == 'expenses' and final[4] is None and not raw['fieldConflicts'].get(field)
                assert not glyph['blank'] and glyph['matchesSourceCalibratedDashGeometry']
                assert glyph['connectedInkComponents'] == 1 and glyph['glyphWidth'] > glyph['glyphHeight'] > 0
                assert not any(reader and reader['expense']['kind'] == 'number' for reader in [raw['tesseract'], raw['rapidocr']])
            else:
                assert route in ['baseline-independent-reader-agreement', 'calibrated-paired-reader-confidence-corroboration'], (key, field, route, fk in manual, fk in holdouts)
                a, b = raw['tesseract'], raw['rapidocr']
                assert a is not None and b is not None
                if field == 'name':
                    assert normalized_name(a['name']) == normalized_name(b['name']) == final[1]
                else:
                    token = 'pay' if field == 'remuneration' else 'expense'
                    assert a[token]['kind'] == b[token]['kind'] == 'number'
                    assert type(final[index]) is int and final[index] > 0
                    assert a[token]['value'] == b[token]['value'] == final[index]
                flags = set(raw['fieldConflicts'].get(field, []))
                if route == 'calibrated-paired-reader-confidence-corroboration':
                    assert flags and flags <= CONFIDENCE[field]
                    assert proof['evidence']['corroborated'] and not proof['evidence']['exclusions']
                else:
                    assert not flags
            confirmation = proof.get('evidence', {}).get('freshIndependentSourceMoneyPeer')
            if confirmation is not None:
                assert field in ['remuneration', 'expenses']
                assert fk in manual and confirmation['confirmedValue'] == final[index]
                assert confirmation['sourceId'] == source_id and confirmation['sourceSha256'] == metadata['sha256']
                assert (confirmation['physicalPage'], confirmation['sourceRowOnPage'], confirmation['field']) == fk
                assert confirmation['effectiveAuthorOverlay'] == manual[fk]['overlay']
                independent_current_money_peer(confirmation, source_id, metadata['sha256'])
                pinned(confirmation['freshSourceImage'], False)
                pinned(confirmation['imageFirstTranscript'], False)
                monetary_confirmations[fk] = confirmation['peerComparison']
            if fk in manual and field in ['remuneration', 'expenses'] and final[index] is not None:
                token = 'pay' if field == 'remuneration' else 'expense'
                reader_values = [r[token]['value'] for r in [raw['tesseract'], raw['rapidocr']]
                                 if r is not None and r[token]['kind'] == 'number' and type(r[token]['value']) is int]
                if final[index] not in reader_values:
                    assert fk in monetary_confirmations, ('Missing fresh monetary peer', fk, final[index], reader_values)
            if final[index] != raw['candidateRow'][index]:
                assert fk in manual
                changes[field] += 1
        assert final == entry['row']
        assert final[0] == 'provincial-health-services-authority' and final[2] is None and final[5] == key[0]
        assert isinstance(final[1], str) and final[1], 'Named source observation cannot lose its literal name'
        assert type(final[3]) is int and (final[4] is None or type(final[4]) is int)
        expected_rows.append(final)
    assert seen_manual == set(manual)
    assert expected_rows == payload
    assert source['sourcePrintedControls'] == context['finalPagePrintedControls']
    pay = sum(r[3] for r in payload)
    expense = sum(r[4] for r in payload if r[4] is not None)
    residual = [pay - source['sourcePrintedControls']['remuneration'], expense - source['sourcePrintedControls']['expenses']]
    assert [pay, expense] == [source['diagnosticRemunerationSum'], source['diagnosticKnownExpenseSum']]
    assert residual == source['diagnosticControlResiduals']
    assert metadata['retainCompiledPartition'] is True
    assert metadata['rowCount'] == len(payload)
    assert [metadata['totalRemuneration'], metadata['totalExpenses']] == [pay, expense]
    assert metadata['scope'] == metadata['category'] == 'employee-remuneration'
    assert metadata['completeEmployeeSchedule'] is True
    assert metadata['publicationStatus'] == 'official-published-unsigned-standalone-schedule'
    assert metadata['publicWarning']
    if qualified:
        assert any(word in metadata['publicWarning'].lower() for word in ['typograph', 'glyph', 'compressed', 'i/l', 'segmentation'])
    if any(residual):
        assert 'residual' in metadata['publicWarning'].lower() or 'differ' in metadata['publicWarning'].lower()
    assert metadata['periodType'] == 'fiscal' and metadata['threshold'] == 75000 and metadata['thresholdComparison'] == '>'
    assert metadata['periodStart'] == metadata['year'][:4] + '-04-01'
    assert metadata['periodEnd'] == str(int(metadata['year'][:4]) + 1) + '-03-31'
    canonical_ref = pin(ROOT / args.canonical_closure)
    if provenance.get('rootCanonicalSourceClosure') is not None:
        assert provenance['rootCanonicalSourceClosure'] == canonical_ref
    canonical_check = independent_canonical_source(canonical_ref, source_id, metadata['sha256'], source, staged=staged)
    result = {
        'frozen': True, 'frozenAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reviewer': '/root/held_health_review', 'sourceId': source_id,
        'sourceSha256': metadata['sha256'], 'script': pin(Path(__file__)),
        'candidateMetadata': pin(metadata_path), 'payload': pin(data_path), 'provenance': pin(provenance_path),
        'independentHelperCodeComponents': list(_MONEY_HELPER_PINS.values()),
        'additionalExactHistoricalArchiveProofInputs': supplementary_archive_refs,
        'checkedCompletePhysicalPages': len(pages), 'checkedLiteralNamedRows': len(payload),
        'independentRawPlusOnlyExactPinnedOverlayReconstructionEqualsPayload': True,
        'allOriginalRowOrderMultiplicityAndNonreviewedFieldsPreserved': True,
        'everyFieldHasExactlyOneClosedEvidenceRoute': True,
        'qualifiedNameCases': len(qualified), 'rootHoldoutFields': len(holdouts),
        'manualImageFields': len(manual),
        'allNineExactSourceHoldoutReceipts': all_holdout_pins,
        'allNineBlindHoldoutFields': all_holdout_fields,
        'sourceSpecificHoldoutReceipts': provenance['rootHoldoutComparisons'],
        'freshIndependentMonetaryConfirmationFields': len(monetary_confirmations),
        'explicitOrdinaryOverlaySelectionEdgesVerified': ordinary_selection_count,
        'explicitRootAdoptionSelectionsVerified': len(adoption_selections),
        'exactRetiredWrongNameFamiliesVerified': len(retirement_records),
        'canonicalSourceDecisionAndHumanRecordReplay': canonical_check,
        'fieldRouteCounts': {field: {route: count for (f, route), count in route_counts.items() if f == field} for field in FIELDS},
        'changedFieldsFromRaw': dict(changes), 'remunerationSum': pay, 'knownExpenseSum': expense,
        'sourcePrintedControls': source['sourcePrintedControls'], 'literalSourceControlResiduals': residual,
        'expenseNullRows': sum(r[4] is None for r in payload), 'expenseExplicitZeroRows': sum(r[4] == 0 for r in payload),
        'expenseNegativeRows': sum(r[4] is not None and r[4] < 0 for r in payload),
        'semanticAndMonetaryControlAcceptanceNotClaimedByReplayAlone': True,
        'limits': [
            'Independent implementation reads raw pages, explicit requested-field reviews and original geometry without importing author ledger/finalizer code.',
            'Personally image-reviewed cells are limited to this reviewer\'s separately frozen source receipts; machine agreement is not represented as personal image transcription.',
            'Pinned peer/root decisions are verified as provenance, not relabelled independent visual proof for every field.',
            'Exact source control residuals are diagnostics; this replay does not explain them or change a cell to balance.',
            'This per-source candidate replay does not accept the complete nine-cohort tranche or promote a source status.',
        ],
    }
    if args.check_only:
        print(json.dumps({'schemaProbeOnly': True, 'noReceiptWrittenOrScriptFrozen': True,
                          'sourceId': source_id, 'rows': len(payload), 'residuals': residual,
                          'canonicalTargets': canonical_check['targets'], 'qualifiedNames': len(qualified)}))
    else:
        out.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'path': str(out.relative_to(ROOT)), 'sha256': digest(out.read_bytes()), 'rows': len(payload), 'residuals': residual}))


if __name__ == '__main__':
    main()
