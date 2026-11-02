#!/usr/bin/env python3
"""Freeze the completed bounded municipal tranche and precise remaining blocker."""
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/municipal'
COLLECTION=ROOT/'research/salaries/queue-completion-municipal'
REVIEWS=AREA.parent/'reviews'
KEYS={'id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(gzip.decompress(path.read_bytes())) if path.suffix=='.gzip' else json.loads(path.read_text())
def freeze(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():assert path.read_bytes()==data,str(path)
 else:path.write_bytes(data)
def freezejson(path,data):freeze(path,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
def ptr(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}

def run():
 manifest=load(COLLECTION/'sources.json');sources=manifest['sources'];assert len(sources)==9
 continuation=load(ROOT/'research/salaries/continuation-2026-11-01/municipal/work-queue.json')
 queue=[]
 for key in ['mission-2023','mission-2024','mission-2025','vernon-2025','creston-2024']:
  group=[s for s in sources if key in s['id']];assert group
  source=group[0];old=[r['id'] for r in continuation if r.get('sourceUrl')==source['sourceUrl']]
  qualified=key in ['mission-2023','vernon-2025','creston-2024']
  queue.append(dict(id='queue-completion-municipal-'+key+'-complete-scope',employerSlug=source['employerSlug'],employerName=source['employerName'],sector='Municipalities',reportingPeriods=[source['year']],sourceUrl=source['sourceUrl'],sourceIndexUrl=source['sourceIndexUrl'],status='verified-complete-source-qualified' if qualified else 'verified-complete-source',route='processing',nextAction='Integrate the complete verified named scopes from this tranche using the frozen manifest; retain compiled partitions and the exact public source-control qualifications.',reason='Complete original-image and two-engine processing plus independent image-first full-scope peer closure: '+str(sum(s['rowCount'] for s in group))+' rows in '+str(len(group))+' distinct scopes. '+('The already accepted Creston2024 council scope is excluded. ' if key=='creston-2024' else '')+'Resolves these source-specific prior tasks: '+', '.join(old)+'. This does not claim every historical municipal year is now covered.'))
 queue.append(dict(id='queue-completion-municipal-mcbride-exact-council-period',employerSlug='village-of-mcbride',employerName='Village of McBride',sector='Municipalities',reportingPeriods=['2024','2025'],sourceUrl='https://mcbride.civicweb.net/document/45990',sourceIndexUrl='https://www.mcbride.ca/government-bylaws/finance',status='held-period-conflict-public-route-checked-unsent-request-ready',route='clarification-request',nextAction='Use the recipient-verified UNSENT ordinary request draft for an existing corrected official council schedule or an exact-five-row issuer period clarification. No request has been sent; no relabelling, duplicate import or fee is authorized.',reason='All four examined council-table headings say2024 inside2025 packages, with expenses differing from the accepted2024 schedule. Current finance/council/policy/bylaw routes, the2025 audited statements and six new bounded web queries did not resolve the specific row period. Whole-package adoption does not repair the heading. Links held-resolution-municipal-mcbride-request-period-copy, recovery-municipal-clarify-mcbride-2025-council-period, continuation-municipal-745c924ec3956e1c and continuation-municipal-dbbe229bcb97c4ac. The already accepted2025 employee cohort is unaffected.'))
 queue.append(dict(id='queue-completion-municipal-terrace-historical-triage',employerSlug='city-of-terrace',employerName='City of Terrace',sector='Municipalities',reportingPeriods=['2015','2016'],sourceUrl=None,sourceIndexUrl='https://www.terrace.ca/city-services/finance-taxation',status='bounded-historical-public-route-checked-no-new-salary-source',route='public-archive-research',nextAction='Continue only if another actual historical named salary original is located; existing2017–2025 official scopes are already accepted and must not be duplicated.',reason='Current index links SOFI back to2017. Linked2015/2016 annual reports were retrieved and native-keyword searched without finding a named salary table; two guessed SOFI paths returned404. This bounded route is not proof that reports never existed or need FOI. Links continuation-municipal-fdfe3e996bc3289a and continuation-municipal-6885a463c109ea1e.'))
 assert all(set(r)==KEYS and isinstance(r['reportingPeriods'],list) for r in queue)
 freezejson(AREA/'work-queue.json',queue)
 old_sources=[];overlaps=[];triage=[]
 for directory in ['municipal-lower-mainland','municipal-small','municipal-ocr']:
  p=ROOT/'research/salaries'/directory/'sources.json'
  for s in load(p)['sources']:
   if s.get('employerSlug') in ['city-of-surrey','city-of-north-vancouver','village-of-montrose'] and (s.get('employerSlug'),s.get('year')) in [('city-of-surrey','2025'),('city-of-north-vancouver','2022'),('village-of-montrose','2023')]:
    if s.get('category')!='employee-remuneration':continue
    data=p.parent/s['file'];assert sha(data)==s['dataSha256'];triage.append({'sourceId':s['id'],'manifest':ptr(p),'data':ptr(data),'status':s.get('status'),'rows':s['rowCount'],'finding':'Already accepted in the current baseline; no new rows or changes proposed.'})
 for p in (ROOT/'research/salaries').glob('*/sources.json'):
  if p.parent==COLLECTION:continue
  for s in load(p).get('sources',[]):
   if s.get('employerSlug') in ['city-of-mission','city-of-vernon','town-of-creston'] and s.get('status','verified') in ['accepted','verified','imported']:
    old_sources.append({'manifest':ptr(p),'sourceId':s['id'],'employerSlug':s['employerSlug'],'year':s.get('year'),'scope':s.get('category') or s.get('scope'),'rows':s.get('rowCount')})
    if any(t['employerSlug']==s['employerSlug'] and t['year']==s.get('year') and t['category']==(s.get('category') or s.get('scope')) for t in sources):overlaps.append(s['id'])
 assert not overlaps
 freezejson(AREA/'overlap-and-existing-source-triage.json',{'date':'2026-11-01','newSourcePeriodScopeOverlaps':overlaps,'existingTargetJurisdictionOfficialScopesRetained':old_sources,'rootSuggestedAdditionalSourcesAlreadyAccepted':triage,'oldFilesModified':False})
 summary={'sources':len(sources),'originals':5,'rows':sum(s['rowCount'] for s in sources),'employeeRows':sum(s['rowCount'] for s in sources if s['category']=='employee-remuneration'),'electedRows':sum(s['rowCount'] for s in sources if s['category']=='elected-officials'),'totalRemuneration':sum(s['totalRemuneration'] for s in sources),'knownExpenses':sum(s['totalExpenses'] for s in sources),'nullExpenses':sum(s['validation']['nullExpenses'] for s in sources),'explicitZeroExpenses':sum(s['validation']['explicitZeroExpenses'] for s in sources),'nullPositions':sum(sum(r[2] is None for r in load(COLLECTION/s['file'])) for s in sources)}
 progress=load(AREA/'research-progress.json');progress.update(status='complete-municipal-tranche-peer-closed-frozen',summary=summary,plannedScopes='All five original sources completed and independently reviewed. McBride five council rows remain held; no unrelated council duplicate imported.',manifest=ptr(COLLECTION/'sources.json'),remainingExternalNeed='Existing corrected McBride council schedule or exact-five-row period clarification; recipient-verified ordinary request remains UNSENT.',oldFrozenFilesChanged=False,contactsSent=False)
 freezejson(AREA/'research-progress-final.json',progress)
 readme='''Five public originals now supply nine complete named scopes: Mission2023–2025 employee and elected-official tables, Vernon2025 employee and elected-official tables, and Creston2024 employees only. Total835 observations comprise807employees and28elected officials. The already accepted Creston council scope and McBride2025 employee scope are not duplicated.

Every published source field was checked on actual PDF-painted images. Tesseract and Paddle outputs remain separate; independent image-first peers transcribed all835rows before full candidate comparison, with their limited prior context and subsequent rereads retained honestly. All30 captured salary/context renders were reproduced from the hashed original PDFs. No invisible native job-title strings were imported. Vernon’s264 absent employee titles remain null;60 literal expense dashes remain null and38 printed zeros remain0.

Three employee scopes carry exact source-control qualifications: Mission2023 named/page6 pay is3 below the printed controls (the visibly printed Blaschuk pay93,271 also yields a3 difference from its separate printed expense-inclusive Total); Vernon2025 named expenses are1,007 below the printed control; Creston2024 named pay/expense differences are−12/−10, with separate1 expense aggregate and10 remuneration reconciliation discrepancies. No amounts are balanced and no causes inferred. Mission’s combined remuneration-and-expenses named-selection label is preserved. Mission2024’s separate5,370 corporate-paid-expense aggregate is not allocated to individuals.

The sources.json manifest is the canonical final metadata. It adds public compensation-definition notes and required compiled-retention validation fields through new additive metadata receipts; earlier frozen specs, provisional payloads and evidence are unchanged. Mission2023’s first-pass employee file remains preserved but is excluded from the final manifest; the corrected-v2 payload is accepted. All nine sources retain compiled partitions. The complete strict multiset comparison supports no calendar/fiscal mapping or deletion.

McBride’s five conflicting council rows remain unimported: all four reviewed internal headings say2024 within2025 packages, and the exact expense cells differ from accepted2024. Fresh finance/council/policy/bylaw routes,35-page audited-statement native research and six bounded web queries produced no specifically dated correction. The focused ordinary request in the acquisition outbox remains UNSENT; no contact, webform or FOI submission or fee occurred. Terrace2015/2016 was bounded historical triage only, with no new salary source claimed. Surrey2025, North Vancouver City2022 and Montrose2023 employee scopes were already accepted and remain unchanged.

Reproduce offline with python scripts/finish_salary_municipal_verify.py; add --originals for all30 actual300dpi render hashes. Run PYTHONPATH=scripts python -m unittest test_finish_salary_municipal test_finish_salary_municipal_final. No new OCR run is needed. Root owns global registry/build/publication, compiled decisions and any external request authorization.
'''
 readme=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',readme)
 freeze(AREA/'README.md',readme.encode());freeze(COLLECTION/'README.md',readme.encode())
 peer_paths=[REVIEWS/'independent-mission-queue-2023-final-source-closure.json',REVIEWS/'independent-mission-queue-2024-final-source-closure.json',REVIEWS/'root-mission-2025-final-source-closure.json',REVIEWS/'independent-vernon-queue-2025-final-source-closure.json',REVIEWS/'independent-creston-queue-final-payload-comparison.json',REVIEWS/'independent-creston-queue-two-engine-source-comparison.json']
 handoff={'date':'2026-11-01','owner':'recovery_municipal','status':'complete-bounded-municipal-tranche-ready-for-root-integration','summary':summary,'manifest':ptr(COLLECTION/'sources.json'),'sourceSummaries':[{k:s[k] for k in ['id','employerSlug','year','scope','rowCount','sourceUrl','sha256','file','dataSha256','retainCompiledPartition','publicWarning']} for s in sources],'originalInventory':load(AREA/'research-progress.json')['sourceInventory']+[load(AREA/'research-progress.json')['additionalSource']],'independentPeerClosures':[ptr(p) for p in peer_paths],'originalReplay':ptr(AREA/'original-replay-verification.json'),'offlineReplay':ptr(AREA/'offline-replay-verification.json'),'compiledComparison':ptr(AREA/'compiled-comparison.json.gzip'),'overlapCheck':ptr(AREA/'overlap-and-existing-source-triage.json'),'workQueue':ptr(AREA/'work-queue.json'),'mcbrideUnresolvedPublicRoute':ptr(AREA/'mcbride-current-public-route-review.json'),'unsentMcBrideDraft':'research/salaries/queue-completion-2026-11-01/acquisition/outbox/outbox-mcbride-council-period.md','outboxRecipientVerification':'research/salaries/queue-completion-2026-11-01/acquisition/outbox/contact-verification.json','messagesSent':False,'feesIncurred':False,'oldFrozenFilesModified':False,'globalFilesModifiedByThisWorker':False,'compiledDeletionAuthorized':False,'nextTeamWork':'After this municipal handoff, join PHSA historical image batches coordinated by recovery_review. This handoff does not claim that issuer-dependent McBride clarification has been resolved.'}
 freezejson(AREA/'handoff.json',handoff)
 paths=set(p for p in AREA.rglob('*') if p.is_file() and p.name!='candidate-freeze.json')
 paths.update(p for p in COLLECTION.rglob('*') if p.is_file())
 paths.update((ROOT/'scripts').glob('finish_salary_municipal*.py'));paths.update((ROOT/'scripts').glob('test_finish_salary_municipal*.py'))
 for pattern in ['independent-creston-*','independent-mission-*','independent-vernon-*','root-mission-2025-*']:paths.update(p for p in REVIEWS.glob(pattern) if p.is_file())
 freezejson(AREA/'candidate-freeze.json',{'date':'2026-11-01','scope':'Only new municipal tranche, unchanged supporting earlier Creston freeze and exact independent peer receipts; no caches, bytecode, global outputs or future mutable files.','manifestSha256':sha(COLLECTION/'sources.json'),'summary':summary,'files':[ptr(p) for p in sorted(paths)]})
 print(json.dumps({'handoff':ptr(AREA/'handoff.json'),'freeze':ptr(AREA/'candidate-freeze.json'),'files':len(paths),'summary':summary},indent=2))

if __name__=='__main__':run()
