#!/usr/bin/env python3
"""Freeze only the separately owned19-source supplemental board evidence."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_board_supplement'
OUT=ROOT/'research/salaries/gap-fill-health-board-supplement'
SCRIPTS=['gap_health_board_supplement.py','gap_health_board_supplement_freeze.py','test_gap_health_board_supplement.py']


def current():
    paths={p for base in [AREA,OUT] for p in base.rglob('*')if p.is_file()and p.name not in ['candidate-freeze.json','handoff.json']}
    paths.update(ROOT/'scripts'/s for s in SCRIPTS)
    return {'schema':'health-board-supplement-owned-freeze-v1','noOutreach':True,
        'ownership':'Only new supplemental board collection/research/scripts. Original health_boards frozen inputs and peer reviews owned by North/root remain outside this freeze.',
        'files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(paths)]}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');args=ap.parse_args();path=AREA/'candidate-freeze.json';result=current();raw=(json.dumps(result,indent=2)+'\n').encode()
    if args.check:
        if path.read_bytes()!=raw:raise ValueError('Owned supplemental inputs changed after freeze')
    else:
        if path.exists():raise ValueError('Freeze exists; refusing to overwrite')
        path.write_bytes(raw)
    print(json.dumps({'files':len(result['files']),'sha256':hashlib.sha256(raw).hexdigest(),'checked':args.check}))


if __name__=='__main__':main()
