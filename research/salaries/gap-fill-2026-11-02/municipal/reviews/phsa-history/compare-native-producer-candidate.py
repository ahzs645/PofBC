from pathlib import Path
import gzip,json,hashlib,re
from decimal import Decimal
R=Path('/workspace/PofBC');B=Path(__file__).resolve().parent;P=R/'research/salaries/gap-fill-2026-11-02/phsa_history'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def norm(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip()) if isinstance(s,str) else s
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
freeze=json.loads((B/'native-independent-source-freeze.json').read_text());assert all(sha((R/x['path']).read_bytes())==x['sha256'] for x in freeze['files'])
out=[]
for key in ['phsa-2006-07','phsa-2007-08','phsa-2008-09']:
 pp=P/(key+'-native-candidate-v2.json.gzip');ep=B/(key+'-peer-selected-native-rows.json.gzip');p=read(pp);e=read(ep);comparisons=[]
 for reader in ['popplerRows','mupdfRows']:
  diffs=[];assert len(p[reader])==len(e['rows'])
  for i,(a,b) in enumerate(zip(e['rows'],p[reader]),1):
   for f in ['pdfPage','name','position','remuneration','expenses']:
    av=a[f];bv=b[f]
    if f in ['remuneration','expenses']:bv=None if bv is None else Decimal(str(bv));av=None if av is None else Decimal(str(av))
    if f=='name':av=norm(av);bv=norm(bv)
    if av!=bv:diffs.append({'sequence':i,'field':f,'peer':str(av),'producer':str(bv)})
   if a['sourceNameFootnote']!=b['sourceFootnoteMarker']:diffs.append({'sequence':i,'field':'sourceFootnoteMarker','peer':a['sourceNameFootnote'],'producer':b['sourceFootnoteMarker']})
   # Complete literal monetary cell comparison catches null/zero definition changes.
   if a['sourceRemuneration']!=b['sourceCellTexts'][1] or a['sourceExpenses']!=b['sourceCellTexts'][2]:diffs.append({'sequence':i,'field':'literalMoneyCells','peer':[a['sourceRemuneration'],a['sourceExpenses']],'producer':b['sourceCellTexts'][1:]})
  comparisons.append({'reader':reader,'rowsCompared':len(e['rows']),'fiveFieldsAndLiteralMoneyAndFootnotesCompared':True,'differences':diffs})
 assert p['source']['sourceSha256']==e['sourceSha256'];assert not any(c['differences'] for c in comparisons),comparisons
 out.append({'sourceKey':key,'sourceSha256':e['sourceSha256'],'producerCandidatePin':pin(pp),'independentPeerRowsPin':pin(ep),'comparisons':comparisons,'all4082PersonRowsPersonallyRead':False})
result={'status':'pass for exact pinned native-v2 candidate fields, qualified source controls/counts retained','scope':'Complete4082-row native computational comparison and independent full payment census; bounded33-row personal image transcription/66money cells plus actual source contexts/definitions/control totals.','sourceFirstEvidenceFreeze':pin(B/'native-independent-source-freeze.json'),'independentSourceAudit':pin(B/'native-complete-independent-source-audit.json'),'sources':out,'totalRows':4082,'twoProducerReadersComparedAgainstIndependentPeerExtraction':True,'allFieldsAgree':True,'allLiteralMoneyCellsAgree':True,'sourceDashesRemainUnknown':True,'noAmountsBalancedOrRowsDropped':True,'requiredPublicationQualifications':['2006/07 actual table1267names differs narrative1280; literal printed pay and known-expense controls differ from rows.','2007/08 and2008/09 literal monetary-control residuals preserved, no inferred rounding cause.','No annualized base salary or complete workforce claim; expenses can include third-party payments; job titles not published.','Source is official Legislative Library archival copy with explicit added cover and delivered SHA distinct from stored bitstreamMD5/size.'],'producerFinalNormalizedSourceManifestNotYetReviewed':True,'noOutreach':True}
p=B/'native-v2-producer-comparison.json';p.write_text(json.dumps(result,indent=2)+'\n');print(sha(p.read_bytes()))
