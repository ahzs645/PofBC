#!/usr/bin/env python3
"""Freeze literal candidate payloads only after complete MuPDF/Poppler agreement."""
import collections,gzip,hashlib,json,pathlib
from finish_salary_acquisition_native import SPECS,ROOT,AREA
COLLECTION=ROOT/'research/salaries/queue-completion-acquisition'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def freeze(path,raw):
 if path.exists():assert path.read_bytes()==raw,('Immutable candidate differs',path)
 else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
def build():
 summaries=[]
 for s in SPECS:
  mp=AREA/(s['id']+'-mupdf-raw.json.gzip');pp=AREA/(s['id']+'-poppler-raw.json.gzip');m=json.loads(gzip.decompress(mp.read_bytes()));p=json.loads(gzip.decompress(pp.read_bytes()))
  for scope in ['employeeRecords','boardRecordsAllLiteral']:assert [r['row'] for r in m[scope]]==[r['row'] for r in p[scope]]
  for category,records in [('employees',m['employeeRecords']),('board-numeric-pay',[r for r in m['boardRecordsAllLiteral'] if r['row'][3] is not None])]:
   rows=[r['row'] for r in records];raw=gzip.compress(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);path=COLLECTION/(s['id']+'-'+category+'.json.gzip');freeze(path,raw);summaries.append({'id':s['id']+'-'+category,'file':str(path.relative_to(ROOT)),'sha256':sha(raw),'rowCount':len(rows),'remuneration':sum(r[3] for r in rows),'knownExpenses':sum(r[4] or 0 for r in rows),'nullExpenses':sum(r[4] is None for r in rows),'zeroExpenses':sum(r[4]==0 for r in rows),'negativeExpenses':sum((r[4] or 0)<0 for r in rows),'sourcePages':sorted(set(r[5] for r in rows)),'sourceSha256':s['sha256'],'mupdfEvidenceSha256':sha(mp.read_bytes()),'popplerEvidenceSha256':sha(pp.read_bytes()),'independentNativeRowsExactlyEqual':True,'status':'candidate-awaiting-source-image-and-independent-peer-closure','retainCompiledPartition':True})
  nonnumeric=[r for r in m['boardRecordsAllLiteral'] if r['row'][3] is None]
  if nonnumeric:
   path=AREA/(s['id']+'-board-nonnumeric-pay-research.json');raw=(json.dumps({'scope':'All printed board observations with nonnumeric remuneration, retained only as research; no dash-to-zero inference or normalized salary row','sourceSha256':s['sha256'],'rows':nonnumeric,'normalizedSalaryRows':0},ensure_ascii=False,indent=2)+'\n').encode();freeze(path,raw)
 p=AREA/'native-candidate-payloads.json';freeze(p,(json.dumps({'sources':summaries,'nameTypographyOnly':'Collapse source whitespace and spaces adjacent to comma; combine Providence visibly separate last/first columns with comma. Preserve all source letters/case/hyphen characters and literal suffixes, positions null.','sourceMutationCount':0,'status':'candidates; not accepted until independent review'},ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'manifest':str(p.relative_to(ROOT)),'manifestSha256':sha(p.read_bytes()),'candidates':[{k:x[k] for k in ['id','rowCount','remuneration','knownExpenses','nullExpenses','zeroExpenses','negativeExpenses','sha256']} for x in summaries]},ensure_ascii=False,indent=2))
if __name__=='__main__':build()
