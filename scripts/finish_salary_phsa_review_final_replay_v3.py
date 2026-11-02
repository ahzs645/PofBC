#!/usr/bin/env python3
"""Independent raw-page/explicit-overlay replay of one complete PHSA candidate.

Does not import the author's finalizer, ledger or resolution implementation.
Writes only a new independent review receipt. No candidate/raw data mutations.
Version 3 additionally reproduces unretained exact-serif Mac context crops from pinned actual page pixels.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import io
import json
import re
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


def pinned(reference, parse=True):
    path = ROOT / reference['path']
    assert path.resolve().is_relative_to(ROOT)
    assert digest(path.read_bytes()) == reference['sha256'], str(path)
    return read(path) if parse else path.read_bytes()


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--metadata', help='Explicit versioned candidate metadata path')
    args = parser.parse_args()
    out = ROOT / args.output
    assert not out.exists(), 'Never overwrite a frozen independent review'
    source_id = args.source
    metadata_path = ROOT / args.metadata if args.metadata else AREA / 'phsa/candidates' / (source_id + '-source.json')
    metadata = read(metadata_path)
    data_path = COLLECTION / metadata['file']
    assert digest(data_path.read_bytes()) == metadata['dataSha256']
    payload = read(data_path)
    provenance_path = COLLECTION / metadata['provenanceFile']
    assert digest(provenance_path.read_bytes()) == metadata['provenanceSha256']
    provenance = read(provenance_path)
    source = provenance['originalRowsAndPerFieldResolution']
    assert source['sourceId'] == source_id and source['sourceSha256'] == metadata['sha256']
    assert provenance['dataSha256'] == metadata['dataSha256']
    assert source['completePhysicalSource'] and not source['pendingFields']
    inventory = pinned(provenance['sourceInventory'])
    inv = next(s for s in inventory['sources'] if s['id'] == source_id)
    assert inv['sourceSha256'] == metadata['sha256']
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
    for hp in sorted((AREA / 'reviews').glob('root-phsa-history-*-holdout-source-comparison.json')):
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
    for item in source['rootAdoptedQualifiedNameCases']:
        key = item['physicalPage'], item['sourceRowOnPage']
        assert key not in qualified and item['sourceSha256'] == metadata['sha256']
        adoption = pinned(item['rootAdoption'])
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
        if adoption.get('exactCaseLedger'):
            exact_ledger = pinned(adoption['exactCaseLedger'])
            if adopted_cases is None:
                adopted_cases = exact_ledger.get('qualifications', exact_ledger.get('cases', exact_ledger.get('sourceTypographyQualifications')))
        if adoption.get('caseLedgerFile'):
            pinned({'path': str((AREA / 'reviews' / adoption['caseLedgerFile']).relative_to(ROOT)), 'sha256': adoption['caseLedgerSha256']})
        if adoption.get('independentPeer'):
            pinned(adoption['independentPeer'])
        if adoption.get('independentPeerFile'):
            pinned({'path': str((AREA / 'reviews' / adoption['independentPeerFile']).relative_to(ROOT)), 'sha256': adoption['independentPeerSha256']})
        assert isinstance(adopted_cases, list)
        matching = [c for c in adopted_cases if (c['physicalPage'], c['sourceRowOnPage']) == key]
        assert len(matching) == 1
        assert source_case_name(matching[0]) == item['chosenName']
        assert item['originalCaseEvidence'] == matching[0]
        assert item['completeAdoptionEvidence'] == adoption
        assert item['caseProvenByPixels'] is False and item['sourcePublicWarningRequired']
        qualified[key] = item
    expected_rows, route_counts, changes = [], collections.Counter(), collections.Counter()
    recorded = {(entry['row'][5], entry['sourceRowOnPage']): entry for entry in source['rows']}
    assert len(recorded) == len(source['rows']) == len(staged)
    seen_manual = set()
    monetary_confirmations = {}
    for key in sorted(staged):
        raw = staged[key]
        entry = recorded[key]
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
                confirmation_ledger = pinned(confirmation['confirmationLedger'])
                assert confirmation_ledger['noSalaryValuesChanged']
                expected_confirmation = {k: v for k, v in confirmation.items() if k != 'confirmationLedger'}
                assert expected_confirmation in confirmation_ledger['confirmations']
                peer = pinned(confirmation['peerComparison'])
                assert not peer['candidateChanges'] and not peer['unresolvedFields']
                peer_rows = [r for r in peer['rows'] if r['sourceId'] == source_id and (r['physicalPage'], r['sourceRowOnPage'], r['field']) == fk]
                assert len(peer_rows) == 1 and peer_rows[0]['literalSourceValue'] == final[index]
                assert peer_rows[0]['actualSource600DpiPixelsIndependentlyReproducedExactly']
                pinned(confirmation['freshSourceImage'], False)
                pinned(confirmation['imageFirstTranscript'], False)
                monetary_confirmations[fk] = confirmation['peerComparison']
            if fk in manual and field in ['remuneration', 'expenses'] and final[index] is not None:
                token = 'pay' if field == 'remuneration' else 'expense'
                reader_values = [(r.get(token) or {}).get('value') for r in [raw['tesseract'], raw['rapidocr']] if r is not None]
                if final[index] not in reader_values:
                    assert fk in monetary_confirmations, ('Missing fresh monetary peer', fk, final[index], reader_values)
            if final[index] != raw['candidateRow'][index]:
                assert fk in manual
                changes[field] += 1
        assert final == entry['row']
        assert final[0] == 'provincial-health-services-authority' and final[2] is None and final[5] == key[0]
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
    result = {
        'reviewer': '/root/held_health_review', 'sourceId': source_id,
        'sourceSha256': metadata['sha256'], 'script': pin(Path(__file__)),
        'candidateMetadata': pin(metadata_path), 'payload': pin(data_path), 'provenance': pin(provenance_path),
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
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'path': str(out.relative_to(ROOT)), 'sha256': digest(out.read_bytes()), 'rows': len(payload), 'residuals': residual}))


if __name__ == '__main__':
    main()
