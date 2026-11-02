#!/usr/bin/env python3
"""Source-reviewed nine-history payloads; exact literal comma-free row adoption."""
import json,gzip,copy,pathlib,collections,re
from decimal import Decimal
from gap_health_other_history import ROOT,AREA,dump,sha
from gap_health_employees_native import amount,nameclean
from gap_health_employees_export import definitions,named_control
COLLECTION=ROOT/'research/salaries/gap-fill-health-other-history'
PEER_FIRST='research/salaries/gap-fill-2026-11-02/school_native/reviews/health-other-history/independent-first247-source-transcript.json'
PEER_FIRST_SHA='554b27110baa72d90d1c36c4f07a7eb3eb566b6882e3ee334e9066f0d1815b06'
PEER_ADDITIVE='research/salaries/gap-fill-2026-11-02/school_native/reviews/health-other-history/additive-three-own-source-rereads.json'
PEER_ADDITIVE_SHA='8aba7a9731055abd4773d39787eed87f92278fe49f837baa1993d380628b59f6'
PEER_FINAL='research/salaries/gap-fill-2026-11-02/school_native/reviews/health-other-history/independent-final247-source-transcript.json'
PEER_FINAL_SHA='5ec070934054f9430d9344f10fd8173582fbb3f0881573c470993e5eb61a5706'
PEER_ACCEPT='research/salaries/gap-fill-2026-11-02/school_native/reviews/health-other-history/independent247-source-exception-review.json'
PEER_ACCEPT_SHA='48d870b7820a1e8b20c2d5528b6d99244313434f778e4951e210f5f92e15610b'
CONTEXT='research/salaries/gap-fill-2026-11-02/reviews/health-other-context-root/root-nine-source-context-acceptance.json'
CONTEXT_SHA='637ee861ba71716949d5e72e73bcda78e1ac6772f952cc4017270dba04d025f8'
def pinned(path,h):
 p=ROOT/path;assert sha(p.read_bytes())==h,('pin changed',path);return json.load(open(p))
def ref(path,h):return {'path':path,'sha256':h}
def load(p):return json.loads(gzip.decompress(pathlib.Path(p).read_bytes()))
def peer_selection():
 first=pinned(PEER_FIRST,PEER_FIRST_SHA);additive=pinned(PEER_ADDITIVE,PEER_ADDITIVE_SHA);final=pinned(PEER_FINAL,PEER_FINAL_SHA);pinned(PEER_ACCEPT,PEER_ACCEPT_SHA);assert first['candidateValuesPreviouslyRead'] is False
 a={r['id']:r for r in first['rows']};b={r['id']:r for r in final['rows']};assert a.keys()==b.keys() and len(b)==247;changes=[]
 for tid,r in a.items():
  for field in ['literalName','remuneration','expenses','sourceSha256','sourceKey','physicalPage','sourceRowOnPage']:
   if r[field]!=b[tid][field]:changes.append((tid,field,r[field],b[tid][field]))
 assert {(tid,f) for tid,f,old,new in changes}=={('health-other-source-001-048','expenses'),('health-other-source-001-218','literalName'),('health-other-source-001-228','literalName')},changes
 assert len(additive['rereads'])==3 and additive['candidateChangesRequestedForTheseThree'] is False
 return b,changes

def validate_retention(s):
 assert s['retainCompiledPartition'] is True
 assert s['completeEmployeeSchedule']==s['validation']['completeEmployeeSchedule']
 assert s['validation']['compiledPartitionRetained'] is True and s['validation']['compiledPartitionRetentionReason'] and s['publicWarning']

def main():
 peer,changes=peer_selection();pinned(CONTEXT,CONTEXT_SHA);specs={r['sourceSha256']:r for r in json.load(open(AREA/'recovered-employee-originals-v2.json'))};evidence={r['sourceSha256']:r for r in json.load(open(AREA/'native-reader-evidence-index-v2.json'))};contexts={r['sourceSha256']:r for r in json.load(open(AREA/'source-context-review-packet.json'))['sources']};sources=[];comparisons=[];COLLECTION.mkdir(exist_ok=True)
 for c in json.load(open(AREA/'native-primary-candidate-index.json')):
  s=specs[c['sourceSha256']];e=evidence[c['sourceSha256']];ctx=contexts[c['sourceSha256']];primary=load(ROOT/c['file']);secondary=load(ROOT/c['secondaryFile']);assert [r['row'] for r in primary['rows']]==[r['row'] for r in secondary['rows']];rows=copy.deepcopy(primary['rows']);matches={}
  for tid,r in peer.items():
   if r['sourceKey']!=c['key'] or r['sourceRowOnPage'] is None:continue
   raw=next(v for v in rows if v['row'][5]==r['physicalPage'] and v['sourceRowOnPage']==r['sourceRowOnPage']);assert [raw['row'][1],raw['row'][3],raw['row'][4]]==[nameclean(r['literalName']),amount(r['remuneration']),amount(r['expenses']) if r['expenses'] is not None else None];raw.setdefault('sourceImageTargetIds',[]).append(tid);matches[tid]=True
  if c['key']=='island-health-2009-10':
   r=peer['health-other-source-001-001'];assert r['sourceRowOnPage'] is None and [r['literalName'],amount(r['remuneration']),amount(r['expenses'])]==['WILSON. TOM',77451,0] and r['physicalPage']==47
   flag=next(f for f in primary['flags'] if f['kind']=='pay-line-without-comma-name');assert flag['physicalPage']==47 and 'WILSON. TOM' in flag['line'];pages=load(ROOT/e['popplerLayout']['path'])['pages'];lines=pages[46].splitlines();loc=[i for i,l in enumerate(lines) if l==flag['line']];assert len(loc)==1;loc=loc[0]
   after=[(i,v) for i,v in enumerate(rows) if v['row'][5]==47 and lines.index(v['rawLine'])>loc];assert after
   insertAt=min(after,key=lambda pair:lines.index(pair[1]['rawLine']))[0];previous=rows[insertAt-1]['row'];following=rows[insertAt]['row'];assert previous[5]==following[5]==47
   rows.insert(insertAt,{'row':['island-health','WILSON. TOM',None,77451,0,47],'rawLine':flag['line'],'payToken':'77,451','expenseToken':'0','sourceRowOnPage':None,'sourceImageTargetIds':[r['id']],'literalLayoutLineOnPage':loc+1,'adoption':'Additional actual source observation omitted by comma-only candidate-name grammar. Preserve literal WILSON. TOM with period, numeric77451 and numericexpense0. No comma correction or expanded identity.','sourceNeighborsBeforeAndAfter':[previous,following]})
   matches[r['id']]=True
  for r in primary['flags']+secondary['flags']:assert c['key']=='island-health-2009-10' and r['physicalPage']==47
  values=[r['row'] for r in rows];pay=sum(Decimal(str(v[3])) for v in values);expenses=sum(Decimal(str(v[4])) for v in values if v[4] is not None);control=named_control(ctx);residual=[str(pay-Decimal(str(control['remuneration']))),str(expenses-Decimal(str(control['expenses'])))] if control else None
  sourceId='gap-health-other-history-'+c['key'];filename=c['key']+'-employees.json.gzip';raw=gzip.compress(json.dumps(values,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);(COLLECTION/filename).write_bytes(raw)
  provenance=[];pageRows=collections.Counter()
  for i,r in enumerate(rows,1):
   pageRows[r['row'][5]]+=1;v={'rowIndex':i,'physicalPage':r['row'][5],'sourceRowOnPage':pageRows[r['row'][5]],'initialPrimarySourceRowOnPage':r['sourceRowOnPage'],'rawPrimaryLayoutLine':r['rawLine'],'rawRemunerationToken':r['payToken'],'rawExpenseToken':r['expenseToken'],'independentNativeRowsAgree':r['sourceRowOnPage'] is not None,'sourceImageTargetIds':r.get('sourceImageTargetIds',[])}
   for k in ['adoption','literalLayoutLineOnPage','sourceNeighborsBeforeAndAfter']:
    if k in r:v[k]=r[k]
   provenance.append(v)
  peerRefs={'first':ref(PEER_FIRST,PEER_FIRST_SHA),'additive':ref(PEER_ADDITIVE,PEER_ADDITIVE_SHA),'final':ref(PEER_FINAL,PEER_FINAL_SHA),'reviewAcceptance':ref(PEER_ACCEPT,PEER_ACCEPT_SHA)};proof={'sourceSha256':s['sourceSha256'],'status':'complete source review; root final normalized adoption pending','sourceEvidence':e,'sourceContextAcceptance':ref(CONTEXT,CONTEXT_SHA),'independentSourceImageReview':peerRefs,'rows':provenance};provfile=c['key']+'-provenance.json.gzip';prov=gzip.compress(json.dumps(proof,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);(COLLECTION/provfile).write_bytes(prov)
  warning='Official Legislative Library archival copy includes an added cover at physical page 1; page citations identify this downloaded copy. These are disclosed payments, not annual base salary rates or a complete workforce roster. Separate expenses remain literal: printed zero stays zero, blank/dash stays unknown, negative amounts stay negative.'
  if residual and any(Decimal(x)!=0 for x in residual):warning+=f' Literal named rows differ from printed named controls by {residual[0]} dollars remuneration and {residual[1]} dollars known expenses. No amount is adjusted and no cause is established.'
  if c['key']=='northern-health-2014-15':warning+=' The source summary counts 1,255 employees above the disclosure threshold; the complete actual table contains 1,254 observations. Complete independent monetary-anchor and row censuses find no extra employee row. The count discrepancy remains unexplained; no employee is invented.'
  if c['key']=='island-health-2009-10':warning+=' One name is literally printed WILSON. TOM with a period; that punctuation and its explicit zero expense are preserved without an inferred name correction.'
  warning+=' Existing compiled observations are retained and may overlap this official schedule. No complete-copy, calendar-label or identity equivalence is assumed.'
  year=s['item']['candidateYear'];start=int(year[:4]);retentionReason='No complete source-compatible duplicate-copy comparison proves this official cohort replaces a compiled partition. Preserve every compiled observation.';notes=['Complete source table is retained in printed order, including repeated observations. Source names are disclosed strings, not resolved identities.','No job titles are published in this employee schedule; position remains null.','The conventional fiscal start is April 1 before the actual internally printed March 31 year-end; these are payment periods, not annualized salary rates.']+definitions(ctx)
  source={'id':sourceId,'employerSlug':s['item']['employerSlug'],'employerName':s['item']['issuer'],'sector':'Health authorities','year':year,'periodType':'fiscal','periodStart':f'{start}-04-01','periodEnd':f'{start+1}-03-31','periodEvidence':'Actual original salary-period heading independently reviewed in the exact first/last context images; catalogue metadata used for discovery only.','title':s['item']['issuer']+' employee remuneration '+year+' (official Legislative Library copy)','sourceUrl':s['url'],'sourceIndexUrl':'https://www.northernhealth.ca/about-us/accountability/reports/financial-accountability' if c['key'].startswith('northern') else 'https://www.islandhealth.ca/about-us/plans-reports-and-policies/financial-reports','catalogueUrl':'https://digitalcollections.llbc.leg.bc.ca/handle/'+s['item']['handle'],'sha256':s['sourceSha256'],'file':filename,'dataSha256':sha(raw),'rowCount':len(values),'status':'source-reviewed-awaiting-root-adoption','sourceKind':'official','scope':'employee-remuneration','category':'employee-remuneration','currency':'CAD','threshold':75000,'thresholdComparison':'as-published','completeEmployeeSchedule':True,'retainCompiledPartition':True,'notes':notes,'publicWarning':warning,'provenanceFile':provfile,'provenanceSha256':sha(prov),'validation':{'candidateOnly':True,'completeEmployeeSchedule':True,'compiledPartitionRetained':True,'compiledPartitionRetentionReason':retentionReason,'literalRemunerationSum':str(pay),'literalKnownExpenseSum':str(expenses),'printedNamedControls':control,'literalNamedControlResiduals':residual,'residualCauseEstablished':False,'printedEmployeeSummaryCount':1255 if c['key']=='northern-health-2014-15' else 2245 if c['key']=='island-health-2009-10' else None,'actualEmployeeObservations':len(values),'allNativeRowsExactlyAgreeBeforeSourceAddition':True,'independentOriginalImageTargetsForThisSource':len(matches),'sourceContextAcceptance':ref(CONTEXT,CONTEXT_SHA),'independentSourceImageReview':peerRefs,'pendingGates':['root final normalized reconstruction/adoption','owned freeze']}}
  validate_retention(source)
  sources.append(source);comparisons.append({'sourceId':sourceId,'sourceSha256':s['sourceSha256'],'rows':len(values),'dataSha256':source['dataSha256'],'provenanceSha256':source['provenanceSha256'],'literalNamedControlResiduals':residual,'sourceImageTargets':len(matches)})
 manifest={'schemaVersion':1,'status':'nine official employee cohorts source-reviewed; root final normalized adoption pending','noOutreach':True,'sources':sources};mp=COLLECTION/'sources-candidate.json';dump(mp,manifest);dump(AREA/'normalized-candidate-summary.json',{'sources':comparisons,'candidateRows':sum(s['rowCount'] for s in sources),'sourceImageTargetTotal':sum(s['validation']['independentOriginalImageTargetsForThisSource'] for s in sources),'sourceAddition':'exact literal WILSON. TOM77,451/0 at original physical47 position','firstReadingChangesExplicit':changes,'manifest':{'path':str(mp.relative_to(ROOT)),'sha256':sha(mp.read_bytes())},'noOutreach':True});print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'manifestSha256':sha(mp.read_bytes())}))
if __name__=='__main__':main()
