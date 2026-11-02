import json,hashlib,re
from pathlib import Path
import fitz
from PIL import Image
R=Path(__file__).resolve().parents[4];A=R/'research/salaries/queue-completion-2026-11-01';V=A/'reviews';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for tp in sorted(V.glob('root-phsa-history-*-holdout-image-transcript.json')):
 t=json.loads(tp.read_text());year=t['sourceId'].removeprefix('phsa-');out=V/f'root-phsa-history-{year}-holdout-source-comparison.json'
 if out.exists():continue
 amendment_pin=None;amendment_count=0
 ap=V/f'root-phsa-history-{year}-holdout-image-reading-amendments.json'
 if ap.exists():
  a=json.loads(ap.read_text());assert a['sourceId']==t['sourceId'] and a['sourceSha256']==t['sourceSha256'] and a['originalImageFirstTranscript']['sha256']==sha(tp)
  pp=R/a['independentSourceOnlyPeer']['path'];assert sha(pp)==a['independentSourceOnlyPeer']['sha256'];peer=json.loads(pp.read_text());assert peer['frozenBeforeRootOrCandidateAlternatives'] is True and not peer['unresolvedRows']
  readings={(x['sourceId'],x['sequence']):x for x in peer['readings']};by={x['sequence']:x for x in t['rows']}
  for change in a['changes']:
   x=by[change['sequence']];p=readings[(t['sourceId'],change['sequence'])];assert change['field']=='name' and 'name' in x['reviewTargetFields'] and x['literalSourceFields']['name']==change['firstRootReading'] and change['confirmedSourceReading']==p['literalImageName'] and p['sourceSha256']==t['sourceSha256'] and (x['physicalPage'],x['sourceRowOnPage'])==(p['physicalPage'],p['sourceRowOnPage'])
   x['literalSourceFields']['name']=change['confirmedSourceReading'];amendment_count+=1
  amendment_pin={'path':str(ap.relative_to(R)),'sha256':sha(ap)}
 ip=R/t['sourceOnlyPacket']['path'];assert sha(ip)==t['sourceOnlyPacket']['sha256'];i=json.loads(ip.read_text());cp=R/i['fullCandidate']['path'];assert sha(cp)==i['fullCandidate']['sha256'];c=json.loads(cp.read_text());findings=[]
 assert len(t['rows'])==len(i['rows'])==len(c['rows'])==10
 for x,y in zip(t['rows'],c['rows']):
  assert (x['sequence'],x['physicalPage'],x['sourceRowOnPage'],x['reviewTargetFields'])==(y['sequence'],y['physicalPage'],y['sourceRowOnPage'],y['reviewTargetFields'])
  assert set(x['literalSourceFields'])==set(x['reviewTargetFields'])
  for f,val in x['literalSourceFields'].items():
   if val!=y['expectedValues'][f]:findings.append({'sequence':x['sequence'],'field':f,'rootLiteral':val,'candidate':y['expectedValues'][f]})
 if findings:
  print(year,'SOURCE-RECHECK-REQUIRED',findings);continue
 source=Path(i['originalPdfCachePath']);assert sha(source)==i['sourceSha256'];doc=fitz.open(source);rendered={};field_crops=0
 for row in i['rows']:
  n=row['physicalPage']
  if n not in rendered:
   p=doc[n-1].get_pixmap(dpi=300,alpha=False);raw=p.tobytes('png');assert hashlib.sha256(raw).hexdigest()==row['actualSourceImageSha256'];rendered[n]=Image.frombytes('RGB',(p.width,p.height),p.samples)
  for field in row['sourceNativeFieldViews']:
   fp=R/field['path'];assert sha(fp)==field['sha256'];im=Image.open(fp).convert('RGB');actual=rendered[n].crop(field['originalPdf300DpiPixelBox']);assert actual.size==im.size and actual.tobytes()==im.tobytes();field_crops+=1
 result={'frozen':True,'reviewer':'/root','reviewedOn':'2026-11-01','sourceId':i['sourceId'],'sourceSha256':i['sourceSha256'],'imageFirstTranscript':{'path':str(tp.relative_to(R)),'sha256':sha(tp)},'sourceOnlyPacket':t['sourceOnlyPacket'],'candidate':i['fullCandidate'],'fieldPolicy':i['fieldPolicy'],'selectionConfiguration':i['selectionConfiguration'],'sourceThirdAllocation':i['sourceThirdAllocation'],'rows':10,'personallyImageTranscribedFields':t['fieldCount'],'allRequestedFieldsMatchExactly':True,'reviewerReadingCorrections':0,'candidateChanges':0,'unresolvedFields':0,'actualPdf300DpiPagesIndependentlyRegenerated':sorted(rendered),'everyActualSourceRenderShaMatched':True,'allNativeFieldCropsIndependentlyRegeneratedPixelExact':field_crops,'selectionLimitation': 'All2015flaggedrowsalreadyreserved; these10additionalunflaggedguardedrowsaddlayoutcoverage anddo notreplace anymanualreview.' if year=='2015-16' else 'Unreserved confidence-only eligible rows were deterministically selected3/4/3 across actual source page thirds; benchmark/manual/reserved rows excluded.','decision':'Pass this finite source-layout holdout. Whole-source acceptance still requires every real disagreement and source-quality target resolved, exact source controls or qualified literal residuals, independent final closure and all nine source holdouts. This is not personal image transcription or proof of every whole-source cell.','wholeSourceAccepted':False}
 if amendment_pin:result.update(reviewerReadingCorrections=amendment_count,additiveImageReadingAmendments=amendment_pin)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(str(out.relative_to(R)),sha(out),t['fieldCount'])
