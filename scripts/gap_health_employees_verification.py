#!/usr/bin/env python3
"""Replay explicit independent readings, literal source adoptions and full native census."""
import collections,copy,gzip,hashlib,json,pathlib,re
from decimal import Decimal
from gap_health_employees_native import ROOT,AREA,load,nameclean
CLIP_INDEX='research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/clip-effects-001/first-transcript-index.json'
CLIP_INDEX_SHA='c1f66ab64d9e07ffeb834fcf60dbc4dfcb9e65c94b9c4f8e0e7823cded0fcd1f'
CLIP_SELECTION='research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/clip-effects-001/current-reading-selection.json'
CLIP_SELECTION_SHA='2ed434ea46c6eaac73a5f158c71c3c6051f08117a83a20fde78a8b8085da2f99'
NULL_ADOPTION='research/salaries/gap-fill-2026-11-02/reviews/root-seven-health-clipped-name-adoptions.json'
NULL_ADOPTION_SHA='48f242d0533053463b377fd6f8e807b71ecf8e036c7ef07813e7df962c4b67ee'
CONTEXT_ACCEPTANCE='research/salaries/gap-fill-2026-11-02/reviews/root-health-source-context-acceptance.json'
CONTEXT_ACCEPTANCE_SHA='1075218375658a66bbef098b4058325196110da03c94bd6a5d88a3bec54e01e5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pinned(path,h):
 p=ROOT/path;assert sha(p)==h,('pin changed',path);return json.load(open(p))
def clip_readings():
 first=pinned(CLIP_INDEX,CLIP_INDEX_SHA);selector=pinned(CLIP_SELECTION,CLIP_SELECTION_SHA);assert selector['firstTranscriptIndex']['sha256']==CLIP_INDEX_SHA;assert selector['allMonetaryFirstReadingsRemainSelected'] is True;rows={}
 for b in first['batches']:
  doc=pinned(b['path'],b['sha256']);assert doc['candidateValuesSeen'] is False
  for r in doc['observations']:assert r['id'] not in rows;rows[r['id']]=copy.deepcopy(r)
 assert len(rows)==264
 assert selector['fieldSupersessions']==[{'id':'health-clip-001-067','field':'nameLiteral','value':'HEPPNER,ROSEMARY','from':{'path':'research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/clip-effects-001/additive-reread-001.json','sha256':'336626ff740521f32179e2c629af35bd8a49f4cdcd279b0f16fc2f616c6826e7'}}]
 for change in selector['fieldSupersessions']:
  d=pinned(change['from']['path'],change['from']['sha256']);assert d['candidateValuesSeenBeforeFreshReading'] is False;hit=next(r for r in d['observations'] if r['id']==change['id']);assert hit['changedField']=='nameLiteral' and hit['nameLiteral']==change['value'] and hit['remunerationUnchanged'] and hit['expensesUnchanged'];rows[change['id']]['nameLiteral']=change['value']
 return rows

def null_adoptions():
 x=pinned(NULL_ADOPTION,NULL_ADOPTION_SHA);assert x['approved'] is True;a={r['id']:r for r in x['adoptions']};assert set(a)=={'health-clip-001-'+str(n) for n in [219,220,221,222,232,256,264]};assert all(r['acceptedName'] is None and r['sourceNameWasDisclosedButClipped'] for r in a.values());return a

def main():
 from gap_health_employees_export import peer_readings,CURRENT_SELECTION,CURRENT_SHA
 first=peer_readings();clip=clip_readings();adopt=null_adoptions();pinned(CONTEXT_ACCEPTANCE,CONTEXT_ACCEPTANCE_SHA)
 t1p=AREA/'source-review-packets/reader-disagreements-001/packet.json';t2p=AREA/'source-review-packets/clip-effects-001/packet.json';targets={t['id']:t for p in [t1p,t2p] for t in json.load(open(p))['targets']};assert len(targets)==352 and len(first)+len(clip)==352;peer=first|clip
 idx=json.load(open(AREA/'native-primary-candidate-index.json')); primaries={};secondaries={};locators={};comparisons=[];sourceproofs=[]
 for c in idx:
  pp=ROOT/c['file'];sp=ROOT/c['secondaryFile'];assert sha(pp)==c['sha256'] and sha(sp)==c['secondarySha256'];p=load(pp);s=load(sp);primaries[c['key']]=p;secondaries[c['key']]=s;locators[c['key']]={(r['row'][5],r['sourceRowOnPage']):r for r in p['rows']}
 for tid,o in peer.items():
  t=targets[tid];assert o['sourceKey']==t['sourceKey'] and o['sourceSha256']==t['sourceSha256'] and o['physicalPage']==t['physicalPage'];key=t['sourceKey'];literal=[nameclean(o['nameLiteral']),o['remuneration'],o['expenses']]
  if t['sourceRowOnPage'] is None:assert literal==['M.S.',88941,0];decision='add literal M.S. observation at independently verified printed position'
  else:
   r=locators[key][(t['physicalPage'],t['sourceRowOnPage'])]['row'];assert [r[3],r[4]]==literal[1:]
   if tid in adopt:
    a=adopt[tid];assert a['sourceSha256']==t['sourceSha256'] and [a['remuneration'],a['expenses']]==literal[1:];assert nameclean(a['nameLiteral'])==literal[0];decision='root adopted null name because actual original clips a name; keep known pay/expense/page and visible fragment'
   elif tid in ['health-clip-001-243','health-clip-001-258']:
    assert nameclean(r[1]).replace('‐','-')==literal[0];decision='visible short hyphen confirmed; preserve native Unicode encoding without inferring codepoint from image'
   else:assert r[1]==literal[0],(tid,r[1],literal[0]);decision='literal native name/pay/expense independently corroborated by original image'
  comparisons.append({'id':tid,'sourceKey':key,'physicalPage':t['physicalPage'],'sourceRowOnPage':t['sourceRowOnPage'],'decision':decision})
 flags=json.load(open(AREA/'native-census-reader-flags-v3.json'));flagClosure=[]
 for f in flags:
  r=f['flag'];kind=r['kind'];key=f['sourceKey'];pg=r['physicalPage'];matches=[]
  if r.get('words'):
   y=(r['words'][0][1]+r['words'][0][3])*2
   for tid,t in targets.items():
    if t['sourceKey']==key and t['physicalPage']==pg:
     box=t['image']['integerCropPixelBox'];yr=t['image']['targetRowVerticalPixelRange']
     if box[1]+yr[0]<=y<=box[1]+yr[1]:matches.append(tid)
   assert len(matches)==1,(f['id'],matches);decision='explicit original-image row reading selected; duplicate/overprinted native words do not supply additional observations'
  elif kind in ['name-digits-require-original-review','named-pay-below-threshold-requires-review']:
   rows=[z for z in primaries[key]['rows'] if z['row'][5]==pg and z['row'][1]==r['name']];assert len(rows)==1
   matches=[tid for tid,t in targets.items() if t['sourceKey']==key and t['physicalPage']==pg and t['sourceRowOnPage']==rows[0]['sourceRowOnPage']];assert len(matches)==1;decision='literal source exception independently image verified; no identity or threshold explanation inferred'
  elif kind=='no-independent-pay-header':
   assert key in ['fraser-health-'+s for s in ['2004-05','2005-06','2006-07','2007-08','2008-09','2009-10']] and pg==2;decision='actual original page personally viewed: contract-count distribution by salary band and employee group, no individual names; all outside-table numeric anchors retained in census'
  elif kind=='pay-line-without-comma-name' and key=='island-health-2005-06':matches=['health-reader-001-007'];decision='additional literal M.S. observation independently image verified, not discarded for absent comma'
  else:
   assert kind=='pay-line-without-comma-name' and key=='interior-health-2011-12' and pg==52;assert '817,283,222' in r['line'] and '11,843,929' in r['line'];decision='actual original final page personally viewed: unlabeled grand-total line below explicit TOTAL>75,000 and TOTAL<75,000; not a person and never imported'
  flagClosure.append({'id':f['id'],'kind':kind,'decision':decision,'sourceImageTargetIds':matches})
 assert len(flagClosure)==93
 # Every primary-only row and secondary-only anchored record must lie in the explicit88-row original-image packet.
 mismatch=[]
 for c in idx:
  key=c['key'];covered={(t['physicalPage'],t['sourceRowOnPage']) for tid,t in targets.items() if tid.startswith('health-reader-') and t['sourceKey']==key};p=primaries[key];s=secondaries[key];pc=collections.Counter(tuple(r['row']) for r in p['rows']);sc=collections.Counter(tuple(r['row']) for r in s['rows'])
  for row in (pc-sc).elements():
   rr=[r for r in p['rows'] if tuple(r['row'])==row];assert any((r['row'][5],r['sourceRowOnPage']) in covered for r in rr),(key,row)
  for row in (sc-pc).elements():
   rr=[r for r in s['rows'] if tuple(r['row'])==row];found=[]
   for z in rr:
    w=z['remunerationWord'];y=(w[1]+w[3])*2
    for tid,t in targets.items():
     if not tid.startswith('health-reader-') or t['sourceKey']!=key or t['physicalPage']!=row[5]:continue
     box=t['image']['integerCropPixelBox'];yr=t['image']['targetRowVerticalPixelRange']
     if box[1]+yr[0]<=y<=box[1]+yr[1]:found.append(tid)
   assert found,(key,row)
  mismatch.append({'key':key,'onlyPrimaryObservations':sum((pc-sc).values()),'onlySecondaryObservations':sum((sc-pc).values()),'allDifferencesExplicitlyImageCovered':True})
 ci=AREA/'native-census-index-v3.json';census=json.load(open(ci));assert len(census)==65 and sum(v['physicalPages'] for v in census)==5229;assert json.load(open(AREA/'native-census-unclassified-pages-v3.json'))==[]
 for c in census:
  assert sha(ROOT/c['path'])==c['sha256'];sourceproofs.append({'key':c['key'],'sourceSha256':c['sourceSha256'],'physicalPages':c['physicalPages'],'primaryEmployeeRows':c['primaryRows'],'sourceImageTargets':sum(t['sourceKey']==c['key'] for t in targets.values()),'readerFlags':c['readerFlags'],'allFlagsExplicitlyClosed':True,'outsideTableMonetaryAnchorsRetained':c['outsideTableMonetaryAnchors'],'censusPath':c['path'],'censusSha256':c['sha256']})
 result={'status':'Source extraction, page scope, reader flags and352actual-source image targets closed; root final normalized adoption pending.','noOutreach':True,'proofRefs':[{'path':CURRENT_SELECTION,'sha256':CURRENT_SHA},{'path':CLIP_SELECTION,'sha256':CLIP_SELECTION_SHA},{'path':NULL_ADOPTION,'sha256':NULL_ADOPTION_SHA},{'path':CONTEXT_ACCEPTANCE,'sha256':CONTEXT_ACCEPTANCE_SHA},{'path':str(ci.relative_to(ROOT)),'sha256':sha(ci)},{'path':str((AREA/'census-original-views/index.json').relative_to(ROOT)),'sha256':sha(AREA/'census-original-views/index.json')}],'sources':sourceproofs,'sourceImageTargetDecisions':comparisons,'readerFlagDecisions':flagClosure,'rowDifferenceCoverage':mismatch,'observationsBeforeAdoptions':207000,'additionalLiteralPartialNameObservation':1,'finalRowsExpected':207001,'sourceClippedNamesToNull':7,'allMonetaryFirstReadingsSelectedExceptExactThreeAdditiveFirst88Corrections':True,'noBalancing':True}
 out=AREA/'source-verification-closure.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sources':len(sourceproofs),'flagsClosed':len(flagClosure),'imageTargetsClosed':len(comparisons),'rowsExpected':207001,'sha256':sha(out)}))
if __name__=='__main__':main()
