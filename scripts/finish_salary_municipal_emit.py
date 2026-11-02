#!/usr/bin/env python3
"""Freeze a fully image-reviewed source candidate; no source is auto-accepted."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/"research/salaries/queue-completion-2026-11-01/municipal";COLLECTION=ROOT/"research/salaries/queue-completion-municipal"
SLUGS={"mission-2023":"city-of-mission","mission-2024":"city-of-mission","mission-2025":"city-of-mission","vernon-2025":"city-of-vernon"}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_once(path,raw):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():assert path.read_bytes()==raw,f"Frozen artifact differs: {path}"
 else:path.write_bytes(raw)
def emit(key):
 draft=AREA/"reader-draft-v2.json.gzip";packets=json.loads((AREA/"manual-review-packets.json").read_text());ledger=json.loads((AREA/"manual-review-ledger.json").read_text());allSections=json.loads(gzip.decompress(draft.read_bytes()))["sections"]
 expected=[p for p in packets["packets"] if p["sourceKey"]==key];reviewed={p["packetId"]:p for p in ledger["packets"]};assert expected and all(p["packetId"] in reviewed for p in expected),"Complete source review is not finished"
 relevant=[reviewed[p["packetId"]] for p in expected];corrections={(c["sectionIndex"],c["sectionRow"],c["field"]):c for p in relevant for c in p["corrections"]};outputs={};evidence=[]
 for si,section in enumerate(allSections):
  if section["layout"]["sourceKey"]!=key:continue
  cfg=section["layout"];scope=cfg["scope"];rows=outputs.setdefault(scope,[]);observations=[]
  for j,r in enumerate(section["tesseractRows"],1):
   cells={}
   for field in ("name","position","remuneration","expenses","total"):
    if field not in r["fields"]:continue
    source=r["fields"][field];amend=corrections.get((si,j,field))
    if amend:cells[field]=amend["value"]
    elif field in ("remuneration","expenses","total"):
     assert source["kind"] not in ("missing-detection","unparsed"),(si,j,field,source["raw"])
     cells[field]=source["value"]
    else:cells[field]=source["raw"]
   assert cells["name"] and cells.get("remuneration") is not None
   row=[SLUGS[key],cells["name"],cells.get("position"),cells["remuneration"],cells.get("expenses"),cfg["physicalPage"]];rows.append(row)
   observations.append({"sectionRow":j,"resolvedFields":cells,"tesseract":r,"paddle":section["paddleRows"][j-1],"amendments":[c for (s,n,_),c in corrections.items() if s==si and n==j]})
  evidence.append({"layout":cfg,"rawEvidenceFile":section["evidenceFile"],"rawEvidenceSha256":section["evidenceSha256"],"rowCount":len(observations),"observations":observations})
 files=[]
 for scope,rows in outputs.items():
  path=COLLECTION/f'{key}-{scope}.json.gzip';raw=json.dumps(rows,ensure_ascii=False,separators=(",",":")).encode();write_once(path,gzip.compress(raw,mtime=0));files.append({"scope":scope,"file":str(path.relative_to(ROOT)),"dataSha256":sha(path),"normalizedSha256":hashlib.sha256(raw).hexdigest(),"rowCount":len(rows),"totalRemuneration":sum(r[3] for r in rows),"knownTotalExpenses":sum(r[4] for r in rows if r[4] is not None),"nullExpenses":sum(r[4] is None for r in rows),"explicitZeroExpenses":sum(r[4]==0 for r in rows),"nullPositions":sum(r[2] is None for r in rows),"physicalPages":sorted(set(r[5] for r in rows))})
 snapshot={"date":"2026-11-01","sourceKey":key,"sourceEmployeeScopeComplete":True,"rowReviewBasis":"Every named source row personally checked for all published names, titles and money fields against actual PDF-painted300dpi images. Each source-dash versus zero personally checked; no missing OCR detection automatically treated as a dash. Every raw-engine disagreement adjudicated to the final original-image reading. All repeated names/observations retained literally.","rawReaderV2Sha256":sha(draft),"reviewPackets":expected,"manualPacketReviews":relevant,"sections":evidence,"candidateFiles":files,"independentPeerReviewStatus":"pending","acceptedRows":0}
 path=AREA/f'{key}-original-review.json.gzip';write_once(path,gzip.compress(json.dumps(snapshot,ensure_ascii=False,separators=(",",":")).encode(),mtime=0))
 print(json.dumps({"source":key,"sourceReview":str(path.relative_to(ROOT)),"sourceReviewSha256":sha(path),"cohorts":files},indent=2))
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("key",choices=SLUGS);args=parser.parse_args();emit(args.key)

