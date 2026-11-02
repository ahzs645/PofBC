#!/usr/bin/env python3
"""Fresh disjoint native extraction of eleven known pay-column supplements."""
import gzip,hashlib,json
from pathlib import Path
from decimal import Decimal
import fitz
import parse_wave_lower_mainland as native
from gap_municipal_transcribe import AREA
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
 proofpath=AREA/'abbotsford-known-column-supplement.json';proof=json.loads(proofpath.read_bytes());prior=ROOT/proof['priorData']['path'];before=prior.read_bytes();assert sha(before)==proof['priorData']['sha256'];oldrows=json.loads(gzip.decompress(before));assert len(oldrows)==449
 cfgpath=ROOT/'research/salaries/municipal-wave-lower-mainland/reviewed-layouts.json';cfg=next(r for r in json.loads(cfgpath.read_bytes())['reports'] if r['key']=='city-of-abbotsford-2023');parts=next(s for s in cfg['sections'] if s['category']=='employee-remuneration')['parts'];src=next(x for x in json.loads((AREA/'refreshed-originals.json').read_bytes())['sources'] if x['leadId']=='lead-026');pdf=Path(src['cachedOriginal']);assert sha(pdf.read_bytes())==proof['sourceSha256'];d=fitz.open(pdf)
 selected=[];partproof=[]
 for part in parts:
  if part['page'] not in {r['pdfPage'] for r in proof['exactPriorHeldRows']}:continue
  pn=part['page'];a=native.words_mupdf(d[pn-1]);b=native.words_poppler(pdf,pn);ra=native.extract(a,part);rb=native.extract(b,part);assert ra==rb,(pn,'fresh native readers disagree')
  raw=native.extract(a,part,raw_fields=True);assert len(raw)==len(ra)
  partproof.append({'physicalPage':pn,'mupdfWords':a,'popplerWords':b,'independentFieldRows':ra,'sourceRawRows':raw,'completeTablePartFieldAgreement':True})
  for row,literals in zip(ra,raw):
   wanted=[h for h in proof['exactPriorHeldRows'] if h['name']==row['name'] and h['pdfPage']==pn]
   if not wanted:continue
   h=wanted[0];assert row['benefits'] is None and row['pay'] is None;assert native.dollars(row['salary'])==h['knownRemunerationColumn'];assert row['position']==h['position'] and native.dollars(row['expenses'])==h['expenses'];assert literals['benefits']=='-'
   selected.append({'name':row['name'],'position':row['position'],'remunerationComponent':str(Decimal(row['salary'])/100),'taxableBenefits':literals['benefits'],'expenses':literals['expenses'],'expenseInclusiveTotal':None,'physicalPage':pn,'sourceRawNativeFields':literals})
 assert len(selected)==11
 selected.sort(key=lambda row:next(i for i,h in enumerate(proof['exactPriorHeldRows']) if h['name']==row['name'] and h['pdfPage']==row['physicalPage']))
 prioridentities={(r[1],r[2],r[5]) for r in oldrows};newidentities={(r['name'],r['position'],r['physicalPage']) for r in selected};assert len(newidentities)==11 and not(prioridentities & newidentities)
 assert prior.read_bytes()==before
 raw={'sourceSha256':proof['sourceSha256'],'physicalPage':6,'physicalPages':[6,7,8,9,11],'method':'Fresh independent PyMuPDF and Poppler positioned-word extraction using the pinned previously reviewed source layout; actual original image crops were also author-read for all eleven selected rows.','render':{'method':'Full original PDF pages painted at300dpi then integer row crops, with full-page and crop hashes retained.','sourceCrops':[{k:v for k,v in s.items() if k!='priorHeldRow'} for s in proof['cropSpecs']]},'engines':{'readers':['PyMuPDF positioned words','Poppler bbox-layout words'],'pymupdfVersion':fitz.VersionBind},'parts':partproof,'disjointSupplementProof':{'originalSourceId':proof['sourceId'],'priorManifest':proof['priorManifest'],'priorData':proof['priorData'],'priorAcceptedRows':449,'previouslyHeldRows':11,'originalSourceNamedRows':460,'priorAcceptedRowsRemainByteIdentical':True,'exactDisjointSourceRowIdentities':True,'knownColumnPayOnly':True,'noMissingBenefitImputedZero':True,'priorHeldRowsSha256':proof['exactPriorHeldRowsSha256']}}
 rp=AREA/'abbotsford-fresh-native-readers.json.gzip';rp.write_bytes(gzip.compress(json.dumps(raw,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 sec={'sourceShaPrefix':proof['sourceSha256'][:12],'year':'2023','physicalPage':6,'physicalPages':[6,7,8,9,11],'scope':'employee-remuneration','authorActualOriginalImageReview':True,'rows':selected,'printedControls':{},'payIsSumOfRemunerationAndTaxableBenefits':True,'payRepresentation':'remuneration-column-excluding-separately-published-taxable-benefits','completeEmployeeSchedule':False,'disjointSupplement':raw['disjointSupplementProof'],'nativeEvidencePath':str(rp.relative_to(ROOT)),'nativeEvidenceSha256':sha(rp.read_bytes()),'sourceNotes':['Additional eleven previously unpublished source observations use only the numeric Remuneration & Payouts column. Their separate Taxable Benefits are printed dashes and remain unknown. These values exclude that unknown component and are partial compensation, not complete remuneration including benefits.','The existing449published observations from this same report include numeric separate benefits; these eleven narrower known-column observations require that qualification when comparing payments. The original449records and metadata are preserved unchanged.','The source schedule explicitly excludes Police and Elected Officials. Original names and positions remain as printed. No missing component is inferred zero and no source control is used to reconstruct a benefit.'],'unknownExpenseMeaning':'Two literal expense dashes remain unknown, not zero.'}
 (AREA/'transcripts-abbotsford-known-column.json').write_text(json.dumps({'status':'candidate-only-awaiting-root-definition-adoption-and-independent-source-review','sections':[sec]},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'selectedRows':len(selected),'nativePageParts':len(partproof),'prior449Unchanged':True,'disjoint':True}))
if __name__=='__main__':run()
