"""Offline source regressions for the nine earlier PHSA originals.

Only committed evidence, the standard library and PyMuPDF are used. No original
PDF cache, live retrieval, image-library import or OCR model is required.
"""
import copy
import gzip
import json
from pathlib import Path
import unittest

from gap_phsa_history_build import EMPLOYER, COLLECTION, normalized_rows, number, source_name, validate_source_context, validate_retention, pinned, sha, encoded
from gap_phsa_history_fetch import AREA
from gap_phsa_history_native import amount, row


FINAL_SCANS = {
    'phsa-2009-10': ('v4', 1800, [217818851, 4396581]),
    'phsa-2010-11': ('v4', 2004, [237473291, 5486077]),
    'phsa-2011-12': ('v4', 3423, [369888459, 8500874]),
    'phsa-2012-13': ('v4', 3351, [369114727, 8792836]),
    'phsa-2013-14': ('v2', 3991, [425632576, 8642235]),
    'phsa-2014-15': ('v2', 4145, [438199995, 9051755]),
}


def load(name):
    return json.loads(gzip.decompress((AREA / name).read_bytes()))


def selected(key):
    return load(key + '-scan-selected-' + FINAL_SCANS[key][0] + '.json.gzip')


class PhsaHistorySourceTests(unittest.TestCase):
    def test_all_nine_normalized_payloads_and_provenance_match_pinned_sources(self):
        index = json.loads((AREA / 'source-acceptance-index.json').read_text())
        manifest = json.loads((COLLECTION / 'sources-candidate.json').read_text())
        by_key = {s['key']: s for s in index['sources']}
        self.assertEqual(index['pendingPeerScopes'], [])
        self.assertEqual(len(manifest['sources']), 9)
        self.assertEqual(sum(s['rowCount'] for s in manifest['sources']), 22796)
        self.assertEqual([s['year'] for s in manifest['sources']], [f'{year}/{str(year+1)[-2:]}' for year in range(2006, 2015)])
        for source in manifest['sources']:
            key = source['id'].removeprefix('gap-phsa-history-')
            item = by_key[key]
            evidence = pinned(item['selectedInput'])
            expected = normalized_rows(key, evidence, item['inputKind'])
            raw = (COLLECTION / source['file']).read_bytes()
            self.assertEqual(raw, encoded(expected))
            self.assertEqual(sha(raw), source['dataSha256'])
            self.assertEqual(sha((COLLECTION / source['provenanceFile']).read_bytes()), source['provenanceSha256'])
            self.assertEqual(len(expected), source['rowCount'])
            validate_retention(source)

    def test_compiled_retention_needs_top_level_and_matching_scope_flags(self):
        source = json.loads((COLLECTION / 'sources-candidate.json').read_text())['sources'][0]
        validate_retention(source)
        for mutate in ('top', 'scope', 'validation'):
            changed = copy.deepcopy(source)
            if mutate == 'top':
                del changed['retainCompiledPartition']
            elif mutate == 'scope':
                changed['validation']['completeEmployeeSchedule'] = False
            else:
                changed['validation']['compiledPartitionRetained'] = False
            with self.assertRaises((AssertionError, KeyError)):
                validate_retention(changed)

    def test_context_controls_and_contradictory_narrative_cannot_be_silently_reused(self):
        index = json.loads((AREA / 'source-acceptance-index.json').read_text())
        inventory = {s['key']: s for s in pinned(index['inventory'])['sources']}
        contexts = {s['key']: s for s in pinned(index['sourceContextAcceptance'])['sources']}
        item = next(s for s in index['sources'] if s['key'] == 'phsa-2009-10')
        validate_source_context(item, inventory[item['key']], contexts[item['key']])
        self.assertIsNone(item['printedEmployeeNarrativeCount'])
        self.assertEqual(item['conflictingNarrativeCount'], 1800)
        changed = copy.deepcopy(item)
        changed['printedNamedControls']['expenses'] = 4396581
        with self.assertRaises(AssertionError):
            validate_source_context(changed, inventory[item['key']], contexts[item['key']])

    def test_native_explicit_zero_negative_and_unknown_are_distinct(self):
        self.assertEqual(amount('(0)'), '0')
        self.assertEqual(amount('(1,204)'), '-1204')
        self.assertIsNone(amount('-'))
        self.assertIsNone(amount(''))
        self.assertEqual(number('-1204'), -1204)
        for token in ('NaN', 'Infinity', '-Infinity'):
            with self.assertRaises(AssertionError):
                number(token)

    def test_source_footnote_marker_is_separate_without_rewriting_name(self):
        observed = row(['Cranston,Lynda*', '200,000', '100'], 11, 120, {})
        self.assertEqual(observed['name'], 'Cranston,Lynda')
        self.assertEqual(observed['sourceFootnoteMarker'], '*')
        self.assertEqual(observed['sourceCellTexts'][0], 'Cranston,Lynda*')
        self.assertEqual(source_name('  Van der Meer ,  J.  '), 'Van der Meer,J.')

    def test_native_complete_rows_keep_literal_count_and_controls(self):
        total = 0
        for key, expected, residual in [
            ('phsa-2006-07', 1267, ['-25', '-50831']),
            ('phsa-2007-08', 1271, ['3', '13']),
            ('phsa-2008-09', 1544, ['23', '24']),
        ]:
            evidence = load(key + '-native-candidate-v2.json.gzip')
            values = normalized_rows(key, evidence, 'native')
            self.assertEqual(len(values), expected)
            self.assertEqual(evidence['residuals'], residual)
            self.assertTrue(all(r[0] == EMPLOYER and r[2] is None for r in values))
            total += len(values)
        self.assertEqual(total, 4082)
        original = load('phsa-2006-07-native-candidate-v2.json.gzip')
        self.assertEqual(original['spec']['printedCount'], 1280)
        self.assertNotEqual(len(original['popplerRows']), original['spec']['printedCount'])

    def test_all_six_scan_selections_replay_from_committed_original_evidence(self):
        total = 0
        for key, (_, expected, sums) in FINAL_SCANS.items():
            with self.subTest(key=key):
                evidence = selected(key)
                values = normalized_rows(key, evidence, 'scan')
                self.assertEqual(len(values), expected)
                self.assertEqual(evidence['literalComputedTotals'], sums)
                self.assertEqual(evidence['pending'], [])
                self.assertTrue(all(r[2] is None for r in values))
                total += len(values)
        self.assertEqual(total, 18714)

    def test_a_stale_or_edited_selected_amount_is_rejected(self):
        evidence = copy.deepcopy(selected('phsa-2012-13'))
        evidence['rows'][2103]['selected']['expenses'] = 0
        with self.assertRaises(AssertionError):
            normalized_rows('phsa-2012-13', evidence, 'scan')
        evidence = copy.deepcopy(selected('phsa-2012-13'))
        evidence['pending'] = [{'sequence': 2104, 'reasons': ['unreviewed-original-cell']}]
        with self.assertRaises(AssertionError):
            normalized_rows('phsa-2012-13', evidence, 'scan')

    def test_primary_moosa_mistake_is_preserved_and_source_corrected_additively(self):
        first = json.loads((AREA / 'primary-image-readings/phsa-2012-13-v4-batch107.json').read_text())
        self.assertIsNone(next(r for r in first['rows'] if r['sequence'] == 2104)['expenses'])
        amendment = json.loads((AREA / 'primary-image-readings/phsa-2012-13-v4-additive001.json').read_text())
        self.assertEqual(amendment['amendments'][0]['actualSourceSelected'], {'expenses': 271})
        self.assertEqual(selected('phsa-2012-13')['rows'][2103]['selected']['expenses'], 271)

    def test_actual_digit_and_actual_dash_are_not_merged(self):
        evidence = selected('phsa-2014-15')
        self.assertEqual(evidence['rows'][1746]['selected']['expenses'], 7)
        self.assertIsNone(evidence['rows'][1505]['selected']['expenses'])
        raw = load('phsa-2014-15-scan-candidate-v4.json.gzip')
        self.assertEqual(raw['rows'][1505]['tesseract']['expense']['value'], 2)
        self.assertEqual(sum(r['selected']['expenses'] is None for r in evidence['rows']), 1862)

    def test_shared_ocr_name_errors_keep_source_adoptions_and_first_alternatives(self):
        final = selected('phsa-2012-13')
        self.assertEqual(source_name(final['rows'][1976]['selected']['name']), 'McIlhargey,Allen')
        self.assertEqual(source_name(final['rows'][3329]['selected']['name']), 'Zamjitski,Serguei Vassilievitch')
        self.assertEqual(source_name(final['rows'][1316]['selected']['name']), 'Ionescu,Diana')
        raw = load('phsa-2012-13-scan-candidate-v4.json.gzip')
        self.assertEqual(raw['rows'][1976]['tesseract']['name'], 'Mclthargey, Allen')

    def test_all_scan_body_pages_have_both_preserved_raw_reader_streams(self):
        inventory = json.loads((AREA / 'source-inventory.json').read_text())['sources']
        sources = {r['key']: r for r in inventory}
        captured = set()
        for path in (AREA / 'raw-ocr').glob('*.json.gzip'):
            evidence = json.loads(gzip.decompress(path.read_bytes()))
            key, page = evidence['key'], evidence['physicalPage']
            self.assertEqual(evidence['sourceSha256'], sources[key]['sourceSha256'])
            self.assertIn('tesseractRawTsv', evidence)
            self.assertIn('rapidOcrRaw', evidence)
            self.assertNotIn((key, page), captured)
            captured.add((key, page))
        expected = {(r['key'], page) for r in inventory if r['imageOnlyPages'] for page in range(2, r['pageCount'] + 1)}
        self.assertEqual(captured, expected)
        self.assertEqual(len(captured), 475)
        self.assertEqual(sum(r['pageCount'] for r in inventory), 602)
        blank = load('raw-ocr/phsa-2012-13-p087.json.gzip')
        self.assertEqual(blank['rapidOcrRaw'], [])


if __name__ == '__main__':
    unittest.main()
