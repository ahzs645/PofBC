#!/usr/bin/env python3
"""Freeze only the southern worker's source/evidence/normalized/code ownership."""
import argparse,hashlib,json
from pathlib import Path
from gap_school_south_fetch import AREA,ROOT
COLLECTION=ROOT/'research/salaries/gap-fill-school-south'
FREEZE=AREA/'producer-freeze.json'

def sha(b):return hashlib.sha256(b).hexdigest()
def files():
 paths=set(p for base in [AREA,COLLECTION] for p in base.rglob('*') if p.is_file() and p.name not in ['producer-freeze.json','handoff.json'] and '__pycache__' not in p.parts)
 paths.update((ROOT/'scripts').glob('gap_school_south*.py'));paths.update((ROOT/'scripts').glob('test_gap_school_south*.py'))
 return sorted(paths)
def document():
 manifest=json.loads((COLLECTION/'sources.json').read_text());assert manifest['reviewed'] and len(manifest['sources'])==20 and sum(s['rowCount'] for s in manifest['sources'])==9845
 return {'schema':'salary-gap-fill-school-south-producer-freeze-v1','owner':'school_south','createdOn':'2026-11-02','normalizedManifest':str((COLLECTION/'sources.json').relative_to(ROOT)),'normalizedManifestSha256':sha((COLLECTION/'sources.json').read_bytes()),'scope':'Only owned school_south/**, gap-fill-school-south/** and gap_school_south/test_gap_school_south scripts. Old frozen and global inputs are outside this freeze. handoff.json is excluded to avoid a checksum cycle and pins this freeze.','files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in files()],'noOutreach':True,'noCompiledRowsDeleted':True}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();current=document();blob=(json.dumps(current,ensure_ascii=False,indent=2)+'\n').encode()
 if a.check:assert FREEZE.read_bytes()==blob,'Southern producer files changed after freeze.'
 else:FREEZE.write_bytes(blob)
 print(json.dumps({'frozenFiles':len(current['files']),'bytes':sum(x['bytes'] for x in current['files']),'freezeSha256':sha(blob),'pass':True}))
if __name__=='__main__':main()
