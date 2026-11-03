import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from check_salary_historical_releases import prepare


class HistoricalIsolation(unittest.TestCase):
    def test_live_roots_and_nonempty_output_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); root = base / 'live'; root.mkdir()
            (root / 'marker').write_text('live')
            area = root / 'area'; area.mkdir()
            for output in [root, base, root / 'inside']:
                with self.assertRaisesRegex(ValueError, 'overlap'):
                    prepare(root, area, output)
            output = base / 'output'; output.mkdir(); (output / 'marker').write_text('keep')
            with self.assertRaisesRegex(ValueError, 'empty isolated'):
                prepare(root, area, output)
            self.assertEqual((root / 'marker').read_text(), 'live')
            self.assertEqual((output / 'marker').read_text(), 'keep')

    def test_archive_escape_is_rejected_before_extracting_any_code(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); root = base / 'live'; root.mkdir(); area = root / 'area'; area.mkdir()
            archive = area / 'baseline-code.tar.gz'
            with tarfile.open(archive, 'w:gz') as stream:
                data = b'bad'; member = tarfile.TarInfo('../escape'); member.size = len(data); stream.addfile(member, io.BytesIO(data))
            manifest = {'baselineCodeSha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'researchInputs': []}
            (area / 'baseline.json.gzip').write_bytes(gzip.compress(json.dumps(manifest).encode()))
            with self.assertRaisesRegex(ValueError, 'Unsafe historical archive'):
                prepare(root, area, base / 'isolated')
            self.assertFalse((base / 'escape').exists())


if __name__ == '__main__':
    unittest.main()
