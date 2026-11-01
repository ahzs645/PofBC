"""Keep the prior recovery reproducible while later salary cohorts grow."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from salary_release_audit import verify_frozen_release

SPEC = importlib.util.spec_from_file_location('recovery_review', Path(__file__).with_name('review-salary-recovery.py'))
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class FrozenRecoveryTests(unittest.TestCase):
    def check_with_override(self, filename, change):
        original = REVIEW.read
        def read(path):
            value = original(path)
            if Path(path).as_posix().endswith(filename):
                value = copy.deepcopy(value)
                change(value)
            return value
        with patch.object(REVIEW, 'read', side_effect=read):
            return REVIEW.validate_frozen_recovery()

    def test_later_counts_do_not_change_historical_outputs(self):
        path = REVIEW.OUT / 'release.json'
        before = path.read_bytes()
        result = self.check_with_override('public/salaries/employers/index.json',
            lambda value: value.update(recordCounts={'official': 9999999, 'compiled': 1000000}))
        self.assertEqual(result['records'], 1022585)
        self.assertEqual(result['sourceInputsVerified'], 35)
        self.assertEqual(path.read_bytes(), before)

    def test_published_qualification_cannot_disappear(self):
        def change(value):
            source = next(s for s in value['sources'].values()
                          if s['id'].startswith('recovery-') and s.get('publicWarning'))
            source['publicWarning'] = None
        with self.assertRaises(AssertionError):
            self.check_with_override('public/salaries/employers/index.json', change)

    def test_published_period_cannot_change(self):
        def change(value):
            source = next(s for s in value['sources'].values() if s['id'].startswith('recovery-'))
            source['periodEnd'] = '1900-01-01'
        with self.assertRaises(AssertionError):
            self.check_with_override('public/salaries/employers/index.json', change)

    def test_frozen_manifest_hash_remains_required(self):
        def change(value):
            first = next(iter(value['manifestSha256']))
            value['manifestSha256'][first] = '0' * 64
        with self.assertRaises(AssertionError):
            self.check_with_override('recovery-wave-2026-11-01/release.json', change)


class CompressedBaselineTests(unittest.TestCase):
    def test_compressed_baseline_is_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            baseline = {'records': 2, 'officialRecords': 1, 'compiledRecords': 1}
            release = {'baseline': baseline, 'proposed': baseline, 'imports': [],
                       'officialRowsAdded': 0, 'compiledRowsReplaced': 0,
                       'netRowsAdded': 0, 'taskInputSha256': {}}
            (folder / 'baseline.json.gzip').write_bytes(gzip.compress(json.dumps({'overall': baseline}).encode()))
            (folder / 'release.json').write_text(json.dumps(release))
            (folder / 'work-queue.json').write_text('{"tasks":[]}')
            self.assertEqual(verify_frozen_release(folder, folder)['records'], 2)
            release['baseline']['records'] = 3
            (folder / 'release.json').write_text(json.dumps(release))
            with self.assertRaises(AssertionError):
                verify_frozen_release(folder, folder)


if __name__ == '__main__':
    unittest.main()
