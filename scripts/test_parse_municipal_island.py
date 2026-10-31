#!/usr/bin/env python3
"""Offline regressions for source scope, money semantics and import provenance."""
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('island_parser',Path(__file__).with_name('parse_municipal_island.py'))
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)


class SalaryImportTests(unittest.TestCase):
    def test_zero_missing_and_negative_expenses_remain_distinct(self):
        text='''Council\nMayor, A  Mayor  15,000  100\nEmployees\nDoe, Jane  Analyst  80,000  0\nSmith, A  Technician  90,000  -\nJones, B  Manager  100,000  (12.50)\nEnd employees\nVendor, C  Contractor  200,000  500\n'''
        entry={'city':'fixture','category':'employee-remuneration','id':'fixture','pages':[1],
               'pageSlices':[{'page':1,'after':'Employees','before':'End employees'}]}
        rows=m.simple_rows([text],entry)
        self.assertEqual([r[0] for r in rows],['Doe, Jane','Smith, A','Jones, B'])
        self.assertEqual([r[3] for r in rows],[Decimal(0),None,Decimal('-12.50')])

    def test_saanich_wrapped_names_preserve_all_published_given_names(self):
        text='Jonnalagadda, Sai  Manager, Business Planning & Reporting  120,424  889\nSashank\nExempt\n'
        rows=m.simple_rows([text],{'id':'saanich-2025-test','city':'saanich','year':'2025','category':'employee-remuneration','pages':[1]})
        self.assertEqual(rows[0][0],'Jonnalagadda, Sai Sashank')
        pages=['']*40+['Blick McStravick,                  448\nAmanda  Park Planner Designer  88,878\n']
        row=m.simple_rows(pages,{'id':'saanich-2025-employees','city':'saanich','year':'2025','category':'employee-remuneration','pages':[41]})[0]
        self.assertEqual(row,['Blick McStravick, Amanda','Park Planner Designer',Decimal(88878),Decimal(448),41])

    def test_victoria_benefits_are_separate_and_pdf_values_win(self):
        csv_rows=[['Doe, J','Planner',Decimal(99000),Decimal(500),None,Decimal(3500)]]
        rows,components,differences=m.victoria_rows(['DOE, J  Planner  100,000.00  2,500.00  500.00'],csv_rows,{'pages':[1]})
        self.assertEqual(rows[0][2],Decimal(100000))
        self.assertEqual(components[0][2],Decimal(2500))
        self.assertEqual(differences[0]['csv'],[99000,3500,500])
        self.assertEqual(differences[0]['pdf'],[100000,2500,500])

    def test_changed_source_bytes_fail_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory,'source.pdf').write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError,'Unreviewed source bytes'):
                m.source_bytes(Path(directory),{'localFile':'source.pdf','sha256':hashlib.sha256(b'reviewed source').hexdigest()},False)

    def test_independent_check_rejects_money_assigned_to_wrong_name(self):
        class Page:
            def get_text(self,kind=None):
                if kind=='words':
                    return [(x,y,x+30,y+10,t) for y,name,pay,exp in [(100,'Doe, Jane','80,000','100'),(120,'Smith, A','90,000','200')]
                            for x,t in [(50,name),(220,'Analyst'),(430,pay),(510,exp)]]
                return 'Doe, Jane Analyst 80,000 100\nSmith, A Analyst 90,000 200'
        rows=[['Doe, Jane','Analyst',Decimal(90000),Decimal(200),1],['Smith, A','Analyst',Decimal(80000),Decimal(100),1]]
        with patch.object(m.fitz,'open',return_value=[Page()]):
            with self.assertRaisesRegex(ValueError,'Independent monetary cells disagree'):
                m.verify_positioned_simple('unused',rows,{'id':'swapped','city':'fixture','year':'2024','pages':[1],'nameX':200})

    def test_generated_collection_matches_pinned_review(self):
        manifest=json.loads((m.OUT/'sources.json').read_text())
        configs={e['id']:e for e in json.loads((m.OUT/'reviewed-inputs.json').read_text())['accepted']}
        self.assertEqual(set(configs),{s['id'] for s in manifest['sources']})
        for source in manifest['sources']:
            with self.subTest(source=source['id']):
                compressed=(m.OUT/source['file']).read_bytes(); payload=gzip.decompress(compressed);rows=json.loads(payload)
                self.assertEqual(hashlib.sha256(compressed).hexdigest(),source['dataSha256'])
                self.assertEqual(hashlib.sha256(payload).hexdigest(),source['normalizedSha256'])
                self.assertEqual(source['sha256'],configs[source['id']]['sha256'])
                self.assertEqual(len(rows),source['rowCount'])
                self.assertTrue(all(len(r)==6 and r[0]==source['employerSlug'] for r in rows))
                self.assertEqual(sum((Decimal(str(r[3])) for r in rows),Decimal(0)),Decimal(str(source['totalRemuneration'])))
                self.assertEqual(sum((Decimal(str(r[4])) for r in rows if r[4] is not None),Decimal(0)),Decimal(str(source['totalExpenses'])))
                self.assertEqual(source['periodStart'],source['year']+'-01-01')
                self.assertEqual(source['periodEnd'],source['year']+'-12-31')


if __name__=='__main__':unittest.main()
