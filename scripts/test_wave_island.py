"""Source-grounded regressions for island/coast municipal disclosures."""
from decimal import Decimal
import gzip
import json
from pathlib import Path
import unittest

from import_wave_island import amount, layout_table, total, visible_title_guard

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/municipal-wave-island'


def rows(slug,kind,year=2025):
    return json.loads(gzip.decompress((OUT/f'{slug}-{year}-{kind}.json.gzip').read_bytes()))


class IslandDisclosureTests(unittest.TestCase):
    def test_missing_numeric_zero_negative_and_cents_are_distinct(self):
        self.assertIsNone(amount('-'))
        self.assertIsNone(amount(''))
        self.assertEqual(amount('0'),0)
        self.assertEqual(amount('-1,727'),-1727)
        self.assertEqual(amount('23,890.04'),23890.04)
        with self.assertRaises(ValueError):amount('1,23')

    def test_wrapped_title_does_not_steal_numeric_continuation(self):
        text='2. Other Employees\nName  Position  Remuneration  Expenses\nAitken, Peter  Truck Driver/Labourer  75,192  1,670\nFarley, Tyler  Parks, Trails and Lands\n  Supervisor  82,004  643\nMason, Michelle  Chief Administrative Officer\n  162,904  8,355\nConsolidated total of other employees with\nremuneration and expenses of $75,000 or less  1,541,319  29,144\nTotal: Other Employees  3,618,748  78,109'
        # A preceding council header is part of this source's layout profile.
        text='Name  Position  Remuneration  Expenses\nBorecky, Neil  Councillor  16,010  1,475\n'+text
        parsed=layout_table(text,'village-of-cumberland','employees')
        self.assertEqual(parsed[-1],['Mason, Michelle','Chief Administrative Officer',162904,8355])
        self.assertEqual(parsed[1],['Farley, Tyler','Parks, Trails and Lands Supervisor',82004,643])
        self.assertEqual(len(parsed),3)

    def test_gibsons_total_includes_expenses_and_is_not_remuneration(self):
        text='Remuneration  Expenses  Total\nJaswal, Tamara  Bylaw Officer  74,572  3,252  77,824\nRemuneration:  Above $75,000  2,715,735  71,293  2,787,028'
        self.assertEqual(layout_table(text,'town-of-gibsons','employees'),[['Jaswal, Tamara','Bylaw Officer',74572,3252]])
        self.assertIn(['town-of-gibsons','Jaswal, Tamara','Bylaw Officer',74572,3252,10],rows('town-of-gibsons','employees'))

    def test_clipped_visible_title_guard_requires_exact_raw_context(self):
        row=['Wyka, R.','Manager of Financial Planning, Payroll & Business Performance',131252,2362]
        result=visible_title_guard('city-of-courtenay','employees',35,[row.copy()])
        self.assertTrue(result[0][1].endswith('Perform'))
        bad=row.copy();bad[2]+=1
        with self.assertRaises(AssertionError):visible_title_guard('city-of-courtenay','employees',35,[bad])

    def test_final_titles_do_not_include_headers_or_aggregates(self):
        expected={'city-of-courtenay':('Zervakis, L.','Communications & Marketing Supervisor'),'village-of-cumberland':('Williamson, Michael','Manager of Protective Services'),'town-of-gibsons':('Wright, Jackson','Water Distribution Operator'),'village-of-gold-river':('Roy, Michael','Chief Administrative Officer'),'village-of-tahsis':('Kyle Wilkinson','Fire Chief'),'district-of-ucluelet':('Zhou, Z.','Director of Corporate Services')}
        for slug,(name,title) in expected.items():
            self.assertEqual(rows(slug,'employees')[-1][1:3],[name,title])

    def test_courtenay_page_boundaries_preserve_distinct_titles(self):
        r=rows('city-of-courtenay','employees')
        expected={33:(('Adams, J.','Utilities Maintenance Operator'),('Kellinghusen, J.','Equipment Operator')),34:(('Kerr, C.','EVT / Fire Inspector'),('Tasker, C.','Operations Maintenance Worker')),35:(('Tazzioli, J.','Manager of Environmental Engineering'),('Zervakis, L.','Communications & Marketing Supervisor'))}
        for page,(first,last) in expected.items():
            p=[x for x in r if x[5]==page]
            self.assertEqual(p[0][1:3],list(first));self.assertEqual(p[-1][1:3],list(last))

    def test_tahsis_published_boundary_exceptions_and_missing_title_retained(self):
        r=rows('village-of-tahsis','employees')
        self.assertEqual([(x[1],x[3]) for x in r if x[3]<75000],[('Adia Mavrikos',73621),('Paige Sawyer',73633),('Kyle Wilkinson',72620)])
        self.assertIsNone(next(x[2] for x in r if x[1]=='John Manson'))

    def test_ucluelet_cent_residual_is_not_balanced_away(self):
        r=rows('district-of-ucluelet','employees')
        self.assertEqual(total(r,4),Decimal('58958.69'))
        self.assertEqual(sum(x[4] is None for x in r),4)

    def test_reviewed_ocr_preserves_explicit_zero_and_source_residual(self):
        r=rows('village-of-sayward','council',2024)
        self.assertEqual([(x[1],x[4]) for x in r if x[4]==0],[('Gilkin, Kohen',0),('Tinsley, Tom',0)])
        self.assertEqual(total(r,4),Decimal(16876))
        source=next(s for s in json.loads((OUT/'sources.json').read_text())['sources'] if s['id']=='wave-island-village-of-sayward-2024-council')
        self.assertEqual(source['validation']['expensesResidual'],-1)
        self.assertTrue(source['publicWarning'])

    def test_cohorts_and_periods_are_separate(self):
        s=json.loads((OUT/'sources.json').read_text())['sources']
        self.assertEqual(len(s),14);self.assertEqual(sum(x['rowCount'] for x in s),219)
        for source in s:
            self.assertEqual(source['periodType'],'calendar')
            self.assertIn(source['category'],['employee-remuneration','elected-officials'])
            self.assertEqual(source['year'],'2024' if source['employerSlug']=='village-of-sayward' else '2025')


if __name__=='__main__':unittest.main()
