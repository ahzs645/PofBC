"""Actual-schema checks and adversarial mutations for complete-author modes 011/012."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import finish_salary_phsa_review_money_complete_v7 as subject


ROOT = Path(__file__).resolve().parents[1]
TRI = ROOT / subject.BASE / 'phsa/triangulation'


class Loader:
    """Independent byte loader; archive aliases use exact original reference pins."""
    def __init__(self):
        self.aliases = {}
        for path in TRI.glob('archived-source-money-views-*.json'):
            value = json.loads(path.read_text())
            for row in value.get('rows', []):
                old, new = row['originalReference'], row['archivedExactBytes']
                if old['sha256'] != new['sha256']:
                    raise ValueError('archive changed bytes')
                self.aliases[(old['path'], old['sha256'])] = new['path']

    def __call__(self, ref, parse=True):
        path = Path(ref['path'])
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            path = ROOT / self.aliases[(ref['path'], ref['sha256'])]
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != ref['sha256']:
            raise ValueError('test loader hash mismatch')
        return json.loads(data) if parse else data


class ChangedDocuments(subject._Pinned):
    """Keep real schema/documents, then inject semantic faults after pin loading.

    This deliberately models semantic faults independently of the earlier hash
    guard. Production _Pinned never permits such mutated immutable documents.
    """
    def __init__(self, load, path_fragment, change):
        super().__init__(load)
        self.fragment, self.change = path_fragment, change
        self.changed = False

    def json(self, ref):
        value = copy.deepcopy(super().json(ref))
        if self.fragment in ref['path']:
            self.change(value)
            self.changed = True
        return value


class CompleteAuthorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = Loader()
        subject._CACHE.clear()
        cls.ledgers = [cls.loader(ref) for ref in subject.LEDGERS]

    def member(self, which=0, index=0):
        return {**copy.deepcopy(self.ledgers[which]['confirmations'][index]),
                'confirmationLedger': copy.deepcopy(subject.LEDGERS[which])}

    def semantic_failure(self, fragment, change, message):
        reader = ChangedDocuments(self.loader, fragment, change)
        with self.assertRaisesRegex(ValueError, message):
            subject._build(reader, lambda *args: None)
        self.assertTrue(reader.changed)

    def test_00_actual_51_members_and_original_pdf_pixels(self):
        for n, ledger in enumerate(self.ledgers):
            for i in range(len(ledger['confirmations'])):
                subject.verify(self.member(n, i), subject.SOURCE, subject.SOURCE_SHA, self.loader)
        self.assertEqual(len(subject._CACHE), 1)

    def test_ledger_hash_and_source_drift_rejected(self):
        entry = self.member()
        entry['confirmationLedger']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'unknown ledger'):
            subject.verify(entry, subject.SOURCE, subject.SOURCE_SHA, self.loader)
        with self.assertRaisesRegex(ValueError, 'unsupported source'):
            subject.verify(self.member(), 'phsa-2020-21', subject.SOURCE_SHA, self.loader)

    def test_supplied_member_extra_field_or_wrong_scope_rejected(self):
        for key, value in [('field', 'name'), ('physicalPage', 999), ('confirmedValue', 1913), ('unknown', True)]:
            entry = self.member()
            entry[key] = value
            with self.assertRaises(ValueError):
                subject.verify(entry, subject.SOURCE, subject.SOURCE_SHA, self.loader)

    def test_no_bool_zero_null_negative_or_string_amounts(self):
        for value in [True, False, 0, None, -1, '1,912', 1912.0]:
            entry = self.member()
            entry['confirmedValue'] = value
            with self.assertRaisesRegex(ValueError, 'strict positive integer'):
                subject.verify(entry, subject.SOURCE, subject.SOURCE_SHA, self.loader)

    def test_byte_pinning_independent_of_loader_claim(self):
        def bad_loader(ref, parse=True):
            return b'{}'
        with self.assertRaisesRegex(ValueError, 'byte hash differs'):
            subject.verify(self.member(), subject.SOURCE, subject.SOURCE_SHA, bad_loader)

    def test_complete_author_row_scope_not_just_peer_counts(self):
        self.semantic_failure('-original-transcript.json', lambda d: d['rows'].pop(), 'not 400')

    def test_complete_author_crop_and_requested_fields(self):
        self.semantic_failure('-original-transcript.json', lambda d: d['rows'][0].update(sourceCropSha256='0' * 64), 'crop differs')
        self.semantic_failure('-original-transcript.json', lambda d: d['rows'][0]['imageFirstValues'].pop('expenses'), 'fields missing')

    def test_complete_author_null_is_not_a_dash_or_imputed_value(self):
        self.semantic_failure('-original-transcript.json', lambda d: d['rows'][0]['imageFirstValues'].update(expenses=None), 'strict positive integer')

    def test_first_chronology_and_secondary_history_are_separate(self):
        self.semantic_failure('-original-transcript.json', lambda d: d.update(candidateOpenedBeforeFreeze=True), 'chronology')
        self.semantic_failure('-postcomparison-money-reread-transcript.json', lambda d: d['rows'][0].update(secondSourceReading=7984), 'secondary disagreements')

    def test_explicit_source_corrections_cannot_be_dropped_or_rewritten(self):
        self.semantic_failure('-postcomparison-money-source-corrections.json', lambda d: d['ownMonetaryDataCorrections'].pop(), 'declared correction history')
        self.semantic_failure('-postcomparison-money-source-corrections.json', lambda d: d['ownMonetaryDataCorrections'][0].update(initialBlindValue=99999), 'before/after differs')
        self.semantic_failure('-post-peer-own-additional-money-source-correction.json', lambda d: d.update(finalCurrentOriginalSourceValue=1988), 'overlay monetary value')

    def test_actual_peer_tuple_scope_and_literal_amount(self):
        self.semantic_failure('-four-money-source-first.json', lambda d: d['rows'].append(copy.deepcopy(d['rows'][0])), 'duplicate source field')
        self.semantic_failure('-fortyseven-money-image-first.json', lambda d: d['rows'][0].update(literalSourceAmount='7.983'), 'unsupported money separators')
        self.semantic_failure('-four-money-source-first.json', lambda d: d['rows'][0].update(literalSourceValue=1917), 'peer literal differs')

    def test_neither_overlay_nor_confirmation_flag_supplies_source_value(self):
        self.semantic_failure('manual-overlay-004.json', lambda d: d['overlays'][0]['resolvedRow'].__setitem__(4, 7984), 'overlay monetary value')
        self.semantic_failure('money-peer-confirmations-012.json', lambda d: d['confirmations'].pop(), 'confirmation count differs')

    def test_raw_peer_and_source_geometry_must_match(self):
        def corrupt(d):
            d['rows'][0]['nativeSourceField']['originalPdf300DpiPixelBox'][0] += 1
        self.semantic_failure('-remaining-forty-seven-money-peer-source-only.json', corrupt, 'native field differs')


if __name__ == '__main__':
    unittest.main()
