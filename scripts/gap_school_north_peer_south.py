#!/usr/bin/env python3
"""Compare immutable personal source-first school peer transcripts, additively."""
import argparse,gzip,hashlib,json,re
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
OWN=ROOT/'research/salaries/gap-fill-2026-11-02/school_north/reviews/south35-38'
SOUTH=ROOT/'research/salaries/gap-fill-2026-11-02/school_south'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gzip') else b)
def numeric(s):
 if isinstance(s,str):s=re.sub(r'\s+\(\d+\)$','',s)
 if s is None or s=='-':return None
 return Decimal(re.sub(r'[,\s$*]','',str(s)))
def text(s):return None if s is None else re.sub(r'\s*,\s*',', ',re.sub(r'\s+',' ',s).strip())
def transcript(path):
 out={}
 for line in path.read_text().splitlines():
  if not line or line.startswith('#'):continue
  seq,name,role,pay,expense=line.split('|');assert int(seq) not in out
  out[int(seq)]={'name':name,'position':None if role=='NULL' else role,'remuneration':pay,'expenses':expense}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--district',type=int,choices=[35,38],required=True);ap.add_argument('--final',action='store_true');args=ap.parse_args();n=args.district
 if args.final:return final_acceptance(n)
 checkpoint=read(OWN/f'sd{n}-source-first-checkpoint.json');first=OWN/f'sd{n}-first-source-transcript.txt'
 assert sha(first.read_bytes())==checkpoint['firstPersonalTranscriptSha256']
 packet=read(SOUTH/f'sd{n}-scan-source-only-peer-packet.json');pin=packet['candidateSnapshot'];candidate=Path(pin['path']);assert sha(candidate.read_bytes())==pin['sha256'];x=read(candidate);source=transcript(first);targets={t['sequence']:t for t in packet['targets']}
 differences=[]
 for seq,r in source.items():
  c=x['rows'][seq-1];diff={}
  for field in ['name','position','remuneration','expenses']:
   norm=numeric if field in ['remuneration','expenses'] else text
   if norm(r[field])!=norm(c[field]):diff[field]={'firstPersonalSourceRead':r[field],'candidate':c[field]}
  expected_page=targets[seq]['physicalPage'] if seq in targets else packet['salaryPages'][0]
  if c['pdfPage']!=expected_page:diff['pdfPage']={'source':expected_page,'candidate':c['pdfPage']}
  if diff:differences.append({'district':n,'sequence':seq,'physicalPage':expected_page,'differences':diff})
 out={'district':n,'sourceFirstCheckpoint':{'file':str((OWN/f'sd{n}-source-first-checkpoint.json').relative_to(ROOT)),'sha256':sha((OWN/f'sd{n}-source-first-checkpoint.json').read_bytes())},'firstSourceTranscriptSha256':sha(first.read_bytes()),'candidateSnapshot':{'file':str(candidate.relative_to(ROOT)),'sha256':sha(candidate.read_bytes())},'personallyReadRows':len(source),'differences':differences,'sourceOnlyFlagAndHoldoutProtocol':True,'noOutreach':True}
 path=OWN/f'sd{n}-first-candidate-comparison.json';raw=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode()
 if path.exists():assert path.read_bytes()==raw,'Initial independent comparison is immutable'
 else:path.write_bytes(raw)
 print(json.dumps(out,ensure_ascii=False,indent=2))

def pin(path):return {'file':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def final_acceptance(n):
 packet_path=SOUTH/f'sd{n}-scan-source-only-peer-packet.json';packet=read(packet_path)
 checkpoint_path=OWN/f'sd{n}-source-first-checkpoint.json';checkpoint=read(checkpoint_path);first_path=OWN/f'sd{n}-first-source-transcript.txt';assert sha(first_path.read_bytes())==checkpoint['firstPersonalTranscriptSha256']
 source=transcript(first_path);corrections_path=OWN/f'sd{n}-additive-source-reread-resolutions.json';corrections=read(corrections_path)
 for r in corrections['resolutions']:
  source[r['sequence']][r['field']]=r['confirmedSourceValue'];p=ROOT/r['freshOriginalSource']['file'];assert sha(p.read_bytes())==r['freshOriginalSource']['sha256']
 confidence_path=OWN/f'sd{n}-confidence-source-corroboration.txt';confidence=transcript(confidence_path)
 if n==35:confidence[556]['position']=read(OWN/'sd35-confidence-additive-reread.json')['confirmedOriginalSource']
 selected=SOUTH/f'sd{n}-scan-reviewed-candidate-v14.json.gzip';candidate=read(selected);rows=candidate['rows']
 assert not candidate['remainingFlags']
 expected={r['sequence'] for r in packet['targets'] if 'initial-true-field-flag' in r['kinds'] or 'withheld-guarded-agreement-benchmark' in r['kinds']}
 assert expected<=set(source)
 confidence_expected={r['sequence'] for r in packet['targets'] if 'confidence-only-primary-image-audit' in r['kinds']};assert set(confidence)==confidence_expected
 for seq,r in list(source.items())+list(confidence.items()):
  c=rows[seq-1]
  for field in ['name','position','remuneration','expenses']:
   normal=numeric if field in ['remuneration','expenses'] else text
   assert normal(r[field])==normal(c[field]),(n,seq,field,r[field],c[field])
 adaptive_path=OWN/'adaptive13-personal-source-readings.json';adaptive=read(adaptive_path)
 for r in adaptive['readings']:
  if r['district']==n:assert numeric(rows[r['sequence']-1]['expenses'])==numeric(r['expenses'])
 raw=read(Path(candidate['rawReaderReplay']['path']));assert sha(Path(candidate['rawReaderReplay']['path']).read_bytes())==candidate['rawReaderReplay']['sha256']
 assert len(raw['tesseractRows'])==len(raw['paddleRows'])==len(rows)
 census_path=SOUTH/f'sd{n}-complete-page-census-and-original-replay.json';census=read(census_path);assert census['pass'] and not census['unexplainedMoneyRows'];assert census['sourceSha256']==packet['source']['sha256'];assert {p['physicalPage'] for p in census['pages']}==set(packet['salaryPages'])
 replay_path=OWN/f'sd{n}-source-crop-replay.json';replay=read(replay_path);assert replay['allCropsExact'] and replay['sourceSha256']==packet['source']['sha256']
 primary=[]
 for r in candidate['manualSourceReadings']:
  path=Path(r['path']);assert sha(path.read_bytes())==r['sha256'];primary.append(pin(path))
 glyph=Path(candidate['glyphEvidence']['path']);assert sha(glyph.read_bytes())==candidate['glyphEvidence']['sha256']
 context_path=OWN/f'sd{n}-first-source-context.json';context=read(context_path);controls={}
 for category,key in [('employee-remuneration','employees'),('school-trustees','trustees')]:
  subset=[r for r in rows if r['category']==category];sums=[sum((numeric(r[f]) or Decimal(0) for r in subset),Decimal(0)) for f in ['remuneration','expenses']];printed=context['printedNamedControls'][key]
  controls[category]={'rows':len(subset),'computedTotals':[str(v) for v in sums],'printedControls':printed,'literalRowsMinusPrintedControls':[str(a-Decimal(b)) for a,b in zip(sums,printed)],'nullExpenseCells':sum(r['expenses'] is None for r in subset)}
 receipt={'schema':'south-school-scan-independent-peer-review-v1','reviewerAgent':'/root/gap_school_north','district':n,'accepted':True,'sourceSha256':packet['source']['sha256'],'selectedCandidate':pin(selected),'rawReaderReplay':pin(Path(candidate['rawReaderReplay']['path'])),'sourceOnlyPacket':pin(packet_path),'sourceFirstCheckpoint':pin(checkpoint_path),'firstPersonalSourceTranscript':pin(first_path),'firstCandidateComparison':pin(OWN/f'sd{n}-first-candidate-comparison.json'),'additiveSourceRereads':pin(corrections_path),'personalSourceFirstRows':len(source),'allInitialTrueFieldFlagsPersonallyRead':packet['guardedAgreementPolicy']['initialTrueFlagCount'],'withheldSourceOnlyBenchmarksPersonallyRead':10,'completeTrusteeRowsPersonallyRead':7 if n==35 else 10,'personalConfidenceOnlySourceCorroborations':len(confidence),'confidenceSourceCorroborationWasBlind':False,'confidenceSourceReadings':pin(confidence_path),'adaptiveAll13LowExpenseSourceReadings':pin(adaptive_path),'expenseGlyphSourceBenchmarksPersonallyRead':15,'sourceExpenseCalibrationContact':pin(OWN/(f'sd{n}-source-expense-calibration'+('-v2.png' if n==38 else '.png'))),'actualOriginalCropsIndependentlyReplayed':pin(replay_path),'completePageIndependentMoneyCensus':pin(census_path),'primaryManualSourceReceiptsAudited':primary,'expenseWholeCellGeometryEvidence':pin(glyph),'sourceContext':pin(context_path),'allPersonallyReviewedFieldsAgreeAfterAdditiveOriginalReread':True,'allFinalRowsComparedToRawIndependentReaderCardinalities':len(rows),'controls':controls,'scopeLimit':'Source-first personal transcription covers every actual initial field flag, ten withheld agreement benchmarks and the complete trustee table. All confidence-only source rows and13adaptive lowexpenses were additionally personally corroborated after candidate exposure. Other employee rows rely on explicit distinct-reader, complete-page-census and independently calibrated whole-cell-ink guards; this is not a personal transcription of every employee row, nor a mathematical source-accuracy guarantee.','residualAcceptance':'Accept literal observations with the exact unexplained source-control residuals disclosed publicly. Whole-dollar display does not prove rounding. No source amount or identity was inferred or adjusted to balance; source dashes stay null and true numeric single digits remain numeric.','noCompiledRowsDeleted':True,'noOutreach':True}
 path=OWN/f'sd{n}-independent-source-peer-acceptance.json';blob=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()
 if path.exists():assert path.read_bytes()==blob,'Peer acceptance changed; add an explicit revision'
 else:path.write_bytes(blob)
 print(json.dumps({'district':n,'accepted':True,'personalSourceFirstRows':len(source),'confidenceCorroborations':len(confidence),'controls':controls,'receiptSha256':sha(blob)}))
if __name__=='__main__':main()
