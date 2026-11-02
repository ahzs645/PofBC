#!/usr/bin/env python3
"""Independent source-row, pixel-view and first-image review of three south reports."""
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/school_native'
PACKET=ROOT/'research/salaries/gap-fill-2026-11-02/school_south/native-peer-packet.json'
FIELDS=['name','position','department','remuneration','expenses','pdfPage','category']


def sha(raw):return hashlib.sha256(raw).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}


def raw_payment_rows(doc,spec,n,candidate):
    """Do not use either native reader's name or monetary acceptance predicate."""
    results=[];unclassified=[]
    for number in spec['pages']:
        groups=[]
        for word in sorted(doc[number-1].get_text('words'),key=lambda w:((w[1]+w[3])/2,w[0])):
            y=(word[1]+word[3])/2
            near=[g for g in groups if abs(g['y']-y)<spec.get('rowTolerance',1.6)]
            if near:g=min(near,key=lambda g:abs(g['y']-y))
            else:g={'y':y,'words':[]};groups.append(g)
            g['words'].append(word)
        for g in groups:
            cells=[[] for _ in range(len(spec['bounds'])+1)]
            for w in sorted(g['words'],key=lambda w:w[0]):
                if w[4]=='$':continue
                cells[sum(w[0]>=b for b in spec['bounds'])].append(w[4])
            c=[' '.join(x).strip() for x in cells]
            pay_index=3 if spec['kind']=='separate-names' else 2
            if not c[0] or not re.search(r'\d',c[pay_index]):continue
            item={'physicalPage':number,'sourceY':g['y'],'cells':c}
            if c[0]=='Total' or re.match(r'^(?:Total (?:for |Employees|Detailed Employees|Elected|Employer|remuneration)|Consolidated|Prepared as)',c[0],re.I):
                item.update(disposition='excluded-printed-non-person-control',reason='Actual source aggregate/header, retained literally in this audit')
            else:
                matches=[(i+1,r) for i,r in enumerate(candidate['mupdfRows']) if r['pdfPage']==number and abs(r['sourceY']-g['y'])<spec.get('rowTolerance',1.6)]
                if len(matches)!=1:item['disposition']='unclassified-payment-row';unclassified.append(item)
                else:item.update(disposition='included-named-observation',sequence=matches[0][0])
            results.append(item)
    included=[x for x in results if x['disposition']=='included-named-observation']
    assert len(included)==len(candidate['mupdfRows']),(n,len(included),len(candidate['mupdfRows']))
    assert len({x['sequence'] for x in included})==len(included)
    assert not unclassified,(n,unclassified)
    return results


def review():
    import fitz
    from PIL import Image
    worker_code=AREA/'peer-code/gap_school_south_native-v4.py';worker_code_sha=sha(worker_code.read_bytes())
    module_spec=importlib.util.spec_from_file_location('native_peer_south_frozen_v4',worker_code)
    frozen_parser=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(frozen_parser)
    poppler_geometry_reader=frozen_parser.poppler_geometry_reader;geometry_reader=frozen_parser.geometry_reader
    packet_bytes=PACKET.read_bytes();packet=json.loads(packet_bytes);firstpath=AREA/'peer-south-native-first-image-readings.json';readpath=AREA/'peer-south-native-source-readings-v2.json';reads=json.loads(readpath.read_bytes())
    assert len(reads['rows'])==52
    assert reads['supersedes']==ref(firstpath)
    receipts=[]
    for d in packet['districts']:
        n=d['number'];source=d['source'];path=Path(source['cachePath']);assert sha(path.read_bytes())==source['sha256']
        cp=ROOT/d['candidate']['path'];assert sha(cp.read_bytes())==d['candidate']['sha256'];candidate=json.loads(gzip.decompress(cp.read_bytes()))
        assert cp.name==f'sd{n}-native-candidate-v4.json.gzip'
        assert candidate['differences']==[]
        assert all(not p['nonPaintedOrWhiteTextTraces'] for p in candidate['nativeVisibility'])
        assert [[r.get(f) for f in FIELDS] for r in candidate['popplerRows']]==[[r.get(f) for f in FIELDS] for r in candidate['mupdfRows']]
        doc=fitz.open(path);image_checks=[];cache={}
        original_xml=subprocess.check_output(['pdftotext','-bbox-layout',str(path),'-'])
        stored_xml=ROOT/f'research/salaries/gap-fill-2026-11-02/school_south/sd{n}-issuer-poppler-bbox.xml.gzip'
        assert original_xml==gzip.decompress(stored_xml.read_bytes())
        replay_a=poppler_geometry_reader(original_xml,n);replay_b,_,_=geometry_reader(doc,n)
        for field in FIELDS:
            assert [r.get(field) for r in replay_a]==[r.get(field) for r in candidate['popplerRows']],(n,field,'fresh Poppler replay differs')
            assert [r.get(field) for r in replay_b]==[r.get(field) for r in candidate['mupdfRows']],(n,field,'fresh MuPDF replay differs')
        for target in d['boundedSourceImageTargets']:
            p=ROOT/target['image'];assert sha(p.read_bytes())==target['sha256'];expected=Image.open(p).convert('RGB');number=target['physicalPage']
            if number not in cache:
                pix=doc[number-1].get_pixmap(dpi=300);cache[number]=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            actual=cache[number].crop(target['integerCropBox300Dpi'])
            assert actual.size==expected.size and actual.tobytes()==expected.tobytes(),(n,number,'source crop pixels differ')
            observation=next(r for r in reads['rows'] if r['district']==n and r['sequence']==target['sequence'])
            row=candidate['popplerRows'][target['sequence']-1]
            for f in ['name','position','remuneration','expenses']:assert row[f]==observation[f],(n,target['sequence'],f,row[f],observation[f])
            assert row['pdfPage']==observation['physicalPage']
            if observation['expenseFootnote']:
                assert row.get('expenseFootnoteMarker')==observation['expenseFootnote']
            image_checks.append({**target,'actualOriginalPixelsReplayed':True,'firstImageReadCompared':True})
        for target in d['contextImages']:
            p=ROOT/target['image'];assert sha(p.read_bytes())==target['sha256'];expected=Image.open(p).convert('RGB');page=doc[target['physicalPage']-1]
            dpi=round(expected.width/page.rect.width*72);pix=page.get_pixmap(dpi=dpi);actual=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            assert actual.size==expected.size and actual.tobytes()==expected.tobytes(),(n,target['physicalPage'],'context pixels differ')
            image_checks.append({**target,'dpi':dpi,'actualOriginalPixelsReplayed':True})
        sums={}
        for scope in ['school-trustees','employee-remuneration']:
            rows=[r for r in candidate['popplerRows'] if r['category']==scope]
            computed=[str(sum((Decimal(r[f]) for r in rows if r[f] is not None),Decimal())) for f in ['remuneration','expenses']]
            printed=d['printedControls'][scope]
            assert computed==[d['computed'][scope]['remuneration'],d['computed'][scope]['knownExpenses']]
            sums[scope]={'rows':len(rows),'computed':computed,'literalPrintedControls':printed,'residuals':[str(Decimal(a)-Decimal(b)) for a,b in zip(computed,printed)],'noBalancingAdjustment':True}
        coverage=raw_payment_rows(doc,candidate['spec'],n,candidate)
        visibility=ROOT/d['nativeVisibilityReceipt'];v=json.loads(gzip.decompress(visibility.read_bytes()))
        assert v['mandatoryImageReviewFlags']==[]
        assert v['candidateSha256']==d['candidate']['sha256'] and v['sourceSha256']==source['sha256']
        receipts.append({'district':n,'sourceSha256':source['sha256'],'candidate':ref(cp),'scopes':sums,'sourceImageReplays':image_checks,'independentPaymentRowAudit':coverage,'nativeVisibilityReceipt':ref(visibility),'fullNativeRowsCorroborated':len(candidate['popplerRows']),'personalSourceRowsRead':len(d['boundedSourceImageTargets']),
                         'freshOriginalBothReaderReplay':True,'freshPopplerXmlSha256':sha(original_xml),'nativeParserCode':{'path':str(worker_code.relative_to(ROOT)),'sha256':worker_code_sha},
                         'sourcePeriod':'2024/25; actual declaration and remuneration heading endJune30,2025','declarationNotationsObserved':{39:'Original Signed By notations datedDecember1,2025',45:'Original Signed By notations datedNovember4and6,2025',75:'Original Signed By notations datedDecember18,2025'}[n],'noSignatureAuthenticationClaim':True})
        print(n,len(candidate['popplerRows']),'rows source corroborated',flush=True)
    assert PACKET.read_bytes()==packet_bytes,'Peer packet changed during review'
    assert sha(worker_code.read_bytes())==worker_code_sha,'Native worker parser changed during review'
    result={'schema':'gap-native-schools-south-independent-source-review-v1','accepted':True,'noOutreach':True,'reviewer':'/root/gap_school_native','packet':ref(PACKET),'sourceImageFirstTranscript':ref(firstpath),'currentSourceImageTranscript':ref(readpath),'peerTranscriptCorrectionPreserved':reads['peerTranscriptCorrections'],
            'personalReviewScope':'All52 bounded named-row source crops and12full source-context images personally viewed; all4239native observations corroborated by full independent-reader comparison and separate payment-row coverage. Not a personal transcription of all4239rows.','sources':receipts,
            'qualifications':['VSB surname/given cells explicitly joined with comma and space; no inferred employee identities. Two student-trustee payments remain included. A literal negative94 expense remains negative.','WestVancouver literal named employee pay is15 above the printed control; trustee controls differ+1/-1. No rounding cause or balancing amount is established. Two expenses carry source*international recruitment footnotes.','Mission trustees have no printed position column and retain null positions. Exact Total control is excluded as aggregate, while444named employee observations remain.'],
            'originalParserActivePath':'scripts/gap_school_south_native.py','parserSnapshotReason':'Preserve the exact bytes executed for these three v4 candidates while the worker continues other layouts; source/data/image values do not change.',
            'earlierActiveParserReplayReceipt':ref(AREA/'peer-south-native-first-replay-review.json'),
            'code':ref(Path(__file__).resolve())}
    out=AREA/'peer-south-native-final-review.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('accepted',sha(out.read_bytes()))
    return result


if __name__=='__main__':review()
