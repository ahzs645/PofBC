#!/usr/bin/env python3
"""Build bounded municipal candidate payloads from explicit literal transcripts.

Raw OCR is corroborating evidence, not accepted truth. Independent final review is
required before a candidate may be registered or published. This script never
edits the global collections or current public salary build.
"""
import argparse,gzip,hashlib,json,re
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/'research/salaries/gap-fill-2026-11-02/municipal';COL=ROOT/'research/salaries/gap-fill-municipal'
TRANSCRIPTS=['transcripts-initial.json','transcripts-middle-v2.json','transcripts-rossland-additional.json','transcripts-clearwater-2012-2016.json','transcripts-clearwater-2011-and-2017-2020.json','transcripts-final.json','transcripts-recovered-originals.json','transcripts-abbotsford-known-column.json']
COMPONENT_FIELDS=['remunerationComponent','taxableBenefits','expenses','expenseInclusiveTotal']
RETENTION='Existing compiled observations are retained and may overlap these official disclosures; a complete source-compatible duplicate-copy comparison has not established a replacement.'

def sha(b):return hashlib.sha256(b).hexdigest()
def packed(r):return (json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def gz(r):return gzip.compress(json.dumps(r,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode(),mtime=0)
def amount(v):
 if v is None:return None
 if not isinstance(v,str):raise ValueError('Amount literals must remain text or null')
 s=v.strip()
 if s in ['','-','–','—']:return None
 if s.lower()=='nil':return Decimal(0)
 if not re.fullmatch(r'-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?',s):raise ValueError('Unparsed source amount '+repr(v))
 return Decimal(s.replace(',',''))
def number(v):
 if v is None:return None
 return int(v) if v==v.to_integral_value() else float(v)
def numeric_row(row,section):
 base=amount(row['remunerationComponent'])
 if base is None:raise ValueError('Unknown required source remuneration')
 literal_column=section.get('payRepresentation')=='remuneration-column-excluding-separately-published-taxable-benefits'
 if section['payIsSumOfRemunerationAndTaxableBenefits'] and not literal_column:
  ben=amount(row.get('taxableBenefits'))
  if ben is None:raise ValueError('Unknown taxable benefit cannot be imputed zero in composite pay')
  pay=base+ben
 else:pay=base
 return pay,amount(row.get('expenses'))
def strip_footnote(v):return re.sub(r'\*+$','',v).strip() if isinstance(v,str) else None

def controls(section):
 printed=section['printedControls'];result=[]
 if 'allEmployees' in printed:
  target={}
  for field,v in printed['allEmployees'].items():
   under=printed['unnamedEmployees'].get(field)
   if amount(v) is not None and amount(under) is not None:target[field]=number(amount(v)-amount(under))
  basis='Printed all-employee total minus the separately printed unnamed aggregate, only when both controls are numeric.'
 else:target=printed;basis='Printed named-cohort subtotal.'
 for field,value in target.items():
  expected=amount(str(value)) if value is not None else None
  vals=[amount(row.get(field)) for row in section['rows']]
  known=sum((v for v in vals if v is not None),Decimal(0));missing=sum(v is None for v in vals)
  #Unknown cells stay unknown even when the known sum happens to equal control.
  residual=known-expected if expected is not None and any(v is not None for v in vals) else None
  result.append({'field':field,'printedControl':number(expected),'knownRowSum':number(known),'unknownRowCells':missing,'knownSumMinusPrintedControl':number(residual),'allCellsKnown':missing==0,'basis':basis,'noMissingCellImputedZero':True})
 return result

def build(*,include_publication_qualifications=True):
 raw_sources=json.loads((AREA/'refreshed-originals.json').read_bytes())['sources'];sections=[];inputpins=[]
 baseline_path=ROOT/'research/salaries/gap-fill-2026-11-02/baseline.json.gzip';baseline_raw=baseline_path.read_bytes();assert sha(baseline_raw)=='fa35799b84e173aa7e61f9225935ec1936d744375107c14ccf709edeac937fa4'
 existing={'sources':json.loads(gzip.decompress(baseline_raw))['sourceMetadata']}
 for name in TRANSCRIPTS:
  p=AREA/name;b=p.read_bytes();r=json.loads(b);sections+=r['sections'];inputpins.append({'path':str(p.relative_to(ROOT)),'sha256':sha(b)})
 qualification_path=AREA/'source-publication-qualifications.json'
 qualifications={}
 if include_publication_qualifications and qualification_path.is_file():
  qb=qualification_path.read_bytes();q=json.loads(qb);assert q['salaryRowsChanged']==0 and q['noOutreach'] is True
  qualifications={x['sourceId']:x for x in q['qualifications']};assert len(qualifications)==len(q['qualifications'])
  inputpins.append({'path':str(qualification_path.relative_to(ROOT)),'sha256':sha(qb)})
 ids=set();sources=[];outputs={};reviewpacket=[]
 for section in sections:
  s=next(s for s in raw_sources if s.get('sha256','').startswith(section['sourceShaPrefix']));slug=s['employerSlug'];year=section['year'];scope=section['scope'];key=f'{slug}-{year}-{scope}';identifier='gap-fill-municipal-'+key
  if identifier in ids:raise ValueError('Repeated candidate source '+identifier)
  ids.add(identifier)
  for old in existing['sources'].values():
   if old.get('sha256')==s['sha256'] and old.get('year')==year and old.get('scope')==scope:
    supplement=section.get('disjointSupplement')
    if not supplement or old.get('id')!=supplement['originalSourceId']:raise ValueError('Existing official scope '+identifier)
    assert supplement['priorAcceptedRows']==449 and supplement['previouslyHeldRows']==11 and supplement['exactDisjointSourceRowIdentities'] is True
    prior=(ROOT/supplement['priorData']['path']).read_bytes();assert sha(prior)==supplement['priorData']['sha256']
    oldrows=json.loads(gzip.decompress(prior));newids={(r['name'],r['position'],r['physicalPage']) for r in section['rows']}
    assert len(oldrows)==449 and len(newids)==11 and not (newids & {(r[1],r[2],r[5]) for r in oldrows})
  original_key=slug+'-'+s['sha256'][:12];pn=section['physicalPage'];rawpath=ROOT/section['nativeEvidencePath'] if section.get('nativeEvidencePath') else AREA/'ocr'/f'{original_key}-p{pn:02d}.json.gzip';rawbytes=rawpath.read_bytes();raw=json.loads(gzip.decompress(rawbytes));assert raw['sourceSha256']==s['sha256'] and raw['physicalPage']==pn
  if section.get('nativeEvidenceSha256'):assert sha(rawbytes)==section['nativeEvidenceSha256']
  rows=[];derivations=[]
  for n,row in enumerate(section['rows'],1):
   pay,expense=numeric_row(row,section)
   rows.append([slug,strip_footnote(row['name']),strip_footnote(row['position']),number(pay),number(expense),row.get('physicalPage',pn)])
   derivations.append({'sourceRowOnPage':n,'physicalPage':row.get('physicalPage',pn),'sourceLiteral':row,'normalizedName':strip_footnote(row['name']),'normalizedPosition':strip_footnote(row['position']),'pay':number(pay),'expenses':number(expense),'payRepresentation':section.get('payRepresentation') or ('sum-of-two-known-published-pay-components' if section['payIsSumOfRemunerationAndTaxableBenefits'] else 'literal-published-remuneration-column'),'unknownExpensesRemainNull':expense is None})
  cs=controls(section);res=[x for x in cs if x['knownSumMinusPrintedControl'] not in [0,None]];notes=section['sourceNotes'][:]
  qualification=qualifications.get(identifier)
  if qualification:
   assert qualification['sourceSha256']==s['sha256']
   for qp in [qualification['independentSourceContextReview'],qualification.get('additionalAdoptionSourceReceipt')]:
    if qp:assert sha((ROOT/qp['path']).read_bytes())==qp['sha256']
   notes+=qualification['publicNotes']
  if section.get('payRepresentation'):
   notes.append('Pay is uniformly the literal Remuneration column for every observation in this cohort, excluding the separate Taxable Benefit column. Source blank/dash benefit cells remain unknown; no value is inferred from totals.')
  elif section['payIsSumOfRemunerationAndTaxableBenefits']:
   notes.append('Pay is the exact sum of two numeric source components: Remuneration plus separately printed Taxable Benefits. The expense-inclusive Total is never substituted for remuneration.')
  warnings=['These are published payment disclosures, not a complete workforce roster or an annualized base salary rate.']
  if any(r[4] is None for r in rows):warnings.append(f'{sum(r[4] is None for r in rows)} source blank/dash expense cells remain unknown, not zero. Known-expense sums do not establish those missing cells\' values.')
  if res:warnings.append('Known literal row sums minus printed source controls: '+', '.join(x['field']+' '+f"{x['knownSumMinusPrintedControl']:+g}" for x in res)+' CAD. Source cells are retained unchanged; the cause is not inferred and no amount is balanced.')
  warnings+=notes;warnings.append(RETENTION)
  pay_sum=sum((Decimal(str(row[3])) for row in rows),Decimal(0));expense_sum=sum((Decimal(str(row[4])) for row in rows if row[4] is not None),Decimal(0))
  data=gz(rows);data_file=key+'.json.gzip';evidence_file='evidence/'+key+'.json.gzip'
  evidence={'sourceId':identifier,'sourceSha256':s['sha256'],'sourceUrl':s['sourceUrl'],'year':year,'periodType':'calendar','physicalPage':pn,'scope':scope,'completeNamedScopeAuthorTranscribed':not bool(section.get('disjointSupplement')),'completeBoundedSubsetAuthorTranscribed':bool(section.get('disjointSupplement')),'status':'candidate-awaiting-independent-peer','authorActuallyViewedPdfPaintedWholePage':not bool(section.get('disjointSupplement')),'authorActuallyViewedAllBoundedOriginalImageRowCrops':bool(section.get('disjointSupplement')),'notAClaimThatOcrWasErrorFree':True,'rawOcrEvidence':{'path':str(rawpath.relative_to(ROOT)),'sha256':sha(rawbytes)},'originalRender':raw['render'],'independentOcrEngines':raw['engines'],'rawOcrLimitations':'Tesseract PSM6 often loses ruled-table cells; neither OCR output is substituted for the actual original. Every candidate field is author-transcribed from the original image and requires full independent peer source verification.','sourcePeriodBasis':'The reporting year is stated in the original schedule itself; upload paths and later meeting dates do not replace it.','literalSection':section,'rows':derivations,'controls':cs,'sourceDefinitions':notes,'noOutreach':True}
  evidencebytes=gz(evidence);outputs[data_file]=data;outputs[evidence_file]=evidencebytes
  source={'id':identifier,'employerSlug':slug,'employerName':next(a['employer'] for a in json.loads((AREA/'assigned-leads.json').read_bytes()) if a['id']==s['leadId']),'sector':'Municipalities','year':year,'periodType':'calendar','periodStart':year+'-01-01','periodEnd':year+'-12-31','sourceUrl':s['sourceUrl'],'sourceIndexUrl':s['sourceIndexUrl'],'sha256':s['sha256'],'file':data_file,'dataSha256':sha(data),'provenanceFile':evidence_file,'provenanceSha256':sha(evidencebytes),'category':scope,'scope':scope,'title':f'{slug} {year} official {scope}','status':'candidate','verified':False,'sourceKind':'official','rowCount':len(rows),'totalRemuneration':number(pay_sum),'totalExpenses':number(expense_sum),'pages':section.get('physicalPages',[pn]),'currency':'CAD','amountUnit':'dollars','threshold':None,'thresholdComparison':None,'completeEmployeeSchedule':section.get('completeEmployeeSchedule',scope=='employee-remuneration'),'notes':notes,'publicWarning':' '.join(warnings),'validation':{'method':'Two raw OCR engines preserved separately; complete author actual-original image transcript; independent complete source peer verification required before release.','candidateOnly':True,'completeEmployeeSchedule':section.get('completeEmployeeSchedule',scope=='employee-remuneration'),'authorActualOriginalImageReview':True,'independentPeerVerified':False,'compiledPartitionRetained':True,'compiledPartitionRetentionReason':RETENTION,'rawOcrEvidenceFile':str(rawpath.relative_to(ROOT)),'rawOcrEvidenceSha256':sha(rawbytes),'knownLiteralControls':cs,'allEarlierOfficialRecordsPreserved':True,'reportingYearReadFromOriginalSchedule':True}}
  if section.get('disjointSupplement'):
   source['validation']['disjointSupplement']=section['disjointSupplement']
   source['validation']['partialCompensationDefinition']=True
   source['validation']['independentPdfReaders']=['PyMuPDF positioned words','Poppler bbox-layout positioned words']
   evidence['rawOcrLimitations']='This supplement uses fresh independent native PDF readers rather than OCR; both readers agree on every cell in the five full page parts. All eleven selected actual image crops were also author-read; final independent peer verification remains required.'
   evidencebytes=gz(evidence);outputs[evidence_file]=evidencebytes;source['provenanceSha256']=sha(evidencebytes)
  if qualification:
   evidence['sourcePublicationQualification']=qualification
   source['validation']['sourcePublicationQualification']=qualification
   evidencebytes=gz(evidence);outputs[evidence_file]=evidencebytes;source['provenanceSha256']=sha(evidencebytes)
  sources.append(source)
  reviewpacket.append({'sourceId':identifier,'leadId':s['leadId'],'sourceSha256':s['sha256'],'sourceUrl':s['sourceUrl'],'cachedPdf':s['cachedOriginal'],'physicalPage':pn,'scope':scope,'expectedNamedRows':len(rows),'render300DpiImage':str(Path('/workspace/gap-municipal-cache')/f'{original_key}-p{pn:02d}-300dpi.png') if not section.get('disjointSupplement') else None,'renderSha256':raw['render'].get('imageSha256'),'physicalPages':section.get('physicalPages',[pn]),'boundedSupplementCropPacket':[{k:v for k,v in x.items() if k not in ['sourceName','priorHeldRow']} for x in json.loads((AREA/'abbotsford-known-column-supplement.json').read_bytes())['cropSpecs']] if section.get('disjointSupplement') else None,'candidateValuesWithheldInPacket':True})
 outputs['sources.json']=packed({'version':1,'sources':sources})
 assert set(qualifications).issubset(ids),'Unknown source publication qualification'
 summary={'candidateOnly':True,'noOutreach':True,'sources':len(sources),'originals':len({s['sha256'] for s in sources}),'rows':sum(s['rowCount'] for s in sources),'employeeRows':sum(s['rowCount'] for s in sources if s['scope']=='employee-remuneration'),'councilRows':sum(s['rowCount'] for s in sources if s['scope']=='elected-officials'),'inputTranscripts':inputpins,'outputs':[{'path':str((COL/p).relative_to(ROOT)),'sha256':sha(b)} for p,b in outputs.items()]}
 return outputs,summary,reviewpacket

def run():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args();outputs,summary,packet=build()
 final_summary=None
 acceptance=AREA/'acceptance.json'
 if acceptance.is_file():
  from gap_municipal_finalize import accepted_outputs
  outputs,final_summary=accepted_outputs(outputs,json.loads(acceptance.read_bytes()))
 if args.write:
  for path,raw in outputs.items():p=COL/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  (AREA/'candidate-summary.json').write_bytes(packed(summary));(AREA/'independent-review-packet.json').write_bytes(packed({'phase':'image-first independent transcript; compare candidates only afterward','noOutreach':True,'sections':packet}))
  if final_summary is not None:(AREA/'accepted-summary.json').write_bytes(packed(final_summary))
 elif args.check:
  for path,raw in outputs.items():assert (COL/path).read_bytes()==raw,path
  if final_summary is not None:assert (AREA/'accepted-summary.json').read_bytes()==packed(final_summary),'accepted-summary.json'
 print(json.dumps({k:v for k,v in (final_summary or summary).items() if k!='outputs' and k!='inputTranscripts'},indent=2))
if __name__=='__main__':run()
