#!/usr/bin/env python3
"""Build source-faithful southern school cohorts from closed review inputs."""
import argparse,collections,gzip,hashlib,json
from decimal import Decimal
from pathlib import Path
from gap_school_south_fetch import AREA,ROOT

COLLECTION=ROOT/'research/salaries/gap-fill-school-south'
PEER='research/salaries/gap-fill-2026-11-02/school_native/peer-south-native-final-review.json'
PEER_SHA='55c45627a784e266b23c3baa23c26ceb8f2b2caea29617ac3de5735e5f07809a'
NATIVE={39:('vancouver-school-district','School District No. 39 (Vancouver)'),45:('west-vancouver-school-district','School District No. 45 (West Vancouver)'),75:('mission-school-district','School District No. 75 (Mission)')}
INDEX={39:'https://www.vsb.bc.ca/financial-information',45:'https://westvancouverschools.ca/about-wvs/financial-information/',75:'https://www.mpsd.ca/budgets-financials-reports'}

def sha(b):return hashlib.sha256(b).hexdigest()
def packed(v):
    raw=(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode();return gzip.compress(raw,mtime=0),raw
def number(v):
    d=Decimal(str(v));return int(d) if d==int(d) else float(d)
def write(path,b,check):
    if check:
        if path.read_bytes()!=b:raise ValueError('Reviewed output differs: '+str(path))
    else:path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(b)

def native_sources(check=False):
    peer_raw=(ROOT/PEER).read_bytes();assert sha(peer_raw)==PEER_SHA
    peer=json.loads(peer_raw);assert peer['accepted'] is True
    sources=[]
    for district,(employer_slug,employer_name) in NATIVE.items():
        review=next(x for x in peer['sources'] if x['district']==district)
        candidate_ref=review['candidate'];b=(ROOT/candidate_ref['path']).read_bytes();assert sha(b)==candidate_ref['sha256'];proof=json.loads(gzip.decompress(b));assert not proof['differences']
        assert proof['source']['sha256']==review['sourceSha256']
        assert [[r[k] for k in proof['fields']] for r in proof['popplerRows']]==[[r[k] for k in proof['fields']] for r in proof['mupdfRows']]
        for scope in ['employee-remuneration','school-trustees']:
            rows=[r for r in proof['mupdfRows'] if r['category']==scope];detail=review['scopes'][scope]
            assert len(rows)==detail['rows']
            summed=[str(sum(Decimal(r['remuneration']) for r in rows)),str(sum(Decimal(r['expenses'] or '0') for r in rows))]
            assert list(map(Decimal,summed))==list(map(Decimal,detail['computed']))
            role='employees' if scope=='employee-remuneration' else 'trustees';key=f'sd{district}-2025-{role}'
            payload=[[employer_slug,r['name'],r['position'],number(r['remuneration']),None if r['expenses'] is None else number(r['expenses']),r['pdfPage']] for r in rows]
            blob,raw=packed(payload);file=key+'.json.gzip';write(COLLECTION/file,blob,check)
            evidence={'sourceSha256':review['sourceSha256'],'candidate':candidate_ref,'independentSourceReview':{'path':PEER,'sha256':PEER_SHA},'sourceFields':[{k:v for k,v in r.items() if k not in ('sourceWordBoxes','popplerWordBoxes')} for r in rows],'completeReaderFieldAgreement':True,'literalComputedTotals':summed,'literalPrintedTotals':detail['literalPrintedControls'],'residuals':detail['residuals'],'causeEstablished':False if any(Decimal(x)!=0 for x in detail['residuals']) else None,'dataSha256':sha(blob),'normalizedSha256':sha(raw),'noOutreach':True}
            eblob,_=packed(evidence);efile=key+'-evidence.json.gzip';write(COLLECTION/efile,eblob,check)
            warning='Fiscal-year payment disclosures are not annual base salary rates or a complete workforce census. Source expense dashes remain unknown (null); explicit zero and negative amounts remain literal. '
            if district==39:
                warning+='The source surname and given-name columns are joined with a comma and space, without expanding or resolving identities. Student trustee observations are retained in the separate trustee category. '
            if district==45:
                warning+='Literal employee rows total $44,364,345 remuneration versus the printed $44,364,330 (+$15); known expenses reconcile at $258,403. Trustee rows total $133,244/$1,797 versus printed $133,243/$1,798 (+$1/−$1). Causes are not established and no amount is adjusted. Two starred employee expense cells include travel for international student recruitment. '
            if district==75 and scope=='school-trustees':warning+='Trustee position cells are not published in the named table and remain null. '
            warning+='Existing compiled observations, where present, remain retained; equivalence between compiled edition labels and this fiscal reporting year has not been proved.'
            source={'id':'gap-fill-school-south-'+key,'employerSlug':employer_slug,'employerName':employer_name,'sector':'School districts','year':'2024/25','slug':'2024-25','periodType':'fiscal','periodStart':'2024-07-01','periodEnd':'2025-06-30','title':employer_name+', fiscal year ended June 30, 2025: '+role,'sourceUrl':proof['source']['sourceUrl'],'sourceIndexUrl':INDEX[district],'sha256':review['sourceSha256'],'file':file,'dataSha256':sha(blob),'normalizedSha256':sha(raw),'provenanceFile':efile,'provenanceSha256':sha(eblob),'category':scope,'scope':scope,'scopeDescription':'Complete published named '+('employee schedule above the stated disclosure threshold' if role=='employees' else 'trustee/elected-official schedule'),'currency':'CAD','amountUnit':'dollars','amountPrecision':'cents' if district==75 else 'whole-dollars','threshold':75000 if role=='employees' else None,'thresholdComparison':'>' if role=='employees' else None,'nameDisclosure':'separate-surname-and-given-name-cells-joined-with-comma' if district==39 else 'published-name-as-disclosed','positionDisclosure':'not-published' if district==75 and role=='trustees' else 'published-visible-text-only','pages':sorted({r['pdfPage'] for r in rows}),'rowCount':len(rows),'totalRemuneration':number(summed[0]),'totalExpenses':number(summed[1]),'status':'verified','sourceKind':'official','completeEmployeeSchedule':role=='employees','verifiedOn':'2026-11-02','publicWarning':warning,'notes':['Only literal named observations are imported. Below-threshold totals, employer CPP/EI, vendors and financial statements remain supporting evidence.','No amount was changed to balance a printed subtotal. Independent native extraction and finite source-image checks do not establish perfect transcription accuracy.'],'validation':{'originalFingerprintVerified':True,'independentReaders':proof['readers'],'rowsIndependentlyChecked':len(rows),'allFieldsOrderAndMultiplicityAgree':True,'rowsByPhysicalPage':dict(collections.Counter(r['pdfPage'] for r in rows)),'printedControlTotals':detail['literalPrintedControls'],'computedComponentTotals':summed,'controlResiduals':detail['residuals'],'summaryReconciles':all(Decimal(x)==0 for x in detail['residuals']),'knownExpenseValueCount':sum(r['expenses'] is not None for r in rows),'nullExpenseRows':sum(r['expenses'] is None for r in rows),'zeroExpenseRows':sum(r['expenses'] is not None and Decimal(r['expenses'])==0 for r in rows),'negativeExpenseRows':sum(r['expenses'] is not None and Decimal(r['expenses'])<0 for r in rows),'completeEmployeeSchedule':role=='employees','compiledPartitionRetained':True,'compiledPartitionRetentionReason':'Complete source-versus-compiled equivalence is not proved; no person identity or reporting-period match is inferred.','independentPeerReview':{'path':PEER,'sha256':PEER_SHA},'candidate':candidate_ref,'actualOriginalRasterVisibilityProof':{'path':str((AREA/f'sd{district}-native-original-raster-visibility-v2.json.gzip').relative_to(ROOT)),'sha256':sha((AREA/f'sd{district}-native-original-raster-visibility-v2.json.gzip').read_bytes())},'actualRasterVisibilityIsGlyphRecognition':False}}
            sources.append(source)
    return sources

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    sources=native_sources(args.check)
    manifest={'version':1,'reviewed':True,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources}
    write(COLLECTION/'sources-native-reviewed.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(),args.check)
    # The final combined manifest is assembled only after all assigned scans and
    # the crowded Delta cells close. Root may inspect this reviewed native subset.
    print(json.dumps({'reviewedNativeScopes':len(sources),'nativeRows':sum(x['rowCount'] for x in sources)}))

if __name__=='__main__':main()
