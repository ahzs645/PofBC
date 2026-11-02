#!/usr/bin/env python3
"""Freeze north producer inputs only; later disjoint peer work stays outside."""
import argparse,gzip,hashlib,json
from pathlib import Path
from gap_school_north_accept import ROOT,AREA,COLLECTION,read,ref,sha,build_adoption,validate_adoption
SCRIPTS=['gap_school_north_discovery.py','gap_school_north_ocr.py','gap_school_north_extra_tess.py','gap_school_north_parse.py','gap_school_north_pixels.py','gap_school_north_candidates.py','gap_school_north_packets.py','gap_school_north_sd82_packets.py','gap_school_north_spacing.py','gap_school_north_context.py','gap_school_north_finalize.py','gap_school_north_accept.py','gap_school_north_handoff.py','test_gap_school_north.py']

def build():
 adoption=read(AREA/'review-adoption.json');validate_adoption(adoption)
 assert adoption==build_adoption(),'Independent acceptance no longer matches exact source/data/provenance inputs'
 manifest=read(COLLECTION/'sources.json');assert manifest['reviewed'] and all(s['status']=='verified' for s in manifest['sources'])
 paths=[]
 for root in [AREA,COLLECTION]:
  for p in root.rglob('*'):
   if not p.is_file() or p.name in ['candidate-freeze.json','handoff.json'] or 'reviews' in p.relative_to(root).parts:continue
   paths.append(p)
 paths += [ROOT/'scripts'/s for s in SCRIPTS]
 files=[ref(p) for p in sorted(paths)]
 freeze={'schema':'gap-school-north-producer-freeze-v1','baselineCommit':'de42c55e98e42b8001f07e4ecbd210f892ab2716','noOutreach':True,'scope':'Only north producer research, normalization and explicitly listed producer scripts/tests. Other agents own their independent source receipts, which are hash-referenced rather than frozen by this worker. Future reviews/ files and later north peer scripts are outside this producer freeze.','files':files}
 dispositions=[]
 for spec in read(AREA/'ocr-plan.json'):
  n=spec['number'];sources=[s for s in manifest['sources'] if s['employerSlug']==f'school-district-{n:02}']
  dispositions.append({'leadId':spec['leadId'],'number':n,'disposition':'completed-official-source-import-with-explicit-source-qualifications','reportedPeriod':'2024/25','sourceUrl':spec['sourceUrl'],'sourceSha256':spec['sha256'],'sourcePhysicalSalaryPages':spec['salaryPages'],'rowsAdded':sum(s['rowCount'] for s in sources),'cohorts':[{'id':s['id'],'scope':s['scope'],'rows':s['rowCount'],'data':ref(COLLECTION/s['file']),'provenance':ref(COLLECTION/s['provenanceFile']),'printedControls':s['validation']['printedControlTotals'],'computedTotals':s['validation']['computedComponentTotals'],'literalRowsMinusPrintedControls':s['validation']['controlResiduals'],'publicWarning':s['publicWarning']} for s in sources],'compiledRowsRemoved':0,'outreachPerformed':False,'remainingProcessingBlockers':[]})
 return freeze,{'schema':'gap-school-north-final-handoff-v1','complete':True,'noOutreach':True,'reports':8,'cohorts':16,'rowsAdded':1884,'employeeRowsAdded':1827,'trusteeRowsAdded':57,'employersNewAgainstBaseline':7,'compiledRowsRemoved':0,'collection':'gap-fill-school-north','sourceManifest':ref(COLLECTION/'sources.json'),'independentAcceptance':ref(AREA/'review-adoption.json'),'dispositions':dispositions,'remainingPublicProcessingTasks':0,'sourceClarificationNotes':[{'number':8,'issue':'Source whole-dollar literal rows differ from printed named controls by small nonzero residuals. Cause unknown; no rounding claim. No outreach performed.'},{'number':59,'issue':'Complete independently transcribed248employee rows differ from printed named controls by−504385.57remuneration/−580.00expenses. Literal rows accepted with public warning; clarification from the publisher remains useful, with no outreach performed.'}],'validationCommands':['python -m unittest discover -s scripts -p test_gap_school_north.py -v','python scripts/gap_school_north_accept.py','python scripts/gap_school_north_finalize.py --check','python scripts/gap_school_north_handoff.py --check'],'freezeScopeExcludesFuturePeerWork':True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();freeze,handoff=build();fp=AREA/'candidate-freeze.json';fr=(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n').encode()
 if args.check or fp.exists():assert fp.read_bytes()==fr,'Frozen producer inputs changed; create an explicit additive revision'
 else:fp.write_bytes(fr)
 handoff['producerFreeze']=ref(fp);hp=AREA/'handoff.json';hr=(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n').encode()
 if args.check:assert hp.read_bytes()==hr,'Handoff changed'
 else:hp.write_bytes(hr)
 print(json.dumps({'status':'passed','reports':8,'cohorts':16,'rows':1884,'producerFiles':len(freeze['files']),'freezeSha256':sha(fr),'handoffSha256':sha(hr)}))

if __name__=='__main__':main()
