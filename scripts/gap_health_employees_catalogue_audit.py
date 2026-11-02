#!/usr/bin/env python3
"""Account for every captured serial item using broad literal-label classes.

Catalogue dates classify discovery only. Actual-source period/scope acceptance is
separately pinned to prior accepted sources,65 reviewed originals, or delegated
source review. Standalone financial titles never establish absence of salaries.
"""
import json,gzip,re,pathlib,hashlib,collections
from gap_health_employees_native import ROOT,AREA
SLUG={'Fraser Health':'fraser-health','Interior Health':'interior-health','Northern Health':'northern-health','Providence Health Care':'providence-health-care','Provincial Health Services Authority':'provincial-health-services-authority','Vancouver Coastal Health':'vancouver-coastal-health','Vancouver Island Health':'island-health'}
def main():
 catp=AREA/'exact-serial-catalogue.json';cat=json.load(open(catp));basep=ROOT/'research/salaries/gap-fill-2026-11-02/baseline.json.gzip';base=json.load(gzip.open(basep,'rt'));specs=json.load(open(AREA/'recovered-employee-originals-v2.json'));selected={r['item']['uuid']:r for r in specs};covered=collections.defaultdict(list)
 for g in base['groups']:
  meta=base['sourceMetadata'][g['sourceId']]
  if meta['sourceKind']=='official':covered[(g['employerSlug'],g['year'],meta.get('scope'))].append(g['sourceId'])
 assets={}
 for f in ['phsa-earlier-original-locators.json','additional-salary-label-original-locators.json','northern-2014-original-locator.json']:
  for a in json.load(open(AREA/f)):assets.setdefault(a['item']['uuid'],[]).append({'url':a['url'],'bitstreamUuid':a['bitstreamUuid'],'name':a['name'],'metadataReceiptSha256':a['bundleMetadataSha256']})
 out=[];uncovered=[];financeUnassessed=[]
 for r in cat:
  label=' | '.join(r['serialIssue']);l=label.lower();m=re.match(r'(20\d\d)/(20\d\d)',label);year=m[1]+'/'+m[2][-2:] if m else None;slug=SLUG[r['issuer']]
  if re.search(r'executive|psec|compensation (?:report|discuss)|compensation disclosure',l):kind='separate-executive-compensation-disclosure'
  elif re.search(r'board',l):kind='separate-board-disclosure'
  elif re.search(r'statement of financial information',l):kind='combined-sofi-candidate'
  elif re.search(r'suppli|vendor|schedule of payment',l):kind='supplier-payments'
  elif 'contract employees' in l:kind='named-employee-contract-detail-context'
  elif re.search(r'remuner|remener|renumer|salar(?:y|ies)|staff|employee',l):kind='employee-remuneration-candidate'
  elif re.search(r'financial statement',l):kind='standalone-financial-statements-metadata-only'
  elif re.search(r'compensation',l):kind='compensation-scope-not-assessed-from-metadata'
  elif re.search(r'disclaimer|executive summary',l):kind='supporting-scope-document'
  else:kind='unclassified'
  assert kind!='unclassified',(r['uuid'],label)
  employeeScope=covered.get((slug,year,'employee-remuneration'),[]);boardScope=covered.get((slug,year,'board-remuneration'),[])
  if r['uuid'] in selected:
   s=selected[r['uuid']];status='actual-original-employee-period-and-scope-reviewed-in65batch';actual={'year':s['item']['candidateYear'],'scope':'employee-remuneration','sourceSha256':s['sourceSha256'],'proof':'source-verification-closure.json'}
  elif kind in ['employee-remuneration-candidate','combined-sofi-candidate'] and employeeScope:status='employee-period-scope-already-accepted-in-frozen-baseline';actual={'year':year,'scope':'employee-remuneration','priorSourceIds':employeeScope,'caution':'This catalogue item itself is not newly accepted merely from matching a period; no duplicate import.'}
  elif kind=='employee-remuneration-candidate':status='located-uncovered-original-delegated-for-actual-period-and-complete-source-review';actual=None;uncovered.append({'itemUuid':r['uuid'],'issuer':r['issuer'],'employerSlug':slug,'catalogueYearDiscoveryOnly':year,'label':label,'assets':assets.get(r['uuid'],[]),'owner':'phsa_history' if slug=='provincial-health-services-authority' else 'health_other_history'})
  elif kind=='named-employee-contract-detail-context':status='actual-original-has-named-employees-components-and-titles-needs-source-compatible-overlap-comparison';actual={'periodEnd':'2011-03-31','physicalPages':'3–11','sourceScope':'Named contract employees earning over$100,000; not merely aggregate headcount.','proof':'fraser-contract-context-retrieval.json'};uncovered.append({'itemUuid':r['uuid'],'issuer':r['issuer'],'employerSlug':slug,'catalogueYearDiscoveryOnly':year,'label':label,'assets':assets.get(r['uuid'],[]),'owner':'health_other_history','scopeQualification':'Actual original personally viewed; named source fields may overlap2010/11 employee schedule. Do not append duplicates or claim no names from page2aggregate alone.'})
  elif kind=='standalone-financial-statements-metadata-only':status='metadata-only-not-assessed-for-named-salary-appendices';actual=None
  elif kind=='separate-board-disclosure':status='separate-board-scope-baseline-subtraction-or-board-workers';actual={'baselineBoardSourceIdsForDiscoveryYear':boardScope,'notEmployeeScope':True}
  else:status='separate-scope-not-imported-as-individual-employee-salary';actual=None
  item={'itemUuid':r['uuid'],'issuer':r['issuer'],'employerSlug':slug,'serialIssueLiteral':r['serialIssue'],'catalogueYearDiscoveryOnly':year,'kind':kind,'disposition':status,'actualSourceResolution':actual,'explicitOriginalLocators':assets.get(r['uuid'],[]),'cataloguePeriodIsNotAcceptanceEvidence':True};out.append(item)
  if kind=='standalone-financial-statements-metadata-only' and not employeeScope and not any(s['item']['employerSlug']==slug and s['item']['candidateYear']==year for s in specs):financeUnassessed.append(item)
 assert len(out)==len(cat)==606 and len({x['itemUuid'] for x in out})==606
 assert len([r for r in uncovered if r['employerSlug']=='provincial-health-services-authority'])==9
 assert len([r for r in uncovered if r['employerSlug']=='northern-health'])==6
 assert len([r for r in uncovered if r['employerSlug']=='island-health'])==3
 assert len(uncovered)==19 and all(r['assets'] for r in uncovered)
 result={'allCapturedItems':606,'allUniqueItemsClassified':True,'metadataLabelClasses':dict(collections.Counter(r['kind'] for r in out)),'sourceSelectionCorrection':'Earlier exact-label selection omitted salaries and the literal misspelling Remeneration. This audit accounts for every captured item, uses all spellings above, and exposes every uncovered labelled employee original as one finite set. No title establishes salary absence.','metadataOnlyFinancialItemsStillRequireActualAppendixReview':len(financeUnassessed),'finiteLocatedUncoveredSalaryOrContractOriginals':uncovered,'items':out,'noOutreach':True,'baseline':{'path':str(basep.relative_to(ROOT)),'sha256':hashlib.sha256(basep.read_bytes()).hexdigest()},'catalogue':{'path':str(catp.relative_to(ROOT)),'sha256':hashlib.sha256(catp.read_bytes()).hexdigest()}}
 p=AREA/'full606-catalogue-label-scope-audit.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');q=AREA/'financial-originals-not-yet-assessed-for-named-scope.json';q.write_text(json.dumps(financeUnassessed,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'items':606,'classes':result['metadataLabelClasses'],'finiteLocatedUncovered':len(uncovered),'financeUnassessed':len(financeUnassessed),'auditSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
