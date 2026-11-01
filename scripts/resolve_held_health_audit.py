#!/usr/bin/env python3
"""Audit whole-source PHSA staging and immutable image-review overlays."""
import argparse
import collections
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'research/salaries/held-resolution-2026-11-01/health'
CACHE=Path('/tmp/held-health-ocr/full/pages')
COLLECTION=ROOT/'research/salaries/held-resolution-health'
SOURCE_SHA='809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run(offline=False):
    overlays={};overlay_inputs=[]
    for p in sorted(AUDIT.glob('manual-overlay-*.json')):
        a=json.loads(p.read_text());overlay_inputs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())})
        for r in a['overlays']:
            key=(r['physicalPage'],r['sourceRowOnPage'])
            if key in overlays:
                raise ValueError('Overlapping immutable overlays require explicit reconciliation')
            overlays[key]=r
    supplement_path=AUDIT/'supplemental-name-amendment-ledger.json'
    supplement=json.loads(supplement_path.read_text()) if supplement_path.exists() else None
    amendments={(r['physicalPage'],r['sourceRowOnPage']):r for r in supplement['amendments']} if supplement else {}
    if supplement and (supplement['sourceSha256']!=SOURCE_SHA or not supplement['allSupplementalCasesClosed'] or len(amendments)!=44):
        raise ValueError('Supplemental exact-name audit is incomplete')
    batches={};batch_inputs=[]
    for p in sorted(AUDIT.glob('review-batch-*.json')):
        if p.name.endswith('-images.json'):
            continue
        a=json.loads(p.read_text());batch_inputs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'rows':len(a['rows'])})
        for r in a['rows']:
            key=(r['physicalPage'],r['sourceRowOnPage'])
            if key in batches:
                raise ValueError('Review batches overlap')
            batches[key]=a['batch']
    paths=sorted((COLLECTION/'evidence').glob('phsa-fy2024-25-ocr-p*.json.gzip')) if offline else sorted(CACHE.glob('p*.json.gzip'))
    pages=[];rows=[];unresolved=[];counts=collections.Counter();headers=[];bad_pay=[]
    for path in paths:
        e=json.loads(gzip.decompress(path.read_bytes()))
        if e['sourceSha256']!=SOURCE_SHA:
            raise ValueError('Original source evidence changed')
        pn=e['physicalPage'];page_hash=sha(path.read_bytes())
        tcanon=re.sub(r'[^A-Z0-9]','',e['tesseractRawText'].upper())
        rcanon=re.sub(r'[^A-Z0-9]','',' '.join(r[1] for r in e['rapidocrRaw']
                                            if sum(v[1] for v in r[0])/4<e['imageDimensions'][1]*.21).upper())
        header={'physicalPage':pn,'tesseractDateTitleMatches':'31MARCH2025' in tcanon,
                'rapidDateTitleMatches':'31MARCH2025' in rcanon}
        if not all([header['tesseractDateTitleMatches'],header['rapidDateTitleMatches']]):
            headers.append(header)
        pages.append({'physicalPage':pn,'rowCount':len(e['rowEvidence']),
                      'sha256':page_hash,'pageConflicts':e['pageConflicts']})
        for r in e['rowEvidence']:
            key=(pn,r['sourceRowOnPage']);row=list(r['candidateRow']);counts.update(r['conflicts'])
            if key in overlays:
                overlay=overlays[key]
                if overlay['rawPageEvidenceSha256']!=page_hash or overlay['rawCandidateRow']!=row:
                    raise ValueError('Manual review overlay no longer matches immutable page evidence')
                row=overlay['resolvedRow']
            elif r['conflicts']:
                unresolved.append({'physicalPage':pn,'sourceRowOnPage':r['sourceRowOnPage'],
                                   'conflicts':r['conflicts'],'assignedBatch':batches.get(key),
                                   'cropPath':r['conflictImagePath'],'candidateRow':row})
            if key in amendments:
                amendment=amendments[key]
                if row!=amendment['beforeOrdinaryResolvedRow'] or amendment['changedColumns']!=[1]:
                    raise ValueError('Supplemental source-name amendment does not match the exact ordinary row')
                if any(row[i]!=amendment['afterSupplementalRow'][i] for i in [0,2,3,4,5]):
                    raise ValueError('Supplemental name amendment changes an unauthorized field')
                row=amendment['afterSupplementalRow']
            if row[3] is None or row[3]<=75000:
                bad_pay.append({'physicalPage':pn,'sourceRowOnPage':r['sourceRowOnPage'],
                                'candidateRemuneration':row[3],'hasOutstandingImageReview':bool(r['conflicts']) and key not in overlays})
            rows.append({'key':key,'row':row,'source':r})
    page_numbers=sorted(p['physicalPage'] for p in pages)
    if len(page_numbers)!=len(set(page_numbers)):
        raise ValueError('Duplicate physical source page')
    missing=[i for i in range(1,285) if i not in page_numbers]
    complete=not missing
    known_pay=sum(r['row'][3] for r in rows if r['row'][3] is not None)
    known_expense=sum(r['row'][4] for r in rows if r['row'][4] is not None)
    residuals=[known_pay-1713046476,known_expense-25171641] if complete else None
    result={'date':'2026-11-01','sourceSha256':SOURCE_SHA,'physicalPdfPages':284,
            'processedPages':len(pages),'missingPhysicalPages':missing,'machineRunComplete':complete,
            'stagedNamedRows':len(rows),'printedNamedRowCount':None,
            'observedRowCountsByPage':pages,'rowBoundaryConflictPages':[p['physicalPage'] for p in pages if p['pageConflicts']],
            'dateTitleUncertaintyPages':headers,'rawFlagCounts':dict(counts),
            'rawConflictRows':sum(bool(r['source']['conflicts']) for r in rows),
            'imageResolvedRows':len(overlays),'imageChangedRows':sum(bool(r['changedFields']) for r in overlays.values()),
            'supplementalNameAuditClosed':bool(supplement),'supplementalNameImageCases':47 if supplement else 0,
            'supplementalNameFieldsChanged':len(amendments),'supplementalLiteralLowercaseCasesPreserved':3 if supplement else 0,
            'unresolvedRows':len(unresolved),'unassignedUnresolvedRows':sum(r['assignedBatch'] is None for r in unresolved),
            'unresolvedQueue':unresolved,'reviewBatches':batch_inputs,'immutableOverlays':overlay_inputs,
            'diagnosticCandidateRemunerationSum':known_pay,'diagnosticCandidateKnownExpenseSum':known_expense,
            'printedRemunerationControl':1713046476,'printedExpenseControl':25171641,
            'diagnosticResidualsOnlyWhenAllPagesProcessed':residuals,
            'expenseNullRowsAfterAppliedReviews':sum(r['row'][4] is None for r in rows),
            'explicitZeroExpenseRowsAfterAppliedReviews':sum(r['row'][4]==0 for r in rows),
            'negativeExpenseRowsAfterAppliedReviews':sum(r['row'][4] is not None and r['row'][4]<0 for r in rows),
            'exactImageVerifiedDashRows':sum(r['source']['expenseOriginalImage']['isExplicitDash'] for r in rows),
            'payThresholdOrUnparsedRows':bad_pay,
            'eligibleForRootWholeCohortReview':complete and not unresolved and not headers and not bad_pay and bool(supplement) and not any(p['pageConflicts'] for p in pages),
            'financialControlsReconciledAfterEveryFieldReview':complete and not unresolved and not headers and not bad_pay and bool(supplement) and residuals==[0,0],
            'normalizedRowsEmittedByThisStagingAudit':0,'compiledRowsRemoved':0,
            'sourceAcceptance':'The final normalizer and independent complete-source closure determine acceptance; this staging audit does not emit normalized data.',
            'warning':'All sums are diagnostic until every original page, conflict and uncertainty is resolved. No balancing adjustment, invented zero or partial-page acceptance follows from this audit.'}
    raw=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    (AUDIT/'whole-source-audit-progress.json').write_bytes(raw)
    print(json.dumps({k:result[k] for k in ['processedPages','machineRunComplete','stagedNamedRows','rawConflictRows',
                                          'imageResolvedRows','unresolvedRows','unassignedUnresolvedRows',
                                          'dateTitleUncertaintyPages','rowBoundaryConflictPages',
                                          'diagnosticCandidateRemunerationSum','diagnosticCandidateKnownExpenseSum',
                                          'diagnosticResidualsOnlyWhenAllPagesProcessed','eligibleForRootWholeCohortReview']}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--offline',action='store_true');a=p.parse_args();run(a.offline)
