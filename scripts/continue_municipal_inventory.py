#!/usr/bin/env python3
"""Reconcile province-wide municipal research receipts, accepted cohorts and draft tasks."""
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import unquote,urlparse
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-2026-11-01/municipal';COLL=ROOT/'research/salaries/continuation-municipal'
KEYS=['id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason']
ROUTES={'processing','public-archive-research','ordinary-records-request','clarification-request','foi-fallback'}
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def canon(u):return unquote(u or'').lower().rstrip('/')
def main():
 cov=json.loads((ROOT/'research/salaries/municipal-audit/coverage.json').read_text());inv=json.loads((OUT/'inventory.json').read_text());by={m['employerSlug']:m for m in cov['municipalities']}
 sources=json.loads((COLL/'sources.json').read_text())['sources'];accepted=defaultdict(list)
 for s in sources:accepted[s['employerSlug']].append(s)
 receipts=[]
 for p in sorted(OUT.glob('*receipt*.json')):
  x=json.loads(p.read_text());receipts+=x if isinstance(x,list)else [x]
 all_url={canon(r.get('url')):r for r in receipts if isinstance(r,dict)and r.get('url')};by_slug=defaultdict(list)
 for r in receipts:
  if isinstance(r,dict)and r.get('employerSlug'):by_slug[r['employerSlug']].append(r)
 srch={}
 for p in sorted(OUT.glob('search-*.json')):
  for q in json.loads(p.read_text())['queries']:srch[q['employerSlug']]=p.name
 registered=[]
 for collection in json.loads((ROOT/'research/salaries/collections.json').read_text())['collections']:
  if collection=='continuation-municipal':continue
  for item in json.loads((ROOT/'research/salaries'/collection/'sources.json').read_text())['sources']:
   if item.get('employerSlug')in by:registered.append(item)
 known=registered+sources
 full_urls={canon(s['sourceUrl'])for s in known if s.get('category')=='employee-remuneration'and s.get('completeEmployeeSchedule',True)}&{canon(s['sourceUrl'])for s in known if s.get('category')=='elected-officials'}
 full_hashes={s['sha256']for s in known if s.get('category')=='employee-remuneration'and s.get('completeEmployeeSchedule',True)}&{s['sha256']for s in known if s.get('category')=='elected-officials'}
 full_years=defaultdict(set)
 for u in full_urls:
  em={str(s['year'])for s in known if canon(s['sourceUrl'])==u and s.get('category')=='employee-remuneration'and s.get('completeEmployeeSchedule',True)}
  co={str(s['year'])for s in known if canon(s['sourceUrl'])==u and s.get('category')=='elected-officials'}
  full_years[u]=em&co
 queue=[];identities=set();retired=[]
 def add(slug,periods,url,index,status,route,next_action,reason,old_id=None):
  assert route in ROUTES
  identity=(slug,tuple(periods),canon(url),route,status)
  if identity in identities:return
  identities.add(identity);name=by.get(slug,{}).get('employerName',slug.replace('-',' ').title());id='continuation-municipal-'+hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:16]
  queue.append(dict(zip(KEYS,[id,slug,name,'Municipalities',periods,url,index,status,route,next_action,reason+(' Prior task: '+old_id+'.'if old_id else'')])))
 old=json.loads((ROOT/'research/salaries/municipal-history-pass/work-queue.json').read_text())['tasks']
 # All 308 prior historical tasks are reconciled individually rather than silently discarded.
 for t in old:
  url=t.get('sourceUrl');route=t['route'];status=t['status'];nxt=t['nextAction'];reason=t['reason']
  concrete={str(y)for y in t.get('reportingPeriods',[])if str(y)not in ['unknown','unverified']}
  if route=='processing'and canon(url)in full_urls and (not concrete or concrete<=full_years[canon(url)]):
   retired.append({'priorId':t['id'],'sourceUrl':url,'reason':'Both complete named employee and elected schedules are already verified for the requested period/scope from this exact original in registered collections or continuation-municipal. Grouped historical requests with other unaccepted years remain queued.'});continue
  rec=all_url.get(canon(url))
  if route=='ordinary-records-request'and rec and rec.get('pages'):
   route='processing';status='retrieved-public-original-awaits-complete-processing';nxt='Use the already retrieved official original, locate the actual named employee/council salary pages and verify each printed period, row, component and control. For scan pages, complete OCR and full image transcription. Do not request an available public PDF merely because extraction is unfinished.';reason+=' The current continuation retrieved this exact public original.'
  if route=='foi-fallback':
   route='ordinary-records-request';nxt='First complete the public archive and council attachment retrieval route; if the existing report remains unavailable, prepare a routine copy request for the exact named schedules and any existing native spreadsheet. Formal access is only a later fallback; no request is sent.'
  add(t['employerSlug'],t.get('reportingPeriods',[]),url,t.get('sourceIndexUrl'),status,route,nxt,reason,t['id'])
 # Preserve every exact older municipal audit blocker, including draft/adoption and mixed-year holds.
 audit=json.loads((ROOT/'research/salaries/municipal-audit/follow-up.json').read_text())
 route_map={'final-version-or-adoption-evidence':'public-archive-research','missing-schedules':'ordinary-records-request','public-retrieval-or-routine-copy-request':'public-archive-research','public-source-processing':'processing','reporting-period-clarification':'clarification-request','verify-completed-ocr-or-layout':'processing'}
 for task in audit['sourceTasks']:
  slug=task['employerSlug'];url=task.get('sourceUrl');yr=str(task.get('year'))if task.get('year')is not None else None
  route=route_map[task['route']]
  if canon(url)in full_urls and route=='processing' and (not yr or yr in full_years[canon(url)]):continue
  next_action=task['nextAction'];reason=task.get('blocker','')
  if task.get('ocrEvidence'):reason+=' Existing staged OCR evidence: '+task['ocrEvidence'].get('file','')+'.'
  add(slug,[yr]if yr and task.get('periodVerified')else [],url,task.get('archiveUrl'),task['status'],route,next_action,reason,task['id'])
 # Processing inventory of every freshly retrieved PDF and every explicit SOFI link.
 for rec in receipts:
  if not isinstance(rec,dict)or rec.get('httpStatus')!=200 or not rec.get('employerSlug'):continue
  slug=rec['employerSlug'];url=rec['url'];index=by.get(slug,{}).get('archiveUrl')or by.get(slug,{}).get('website')or url
  if rec.get('pages')and canon(url)not in full_urls and rec.get('sha256')not in full_hashes:
   already=accepted.get(slug,[]);covered=[s for s in already if canon(s['sourceUrl'])==canon(url)]
   if covered and slug in ['district-of-port-edward','district-of-wells']:continue
   add(slug,[],url,index,'official-original-retrieved-salary-scope-unverified','processing','Inspect the complete original and identify actual remuneration periods/scopes. Complete named-row extraction, independent reader or manual image transcription, and original control review before importing. The PDF is already public; do not route OCR work to FOI.',f"Original retrieved and hashed: {rec.get('sha256')}; {rec['pages']} physical pages; {rec.get('textCharacters',0)} extractable characters. Detected salary-text page candidates: {[p['physicalPage']for p in rec.get('salaryTextCandidates',[])]}. No period or named scope is inferred from the URL.")
  for c in rec.get('candidates',[]):
   u=c['url'];label=c.get('label','')
   if not re.search(r'sofi|statement.{0,30}financial information|remuneration',u+' '+label,re.I):continue
   if canon(u)in full_urls or canon(u)==canon(url):continue
   add(slug,[],u,url,'official-salary-link-awaits-period-and-scope-verification','processing'if re.search(r'\.pdf|/document/|/media/file/|download_file',u,re.I)else'public-archive-research','Follow the official archive link, retrieve the original salary schedule and verify its printed reporting year/period and employee/council scope. Review all named rows, compensation components and controls. Do not infer a salary year from this index label.',f'Fresh official archive link label: {label!r}. Candidate labels and upload-path tokens are leads only; historical completeness is not established.')
 for slug in ['district-of-port-edward']:
  for s in accepted[slug]:
   add(slug,[s['year']],s['sourceUrl'],s['sourceIndexUrl'],'employee-component-and-total-definition-held','clarification-request','Seek an existing corrected/native employee schedule or explicit issuer explanation of the Other Remuneration blanks/dashes and the field labelled Total Remuneration. Retain known raw remuneration/expense cells; do not substitute an expense-inclusive total or infer zero for unpublished components. Council is already separately verified.','Employee physical page6 publishes Remuneration and Taxable Benefits, Other Remuneration, Total Remuneration and two separate expense components. The displayed Total Remuneration includes expense amounts in visible rows; missing Other Remuneration cells are not established zero. No employee row from these originals is accepted.')
 wells=next(s for s in sources if s['employerSlug']=='district-of-wells')
 add('district-of-wells',[],wells['sourceUrl'],wells['sourceIndexUrl'],'employee-subheading-2018-conflicts-with-2020-report','clarification-request','Find an existing corrected/adopted employee schedule or explicit period clarification for Donna Forseille’s row. The council schedule has its own2020 heading and is separately verified; do not use its dates to resolve employee dates.','Physical page3 overall heading says Schedule of Remuneration and Expenses2020 while employee subsection says Staff2018 Remuneration and Expenses(combined). The employee row is held; salary90000 and expense425.59 are not assigned to either year.')
 for m in inv['jurisdictions']:
  slug=m['employerSlug'];new=accepted.get(slug,[]);rr=by_slug[slug];current=m['status']!='pending-incorporation';prior=by[slug]
  m['baselineHeldOrUnparsedSources']=prior.get('heldOrUnparsedSources',[])
  m['continuationEmployeeYears']=sorted({s['year']for s in new if s['category']=='employee-remuneration'});m['continuationCouncilYears']=sorted({s['year']for s in new if s['category']=='elected-officials'});m['continuationRows']=sum(s['rowCount']for s in new);m['continuationCohorts']=[s['id']for s in new]
  m['freshOfficialRetrievals']=[{'url':r['url'],'httpStatus':r.get('httpStatus'),'sha256':r.get('sha256'),'pages':r.get('pages'),'error':r.get('error')}for r in rr];m['uncoveredWebSearchReceipt']=srch.get(slug);m['freshArchiveCandidateLinks']=len({canon(c['url'])for r in rr for c in r.get('candidates',[])})
  m['currentOfficialCoverageAfterContinuation']=bool(prior['officialRecords']or new);m['employeeOfficialCoverageAfterContinuation']=bool(prior['officialEmployeeYears']or m['continuationEmployeeYears']);m['historicalCompletenessEstablished']=False
  if current and not m['currentOfficialCoverageAfterContinuation']:
   add(slug,[],m['archiveUrl']or m['website'],m['archiveUrl']or m['website'],'current-jurisdiction-still-without-accepted-official-cohort','public-archive-research','Continue from the retained official archive/search receipts and council attachments. Retrieve actual named employee and council schedules, including historical versions/native tables; distinguish ordinary records-copy needs from public PDFs that only require OCR or layout review.','This jurisdiction was rechecked in the fresh all161-jurisdiction primary archive pass and all60-uncovered web-search pass. No completed named cohort from it is accepted by this continuation. A bounded search does not establish that historical reports are unavailable or must be obtained through FOI.')
  elif current:
   add(slug,[],m['archiveUrl']or m['website'],m['archiveUrl']or m['website'],'remaining-historical-coverage-not-established','public-archive-research','Compare the exact accepted employee/council year inventory with newly located archive/council attachments and prior historical tasks. Process only missing employer/year/category cohorts; retain source conflicts, draft holds and exact scope.','Fresh primary archive check completed. Accepted years are an evidence inventory, not proof of complete historical coverage. Do not duplicate existing sources or treat an annual-report index label as a verified salary year.')
 add('district-of-okanagan-falls',[],'https://news.gov.bc.ca/releases/2026HMA0069-000747','https://engage.gov.bc.ca/govtogetherbc/engagement/okanaganfalls/','pending-incorporation-2026-11-06','public-archive-research','Revisit official municipal reporting after incorporation on November6,2026; keep pre-incorporation RDOS employer records with the regional-district sector. Do not count Okanagan Falls as a current municipality on November1.','The province’s June24,2026 announcement explicitly sets formal incorporation and first council meeting to November6,2026. The pending jurisdiction is excluded from the current161 denominator.')
 add('shishalh-nation-government-district',[],'https://shishalh.com/services/inter-government/sngd/','https://shishalh.com/services/inter-government/sngd/','separate-governance-and-employer-identity-review','public-archive-research','Inspect the district’s own existing financial statements and governance records for named disclosures. Separate Nation and Government District scopes/employer identities before any import; do not assume municipal SOFI/FIPPA rules or map Nation compensation to the district.','The official sNGD page states that the Nation Chief and Council governs the district and links district financial statements. Governance overlap alone does not establish that a Nation report is the district’s employer disclosure.')
 add('jumbo-glacier-mountain-resort-municipality',[],'https://www2.gov.bc.ca/gov/content/governments/local-governments/facts-framework/local-government-system/municipalities','https://www2.gov.bc.ca/gov/content/governments/local-governments/facts-framework/local-government-system/municipalities','former-municipality-historical-discovery-incomplete','public-archive-research','Search existing official archived council/financial records from the former municipality, retaining a separate historical employer identity if a named schedule is located. Do not add the dissolved municipality to the current denominator.','Jumbo Glacier is outside the current roster because it was dissolved in2021. This bounded historical query did not retrieve a verified named salary original; no claim of complete historical availability is made.')
 queue.sort(key=lambda t:(t['employerSlug'],t['route'],t['sourceUrl']or'',t['id']));assert all(list(t)==KEYS for t in queue);assert len({t['id']for t in queue})==len(queue)
 for m in inv['jurisdictions']:m['remainingTaskIds']=[t['id']for t in queue if t['employerSlug']==m['employerSlug']]
 inv['summary']={'rosterEntries':162,'currentJurisdictions':161,'pendingJurisdictions':1,'allCurrentPrimaryArchivesChecked':len({r['employerSlug']for r in json.loads((OUT/'archive-receipts.json').read_text())}),'previouslyUncoveredWebSearches':len(srch),'continuationOriginals':len({s['sha256']for s in sources}),'continuationCohorts':len(sources),'continuationRows':sum(s['rowCount']for s in sources),'employeeRows':sum(s['rowCount']for s in sources if s['category']=='employee-remuneration'),'councilRows':sum(s['rowCount']for s in sources if s['category']=='elected-officials'),'newOfficialJurisdictions':sum(not by[k]['officialRecords'] for k in accepted),'withAnyOfficialAfter':sum(m['currentOfficialCoverageAfterContinuation']for m in inv['jurisdictions']if m['status']!='pending-incorporation'),'withOfficialEmployeeAfter':sum(m['employeeOfficialCoverageAfterContinuation']for m in inv['jurisdictions']if m['status']!='pending-incorporation'),'stillWithoutOfficialAfter':sum(not m['currentOfficialCoverageAfterContinuation']for m in inv['jurisdictions']if m['status']!='pending-incorporation'),'priorHistoryTasksReconciled':len(old),'priorAuditSourceTasksReconciled':len(audit['sourceTasks']),'priorHistoryTasksResolvedByExactOriginal':len(retired),'remainingTasks':len(queue),'tasksByRoute':dict(Counter(t['route']for t in queue)),'historicalCompletenessEstablished':False,'outreachSent':False}
 dump(OUT/'inventory.json',inv);dump(OUT/'work-queue.json',queue);dump(OUT/'resolved-prior-history-tasks.json',retired)
 acquisitions=[t for t in queue if t['route']in ['ordinary-records-request','clarification-request','foi-fallback']];dump(OUT/'acquisition-list.json',acquisitions)
 for filename,arr in [('work-queue.csv',queue),('acquisition-list.csv',acquisitions)]:
  with (OUT/filename).open('w',newline='')as f:
   writer=csv.DictWriter(f,fieldnames=KEYS);writer.writeheader()
   for t in arr:writer.writerow(dict(t,reportingPeriods='; '.join(t['reportingPeriods'])))
 dump(OUT/'compiled-replacement-review.json',{'decision':'No compiled partitions are replaced or removed.','acceptedEmployerCompiledBaselines':[{'employerSlug':slug,'compiledRecords':by[slug]['compiledUnverifiedRecords'],'editionLabels':by[slug]['compiledUnverifiedEditionLabels']}for slug in sorted(accepted)],'automaticFiscalReplacementCandidates':[],'basis':'Every accepted source is calendar-year; all ten accepted employers have zero compiled baseline records. Employee imports cannot remove compiled council/board/executive observations for these employers.','aliasEdits':[]})
 print(json.dumps(inv['summary'],indent=2))
if __name__=='__main__':main()
