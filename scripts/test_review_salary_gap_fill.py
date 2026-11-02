"""Mutation checks for the release's bounded supplement and queue closure."""
import copy
from pathlib import Path
import tempfile
import unittest

from gap_fill_baseline import AREA, read
from review_salary_gap_fill import (OLD_ABBOTSFORD, NEW_ABBOTSFORD,
                                    ABBOTSFORD_SHA, verify_supplement,
                                    verify_novelty, verify_dispositions,
                                    projected_metadata, verify_metadata, collection_file, freeze_entries)
from gap_fill_baseline import sha


class SupplementBounds(unittest.TestCase):
    def setUp(self):
        proof = read(AREA / 'municipal/abbotsford-known-column-supplement.json')
        held = proof['exactPriorHeldRows']
        self.baseline = {'sourceMetadata': {OLD_ABBOTSFORD: {
            'sourceKind': 'official', 'scope': 'employee-remuneration',
            'sha256': ABBOTSFORD_SHA, 'validation': {'heldRows': copy.deepcopy(held)}}}}
        self.source = {'id': NEW_ABBOTSFORD, 'sha256': ABBOTSFORD_SHA,
                       'employerSlug': 'city-of-abbotsford', 'year': '2023',
                       'scope': 'employee-remuneration', 'completeEmployeeSchedule': False,
                       'validation': {'partialCompensationDefinition': True},
                       'publicWarning': 'Partial known pay component; separate benefits remain unknown.'}
        self.rows = [[h['name'], h['position'], h['knownRemunerationColumn'], h['expenses'], h['pdfPage']] for h in held]
        self.key = ('city-of-abbotsford', '2023', OLD_ABBOTSFORD)
        self.groups = {self.key: [['Previously accepted ' + str(n), None, 80000 + n, None, 6] for n in range(449)]}

    def test_exact_eleven_known_components_allowed(self):
        verify_supplement(self.source, self.rows, self.baseline, self.groups)
        verify_novelty([(self.source, self.rows)], self.baseline, self.groups)

    def test_benefit_imputation_or_cent_change_rejected(self):
        self.rows[0][2] += .01
        with self.assertRaises(ValueError):
            verify_supplement(self.source, self.rows, self.baseline, self.groups)

    def test_twelfth_or_duplicate_row_rejected(self):
        self.rows.append(copy.deepcopy(self.rows[0]))
        with self.assertRaises(ValueError):
            verify_supplement(self.source, self.rows, self.baseline, self.groups)

    def test_prior_row_overlap_rejected(self):
        self.groups[self.key][0] = copy.deepcopy(self.rows[0])
        with self.assertRaises(ValueError):
            verify_supplement(self.source, self.rows, self.baseline, self.groups)

    def test_full_compensation_claim_rejected(self):
        self.source['completeEmployeeSchedule'] = True
        with self.assertRaises(ValueError):
            verify_supplement(self.source, self.rows, self.baseline, self.groups)

    def test_other_same_scope_import_rejected(self):
        self.source['id'] = 'another-abbotsford-import'
        with self.assertRaises(ValueError):
            verify_novelty([(self.source, self.rows)], self.baseline, self.groups)

    def test_prior_ocr_or_native_source_kind_still_blocks_overlap(self):
        self.baseline['sourceMetadata'][OLD_ABBOTSFORD]['sourceKind'] = 'official-scanned-pdf'
        self.source['id'] = 'another-abbotsford-import'
        with self.assertRaises(ValueError):
            verify_novelty([(self.source, self.rows)], self.baseline, self.groups)

    def test_duplicate_new_scope_rejected(self):
        with self.assertRaises(ValueError):
            verify_novelty([(self.source, self.rows), (self.source, self.rows)], self.baseline, self.groups)


class ExactLeadClosure(unittest.TestCase):
    def setUp(self):
        self.leads = read(AREA / 'input-leads.json')
        self.ledger = {'records': [{'leadId': r['id'], 'owner': r['owner'],
            'disposition': 'completed-public-source-processing',
            'remainingPublicProcessingTasks': 0, 'outreachSent': False}
            for r in self.leads['records']], 'noOutreach': True,
            'heldIssuerRequests': ['NIC', 'McBride', 'SD8', 'SD10']}

    def test_exact_original_leads(self):
        verify_dispositions(self.leads, self.ledger)

    def test_repeated_lead_cannot_hide_missing_lead(self):
        self.ledger['records'][-1] = copy.deepcopy(self.ledger['records'][0])
        with self.assertRaises(ValueError):
            verify_dispositions(self.leads, self.ledger)

    def test_unfinished_public_processing_rejected(self):
        self.ledger['records'][0]['remainingPublicProcessingTasks'] = 1
        with self.assertRaises(ValueError):
            verify_dispositions(self.leads, self.ledger)

    def test_unauthorized_outreach_or_changed_hold_rejected(self):
        self.ledger['records'][0]['outreachSent'] = True
        with self.assertRaises(ValueError):
            verify_dispositions(self.leads, self.ledger)
        self.ledger['records'][0]['outreachSent'] = False
        self.ledger['heldIssuerRequests'].remove('SD8')
        with self.assertRaises(ValueError):
            verify_dispositions(self.leads, self.ledger)


class AppDefinitionPreservation(unittest.TestCase):
    def test_retention_overlay_is_bounded_to_pinned_new_source(self):
        source = {'id': 'fixture', 'year': '2023', 'sha256': 'a' * 64,
                  'sourceKind': 'official', 'completeEmployeeSchedule': True,
                  'validation': {'compiledPartitionRetained': True, 'compiledPartitionRetentionReason': 'Scope equivalence unproved.'},
                  'publicWarning': 'Compiled observations remain retained.'}
        decision = {'sourceId': 'fixture', 'sourceSha256': 'a' * 64, 'dataSha256': 'b' * 64,
                    'approvedBy': 'root', 'retainCompiledPartition': True,
                    'completeEmployeeSchedule': True, 'reason': 'Preserve earlier observations.'}
        actual = projected_metadata(source, 'fixture', 'b' * 64, decision)
        self.assertTrue(actual['retainCompiledPartition'])
        self.assertTrue(actual['validation']['completeEmployeeSchedule'])
        self.assertNotIn('completeEmployeeSchedule', source['validation'])
        for field, changed in [('sourceSha256', 'c' * 64), ('dataSha256', 'd' * 64), ('completeEmployeeSchedule', False)]:
            bad = {**decision, field: changed}
            with self.assertRaises(ValueError):
                projected_metadata(source, 'fixture', 'b' * 64, bad)

    def test_stale_provenance_hash_and_outside_pointer_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory) / 'collection'
            parent.mkdir()
            raw = b'{"literalExpense":null}\n'
            (parent / 'evidence.json').write_bytes(raw)
            collection_file(parent, 'evidence.json', sha(raw))
            with self.assertRaises(ValueError):
                collection_file(parent, 'evidence.json', '0' * 64)
            outside = Path(directory) / 'outside.json'
            outside.write_bytes(raw)
            with self.assertRaises(ValueError):
                collection_file(parent, '../outside.json', sha(raw))

    def test_app_source_field_mutations_rejected(self):
        source = {'id': 'fixture', 'year': '2023', 'sourceUrl': 'https://example.gov/source.pdf',
                  'scope': 'employee-remuneration', 'threshold': None,
                  'completeEmployeeSchedule': False, 'nameDisclosure': 'source-clipped',
                  'periodStart': '2023-01-01', 'periodEnd': '2023-12-31',
                  'notes': ['Known component only; benefit unknown.'],
                  'validation': {'sourceImageProof': {'sha256': 'a' * 64}, 'unknownBenefitsRemainUnknown': True}}
        actual = projected_metadata(source, 'fixture', 'b' * 64)
        verify_metadata(source, actual, 'fixture', 'b' * 64)
        mutations = {'url': 'https://example.gov/other.pdf', 'threshold': 0,
                     'completeEmployeeSchedule': True, 'nameDisclosure': 'complete-name',
                     'periodEnd': '2024-12-31', 'notes': [],
                     'validation': {'unknownBenefitsRemainUnknown': False}}
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(actual)
                changed[field] = value
                with self.assertRaises(ValueError):
                    verify_metadata(source, changed, 'fixture', 'b' * 64)
        source['threshold'] = 0
        actual = projected_metadata(source, 'fixture', 'b' * 64)
        actual['threshold'] = False
        with self.assertRaises(ValueError):
            verify_metadata(source, actual, 'fixture', 'b' * 64)


class ProducerFreezeSchemas(unittest.TestCase):
    def test_each_exact_producer_schema_exposes_all_pins(self):
        entries = [{'path': 'source.json', 'sha256': 'a' * 64}]
        self.assertIs(freeze_entries({'files': entries}), entries)
        self.assertIs(freeze_entries({'inputs': entries, 'scope': ['source area']}), entries)

    def test_ambiguous_or_malformed_frozen_lists_fail_closed(self):
        for document in ({}, {'inputs': {}}, {'files': None}, {'files': [], 'inputs': []}):
            with self.subTest(document=document), self.assertRaises(ValueError):
                freeze_entries(document)


if __name__ == '__main__':
    unittest.main()
