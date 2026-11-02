"""Semantic mutation regressions for explicit canonical source closures."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import unittest

import finish_salary_phsa_canonical as canonical


class CanonicalClosureTests(unittest.TestCase):
    def setUp(self):
        self.source = 'phsa-2021-22'
        self.pdf = 'f' * 64
        self.documents = {}
        self.original = {'sourceId': self.source, 'sourceSha256': self.pdf,
                         'pendingFields': [], 'rootAdoptedQualifiedNameCases': [{}], 'rows': []}
        names = ['Mundi,Jacqueline', 'Smith,Sherman', 'Jacyln,Anne']
        self.families = [[names[0]], [names[1], 'Smith,Sherrnan'], [names[2]]]
        for index, name in enumerate(names, 31):
            qualified = index == 32
            q = {'chosenName': name, 'visibleAlternatives': ['Smith,Sherrnan'],
                 'caseProvenByPixels': False} if qualified else None
            self.original['rows'].append({'row': ['phsa', name, None, 100000, 12, 119],
                'sourceRowOnPage': index, 'fields': {'name': {
                    'status': canonical.QUALIFIED if qualified else 'manual-original-image',
                    'evidence': {'nameTypographyQualification': q}},
                    'remuneration': {'status': 'manual-original-image', 'evidence': {}},
                    'expenses': {'status': 'manual-original-image', 'evidence': {}}}})
        packets = []
        for path in sorted(canonical.expected_packet_paths(self.source)):
            if '-qualified-name-' in path:
                rows = [{'physicalPage': 119, 'sourceRowOnPage': n} for n in [31, 32]]
                count = 'qualifiedNameFields'
            elif '-direct-neither-name-' in path:
                rows = [{'physicalPage': 119, 'sourceRowOnPage': 33}]
                count = 'directManualNeitherNameFields'
            else:
                rows = [{'physicalPage': 119, 'sourceRowOnPage': 31, 'field': 'remuneration'},
                        {'physicalPage': 119, 'sourceRowOnPage': 33, 'field': 'expenses'}]
                count = 'positiveMonetaryFields'
            packets.append(self.put(path, {'sourceId': self.source, 'sourceSha256': self.pdf,
                'candidateValuesWithheld': True, count: len(rows), 'rows': rows}))
        name_rows = [{'physicalPage': 119, 'sourceRowOnPage': n,
            'currentAcceptedSourceLiteral': name, 'currentCompleteVisibleAlternatives': family}
            for n, name, family in zip([31, 32, 33], names, self.families)]
        self.name_ref = self.put('reviews/name-final.json', {
            'sourceId': self.source, 'sourceSha256': self.pdf, 'accepted': True,
            'closed': True, 'unresolved': [], 'rows': name_rows})
        # A combined audit is legitimate only through exact per-row source identity.
        money_rows = [{'sourceId': self.source, 'sourceSha256': self.pdf,
            'physicalPage': 119, 'sourceRowOnPage': n, 'field': field,
            'canonicalLiteralValueBeforeHeldChoices': amount}
            for n, field, amount in [(31, 'remuneration', 100000), (33, 'expenses', 12)]]
        money_rows.append({'sourceId': 'phsa-2020-21', 'sourceSha256': 'e' * 64,
            'physicalPage': 1, 'sourceRowOnPage': 2, 'field': 'remuneration',
            'canonicalLiteralValueBeforeHeldChoices': 80000})
        self.money_ref = self.put('reviews/combined-money138.json', {
            'accepted': True, 'closed': True, 'unresolved': [], 'rows': money_rows})
        outcomes = []
        for index, (name, family) in enumerate(zip(names, self.families)):
            outcomes.append({'physicalPage': 119, 'sourceRowOnPage': index + 31,
                'field': 'name', 'value': name,
                'status': 'qualified' if len(family) > 1 else 'direct',
                'visibleAlternatives': family,
                'decisionRecord': {'receipt': self.name_ref,
                    'rowRecordPointer': f'/rows/{index}',
                    'valueField': 'currentAcceptedSourceLiteral',
                    'finiteField': 'currentCompleteVisibleAlternatives'}})
        for index, (number, field, amount) in enumerate([(31, 'remuneration', 100000), (33, 'expenses', 12)]):
            outcomes.append({'physicalPage': 119, 'sourceRowOnPage': number,
                'field': field, 'value': amount, 'status': 'direct',
                'decisionRecord': {'receipt': self.money_ref,
                    'rowRecordPointer': f'/rows/{index}',
                    'valueField': 'canonicalLiteralValueBeforeHeldChoices', 'finiteField': None}})
        self.closure = {'schema': canonical.SCHEMA, 'sourceId': self.source,
            'sourceSha256': self.pdf, 'accepted': True, 'closed': True, 'unresolved': [],
            'scopeKind': canonical.PRIOR_SCOPE, 'targetPackets': packets,
            'humanReviewReceipts': [self.name_ref, self.money_ref], 'outcomes': outcomes,
            'counts': {'targets': 5, 'nameTargets': 3, 'positiveMoneyTargets': 2,
                       'qualifiedNameTargets': 1}}

    def put(self, path, document):
        value = copy.deepcopy(document)
        digest = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
        self.documents[path] = digest, value
        return {'path': path, 'sha256': digest}

    def read(self, reference):
        digest, value = self.documents[reference['path']]
        if reference['sha256'] != digest:
            raise ValueError('Byte pin changed')
        return copy.deepcopy(value)

    def check(self, closure=None, original=None, source=None):
        closure = self.closure if closure is None else closure
        return canonical.validate(self.put('reviews/root-canonical.json', closure),
            self.source if source is None else source, self.pdf,
            self.original if original is None else original, read=self.read)

    def replace_human(self, closure, old, new_document):
        new = self.put(old['path'], new_document)
        closure['humanReviewReceipts'] = [new if r == old else r for r in closure['humanReviewReceipts']]
        for outcome in closure['outcomes']:
            if outcome['decisionRecord']['receipt'] == old:
                outcome['decisionRecord']['receipt'] = new

    def test_exact_source_scope_and_combined_money_row_authority_pass(self):
        self.assertEqual(self.check()['targets'], 5)

    def test_headerless_open_unaccepted_and_wrong_source_root_closures_fail(self):
        changes = [('sourceId', None), ('sourceSha256', 'e' * 64), ('schema', 'arbitrary'),
                   ('accepted', False), ('accepted', 1), ('closed', False),
                   ('unresolved', ['open']), ('unresolved', None)]
        for field, value in changes:
            changed = copy.deepcopy(self.closure)
            changed[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.check(changed)

    def test_missing_or_extra_canonical_packets_cannot_shrink_scope(self):
        for refs in [[], self.closure['targetPackets'][:-1],
                     self.closure['targetPackets'] + [self.closure['targetPackets'][0]]]:
            changed = copy.deepcopy(self.closure)
            changed['targetPackets'] = refs
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                self.check(changed)

    def test_packet_source_identity_count_and_duplicate_rows_are_replayed(self):
        for mutation in ['pdf', 'count', 'duplicate', 'not-source-only']:
            changed = copy.deepcopy(self.closure)
            ref = changed['targetPackets'][0]
            packet = self.read(ref)
            if mutation == 'pdf':
                packet['sourceSha256'] = 'e' * 64
            elif mutation == 'count':
                packet['rowCount'] = 100
            elif mutation == 'duplicate':
                packet['rows'].append(copy.deepcopy(packet['rows'][0]))
                for key in list(packet):
                    if key.endswith('Fields'):
                        packet[key] = len(packet['rows'])
            else:
                packet['candidateValuesWithheld'] = False
            changed['targetPackets'][0] = self.put(ref['path'], packet)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check(changed)
            self.setUp()

    def test_missing_duplicate_or_unrequested_outcomes_fail(self):
        for mutation in ['missing', 'duplicate', 'extra']:
            changed = copy.deepcopy(self.closure)
            if mutation == 'missing':
                changed['outcomes'].pop()
            elif mutation == 'duplicate':
                changed['outcomes'].append(copy.deepcopy(changed['outcomes'][0]))
            else:
                changed['outcomes'][0]['sourceRowOnPage'] = 1000
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check(changed)

    def test_cross_packet_overlap_cannot_hide_an_omitted_direct_name(self):
        changed = copy.deepcopy(self.closure)
        for index, ref in enumerate(changed['targetPackets']):
            if '-direct-neither-name-' in ref['path']:
                packet = self.read(ref)
                # Counts still match this packet, but its old direct target has
                # been replaced by a target already present in qualified names.
                packet['rows'][0]['sourceRowOnPage'] = 31
                changed['targetPackets'][index] = self.put(ref['path'], packet)
        changed['outcomes'].pop(2)
        changed['counts'] = {'targets': 4, 'nameTargets': 2,
                             'positiveMoneyTargets': 2, 'qualifiedNameTargets': 1}
        with self.assertRaisesRegex(ValueError, 'across scopes'):
            self.check(changed)

    def test_old_mundl_cannot_hide_behind_empty_root_correction_list(self):
        changed, original = copy.deepcopy(self.closure), copy.deepcopy(self.original)
        changed['canonicalNameCorrections'] = []
        changed['outcomes'][0]['value'] = 'Mundl,Jacqueline'
        changed['outcomes'][0]['visibleAlternatives'] = ['Mundl,Jacqueline']
        original['rows'][0]['row'][1] = 'Mundl,Jacqueline'
        # Root and selected candidate agree; actual pinned semantic row still says Mundi.
        with self.assertRaisesRegex(ValueError, 'pinned final human decision'):
            self.check(changed, original)

    def test_selected_name_must_match_literal_status_and_complete_finite_set(self):
        for mutation in ['literal', 'old-waiver', 'extra-family', 'dropped-family']:
            original = copy.deepcopy(self.original)
            if mutation == 'literal':
                original['rows'][0]['row'][1] = 'Mundl,Jacqueline'
            elif mutation == 'old-waiver':
                original['rows'][0]['fields']['name']['evidence']['nameTypographyQualification'] = {
                    'visibleAlternatives': ['Mundl,Jacqueline']}
            elif mutation == 'extra-family':
                original['rows'][1]['fields']['name']['evidence']['nameTypographyQualification']['visibleAlternatives'].append('Smith,Shennnan')
            else:
                original['rows'][1]['fields']['name']['evidence']['nameTypographyQualification']['visibleAlternatives'] = []
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check(original=original)

    def test_human_full_family_cannot_disagree_even_if_root_and_candidate_match(self):
        changed = copy.deepcopy(self.closure)
        human = self.read(self.name_ref)
        human['rows'][1]['currentCompleteVisibleAlternatives'] = ['Smith,Sherman', 'Smith,Other']
        self.replace_human(changed, self.name_ref, human)
        with self.assertRaisesRegex(ValueError, 'pinned final human decision'):
            self.check(changed)

    def test_decision_pointer_cannot_select_another_row_or_an_absent_value(self):
        for pointer in ['/rows/1', '/rows/99', '/rows/-1', '/rows/00', '/rows/~2', 'rows/0']:
            changed = copy.deepcopy(self.closure)
            changed['outcomes'][0]['decisionRecord']['rowRecordPointer'] = pointer
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                self.check(changed)
        changed = copy.deepcopy(self.closure)
        changed['outcomes'][0]['decisionRecord']['valueField'] = 'not-a-semantic-field'
        with self.assertRaises(ValueError):
            self.check(changed)

    def test_headerless_or_foreign_human_row_cannot_supply_a_decision(self):
        for mutation in ['no-header', 'other-header', 'open', 'wrong-money-source']:
            changed = copy.deepcopy(self.closure)
            old = self.money_ref if mutation == 'wrong-money-source' else self.name_ref
            human = self.read(old)
            if mutation == 'no-header':
                del human['sourceId'], human['sourceSha256']
            elif mutation == 'other-header':
                human['sourceId'] = 'phsa-2020-21'
            elif mutation == 'open':
                human['accepted'] = False
            else:
                human['rows'][0]['sourceId'] = 'phsa-2020-21'
            self.replace_human(changed, old, human)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check(changed)
            self.setUp()

    def test_unmapped_unrelated_human_receipts_fail(self):
        changed = copy.deepcopy(self.closure)
        changed['humanReviewReceipts'].append(self.put('reviews/unrelated.json', {
            'sourceId': self.source, 'sourceSha256': self.pdf, 'rows': []}))
        with self.assertRaisesRegex(ValueError, 'irrelevant'):
            self.check(changed)

    def test_open_individual_outcome_or_semantic_record_cannot_hide_in_closed_receipt(self):
        for location in ['outcome', 'decision']:
            for flag, value in [('accepted', False), ('closed', False),
                                ('unresolved', ['source letters pending']), ('unresolved', False)]:
                changed = copy.deepcopy(self.closure)
                if location == 'outcome':
                    changed['outcomes'][0][flag] = value
                else:
                    human = self.read(self.name_ref)
                    human['rows'][0][flag] = value
                    self.replace_human(changed, self.name_ref, human)
                with self.subTest(location=location, flag=flag), self.assertRaises(ValueError):
                    self.check(changed)
                self.setUp()

    def test_amounts_are_literal_positive_integers_without_numeric_qualification(self):
        for value in [True, 0, -1, None, '100000', 100000.0]:
            changed, original = copy.deepcopy(self.closure), copy.deepcopy(self.original)
            changed['outcomes'][3]['value'] = value
            original['rows'][0]['row'][3] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(changed, original)
        changed = copy.deepcopy(self.closure)
        changed['outcomes'][3]['status'] = 'qualified'
        with self.assertRaises(ValueError):
            self.check(changed)

    def test_boolean_human_amount_cannot_alias_integer_one(self):
        changed, original = copy.deepcopy(self.closure), copy.deepcopy(self.original)
        changed['outcomes'][3]['value'] = 1
        original['rows'][0]['row'][3] = 1
        human = self.read(self.money_ref)
        human['rows'][0]['canonicalLiteralValueBeforeHeldChoices'] = True
        self.replace_human(changed, self.money_ref, human)
        with self.assertRaisesRegex(ValueError, 'type'):
            self.check(changed, original)

    def test_selected_boolean_or_float_amount_cannot_alias_human_integer(self):
        for wrong in [True, 1.0]:
            changed, original = copy.deepcopy(self.closure), copy.deepcopy(self.original)
            changed['outcomes'][3]['value'] = 1
            original['rows'][0]['row'][3] = wrong
            human = self.read(self.money_ref)
            human['rows'][0]['canonicalLiteralValueBeforeHeldChoices'] = 1
            self.replace_human(changed, self.money_ref, human)
            with self.subTest(value=wrong), self.assertRaises(ValueError):
                self.check(changed, original)
            self.setUp()

    def test_selected_money_cannot_retain_a_glyph_qualification(self):
        original = copy.deepcopy(self.original)
        original['rows'][0]['fields']['remuneration']['status'] = canonical.QUALIFIED
        with self.assertRaises(ValueError):
            self.check(original=original)
        original = copy.deepcopy(self.original)
        original['rows'][0]['fields']['remuneration']['evidence']['nameTypographyQualification'] = {
            'visibleAlternatives': [100000, 100001]}
        with self.assertRaises(ValueError):
            self.check(original=original)

    def test_reference_aliases_cannot_duplicate_an_immutable_file(self):
        for path in ['reviews/./name-final.json', 'reviews//name-final.json',
                     '/reviews/name-final.json', 'reviews/../name-final.json']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                canonical._reference({'path': path, 'sha256': 'a' * 64})

    def test_qualified_family_cannot_be_duplicated_or_omitted(self):
        changed = copy.deepcopy(self.closure)
        changed['outcomes'][1]['visibleAlternatives'].append('Smith,Sherman')
        with self.assertRaises(ValueError):
            self.check(changed)
        changed = copy.deepcopy(self.closure)
        changed['outcomes'][1]['decisionRecord']['finiteField'] = None
        with self.assertRaises(ValueError):
            self.check(changed)

    def test_source_counts_pending_and_original_identity_are_strict(self):
        for count in [0, True, '5']:
            changed = copy.deepcopy(self.closure)
            changed['counts']['targets'] = count
            with self.subTest(count=count), self.assertRaises(ValueError):
                self.check(changed)
        for field, value in [('sourceId', 'phsa-2020-21'), ('pendingFields', ['one open field']),
                             ('pendingFields', 0), ('pendingFields', False), ('pendingFields', None)]:
            original = copy.deepcopy(self.original)
            original[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.check(original=original)

    def test_prior_packets_cannot_omit_a_selected_qualified_field(self):
        changed = copy.deepcopy(self.closure)
        for index, ref in enumerate(changed['targetPackets']):
            packet = self.read(ref)
            if '-qualified-name-' in ref['path']:
                packet['rows'] = packet['rows'][:1]
                packet['qualifiedNameFields'] = 1
                changed['targetPackets'][index] = self.put(ref['path'], packet)
        changed['outcomes'].pop(1)
        changed['counts'] = {'targets': 4, 'nameTargets': 2, 'positiveMoneyTargets': 2, 'qualifiedNameTargets': 0}
        with self.assertRaisesRegex(ValueError, 'omit a selected qualified'):
            self.check(changed)

    def test_zero_target_source_is_explicit_without_invented_positive_values(self):
        source = 'phsa-2023-24'
        refs = [self.put(path, {'sourceId': source, 'sourceSha256': self.pdf,
                'candidateValuesWithheld': True, 'rows': []})
                for path in canonical.expected_packet_paths(source)]
        human = self.put('reviews/complete-zero-source.json', {'sourceId': source,
            'sourceSha256': self.pdf, 'checkedCompletePhysicalPages': 284})
        closure = {'schema': canonical.SCHEMA, 'sourceId': source, 'sourceSha256': self.pdf,
            'accepted': True, 'closed': True, 'unresolved': [], 'scopeKind': canonical.PRIOR_SCOPE,
            'targetPackets': refs, 'humanReviewReceipts': [human], 'outcomes': [],
            'counts': {'targets': 0, 'nameTargets': 0, 'positiveMoneyTargets': 0, 'qualifiedNameTargets': 0}}
        original = {'sourceId': source, 'sourceSha256': self.pdf, 'pendingFields': [], 'rows': []}
        self.assertEqual(self.check(closure, original, source)['targets'], 0)
        closure['humanReviewReceipts'] = [self.put('reviews/headerless.json', {'accepted': True})]
        with self.assertRaises(ValueError):
            self.check(closure, original, source)

    def test_fy2019_bounded_scope_does_not_claim_all_source_rows(self):
        source = 'phsa-2019-20'
        packet = self.put('reviews/2019-bounded-source-only.json', {'sourceId': source,
            'sourceSha256': self.pdf, 'sourceOnly': True,
            'rows': [{'physicalPage': 119, 'sourceRowOnPage': 31, 'field': 'name'}]})
        human = self.put('reviews/2019-bounded-final.json', {'sourceId': source,
            'sourceSha256': self.pdf, 'rows': [{'physicalPage': 119, 'sourceRowOnPage': 31,
                'acceptedLiteral': 'Mundi,Jacqueline'}]})
        outcome = copy.deepcopy(self.closure['outcomes'][0])
        outcome['decisionRecord'] = {'receipt': human, 'rowRecordPointer': '/rows/0',
                                    'valueField': 'acceptedLiteral', 'finiteField': None}
        closure = {'schema': canonical.SCHEMA, 'sourceId': source, 'sourceSha256': self.pdf,
            'accepted': True, 'closed': True, 'unresolved': [], 'scopeKind': canonical.CURRENT_SCOPE,
            'targetPackets': [packet], 'humanReviewReceipts': [human], 'outcomes': [outcome],
            'counts': {'targets': 1, 'nameTargets': 1, 'positiveMoneyTargets': 0, 'qualifiedNameTargets': 0}}
        original = copy.deepcopy(self.original)
        original['sourceId'] = source
        self.assertEqual(self.check(closure, original, source)['targets'], 1)
        closure['scopeKind'] = canonical.PRIOR_SCOPE
        with self.assertRaises(ValueError):
            self.check(closure, original, source)

    def test_byte_pin_drift_fails_before_semantic_replay(self):
        changed = copy.deepcopy(self.closure)
        changed['humanReviewReceipts'][0]['sha256'] = 'a' * 64
        with self.assertRaises(ValueError):
            self.check(changed)

    def test_real_selected_v3_provenance_schema_smoke(self):
        source = 'phsa-2020-21'
        path = canonical.ledger.AREA / 'candidates' / f'{source}-source-v3.json'
        if not path.exists():
            self.skipTest('Concrete immutable held-v3 fixture is unavailable in this checkout')
        candidate = json.loads(path.read_text())
        provenance = canonical.ledger.COLLECTION / candidate['provenanceFile']
        payload = provenance.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), candidate['provenanceSha256'])
        original = json.loads(gzip.decompress(payload))['originalRowsAndPerFieldResolution']
        self.assertEqual(original['pendingFields'], [])
        self.assertIsInstance(original['pendingFields'], list)
        selected = canonical._selected_rows(original, source, candidate['sha256'])
        self.assertEqual(len(selected), candidate['rowCount'])
        qualified = 0
        for row in selected.values():
            status, family = canonical._selected_name(row)
            self.assertIn(row['row'][1], family)
            qualified += status == 'qualified'
        self.assertEqual(qualified, len(original['rootAdoptedQualifiedNameCases']))


if __name__ == '__main__':
    unittest.main()
