#!/usr/bin/env python3
"""Independent native readers for the consistently dated SD8 board-agenda SOFI."""
import argparse
import collections
import gzip
import json
import re
import subprocess
from decimal import Decimal

import resolve_held_schools as s

PDF=s.CACHE/'sd08-sep2026-agenda.pdf'
SHA='aed4f0e7026a198429707247d6cccf49c18c72bdfaefc62e0bb7bd65dafbf8b4'
URL='https://www.sd8.bc.ca/sites/default/files/documents/2026-09/2026.09.08%20-%204%20Public%20Agenda_FINAL_2.pdf'
FINAL_PDF=s.CACHE/'sd08-current-sofi-2026.pdf'
FINAL_SHA='b9a2483c8a81e0414c1e55d620cfe234fcba6af1f4e2d8388ed59e492cc2d47f'
FINAL_URL='https://sd8.bc.ca/sites/default/files/documents/2026-09/2025-2026%20SOFI%20Report_Final_Redacted_0.pdf'
FINAL_PAGES=list(range(51,60))
ID='held-resolution-schools-sd08-2026-employees'
PEER_REVIEW={'file':'research/salaries/held-resolution-2026-11-01/reviews/independent-sd8-comparison.json',
             'sha256':'62e907b8d4356bdaf24c331bab1e5ef777af20d3ff42dd1a507d46be5245e793'}
PAGES=list(range(185,194))
WARNING=('The posted SOFI employee schedule has conflicting years: physical page 52 prints June 30, 2025, '
         'while its other employee pages print June 30, 2026. The assigned 2025/26 period is supported by all 340 '
         'matching employee rows in the separately published September 8, 2026 board agenda, whose complete '
         'salary schedule on pages 185–193 consistently prints June 30, 2026 and is introduced by a dated memorandum. '
         'Names, remuneration, expenses, order and multiplicity agree across both originals under page mapping +134. '
         'The conflicting finance heading remains literal; no typo or cause is asserted. The agenda financial-statement '
         'subsection contains DRAFT/Not Finalized marks, while its remuneration pages are unmarked. The agenda is '
         'period corroboration, not the payment-source original or proof of final adoption. Posted SOFI signature areas '
         'are redacted; its declaration date fields read September 8, 2026. The minutes record SOFI presentation, not '
         'an explicit adoption motion. The named employee controls reconcile exactly. Elsewhere, posted SOFI '
         'reconciliation page 64 prints $56,431,182 remuneration and $594,827 expenses, while schedule page 59 prints '
         '$56,431,196 and $594,437 respectively: reconciliation minus schedule is −$14 remuneration and +$390 expenses. '
         'Both sets remain literal; their cause is unresolved.')


def poppler_rows(text, pages=PAGES):
    rows=[];active=False;controls=None
    pattern=re.compile(r'^\s*([^\d]+?\S)\s+(\d[\d,]*)\s+(\d[\d,]*|-)\s*(\*{0,2})\s*$')
    for page in pages:
        t=text.split('\f')[page-1]
        expected_year=2025 if pages==FINAL_PAGES and page==52 else 2026
        assert re.search(r'the Fiscal Year Ended June 30, '+str(expected_year),t), page
        for line in t.splitlines():
            if 'Detailed Employees >' in line:active=True;continue
            if line.strip().startswith('Total for Employees >'):
                vals=re.findall(r'\d[\d,]*',line);controls=[s.amount(v) for v in vals[-2:]]
            m=pattern.fullmatch(line)
            if not active or not m:continue
            name,pay,exp,marker=m.groups()
            if ',' not in name:continue
            assert Decimal(s.amount(pay))>75000
            rows.append({'name':s.clean(name),'position':None,'remuneration':s.amount(pay),'expenses':s.amount(exp),
                         'pdfPage':page,'category':'employee-remuneration','sourceExpenseFootnoteMarker':marker or None,
                         'popplerSourceLine':line})
    assert controls==['37683809','414506'],controls
    assert len(rows)==340,len(rows)
    return rows


def mupdf_rows(path, pages=PAGES):
    import fitz
    doc=fitz.open(path);rows=[]
    for page in pages:
        groups=[]
        for w in sorted(doc[page-1].get_text('words'),key=lambda w:((w[1]+w[3])/2,w[0])):
            y=(w[1]+w[3])/2
            g=next((g for g in groups[-3:] if abs(g['y']-y)<2),None)
            if g is None:g={'y':y,'words':[]};groups.append(g)
            g['words'].append(w)
        bounds=[333.1045837402344,429.6269226074219] if page==pages[0] else [353.54010009765625,457.079345703125]
        for group in groups:
            cols=[[],[],[]];words=sorted(group['words'],key=lambda w:w[0])
            for w in words:
                if w[4]=='$':continue
                cols[sum(w[0]>=b for b in bounds)].append(w[4])
            name,pay,exp=[s.clean(' '.join(c)) for c in cols]
            if name.lower().startswith(('total','consolidated','notes')):continue
            if ',' not in name or not re.fullmatch(r'\d[\d,]*',pay):continue
            if Decimal(s.amount(pay))<=75000:continue
            m=re.fullmatch(r'(\d[\d,]*|-)\s*(\*{0,2})',exp)
            assert m,(page,name,exp)
            rows.append({'name':name,'position':None,'remuneration':s.amount(pay),'expenses':s.amount(m[1]),
                         'pdfPage':page,'category':'employee-remuneration','sourceExpenseFootnoteMarker':m[2] or None,
                         'mupdfWords':[{'text':w[4],'bbox':[round(x,3) for x in w[:4]]} for w in words]})
    assert len(rows)==340,len(rows)
    return rows


def read_original():
    assert s.sha(PDF.read_bytes())==SHA
    text=subprocess.check_output(['pdftotext','-layout',str(PDF),'-']).decode()
    first,second=poppler_rows(text),mupdf_rows(PDF)
    assert s.fields(first)==s.fields(second)
    assert [r['sourceExpenseFootnoteMarker'] for r in first]==[r['sourceExpenseFootnoteMarker'] for r in second]
    return first,second,text


def read_final_original():
    assert s.sha(FINAL_PDF.read_bytes())==FINAL_SHA
    text=subprocess.check_output(['pdftotext','-layout',str(FINAL_PDF),'-']).decode()
    first,second=poppler_rows(text,FINAL_PAGES),mupdf_rows(FINAL_PDF,FINAL_PAGES)
    assert s.fields(first)==s.fields(second)
    assert [r['sourceExpenseFootnoteMarker'] for r in first]==[r['sourceExpenseFootnoteMarker'] for r in second]
    return first,second,text


def held_comparison(rows, offset=134):
    held_sources=json.loads((s.ROOT/'research/salaries/continuation-2026-11-01/schools/held-candidates.json').read_text())
    held=next(h for h in held_sources if h['id']=='continuation-schools-sd08-2026-employees')
    raw=(s.ROOT/'research/salaries/continuation-schools'/held['provenanceFile']).read_bytes()
    assert s.sha(raw)==held['provenanceSha256']
    old=json.loads(gzip.decompress(raw))['rows']
    keys=['name','position','remuneration','expenses']
    a=[[r[k] for k in keys] for r in old];b=[[r[k] for k in keys] for r in rows]
    assert a==b and len(a)==340
    assert all(new['pdfPage']==prior['pdfPage']+offset for prior,new in zip(old,rows))
    return {'heldSourceId':held['id'],'heldOriginalSha256':held['sha256'],'heldDataSha256':held['dataSha256'],
            'heldProvenanceSha256':held['provenanceSha256'],'fieldsCompared':keys,'rowsCompared':340,
            'orderMultiplicityAndAllLiteralFieldsExact':True,'physicalPageMapping':('agenda page = finance-copy page + 134' if offset else 'same finance-copy physical pages'),
            'conflict':'finance copy physical52 prints2025; agenda physical186 prints2026 over the same41rows',
            'newObservationPeriodBasis':'Independent agenda source own explicit2026table headings and dated September8,2026 memorandum; no filename inference'}


def build_source():
    first,second,text=read_final_original();comparison=held_comparison(first,0)
    agenda_first,agenda_second,agenda_text=read_original();agenda_comparison=held_comparison(agenda_first)
    context=json.loads((s.RESEARCH/'sd08-period-and-version-evidence.json').read_text())
    proof={'version':1,'sourceSha256':FINAL_SHA,'rows':first,'independentRows':second,'heldComparison':comparison,
           'agendaCorroborationOriginalSha256':SHA,'agendaCorroborationRows':agenda_first,
           'independentAgendaCorroborationRows':agenda_second,'agendaToFinalComparison':agenda_comparison,
           'periodAndVersionEvidence':context,'printedControlTotals':['37683809','414506'],
           'fullSourcePagesPopplerText':{str(p):text.split('\f')[p-1] for p in [1,3,5,*FINAL_PAGES,60,64,65]},
           'agendaContextPagesPopplerText':{str(p):agenda_text.split('\f')[p-1] for p in [2,134,135,137,139,*PAGES,194,198,199]}}
    normalized=s.normalized({'employerSlug':'school-district-08'},first)
    data,raw=s.packed(normalized);evidence,_=s.packed(proof);key='sd08-2026-employees'
    (s.COLLECTION/f'{key}.json.gzip').write_bytes(data);(s.COLLECTION/f'{key}-evidence.json.gzip').write_bytes(evidence)
    source={'id':ID,'employerSlug':'school-district-08','employerName':'School District No. 8 (Kootenay Lake)',
            'sector':'School districts','year':'2025/26','slug':'2025-26','periodType':'fiscal','periodStart':'2025-07-01','periodEnd':'2026-06-30',
            'title':'School District No. 8 (Kootenay Lake), year ended June 30, 2026: employees with dated board-agenda corroboration',
            'sourceUrl':FINAL_URL,'sourceIndexUrl':'https://sd8.bc.ca/finance','sha256':FINAL_SHA,
            'file':f'{key}.json.gzip','dataSha256':s.sha(data),'normalizedSha256':s.sha(raw),
            'provenanceFile':f'{key}-evidence.json.gzip','provenanceSha256':s.sha(evidence),
            'category':'employee-remuneration','scope':'employee-remuneration','scopeDescription':'Complete published employee remuneration schedule over $75,000; trustees and all aggregates excluded',
            'currency':'CAD','amountUnit':'dollars','amountPrecision':'whole-dollars','nameDisclosure':'published-name-as-disclosed','positionDisclosure':'not-published',
            'rowCount':340,'totalRemuneration':37683809.0,'totalExpenses':414506.0,'pages':FINAL_PAGES,
            'status':'verified','sourceKind':'official','verifiedOn':'2026-11-01','completeEmployeeSchedule':True,'publicWarning':WARNING,
            'notes':['Payment-source rows come from the separately posted SOFI. A dated September 8, 2026 official agenda memorandum and its complete matching employee schedule establish period corroboration: all nine agenda salary pages explicitly print June 30, 2026.',
                     'All 340 employee rows agree between independent Poppler lexical lines and PyMuPDF geometric columns, including null dash expenses, exact names, page boundaries, order and multiplicity. No positions are inferred.',
                     'Every literal name and monetary component agrees with the previously held finance-copy table and both independent agenda readers. The agenda page186 and finance-copy page52 have different year headings; the printed2025heading remains in source evidence and is not silently repaired.',
                     'Remuneration and expenses are separate cash-basis reported payments, not annual base salary. Source reconciliation says salary amounts recovered from third parties remain in SOFI remuneration; no recovery adjustment is made.',
                     'Trustees already accepted from another original are not reimported. Below-threshold aggregates, supplier payments, CPP/EI employer premiums and financial-statement totals are excluded from person rows.',
                     'Expense footnote markers remain in row evidence: source identifies international-program travel and travel to schools. Asterisk annotations are not extra monetary components.'],
            'validation':{'originalFingerprintVerified':True,'independentReaders':['Poppler lexical native rows','PyMuPDF independent geometric columns'],
                          'rowsIndependentlyChecked':340,'completeRowTextAmountsOrderAndMultiplicityAgree':True,'completeEmployeeSchedule':True,
                          'rowsByPhysicalPage':dict(collections.Counter(str(r['pdfPage']) for r in first)),
                          'componentColumns':['remuneration','expenses'],'printedControlTotals':['37683809','414506'],
                          'computedComponentTotals':s.totals(first),'controlResiduals':['0','0'],'summaryReconciles':True,
                          'allPublishedNamedControlsExact':True,'allPrintedComponentControlsExact':False,
                          'knownExpenseValueCount':sum(r['expenses'] is not None for r in first),
                          'aggregateReconciliationPrintedMinusScheduleControls':['-14','390'],
                          'periodEvidenceFile':'research/salaries/held-resolution-2026-11-01/schools/sd08-period-and-version-evidence.json',
                          'periodEvidenceSha256':s.sha((s.RESEARCH/'sd08-period-and-version-evidence.json').read_bytes()),
                          'periodHeadingConflictInChosenSource':True,'periodResolvedByCompleteDatedRowCorroboration':True,
                          'corroborationSourceUrl':URL,'corroborationOriginalSha256':SHA,'corroborationPhysicalPages':PAGES,
                          'agendaFinancialStatementSubsectionMarkedDraft':True,'agendaSalaryPagesMarkedDraft':False,
                          'chosenPaymentSourceMarkedDraft':False,'chosenPaymentSourceSignatureAreasRedacted':True,
                          'chosenPaymentSourceDeclarationDates':'September 8, 2026',
                          'independentNativePeerReview':PEER_REVIEW,'independentThirdReader':'PDFMiner nested Form-XObject cell grouping',
                          'completeIndependentPeerReviewPending':False,
                          'SOFIAdoptionMotionEstablished':False,'heldVersionFullRowComparison':comparison}}
    return source


def verify_source(source,proof,originals=False):
    assert source['sha256']==proof['sourceSha256']==FINAL_SHA
    assert s.fields(proof['rows'])==s.fields(proof['independentRows'])
    assert len(proof['rows'])==source['rowCount']==340
    assert s.totals(proof['rows'])==source['validation']['computedComponentTotals']==['37683809','414506']
    assert source['publicWarning']==WARNING
    assert held_comparison(proof['rows'],0)==proof['heldComparison']
    assert held_comparison(proof['agendaCorroborationRows'])==proof['agendaToFinalComparison']
    assert s.fields(proof['agendaCorroborationRows'])==s.fields(proof['independentAgendaCorroborationRows'])
    context=(s.RESEARCH/'sd08-period-and-version-evidence.json').read_bytes()
    assert s.sha(context)==source['validation']['periodEvidenceSha256']
    assert json.loads(context)==proof['periodAndVersionEvidence']
    data,raw=s.packed(s.normalized(source,proof['rows']))
    assert s.sha(data)==source['dataSha256'] and s.sha(raw)==source['normalizedSha256']
    assert data==(s.COLLECTION/source['file']).read_bytes()
    peer_bytes=(s.ROOT/PEER_REVIEW['file']).read_bytes();assert s.sha(peer_bytes)==PEER_REVIEW['sha256']
    peer=json.loads(peer_bytes)['candidate']
    assert peer['dataSha256']==source['dataSha256'] and peer['provenanceSha256']==source['provenanceSha256']
    assert peer['rowCount']==340 and peer['allSixFieldsExact'] and peer['multiplicityAndFullMultisetExact']
    if originals:
        first,second,text=read_final_original()
        assert first==proof['rows'] and second==proof['independentRows']
        first,second,text=read_original()
        assert first==proof['agendaCorroborationRows'] and second==proof['independentAgendaCorroborationRows']


def main():
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--originals',action='store_true');args=p.parse_args()
    path=s.COLLECTION/'sources.json';manifest=json.loads(path.read_text())
    if args.build:
        source=build_source();manifest['sources']=[r for r in manifest['sources'] if r['id']!=ID]+[source]
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    source=next(r for r in manifest['sources'] if r['id']==ID)
    raw=(s.COLLECTION/source['provenanceFile']).read_bytes();assert s.sha(raw)==source['provenanceSha256']
    verify_source(source,json.loads(gzip.decompress(raw)),args.originals)
    print('Verified SD8 final SOFI employees with dated agenda corroboration: 340 rows, all native fields exact')


if __name__=='__main__':main()
