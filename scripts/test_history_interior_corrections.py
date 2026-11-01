"""Verify that the PR27 text repair preserves its exact original evidence and monetary cells."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries/municipal-history-pass/corrections/interior-initials'
ARCHIVE=BASE/'pr27-original'
CURRENT=ROOT/'research/salaries/municipal-wave-interior'


class InteriorInitialCorrectionAudit(unittest.TestCase):
    def test_every_original_snapshot_is_byte_locked(self):
        snapshot=json.loads((ARCHIVE/'snapshot.json').read_text())
        for entry in snapshot['files']:
            raw=(ARCHIVE/entry['archivePath']).read_bytes()
            self.assertEqual(len(raw),entry['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),entry['sha256'])
        ledger=json.loads((BASE/'corrections.json').read_text())
        self.assertEqual(hashlib.sha256((ARCHIVE/'snapshot.json').read_bytes()).hexdigest(),ledger['snapshotManifestSha256'])

    def test_explicit_amendments_cover_all_changed_sources(self):
        ledger=json.loads((BASE/'corrections.json').read_text());original={s['id']:s for s in json.loads((ARCHIVE/'sources.json').read_text())['sources']};current={s['id']:s for s in json.loads((CURRENT/'sources.json').read_text())['sources']};amendments={a['sourceId']:a for a in ledger['amendments']}
        self.assertEqual(original.keys(),current.keys());self.assertEqual(len(original),21)
        self.assertEqual(sum(s['rowCount'] for s in original.values()),299)
        for sid,before in original.items():
            after=current[sid]
            for key in ['rowCount','year','periodStart','periodEnd','totalRemuneration','totalExpenses','sha256']:
                self.assertEqual(before[key],after[key])
            self.assertEqual(before['validation']['printedControls'],after['validation']['printedControls'])
            changed=before['dataSha256']!=after['dataSha256'] or before['provenanceSha256']!=after['provenanceSha256']
            self.assertEqual(changed,sid in amendments)
            if changed:
                a=amendments[sid]
                self.assertEqual(a['previousDataSha256'],before['dataSha256']);self.assertEqual(a['newDataSha256'],after['dataSha256'])
                self.assertEqual(a['previousProvenanceSha256'],before['provenanceSha256']);self.assertEqual(a['newProvenanceSha256'],after['provenanceSha256'])
        self.assertEqual(len(amendments),7)

    def test_only_published_text_initials_change_in_normalized_rows(self):
        ledger=json.loads((BASE/'corrections.json').read_text());changed=0
        for amendment in ledger['amendments']:
            before=json.loads(gzip.decompress((ARCHIVE/amendment['dataFile']).read_bytes()));after=json.loads(gzip.decompress((CURRENT/amendment['dataFile']).read_bytes()))
            actual=[]
            for index,(a,b) in enumerate(zip(before,after)):
                self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:])
                if a!=b:
                    self.assertEqual(b[1],a[1]+' A');actual.append(index);changed+=1
            self.assertEqual(actual,[r['rowIndex'] for r in amendment['rowChanges']])
            for row in amendment['rowChanges']:
                self.assertEqual(before[row['rowIndex']],row['before']);self.assertEqual(after[row['rowIndex']],row['after'])
        self.assertEqual(changed,8)


if __name__=='__main__':unittest.main()
