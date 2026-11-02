#!/usr/bin/env python3
"""Read-only independent projection review; stdlib only, no producer mutations."""
import argparse,collections,gzip,hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[5];A=R/'research/salaries/gap-fill-2026-11-02';O=A/'health_boards/peer-phsa-history';C=R/'research/salaries/gap-fill-phsa-history'
def load(p):return json.loads(gzip.decompress(p.read_bytes()))if p.suffix=='.gzip'else json.loads(p.read_bytes())
def pin(p):return{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def norm(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip())
def exact(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 if isinstance(a,dict):return a.keys()==b.keys()and all(exact(a[k],b[k])for k in a)
 return a==b
def check(manifest):
 m=load(manifest);peerpath=O/'independent-first-two-scans-source-review.json';peer=load(peerpath);rootpath=A/'reviews/root-nine-phsa-history-source-acceptance.json';root=load(rootpath);inventory=load(A/'phsa_history/source-inventory.json');out=[]
 assert peer['accepted']and root['accepted']and root['noOutreach']and m['noOutreach']
 for key in ['phsa-2009-10','phsa-2010-11']:
  s=next(s for s in m['sources']if s['id']=='gap-phsa-history-'+key);accepted=next(s for s in root['sources']if s['sourceId']=='gap-phsa-history-'+key);ps=next(s for s in peer['sources']if s['sourceKey']==key);raw=next(s for s in inventory['sources']if s['key']==key);sp=R/ps['selected']['path'];sel=load(sp);dp=C/s['file'];pp=C/s['provenanceFile'];data=load(dp);prov=load(pp);v=s['validation'];startyear=int(key[5:9]);year=f'{startyear}/{str(startyear+1)[2:]}'
  assert pin(sp)==ps['selected']==v['sourceSelection']==prov['sourceSelection']==accepted['selectedInput']
  assert s['sha256']==sel['sourceSha256']==ps['sourceSha256']==raw['sourceSha256']==accepted['sourceSha256']==prov['sourceSha256']
  assert s['sourceUrl']==raw['sourceUrl']and s['indexUrl']==raw['officialCatalogueHandle']and s['pdfBytes']==raw['bytes']
  assert s['dataSha256']==pin(dp)['sha256']==accepted['dataSha256']and s['provenanceSha256']==pin(pp)['sha256']==accepted['provenanceSha256']
  expected=[];prows=[]
  for i,r in enumerate(sel['rows'],1):
   assert r['sequence']==i;d=r['selected'];n=norm(d['name']);expected.append(['provincial-health-services-authority',n,None,d['remuneration'],d['expenses'],d['pdfPage']]);prows.append({'rowIndex':i,'pdfPage':d['pdfPage'],'name':n,'sourceFootnoteMarker':None})
  assert exact(data,expected),'normalized salary rows/name/pay/expense/null/order/page differ'
  assert exact(prov['rows'],prows),'row provenance differs'
  assert len(data)==s['rowCount']==accepted['rowCount']==v['actualNamedObservations']==ps['selectedRows']
  for k,e in {'employerSlug':'provincial-health-services-authority','employerName':'Provincial Health Services Authority','sector':'Health authorities','year':year,'periodType':'fiscal','periodStart':f'{startyear}-04-01','periodEnd':f'{startyear+1}-03-31','sourceKind':'official','category':'employee-remuneration','scope':'employee-remuneration','currency':'CAD','threshold':75000,'thresholdComparison':'as-published','completeEmployeeSchedule':True,'retainCompiledPartition':True}.items():assert exact(s[k],e),(key,k)
  assert 'conventional' in s['periodEvidence']and 'catalogue' in s['periodEvidence']
  assert v['completeEmployeeSchedule']and v['completePrintedNamedScope']and v['compiledPartitionRetained']and v['compiledPartitionRetentionReason']
  assert not v['residualCauseEstablished']and v['allKnownSalaryAmountsRemainLiteral']and v['initialAndSupersededReaderEvidenceRetained']
  assert prov['literalRowsRemainInPrintedOrderIncludingRepeatedObservations']and prov['noOutreach']
  assert prov['primaryImageReceipts']==sel['primaryPersonalReceipts']and prov['primaryPersonallyReadRows']==sel['primaryPersonallyReadRows']and prov['finiteSourceGuard']==sel['finiteSourceGuard']and prov['primaryCorrections']==sel['primaryCorrections']
  for f in ['independentPeerReviews','sourceContextAcceptance','fullOriginalPageCensusEvidence']:assert prov[f]==v[f]
  assert pin(peerpath)in prov['independentPeerReviews']and pin(peerpath)in prov['fullOriginalPageCensusEvidence']
  assert 'not prove' in prov['sourceTypographyQualification']and 'identity' in prov['sourceTypographyQualification']
  assert 'source whitespace/comma spacing' in prov['normalization']and 'No identities' in prov['normalization']
  assert 'all-row' not in prov['readingMethod'].lower()or 'not' in prov['readingMethod'].lower()
  pay=sum(r[3]for r in data);exp=sum(r[4]or 0 for r in data);controls=ps['personallySourceReadPrintedTotals'];residual=[str(pay-controls['remuneration']),str(exp-controls['expenses'])]
  assert v['literalRemunerationSum']==str(pay)==accepted['literalRemunerationSum']and v['literalKnownExpenseSum']==str(exp)==accepted['literalKnownExpenseSum']
  assert v['literalNamedControlResiduals']==residual==accepted['literalNamedControlResiduals']
  assert v['printedNamedControls']['remuneration']==controls['remuneration']and v['printedNamedControls']['expenses']==controls['expenses']and v['printedNamedControls']['physicalPage']==max(r[5]for r in data)
  warning=s['publicWarning'];assert all(t in warning for t in ['not annual base salary','not','dashes remain unknown','numeric zero remains zero','No cell is adjusted','no cause','compiled observations are retained','may overlap','no complete-copy','physical page 1','no byte identity'])
  assert f'{residual[0]} dollars remuneration' in warning and f'{residual[1]} dollars known expenses' in warning
  if key=='phsa-2009-10':
   assert v['printedEmployeeNarrativeCount']is None and v['printedNarrativeCountIsReportingPeriodControl']is False and v['conflictingNarrativeCount']==1800 and v['conflictingNarrativeCountPeriodEnd']=='2009-03-31'
   assert all(t in warning for t in ['March 31, 2009','March 31, 2010','contradictory narrative','not adopted as a 2010 table count control'])
  else:assert v['printedEmployeeNarrativeCount']==2004 and v['printedNarrativeCountIsReportingPeriodControl']is True and v['conflictingNarrativeCount']is None and v['conflictingNarrativeCountPeriodEnd']is None
  for ref in [*prov['independentPeerReviews'],prov['sourceContextAcceptance'],*prov['fullOriginalPageCensusEvidence'],*prov['primaryImageReceipts']]:assert pin(R/ref['path'])==ref
  out.append({'sourceId':s['id'],'sourceSha256':s['sha256'],'selected':pin(sp),'data':pin(dp),'provenance':pin(pp),'sourceMetadata':s,'everyNormalizedRowReconstructedExactly':True,'everyRowProvenanceReconstructedExactly':True,'allSourceProvenanceInputPinsMatchExactSelectedV4':True,'sourceOrderAndMultiplicityPreserved':True,'nullNumericAndDigitCharactersPreserved':True,'positionAlwaysNull':all(r[2]is None for r in data),'literalTotals':{'remuneration':pay,'knownExpenses':exp},'nullExpenseCount':sum(r[4]is None for r in data),'explicitZeroExpenseCount':sum(type(r[4])is int and r[4]==0 for r in data),'namedRowsByPhysicalPage':dict(sorted(collections.Counter(r[5]for r in data).items())),'financialResidualsPeriodNarrativeAndCompiledRetentionQualificationsPresent':True})
 return {'accepted':True,'scope':'Independent read-only exact final normalized projection of two previously source-reviewed PHSA scans; no new source acceptance or producer mutation.','manifest':pin(manifest),'originalSourcePeerAcceptance':pin(peerpath),'rootNineSourceAcceptance':pin(rootpath),'sources':out,'noOutreach':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--manifest',default=str(C/'sources-candidate.json'));p.add_argument('--output');a=p.parse_args();out=check(Path(a.manifest))
 if a.output:
  dest=O/a.output;assert not dest.exists();dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(pin(dest)))
 else:print(json.dumps({'passed':True,'manifest':out['manifest'],'rows':sum(s['sourceMetadata']['rowCount']for s in out['sources'])}))
