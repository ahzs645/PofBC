#!/usr/bin/env python3
"""Finalize only complete peer-closed municipal scopes in the new collection."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/municipal'
COLLECTION=ROOT/'research/salaries/queue-completion-municipal'
RETENTION='Retain the compiled partition: no compatible same-calendar-year compiled cohort has been established. Root owns any future period mapping or deletion; full strict multiset comparison is pinned separately.'
SPECS={
 'mission-2023':('city-of-mission','City of Mission','2023','https://www.mission.ca/media/file/2023-sofi-report'),
 'mission-2024':('city-of-mission','City of Mission','2024','https://www.mission.ca/media/file/2024-sofi-report'),
 'mission-2025':('city-of-mission','City of Mission','2025','https://www.mission.ca/media/file/2025-sofi-reportpdf'),
 'vernon-2025':('city-of-vernon','City of Vernon','2025','https://www.vernon.ca/sites/default/files/2026-08/SOFI%20Signed%20-%20CORRECTED.pdf'),
}
WARNINGS={
 ('mission-2023','employee-remuneration'):'The 148 named employee rows total CAD 16,445,762 remuneration and 318,887 known expenses. The printed named-employee remuneration subtotal is 16,445,765, 3 higher; its expense subtotal agrees. Physical 6 employee rows total 4,050,146 remuneration versus printed page subtotal 4,050,149, also 3 higher. Blaschuk, S visibly prints 93,271 remuneration and 1,718 expenses (sum 94,989), while its separate printed expense-inclusive Total is 94,992, 3 higher. Every individual cell is retained as visibly printed; no cause is inferred and no amount is balanced. Nine printed expense dashes remain null.',
 ('mission-2024','employee-remuneration'):'The source labels its named selection as employees with remuneration and expenses exceeding CAD 75,000; this is preserved without silently imposing a pay-only rule. Eighteen printed expense dashes remain null. A separate footnote discloses CAD 5,370 of Mission Bridgehead Investment Corporation expenses outside the table; that aggregate is not assigned or added to individual observations. Source footnote markers on Crawford, S* and DeSousa, K* remain literal.',
 ('mission-2025','employee-remuneration'):'The source labels its named selection as employees with remuneration and expenses exceeding CAD 75,000; this is preserved without silently imposing a pay-only rule. Thirty-one printed expense dashes remain null. Source footnote markers identify City-paid work assigned to Mission Bridgehead Investment Corporation; no outside amount is assigned or added to individual observations.',
 ('vernon-2025','employee-remuneration'):'The 264 named employee rows total CAD 28,678,528 gross earnings and 380,683 expenses net of tax. Gross earnings agree with the printed named subtotal; the printed named-expense subtotal is 381,690, so literal row expenses minus that control are -1,007. Printed named expenses 381,690 plus below-threshold expenses 100,126 equal the printed all-employee expense total 481,816. Individual cells remain as printed, without balancing or a cause inferred. All 25 literal zero expenses remain 0. Employee job titles are not published and remain null.',
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def freeze(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():assert path.read_bytes()==data,str(path)
 else:path.write_bytes(data)
def pointer(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def load(path):return json.loads(gzip.decompress(path.read_bytes())) if path.suffix=='.gzip' else json.loads(path.read_text())

def finalize(key,peer_path):
 slug,name,year,url=SPECS[key]
 context_path=AREA/(key+'-context-review'+('-v2' if key=='mission-2023' else '')+'.json')
 context=load(context_path);original_review=AREA/(key+'-original-review.json.gzip');original=load(original_review)
 peer=ROOT/peer_path;peer_raw=peer.read_text();assert peer.is_file()
 data=[]
 for scope in ['employee-remuneration','elected-officials']:
  filename=key+'-'+scope+('-v2' if key=='mission-2023' and scope=='employee-remuneration' else '')+'.json.gzip'
  path=COLLECTION/filename;rows=load(path)
  assert sha(path) in peer_raw, 'Peer receipt must pin this exact final candidate hash'
  assert str(path.relative_to(ROOT)) in peer_raw or path.name in peer_raw, 'Peer must identify this file'
  data.append({'scope':scope,**pointer(path),'rows':rows})
 evidence={'date':'2026-11-01','sourceKey':key,'sourceSha256':context['sourceSha256'],'sourceContextReview':pointer(context_path),'completeAuthorOriginalReviewSnapshot':pointer(original_review),'independentPeerReceipt':pointer(peer),'allFinalCohorts':data,'rawIndependentOcrFiles':[{'path':s['rawEvidenceFile'],'sha256':s['rawEvidenceSha256']} for s in original['sections']],'retentionComparison':pointer(AREA/'compiled-comparison.json.gzip'),'noSourceBalancing':True,'noAnnualizationNameExpansionOrIdentityInference':True}
 if key=='mission-2023':evidence['postPeerOriginalImageAmendment']=pointer(AREA/'mission-2023-post-peer-source-amendment.json')
 evidence_path=COLLECTION/'evidence'/(key+'-complete-source.json.gzip')
 freeze(evidence_path,gzip.compress(json.dumps(evidence,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 sources=[]
 for item in data:
  scope=item['scope'];rows=item['rows'];employee=scope=='employee-remuneration';pages=sorted({r[5] for r in rows});nulls=sum(r[4] is None for r in rows);zeros=sum(r[4]==0 for r in rows)
  warning=WARNINGS.get((key,scope),'This source contains the complete seven-person elected-official scope only; employee observations are a separate source.')
  if key=='mission-2023' and employee:warning+=' The source uses a combined remuneration-and-expenses named-selection label; the below-75,000 remuneration rows remain as published.'
  if key=='mission-2025' and not employee:warning+=' Two printed expense dashes remain null; known-expense sums do not impute those dashes as zero.'
  warning+=' '+RETENTION
  notes=[
   'Every published name, title where present, separate remuneration and expense cell was checked on actual PDF-painted source images; independent Tesseract and Paddle OCR outputs and their source-reviewed corrections remain separate.',
   'An independent peer transcribed the complete source-image scope before full candidate comparison. Prior context disclosures and reviewer-only rereads remain in the immutable peer receipts.',
   'Repeated names or initials remain distinct literal observations; no identity merging, full-name enrichment, annualization or redistribution of aggregate amounts.',
   'The separate source expense-inclusive Total column, when printed, is retained only in supporting evidence and is never substituted for remuneration.',
   'Printed schedule year and signed approval are independently recorded; URL/upload dates are not used as reporting-year evidence.'
  ]
  if key=='vernon-2025':notes.append('The official index links the corrected signed original. The cover labels SOFI unaudited; the signed approval page approves the statements and schedules. No audited-compensation claim is made.')
  if key=='mission-2024' and employee:notes.append('The separate CAD 5,370 corporate-paid-expense footnote is aggregate supporting evidence only. City-paid wages/expenses for corporate-assigned work remain in their source rows.')
  validation={'method':'Complete independent Tesseract and Paddle OCR geometry readers, complete author actual-original image review, and independent full-scope image-first peer transcription with final candidate comparison.','allFinalRowFieldsOriginalImageVerified':True,'rawOcrReadersAgree':False,'allRawMachineDifferencesOriginalImageResolved':True,'completeEmployeeSchedule':employee,'compiledPartitionRetained':True,'compiledPartitionRetentionReason':RETENTION,'evidenceFile':'evidence/'+evidence_path.name,'evidenceSha256':sha(evidence_path),'sourceContextReview':pointer(context_path),'independentPeerReview':pointer(peer),'salaryPagesReviewedInFull':pages,'periodEvidence':context['printedPeriodEvidence'],'signedApproval':context['approval'],'nullExpenses':nulls,'explicitZeroExpenses':zeros,'nullPositions':sum(r[2] is None for r in rows),'controls':{'printed':context['printedCohortControls']['namedEmployees' if employee else 'electedOfficials'],'observed':{'remuneration':sum(r[3] for r in rows),'knownExpenses':sum(r[4] or 0 for r in rows)}}}
  if employee and key=='mission-2023':validation['controls']['sourceDiscrepancies']=context['literalControlDiscrepancies']
  if employee and key=='vernon-2025':validation['controls']['namedRowsMinusPrinted']=context['namedRowSumsMinusPrinted']
  spec={'id':'queue-completion-municipal-'+key+'-'+scope,'employerSlug':slug,'employerName':name,'sector':'Municipalities','year':year,'periodType':'calendar','periodStart':year+'-01-01','periodEnd':year+'-12-31','sourceUrl':url,'sourceIndexUrl':'https://www.mission.ca/council-government/budget-finance/financial-reporting' if key.startswith('mission') else 'https://www.vernon.ca/government-services/departments/financial-services/financial-statements-annual-reports','sha256':context['sourceSha256'],'file':Path(item['path']).name,'category':scope,'scope':scope,'title':name+' '+year+' SOFI: complete named '+('employee remuneration and expenses' if employee else 'elected-official remuneration and expenses'),'status':'accepted','verified':True,'verifiedOn':'2026-11-01','sourceKind':'official-scanned-pdf','rowCount':len(rows),'totalRemuneration':sum(r[3] for r in rows),'totalExpenses':sum(r[4] or 0 for r in rows),'pages':pages,'currency':'CAD','amountUnit':'dollars','threshold':75000 if key=='vernon-2025' and employee else None,'completeEmployeeSchedule':employee,'retainCompiledPartition':True,'dataSha256':item['sha256'],'notes':notes,'definitions':context['definitions'],'publicWarning':warning,'validation':validation}
  if employee:
   spec['publishedSelectionCriterion']=context['definitions'].get('sourceNamedSubtotalLabel',context['definitions'].get('publishedEmployeeSelection'))
   spec['thresholdBasis']='combined remuneration and expenses as the literal source named-subtotal label' if key.startswith('mission') else 'employee gross earnings'
   if key=='vernon-2025':spec['thresholdComparison']='>'
  spec_path=AREA/(key+'-'+scope+'-source-spec.json');freeze(spec_path,(json.dumps(spec,ensure_ascii=False,indent=2)+'\n').encode());sources.append(spec)
 print(json.dumps({'source':key,'rows':sum(s['rowCount'] for s in sources),'evidenceSha256':sha(evidence_path),'peerSha256':sha(peer)}))

def manifest():
 sources=[]
 for key in SPECS:
  for scope in ['employee-remuneration','elected-officials']:sources.append(load(AREA/(key+'-'+scope+'-source-spec.json')))
 publication_addenda=[]
 for source in sources:
  definitions=source['definitions']
  added=['Published remuneration meaning: '+definitions['remuneration'],'Published expense meaning: '+definitions['expenses'],'Published relation to financial statements: '+definitions['financialStatementRelation']]
  source['notes'].extend(added)
  publication_addenda.append({'sourceId':source['id'],'addedPublicNotes':added,'purpose':'The application publishes notes and publicWarning; preserve the source compensation definitions there as well as in the full metadata object. No data or evidence bytes changed.'})
 prior=AREA/'creston-source-spec.json';creston=copy.deepcopy(load(prior));creston['validation'].update(compiledPartitionRetained=True,compiledPartitionRetentionReason=RETENTION,completeEmployeeSchedule=True);creston['publicWarning']+=' '+RETENTION
 addendum={'date':'2026-11-01','originalFrozenSpec':pointer(prior),'scope':'metadata-only retention validation fields and appended public compiled-retention explanation in new combined manifest','unchangedDataSha256':creston['dataSha256'],'unchangedEvidenceSha256':creston['validation']['evidenceSha256'],'newFinalSourceMetadata':creston,'priorFrozenFilesUnchanged':True}
 freeze(AREA/'creston-retention-metadata-addendum.json',(json.dumps(addendum,ensure_ascii=False,indent=2)+'\n').encode());sources.append(creston)
 freeze(AREA/'source-metadata-publication-addendum.json',(json.dumps({'date':'2026-11-01','sourceAddenda':publication_addenda,'priorFrozenFilesUnchanged':True},ensure_ascii=False,indent=2)+'\n').encode())
 assert len(sources)==9 and sum(s['rowCount'] for s in sources)==835
 for s in sources:
  assert s['retainCompiledPartition'] and s['publicWarning'] and s['validation']['compiledPartitionRetained'] and s['validation']['compiledPartitionRetentionReason']
  assert s['validation']['completeEmployeeSchedule']==s['completeEmployeeSchedule']
 freeze(COLLECTION/'sources.json',(json.dumps({'version':1,'sources':sources},ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'sources':len(sources),'rows':835,'manifestSha256':sha(COLLECTION/'sources.json')}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--key',choices=SPECS);p.add_argument('--peer');p.add_argument('--manifest',action='store_true');args=p.parse_args()
 if args.key:assert args.peer;finalize(args.key,args.peer)
 if args.manifest:manifest()
