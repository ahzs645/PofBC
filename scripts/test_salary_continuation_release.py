"""Protect the published continuation while unrelated salary history grows."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('continuation_review', Path(__file__).with_name('build-salary-continuation-review.py'))
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class FrozenContinuationTests(unittest.TestCase):
    def check_with_override(self, filename, change):
        original = REVIEW.read
        def read(path):
            value = original(path)
            if Path(path).as_posix().endswith(filename):
                value = copy.deepcopy(value)
                change(value)
            return value
        with patch.object(REVIEW, 'read', side_effect=read):
            return REVIEW.validate_frozen_release()

    def test_later_unrelated_counts_do_not_rewrite_the_released_report(self):
        path = REVIEW.OUT / 'release.json'
        before = path.read_bytes()
        result = self.check_with_override('public/salaries/employers/index.json',
            lambda value: value.update(recordCounts={'official': 9999999, 'compiled': 1000000}))
        self.assertEqual(result['records'], 1010217)
        self.assertEqual(result['sourceInputsVerified'], 244)
        self.assertEqual(path.read_bytes(), before)

    def test_published_control_warning_cannot_disappear(self):
        def change(value):
            source = next(s for s in value['sources'].values()
                          if s['id'].startswith('continuation-crowns-') and s.get('publicWarning'))
            source['publicWarning'] = None
        with self.assertRaises(AssertionError):
            self.check_with_override('public/salaries/employers/index.json', change)

    def test_published_source_period_cannot_drift(self):
        def change(value):
            value['sources']['continuation-crowns-icbc-2016-17']['periodStart'] = '2016-04-01'
        with self.assertRaises(AssertionError):
            self.check_with_override('public/salaries/employers/index.json', change)

    def test_exact_compiled_replacement_fingerprint_is_still_required(self):
        def change(value):
            value['decisions'][0]['compiledRowsSha256'] = '0' * 64
        with self.assertRaises(AssertionError):
            self.check_with_override('replacement-review.json', change)


if __name__ == '__main__':
    unittest.main()
