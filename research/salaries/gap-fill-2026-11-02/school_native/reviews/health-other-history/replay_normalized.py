from pathlib import Path
from decimal import Decimal
import json,gzip,hashlib,re
R=Path('/workspace/PofBC');A=Path(__file__).resolve().parent;H=R/'research/salaries/gap-fill-2026-11-02/health_other_history';C=R/'research/salaries/gap-fill-health-other-history';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin=lambda p:{'file':str(p.relative_to(R)),'sha256':sha(p)}
M=C/'sources-candidate.json';assert sha(M)=='ab974e2780ef9fc3706b0d2d64b8fafd188644ca556a6763a4cf22ce4e8e8a22'
rawindex={s['key']:s for s in json.loads((H/'native-primary-candidate-index.json').read_text())};sources=json.loads(M.read_text())['sources'];personal={r['id']:r for r in json.loads((A/'independent-final247-source-transcript.json').read_text())['rows']};seen=set();observations=[];sourcepins=[]
name=lambda s:re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip())if s is not None else None
value=lambda v:None if v is None else Decimal(str(v))
def equal(a,b):
    return a[0]==b[0]and name(a[1])==name(b[1])and a[2]==b[2]and value(a[3])==value(b[3])and value(a[4])==value(b[4])and a[5]==b[5]
for source in sources:
    key=source['id'].removeprefix('gap-health-other-history-');raw=rawindex[key];p=C/source['file'];e=C/source['provenanceFile'];assert sha(p)==source['dataSha256'];assert sha(e)==source['provenanceSha256'];assert sha(R/raw['file'])==raw['sha256'];data=json.loads(gzip.decompress(p.read_bytes()));proof=json.loads(gzip.decompress(e.read_bytes()));primary=json.loads(gzip.decompress((R/raw['file']).read_bytes()))['rows'];assert len(data)==len(proof['rows'])==source['rowCount'];assert source['sha256']==raw['sourceSha256']==proof['sourceSha256']
    expected=[r['row']for r in primary];added=[]
    for row,detail in zip(data,proof['rows']):
        assert detail['rowIndex']>=1 and data[detail['rowIndex']-1]==row
        assert detail['physicalPage']==row[5]
        for target in detail['sourceImageTargetIds']:
            assert target in personal and target not in seen;seen.add(target);r=personal[target]
            assert key==r['sourceKey']and row[5]==r['physicalPage']
            assert name(row[1])==name(r['literalName'])and value(row[3])==value(r['remuneration'])and value(row[4])==value(r['expenses'])
            if r['sourceRowOnPage']is not None:assert detail['initialPrimarySourceRowOnPage']==r['sourceRowOnPage']
            else:
                assert row==['island-health','WILSON. TOM',None,77451,0,47]
                assert detail['initialPrimarySourceRowOnPage']is None
                expected.insert(detail['rowIndex']-1,row)
                added.append({'target':target,'rowIndex':detail['rowIndex'],'literalSourceRow':row,'provenance':detail})
            observations.append({'id':target,'sourceId':source['id'],'normalizedRowIndex':detail['rowIndex'],'exactFieldsMatch':True})
    assert len(expected)==len(data)and all(equal(a,b)for a,b in zip(expected,data)),key
    sourcepins.append({'sourceId':source['id'],'sourceSha256':source['sha256'],'sourceUrl':source['sourceUrl'],'rowCount':len(data),'data':pin(p),'provenance':pin(e),'rawCandidate':pin(R/raw['file']),'rawCandidateRowsPreserved':len(primary),'explicitSourceImageAdditions':added})
assert len(sources)==9 and sum(s['rowCount']for s in sources)==11471
assert len(seen)==len(observations)==247
result={'status':'normalized-candidate-data-replay-passed-for-allnine-sources-and247-personal-targets','sourceReview':pin(A/'independent247-source-exception-review.json'),'manifestSnapshot':pin(M),'independentFinalTranscript':pin(A/'independent-final247-source-transcript.json'),'counts':{'normalizedSources':9,'normalizedObservations':11471,'rawNativeObservationsPreserved':11470,'explicitImageBackedOmittedObservationAdded':1,'personalSourceTargetsReplayedToNormalizedData':247,'unexpectedRawNativeValueChanges':0},'sources':sourcepins,'personalTargetReplay':observations,'scopeQualification':'All11471 normalized records are checked against the immutable native rows plus one explicit image-backed source addition. Only247 records were personally image-transcribed here. Root separately owns complete source context, census and derivation review; no claim of second personal transcription of every record. Exact candidate manifest/provenance pins may need an explicit metadata-adoption overlay at promotion; data bytes are independently pinned.','preservedSourceQualification':'Northern2014/15 has1254 actual rows against printed1255 summary; source census and residual qualification remain root-owned. No missing employee or payment inferred.','noOutreach':True};p=A/'final-normalized247-source-review-overlay.json';assert not p.exists();p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(sha(p));print(result['counts'])
