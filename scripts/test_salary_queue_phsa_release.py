#!/usr/bin/env python3
"""Strict metadata-only release checks using the actual frozen PHSA base.

Only temporary roots are ever written. The expensive frozen source promoter is
mocked with its exact c510 manifest in focused cases; the real source replay is
performed separately before the two immutable integration inputs are staged.
"""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import finish_salary_queue_phsa_release as release


REAL_ROOT = release.ROOT
BASE_RAW = (REAL_ROOT / release.ARCHIVE_PATH).read_bytes()
ADOPTION_RAW = (REAL_ROOT / release.ADOPTION_PATH).read_bytes()
ROOT_RAW = (REAL_ROOT / release.BASE_ROOT_ACCEPTANCE['path']).read_bytes()
BASE = json.loads(BASE_RAW)
ADOPTION = json.loads(ADOPTION_RAW)
assert hashlib.sha256(BASE_RAW).hexdigest() == release.BASE_MANIFEST_SHA


class PhsaReleaseMetadata(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='phsa-release-tests-')
        self.root = Path(self.temporary.name)
        for relative, raw in [(release.ARCHIVE_PATH, BASE_RAW), (release.ACTIVE_PATH, BASE_RAW),
                              (release.ADOPTION_PATH, ADOPTION_RAW),
                              (release.BASE_ROOT_ACCEPTANCE['path'], ROOT_RAW)]:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.root_patch = patch.object(release, 'ROOT', self.root)
        self.root_patch.start()
        self.promoter_patch = patch.object(release.promoter, 'build', return_value=BASE)
        self.promoter = self.promoter_patch.start()

    def tearDown(self):
        self.promoter_patch.stop()
        self.root_patch.stop()
        self.temporary.cleanup()

    def adoption(self):
        return json.loads((self.root / release.ADOPTION_PATH).read_bytes())

    def mutate_adoption(self, mutation):
        value = self.adoption()
        mutation(value)
        (self.root / release.ADOPTION_PATH).write_bytes(release.packed(value))

    def denied(self, function=None):
        before = (self.root / release.ACTIVE_PATH).read_bytes()
        with self.assertRaises((ValueError, FileNotFoundError, KeyError)):
            (function or release.build)()
        self.assertEqual((self.root / release.ACTIVE_PATH).read_bytes(), before)

    def test_actual_frozen_base_yields_only_exact27_source_metadata_fields(self):
        result = release.build(copy.deepcopy(release.BASE_ROOT_ACCEPTANCE))
        self.promoter.assert_called_once_with(release.BASE_ROOT_ACCEPTANCE)
        self.assertEqual(len(result['sources']), 9)
        self.assertEqual(sum(s['rowCount'] for s in result['sources']), 64912)
        self.assertEqual(release.sha(release.packed(result)), ADOPTION['releaseManifestSHA'])
        self.assertEqual(len(release._metadata_only(BASE, result)), 27)
        self.assertEqual(release.packed(BASE), BASE_RAW)
        for before, after in zip(BASE['sources'], result['sources']):
            self.assertEqual(after['publicWarning'], before['publicWarning'] + ' ' + release.WARNING_APPEND)
            self.assertIs(after['validation']['compiledPartitionRetained'], True)
            self.assertEqual(after['validation']['compiledPartitionRetentionReason'], release.RETENTION_REASON)

    def test_optional_root_selection_reads_only_exact_adoption_pin(self):
        release.build()
        self.promoter.assert_called_once_with(release.BASE_ROOT_ACCEPTANCE)

    def test_wrong_root_sha_rejected_before_promoter_call(self):
        self.denied(lambda: release.build({**release.BASE_ROOT_ACCEPTANCE, 'sha256': 'f' * 64}))
        self.promoter.assert_not_called()

    def test_another_root_path_is_not_discovered_or_accepted(self):
        self.denied(lambda: release.build({**release.BASE_ROOT_ACCEPTANCE, 'path': 'other-root.json'}))

    def test_optional_root_cannot_be_rebound_through_artifact(self):
        self.mutate_adoption(lambda x: x['baseRootAcceptance'].update(sha256='a' * 64))
        self.denied()

    def test_root_receipt_byte_change_rejected(self):
        path = self.root / release.BASE_ROOT_ACCEPTANCE['path']
        path.write_bytes(ROOT_RAW + b' ')
        self.denied()

    def test_frozen_promoter_result_must_reproduce_exact_c510_bytes(self):
        changed = copy.deepcopy(BASE)
        changed['sources'][0]['year'] = '2024/25'
        self.promoter.return_value = changed
        self.denied()

    def test_archive_exact_bytes_not_just_semantic_json(self):
        (self.root / release.ARCHIVE_PATH).write_bytes(json.dumps(BASE).encode())
        self.denied()

    def test_missing_archive_cannot_be_generated_implicitly(self):
        (self.root / release.ARCHIVE_PATH).unlink()
        self.denied(lambda: release.build(release.BASE_ROOT_ACCEPTANCE))

    def test_missing_adoption_cannot_be_implicitly_approved(self):
        (self.root / release.ADOPTION_PATH).unlink()
        self.denied(lambda: release.build(release.BASE_ROOT_ACCEPTANCE))

    def test_adoption_whitespace_changes_are_not_the_frozen_artifact(self):
        (self.root / release.ADOPTION_PATH).write_bytes(json.dumps(ADOPTION).encode())
        self.denied()

    def test_adoption_rejects_an_arbitrary_extra_key(self):
        self.mutate_adoption(lambda x: x.update(arbitraryApproval=True))
        self.denied()

    def test_adoption_rejects_wrong_release_hash(self):
        self.mutate_adoption(lambda x: x.update(releaseManifestSHA='f' * 64))
        self.denied()

    def test_adoption_rejects_wrong_base_archive_pin(self):
        self.mutate_adoption(lambda x: x['baseManifestArchive'].update(sha256='f' * 64))
        self.denied()

    def test_adoption_rejects_missing_change_even_with_adjusted_count(self):
        def mutation(x):
            x['changes'].pop()
            x['changedFieldCount'] = 26
        self.mutate_adoption(mutation)
        self.denied()

    def test_adoption_rejects_duplicate_change_with_count27(self):
        self.mutate_adoption(lambda x: x['changes'].__setitem__(-1, copy.deepcopy(x['changes'][0])))
        self.denied()

    def test_adoption_rejects_null_instead_of_originally_absent_field(self):
        self.mutate_adoption(lambda x: x['changes'][0].update(before={'present': True, 'value': None}))
        self.denied()

    def test_adoption_rejects_integer_one_instead_of_bool_true(self):
        self.mutate_adoption(lambda x: x['changes'][0]['after'].update(value=1))
        self.denied()

    def test_adoption_cannot_authorize_a_year_change_in_place_of_a_guard(self):
        self.mutate_adoption(lambda x: x['changes'][0].update(path='/sources/0/year'))
        self.denied()

    def test_release_cannot_change_payload_hash_or_original_root_pin(self):
        for field in ['dataSha256', 'sha256', 'provenanceSha256']:
            with self.subTest(field=field):
                result = release._make_release(BASE)
                result['sources'][0][field] = '0' * 64
                with self.assertRaisesRegex(ValueError, 'outside the exact 27'):
                    release._metadata_only(BASE, result)
        result = release._make_release(BASE)
        result['sources'][0]['validation']['rootAcceptanceReceipt']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'outside the exact 27'):
            release._metadata_only(BASE, result)

    def test_release_cannot_change_nested_bool_to_equal_integer_one(self):
        result = release._make_release(BASE)
        result['sources'][0]['validation']['completeEmployeeSchedule'] = 1
        with self.assertRaisesRegex(ValueError, 'outside the exact 27'):
            release._metadata_only(BASE, result)

    def test_release_cannot_remove_or_reword_existing_source_warning(self):
        result = release._make_release(BASE)
        result['sources'][0]['publicWarning'] = release.WARNING_APPEND
        with self.assertRaises(ValueError):
            release._metadata_only(BASE, result)

    def test_build_rechecks_only_allowed_paths_after_release_generation(self):
        result = release._make_release(BASE)
        result['sources'][0]['year'] = '2024/25'
        with patch.object(release, '_make_release', return_value=result):
            self.denied()

    def test_arbitrary_active_state_rejected_and_not_overwritten(self):
        (self.root / release.ACTIVE_PATH).write_bytes(BASE_RAW + b' ')
        with patch.object(release, '_atomic_release') as atomic:
            self.denied(lambda: release.run(write=True))
            atomic.assert_not_called()

    def test_default_preview_does_not_mutate_any_input_or_active_file(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with contextlib.redirect_stdout(io.StringIO()):
            output = release.main([])
        self.assertTrue(output['previewOnly'])
        self.assertEqual(output['activeManifest']['sha256'], release.BASE_MANIFEST_SHA)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_readonly_check_rejects_base_before_explicit_write(self):
        self.denied(lambda: release.run(check=True))

    def test_explicit_write_and_optional_root_check_only_in_temporary_root(self):
        target = self.root / release.ACTIVE_PATH
        target.chmod(0o640)
        archive = (self.root / release.ARCHIVE_PATH).read_bytes()
        adoption = (self.root / release.ADOPTION_PATH).read_bytes()
        with patch.object(release, '_atomic_release', wraps=release._atomic_release) as atomic:
            release.run(write=True)
            release.run(write=True)
            self.assertEqual(atomic.call_count, 1)
        self.assertEqual(target.stat().st_mode & 0o777, 0o640)
        self.assertEqual(release.sha(target.read_bytes()), ADOPTION['releaseManifestSHA'])
        with contextlib.redirect_stdout(io.StringIO()):
            output = release.main(['--check'])
        self.assertFalse(output['previewOnly'])
        self.assertEqual((self.root / release.ARCHIVE_PATH).read_bytes(), archive)
        self.assertEqual((self.root / release.ADOPTION_PATH).read_bytes(), adoption)

    def test_write_fails_if_inputs_change_after_validation(self):
        original = release.build
        def changing_build(root_reference):
            result = original(root_reference)
            (self.root / release.ADOPTION_PATH).write_bytes(ADOPTION_RAW + b' ')
            return result
        with patch.object(release, 'build', side_effect=changing_build), patch.object(release, '_atomic_release') as atomic:
            self.denied(lambda: release.run(write=True))
            atomic.assert_not_called()

    def test_write_check_flags_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            release.main(['--write', '--check'])


if __name__ == '__main__':
    unittest.main()
