#!/usr/bin/env python3
"""Reproduce qualified Creston2024 employee scope; never changes earlier evidence."""
import gzip,hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/"research/salaries/queue-completion-2026-11-01/municipal"
COLLECTION=ROOT/"research/salaries/queue-completion-municipal"
REV=ROOT/"research/salaries/queue-completion-2026-11-01/reviews"
SOURCE_SHA="24a6cd0394f42596859f15cb4a1ec811c28c5a5c09e004a3766aa78130396ac6"
DATA_SHA="e71de303545fbf4f668a240b11128a2e106b979b3c817be543a36be311c2fce9"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frozen_write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  if path.read_bytes()!=data:raise ValueError(f"Refuse to overwrite frozen {path}")
 else:path.write_bytes(data)
def build():
 manual=AREA/"creston-author-manual-transcript.json";amend=AREA/"creston-author-reviewed-amendments.json"
 assert sha(manual)=="aabd7bc29713fb5464400759428e1e2a1130fd3c2e12b904483cd87e6b444a33"
 d=json.loads(manual.read_text());a=json.loads(amend.read_text());rows=[list(r) for r in d["rows"]]
 for c in a["corrections"]:
  r=rows[c["sourceRow"]-1];index={"name":1,"remuneration":3}[c["field"]];assert r[index]==c["before"];r[index]=c["after"]
 assert len(rows)==27 and all(r[0]=="town-of-creston" and r[5]==37 for r in rows)
 assert sum(r[3] for r in rows)==2684996 and sum(r[4] for r in rows)==61034
 assert sum(r[4]==0 for r in rows)==13 and all(r[4] is not None for r in rows)
 payload=json.dumps(rows,ensure_ascii=False,separators=(",",":")).encode()
 data=COLLECTION/"creston-2024-employee-remuneration.json.gzip"
 frozen_write(data,gzip.compress(payload,mtime=0));assert sha(data)==DATA_SHA
 comparison=REV/"independent-creston-queue-final-payload-comparison.json"
 engines=REV/"independent-creston-queue-two-engine-source-comparison.json"
 assert sha(comparison)=="10d2b1579e743510f1341967021ae0feeb064e2e09d2720af11d4c2b83ce9664"
 assert sha(engines)=="8fa329f360e3c1417b551d653f2320aa42344fcd3ed4265323754220fafbff3d"
 draft=AREA/"reader-draft.json.gzip"
 sections=json.loads(gzip.decompress(draft.read_bytes()))["sections"]
 section=next(s for s in sections if s["layout"]["sourceKey"]=="creston-2024")
 assert len(section["tesseractRows"])==len(section["paddleRows"])==27
 controls={"printedNamed":{"remuneration":2685008,"expenses":61044},"knownNamedRows":{"remuneration":2684996,"expenses":61034},"namedRowSumMinusPrinted":{"remuneration":-12,"expenses":-10},"printedBelowThreshold":{"remuneration":1583173,"expenses":67341},"printedAllEmployees":{"remuneration":4268181,"expenses":128386},"printedNamedPlusBelowExpenses":128385,"printedAllEmployeeExpensesMinusPrintedNamedPlusBelow":1,"separateRemunerationReconciliation":{"printedElected":164518,"printedAllEmployees":4268181,"printedSubtotal":4432699,"printedIncludedStatementOfRevenueAndExpenditure":4432689,"finalMinusSubtotal":-10}}
 evidence={"sourceSha256":SOURCE_SHA,"physicalPage":37,"employeeOnly":True,"rowCount":27,"rowFields":rows,"initialAuthorTranscript":{"path":str(manual.relative_to(ROOT)),"sha256":sha(manual)},"authorAmendments":{"path":str(amend.relative_to(ROOT)),"sha256":sha(amend)},"twoIndependentOcrReaders":section,"independentPeerComparison":{"path":str(comparison.relative_to(ROOT)),"sha256":sha(comparison)},"independentTwoEngineAdjudication":{"path":str(engines.relative_to(ROOT)),"sha256":sha(engines)},"controls":controls,"approval":{"physicalPage":9,"signedBy":["Steffan Klassen","Acting Mayor Carolyn Hawton"],"date":"2025-06-30","scope":"All statements and schedules in the SOFI; independently visually confirmed."},"nullExpenses":0,"explicitZeroExpenses":13,"noBalancing":True,"noExistingCouncilRowsDuplicated":True}
 evidencePath=COLLECTION/"evidence/creston-2024-employee-remuneration.json.gzip"
 frozen_write(evidencePath,gzip.compress(json.dumps(evidence,ensure_ascii=False,separators=(",",":")).encode(),mtime=0))
 warning="The27 named employee rows total CAD2,684,996 remuneration and61,034 expenses, compared with printed named-employee subtotals2,685,008 and61,044: row sums minus printed controls are -12 and -10. Separately, printed named plus below-threshold employee expense controls61,044+67,341 equal128,385, while the all-employee expense control is128,386 (1 higher). The separate remuneration reconciliation shows elected164,518 plus all employees4,268,181, with printed subtotal4,432,699, but the final amount included in the Statement of Revenue and Expenditure is4,432,689 (10 lower). Published individual cells are retained unchanged; causes remain unresolved."
 spec={"id":"queue-completion-municipal-creston-2024-employee-remuneration","employerSlug":"town-of-creston","employerName":"Town of Creston","sector":"Municipalities","year":"2024","periodType":"calendar","periodStart":"2024-01-01","periodEnd":"2024-12-31","sourceUrl":"https://www.creston.ca/sites/default/files/2025-07/Statement%20of%20Financial%20Information%202024.pdf","sourceIndexUrl":"https://www.creston.ca/statement-financial-information","sha256":SOURCE_SHA,"file":data.name,"category":"employee-remuneration","scope":"employee-remuneration","title":"Town of Creston2024 SOFI: complete named employee remuneration and expenses","status":"accepted","verified":True,"verifiedOn":"2026-11-01","sourceKind":"official-scanned-pdf","rowCount":27,"totalRemuneration":2684996,"totalExpenses":61034,"pages":[37],"currency":"CAD","amountUnit":"dollars","threshold":75000,"thresholdComparison":">","completeEmployeeSchedule":True,"retainCompiledPartition":True,"dataSha256":DATA_SHA,"notes":["Only the complete27-person employee scope is new; already accepted2024 council observations are excluded.","Published names, initials, literal spellings, word order and positions remain as visibly printed, including Jeff Webb and Waste Water Treatment Plan Operator.","Remuneration is the separate published REMUNERATION column. Expenses remain separate; employer EI and CPP are excluded from employee remuneration under the checked source schedule policy (physical4).","All13 printed zero expense cells remain0; no expense dashes, missing expense values, imputation or annualization.","Two independent OCR engines (Tesseract and Paddle via RapidOCR) read all27 rows; every machine difference and all original employee fields were checked against actual PDF-painted images. A peer independently transcribed all27 original-image rows before comparing the frozen candidate.","Original physical9 signed June30,2025 approves all SOFI statements and schedules. Printed employee schedule heading is2024; whole-report calendar end December31,2024 is separately printed on physical1.","Retain the compiled partition until root reviews exact-year full-cohort comparison; no compiled calendar mapping or deletion inferred."],"validation":{"method":"Independent Tesseract and Paddle OCR geometry readers; complete author original-image review; independent peer image-first full27-row transcription and exact162-field normalized comparison.","allRowFieldsAgreeWithFinalOriginalImageReview":True,"rawOcrReadersAgree":False,"allRawMachineDifferencesOriginalImageResolved":True,"evidenceFile":"evidence/"+evidencePath.name,"evidenceSha256":sha(evidencePath),"controls":controls,"physicalPagesVisuallyReviewed":[1,3,4,5,7,8,9,10,11,12,36,37,38,39,41,42],"salaryPagesReviewedInFull":[37],"periodEvidence":[{"page":37,"text":"SCHEDULE SHOWING REMUNERATION AND EXPENSES PAID FOR2024"},{"page":1,"text":"Fiscal Year End:31 December,2024"}],"independentPeerReview":{"path":str(comparison.relative_to(ROOT)),"sha256":sha(comparison),"allRowsExact":True,"rows":27,"fields":162},"independentTwoEngineAdjudication":{"path":str(engines.relative_to(ROOT)),"sha256":sha(engines),"machineFieldsCompared":216},"nullExpenses":0,"explicitZeroExpenses":13,"signedApproval":{"physicalPage":9,"date":"2025-06-30"}},"publicWarning":warning}
 spec["title"]="Town of Creston 2024 SOFI: complete named employee remuneration and expenses"
 spec["publicWarning"]="The 27 named employee rows total CAD 2,684,996 remuneration and 61,034 expenses, compared with printed named-employee subtotals 2,685,008 and 61,044: row sums minus printed controls are -12 and -10. Separately, printed named plus below-threshold employee expense controls 61,044 + 67,341 equal 128,385, while the all-employee expense control is 128,386 (1 higher). The separate remuneration reconciliation shows elected 164,518 plus all employees 4,268,181, with printed subtotal 4,432,699, but the final amount included in the Statement of Revenue and Expenditure is 4,432,689 (10 lower). Published individual cells are retained unchanged; causes remain unresolved."
 spec["notes"]=[re.sub(r"(?<=[A-Za-z])(?=[0-9])"," ",s) for s in spec["notes"]]
 spec["validation"]["method"]=re.sub(r"(?<=[A-Za-z])(?=[0-9])"," ",spec["validation"]["method"])
 spec["validation"]["periodEvidence"]=[{"page":37,"text":"SCHEDULE SHOWING REMUNERATION AND EXPENSES PAID FOR 2024"},{"page":1,"text":"Fiscal Year End: 31 December, 2024"}]
 specPath=AREA/"creston-source-spec.json";frozen_write(specPath,(json.dumps(spec,indent=2,ensure_ascii=False)+"\n").encode())
 print(json.dumps({"sourceSpec":str(specPath.relative_to(ROOT)),"sourceSpecSha256":sha(specPath),"dataSha256":sha(data),"evidenceSha256":sha(evidencePath),"rows":27,"nullExpenses":0,"literalZeroExpenses":13}))
if __name__=="__main__":build()

