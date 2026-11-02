"""Pin independent complete source transcription and candidate comparison, retaining first differences."""
from pathlib import Path
import json,gzip,hashlib,re
from decimal import Decimal
ROOT=Path('/workspace/PofBC');A=ROOT/'research/salaries/gap-fill-2026-11-02/school_native/reviews';C=ROOT/'research/salaries/gap-fill-municipal'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
first=A/'municipal-earliest-12-first-source-transcript.json';assert sha(first)=='0ef0222577ead359215a43d22ef04f4ca60463ed8443485a14964fc368f09cf3'
book=json.loads(first.read_text());initial=json.loads((A/'municipal-earliest-12-initial-comparison.json').read_text());sources={s['id']:s for s in json.loads((C/'sources.json').read_text())['sources']}
def n(x):
 if x is None or x=='-':return None
 if str(x).lower()=='nil':return Decimal(0)
 return Decimal(str(x).replace(',',''))
def serial(x):
 if isinstance(x,Decimal):return str(x)
 raise TypeError(type(x))
controls=[];pins=[];observations=[]
for p in book['cohorts']:
 s=sources[p['sourceId']];e=json.loads(gzip.decompress((C/s['provenanceFile']).read_bytes()));lit=e['literalSection']; pc=p['sourceControls'];expected={}
 if 'printedNamedTotals'in pc:expected.update(remunerationComponent=pc['printedNamedTotals'][0],expenses=pc['printedNamedTotals'][1])
 if 'printedAllEmployeesTotals'in pc:expected['allEmployees']={'remunerationComponent':pc['printedAllEmployeesTotals'][0],'expenses':pc['printedAllEmployeesTotals'][1]}
 if 'printedOtherEmployees'in pc:expected['unnamedEmployees']={'remunerationComponent':pc['printedOtherEmployees'][0],'expenses':pc['printedOtherEmployees'][1]}
 if 'printedOtherEmployeesExpenseInclusiveTotal'in pc:expected['unnamedEmployees']['expenseInclusiveTotal']=pc['printedOtherEmployeesExpenseInclusiveTotal']
 if 'printedAllEmployeesExpenseInclusiveTotal'in pc:expected['allEmployees']['expenseInclusiveTotal']=pc['printedAllEmployeesExpenseInclusiveTotal']
 for pk,ck in [('printedTaxableBenefitsTotal','taxableBenefits'),('printedExpenseInclusiveTotal','expenseInclusiveTotal'),('printedNamedBenefitsTotal','taxableBenefits'),('printedNamedExpenseInclusiveTotal','expenseInclusiveTotal')]:
  if pk in pc:expected[ck]=pc[pk]
 if p['sourceId']=='gap-fill-municipal-city-of-rossland-2010-employee-remuneration':expected['unnamedEmployees']['expenseInclusiveTotal']='1417863.64'
 # Last Rossland2016 salary page supplies named controls plus all/unnamed aggregates; selected evidence retains named controls.
 additional={}
 if p['sourceId']=='gap-fill-municipal-city-of-rossland-2016-employee-remuneration':
  additional={k:expected.pop(k) for k in ['allEmployees','unnamedEmployees']}
  additional['sourceOnlyOtherBenefits']=pc['printedOtherBenefits'];additional['sourceOnlyOtherExpenseInclusiveTotal']=pc['printedOtherExpenseInclusiveTotal'];additional['sourceOnlyAllBenefitsTotal']=pc['printedAllBenefitsTotal']
 diffs=[]
 def compare(a,b,path=''):
  for k,v in a.items():
   if isinstance(v,dict):compare(v,b.get(k,{}),path+k+'.')
   elif n(v)!=n(b.get(k)):diffs.append({'field':path+k,'independentPrinted':v,'candidate':b.get(k)})
 compare(expected,lit['printedControls']);assert not diffs,(s['id'],diffs)
 rowmath={}
 for field in ['remunerationComponent','taxableBenefits','expenses','expenseInclusiveTotal']:
  if not any(field in r for r in lit['rows']):continue
  values=[n(r.get(field)) for r in lit['rows']];known=sum((x for x in values if x is not None),Decimal(0));printed=lit['printedControls'].get(field);basis='printed named total' if printed is not None else None
  if printed is None and 'allEmployees'in lit['printedControls']:
   ap=lit['printedControls']['allEmployees'].get(field);up=lit['printedControls']['unnamedEmployees'].get(field)
   if n(ap)is not None and n(up)is not None:printed=n(ap)-n(up);basis='printed all-employee less printed unnamed aggregate'
  rowmath[field]={'knownRowSum':known,'unknownRows':sum(v is None for v in values),'printedNamedControlOrDerivation':printed,'knownMinusControl':known-n(printed) if printed is not None else None,'controlBasis':basis,'unknownCellsNotImputedZero':True}
 controls.append({'sourceId':s['id'],'allPeerPrintedControlsComparedExact':True,'math':rowmath,'additionalIndependentPrintedControlsNotClaimedInCandidateNamedControl':additional})
 pins.append({'sourceId':s['id'],'sourceSha256':s['sha256'],'file':str((C/s['file']).relative_to(ROOT)),'dataSha256':sha(C/s['file']),'provenanceFile':str((C/s['provenanceFile']).relative_to(ROOT)),'provenanceSha256':sha(C/s['provenanceFile']),'rowCount':s['rowCount']})
 observations.extend(p['sourceNotes'])
result={'reviewer':'/root/gap_school_native','reviewProtocol':'Complete actual-original image-first personal transcription of every named row of all12assigned originals before any candidate literals or normalized payloads were opened. Every149name/title/pay/expense and every separately printed benefit/expense-inclusive total compared. All22normalized cohorts match exactly with explicitly declared footnote-marker removal and2016employee benefit addition. Not merely an OCR or control-total check.','completeOriginalCount':12,'completeCohortCount':22,'completeRowCount':149,'allNormalizedRowsExact':initial['normalizedMismatches']==0,'firstTranscript':str(first.relative_to(ROOT)),'firstTranscriptSha256':sha(first),'firstTranscriptPreserved':True,'originalReplayFile':str((A/'municipal-earliest-12-original-replay.json').relative_to(ROOT)),'originalReplaySha256':sha(A/'municipal-earliest-12-original-replay.json'),'initialComparisonFile':str((A/'municipal-earliest-12-initial-comparison.json').relative_to(ROOT)),'initialComparisonSha256':sha(A/'municipal-earliest-12-initial-comparison.json'),'firstDifferencesAndResolutions':[{'type':'only whitespace before footnote marker','sourceId':'gap-fill-municipal-district-of-clearwater-2014-elected-officials','row':4,'peerFirst':'Greffard, Dennis *','candidate':'Greffard, Dennis*','resolution':'Original image shows a separate star. The exact footnote marker is preserved in both evidence readings; no changed letters or value. Normalized name is Greffard, Dennis in both.'},{'type':'peer first aggregate reading error; candidate already correct','sourceId':'gap-fill-municipal-city-of-rossland-2010-employee-remuneration','peerFirst':'1447863.64','freshOriginalImageReading':'1417863.64','candidate':'1417863.64','freshOriginalCropFile':str((A/'rossland2010-aggregate-fresh-reread.png').relative_to(ROOT)),'freshOriginalCropSha256':sha(A/'rossland2010-aggregate-fresh-reread.png'),'resolution':'Fresh rendered original clearly prints1,417,863.64; candidate control was already correct. Earlier peer30,000aggregate-disagreement claim is withdrawn, first transcript preserved.'}],'allPrintedControlComparisons':controls,'literalSourceQualifications':observations,'approvalContext':{'Rossland2010':'Checklist2010, actual2010schedule; Mayor and finance signaturesMay18,2011.','Rossland2011':'Checklist2011; CAO signedJune25,2012, mayor signature blank. No employee schedule in this allocation.','Rossland2012':'ChecklistDec31,2012 and submittedJune28,2013; approval page names/datesJune27,2013 but both signature lines blank. Official archive publication supports literal-source acceptance, must retain unsigned-approval qualification.','Rossland2013':'Checklist2013 submittedMay12,2014 and approval names/datesMay12,2014; bothsignaturelinesblank. Memo datesJune20,2013 andMay12,2013 conflict with later full-year schedule but actualsalaryyear2013 consistentlyexplicit. Mustretain exact date and unsigned-approval qualifications.','Rossland2014':'OfficialJune22,2015agenda p16 recommendsCouncilapproval of2014SOFI and p60approval signatures/daydates blank. Literal employee table fullyverified but final/adoptedstatus not established bythisagenda. Issuer minutes/adopted report evidence required before treating approval as confirmed.','Rossland2016':'Originalp3 bothSOFIapprovalsignaturesJune22,2017; salarysupplementlabelUnaudited isdisclosed, distinctfromdraftstatus.','Clearwater2011-2016':'Allsixoriginals haveactualSOFIyearcover andsignedapprovals.2015cover sayspresentedJune21st,2015whileapprovalsignaturesareJune24,2016; retaincover/signaturedateinconsistency withoutalteringexplicit2015salaryperiod.'},'acceptance':'All149candidate normalized rows and literalsourcefields accepted as faithful source transcription. Publication acceptance requires the stated source-approval qualifications; Rossland2014 six employee rows remain approval-context pending until municipal/root pins corroborating adoption evidence.','candidatePayloadPins':pins,'noOutreach':True,'noCompiledRowsDeleted':True,'limitations':['No claim that unsigned source copies prove signature/adoption.','All source blanks/dashes remain unknown; explicitNil is a source zero statement.','Payment disclosures do not establish annual base salary or complete workforce rosters.','All sums preserve source residuals and do not adjust published individual cells.']}
p=A/'municipal-earliest-12-peer-source-review.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=serial)+'\n');print(sha(p));print('Literal149rows exact,22cohorts; approvalcontextqualification explicit.')
