#!/usr/bin/env python3
"""Finalize the exact65 source batch from the pinned root adoption; no registration."""
import copy,gzip,hashlib,json,pathlib,sys
from gap_health_employees_native import ROOT,AREA
COLLECTION=ROOT/'research/salaries/gap-fill-health-employees'
APPROVAL='research/salaries/gap-fill-2026-11-02/reviews/root-sixty-five-health-source-acceptance.json'
APPROVAL_SHA='617e3e025adea89e6b44d2772564c80fedeb5ceae97dd88d67d70961e4445ee1'
CANDIDATE_SHA='ad82f4dba33d6322715c0bb7e278d6ecccf2a27e263e5658eb3fee2f2886bbb6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def main():
 if '--check' in sys.argv:
  frozen=json.load(open(AREA/'frozen-inputs.json'))
  for f in frozen['files']:assert sha(ROOT/f['path'])==f['sha256'],('Frozen input changed',f['path'])
  print(json.dumps({'frozenInputs':len(frozen['files']),'status':'PASS'}));return
 approval=ROOT/APPROVAL;assert sha(approval)==APPROVAL_SHA
 original=COLLECTION/'sources-candidate.json';assert sha(original)==CANDIDATE_SHA
 manifest=json.load(open(original));assert len(manifest['sources'])==65 and sum(s['rowCount'] for s in manifest['sources'])==207001
 sources=copy.deepcopy(manifest['sources']);proof={'path':APPROVAL,'sha256':APPROVAL_SHA}
 for s in sources:
  data=COLLECTION/s['file'];candidateProv=COLLECTION/s['provenanceFile'];assert sha(data)==s['dataSha256'] and sha(candidateProv)==s['provenanceSha256']
  p=json.load(gzip.open(candidateProv,'rt'));prior=ref(candidateProv);p['status']='verified through exact root full-source and normalized-data adoption; source qualifications remain explicit';p['publicationAdoption']=proof;p['candidateProvenance']=prior
  fname=s['provenanceFile'].replace('-provenance.json.gzip','-reviewed-provenance.json.gzip');f=COLLECTION/fname;f.write_bytes(gzip.compress(json.dumps(p,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));s['provenanceFile']=fname;s['provenanceSha256']=sha(f);s['status']='verified';v=s['validation'];v['status']='verified with literal source qualifications';v['candidateOnly']=False;v['pendingGates']=[];v['independentPeerVerified']=True;v['rootSourceAcceptance']=proof;v['acceptedCandidateManifest']={'path':str(original.relative_to(ROOT)),'sha256':CANDIDATE_SHA};v['acceptedCandidateProvenance']=prior
 final={'schemaVersion':1,'status':'verified; original monetary/count/name-clipping qualifications remain explicit','noOutreach':True,'rootSourceAcceptance':proof,'sources':sources};mp=COLLECTION/'sources.json';mp.write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
 ld=AREA/'lead-dispositions.json';ledger=json.load(open(ld));ledger['publicationStatus']='verified65batch; delegated extensions are separate and remain pending in this historical ownership handoff';ledger['sourceManifest']=ref(mp)
 for r in ledger['leads']:r['batchAcceptanceState']='verified65batch; pending delegated scopes are not included in accepted counts'
 ld.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
 md=AREA/'lead-dispositions.md';text=md.read_text();text=text.replace('The65batch is source-reviewed and awaits root final adoption.','The 65-source batch has root final adoption; separately delegated scopes remain pending in this historical ownership ledger.');md.write_text(text)
 summary=AREA/'normalized-candidate-summary.json';reviewed=json.load(open(summary));reviewed['status']='verified65batch';reviewed['rootSourceAcceptance']=proof
 for s in reviewed['sources']:
  fin=next(v for v in sources if v['id']==s['id']);s['provenanceSha256']=fin['provenanceSha256'];s['candidate']=False
 (AREA/'normalized-reviewed-summary.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n')
 ready=json.load(open(AREA/'handoff-ready.json'));ready.update({'accepted':True,'rootAccepted':True,'candidateReady':True,'manifest':ref(mp),'leadDispositions':ref(ld),'rootSourceAcceptance':proof,'status':'accepted65employee batch; ready for root integration; delegated extensions excluded','pending':['Separate PHSA9, Northern6/Island3, Frasercontractcomparison,19boardsupplement and28financialscopeaudit close through their own handoffs.']})
 for r in ready['sources']:
  fin=next(v for v in sources if v['id']==r['sourceId']);r['provenanceSha256']=fin['provenanceSha256']
 # Freeze only this worker's owned files and current owned-prefix scripts. Other
 # workers' review receipts are referenced by exact hashes, never frozen here.
 paths=[]
 for base in [AREA,COLLECTION]:
  paths += [p for p in base.rglob('*') if p.is_file() and p.name not in ['frozen-inputs.json','handoff.json'] and '__pycache__' not in p.parts]
 paths += list((ROOT/'scripts').glob('gap_health_employees*.py'))+[ROOT/'scripts/test_gap_health_employees.py']
 paths=sorted(set(paths));freeze={'scope':'Only65employee worker owned inputs; root/common/otherworker files are not frozen by this manifest. Later health_other_history area is separate.','rootSourceAcceptance':proof,'files':[dict(ref(p),bytes=p.stat().st_size) for p in paths]};fp=AREA/'frozen-inputs.json';fp.write_text(json.dumps(freeze,indent=2)+'\n');ready['freeze']=ref(fp);ready['frozenInputCount']=len(paths);hp=AREA/'handoff.json';hp.write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'sources':65,'rows':207001,'manifest':ref(mp),'handoff':ref(hp),'freeze':ref(fp),'frozenInputs':len(paths)}))
if __name__=='__main__':main()
