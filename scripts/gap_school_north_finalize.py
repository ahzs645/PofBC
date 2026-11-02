#!/usr/bin/env python3
"""Replay finite source-image decisions, preserve raw readers, stage normalized rows."""
import argparse,collections,copy,gzip,hashlib,json,re
from decimal import Decimal
from pathlib import Path
from gap_school_north_parse import ROOT,AREA,DEFS,FIELD_NAMES,pack,sha,signature
OUT=ROOT/'research/salaries/gap-fill-school-north'
NAMES={8:'Kootenay Lake',28:'Quesnel',54:'Bulkley Valley',58:'Nicola-Similkameen',59:'Peace River South',60:'Peace River North',81:'Fort Nelson',82:'Coast Mountains'}
CONTROLS={8:{'school-trustees':['194820','51129'],'employee-remuneration':['36984246','450936']},28:{'school-trustees':['117029.40','7862.97'],'employee-remuneration':['22251599.97','151556.63']},54:{'school-trustees':['99129.60','38347.75'],'employee-remuneration':['13820714.53','393279.19']},58:{'school-trustees':['155183.68','49455.08'],'employee-remuneration':['16244426.44','243281.41']},59:{'school-trustees':['125569.44','32790.44'],'employee-remuneration':['26885896.54','299076.71']},60:{'school-trustees':['112757.09','21852.73'],'employee-remuneration':['42576364.73','586562.81']},81:{'school-trustees':['63000','3712.11'],'employee-remuneration':['5680305.87','126136.69']},82:{'school-trustees':['108258.96','36964.95'],'employee-remuneration':['31906004.74','296856.18']}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=int,action='append');ap.add_argument('--check',action='store_true');args=ap.parse_args()
 own_path=AREA/'own-image-review.json';own=json.loads(own_path.read_text());packet_path=AREA/'source-image-packet-index.json';packets=json.loads(packet_path.read_text())['packets'];specs={x['number']:x for x in json.loads((AREA/'ocr-plan.json').read_text())};sources=[];handoff=[]
 context_path=AREA/'source-context-review.json';context=json.loads(context_path.read_text()) if context_path.exists() else None
 adoption_path=AREA/'review-adoption.json';adoption=json.loads(adoption_path.read_text()) if adoption_path.exists() else None
 if adoption:
  from gap_school_north_accept import validate_adoption
  validate_adoption(adoption)
 # SD82's sloping source columns require separately aligned integer pixel crops.
 # Earlier fullrow SD82 sheets clipped monetary glyphs and are not review evidence.
 packets=[p for p in packets if not Path(p['file']).name.startswith('sd82-')]
 packets+=json.loads((AREA/'sd82-source-field-packet-index-v2.json').read_text())['packets']
 for n in DEFS:
  if args.source and n not in args.source:continue
  if str(n) not in own['sources']:continue
  review=own['sources'][str(n)];proof_path=AREA/f'sd{n:02}-pixel-candidate.json.gzip';proof=json.loads(gzip.decompress(proof_path.read_bytes()));first=copy.deepcopy(proof['readers']['tesseract']);second=copy.deepcopy(proof['readers']['rapid']);changes=[]
  seen={}
  for packet in packets:
   if Path(packet['file']).name not in review['seenPackets']:continue
   assert sha((ROOT/packet['file']).read_bytes())==packet['sha256']
   assert packet['sourceSha256']==specs[n]['sha256']
   for row in packet['rows']:seen[row['sequence']]={'file':packet['file'],'sha256':packet['sha256'],'physicalPage':row['physicalPage'],**({'sourceFieldPixelCrops':row['fieldCrops']} if 'fieldCrops' in row else {'sourcePixelCrop':row['originalPixelCrop']})}
  for row in review.get('additionalRows',[]):
   assert sha((ROOT/row['sourceImage']).read_bytes())==row['sha256']
   seen[row['sequence']]={'file':row['sourceImage'],'sha256':row['sha256'],'physicalPage':row['physicalPage'],'sourceClipPoints':row['sourceClipPoints'],'renderDpi':row['renderDpi']}
  name_packets=json.loads((AREA/'name-spacing-image-index.json').read_text())['packets']+json.loads((AREA/'uppercase-names-image-index.json').read_text())['packets']
  for packet in name_packets:
   if Path(packet['file']).name not in review.get('nameOnlySeenPackets',[])+review.get('uppercaseNameOnlySeenPackets',[]):continue
   assert sha((ROOT/packet['file']).read_bytes())==packet['sha256']
   for row in packet['rows']:
    if row['number']!=n:continue
    assert row['sourceSha256']==specs[n]['sha256']
    ref={'file':packet['file'],'sha256':packet['sha256'],'physicalPage':row['physicalPage'],'sourcePixelCrop':row['originalPixelCrop'],'reviewedFields':['name']}
    if row['sequence'] in seen:seen[row['sequence']]['additionalNameOnlyProof']=ref
    else:seen[row['sequence']]=ref
  targets=json.loads((AREA/'additional-source-image-targets.json').read_text())['rows']
  assert all(t['sequence'] in seen for t in targets if t['number']==n),'New flagged source row lacks finite image review'
  corrections={(x['sequence'],x['field']):x['after'] for x in review['corrections']}
  for i,(a,b) in enumerate(zip(first,second),1):
   if i in seen:
    for field in seen[i].get('reviewedFields',FIELD_NAMES[:4]):
     v=corrections.get((i,field),a[field]);a[field]=v
     if b[field]!=v:changes.append({'engine':'rapid','sequence':i,'field':field,'before':b[field],'after':v,'sourceImage':seen[i]});b[field]=v
    for (seq,field),after in corrections.items():
     if seq==i:changes.append({'engine':'tesseract','sequence':i,'field':field,'before':proof['readers']['tesseract'][i-1][field],'after':after,'sourceImage':seen[i]})
   assert signature(a)==signature(b),(n,i,'Unreviewed reader differences',signature(a),signature(b))
   assert all(not (isinstance(a[f],str) and a[f].startswith('UNRESOLVED:')) for f in ['remuneration','expenses']),(n,i,'Unresolved amount')
   assert a['name'] is not None or n==58 and i in [60,128]
  if n==58:
   assert [(i,r['position'],r['remuneration'],r['expenses']) for i,r in enumerate(first,1) if r['name'] is None]==[(60,'TEACHERS','87804.23','0.00'),(128,'TEACHERS','103044.97','0.00')]
  outproof={'sourceSha256':specs[n]['sha256'],'rawReaderCandidate':{'file':str(proof_path.relative_to(ROOT)),'sha256':sha(proof_path.read_bytes())},'ownImageReview':{'file':str(own_path.relative_to(ROOT)),'sha256':sha(own_path.read_bytes())},'finalReaders':{'tesseract':first,'rapid':second},'sourceImageAmendments':changes,'personallyReviewedSourceRows':sorted(seen),'qualifiedSourceNames':review.get('qualifiedNames',[]),'nameUnavailableAdoption':review.get('nameUnavailableAdoption'),'independentPeerReview':None,'acceptedRows':0}
  final=AREA/f'sd{n:02}-image-reviewed-candidate.json.gzip';blob=pack(outproof)
  if args.check:assert final.read_bytes()==blob
  else:final.write_bytes(blob)
  OUT.mkdir(exist_ok=True)
  for category in ['school-trustees','employee-remuneration']:
   rows=[x for x in first if x['category']==category];slug='school-district-'+f'{n:02}';key=f'sd{n:02}-2024-25-'+('trustees' if category=='school-trustees' else 'employees');numeric=lambda s:None if s is None else int(Decimal(s)) if DEFS[n]['precision']=='whole-dollars' else float(Decimal(s))
   data=[[slug,r['name'],r['position'],numeric(r['remuneration']),numeric(r['expenses']),r['pdfPage']] for r in rows];data_blob=pack(data);data_path=OUT/(key+'.json.gzip')
   if args.check:assert data_path.read_bytes()==data_blob
   else:data_path.write_bytes(data_blob)
   sums=[str(sum((Decimal(r[f]) for r in rows if r[f] is not None),Decimal(0))) for f in ['remuneration','expenses']];printed=CONTROLS[n][category];res=[str(Decimal(a)-Decimal(b)) for a,b in zip(sums,printed)]
   warning='Payment disclosures are not an annual salary rate or a complete workforce roster. Source dashes or visibly blank expense cells remain unknown, not zero. Published clipped titles and literal spelling are retained.'
   if any(Decimal(x)!=0 for x in res):warning+=f' Literal row sums differ from the printed named controls by remuneration ${res[0]} and known expenses ${res[1]}; no source amount was changed to balance and the cause is not established.'
   if review.get('qualifiedNames') and category=='employee-remuneration':warning+=' Specific capital I/l name interpretations are qualified in source provenance; a unique glyph reading or identity is not claimed.'
   if n==58 and category=='employee-remuneration':warning+=' Two disclosed employee name cells are unreadable in both the Ministry and district copies. Their known payments and positions are retained with name unavailable; visible name fragments and source images remain in provenance, without guessed missing letters.'
   if n==81:warning+=' The approval form YEAR box says 2024, while its declaration and the salary schedules explicitly state the year ended June 30, 2025; the salary period follows those explicit statements.'
   if n==82:warning+=' The public copies redact the signature block and show blank approval-date fields; approval signatures and dates cannot be verified from the available copies.'
   warning+=' Compiled entries, where present, are retained under their unverified edition labels; no same-person or reporting-period equivalence is assumed.'
   source={'id':'gap-school-north-'+key,'employerSlug':slug,'employerName':f'School District No. {n} ({NAMES[n]})','sector':'School districts','year':'2024/25','slug':'2024-25','periodType':'fiscal','periodStart':'2024-07-01','periodEnd':'2025-06-30','title':f'School District No. {n} ({NAMES[n]}), year ended June 30, 2025: '+category,'sourceUrl':specs[n]['sourceUrl'],'sourceIndexUrl':'https://www2.gov.bc.ca/gov/content/education-training/k-12/administration/financial-management/school-district-financial-reporting/statement-of-financial-information','sha256':specs[n]['sha256'],'file':data_path.name,'dataSha256':sha(data_blob),'normalizedSha256':sha(data_blob),'provenanceFile':f'{key}-evidence.json.gzip','category':category,'scope':category,'currency':'CAD','amountUnit':'dollars','amountPrecision':DEFS[n]['precision'],'pages':sorted({r['pdfPage'] for r in rows}),'rowCount':len(rows),'status':'candidate-independent-peer-review-pending','sourceKind':'official','completeEmployeeSchedule':category=='employee-remuneration','nameDisclosure':'source-includes-two-unreadable-name-cells' if n==58 and category=='employee-remuneration' else 'published-name-as-disclosed','positionDisclosure':'published-visible-text-only' if DEFS[n]['positions'] else 'not-published','totalRemuneration':numeric(sums[0]),'totalExpenses':numeric(sums[1]),'publicWarning':warning,'notes':['Only complete published employee/trustee observations are imported; aggregate payroll, employer CPP/EI, suppliers, reconciliation entries and severance aggregates stay excluded.','No payment, date, personal identity or job expansion was inferred from compiled records. Original OCR disagreements and finite image amendments remain separate.'],'validation':{'originalFingerprintVerified':True,'independentReaders':['Tesseract5.5 source-specific PSM6/PSM3 raw words','RapidOCR1.4.4 PP-OCRv4 independent detector/recognizer raw boxes'],'rowsIndependentlyChecked':len(rows),'allFinalPublishedFieldsOrderMultiplicityAgreeAfterSourceImageReview':True,'uniqueNameTranscriptionEstablishedForEveryRow':False if (n==58 or review.get('qualifiedNames')) and category=='employee-remuneration' else True,'sourceDisclosedButDamagedNameCells':2 if n==58 and category=='employee-remuneration' else 0,'sourceImageReviewFile':str(final.relative_to(ROOT)),'sourceImageReviewSha256':sha(blob),'printedControlTotals':printed,'computedComponentTotals':sums,'controlResiduals':res,'completeEmployeeSchedule':category=='employee-remuneration','compiledPartitionRetained':True,'compiledPartitionRetentionReason':'Complete copy equivalence and reporting-period equivalence have not been proved; existing compiled observations remain retained.','independentPeerReviewPending':True,'nameUnavailableSourceRows':[60,128] if n==58 and category=='employee-remuneration' else []}}
   ev={'sourceSha256':specs[n]['sha256'],'normalizedDataSha256':sha(data_blob),'completeReviewedCandidate':{'file':str(final.relative_to(ROOT)),'sha256':sha(blob)},'scope':category,'rows':[{k:r.get(k) for k in ['name','position','remuneration','expenses','pdfPage','category','sourceYPoints','expenseFootnote']} for r in rows],'sourceNameReadability':review.get('unresolvedSourceFields',[]),'publicWarning':warning,'acceptedRows':0};evblob=pack(ev)
   if adoption:
    pin=next(s for s in adoption['sources'] if s['id']==source['id'])
    assert pin['sourceSha256']==source['sha256'] and pin['rows']==len(rows)
    assert pin['data']['sha256']==sha(data_blob) and pin['candidateProvenance']['sha256']==sha(blob)
    assert pin['candidateCohortEvidenceSha256BeforeAcceptance']==sha(evblob),'Candidate provenance changed after independent acceptance'
    source['status']='verified';source['validation']['independentPeerReviewPending']=False
    source['validation']['candidateEvidenceSha256BeforeAcceptance']=sha(evblob)
    acceptance_ref={'file':str(adoption_path.relative_to(ROOT)),'sha256':sha(adoption_path.read_bytes())}
    source['validation']['independentReviewAcceptance']=acceptance_ref
    source['validation']['peerScopeStatement']=adoption['scopeStatement']
    ev.update(acceptedRows=len(rows),independentReviewAcceptance=acceptance_ref,peerScopeStatement=adoption['scopeStatement'])
    evblob=pack(ev)
   evpath=OUT/source['provenanceFile'];source['provenanceSha256']=sha(evblob)
   if args.check:assert evpath.read_bytes()==evblob
   else:evpath.write_bytes(evblob)
   if context:
    source['sourceContextReview']={'file':str(context_path.relative_to(ROOT)),'sha256':sha(context_path.read_bytes()),'district':n}
    source['validation']['independentOCRMeansDistinctModelsNotSourceAccuracyGuarantee']=True
    source['validation']['preferredReaderFieldsArbitratedAgainstSourceImages']=True
    source['validation']['sourceFieldCasePunctuationNotIdentityInference']=True
   sources.append(source);print(json.dumps({'number':n,'scope':category,'rows':len(rows),'sums':sums,'printed':printed,'residuals':res}))
  handoff.append({'number':n,'rows':len(first),'personalImageRows':len(seen),'candidateFile':str(final.relative_to(ROOT)),'candidateSha256':sha(blob)})
 manifest={'version':1,'reviewed':bool(adoption),'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources};path=OUT/'sources.json';raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
 if args.check:assert path.read_bytes()==raw
 else:path.write_bytes(raw)
 handoff_path=AREA/'candidate-handoff.json';handoff_raw=json.dumps({'candidateOnly':not bool(adoption),'sources':handoff,'noOutreach':True},indent=2)+'\n'
 if args.check:assert handoff_path.read_text()==handoff_raw
 else:handoff_path.write_text(handoff_raw)
if __name__=='__main__':main()
