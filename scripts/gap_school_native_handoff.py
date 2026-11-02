#!/usr/bin/env python3
"""Freeze only this worker's final inputs; append-only peer reviews remain separate."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native'
COLLECTION=ROOT/'research/salaries/gap-fill-school-native'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def pack(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()


def main(check=False):
    manifest=json.loads((COLLECTION/'sources.json').read_bytes());assert manifest['reviewed'] is True
    assert len(manifest['sources'])==14 and sum(s['rowCount'] for s in manifest['sources'])==5476
    assert all(s['status']=='verified' and s['validation']['compiledPartitionRetained'] is True for s in manifest['sources'])
    files=[]
    for folder in [AREA,COLLECTION]:
        for path in folder.rglob('*'):
            if not path.is_file() or path.name in ['candidate-freeze.json','handoff.json'] or '__pycache__' in path.parts:continue
            if folder==AREA and 'reviews' in path.relative_to(AREA).parts:continue
            files.append(path)
    files+=list((ROOT/'scripts').glob('gap_school_native*.py'))
    files.append(ROOT/'scripts/test_gap_school_native.py')
    entries=[ref(p) for p in sorted(set(files))]
    freeze={'schema':'gap-fill-school-native-worker-freeze-v1','baselineCommit':'de42c55e98e42b8001f07e4ecbd210f892ab2716','noOutreach':True,'files':entries,'scope':'Only own seven-source final processing/payload inputs and already-completed south peer evidence. No root/global/other-worker live files are frozen. Future owned reviews/ additions are explicitly outside this freeze.'}
    frozen=pack(freeze);fpath=AREA/'candidate-freeze.json'
    if check:assert fpath.read_bytes()==frozen,'Worker input freeze differs'
    else:fpath.write_bytes(frozen)
    dispositions=[]
    for lead in json.loads((AREA/'assigned-leads.json').read_bytes()):
        number=int(lead['employer'].split('No. ')[1].split()[0]);sources=[s for s in manifest['sources'] if s['id'].startswith(f'gap-fill-school-native-sd{number}-2025-')]
        assert len(sources)==2
        dispositions.append({'leadId':lead['id'],'status':'completed-with-published-source-qualifications' if any(not s['validation']['summaryReconciles'] or (number==34 and s['category']=='employee-remuneration') for s in sources) else 'completed-verified-public-original',
                             'sourceIds':[s['id'] for s in sources],'officialRowsAdded':sum(s['rowCount'] for s in sources),'remainingPublicProcessingTasks':0,'issuerRequestSent':False,'notes':'Literal source definitions, source control residuals, clipping and bounded OCR qualifications remain public; no inferred individual or compiled-copy deletion.'})
    handoff={'schema':'gap-fill-school-native-worker-handoff-v1','complete':True,'baselineCommit':freeze['baselineCommit'],'noOutreach':True,'collection':'gap-fill-school-native','manifest':ref(COLLECTION/'sources.json'),'candidateFreeze':{'path':str(fpath.relative_to(ROOT)),'sha256':sha(frozen)},'reports':7,'sourceCohorts':14,'rowsAdded':5476,'employeeRowsAdded':5429,'trusteeRowsAdded':47,'compiledRowsRemoved':0,'remainingPublicProcessingTasks':0,'dispositions':dispositions,
             'sourcePayloads':[{'sourceId':s['id'],'sourceSha256':s['sha256'],'file':s['file'],'dataSha256':s['dataSha256'],'provenanceFile':s['provenanceFile'],'provenanceSha256':s['provenanceSha256'],'rows':s['rowCount'],'sourceUrl':s['sourceUrl'],'status':s['status']} for s in manifest['sources']],
             'reviewSelection':ref(AREA/'peer-selection.json'),'verificationCommands':['python3 scripts/gap_school_native_build.py --check','python3 scripts/gap_school_native_coverage.py','python3 -m unittest discover -s scripts -p test_gap_school_native.py','python3 scripts/gap_school_native_handoff.py --check'],
             'regressionTests':16,'sourceProcessingQualifications':['SD53/84 originally mislabeled native leads but salary tables need OCR; complete two-reader processing and bounded source image reviews are preserved.','SD41 district original used instead of Ministry hidden OCR; source representations and differences preserved.','SD34tenclipped positions retain only exact independently adopted visible prefixes.','All source residuals remain literal and qualified; no cause or balancing value inferred.','All prior compiled observations retained without identity or period equivalence.']}
    hp=AREA/'handoff.json';raw=pack(handoff)
    if check:assert hp.read_bytes()==raw,'Final handoff differs'
    else:hp.write_bytes(raw)
    print(json.dumps({'status':'passed','files':len(entries),'cohorts':14,'rows':5476,'handoffSha256':sha(raw),'freezeSha256':sha(frozen)}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();main(args.check)
