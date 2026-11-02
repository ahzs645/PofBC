#!/usr/bin/env python3
"""Create a frozen manual source-copy receipt from the LIVE people index.
Only root-reviewed original crops and unique monetary witnesses are eligible.
No source observations, periods, exports or disclosed names are rewritten.
"""
import argparse,csv,gzip,hashlib,io,json,pathlib,re,unicodedata
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/source-follow-through-2026-11-02'
PDF='ca0634bec6ffece72903f8dcfb622a6b082526afaf955fadebc80d910ace2258'
SOURCE='rru-sofi-2021-22-employees';EMP='royal-roads-university'
def encoded(x):
 if isinstance(x,float) and x.is_integer():return int(x)
 if isinstance(x,list):return [encoded(z) for z in x]
 if isinstance(x,dict):return {k:encoded(v) for k,v in x.items()}
 return x
def dumpbytes(x):return json.dumps(encoded(x),ensure_ascii=False,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def hashjson(x):return sha(dumpbytes(x))
def namekey(s):
 s=re.split(r'\s{3,}|\t',s)[0].strip();parts=s.split(',')
 def letters(z):return re.sub('[^a-z]','',unicodedata.normalize('NFD',z).lower())
 return letters(parts[0])+'|'+' '.join(z for z in (letters(v) for v in re.split(r'[\s.]+',' '.join(parts[1:]).strip())) if z)
def stable(r,index):return r[:4]+[index['employers'][r[4]][3],index['years'][r[5]],r[6],r[7] if len(r)>7 else None]
def rowhash(r,index):return hashjson(stable(r,index))
def rowshash(rs,index):return hashjson(sorted(rowhash(r,index) for r in rs))
def sourcehash(s):return hashjson([s.get('id'),s.get('url'),s.get('sha256'),s.get('dataSha256'),s.get('year'),s.get('periodType'),s.get('periodStart'),s.get('periodEnd'),s.get('sourceKind'),s.get('scope'),s.get('currency','CAD')])
def cents(z):return None if z is None else int(round(z*100))
def compiled(s):return s.get('sourceKind')=='compiled' or s.get('scope')=='compiled-unverified'
def write_json(p,x):p.write_text(json.dumps(encoded(x),ensure_ascii=False,indent=2)+'\n')
def write_gzip(p,x):p.write_bytes(gzip.compress(dumpbytes(x)+b'\n',mtime=0))

def profile_receipt(kind,index,rows,original,pending):
 base='research/salaries/follow-through-'+kind+'/'
 employer='royal-roads-university' if kind=='rru' else 'college-of-new-caledonia'
 sid='rru-sofi-2021-22-employees' if kind=='rru' else 'cnc-sofi-2023-24-employees'
 oy,cy,count=('2021/22','2020/21',223) if kind=='rru' else ('2023/24','2023/24',312)
 registry=base+'name-crops/receipts.json' if kind=='rru' else 'research/salaries/source-follow-through-2026-11-02/cnc-name-review.json'
 registry_data=json.loads((ROOT/registry).read_text());receipts=registry_data['receipts'];source=index['sources'][sid]
 if kind=='rru':assert source['sha256']==PDF
 at=next(i for i,e in enumerate(index['employers']) if e[3]==employer);rs=[r for r in rows if r[4]==at]
 byname={}
 for r in rs:byname.setdefault(namekey(r[0]),[]).append(r)
 oc=[r for r in rs if r[6]==sid and index['years'][r[5]]==oy]
 cc=[r for r in rs if compiled(index['sources'][r[6]]) and index['years'][r[5]]==cy]
 assert len(oc)==len(cc)==count,(kind,len(oc),len(cc))
 outcomes='research/salaries/source-follow-through-2026-11-02/name-review-original-outcomes.json.gzip'
 pinpaths={outcomes,registry,'research/salaries/compiled-baseline.json.gzip'};decisions=[];holds=[]
 for rec in receipts:
  alias,target=rec['compiledSpelling'],rec['originalSpelling'];ak,tk=namekey(alias),namekey(target);aa=byname.get(ak,[]);tt=byname.get(tk,[])
  cw=[r for r in aa if r in cc and r[0]==alias];ow=[r for r in tt if r in oc and r[0]==target]
  old=[r for r in original if r['employer']==employer and {namekey(r['name_a']),namekey(r['name_b'])}=={ak,tk}]
  assert len(old)<=1;candidate=old[0]['candidate_id'] if old else None
  if len(aa)!=1 or len(cw)!=1 or len(ow)!=1:
   holds.append({'employer':employer,'names':[alias,target],'candidateId':candidate,'reason':f'Complete alias/history witness is not a single exact retained occurrence ({len(aa)} aliases, {len(cw)} compiled witnesses, {len(ow)} original witnesses).'});continue
  cr,orr=cw[0],ow[0];numeric=cr[3] is not None and orr[3] is not None
  match=lambda r:cents(r[2])==cents(orr[2]) and (not numeric or cents(r[3])==cents(orr[3]))
  cm,om=[r for r in cc if match(r)],[r for r in oc if match(r)]
  if cr[2]!=orr[2] or (numeric and cr[3]!=orr[3]) or len(cm)!=1 or len(om)!=1:
   holds.append({'employer':employer,'names':[alias,target],'candidateId':candidate,'reason':f'Monetary witness is not exact and unique in BOTH complete cohorts ({len(cm)} compiled, {len(om)} official).'});continue
  crop=base+rec['cropFile'] if kind=='rru' else rec['cropFile'];page=base+rec['fullPageFile'] if kind=='rru' else rec['fullPageFile']
  normalized=base+'rru-2021-22.json.gzip' if kind=='rru' else rec['sourceDataFile']
  for path,h in [(crop,rec['cropSha256']),(page,rec['fullPageSha256']),(normalized,source['dataSha256'])]:assert sha((ROOT/path).read_bytes())==h,(path,h);pinpaths.add(path)
  if kind=='rru':pinpaths.add(base+'compiled-comparison.json')
  period_reason='Original RRU heading is year ended31March2022. The related223-row compiled cohort retains its2020/21 label; twelve financial occurrences differ on each side. Individual financial witnesses support source-copy spelling only, not wholesale period equivalence, replacement or redating.' if kind=='rru' else 'Original CNC employee schedule explicitly ends31March2024. The compilation also labels the related312-row cohort2023/24, but the compiled edition period remains independently unverified. Monetary copying supports this individual source spelling; neither fiscal-label strings nor any source observation is replaced or redated.'
  proof={'kind':'manual-source-copy-spelling','reviewer':'root','individualCropReviewed':True,'aliasNameKey':ak,'targetNameKey':tk,'retainAllObservations':True,'redateCompiledObservations':False,
   'observations':[{'nameKey':k,'rowCount':len(v),'rowsSha256':rowshash(v,index)} for k,v in [(ak,aa),(tk,tt)]],
   'liveSources':[{'sourceId':s,'sourceSha256':sourcehash(index['sources'][s])} for s in sorted({r[6] for r in aa+tt})],
   'official':{'sourceId':sid,'pdfSha256':source['sha256'],'dataSha256':source['dataSha256'],'sourceUrl':source['url'],'year':oy,'periodType':source['periodType'],'periodStart':source['periodStart'],'periodEnd':source['periodEnd'],'currency':'CAD','rowSha256':rowhash(orr,index),'pdfPage':orr[7],'publishedName':target,'normalizedPath':normalized},
   'compiled':{'normalizedPath':'research/salaries/compiled-baseline.json.gzip','sourceId':cr[6],'sourceSha256':index['sources'][cr[6]]['sha256'],'year':cy,'currency':'CAD','rowSha256':rowhash(cr,index),'pdfPage':cr[7] if len(cr)>7 else None,'publishedName':alias},
   'cohorts':{'official':{'rowCount':count,'rowsSha256':rowshash(oc,index)},'compiled':{'rowCount':count,'rowsSha256':rowshash(cc,index)}},
   'financialWitness':{'mode':'unique-remuneration-and-expenses' if numeric else 'unique-remuneration-only-missing-expense','payCents':cents(orr[2]),'officialExpensesCents':cents(orr[3]),'compiledExpensesCents':cents(cr[3]),'officialOccurrenceCount':1,'compiledOccurrenceCount':1,'nullExpensesEqualZero':False},
   'periodReview':{'officialYear':oy,'compiledYear':cy,'compiledLabelVerified':False,'reason':period_reason},
   'crop':{'path':crop,'sha256':rec['cropSha256'],'fullPagePath':page,'fullPageSha256':rec['fullPageSha256'],'receiptPath':registry,'pdfPage':orr[7],'pdfSha256':source['sha256'],'bboxPoints':rec['bboxPoints'],'printedName':target,'rowSha256':rowhash(orr,index)},'originalOutcomesPath':outcomes}
  supporting=rec.get('earlierNativeSupport')
  if supporting:
   src=index['sources'][supporting['sourceId']];native=supporting['row'];candidate_rows=[r for r in tt if r[6]==supporting['sourceId'] and r[:4]==native[1:5] and r[7]==native[5]];assert len(candidate_rows)==1
   sr=candidate_rows[0];crop_support=supporting['crop'];assert src['sha256']==supporting['pdfSha256'] and src['dataSha256']==supporting['dataSha256']
   pinpaths.update([supporting['dataFile'],crop_support['file']])
   proof['requiresEarlierNativeSpellingSupport']=True
   proof['supportingOriginals']=[{'sourceId':supporting['sourceId'],'pdfSha256':supporting['pdfSha256'],'dataSha256':supporting['dataSha256'],'sourceUrl':supporting['sourceUrl'],'year':supporting['year'],'periodType':src['periodType'],'periodStart':supporting['periodStart'],'periodEnd':supporting['periodEnd'],'currency':'CAD','rowSha256':rowhash(sr,index),'pdfPage':supporting['physicalPdfPage'],'publishedName':target,'normalizedPath':supporting['dataFile'],'cropPath':crop_support['file'],'cropSha256':crop_support['sha256'],'bboxPoints':crop_support['bboxPoints'],'nativeWords':supporting['nativeWordEvidence'],'reason':'Earlier native original clearly distinguishes r+n in the published surname. Later compressed scan and unique financial copy witness remain separately qualified.'}]
  note=f'Individually reviewed original {kind.upper()} source-copy spelling; exact remuneration'+(' and disclosed expenses' if numeric else ' alone, with missing source expenses retained as unknown')+f' is unique in both complete{count}-row cohorts. Original{oy} and compiled{cy} labels and every observation remain unchanged. This connection does not establish a lifetime identity.'
  decisions.append({'employer':employer,'names':[alias,target],'preferredName':target,'decision':'verified','candidateId':candidate,'queueMembership':'original-3173' if old else 'additional-source-copy','note':note,'evidence':[{'sourceId':sid,'pdfPage':orr[7],'url':source['url']+'#page='+str(orr[7]),'title':f'{kind.upper()}{oy} original named employee schedule; individual source crop reviewed'}],'proof':proof})
 if kind=='cnc':
  for r in registry_data.get('reviews',[]):
   if r.get('candidateId') in [1973,1974]:holds.append({'employer':employer,'names':r['names'],'candidateId':str(r['candidateId']),'reason':'Original remuneration113,947 has45 occurrences in each complete312-row cohort; unknown source expenses cannot be equated to compiled0. Keep separate.'})
 trace_path=OUT/f'name-review-{kind}.json'
 initial_index_sha=json.loads(trace_path.read_text()).get('reviewedLiveIndexSha256') if trace_path.exists() else sha((ROOT/'public/salaries/people/index.json').read_bytes())
 payload={'schemaVersion':1,'reviewKind':'manual-source-copy-spelling','reviewedOn':'2026-11-02','reviewer':'root','policy':'Exact source-copy spelling only. All live alias and current target observations and source definitions are pinned. Missing expenses never equal zero. Individual unique financial witnesses do not verify a compiled reporting label or permit replacement/redating.','reviewedLiveIndexSha256':initial_index_sha,'inputs':[{'path':p,'sha256':sha(pending[ROOT/p] if ROOT/p in pending else (ROOT/p).read_bytes())} for p in sorted(pinpaths)],'decisions':decisions,'holds':holds}
 dest=OUT/f'name-review-{kind}.json';pending[dest]=(json.dumps(encoded(payload),ensure_ascii=False,indent=2)+'\n').encode()
 pending[OUT/f'name-review-{kind}-observations.json.gzip']=gzip.compress(dumpbytes({'rowSchema':['name','position','remuneration','expenses','employerSlug','year','sourceId','pdfPage'],'observations':[{'names':d['names'],'aliasRows':[stable(r,index) for r in byname[d['proof']['aliasNameKey']]],'targetRows':[stable(r,index) for r in byname[d['proof']['targetNameKey']]]} for d in decisions]})+b'\n',mtime=0)
 text=io.StringIO(newline='');w=csv.writer(text);w.writerow(['candidate_id','queue_membership','alias','original_spelling','official_year','compiled_label','pay_cents','official_expenses_cents','compiled_expenses_cents','witness_mode','pdf_page','decision'])
 for d in decisions:
  p=d['proof'];m=p['financialWitness'];w.writerow([d['candidateId'],d['queueMembership'],*d['names'],p['official']['year'],p['compiled']['year'],m['payCents'],m['officialExpensesCents'],m['compiledExpensesCents'],m['mode'],p['official']['pdfPage'],d['decision']])
 pending[OUT/f'name-review-{kind}.csv']=text.getvalue().encode()
 return {'profile':kind,'accepted':len(decisions),'originalQueue':sum(d['queueMembership']=='original-3173' for d in decisions),'additional':sum(d['queueMembership']=='additional-source-copy' for d in decisions),'holds':holds,'path':str(dest)}

class UnionFind:
 def __init__(self):self.parents={}
 def find(self,x):
  self.parents.setdefault(x,x)
  if self.parents[x]!=x:self.parents[x]=self.find(self.parents[x])
  return self.parents[x]
 def join(self,a,b):self.parents[self.find(a)]=self.find(b)

def overlay_outputs(pending):
 import collections
 baseline_path='research/salaries/name-links/held-completion-2026-11-02/review-results.json'
 baseline_bytes=(ROOT/baseline_path).read_bytes();baseline=json.loads(baseline_bytes);assert len(baseline)==3173
 baseline_counts=collections.Counter(r['outcome'] for r in baseline)
 assert baseline_counts['connected-verified']==130 and baseline_counts['connected-likely']==25
 all_connections,verified_connections=UnionFind(),UnionFind();linkpins=[]
 for path in sorted((ROOT/'public/salaries/links').glob('*.json.gzip')):
  b=path.read_bytes();linkpins.append({'path':str(path.relative_to(ROOT)),'sha256':sha(b)})
  for slug,key,name,aliases in json.loads(gzip.decompress(b))['links']:
   for alias in aliases:
    if alias[2] not in ['verified','likely']:continue
    left,right=slug+'|'+key,slug+'|'+alias[0];all_connections.join(left,right)
    if alias[2]=='verified':verified_connections.join(left,right)
 decisions=[];decisionfiles=[]
 for kind in ['rru','cnc']:
  path=OUT/f'name-review-{kind}.json';b=pending[path] if path in pending else path.read_bytes();decisionfiles.append({'path':str(path.relative_to(ROOT)),'sha256':sha(b)})
  for d in json.loads(b)['decisions']:decisions.append((str(path.relative_to(ROOT)),d))
 by_candidate={d['candidateId']:(p,d) for p,d in decisions if d['queueMembership']=='original-3173'}
 assert len(by_candidate)==15
 def confidence(employer,names):
  a,b=[employer+'|'+namekey(n) for n in names]
  if verified_connections.find(a)==verified_connections.find(b):return 'verified'
  if all_connections.find(a)==all_connections.find(b):return 'likely'
  return None
 for _,d in decisions:assert confidence(d['employer'],d['names'])=='verified',f'Final published namebuild does not yet include {d["names"]}'
 results=[];changed=[]
 for old in baseline:
  current=confidence(old['employer'],old['names']);before=old['outcome']
  if before=='connected-verified':assert current=='verified',f'Previous verified connection lost: {old["id"]}'
  if before=='connected-likely':assert current in ['verified','likely'],f'Previous likely connection lost: {old["id"]}'
  outcome='connected-verified' if current=='verified' else 'connected-likely' if current=='likely' else before
  if current is None:assert before not in ['connected-verified','connected-likely']
  review=by_candidate.get(str(old['id']))
  public=[]
  for lead in old.get('publicSourceLeads',[]):
   if lead.get('url'):public.append(lead['url']+(f'#page={lead["physicalPage"]}' if lead.get('physicalPage') else ''))
  row={'id':old['id'],'employer':old['employer'],'names':old['names'],'priorOutcome':before,'outcome':outcome,'priorAssessment':old['assessment'],'assessment':old['assessment'],'pending':old.get('pending',current is None) if current is None else False,'currentPublishedConfidence':current,'nextAction':old['nextAction'],'baselineRowSha256':hashjson(old),'publicSources':sorted(set(public))}
  if review:
   file,d=review;row['assessment']='reviewed-original-source-copy-spelling';row['nextAction']='Reviewed original source-copy spelling connection is published. Preserve every raw name, amount, expense, source and reporting label; no compiled observation is replaced or redated.'
   row['sourceFollowThroughReview']={'path':file,'candidateId':d['candidateId'],'names':d['names'],'financialWitnessMode':d['proof']['financialWitness']['mode']};row['publicSources']=sorted(set(row['publicSources']+[e['url'] for e in d['evidence']]))
  elif outcome!=before:
   row['assessment']='current-published-group-after-source-expansion';row['nextAction']='The current published name group establishes the recorded confidence; retain all source-specific observations and prior confidence qualifications.'
  if outcome!=before:changed.append({'id':old['id'],'employer':old['employer'],'names':old['names'],'priorOutcome':before,'outcome':outcome,'manualReview':bool(review)})
  results.append(row)
 counts=collections.Counter(r['outcome'] for r in results);v,l=counts['connected-verified'],counts['connected-likely'];unconnected=3173-v-l
 extras=[{'path':p,'names':d['names'],'employer':d['employer'],'decision':d['decision'],'queueMembership':d['queueMembership']} for p,d in decisions if d['queueMembership']=='additional-source-copy']
 meta={'schemaVersion':1,'reviewedOn':'2026-11-02','scope':'Current overlay of exactly the original3173 reviewed candidate IDs. Three additional source-copy connections are reported separately.','baseline':{'path':baseline_path,'sha256':sha(baseline_bytes),'rows':3173,'verified':130,'likely':25,'unconnected':3018},'current':{'rows':3173,'verified':v,'likely':l,'unconnected':unconnected,'outcomes':dict(sorted(counts.items()))},'changedOriginalCandidates':changed,'additionalReviewedConnections':extras,'nameReviewInputs':decisionfiles,'publishedLinkInputs':linkpins,'preservesAllPriorPublishedConfidence':True,'usesUploadedOutcomeLabelsAsEvidence':False}
 pending[OUT/'name-review-overlay.json']=(json.dumps(meta,ensure_ascii=False,indent=2)+'\n').encode()
 pending[OUT/'review-results.json']=(json.dumps(results,ensure_ascii=False,indent=2)+'\n').encode()
 text=io.StringIO(newline='');w=csv.writer(text);w.writerow(['candidate_id','employer','name_a','name_b','prior_outcome','outcome','prior_assessment','assessment','next_action','public_sources'])
 for r in results:w.writerow([r['id'],r['employer'],*r['names'],r['priorOutcome'],r['outcome'],r['priorAssessment'],r['assessment'],r['nextAction'],' | '.join(r['publicSources'])])
 pending[OUT/'held-pair-outcomes.csv']=text.getvalue().encode()
 lines=['# Current outcomes of the original3173-pair review','', 'This overlay starts from the immutable held-completion review:130 verified,25 likely and3018 unconnected pairs. It derives current confidence from the published name-link graph, retaining every prior verified/likely connection. Uploaded outcome labels are used only to preserve candidate membership, never as identity evidence.','', '| Outcome | Prior review | Current |','| --- | ---: | ---: |',f'| Verified connections |130|{v}|',f'| Likely connections |25|{l}|',f'| Unconnected; kept separate |3018|{unconnected}|','',f'{len(changed)} original candidate outcomes changed;15 have individually reviewed source-copy receipts. The complete original3173 IDs and names remain in [review-results.json](review-results.json) and [held-pair-outcomes.csv](held-pair-outcomes.csv). Raw salary observations, missing expenses, source definitions and period labels remain unchanged.','', 'The11 Royal Roads original-queue spelling cases are supported by the original2021/22 employee schedule while the related compilation keeps its2020/21 label. Four CNC original-queue cases are also accepted:Perlstrom/Per1strom, Rosche/Rasche, Idehen/ldehen and Stuart-Clarke/StuartClar1<e. Stuart-Clarke uses unique remuneration in both312-row cohorts; unknown source expenses remain unknown and the compiled numeric0 remains0.','', 'CNC Maides/Maldes and Rourke/Rour1<e remain separate:113947 remuneration occurs45times in each complete cohort, and unknown expenses cannot be equated to0.','', 'The three additional source-copy connections stay outside the original3173 denominator:','', '| Employer | Compiled spelling | Reviewed original spelling |','| --- | --- | --- |']
 for extra in extras:lines.append('|'+extra['employer']+'|'+extra['names'][0]+'|'+extra['names'][1]+'|')
 lines+=['', 'All18 adopted source-copy connections have pinned individual source crops/pages, normalized source data, exact live alias/current-target histories, source definitions and unique financial witnesses in both complete cohorts. Cornelis and Thorne also require the earlier native2020/21 source crops. These verify the source-copy spellings without claiming lifetime identity or wholesale equivalence between source cohorts.','', 'See [name-review-overlay.json](name-review-overlay.json) for baseline/current counts, every changed original ID, separate extra leads and the exact published graph fingerprints.']
 pending[OUT/'remaining-evidence.md']=('\n'.join(lines)+'\n').encode()
 return meta['current']

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--outcomes',default='/workspace/salary-source-follow-through/provided-held-pair-outcomes.csv');ap.add_argument('--check',action='store_true');ap.add_argument('--overlay',action='store_true');ap.add_argument('--employer',choices=['rru','cnc','all'],default='all');args=ap.parse_args()
 pending={};index=json.loads((ROOT/'public/salaries/people/index.json').read_text())
 if SOURCE not in index['sources']:raise SystemExit('Build live salaries first: official RRU source is absent')
 path=pathlib.Path(args.outcomes);path=path if path.is_absolute() else ROOT/path
 if path.exists():
  csvbytes=path.read_bytes();original=list(csv.DictReader(csvbytes.decode().splitlines()));assert len(original)==3173
  original_snapshot={'schemaVersion':1,'originalFile':'provided-held-pair-outcomes.csv','originalFileSha256':sha(csvbytes),'rowCount':3173,'use':'Candidate membership only; supplied outcomes are not reused as identity evidence. New decisions require individually reviewed original pixels and current unique live witnesses.','rows':original}
 else:original_snapshot=json.loads(gzip.decompress((OUT/'name-review-original-outcomes.json.gzip').read_bytes()));original=original_snapshot['rows']
 pending[OUT/'name-review-original-outcomes.json.gzip']=gzip.compress(dumpbytes(original_snapshot)+b'\n',mtime=0)
 profiles=['rru','cnc'] if args.employer=='all' else [args.employer]
 needed={i for i,e in enumerate(index['employers']) if e[3] in ['royal-roads-university','college-of-new-caledonia']};rows=[]
 for shard in index['shards']:rows.extend(r for r in json.loads(gzip.decompress((ROOT/'public/salaries/people'/f'{shard}.json.gzip').read_bytes())) if r[4] in needed)
 summaries=[profile_receipt(kind,index,rows,original,pending) for kind in profiles]
 if args.overlay or (args.check and (OUT/'name-review-overlay.json').exists()):summaries.append({'overlay':overlay_outputs(pending)})
 for output,data in pending.items():
  if args.check:assert output.exists() and output.read_bytes()==data,f'Name-review output is stale: {output}; root must review changed evidence before reissuing receipts'
  else:output.write_bytes(data)
 print(json.dumps(summaries))
if __name__=='__main__':main()
