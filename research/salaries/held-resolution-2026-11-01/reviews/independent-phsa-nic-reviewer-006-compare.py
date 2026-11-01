#!/usr/bin/env python3
"""Freeze batch 006 requested-field resolutions after image-first transcript."""
import json,hashlib,collections
from pathlib import Path
BASE=Path("research/salaries/held-resolution-2026-11-01")
REV=BASE/"reviews";P="independent-phsa-nic-reviewer-006"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=REV/f"{P}-image-transcript.json";full=BASE/"health/review-batch-006.json";images=BASE/"health/review-batch-006-images.json";fidelity=REV/f"{P}-painted-source-fidelity.json"
assert sha(raw)=="b0d30ff537483eb0bc4486377eaa7165461e4931ff36ceabd172375eafa64c82"
assert sha(full)=="312f420c24910c70036022dc446f7c0de3d8a6954052b5ef47596fdfa852f55a"
assert sha(images)=="0a780d8db722b113b9a48718a1533fe6f3fed821031d5b8e8330f24c55dcae47"
assert sha(fidelity)=="93ee4d75525378e0283317882a782020954924fd4d74a97a65f70e7e2083a968"
t=json.loads(raw.read_text());batch=json.loads(full.read_text());im=json.loads(images.read_text());f=json.loads(fidelity.read_text())
assert len(batch["rows"])==len(t["namesInFrozenBatchOrder"])==len(f["rows"])==300
assert t["paintedSheetsRead"]==list(range(1,31))
names=list(t["namesInFrozenBatchOrder"])
post=[
 {"physicalPage":140,"sourceRowOnPage":1,"before":"Langill,Tae-Eun Sheena","after":"Langill,Tae-Eun","reason":"Reviewer transcript added an unprinted name. Candidate comparison prompted a fresh unchanged actual-PDF individual-crop read: original prints only Tae-Eun. Candidate was already correct; raw transcript preserved unchanged.","phase":"after-candidate-comparison"},
 {"physicalPage":146,"sourceRowOnPage":49,"before":"Leong,Moobun","after":"Leong,Moboun","reason":"Reviewer transposed letters in the context-only name. Candidate comparison prompted a fresh unchanged actual-PDF individual-crop read, which says Moboun. Name is not a requested target on this row; candidate was already correct. Raw transcript preserved unchanged.","phase":"after-candidate-comparison"}
]
for c in post:
    index=next(i for i,r in enumerate(batch["rows"]) if (r["physicalPage"],r["sourceRowOnPage"])==(c["physicalPage"],c["sourceRowOnPage"]))
    assert names[index]==c["before"];names[index]=c["after"]
money={(r["physicalPage"],r["sourceRowOnPage"],r["field"]):r["value"] for r in t["moneyTargetReadings"]}
namecor=[];moneycor=[];resolutions=[]
for index,(r,ir,fr,name) in enumerate(zip(batch["rows"],im["rows"],f["rows"],names)):
    key=(r["physicalPage"],r["sourceRowOnPage"])
    assert key==(ir["physicalPage"],ir["sourceRowOnPage"])==(fr["physicalPage"],fr["sourceRowOnPage"])
    assert r["reviewTargetFields"]==ir["reviewTargetFields"]==fr["reviewTargetFields"]
    assert r["cropSha256"]==ir["cropSha256"]==fr["tileCropSha256"]==sha(r["cropPath"])
    assert fr["cropSha256"]==sha(fr["cropPath"])
    cand=r["candidateRow"];assert len(cand)==6 and cand[0]=="provincial-health-services-authority" and cand[5]==r["physicalPage"]
    vals={}
    for field in r["reviewTargetFields"]:
        value=name if field=="name" else money[(*key,field)]
        vals[field]=value
        old=cand[{"name":1,"remuneration":3,"expenses":4}[field]]
        if value!=old:
            entry={"physicalPage":key[0],"sourceRowOnPage":key[1],"before":old,"after":value}
            if field=="name":namecor.append(entry)
            else:moneycor.append({**entry,"field":field})
    resolutions.append({"physicalPage":key[0],"sourceRowOnPage":key[1],"reviewTargetFields":r["reviewTargetFields"],"resolvedValues":vals,"literalImageName":name,"status":"resolved-from-original-image","cropSha256":r["cropSha256"],"paintedCropSha256":fr["cropSha256"],"paintedCropPath":fr["cropPath"]})
for sheet in im["contactSheets"]+f["contactSheets"]:assert sha(sheet["path"])==sheet["sha256"]
prior=[{**c,"phase":"before-candidate-comparison; original unvalidated first-pass transcript to actual-PDF transcript"} for c in t["reviewerOnlyCorrectionsBeforeCandidate"]]
receipt={"reviewedOn":"2026-11-01","reviewer":"recovery_municipal (NIC reviewer)","sourceSha256":batch["sourceSha256"],"frozenBatchSha256":sha(full),"imageManifestSha256":sha(images),"rawTranscriptSha256":sha(raw),"firstPassUnvalidatedTranscriptSha256":t["firstPassUnvalidatedTranscriptSha256"],"paintedSourceFidelitySha256":sha(fidelity),"reviewedRows":300,"resolvedRows":300,"unresolvedRows":0,"targetFieldCounts":dict(collections.Counter(field for r in batch["rows"] for field in r["reviewTargetFields"])),"reviewScope":"Every requested field in all300 batch006 original row crops, plus all300names as context. All300 separately rerendered from actual PDF at300dpi and manually reread before candidate comparison. Requested-field comparison only; no all284page source approval or complete-source acceptance.","sourceFidelityNote":"Temporary tile-fidelity alert was retracted by reporter and root.117actual crop images pixel-identical to supplied tile crops;183differ at RGBpixel level. Manual reading of all300 actual crops found no semantic field discrepancy attributable to tile stitching. Four own reading/transcription errors are separately recorded, not treated as source-rendering defects.","contactSheetSha256":[s["sha256"] for s in im["contactSheets"]],"paintedContactSheetSha256":[s["sha256"] for s in f["contactSheets"]],"reviewerOnlyCorrections":prior+post,"candidateNameCorrections":namecor,"candidateMoneyCorrections":moneycor,"resolutions":resolutions,"acceptedEmployeeRows":0}
out=REV/f"{P}-resolutions.json";assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({"receipt":str(out),"sha256":sha(out),"rows":len(resolutions),"nameCorrections":len(namecor),"moneyCorrections":len(moneycor),"reviewerOnlyCorrections":len(prior+post),"targetFieldCounts":receipt["targetFieldCounts"]}))

