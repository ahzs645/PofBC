"""The accepted Columbia Hydro Constructors collection is the verified staging, and nothing else."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('accept_chc', ROOT / 'scripts/accept-chc-salaries.py')
accept = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accept)


class AcceptChcTest(unittest.TestCase):
    def test_names_keep_their_initials(self):
        self.assertEqual(accept.disclosed_name('PR Adams'), 'Adams, PR')
        self.assertEqual(accept.disclosed_name('J Van Zyll De Jong'), 'Van Zyll De Jong, J')
        self.assertEqual(accept.disclosed_name('F Gienger Sr.'), 'Gienger Sr., F')
        with self.assertRaises(SystemExit):
            accept.disclosed_name('Adams')

    def test_every_accepted_year_rests_on_its_pdf_check(self):
        review = json.loads((accept.STAGING / 'pdf-verification/review.json').read_text())
        for year in accept.YEARS:
            capture, candidates = accept.checked(year, review)
            self.assertTrue(candidates and all(row['sourceId'] == capture['sourceId'] for row in candidates))

    def test_the_committed_collection_is_the_staged_rows(self):
        manifest = json.loads((accept.OUT / 'sources.json').read_text())
        self.assertEqual([source['year'] for source in manifest['sources']], ['2012/13', '2013/14', '2014/15', '2015/16', '2016/17'])
        self.assertEqual(sum(source['rowCount'] for source in manifest['sources']), 723)
        for source in manifest['sources']:
            data = (accept.OUT / source['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['dataSha256'])
            rows = json.loads(gzip.decompress(data))
            staged = json.loads((accept.STAGING / 'candidates' / source['file'].replace('.json.gzip', '.json')).read_text())
            self.assertEqual([[row[1], row[3], row[4], row[5]] for row in rows],
                             [[accept.disclosed_name(row['rawName']), row['remuneration'], row['expenses'], row['pdfPage']] for row in staged])
            self.assertTrue(all(abs(value) <= 3 for value in source['validation']['residual']))
        self.assertEqual(manifest['aggregateOnlyPeriods'][0]['year'], '2017/18')

    def test_a_capture_changed_after_its_check_is_refused(self):
        review = json.loads((accept.STAGING / 'pdf-verification/review.json').read_text())
        tampered = json.loads(json.dumps(review))
        tampered['controls']['2013-14']['totalRemuneration'] += 1
        with self.assertRaises(SystemExit):
            accept.checked('2013-14', tampered)


if __name__ == '__main__':
    unittest.main()
