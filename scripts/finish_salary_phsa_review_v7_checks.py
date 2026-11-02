#!/usr/bin/env python3
"""Independent replay mutation checks; imports only the independent v7 reader."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('phsa_independent_v7', Path(__file__).with_name('finish_salary_phsa_review_final_replay_v7.py'))
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)
SOURCE = 'phsa-2015-16'
SHA = '1' * 64


def reference(path):
    return {'path': path, 'sha256': '2' * 64}


def fixture():
    prefix = 'research/salaries/queue-completion-2026-11-01/'
    paths = {k: prefix + 'phsa/canonical-review/' + SOURCE + '-' + k + '-source-only.json'
             for k in ['qualified-name', 'direct-neither-name', 'positive-neither-money']}
    packets = []
    documents = {}
    rows = {'qualified-name': [{'physicalPage': 2, 'sourceRowOnPage': 1}],
            'direct-neither-name': [{'physicalPage': 2, 'sourceRowOnPage': 2}],
            'positive-neither-money': [{'physicalPage': 2, 'sourceRowOnPage': 2, 'field': 'remuneration'}]}
    for kind, path in paths.items():
        packets.append(reference(path))
        documents[path] = {'sourceId': SOURCE, 'sourceSha256': SHA, 'sourceOnly': True,
                           'rowCount': len(rows[kind]), 'rows': rows[kind]}
    human_path = prefix + 'reviews/independent-phsa-history-v7-test-semantic-fixture.json'
    human = {'sourceId': SOURCE, 'sourceSha256': SHA, 'rows': [
        {'physicalPage': 2, 'sourceRowOnPage': 1, 'field': 'name', 'literalCurrent': 'A,Iana',
         'fullFamily': ['A,Iana', 'A,lana']},
        {'physicalPage': 2, 'sourceRowOnPage': 2, 'field': 'name', 'literalCurrent': 'B,Bea',
         'fullFamily': ['B,Bea']},
        {'physicalPage': 2, 'sourceRowOnPage': 2, 'field': 'remuneration', 'literalCurrent': 75500}]}
    documents[human_path] = human
    outcomes = []
    for i, row in enumerate(human['rows']):
        outcome = {k: row[k] for k in ['physicalPage', 'sourceRowOnPage', 'field']}
        outcome.update(value=row['literalCurrent'], status='qualified' if i == 0 else 'direct',
                       decisionRecord={'receipt': reference(human_path), 'rowRecordPointer': '/rows/' + str(i),
                                       'valueField': 'literalCurrent', 'finiteField': 'fullFamily' if i < 2 else None})
        if i < 2:
            outcome['visibleAlternatives'] = row['fullFamily'][:]
        outcomes.append(outcome)
    closure_path = prefix + 'reviews/root-phsa-history-v7-test-closure.json'
    closure = {'schema': 'phsa-canonical-source-closure-v1', 'sourceId': SOURCE, 'sourceSha256': SHA,
               'accepted': True, 'closed': True, 'unresolved': [], 'scopeKind': 'prior-eight-three-packets',
               'targetPackets': packets, 'humanReviewReceipts': [reference(human_path)], 'outcomes': outcomes,
               'counts': {'targets': 3, 'nameTargets': 2, 'positiveMoneyTargets': 1, 'qualifiedNameTargets': 1}}
    documents[closure_path] = closure
    source = {'sourceId': SOURCE, 'sourceSha256': SHA, 'completePhysicalSource': True, 'pendingFields': [],
              'rows': [
                  {'row': ['provincial-health-services-authority', 'A,Iana', None, 90000, None, 2],
                   'sourceRowOnPage': 1, 'fields': {'name': {'status': 'manual-qualified-source-typography',
                   'evidence': {'nameTypographyQualification': {'chosenName': 'A,Iana',
                    'visibleAlternatives': ['A,Iana', 'A,lana'], 'caseProvenByPixels': False}}}}},
                  {'row': ['provincial-health-services-authority', 'B,Bea', None, 75500, None, 2],
                   'sourceRowOnPage': 2, 'fields': {'name': {'status': 'manual-original-image', 'evidence': {}}}}]}
    return reference(closure_path), source, documents, paths, human_path


class CanonicalMutations(unittest.TestCase):
    def setUp(self):
        self.ref, self.source, self.docs, self.paths, self.human = fixture()
        self.closure = self.docs[self.ref['path']]

    def check(self):
        return REPLAY.independent_canonical_source(self.ref, SOURCE, SHA, self.source,
                                                  load=lambda ref: self.docs[ref['path']])

    def denied(self):
        with self.assertRaises((AssertionError, KeyError, ValueError, IndexError)):
            self.check()

    def test_positive_complete_semantic_binding(self):
        self.assertEqual(self.check()['targets'], 3)

    def test_missing_outcome_even_with_matching_counts(self):
        self.closure['outcomes'].pop()
        self.closure['counts']['targets'] -= 1
        self.closure['counts']['positiveMoneyTargets'] -= 1
        self.denied()

    def test_scalar_differs_from_human_even_when_payload_changed(self):
        self.source['rows'][1]['row'][3] = 75501
        self.closure['outcomes'][2]['value'] = 75501
        self.denied()

    def test_boolean_is_not_money(self):
        self.source['rows'][1]['row'][3] = True
        self.closure['outcomes'][2]['value'] = True
        self.docs[self.human]['rows'][2]['literalCurrent'] = True
        self.denied()

    def test_human_pointer_cannot_borrow_another_name(self):
        self.closure['outcomes'][0]['decisionRecord']['rowRecordPointer'] = '/rows/1'
        self.denied()

    def test_full_finite_set_must_match_human(self):
        self.source['rows'][0]['fields']['name']['evidence']['nameTypographyQualification']['visibleAlternatives'].append('A,IIana')
        self.closure['outcomes'][0]['visibleAlternatives'].append('A,IIana')
        self.denied()

    def test_qualified_cannot_become_direct_by_dropping_alternatives(self):
        row = self.closure['outcomes'][0]
        row['status'] = 'direct'
        row['visibleAlternatives'] = [row['value']]
        self.denied()

    def test_money_cannot_have_finite_glyph_qualification(self):
        self.closure['outcomes'][2]['visibleAlternatives'] = ['75500', '75501']
        self.denied()

    def test_overlapping_packets_cannot_shrink_claimed_coverage(self):
        self.docs[self.paths['direct-neither-name']]['rows'] = [{'physicalPage': 2, 'sourceRowOnPage': 1}]
        self.closure['outcomes'].pop(1)
        self.closure['counts']['targets'] -= 1
        self.closure['counts']['nameTargets'] -= 1
        self.denied()

    def test_all_three_original_scope_packets_required(self):
        self.closure['targetPackets'].pop()
        self.denied()

    def test_original_source_header_cannot_change(self):
        self.docs[self.human]['sourceSha256'] = '3' * 64
        self.denied()

    def test_explicit_human_unresolved_blocks_closure(self):
        self.docs[self.human]['unresolvedFields'] = 1
        self.denied()

    def test_irrelevant_human_receipt_is_not_coverage(self):
        new = reference('research/salaries/irrelevant-human.json')
        self.closure['humanReviewReceipts'].append(new)
        self.docs[new['path']] = {'sourceId': SOURCE, 'sourceSha256': SHA}
        self.denied()

    def test_qualified_target_cannot_disappear_with_consistent_counts(self):
        self.docs[self.paths['qualified-name']]['rows'] = []
        self.docs[self.paths['qualified-name']]['rowCount'] = 0
        self.closure['outcomes'].pop(0)
        self.closure['counts'].update(targets=2, nameTargets=1, qualifiedNameTargets=0)
        self.denied()

    def test_invalid_json_pointer_escape(self):
        self.closure['outcomes'][0]['decisionRecord']['rowRecordPointer'] = '/rows/~2'
        self.denied()

    def test_external_parsed_reference_rejected(self):
        self.closure['targetPackets'][0] = reference('/tmp/unpinned.json')
        self.denied()

    def test_duplicate_full_alternative_rejected(self):
        self.closure['outcomes'][0]['visibleAlternatives'].append('A,Iana')
        self.denied()

    def test_pending_boolean_cannot_claim_zero(self):
        self.source['pendingFields'] = False
        self.denied()

    def test_pending_integer_cannot_replace_actual_empty_list(self):
        self.source['pendingFields'] = 0
        self.denied()

    def test_current_neither_reader_name_cannot_leave_canonical_scope(self):
        self.docs[self.paths['direct-neither-name']]['rows'] = []
        self.docs[self.paths['direct-neither-name']]['rowCount'] = 0
        self.closure['outcomes'].pop(1)
        self.closure['counts'].update(targets=2, nameTargets=1)
        staged = {(2, 1): {'tesseract': {'name': 'A,Iana'}, 'rapidocr': {'name': 'A,Iana'}},
                  (2, 2): {'tesseract': {'name': 'B,Bye'}, 'rapidocr': {'name': 'B,Bye'}}}
        with self.assertRaises(AssertionError):
            REPLAY.independent_canonical_source(self.ref, SOURCE, SHA, self.source,
                                               load=lambda ref: self.docs[ref['path']], staged=staged)


class RebaseMutations(unittest.TestCase):
    """Real frozen eight-field proof; mutations never touch its actual files."""
    def setUp(self):
        path = REPLAY.AREA / 'phsa/triangulation/confirmation-supersessions/money-peer-confirmations-014-v2.json'
        self.selector_ref = REPLAY.pin(path)
        selector = REPLAY.pinned(self.selector_ref)
        self.ref = selector['effectiveConfirmation']
        self.doc = copy.deepcopy(REPLAY.pinned(self.ref))
        self.actual_loader = REPLAY.pinned

    def denied(self):
        confirmation = {**self.doc['confirmations'][0], 'confirmationLedger': self.ref,
                        'confirmationSupersession': self.selector_ref}
        def mutated_loader(ref, parse=True):
            if ref == self.ref:
                assert parse
                return self.doc
            return self.actual_loader(ref, parse)
        with patch.object(REPLAY, 'pinned', side_effect=mutated_loader):
            with self.assertRaises((AssertionError, KeyError, ValueError, IndexError)):
                REPLAY.independent_current_money_peer(confirmation, confirmation['sourceId'], confirmation['sourceSha256'])

    def test_rebase_cannot_change_confirmed_amount(self):
        self.doc['confirmations'][0]['confirmedValue'] += 1
        self.denied()

    def test_rebase_cannot_drop_unrelated_confirmation(self):
        self.doc['confirmations'].pop()
        self.denied()

    def test_rebase_cannot_change_source_image(self):
        self.doc['confirmations'][0]['freshSourceImage']['sha256'] = 'f' * 64
        self.denied()

    def test_rebase_cannot_rebind_an_unrelated_row(self):
        self.doc['confirmations'][-1]['effectiveAuthorOverlay'] = self.doc['confirmations'][0]['effectiveAuthorOverlay']
        self.denied()

    def test_rebase_cannot_change_derived_rebound_count(self):
        self.doc['unchangedFreshMoneyFieldsRebound'] += 1
        self.denied()

    def test_rebase_cannot_drop_original_input_history(self):
        self.doc['peerInputs'].pop(0)
        self.denied()

    def test_rebase_cannot_claim_name_field_authority(self):
        self.doc['confirmations'][0]['field'] = 'name'
        self.denied()


class MetadataMutations(unittest.TestCase):
    def setUp(self):
        self.source = 'phsa-2021-22'
        self.metadata = REPLAY.read(REPLAY.AREA / 'phsa/candidates/phsa-2021-22-source-v4.json')
        inventory = REPLAY.read(REPLAY.AREA / 'phsa/source-inventory.json')
        self.inventory = next(r for r in inventory['sources'] if r['id'] == self.source)

    def test_actual_selected_metadata_matches_original_period_and_scope(self):
        REPLAY.independent_metadata_identity(self.metadata, self.inventory, self.source)

    def denied(self):
        with self.assertRaises((AssertionError, KeyError, ValueError)):
            REPLAY.independent_metadata_identity(self.metadata, self.inventory, self.source)

    def test_consistently_changed_year_and_period_rejected(self):
        self.metadata.update(year='2020/21', periodStart='2020-04-01', periodEnd='2021-03-31')
        self.denied()

    def test_another_original_url_rejected(self):
        self.metadata['sourceUrl'] = 'https://example.invalid/another-source.pdf'
        self.denied()

    def test_employer_scope_rejected(self):
        self.metadata['employerSlug'] = 'another-health-authority'
        self.denied()

    def test_compiled_status_cannot_replace_official_original(self):
        self.metadata['sourceKind'] = 'compiled'
        self.denied()

    def test_compiled_history_retention_cannot_be_removed(self):
        self.metadata['retainCompiledPartition'] = False
        self.denied()

    def test_threshold_comparison_cannot_drift(self):
        self.metadata['thresholdComparison'] = '>='
        self.denied()


class ExhaustiveMoneyMutations(unittest.TestCase):
    def setUp(self):
        self.ref = REPLAY.pin(REPLAY.AREA / 'phsa/triangulation/money-peer-confirmations-024.json')
        self.doc = copy.deepcopy(REPLAY.pinned(self.ref))
        self.actual_loader = REPLAY.pinned
        REPLAY._EXHAUSTIVE_016_CACHE.clear()

    def denied(self):
        confirmation = {**self.doc['confirmations'][0], 'confirmationLedger': self.ref}
        def mutated_loader(ref, parse=True):
            if ref == self.ref:
                assert parse
                return self.doc
            return self.actual_loader(ref, parse)
        with patch.object(REPLAY, 'pinned', side_effect=mutated_loader):
            with self.assertRaises(AssertionError):
                REPLAY.independent_exhaustive_016(confirmation, confirmation['sourceId'], confirmation['sourceSha256'])

    def test_wrong_positive_amount(self):
        self.doc['confirmations'][0]['confirmedValue'] += 1
        self.denied()

    def test_missing_positive_field(self):
        self.doc['confirmations'].pop()
        self.denied()

    def test_duplicate_positive_field(self):
        self.doc['confirmations'][1] = copy.deepcopy(self.doc['confirmations'][0])
        self.denied()

    def test_author_raw_cannot_be_relabelled_independent(self):
        self.doc['independentPeerImageFirstTranscripts'][0] = self.doc['authorImageFirstTranscript']
        self.denied()

    def test_a_peer_cannot_be_relabelled_author_complete_raw(self):
        self.doc['authorImageFirstTranscript'] = self.doc['independentPeerImageFirstTranscripts'][0]
        self.denied()

    def test_per_field_independent_peer_scope_cannot_change(self):
        self.doc['confirmations'][0]['independentSourcePeer'] = self.doc['confirmations'][-1]['independentSourcePeer']
        self.denied()

    def test_printed_null_cannot_become_numeric_zero(self):
        self.doc['literalSourceDashFieldsConfirmedSeparately'][0]['value'] = 0
        self.denied()

    def test_actual_source_view_cannot_change(self):
        self.doc['confirmations'][0]['freshSourceImage']['sha256'] = '0' * 64
        self.denied()


class PreservedMixedSourceProofs(unittest.TestCase):
    def setUp(self):
        self.current = copy.deepcopy(REPLAY.read(REPLAY.AREA / 'phsa/triangulation/money-peer-confirmations-001-v6.json'))
        self.previous_ref = self.current['previousConfirmationLedger']
        self.previous = REPLAY.pinned(self.previous_ref)
        selector = REPLAY.pinned(self.current['ordinaryOverlaySupersession'])
        self.old_overlay = selector['supersededOverlay']

    def check(self):
        return REPLAY.independent_preserved_money_records(self.previous, self.previous_ref, self.old_overlay, self.current)
    def denied(self):
        with self.assertRaises((AssertionError, KeyError, ValueError)): self.check()
    def test_actual_mixed_source_pointer_preservation(self):
        self.assertTrue(self.check())
    def test_missing_unrelated_pointer_rejected(self):
        self.current['preservedUnchangedFieldProvenance'].pop(); self.denied()
    def test_duplicate_unrelated_pointer_rejected(self):
        self.current['preservedUnchangedFieldProvenance'].append(copy.deepcopy(self.current['preservedUnchangedFieldProvenance'][0])); self.denied()
    def test_later_ledger_cannot_replace_unrelated_previous(self):
        self.current['preservedUnchangedFieldProvenance'][0]['confirmationLedger'] = reference('research/other.json'); self.denied()
    def test_changed_unrelated_source_amount_rejected(self):
        item = self.current['preservedUnchangedFieldProvenance'][0]
        target = next(r for r in self.current['confirmations'] if all(r[k] == item[k] for k in ['sourceId','physicalPage','sourceRowOnPage','field']))
        target['confirmedValue'] += 1; self.denied()
    def test_supersession_to_different_previous_ledger_rejected(self):
        self.current['preservedUnchangedFieldProvenance'][0]['confirmationSupersession'] = self.current['ordinaryOverlaySupersession']; self.denied()


class ExactRetirementMutations(unittest.TestCase):
    def setUp(self):
        self.path = REPLAY.AREA / 'phsa/adoption-supersessions/phsa-2019-20-011-root-adoption-canonical-retired.json'
        self.ref = REPLAY.pin(self.path)
        self.selector = copy.deepcopy(REPLAY.pinned(self.ref))
        self.changed = {}
    def load(self, ref):
        return self.changed.get(ref['path'], self.selector if ref == self.ref else REPLAY.pinned(ref))
    def check(self):
        return REPLAY.independent_adoption_selection(self.ref, self.selector['sourceId'], self.selector['sourceSha256'], self.load)
    def edit(self, ref):
        self.changed[ref['path']] = copy.deepcopy(REPLAY.pinned(ref)); return self.changed[ref['path']]
    def denied(self):
        with self.assertRaises((AssertionError, KeyError, ValueError)): self.check()
    def test_actual_two_exact_current_source_retirements(self): self.check()
    def test_unlisted_deleted_case_rejected(self):
        ledger = self.edit(self.selector['effectiveCaseLedger']); ledger['qualifications'].pop(); self.denied()
    def test_undeclared_retirement_rejected(self):
        self.selector['authorizedRetiredNameCases'].pop(); self.denied()
    def test_root_must_adopt_exact_retirement(self):
        adoption = self.edit(self.selector['effectiveRootAdoption']); adoption['acceptedCaseRetirements'] = []; self.denied()
    def test_retirement_name_only_scope(self):
        self.selector['authorizedRetiredNameCases'][0]['allowedFields'] = ['name', 'expenses']; self.denied()
    def test_wrong_original_case_crop_rejected(self):
        self.selector['authorizedRetiredNameCases'][0]['originalFullRowCropSha256'] = '0'*64; self.denied()
    def test_human_direct_literal_cannot_differ(self):
        case = self.selector['authorizedRetiredNameCases'][0]
        doc = self.edit(case['independentSourcePeer'])
        row = next(r for r in doc['rows'] if (r['physicalPage'],r['sourceRowOnPage']) == (case['physicalPage'],case['sourceRowOnPage']))
        row['educationFirstAndCurrentLiteral'] = 'Wrong,Name'; self.denied()
    def test_other_case_dictionary_cannot_change(self):
        doc = self.edit(self.selector['effectiveCaseLedger']); doc['qualifications'][0]['assumptionBasis'] = 'unapproved change'; self.denied()


class MixedRootScopes(unittest.TestCase):
    def setUp(self):
        self.a = {'physicalPage': 1, 'sourceRowOnPage': 1, 'proposedName': 'One,Name', 'visibleAlternatives': ['One,Name','One,Narne'], 'cropSha256': '1'*64}
        self.b = {'physicalPage': 1, 'sourceRowOnPage': 2, 'proposedName': 'Two,Name', 'visibleAlternatives': ['Two,Name','Two,Narne'], 'cropSha256': '2'*64}
        self.doc = {'cases': [self.a], 'sourceNameSegmentationExceptions': [self.b]}
    def test_generic_root_does_not_adopt_separate_closed_category(self):
        root = {'sourceId': SOURCE, 'cases': [self.a]}
        self.assertEqual(REPLAY.independent_scoped_adoption_cases(root,self.doc),[self.a])
    def test_explicit_closed_only_root_scope(self):
        self.assertEqual(REPLAY.independent_scoped_adoption_cases({'exactCases':[self.b]},self.doc),[self.b])
    def test_explicit_mixed_scope_contains_both_categories(self):
        self.assertEqual(REPLAY.independent_scoped_adoption_cases({'cases':[self.a],'closedCases':[self.b]},self.doc),[self.a,self.b])
    def test_unmatched_closed_root_crop_rejected(self):
        wrong=copy.deepcopy(self.b);wrong['cropSha256']='3'*64
        with self.assertRaises(AssertionError):REPLAY.independent_scoped_adoption_cases({'exactCases':[wrong]},self.doc)
    def test_identical_source_case_alias_is_not_an_extra_case(self):
        self.doc['sourceNameSegmentationExceptions']=[copy.deepcopy(self.a)]
        self.assertEqual(REPLAY.independent_scoped_adoption_cases({},self.doc),[self.a])

if __name__ == '__main__':
    unittest.main()
