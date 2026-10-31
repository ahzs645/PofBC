"""Offline regression checks against both retained PDF word extractions."""
import gzip
import hashlib
import json
import unittest

import parse_municipal_small as parser


class SmallMunicipalSchedules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((parser.OUT / 'reviewed-layouts.json').read_text())
        cls.sources = {s['id']: s for s in json.loads((parser.OUT / 'sources.json').read_text())['sources']}

    def test_blank_zero_and_nil_are_different(self):
        for blank in ['', '-', '–', '—']:
            self.assertIsNone(parser.money(blank))
        for zero in ['0', '0.00', 'nil', 'Nil']:
            self.assertEqual(parser.money(zero), 0)
        self.assertEqual(parser.money('1,234.56'), 123456)
        with self.assertRaises(ValueError):
            parser.money('1,234.56 8,000')

    def test_every_retained_reader_row_reproduces_the_published_data(self):
        seen = 0
        for report in self.config['reports']:
            for section in report['sections']:
                source_id = f"municipal-small-{report['employerSlug']}-{report['year']}-{section['category']}"
                source = self.sources[source_id]
                evidence = json.loads(gzip.decompress((parser.OUT / source['validation']['evidenceFile']).read_bytes()))
                self.assertEqual(evidence['originalPdfSha256'], source['sha256'])
                data = (parser.OUT / source['file']).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), source['dataSha256'])
                actual = json.loads(gzip.decompress(data))
                for reader in ['mupdfWords', 'popplerWords']:
                    rows = parser.extract(evidence[reader], section)
                    expected = [[report['employerSlug'], r['name'], r.get('position'), parser.dollars(r['pay']), parser.dollars(r.get('expenses')), section['page']] for r in rows]
                    self.assertEqual(expected, actual, source_id + ' ' + reader)
                    for field, printed in section['controlsCents'].items():
                        self.assertEqual(parser.total(rows, field) - printed, section.get('reviewedResidualsCents', {}).get(field, 0), source_id + ' ' + field)
                seen += len(actual)
        self.assertEqual(seen, 195)

    def test_mackenzie_total_never_becomes_remuneration(self):
        source = self.sources['municipal-small-district-of-mackenzie-2025-employee-remuneration']
        evidence = json.loads(gzip.decompress((parser.OUT / source['validation']['evidenceFile']).read_bytes()))
        for row in evidence['rows']:
            self.assertEqual(row['pay'], row['base'] + row['other'])
        self.assertEqual(source['totalRemuneration'], 3361805)
        self.assertEqual(source['totalExpenses'], 70221)

    def test_mackenzie_wrapped_title_belongs_to_the_following_employee(self):
        source = self.sources['municipal-small-district-of-mackenzie-2025-employee-remuneration']
        data = json.loads(gzip.decompress((parser.OUT / source['file']).read_bytes()))
        positions = {row[1]: row[2] for row in data}
        self.assertEqual(positions['Stedeford, Ron'], 'LH Equipment Operator')
        self.assertEqual(positions['Taylor, Micaiah'], 'Deputy Emergency Program & Firesmart Coordinator')

    def test_combined_benefits_are_not_published_as_expenses(self):
        source = self.sources['municipal-small-village-of-valemount-2024-employee-remuneration']
        data = json.loads(gzip.decompress((parser.OUT / source['file']).read_bytes()))
        self.assertTrue(all(row[4] is None for row in data))
        evidence = json.loads(gzip.decompress((parser.OUT / source['validation']['evidenceFile']).read_bytes()))
        self.assertTrue(any(row.get('combinedExpensesBenefits') for row in evidence['rows']))

    def test_source_row_loss_fails_instead_of_silently_truncating(self):
        report = next(r for r in self.config['reports'] if r['employerSlug'] == 'district-of-peachland')
        section = next(s for s in report['sections'] if s['category'] == 'employee-remuneration')
        source = self.sources['municipal-small-district-of-peachland-2025-employee-remuneration']
        evidence = json.loads(gzip.decompress((parser.OUT / source['validation']['evidenceFile']).read_bytes()))
        pay_col = section['columns']['pay']
        words = evidence['mupdfWords']
        anchor = next(w for w in words if section['y'][0] <= (w[1] + w[3]) / 2 <= section['y'][1] and pay_col[0] <= (w[0] + w[2]) / 2 < pay_col[1] and parser.MONEY.fullmatch(w[4]))
        with self.assertRaisesRegex(ValueError, 'pay cells'):
            parser.extract([w for w in words if w is not anchor], section)


if __name__ == '__main__':
    unittest.main()
