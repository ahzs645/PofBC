#!/usr/bin/env python3
"""Actual evidence/mutation checks for the independent four current money modes."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import finish_salary_phsa_review_money_current_v7 as subject

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/queue-completion-2026-11-01'
TRI = BASE / 'phsa/triangulation'

class Loader:
    def __init__(self):
        self.aliases = {}
        for path in TRI.glob('archived-source-money-views-*.json'):
            for row in json.loads(path.read_text())['rows']:
                a, b = row['originalReference'], row['archivedExactBytes']
                assert a['sha256'] == b['sha256']
                self.aliases[a['path'], a['sha256']] = b['path']
    def __call__(self, ref, parse=True):
        path = Path(ref['path'])
        if not path.is_absolute(): path = ROOT / path
        if not path.exists(): path = ROOT / self.aliases[ref['path'], ref['sha256']]
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == ref['sha256']
        return json.loads(data) if parse else data

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.load = Loader()
        cls.refs, cls.ledgers = {}, {}
        for mode in [22, 23, 25, 26, 27]:
            path = TRI / f"money-peer-confirmations-{mode:03d}{'-v2' if mode == 23 else ''}.json"
            ref = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            cls.refs[mode], cls.ledgers[mode] = ref, cls.load(ref)

    def semantic(self, mode, fragment, change):
        peer = copy.deepcopy(self.load(self.ledgers[mode]['peerInputs'][0]))
        changed = False
        def mutate(ref, parse=True):
            nonlocal changed
            doc = copy.deepcopy(self.load(ref, parse))
            if parse and fragment in ref['path']:
                change(doc); changed = True
            return doc
        with self.assertRaises((AssertionError, KeyError, ValueError, TypeError, FileNotFoundError)):
            getattr(subject, f'mode{mode}')(peer, mutate)
        self.assertTrue(changed)

    def test_all_192_exact_members_and_original_source_pixels(self):
        subject.CACHE.clear()
        for mode, ledger in self.ledgers.items():
            for row in ledger['confirmations']:
                subject.verify({**row, 'confirmationLedger': self.refs[mode]}, *subject.SOURCE, self.load)
        self.assertEqual(len(subject.CACHE), 5)

    def test_member_scope_and_money_type(self):
        for field, value in [('confirmedValue', True), ('confirmedValue', None), ('confirmedValue', 0),
                             ('confirmedValue', -1), ('confirmedValue', '5065'), ('field', 'name'), ('physicalPage', 999)]:
            row = {**self.ledgers[23]['confirmations'][0], 'confirmationLedger': self.refs[23], field: value}
            with self.assertRaises((AssertionError, KeyError, TypeError)):
                subject.verify(row, *subject.SOURCE, self.load)

    def test_wrong_source_and_unrecognized_old_pointer_ledger(self):
        row = {**self.ledgers[23]['confirmations'][0], 'confirmationLedger': self.refs[23]}
        with self.assertRaises(AssertionError): subject.verify(row, 'phsa-2020-21', subject.SOURCE[1], self.load)
        row['confirmationLedger'] = self.ledgers[23]['previousConfirmationLedger']
        with self.assertRaises(AssertionError): subject.verify(row, *subject.SOURCE, self.load)

    def test_loader_cannot_claim_unpinned_bytes(self):
        row = {**self.ledgers[22]['confirmations'][0], 'confirmationLedger': self.refs[22]}
        with self.assertRaises(AssertionError): subject.verify(row, *subject.SOURCE, lambda ref, parse=True: b'{}')

    def test_022_missing_scope(self):
        self.semantic(22, '-thirtyone-source-only-peer.json', lambda d: d['rows'].pop())
    def test_022_prior_choice_exposure(self):
        self.semantic(22, '-source-first.json', lambda d: d.update(correspondingAuthorChoicesOpened=True))
    def test_022_original_peer_amount(self):
        def change(d): next(r for r in d['rows'] if r['field'] != 'name')['literalPreferred'] += 1
        self.semantic(22, '-source-first.json', change)
    def test_022_author_original_source_identity(self):
        self.semantic(22, '-author-scoped-proposals.json', lambda d: d.update(sourceSha256='0'*64))
    def test_023_root_first_history(self):
        self.semantic(23, '-fiftythree-money-image-first.json', lambda d: d['rows'][0].update(rootFirstImageReading=1))
    def test_023_only_one_cold394(self):
        self.semantic(23, '-money394-source-first.json', lambda d: d['rows'].append(copy.deepcopy(d['rows'][0])))
    def test_023_no_hidden_author_original_change(self):
        self.semantic(23, '-original-transcript.json', lambda d: next(r for r in d['rows'] if (r['physicalPage'],r['sourceRowOnPage'])==(80,13))['sourceImageReadings'].update(expenses='1'))
    def test_023_other52_immutable(self):
        self.semantic(23, '-fiftythree-money-final-source-comparison.json', lambda d: d['rows'][0].update(authorCurrentSourceReading=1))
    def test_025_secondary264_restoration(self):
        self.semantic(25, '-expense264-additive-restoration.json', lambda d: d.update(rootFinalRestoredSourceReading=3988))
    def test_025_author_first_history(self):
        def change(d): next(r for r in d['rows'] if (r['physicalPage'],r['sourceRowOnPage'])==(97,20))['imageFirstValues']['expenses']=1
        self.semantic(25, '-original-transcript.json', change)
    def test_025_third_cannot_have_numeric_qualification(self):
        self.semantic(25, '-thirteen-money-final-comparison.json', lambda d: d['rows'][0].update(uncertainty='ambiguous digit'))
    def test_026_duplicate_first_tuple(self):
        self.semantic(26, '-thirtysix-money-source-first.json', lambda d: d['rows'].append(copy.deepcopy(d['rows'][0])))
    def test_026_author_first_history(self):
        self.semantic(26, '-original-transcript.json', lambda d: next(r for r in d['rows'] if (r['physicalPage'],r['sourceRowOnPage'])==(103,37))['imageFirstValues'].update(remuneration=1))
    def test_026_no_exposure_before_source_freeze(self):
        self.semantic(26, '-original-transcript.json', lambda d: d.update(candidateOpenedBeforeFreeze=True))

    def test_022_original_author_raw_pin_is_required(self):
        self.semantic(22, '-author-scoped-proposals.json', lambda d: d.update(originalRaw={'path': 'unrelated.json', 'sha256': '0'*64}))
    def test_022_final_money_cannot_be_same_value_float(self):
        peer=copy.deepcopy(self.load(self.ledgers[22]['peerInputs'][0]))
        row=next(r for r in peer['rows'] if r['field'] != 'name');row['literalSourceValue']=float(row['literalSourceValue'])
        with self.assertRaises(AssertionError): subject.mode22(peer,self.load)
    def test_025_third_final_must_be_frozen(self):
        self.semantic(25, '-thirteen-money-final-comparison.json', lambda d: d.update(frozen=False))
    def test_025_third235_first_error_must_remain(self):
        self.semantic(25, '-thirteen-money-source-first.json', lambda d: next(r for r in d['rows'] if r['sequence']==235).update(firstActual600VisualValue=1386))

class Early001NewCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.load = Loader()
        cls.peer = json.loads((BASE / 'reviews/root-phsa-history-2019-20-001-fiftyfive-money-final-source-comparison.json').read_text())
    def semantic(self, fragment, change):
        changed = False
        def load(ref, parse=True):
            nonlocal changed
            d = copy.deepcopy(self.load(ref, parse))
            if parse and fragment in ref['path']:
                change(d); changed = True
            return d
        with self.assertRaises((AssertionError, KeyError, ValueError, TypeError, FileNotFoundError)):
            subject.mode27(copy.deepcopy(self.peer), load)
        self.assertTrue(changed)
    def test_actual_all55_and_source110_pixels(self):
        facts, images, a, b = subject.mode27(copy.deepcopy(self.peer), self.load)
        self.assertEqual((len(facts), a, b), (55, 3, 1))
        subject.pixels(images, *subject.SOURCE, self.load)
    def test_root_first_chronology_cannot_be_backfilled(self):
        self.semantic('-fiftyfive-money-source-first.json', lambda d: d.update(authorOrCandidateChoicesOpenedAtFreeze=True))
    def test_current_reread_must_precede_root_values(self):
        self.semantic('-current-source-reread-before-root-choices.json', lambda d: d.update(rootCorrespondingFreshFiftyFiveChoicesOpened=True))
    def test_sparse_duplicate_nonempty_event_rejected(self):
        old_load = self.load
        def load(ref, parse=True):
            value = old_load(ref, parse)
            if ref['path'].endswith('-001-image-transcript.tsv'):
                return value + value.splitlines(keepends=True)[1]
            return value
        with self.assertRaises(AssertionError): subject.mode27(copy.deepcopy(self.peer), load)
    def test_original400_scope_not_shrunk_to_current55(self):
        self.semantic('-001-images.json', lambda d: d['rows'].pop())
    def test_new_author_numeric_uncertainty_not_qualified(self):
        self.semantic('-current-source-reread-before-root-choices.json', lambda d: d['rows'][0].update(sourceUncertainty='0/6'))
    def test_three_old_corrections_are_exact(self):
        peer = copy.deepcopy(self.peer);peer['oldSelectedSourceValueCorrections'].pop()
        with self.assertRaises(AssertionError): subject.mode27(peer, self.load)
    def test_root392_first_error_cannot_be_erased(self):
        peer=copy.deepcopy(self.peer)
        next(r for r in peer['rows'] if r['sequence']==392)['rootFirstLiteralImageValue']=1014
        with self.assertRaises(AssertionError): subject.mode27(peer, self.load)

    def test_027_three_correction_summary_before_after_and_sequence(self):
        for name in ['sequence','oldValue','currentLiteralValue']:
            peer=copy.deepcopy(self.peer);peer['oldSelectedSourceValueCorrections'][0][name]=1
            with self.assertRaises(AssertionError): subject.mode27(peer,self.load)
    def test_027_root_first_literal_cannot_be_float(self):
        self.semantic('-fiftyfive-money-source-first.json',lambda d: d['rows'][0].update(literalImageValue=float(d['rows'][0]['literalImageValue'])))

if __name__ == '__main__': unittest.main()
