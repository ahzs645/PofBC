import gzip,hashlib,json,re
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
ROOT=Path('/workspace/PofBC');AUDIT=ROOT/'research/salaries/held-resolution-2026-11-01/health';REV=AUDIT.parent/'reviews';SOURCE_SHA='809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c'
def digest(b):return hashlib.sha256(b).hexdigest()
LOAD_CACHE={}
def load(p):
 p=Path(p)
 if p not in LOAD_CACHE:LOAD_CACHE[p]=json.loads(p.read_text())
 return LOAD_CACHE[p]
def rows(p):x=json.loads(gzip.decompress(p.read_bytes()));return x if isinstance(x,list) else x['rows']
def targets(flags):
 out=set()
 for f in flags:
  if 'name' in f:out.add('name')
  elif 'pay' in f or 'remuneration' in f:out.add('remuneration')
  elif 'expense' in f:out.add('expenses')
  else:raise AssertionError(('Unknown field conflict',f))
 return out
def norm_name(value):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',value).strip())
def money(value):
 v=''.join(value.split())
 if v in ['-','–','—']:return 'dash',None
 if re.fullmatch(r'(?:\d{1,3}(?:,\d{3})+|\d+)',v):return 'number',int(v.replace(',',''))
 if re.fullmatch(r'\((?:\d{1,3}(?:,\d{3})+|\d+)\)',v):return 'number',-int(v[1:-1].replace(',',''))
 if re.fullmatch(r'-(?:\d{1,3}(?:,\d{3})+|\d+)',v):return 'number',int(v.replace(',',''))
 return 'unparsed',None
SEMANTIC_COUNTS=Counter()
def recheck_fields(r):
 t=r['tesseract'];q=r['rapidocr'];flags=[]
 assert q is not None
 assert r['candidateRow'][1]==norm_name(t['name'])
 if norm_name(t['name'])!=norm_name(q['name']):flags.append('name-disagreement')
 if t['nameConfidence'] is None or t['nameConfidence']<85:flags.append('tesseract-name-confidence-below-85')
 if q['nameConfidence']<.98:flags.append('rapid-name-confidence-below-0.98')
 tk,tv=money(t['pay']['raw']);qk,qv=money(q['pay'][1] if q['pay'] else '')
 assert r['candidateRow'][3]==tv
 if tk!='number' or qk!='number' or tv!=qv:flags.append('remuneration-disagreement-or-unparsed')
 if t['pay']['confidence'] is None or t['pay']['confidence']<90:flags.append('tesseract-pay-confidence-below-90')
 if q['pay'] and q['pay'][2]<.98:flags.append('rapid-pay-confidence-below-0.98')
 ek,ev=money(t['expenses']['raw']);rk,rv=money(q['expenses'][1] if q['expenses'] else '')
 glyph=r['expenseOriginalImage']
 if glyph.get('isExplicitDash'):
  assert glyph['maskSha256']=='884ce82070908630f6df09c8521a1968c09d3350f26e4136c697f86f59974f64' and glyph['templateMatched']
  assert r['candidateRow'][4] is None and glyph['glyphWidth']==9 and glyph['glyphHeight']==2 and glyph['blackPixels']==18
  SEMANTIC_COUNTS['exactSourceDashRows']+=1
 elif ek=='number' and rk=='number' and ev==rv:
  assert r['candidateRow'][4]==ev
  if t['expenses']['confidence'] is None or t['expenses']['confidence']<90:flags.append('tesseract-expense-confidence-below-90')
  if q['expenses'] and q['expenses'][2]<.98:flags.append('rapid-expense-confidence-below-0.98')
 else:
  assert r['candidateRow'][4]==ev;flags.append('expense-disagreement-unparsed-or-unreviewed-glyph')
 assert set(flags)==set(r['conflicts']),(r['physicalPage'],r['sourceRowOnPage'],flags,r['conflicts'])
 for flag in flags:SEMANTIC_COUNTS[flag]+=1
 SEMANTIC_COUNTS['allFieldsIndependentlyReplayedRows']+=1
raw={};pages=[];flagged=set();fidelity=json.loads(gzip.decompress((REV/'independent-phsa-render-fidelity-results.json.gzip').read_bytes()));fmap={p['physicalPage']:p for p in fidelity['pageProof']}
for pn in range(1,285):
 p=Path(f'/tmp/held-health-ocr/full/pages/p{pn:03d}.json.gzip');b=p.read_bytes();e=json.loads(gzip.decompress(b));assert e['physicalPage']==pn and e['sourceSha256']==SOURCE_SHA and not e['pageConflicts'];assert digest(b)==fmap[pn]['rawPageEvidenceSha256'];assert len(e['rowEvidence'])==fmap[pn]['actualBitmapNameBands'];assert len(e['imagePlacements'])>0
 for i,r in enumerate(e['rowEvidence'],1):
  k=(pn,i);assert r['physicalPage']==pn and r['sourceRowOnPage']==i;assert r['candidateRow'][0]=='provincial-health-services-authority' and r['candidateRow'][2] is None and r['candidateRow'][5]==pn;assert r['rapidocr'] is not None;assert abs(r['tesseract']['y']-r['rapidocr']['y'])<16
  recheck_fields(r);raw[k]=r
  if r['conflicts']:flagged.add(k)
 pages.append({'physicalPage':pn,'rows':len(e['rowEvidence']),'sha256':digest(b)})
assert len(raw)==13906 and len(flagged)==3157
batches={digest(p.read_bytes()):(p,load(p)) for p in AUDIT.glob('review-batch-*.json') if not p.name.endswith('-images.json')}
resolved={};proofs=[];reviewpaths=set();overlaypaths=[];changed=Counter();files_checked={}
for path in sorted(AUDIT.glob('manual-overlay-*.json')):
 o=load(path);assert o['sourceSha256']==SOURCE_SHA;reviewinputs={x['path']:x for x in o['reviewInputs']}
 for item in o['overlays']:
  k=(item['physicalPage'],item['sourceRowOnPage']);assert k in flagged and k not in resolved,('Unflagged or overlapping overlay',k);r=raw[k];assert item['rawCandidateRow']==r['candidateRow'];assert item['originalConflicts']==r['conflicts'];assert item['rawPageEvidenceSha256']==pages[k[0]-1]['sha256']
  rp=ROOT/item['reviewReceiptPath'];rb=rp.read_bytes();assert digest(rb)==item['reviewReceiptSha256'];review=load(rp);assert review['sourceSha256']==SOURCE_SHA;assert review['frozenBatchSha256']==item['batchSha256'];batchpath,batch=batches[item['batchSha256']];br=next(v for v in batch['rows'] if (v['physicalPage'],v['sourceRowOnPage'])==k);rr=next(v for v in review['resolutions'] if (v['physicalPage'],v['sourceRowOnPage'])==k)
  assert rr['status']=='resolved-from-original-image';assert set(rr['resolvedValues'])==set(rr['reviewTargetFields'])==set(br['reviewTargetFields'])==targets(r['conflicts']);assert br['candidateRow']==r['candidateRow'];assert rr['cropSha256']==br['cropSha256']==item['cropSha256'];cp=Path(br['cropPath'])
  if str(cp) not in files_checked:files_checked[str(cp)]=digest(cp.read_bytes())
  assert files_checked[str(cp)]==br['cropSha256'];assert digest(Path(br['completePageEvidencePath']).read_bytes())==br['completePageEvidenceSha256']==pages[k[0]-1]['sha256']
  expected=list(r['candidateRow'])
  for f,col in [('name',1),('remuneration',3),('expenses',4)]:
   if f in rr['resolvedValues']:
    expected[col]=rr['resolvedValues'][f]
    if expected[col]!=r['candidateRow'][col]:changed[f]+=1
  assert expected==item['resolvedRow'];assert set(item['reviewedFields'])==targets(r['conflicts']);resolved[k]=expected;reviewpaths.add((str(rp.relative_to(ROOT)),digest(rb)))
 overlaypaths.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'rows':o['resolvedRows']})
missing=sorted(flagged-set(resolved));ordinary={k:resolved.get(k,r['candidateRow']) for k,r in raw.items()};supplementpath=AUDIT/'supplemental-name-amendment-ledger.json';supplements={};supplementproof=[]
if supplementpath.exists():
 ledger=load(supplementpath);assert ledger['sourceSha256']==SOURCE_SHA and ledger['changedNameFields']==44 and ledger['confirmedUnchangedLiteralCases']==3 and ledger['permittedChangedColumns']==[1]
 for inp in ledger['inputLedgers']:
  ip=ROOT/inp['path'];assert digest(ip.read_bytes())==inp['sha256'];sub=load(ip);assert sub['sourceSha256']==SOURCE_SHA
  pins=sub.get('inputs',[])+[sub[k] for k in ['sourceConfirmation','rootAdoption'] if k in sub]
  for pin in pins:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 for amend in ledger['amendments']:
  k=(amend['physicalPage'],amend['sourceRowOnPage']);assert k not in supplements;before=amend['beforeOrdinaryResolvedRow'];after=amend['afterSupplementalRow'];assert ordinary[k]==before and amend['changedColumns']==[1] and amend['changedFields']==['name'];assert [before[i] for i in [0,2,3,4,5]]==[after[i] for i in [0,2,3,4,5]] and before[1]!=after[1];assert amend['rawPageEvidenceSha256']==pages[k[0]-1]['sha256']
  if k==(180,8):
   confirmation=load(ROOT/amend['sourceConfirmation']['path']);adoption=load(ROOT/amend['rootAdoption']['path']);assert before==confirmation['rawCandidateRow'] and after==confirmation['proposedSourceCorrectedRow'];assert adoption['beforeName']==before[1] and adoption['afterName']==after[1]
  else:
   primary=load(REV/'independent-phsa-supplemental-case-proposals.json');peer=load(REV/'independent-phsa-supplemental-name-education-confirmations.json');adoption=load(REV/'root-phsa-supplemental-name-adoption.json');assert digest((REV/'independent-phsa-supplemental-case-proposals.json').read_bytes())==amend['sourcePrimaryReviewSha256'];assert digest((REV/'independent-phsa-supplemental-name-education-confirmations.json').read_bytes())==amend['sourceIndependentReviewSha256'];assert digest((REV/'root-phsa-supplemental-name-adoption.json').read_bytes())==amend['rootAdoptionSha256'];case=next(v for v in primary['changes'] if (v['physicalPage'],v['sourceRowOnPage'])==k);assert case['afterOrdinaryOverlays']==before and case['proposedCorrectedRow']==after and digest(Path(case['actualCropPath']).read_bytes())==case['actualCropSha256']==amend['actualCropSha256'];peercase=next(v for v in peer['changes'] if(v['physicalPage'],v['sourceRowOnPage'])==k);assert peercase['beforeRow']==before and peercase['confirmedRow']==after and peercase['actualCropSha256']==case['actualCropSha256'];adoptcase=next(v for v in adoption['cases'] if(v['physicalPage'],v['sourceRowOnPage'])==k);assert adoptcase['beforeRow']==before and adoptcase['afterRow']==after
  supplements[k]=after
 for unchanged in ledger['confirmedUnchanged']:
  k=(unchanged['physicalPage'],unchanged['sourceRowOnPage']);assert ordinary[k]==unchanged['beforeRow']==unchanged['confirmedRow'];assert k not in supplements;assert digest(Path(unchanged['actualCropPath']).read_bytes())==unchanged['actualCropSha256']
 supplementproof={'path':str(supplementpath.relative_to(ROOT)),'sha256':digest(supplementpath.read_bytes()),'changedNameFields':len(supplements),'confirmedUnchanged':len(ledger['confirmedUnchanged'])}
final=[supplements.get(k,ordinary[k]) for k in raw]

report={'independentFieldReplayCounts':dict(SEMANTIC_COUNTS),'physicalPages':len(pages),'namedRows':len(raw),'rawFlaggedRows':len(flagged),'reviewResolvedRows':len(resolved),'missingReviewRows':len(missing),'firstMissingReviewRows':missing[:10],'ordinaryChangedFields':dict(changed),'supplementalAmendmentLedger':supplementproof,'totalChangedRowsFromRawCandidate':sum(final[i]!=r['candidateRow'] for i,r in enumerate(raw.values())),'sumRemuneration':sum(r[3] or 0 for r in final),'sumKnownExpenses':sum(r[4] or 0 for r in final),'nullExpenses':sum(r[4] is None for r in final),'zeroExpenses':sum(r[4]==0 for r in final),'negativeExpenses':sum(r[4] is not None and r[4]<0 for r in final),'reviewInputs':[{'path':p,'sha256':h} for p,h in sorted(reviewpaths)],'overlays':overlaypaths}
if not missing:
 assert all(isinstance(r[1],str) and r[1] and type(r[3]) in (int,float) and (r[4] is None or type(r[4]) in (int,float)) for r in final)
 sourcefolder=ROOT/'research/salaries/held-resolution-health';manifest=load(sourcefolder/'sources.json');source=next((s for s in manifest['sources'] if s['year']=='2024/25' and s['scope']=='employee-remuneration'),None)
 if source is None:
  report['sourcePayloadPending']=True;Path('/tmp/independent-phsa-render-fidelity/source-closure-replay.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0)
 payload=rows(sourcefolder/source['file']);assert payload==final;assert digest((sourcefolder/source['file']).read_bytes())==source['dataSha256'];assert source['rowCount']==len(final) and source['sha256']==SOURCE_SHA;assert source['periodStart']=='2024-04-01' and source['periodEnd']=='2025-03-31';assert source.get('completeEmployeeSchedule') is True
 val=source['validation'];provenancepath=sourcefolder/val['rowProvenanceFile'];assert digest(provenancepath.read_bytes())==val['rowProvenanceSha256'];provenance=json.loads(gzip.decompress(provenancepath.read_bytes()));assert provenance['sourceSha256']==SOURCE_SHA and len(provenance['rows'])==len(final);assert [r['row'] for r in provenance['rows']]==final
 for item,(key,r) in zip(provenance['rows'],raw.items()):
  assert item['sourceRowOnPage']==key[1] and item['originalRawConflicts']==r['conflicts'];assert item['rawPageEvidenceSha256']==pages[key[0]-1]['sha256'];assert digest((sourcefolder/item['rawPageEvidenceFile']).read_bytes())==item['rawPageEvidenceSha256'];assert item['sourceImageSha256']==fmap[key[0]]['nativeImageSha256'];assert bool(item['originalImageReview'])==(key in flagged);assert bool(item['supplementalSourceNameAmendment'])==(key in supplements)
 manifestpath=sourcefolder/val['completeRawPageManifest'];assert digest(manifestpath.read_bytes())==val['completeRawPageManifestSha256'];rawmanifest=load(manifestpath);assert rawmanifest['sourceSha256']==SOURCE_SHA and len(rawmanifest['pages'])==284
 for p in rawmanifest['pages']:assert digest((ROOT/p['file']).read_bytes())==p['sha256']==pages[p['physicalPage']-1]['sha256']
 assert source['totalRemuneration']==report['sumRemuneration'] and source['totalExpenses']==report['sumKnownExpenses'];assert source['threshold']==75000 and source['thresholdComparison']=='>' and source['currency']=='CAD';assert val['remainingUnresolvedRows']==0 and val['rowBoundaryExceptions']==0 and val['imageReviewedConflictRows']==3157 and val['supplementalNameOnlyCorrections']==44 and val['actualPaintedSourceFieldExceptions']==0
 report['completeRowProvenanceSha256']=val['rowProvenanceSha256'];report['completeRawPageManifestSha256']=val['completeRawPageManifestSha256'];report['everyCommittedRawPageEqualsReviewedRawEvidence']=True;report['all13906ProvenanceRowsEqualFinalSourceRows']=True
 report['sourceId']=source['id'];report['sourceManifestSha256']=digest((sourcefolder/'sources.json').read_bytes());report['sourceDataSha256']=source['dataSha256'];report['sourceOriginalSha256']=source['sha256'];report['controls']={'printedRemuneration':1713046476,'printedExpenses':25171641,'literalPayResidual':report['sumRemuneration']-1713046476,'literalExpenseResidual':report['sumKnownExpenses']-25171641}
 report['sourceNotes']=source['notes'];report['sourceWarning']=source.get('publicWarning');report['minimumPay']=min(r[3] for r in final)

 baseline=json.loads(gzip.decompress((AUDIT.parent/'baseline.json.gzip').read_bytes()));oldgroups=[g for g in load(AUDIT.parent/'baseline-row-fingerprints.json')['groups'] if g['employerSlug']=='provincial-health-services-authority'];index=load(ROOT/'public/salaries/employers/index.json');export=rows(ROOT/'public/salaries/employers/provincial-health-services-authority.json.gzip');published=defaultdict(list)
 for r in export:published[(index['years'][r[4]],r[5])].append([r[0],r[1],r[2],r[3],r[6]])
 def fingerprint(rs):
  keys=[json.dumps([r[0],r[1],int(Decimal(str(r[2]))*100),None if r[3] is None else int(Decimal(str(r[3]))*100),r[4]],ensure_ascii=False,separators=(',',':')) for r in rs]
  return digest('\n'.join(sorted(keys,key=lambda x:x.encode())).encode())
 for g in oldgroups:
  current=published[(g['year'],g['sourceId'])];assert len(current)==g['rows'] and fingerprint(current)==g['rowMultisetSha256'];assert index['sources'][g['sourceId']]==baseline['sources'][g['sourceId']]
 report['baselinePhsaPreservation']={'sourcePeriodGroups':len(oldgroups),'officialRows':sum(g['rows'] for g in oldgroups if g['sourceKind']=='official'),'compiledRows':sum(g['rows'] for g in oldgroups if g['sourceKind']=='compiled'),'allLiteralRowsAndSourceMetadataUnchanged':True}
 regressions=[]
 for pn,rn,field,expected in [(104,2,'remuneration',95479),(67,3,'remuneration',99210),(71,1,'remuneration',99953),(51,39,'expenses',7487),(58,9,'expenses',2717),(95,37,'expenses',2777)]:
  row=final[list(raw).index((pn,rn))];col={'remuneration':3,'expenses':4}[field];assert row[col]==expected;regressions.append({'physicalPage':pn,'sourceRowOnPage':rn,'name':row[1],'field':field,'value':row[col]})
 report['verifiedMoneyRegressions']=regressions
 fixture=rows(ROOT/'research/salaries/recovery-wave-2026-11-01/health/phsa-2024-25-page-1-staged.json.gzip');assert final[:49]==fixture;report['priorIndependentFirstPage49RowsExactlyMatch']=True
 reproduced=gzip.compress(json.dumps(final,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);assert reproduced==(sourcefolder/source['file']).read_bytes();report['independentlyReproducedGzipPayloadBytesExactly']=True
 Path('/tmp/independent-phsa-render-fidelity/final-source-rows.json.gzip').write_bytes(reproduced)
Path('/tmp/independent-phsa-render-fidelity/source-closure-replay.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['reviewInputs','overlays','sourceNotes']}))
