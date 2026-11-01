#!/usr/bin/env python3
"""Build the bounded Lower Mainland source decisions and next-action queue offline."""
import json
from pathlib import Path
from urllib.parse import unquote, urldefrag

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/municipal-next-pass/lower-mainland'
COLLECTION=ROOT/'research/salaries/municipal-wave-lower-mainland'


def read(path):
    return json.loads(path.read_text())


def canonical(url):
    return unquote(urldefrag(url)[0]).replace('://www.','://').rstrip('/')


def main():
    baseline=read(OUT/'audit-baseline.json')
    employers={m['employerSlug']:m for m in baseline['municipalities']}
    archives=read(OUT/'archive-receipts.json')
    follow=read(OUT/'finance-follow-up-receipts.json')
    receipts=read(OUT/'retrieval-receipts.json')
    sources=read(COLLECTION/'sources.json')['sources']
    config=read(COLLECTION/'reviewed-layouts.json')['reports']
    grouped={}
    for source in sources:
        grouped.setdefault(canonical(source['sourceUrl']),[]).append(source)
    decisions=[];queue=[]

    def task(id,slug,periods,url,index,status,route,action,reason):
        queue.append(dict(id=id,employerSlug=slug,employerName=employers[slug]['employerName'],sector='Municipalities',
            reportingPeriods=periods,sourceUrl=url,sourceIndexUrl=index,status=status,route=route,nextAction=action,reason=reason))

    for receipt in receipts:
        ss=grouped.get(canonical(receipt['url']),[])
        report=next((r for r in config if canonical(r['sourceUrl'])==canonical(receipt['url'])),None)
        slug=receipt['employerSlug'];period=report['year'] if report else None
        document=dict(receipt,sector='Municipalities',indexedLabel=receipt['year'],actualScheduleCalendarYear=period,
            periodVerified=bool(report),scope=[s['category'] for s in ss],acceptedSources=[s['id'] for s in ss],
            acceptedRows=sum(s['rowCount'] for s in ss),heldMissingBenefitRows=sum(s['validation']['heldMissingBenefitRows'] for s in ss),
            status='accepted-reviewed-cohorts' if ss else 'retrieval-failed' if receipt.get('error') else 'public-original-awaiting-review')
        document['nextAction']='Retain the reviewed normalized cohorts, partial-scope warnings and original evidence.' if ss else \
            'Locate the moved public original or an official archive copy; cached search text is not an original.' if receipt.get('error') else \
            'Review named schedule pages, actual period, row fields and source controls; OCR only the relevant scanned pages when needed.'
        if report:
            document['periodEvidence']=report['periodEvidence']
        decisions.append(document)
        if not ss and not receipt.get('error'):
            task('wave-lower-process-'+receipt['id'],slug,[],receipt['url'],receipt['indexUrl'],
                'public-original-awaiting-ocr-or-layout-review','processing',document['nextAction'],
                'Original retrieved/rehashed. Indexed label '+str(receipt['year'])+' is not yet a verified named-schedule period. '
                + ('No usable embedded text; begin bounded schedule OCR.' if not receipt.get('textChars') else 'Embedded text may include OCR; verify actual named schedules before acceptance.'))
        if ss and slug in ['city-of-richmond','city-of-port-moody']:
            task('wave-lower-employees-'+receipt['id'],slug,[period],receipt['url'],receipt['indexUrl'],
                'employee-cohort-still-unaccepted','processing',
                'Verify every employee name/row and compensation component against rendered schedules and both readers; handle wrapped layouts or OCR errors and reconcile all available controls.',
                'Only the complete council cohort is accepted. Its acceptance does not establish employee coverage or resolve held employee layouts.'
                + (' Port Moody 2025 p47 prints a staff remuneration grand total of 36,319,110, but its named 28,810,242 plus under-threshold 10,508,868 sums 39,319,110. Preserve this 3,000,000 source discrepancy; do not distribute it among employees.' if slug=='city-of-port-moody' and period=='2025' else ''))
        for source in ss:
            held=source['validation']['heldMissingBenefitRows']
            if not held:
                continue
            task('wave-lower-components-'+source['id'],slug,[period],receipt['url'],receipt['indexUrl'],
                'partial-cohort-component-clarification','clarification-request',
                'Find an original spreadsheet or explicit issuer legend establishing each dash/blank taxable-benefit cell; if absent from the public archive, request that existing record or clarification routinely. Do not infer zero from a subtotal match.',
                str(held)+' named rows remain held. Known remuneration, missing benefit components, expenses, names and physical pages are retained in the source manifest/evidence; accepted-subset totals do not cover the full named cohort.')

    belcarra=employers['village-of-belcarra']
    task('wave-lower-belcarra-early-council','village-of-belcarra',['2010','2012','2013','2014','2017','2018'],
        'https://belcarra.ca/assets/media/2019/05/2017_SOFI_Report.pdf',belcarra['archiveUrl'],
        'historical-council-definition-held','clarification-request',
        'Locate the historical column definitions or existing schedules/spreadsheets separating non-taxable expense allowance, remuneration and ordinary expenses. Ask Finance routinely only if public evidence does not resolve the distinction.',
        '2017/2018 explicitly combine expense allowance and expenses; the earlier council expense definitions also require review. Employee acceptance does not justify presenting combined council amounts as ordinary expenses or total remuneration.')

    for slug in ['city-of-chilliwack','langley-township','district-of-kent','district-of-hope']:
        m=employers[slug]
        url='https://hope.ca/finance' if slug=='district-of-hope' else \
            'https://www.kentbc.ca/district-hall/financial-plans-and-reports/' if slug=='district-of-kent' else m['archiveUrl']
        action='Search official council agenda attachments for adopted SOFI schedules and the historical financial archive; distinguish named remuneration from audited statements and aggregate payroll.'
        reason='Primary official archive was checked; this bounded pass did not retrieve a usable named municipal salary original.'
        if slug=='district-of-hope':
            action='Restore the legacy 2022/2023 SOFI downloads on the current official site, and attempt the separately indexed June 22, 2026 meeting download; follow the new Finance annual-report lead first. If still unavailable, ask Finance routinely for the existing SOFI originals.'
            reason='Search located official legacy SOFI downloads, but direct 2022/2023 retrieval returned404. Cached search text was not imported. The current Finance page links an annual report, which is not yet verified as containing named salary schedules.'
        if slug=='langley-township':
            action+=' An external index points to SOFI consideration at the June 29, 2026 Council meeting; verify this in the official agenda and retrieve its attachment.'
        if slug=='district-of-kent':
            action='Inspect the current official 2025 annual-financial-report PDF for actual named remuneration schedules, then search council SOFI attachments if absent; do not substitute aggregate payroll or financial statements.'
            reason='Current official finance page exposes 2022–2025 annual financial reports. Their labels do not establish individual salary disclosure scope.'
        task('wave-lower-archive-'+slug,slug,[],url,url,'named-schedule-discovery-incomplete','public-archive-research',action,reason)

    m=employers['city-of-abbotsford']
    task('wave-lower-abbotsford-2025-and-older','city-of-abbotsford',['2025'],m['archiveUrl'],m['archiveUrl'],
        'current-year-source-not-yet-retrieved','ordinary-records-request',
        'Check current council attachments for 2025 SOFI first, then ask Finance/Corporate Services routinely for the adopted 2025 named employee/council schedules, existing spreadsheet and an index of earlier years. Verify a formal FOI process only if routine public access fails.',
        'The finance page says SOFI is available on request, but this pass recovered 2023/2024 originals publicly in council attachments. The previous blanket procurement assumption is narrowed; 2025 and pre-2023 history remain to locate.')
    for slug in ['village-of-belcarra','village-of-harrison-hot-springs','city-of-port-moody','city-of-richmond','city-of-mission']:
        m=employers[slug]
        task('wave-lower-history-'+slug,slug,[],m['archiveUrl'],m['archiveUrl'],'historical-archive-not-exhausted','public-archive-research',
            'Follow the official archive and council attachments for unaccepted earlier or later SOFI schedules, inspect each named schedule period and compare against the accepted-source manifest before importing.',
            'This pass accepts a bounded subset and retains located scanned/layout reports in separate processing tasks. It does not claim complete municipal history.')

    summary=dict(asOf='2026-10-31',timeZone='America/Vancouver',baselineCommit='5e5fe01',baselineDatasetRows=917420,
        targetedMunicipalities=len(employers),primaryArchiveChecks=len(archives),originalReceipts=len(receipts),
        availableOriginals=sum(not bool(r.get('error')) for r in receipts),verifiedReports=len(config),verifiedCohorts=len(sources),
        acceptedRows=sum(s['rowCount'] for s in sources),acceptedEmployeeRows=sum(s['rowCount'] for s in sources if s['category']=='employee-remuneration'),
        acceptedCouncilRows=sum(s['rowCount'] for s in sources if s['category']=='elected-officials'),
        municipalitiesWithAcceptedRows=sorted({s['employerSlug'] for s in sources}),
        heldMissingBenefitRows=sum(s['validation']['heldMissingBenefitRows'] for s in sources),compiledRowsRemoved=0,
        requestsSent=0,queueTasks=len(queue))
    for filename,payload in [('source-decisions.json',decisions),('work-queue.json',queue),('summary.json',summary)]:
        (OUT/filename).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':
    main()
