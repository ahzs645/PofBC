"""Release snapshots cannot silently absorb repaired text, money or source scope."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from salary_release_audit import metadata_sha, verify_frozen_release


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class FrozenReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.research = Path(self.tmp.name)
        self.folder = self.research / 'release'
        self.before = ['city-of-example', 'ABLE,', None, 100000, 20, 1]
        self.old_raw = gzip.compress(json.dumps([self.before]).encode(), mtime=0)
        self.source = dict(id='source', employerSlug='city-of-example', year='2024', category='employee-remuneration', status='verified', file='rows.gzip', rowCount=1, sha256='a' * 64, dataSha256=digest(self.old_raw), sourceUrl='https://example.test/source.pdf', publicWarning='Original warning', notes=[], validation={})
        self.old_source = copy.deepcopy(self.source)
        self.entry = dict(collection='collection', sourceId='source', employerSlug=self.source['employerSlug'], year='2024', category='employee-remuneration', rows=1, sourceSha256=self.source['sha256'], dataSha256=self.source['dataSha256'], sourceUrl=self.source['sourceUrl'], publicWarning=self.source['publicWarning'])
        baseline = dict(records=5, officialRecords=2, compiledRecords=3)
        release = dict(baseline=baseline, proposed=dict(records=6, officialRecords=3, compiledRecords=3), imports=[self.entry], officialRowsAdded=1, compiledRowsReplaced=0, netRowsAdded=1)
        write(self.folder / 'release.json', release)
        write(self.folder / 'baseline.json', dict(overall=baseline))
        write(self.folder / 'work-queue.json', dict(tasks=[]))
        self.ledger = dict(amendments=[], metadataAmendments=[])
        (self.research / 'review.md').write_text('Reviewed exact original source fields.')
        self.save_rows(self.before)

    def save_rows(self, after):
        raw = gzip.compress(json.dumps([after]).encode(), mtime=0)
        self.source['dataSha256'] = digest(raw)
        path = self.research / 'collection/rows.gzip'
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
        write(self.research / 'collection/sources.json', dict(sources=[self.source]))

    def check(self):
        write(self.research / 'collection/sources.json', dict(sources=[self.source]))
        write(self.research / 'release-amendments.json', self.ledger)
        return verify_frozen_release(self.folder, self.research)

    def text_amendment(self, after):
        self.save_rows(after)
        (self.research / 'original.gzip').write_bytes(self.old_raw)
        self.ledger['amendments'] = [dict(collection='collection', sourceId='source', kind='restore-published-text', reason='Restore the printed A initial', oldDataSha256=digest(self.old_raw), newDataSha256=self.source['dataSha256'], archivedDataFile='original.gzip', reviewFile='review.md', rowChanges=[dict(rowIndex=0, before=self.before, after=after)])]

    def test_original_snapshot_passes(self):
        self.assertEqual(self.check()['sourceInputsVerified'], 1)

    def test_changed_input_requires_explicit_amendment(self):
        after = self.before.copy(); after[1] = 'ABLE, A'
        self.save_rows(after)
        with self.assertRaisesRegex(AssertionError, 'no exact reviewed amendment'):
            self.check()

    def test_reviewed_text_repair_preserves_original_snapshot(self):
        after = self.before.copy(); after[1] = 'ABLE, A'
        self.text_amendment(after)
        self.assertEqual(self.check()['reviewedAmendments'], ['source'])

    def test_text_amendment_cannot_change_money(self):
        after = self.before.copy(); after[3] = 110000
        self.text_amendment(after)
        with self.assertRaises(AssertionError):
            self.check()

    def test_archived_original_bytes_are_mandatory(self):
        after = self.before.copy(); after[1] = 'ABLE, A'
        self.text_amendment(after)
        (self.research / 'original.gzip').write_bytes(b'changed')
        with self.assertRaises(AssertionError):
            self.check()

    def test_warning_change_needs_archived_metadata_and_exact_hashes(self):
        self.source['publicWarning'] = 'Control has broader scope; blank is unknown'
        with self.assertRaisesRegex(AssertionError, 'no exact reviewed metadata amendment'):
            self.check()
        path = self.research / 'original-manifest.json'
        write(path, dict(sources=[self.old_source]))
        self.ledger['metadataAmendments'] = [dict(collection='collection', sourceId='source', kind='clarify-control-scope', reason='Correct the control scope', oldPublicWarning=self.old_source['publicWarning'], newPublicWarning=self.source['publicWarning'], archivedSourceManifest='original-manifest.json', archivedSourceManifestSha256=digest(path.read_bytes()), oldMetadataSha256=metadata_sha(self.old_source), newMetadataSha256=metadata_sha(self.source), changedFields=['publicWarning'], reviewFile='review.md')]
        self.assertEqual(self.check()['reviewedAmendments'], ['source:metadata'])
        self.source['notes'] = ['An unreviewed metadata change']
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == '__main__':
    unittest.main()
