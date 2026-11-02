#!/usr/bin/env python3
"""Regression checks for source-specific names, privacy rows and control holds."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import follow_through_translink as parser
import follow_through_translink_bridge as bridge


def read_gzip(p):
    return json.loads(gzip.decompress(p.read_bytes()))


class WordPage:
    def __init__(self, words):
        self.words = words

    def get_text(self, kind):
        assert kind == 'words'
        return self.words


class TransLinkParserRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = {(p['year'], p['pdfPage']): p for p in read_gzip(parser.OUT / 'fixtures/native-page-regressions.json.gzip')}

    def parsed(self, year, page):
        p = self.fixtures[year, page]
        native = parser.native_rows(WordPage(p['words']), page)[0]
        independent = parser.poppler_rows(p['popplerLayout'], page)[0]
        self.assertEqual([(r['label'], r['amounts']) for r in native], [(r['label'], r['amounts']) for r in independent])
        return native

    def test_surnames_above_amount_rows_do_not_attach_to_previous_employee(self):
        rows = self.parsed(2020, 124)
        self.assertEqual(next(r['label'] for r in rows if r['amounts'][2] == 89128), 'Rabbani, Abdul')
        self.assertEqual(next(r['label'] for r in rows if r['amounts'][2] == 75102), 'Rahman Zadeh-Balanji, Rahman')
        rows = self.parsed(2024, 24)
        self.assertEqual(next(r['label'] for r in rows if r['amounts'][2] == 123587), 'Mo, Katherine')
        self.assertEqual(next(r['label'] for r in rows if r['amounts'][2] == 95103), 'Mohammed Mohiuddin, Mohammed')

    def test_name_continuations_below_amount_rows(self):
        rows = self.parsed(2024, 67)
        self.assertEqual(next(r['label'] for r in rows if r['amounts'][2] == 96840), 'Lima De Freitas Nobre Vaccari, Debora')
        rows = self.parsed(2025, 55)
        self.assertEqual(next(r['label'] for r in rows if r['amounts'][2] == 88961), 'Almeida Silva da Conceicao, Debora')

    def test_privacy_rows_are_individual_occurrences_and_totals_are_excluded(self):
        rows = self.parsed(2020, 141)
        private = [r for r in rows if parser.name_value(r['label']) is None]
        self.assertEqual([r['amounts'][2] for r in private], [140005, 112464, 122811, 158185])
        self.assertEqual(len(private), 4)
        self.assertFalse(any('Total' in r['label'] or r['amounts'][2] == 247475633 for r in rows))

    def test_parentheses_expenses_are_negative_and_soft_hyphen_is_missing(self):
        rows = self.parsed(2021, 146)
        self.assertEqual(next(r['amounts'][3] for r in rows if r['label'] == 'Constable 32'), -8)
        rows = self.parsed(2024, 196)
        self.assertIsNone(next(r['amounts'][3] for r in rows if r['label'] == 'Corporal 3'))
        self.assertEqual(parser.money('0'), 0)
        self.assertIsNone(parser.money('-'))
        self.assertIsNone(parser.money(''))

    def test_visibly_blank_expenses_and_source_arithmetic_error_are_preserved(self):
        rows = self.parsed(2025, 224)
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(r['amounts'][3] or 0 for r in rows), 3336)
        self.assertEqual(sum(r['amounts'][3] is None for r in rows), 3)
        self.assertEqual(next(r['amounts'][3] for r in rows if r['label'] == 'Kirshin, James'), None)

    def test_salary_component_dash_does_not_erase_published_remuneration(self):
        rows = self.parsed(2025, 153)
        self.assertEqual(next(r['amounts'] for r in rows if r['label'] == 'Lutz, Joe'), [None, 91987, 91987, None])


class TransLinkCollectionRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((parser.OUT / 'sources.json').read_text())

    def test_all_six_reports_accounted_for_and_only_one_cohort_is_held(self):
        dispositions = json.loads((parser.OUT / 'dispositions.json').read_text())['reports']
        self.assertEqual([d['year'] for d in dispositions], list(map(str, range(2020, 2026))))
        self.assertTrue(all(len(d['cohorts']) == 5 for d in dispositions))
        self.assertEqual(len(self.manifest['sources']), 29)
        self.assertEqual(sum(s['rowCount'] for s in self.manifest['sources']), 27402)
        held = self.manifest['unparsedSources']
        self.assertEqual(len(held), 1)
        self.assertEqual((held[0]['employerSlug'], held[0]['year'], held[0]['candidateRowCount']), ('coast-mountain-bus-company', '2024', 3896))
        self.assertNotIn('file', held[0])
        self.assertEqual([c['residual'] for c in held[0]['validation']['printedControls']], [3859, -3212, 647, -12])
        self.assertEqual(len(read_gzip(parser.OUT / held[0]['candidateFile'])), 3896)

    def test_accepted_row_arrays_hashes_periods_and_controls(self):
        all_rows = []
        nonzero = []
        for source in self.manifest['sources']:
            compressed = (parser.OUT / source['file']).read_bytes()
            raw = gzip.decompress(compressed)
            rows = json.loads(raw)
            self.assertEqual(hashlib.sha256(compressed).hexdigest(), source['dataSha256'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['normalizedSha256'])
            self.assertEqual(gzip.compress(raw, mtime=0), compressed)
            self.assertEqual(len(rows), source['rowCount'])
            self.assertEqual(source['periodType'], 'calendar')
            self.assertEqual(source['periodEnd'], source['year'] + '-12-31')
            self.assertEqual(sum(r[3] for r in rows), source['totalRemuneration'])
            self.assertEqual(sum(r[4] or 0 for r in rows), source['totalExpenses'])
            self.assertTrue(all(len(r) == 6 and r[0] == source['employerSlug'] and r[2] is None and r[3] > 75000 for r in rows))
            evidence = read_gzip(parser.OUT / source['provenanceFile'])
            self.assertEqual(len(evidence['rows']), len(rows))
            self.assertTrue(evidence['everyRowAllFourFieldsAndPageAgree'])
            for i, field in enumerate(['salaryPayments', 'other', 'remuneration', 'expenses']):
                control = source['validation']['printedControls'][i]
                row_sum = sum(r['amounts'][i] or 0 for r in evidence['rows'])
                self.assertEqual(control['rowSum'], row_sum)
                self.assertEqual(control['residual'], row_sum - control['printedControl'])
                if control['residual']:
                    nonzero.append((source['year'], source['employerSlug'], field, control['residual']))
                    self.assertIn('Literal source amounts are retained', source['publicWarning'])
            all_rows.extend(rows)
        self.assertEqual(sum(r[1] is None for r in all_rows), 981)
        self.assertEqual(len(nonzero), 10)
        self.assertEqual({r[0] for r in all_rows}, {p[0] for p in parser.ENTITIES})

    def test_security_uses_verified_existing_transit_police_employer_bridge(self):
        security=[s for s in self.manifest['sources'] if s['employerSlug']=='transit-police']
        self.assertEqual(len(security),6)
        for s in security:
            self.assertEqual(s['sector'],'Municipal police')
            self.assertEqual(s['employerName'],'Transit Police (TransLink Security Management Ltd.)')
            self.assertEqual(s['reportedEmployerName'],'TransLink Security Management Ltd.')
            self.assertTrue(s['title'].startswith('TransLink Security Management Ltd.'))
            self.assertTrue(all(r[0]=='transit-police' for r in read_gzip(parser.OUT/s['file'])))
        self.assertFalse(any(s['employerSlug']=='translink-security-management' for s in self.manifest['sources']))

    def test_pinned_primary_policy_bridge_and_official_index(self):
        area=parser.OUT/'employer-bridge'
        self.assertEqual(hashlib.sha256((area/'policy-bridge-receipt.json').read_bytes()).hexdigest(),'09beb74f55734d2618644dcda2682314c6880883619f2aa501b7e7a52c98c14d')
        receipt=json.loads((area/'policy-bridge-receipt.json').read_text())
        self.assertEqual(receipt['pdfSha256'],'79adee0bafbc7b955c27452b92aff8c7ae4062e59a6ecf0c1d28477b6699261b')
        self.assertEqual(hashlib.sha256((area/receipt['pdfFile']).read_bytes()).hexdigest(),receipt['pdfSha256'])
        self.assertEqual(receipt['pdfPages'],4)
        self.assertEqual(receipt['reviewedPhysicalPage'],2)
        self.assertIn('employs Transit Police Personnel',receipt['literalDefinitions']['TSML'])
        self.assertIn('Metro Vancouver Transit Police',receipt['literalDefinitions']['Transit Police'])
        index=receipt['policyIndex']
        self.assertEqual(index['sha256'],'c897451ff59f87acf21cc812c65d0d2263bb74ecaf72c67029a144b70e9dfacf')
        self.assertEqual(hashlib.sha256((area/index['file']).read_bytes()).hexdigest(),index['sha256'])
        self.assertEqual(index['linkVerified'],receipt['sourceUrl'])
        self.assertIn(receipt['sourceUrl'],(area/index['file']).read_text())
        for artifact in receipt['reviewedArtifacts']:
            self.assertEqual(hashlib.sha256((area/artifact['file']).read_bytes()).hexdigest(),artifact['sha256'])

    def test_compiled_comparison_pins_counts_and_literal_null_zero_distinction(self):
        area=parser.OUT/'employer-bridge';report=json.loads((area/'compiled-entity-review.json').read_text())
        self.assertEqual(report['compiledRows'],12464)
        self.assertEqual(report['uniqueCompiledFinancialTuples'],12464)
        self.assertEqual(report['compiledAnonymousRowsExcludedFromEntityProof'],156)
        self.assertEqual(hashlib.sha256((parser.ROOT/report['baseline']['file']).read_bytes()).hexdigest(),report['baseline']['sha256'])
        self.assertEqual(hashlib.sha256((parser.ROOT/report['officialManifest']['file']).read_bytes()).hexdigest(),report['officialManifest']['sha256'])
        for cohort in report['officialCohortPins']:
            self.assertEqual(hashlib.sha256((parser.OUT/cohort['file']).read_bytes()).hexdigest(),cohort['dataSha256'])
        regenerated=bridge.compare()
        self.assertEqual(regenerated['compiledEditionGroups'],report['compiledEditionGroups'])
        groups=report['compiledEditionGroups']
        self.assertEqual([g['exactAcceptedNamedFinancialTupleMatches'] for g in groups],[0,4033,3137])
        self.assertEqual([g['supplementalNameAndRemunerationMatches'] for g in groups],[0,4035,5136])
        self.assertEqual(groups[2]['expenseDifferencesAmongSupplementalOnlyMatches'],{'compiledZeroVersusOfficialNull':1999})
        obs=report['observationEvidence'];compressed=(area/obs['file']).read_bytes();raw=gzip.decompress(compressed)
        self.assertEqual(hashlib.sha256(compressed).hexdigest(),obs['sha256'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),obs['normalizedSha256'])
        self.assertEqual(json.loads(raw),regenerated['compiledObservationComparisons'])
        self.assertEqual(len(json.loads(raw)),12464)
        self.assertFalse(report['decision']['reassignCompiledRows'])
        self.assertFalse(report['decision']['deleteCompiledRows'])
        self.assertFalse(report['decision']['redateCompiledRows'])


if __name__ == '__main__':
    unittest.main()
