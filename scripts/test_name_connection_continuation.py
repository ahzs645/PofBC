"""Prevent likely-name relationships from becoming source proof during queue reconciliation."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import review_name_connection_continuation as review


class ContinuedNameReviewTest(unittest.TestCase):
    def test_only_verified_edges_can_supply_another_names_primary_rows(self):
        groups = [['phsa', 'correct|name', 'Correct,Name', [
            ['typo|name', 'Typo,Name', 'verified', 'Original reviewed'],
            ['correct|n', 'Correct,N', 'likely', 'One fuller name']]]]
        lookup = review.graph(groups)
        self.assertEqual(review.verified_equivalents('phsa', 'correct|n', lookup), {'correct|n'})
        self.assertEqual(review.verified_equivalents('phsa', 'typo|name', lookup), {'correct|name', 'typo|name'})
        self.assertEqual(review.verified_equivalents('another', 'typo|name', lookup), {'typo|name'})

    def test_a_likely_path_cannot_close_a_pair_but_a_verified_source_correction_can(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            area = root / 'review'
            area.mkdir()
            people = root / 'public/salaries/people'
            people.mkdir(parents=True)
            links = root / 'public/salaries/links'
            links.mkdir(parents=True)
            def write(path, value):
                path.write_text(json.dumps(value))
            index = {'employers': [['PHSA', 'Health', None, 'phsa']], 'years': ['2023/24'], 'shards': {'one': 2},
                     'sources': {'original': {'sourceKind': 'official-pdf', 'sha256': 'source-hash', 'url': 'https://example.test/report.pdf'}}}
            write(people / 'index.json', index)
            rows = [['Correct,Name', None, 100000, None, 0, 0, 'original', 1], ['Other,Name', None, 120000, 5, 0, 0, 'original', 2]]
            (people / 'one.json.gzip').write_bytes(gzip.compress(json.dumps(rows).encode()))
            groups = [['phsa', 'correct|name', 'Correct,Name', [
                ['typo|name', 'Typo,Name', 'verified', 'Source reviewed'], ['correct|n', 'Correct,N', 'likely', 'Unique fuller name']]]]
            (links / 'co.json.gzip').write_bytes(gzip.compress(json.dumps({'links': groups}).encode()))
            baseline = area / 'baseline-links.json.gzip'
            baseline.write_bytes(gzip.compress(json.dumps({'groups': groups}).encode()))
            baseline_hash = hashlib.sha256(baseline.read_bytes()).hexdigest()
            write(area / 'inputs.json', {'baseCommit': 'base', 'files': [], 'priorHeldCandidates': 2, 'baselineLinksSha256': baseline_hash})
            write(area / 'render-manifest.json', {'cases': []})
            prior = area / 'prior.json'
            write(prior, [{'id': i, 'employer': 'phsa', 'names': [name, 'Other,Name'], 'status': 'hold-two-primary-spellings',
                           'reason': 'Identity is not established', 'evidence': []} for i, name in enumerate(['Correct,N', 'Typo,Name'], 1)])
            with patch.multiple(review, ROOT=root, AREA=area, PRIOR=prior):
                summary, results, _ = review.build_ledger({'decisions': []}, [], {})
                self.assertTrue(results[0]['pending'])
                self.assertFalse(results[1]['pending'])
                self.assertEqual([e['row'][0] for e in results[1]['evidence']], ['Correct,Name', 'Other,Name'])
                self.assertEqual(summary['candidatePairsResolved'], 1)
                pinned = people / 'index.json'
                write(area / 'inputs.json', {'baseCommit': 'base', 'priorHeldCandidates': 2, 'baselineLinksSha256': baseline_hash,
                                            'files': [{'path': str(pinned.relative_to(root)), 'sha256': hashlib.sha256(pinned.read_bytes()).hexdigest()}]})
                index['years'] = ['2024/25']
                write(pinned, index)
                with self.assertRaisesRegex(ValueError, 'Preserved input changed'):
                    review.build_ledger({'decisions': []}, [], {})

    def test_a_manual_review_cannot_be_reused_for_changed_source_pixels_or_a_changed_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            area = root / 'review'
            area.mkdir()
            (area / 'renders').mkdir()
            def write(path, value):
                path.write_text(json.dumps(value))
            crop = root / 'row.png'
            crop.write_bytes(b'original source crop')
            locator = root / 'locator.json'
            locator.write_text('{}')
            sheet = area / 'renders/sheet-01.png'
            sheet.write_bytes(b'personally viewed original sheet')
            evidence = {'sourceId': 'original', 'physicalPage': 5, 'pdfSha256': 'pdf-hash', 'rowSha256': 'row-hash', 'role': 'financial-witness'}
            proposal = [{'id': 1, 'kind': 'compiled-row', 'employer': 'phsa', 'fromName': 'Murtby,Srinivasa',
                         'toName': 'Murthy,Srinivasa', 'aliasRowsSha256': 'alias-hash', 'reviewRows': [evidence]}]
            write(area / 'review-plan.json', proposal)
            write(area / 'render-manifest.json', {'issues': [], 'cases': [{**evidence, 'planIndex': 0, 'evidenceIndex': 0, 'sheet': 1,
                'crop': 'row.png', 'cropSha256': review.sha(crop), 'locator': {'path': 'locator.json', 'sha256': review.sha(locator)}}]})
            visual = {'reviewPlanSha256': review.sha(area / 'review-plan.json'), 'renderManifestSha256': review.sha(area / 'render-manifest.json'),
                      'sheets': [{'sheet': 1, 'sha256': review.sha(sheet), 'items': [{'planIndex': 0, 'evidenceIndex': 0}]}],
                      'plans': [{'planIndex': 0, 'candidateId': 1, 'decision': 'verified-source-spelling', 'printedName': 'Murthy,Srinivasa'}]}
            write(area / 'visual-review.json', visual)
            with patch.multiple(review, ROOT=root, AREA=area):
                self.assertEqual(len(review.checked_review()[0]['decisions']), 1)
                crop.write_bytes(b'a different row')
                with self.assertRaisesRegex(ValueError, 'reviewed crop'):
                    review.checked_review()
                crop.write_bytes(b'original source crop')
                proposal[0]['toName'] = 'Murthy,Sriram'
                write(area / 'review-plan.json', proposal)
                with self.assertRaisesRegex(ValueError, 'reviewed plan'):
                    review.checked_review()


if __name__ == '__main__':
    unittest.main()
