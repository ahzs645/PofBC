#!/usr/bin/env python3
"""Build seven source-qualified school reports without changing earlier sources."""
import argparse
from collections import Counter
import copy
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native'
COLLECTION=ROOT/'research/salaries/gap-fill-school-native'
FIELDS=['name','position','remuneration','expenses','pdfPage','category']


def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def load(path):return json.loads(gzip.decompress(path.read_bytes()))
def packed(value):return gzip.compress((json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
def reference(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def equal(a,b):
    import re
    return [re.sub(r'\s+','',x) if isinstance(x,str) else x for x in a]==[re.sub(r'\s+','',x) if isinstance(x,str) else x for x in b]


def write(path,raw,check):
    if check:assert path.read_bytes()==raw,('Deterministic replay differs',str(path))
    else:path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(raw)


def native(c,peer):
    path=AREA/c.get('candidateFile',c['key']+'-native-candidate.json.gzip');raw=path.read_bytes();p=load(path)
    assert p['source']==c,'Current native spec differs from the reviewed source candidate'
    reviewed=next(s for s in peer['sources'] if s['key']==c['key'])
    assert reviewed['sourceSha256']==c['sourceSha256'] and reviewed['candidateSha256']==sha(raw)
    first=copy.deepcopy(p['popplerRows']);second=copy.deepcopy(p['mupdfRows']);amendments=[]
    for adoption in peer['titleAdoptions']:
        if adoption['sourceId']!=c['key']:continue
        assert sha((ROOT/adoption['sourceImageFile']).read_bytes())==adoption['sourceImageSha256']
        for engine,rows in [('poppler',first),('mupdf',second)]:
            row=rows[adoption['sequence']-1]
            assert (row['name'],row['pdfPage'],row['remuneration'],row['expenses'])==(adoption['name'],adoption['physicalPage'],adoption['literalRemuneration'],adoption['literalExpenses'])
            value=adoption['acceptedVisiblePositionPrefix']
            if row['position']!=value:
                amendments.append({'reader':engine,'sequence':adoption['sequence'],'field':'position','before':row['position'],'after':value,'sourceImage':adoption})
                row['position']=value
    assert [[r[f] for f in FIELDS] for r in first]==[[r[f] for f in FIELDS] for r in second]
    return first,{'method':'independent painted-native readers plus exact source-image title adoptions','originalProof':reference(path),'firstReaderRows':first,'secondReaderRows':second,'sourceImageAmendments':amendments,'independentPeerReview':reference(ROOT/'research/salaries/gap-fill-2026-11-02/reviews/root-five-native-school-source-review.json'),'personalReviewScope':peer['scope']},reviewed['controls']


def scanned(n,peer):
    p=AREA/f'sd{n}-2025-scan-parsed-v1.json.gzip';raw=load(p)
    first=copy.deepcopy(raw['tesseractRows']);second=copy.deepcopy(raw['paddleRows']);readings={};refs=[]
    for filename in ['scan-primary-image-readings.json','scan-primary-confidence-readings.json','scan-primary-holdout-readings-v2.json']:
        f=AREA/filename;refs.append(reference(f))
        for entry in read(f)['rows']:
            if entry['districtNumber']!=n:continue
            assert sha((ROOT/entry['file']).read_bytes())==entry['sha256']
            if entry['sequence'] in readings:assert readings[entry['sequence']]['fields']==entry['fields']
            readings[entry['sequence']]=entry
    amendments=[]
    for seq,entry in sorted(readings.items()):
        assert entry['fields'][4]==first[seq-1]['pdfPage']
        for reader,rows in [('tesseract',first),('paddle',second)]:
            row=rows[seq-1]
            for f,value in zip(FIELDS,entry['fields']):
                before=row[f]
                # Preserve unamended second-reader spacing. Actual primary
                # source spacing changes remain explicit in first-reader proof.
                differs=(before!=value) if reader=='tesseract' else not equal([before],[value])
                if differs:
                    amendments.append({'reader':reader,'sequence':seq,'field':f,'before':before,'after':value,'sourceImage':{k:entry[k] for k in ['file','sha256','physicalPage']}})
                    row[f]=value
    assert len(first)==len(second)
    for a,b in zip(first,second):
        assert equal([a[f] for f in FIELDS],[b[f] for f in FIELDS])
        assert not any(isinstance(a[f],str) and a[f].startswith('UNRESOLVED:') for f in FIELDS)
    controls=read(AREA/'scan-peer-packet.json')['sources']
    control=next(c for c in controls if c['key']==f'sd{n}-2025')
    return first,{'method':'Tesseract TSV versus independently grouped Paddle boxes; whitespace-only corroboration, actual image amendments retained','originalProof':reference(p),'firstReaderRows':first,'secondReaderRows':second,'sourceImageAmendments':amendments,'primarySourceReadings':refs,'independentPeerReview':peer,'manualSourceRows':len(readings),'personalReviewScope':'All46initialflagrows, all66confidence-only agreeing rows,20deterministic holdout rows with overlap; not a personal transcript of every scanned observation. Source confidence scores are model values, not accuracy probabilities.'},[{'scope':scope,'literalPrintedControls':v} for scope,v in control['printedControls'].items()]


def main(check=False):
    registry=read(AREA/'peer-selection.json')
    rootref=registry['nativeRootReview'];peerpath=ROOT/rootref['path']
    assert rootref['path']=='research/salaries/gap-fill-2026-11-02/reviews/root-five-native-school-source-review.json'
    assert sha(peerpath.read_bytes())==rootref['sha256'],'Explicit native-root review fingerprint changed'
    peer=read(peerpath)
    assert peer['accepted'] is True and peer['acceptedSubjectToExactTitleAdoptions'] is True
    sources=[];specs=read(AREA/'native-specs.json');baseline=read(ROOT/'research/salaries/queue-completion-2026-11-01/schools/registered-gap-inventory.json')
    for n in [34,40,41,53,57,62,84]:
        emp=next(e for e in baseline['employers'] if e['districtNumber']==n)
        key=f'sd{n}-2025';scan=n in [53,84]
        if scan:
            http=read(AREA/(key+'-district-http.json'))
            c={'key':key,'districtNumber':n,'employerSlug':emp['employerSlug'],'employerName':emp['employerName'],'sourceUrl':http['url'],'sourceSha256':http['sha256']}
            peerref=registry.get(key)
            scan_peer=None
            if peerref:
                p=ROOT/peerref['path'];assert sha(p.read_bytes())==peerref['sha256'];scan_peer=read(p)
                assert scan_peer['accepted'] is True and scan_peer['unresolved']==[]
                assert scan_peer['reviewer']!='/root/gap_school_native'
                assert scan_peer['sourcePeriodAndScopePersonallyImageChecked'] is True
                assert scan_peer['sourceSha256'][key]==c['sourceSha256']
                for expected in scan_peer['inputReviewReferences']:
                    assert sha((ROOT/expected['path']).read_bytes())==expected['sha256']
            rows,evidence,controls=scanned(n,peerref)
        else:
            c=next(c for c in specs if c['districtNumber']==n);rows,evidence,controls=native(c,peer);peerref=reference(peerpath)
        for scope in ['school-trustees','employee-remuneration']:
            chosen=[r for r in rows if r['category']==scope];tag='trustees' if scope=='school-trustees' else 'employees';name=key+'-'+tag
            precision='whole-dollars' if n==62 or (n==84 and scope=='school-trustees') else 'cents'
            number=(lambda s:int(Decimal(s))) if precision=='whole-dollars' else (lambda s:float(Decimal(s)))
            if precision=='whole-dollars':assert all(Decimal(r[f])==int(Decimal(r[f])) for r in chosen for f in ['remuneration','expenses'] if r[f] is not None)
            normalized=[[c['employerSlug'],r['name'],r['position'],number(r['remuneration']),None if r['expenses'] is None else number(r['expenses']),r['pdfPage']] for r in chosen]
            blob=packed(normalized);data=COLLECTION/(name+'.json.gzip');write(data,blob,check)
            if scan and peerref:
                accepted=next(x for x in scan_peer['acceptedSources'] if x['sourceId']=='gap-fill-school-native-'+name)
                assert accepted['accepted'] is True and accepted['sourceSha256']==c['sourceSha256']
                assert accepted['dataSha256']==sha(blob) and accepted['rows']==len(chosen),'Accepted scan payload differs from the peer-reviewed literal source rows'
            sums=[str(sum((Decimal(r[f]) for r in chosen if r[f] is not None),Decimal())) for f in ['remuneration','expenses']]
            printed=next(v for v in controls if v['scope']==scope)['literalPrintedControls'];residual=[str(Decimal(a)-Decimal(b)) for a,b in zip(sums,printed)]
            source_evidence={**evidence,'scope':scope,'sourceSha256':c['sourceSha256'],'dataSha256':sha(blob),'literalPrintedControls':printed,'computedTotals':sums,'residuals':residual,'acceptedRows':len(chosen) if peerref else 0}
            eb=packed(source_evidence);ep=COLLECTION/(name+'-evidence.json.gzip');write(ep,eb,check)
            warning=[]
            if any(Decimal(x)!=0 for x in residual):warning.append(f"The complete literal named rows total ${Decimal(sums[0]):,.2f} remuneration and ${Decimal(sums[1]):,.2f} known expenses; the report prints ${Decimal(printed[0]):,.2f}/${Decimal(printed[1]):,.2f}. Residuals are {residual[0]}/{residual[1]} dollars. No value was changed to balance these controls and no cause is assumed.")
            if n==34 and scope=='employee-remuneration':warning.append('Ten published positions are visibly clipped. Only the independently reviewed complete visible prefixes are retained; hidden trailing text and partly clipped terminal glyphs are not expanded. Raw native alternatives and exact affected rows remain in provenance.')
            if n==53 and scope=='employee-remuneration':warning.append('Scanned source: two independent OCR readers, source-image review of every disagreement and low-confidence agreeing row, and finite source holdouts support this transcription; perfect OCR accuracy is not claimed. Source titles and initials remain literal, including clipped text. Exact source-image spacing is retained for separately reviewed name-initial joins.')
            if n==84:warning.append('Scanned source: independent OCR and bounded actual-source image review support this transcription; perfect OCR accuracy is not claimed. Employee expense dashes or blanks remain unknown, not zero. The employee rows print cents while their subtotals print whole dollars; trustee rows print whole dollars.')
            warning.append('Compiled entries, where present, are retained while their edition labels and employee/trustee scopes await a complete-copy comparison. No equivalence between a compiled edition and this fiscal reporting period is assumed.')
            source={'id':'gap-fill-school-native-'+name,'employerSlug':c['employerSlug'],'employerName':c['employerName'],'sector':'School districts','year':'2024/25','slug':'2024-25','periodType':'fiscal','periodStart':'2024-07-01','periodEnd':'2025-06-30','title':c['employerName']+', year ended June30,2025: '+tag,'sourceUrl':c['sourceUrl'],'sourceIndexUrl':next(x['sourceIndexUrl'] for x in read(AREA/'assigned-leads.json') if f'No. {n} ' in x['employer']),
                    'sha256':c['sourceSha256'],'file':data.name,'dataSha256':sha(blob),'normalizedSha256':sha(gzip.decompress(blob)),'provenanceFile':ep.name,'provenanceSha256':sha(eb),'category':scope,'scope':scope,'currency':'CAD','amountUnit':'dollars','amountPrecision':precision,'scopeDescription':'Complete published '+('school trustee remuneration table' if tag=='trustees' else 'named employee table above the source$75,000 threshold'),'nameDisclosure':'published-name-as-disclosed','positionDisclosure':'published-visible-source-text-only','pages':sorted({r['pdfPage'] for r in chosen}),'rowCount':len(chosen),'totalRemuneration':number(sums[0]),'totalExpenses':number(sums[1]),'status':'verified' if peerref else 'candidate-independent-peer-review-pending','sourceKind':'official','completeEmployeeSchedule':scope=='employee-remuneration','verifiedOn':'2026-11-02' if peerref else None,'retainCompiledPartition':True,'publicWarning':' '.join(warning),
                    'notes':['Official fiscal-year payment disclosure, not an annualized salary rate or complete workforce roster.','Literal names, source-visible positions, repeated observations, zeroes, nulls and source row order are retained. No identity, spelling or reporting-year match is inferred from compiled entries.','Only named observations are imported; below-threshold aggregates, employer contributions, suppliers and total financial statements are excluded.','The original printed remuneration schedule endsJune30,2025; later source upload dates do not establish a different remuneration period.'],
                    'validation':{'originalFingerprintVerified':True,'independentReaders':['Tesseract5.5 TSV','Paddle PP-OCR ONNX via RapidOCR1.4.4'] if scan else ['Poppler independent physical layout lines','MuPDF independent painted word geometry'],'rowsIndependentlyChecked':len(chosen),'allSixFieldsOrderMultiplicityAgree':True,'comparisonOnlyWhitespaceNormalization':scan,'rowsByPhysicalPage':dict(Counter(r['pdfPage'] for r in chosen)),'printedControlTotals':printed,'computedComponentTotals':sums,'controlResiduals':residual,'summaryReconciles':all(Decimal(x)==0 for x in residual),'nullExpenseRows':sum(r['expenses'] is None for r in chosen),'zeroExpenseRows':sum(r['expenses'] is not None and Decimal(r['expenses'])==0 for r in chosen),'completeEmployeeSchedule':scope=='employee-remuneration','compiledPartitionRetained':True,'compiledPartitionRetentionReason':'No complete official-versus-compiled source/data/baseline multiset comparison has been independently adopted; all compiled observations remain retained without an identity or period assumption.','reportingPeriodBasis':'Actual fiscal-year cover and complete remuneration schedule printed as year endedJune30,2025, checked from the original source.','salarySchedulePrintedPeriodEnd':'2025-06-30','approvalEvidence':{'status':'Official published source; no signature authentication or separate board-adoption assertion','noAdoptionClaim':True},'independentPeerReviewPending':peerref is None,'independentPeerReview':peerref}}
            sources.append(source)
    manifest={'version':1,'reviewed':all(s['status']=='verified' for s in sources),'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources}
    write(COLLECTION/'sources.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(),check)
    print(json.dumps({'cohorts':len(sources),'rows':sum(s['rowCount'] for s in sources),'reviewed':manifest['reviewed']}))
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();main(args.check)
