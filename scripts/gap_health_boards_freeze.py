#!/usr/bin/env python3
"""Freeze only accepted board-worker inputs, leaving root and later peer work separate."""
import argparse
import hashlib
import json
from pathlib import Path
import gap_health_boards as g

ROOT=g.ROOT
AREA=g.AREA
DEST=AREA/'candidate-freeze.json'
SCRIPTS=['gap_health_boards.py','gap_health_boards_fetch.py','gap_health_boards_library.py','gap_health_boards_visibility.py','gap_health_boards_visibility_v1.py','gap_health_boards_freeze.py','test_gap_health_boards.py']

def frozen_files():
    paths=[]
    for folder in [AREA,g.OUT]:
        for p in folder.rglob('*'):
            if not p.is_file() or p in [DEST,AREA/'handoff.json']:continue
            if p.is_relative_to(AREA/'peer-health-employees'):continue
            paths.append(p)
    paths.extend(ROOT/'scripts'/name for name in SCRIPTS)
    return sorted(paths,key=lambda p:str(p.relative_to(ROOT)))

def snapshot():
    assert g.review_adoption() is not None,'Root independent acceptance must be adopted before freeze'
    files=[]
    for p in frozen_files():
        raw=p.read_bytes();files.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    return {'schema':'salary-gap-fill-health-boards-worker-freeze-v1','noOutreach':True,'scope':'Only board-worker owned source/code/normalization inputs. Root independent receipts are separately owned and hash-referenced by review-adoption.json. Later peer-health-employees readings are separately reviewed inputs and excluded from this board freeze.','files':files}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    if args.write:
        raw=g.packed(snapshot())
        if DEST.exists():assert DEST.read_bytes()==raw,'Existing freeze differs; create an explicit new revision instead of overwriting'
        else:DEST.write_bytes(raw)
    else:
        frozen=json.loads(DEST.read_bytes())
        assert frozen['noOutreach'] is True
        for entry in frozen['files']:
            raw=(ROOT/entry['path']).read_bytes();assert len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],entry['path']
        g.review_adoption()
    print(json.dumps({'files':len(json.loads(DEST.read_bytes())['files']),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'checked':True}))

if __name__=='__main__':main()
