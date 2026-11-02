#!/usr/bin/env python3
"""Emit source-only canonical views for every already-qualified final name.

No semantic decision or old evidence mutation. Optional imaging dependencies load
only when the explicit emit command runs; offline consumers inspect pinned bytes.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/queue-completion-2026-11-01/phsa'
EVIDENCE=ROOT/'research/salaries/queue-completion-phsa/evidence'

def sha(data):return hashlib.sha256(data).hexdigest()
def pin(path):return {'path':str(path.relative_to(ROOT))if path.is_relative_to(ROOT)else str(path),'sha256':sha(path.read_bytes())}
def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data)if path.suffix=='.gzip'else data)
def save(path,value):
    data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('Refusing to change frozen canonical source packet')
    else:path.write_bytes(data)
    return pin(path)
def selected_rows(provenance,direct_neither=False):
    source=provenance['originalRowsAndPerFieldResolution']
    if direct_neither:
        pages={};rows=[]
        letters_digits=lambda value:''.join(c for c in value if c.isalpha()or c.isdigit())
        for row in source['rows']:
            if row['fields']['name']['status']!='manual-original-image':continue
            page_path=ROOT/row['sourcePageEvidence']['path']
            if sha(page_path.read_bytes())!=row['sourcePageEvidence']['sha256']:raise ValueError('Direct-name original reader evidence changed')
            if page_path not in pages:pages[page_path]=read(page_path)
            original=pages[page_path]['rows'][row['sourceRowOnPage']-1]
            observed=letters_digits(row['row'][1])
            if all(engine is None or observed!=letters_digits(engine['name'])for engine in [original['tesseract'],original['rapidocr']]):rows.append(row)
    else:rows=[r for r in source['rows']if r['fields']['name']['status']=='manual-qualified-source-typography']
    keys=[(r['row'][5],r['sourceRowOnPage'])for r in rows]
    if len(keys)!=len(set(keys))or (not direct_neither and len(rows)!=len(source['rootAdoptedQualifiedNameCases'])):
        raise ValueError('Canonical quality scope must exactly equal all distinct qualified source names')
    return rows

def emit(source_id,direct_neither=False):
    import fitz
    from PIL import Image,ImageChops
    provenance_path=EVIDENCE/(source_id+'-provenance-v3.json.gzip');provenance=read(provenance_path)
    if provenance['sourceId']!=source_id:raise ValueError('Canonical source identity differs')
    selected=selected_rows(provenance,direct_neither)
    profile_path=AREA/(source_id+'-processing-profile-001.json');profile=read(profile_path)
    pdf_path=Path('/tmp/queue-completion-phsa/originals')/(source_id+'.pdf')
    if sha(pdf_path.read_bytes())!=provenance['sourceSha256']or profile['sourceSha256']!=provenance['sourceSha256']:
        raise ValueError('Canonical source PDF/profile changed')
    label='direct-neither-name'if direct_neither else'qualified-name'
    destination=AREA/'canonical-review'/(source_id+('-direct-neither'if direct_neither else''));destination.mkdir(parents=True,exist_ok=True)
    document=fitz.open(pdf_path);groups={}
    for row in selected:groups.setdefault(row['row'][5],[]).append(row)
    output=[];choices=[];pages=[]
    def image_write(image,path):
        if path.exists():
            supplied=Image.open(path).convert('RGB')
            if supplied.size!=image.size or ImageChops.difference(supplied,image).getbbox()is not None:
                raise ValueError('Existing frozen canonical image differs')
        else:image.save(path)
        return pin(path)
    for pn,rows in groups.items():
        evidence_path=EVIDENCE/(source_id+f'-rows-p{pn:03d}.json.gzip');page=read(evidence_path)
        source_image=Path(page['sourceImagePath'])
        if sha(source_image.read_bytes())!=page['sourceImageSha256']:raise ValueError('Native300 source image changed')
        pix=document[pn-1].get_pixmap(dpi=300,alpha=False);native=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        existing=Image.open(source_image).convert('RGB')
        if existing.size!=native.size or ImageChops.difference(existing,native).getbbox()is not None:
            raise ValueError('Full physical-page native300 render differs from frozen source')
        pix=document[pn-1].get_pixmap(dpi=600,alpha=False);whole=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        pages.append({'physicalPage':pn,'sourcePageEvidence':pin(evidence_path),'actualNative300Page':pin(source_image),'wholePage600RgbSha256':sha(pix.samples),'wholePage600Dimensions':[pix.width,pix.height]})
        for row in rows:
            raw=page['rows'][row['sourceRowOnPage']-1]
            if raw['sourceRowOnPage']!=row['sourceRowOnPage']or row['sourceImageSha256']!=page['sourceImageSha256']:
                raise ValueError('Canonical row/source provenance differs')
            band=raw['sourceNameBand'];y0=max(0,band['top']-12);y1=min(native.height,band['bottom']+12)
            x0=max(0,band['sourceNameBandBox'][0]-12);x1=int(profile['namePayBoundary'])-5
            boxes={'Name':[x0,y0,x1,y1],'Context':[x0,max(0,y0-100),x1,min(native.height,y1+100)],'FullRow':[0,y0,native.width,y1]}
            entry={'sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'physicalPage':pn,'sourceRowOnPage':row['sourceRowOnPage'],'reviewTargetFields':['name'],'sourcePageEvidence':pin(evidence_path),'sourceImageSha256':page['sourceImageSha256'],'views':{}}
            stem=f'p{pn:03d}-r{row["sourceRowOnPage"]:02d}'
            for kind,box in boxes.items():
                twice=[n*2 for n in box]
                entry['views']['native300'+kind]={**image_write(native.crop(box),destination/(stem+'-native300-'+kind.lower()+'.png')),'sourcePixelBox':box}
                entry['views']['wholePage600'+kind]={**image_write(whole.crop(twice),destination/(stem+'-whole600-'+kind.lower()+'.png')),'sourcePixelBox':twice}
            output.append(entry)
            choices.append({'sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'physicalPage':pn,'sourceRowOnPage':row['sourceRowOnPage'],'heldV3ChosenName':row['row'][1],'heldV3NameResolutionEvidence':row['fields']['name']})
    count_label='directNamesDifferingFromBothReadersLettersDigitsCaseRetained'if direct_neither else'qualifiedNames'
    base={'frozen':True,'createdOn':'2026-11-02','sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'finalV3Provenance':pin(provenance_path),'processingProfile':pin(profile_path),count_label:len(output),'candidateValuesWithheld':True,'method':'Full physical-page PyMuPDF1.26.6 RGB get_pixmap at300and600dpi, THEN integer pixel crops. Native300 fullpage pixels independently compared exactly to original frozen selected-capture images. No partial get_pixmap clip. All prior finite choices withheld from this source-only packet.','limits':'This is a canonical-view post-exposure semantic recheck packet. The emitter validates source bytes and geometry only; no emitted crop implies a name or alternative is semantically supported. Earlier partial views/readings remain immutable. Unsupported alternatives require withdrawal and exact versioned review/root adoption before publication.','pages':pages,'rows':output}
    packet=save(AREA/'canonical-review'/(source_id+'-'+label+'-source-only.json'),base)
    compare=save(AREA/'canonical-review'/(source_id+'-'+label+'-held-v3-choices.json'),{'frozen':True,'sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'sourceOnlyPacket':packet,'doNotOpenUntilCanonicalReadingsFrozen':True,'rows':choices})
    return {'sourceId':source_id,count_label:len(output),'sourceOnlyPacket':packet,'withheldHeldV3Comparison':compare}

def emit_money(source_id):
    import fitz
    from PIL import Image,ImageChops
    provenance_path=EVIDENCE/(source_id+'-provenance-v3.json.gzip');provenance=read(provenance_path)
    profile_path=AREA/(source_id+'-processing-profile-001.json');profile=read(profile_path)
    pdf_path=Path('/tmp/queue-completion-phsa/originals')/(source_id+'.pdf')
    if sha(pdf_path.read_bytes())!=provenance['sourceSha256']or profile['sourceSha256']!=provenance['sourceSha256']:
        raise ValueError('Canonical money PDF/profile changed')
    targets=[]
    for row in provenance['originalRowsAndPerFieldResolution']['rows']:
        for field,index in [('remuneration',3),('expenses',4)]:
            detail=row['fields'][field]['evidence']
            if isinstance(detail,dict)and detail.get('freshIndependentSourceMoneyPeer'):
                if type(row['row'][index])is not int or row['row'][index]<=0:raise ValueError('Canonical positive-neither audit may not absorb nulls/zero')
                targets.append((row,field,index))
    groups={}
    for target in targets:groups.setdefault(target[0]['row'][5],[]).append(target)
    destination=AREA/'canonical-review'/(source_id+'-money');destination.mkdir(parents=True,exist_ok=True)
    document=fitz.open(pdf_path);output=[];choices=[];pages=[]
    for pn,entries in groups.items():
        evidence_path=EVIDENCE/(source_id+f'-rows-p{pn:03d}.json.gzip');page=read(evidence_path);source_image=Path(page['sourceImagePath'])
        if sha(source_image.read_bytes())!=page['sourceImageSha256']:raise ValueError('Canonical money source PNG changed')
        pix=document[pn-1].get_pixmap(dpi=300,alpha=False);native=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        supplied=Image.open(source_image).convert('RGB')
        if supplied.size!=native.size or ImageChops.difference(supplied,native).getbbox()is not None:
            raise ValueError('Canonical money native300 fullpage differs')
        pix=document[pn-1].get_pixmap(dpi=600,alpha=False);whole=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        pages.append({'physicalPage':pn,'sourcePageEvidence':pin(evidence_path),'actualNative300Page':pin(source_image),'wholePage600RgbSha256':sha(pix.samples)})
        for row,field,index in entries:
            raw=page['rows'][row['sourceRowOnPage']-1];band=raw['sourceNameBand'];y0=max(0,band['top']-12);y1=min(native.height,band['bottom']+12)
            x0=int(profile['namePayBoundary'])if field=='remuneration'else int(profile['payExpenseBoundary'])
            x1=int(profile['payExpenseBoundary'])if field=='remuneration'else native.width
            boxes={'Field':[x0,y0,x1,y1],'FullRow':[0,y0,native.width,y1]}
            entry={'sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'physicalPage':pn,'sourceRowOnPage':row['sourceRowOnPage'],'field':field,'sourcePageEvidence':pin(evidence_path),'views':{}}
            stem=f'p{pn:03d}-r{row["sourceRowOnPage"]:02d}-{field}'
            for kind,box in boxes.items():
                for label,image,scale in [('native300',native,1),('wholePage600',whole,2)]:
                    pixels=[n*scale for n in box];path=destination/(stem+'-'+label+'-'+kind.lower()+'.png');cropped=image.crop(pixels)
                    if path.exists():
                        previous=Image.open(path).convert('RGB')
                        if previous.size!=cropped.size or ImageChops.difference(previous,cropped).getbbox()is not None:raise ValueError('Canonical money view changed')
                    else:cropped.save(path)
                    entry['views'][label+kind]={**pin(path),'sourcePixelBox':pixels}
            output.append(entry);choices.append({'sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'physicalPage':pn,'sourceRowOnPage':row['sourceRowOnPage'],'field':field,'heldV3ChosenValue':row['row'][index],'heldV3FieldResolutionEvidence':row['fields'][field]})
    if len(output)!=len({(r['physicalPage'],r['sourceRowOnPage'],r['field'])for r in output}):raise ValueError('Duplicate canonical positive-money field')
    packet=save(AREA/'canonical-review'/(source_id+'-positive-neither-money-source-only.json'),{'frozen':True,'createdOn':'2026-11-02','sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'finalV3Provenance':pin(provenance_path),'processingProfile':pin(profile_path),'positiveMonetaryFields':len(output),'candidateValuesWithheld':True,'method':'Actual full physical-page PyMuPDF1.26.6 RGB300/600 render, THEN integer source pixel crops. Native300 fullpage pixels independently exactly reproduce frozen capture. No partial clip rendering.','limits':'Bounded post-exposure canonical leaf recheck of positive manual fields matched by neither strict parsed engine. All already have raw/source/fresh-peer evidence; this packet does not allege missing source proof, change amounts or include source-null dashes. Explicit canonical-leaf semantic confirmation under this new gate remains pending.','pages':pages,'rows':output})
    compare=save(AREA/'canonical-review'/(source_id+'-positive-neither-money-held-v3-choices.json'),{'frozen':True,'sourceId':source_id,'sourceSha256':provenance['sourceSha256'],'sourceOnlyPacket':packet,'doNotOpenUntilCanonicalReadingsFrozen':True,'rows':choices})
    return {'sourceId':source_id,'positiveMonetaryFields':len(output),'sourceOnlyPacket':packet,'withheldHeldV3Comparison':compare}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='append');mode=parser.add_mutually_exclusive_group();mode.add_argument('--money',action='store_true');mode.add_argument('--direct-neither-name',action='store_true');args=parser.parse_args()
    sources=args.source or [p.name.removesuffix('-provenance-v3.json.gzip')for p in sorted(EVIDENCE.glob('phsa-*-provenance-v3.json.gzip'))]
    for source in sources:print(json.dumps(emit_money(source)if args.money else emit(source,args.direct_neither_name)),flush=True)
if __name__=='__main__':main()
