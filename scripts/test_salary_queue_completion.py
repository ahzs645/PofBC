"""Regression checks for whole-cohort replacement and original-queue completion."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from finish_salary_queue_overlap import compare
from finish_salary_queue_release_inputs import release_manifest
import finish_salary_phsa_promote as phsa_promote

SPEC = importlib.util.spec_from_file_location('queue_review', Path(__file__).with_name('review-salary-queue-completion.py'))
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class CanonicalPhsaPromotionTests(unittest.TestCase):
    def setUp(self):
        self.source = 'phsa-2021-22'
        self.reference = {'path': 'canonical-review.json', 'sha256': 'a' * 64}
        self.accepted = {'candidateRevision': 4,
            'finalCandidate': {'path': str((phsa_promote.ledger.AREA / 'candidates' /
                f'{self.source}-source-v4.json').relative_to(phsa_promote.ledger.ROOT))},
            'canonicalSourceViewReviewReceipts': [self.reference],
            'canonicalQualifiedNameCount': 0,
            'canonicalNameCorrections': [{'physicalPage': 119, 'sourceRowOnPage': 31,
                'value': 'Mundi,Jacqueline', 'requiresDirectLiteral': True,
                'evidence': self.reference}]}
        self.original = {'rootAdoptedQualifiedNameCases': [], 'rows': [{
            'row': ['phsa', 'Mundi,Jacqueline', None, 80000, None, 119],
            'sourceRowOnPage': 31,
            'fields': {'name': {'status': 'manual-original-image'}}}]}

    def test_revision_selection_never_silently_falls_back_to_an_older_candidate(self):
        phsa_promote.selected_candidate_path(self.source, self.accepted)
        for revision in [3, True, '4', None, 5]:
            changed = copy.deepcopy(self.accepted)
            changed['candidateRevision'] = revision
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                phsa_promote.selected_candidate_path(self.source, changed)

    def test_missing_or_wrong_original_canonical_review_cannot_promote(self):
        changed = copy.deepcopy(self.accepted)
        changed['canonicalSourceViewReviewReceipts'] = []
        with self.assertRaises(ValueError):
            phsa_promote.verify_canonical_source_review(self.source, 'pdf-sha', changed, self.original)
        with patch.object(phsa_promote.ledger, 'pinned', return_value={'sourceId': 'another-source'}):
            with self.assertRaises(ValueError):
                phsa_promote.verify_canonical_source_review(self.source, 'pdf-sha', self.accepted, self.original)

    def test_old_name_or_qualification_cannot_survive_a_clear_source_correction(self):
        # The canonical module separately tests exact human-decision records and
        # full target coverage. Here the post-audit correction guard must still
        # reject an old literal or waiver even after a successful canonical call.
        with patch.object(phsa_promote.canonical, 'validate', return_value={}) as canonical_check, \
                patch.object(phsa_promote.ledger, 'pinned', return_value={'sourceId': self.source}):
            phsa_promote.verify_canonical_source_review(self.source, 'pdf-sha', self.accepted, self.original)
            canonical_check.assert_called_once_with(self.reference, self.source, 'pdf-sha', self.original)
            for wrong in ['old-name', 'old-qualification']:
                original = copy.deepcopy(self.original)
                if wrong == 'old-name':
                    original['rows'][0]['row'][1] = 'Mundl,Jacqueline'
                else:
                    original['rows'][0]['fields']['name']['status'] = 'manual-qualified-source-typography'
                with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                    phsa_promote.verify_canonical_source_review(self.source, 'pdf-sha', self.accepted, original)


class CompleteCompiledCopyTests(unittest.TestCase):
    def test_compilation_punctuation_does_not_change_literal_accepted_rows(self):
        official = [['employer', 'Smith-Jones, Élise', None, 75000.25, None, 7]]
        compiled = [['SMITHJONES, ÉLISE', None, 75000.25, 0, 2]]
        self.assertTrue(compare(official, compiled)['completeMultisetMatch'])
        self.assertIsNone(official[0][4])
        self.assertEqual(official[0][1], 'Smith-Jones, Élise')

    def test_letter_changes_and_partial_overlap_never_prove_a_complete_copy(self):
        official = [['employer', 'Smith, Élise', None, 75000, 10, 7]]
        for compiled in [[['Smith, Elise', None, 75000, 10, 2]],
                         [['Smith, Élise', None, 75000, 10, 2], ['Executive, J', None, 150000, 0, 2]],
                         [['Smith, Élise', None, 75000.01, 10, 2]]]:
            with self.subTest(compiled=compiled):
                self.assertFalse(compare(official, compiled)['completeMultisetMatch'])

    def test_repeated_observations_cannot_be_collapsed_for_a_match(self):
        row = ['employer', 'Smith, J', None, 75000, 0, 7]
        self.assertFalse(compare([row, row], [['Smith, J', None, 75000, 0, 2]])['completeMultisetMatch'])

    def test_job_title_scope_cannot_be_erased_to_prove_a_copy(self):
        with self.assertRaises(AssertionError):
            compare([['employer', 'Smith, J', 'President', 75000, 0, 7]],
                    [['Smith, J', None, 75000, 0, 2]])

    def test_fractional_cent_or_nonfinite_money_cannot_prove_a_match(self):
        for amount in [75000.251, float('inf'), float('nan'), True]:
            with self.subTest(amount=amount), self.assertRaises(AssertionError):
                compare([['employer', 'Smith, J', None, amount, 0, 7]],
                        [['Smith, J', None, 75000.25, 0, 2]])


class QueueBaselinePreservationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [['Smith, J', None, 75000.25, None, 7]]
        self.key = ('employer', '2023/24', 'pssdb-2026-10-22')
        self.before = {'rows': 1, 'groups': [{'employerSlug': self.key[0], 'year': self.key[1],
            'sourceId': self.key[2], 'sourceKind': 'compiled', 'rows': 1,
            'rowMultisetSha256': REVIEW.fingerprint(self.rows)}]}
        self.rule = {'employerSlug': self.key[0], 'compiledYear': self.key[1],
                     'expectedRows': 1, 'expectedRetainedRows': 0}

    def test_only_the_exact_reviewed_whole_compiled_group_can_disappear(self):
        self.assertEqual(REVIEW.verify_baseline(self.before, {}, [self.rule]), (0, 1))
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {}, [])
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {self.key: self.rows}, [self.rule])

    def test_official_rows_are_never_removed_by_a_compiled_rule(self):
        before = copy.deepcopy(self.before)
        before['groups'][0]['sourceKind'] = 'official'
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(before, {}, [self.rule])

    def test_retained_null_money_page_and_multiplicity_must_stay_exact(self):
        for field, value in [(0, 'Smith, John'), (2, 75000.26), (3, 0), (4, 8)]:
            changed = copy.deepcopy(self.rows)
            changed[0][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                REVIEW.verify_baseline(self.before, {self.key: changed}, [])
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {self.key: self.rows * 2}, [])
        changed = copy.deepcopy(self.rows)
        changed[0][2] += 0.001
        with self.assertRaises(AssertionError):
            REVIEW.verify_baseline(self.before, {self.key: changed}, [])

    def test_public_processing_cannot_be_called_complete_with_an_unfinished_item(self):
        original = {'tasks': [{'id': str(n)} for n in range(9)]}
        dispositions = {'originalQueueEntries': [{'id': str(n),
            'disposition': 'completed' if n < 5 else 'issuer-dependent',
            'reason': 'Exact original source reviewed.' if n < 5 else 'Exact issuer clarification still needed.',
            'evidence': ['pinned-receipt.json']} for n in range(9)], 'remainingPublicProcessingTasks': []}
        done, external = REVIEW.verify_original_dispositions(dispositions, original)
        self.assertEqual((len(done), len(external)), (5, 4))
        dispositions['remainingPublicProcessingTasks'] = ['one historical report unfinished']
        with self.assertRaises(AssertionError):
            REVIEW.verify_original_dispositions(dispositions, original)


class ReleasedRetentionDescriptionTests(unittest.TestCase):
    def test_replacement_corrects_only_descriptions_and_keeps_frozen_data_unchanged(self):
        import json
        path = REVIEW.RESEARCH / 'queue-completion-acquisition/sources.json'
        raw = path.read_bytes()
        original = json.loads(raw)
        released, amendments = release_manifest(original)
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(len(amendments), 4)
        for before, after in zip(original['sources'], released['sources']):
            restored = copy.deepcopy(after)
            restored['file'] = restored['file'].removeprefix('../queue-completion-acquisition/')
            if before['employerSlug'] == 'providence-health-care':
                self.assertNotIn('coexists with retained compiled observations', after['publicWarning'])
                self.assertIn('3,289-row compiled employee copy', after['publicWarning'])
                restored['publicWarning'] = before['publicWarning']
                restored['validation']['compiledPartitionRetentionReason'] = before['validation']['compiledPartitionRetentionReason']
            self.assertEqual(restored, before)


class WholeScopeAndOutboxTests(unittest.TestCase):
    def test_nine_partial_or_wrong_employer_years_cannot_finish_the_health_queue(self):
        sources = [{'year': f'{year}/{str(year + 1)[-2:]}',
            'employerSlug': 'provincial-health-services-authority', 'category': 'employee-remuneration',
            'completeEmployeeSchedule': True, 'validation': {'completeEmployeeSchedule': True}}
            for year in range(2015, 2024)]
        REVIEW.verify_historical_phsa(sources)
        for field, value in [('category', 'aggregate-only'), ('employerSlug', 'other-health-authority'),
                             ('completeEmployeeSchedule', False)]:
            changed = copy.deepcopy(sources)
            changed[4][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                REVIEW.verify_historical_phsa(changed)
        with self.assertRaises(AssertionError):
            REVIEW.verify_historical_phsa(sources[:-1])

    def test_unsent_claim_requires_all_four_exact_issues_and_zero_actual_contacts(self):
        import json
        outbox = json.loads((REVIEW.OUT / 'acquisition/outbox/outbox.json').read_text())
        ids = {'held-resolution-nic-2019-20-complete-copy-request',
               'held-resolution-municipal-mcbride-request-period-copy',
               'held-resolution-schools-sd10-2025-approval-clarification',
               'held-resolution-schools-sd08-2026-issuer-clarification'}
        tasks = [t for t in json.loads((REVIEW.OUT / 'acquisition/work-queue.json').read_text()) if t['id'] in ids]
        REVIEW.verify_outbox(outbox, tasks)
        for key in ['contactsSent', 'formsSubmitted', 'formalFoiApplicationsSubmitted', 'feesAuthorizedOrPaid']:
            changed = copy.deepcopy(outbox)
            changed[key] = 1
            with self.subTest(key=key), self.assertRaises(AssertionError):
                REVIEW.verify_outbox(changed, tasks)
        changed = copy.deepcopy(outbox)
        changed['items'][0]['sent'] = True
        with self.assertRaises(AssertionError):
            REVIEW.verify_outbox(changed, tasks)
        changed = copy.deepcopy(outbox)
        changed['items'][0]['linkedTaskIds'] = ['a different archive issue']
        with self.assertRaises(AssertionError):
            REVIEW.verify_outbox(changed, tasks)


class HistoricalPhsaFieldClosureTests(unittest.TestCase):
    def setUp(self):
        self.rows = [['provincial-health-services-authority', 'Source, Name', None, 80000, None, 1]]
        counts = {'name': {'baseline-independent-reader-agreement': 1},
                  'remuneration': {'baseline-independent-reader-agreement': 1},
                  'expenses': {'original-source-explicit-dash-geometry': 1}}
        self.detail = {'sourceId': 'phsa-2022-23', 'sourceSha256': 'original-sha',
            'completePhysicalSource': True, 'pendingFields': [], 'rowCount': 1,
            'physicalPages': [{'physicalPage': 1, 'rows': 1}],
            'rows': [{'row': copy.deepcopy(self.rows[0]), 'rawCandidateRow': copy.deepcopy(self.rows[0]),
                      'sourceRowOnPage': 1, 'fields': {f: {'status': next(iter(v))} for f, v in counts.items()}}],
            'fieldResolutionCounts': counts, 'diagnosticRemunerationSum': 80000,
            'diagnosticKnownExpenseSum': 0, 'sourcePrintedControls': {'remuneration': 80001, 'expenses': 3},
            'diagnosticControlResiduals': [-1, -3], 'rootAdoptedQualifiedNameCases': []}
        self.source = {'id': 'queue-completion-phsa-2022-23-employees', 'sha256': 'original-sha',
            'dataSha256': 'payload-sha', 'employerSlug': 'provincial-health-services-authority', 'rowCount': 1,
            'validation': {'physicalPdfPages': 1, 'fieldResolutionCounts': copy.deepcopy(counts),
                           'sourceControlResiduals': [-1, -3], 'rootAdoptedQualifiedNameCases': []}}
        self.provenance = {'sourceId': 'phsa-2022-23', 'sourceSha256': 'original-sha',
            'dataSha256': 'payload-sha', 'allNineSourceHoldoutsPassed': True,
            'rootHoldoutComparisons': [{'path': 'source-specific-holdout.json', 'sha256': 'holdout-sha'}],
            'originalRowsAndPerFieldResolution': self.detail}

    def test_literal_residuals_and_explicit_source_dash_can_be_preserved(self):
        REVIEW.verify_phsa_provenance(self.source, self.rows, self.provenance)

    def test_unfinished_or_missing_layout_holdout_cannot_publish(self):
        for mutation in ['pending', 'holdout', 'physical', 'source']:
            changed = copy.deepcopy(self.provenance)
            if mutation == 'pending':
                changed['originalRowsAndPerFieldResolution']['pendingFields'] = ['one actual field']
            elif mutation == 'holdout':
                changed['rootHoldoutComparisons'] = []
            elif mutation == 'physical':
                changed['originalRowsAndPerFieldResolution']['physicalPages'] = []
            else:
                changed['sourceSha256'] = 'changed-original'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                REVIEW.verify_phsa_provenance(self.source, self.rows, changed)

    def test_unreviewed_cell_change_or_pending_route_cannot_be_hidden(self):
        for mutation in ['change', 'pending', 'typography-money', 'implicit-null']:
            changed = copy.deepcopy(self.provenance)
            entry = changed['originalRowsAndPerFieldResolution']['rows'][0]
            if mutation == 'change':
                entry['rawCandidateRow'][3] = 80001
            elif mutation == 'pending':
                entry['fields']['name']['status'] = 'pending-original-image'
            elif mutation == 'typography-money':
                entry['fields']['remuneration']['status'] = 'manual-qualified-source-typography'
            else:
                entry['fields']['expenses']['status'] = 'baseline-independent-reader-agreement'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                REVIEW.verify_phsa_provenance(self.source, self.rows, changed)

    def test_control_and_field_route_summaries_must_match_actual_rows(self):
        for key, value in [('diagnosticControlResiduals', [0, 0]),
                           ('fieldResolutionCounts', {}), ('diagnosticRemunerationSum', 80001)]:
            changed = copy.deepcopy(self.provenance)
            changed['originalRowsAndPerFieldResolution'][key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                REVIEW.verify_phsa_provenance(self.source, self.rows, changed)


if __name__ == '__main__':
    unittest.main()
