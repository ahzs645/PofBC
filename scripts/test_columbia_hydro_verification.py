import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('chc', Path(__file__).with_name('verify-columbia-hydro-salaries.py'))
chc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chc)


class ColumbiaHydroVerificationTests(unittest.TestCase):
    def test_multiset_fingerprint_retains_identical_source_rows(self):
        row = ('AB Smith', 80000, 0, 5)
        self.assertNotEqual(chc.raw_fingerprint([row]), chc.raw_fingerprint([row, row]))

    def test_two_column_layout_and_compound_surname(self):
        self.assertEqual(chc.layout_rows('PR    Adams   111,962  2,685     J  Van Zyll De Jong 76,937 0', 172),
                         [('PR Adams', 111962, 2685, 172), ('J Van Zyll De Jong', 76937, 0, 172)])

    def test_unparsed_residue_fails(self):
        with self.assertRaises(ValueError):
            chc.layout_rows('PR    Adams 111,962 2,685 BROKEN', 172)

    def test_threshold_is_strict(self):
        with self.assertRaises(ValueError):
            chc.layout_rows('PR    Adams 75,000 0', 172)

    def test_source_period_heading_is_required(self):
        entry = {'periodEnd':'2013-03-31', 'pages':[172,173,174,175]}
        with self.assertRaises(ValueError):
            chc.verify_heading('COLUMBIA HYDRO CONSTRUCTORS LTD. 1 of 4', entry, 172, 1)


if __name__ == '__main__': unittest.main()
