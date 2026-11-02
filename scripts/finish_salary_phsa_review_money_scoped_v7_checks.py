#!/usr/bin/env python3
"""Actual-schema and mutation checks for the independent 007/020 reader only."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import finish_salary_phsa_review_money_scoped_v7 as reader


ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/salaries/queue-completion-2026-11-01/phsa'


def actual(reference, parse=True):
    path = Path(reference['path'])
    if not path.is_absolute():
        path = ROOT / path
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == reference['sha256']
    return json.loads(data) if parse else data


def fixture(number):
    path = AREA / 'triangulation' / f'money-peer-confirmations-{number:03}.json'
    reference = {'path': str(path.relative_to(ROOT)),
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    document = actual(reference)
    return reference, document, {**document['confirmations'][0], 'confirmationLedger': reference}


class IndependentMoneyScoped(unittest.TestCase):
    def setUp(self):
        reader._CACHE.clear()

    def denied(self, number, change, reference=None):
        ledger_ref, ledger, member = fixture(number)
        if reference is None:
            reference = ledger['peerInputs'][0]
        def altered(ref, parse=True):
            value = actual(ref, parse)
            if parse:
                value = copy.deepcopy(value)
                if ref == reference:
                    change(value)
            return value
        reader._CACHE.clear()
        with self.assertRaises((ValueError, AssertionError, KeyError, TypeError, IndexError)):
            reader.verify(member, reader.SOURCE, reader.PDF_SHA, altered)

    def test_every_original_43_and_67_member(self):
        for number in (7, 20):
            reference, ledger, _ = fixture(number)
            for row in ledger['confirmations']:
                self.assertIsNone(reader.verify({**row, 'confirmationLedger': reference},
                                                reader.SOURCE, reader.PDF_SHA, actual))

    def test_unknown_hash_and_other_source_remain_held(self):
        _, _, member = fixture(7)
        for source, sha in [('phsa-2018-19', reader.PDF_SHA), (reader.SOURCE, '0' * 64)]:
            with self.assertRaises(ValueError):
                reader.verify(member, source, sha, actual)
        member['confirmationLedger']['sha256'] = '1' * 64
        with self.assertRaises(ValueError):
            reader.verify(member, reader.SOURCE, reader.PDF_SHA, actual)

    def test_each_cached_call_still_requires_the_exact_member(self):
        _, _, member = fixture(7)
        reader.verify(member, reader.SOURCE, reader.PDF_SHA, actual)
        member['confirmedValue'] += 1
        with self.assertRaises(ValueError):
            reader.verify(member, reader.SOURCE, reader.PDF_SHA, actual)

    def test_sparse_nonempty_events_preserve_repeated_sequence(self):
        data = b'sequence\tnameLiteral\tremunerationLiteral\texpensesLiteral\n1\tA,N\t\t\n1\t\t80,000\t\n1\t\t\t200\n1\t\t\t\n'
        self.assertEqual(reader._sparse_events(data),
                         {(1, 'name'): 'A,N', (1, 'remuneration'): '80,000', (1, 'expenses'): '200'})
        with self.assertRaises(ValueError):
            reader._sparse_events(data + b'1\t\t81,000\t\n')

    def test_007_source_scope_duplicates_and_missing_fields(self):
        _, ledger, _ = fixture(7)
        review = actual(ledger['peerInputs'][0])
        for operation in [lambda doc: doc['rows'].pop(),
                          lambda doc: doc['rows'].append(copy.deepcopy(doc['rows'][0])),
                          lambda doc: doc.update(sourceSha256='0' * 64)]:
            self.denied(7, operation, review['sourceOnlyPacket'])

    def test_007_blindness_freeze_and_first_value(self):
        _, ledger, _ = fixture(7)
        review = actual(ledger['peerInputs'][0])
        for operation in [lambda doc: doc.update(frozen=False),
                          lambda doc: doc.update(authorManualValuesAndCorrectionsUnopened=False),
                          lambda doc: doc['rows'][0].update(literalSourceValue=1)]:
            self.denied(7, operation, review['independentImageFirstTranscript'])

    def test_007_amendment_cannot_erase_wrong_first(self):
        _, ledger, _ = fixture(7)
        review = actual(ledger['peerInputs'][0])
        self.denied(7, lambda doc: doc['changes'][0].update(firstPeerSourceValue=75854),
                    review['peerOwnSourceRereadAmendments'])

    def test_007_pixel_proof_and_literal_author(self):
        _, ledger, _ = fixture(7)
        review = actual(ledger['peerInputs'][0])
        self.denied(7, lambda doc: doc['rows'][0].update(sourcePixelsIndependentlyReproducedExactly=False),
                    review['independentSourcePixelProof'])
        self.denied(7, lambda doc: doc['rows'][0].update(ownLiteralValue=True),
                    review['authorChoicesOpenedAfterPeerRawFreeze'])

    def test_020_raw_blindness_first_and_source_headers(self):
        _, ledger, _ = fixture(20)
        review = actual(ledger['peerInputs'][0])
        for operation in [lambda doc: doc.update(frozen=False),
                          lambda doc: doc.update(sourceId='phsa-2018-19'),
                          lambda doc: doc.update(supplementalAuthorChoicesOrOcrAlternativesOpenedBeforeFreeze=True),
                          lambda doc: doc['rows'][0].update(literalSourceValueFirstPass=1)]:
            self.denied(20, operation, review['originalPeerImageFirstTranscript'])

    def test_020_author_original_cannot_be_replaced_by_scoped_value(self):
        _, ledger, _ = fixture(20)
        overlay = actual(ledger['confirmations'][0]['effectiveAuthorOverlay'])
        author_review = actual(overlay['reviewInput'])
        reference = {'path': author_review['rawTranscriptPath'], 'sha256': author_review['rawTranscriptSha256']}
        def changed(doc):
            next(row for row in doc['rows'] if row['sequence'] == 11)['sourceImageReadings']['expenses'] = '1'
        self.denied(20, changed, reference)

    def test_020_complete_mixed88_coverage_and_pixel_proof(self):
        _, ledger, _ = fixture(20)
        review = actual(ledger['peerInputs'][0])
        self.denied(20, lambda doc: doc['rows'].pop(), review['sourceOnlyPacket'])
        self.denied(20, lambda doc: doc['rows'][0].update(actualOriginal1200PixelsIndependentlyReproducedExactly=False),
                    review['sourcePixelProof'])

    def test_020_third24_is_frozen_complete_and_keeps_money_first(self):
        _, ledger, _ = fixture(20)
        review = actual(ledger['peerInputs'][0])
        third = actual(review['freshThird24Adjudication'])
        self.denied(20, lambda doc: doc.update(frozen=False), third['ownIndependentSourceFirstBeforeChoices'])
        self.denied(20, lambda doc: doc['entries'].pop(), third['ownIndependentSourceFirstBeforeChoices'])
        def first(doc):
            next(row for row in doc['entries'] if row['field'] != 'name')['literalSourceValue'] += 1
        self.denied(20, first, third['ownIndependentSourceFirstBeforeChoices'])

    def test_020_changed_peer_money_without_adjudication_is_rejected(self):
        _, ledger, _ = fixture(20)
        review = actual(ledger['peerInputs'][0])
        self.denied(20, lambda doc: doc['changes'].append({
            'sequence': 11, 'physicalPage': 37, 'sourceRowOnPage': 7, 'field': 'expenses',
            'currentLiteralSourceReading': 1}), review['peerSourceRereadHistory'][-1])

    def test_hidden_correction_counts_and_duplicate_ledger_members(self):
        for number in (7, 20):
            reference, _, _ = fixture(number)
            self.denied(number, lambda doc: doc.update(originalPeerOwnSourceCorrections=0), reference)
            self.denied(number, lambda doc: doc['confirmations'].append(copy.deepcopy(doc['confirmations'][0])), reference)

    def test_consistent_forged_source_geometry_still_fails_original_pdf_pixels(self):
        _, ledger, member = fixture(20)
        review = actual(ledger['peerInputs'][0])
        packet = actual(review['sourceOnlyPacket'])
        image = packet['rows'][0]['actualOriginal1200Renders'][0]
        def alter_tree(value):
            if isinstance(value, dict):
                if value.get('sha256') == image['sha256'] and 'actualPdfPointClip' in value:
                    value['actualPdfPointClip'] = [x + 4 for x in value['actualPdfPointClip']]
                for child in value.values():
                    alter_tree(child)
            elif isinstance(value, list):
                for child in value:
                    alter_tree(child)
        def altered(reference, parse=True):
            value = actual(reference, parse)
            if parse:
                value = copy.deepcopy(value)
                alter_tree(value)
            return value
        with self.assertRaises(ValueError):
            reader.verify(member, reader.SOURCE, reader.PDF_SHA, altered)


if __name__ == '__main__':
    unittest.main()
