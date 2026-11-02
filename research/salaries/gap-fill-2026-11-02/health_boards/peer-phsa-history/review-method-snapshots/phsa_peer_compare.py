import sys,json,gzip,hashlib,re,collections
from pathlib import Path
R=Path('/workspace/PofBC');sys.path.insert(0,str(R/'scripts'));import gap_phsa_history_readers as readers
A=R/'research/salaries/gap-fill-2026-11-02';O=A/'health_boards/peer-phsa-history';C=A/'phsa_history'
def load(p):return json.loads(gzip.decompress(p.read_bytes()))if p.suffix=='.gzip'else json.loads(p.read_bytes())
def pin(p):return{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def norm(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip())
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
cell=load(O/'independent-source-calibrated-expense-cells-v1.json.gzip');census=load(O/'independent-complete-cell-census-v2.json.gzip');selector=load(O/'current-source-reading-selection.json');res={'sourceReadingFreeze':pin(O/'first-two-scans-first-reading-freeze.json'),'sourceReadingSelector':pin(O/'current-source-reading-selection.json'),'independentCensus':pin(O/'independent-complete-cell-census-v2.json.gzip'),'independentCompleteCellGlyphs':pin(O/'independent-source-calibrated-expense-cells-v1.json.gzip'),'candidateAccessAfterAll577PersonalReadingsLocked':True,'nameComparisonNormalization':'Only collapse whitespace and spacing adjacent to comma; no letters, digits, case, punctuation or Unicode identity folding.','sources':[],'noOutreach':True}
for key in ['phsa-2009-10','phsa-2010-11']:
 sp=C/(key+'-scan-selected-v4.json.gzip');sel=load(sp);cp=C/(key+'-scan-candidate-'+sel['candidateRevision']+'.json.gzip');cand=load(cp);assert pin(cp)['sha256']==sel['candidateSha256'];first=[]
 for p in sorted((O/key).glob('first-transcript-???.json')):first+=load(p)['observations']
 for addon in [key+'-v4-adaptive-v1',key+'-v4-adaptive-v3']:
  p=O/addon/'first-transcript.json'
  if p.exists():first+=load(p)['observations']
 first={r['sequence']:r for r in first}
 for rev in selector['selection']:
  if rev['sourceKey']==key:first[rev['sequence']]={**first[rev['sequence']],'nameLiteral':rev['newNameLiteral']}
 ss={r['sequence']:r['selected']for r in sel['rows']};assert list(ss)==list(range(1,len(ss)+1));dis=[]
 for seq,r in first.items():
  expected=ss[seq]
  for f,g in [('nameLiteral','name'),('remuneration','remuneration'),('expenses','expenses'),('physicalPage','pdfPage')]:
   if(norm(r[f])!=norm(expected[g]))if f=='nameLiteral'else(r[f]!=expected[g]):dis.append({'sequence':seq,'field':f,'peer':r[f],'candidate':expected[g]})
 cells=next(s for s in cell['sources']if s['sourceKey']==key);cc=next(s for s in census['sources']if s['sourceKey']==key);glitches=[]
 for p in cells['pages']:
  for r in p['cells']:
   e=ss[r['sequence']]
   if(r['expenseCellClass']=='source-calibrated-dash')!=(e['expenses']is None)or e['pdfPage']!=p['physicalPage']:glitches.append({'sequence':r['sequence'],'class':r['expenseCellClass'],'selected':e})
 rawchecks=[];cr={r['sequence']:r for r in cand['rows']};prof=cand['profile'];engines=collections.Counter()
 for pg in cand['pages']:
  rp=R/pg['rawPath'];raw=load(rp);assert pin(rp)['sha256']==pg['rawSha256'];assert raw['sourceSha256']==sel['sourceSha256'];raster=Path(raw['sourceImageCachePath']);assert hashlib.sha256(raster.read_bytes()).hexdigest()==raw['sourceImageSha256']==pg['sourceImageSha256'];d={**raw,'sourceId':raw['key'],'yearFromInventory':raw['key'][5:],'renderer':{'imageDimensions':[raw['imageWidth'],raw['imageHeight']]},'sourceImagePath':raw['sourceImageCachePath'],'rapidocrRaw':raw['rapidOcrRaw']};foot=pg['pageFooterWords'];pp={**prof,'sourceLegalFooterTop':min(w['box'][1]for w in foot)if foot else prof['sourceLegalFooterTop']};one,tot1,err1=readers.read_tesseract(d,pp);two,tot2,err2=readers.read_rapid(d,pp);assert canon(err1+err2)==canon(pg['readerErrors']);assert canon(tot1)==canon(pg['totalsTesseract']);assert canon(tot2)==canon(pg['totalsRapid']);assert len(one)==pg['tesseractCount']and len(two)==pg['rapidCount'];counts={}
  for engine,values in [('tesseract',one),('rapid',two)]:
   a=collections.Counter(canon(v)for v in values);b=collections.Counter(canon(cr[n][engine])for n in pg['rows']if cr[n][engine]is not None);b.update(canon(v)for v in pg['outsidePaintedNameBands'][engine]);assert a==b,(key,pg['physicalPage'],engine,'raw-reader rows lost/changed/duplicated');counts[engine]=len(values);engines[engine]+=len(values)
  independent=next(p for p in cc['pages']if p['physicalPage']==pg['physicalPage']);assert independent['independentBandCount']==pg['actualNameBandCount'];rawchecks.append({'physicalPage':pg['physicalPage'],'rawCapture':pin(rp),'sourceRasterSha256':raw['sourceImageSha256'],'bothRawReadersReplayedExactly':True,'completeReaderRowsPreservedWithMultiplicity':True,'rawReaderCounts':counts,'independentPaymentBandCount':independent['independentBandCount']})
 assert not dis,dis;assert not glitches,glitches;pay=sum(v['remuneration']for v in ss.values());exp=sum(v['expenses']or 0 for v in ss.values());printed={'phsa-2009-10':(217818830,4433493),'phsa-2010-11':(237473281,5486042)}[key]
 res['sources'].append({'sourceKey':key,'sourceSha256':sel['sourceSha256'],'selected':pin(sp),'candidate':pin(cp),'selectedRows':len(ss),'personalSourceFirstFullRowsCompared':len(first),'allPersonallyReadNamesMoneyAndPagesAgree':True,'personalSourceReadingUncertainties':[{'sequence':n,'uncertainty':r['uncertainty']}for n,r in first.items()if r['uncertainty']],'allSelectedExpensesIndependentlyMatchEveryCompleteSourceCellClass':True,'allIndependentPaymentBandCountsAgree':True,'bothCompleteRawReadersReplayedExactly':True,'rawReaderCounts':dict(engines),'pages':rawchecks,'literalComputedTotals':{'remuneration':pay,'expenses':exp},'personallySourceReadPrintedTotals':{'remuneration':printed[0],'expenses':printed[1]},'residuals':{'remuneration':pay-printed[0],'expenses':exp-printed[1]},'qualification':'Paired complete independent OCR/raster capture with complete original payment-band/expense-cell census and finite image-first personal flag/holdout/calibration review. This does not claim complete personal monetary transcription, exact printed-total reconciliation, infallible OCR, inferred missing amount or a source-error cause. Literal discrepancies remain public warnings; no amount adjusted to balance.'})
p=O/'independent-first-two-scans-comparison-v1.json';assert not p.exists();p.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(str(p),pin(p)['sha256']);print(json.dumps([{k:v for k,v in s.items()if k not in ['pages','personalSourceReadingUncertainties']}for s in res['sources']],indent=2))
