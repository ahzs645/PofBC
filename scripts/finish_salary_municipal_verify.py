#!/usr/bin/env python3
"""Replay frozen readers and verify actual originals without running new OCR."""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import fitz

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/municipal'
COLLECTION=ROOT/'research/salaries/queue-completion-municipal'
CACHE=Path('/tmp/queue-completion-municipal')

def sha(data):return hashlib.sha256(data).hexdigest()
def run(originals=False):
    commands=[['scripts/finish_salary_municipal_reader_v2.py']]
    commands += [['scripts/finish_salary_municipal_emit.py',k] for k in ['mission-2023','mission-2024','mission-2025','vernon-2025']]
    commands += [['scripts/finish_salary_municipal_amend.py'],['scripts/finish_salary_municipal_creston.py'],['scripts/finish_salary_municipal_compare.py'],['scripts/finish_salary_municipal_routes.py']]
    for command in commands:
        subprocess.run([sys.executable,*command],cwd=ROOT,check=True,capture_output=True)
    files=['mission-2023-employee-remuneration-v2.json.gzip','mission-2023-elected-officials.json.gzip','mission-2024-employee-remuneration.json.gzip','mission-2024-elected-officials.json.gzip','mission-2025-employee-remuneration.json.gzip','mission-2025-elected-officials.json.gzip','vernon-2025-employee-remuneration.json.gzip','vernon-2025-elected-officials.json.gzip','creston-2024-employee-remuneration.json.gzip']
    payloads={f:json.loads(gzip.decompress((COLLECTION/f).read_bytes())) for f in files}
    rows=[r for group in payloads.values() for r in group]
    assert len(rows)==835
    assert sum(r[4] is None for r in rows)==60
    assert sum(r[4]==0 for r in rows)==38
    assert sum(r[2] is None for r in rows)==264
    assert all(len(r)==6 and isinstance(r[3],(int,float)) and (r[4] is None or isinstance(r[4],(int,float))) for r in rows)
    assert payloads['mission-2023-employee-remuneration-v2.json.gzip'][10][3]==93271
    result={'date':'2026-11-01','offlineReplayPassed':True,'candidateSources':9,'rows':835,'nullExpenses':60,'explicitZeroExpenses':38,'nullPositions':264,'replayedCommands':commands,'originalPdfPaintedRenderRechecks':[]}
    if originals:
        docs={}
        for path in sorted((AREA/'ocr').glob('*.json.gzip')):
            raw=json.loads(gzip.decompress(path.read_bytes()));key=raw['sourceKey'];original=CACHE/(key+'.pdf')
            assert sha(original.read_bytes())==raw['sourceSha256']
            if key not in docs:docs[key]=fitz.open(original)
            page=raw['physicalPage'];png=docs[key][page-1].get_pixmap(dpi=300,alpha=False).tobytes('png')
            assert sha(png)==raw['render']['imageSha256'],(key,page)
            result['originalPdfPaintedRenderRechecks'].append({'sourceKey':key,'physicalPage':page,'sourceSha256':raw['sourceSha256'],'actualRgb300DpiPngSha256':sha(png),'matchesFrozenRawOcrInput':True})
        assert len(result['originalPdfPaintedRenderRechecks'])==30
    out=AREA/('original-replay-verification.json' if originals else 'offline-replay-verification.json')
    data=(json.dumps(result,indent=2)+'\n').encode()
    if out.exists():assert out.read_bytes()==data
    else:out.write_bytes(data)
    print(json.dumps({'receipt':str(out.relative_to(ROOT)),'sha256':sha(data),'rows':835,'originalRenderChecks':len(result['originalPdfPaintedRenderRechecks'])}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--originals',action='store_true');a=p.parse_args();run(a.originals)
