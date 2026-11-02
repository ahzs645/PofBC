"""Negative release checks: financial equality cannot replace exact provenance."""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import check_salary_source_follow_through as check


class OriginalPreservationTests(unittest.TestCase):
    def setUp(self):
        self.source = 'compiled-source'
        self.rows = [
            ['employer', '2023/24', None, None, 80000, None, self.source, 2],
            ['employer', '2023/24', 'Doe, A', None, 90000, 0, self.source, 3],
            ['employer', '2023/24', 'Doe, A', None, 90000, 0, self.source, 3],
        ]
        self.definition = {'sourceKind': 'compiled', 'year': '2023/24', 'qualified': True}
        self.baseline = {'sourceDefinitions': {self.source: self.definition}, 'originalRecords': 3, 'originalCompiledRecords': 3}
        self.key = check.group_key(self.source, 'employer', '2023/24')
        self.frozen = {'schemaVersion': 1, 'rows': 3, 'groups': {self.key: {'rows': 3, 'sha256': check.group_hash([check.row_hash(r) for r in self.rows])}}}

    def validate(self, rows, definitions=None):
        return check.verify_old_groups(self.baseline, self.frozen,
            definitions or {self.source: self.definition}, {self.key: [check.row_hash(r) for r in rows]}, 3)

    def test_original_multiset_including_anonymous_rows_passes_in_any_order(self):
        self.assertEqual(self.validate(list(reversed(self.rows))), 3)

    def test_anonymous_observation_cannot_be_named_even_when_pay_is_unchanged(self):
        rows = copy.deepcopy(self.rows);rows[0][2] = 'Invented, Name'
        with self.assertRaisesRegex(ValueError, 'Original observations changed'):self.validate(rows)

    def test_same_count_and_pay_do_not_hide_a_duplicate_replacement(self):
        rows = copy.deepcopy(self.rows);rows[2][2] = 'Other, A'
        with self.assertRaisesRegex(ValueError, 'Original observations changed'):self.validate(rows)

    def test_original_null_expense_cannot_become_zero(self):
        rows = copy.deepcopy(self.rows);rows[0][5] = 0
        with self.assertRaisesRegex(ValueError, 'Original observations changed'):self.validate(rows)

    def test_source_definition_type_changes_are_not_coerced(self):
        changed = copy.deepcopy(self.definition);changed['qualified'] = 1
        with self.assertRaisesRegex(ValueError, 'Original source definition'):self.validate(self.rows, {self.source: changed})

    def test_original_page_period_and_source_are_in_the_hash(self):
        for field, value in [(1, '2022/23'), (6, 'replacement-source'), (7, 99)]:
            with self.subTest(field=field):
                rows = copy.deepcopy(self.rows);rows[0][field] = value
                with self.assertRaisesRegex(ValueError, 'Original observations changed'):self.validate(rows)


class NewSourceTests(unittest.TestCase):
    def setUp(self):
        self.rows = [check.observation('employer', '2024', 'Doe, A', None, 80000, None, 'new', 2),
                     check.observation('employer', '2024', None, 'Constable', 90000, 0, 'new', 3)]
        self.source = {'id': 'new', 'rowCount': 2, 'totalRemuneration': 170000, 'totalExpenses': 0,
                       'namedRowCount': 1, 'anonymousRowCount': 1}

    def test_exact_rows_preserve_missing_zero_and_anonymous_counts(self):
        metrics = check.verify_source_rows(self.source, self.rows, self.rows)
        self.assertEqual((metrics['nullExpenses'], metrics['zeroExpenses'], metrics['anonymousRows']), (1, 1, 1))

    def test_offsetting_pay_changes_cannot_pass_on_subtotal_alone(self):
        rows = [list(r) for r in self.rows];rows[0][4] += 100;rows[1][4] -= 100
        with self.assertRaisesRegex(ValueError, 'observations/multiplicity'):check.verify_source_rows(self.source, self.rows, list(map(tuple, rows)))

    def test_null_to_zero_is_rejected_even_when_known_expense_sum_stays_zero(self):
        rows = [list(r) for r in self.rows];rows[0][5] = 0
        with self.assertRaisesRegex(ValueError, 'observations/multiplicity'):check.verify_source_rows(self.source, self.rows, list(map(tuple, rows)))

    def test_repeated_row_cannot_replace_the_anonymous_observation(self):
        with self.assertRaisesRegex(ValueError, 'observations/multiplicity'):check.verify_source_rows(self.source, self.rows, [self.rows[0], self.rows[0]])

    def test_nonfinite_boolean_and_subcent_money_are_rejected(self):
        for amount in [True, float('nan'), float('inf'), 123.001]:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):check.cents(amount)

    def test_held_candidate_cannot_be_published_under_its_source_id(self):
        raw = gzip.compress(json.dumps([['held']] * check.HELD_ROWS).encode(), mtime=0)
        source = {'id': check.HELD_ID, 'status': 'held-for-review', 'candidateRowCount': check.HELD_ROWS,
                  'dataSha256': check.digest(raw), 'reason': 'Four unresolved printed controls',
                  'nextAction': 'Inspect a corrected official report'}
        check.verify_held_candidate(source, raw, set())
        with self.assertRaisesRegex(ValueError, 'source is published'):check.verify_held_candidate(source, raw, {check.HELD_ID})
        with self.assertRaisesRegex(ValueError, 'hash changed'):check.verify_held_candidate(source, raw + b'changed', set())

    def test_document_dispositions_must_cover_the_exact_three_langara_reports(self):
        sources = {};reports = []
        for report in sorted(check.expected_reports()['follow-through-langara']):
            sid = report + '-employees';sources[sid] = {'rowCount': 1, 'sha256': 'a' * 64}
            reports.append({'id': report, 'status': 'imported', 'acceptedSourceId': sid, 'employeeRows': 1})
        self.assertEqual(check.verify_dispositions('follow-through-langara', {'sources': reports}, sources, {}), 3)
        changed = copy.deepcopy(reports);changed[-1]['id'] = 'additional-source-langara-unread-future-work'
        with self.assertRaisesRegex(ValueError, 'Document dispositions changed'):check.verify_dispositions('follow-through-langara', {'sources': changed}, sources, {})
        changed = copy.deepcopy(reports);changed[0]['employeeRows'] = 0
        with self.assertRaisesRegex(ValueError, 'row count changed'):check.verify_dispositions('follow-through-langara', {'sources': changed}, sources, {})


class QualifiedMetadataTests(unittest.TestCase):
    def setUp(self):
        self.source = {'id': 'new', 'sha256': 'a' * 64, 'dataSha256': 'b' * 64, 'year': '2024',
                       'sourceUrl': 'https://official.example/report.pdf', 'category': 'employee-remuneration',
                       'employerSlug': 'employer', 'scope': 'employee-remuneration', 'completeEmployeeSchedule': True,
                       'periodStart': '2024-01-01', 'periodEnd': '2024-12-31', 'validation': {'rowCount': 2},
                       'publicWarning': 'Literal source residual retained.'}
        self.decision = {'sourceId': 'new', 'approvedBy': 'root', 'sourceSha256': 'a' * 64,
                         'dataSha256': 'b' * 64, 'completeEmployeeSchedule': True,
                         'retainCompiledPartition': True, 'reason': 'Compiled scope remains unverified.',
                         'employerSlug': 'employer'}
        self.current = {'sha256': 'a' * 64, 'dataSha256': 'b' * 64, 'year': '2024', 'url': self.source['sourceUrl'],
                        'scope': 'employee-remuneration', 'periodStart': '2024-01-01', 'periodEnd': '2024-12-31',
                        'currency': 'CAD', 'completeEmployeeSchedule': True, 'retainCompiledPartition': True,
                        'sourceKind': 'official', 'publicWarning': self.source['publicWarning'] + ' ' + self.decision['reason'],
                        'validation': {'rowCount': 2, 'completeEmployeeSchedule': True,
                                       'compiledPartitionRetained': True,
                                       'compiledPartitionRetentionReason': self.decision['reason']}}
        self.current.update({'id': 'new', 'periodType': 'calendar', 'scopeDescription': 'employee-remuneration',
                             'threshold': None, 'thresholdComparison': None, 'nameDisclosure': None, 'positionDisclosure': None})
        self.decision['metadataSha256'] = check.qualification_metadata_fingerprint(self.current, ['employer'])

    def test_exact_qualification_is_required_even_when_rows_agree(self):
        check.verify_qualification(self.source, self.current, self.decision)
        for field, value in [('dataSha256', 'c' * 64), ('sourceSha256', 'c' * 64), ('approvedBy', 'unreviewed')]:
            with self.subTest(field=field):
                bad = copy.deepcopy(self.decision);bad[field] = value
                with self.assertRaisesRegex(ValueError, 'qualification'):check.verify_qualification(self.source, self.current, bad)

    def test_public_warning_and_compiled_retention_cannot_be_dropped(self):
        for field, value in [('publicWarning', self.source['publicWarning']), ('retainCompiledPartition', False)]:
            with self.subTest(field=field):
                bad = copy.deepcopy(self.current);bad[field] = value
                with self.assertRaisesRegex(ValueError, 'metadata changed'):check.verify_qualification(self.source, bad, self.decision)

    def test_integral_json_numbers_can_lose_point_zero_but_booleans_cannot_replace_them(self):
        self.source['validation']['roundingBound'] = 2.0
        self.current['validation']['roundingBound'] = 2
        check.verify_qualification(self.source, self.current, self.decision)
        self.current['validation']['roundingBound'] = True
        with self.assertRaisesRegex(ValueError, 'validation changed'):check.verify_qualification(self.source, self.current, self.decision)

    def test_unchanged_pdf_and_payload_do_not_authorize_new_period_currency_or_url(self):
        for raw_field, live_field, value in [('year', 'year', '2025'),
                ('periodStart', 'periodStart', '2024-02-01'), ('periodEnd', 'periodEnd', '2025-03-31'),
                ('currency', 'currency', 'USD'), ('sourceUrl', 'url', 'https://official.example/different-report.pdf')]:
            with self.subTest(field=raw_field):
                source = copy.deepcopy(self.source);current = copy.deepcopy(self.current)
                source[raw_field] = current[live_field] = value
                with self.assertRaisesRegex(ValueError, 'qualification metadata fingerprint'):
                    check.verify_qualification(source, current, self.decision)

    def test_scope_threshold_and_disclosure_meaning_are_part_of_the_qualification(self):
        for raw_field, live_field, value in [('category', 'scope', 'board-remuneration'),
                ('scopeDescription', 'scopeDescription', 'Executive compensation only'),
                ('threshold', 'threshold', 100000), ('thresholdComparison', 'thresholdComparison', '>='),
                ('nameDisclosure', 'nameDisclosure', 'anonymous'), ('positionDisclosure', 'positionDisclosure', 'inferred')]:
            with self.subTest(field=raw_field):
                source = copy.deepcopy(self.source);current = copy.deepcopy(self.current)
                source[raw_field] = current[live_field] = value
                with self.assertRaisesRegex(ValueError, 'qualification metadata fingerprint'):
                    check.verify_qualification(source, current, self.decision)

    def test_the_approved_employer_cannot_change_even_when_source_bytes_do_not(self):
        source = copy.deepcopy(self.source);source['employerSlug'] = 'different-legal-employer'
        with self.assertRaisesRegex(ValueError, 'Invalid/stale source qualification'):
            check.verify_qualification(source, self.current, self.decision)
        decision = copy.deepcopy(self.decision);decision['employerSlug'] = source['employerSlug']
        with self.assertRaisesRegex(ValueError, 'qualification metadata fingerprint'):
            check.verify_qualification(source, self.current, decision)

    def test_raw_manifest_metadata_change_is_stale_even_before_a_rebuild(self):
        source = copy.deepcopy(self.source);source['threshold'] = 100000
        with self.assertRaisesRegex(ValueError, 'qualification metadata fingerprint'):
            check.verify_qualification(source, self.current, self.decision)


class ImmutableReceiptTests(unittest.TestCase):
    def test_rewritten_baseline_manifest_is_rejected_before_any_export_reads(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);area = root / check.AREA;area.mkdir(parents=True)
            (area / 'baseline.json.gzip').write_bytes(gzip.compress(b'{}', mtime=0))
            with self.assertRaisesRegex(ValueError, 'Immutable follow-through input changed'):
                check.load_inputs(root)

    def test_461_name_decisions_remain_bound_to_the_exact_old_receipt_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);pins = []
            for name, count in [('source-reviewed.json', 251), ('continuation-reviewed.json', 43),
                                ('held-completion-reviewed.json', 167), ('reviewed.json', 1)]:
                relative = 'research/salaries/name-links/' + name
                path = root / relative;path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({'decisions': [{'note': 'Pinned'}] * count}))
                pins.append({'path': relative, 'sha256': check.digest(path.read_bytes())})
            baseline = {'researchInputs': pins}
            self.assertEqual(check.verify_review_receipts(root, baseline), 461)
            path = root / 'research/salaries/name-links/held-completion-reviewed.json'
            changed = json.loads(path.read_text());changed['decisions'][0]['note'] = 'Silently broadened'
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'Original name-review receipt changed'):
                check.verify_review_receipts(root, baseline)


class ConcurrentMainReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root = Path(self.temp.name)
        self.relative = 'research/salaries/name-links/reviewed.json'
        self.old = [{'employer': 'employer', 'names': [f'Alias{i}, A', f'Original{i}, A'],
                     'decision': 'verified', 'note': 'Original individual decision'} for i in range(4)]
        self.addition = {'employer': 'employer', 'names': ['Misread, Name', 'Original, Name'],
                         'decision': 'verified', 'preferredName': 'Original, Name', 'note': 'Explicit owner review'}
        original = json.dumps({'note': 'Legacy policy', 'decisions': self.old}).encode()
        archive = self.root / check.AREA / 'baseline-code.tar.gz';archive.parent.mkdir(parents=True)
        with tarfile.open(archive, 'w:gz') as stream:
            info = tarfile.TarInfo(self.relative);info.size = len(original);stream.addfile(info, io.BytesIO(original))
        self.baseline = {'baselineCodeSha256': check.digest(archive.read_bytes()),
                         'researchInputs': [{'path': self.relative, 'sha256': check.digest(original)}]}
        self.current = {'note': 'Legacy policy', 'decisions': copy.deepcopy(self.old) + [self.addition]}
        path = self.root / self.relative;path.parent.mkdir(parents=True, exist_ok=True);path.write_text(json.dumps(self.current))
        self.capsule = {'schemaVersion': 1, 'mainCommit': 'a' * 40, 'reviewedFile': self.relative,
                        'reviewedFileSha256': check.digest(path.read_bytes()),
                        'baselineReviewedFileSha256': check.digest(original),
                        'baselineDecisions': copy.deepcopy(self.old), 'additionalDecisions': [self.addition]}

    def rewrite_current_and_repin_only_current_bytes(self):
        path = self.root / self.relative;path.write_text(json.dumps(self.current))
        self.capsule['reviewedFileSha256'] = check.digest(path.read_bytes())

    def test_only_the_exact_one_capsule_addition_can_extend_the_original_four(self):
        self.assertEqual(check.verify_concurrent_main_review(self.root, self.baseline, self.capsule), 1)

    def test_altering_any_original_decision_is_rejected_even_with_a_new_current_file_hash(self):
        self.current['decisions'][0]['note'] = 'Silently broadened old evidence'
        self.rewrite_current_and_repin_only_current_bytes()
        with self.assertRaisesRegex(ValueError, 'changed old decisions'):
            check.verify_concurrent_main_review(self.root, self.baseline, self.capsule)

    def test_removing_a_baseline_decision_cannot_be_excused_as_concurrent_main(self):
        del self.current['decisions'][2];self.rewrite_current_and_repin_only_current_bytes()
        with self.assertRaisesRegex(ValueError, 'changed old decisions'):
            check.verify_concurrent_main_review(self.root, self.baseline, self.capsule)

    def test_an_unapproved_sixth_decision_cannot_use_the_approved_addition_capsule(self):
        self.current['decisions'].append({'names': ['Other, A', 'Other, B'], 'decision': 'verified'})
        self.rewrite_current_and_repin_only_current_bytes()
        with self.assertRaisesRegex(ValueError, 'unapproved decision'):
            check.verify_concurrent_main_review(self.root, self.baseline, self.capsule)


class EmployerLinkExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root = Path(self.temp.name)
        self.folder = self.root / 'public/salaries/links/employers';self.folder.mkdir(parents=True)
        self.employers = ['employer']
        self.groups = [['employer', 'surname|full', 'Surname, Full',
                        [['surname|f', 'Surname, F', 'verified', 'Pinned source row']]],
                       ['employer', 'other|full', 'Other, Full',
                        [['other|f', 'Other, F', 'likely', 'Qualified inference']]]]
        self.write(self.groups)

    def write(self, groups):
        raw = json.dumps({'links': groups}).encode()
        (self.folder / 'employer.json.gzip').write_bytes(gzip.compress(raw, mtime=0))

    def test_employer_file_contains_the_exact_complete_groups_independent_of_order(self):
        self.write(list(reversed(self.groups)))
        self.assertEqual(check.verify_employer_link_exports(self.root, self.groups, self.employers), 1)

    def test_missing_a_group_is_rejected_even_though_the_file_exists(self):
        self.write(self.groups[:1])
        with self.assertRaisesRegex(ValueError, 'groups differ'):check.verify_employer_link_exports(self.root, self.groups, self.employers)

    def test_altered_status_or_evidence_in_an_employer_file_is_rejected(self):
        changed = copy.deepcopy(self.groups);changed[0][3][0][2] = 'likely';self.write(changed)
        with self.assertRaisesRegex(ValueError, 'groups differ'):check.verify_employer_link_exports(self.root, self.groups, self.employers)

    def test_missing_or_unknown_employer_files_cannot_hide_behind_valid_global_groups(self):
        (self.folder / 'employer.json.gzip').unlink()
        with self.assertRaisesRegex(ValueError, 'missing/unknown files'):check.verify_employer_link_exports(self.root, self.groups, self.employers)
        self.write(self.groups);(self.folder / 'unknown.json.gzip').write_bytes(gzip.compress(b'{"links":[]}'))
        with self.assertRaisesRegex(ValueError, 'missing/unknown files'):check.verify_employer_link_exports(self.root, self.groups, self.employers)

    def test_known_employer_without_joins_has_an_explicit_empty_link_file(self):
        self.employers.append('no-joins')
        (self.folder / 'no-joins.json.gzip').write_bytes(gzip.compress(b'{"links":[]}'))
        self.assertEqual(check.verify_employer_link_exports(self.root, self.groups, self.employers), 2)

    def test_a_missing_empty_employer_file_is_rejected(self):
        self.employers.append('no-joins')
        with self.assertRaisesRegex(ValueError, 'missing/unknown files'):
            check.verify_employer_link_exports(self.root, self.groups, self.employers)

    def test_a_known_empty_employer_cannot_acquire_an_invented_group(self):
        self.employers.append('no-joins')
        invented = copy.deepcopy(self.groups[0]);invented[0] = 'no-joins'
        (self.folder / 'no-joins.json.gzip').write_bytes(gzip.compress(json.dumps({'links': [invented]}).encode()))
        with self.assertRaisesRegex(ValueError, 'groups differ'):
            check.verify_employer_link_exports(self.root, self.groups, self.employers)


class GraphPreservationTests(unittest.TestCase):
    def group(self, primary, aliases, employer='employer'):
        return [employer, primary, 'Disclosed ' + primary, [[key, 'Disclosed ' + key, status, 'Evidence'] for key, status in aliases]]

    def test_new_primary_can_preserve_old_verified_pair_through_verified_bridge(self):
        old = [self.group('old-primary', [('old-alias', 'verified')])]
        live = [self.group('new-source-name', [('old-primary', 'verified'), ('old-alias', 'verified')])]
        self.assertEqual(check.verify_link_preservation(old, live)['preservedVerifiedRelationships'], 1)

    def test_verified_pair_cannot_survive_only_through_a_likely_edge(self):
        old = [self.group('a', [('b', 'verified')])]
        with self.assertRaisesRegex(ValueError, 'downgraded'):
            check.verify_link_preservation(old, [self.group('new', [('a', 'verified'), ('b', 'likely')])])

    def test_likely_pair_can_upgrade_and_survive_transitively(self):
        old = [self.group('a', [('b', 'likely')])]
        live = [self.group('new', [('a', 'verified'), ('b', 'verified')])]
        self.assertEqual(check.verify_link_preservation(old, live)['preservedNameRelationships'], 1)

    def test_same_keys_at_another_employer_do_not_preserve_a_relationship(self):
        with self.assertRaisesRegex(ValueError, 'disappeared'):
            check.verify_link_preservation([self.group('a', [('b', 'likely')])],
                                           [self.group('a', [('b', 'verified')], 'different-employer')])

    def new_review(self):
        return {'employer': 'employer', 'decision': 'verified', 'preferredName': 'Official, A',
                'names': ['Compiled, A', 'Official, A'],
                'proof': {'aliasNameKey': 'compiled|a', 'targetNameKey': 'official|a'}}

    def test_old_graph_cannot_substitute_for_missing_new_reviewed_output(self):
        old_only = [self.group('old', [('old-alias', 'verified')])]
        with self.assertRaisesRegex(ValueError, 'Required new verified source-copy output'):
            check.verify_required_name_links([self.new_review()], old_only)

    def test_new_source_copy_review_cannot_be_published_as_only_likely(self):
        with self.assertRaisesRegex(ValueError, 'Required new verified source-copy output'):
            check.verify_required_name_links([self.new_review()],
                [self.group('official|a', [('compiled|a', 'likely')])])

    def test_new_source_copy_can_use_a_different_primary_and_verified_bridge(self):
        groups = [self.group('new-canonical', [('official|a', 'verified'), ('compiled|a', 'verified')])]
        self.assertEqual(check.verify_required_name_links([self.new_review()], groups), 1)


class BacklogMappingTests(unittest.TestCase):
    def setUp(self):
        self.ref = {'sourceId': 'accepted', 'manifest': 'research/salaries/actual/sources.json',
                    'file': 'research/salaries/actual/2024.json.gzip', 'rowCount': 1,
                    'dataSha256': 'a' * 64, 'sourceSha256': 'b' * 64,
                    'employerSlug': 'employer', 'year': '2024', 'periodStart': '2024-01-01',
                    'periodEnd': '2024-12-31', 'sourceUrl': 'https://official.example/report.pdf'}
        accepted = {'id': 'old-pending-now-accepted', 'group': 'original73',
                    'recommendedBacklogStatus': 'imported', 'employeeScopeComplete': True,
                    'currentAcceptedEmployeeCohorts': [self.ref], 'acceptedEmployeeRows': 1,
                    'heldCohorts': [], 'blockers': [], 'providedPendingStatusIsStale': True}
        opened = {'id': 'open-scan', 'group': 'original73', 'recommendedBacklogStatus': 'requires-ocr',
                  'employeeScopeComplete': False, 'currentAcceptedEmployeeCohorts': [],
                  'acceptedEmployeeRows': 0, 'heldCohorts': [], 'blockers': [{'reason': 'Image cells need independent verification'}]}
        self.plan = {'dispositions': [accepted, opened]}
        self.provided = {'sources': [{'id': 'old-pending-now-accepted'}, {'id': 'open-scan'}]}
        fields = ('sourceId', 'manifest', 'file', 'rowCount', 'dataSha256', 'sourceSha256',
                  'employerSlug', 'year', 'periodStart', 'periodEnd')
        self.live = {'sources': [
            {'id': 'old-pending-now-accepted', 'status': 'imported', 'employeeScopeComplete': True,
             'acceptedRows': 1, 'acceptedSourceIds': ['accepted'], 'acceptedManifests': [self.ref['manifest']],
             'acceptedSourceId': 'accepted', 'acceptedManifest': self.ref['manifest'],
             'acceptedCohorts': [{k: self.ref[k] for k in fields}], 'heldCohorts': []},
            {'id': 'open-scan', 'status': 'requires-ocr', 'employeeScopeComplete': False,
             'acceptedRows': 0, 'acceptedSourceIds': [], 'acceptedManifests': [], 'heldCohorts': [],
             'nextAction': 'Review each original employee cell and both monetary controls.'},
        ]}
        self.catalog = [
            {'id': 'accepted', 'acceptedSourceId': 'accepted', 'employerSlug': 'employer',
             'year': '2024', 'rows': 1, 'status': 'imported', 'scope': 'employee-remuneration',
             'url': self.ref['sourceUrl']},
            {'id': check.HELD_ID, 'status': 'held-for-review', 'rows': 0},
        ]

    def validate(self):
        return check.verify_backlog_mapping(self.provided, self.plan, self.live, lambda ref: None, self.catalog)

    def test_resolved_pending_entry_and_concrete_open_blocker_remain_distinct(self):
        result = self.validate()
        self.assertEqual((result['backlogImportedEntries'], result['backlogOpenEntries'], result['staleOriginalPendingEntriesResolved']), (1, 1, 1))

    def test_duplicate_or_missing_provided_id_cannot_be_hidden_by_total_count(self):
        self.live['sources'][1]['id'] = 'old-pending-now-accepted'
        with self.assertRaisesRegex(ValueError, 'Repeated backlog identifier'):self.validate()

    def test_stale_old_requires_ocr_status_cannot_survive_an_accepted_mapping(self):
        self.live['sources'][0]['status'] = 'requires-ocr'
        with self.assertRaisesRegex(ValueError, 'Backlog status is stale'):self.validate()

    def test_old_prepared_manifest_pointer_cannot_coexist_with_correct_array_pointer(self):
        self.live['sources'][0]['acceptedManifest'] = 'research/salaries/prepared-staging/sources.json'
        with self.assertRaisesRegex(ValueError, 'Stale singular accepted manifest'):self.validate()

    def test_correct_imported_catalog_entry_does_not_hide_a_stale_held_copy(self):
        self.catalog.append({'id': 'old-pending-now-accepted', 'employerSlug': 'employer',
                             'year': '2024', 'url': self.ref['sourceUrl'],
                             'scope': 'employee-remuneration', 'status': 'held-for-review'})
        with self.assertRaisesRegex(ValueError, 'retains a stale held employee lead'):self.validate()

    def test_held_cmbc_can_never_enter_accepted_backlog_source_ids(self):
        self.plan['dispositions'][0]['currentAcceptedEmployeeCohorts'][0]['sourceId'] = check.HELD_ID
        self.live['sources'][0]['acceptedSourceIds'] = [check.HELD_ID]
        with self.assertRaisesRegex(ValueError, 'Held/repeated source'):self.validate()


class CurrencyPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root = Path(self.temp.name)
        self.record = {'employer': 'bc-investment-management-corporation', 'period': '2023/24',
                       'name': 'Pittmsn, Jim', 'position': 'Executive Vice President', 'pay': 3902330,
                       'expenses': 0, 'sourceId': 'compiled', 'pdfPage': None}
        annotations = {'schemaVersion': 1, 'annotations': [{'id': 'bci-pittman-2023-24-usd-total-compensation',
                                                          'record': self.record, 'currency': 'USD'}]}
        self.write('research/salaries/record-annotations.json', annotations)
        self.write('public/salaries/record-annotations.json', annotations)
        self.baseline = {'researchInputs': [{'path': 'research/salaries/record-annotations.json',
            'sha256': check.digest((self.root / 'research/salaries/record-annotations.json').read_bytes())}]}
        self.index = {'years': ['2023/24'], 'sources': {'compiled': {'currency': 'CAD'}}}
        self.write('public/salaries/people/index.json', {**self.index,
            'employers': [['BCI', 'Crown', None, self.record['employer']]]})
        self.person = [self.record[k] for k in ['name', 'position', 'pay', 'expenses']] + [0, 0, 'compiled', None]
        self.write('public/salaries/employers/bc-investment-management-corporation.json.gzip',
                   [self.person[:4] + [0, 'compiled', None]])
        self.top = {'comparisonCurrency': 'CAD', 'rows': [], 'unrankedRows': [self.person]}
        self.write('public/salaries/people/top.json.gzip', self.top)

    def write(self, path, value):
        target = self.root / path;target.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value).encode();target.write_bytes(gzip.compress(raw, mtime=0) if target.suffix == '.gzip' else raw)

    def test_original_usd_observation_remains_accessible_outside_cad_ranking(self):
        self.assertEqual(check.verify_currency(self.root, self.baseline, self.index), 1)

    def test_usd_row_cannot_leak_into_cad_ranking_even_with_unchanged_salary_rows(self):
        self.top['rows'] = [self.person];self.write('public/salaries/people/top.json.gzip', self.top)
        with self.assertRaisesRegex(ValueError, 'leaked into CAD'):check.verify_currency(self.root, self.baseline, self.index)

    def test_missing_unranked_access_or_mutated_annotation_is_rejected(self):
        self.top['unrankedRows'] = [];self.write('public/salaries/people/top.json.gzip', self.top)
        with self.assertRaisesRegex(ValueError, 'unranked top access'):check.verify_currency(self.root, self.baseline, self.index)
        self.write('research/salaries/record-annotations.json', {'annotations': []})
        with self.assertRaisesRegex(ValueError, 'receipt changed'):check.verify_currency(self.root, self.baseline, self.index)


if __name__ == '__main__':unittest.main()
