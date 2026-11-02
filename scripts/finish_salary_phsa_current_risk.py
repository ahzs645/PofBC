#!/usr/bin/env python3
"""Freeze bounded FY2019 current-name risk membership and canonical views."""
import gzip
import hashlib
import json
from pathlib import Path
import finish_salary_phsa_ledger as ledger
ROOT=ledger.ROOT
AREA=ledger.AREA
REVIEWS=ledger.REVIEWS

def norm(value):return ''.join(c for c in value if c.isalpha()or c.isdigit())
def inventory():
    manual,_=ledger.manual_fields(verify=False);pages={};selected=[]
    for key,proof in manual.items():
        source,pn,rn,field=key
        if source!='phsa-2019-20'or field!='name':continue
        overlay=ledger.pinned(proof['overlay']);batch=overlay.get('batch')
        if not batch or not batch.rsplit('-',1)[1].isdigit()or not 1<=int(batch.rsplit('-',1)[1])<=13:continue
        path=ledger.COLLECTION/'evidence'/f'{source}-rows-p{pn:03d}.json.gzip'
        if path not in pages:pages[path]=json.loads(gzip.decompress(path.read_bytes()))
        page=pages[path];raw=page['rows'][rn-1]
        if page['sourceId']!=source or raw['candidateRow']!=proof['rawCandidateRow']:raise ValueError('Current risk scope binds another raw observation')
        q=proof['nameTypographyQualification'];engines=[raw['tesseract'],raw['rapidocr']]
        if q:
            if q.get('ambiguityKind')=='rn-m-source-segmentation':
                family={norm(name)for name in [proof['value']]+q['visibleAlternatives']}
                if any(engine is not None and norm(engine['name'])in family for engine in engines):continue
                reason='qualified-name-other-letters-outside-both-reader-families'
            else:reason='closed-non-rn-m-source-name-qualification'
        else:
            if any(engine is not None and norm(engine['name'])==norm(proof['value'])for engine in engines):continue
            reason='direct-name-neither-reader-letters-digits-case-retained'
        selected.append({'sourceId':source,'physicalPage':pn,'sourceRowOnPage':rn,'field':'name','batch':batch,'reason':reason,'proof':proof,'sourcePageEvidence':ledger.pin(path)})
    selected.sort(key=lambda row:(row['physicalPage'],row['sourceRowOnPage']))
    if len(selected)!=len({(r['physicalPage'],r['sourceRowOnPage'])for r in selected}):raise ValueError('Duplicate risk name field')
    return selected

def emit():
    import fitz
    from PIL import Image,ImageChops
    selected=inventory();source='phsa-2019-20';profile_path=AREA/(source+'-processing-profile-001.json');profile=json.loads(profile_path.read_text());pdf_path=Path('/tmp/queue-completion-phsa/originals')/(source+'.pdf')
    if ledger.sha(pdf_path.read_bytes())!=profile['sourceSha256']:raise ValueError('Current-risk original PDF changed')
    document=fitz.open(pdf_path);destination=AREA/'canonical-review/phsa-2019-20-earlier-current-risk';destination.mkdir(parents=True,exist_ok=True);groups={};output=[];choices=[];pages=[]
    for sequence,row in enumerate(selected,1):row['sequence']=sequence;groups.setdefault(row['physicalPage'],[]).append(row)
    def save_image(image,path):
        if path.exists():
            old=Image.open(path).convert('RGB')
            if old.size!=image.size or ImageChops.difference(old,image).getbbox()is not None:raise ValueError('Frozen current-risk image changed')
        else:image.save(path)
        return ledger.pin(path)
    for pn,targets in groups.items():
        page=json.loads(gzip.decompress((ROOT/targets[0]['sourcePageEvidence']['path']).read_bytes()))
        native_path=Path(page['sourceImagePath'])
        if ledger.sha(native_path.read_bytes())!=page['sourceImageSha256']:raise ValueError('Frozen current-risk page PNG changed')
        pix=document[pn-1].get_pixmap(dpi=300,alpha=False);native=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);old=Image.open(native_path).convert('RGB')
        if native.size!=old.size or ImageChops.difference(native,old).getbbox()is not None:raise ValueError('Native300 current-risk page differs from frozen original')
        pix=document[pn-1].get_pixmap(dpi=600,alpha=False);whole=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        pages.append({'physicalPage':pn,'native300OriginalPage':{'path':str(native_path),'sha256':ledger.sha(native_path.read_bytes())},'wholePage600RgbSha256':ledger.sha(pix.samples),'sourcePageEvidence':targets[0]['sourcePageEvidence']})
        for target in targets:
            rn=target['sourceRowOnPage'];band=page['rows'][rn-1]['sourceNameBand'];y0=max(0,band['top']-12);y1=min(native.height,band['bottom']+12);x0=max(0,band['sourceNameBandBox'][0]-12);x1=int(profile['namePayBoundary'])-5
            boxes={'Name':[x0,y0,x1,y1],'Context':[x0,max(0,y0-100),x1,min(native.height,y1+100)],'FullRow':[0,y0,native.width,y1]}
            entry={k:target[k]for k in ['sequence','sourceId','physicalPage','sourceRowOnPage','field','batch','reason','sourcePageEvidence']};entry['sourceSha256']=profile['sourceSha256'];entry['views']={};stem=f"{target['sequence']:03d}-p{pn:03d}-r{rn:02d}"
            for label,box in boxes.items():
                for dpi,image,scale in [(300,native,1),(600,whole,2)]:
                    pixelbox=[n*scale for n in box];path=destination/(stem+f'-whole{dpi}-'+label.lower()+'.png');entry['views'][('native300'if dpi==300 else'wholePage600')+label]={**save_image(image.crop(pixelbox),path),'sourcePixelBox':pixelbox}
            output.append(entry);choices.append({k:target[k]for k in ['sequence','sourceId','physicalPage','sourceRowOnPage','field','batch','reason','sourcePageEvidence']}|{'currentSelectedName':target['proof']['value'],'currentSelectedFieldProof':target['proof']})
    def save(path,value):
        data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
        if path.exists():
            if path.read_bytes()!=data:raise ValueError('Never replace frozen current-risk packet')
        else:path.write_bytes(data)
        return ledger.pin(path)
    packet=save(AREA/'canonical-review/phsa-2019-20-earlier-current-risk-source-only.json',{'frozen':True,'reviewedOn':'2026-11-02','sourceId':source,'sourceSha256':profile['sourceSha256'],'sourceOnly':True,'currentLiteralAndFiniteChoicesWithheld':True,'fieldCount':len(output),'profile':ledger.pin(profile_path),'pages':pages,'rows':output,'scope':'Current earlier ordinary batches001–013; batch012 separately receives complete127currentcanonical-name review and is not yet materialized in this membership snapshot. Source benchmarkfirsttable and later014–017excluded. Letters/digits comparison retainscase and I/l, ignorespunctuation onlyforrisk targeting, neverforacceptingnames.','limits':'Mixed prior-view exposure: earlier first-pass native300 reviews and source hashes already exist. This bounded set does NOT allege allfieldswere readonlyfrompartialclips or anoriginalPDF defect. It conservatively requests explicit canonical-leaf assurance for direct-neither/closed-non-rn-m/otherlettersoutsidequalifiedreaderfamilies before finalsourceclosure. Postexposure reviewonly, notclaimedfreshblind. Money is outside this packet and has separate original/peer gates.','method':'Full physical originalPDFpage RGB300/600 renderedfirst, THEN exactintegercroppedname/context/fullrow views. Every native300fullpageRGB equals frozen capture. No partial get_pixmap clip, resampling, OCR or semanticdecision.'})
    compare=save(AREA/'canonical-review/phsa-2019-20-earlier-current-risk-held-choices.json',{'frozen':True,'reviewedOn':'2026-11-02','sourceId':source,'sourceSha256':profile['sourceSha256'],'sourceOnlyPacket':packet,'withheldUntilSourceReadingsFrozen':True,'rows':choices})
    print(json.dumps({'fields':len(output),'sourceOnlyPacket':packet,'withheldCurrentChoices':compare}))
if __name__=='__main__':emit()
