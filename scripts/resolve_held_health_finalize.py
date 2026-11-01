#!/usr/bin/env python3
"""Reproduce a complete PHSA cohort from frozen OCR evidence and image reviews.

This never imports a partial page or unresolved OCR guess. Raw OCR, source pixels,
review batches and manual overlays remain separate immutable inputs.
"""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

import resolve_held_health_audit as audit
import resolve_held_health_overlays as overlay_replay
import resolve_held_health_name_amendments as name_amendments
from resolve_held_health_ocr import name_comparison

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/held-resolution-health'
AUDIT=ROOT/'research/salaries/held-resolution-2026-11-01/health'
FIDELITY=ROOT/'research/salaries/held-resolution-2026-11-01/reviews/independent-phsa-render-source-fidelity.json'
FIDELITY_SHA='e69e88ba02b685b298c8c44b028008eb7d880477d9bdf3ce2f8a97ce9d655eb8'
SUPPLEMENTAL=AUDIT/'supplemental-name-amendment-ledger.json'
SOURCE_ID='held-resolution-phsa-2024-25-employees'
SCHEMA=['employerSlug','name','position','remuneration','expenses','pdfPage']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()


def write_or_check(path,raw,check):
    if check:
        if path.read_bytes()!=raw:
            raise ValueError('Frozen output differs: '+str(path))
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)


def run(check=False,status='held-for-peer-review'):
    summary=audit.run(offline=True)
    if not summary['eligibleForRootWholeCohortReview']:
        raise ValueError('Complete original/page/field review has not closed; no partial import emitted')
    if not SUPPLEMENTAL.exists():
        raise ValueError('The confirmed shared-engine name blind spot still needs its supplemental source-review ledger')
    supplemental=name_amendments.aggregate(check=True)
    amendments={(r['physicalPage'],r['sourceRowOnPage']):r for r in supplemental['amendments']}
    if sha(FIDELITY.read_bytes())!=FIDELITY_SHA:
        raise ValueError('Independent actual-PDF source fidelity receipt changed')
    fidelity=json.loads(FIDELITY.read_text())
    if [fidelity['actualPdfRendersChecked'],fidelity['namedRowsCompared'],fidelity['fieldRegionsCompared'],
        fidelity['unmatchedFieldRegions'],fidelity['independentRasterRowBoundaryExceptions']]!=[284,13906,41718,0,0]:
        raise ValueError('Independent painted-source/row-boundary audit is incomplete')
    overlays={};overlay_ledger=[];review_inputs={}
    for p in sorted(AUDIT.glob('manual-overlay-*.json')):
        e=json.loads(p.read_text())
        recomputed=overlay_replay.build([(ROOT/i['path'],i['sha256']) for i in e['reviewInputs']])
        if (json.dumps(recomputed,ensure_ascii=False,indent=2)+'\n').encode()!=p.read_bytes():
            raise ValueError('Immutable overlay does not exactly replay the reviewer values')
        overlay_ledger.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'rows':e['resolvedRows']})
        for source in e['reviewInputs']:
            rp=ROOT/source['path']
            if sha(rp.read_bytes())!=source['sha256']:
                raise ValueError('Original-image reviewer receipt changed')
            review_inputs[source['path']]=source['sha256']
        for r in e['overlays']:
            key=(r['physicalPage'],r['sourceRowOnPage'])
            if key in overlays:
                raise ValueError('Overlapping original-image resolutions')
            overlays[key]=r
    rows=[];proof=[];page_ledger=[];agreement=collections.Counter();image_fields=collections.Counter()
    for path in sorted((OUT/'evidence').glob('phsa-fy2024-25-ocr-p*.json.gzip')):
        e=json.loads(gzip.decompress(path.read_bytes()));pn=e['physicalPage'];page_sha=sha(path.read_bytes())
        page_ledger.append({'physicalPage':pn,'file':'evidence/'+path.name,'sha256':page_sha,
                            'rows':len(e['rowEvidence']),'imageSha256':e['imageSha256']})
        for r in e['rowEvidence']:
            key=(pn,r['sourceRowOnPage']);overlay=overlays.get(key);row=list(r['candidateRow'])
            if r['conflicts'] and overlay is None:
                raise ValueError('Unresolved original-image field')
            if overlay:
                if overlay['rawCandidateRow']!=row or overlay['rawPageEvidenceSha256']!=page_sha:
                    raise ValueError('Image review does not bind this raw original row')
                row=overlay['resolvedRow'];image_fields.update(overlay['reviewedFields'])
            amendment=amendments.get(key)
            if amendment:
                if row!=amendment['beforeOrdinaryResolvedRow'] or amendment['changedColumns']!=[1]:
                    raise ValueError('Pinned supplemental name does not match the source-derived row')
                if any(row[i]!=amendment['afterSupplementalRow'][i] for i in [0,2,3,4,5]):
                    raise ValueError('Supplemental name changed money or row identity')
                row=amendment['afterSupplementalRow']
            if row[0]!='provincial-health-services-authority' or row[2] is not None or row[5]!=pn:
                raise ValueError('Reporting entity/title/page scope changed')
            if type(row[3]) not in (int,float) or row[3]<=75000:
                raise ValueError('Unparsed or inconsistent remuneration requires explicit source review')
            if row[4] is not None and type(row[4]) not in (int,float):
                raise ValueError('Expense field is unparsed')
            rapid=r['rapidocr'];tess=r['tesseract']
            names_match=bool(rapid) and name_comparison(rapid['name'])==name_comparison(tess['name'])
            pay_match=r['payToken']['kind']=='number' and r['rapidPayToken']['kind']=='number' and r['payToken']['value']==r['rapidPayToken']['value']
            expense_match=r['expenseToken']['kind']=='number' and r['rapidExpenseToken']['kind']=='number' and r['expenseToken']['value']==r['rapidExpenseToken']['value']
            agreement.update({'name':int(names_match),'remuneration':int(pay_match),'numericExpenses':int(expense_match)})
            proof.append({'row':row,'sourceRowOnPage':key[1],'rawPageEvidenceFile':'evidence/'+path.name,
                          'rawPageEvidenceSha256':page_sha,'sourceImageSha256':e['imageSha256'],
                          'originalEngineFieldAgreement':{'name':names_match,'remuneration':pay_match,'numericExpenses':expense_match},
                          'explicitDashSourceImage':r['expenseOriginalImage'] if r['expenseOriginalImage']['isExplicitDash'] else None,
                          'originalRawConflicts':r['conflicts'],'originalImageReview':overlay,
                          'supplementalSourceNameAmendment':amendment})
            rows.append(row)
    if len(rows)!=13906 or [p['physicalPage'] for p in page_ledger]!=list(range(1,285)):
        raise ValueError('Complete original employee schedule is missing rows or pages')
    if len(overlays)!=3157:
        raise ValueError('Every independently flagged row needs exactly one image resolution')
    data=gzip.compress(encoded(rows),mtime=0);filename='phsa-2024-25-employees.json.gzip'
    provenance={'sourceSha256':audit.SOURCE_SHA,'rowSchema':SCHEMA,'rows':proof,
                'rawPageEvidence':page_ledger,'immutableImageReviewOverlays':overlay_ledger,
                'independentReviewerInputs':[{'path':p,'sha256':h} for p,h in sorted(review_inputs.items())],
                'supplementalNameAmendmentLedger':{'path':str(SUPPLEMENTAL.relative_to(ROOT)),
                                                   'sha256':sha(SUPPLEMENTAL.read_bytes()),'ledger':supplemental},
                'actualPdfFidelityReceipt':{'path':str(FIDELITY.relative_to(ROOT)),'sha256':FIDELITY_SHA}}
    provenance_data=gzip.compress(encoded(provenance),mtime=0);provenance_file='evidence/phsa-2024-25-complete-row-provenance.json.gzip'
    total_pay=sum(r[3] for r in rows);total_expense=sum(r[4] for r in rows if r[4] is not None)
    residuals=[total_pay-1713046476,total_expense-25171641]
    notes=[
        'Complete original alphabetical named employee schedule: remuneration exceeding $75,000 for the year ended March 31, 2025, with expenses paid during that period. This is a threshold disclosure, not a workforce census.',
        'Remuneration is the published original remuneration field, not an annual base-salary rate. The original does not itemize all compensation components; no missing component is inferred as zero and nothing is annualized.',
        'Expenses may be direct employee reimbursements or third-party supplier payments. Original expense dashes remain null; explicit zero and negative values are preserved literally. Known-value expense sums do not turn unknown cells into zero.',
        'No job titles are published by this schedule, so all positions are null. The reporting entity is exactly the printed Provincial Health Services Authority; no unit-specific staff reassignment or cross-year identity inference is made.',
        'Two independent OCR engines compared every original page and row. Every disagreement or conservative confidence flag was separately resolved from original images with immutable reviewer receipts. Exact recurring dash pixels were independently checked against all 18 manually reviewed first-page examples; detector absence alone never determines a dash.',
        'An independent audit rendered all 284 actual PDF pages and checked every name/pay/expense region plus all row boundaries against the source-backed tile images. Pixel antialiasing differences are not claimed to be pixel identity. No semantic source-view exception was established.',
        'Names retain source letters, diacritics, initials and word boundaries. Only benign whitespace around existing commas/line wraps is normalized for comparison; all raw OCR and literal original-image readings remain in provenance.',
        'A documented shared-engine capital-I/lowercase-l ambiguity triggered a bounded 47-row additional actual-PDF name audit. Two independent image readers confirmed 44 exact name-only corrections and three legitimate lowercase names unchanged. Root-adopted supplemental ledgers apply only those individual source-derived names; no general casing or identity rule is used.',
        'Officially published standalone scanned employee disclosure. It is unsigned and does not separately establish board approval or adoption. The printed salary year is consistent across every page.',
        'The final original page has 39 named rows and a separately ruled Total. No named-row count or below-threshold aggregate is printed there. The full 13,906-row count is independently established from the original row boundaries, not inferred from financial totals.',
        'No compiled partition is replaced or re-dated. The registered same-period PHSA source is a separate board schedule; this recovery adds employee observations only.'
    ]
    validation={'independentOcrEngines':['Tesseract 5.5.0 eng, original 300-dpi images, psm 6',
                                        'RapidOCR ONNX Runtime 1.4.4 / PaddleOCR PP-OCRv4, independent neural detection and recognition'],
                'independentlyComparedRows':len(rows),'completeEmployeeSchedule':True,
                'physicalPdfPages':list(range(1,285)),
                'sourceRowsPerPhysicalPage':[[p['physicalPage'],p['rows']] for p in page_ledger],
                'printedNamedRowCount':None,'independentActualRasterRowBoundariesChecked':13906,
                'originalEngineAgreementFieldCounts':dict(agreement),
                'imageReviewedConflictRows':3157,'imageReviewedTargetFieldCounts':dict(image_fields),
                'supplementalNameAuditCases':47,'supplementalNameOnlyCorrections':44,
                'supplementalLiteralLowercaseNamesPreserved':3,
                'supplementalNameAmendmentLedger':str(SUPPLEMENTAL.relative_to(ROOT)),
                'supplementalNameAmendmentLedgerSha256':sha(SUPPLEMENTAL.read_bytes()),
                'remainingUnresolvedRows':0,'remainingUncertainDateTitles':0,'rowBoundaryExceptions':0,
                'actualPaintedSourceFieldRegionsChecked':41718,'actualPaintedSourceFieldExceptions':0,
                'missingExpenseRows':sum(r[4] is None for r in rows),
                'explicitZeroExpenseRows':sum(r[4]==0 for r in rows),
                'negativeExpenseRows':sum(r[4] is not None and r[4]<0 for r in rows),
                'duplicateRowsPreserved':sum(n-1 for n in collections.Counter(tuple(r[:5]) for r in rows).values() if n>1),
                'printedRemunerationControl':1713046476,'printedExpenseControl':25171641,
                'remunerationResidual':residuals[0],'knownExpenseResidual':residuals[1],
                'sourceControlScope':'Complete original named employee schedule; distinct final Total row, no final-page below-threshold aggregate.',
                'rowProvenanceFile':provenance_file,'rowProvenanceSha256':sha(provenance_data),
                'completeRawPageManifest':'../held-resolution-2026-11-01/health/complete-raw-page-manifest.json',
                'completeRawPageManifestSha256':sha((AUDIT/'complete-raw-page-manifest.json').read_bytes()),
                'independentPaintedSourceFidelityReceipt':str(FIDELITY.relative_to(ROOT)),
                'independentPaintedSourceFidelitySha256':FIDELITY_SHA,
                'renderReviewCoverage':'Every source page/field region and row boundary geometrically compared to actual PDF rendering; all 3,157 conflict rows independently image reviewed. Human review does not claim manual transcription of every otherwise-agreeing row.'}
    source={'id':SOURCE_ID,'employerSlug':'provincial-health-services-authority',
            'employerName':'Provincial Health Services Authority','sector':'Health authorities',
            'title':'Provincial Health Services Authority employee remuneration and expenses 2024/25',
            'year':'2024/25','periodType':'fiscal','periodStart':'2024-04-01','periodEnd':'2025-03-31',
            'sourceUrl':'https://www.phsa.ca/about-site/Documents/FY2025-Employee-Salary-and-Expenses-exceeding-75000.pdf',
            'sourceIndexUrl':'https://www.phsa.ca/about/accountability/budget-financials',
            'sha256':audit.SOURCE_SHA,'pdfBytes':54160556,'sourceKind':'official',
            'file':filename,'dataSha256':sha(data),'rowCount':len(rows),'totalRemuneration':total_pay,
            'totalExpenses':total_expense,'totalDisclosedExpenses':total_expense,
            'status':status,'verifiedOn':'2026-11-01','category':'employee-remuneration','scope':'employee-remuneration',
            'threshold':75000,'thresholdComparison':'>','currency':'CAD','nameDisclosure':'named',
            'completeEmployeeSchedule':True,'publicationStatus':'official-published-unsigned-standalone-schedule',
            'notes':notes,'validation':validation}
    if any(residuals):
        source['publicWarning']=f'After complete independent row and original-image verification, displayed employee remuneration minus printed schedule Total = {residuals[0]:+d} CAD; known disclosed expenses minus printed schedule Total = {residuals[1]:+d} CAD. All published individual cells remain literal; the cause is unconfirmed and no balancing adjustment is made. Expense dashes remain unknown.'
    manifest={'version':1,'rowSchema':SCHEMA,'sources':[source]}
    write_or_check(OUT/filename,data,check)
    write_or_check(OUT/provenance_file,provenance_data,check)
    write_or_check(OUT/'sources.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(),check)
    print(json.dumps({'sourceId':SOURCE_ID,'status':status,'rows':len(rows),'sums':[total_pay,total_expense],
                      'residuals':residuals,'dataSha256':sha(data),'provenanceSha256':sha(provenance_data)}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true')
    p.add_argument('--status',choices=['held-for-peer-review','verified'],default='held-for-peer-review')
    a=p.parse_args();run(a.check,a.status)
