"""Adding reviewed sources cannot remove, reorder or rewrite earlier collections."""
import copy
import unittest

from gap_fill_previous_release import verify_registry_extension


class CollectionExtensionTests(unittest.TestCase):
    def setUp(self):
        self.old = {'version': 1, 'collections': ['original-a', 'original-b']}

    def test_exact_historical_prefix_and_explicit_new_sources_pass(self):
        verify_registry_extension(self.old, copy.deepcopy(self.old), [])
        verify_registry_extension(self.old,
            {'version': 1, 'collections': ['original-a', 'original-b', 'new-source']}, ['new-source'])

    def test_removal_reordering_version_change_and_unreviewed_append_fail(self):
        for active in [{'version': 1, 'collections': ['original-b']},
                       {'version': 1, 'collections': ['original-b', 'original-a']},
                       {'version': 2, 'collections': ['original-a', 'original-b']},
                       {'version': 1, 'collections': ['original-a', 'original-b', 'new-source']}]:
            with self.subTest(active=active), self.assertRaises(ValueError):
                verify_registry_extension(self.old, active, [])

    def test_duplicate_or_invalid_new_identifiers_fail(self):
        for additions in [['original-a'], ['new', 'new'], [None], [''], 'new']:
            with self.subTest(additions=additions), self.assertRaises(ValueError):
                verify_registry_extension(self.old, self.old, additions)


if __name__ == '__main__':
    unittest.main()
