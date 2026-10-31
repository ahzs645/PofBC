"""Regression tests for BCIT source boundaries and observed extraction failures."""
import copy
import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location('bcit_importer', Path(__file__).with_name('import-bcit-salaries.py'))
bcit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bcit)


def fixture():
    heading = 'FOR THE YEAR ENDED MARCH 31, 2025'
    pages = [
        f'BRITISH COLUMBIA INSTITUTE OF TECHNOLOGY\n{heading}',
        f'STATEMENT OF EMPLOYEES’ REMUNERATION AND EXPENSES\n{heading}\nEXHIBIT B',
        '\n'.join([
            'Page6                                            EXHIBIT B',
            'Name                            Remuneration    Expenses',
            'Alpha, Alice                       100,000       -',
            'Cohen-Fernandez                     90,000        (443)',
            'Beta, Bob                          80,000        443',
            'Gamma, Gail                        75,000        0',
            'ZZ --- Salaries under $75000        50,000        -',
            '                                   395,000       0',
            '*May include overtime, allowances and part-time salary',
        ]),
        f'STATEMENT OF BOARD OF GOVERNORS, REMUNERATION AND EXPENSES\n{heading}',
        f'STATEMENT OF FINANCIAL INFORMATION APPROVAL\n{heading}',
    ]
    spec = {
        'yearEnd': 2025, 'pdfPageCount': 5, 'pages': [3], 'printedPages': [6],
        'pageCounts': [4], 'rowCount': 4, 'totalRemuneration': 345000,
        'totalDisclosedExpenses': 0, 'printedTotalRemuneration': 395000,
        'printedTotalExpenses': 0, 'underThresholdRemuneration': 50000,
        'namesWithoutComma': 1, 'negativeExpenseRows': 1,
    }
    return '\f'.join(pages) + '\f', spec


class BCITImportTests(unittest.TestCase):
    def test_preserves_names_missing_zero_and_negative_expenses(self):
        text, spec = fixture()
        rows, cells, checks = bcit.parse(text, spec)
        self.assertEqual([row[4] for row in rows], [None, -443, 443, 0])
        self.assertEqual(rows[1][1], 'Cohen-Fernandez')
        self.assertTrue(all(row[5] == 3 for row in rows))
        self.assertEqual(checks['remunerationResidual'], 0)
        self.assertEqual(checks['expensesResidual'], 0)
        self.assertEqual(len(rows), 4)
        self.assertEqual(cells[3][-2:], [['ZZ --- Salaries under $75000', 50000, None], ['', 395000, 0]])

    def test_rejects_wrong_employee_period_despite_correct_cover(self):
        text, spec = fixture()
        text = text.replace('STATEMENT OF EMPLOYEES’ REMUNERATION AND EXPENSES\nFOR THE YEAR ENDED MARCH 31, 2025',
                            'STATEMENT OF EMPLOYEES’ REMUNERATION AND EXPENSES\nFOR THE YEAR ENDED MARCH 31, 2024')
        with self.assertRaisesRegex(ValueError, 'fiscal year mismatch'):
            bcit.parse(text, spec)

    def test_rejects_silently_dropped_employee(self):
        text, spec = fixture()
        text = text.replace('Cohen-Fernandez                     90,000        (443)\n', '')
        with self.assertRaisesRegex(ValueError, 'sequence/counts'):
            bcit.parse(text, spec)

    def test_rejects_missing_page_header(self):
        text, spec = fixture()
        with self.assertRaisesRegex(ValueError, 'sequence/counts'):
            bcit.parse(text.replace('EXHIBIT B', 'EXHIBIT C'), spec)

    def test_rejects_repeated_summary(self):
        text, spec = fixture()
        text = text.replace('                                   395,000       0',
                            '                                   395,000       0\n                                   395,000       0')
        with self.assertRaisesRegex(ValueError, 'repeated or changed printed totals'):
            bcit.parse(text, spec)

    def test_rejects_unparsed_money(self):
        text, spec = fixture()
        with self.assertRaisesRegex(ValueError, 'Unparsed employee-schedule line'):
            bcit.parse(text.replace('100,000       -', '100,000.25       -'), spec)

    def test_rejects_below_threshold_employee(self):
        text, spec = fixture()
        with self.assertRaisesRegex(ValueError, 'Invalid employee row'):
            bcit.parse(text.replace('75,000        0', '74,999        0'), spec)

    def test_rejects_unexplained_large_subtotal_residual(self):
        text, spec = fixture()
        spec = copy.deepcopy(spec)
        spec['printedTotalRemuneration'] = 396000
        with self.assertRaisesRegex(ValueError, 'rounding bound'):
            bcit.parse(text.replace('395,000', '396,000'), spec)

    def test_joins_observed_split_numeric_glyph_but_not_separate_columns(self):
        words = [
            {'text': '7', 'x0': 379.56, 'x1': 385.157},
            {'text': '3,371,238', 'x0': 385.201, 'x1': 430.168},
            {'text': '123', 'x0': 479.76, 'x1': 505.04},
        ]
        result = bcit.join_split_amounts(words)
        self.assertEqual([word['text'] for word in result], ['73,371,238', '123'])
        self.assertEqual(words[0]['text'], '7')


if __name__ == '__main__':
    unittest.main()
