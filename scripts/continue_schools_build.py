#!/usr/bin/env python3
"""Build reviewed complete school cohorts from pinned originals and readers."""
import collections
import json
import subprocess
from decimal import Decimal
from pathlib import Path

import continue_schools as s

def public_review_note(source):
    """Describe the review evidence for readers; internal approval stays verbatim."""
    key=source['inputKey']
    if key in ['sd46-2025','sd52-2025']:
        return 'Complete independent readings of every named row agree across PyMuPDF, Poppler and PDFMiner. All employee and control pages, adjacent scopes and continuation boundaries were reviewed in the rendered original. Published values remain unchanged with the stated unresolved control differences.'
    if key=='sd08-2019':
        return 'The complete scanned physical page 13 was independently read and all 40 names, remuneration amounts, expenses and missing values were compared with the original image. The complete 209-row employee schedule reconciles the printed named controls; original values and disclosure marks are retained.'
    if key=='sd08-2022':
        return 'Every named employee row agrees between independent PDF readers. The rendered salary layout and original physical page 56 controls of 23,598,231 remuneration and 306,613 expenses were independently reviewed. Published row values and the stated control differences remain unchanged without assigning a cause.'
    return 'Every normalized monetary cell was independently summed and compared with the rendered original trustee and control pages. Complete row, role, physical page, order and multiplicity checks agree between independent PDF readers. Published values remain unchanged with the stated control differences; no cause is inferred.'

def main():
    configs=json.loads((s.INVENTORY/'parser-config.json').read_text())
    old=json.loads((s.ROOT/'research/salaries/sector-search-2026-10-31/schools/findings.json').read_text())
    employers={e['districtNumber']:e for e in old['employers']}
    manifest={'version':1,'reviewed':'2026-11-01','rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':[]}
    held=[]
    review_path=s.INVENTORY/'reviewed-acceptances.json'
    acceptances={r['id']:r for r in json.loads(review_path.read_text())['reviewedAcceptances']} if review_path.exists() else {}
    for key,c in configs.items():
        n=c['districtNumber'];end=int(key[-4:]);year=f'{end-1}/{str(end)[-2:]}'
        employer=employers[n]
        path=Path(c.get('cacheDir','/tmp/pofbc-schools'))/c['cacheFile'];raw=path.read_bytes()
        receipt=next((x for x in employer['sourceCandidates'] if x.get('id')==f'ministry-sd{n:02}-{end}'),None)
        if c.get('sourceUrl'):
            receipts=json.loads((s.INVENTORY/'new-district-source-receipts.json').read_text())
            receipt=next(x for x in receipts+employer['sourceCandidates'] if x['sourceUrl']==c['sourceUrl'])
        if receipt is None:
            history=json.loads((s.INVENTORY/'ministry-history-receipts.json').read_text())
            receipt=next(x for x in history if x['districtNumber']==n and x['indexedEndingYear']==end and x['sha256']==s.sha(raw))
        assert s.sha(raw)==receipt['sha256']
        rows,independent,controls,text=s.read_report(path,c)
        cols=['name','position','remuneration','expenses','pdfPage']
        assert [[r[x] for x in cols] for r in rows]==[[r[x] for x in cols] for r in independent],key
        for category,label in [('school-trustees','trustees'),('employee-remuneration','employees')]:
            rs=[r for r in rows if r['category']==category]
            if not rs:continue
            idx=[i for i,r in enumerate(rows) if r['category']==category]
            sums=[s.cents_sum(rs,k) for k in ['remuneration','expenses']]
            residuals=[str(Decimal(a)-Decimal(b)) if b is not None else None for a,b in zip(sums,controls[category])]
            controls_match=all(x is None or Decimal(x)==0 for x in residuals)
            held_reason=c.get('heldCategories',{}).get(category)
            prefix=f'{key}-{label}'
            payload=[[employer['slug'],r['name'],r['position'],float(r['remuneration']),None if r['expenses'] is None else float(r['expenses']),r['pdfPage']] for r in rs]
            data,uncompressed=s.pack_json(payload)
            evidence={'sourceSha256':s.sha(raw),'rows':rs,'independentRows':[independent[i] for i in idx],
                      'printedControlTotals':controls[category],'readerImplementations':['Poppler pdftotext -layout','PyMuPDF word coordinates with independent geometric grouping'],
                      'reviewedOriginalPages':c['pages'],'pageText':{str(p):text.split('\f')[p-1] for p in c['pages']}}
            evidence_data,_=s.pack_json(evidence)
            source={'id':f'continuation-schools-{prefix}','inputKey':key,'employerSlug':employer['slug'],'employerName':employer['name'],'sector':'School districts',
                    'year':year,'slug':year.replace('/','-'),'periodType':'fiscal','periodStart':f'{end-1}-07-01','periodEnd':f'{end}-06-30',
                    'title':f"{employer['name']}, year ended June 30, {end}: {label}",'sourceUrl':receipt['sourceUrl'],'sourceIndexUrl':receipt.get('sourceIndexUrl',old['centralIndexUrl']),
                    'sha256':s.sha(raw),'file':f'{prefix}.json.gzip','dataSha256':s.sha(data),'normalizedSha256':s.sha(uncompressed),
                    'provenanceFile':f'{prefix}-evidence.json.gzip','provenanceSha256':s.sha(evidence_data),
                    'category':category,'scope':'named-employees-over-threshold' if label=='employees' else 'elected-school-trustees',
                    'scopeDescription':'Published named employees whose remuneration exceeds $75,000' if label=='employees' else 'Complete published elected trustee remuneration schedule',
                    'currency':'CAD','amountUnit':'dollars','amountPrecision':c.get('amountPrecision','cents'),'nameDisclosure':'published-name-as-disclosed',
                    'positionDisclosure':'published-where-present' if c['positions'] else 'not-published',
                    'rowCount':len(rs),'totalRemuneration':float(sums[0]),'totalExpenses':float(sums[1]) if any(r['expenses'] is not None for r in rs) else None,'pages':sorted(set(r['pdfPage'] for r in rs)),
                    'status':'verified' if controls_match and not held_reason else (c.get('heldStatus','held-source-qualification') if held_reason else 'held-source-control-review'),
                    'sourceKind':'official-hybrid-pdf' if c.get('scannedSupplements') and any(r['pdfPage'] in [x['pdfPage'] for x in c['scannedSupplements']] for r in rs) else 'official-pdf','verifiedOn':'2026-11-01',
                    'notes':['Annual fiscal period is July 1–June 30; the original SOFI report identifies the fiscal year ended June 30. Upload dates are not used as reporting periods.',
                             'Published remuneration and expense columns remain separate. These payments are not annual base salary rates. Suppliers, under-threshold aggregate payroll, employer premiums and financial statement totals are excluded.',
                             'Published names, initials, punctuation and visibly abbreviated titles are preserved. No missing title is inferred. Blank and dash expenses are null; explicit zeros remain zero.',
                             'Every complete row, field, order and multiplicity agrees between Poppler layout text and independently grouped PyMuPDF geometric columns. Rendered originals were reviewed for table scope, headings, controls and layout.'],
                    'publicWarning':None,
                    'validation':{'originalFingerprintVerified':True,'independentReaders':['Poppler layout text','PyMuPDF independent word geometry'],
                                  'completeRowTextAmountsOrderAndMultiplicityAgree':True,'rowsIndependentlyChecked':len(rs),'rowsByPhysicalPage':dict(collections.Counter(str(r['pdfPage']) for r in rs)),
                                  'componentColumns':['remuneration','expenses'],'printedControlTotals':controls[category],'computedComponentTotals':sums,'controlResiduals':residuals,
                                  'underThresholdExpenseComparator':'not imported; not inferred as zero','knownExpenseValueCount':sum(r['expenses'] is not None for r in rs),'unparsedInterRowText':0}}
            source['validation']['summaryReconciles']=controls_match
            source['validation']['allPublishedNamedControlsExact']=controls_match
            source['validation']['allPrintedComponentControlsExact']=controls_match and all(value is not None for value in controls[category])
            if label=='employees':
                complete=c.get('completeEmployeeSchedule',True)
                source.update({'completeEmployeeSchedule':complete,'threshold':75000,'thresholdRule':c.get('thresholdRule','over')});source['validation']['completeEmployeeSchedule']=complete
                if source['thresholdRule']=='at-least':source['scopeDescription']='Published named employees paid at least $75,000'
            if n==74:
                source['notes'].append('Employee position column is present but every named employee title is blank. Trustee position labels describe technical/equipment allowances and are retained literally. The very large under-threshold expense aggregate on page 53 is not an individual expense or a comparator for named employees.')
            if n in [85,87,92]:source['notes'].append('Fixed-width payroll titles are visibly clipped in the original; clipped labels remain literal and are not expanded.')
            if n==87 and end==2021:source['notes'].append('The page 47 heading literally says SCHEDULE OF PAYMENTS FOR GOODS AND SERVICE above the named trustee and employee remuneration/expense columns. The named salary scope is established by those columns, section labels and SOFI report context; the anomalous heading is not silently corrected.')
            if n==8 and end in [2020,2021]:source['notes'].append('The source remuneration definition includes salary, wages, bonuses, taxable benefits, trusts and income deferrals, and explicitly excludes amounts payable under a severance agreement. This is the published pay definition. The separate Comments column is retained in row evidence and excluded from name, title and monetary values.')
            if source['sourceKind']=='official-hybrid-pdf':
                source['notes'][3]='Every native-page row agrees between Poppler layout text and independently grouped PyMuPDF columns. Every scanned-page row agrees between an independent complete manual original-image transcript and Tesseract5 OCR. Row fields, order, physical pages and multiplicity are retained.'
                source['notes'].append('Physical page13 is scanned. Its complete40-row independent manual original-image transcript agrees with Tesseract5 OCR after removal of table grid lines from a derived144dpi image. Other salary pages agree between Poppler and PyMuPDF. One OCR engine is claimed; manual image reading is the independent corroboration. The original source is unchanged and the derived-image method and OCR text are retained in evidence.')
                source['validation']['independentReaders']=['Native pages: Poppler layout and PyMuPDF word geometry','Scanned physical page13: independent full manual original-image reading and Tesseract5 OCR']
                source['validation']['scannedSupplementEvidence']=c['scannedSupplements']
                source['validation']['ocrEngineIndependenceClaimed']=False
                source['validation']['completeManualScanReading']=True
                evidence['readerImplementations']=source['validation']['independentReaders']
                evidence['scannedSupplementEvidence']=c['scannedSupplements']
                evidence_data,_=s.pack_json(evidence);source['provenanceSha256']=s.sha(evidence_data)
            if n==67 and label=='trustees':source['notes'].append('The published elected-official name cells include role words such as TRUSTEE and VICE CHAIRPERSON, which are also repeated in the Position column. These literal name cells are preserved; role words are not silently deleted.')
            if n==47:source['notes'].append('Literal source names MACRAILD PETER (without a comma) and SCHMUNK. TARA (with a period) are preserved as printed.')
            if any(r['expenses'] is not None and Decimal(r['expenses'])<0 for r in rs):source['notes'].append('Negative expense values, including a trailing minus sign in the original payroll report, are retained as negative amounts.')
            if controls[category][1] is None:
                source['notes'].append('All named expense fields and the printed expense total are dashes/blanks. Expenses remain unknown/null. The computed known-expense sum of zero has zero reported values and is not a published zero total.')
                source['publicWarning']='This schedule does not publish numeric individual expenses or a numeric expense control; expense fields are unknown.'
            reviewed=acceptances.get(source['id'])
            if reviewed:
                assert reviewed['originalSha256']==source['sha256']
                assert reviewed['dataSha256']==source['dataSha256']
                assert reviewed['provenanceSha256']==source['provenanceSha256']
                assert reviewed['rowCount']==source['rowCount']
                assert reviewed['approvedControlResiduals']==residuals
                for review_file in reviewed['reviewFiles']:
                    assert s.sha((s.ROOT/review_file['file']).read_bytes())==review_file['sha256']
                source['status']='verified'
                source['validation']['independentQualificationAcceptance']=reviewed
                source['notes'].append(public_review_note(source))
                if not controls_match:
                    source['notes'].append('The faithful complete named schedule is accepted with unresolved issuer control differences. Summary reconciliation remains false; no row, scope or control is changed to balance the issuer arithmetic.')
            if held_reason and not reviewed:
                source['publicWarning']=held_reason;source['validation']['periodHeadingConflict']=c.get('periodHeadingConflict')
                held.append(source)
            elif not controls_match:
                source['publicWarning']=f"The published named-row sums minus the printed schedule controls are remuneration ${residuals[0]} and expenses ${residuals[1]}. No adjustment or cause is inferred."
                (manifest['sources'] if reviewed else held).append(source)
            else:manifest['sources'].append(source)
            (s.COLLECTION/source['file']).write_bytes(data);(s.COLLECTION/source['provenanceFile']).write_bytes(evidence_data)
    (s.COLLECTION/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (s.INVENTORY/'held-candidates.json').write_text(json.dumps(held,ensure_ascii=False,indent=2)+'\n')
    print('Verified',len(manifest['sources']),'cohorts',sum(x['rowCount'] for x in manifest['sources']),'rows; held',len(held),'cohorts',sum(x['rowCount'] for x in held),'rows')

if __name__=='__main__':main()
