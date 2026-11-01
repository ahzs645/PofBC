"""Regressions for source-specific OCR mistakes and acceptance controls."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from parse_municipal_ocr import OUT, amount, build, extract, validate_section


class MunicipalOCR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((OUT / 'reviewed-layouts.json').read_text())

    def report(self, text):
        return next(r for r in self.config['reports'] if text in r['id'])

    def evidence(self, r, s):
        return json.loads(gzip.decompress((OUT / 'evidence' / f"{r['id']}-p{s['page']:03}.json.gzip").read_bytes()))

    def test_every_accepted_ocr_file_reproduces_offline(self):
        build(self.config, Path('/unused'), check_data=True)

    def test_all_candidate_receipts_are_complete_and_hash_checked(self):
        register = json.loads((OUT / 'ocr-register.json').read_text())
        self.assertEqual(register['summary']['physicalPages'], 3518)
        self.assertEqual(register['summary']['processingErrors'], 0)
        for source in register['sources']:
            data = (OUT / source['evidenceFile']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['evidenceSha256'])
            staged = json.loads(gzip.decompress(data))
            self.assertEqual(staged['originalSha256'], source['sha256'])
            self.assertEqual(len(staged['pages']), source['pdfPages'])
            self.assertEqual(len({p['physicalPage'] for p in staged['pages']}), source['pdfPages'])

    def test_ocr_cannot_invent_thousands_from_a_misread_currency_sign(self):
        r = self.report('logan-lake')
        s = next(s for s in r['sections'] if s['category'] == 'employee-remuneration')
        e = self.evidence(r, s)
        rows, _ = validate_section(r, s, e)
        self.assertEqual(rows[11][4], 991.05)
        changed = copy.deepcopy(s)
        changed['corrections'] = []
        with self.assertRaisesRegex(ValueError, 'OCR passes differ'):
            validate_section(r, changed, e)

    def test_position_numerals_are_checked_even_when_money_is_unchanged(self):
        r = self.report('terrace-sofi-2017')
        s = next(s for s in r['sections'] if s['category'] == 'employee-remuneration')
        rows, _ = validate_section(r, s, self.evidence(r, s))
        self.assertEqual(rows[26][2], 'Environmental Technician II')
        stale = copy.deepcopy(s)
        stale['corrections'][0]['before'] = 'An unreviewed source spelling'
        with self.assertRaisesRegex(ValueError, 'Changed reviewed OCR correction'):
            validate_section(r, stale, self.evidence(r, s))

    def test_source_total_error_is_not_converted_into_remuneration(self):
        r = self.report('terrace-sofi-2022')
        s = next(s for s in r['sections'] if s['category'] == 'employee-remuneration')
        e = self.evidence(r, s)
        rows, controls = validate_section(r, s, e)
        self.assertEqual(round(sum(row[3] for row in rows) * 100), 533734767)
        self.assertEqual(next(c for c in controls if c['field'] == 'pay')['residual'], 0)
        self.assertEqual(next(c for c in controls if c['field'] == 'total')['residual'], 582015.69)
        changed = copy.deepcopy(s)
        changed['reviewedResidualsCents'] = {}
        with self.assertRaisesRegex(ValueError, 'unreviewed control difference'):
            validate_section(r, changed, e)

    def test_blank_expenses_remain_missing_and_printed_zero_remains_zero(self):
        r = self.report('salmo')
        s = next(s for s in r['sections'] if s['category'] == 'elected-officials')
        rows, _ = validate_section(r, s, self.evidence(r, s))
        self.assertIsNone(rows[2][4])
        r = self.report('telkwa')
        s = next(s for s in r['sections'] if s['category'] == 'elected-officials')
        rows, _ = validate_section(r, s, self.evidence(r, s))
        self.assertEqual(rows[-1][4], 0)

    def test_an_omitted_row_fails_before_controls_can_hide_it(self):
        r = self.report('terrace-sofi-2018')
        s = next(s for s in r['sections'] if s['category'] == 'employee-remuneration')
        changed = copy.deepcopy(s)
        changed['rowCount'] -= 1
        with self.assertRaisesRegex(ValueError, 'pay anchors'):
            extract(self.evidence(r, s)['words']['250-6'], changed, '250-6')

    def test_ambiguous_money_requires_review(self):
        for text in ['0,00', '1§3,029', '5991.05 extra']:
            with self.assertRaises(ValueError):
                amount(text)
        self.assertEqual(amount('5301.2'), 530120)


if __name__ == '__main__':
    unittest.main()
