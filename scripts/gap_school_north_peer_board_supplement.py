"""Independent source-first complete board-table comparison; no producer mutations."""
from pathlib import Path
from decimal import Decimal
import copy,gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/salaries/gap-fill-2026-11-02/school_north/reviews/health-board-supplement'
PROD=ROOT/'research/salaries/gap-fill-2026-11-02/health_board_supplement'
COLL=ROOT/'research/salaries/gap-fill-health-board-supplement'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):return json.loads(p.read_text())
def put(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def num(x):return None if x in ('','-',None) else Decimal(str(x).replace(',',''))
def main():
 freeze=js(BASE/'first-read-freeze.json')
 for f in freeze['files']:assert sha(ROOT/f['path'])==f['sha256'],f
 transcript=js(BASE/'first-source-transcript.json');corrected=copy.deepcopy(transcript)
 next(s for s in corrected['sources'] if s['sourceKey']=='fraser-health-2008-09')['rows'][7][2]='12500'
 idx=js(COLL/'sources.json');si={s['id']:s for s in idx['sources']}
 snapshot=BASE/'candidate-observed-first.json.gzip'
 if not snapshot.exists():
  payload={s['sourceKey']:dict(proof=js(PROD/f"gap-health-board-supplement-{s['sourceKey']}-row-review.json"),proofSha256=sha(PROD/f"gap-health-board-supplement-{s['sourceKey']}-row-review.json"),source=si['gap-health-board-supplement-'+s['sourceKey']]) for s in corrected['sources']}
  snapshot.write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False).encode(),mtime=0))
 payload=json.loads(gzip.decompress(snapshot.read_bytes()));diff=[];reports=[]
 for s in corrected['sources']:
  key=s['sourceKey'];proof=payload[key]['proof'];source=payload[key]['source'];allcells=proof['allPrimaryCells'];assert len(s['rows'])==len(allcells)
  for seq,(r,c) in enumerate(zip(s['rows'],allcells),1):
   expected=[r[0],r[1] or None,num(r[2]),num(r[3]),s['physicalPage']];got=c['row'][1:]
   for field,a,z in zip(['name','position','remuneration','expenses','pdfPage'],expected,got):
    if field in ('remuneration','expenses'):z=num(z)
    if a!=z:diff.append(dict(sourceKey=key,sourceRow=seq,field=field,personal=a if not isinstance(a,Decimal) else str(a),candidate=z if not isinstance(z,Decimal) else str(z)))
   if len(r)>4 and num(r[4])!=num(c['expenseInclusivePrintedRowTotal']):diff.append(dict(sourceKey=key,sourceRow=seq,field='inclusiveTotal',personal=r[4],candidate=c['expenseInclusivePrintedRowTotal']))
  printcontrol=proof['printedControlReadings']['pymupdf'];assert printcontrol==proof['printedControlReadings']['poppler']
  for col,lit in zip(['remuneration','expenses','total'],s['printedTotals']):assert num(lit)==num(printcontrol[col]),(key,col)
  assert source['periodEnd']==s['fiscalYearEnded'];assert source['year']==str(int(s['fiscalYearEnded'][:4])-1)+'/'+s['fiscalYearEnded'][2:4]
  numeric=[c['row'] for c in allcells if c['row'][3] is not None];assert [c['row'] for c in allcells]==proof['primaryRows']==proof['secondaryRows'];data=json.loads(gzip.decompress((COLL/source['file']).read_bytes()));assert data==numeric
  assert sha(COLL/source['file'])==source['dataSha256'];assert sha(COLL/source['provenanceFile'])==source['provenanceSha256']
  reports.append(dict(sourceKey=key,allNamedRows=len(allcells),numericPayRows=len(numeric),heldUnknownPayRows=len(allcells)-len(numeric),proofPath=str((PROD/f'gap-health-board-supplement-{key}-row-review.json').relative_to(ROOT)),observedProofSha256=payload[key]['proofSha256'],dataPath=str((COLL/source['file']).relative_to(ROOT)),dataSha256=source['dataSha256'],provenancePath=str((COLL/source['provenanceFile']).relative_to(ROOT)),provenanceSha256=source['provenanceSha256'],sourceSha256=source['sha256'],allPrintedControlsAgreeWithPersonalRead=True,actualFiscalEndAgrees=True))
 result=dict(completeOriginalTables=19,completeNamedRows=194,personalFirstTranscriptSha256=sha(BASE/'first-source-transcript.json'),firstReadFreezeSha256=sha(BASE/'first-read-freeze.json'),candidateFirstSnapshotSha256=sha(snapshot),preCandidateOwnReadingCorrection='Fraser2008/09 sourceRow8 McLeod2500→12500 from fresh400dpi source; immutable first read retained.',reports=reports,differences=diff,noOutreach=True)
 out=BASE/'first-comparison.json'
 if not out.exists():put(out,result)
 else:put(BASE/'comparison-replay.json',result)
 print(json.dumps(diff,indent=2));print('rows',sum(s['allNamedRows'] for s in reports),'numeric',sum(s['numericPayRows'] for s in reports),'held',sum(s['heldUnknownPayRows'] for s in reports))
if __name__=='__main__' and '--final' not in __import__('sys').argv:main()

# The first comparison is intentionally retained. Final acceptance replays current
# candidates against the separately resolved personal transcript.
def final():
 from PIL import Image
 import fitz
 first=js(BASE/'first-read-freeze.json')
 for f in first['files']:assert sha(ROOT/f['path'])==f['sha256']
 snap=json.loads(gzip.decompress((BASE/'candidate-observed-first.json.gzip').read_bytes()))
 personal=js(BASE/'resolved-personal-transcript.json');marks=js(BASE/'post-comparison-original-reread-addendum.json')['sourceFootnoteMarkers']
 packet=js(ROOT/first['sourceOnlyPacket']['path']);sourceby={s['sourceKey']:s for s in packet['sources']};index=js(COLL/'sources.json');idx={s['id']:s for s in index['sources']};reports=[]
 for s in personal['sources']:
  key=s['sourceKey'];desc=sourceby[key];source=idx['gap-health-board-supplement-'+key];proofpath=PROD/f'gap-health-board-supplement-{key}-row-review.json';proof=js(proofpath);cells=proof['allPrimaryCells'];assert len(cells)==len(s['rows']);assert proof['sourceSha256']==source['sha256']==desc['sourceSha256'];assert sha(Path(desc['sourceCachePath']))==source['sha256']
  doc=fitz.open(desc['sourceCachePath'])
  for v in desc['sourceViews']:
   p=ROOT/v['path'];assert sha(p)==v['sha256'];im=Image.open(p).convert('RGB');pix=doc[v['physicalPage']-1].get_pixmap(matrix=fitz.Matrix(200/72,200/72),alpha=False);assert im.size==(pix.width,pix.height) and im.tobytes()==pix.samples
  for seq,(r,c) in enumerate(zip(s['rows'],cells),1):
   assert r[0]==c['row'][1] and (r[1] or None)==c['row'][2],(key,seq,'identity')
   assert num(r[2])==num(c['row'][3]) and num(r[3])==num(c['row'][4]) and s['physicalPage']==c['row'][5],(key,seq,'money/page')
   for field,lit in [('remuneration',r[2]),('expenses',r[3])]:
    raw=c['rawCells'][field].strip(); clean=raw.replace(',','').replace('$','').strip(); assert (clean==lit if lit in ('','-') else num(clean)==num(lit)),(key,seq,field,raw,lit)
   if len(r)>4:
    assert num(r[4])==num(c['expenseInclusivePrintedRowTotal']);assert c['rawCells']['total'].strip().replace(',','')==r[4]
   assert str(c['sourceFootnoteMarker'] or '')==marks.get(key,{}).get(str(seq),''),(key,seq,'marker')
  allrows=[c['row'] for c in cells];assert allrows==proof['primaryRows']==proof['secondaryRows'];assert proof['allSecondaryCells'] and len(proof['allSecondaryCells'])==len(cells)
  for a,z in zip(cells,proof['allSecondaryCells']):
   assert a['row']==z['row'];assert a['rawCells']['remuneration']==z['rawCells']['remuneration'];assert a['rawCells']['expenses']==z['rawCells']['expenses']
  known=[r for r in allrows if r[3] is not None];held=[r for r in allrows if r[3] is None];data=COLL/source['file'];prov=COLL/source['provenanceFile'];assert json.loads(gzip.decompress(data.read_bytes()))==known;assert sha(data)==source['dataSha256'] and sha(prov)==source['provenanceSha256'];assert source['validation']['heldUnknownPayRows']==held;assert source['completeBoardSchedule']==(not held);assert source['completeEmployeeSchedule'] is False;assert source['validation']['compiledPartitionRetained'] is True
  assert source['periodEnd']==s['fiscalYearEnded'];controls=proof['printedControlReadings']['pymupdf'];assert controls==proof['printedControlReadings']['poppler']
  for col,lit in zip(['remuneration','expenses','total'],s['printedTotals']):assert num(lit)==num(controls[col])
  def sm(i):return sum((num(r[i]) for r in allrows if r[i] is not None),Decimal(0))
  residuals={k:str(sm(i)-num(controls[k])) for i,k in [(3,'remuneration'),(4,'expenses')]}
  reports.append(dict(sourceKey=key,sourceSha256=source['sha256'],personallyReadNamedRows=len(cells),numericPayRows=len(known),heldUnknownPayRows=held,sourceExpenseDashRows=[i for i,r in enumerate(s['rows'],1) if r[3]=='-'],sourceExpenseBlankRows=[i for i,r in enumerate(s['rows'],1) if r[3]==''],sourceRemunerationDashRows=[i for i,r in enumerate(s['rows'],1) if r[2]=='-'],allFieldValuesAgree=True,allLiteralMonetaryCellsAgree=True,allFootnoteMarkersAgree=True,allPeriodAndPrintedControlsAgree=True,sourceControlResiduals=residuals,proofPath=str(proofpath.relative_to(ROOT)),proofSha256=sha(proofpath),dataPath=str(data.relative_to(ROOT)),dataSha256=sha(data),provenancePath=str(prov.relative_to(ROOT)),provenanceSha256=sha(prov),firstObservedProofSha256=snap[key]['proofSha256']))
 receipt=dict(reviewerAgent='/root/gap_school_north',scope='Complete personal original-image read of every named board schedule, before candidate/native extraction access:19 source originals/194 literal named observations. Candidate comparison after immutable first reads and additive original rereads.',sourceOnlyFirstReadFreezeSha256=sha(BASE/'first-read-freeze.json'),immutableFirstTranscriptSha256=sha(BASE/'first-source-transcript.json'),firstCandidateSnapshotSha256=sha(BASE/'candidate-observed-first.json.gzip'),preCandidateRereadAddendumSha256=sha(BASE/'pre-candidate-control-reread-addendum.json'),postCandidateRereadAddendumSha256=sha(BASE/'post-comparison-original-reread-addendum.json'),resolvedPersonalTranscriptSha256=sha(BASE/'resolved-personal-transcript.json'),sourceCount=19,all194NamedObservationsAgree=True,numericPayRows=186,heldUnknownPayRows=8,allSourceOriginalHashesAndSuppliedViewsPixelExact=True,allCurrentNormalizedRowsExact=True,noCandidateCorrectionRequired=True,firstPersonalCorrections={'numeric':1,'commaWhitespace':22},qualifications=['Eight source remuneration dashes remain unknown; no invented zero. Full literal named-table evidence retains all194, normalized numeric-pay subset186. Three held observations retain known expenses194,18,1589.71 in evidence.','VCH2023/24 literal expense sum12783 vs printed12781; inclusive total sum387154 vs printed387152. VCH2018/19 known expense sum6235 vs printed6234. Sources unchanged, causes unknown.','VCH printed Total includes expenses and is excluded from remuneration. Null expense cells are missing, not numeric0.','Fraser2004/05 board retainer footnote explicitly covers three quarterly retainers due to changed advance/arrears policy; no annualization.','Definitions on VCH employee count pages apply to the employee schedule; no unsupported expansion of board remuneration definitions.','All compiled partitions retained; no identity/year duplicate equivalence assumed.','Receipt pins exact observed proof/data/provenance bytes. Source metadata may adopt this review additively; changed underlying values require new comparison.'],reports=reports,noOutreach=True)
 dest=BASE/'independent-complete-board-source-review.json';put(dest,receipt);print('FINAL',sha(dest),'19sources194named186numeric8held')
if __name__=='__main__' and '--final' in __import__('sys').argv:final()
