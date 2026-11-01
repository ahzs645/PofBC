#!/usr/bin/env python3
"""Rebuild this pass's municipal findings and diagnostic compiled overlaps offline."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urldefrag

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/sector-search-2026-10-31/municipal'


def read(path):
    return json.loads(path.read_text())


def canonical(url):
    return unquote(urldefrag(url)[0]).replace('://www.', '://').rstrip('/')


def normalized(name):
    return re.sub('[^A-Z0-9]', '', name.upper())


def main():
    coverage = read(ROOT / 'research/salaries/municipal-audit/coverage.json')
    baseline = {m['employerSlug']: m for m in coverage['municipalities']}
    receipts = read(OUT / 'archive-receipts.json')
    documents = read(OUT / 'document-receipts.json')
    sources = read(ROOT / 'research/salaries/sector-municipal/sources.json')['sources']
    by_url = {}
    for source in sources:
        by_url.setdefault(canonical(source['sourceUrl']), []).append(source)
    # These exact named schedule pages were inspected in the retrieved originals.
    historical_revelstoke = {'2021': [39, 40], '2022': [38, 39], '2023': [48, 49], '2024': [46, 47]}
    for document in documents:
        accepted = by_url.get(canonical(document['url']), [])
        document['indexedYear'] = document.pop('year')
        document['acceptedOverlapAtBaseline'] = [s for s in baseline[document['employerSlug']]['acceptedSources']
            if str(s.get('year')) == document['indexedYear']]
        document['retrievalStatus'] = 'retrieved' if document['downloaded'] else 'retrieval-failed'
        document['periodInspected'] = None
        document['namedSchedulePresence'] = 'not-yet-verified'
        document['textAvailability'] = ('no-embedded-text' if not document.get('totalTextChars') else 'embedded-text-present; may include OCR')
        document['scope'] = None
        document['processingOrProcurement'] = 'processing'
        if accepted:
            document.update(status='accepted-import-ready', periodInspected={'calendarYear': document['indexedYear'],
                'basis': 'Named schedule year checked in complete rendered schedule; all row fields reviewed',
                'physicalPages': sorted({p for s in accepted for p in s['pages']})},
                namedSchedulePresence='verified-named-employees-and-elected-officials',
                scope=['employee-remuneration', 'elected-officials'],
                acceptedImportSources=[s['id'] for s in accepted], rowsReady=sum(s['rowCount'] for s in accepted),
                nextAction='Register the hash-pinned reviewed collection and expose its public source warnings; retain compiled cohorts unless a full independent match is proved.')
        elif document['employerSlug'] == 'city-of-revelstoke' and document['indexedYear'] in historical_revelstoke:
            document.update(status='public-named-schedules-awaiting-review', namedSchedulePresence='named-employees-and-elected-officials-located',
                periodInspected={'calendarYear': document['indexedYear'], 'basis': 'Year and named schedule text inspected; row acceptance not completed',
                    'physicalPages': historical_revelstoke[document['indexedYear']]},
                scope=['employee-remuneration', 'elected-officials'],
                nextAction='Verify every rendered name/title/amount with both readers, full cohort counts, remuneration definition and monetary controls. The 2022 OCR-like layer requires particular glyph review.')
        elif document['employerSlug'] == 'city-of-port-moody':
            document.update(status='public-layout-review', namedSchedulePresence='candidate-named-tables-in-embedded-text',
                nextAction='Resolve wrapped positions and the separate remuneration/tax-benefits-and-payouts/expense columns; verify the exact schedule period and all rows and controls before import.')
        else:
            document.update(status='public-ocr-or-layout-review',
                nextAction='Locate the named employee/council schedules, verify their calendar period, then use source-specific OCR/layout extraction with complete row and monetary-control checks. Originals are already retrieved; no request is needed to start.')
    employers = []
    for receipt in receipts:
        municipality = baseline[receipt['employerSlug']]
        docs = [d for d in documents if d['employerSlug'] == municipality['employerSlug']]
        indexed_labels = sorted({y for item in [receipt] + receipt.get('alternateArchiveChecks', [])
            for c in item['candidates'] for y in c.get('indexedLabelYears', [])})
        employers.append({'employerSlug': municipality['employerSlug'], 'employerName': municipality['employerName'],
            'sector': 'Municipalities', 'baselineOfficialEmployeeYears': municipality['officialEmployeeYears'],
            'baselineOfficialCouncilYears': municipality['officialCouncilYears'],
            'baselineCompiledEditionLabels': municipality['compiledUnverifiedEditionLabels'],
            'baselineCompiledRecords': municipality['compiledUnverifiedRecords'],
            'officialIndexUrl': receipt.get('alternateArchiveChecks', [{}])[0].get('archiveUrl', receipt['archiveUrl']),
            'archiveReceipt': receipt,
            'historicalRange': {'indexedLabelYears': indexed_labels, 'documentYearsRetrieved': sorted(d['indexedYear'] for d in docs),
                'periodsInspected': sorted(d['periodInspected']['calendarYear'] for d in docs if d['periodInspected']),
                'caution': 'Index labels and upload-path year tokens do not establish schedule periods or historical completeness.'},
            'documents': docs,
            'reuseExistingOcr': [str(p.relative_to(ROOT)) for p in (ROOT/'research/salaries/municipal-ocr/staging').glob('*.json.gzip')
                if any(p.name == s['id']+'.json.gzip' for s in municipality['heldOrUnparsedSources'])],
            'processingOrProcurement': 'processing' if docs or receipt['candidates'] else 'deeper-archive-research',
            'nextAction': 'Review the retrieved schedules and remaining linked history.' if docs else
                'Follow the linked document/archive entries; check historical council attachments before making a routine report request.' if receipt['candidates'] else
                'Search the official document centre and council agenda archive; absence of a detected HTML link is not evidence a report must be procured.'})
    requests = read(ROOT/'research/salaries/municipal-audit/follow-up.json')['requests']
    findings = {'version': 1, 'asOf': '2026-10-31', 'timeZone': 'America/Vancouver', 'baselineCommit': '96d798e',
        'scope': 'Municipal historical follow-up; municipal police and regional districts assigned separately.',
        'summary': {'municipalArchiveChecks': len(receipts), 'retrievedOriginals': sum(d['downloaded'] for d in documents),
            'acceptedReports': len(by_url), 'acceptedCohorts': len(sources), 'rowsReady': sum(s['rowCount'] for s in sources),
            'employeeRowsReady': sum(s['rowCount'] for s in sources if s['category']=='employee-remuneration'),
            'councilRowsReady': sum(s['rowCount'] for s in sources if s['category']=='elected-officials'),
            'employersReady': len({s['employerSlug'] for s in sources})},
        'assumptions': ['Use the calendar year printed on the named schedule, never infer it from a fiscal-like compiled label or an upload path.',
            'Import named payment disclosures in their actual scope, not aggregate payroll, supplier payments, executive-only substitutes or assumed full employee rosters.',
            'Pitt Meadows pay is base salary plus benefits/other; Revelstoke uses its separate remuneration column; Parksville employee remuneration already includes taxable benefits. Expenses stay separate.',
            'No inferred amounts, balancing edits, silent name/title repairs, compiled deletions or alias changes.',
            'Minor issuer subtotal differences are disclosed with exact residuals after complete rendered-row verification; an ambiguous transcription is held.',
            'A retrieved scanned report is processing work. Request an existing spreadsheet or clearer original only where review remains blocked; routine public access precedes any formal FOI fallback.'],
        'acceptedManifest': '../../sector-municipal/sources.json', 'employers': employers,
        'procurementRequests': {'provenance': '../../municipal-audit/follow-up.json from the merged audit; carried forward, not newly asserted to have been reverified by these archive checks.',
            'requestStatus': 'not-sent', 'requests': requests},
        'limits': ['This pass checks 24 priority municipal archives; the existing province-wide municipal audit remains the full roster.',
            'A successful index download does not establish that all historical documents or schedules were found.',
            'Selectable PDF text may be embedded OCR. Reader agreement alone does not prove correct names, titles or amounts.']}
    (OUT/'findings.json').write_text(json.dumps(findings, ensure_ascii=False, indent=2)+'\n')
    queue = []
    for document in documents:
        if document['status'] == 'accepted-import-ready':
            continue
        employer = baseline[document['employerSlug']]
        verified = document['periodInspected']
        queue.append({'id': 'municipal-process-' + document['id'], 'employerSlug': document['employerSlug'],
            'employerName': employer['employerName'], 'sector': 'Municipalities',
            'reportingPeriods': [verified['calendarYear']] if verified else [],
            'sourceUrl': document['url'], 'sourceIndexUrl': document['indexUrl'],
            'status': document['status'], 'route': 'processing', 'nextAction': document['nextAction'],
            'reason': ('Original retrieved and SHA-256 pinned. ' + document['textAvailability'] + '. ' +
                ('Named schedule period inspected.' if verified else 'The indexed label is ' + document['indexedYear'] + '; the actual named schedule period remains unverified.'))})
    for employer in employers:
        if employer['documents'] and employer['employerSlug'] != 'city-of-parksville':
            continue
        queue.append({'id': 'municipal-history-' + employer['employerSlug'],
            'employerSlug': employer['employerSlug'], 'employerName': employer['employerName'], 'sector': 'Municipalities',
            'reportingPeriods': [], 'sourceUrl': employer['officialIndexUrl'], 'sourceIndexUrl': employer['officialIndexUrl'],
            'status': 'historical-archive-research', 'route': 'public-archive-research',
            'nextAction': 'Follow SOFI/document-centre and council agenda links to identify and retrieve unaccepted historical named employee/council schedules; inspect periods before extraction.',
            'reason': 'Priority archive checked; linked documents or deeper archive navigation still require review. No absence of a document or need for FOI is inferred from HTML discovery.'})
    clarification_routes = {'final-version-or-adoption-evidence', 'reporting-period-clarification',
        'source-control-clarification', 'source-total-clarification'}
    for index, request in enumerate(requests):
        routine = request['route'] not in clarification_routes
        queue.append({'id': 'municipal-procure-' + request['employerSlug'] + '-' + str(request.get('year') or 'historical') + '-' + str(index),
            'employerSlug': request['employerSlug'], 'employerName': request['municipality'], 'sector': 'Municipalities',
            'reportingPeriods': [str(request['year'])] if request.get('year') else [],
            'sourceUrl': next(iter(request.get('sourceUrls') or []), request.get('url') or request['archiveUrl']),
            'sourceIndexUrl': request['archiveUrl'], 'status': 'not-sent',
            'route': 'ordinary-records-request' if routine else 'clarification-request',
            'nextAction': request['ask'] + ' First check the linked public archive, then approach Finance/Corporate Services routinely. Verify the official FOI route only if routine access does not resolve the blocker.',
            'reason': request['blocker'] + ' Carried forward from the merged municipal follow-up audit; no request has been sent.'})
    (OUT/'work-queue.json').write_text(json.dumps(queue, ensure_ascii=False, indent=2)+'\n')
    raw = (ROOT/'research/salaries/compiled-baseline.json.gzip').read_bytes()
    compiled = json.loads(gzip.decompress(raw)); comparisons=[]
    for source in sources:
        if source['category'] != 'employee-remuneration':
            continue
        employer = next((e for e in compiled['employers'] if e['slug']==source['employerSlug']), None)
        if not employer:
            continue
        official = json.loads(gzip.decompress((ROOT/'research/salaries/sector-municipal'/source['file']).read_bytes()))
        official_counter=Counter((normalized(r[1]),r[3],r[4]) for r in official)
        for index, label in enumerate(compiled['years']):
            group=[r for r in employer['rows'] if r[-1]==index and not re.search(r'councill|mayor|city council',r[1],re.I)]
            if not group:
                continue
            signatures=Counter((normalized(r[0]),r[2],r[3]) for r in group)
            overlap=signatures & official_counter
            comparisons.append({'employerSlug': source['employerSlug'], 'officialCalendarYear': source['year'],
                'officialSourceUrl': source['sourceUrl'], 'officialOriginalSha256': source['sha256'], 'officialDataSha256': source['dataSha256'],
                'compiledEditionLabel':label,'officialEmployeeRows':len(official),'compiledCandidateEmployeeRows':len(group),
                'exactNamePayExpenseMatches':sum(overlap.values()),'wholeGroupIdentityProved':False,
                'unmatchedOfficial':list((official_counter-signatures).elements()),'unmatchedCompiled':list((signatures-official_counter).elements()),
                'decision':'Diagnostic only. Preserve the entire compiled group and its unverified label; partial overlap is not a replacement decision.'})
    result={'version':1,'compiledSnapshotSha256':hashlib.sha256(raw).hexdigest(),
        'comparison':'Case/punctuation-folded name plus exact remuneration and expenses; no title equivalence or row deletion is inferred.',
        'comparisons':comparisons,'compiledRowsRemoved':0}
    (OUT/'compiled-overlap.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(findings['summary']))


if __name__ == '__main__':
    main()
