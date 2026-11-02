#!/usr/bin/env python3
"""Complete comparison-only municipal multisets; never infer period mappings."""
import collections
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/municipal'
COLLECTION=ROOT/'research/salaries/queue-completion-municipal'
BASELINE=ROOT/'research/salaries/compiled-baseline.json.gzip'
TARGETS=[('city-of-mission','2023','mission-2023-employee-remuneration-v2.json.gzip'),('city-of-mission','2024','mission-2024-employee-remuneration.json.gzip'),('city-of-mission','2025','mission-2025-employee-remuneration.json.gzip'),('city-of-vernon','2025','vernon-2025-employee-remuneration.json.gzip'),('town-of-creston','2024','creston-2024-employee-remuneration.json.gzip')]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def freeze(path,data):
    if path.exists():assert path.read_bytes()==data,str(path)
    else:path.write_bytes(data)

def run():
    assert sha(BASELINE)=='410bcae27c9755e387c473ab44d62081a50b46e7330f4d6d5c0b74979d392760'
    baseline=json.loads(gzip.decompress(BASELINE.read_bytes()))
    employers={e['slug']:e for e in baseline['employers']}
    findings=[]
    for slug,year,filename in TARGETS:
        path=COLLECTION/filename;rows=json.loads(gzip.decompress(path.read_bytes()));official=[r[1:5] for r in rows]
        finding={'employerSlug':slug,'officialCalendarYear':year,'officialFile':str(path.relative_to(ROOT)),'officialDataSha256':sha(path),'officialEmployeeRows':len(rows),'completeOfficialRows':rows,'compiledComparisons':[],'retainCompiledPartition':True,'periodMappingInferred':False,'deletionAuthorized':False}
        employer=employers.get(slug)
        if employer:
            for i,label in enumerate(baseline['years']):
                compiled=[r[:4] for r in employer['rows'] if r[4]==i]
                if not compiled:continue
                ca=collections.Counter(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in compiled)
                oa=collections.Counter(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in official)
                matched=ca&oa
                finding['compiledComparisons'].append({'compiledLabel':label,'compiledRows':len(compiled),'completeCompiledRows':compiled,'strictNamePositionPayExpenseMultisetMatches':sum(matched.values()),'strictUnmatchedCompiledRows':[json.loads(k) for k,n in (ca-oa).items() for _ in range(n)],'strictUnmatchedOfficialRows':[json.loads(k) for k,n in (oa-ca).items() for _ in range(n)],'periodCompatibility':'unproved: fiscal-style compiled label is not silently mapped to a calendar year','noInitialExpansionNameInferenceNullZeroEquivalenceOrRounding':True})
        finding['compiledEmployerPresent']=employer is not None
        findings.append(finding)
    receipt={'date':'2026-11-01','baselineFile':str(BASELINE.relative_to(ROOT)),'baselineSha256':sha(BASELINE),'baselineSnapshotSourceId':'pssdb-2026-10-22','method':'Complete strict name/position/pay/expense multiset comparison against every retained compiled label for the exact employer slug; multiplicity and null-versus0 remain distinct. Physical PDF page is an official-source locator, not a comparable compiled field. No name expansion, punctuation/case normalization, rounding or calendar/fiscal mapping. Comparisons are supporting evidence only. All new sources retain compiled partitions.','findings':findings,'deletionAuthorized':False}
    out=AREA/'compiled-comparison.json.gzip';freeze(out,gzip.compress(json.dumps(receipt,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    print(json.dumps({'path':str(out.relative_to(ROOT)),'sha256':sha(out),'summary':[{'employerSlug':f['employerSlug'],'calendarYear':f['officialCalendarYear'],'officialRows':f['officialEmployeeRows'],'compiledLabels':[{k:c[k] for k in ['compiledLabel','compiledRows','strictNamePositionPayExpenseMultisetMatches']} for c in f['compiledComparisons']]} for f in findings]},indent=2))

if __name__=='__main__':run()
