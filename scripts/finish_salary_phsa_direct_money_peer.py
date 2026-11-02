#!/usr/bin/env python3
"""Bind direct blinded source-field transcripts to exact reviewed money cells."""
import json
import re
from pathlib import Path

import finish_salary_phsa_ledger as ledger


def keyed(rows):
    if any(type(r['sequence'])is not int or r['sequence']<1 or r['field']not in ['name','remuneration','expenses']
           or any(type(r[k])is not int or r[k]<1 for k in ['physicalPage','sourceRowOnPage']if k in r)for r in rows):
        raise ValueError('Invalid direct source-field locator/type')
    out={(r['sequence'],r['field']):r for r in rows}
    if len(out)!=len(rows):raise ValueError('Duplicate direct source-field peer target')
    return out


def reproduce(peer_reference,out):
    """Research-only original raster reproduction; no OCR or interpretation."""
    import fitz
    peer=ledger.pinned(peer_reference)
    if 'input'in peer and 'blindness'in peer:return reproduce_current_fields(peer_reference,out)
    packet=ledger.pinned(peer['sourceOnlyPacket'])
    inventory=next(s for s in json.loads((ledger.AREA/'source-inventory.json').read_text())['sources']if s['id']==peer['sourceId'])
    original=Path(inventory['cachePath'])
    if ledger.sha(original.read_bytes())!=peer['sourceSha256']:raise ValueError('Wrong original for direct source-field pixels')
    document=fitz.open(original);rows=[]
    for row in packet['rows']:
        image=row['actualOriginal600DpiField'];native=row['original300SourceField'];box=native['originalPdf300DpiPixelBox']
        actual=document[row['physicalPage']-1].get_pixmap(dpi=600,alpha=False,clip=fitz.Rect(*(v*72/300 for v in box)))
        supplied=fitz.Pixmap(str(ledger.ROOT/image['path']))
        if (actual.width,actual.height,actual.n,actual.samples)!=(supplied.width,supplied.height,supplied.n,supplied.samples):
            raise ValueError('Direct peer source field differs from actual original pixels')
        if ledger.sha((ledger.ROOT/image['path']).read_bytes())!=image['sha256']:raise ValueError('Direct peer source view changed')
        rows.append({'sequence':row['sequence'],'field':row['field'],'physicalPage':row['physicalPage'],
                     'sourceRowOnPage':row['sourceRowOnPage'],'actualOriginal600DpiField':image,
                     'original300DpiPixelBox':box,'independentlyReproducedOriginalPixelsExact':True})
    value={'frozen':True,'sourceId':peer['sourceId'],'sourceSha256':peer['sourceSha256'],'batch':peer['batch'],
           'sourcePeer':peer_reference,'sourceOnlyPacket':peer['sourceOnlyPacket'],'rows':rows,
           'method':'Independent PyMuPDF1.26.6 actualPDF600dpi RGB pixel reproduction using original300pixel-box coordinates; no OCR/field interpretation.'}
    if out.exists():raise ValueError('Never replace direct source pixel proof')
    out.write_text(json.dumps(value,indent=2)+'\n');return ledger.pin(out)


def build(peer_reference,overlay_reference,proof_reference):
    peer=ledger.pinned(peer_reference)
    if 'input'in peer and 'blindness'in peer:return build_current_fields(peer_reference,overlay_reference,proof_reference)
    packet=ledger.pinned(peer['sourceOnlyPacket'])
    overlay=ledger.pinned(overlay_reference);proof=ledger.pinned(proof_reference)
    identity=(peer['sourceId'],peer['sourceSha256'],peer['batch'])
    for document in [packet,overlay,proof]:
        if tuple(document[k]for k in ['sourceId','sourceSha256','batch'])!=identity:
            raise ValueError('Direct source-field peer/overlay identity differs')
    if (peer['frozenBeforeRootAuthorOrOcrChoices'] is not True or peer['fullBatchCandidateOpened'] is not False
            or proof['sourcePeer']!=peer_reference or proof['sourceOnlyPacket']!=peer['sourceOnlyPacket']):
        raise ValueError('Direct source-first/pixel proof gate differs')
    targets,entries,pixels=keyed(packet['rows']),keyed(peer['entries']),keyed(proof['rows'])
    if set(targets)!=set(entries) or set(targets)!=set(pixels):raise ValueError('Direct source-field transcript/proof scope is incomplete')
    frozen=ledger.pinned(overlay['frozenBatch']);original_rows={r['sequence']:r for r in frozen['rows']}
    reviewed={(r['physicalPage'],r['sourceRowOnPage']):r for r in overlay['overlays']};confirmed=[]
    for key,target in targets.items():
        entry,checked,original=entries[key],pixels[key],original_rows[key[0]]
        locator=(target['physicalPage'],target['sourceRowOnPage']);field=target['field']
        view=next(v for v in original['reviewTargetFields']if v==field)
        if (locator!=(original['physicalPage'],original['sourceRowOnPage']) or target['cropSha256']!=original['cropSha256']
                or checked['physicalPage']!=locator[0] or checked['sourceRowOnPage']!=locator[1]
                or checked['original300DpiPixelBox']!=target['original300SourceField']['originalPdf300DpiPixelBox']
                or checked['actualOriginal600DpiField']!=target['actualOriginal600DpiField']
                or checked['independentlyReproducedOriginalPixelsExact'] is not True):
            raise ValueError('Direct source-field pixel/crop/frozen row proof differs')
        image=target['actualOriginal600DpiField']
        if ledger.sha((ledger.ROOT/image['path']).read_bytes())!=image['sha256']:raise ValueError('Direct source original image changed')
        if field=='name':continue  # no name interpretation authority from this monetary adapter
        value=entry['literalSourceValue'];row=reviewed[locator]
        if (type(value)is not int or value<=0 or entry['realUncertainty'] is not None
                or field not in row['reviewedFields'] or row['resolvedRow'][ledger.FIELDS[field]]!=value
                or row['cropSha256']!=target['cropSha256']):
            raise ValueError('Direct independent source money does not confirm exact effective field')
        if 'physicalPage'in entry and (entry['physicalPage'],entry['sourceRowOnPage'])!=locator:
            raise ValueError('Direct monetary transcript moved its actual source row')
        confirmed.append({'sourceId':identity[0],'sourceSha256':identity[1],'physicalPage':locator[0],
                          'sourceRowOnPage':locator[1],'field':field,'confirmedValue':value,
                          'effectiveAuthorOverlay':overlay_reference,'peerComparison':peer_reference,
                          'freshSourceImage':image,'imageFirstTranscript':peer_reference})
    if not confirmed:raise ValueError('Direct source peer has no money fields')
    return {'frozen':True,'adapter':'direct-scoped-source-peer-v1','peerInputs':[peer_reference,peer['sourceOnlyPacket'],proof_reference],
            'pixelProof':proof_reference,'confirmations':confirmed,'completeFrozenSourcePeerFields':len(targets),
            'confirmedMonetaryFields':len(confirmed),'originalAuthorFirstReadingAgreementNotAsserted':True,
            'scope':'Only listed money fields; peer source-first transcript and exact original pixel/crop mapping confirm current effective values. Ordinary source review retains all author corrections; no name/balance/unrelated-column authority.'}


def emit(peer_reference,overlay_reference,proof_reference,out):
    value=build(peer_reference,overlay_reference,proof_reference)
    if out.exists():raise ValueError('Never replace direct source confirmations')
    out.write_text(json.dumps(value,indent=2)+'\n');return ledger.pin(out)


def reproduce_current_fields(peer_reference,out):
    import fitz
    peer=ledger.pinned(peer_reference);packet=ledger.pinned(peer['input'])
    inventory=next(s for s in json.loads((ledger.AREA/'source-inventory.json').read_text())['sources']if s['id']==packet['sourceId'])
    original=Path(inventory['cachePath'])
    if ledger.sha(original.read_bytes())!=peer['sourceSha256']:raise ValueError('Wrong original for scoped source fields')
    pdf=fitz.open(original);rows=[]
    for row in packet['rows']:
        image=row['actual1200Source'];clip=row['actualPdfPointClip']
        actual=pdf[row['physicalPage']-1].get_pixmap(dpi=1200,alpha=False,clip=fitz.Rect(clip))
        supplied=fitz.Pixmap(str(ledger.ROOT/image['path']))
        if ((actual.width,actual.height,actual.n,actual.samples)!=(supplied.width,supplied.height,supplied.n,supplied.samples)
                or ledger.sha((ledger.ROOT/image['path']).read_bytes())!=image['sha256']):
            raise ValueError('Scoped source1200 image differs from actual original pixels')
        rows.append({**{k:row[k]for k in ['sequence','field','physicalPage','sourceRowOnPage','originalFullRowCropSha256']},
                     'actualOriginalSourceField':image,'actualPdfPointClip':clip,'dpi':1200,'independentlyReproducedOriginalPixelsExact':True})
    value={'frozen':True,'version':2,'sourceId':packet['sourceId'],'sourceSha256':peer['sourceSha256'],'batch':peer['batch'],
           'sourcePeer':peer_reference,'sourceOnlyPacket':peer['input'],'rows':rows,
           'method':'Independent PyMuPDF1.26.6 RGB1200 original-source field reproduction; no OCR or value interpretation.'}
    if out.exists():raise ValueError('Never replace scoped source-field pixel proof')
    out.write_text(json.dumps(value,indent=2)+'\n');return ledger.pin(out)


def build_current_fields(peer_reference,overlay_reference,proof_reference):
    peer=ledger.pinned(peer_reference);packet=ledger.pinned(peer['input']);proof=ledger.pinned(proof_reference)
    overlay=ledger.pinned(overlay_reference);identity=(packet['sourceId'],peer['sourceSha256'],peer['batch'])
    if 'sourceId'in peer and peer['sourceId']!=identity[0]:raise ValueError('Scoped source peer header differs')
    for document in [packet,proof,overlay]:
        if tuple(document[k]for k in ['sourceId','sourceSha256','batch'])!=identity:raise ValueError('Scoped source-field identity differs')
    if (peer['frozen']is not True or any(peer['blindness'][k]is not False for k in
            ['authorScopedProposalsOpened','fullCandidateOpened','correspondingExpectedValuesSupplied'])
            or proof['sourcePeer']!=peer_reference or proof['sourceOnlyPacket']!=peer['input']or proof['version']!=2):
        raise ValueError('Scoped source-first order or actual-source proof changed')
    target,entries,pixels=keyed(packet['rows']),keyed(peer['rows']),keyed(proof['rows'])
    if set(target)!=set(entries)or set(target)!=set(pixels):raise ValueError('Scoped source-first field set incomplete')
    batch=ledger.pinned(overlay['frozenBatch']);original={r['sequence']:r for r in batch['rows']}
    reviewed={(r['physicalPage'],r['sourceRowOnPage']):r for r in overlay['overlays']};confirmed=[]
    for key,row in target.items():
        entry,pixel,base=entries[key],pixels[key],original[key[0]];locator=(row['physicalPage'],row['sourceRowOnPage']);field=key[1]
        if (locator!=(base['physicalPage'],base['sourceRowOnPage'])or field not in base['reviewTargetFields']
                or row['originalFullRowCropSha256']!=base['cropSha256']or entry['cropSha256']!=base['cropSha256']
                or (entry['physicalPage'],entry['sourceRowOnPage'])!=locator
                or (pixel['physicalPage'],pixel['sourceRowOnPage'])!=locator
                or pixel['originalFullRowCropSha256']!=base['cropSha256']
                or pixel['actualOriginalSourceField']!=row['actual1200Source']or pixel['actualPdfPointClip']!=row['actualPdfPointClip']
                or pixel['dpi']!=1200 or pixel['independentlyReproducedOriginalPixelsExact']is not True):
            raise ValueError('Scoped source-field original row/crop/pixel mapping differs')
        image=row['actual1200Source']
        if ledger.sha((ledger.ROOT/image['path']).read_bytes())!=image['sha256']:raise ValueError('Scoped original-source image changed')
        if field=='name':continue
        value=entry['value'];current=reviewed[locator]
        if (field not in ['remuneration','expenses']or type(value)is not int or value<=0 or entry['uncertain']is not False
                or not re.fullmatch(r'(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)',entry['literalPrinted'])
                or int(entry['literalPrinted'].replace(',',''))!=value
                or field not in current['reviewedFields']or current['resolvedRow'][ledger.FIELDS[field]]!=value
                or current['cropSha256']!=base['cropSha256']):
            raise ValueError('Scoped positive source money differs from literal first reading/effective overlay')
        confirmed.append({'sourceId':identity[0],'sourceSha256':identity[1],'physicalPage':locator[0],'sourceRowOnPage':locator[1],
                          'field':field,'confirmedValue':value,'effectiveAuthorOverlay':overlay_reference,'peerComparison':peer_reference,
                          'freshSourceImage':image,'imageFirstTranscript':peer_reference})
    if not confirmed:raise ValueError('Scoped source-first peer has no positive monetary fields')
    return {'frozen':True,'adapter':'direct-scoped-source-peer-v2','peerInputs':[peer_reference,peer['input'],proof_reference],
            'pixelProof':proof_reference,'confirmations':confirmed,'completeFrozenSourcePeerFields':len(target),
            'confirmedMonetaryFields':len(confirmed),'originalAuthorFirstReadingAgreementNotAsserted':True,
            'scope':'Exact positive source-money fields only; unrelated source names/qualifications remain with their own reviews.'}
