#!/usr/bin/env python3
"""Validate exact baseline preservation, reviewed replacements and original-backed recovery."""
import argparse,csv,gzip,hashlib,json
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
from salary_release_audit import verify_frozen_release
ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/'research/salaries'
OUT=RESEARCH/'recovery-wave-2026-11-01'
AREAS=['municipal','health','schools','education','crowns']
FIELDS=['id','employerSlug','employerName','sector','reportingPeriods','sourceUrl','sourceIndexUrl','status','route','nextAction','reason']
ACCEPTED={'verified','accepted','imported'}
COMPLETED={'resolved-original-processing','four-original-board-scopes-verified-candidate-awaiting-integration','worker-and-peer-reviewed-ready-for-root-integration','recovered-awaiting-peer-review'}
def read(path):return json.loads(path.read_text())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def decode(raw):
 x=json.loads(gzip.decompress(raw));return x if isinstance(x,list) else x['rows']
def fingerprint(rows):
 keys=[json.dumps([r[0],r[1],int(Decimal(str(r[2]))*100),None if r[3] is None else int(Decimal(str(r[3]))*100),r[4]],ensure_ascii=False,separators=(',',':')) for r in rows]
 return sha('\n'.join(sorted(keys,key=lambda x:x.encode())).encode())
def md(value):return str(value or '').replace('|','\\|').replace('\n',' ')
def validate_frozen_recovery(root=ROOT):
 """Verify PR35's exact accepted inputs without absorbing unrelated later sources."""
 root=Path(root);research=root/'research/salaries';folder=research/'recovery-wave-2026-11-01'
 result=verify_frozen_release(folder,research);release=read(folder/'release.json')
 index=read(root/'public/salaries/employers/index.json');registered=read(research/'collections.json')['collections']
 acceptance=read(folder/'parent-acceptance.json');assert acceptance['accepted'] is True
 for relative,expected in acceptance['reviewReceiptSha256'].items():
  path=(folder/relative).resolve();assert path.is_relative_to(folder.resolve()) and sha(path.read_bytes())==expected,relative
 for relative,expected in release['manifestSha256'].items():
  path=(root/relative).resolve();assert path.is_relative_to(research.resolve()) and sha(path.read_bytes())==expected,relative
 sources={}
 for area in AREAS:
  collection='recovery-'+area;assert collection in registered
  for source in read(research/collection/'sources.json')['sources']:
   if source.get('status','verified') in ACCEPTED:sources[source['id']]=(collection,source)
 needed={entry['employerSlug'] for entry in release['imports']};groups=defaultdict(list)
 for employer in index['employers']:
  if employer['slug'] not in needed:continue
  for row in decode((root/'public/salaries/employers'/(employer['slug']+'.json.gzip')).read_bytes()):
   groups[(employer['slug'],index['years'][row[4]],row[5])].append([row[0],row[1],row[2],row[3],row[6]])
 for expected in release['imports']:
  collection,source=sources[expected['sourceId']];published=index['sources'][source['id']]
  for key in ['year','periodType','periodStart','periodEnd','notes','validation','publicWarning','sha256','dataSha256','completeEmployeeSchedule']:
   assert published.get(key)==source.get(key),(source['id'],key)
  assert published['scope']==(source.get('category') or source['scope']) and published['url']==source['sourceUrl'],source['id']
  for key,hkey in [('evidenceFile','evidenceSha256'),('provenanceFile','provenanceSha256')]:
   if source.get(key):assert sha((research/collection/source[key]).read_bytes())==source[hkey],source['id']
  rows=decode((research/collection/source['file']).read_bytes())
  for slug in {r[0] for r in rows}:
   before=[[r[1],r[2],r[3],r[4],r[5]] for r in rows if r[0]==slug];after=groups[(slug,source['year'],source['id'])]
   assert len(before)==len(after) and fingerprint(before)==fingerprint(after),source['id']
 for decision in release['compiledReplacementDecisions']:
  assert not groups.get((decision['employerSlug'],decision['compiledYear'],decision['compiledSourceId'])),decision['employerSlug']
  source=index['sources'][decision['sourceId']]
  assert source['sha256']==decision['sourceSha256'] and source['dataSha256']==decision['sourceDataSha256']
 return result

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--frozen',action='store_true',help='Check historical release inputs and arithmetic without rewriting released outputs');args=parser.parse_args(argv)
 if args.frozen:
  print(json.dumps(validate_frozen_recovery()));return
 baseline_raw=(OUT/'baseline.json.gzip').read_bytes();baseline=json.loads(gzip.decompress(baseline_raw))
 before=read(OUT/'baseline-row-fingerprints.json');index=read(ROOT/'public/salaries/employers/index.json');audit=read(ROOT/'public/salaries/coverage.json')
 acceptance=read(OUT/'parent-acceptance.json');assert acceptance['accepted'] is True
 for relative,expected in acceptance['reviewReceiptSha256'].items():
  path=(OUT/relative).resolve();assert path.is_relative_to(OUT.resolve()) and sha(path.read_bytes())==expected,relative
 assert sha((RESEARCH/'recovery-crowns/sources.json').read_bytes())==acceptance['crownMetadataOnlyPromotion']['acceptedManifestSha256']
 for identifier,source in baseline['sources'].items():assert index['sources'][identifier]==source,('Prior source metadata changed',identifier)
 decisions=read(OUT/'replacement-decisions.json');assert before['baselineCommit']==baseline['repositoryCommit']==decisions['baselineCommit']
 removals={(r['employerSlug'],r['compiledYear'],r['compiledSourceId']):r for r in decisions['decisions']}
 assert len(removals)==len(decisions['decisions'])
 groups=defaultdict(list);employers={};totals=Counter()
 for e in index['employers']:
  raw=(ROOT/'public/salaries/employers'/(e['slug']+'.json.gzip')).read_bytes();rows=decode(raw)
  assert len(rows)==sum(e['counts']),e['slug'];employers[e['slug']]={'name':e['names'][-1],'sector':e['sector'],'rows':len(rows),'sha256':sha(raw)}
  for r in rows:
   groups[(e['slug'],index['years'][r[4]],r[5])].append([r[0],r[1],r[2],r[3],r[6]])
   kind='compiled' if index['sources'][r[5]].get('sourceKind')=='compiled' else 'official';totals[kind]+=1
 removed=0;preserved=0
 for old in before['groups']:
  key=(old['employerSlug'],old['year'],old['sourceId']);current=groups.get(key,[])
  if key in removals:
   d=removals[key];assert old['sourceKind']=='compiled' and d['status']=='reviewed' and d['reason'],key
   assert old['rows']==d['removedRows'] and old['rowMultisetSha256']==d['compiledRowMultisetSha256'],key
   assert not current,('Reviewed compiled partition remains',key)
   source=index['sources'][d['sourceId']];assert source['year']==d['replacementYear'] and source['sha256']==d['sourceSha256'] and source['dataSha256']==d['sourceDataSha256'],key
   removed+=old['rows']
  else:
   assert len(current)==old['rows'] and fingerprint(current)==old['rowMultisetSha256'],('Baseline observations changed',key)
   preserved+=old['rows']
 assert set(removals)<=set((g['employerSlug'],g['year'],g['sourceId']) for g in before['groups'])
 registered=read(RESEARCH/'collections.json')['collections'];imports=[];files={}
 for area in AREAS:
  collection='recovery-'+area;assert collection in registered
  folder=RESEARCH/collection;manifest=read(folder/'sources.json');files[str((folder/'sources.json').relative_to(ROOT))]=sha((folder/'sources.json').read_bytes())
  for s in manifest['sources']:
   if s.get('status','verified') not in ACCEPTED:continue
   assert s['id'] not in baseline['sources'],('Existing source imported again',s['id'])
   assert isinstance(s['notes'],list) and all(isinstance(n,str) for n in s['notes']),s['id']
   raw=(folder/s['file']).read_bytes();assert sha(raw)==s['dataSha256'],s['id'];rows=decode(raw);assert len(rows)==s['rowCount'],s['id']
   published=index['sources'][s['id']]
   for k in ['sha256','dataSha256','periodStart','periodEnd','notes','validation','publicWarning','completeEmployeeSchedule']:
    assert published.get(k)==s.get(k),(s['id'],k)
   assert published['scope']==(s.get('category') or s['scope']) and published['url']==s['sourceUrl'],s['id']
   if (int(s['periodEnd'][:4])-int(s['periodStart'][:4]))>1 or s.get('periodStart','').endswith('01-01') and s['periodType']=='fiscal':assert s.get('publicWarning'),s['id']
   for key,hkey in [('evidenceFile','evidenceSha256'),('provenanceFile','provenanceSha256')]:
    if s.get(key):assert sha((folder/s[key]).read_bytes())==s[hkey],s['id']
   for slug in {r[0] for r in rows}:
    expected=[[r[1],r[2],r[3],r[4],r[5]] for r in rows if r[0]==slug];actual=groups[(slug,s['year'],s['id'])]
    assert len(actual)==len(expected) and fingerprint(actual)==fingerprint(expected),s['id']
   imports.append({'collection':collection,'sourceId':s['id'],'employerSlug':s['employerSlug'],'year':s['year'],'scope':s.get('category') or s['scope'],'rows':len(rows),'sourceUrl':s['sourceUrl'],'sourceSha256':s['sha256'],'dataSha256':s['dataSha256'],'publicWarning':s.get('publicWarning')})
 added=sum(s['rows'] for s in imports);total=sum(totals.values())
 assert totals['official']-baseline['overall']['officialRecords']==added
 assert baseline['overall']['compiledRecords']-totals['compiled']==removed
 assert total-baseline['overall']['records']==added-removed and total==preserved+added
 assert index['recordCounts']=={'official':totals['official'],'compiled':totals['compiled']}
 assert audit['officialRows']==totals['official'] and audit['legacyRowsRetained']==totals['compiled']
 assert all(identifier in index['sources'] for identifier in baseline['sources'])
 tasks=[];completed=[];task_hashes={}
 for area in AREAS:
  path=OUT/area/'work-queue.json';raw=path.read_bytes();task_hashes[area]=sha(raw);entries=json.loads(raw);entries=entries if isinstance(entries,list) else entries['tasks']
  for t in entries:
   assert all(k in t for k in FIELDS) and isinstance(t['reportingPeriods'],list),t.get('id')
   item={**t,'researchArea':area,'requestStatus':'not-sent'}
   if t['status'] in COMPLETED:
    item['workerStatus']=t['status'];item['status']='completed-source-import';item['workerNextAction']=t['nextAction'];item['nextAction']='Reviewed source cohorts are imported. Preserve source qualifications; other historical periods and scopes remain open.';completed.append(item)
   else:tasks.append(item)
 assert len({t['id'] for t in tasks+completed})==len(tasks+completed)
 tasks.sort(key=lambda t:(t['sector'],t['employerName'],t['id']));requests=[t for t in tasks if t['route'] in {'ordinary-records-request','clarification-request','foi-fallback'}]
 municipal=read(RESEARCH/'municipal-audit/coverage.json')['summary']
 report={'version':1,'asOf':'2026-11-01','timezone':'America/Vancouver','baselineCommit':baseline['repositoryCommit'],'baselineFileSha256':sha(baseline_raw),'baseline':baseline['overall'],'proposed':{'records':total,'officialRecords':totals['official'],'compiledRecords':totals['compiled'],'employers':len(employers),'acceptedSourceFiles':len(audit['imports'])},'officialRowsAdded':added,'compiledRowsReplaced':removed,'netRowsAdded':added-removed,'baselineRowsPreservedExactly':preserved,'priorOfficialRowsPreservedExactly':baseline['overall']['officialRecords'],'originalReports':len({s['sourceSha256'] for s in imports}),'acceptedCohorts':len(imports),'countsByScope':{k:sum(s['rows'] for s in imports if s['scope']==k) for k in sorted({s['scope'] for s in imports})},'collections':[{'collection':'recovery-'+a,'rows':sum(s['rows'] for s in imports if s['collection']=='recovery-'+a),'cohorts':sum(s['collection']=='recovery-'+a for s in imports)} for a in AREAS],'imports':imports,'compiledReplacementDecisions':decisions['decisions'],'municipalCoverage':municipal,'currentWaveOpenTasks':len(tasks),'completedWorkerIntegrationTasks':len(completed),'currentWaveUnsentRequestCandidates':len(requests),'taskInputSha256':task_hashes,'manifestSha256':files}
 save('release.json',report);save('task-dispositions.json',{'completed':completed,'open':tasks,'policy':'These are changed tasks from this bounded wave. Earlier frozen queues overlap and are not an additive missing-record denominator.'});save('work-queue.json',{'tasks':tasks});save('acquisition-list.json',{'requestStatus':'not-sent','candidates':requests})
 for filename,entries in [('work-queue.csv',tasks),('acquisition-list.csv',requests)]:
  with (OUT/filename).open('w',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=FIELDS+['researchArea','requestStatus'],lineterminator='\n');writer.writeheader()
   for t in entries:writer.writerow({k:'; '.join(t[k]) if k=='reportingPeriods' else t[k] for k in writer.fieldnames})
 lines=['# Salary recovery wave — 1 November 2026','',f'This wave accepts **{added:,} official observations** from **{report["originalReports"]} original reports** and **{len(imports)} separate cohorts**. **{removed:,} reviewed compiled observations** are replaced; the dataset grows by **{added-removed:,} net records** to **{total:,}**. All **{baseline["overall"]["officialRecords"]:,} previously official observations** remain exactly unchanged.','', '| Collection | Added observations | Cohorts |','| --- | ---: | ---: |']
 for r in report['collections']:lines.append(f'| [{r["collection"]}](../{r["collection"]}/README.md) | {r["rows"]:,} | {r["cohorts"]} |')
 lines+=['','## What changed','',f'The app now contains **{totals["official"]:,} official observations** and **{totals["compiled"]:,} retained compiled observations**, across **{len(employers)} employers**. Official municipal coverage is **{municipal["withOfficialRecordsAfter"]}/161**, including **{municipal["withOfficialEmployeeRecords"]}** employee jurisdictions; **{municipal["withNoOfficialRecords"]}** still lack accepted official records. Regional districts remain outside this municipal denominator.','', '- UBC contributes 9,633 named FY2025/26 employee observations with exact source controls. Repeated names and eleven negative expense cells remain literal, without assumed identities or causes.','- Coast Mountain adds three complete employee schedules. Salary Plus Benefits is remuneration; the expense-inclusive Total is supporting evidence. Exact small control differences, the unsigned FY2022/23 form and its clipped literal surname remain qualified.','- BC Assessment adds calendar 2020 and FY2021/22–2024/25; FY2021/22 actually covers fifteen months. Earlier T4 Box 14 definitions differ from later FIR remuneration definitions. CPP/EI and broader payroll totals are excluded from named remuneration/expenses.','- BCER adds FY2023/24–2025/26 complete employee schedules. Former Oil and Gas Commission identity/history remains a separate unresolved canonicalization and processing task.','- McBride, Midway and Sooke add employee histories and separate council scopes. Signed Midway minutes establish adoption. McBride’s contradictory-period council attachment remains held; its separately verified employee schedule is accepted with a warning.','- Revelstoke, Central Coast and Gulf Islands add separate employee/trustee scopes. Complete image transcription and independent review cover the small scans; Gulf Islands employees have complete independent native readers. Published control differences remain visible, with no balancing changes.','- Health additions are 43 Interior Health board observations, not new employee coverage. PHSA’s first 49 employee rows remain staged only; the rest of the original is unverified. VCH and Providence original retrieval remains blocked.','', '## Replacement and verification decisions','', 'The [four reviewed replacement decisions](replacement-decisions.json) pin exact original/data and baseline row fingerprints. BC Assessment’s full 362-row compiled FY2020/21 label matches the original calendar 2020 cohort. The 394 BC Assessment, 249 BCER and 124 Coast Mountain same-fiscal groups also match completely. Source null expenses replace compiler zeros; null/zero equivalence is comparison-only, not a claim that the original expenses were zero. No unmatched council or board observations are removed.','', 'The baseline fingerprint gate checks every original employer/year/source row multiset, including literal names, titles, cents, nulls, physical pages and multiplicity. Every newly imported row must equal its normalized source. Source warning, period, scope and evidence hashes must match published metadata. No previously official row is deleted or edited.','', 'Independent reviews distinguish all-field machine agreement from the exact original pages visually checked. Native readers use independently implemented Poppler, PyMuPDF and PDFMiner paths. Small scanned schedules have full independent image transcription; two Tesseract settings are not called independent OCR. Matching totals alone do not establish acceptance.','', '## Remaining work and source copies','',f'The [changed-task queue](work-queue.csv) contains **{len(tasks)} open tasks** for this bounded wave; **{len(completed)} integration tasks** are completed in [the disposition ledger](task-dispositions.json). The [copy/clarification list](acquisition-list.md) contains **{len(requests)} unsent candidates**. Earlier [six-sector queues](../continuation-2026-11-01/work-queue.csv) and the [current source-catalog comparison](../sunshine-lists/comparison.md) remain available; lists overlap and must not be added as unique missing-report counts.','', 'NIC FY2019/20 needs a complete original: printed employee pages 1, 3 and 5 are missing from the public nine-page file, so OCR alone cannot complete it. CNC FY2020/21 remains held for hidden-versus-rendered surname disagreement. Arrow Lakes remains held for contradictory declaration years. All exact source-control clarifications stay unresolved; no cause is inferred from a numerical coincidence.','', 'No public body was contacted, no request or FOI submitted, and no fee incurred. Public native reports and complete adopted originals are preferred; source discovery and staged OCR are not published employee coverage.','', '## Review receipts','']
 lines += ['Use final handoffs and comparison receipts for acceptance. Initial raw reviewer transcripts and first-pass extraction differences are immutable review records; reviewer-only corrections are explicitly reconciled in the final comparisons. They are not alternative accepted datasets.','']
 lines += [f'- [{p.stem.replace("-"," ")}](reviews/{p.name})' for p in sorted((OUT/'reviews').glob('*.json')) if not p.name.endswith('-original-transcription.json')]
 lines+=['','## Reproduce','', '```sh','npm run compare:municipal-periods','npm run build:salaries','npm run check:salaries','npm run audit:municipal-salaries','npm run follow-up:municipal-salaries','npm run review:sector-salaries','npm run review:municipal-wave','npm run review:municipal-history','npm run review:salary-continuation','npm run review:salary-recovery','npm run audit:sunshine','npm run preview:salaries -- --build','```','', 'Each collection guide documents original-backed and offline replay. Former releases remain validated with their frozen inputs and totals.','']
 (OUT/'README.md').write_text('\n'.join(lines))
 lines=['# Unsent copy and clarification candidates','', 'Changed tasks from this recovery wave only; earlier acquisition lists may overlap. No requests, FOIs, contacts or fees.','', '| Employer / periods | Route | Source issue | Next action |','| --- | --- | --- | --- |']
 for t in requests:lines.append(f'| [{md(t["employerName"])} — {md(", ".join(t["reportingPeriods"]))}]({t["sourceUrl"] or t["sourceIndexUrl"]}) | {md(t["route"])} | {md(t["reason"])} | {md(t["nextAction"])} |')
 lines+=['','[CSV](acquisition-list.csv) · [JSON](acquisition-list.json) · [All changed tasks](work-queue.csv)',''];(OUT/'acquisition-list.md').write_text('\n'.join(lines))
 print(json.dumps({k:report[k] for k in ['officialRowsAdded','compiledRowsReplaced','netRowsAdded','originalReports','acceptedCohorts','currentWaveOpenTasks','currentWaveUnsentRequestCandidates']}))
if __name__=='__main__':main()
