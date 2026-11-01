#!/usr/bin/env python3
"""Source-derived supplemental name amendments; never a casing substitution rule."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'research/salaries/held-resolution-2026-11-01/health'
REVIEWS=ROOT/'research/salaries/held-resolution-2026-11-01/reviews'
SOURCE_SHA='809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c'
CONFIRM_SHA='841832b05cd047c83a6279c1879f648de49765258cda0f35ef8b6a63e60a8502'
ADOPTION_SHA='3fff2c70fddd00b056bae6c9ee343746b87c8a35aace1634243f1a28e93aa1e6'
PRIMARY_SHA='647b68298b35017d822332aa307f2b478528c561010032918ffa131973630b8b'
SECONDARY_SHA='4fee514b22aa3b6df19b4e41d0b5985e79b11e051dd3161b42232b0a9cee519d'
SECOND_ADOPTION_SHA='4cd76e4422ef03a1c0454c7295cadb68d3bb80ea544ae0f9685ce76c88bc7455'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path,digest):
    if sha(path.read_bytes())!=digest:
        raise ValueError('Source-derived amendment input changed')
    return json.loads(path.read_text())


def output(result,filename,check):
    out=AUDIT/filename;raw=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if check:
        if out.read_bytes()!=raw:
            raise ValueError('Frozen supplemental name ledger differs')
    else:
        if out.exists():
            raise ValueError('Use a new amendment filename rather than rewriting a frozen ledger')
        out.write_bytes(raw)
    print(json.dumps({'path':str(out.relative_to(ROOT)),'sha256':sha(raw)}))
    return result


def muir(check=False):
    cp=REVIEWS/'independent-phsa-muir-rendered-name-confirmation.json'
    ap=REVIEWS/'root-phsa-muir-name-adoption.json'
    confirmation=pinned(cp,CONFIRM_SHA);adoption=pinned(ap,ADOPTION_SHA)
    if confirmation['sourceSha256']!=SOURCE_SHA or adoption['sourceSha256']!=SOURCE_SHA:
        raise ValueError('Wrong original source')
    p=ROOT/'research/salaries/held-resolution-health/evidence/phsa-fy2024-25-ocr-p180.json.gzip'
    if sha(p.read_bytes())!=confirmation['rawPageEvidenceSha256']:
        raise ValueError('Original raw row changed')
    e=json.loads(gzip.decompress(p.read_bytes()));raw=e['rowEvidence'][7]['candidateRow']
    if raw!=confirmation['rawCandidateRow']:
        raise ValueError('Source row identity differs')
    op=AUDIT/'manual-overlay-008.json';ordinary=json.loads(op.read_text())
    prior=next(r for r in ordinary['overlays'] if (r['physicalPage'],r['sourceRowOnPage'])==(180,8))
    if prior['reviewedFields']!=['remuneration']:
        raise ValueError('Do not silently broaden the earlier pay-only review')
    before=prior['resolvedRow'];after=list(before);after[1]=adoption['afterName']
    if before[1]!=adoption['beforeName'] or after!=confirmation['proposedSourceCorrectedRow']:
        raise ValueError('Exact authorized name amendment differs')
    if any(before[i]!=after[i] for i in [0,2,3,4,5]):
        raise ValueError('Only the source name may change')
    result={'frozen':True,'date':'2026-11-01','sourceSha256':SOURCE_SHA,
            'kind':'root-adopted-exact-name-only-supplement','physicalPage':180,'sourceRowOnPage':8,
            'beforeOrdinaryResolvedRow':before,'afterSupplementalRow':after,
            'changedColumns':[1],'changedFields':['name'],'rowMultiplicityUnchanged':True,
            'originalRawCandidateRow':raw,'rawPageEvidenceSha256':sha(p.read_bytes()),
            'priorOrdinaryOverlayPath':str(op.relative_to(ROOT)),'priorOrdinaryOverlaySha256':sha(op.read_bytes()),
            'priorOrdinaryReviewedFields':prior['reviewedFields'],
            'sourceConfirmation':{'path':str(cp.relative_to(ROOT)),'sha256':CONFIRM_SHA},
            'rootAdoption':{'path':str(ap.relative_to(ROOT)),'sha256':ADOPTION_SHA},
            'actualPdfContextImages':confirmation['actualPdfContextImages'],
            'notAGeneralCasingRule':True,'oldRawOcrBatchAndPayReviewUnchanged':True,
            'scope':'One explicitly image-confirmed source name field applied only after the ordinary image-review overlays; every money/null/title/employer/page field and multiplicity remain exact.'}
    # Preserve the already frozen first ledger's exact serialization/schema.
    out=AUDIT/'supplemental-name-amendment-001-muir.json';rawout=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if check:
        if out.read_bytes()!=rawout:raise ValueError('Frozen supplemental Muir amendment differs')
    else:
        if out.exists():raise ValueError('Use a new amendment filename')
        out.write_bytes(rawout)
    print(json.dumps({'path':str(out.relative_to(ROOT)),'sha256':sha(rawout),'changedFields':['name']}))
    return result


def supplemental(check=False):
    pp=REVIEWS/'independent-phsa-supplemental-case-proposals.json'
    sp=REVIEWS/'independent-phsa-supplemental-name-education-confirmations.json'
    ap=REVIEWS/'root-phsa-supplemental-name-adoption.json'
    primary=pinned(pp,PRIMARY_SHA);secondary=pinned(sp,SECONDARY_SHA);adoption=pinned(ap,SECOND_ADOPTION_SHA)
    if any(x['sourceSha256']!=SOURCE_SHA for x in [primary,secondary,adoption]):
        raise ValueError('Wrong original source')
    pmap={(r['physicalPage'],r['sourceRowOnPage']):r for r in primary['changes']}
    smap={(r['physicalPage'],r['sourceRowOnPage']):r for r in secondary['changes']}
    if [len(primary['changes']),len(secondary['changes']),len(adoption['cases'])]!=[44,43,43]:
        raise ValueError('Supplemental review/adoption coverage differs')
    entries=[]
    for r in adoption['cases']:
        key=(r['physicalPage'],r['sourceRowOnPage'])
        if key==(180,8):raise ValueError('Muir must not be applied twice')
        a=pmap[key];b=smap[key]
        if r['beforeRow']!=a['afterOrdinaryOverlays'] or r['beforeRow']!=b['beforeRow']:
            raise ValueError('Before row differs from independent source reviews')
        if r['afterRow']!=a['proposedCorrectedRow'] or r['afterRow']!=b['confirmedRow']:
            raise ValueError('Root-adopted literal source name differs')
        if r['authorizedChangedColumns']!=[1] or a['changedColumns']!=[1] or b['changedColumns']!=[1]:
            raise ValueError('Only the separately reviewed source name may change')
        if any(r['beforeRow'][i]!=r['afterRow'][i] for i in [0,2,3,4,5]):
            raise ValueError('Money/title/entity/page must remain unchanged')
        p=ROOT/'research/salaries/held-resolution-health/evidence'/f'phsa-fy2024-25-ocr-p{key[0]:03d}.json.gzip'
        if sha(p.read_bytes())!=r['rawPageEvidenceSha256'] or r['rawPageEvidenceSha256']!=b['rawPageEvidenceSha256']:
            raise ValueError('Supplemental source row evidence changed')
        e=json.loads(gzip.decompress(p.read_bytes()));raw=e['rowEvidence'][key[1]-1]['candidateRow']
        if raw!=r['beforeRow'] or raw!=a['rawCandidateRow'] or e['rowEvidence'][key[1]-1]['conflicts']:
            raise ValueError('This exact unflagged raw row was not the reviewed source case')
        if r['actualCropSha256']!=a['actualCropSha256'] or r['actualCropSha256']!=b['actualCropSha256']:
            raise ValueError('Independent actual source crops differ')
        entries.append({'physicalPage':key[0],'sourceRowOnPage':key[1],
                        'beforeOrdinaryResolvedRow':r['beforeRow'],'afterSupplementalRow':r['afterRow'],
                        'changedColumns':[1],'changedFields':['name'],'rowMultiplicityUnchanged':True,
                        'rawPageEvidenceSha256':r['rawPageEvidenceSha256'],'actualCropSha256':r['actualCropSha256'],
                        'sourcePrimaryReviewSha256':PRIMARY_SHA,'sourceIndependentReviewSha256':SECONDARY_SHA,
                        'rootAdoptionSha256':SECOND_ADOPTION_SHA})
    unchanged=[]
    for r in secondary['unchanged']:
        if r['beforeRow']!=r['confirmedRow'] or r['changedColumns']:
            raise ValueError('Legitimate lowercase name must remain unchanged')
        if not any((x['physicalPage'],x['sourceRowOnPage'],x['name'])==(r['physicalPage'],r['sourceRowOnPage'],r['literalImageName']) for x in adoption['unchangedLiteralCases']):
            raise ValueError('Root unchanged-case adoption differs')
        unchanged.append(r)
    if len(unchanged)!=3:raise ValueError('All three unchanged source names must be retained')
    result={'frozen':True,'date':'2026-11-01','sourceSha256':SOURCE_SHA,
            'kind':'root-adopted-source-name-only-supplement-002','changedRows':43,
            'changedColumns':[1],'muirExcludedAndAppliedSeparately':True,
            'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':d} for p,d in [(pp,PRIMARY_SHA),(sp,SECONDARY_SHA),(ap,SECOND_ADOPTION_SHA)]],
            'amendments':entries,'confirmedUnchangedLiteralLowercaseNames':unchanged,
            'allMoneyPositionsEmployersPagesAndMultiplicityPreserved':True,
            'notAGeneralCasingRule':True,'oldRawOcrBatchesAndOrdinaryOverlaysUnchanged':True}
    return output(result,'supplemental-name-amendment-002-additional.json',check)


def aggregate(check=False):
    first=muir(check=True);second=supplemental(check=True)
    fp=AUDIT/'supplemental-name-amendment-001-muir.json';sp=AUDIT/'supplemental-name-amendment-002-additional.json'
    muir_entry={k:first[k] for k in ['physicalPage','sourceRowOnPage','beforeOrdinaryResolvedRow',
                                     'afterSupplementalRow','changedColumns','changedFields','rowMultiplicityUnchanged','rawPageEvidenceSha256']}
    muir_entry['sourceConfirmation']=first['sourceConfirmation'];muir_entry['rootAdoption']=first['rootAdoption']
    entries=[muir_entry]+second['amendments']
    if len(entries)!=44 or len({(r['physicalPage'],r['sourceRowOnPage']) for r in entries})!=44:
        raise ValueError('Exact supplemental name cases must apply once, including Muir once')
    result={'frozen':True,'date':'2026-11-01','sourceSha256':SOURCE_SHA,
            'kind':'root-adopted-exact-name-amendment-ledger','sourceImageAuditCases':47,
            'changedNameFields':44,'confirmedUnchangedLiteralCases':3,'allSupplementalCasesClosed':True,
            'inputLedgers':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in [fp,sp]],
            'amendments':entries,'confirmedUnchanged':second['confirmedUnchangedLiteralLowercaseNames'],
            'permittedChangedColumns':[1],'noAutomaticCasingRule':True,
            'moneyTitleEmployerPageRowCountAndMultiplicityUnchanged':True,
            'oldRawOcrBatchesAndOrdinaryOverlaysUnchanged':True}
    return output(result,'supplemental-name-amendment-ledger.json',check)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--muir',action='store_true');p.add_argument('--supplemental',action='store_true');p.add_argument('--aggregate',action='store_true');p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if a.aggregate:aggregate(a.check)
    elif a.supplemental:supplemental(a.check)
    elif a.muir:muir(a.check)
    else:
        raise ValueError('Specify a pinned source-derived amendment; no automatic casing mode exists')
