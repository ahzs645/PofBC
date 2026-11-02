#!/usr/bin/env python3
"""Actual-schema checks for the independent ordered monetary receipt reader.

No producer or v7 implementation is imported. Mutation loaders intentionally
substitute parsed JSON after the ordinary byte guard, to test semantic checks
rather than merely proving that changing a frozen file changes its SHA.
"""
import collections
import copy
import gzip
import hashlib
import json
from pathlib import Path
import unittest

import finish_salary_phsa_review_money_ordered_v7 as reader


ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/queue-completion-2026-11-01/phsa/triangulation'


class ActualFixture:
    def __init__(self, number):
        self.overrides = {}
        self.json_cache = {}
        self.aliases = {}
        for path in sorted(AREA.glob('archived-source-money-views-*.json')):
            document = json.loads(path.read_bytes())
            for row in document['rows']:
                old, archived = row['originalReference'], row['archivedExactBytes']
                key = old['path'], old['sha256']
                if key in self.aliases:
                    assert self.aliases[key] == archived
                self.aliases[key] = archived
        path = AREA / f'money-peer-confirmations-{number}.json'
        self.reference = {'path': str(path.relative_to(ROOT)),
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        assert self.reference['sha256'] in reader.CONFIG
        self.ledger = self.load(self.reference)
        self.confirmation = {**copy.deepcopy(self.ledger['confirmations'][0]),
                             'confirmationLedger': self.reference}
        self.reader = self.load

    def load(self, reference, parse=True):
        path = ROOT / reference['path']
        if not path.resolve().is_relative_to(ROOT):
            assert parse is False
            alias = self.aliases[reference['path'], reference['sha256']]
            assert alias['sha256'] == reference['sha256']
            path = ROOT / alias['path']
        assert path.resolve().is_relative_to(ROOT)
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == reference['sha256']
        if not parse:
            return raw
        if reference['path'] in self.overrides:
            return self.overrides[reference['path']]
        key = reference['path'], reference['sha256']
        if key not in self.json_cache:
            self.json_cache[key] = json.loads(gzip.decompress(raw) if path.suffix == '.gzip' else raw)
        return self.json_cache[key]

    def mutate(self, reference):
        document = copy.deepcopy(self.load(reference))
        self.overrides[reference['path']] = document
        return document

    def verify(self, confirmation=None):
        return reader.verify(self.confirmation if confirmation is None else confirmation,
                             reader.SOURCE, reader.SOURCE_SHA, self.reader)


class ActualOrderedSchemas(unittest.TestCase):
    def setUp(self):
        reader._CACHE.clear()

    def denied(self, fixture):
        with self.assertRaises((ValueError, AssertionError, KeyError, IndexError)):
            fixture.verify()

    def test_00_all_actual_116_fields_and_original_pixels(self):
        total = 0
        for number in ['002', '003', '008', '010']:
            with self.subTest(ledger=number):
                fixture = ActualFixture(number)
                for row in fixture.ledger['confirmations']:
                    fixture.verify({**row, 'confirmationLedger': fixture.reference})
                    total += 1
        self.assertEqual(total, 116)
        modes = collections.Counter(reader._PIXEL_MODES.values())
        self.assertEqual(modes['whole-page600-integer-crop-rgb-exact'], 113)
        self.assertEqual(modes['exact-listed-historical-partial600-rgb-plus-canonical-whole300-png-sha'], 3)
        self.assertEqual({k for k, mode in reader._PIXEL_MODES.items() if mode.startswith('exact-listed')},
                         set(reader.HISTORICAL_PARTIAL_600))

    def test_unknown_frozen_ledger_fails(self):
        fixture = ActualFixture('002')
        fixture.confirmation['confirmationLedger']['sha256'] = '0' * 64
        self.denied(fixture)

    def test_another_fiscal_original_fails(self):
        fixture = ActualFixture('003')
        with self.assertRaises(ValueError):
            reader.verify(fixture.confirmation, 'phsa-2018-19', reader.SOURCE_SHA, fixture.reader)

    def test_flat_confirmation_cannot_claim_name_field(self):
        fixture = ActualFixture('008')
        fixture.confirmation['field'] = 'name'
        self.denied(fixture)

    def test_null_zero_bool_float_and_numeric_string_are_not_money(self):
        for value in [None, 0, True, 8977.0, '8977']:
            with self.subTest(value=value):
                fixture = ActualFixture('002')
                fixture.confirmation['confirmedValue'] = value
                self.denied(fixture)

    def test_confirmation_supersession_must_be_normalized_by_caller(self):
        fixture = ActualFixture('003')
        fixture.confirmation['confirmationSupersession'] = fixture.reference
        self.denied(fixture)

    def test_missing_unrequested_confirmation_is_detected(self):
        fixture = ActualFixture('010')
        fixture.mutate(fixture.reference)['confirmations'].pop()
        self.denied(fixture)

    def test_duplicate_confirmation_cannot_preserve_claimed_count(self):
        fixture = ActualFixture('008')
        ledger = fixture.mutate(fixture.reference)
        ledger['confirmations'][-1] = copy.deepcopy(ledger['confirmations'][0])
        self.denied(fixture)

    def test_late_confirmation_float_does_not_equal_integer(self):
        fixture = ActualFixture('003')
        row = fixture.mutate(fixture.reference)['confirmations'][-1]
        row['confirmedValue'] = float(row['confirmedValue'])
        self.denied(fixture)

    def test_wrong_known_overlay_cannot_be_substituted(self):
        fixture = ActualFixture('002')
        fixture.mutate(fixture.reference)['confirmations'][-1]['effectiveAuthorOverlay'] = fixture.reference
        self.denied(fixture)

    def test_peer_and_author_raw_roles_cannot_be_swapped(self):
        fixture = ActualFixture('010')
        ledger = fixture.mutate(fixture.reference)
        ledger['peerInputs'][1], ledger['peerInputs'][-1] = ledger['peerInputs'][-1], ledger['peerInputs'][1]
        self.denied(fixture)

    def test_extra_peer_input_cannot_widen_coverage(self):
        fixture = ActualFixture('003')
        fixture.mutate(fixture.reference)['peerInputs'].append(fixture.reference)
        self.denied(fixture)

    def test_ordered_raw_cannot_be_shifted_to_neighbour_fields(self):
        for number in ['003', '008', '010']:
            with self.subTest(ledger=number):
                fixture = ActualFixture(number)
                raw = fixture.mutate(fixture.ledger['peerInputs'][1])
                values = raw['readingsInPacketOrder']
                raw['readingsInPacketOrder'] = values[1:] + values[:1]
                self.denied(fixture)

    def test_ordered_raw_requires_full_target_length(self):
        fixture = ActualFixture('003')
        fixture.mutate(fixture.ledger['peerInputs'][1])['readingsInPacketOrder'].pop()
        self.denied(fixture)

    def test_raw_role_timing_cannot_be_relabelled_source_first(self):
        fixture = ActualFixture('010')
        fixture.mutate(fixture.ledger['peerInputs'][1])['authorOrOcrChoicesOpened'] = True
        self.denied(fixture)

    def test_unresolved_source_money_cannot_close(self):
        fixture = ActualFixture('008')
        fixture.mutate(fixture.ledger['peerInputs'][1])['unresolvedFields'] = [1]
        self.denied(fixture)

    def test_author_rows_are_joined_by_exact_tuple_not_array_order(self):
        fixture = ActualFixture('010')
        author = fixture.mutate(fixture.ledger['peerInputs'][3])
        author['rows'] = list(reversed(author['rows']))
        self.assertIsNone(fixture.verify())

    def test_author_neighbour_value_cannot_be_borrowed(self):
        fixture = ActualFixture('010')
        author = fixture.mutate(fixture.ledger['peerInputs'][3])
        author['rows'][0]['finalAuthorSourceValue'] = author['rows'][1]['finalAuthorSourceValue']
        self.denied(fixture)

    def test_author_field_cannot_change_between_pay_and_expenses(self):
        fixture = ActualFixture('010')
        author = fixture.mutate(fixture.ledger['peerInputs'][3])
        author['rows'][0]['field'] = 'remuneration'
        self.denied(fixture)

    def test_peer_source_crop_hash_cannot_be_borrowed(self):
        fixture = ActualFixture('003')
        packet = fixture.mutate(fixture.ledger['peerInputs'][3])
        packet['rows'][0]['originalFullRowCropSha256'] = packet['rows'][1]['originalFullRowCropSha256']
        self.denied(fixture)

    def test_source_year_header_is_checked(self):
        fixture = ActualFixture('008')
        fixture.mutate(fixture.ledger['peerInputs'][2])['sourceSha256'] = 'a' * 64
        self.denied(fixture)

    def test_source_packet_cannot_drop_a_field_with_same_receipt_count(self):
        fixture = ActualFixture('002')
        fixture.mutate(fixture.ledger['peerInputs'][2])['rows'].pop()
        self.denied(fixture)

    def test_pixel_proof_cannot_use_another_packet_hash(self):
        fixture = ActualFixture('003')
        fixture.mutate(fixture.ledger['peerInputs'][4])['sourceOnlyPacketSha256'] = 'a' * 64
        self.denied(fixture)

    def test_numeric_alternative_is_not_a_valid_money_qualification(self):
        fixture = ActualFixture('010')
        fixture.mutate(fixture.ledger['peerInputs'][0])['rows'][0]['visibleAlternatives'] = [2510, 2518]
        self.denied(fixture)

    def test_comparison_literal_float_does_not_equal_int(self):
        fixture = ActualFixture('008')
        fixture.mutate(fixture.ledger['peerInputs'][0])['rows'][0]['literalSourceValue'] = 132360.0
        self.denied(fixture)

    def test_boolean_error_count_is_not_integer_one(self):
        fixture = ActualFixture('003')
        fixture.mutate(fixture.ledger['peerInputs'][0])['authorOwnFirstReadingCorrections'] = True
        self.denied(fixture)

    def test_peer_first_mistake_cannot_disappear_from_amendment(self):
        fixture = ActualFixture('003')
        fixture.mutate(fixture.ledger['peerInputs'][5])['firstRootReading'] = 4301
        self.denied(fixture)

    def test_author_error_history_is_not_just_an_aggregate_count(self):
        fixture = ActualFixture('010')
        fixture.mutate(fixture.ledger['peerInputs'][5])['ownCorrections'].pop()
        self.denied(fixture)

    def test_money89_rejected_intermediate_must_remain_visible(self):
        fixture = ActualFixture('008')
        fixture.mutate(fixture.ledger['peerInputs'][6])['earlierOwn600RereadAlsoWrong'] = 3757
        self.denied(fixture)

    def test_money89_third_printed_literal_has_exact_grouping_and_digits(self):
        fixture = ActualFixture('008')
        fixture.mutate(fixture.ledger['peerInputs'][7])['literalPrinted'] = '37,57'
        self.denied(fixture)

    def test_legacy_third_source_amount_cannot_change(self):
        fixture = ActualFixture('002')
        comparison = fixture.load(fixture.ledger['peerInputs'][0])
        third = comparison['sourceBasedAuthorCorrectionsRequired'][0]['freshThirdSourceImagePeer']
        fixture.mutate(third)['literalSourceInteger'] = 104807
        self.denied(fixture)

    def test_source_geometry_changes_are_checked_even_after_pixel_cache(self):
        fixture = ActualFixture('010')
        packet = fixture.mutate(fixture.ledger['peerInputs'][2])
        packet['rows'][0]['actual600PdfClip'][0] += 0.24
        self.denied(fixture)

    def test_real_borrowed_source_image_fails_actual_original_rgb(self):
        fixture = ActualFixture('003')
        packet = fixture.mutate(fixture.ledger['peerInputs'][3])
        target = packet['rows'][0]
        box = target['sourceNative300']['originalPdf300DpiPixelBox']
        borrowed = next(row for row in packet['rows'][1:]
                        if row['field'] == target['field'] and
                        row['sourceNative300']['originalPdf300DpiPixelBox'][3] -
                        row['sourceNative300']['originalPdf300DpiPixelBox'][1] == box[3] - box[1])
        target['actual600SourceField'] = borrowed['actual600SourceField']
        author = fixture.mutate(fixture.ledger['peerInputs'][2])
        author['rows'][0]['actual600SourceField'] = borrowed['actual600SourceField']
        ledger = fixture.mutate(fixture.reference)
        ledger['confirmations'][0]['freshSourceImage'] = borrowed['actual600SourceField']
        with self.assertRaisesRegex(ValueError, 'whole600 source field RGB difference'):
            fixture.verify()

    def test_native300_sha_is_reconstructed_without_external_file_trust(self):
        fixture = ActualFixture('003')
        packet = fixture.mutate(fixture.ledger['peerInputs'][3])
        target = packet['rows'][0]
        target['sourceNative300']['sha256'] = 'f' * 64
        author = fixture.load(fixture.ledger['peerInputs'][2])
        raw = fixture.load(author['independentOriginalImageFirstTranscript'])
        views = fixture.mutate(raw['sourceOnlyTargetViews'])
        row = next(row for row in views['rows'] if row['sequence'] == target['sequence'])
        view = next(view for view in row['sourceNativeTargetViews'] if view['field'] == target['field'])
        view['sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'whole300 native field PNG hash differs'):
            fixture.verify()

    def test_postchoice_history_cannot_claim_prepeer_correction(self):
        fixture = ActualFixture('008')
        comparison = fixture.mutate(fixture.ledger['peerInputs'][0])
        comparison['authorOwnCorrectionAlreadyFrozenBeforeRootFirstReading'] = fixture.ledger['peerInputs'][6]
        self.denied(fixture)

    def test_overlay_physical_page_float_is_not_an_integer(self):
        fixture = ActualFixture('003')
        overlay = fixture.mutate(fixture.confirmation['effectiveAuthorOverlay'])
        overlay['overlays'][0]['resolvedRow'][5] = 13.0
        self.denied(fixture)

    def test_effective_author_resolution_scope_cannot_drop_a_row(self):
        fixture = ActualFixture('010')
        overlay = fixture.load(fixture.confirmation['effectiveAuthorOverlay'])
        fixture.mutate(overlay['reviewInput'])['resolutions'].pop()
        self.denied(fixture)

    def test_third_source_timing_flags_cannot_be_renamed(self):
        fixture = ActualFixture('008')
        third = fixture.mutate(fixture.ledger['peerInputs'][7])
        third['blindness'].pop('expectedAmountSupplied')
        third['blindness']['unrelatedFalseFlag'] = False
        self.denied(fixture)

    def test_pixel_proof_cannot_declare_failed_original_image_sha(self):
        fixture = ActualFixture('008')
        fixture.mutate(fixture.ledger['peerInputs'][8])['rows'][0]['actual600PngSha256Matches'] = False
        self.denied(fixture)


if __name__ == '__main__':
    unittest.main()
