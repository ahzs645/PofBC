#!/usr/bin/env python3
"""Batch010457 requested-field resolution from immutable image-first transcript."""
import json,hashlib,collections
from pathlib import Path
BASE=Path("research/salaries/held-resolution-2026-11-01");REV=BASE/"reviews";P="independent-phsa-nic-reviewer-010"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=REV/f"{P}-image-transcript.json";full=BASE/"health/review-batch-010.json";images=BASE/"health/review-batch-010-images.json";fidelity=REV/f"{P}-painted-source-fidelity.json"
assert sha(raw)=="a518cf203d9e080209e848d2ccd61da39813504b9c4a859e0d7e9674cd148587"
assert sha(full)=="14529e936061b9997f332195b17213daa48e2b0a87b75f699c99966cf4e5a852"
assert sha(images)=="1f45e5b1b43e524062ff6ffe87007f63b77fd5eec7b997037199105acafcc947"
assert sha(fidelity)=="66b4cc6c93cbe248bd96aa7d53123ef6a02220e6263a388aa003123f28991592"
t=json.loads(raw.read_text());batch=json.loads(full.read_text());im=json.loads(images.read_text());f=json.loads(fidelity.read_text());assert len(batch["rows"])==len(t["namesInFrozenBatchOrder"])==len(f["rows"])==457;assert t["paintedSheetsRead"]==list(range(1,47))
names=list(t["namesInFrozenBatchOrder"])
corrections=[
 {"physicalPage":253,"sourceRowOnPage":1,"before":"Toews,Jordane M","after":"Toews,Jordanne M","reason":"Candidate comparison prompted fresh individual actualPDF crop reread; reviewer had omitted one n. The original visibly prints Jordanne. Candidate already correct; frozen raw transcript unchanged.","phase":"after-candidate-comparison"},
 {"physicalPage":281,"sourceRowOnPage":9,"before":"Yuille,Ida Valesca","after":"Yuile,Ida Valesca","reason":"Candidate comparison prompted fresh individual actualPDF crop reread; reviewer had added an extra l in surname. Original visibly prints Yuile. Candidate surname already correct; candidate first initial is separately corrected from lowercase l to visible capital I. Frozen raw transcript unchanged.","phase":"after-candidate-comparison"}
]
for c in corrections:
 i=next(i for i,r in enumerate(batch["rows"]) if (r["physicalPage"],r["sourceRowOnPage"])==(c["physicalPage"],c["sourceRowOnPage"]));assert names[i]==c["before"];names[i]=c["after"]
money={(r["physicalPage"],r["sourceRowOnPage"],r["field"]):r["value"] for r in t["moneyTargetReadings"]};namecor=[];moneycor=[];resolutions=[]
for r,ir,fr,name in zip(batch["rows"],im["rows"],f["rows"],names):
 key=(r["physicalPage"],r["sourceRowOnPage"]);assert key==(ir["physicalPage"],ir["sourceRowOnPage"])==(fr["physicalPage"],fr["sourceRowOnPage"]);assert r["reviewTargetFields"]==ir["reviewTargetFields"]==fr["reviewTargetFields"];assert r["cropSha256"]==ir["cropSha256"]==fr["tileCropSha256"]==sha(r["cropPath"]);assert fr["cropSha256"]==sha(fr["cropPath"]);cand=r["candidateRow"];assert len(cand)==6 and cand[0]=="provincial-health-services-authority" and cand[5]==key[0];vals={}
 for field in r["reviewTargetFields"]:
  value=name if field=="name" else money[(*key,field)];vals[field]=value;old=cand[{"name":1,"remuneration":3,"expenses":4}[field]]
  if value!=old:
   entry={"physicalPage":key[0],"sourceRowOnPage":key[1],"before":old,"after":value}
   if field=="name":namecor.append(entry)
   else:moneycor.append({**entry,"field":field})
 resolutions.append({"physicalPage":key[0],"sourceRowOnPage":key[1],"reviewTargetFields":r["reviewTargetFields"],"resolvedValues":vals,"literalImageName":name,"status":"resolved-from-original-image","cropSha256":r["cropSha256"],"paintedCropSha256":fr["cropSha256"],"paintedCropPath":fr["cropPath"]})
for sheet in im["contactSheets"]+f["contactSheets"]:assert sha(sheet["path"])==sheet["sha256"]
receipt={"reviewedOn":"2026-11-01","reviewer":"recovery_municipal (NIC reviewer)","sourceSha256":batch["sourceSha256"],"frozenBatchSha256":sha(full),"imageManifestSha256":sha(images),"rawTranscriptSha256":sha(raw),"paintedSourceFidelitySha256":sha(fidelity),"reviewedRows":457,"resolvedRows":457,"unresolvedRows":0,"targetFieldCounts":dict(collections.Counter(field for r in batch["rows"] for field in r["reviewTargetFields"])),"reviewScope":"Every requested field in all457 batch010 rows; all457 names additionally transcribed as context. All457 actual officialPDF row crops independently rendered at300dpi and manually read before fullcandidate comparison. Requested-field review only; does not approve all284pages or complete employee source.","sourceFidelityNote":"Actual PDF page rendering respects PDF clipping/masks.182painted crops pixel-identical to provided native crops;275differ at RGBpixel level, which does not establish a semantic field difference. All resolutions use actual PDF-painted source. No common-name inference, name enrichment, or compensation balancing.","contactSheetSha256":[s["sha256"] for s in im["contactSheets"]],"paintedContactSheetSha256":[s["sha256"] for s in f["contactSheets"]],"reviewerOnlyCorrections":corrections,"candidateNameCorrections":namecor,"candidateMoneyCorrections":moneycor,"resolutions":resolutions,"acceptedEmployeeRows":0}
out=REV/f"{P}-resolutions.json";assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps({"receipt":str(out),"sha256":sha(out),"rows":len(resolutions),"nameCorrections":len(namecor),"moneyCorrections":len(moneycor),"reviewerOnlyCorrections":len(corrections),"targetFieldCounts":receipt["targetFieldCounts"]}))

