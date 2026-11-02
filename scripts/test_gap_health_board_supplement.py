"""Offline committed-original regressions for the19-source board supplement."""
import copy
import unittest

import gap_health_board_supplement as g


class BoardSupplementSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs=g.read(g.AREA/'source-specs.json')
        cls.bykey={s['sourceKey']:s for s in cls.specs}

    def source(self,key):
        spec=self.bykey[key]
        return spec,g.read(g.ROOT/spec['nativeEvidence']['path'])

    def test_complete_paired_original_scopes(self):
        counts=[]
        for spec in self.specs:
            proof=g.read(g.ROOT/spec['nativeEvidence']['path'])
            rows,_,second,_,controls=g.paired(spec,proof)
            self.assertEqual(rows,second)
            self.assertEqual(controls['pymupdf'],controls['poppler'])
            counts.append((len(rows),sum(r[3]is not None for r in rows)))
        self.assertEqual((len(counts),sum(x[0]for x in counts),sum(x[1]for x in counts)),(19,194,186))

    def test_unknown_pay_preserves_known_expenses_without_invented_zero(self):
        amounts=[]
        for spec in self.specs:
            rows,*_=g.paired(spec,g.read(g.ROOT/spec['nativeEvidence']['path']))
            amounts.extend(r[4]for r in rows if r[3]is None)
        self.assertEqual(len(amounts),8)
        self.assertEqual(g.exact_sum(amounts),1801.71)
        self.assertEqual(sum(v is None for v in amounts),5)

    def test_blank_expenses_remain_missing_in_spite_of_inclusive_total(self):
        spec,proof=self.source('vancouver-coastal-health-2023-24')
        rows,details,*_=g.paired(spec,proof)
        r=next(x for x in rows if x[1]=='Baydala, Allan')
        self.assertIsNone(r[4]);self.assertEqual(r[3],6625)
        d=next(x for x in details if x['row'][1]==r[1])
        self.assertEqual(d['expenseInclusivePrintedRowTotal'],6625)
        self.assertEqual(d['rawCells']['expenses'],'')

    def test_visible_expense_control_residuals_are_not_balanced(self):
        for key,delta in [('vancouver-coastal-health-2023-24',2),('vancouver-coastal-health-2018-19',1)]:
            spec,proof=self.source(key);rows,*_=g.paired(spec,proof)
            self.assertEqual(g.exact_difference(g.exact_sum(r[4]for r in rows),spec['printedControlCells']['expenses']['value']),delta)
        spec,proof=self.source('vancouver-coastal-health-2018-19');rows,*_=g.paired(spec,proof)
        imported=[r for r in rows if r[3]is not None]
        self.assertEqual(g.exact_sum(r[4]for r in imported),6041)
        self.assertEqual(g.exact_sum(r[4]for r in rows),6235)

    def test_repeated_pay_observations_and_literal_role_separation(self):
        spec,proof=self.source('fraser-health-2009-10')
        raw=g.primary(proof['pymupdf'][spec['page']-1],spec)
        rows,_=g.interpret([raw[0],raw[0]],spec)
        self.assertEqual(len(rows),2);self.assertEqual(rows[0],rows[1])
        self.assertEqual(rows[0][1:3],['BAREFOOT, GORDON','CHAIR'])

    def test_wrong_original_or_internal_period_is_rejected(self):
        spec,proof=self.source('fraser-health-2009-10')
        changed=copy.deepcopy(proof);changed['sourceSha256']='0'*64
        with self.assertRaises(ValueError):g.paired(spec,changed)
        changed_spec=copy.deepcopy(spec);changed_spec['year']='2008/09'
        with self.assertRaises(AssertionError):g.paired(changed_spec,proof)

    def test_independent_monetary_cell_change_is_rejected(self):
        spec,proof=self.source('fraser-health-2009-10');changed=copy.deepcopy(proof)
        words=changed['poppler'][spec['page']-1]
        first=next(w for w in words if w[4]=='31,250');first[4]='31,251'
        with self.assertRaises(ValueError):g.paired(spec,changed)

    def test_missing_named_row_is_rejected(self):
        spec,proof=self.source('fraser-health-2009-10');changed=copy.deepcopy(proof)
        words=changed['poppler'][spec['page']-1]
        changed['poppler'][spec['page']-1]=[w for w in words if not 180<((w[1]+w[3])/2)<200]
        with self.assertRaises(ValueError):g.paired(spec,changed)

    def test_cents_and_explicit_zero_differ_from_missing(self):
        self.assertEqual(g.exact_sum([376.25,72,5063]),5511.25)
        self.assertEqual(g.numeric('0'),0);self.assertIsNone(g.numeric('-'))
        self.assertIsNone(g.numeric(''))
        self.assertEqual(g.numeric('1,589.71'),1589.71)

    def test_check_rejects_mutating_originals_mode(self):
        with self.assertRaises(ValueError):g.run(check=True,originals=True)


if __name__=='__main__':unittest.main()
