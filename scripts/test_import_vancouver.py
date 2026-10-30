import contextlib
import gzip
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('vancouver_import', Path(__file__).with_name('import-vancouver-salaries.py'))
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


class VancouverChecks(unittest.TestCase):
    def test_import_precision_is_distinct_from_compiler_comparison_rounding(self):
        self.assertEqual(IMPORTER.number('75000.01'), 75000.01)
        self.assertEqual(IMPORTER.number('-5.10'), -5.1)
        self.assertEqual(IMPORTER.number('0'), 0)
        self.assertIsNone(IMPORTER.number(''))
        self.assertEqual(IMPORTER.comparison_key('Example, A', '100000.50')[1], 100000)
        self.assertEqual(IMPORTER.number('100000.50'), 100000.5)
        with self.assertRaises(ValueError):
            IMPORTER.number('75000.001')

    def test_rejected_annual_control_cannot_partially_overwrite_a_collection(self):
        raw = IMPORTER.OUT / 'raw'
        controls = json.loads(gzip.decompress((raw / 'annual-controls.json.gzip').read_bytes()))
        controls['results'][0]['rows'] += 1
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            control_file = path / 'incorrect-controls.json'
            control_file.write_text(json.dumps(controls))
            out = path / 'existing'
            out.mkdir()
            (out / 'sentinel').write_text('previous accepted input')
            with self.assertRaisesRegex(ValueError, 'does not reconcile'):
                with contextlib.redirect_stdout(io.StringIO()):
                    IMPORTER.process(raw / 'employee-remuneration.csv.gzip', raw / 'employee-remuneration.json.gzip',
                                     control_file, IMPORTER.ROOT / 'research/salaries/compiled-baseline.json.gzip', out)
            self.assertEqual([p.name for p in out.iterdir()], ['sentinel'])
            self.assertEqual((out / 'sentinel').read_text(), 'previous accepted input')


if __name__ == '__main__':
    unittest.main()
