#!/usr/bin/env python3
"""Actual frozen-schema tests for the independent v7 tuple-money reader."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import finish_salary_phsa_review_money_tuple_v7 as reader
AREA = ROOT / 'research/salaries/queue-completion-2026-11-01/phsa/triangulation'


class Loader:
    def __init__(self):
        self.aliases = {}
        for path in sorted(AREA.glob('archived-source-money-views-*.json')):
            for row in json.loads(path.read_text()).get('rows', []):
                source = row['originalReference']
                key = source['path'], source['sha256']
                archive = row['archivedExactBytes']
                if key in self.aliases:
                    assert self.aliases[key] == archive
                self.aliases[key] = archive

    def __call__(self, ref, parse=True):
        selected = self.aliases.get((ref['path'], ref['sha256']), ref)
        path = Path(selected['path'])
        if not path.is_absolute():
            path = ROOT / path
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != ref['sha256']:
            raise ValueError('Test loader byte pin differs')
        return json.loads(data) if parse else data


LOAD = Loader()
FIXTURES = {}
for sha, spec in reader.SPECS.items():
    ref = {'path': reader.BASE + 'money-peer-confirmations-' + spec[0] + '.json', 'sha256': sha}
    FIXTURES[spec[0]] = (ref, LOAD(ref))


def entry(mode, index=0):
    ref, fixture = FIXTURES[mode]
    return {**copy.deepcopy(fixture['confirmations'][index]), 'confirmationLedger': copy.deepcopy(ref)}


def call(value, load=LOAD):
    return reader.verify(value, reader.SOURCE, reader.PDF_SHA, load)


class ActualSchemas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reader._CACHE.clear()
        reader._AUDIT.clear()
        for mode in ['009', '013', '015', '018']:
            ref, fixture = FIXTURES[mode]
            for row in fixture['confirmations']:
                call({**copy.deepcopy(row), 'confirmationLedger': copy.deepcopy(ref)})

    def test_all_175_live_frozen_confirmations(self):
        self.assertEqual(sum(len(v['confirmations']) for _, v in FIXTURES.values()), 175)
        self.assertEqual(sum(v['positiveFields'] for v in reader._AUDIT.values()), 175)
        self.assertEqual(sum(v['sourceTargets'] for v in reader._AUDIT.values()), 176)
        self.assertEqual(sum(v['native300RgbExact'] for v in reader._AUDIT.values()), 176)
        self.assertEqual(sum(v['oldFullRow300RgbExact'] for v in reader._AUDIT.values()), 176)

    def test_boolean_float_null_zero_negative_string_amounts_rejected(self):
        for value in [True, False, None, 0, -1, 79476.0, '79476']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                row = entry('009'); row['confirmedValue'] = value; call(row)

    def test_unknown_ledger_sha_and_path_rejected(self):
        for ref in [{'path': reader.BASE + 'money-peer-confirmations-009.json', 'sha256': '0' * 64},
                    {'path': reader.BASE + 'money-peer-confirmations-013.json', 'sha256': FIXTURES['009'][0]['sha256']}]:
            with self.assertRaises(ValueError):
                row = entry('009'); row['confirmationLedger'] = ref; call(row)

    def test_wrong_identity_or_field_or_tuple_rejected(self):
        for key, value in [('sourceId', 'phsa-2020-21'), ('sourceSha256', '1' * 64), ('field', 'name'),
                           ('physicalPage', True), ('sourceRowOnPage', 0), ('physicalPage', 56)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                row = entry('009'); row[key] = value; call(row)

    def test_overlay_image_and_untracked_entry_mutations_rejected(self):
        for mutate in [lambda r: r['effectiveAuthorOverlay'].update(sha256='2' * 64),
                       lambda r: r['freshSourceImage'].update(sha256='3' * 64),
                       lambda r: r['freshSourceImage']['original300DpiPixelBox'].__setitem__(0, 0),
                       lambda r: r.update(confirmationSupersession={'not': 'normalized'}),
                       lambda r: r.update(extraProof=True)]:
            with self.assertRaises(ValueError):
                row = entry('009'); mutate(row); call(row)

    def test_printed_dash_never_becomes_numeric_confirmation(self):
        row = entry('009'); row.update(physicalPage=61, sourceRowOnPage=41, field='expenses', confirmedValue=None)
        with self.assertRaises(ValueError):
            call(row)
        audit = reader._AUDIT[FIXTURES['009'][0]['sha256']]
        self.assertEqual(audit['dashFields'], 1)
        self.assertEqual(audit['positiveFields'], 50)

    def test_rejected_secondary_restores_correct_raw_without_new_first_error(self):
        fixture = FIXTURES['009'][1]
        row = next(r for r in fixture['confirmations']
                   if (r['physicalPage'], r['sourceRowOnPage'], r['field']) == (56, 51, 'expenses'))
        self.assertEqual(row['confirmedValue'], 4558)
        audit = reader._AUDIT[FIXTURES['009'][0]['sha256']]
        self.assertEqual(audit['authorFirstCorrections'], 5)
        self.assertEqual(audit['authorRejectedSecondaryReadings'], 1)

    def test_exact_cached_member_still_checked(self):
        original = reader._reconstruct
        try:
            def forbidden(*args):
                raise AssertionError('Unexpected second reconstruction of immutable SHA')
            reader._reconstruct = forbidden
            self.assertIsNone(call(entry('009')))
            changed = entry('009'); changed['confirmedValue'] += 1
            with self.assertRaises(ValueError):
                call(changed)
        finally:
            reader._reconstruct = original

    def test_duplicate_or_bool_raw_tuple_rejected(self):
        raw = LOAD(LOAD(FIXTURES['009'][1]['peerInputs'][0])['independentImageFirstTranscript'])['rows']
        with self.assertRaises(ValueError):
            reader._rows([raw[0], copy.deepcopy(raw[0])])
        bad = copy.deepcopy(raw[0]); bad['physicalPage'] = True
        with self.assertRaises(ValueError):
            reader._rows([bad])

    def test_peer_amendment_wrong_first_value_or_scope_rejected(self):
        final = LOAD(FIXTURES['009'][1]['peerInputs'][0]); targets = reader._rows(LOAD(final['sourceOnlyPacket'])['rows'])
        raw = LOAD(final['independentImageFirstTranscript']); raw_map = reader._rows(raw['rows'])
        values = {k: r['literalSourceValue'] for k, r in raw_map.items()}
        amendment = LOAD(final['peerOwnAdditiveSourceCorrections'])
        for mutate in [lambda a: a['changes'][0].update(firstPeerSourceValue=1),
                       lambda a: a['changes'][0].update(finalSourceValue=True),
                       lambda a: a['changes'][0].update(physicalPage=1),
                       lambda a: a['changes'].append(copy.deepcopy(a['changes'][0]))]:
            bad = copy.deepcopy(amendment); mutate(bad)
            with self.assertRaises(ValueError):
                reader._amend_peer(values, bad, final['independentImageFirstTranscript'], targets,
                                   final['batch'], LOAD)

    def test_actual_author_raw_blindness_and_missing_field_mutations(self):
        final = LOAD(FIXTURES['009'][1]['peerInputs'][0])
        targets = reader._rows(LOAD(final['sourceOnlyPacket'])['rows'])
        overlay = LOAD(FIXTURES['009'][1]['confirmations'][0]['effectiveAuthorOverlay'])
        review = LOAD(overlay['reviewInput'])
        views = LOAD(review['nativeFieldCompanion'])
        view_rows = {(r['physicalPage'], r['sourceRowOnPage']): r for r in views['rows']}
        original = LOAD(final['authorOriginalFrozenTranscript'])
        for kind in ['candidate-seen', 'missing-money']:
            mutated = copy.deepcopy(original)
            if kind == 'candidate-seen':
                mutated['candidateOpenedBeforeFreeze'] = True
            else:
                target = next(iter(targets.values()))
                row = next(r for r in mutated['transcript'] if r['sequence'] == target['sequence'])
                del row['literalValues'][target['field']]
            data = (json.dumps(mutated) + '\n').encode()
            ref = {'path': 'mutation/author-raw.json', 'sha256': hashlib.sha256(data).hexdigest()}
            def supplied(r, parse=True):
                return (json.loads(data) if parse else data) if r == ref else LOAD(r, parse)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                reader._raw_author(ref, final['batch'], targets, view_rows, review, supplied, '009')

    def test_legacy_no_batch_raw_requires_exact_target_manifest_sha(self):
        final = LOAD(FIXTURES['013'][1]['peerInputs'][0])
        targets = reader._rows(LOAD(final['sourceOnlyPacket'])['rows'])
        overlay = LOAD(FIXTURES['013'][1]['confirmations'][0]['effectiveAuthorOverlay'])
        review = LOAD(overlay['reviewInput'])
        raw = LOAD(final['authorOriginalFrozenTranscript'])
        self.assertNotIn('batch', raw)
        raw['sourceOnlyTargetViewsSha256'] = '0' * 64
        data = json.dumps(raw).encode()
        ref = {'path': 'mutation/legacy-raw.json', 'sha256': hashlib.sha256(data).hexdigest()}
        def supplied(r, parse=True):
            return (json.loads(data) if parse else data) if r == ref else LOAD(r, parse)
        with self.assertRaises(ValueError):
            reader._raw_author(ref, final['batch'], targets, {}, review, supplied, '013')

    def test_actual_pdf_native_crop_geometry_mutation_rejected(self):
        final = LOAD(FIXTURES['018'][1]['peerInputs'][0])
        target = LOAD(final['sourceOnlyPacket'])['rows'][0]
        key = reader._key(target)
        native = copy.deepcopy(target['native300SourceField'])
        native['originalPdf300DpiPixelBox'][0] += 1
        old = target['originalFullRowCrop']
        image_row = {'cropPath': old['path'], 'cropSha256': old['sha256'],
                     'cropRectOriginal300DpiPixels': old['original300DpiPixelBox']}
        with self.assertRaises(ValueError):
            reader._pixels({key: target}, {key: (target['actual1200SourceField'], 1200, None)},
                           {key: native}, {key[:2]: image_row}, LOAD)

    def test_document_byte_mismatch_rejected_even_if_loader_returns_bytes(self):
        ref = FIXTURES['009'][0]
        with self.assertRaises(ValueError):
            reader._document(ref, lambda r, parse=True: b'{}')

    def test_json_duplicate_members_rejected(self):
        data = b'{"sourceId":"one","sourceId":"two"}'
        ref = {'path': 'mutation.json', 'sha256': hashlib.sha256(data).hexdigest()}
        with self.assertRaises(ValueError):
            reader._document(ref, lambda r, parse=True: data)

    def test_hidden_transparent_rgb_is_not_visible_source_ink(self):
        from PIL import Image
        buffer = io.BytesIO()
        Image.new('RGBA', (2, 2), (0, 0, 0, 0)).save(buffer, format='PNG')
        data = buffer.getvalue()
        ref = {'path': 'mutation/transparent-ink.png', 'sha256': hashlib.sha256(data).hexdigest()}
        visible = reader._image(ref, lambda r, parse=True: data)
        self.assertEqual(visible.tobytes(), bytes([255, 255, 255]) * 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
