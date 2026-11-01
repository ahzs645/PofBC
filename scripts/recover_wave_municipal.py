#!/usr/bin/env python3
"""Bounded municipal recovery. Independent native readers + peer-reviewed scan transcription.

No network, registry or generated-public writes. --build reads hash-pinned originals;
--verify replays the retained reader inputs without the original PDFs.
"""
import argparse
from collections import defaultdict
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/salaries/recovery-municipal'
REPORT = ROOT / 'research/salaries/recovery-wave-2026-11-01/municipal'
BASE = ROOT / 'research/salaries'
DATE = '2026-11-01'
SCHEMA = ['employerSlug', 'name', 'position', 'remuneration', 'expenses', 'pdfPage']
EMP = 'employee-remuneration'
COUNCIL = 'elected-officials'
PEER = ROOT/'research/salaries/recovery-wave-2026-11-01/reviews/independent-manual-mcbride-comparison.json'
PEER_SHA = '61951a9c796edcda23f204f2eaa4dae2f1ef668e1557b0b5ccf1a52fc602f956'
APPROVAL = dict(sourceUrl='https://midwaybc.ca/wp-content/uploads/2025/07/13-Regular-Meeting-June-9-2025.pdf',
                sourceIndexUrl='https://midwaybc.ca/2025-newsletters-meeting-minutes-agenda/',
                cachePath='/tmp/recovery-municipal-review/midway-june9-2025-minutes.pdf',
                sha256='930ed8bb23cd786c97a7d16dd59d62678ec892fab5476f51c5603b4a8f1ce33d',
                physicalPage=2,printedPage=6952,signedMinutesPage=3,
                motions=[dict(id='025-2025',text='THAT Council approves revised 2023 Statement of Financial Information (SOFI) Schedules.',result='Carried'),
                         dict(id='026-2025',text='THAT Council approves revised 2024 Statement of Financial Information (SOFI) Schedules',result='Carried')],
                review='All three original-image minutes pages reviewed by recovery_municipal; signatures visible on page 3.')

ORIGINALS = [
    dict(key='mcbride-2022', employerSlug='village-of-mcbride', employerName='Village of McBride', year='2022',
         sourceUrl='https://mcbride.civicweb.net/document/18711', sourceIndexUrl='https://www.mcbride.ca/government-bylaws/finance',
         sha256='c07190fb089fe01b1b92776480b4e63fcf199fd02c70754acafa4a5c27d3af0e',
         cachePath='/tmp/continuation-municipal/village-of-mcbride-c07190fb089fe0.pdf', pages=[39,40], approvalPage=45,
         approval='Officially linked original; approval page 45 is unsigned with blank dates. Adoption is not established by this original.', method='manual'),
    dict(key='mcbride-2023', employerSlug='village-of-mcbride', employerName='Village of McBride', year='2023',
         sourceUrl='https://mcbride.civicweb.net/document/29458', sourceIndexUrl='https://www.mcbride.ca/government-bylaws/finance',
         sha256='afadbdc30c4bcd5e49f92a1305b8c7d4e5047c728e60e01867082bfea200868d',
         cachePath='/tmp/continuation-municipal/village-of-mcbride-afadbdc30c4bcd.pdf', pages=[44,45], approvalPage=50,
         approval='Approval page 50 carries signatures of Jeanette McDougall and Eugene Runtz and handwritten June 19, 2024 dates.', method='manual'),
    dict(key='mcbride-2024', employerSlug='village-of-mcbride', employerName='Village of McBride', year='2024',
         sourceUrl='https://mcbride.civicweb.net/document/39757', sourceIndexUrl='https://www.mcbride.ca/government-bylaws/finance',
         sha256='ab3285b9156ba179775263f5d730d24cbd96af3f51fbd7595ac9852c311044f1',
         cachePath='/tmp/continuation-municipal/village-of-mcbride-ab3285b9156ba1.pdf', pages=[45,46], approvalPage=51,
         approval='Approval page 51 carries signatures of Jeanette McDougall and Eugene Runtz and handwritten June 24, 2025 dates.', method='manual'),
    dict(key='mcbride-2025', employerSlug='village-of-mcbride', employerName='Village of McBride', year='2025',
         sourceUrl='https://mcbride.civicweb.net/document/45990', sourceIndexUrl='https://www.mcbride.ca/government-bylaws/finance',
         sha256='11733872fa678d7af449e391271581ca65602df4b35898661f903043a0b7e214',
         cachePath='/tmp/continuation-municipal/village-of-mcbride-11733872fa678d.pdf', pages=[43], approvalPage=48,
         approval='Approval page 48 carries signatures of Jeanette McDougall and Eugene Runtz and handwritten 2026 dates. Council page 42 is held separately for its contradictory 2024 heading.', method='manual'),
    dict(key='midway-2023-2024', employerSlug='village-of-midway', employerName='Village of Midway', year=None,
         sourceUrl='https://midwaybc.ca/wp-content/uploads/2025/06/13-Agenda-JUN-9-2025.pdf',
         sourceIndexUrl='https://midwaybc.ca/2025-newsletters-meeting-minutes-agenda/',
         sha256='04bb08ea2b2fc40cce7972a28ff7ccc00a373dd9341f8587286d572d97954331',
         cachePath='/tmp/continuation-municipal/village-of-midway-04bb08ea2b2fc4.pdf', pages=[9,11], approvalPage=8,
         approval='Revised 2023 and 2024 schedules in the June 9, 2025 agenda; signed official minutes page 2 (printed 6952), motions 025-2025 and 026-2025, approve both revised schedules. Minutes SHA256 930ed8bb23cd786c97a7d16dd59d62678ec892fab5476f51c5603b4a8f1ce33d.', method='native'),
    dict(key='sooke-2025', employerSlug='district-of-sooke', employerName='District of Sooke', year='2025',
         sourceUrl='https://www.sooke.ca/media/emqbjnxm/2025-statement-of-financial-information.pdf',
         sourceIndexUrl='https://www.sooke.ca/media-manager/media-pages/plans-and-reports/2025-statement-of-financial-information-sofi/',
         sha256='f7c218a601804343d7d4ae4f480d7b9b34cb4dcaa9c6115be8d5602992cb1e13',
         cachePath='/tmp/continuation-municipal/district-of-sooke-f7c218a6018043.pdf', pages=[37,38], approvalPage=2,
         approval='Approval page 2 carries Director of Financial Services and Mayor signatures with June 2026 dates.', method='native'),
]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    path = Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gzip' else path.read_bytes())

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    path.write_bytes(gzip.compress(payload, mtime=0) if path.suffix == '.gzip' else payload)
    return sha(path)

def money(value):
    value = value.strip().replace(',', '').replace('$', '').strip()
    if not value or value in {'-', '—'}:
        return None
    if not re.fullmatch(r'-?\d+(?:\.\d{2})?', value):
        raise ValueError(f'Not a printed money value: {value!r}')
    return float(Decimal(value)) if '.' in value else int(value)

def amount_sum(rows, index):
    return float(sum((Decimal(str(r[index])) for r in rows if r[index] is not None), Decimal(0)))

def poppler_reader(text, original, page):
    """Read literal fixed-width lines, retaining prewrapped titles and off-baseline cells.

    This path does not consume PyMuPDF words or row anchors.
    """
    scope = EMP if page == 38 else COUNCIL
    rows = []
    pending_title = []
    pending_expense = None
    midway = original['key'].startswith('midway')
    for line in text.splitlines():
        line = line.replace('$', ' ')
        clean = line.strip()
        if clean.startswith('Employees with Gross Salary') or clean.startswith('2. List of employees'):
            scope = EMP
            pending_title = []
        if clean.startswith('Total') or clean.startswith('Add:') or clean.startswith('Notes to the reader'):
            pending_title = []
            scope = None
            continue
        if scope is None:
            continue
        match = re.match(r'^\s*([A-Za-z][A-Za-z -]*,\s*\S.*?)\s{2,}(.*)$', line)
        if match:
            name, rest = match.groups()
            cells = re.split(r'\s{2,}', rest.strip())
            if midway:
                assert len(cells) == 3, (name,cells)
                title, pay, expenses = cells
            elif len(cells) in (2,3) and not re.match(r'^\d', cells[0]):
                title, pay = cells[:2]
                expenses = cells[2] if len(cells) == 3 else ''
            elif len(cells) == 1 and re.fullmatch(r'[\d,]+', cells[0]):
                title, pay, expenses = '', cells[0], pending_expense or ''
            else:
                raise AssertionError((page,name,cells))
            title = ' '.join(pending_title + [title]).strip()
            rows.append(dict(scope=scope, row=[original['employerSlug'],name.strip(),title or None,money(pay),money(expenses),page]))
            pending_title = []
            pending_expense = None
        elif not midway and page == 37 and line.startswith('                         ') and not clean.startswith(('Position','Name')):
            if re.search(r'[A-Za-z]',clean) and not any(x in clean for x in ['Remuneration','Expenses']):
                pending_title.append(clean)
            elif clean == '33':
                # Printed expense sits above the Mills name baseline. Original-image
                # review confirms this cell, not a page footer (the footer is 34).
                pending_expense = '33'
    return rows

def pymupdf_reader(words, original, page):
    """Independent positioned-word reader using left-column name anchors and cell bands.

    No Poppler lines, extracted rows or name list are consumed by this path.
    """
    midway = original['key'].startswith('midway')
    name_right, title_right, pay_right, table_right = ((245,424,503,570) if midway else (165,377,474,555))
    anchors = sorted([w for w in words if 50 <= w[0] < name_right and re.fullmatch(r'[A-Za-z-]+,', w[4])], key=lambda w:w[1])
    result = []
    previous = None
    for anchor in anchors:
        y = anchor[1]
        if midway and not 180 < y < 355:
            continue
        if not midway and page == 37 and y < 120:
            continue
        if not midway and page == 38 and y > 260:
            continue
        scope = EMP if (midway and y > 270) or (not midway and (page == 38 or y > 250)) else COUNCIL
        name = ' '.join(w[4] for w in sorted(words, key=lambda w:w[0]) if 50 <= w[0] < name_right and abs(w[1]-y) < 1.5)
        lower = y-6 if previous is None or previous[1] != scope else previous[0]+6
        title = ' '.join(w[4] for w in sorted(words,key=lambda w:(round(w[1],0),w[0]))
                         if name_right <= w[0] < title_right and lower < w[1] < y+6)
        pay = [w[4] for w in words if title_right <= w[0] < pay_right and abs(w[1]-y) < 1.5 and w[4] != '$']
        expenses = [w[4] for w in words if pay_right <= w[0] < table_right and lower < w[1] < y+6 and w[4] != '$']
        assert len(pay) == 1 and len(expenses) <= 1, (page,name,pay,expenses)
        result.append(dict(scope=scope,row=[original['employerSlug'],name,title or None,money(pay[0]),money(expenses[0]) if expenses else None,page]))
        previous = (y,scope)
    return result

def raw_native(original):
    import fitz
    assert sha(original['cachePath']) == original['sha256']
    doc = fitz.open(original['cachePath'])
    return {str(page):dict(words=doc[page-1].get_text('words'),
                          layoutText=subprocess.check_output(['pdftotext','-f',str(page),'-l',str(page),'-layout',original['cachePath'],'-']).decode())
            for page in original['pages']}

def all_native_rows(raw, original):
    rows = []
    for page in original['pages']:
        inputs = raw[str(page)]
        pop = poppler_reader(inputs['layoutText'], original, page)
        mup = pymupdf_reader(inputs['words'], original, page)
        assert pop == mup, f'Independent native reader mismatch {original["key"]} p{page}: {list(zip(pop,mup))}'
        rows += pop
    return rows

def baseline_overlap(sources):
    registered = read(BASE/'collections.json')['collections']
    baseline = [s for collection in registered if collection != 'recovery-municipal' for s in read(BASE/collection/'sources.json')['sources'] if s.get('file') and s.get('status','verified') in {'verified','accepted','imported'}]
    collisions = []
    for source in sources:
        for old in baseline:
            same_scope = (old.get('category') or old.get('scope')) == source['category']
            if old.get('employerSlug') == source['employerSlug'] and str(old['year']) == source['year'] and same_scope:
                collisions.append([source['id'],old['id']])
    assert not collisions, collisions
    employer_index=read(ROOT/'public/salaries/index.json')
    compiled_counts={slug:sum(cohort['count'] for cohort in employer_index['bodies'].get(slug,{}).values()
                              if any(employer_index['sources'][source_id].get('sourceKind')=='compiled' for source_id in cohort.get('sourceIds',[])))
                     for slug in sorted({s['employerSlug'] for s in sources})}
    assert not any(compiled_counts.values()), compiled_counts
    return dict(registeredCollections=len(registered), acceptedSourcesChecked=len(baseline), sourcePeriodScopeCollisions=collisions,
                registeredEmployerSourceCounts={slug:sum(s.get('employerSlug')==slug for s in baseline) for slug in compiled_counts},
                compiledBaselineCounts=compiled_counts,employersWithCompiledBaselineRows=[])

def verify_peer():
    assert sha(PEER)==PEER_SHA
    receipt=read(PEER)
    assert receipt['candidate']['sha256']==sha(OUT/'manual-transcription.json')
    assert receipt['rowsCompared']==35
    assert all(c['allFieldsExact'] and c['controlsExact'] and not c['corrections'] for c in receipt['comparisons'])
    transcript=receipt['independentOriginalTranscript']
    assert transcript['writtenBeforeCandidateOpened']
    assert sha(ROOT/transcript['path'])==transcript['sha256']
    return dict(path=str(PEER.relative_to(ROOT)),sha256=PEER_SHA,
                independentTranscript=transcript,allRowFieldsExact=True,reviewer=receipt['reviewer'])

def controls_for(key, scope, manual=None):
    if manual:
        return manual['printedNamedControls'][:2]
    if key.startswith('midway-2023-'):
        return [357899,19816] if scope == EMP else [46270,22608]
    if key.startswith('midway-2024-'):
        return [362652,2866] if scope == EMP else [48077,23919]
    if key.startswith('sooke-'):
        return [6874287,110474] if scope == EMP else [172062,26266]
    raise ValueError(key)

def make_source(original, key, year, scope, rows, evidence_name, evidence_hash, manual=None):
    controls = controls_for(key,scope,manual)
    source = dict(id='recovery-municipal-'+key,employerSlug=original['employerSlug'],employerName=original['employerName'],sector='Municipalities',
                  year=year,periodType='calendar',periodStart=year+'-01-01',periodEnd=year+'-12-31',sourceUrl=original['sourceUrl'],sourceIndexUrl=original['sourceIndexUrl'],
                  sha256=original['sha256'],file=key+'.json.gzip',category=scope,scope=scope,title=original['employerName']+' '+year+' SOFI: '+scope,
                  status='verified',verifiedOn=DATE,sourceKind='official',rowCount=len(rows),totalRemuneration=amount_sum(rows,3),totalExpenses=amount_sum(rows,4),
                  pages=sorted({row[5] for row in rows}),currency='CAD',amountUnit='dollars',threshold=75000 if scope == EMP else None,
                  thresholdComparison='greater-than' if scope == EMP else None,completeEmployeeSchedule=True if scope == EMP else None,
                  notes=[original['approval'],
                         'Only individually named persons are imported. Below-threshold aggregates, expense-inclusive combined totals and financial-statement employer costs are retained as evidence and are not personal remuneration.',
                         'Published names, initials and titles are preserved without enrichment. Missing titles and blank/dash expenses remain null; explicit zeros would remain zero. Expenses are separate from remuneration.'],
                  validation=dict(completeEmployeeSchedule=True if scope == EMP else None,allRowFieldsAgree=True,controls=[],
                                  evidenceFile=evidence_name,evidenceSha256=evidence_hash,physicalPagesVisuallyReviewed=sorted({row[5] for row in rows}),
                                  periodEvidence=[dict(page=row[5],text=(year+' FINANCIAL INFORMATION' if original['method']=='manual' else 'For the year ended December 31, '+year)) for row in rows[:1]]))
    source['dataSha256'] = write(OUT/source['file'],rows)
    for index,field in [(3,'remuneration'),(4,'expenses')]:
        row_sum=amount_sum(rows,index)
        source['validation']['controls'].append(dict(field=field,printedNamedControl=controls[index-3],knownRowSum=row_sum,
                                                     residual=float(Decimal(str(row_sum))-Decimal(str(controls[index-3]))),
                                                     basis='Complete named cohort. Null expenses excluded from known sum and not imputed.'))
    warnings=[]
    if original['method']=='manual':
        source['validation']['extractionMethod']='Complete original-image manual transcription, independently transcribed and compared by peer; OCR overlay is discovery only.'
        source['validation']['independentPeerReview']=verify_peer()
        source['notes'].append('Wages/indemnity/remuneration are the separate published pay column; the combined Total column includes expenses and is not imported as pay.')
        if manual.get('warning'):warnings.append(manual['warning'])
        if manual.get('note'):source['notes'].append(manual['note'])
        if year=='2022':warnings.append('The officially linked 2022 original has an unsigned approval page with blank dates; adoption is not established by this original.')
    else:
        source['validation']['independentPdfReaders']=['Poppler fixed-width text line state machine','PyMuPDF positioned-word name anchors and cell bands']
        if original['key'].startswith('sooke'):
            source['notes'].append('Remuneration includes salary, wages and taxable benefits paid during the year (cash basis). Expenses include travel, memberships, tuition, relocation, vehicle leases, extraordinary hiring expenses, registration fees and similar amounts outside remuneration.')
            warnings.append('Sooke 2025 prints council remuneration of 172,062 and council expenses of 26,266 on page 37, but carries 172,064 in both council remuneration and council expenses columns on page 38. Page 38 prints total remuneration 8,634,739 and expenses 282,537. These published controls are retained literally; the differences remain unresolved and no cells have been adjusted.')
    bad=[c for c in source['validation']['controls'] if c['residual']]
    if bad:
        warnings.append('Known individual sums differ from printed named controls: '+ '; '.join(f'{c["field"]} {c["knownRowSum"]:,.2f} CAD versus {c["printedNamedControl"]:,.2f} CAD (residual {c["residual"]:+,.2f})' for c in bad)+'. Original row values remain literal; cause unresolved.')
    if warnings:source['publicWarning']=' '.join(warnings)
    return source

def write_handoff(sources, original_receipts, overlap):
    queue=read(BASE/'continuation-2026-11-01/municipal/work-queue.json')
    actions=[]
    prior=[]
    for original in ORIGINALS:
        matching=[t['id'] for t in queue if t['sourceUrl']==original['sourceUrl'] or
                  (original['key']=='sooke-2025' and t['sourceUrl']=='https://media-002-ca.cdn.govstack.com/sooke-012-ca/media/emqbjnxm/2025-statement-of-financial-information.pdf')]
        selected=[s for s in sources if s['sha256']==original['sha256']]
        partial=original['key']=='mcbride-2025'
        prior.append(dict(originalKey=original['key'],priorTaskIds=matching,acceptedSourceIds=[s['id'] for s in selected],
                          disposition='employee scope completed; council remains held for period clarification' if partial else 'exact original processing completed; broader historical discovery not closed'))
        actions.append(dict(id='recovery-municipal-resolved-'+original['key'],employerSlug=original['employerSlug'],employerName=original['employerName'],sector='Municipalities',
                            reportingPeriods=sorted({s['year'] for s in selected}),sourceUrl=original['sourceUrl'],sourceIndexUrl=original['sourceIndexUrl'],
                            status='employee-completed-council-held' if partial else 'resolved-original-processing',route='processing',
                            nextAction='Register the reviewed complete employee cohort; retain separate held council-period clarification.' if partial else 'Register these reviewed original cohorts; preserve source warnings and leave other historical archive tasks open.',
                            reason='Resolves exact original tasks '+', '.join(matching)+'. Sources: '+', '.join(s['id'] for s in selected)+'.'))
    for key,slug,year,reason,next_action in [
        ('mcbride-2022-combined-control','village-of-mcbride','2022',
         'Physical page 39 prints separate council controls 34,965.00 remuneration and 24,087.83 expenses, but a 55,812.83 combined total; separate controls sum to 59,052.83. Named values remain literal. Linked resolved original tasks: continuation-municipal-68afeec9b595ba06, continuation-municipal-e738eb304848f90b.',
         'Draft a clarification of the printed combined total without assigning a cause or changing any value; no message has been sent.'),
        ('mcbride-2025-council-period','village-of-mcbride','2025',
         'Physical page 42 in the 2025 package explicitly says 2024 and differs from council page 45 in the separate 2024 original. Five council rows remain held; employee page 43 independently and coherently identifies 2025. Supersedes the council scope of continuation-municipal-745c924ec3956e1c and continuation-municipal-dbbe229bcb97c4ac.',
         'Locate an official corrected council schedule or draft a period clarification. Do not relabel or import the held rows; no message has been sent.'),
        ('sooke-2025-controls','district-of-sooke','2025',
         'Employee named rows sum to 6,874,288 remuneration and 110,428 known expenses, versus printed 6,874,287 and 110,474. Page 37 council controls are 172,062/26,266, while page 38 carries 172,064 in both council columns and prints combined controls 8,634,739/282,537. All cells remain literal, expense blanks remain null, and no cause is inferred. Linked exact-original processing tasks are listed in resolved-prior-tasks.json.',
         'Draft clarification of named employee and carried council control discrepancies against physical pages 37–38; seek any public corrected original first. No message has been sent.')]:
        original=next(o for o in ORIGINALS if o['key']==('sooke-2025' if slug=='district-of-sooke' else 'mcbride-'+year))
        actions.append(dict(id='recovery-municipal-clarify-'+key,employerSlug=slug,employerName=original['employerName'],sector='Municipalities',reportingPeriods=[year],
                            sourceUrl=original['sourceUrl'],sourceIndexUrl=original['sourceIndexUrl'],status='not-sent-source-clarification',route='clarification-request',nextAction=next_action,reason=reason))
    write(REPORT/'work-queue.json',actions)
    write(REPORT/'resolved-prior-tasks.json',prior)
    write(REPORT/'adoption-evidence.json',APPROVAL)
    write(REPORT/'handoff.json',dict(version=1,verifiedOn=DATE,collection='recovery-municipal',acceptedOriginals=6,acceptedCohorts=len(sources),acceptedRows=sum(s['rowCount'] for s in sources),
                                    acceptedEmployeeCohorts=sum(s['category']==EMP for s in sources),acceptedEmployeeRows=sum(s['rowCount'] for s in sources if s['category']==EMP),
                                    acceptedCouncilCohorts=sum(s['category']==COUNCIL for s in sources),acceptedCouncilRows=sum(s['rowCount'] for s in sources if s['category']==COUNCIL),
                                    newlyCoveredOfficialJurisdictions=3,newlyCoveredEmployeeJurisdictions=3,councilOnlyNewJurisdictions=0,
                                    heldCohorts=1,heldRows=5,heldReason='McBride 2025-package council page 42 says 2024 and conflicts with separate 2024 original.',
                                    sources=[dict(id=s['id'],year=s['year'],scope=s['category'],rows=s['rowCount'],file=s['file'],dataSha256=s['dataSha256'],
                                                  originalSha256=s['sha256'],evidenceFile=s['validation']['evidenceFile'],evidenceSha256=s['validation']['evidenceSha256']) for s in sources],
                                    originals=original_receipts,independentManualPeerReview=verify_peer(),nativeReaderRows=80,manualPeerComparedRows=35,
                                    overlapReview=overlap,adoptionEvidence=APPROVAL,publicWarnings={s['id']:s['publicWarning'] for s in sources if s.get('publicWarning')},
                                    visualReviewCoverage=[dict(key=o['key'],salaryPages=o['pages'],coverPages=[] if o['key'].startswith('midway') else [1],
                                                              approvalPages=[o['approvalPage']],alsoReviewedHeldCouncilPage=42 if o['key']=='mcbride-2025' else None,
                                                              completeSalaryRowsReviewed=True,reviewer='recovery_municipal',
                                                              scope='Specified salary/cover/approval pages only; not every page of the report.') for o in ORIGINALS],
                                    reproduction=['python scripts/recover_wave_municipal.py --verify','python -m unittest discover -s scripts -p test_recover_wave_municipal*.py'],
                                    noGlobalOrExistingCollectionEdits=True,noContactsOrRequestsSent=True))

def build():
    manual = read(OUT/'manual-transcription.json')
    peer = verify_peer()
    sources=[]
    original_receipts=[]
    for original in ORIGINALS:
        assert sha(original['cachePath']) == original['sha256']
        evidence=dict(original=original,reviewer='recovery_municipal',reviewedOn=DATE,
                      visualCoverage=dict(salaryPages=original['pages'],coverPages=[1] if not original['key'].startswith('midway') else [],approvalPages=[original['approvalPage']]),
                      originalImageHashes={})
        for p in original['pages']:
            image_key='midway' if original['key'].startswith('midway') else original['key']
            path=f'/tmp/recovery-municipal-review/{image_key}-p{p}.png'
            evidence['originalImageHashes'][str(p)]=dict(path=path,sha256=sha(path))
        if original['method']=='native':
            evidence['readerInputs']=raw_native(original)
            native_rows=all_native_rows(evidence['readerInputs'],original)
            evidence['independentRows']=native_rows
            if original['key'].startswith('midway'):
                assert sha(APPROVAL['cachePath'])==APPROVAL['sha256']
                evidence['adoptionEvidence']=APPROVAL
            groups=defaultdict(list)
            for item in native_rows:
                year=('2023' if item['row'][5]==9 else '2024') if original['key'].startswith('midway') else original['year']
                groups[(year,item['scope'])].append(item['row'])
            evidence_name='evidence/'+original['key']+'.json.gzip'
            evidence_hash=write(OUT/evidence_name,evidence)
            for (year,scope),rows in groups.items():
                key=original['key'].split('-')[0]+'-'+year+'-'+scope
                sources.append(make_source(original,key,year,scope,rows,evidence_name,evidence_hash))
        else:
            evidence['manualCohorts']=[c for c in manual['cohorts'] if c['key'].startswith(original['key']+'-')]
            evidence['manualTranscriptionSha256']=sha(OUT/'manual-transcription.json')
            evidence['independentPeerReview']=peer
            evidence_name='evidence/'+original['key']+'.json.gzip'
            evidence_hash=write(OUT/evidence_name,evidence)
            for cohort in evidence['manualCohorts']:
                scope=EMP if cohort['key'].endswith(EMP) else COUNCIL
                rows=[[original['employerSlug'],*r[:4],cohort['page']] for r in cohort['rows']]
                sources.append(make_source(original,cohort['key'],cohort['year'],scope,rows,evidence_name,evidence_hash,cohort))
        original_receipts.append(dict(**original,evidenceFile=evidence_name,evidenceSha256=evidence_hash))
    overlap=baseline_overlap(sources)
    write(OUT/'sources.json',dict(version=1,rowSchema=SCHEMA,sources=sources))
    write(REPORT/'originals.json',original_receipts)
    write(REPORT/'overlap-review.json',overlap)
    write_handoff(sources,original_receipts,overlap)
    print(json.dumps(dict(cohorts=len(sources),rows=sum(s['rowCount'] for s in sources),originals=len(original_receipts),employers=sorted({s['employerSlug'] for s in sources}))))

def verify():
    verify_peer()
    manifest=read(OUT/'sources.json')
    for source in manifest['sources']:
        assert sha(OUT/source['file']) == source['dataSha256']
        rows=read(OUT/source['file'])
        assert len(rows)==source['rowCount']
        assert amount_sum(rows,3)==source['totalRemuneration']
        assert amount_sum(rows,4)==source['totalExpenses']
        evidence_path=OUT/source['validation']['evidenceFile']
        assert sha(evidence_path)==source['validation']['evidenceSha256']
        evidence=read(evidence_path)
        if evidence['original']['method']=='native':
            independent=all_native_rows(evidence['readerInputs'],evidence['original'])
            expected=[x['row'] for x in independent if x['scope']==source['category'] and x['row'][5] in source['pages']]
        else:
            cohort=next(c for c in evidence['manualCohorts'] if 'recovery-municipal-'+c['key']==source['id'])
            expected=[[source['employerSlug'],*r[:4],cohort['page']] for r in cohort['rows']]
        assert rows==expected,source['id']
    baseline_overlap(manifest['sources'])
    print('Verified all retained row fields, independent native replay, data/evidence hashes and source/period/scope overlap guard.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--build',action='store_true')
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.build:build()
    if args.verify:verify()
    if not args.build and not args.verify:parser.error('use --build and/or --verify')
