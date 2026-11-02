#!/usr/bin/env python3
"""Find manual money unsupported by either reader; freeze source-only peer views."""
import argparse
import functools
import gzip
import hashlib
import json
import re
from pathlib import Path

import finish_salary_phsa_ledger as ledger

ROOT=ledger.ROOT
AREA=ledger.AREA
COLLECTION=ledger.COLLECTION


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pin(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def matches_reader(row,field,value):
    token='pay' if field=='remuneration' else 'expense'
    return any(r is not None and r[token]['kind']=='number' and type(r[token]['value'])is int
               and r[token]['value']==value for r in [row['tesseract'],row['rapidocr']])


def verified_confirmation(reference,seen=None):
    path=ROOT/reference['path'];seen=set()if seen is None else set(seen)
    if path in seen:raise ValueError('Cyclic source-money confirmation derivation')
    seen.add(path);document=ledger.pinned(reference)
    for reference in document['peerInputs']:
        # First transcripts may be sparse TSV events. The source-specific
        # replay below parses their actual schema after this byte pin.
        input_path=ROOT/reference['path']
        if not input_path.resolve().is_relative_to(ROOT)or sha(input_path.read_bytes())!=reference['sha256']:
            raise ValueError('Pinned monetary peer input changed')
    peer=document['peerInputs'][0]
    if document.get('adapter')=='source-first-provenance-correction-v1':
        from finish_salary_phsa_money_provenance import build
        expected=build(document['previousConfirmationLedger'],lambda ref:verified_confirmation(ref,seen))
    elif document.get('adapter')in ['unchanged-money-overlay-revision-v1','unchanged-money-overlay-revision-v2']:
        from finish_salary_phsa_money_supersessions import rebase
        expected=rebase(document['previousConfirmationLedger'],document['ordinaryOverlaySupersession'],lambda ref:verified_confirmation(ref,seen),
                        preserve_unrelated_provenance=document['adapter']=='unchanged-money-overlay-revision-v2')
    elif document.get('adapter') in ['direct-scoped-source-peer-v1','direct-scoped-source-peer-v2']:
        from finish_salary_phsa_direct_money_peer import build
        overlay_refs={json.dumps(r['effectiveAuthorOverlay'],sort_keys=True)for r in document['confirmations']}
        if len(overlay_refs)!=1:raise ValueError('One ordinary overlay is required for direct source proof')
        expected=build(peer,document['confirmations'][0]['effectiveAuthorOverlay'],document['pixelProof'])
    elif document.get('adapter') == 'literal-source-table-money-peer-v1':
        expected=adopt_table_peer(ROOT/peer['path'],peer['sha256'],None)
    elif document.get('adapter') == 'count-independent-source-money-peer-v1':
        from finish_salary_phsa_money_peer import build
        overlay_refs={json.dumps(r['effectiveAuthorOverlay'],sort_keys=True)for r in document['confirmations']}
        if len(overlay_refs)!=1:raise ValueError('One ordinary overlay is required for this source peer adapter')
        expected=build(peer,document['confirmations'][0]['effectiveAuthorOverlay'])
    elif document.get('noSalaryValuesChanged') is True:
        expected=adopt_peer(ROOT/peer['path'],peer['sha256'],None)
    elif document.get('doesNotEditAnySalaryOrRawEvidence') is True:
        overlay_refs={json.dumps(r['effectiveAuthorOverlay'],sort_keys=True)for r in document['confirmations']}
        if len(overlay_refs)!=1:raise ValueError('One ordinary overlay is required for this source peer adapter')
        expected=adopt_overlay_peer(ROOT/peer['path'],peer['sha256'],document['confirmations'][0]['effectiveAuthorOverlay'],None)
    else:raise ValueError('Unrecognized monetary confirmation derivation')
    if ((json.dumps(expected,ensure_ascii=False,indent=2)+'\n').encode()!=path.read_bytes()
            or json.dumps(expected,ensure_ascii=False,sort_keys=True)!=json.dumps(document,ensure_ascii=False,sort_keys=True)):
        raise ValueError('Derived monetary confirmation does not replay its pinned source peer evidence')
    return document


def confirmations():
    result={}
    from finish_salary_phsa_money_supersessions import selected
    paths,revisions=selected((AREA/'triangulation').glob('money-peer-confirmations-*.json'))
    for path in paths:
        document=json.loads(path.read_text())
        document=verified_confirmation(pin(path))
        preserved={tuple(r[k]for k in ['sourceId','physicalPage','sourceRowOnPage','field']):r for r in document.get('preservedUnchangedFieldProvenance',[])}
        for entry in document['confirmations']:
            key=(entry['sourceId'],entry['physicalPage'],entry['sourceRowOnPage'],entry['field'])
            if key in result or entry['field'] not in ['remuneration','expenses'] or type(entry['confirmedValue'])is not int:
                raise ValueError('Duplicate/invalid fresh source-money peer confirmation')
            ledger.pinned(entry['effectiveAuthorOverlay']);ledger.pinned(entry['peerComparison'])
            if key in preserved:
                record=preserved[key];original=verified_confirmation(record['confirmationLedger'])
                matches=[r for r in original['confirmations']if tuple(r[k]for k in ['sourceId','physicalPage','sourceRowOnPage','field'])==key]
                if matches!=[entry]:raise ValueError('Unrelated field provenance no longer binds its exact original confirmation')
                result[key]={**entry,'confirmationLedger':record['confirmationLedger']}
                if record.get('confirmationSupersession'):
                    selector=ledger.pinned(record['confirmationSupersession'])
                    if selector['effectiveConfirmation']!=record['confirmationLedger']:raise ValueError('Preserved field selector points to a different confirmation')
                    result[key]['confirmationSupersession']=record['confirmationSupersession']
            else:
                result[key]={**entry,'confirmationLedger':pin(path)}
                if path in revisions:result[key]['confirmationSupersession']=revisions[path]
    return result


def adopt_table_peer(path,digest,out):
    """Exact source-only table with an unchanged independently frozen transcript."""
    peer_ref={'path':str(path.relative_to(ROOT)),'sha256':digest};review=ledger.pinned(peer_ref)
    packet=ledger.pinned(review['sourceOnlyPacket']);raw=ledger.pinned(review['peerRawSourceFirst'])
    choices=ledger.pinned(review['authorScopedChoicesOpenedAfterRaw'])
    identity=lambda r:(r['physicalPage'],r['sourceRowOnPage'],r['field'])
    def unique(rows):
        if any(type(r['physicalPage'])is not int or type(r['sourceRowOnPage'])is not int
               or min(r['physicalPage'],r['sourceRowOnPage'])<1 for r in rows):
            raise ValueError('Invalid literal source-table locator')
        result={identity(r):r for r in rows}
        if len(result)!=len(rows):raise ValueError('Duplicate literal source-table field')
        return result
    target,first,author,peers=map(unique,[packet['rows'],raw['rows'],choices['rows'],review['rows']])
    if (not target or any(set(rows)!=set(target)for rows in [first,author,peers])
            or raw['frozen']is not True or raw['correspondingChoicesOpened']is not False
            or raw['sourceOnlyPacket']!=review['sourceOnlyPacket']
            or any(type(v)is not int for v in review['counts'].values())
            or review['counts']!={'sourceFields':len(target),'positiveIntegerFields':len(target),
                                 'firstValuesMatchingAuthor':len(target),'ownSourceCorrections':0,'unresolved':0}):
        raise ValueError('Literal source-table scope/first-reading gate differs')
    confirmed=[]
    for key,source in target.items():
        original,choice,peer=first[key],author[key],peers[key];value=original['literalImageValue']
        if (key[2]not in ['remuneration','expenses']or type(value)is not int or value<=0
                or any(type(v)is not int for v in [choice['authorResolvedValue'],peer['peerInitialImageFirstValue'],peer['peerFinalValue'],peer['authorFinalValue']])
                or not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',original['literalImageText'])
                or int(original['literalImageText'].replace(',',''))!=value or original['uncertainty']is not None
                or any((r['sourceId'],r['sourceSha256'])!=(review['sourceId'],review['sourceSha256'])for r in [source,original,choice])
                or any(r['sequence']!=source['sequence']for r in [original,choice,peer])
                or original['actualPdf600View']!=source['actualPdf600View']or choice['actualPdf600View']!=source['actualPdf600View']
                or choice['authorResolvedValue']!=value or peer['peerInitialImageFirstValue']!=value
                or peer['peerFinalValue']!=value or peer['authorFinalValue']!=value
                or peer['sourceImage']!=source['actualPdf600View']or peer['independentActualPdfPixelsMatch']is not True
                or peer['status']!='confirmed-exact-from-original-image'):
            raise ValueError('Literal source-table value/source/history differs')
        overlay=ledger.pinned(choice['authorOverlay'])
        candidates=[r for r in overlay['overlays']if(r['physicalPage'],r['sourceRowOnPage'])==key[:2]]
        if (overlay['sourceId']!=review['sourceId']or overlay['sourceSha256']!=review['sourceSha256']
                or len(candidates)!=1 or key[2]not in candidates[0]['reviewedFields']
                or candidates[0]['resolvedRow'][ledger.FIELDS[key[2]]]!=value):
            raise ValueError('Literal source-table amount differs from exact effective overlay')
        source_path=ROOT/source['actualPdf600View']['path']
        if sha(source_path.read_bytes())!=source['actualPdf600View']['sha256']:raise ValueError('Literal source-table image changed')
        confirmed.append({'sourceId':review['sourceId'],'sourceSha256':review['sourceSha256'],
                          'physicalPage':key[0],'sourceRowOnPage':key[1],'field':key[2],'confirmedValue':value,
                          'effectiveAuthorOverlay':choice['authorOverlay'],'peerComparison':peer_ref,
                          'freshSourceImage':source['actualPdf600View'],'imageFirstTranscript':review['peerRawSourceFirst']})
    value={'frozen':True,'adapter':'literal-source-table-money-peer-v1',
           'peerInputs':[peer_ref,review['sourceOnlyPacket'],review['peerRawSourceFirst'],review['authorScopedChoicesOpenedAfterRaw']],
           'confirmations':confirmed,'scope':'Exact unchanged source-first positive monetary fields only; no other field, inferred null or source-control authority.'}
    if out is None:return value
    if out.exists():raise ValueError('Never replace frozen literal source-table confirmations')
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');return pin(out)


def adopt_peer(path,digest,out):
    review=ledger.pinned({'path':str(path.relative_to(ROOT)),'sha256':digest})
    confirmed_all=(review.get('allLiteralValuesMatchFrozenAuthor') is True
                   or (review.get('all15LiteralValuesMatchFrozenAuthor') is True and len(review['rows'])==15))
    if not confirmed_all or review['candidateChanges'] or review['unresolvedFields']:
        raise ValueError('A source-money mismatch needs revised ordinary source review, not confirmation')
    packet=ledger.pinned(review['sourceOnlyPacket']);choices=ledger.pinned(review['authorChoicesOpenedAfterTranscriptFreeze'])
    transcript=ledger.pinned(review['independentImageFirstTranscript'])
    identity=lambda r:(r['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field'])
    before={identity(r):r for r in choices['rows']};blind={identity(r):r for r in packet['rows']};seen=set();confirmed=[]
    if 'rows' in transcript:
        raw_rows=transcript['rows']
        blind_gate=(transcript['sourceOnlyPacket']==review['sourceOnlyPacket']
                    and transcript['readFromActualOriginal600DpiViewsBeforeAnyAuthorOrMachineChoices'] is True
                    and not transcript['unresolvedFields'])
    else:
        values=transcript['readingsInPacketOrder']
        if len(values)!=len(packet['rows']):raise ValueError('Ordered source-first transcript is incomplete')
        raw_rows=[{**r,'literalSourceValue':value}for r,value in zip(packet['rows'],values)]
        blind_gate=(transcript['sourceOnlyPacketSha256']==review['sourceOnlyPacket']['sha256']
                    and transcript['authorOrOcrChoicesOpened'] is False and transcript['frozen'] is True
                    and not transcript['genuineUnresolvedMonetaryFields']
                    and all((r['sourceId'],r['sourceSha256'])==(transcript['sourceId'],transcript['sourceSha256'])for r in packet['rows']))
    raw={identity(r):r for r in raw_rows}
    if len(raw)!=len(raw_rows) or set(raw)!=set(blind) or not blind_gate:
        raise ValueError('Incomplete actual source-first money transcript')
    for row in review['rows']:
        key=identity(row)
        if key in seen or key not in before or key not in blind:raise ValueError('Duplicate/out-of-scope monetary peer result')
        seen.add(key);author=before[key];source=blind[key]
        if (any(type(v)is not int for v in [row['literalSourceValue'],author['authorResolvedValue'],raw[key]['literalSourceValue']])
                or row['literalSourceValue']!=author['authorResolvedValue'] or row['authorOverlay']!=author['authorOverlay']
                or raw[key]['literalSourceValue']!=row['literalSourceValue']
                or raw[key]['actualPdf600View']!=row['sourceImage']
                or row['sourceSha256']!=source['sourceSha256'] or row['sourceImage']!=source['actualPdf600View']
                or not row['matchesPreviouslyFrozenAuthorAmount'] or not row['actualSource600DpiPixelsIndependentlyReproducedExactly']):
            raise ValueError('Fresh peer amount/source/author proof differs')
        image=ROOT/row['sourceImage']['path']
        if sha(image.read_bytes())!=row['sourceImage']['sha256']:raise ValueError('Source-money peer image changed')
        confirmed.append({'sourceId':key[0],'sourceSha256':row['sourceSha256'],'physicalPage':key[1],
                          'sourceRowOnPage':key[2],'field':key[3],'confirmedValue':row['literalSourceValue'],
                          'effectiveAuthorOverlay':row['authorOverlay'],'peerComparison':{'path':str(path.relative_to(ROOT)),'sha256':digest},
                          'freshSourceImage':row['sourceImage'],'imageFirstTranscript':review['independentImageFirstTranscript']})
    if seen!=set(before) or seen!=set(blind):raise ValueError('Incomplete source-money peer confirmation')
    value={'frozen':True,'scope':'Only exact listed fresh-source monetary confirmations; no balancing/control/name authority.',
           'peerInputs':[{'path':str(path.relative_to(ROOT)),'sha256':digest},review['sourceOnlyPacket'],
                         review['authorChoicesOpenedAfterTranscriptFreeze'],review['independentImageFirstTranscript']],
           'confirmations':confirmed,'noSalaryValuesChanged':True}
    if out is None:return value
    if out.exists():raise ValueError('Never replace frozen monetary confirmation')
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(pin(out)))


def adopt_overlay_peer(path,digest,overlay_reference,out):
    """Bind adjudicated source-first peer values after an ordinary overlay exists."""
    review=ledger.pinned({'path':str(path.relative_to(ROOT)),'sha256':digest});overlay=ledger.pinned(overlay_reference)
    if not review.get('all12SourceFieldsIndependentlyConfirmed') or review['unresolvedFields'] or review['candidateChangesMadeByPeer']:
        raise ValueError('Incomplete source monetary peer/adjudication')
    inputs={field:ledger.pinned(review[field])for field in ['independentImageFirstTranscript','sourceOnlyPacket','authorChoicesOpenedAfterTranscriptFreeze']}
    identity=lambda r:(r['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field'])
    target={identity(r):r for r in inputs['sourceOnlyPacket']['rows']}
    original_choices={identity(r):r for r in inputs['authorChoicesOpenedAfterTranscriptFreeze']['rows']}
    peer_rows={identity(r):r for r in review['rows']}
    if len(target)!=len(inputs['sourceOnlyPacket']['rows']) or len(peer_rows)!=len(review['rows']) or set(target)!=set(peer_rows) or set(target)!=set(original_choices):
        raise ValueError('Fresh monetary peer must cover exactly the complete frozen source-only field set')
    rows={(r['physicalPage'],r['sourceRowOnPage']):r for r in overlay['overlays']};confirmed=[];seen=set()
    if (review['sourceId'],review['sourceSha256'],review['batch'])!=(overlay['sourceId'],overlay['sourceSha256'],overlay['batch']):
        raise ValueError('Peer source/batch differs from effective reviewed overlay')
    for r in review['rows']:
        key=(r['physicalPage'],r['sourceRowOnPage']);field=r['field'];value=r['literalSourceValue'];row=rows[key]
        if (*key,field) in seen or field not in ['remuneration','expenses'] or type(value)is not int:
            raise ValueError('Invalid fresh source monetary field')
        seen.add((*key,field))
        original=target[identity(r)];choice=original_choices[identity(r)]
        if (r['sourceSha256']!=overlay['sourceSha256'] or original['sourceSha256']!=overlay['sourceSha256']
                or r['actual600SourceField']!=original['actual600SourceField']
                or r['originalFullRowCropSha256']!=original['originalFullRowCropSha256']
                or r['authorFrozenValue']!=choice['authorSourceValue']
                or r['matchesFrozenAuthorValue']!=(r['literalSourceValue']==choice['authorSourceValue'])):
            raise ValueError('Monetary peer source/image/original-choice facts differ')
        if field not in row['reviewedFields'] or row['resolvedRow'][ledger.FIELDS[field]]!=value or row['cropSha256']!=r['originalFullRowCropSha256']:
            raise ValueError('Final source reading is not the exact peer-confirmed field/crop')
        image=r['actual600SourceField'];ip=ROOT/image['path']
        if sha(ip.read_bytes())!=image['sha256'] or not r['actual600DpiSourcePixelsIndependentlyReproducedExactly']:
            raise ValueError('Fresh peer source image is not independently validated')
        confirmed.append({'sourceId':review['sourceId'],'sourceSha256':review['sourceSha256'],'physicalPage':key[0],
                          'sourceRowOnPage':key[1],'field':field,'confirmedValue':value,'effectiveAuthorOverlay':overlay_reference,
                          'peerComparison':{'path':str(path.relative_to(ROOT)),'sha256':digest},'freshSourceImage':image,
                          'imageFirstTranscript':review['independentImageFirstTranscript']})
    result={'frozen':True,'peerInputs':[{'path':str(path.relative_to(ROOT)),'sha256':digest},review['independentImageFirstTranscript'],
                                      review['sourceOnlyPacket'],review['authorChoicesOpenedAfterTranscriptFreeze']],
            'confirmations':confirmed,'doesNotEditAnySalaryOrRawEvidence':True,
            'originalAuthorFirstReadMatches':review['authorFirstReadMatches'],
            'originalAuthorSourceCorrectionsRequired':review['sourceBasedAuthorCorrectionsRequired'],
            'notClaimingUnanimityForOriginalAuthorReadings':True}
    if out is None:return result
    if out.exists():raise ValueError('Never replace immutable source monetary confirmations')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(pin(out)))


@functools.lru_cache(maxsize=None)
def page(path):return json.loads(gzip.decompress(path.read_bytes()))


def needed():
    manual,_=ledger.manual_fields();result=[]
    for key,proof in sorted(manual.items()):
        source,pn,rn,field=key;value=proof['value']
        if field=='name' or value is None:continue
        pp=COLLECTION/'evidence'/f'{source}-rows-p{pn:03d}.json.gzip';p=page(pp);row=p['rows'][rn-1]
        if matches_reader(row,field,value):continue
        result.append({'sourceId':source,'physicalPage':pn,'sourceRowOnPage':rn,'field':field,
                       'value':value,'proof':proof,'pageEvidence':pin(pp),'row':row})
    return result


def emit(number,source_filter=None):
    from PIL import Image,ImageDraw
    import fitz
    directory=AREA/'triangulation';directory.mkdir(parents=True,exist_ok=True)
    blind_path=directory/f'money-{number:03d}-source-only.json';candidate_path=directory/f'money-{number:03d}-candidate.json'
    if blind_path.exists() or candidate_path.exists():raise ValueError('Never replace a frozen monetary peer packet')
    excluded=set(confirmations());external=[]
    source_peer=ROOT/'research/salaries/queue-completion-2026-11-01/reviews/root-phsa-history-2018-19-batch-002-triangulation-source-only-peer.json'
    if source_peer.exists():
        peer=json.loads(source_peer.read_text());external.append(pin(source_peer))
        excluded.update((peer['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field']) for r in peer['rows'])
    for path in directory.glob('money-*-source-only.json'):
        previous=json.loads(path.read_text())
        excluded.update((r['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field']) for r in previous['rows'])
    targets=[r for r in needed() if (source_filter is None or r['sourceId']==source_filter)
             and (r['sourceId'],r['physicalPage'],r['sourceRowOnPage'],r['field']) not in excluded]
    if not targets:raise ValueError('No new unassigned source-money targets')
    inventory={s['id']:s for s in json.loads((AREA/'source-inventory.json').read_text())['sources']}
    docs={};profiles={};blind=[];full=[];images=[]
    for sequence,target in enumerate(targets,1):
        source=target['sourceId'];pn=target['physicalPage'];rn=target['sourceRowOnPage'];field=target['field'];spec=inventory[source]
        if source not in docs:
            original=Path(spec['cachePath'])
            if sha(original.read_bytes())!=spec['sourceSha256']:raise ValueError('Wrong actual original for monetary peer')
            docs[source]=fitz.open(original);profiles[source]=json.loads((AREA/(source+'-processing-profile-001.json')).read_text())
        profile=profiles[source];p=page(ROOT/target['pageEvidence']['path']);box=list(target['row']['expenseOriginalImage']['sourceExpenseCellBox'])
        if field=='remuneration':box[0]=profile['namePayBoundary']-8;box[2]=profile['payExpenseBoundary']+8
        else:box[0]=profile['payExpenseBoundary']-8
        image_path=Path('/tmp/queue-completion-phsa')/source/'images'/f'p{pn:03d}.png'
        if sha(image_path.read_bytes())!=p['sourceImageSha256']:raise ValueError('Wrong actual painted source image')
        asset=directory/'assets'/f'money-{number:03d}-{sequence:03d}-300.png';asset.parent.mkdir(parents=True,exist_ok=True)
        native=Image.open(image_path).crop(box);native.save(asset)
        zoom=directory/'assets'/f'money-{number:03d}-{sequence:03d}-actual600.png'
        clip=fitz.Rect([v*72/300 for v in box]);docs[source][pn-1].get_pixmap(dpi=600,clip=clip,alpha=False).save(zoom)
        row={'sequence':sequence,'sourceId':source,'sourceSha256':spec['sourceSha256'],
             'physicalPage':pn,'sourceRowOnPage':rn,'field':field,'pageEvidence':target['pageEvidence'],
             'sourceImageSha256':p['sourceImageSha256'],'original300DpiPixelBox':box,
             'sourceNative300View':pin(asset),'actualPdf600View':pin(zoom),
             'originalMoneyScopePreserved':True}
        blind.append(row);full.append({**row,'authorResolvedValue':target['value'],'authorOverlay':target['proof']['overlay']})
        images.append((sequence,source,pn,rn,field,Image.open(zoom).copy()))
    sheets=[]
    for offset in range(0,len(images),15):
        block=images[offset:offset+15];width=max(im.width for *_,im in block);height=sum(im.height+30 for *_,im in block)
        sheet=Image.new('RGB',(width,height),'white');draw=ImageDraw.Draw(sheet);y=0
        for seq,source,pn,rn,field,im in block:
            draw.text((0,y+4),f'{seq:03d} | {source} | p{pn} r{rn} | {field}',fill='black')
            sheet.paste(im,(0,y+30));y+=30+im.height
        sheet_path=directory/'assets'/f'money-{number:03d}-actual600-sheet-{offset//15+1:03d}.png';sheet.save(sheet_path);sheets.append(pin(sheet_path))
    candidate={'frozen':True,'rows':full,'doesNotAuthorizeCorrectionsWithoutFreshPeer':True}
    candidate_path.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n')
    packet={'frozen':True,'date':'2026-11-01','assignedReviewer':'/root','rows':blind,
            'scope':'Fresh source-image transcription of manual money matched by neither independent parsed reader; these are targets, not presumed source errors.',
            'contactSheets':sheets,'separateAuthorChoices':pin(candidate_path),'excludedAlreadyAssignedSourcePeerPackets':external,
            'instructions':['Do not open author choices before freezing the literal source-only transcript.','Read each requested monetary field from native original pixels or actual600dpi PDF view. No balancing, guessed digit, threshold correction, dash/zero imputation or unrelated field change.','Any mismatch requires explicit original-source reread/secondary adjudication before a revised ordinary overlay. Existing overlays/raw stay immutable.']}
    blind_path.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sourceOnly':pin(blind_path),'fields':len(blind),'contactSheets':sheets}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--emit',type=int);p.add_argument('--source');p.add_argument('--adopt-peer');p.add_argument('--author-overlay');p.add_argument('--out');a=p.parse_args()
    if a.emit:emit(a.emit,a.source)
    elif a.adopt_peer:
        path,digest=a.adopt_peer.rsplit('=',1)
        if a.author_overlay:
            op,os=a.author_overlay.rsplit('=',1);adopt_overlay_peer(ROOT/path,digest,{'path':op,'sha256':os},ROOT/a.out)
        else:adopt_peer(ROOT/path,digest,ROOT/a.out)
    else:print(json.dumps([{k:v for k,v in r.items()if k not in ['row','proof','value']} for r in needed()]))
