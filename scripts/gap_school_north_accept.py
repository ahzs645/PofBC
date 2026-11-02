#!/usr/bin/env python3
"""Adopt exact independently reviewed source scopes; never broaden peer claims."""
import argparse,collections,gzip,hashlib,json,re
from decimal import Decimal
from pathlib import Path
from gap_school_north_parse import ROOT,AREA,DEFS,signature
COLLECTION=ROOT/'research/salaries/gap-fill-school-north'
PEER=AREA.parent/'municipal/reviews/school-north'
NATIVE=AREA.parent/'school_native/reviews/sd59'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
 raw=Path(path).read_bytes()
 return json.loads(gzip.decompress(raw) if str(path).endswith('.gzip') else raw)
def ref(path):return {'file':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def require_ref(item):
 path=ROOT/item.get('path',item.get('file',''))
 assert path.is_file() and sha(path.read_bytes())==item['sha256'],('Changed reviewed input',str(path))
 return read(path) if path.suffix in ['.json','.gzip'] else path.read_bytes()
def canonical_name(value):
 return None if value is None else re.sub(r'\s*,\s*',', ',re.sub(r'\s+',' ',value).strip())
def numeric(value):
 if value is None or value in ['','-','–','—']:return None
 return Decimal(str(value).replace(',','').replace('$',''))

def peer_closure():
 # The final pin addendum is written by the independent reviewer after all
 # producer source-image amendments are stable. It retains the initial readings.
 final_path=PEER/'final-stable-candidate-pins.json'
 assert final_path.exists(),'Final seven-source independent pins are pending'
 final=read(final_path)
 assert final.get('allCurrentHoldoutFieldsAgree') is True
 for pin in final['candidatePins']:require_ref(pin)
 for pin in final['normalizedDataPins']:require_ref(pin)
 seven_path=PEER/'north-seven-bounded-peer-review.json';seven=read(seven_path)
 assert seven['status']=='pass-for-explicit-bounded-scope' and seven['holdoutRowsCompared']==70
 for key in ['firstSourceHoldouts','firstSourceContext','additiveOwnContextCorrection','firstCandidateComparison','additionalFourSourceNames']:require_ref(seven[key])
 holds=read(ROOT/seven['firstSourceHoldouts']['path'])['rows']
 wanted={(t['number'],t['sequence']) for t in read(AREA/'source-image-targets.json')['rows'] if t['number']!=59 and 'deterministic-source-image-holdout' in t['reasons']}
 assert {(r['number'],r['sequence']) for r in holds}==wanted and len(wanted)==70
 proofs={n:read(AREA/f'sd{n:02}-image-reviewed-candidate.json.gzip') for n in DEFS}
 for r in holds:
  current=proofs[r['number']]['finalReaders']['tesseract'][r['sequence']-1];literal=r['sourceLiteral']
  assert proofs[r['number']]['sourceSha256']==r['sourceSha256']
  assert canonical_name(current['name'])==canonical_name(literal['name'])
  assert (current['position'] or '').strip()==(literal['position'] or '').strip()
  assert current['pdfPage']==r['physicalPage']
  for f in ['remuneration','expenses']:assert numeric(current[f])==numeric(literal[f]),(r['number'],r['sequence'],f)
  require_ref(r['sourceImageSheet']);require_ref(r['originalSourceSheet'])
 for scope,count in [('employee',248),('trustee',7)]:
  p=NATIVE/f'independent-complete-{scope}-source-review.json';review=read(p)
  if scope=='employee':
   require_ref({'file':review['normalizedDataFile'],'sha256':review['normalizedDataSha256']})
   assert review['acceptedEmployeeRows']==count
   assert review['allFinalNormalizedRowsExactlyAgreeWithIndependentSourceTranscript'] is True
  else:
   require_ref({'file':review['dataFile'],'sha256':review['dataSha256']})
   assert review['acceptedRows']==count and review['allSevenNamesTitlesAmountsAndPagesExactlyMatch'] is True
 south_path=AREA.parent/'school_south/peer-north-three-source-acceptance.json';south=read(south_path)
 assert south['accepted'] and len(south['readings'])==3
 for r in south['readings']:
  current=proofs[r['district']]['finalReaders']['tesseract'][r['sequence']-1]
  for f in ['name','position','remuneration','expenses']:assert current[f]==r[f]
 for pin in south['sourceCrops']:require_ref(pin)
 return [ref(p) for p in [seven_path,final_path,NATIVE/'independent-complete-employee-source-review.json',NATIVE/'independent-complete-trustee-source-review.json',south_path]]

def build_adoption():
 peer_refs=peer_closure();manifest=read(COLLECTION/'sources.json');source_pins=[]
 assert len(manifest['sources'])==16 and sum(s['rowCount'] for s in manifest['sources'])==1884
 for s in manifest['sources']:
  data=COLLECTION/s['file'];evidence=COLLECTION/s['provenanceFile'];n=int(s['employerSlug'].rsplit('-',1)[-1]);candidate=AREA/f'sd{n:02}-image-reviewed-candidate.json.gzip'
  assert sha(data.read_bytes())==s['dataSha256']
  assert sha(evidence.read_bytes())==s['provenanceSha256']
  assert read(candidate)['sourceSha256']==s['sha256']
  source_pins.append({'id':s['id'],'sourceSha256':s['sha256'],'rows':s['rowCount'],'data':ref(data),'candidateProvenance':ref(candidate),'candidateCohortEvidenceSha256BeforeAcceptance':s['validation'].get('candidateEvidenceSha256BeforeAcceptance',sha(evidence.read_bytes())),'scope':s['scope']})
 own=read(AREA/'own-image-review.json');adoption=own['sources']['58']['nameUnavailableAdoption']
 assert adoption['approvedBy']=='root' and adoption['sequences']==[60,128]
 return {'schema':'gap-school-north-exact-review-adoption-v1','approved':True,'noOutreach':True,'sources':source_pins,'peerReceipts':peer_refs,'parentDirectedNameUnavailableAdoption':adoption,'scopeStatement':'Distinct OCR readers cover all literal source observations; producer source-image review covers all finite flags, fixed holdouts, all142 raw name word-boundary differences and all406 names in the other uppercase layouts. Independent personal source review covers70 source-first holdouts and seven report contexts, the complete248employee+7trustee SD59 scopes, and three specific source-payment/name-readability cases. A bounded benchmark is not described as full personal transcription of every source.','residualPolicy':'Retain literal independently checked SD8 and SD59 rows with the exact public source-control residuals and cause unknown; no balancing amounts, invented rows or inferred personal identities.','parentReviewInstruction':'Root directed closure after the exact peer scopes and source qualifications, including only the exact2SD58 damaged-name observations with name unavailable.','ownImageReview':ref(AREA/'own-image-review.json'),'sourceContextReview':ref(AREA/'source-context-review.json')}

def validate_adoption(adoption):
 assert adoption['schema']=='gap-school-north-exact-review-adoption-v1' and adoption['approved'] and adoption['noOutreach']
 assert len(adoption['sources'])==16 and sum(s['rows'] for s in adoption['sources'])==1884
 for p in adoption['peerReceipts']+[adoption['ownImageReview'],adoption['sourceContextReview']]:require_ref(p)
 for s in adoption['sources']:require_ref(s['data']);require_ref(s['candidateProvenance'])
 assert adoption['parentDirectedNameUnavailableAdoption']['sequences']==[60,128]
 assert adoption['parentDirectedNameUnavailableAdoption']['approvedBy']=='root'
 return True

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();value=build_adoption();validate_adoption(value);raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode();path=AREA/'review-adoption.json'
 if args.write and not path.exists():path.write_bytes(raw)
 else:assert path.read_bytes()==raw,'Review adoption changed; an explicit new revision is required'
 print(json.dumps({'status':'passed','cohorts':16,'rows':1884,'adoptionSha256':sha(raw)}))

if __name__=='__main__':main()
