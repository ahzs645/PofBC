#!/usr/bin/env python3
"""Regression checks for original field fidelity and qualified/partial scopes."""
import copy
import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

import parse_history_lower_mainland as parser

OUT = parser.OUT
CONFIG = json.loads((OUT / 'reviewed-layouts.json').read_text())
MANIFEST = json.loads((OUT / 'sources.json').read_text())


def source(year, category='employee-remuneration'):
    return next(s for s in MANIFEST['sources'] if s['year'] == str(year) and s['category'] == category
                and s['employerSlug'] == 'city-of-port-moody')


def data(s):
    return json.loads(gzip.decompress((OUT / s['file']).read_bytes()))


def evidence(s):
    return json.loads(gzip.decompress((OUT / s['validation']['evidenceFile']).read_bytes()))


class OriginalFields(unittest.TestCase):
    def test_offline_dual_reader_reproduction(self):
        with redirect_stdout(io.StringIO()):
            parser.build(CONFIG, Path('/does-not-exist'), check_data=True)

    def test_money_missing_zero_negative_and_unreviewed_token(self):
        self.assertIsNone(parser.money('-'))
        self.assertIsNone(parser.money(''))
        self.assertEqual(parser.money('0'), 0)
        self.assertEqual(parser.money('(61)'), -6100)
        self.assertEqual(parser.money('−9'), -900)
        with self.assertRaises(ValueError):
            parser.money('I,234')

    def test_initials_ampersand_and_wrapped_position_are_literal(self):
        rows = data(source(2021))
        self.assertEqual(next(r for r in rows if r[1] == 'Smith, Matt J')[2], 'Production Coordinator')
        row = next(r for r in rows if r[1] == 'Rutherford, Virgelene')
        self.assertEqual(row[2], 'Manager of Labour Relations, Learning & Wellness')
        self.assertEqual(row[3:], [144927, 2407, 11])
        for report in CONFIG['reports']:
            for section in report['sections']:
                for part in section.get('parts', [section]):
                    self.assertFalse(part.get('ignoreTokens'))
        earlier = data(source(2019))
        self.assertIn('Smith, Matt J', {r[1] for r in earlier})
        self.assertEqual(next(r for r in earlier if r[1] == 'Boechler, Michael')[4], -17)

    def test_negative_expenses_and_blank_expenses_remain_distinct(self):
        rows = data(source(2024))
        negatives = {r[1]: r[4] for r in rows if r[4] is not None and r[4] < 0}
        self.assertEqual(negatives, {'Ballena, Trifon': -34, 'Brown, Corene': -29, 'Butt, Kevin': -124,
                                    'Finlay, Jeff': -4, 'Peters, Trina': -6044, 'Piffer, David': -310,
                                    'Wallbank, Mark': -9, 'Werner, Kari': -61})
        self.assertIsNone(next(r for r in rows if r[1] == 'Afsahi, Fakhriazam')[4])

    def test_office_transition_is_not_name_deduplicated(self):
        rows = [r for r in data(source(2022, 'elected-officials')) if r[1] == 'Lahti, Meghan']
        self.assertEqual([(r[2], r[3]) for r in rows], [('Mayor', 17852), ('Councilor', 37202)])
        self.assertEqual(source(2022, 'elected-officials')['rowCount'], 12)

    def test_missing_benefit_components_are_held_and_never_replacement_complete(self):
        expected = {2019: (145, 144, 1), 2020: (151, 150, 1), 2021: (163, 163, 0), 2022: (164, 163, 1),
                    2023: (164, 163, 1), 2024: (242, 238, 4), 2025: (220, 216, 4)}
        for year, (full, accepted, held) in expected.items():
            s = source(year)
            self.assertEqual((s['validation']['sourceNamedRows'], s['rowCount'], s['validation']['heldMissingBenefitRows']), (full, accepted, held))
            self.assertEqual(s['completeEmployeeSchedule'], not bool(held))
            self.assertEqual(s['validation']['completeEmployeeSchedule'], not bool(held))
            raw = evidence(s)['componentRows']
            held_names = {r['name'] for r in raw if r['benefits'] is None}
            self.assertEqual(held_names, {r['name'] for r in s['validation']['heldRows']})
            self.assertFalse(held_names & {r[1] for r in data(s)})
            self.assertTrue(all(r['salary'] is not None and r['pay'] is None for r in raw if r['name'] in held_names))

    def test_2025_material_conflict_keeps_all_original_scope_equations(self):
        s = source(2025)
        raw = evidence(s)['componentRows']
        self.assertEqual(len(raw), 220)
        self.assertEqual(sum(r['salary'] for r in raw), 2581025200)
        self.assertEqual(s['totalRemuneration'], 25930099)
        controls = {c['field']: c for c in s['validation']['controls']}
        self.assertEqual(controls['salary']['sourceColumnLabel'], 'Remuneration')
        self.assertEqual(controls['salary']['residual'], -2999990)
        aggregate = s['validation']['printedAggregateControls']
        self.assertEqual(aggregate['printedNamedPlusUnderMinusGrand'], [3000000, 0, 0])
        self.assertEqual(aggregate['knownNamedPlusPrintedUnderMinusGrand'], [10, 12, -1])
        self.assertEqual(s['validation']['sourceRowCountsByPhysicalPage'], [
            {'page': p, 'rows': n} for p, n in zip(range(41, 48), [31, 38, 37, 37, 37, 37, 3])])
        self.assertEqual(s['validation']['independentCrossReview']['fullRenderedEmployeePages'], list(range(41, 48)))
        for text in ['−$2,999,990', '$3,000,000', '$10 above', '216 accepted', 'cause is unknown']:
            self.assertIn(text, s['publicWarning'])
        self.assertNotIn('e+06', s['publicWarning'])
        self.assertEqual({r['name'] for r in s['validation']['heldRows']},
                         {'Cameron, Matthew', 'Dhak, Jaspal', 'Mohebi, Mohammad', 'Virgo, Everton'})

    def test_disclosed_rows_below_first_component_threshold_are_retained(self):
        rows = data(source(2025))
        for name, pay in [('Haddon, Brad', 75500), ('King, Traci', 76515), ('Wilde, Andrew', 75445)]:
            self.assertEqual(next(r for r in rows if r[1] == name)[3], pay)

    def test_changed_original_cannot_reuse_reviewed_layout(self):
        config = copy.deepcopy(CONFIG)
        config['reports'] = [config['reports'][0]]
        report = config['reports'][0]
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, report['key'] + '.pdf').write_bytes(b'%PDF-changed-original')
            with self.assertRaisesRegex(ValueError, 'fingerprint changed'):
                parser.build(config, Path(tmp))

    def test_richmond_independent_ocr_and_source_controls_keep_exact_residuals(self):
        s = next(s for s in MANIFEST['sources'] if s['employerSlug'] == 'city-of-richmond')
        raw = evidence(s)['componentRows']
        self.assertEqual((len(raw), s['rowCount']), (1233, 1231))
        self.assertEqual([sum(r[f] or 0 for r in raw)//100 for f in ['salary', 'benefits', 'expenses']],
                         [124813470, 23773412, 577933])
        self.assertEqual([r['residual'] for r in s['validation']['controls']], [30, -28, 40])
        self.assertEqual(s['totalRemuneration'], 148393545)
        self.assertEqual(s['validation']['printedAggregateControls']['knownNamedComponentsMinusPrintedCombinedNamedRemuneration'], 3)
        self.assertEqual(s['validation']['printedAggregateControls']['printedNamedComponentsMinusPrintedCombinedNamedRemuneration'], 1)
        self.assertEqual(s['pages'], list(range(47, 76)))
        self.assertEqual([r['rows'] for r in s['validation']['sourceRowCountsByPhysicalPage']], [44]*27+[40, 5])
        self.assertTrue(s['validation']['independentOcr']['allAcceptedAndHeldRowFieldsAgreeAfterRenderedCorrections'])
        self.assertEqual(len(evidence(s)['parts']), 29)
        review = s['validation']['independentCrossReview']
        self.assertEqual(review['sourceRowsReviewedByPartition'], [308, 352, 573])
        self.assertEqual(review['acceptedRowsReviewedByPartition'], [308, 351, 572])
        self.assertEqual(s['validation']['physicalPagesVisuallyReviewed'], list(range(47, 76)))
        self.assertEqual(len(review['files']), 3)

    def test_richmond_missing_base_component_is_not_replaced_by_known_benefits(self):
        s = next(s for s in MANIFEST['sources'] if s['employerSlug'] == 'city-of-richmond')
        self.assertIs(s['completeEmployeeSchedule'], False)
        self.assertIs(s['validation']['completeEmployeeSchedule'], False)
        self.assertEqual(s['validation']['heldMissingPayComponentRows'], 2)
        self.assertEqual(s['validation']['heldMissingBenefitRows'], 0)
        held = s['validation']['heldRows']
        self.assertEqual([(r['name'], r['pdfPage'], r['knownBaseSalary'], r['knownBenefitsAndOther']) for r in held],
                         [('Duncan, Scott', 54, None, 98718), ('Young, Jim', 74, None, 94619)])
        self.assertFalse({r['name'] for r in held} & {r[1] for r in data(s)})
        self.assertTrue(all(r[2] is None for r in data(s)))

    def test_richmond_ocr_adjudications_preserve_initials_and_exact_printed_cells(self):
        s = next(s for s in MANIFEST['sources'] if s['employerSlug'] == 'city-of-richmond')
        rows = data(s)
        self.assertIn('Chiu, I Lin', {r[1] for r in rows})
        self.assertIn('Chien, Johny', {r[1] for r in rows})
        self.assertIn('Wringe, Iain', {r[1] for r in rows})
        self.assertIn('Gill, Manraj', {r[1] for r in rows})
        self.assertEqual(next(r for r in rows if r[1] == 'Basraon, Avtar')[3], 140603)
        self.assertEqual(next(r for r in evidence(s)['componentRows'] if r['name'] == 'Mumblo, Ian')['salary'], 11682500)
        report = next(r for r in CONFIG['reports'] if r['employerSlug'] == 'city-of-richmond')
        part = copy.deepcopy(report['sections'][0]['parts'][0])
        part['readerCorrections']['independent-ocr'][0]['before'] = 'an unreviewed changed input'
        with self.assertRaisesRegex(ValueError, 'correction changed'):
            parser.extract(evidence(s)['parts'][0]['independentOcrWords'], parser.reader_layout(part, 'independent-ocr'))


if __name__ == '__main__':
    unittest.main()
