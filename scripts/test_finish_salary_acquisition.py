import gzip,json,pathlib,sys,unittest,subprocess
import fitz
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import finish_salary_acquisition_native as native
import finish_salary_acquisition_poppler as poppler
from finish_salary_acquisition_fetch import classification
ROOT=pathlib.Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/acquisition'
class AcquisitionTests(unittest.TestCase):
 def test_http_html_and_truncated_pdf_are_not_originals(self):
  self.assertFalse(classification(200,{},b'<html>denied</html>')['candidateOriginal'])
  self.assertFalse(classification(403,{},b'%PDF-1.7\n%%EOF')['candidateOriginal'])
  self.assertFalse(classification(200,{'Warning':'299 archive "response truncated"','X-Archive-Orig-Content-Length':'3739511'},b'%PDF-1.7\n%%EOF')['candidateOriginal'])
  self.assertFalse(classification(200,{'Content-Length':'1000'},b'%PDF-1.7\n%%EOF')['candidateOriginal'])
  self.assertTrue(classification(200,{},b'%PDF-1.7\n%%EOF')['candidateOriginal'])
 def test_literal_null_zero_negative_and_double_hyphen(self):
  for fn in [lambda s:native.money(s)['value'],poppler.literal_amount]:
   self.assertIsNone(fn('--'));self.assertIsNone(fn('‐'));self.assertEqual(fn('0'),0);self.assertEqual(fn('-590'),-590);self.assertEqual(fn('(1,234)'),-1234)
   with self.assertRaises(ValueError):fn('')
  self.assertEqual(native.money('--')['kind'],'explicit-double-hyphen-marker')
 def test_unpainted_white_native_text_cannot_be_accepted(self):
  doc=fitz.open();page=doc.new_page();page.insert_text((50,50),'Visible salary');page.insert_text((50,80),'Hidden job title',color=(1,1,1))
  with self.assertRaises(ValueError):native.traces(doc,[1])
 def test_full_source_readers_agree_all_fields_and_multiplicity(self):
  for key in ['providence-2023-24','vch-2020-21']:
   a=json.loads(gzip.decompress((AREA/(key+'-mupdf-raw.json.gzip')).read_bytes()));b=json.loads(gzip.decompress((AREA/(key+'-poppler-raw.json.gzip')).read_bytes()))
   for field in ['employeeRecords','boardRecordsAllLiteral']:self.assertEqual([r['row'] for r in a[field]],[r['row'] for r in b[field]])
 def test_five_board_pay_dashes_remain_research_only(self):
  a=json.loads(gzip.decompress((AREA/'providence-2023-24-mupdf-raw.json.gzip').read_bytes()));raw=a['boardRecordsAllLiteral'];self.assertEqual(len(raw),15);held=[r for r in raw if r['row'][3] is None];self.assertEqual(len(held),5);self.assertTrue(all(r['remunerationCell']['kind']=='explicit-dash' for r in held))
  data=json.loads(gzip.decompress((ROOT/'research/salaries/queue-completion-acquisition/providence-2023-24-board-numeric-pay.json.gzip').read_bytes()));self.assertEqual(len(data),10);self.assertTrue(all(type(r[3]) in [int,float] for r in data));self.assertEqual(sum(r[4] or 0 for r in data),5455)
 def test_real_double_hyphen_is_null_and_duplicate_names_preserved(self):
  a=json.loads(gzip.decompress((AREA/'providence-2023-24-mupdf-raw.json.gzip').read_bytes()));rows=a['employeeRecords'];special=[r for r in rows if r['expenseCell']['kind']=='explicit-double-hyphen-marker'];self.assertEqual(len(special),1);self.assertEqual(special[0]['row'][1],'Mckinnon,Patricia');self.assertIsNone(special[0]['row'][4]);self.assertEqual(sum(r['row'][1]=='Le,Jessica' for r in rows),2);self.assertEqual(sum(r['row'][1]=='Zhang,Wen' for r in rows),2)
 def test_vch_literal_control_residual_is_not_balanced(self):
  rows=json.loads(gzip.decompress((ROOT/'research/salaries/queue-completion-acquisition/vch-2020-21-employees.json.gzip').read_bytes()));self.assertEqual(len(rows),7740);self.assertEqual(sum(r[3] for r in rows)-771927987,39);self.assertEqual(sum(r[4] or 0 for r in rows)-3773890,22)
 def test_builder_consumes_visible_qualifications_and_retention_guards(self):
  js="""import fs from 'node:fs';import {compiledPartitionsToRetain} from './scripts/lib/salary-data.mjs';const a=JSON.parse(fs.readFileSync('research/salaries/queue-completion-acquisition/sources.json','utf8')).sources;const sources=Object.fromEntries(a.map(s=>[s.id,s]));const rows=a.map(s=>({sourceId:s.id,slug:s.employerSlug,year:s.year}));if(compiledPartitionsToRetain(rows,sources).size!==2)throw Error('Two employer/period partitions expected');for(const s of a){if(!s.publicWarning||s.sourceWarning||s.completeEmployeeSchedule!==s.validation.completeEmployeeSchedule)throw Error('Incomplete consumed warning/guard schema')}sources[a[0].id].publicWarning='';let rejected=false;try{compiledPartitionsToRetain(rows,sources)}catch{rejected=true}if(!rejected)throw Error('Missing public warning should fail');console.log('pass');"""
  result=subprocess.run(['node','--input-type=module','-e',js],cwd=ROOT,text=True,capture_output=True,check=True);self.assertEqual(result.stdout.strip(),'pass')
 def test_frozen_outbox_never_submitted_and_sender_fields_required(self):
  a=json.loads((AREA/'outbox/outbox.json').read_text());self.assertEqual(a['requestCount'],4);self.assertFalse(a['explicitSendingAuthorizationReceived']);self.assertEqual(a['contactsSent'],0);self.assertEqual(a['formsSubmitted'],0);self.assertEqual(a['feesAuthorizedOrPaid'],0)
  for r in a['items']:self.assertFalse(r['sent']);self.assertFalse(r['submitted']);self.assertFalse(r['noFeeRoute']['feesAuthorized']);self.assertFalse(r['noFeeRoute']['formalFoiApplicationAuthorized'])
  sd10=next(x for x in a['items'] if x['employerSlug']=='school-district-10');self.assertIsNone(sd10['formFields']['Email']);self.assertIsNone(sd10['formFields']['Name'])
if __name__=='__main__':unittest.main()
