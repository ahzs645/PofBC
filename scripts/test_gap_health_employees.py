"""Real-source and mutation regressions for the finite health-history recovery."""
import gzip,json,pathlib,unittest
import fitz
import gap_health_employees_native as native
from gap_health_employees_clip_audit import remove_clip_operators,declipped_document,compare

ROOT=pathlib.Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_employees'

class LiteralAmounts(unittest.TestCase):
    def test_dash_blank_and_numeric_zero_have_different_source_evidence(self):
        self.assertIsNone(native.amount('-'));self.assertIsNone(native.amount(''))
        self.assertEqual(native.amount('0'),0);self.assertEqual(native.amount('$ 0.00'),0)

    def test_separate_negative_sign_and_cents_remain_literal(self):
        self.assertEqual(native.amount('‐ 1,998'),-1998)
        self.assertEqual(native.amount('(1,034.50)'),-1034.5)
        self.assertEqual(native.amount('88,941'),88941)

    def test_missing_or_misencoded_numeric_character_is_not_inferred(self):
        for value in ['1ϯ,ϭϭϳ','O','None','12,34','1,000 and 2']:
            with self.assertRaises(ValueError):native.amount(value)

    def test_real_printed_negative_expense_line_stays_negative(self):
        m=native.ROW.fullmatch('Balisky,Charla                     98,892 -       1,998')
        self.assertIsNotNone(m);self.assertEqual(native.amount(m['expense']),-1998)

    def test_board_table_is_excluded_from_employee_scope(self):
        text='FRASER HEALTH AUTHORITY Schedule of Board Member Remuneration and Expenses'
        self.assertFalse(native.selected_page('fraser-health-2006-07',3,text))

    def test_catalogue_cover_is_not_a_salary_page(self):
        self.assertFalse(native.selected_page('vancouver-coastal-health-2024-25',1,'Employee Remuneration Expenses'))

    def test_partial_source_initials_are_flagged_without_identity_expansion(self):
        m=native.ROW.fullmatch('M.S.                       88,941                   0')
        self.assertIsNotNone(m);self.assertEqual(m['name'],'M.S.')
        self.assertEqual(native.amount(m['pay']),88941);self.assertEqual(native.amount(m['expense']),0)

class SafeClippingAudit(unittest.TestCase):
    def test_only_pdf_operators_change_not_strings_comments_hex_or_names(self):
        raw=b'q 0 0 10 10 re W n (W W* \\( W \\)) Tj /W /W#2A % W W*\n<57572a> Tj W* n Q'
        changed,count=remove_clip_operators(raw)
        self.assertEqual(count,2)
        self.assertIn(b'(W W* \\( W \\))',changed)
        self.assertIn(b'/W /W#2A % W W*\n<57572a>',changed)
        self.assertEqual(changed.replace(b'n n (',b'W n (',1).replace(b' n  n Q',b' W* n Q'),raw)

    def test_dictionaries_are_tokenized_without_becoming_hexadecimal_strings(self):
        raw=b'/P <</MCID 26 /Lang (x-none)>> BDC q 0 0 10 10 re W n Q EMC'
        changed,count=remove_clip_operators(raw)
        self.assertEqual(count,1);self.assertIn(b'<</MCID 26 /Lang (x-none)>>',changed)

    def test_split_stream_fragments_cannot_be_silently_accepted(self):
        with self.assertRaises(ValueError):remove_clip_operators(b'<0041')
        changed,count=remove_clip_operators(b'<0041'+b'0042> Tj W n')
        self.assertEqual(count,1);self.assertTrue(changed.startswith(b'<00410042>'))

    def test_inline_image_bytes_fail_closed(self):
        with self.assertRaises(ValueError):remove_clip_operators(b'BI /W 1 /H 1 ID abcW n EI')

    def test_actual_clipped_native_name_is_detected_by_original_pixels(self):
        doc=fitz.open();page=doc.new_page(width=220,height=100)
        page.insert_text((20,50),'BRIANNA TEACHER',fontsize=16)
        ref=page.get_contents()[0];body=doc.xref_stream(ref)
        doc.update_stream(ref,b'q 0 0 89 100 re W n\n'+body+b'\nQ')
        raw=doc.tobytes();original=fitz.open(stream=raw,filetype='pdf')
        derived,changes,merged=declipped_document(raw,[1])
        a=original[0].get_pixmap(alpha=False);m=merged[0].get_pixmap(alpha=False);b=derived[0].get_pixmap(alpha=False)
        self.assertEqual(a.samples,m.samples);self.assertTrue(changes)
        total,bounds,regions=compare(a,b,[[0,0,a.width,a.height]])
        self.assertGreater(total,0);self.assertIsNotNone(bounds);self.assertEqual(total,regions[0])
        #The diagnostic exposes hidden letters only after removing clipping;
        #the unchanged original pixels remain the acceptance evidence.
        self.assertIn('TEACHER',derived[0].get_text())

class ActualSourceContracts(unittest.TestCase):
    def test_complete_exact_serial_catalogue_contains_the_named_missing_periods(self):
        c=json.loads((AREA/'exact-serial-catalogue.json').read_bytes())
        targets={('Northern Health','2017/2018'),('Northern Health','2018/2019'),('Northern Health','2019/2020'),('Interior Health','2013/2014'),('Fraser Health','2012/2013')}
        for issuer,period in targets:
            self.assertTrue(any(x['issuer']==issuer and period in ' '.join(x['serialIssue']) and 'Remuneration' in ' '.join(x['serialIssue']) for x in c),(issuer,period))

    def test_process_isolated_current_reader_selection_covers_all65_originals(self):
        s=json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes());e=json.loads((AREA/'native-reader-evidence-index-v2.json').read_bytes())
        self.assertEqual(len(s),65);self.assertEqual(len(e),65)
        self.assertEqual({x['sourceSha256'] for x in s},{x['sourceSha256'] for x in e})
        self.assertTrue(all('isolated worker process' in x['execution'] for x in e))

    def test_real_two_engine_vch_cents_schedule_agrees_without_rounding(self):
        c=json.loads((AREA/'native-primary-candidate-index.json').read_bytes());x=next(x for x in c if x['key']=='vancouver-coastal-health-2012-13')
        a=native.load(ROOT/x['file']);b=native.load(ROOT/x['secondaryFile'])
        self.assertEqual([r['row'] for r in a['rows']],[r['row'] for r in b['rows']]);self.assertEqual(len(a['rows']),3563)
        self.assertEqual(x['remuneration'],'330891352.08');self.assertEqual(x['expenses'],'3167132.37')

    def test_real_partial_name_does_not_become_an_invented_full_name(self):
        packet=json.loads((AREA/'source-review-packets/reader-disagreements-001/packet.json').read_bytes())
        self.assertTrue(all(x['candidateValuesWithheld'] for x in packet['targets']))
        self.assertEqual(len(packet['targets']),88)


class ReviewedAdoptionContracts(unittest.TestCase):
    def test_name_spacing_does_not_erase_internal_word_boundaries(self):
        self.assertNotEqual(native.nameclean('DENTON, JENNIFER A'),native.nameclean('DENTON,JENNIFERA'))
        self.assertEqual(native.nameclean('DENTON,  JENNIFER A'),native.nameclean('DENTON,JENNIFER A'))

    def test_exact_seven_clipped_names_keep_original_payment_and_expense(self):
        import gap_health_employees_verification as verify
        adoptions=verify.null_adoptions()
        manifest=json.loads((ROOT/'research/salaries/gap-fill-health-employees/sources-candidate.json').read_bytes())
        nullrows=0
        for source in manifest['sources']:
            rows=native.load(ROOT/'research/salaries/gap-fill-health-employees'/source['file'])
            proof=native.load(ROOT/'research/salaries/gap-fill-health-employees'/source['provenanceFile'])['rows']
            for row,p in zip(rows,proof):
                if row[1] is not None:continue
                nullrows+=1
                matches=[a for a in adoptions.values() if a['sourceSha256']==source['sha256'] and a['physicalPage']==row[5] and a['sourceRowOnPage']==p['initialPrimarySourceRowOnPage']]
                self.assertEqual(len(matches),1)
                self.assertEqual([row[3],row[4]],[matches[0]['remuneration'],matches[0]['expenses']])
                self.assertTrue(p['sourceNameWasDisclosedButClipped'])
                self.assertEqual(p['visibleSourceNameFragment'],matches[0]['nameLiteral'])
        self.assertEqual(nullrows,7)

    def test_unapproved_peer_field_supersession_fails_closed(self):
        import gap_health_employees_verification as verify
        from unittest import mock
        real=verify.pinned
        def changed(path,digest):
            value=real(path,digest)
            if path==verify.CLIP_SELECTION:value['fieldSupersessions'].append({'id':'health-clip-001-001','field':'remuneration','value':0})
            return value
        with mock.patch.object(verify,'pinned',changed):
            with self.assertRaises(AssertionError):verify.clip_readings()

    def test_complete_catalogue_audit_includes_salary_aliases_and_actual_typo(self):
        audit=json.loads((AREA/'full606-catalogue-label-scope-audit.json').read_bytes())
        self.assertEqual(len({r['itemUuid'] for r in audit['items']}),606)
        uncovered=audit['finiteLocatedUncoveredSalaryOrContractOriginals']
        self.assertEqual(len(uncovered),19)
        self.assertTrue(any('Remeneration' in r['label'] and r['catalogueYearDiscoveryOnly']=='2014/15' for r in uncovered))
        self.assertEqual(sum(r['employerSlug']=='provincial-health-services-authority' for r in uncovered),9)

if __name__=='__main__':unittest.main()
