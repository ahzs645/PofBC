#!/usr/bin/env python3
"""Deterministically materialize complete PHSA source candidates and provenance.

Every field must have an explicit closed evidence route. This emits held review
candidates only; source acceptance/status promotion is a separate peer/root gate.
"""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

import finish_salary_phsa_ledger as ledger

ROOT=ledger.ROOT
AREA=ledger.AREA
COLLECTION=ledger.COLLECTION
REVIEWS=ledger.REVIEWS
SLUG='provincial-health-services-authority'
ALLOWED={'manual-original-image','manual-qualified-source-typography','manual-blind-source-holdout',
         'calibrated-paired-reader-confidence-corroboration','original-source-explicit-dash-geometry',
         'baseline-independent-reader-agreement'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def packed(value):return gzip.compress(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode(),mtime=0)


def save(path,data,check=False):
    if isinstance(data,dict):data=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
    if check:
        if path.read_bytes()!=data:raise ValueError('Final source bytes do not replay: '+str(path))
    else:
        if path.exists():
            if path.read_bytes()!=data:raise ValueError('Never replace an emitted source candidate: '+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(data)}


def validate_source(source,inventory):
    if (source['sourceId'],source['sourceSha256'])!=(inventory['id'],inventory['sourceSha256']):
        raise ValueError('Candidate source identity differs from pinned inventory')
    if not source['completePhysicalSource'] or source['pendingFields']:
        raise ValueError('Source is incomplete or still has unresolved fields: '+source['sourceId'])
    if type(source['rowCount'])is not int or source['rowCount']!=len(source['rows']) or source['rowCount']<=0:raise ValueError('Missing literal salary scope')
    physical=source['physicalPages'];pns=[p['physicalPage']for p in physical]
    if pns!=list(range(1,inventory['pdfPages']+1)) or any(type(p['physicalPage'])is not int or type(p['rows'])is not int or p['rows']<0 for p in physical):
        raise ValueError('Incomplete/duplicate/reordered physical source pages')
    if sum(p['rows']for p in physical)!=source['rowCount']:raise ValueError('Physical page row counts differ from payload')
    expected_rows=[(p['physicalPage'],rn)for p in physical for rn in range(1,p['rows']+1)]
    seen=set();previous=(0,0);rows=[]
    for entry in source['rows']:
        final=entry['row'];raw=entry['rawCandidateRow'];pn=final[5];rn=entry['sourceRowOnPage'];key=(pn,rn)
        if type(pn)is not int or type(rn)is not int or rn<1:raise ValueError('Noninteger/boolean physical source locator')
        if key in seen or key<=previous:raise ValueError('Source row order/multiplicity changed')
        previous=key;seen.add(key)
        if len(final)!=6 or final[0]!=SLUG or final[2] is not None or not (1<=pn<=inventory['pdfPages']):
            raise ValueError('Invalid PHSA employer/title/page scope')
        if [final[i] for i in [0,2,5]]!=[raw[i] for i in [0,2,5]]:raise ValueError('Unauthorized non-field change')
        if not isinstance(final[1],str) or not final[1].strip():raise ValueError('Missing literal source name')
        if type(final[3]) is not int or (final[4] is not None and type(final[4]) is not int):
            raise ValueError('Unparsed/noninteger/boolean money remains held')
        for field,index in ledger.FIELDS.items():
            proof=entry['fields'][field];status=proof['status']
            if status not in ALLOWED:raise ValueError('Unclosed field evidence route')
            if status=='manual-qualified-source-typography' and field!='name':raise ValueError('Typography cannot waive money')
            if final[index]!=raw[index] and not status.startswith('manual-'):raise ValueError('Automated route cannot change a source field')
            if field!='name' and final[index] is not None and final[index]<=0 and not status.startswith('manual-'):
                raise ValueError('Zero/negative money requires original-image coverage')
            if field=='expenses' and final[index] is None and status not in ['manual-original-image','manual-blind-source-holdout','original-source-explicit-dash-geometry']:
                raise ValueError('Unknown expense needs actual source dash/image evidence')
        rows.append(final)
    if [(r['row'][5],r['sourceRowOnPage'])for r in source['rows']]!=expected_rows:
        raise ValueError('Missing/duplicate/reordered physical-page source-row sequence')
    return rows


def warning(source,context):
    parts=['Fiscal-year remuneration above the disclosure threshold is not an annual salary rate or a workforce census. Expenses may include third-party supplier payments; original expense dashes remain unknown (null). The published standalone schedule is unsigned and does not establish board approval.']
    qualified=source['rootAdoptedQualifiedNameCases']
    if qualified:
        kinds=collections.Counter(q.get('qualificationKind',q['originalCaseEvidence'].get('ambiguityKind','I-l-source-case')) for q in qualified)
        if not kinds['rn-m-source-segmentation'] and not kinds['exact-root-bound-source-name-alternatives']:
            parts.append(f"{len(qualified)} source-name readings have an explicit contextual capital-I/lowercase-l qualification. Their exact affected rows, primary readings, visible alternatives and independently reviewed/root-adopted context are retained in provenance; glyph case is not claimed to be proved by pixels.")
        else:
            description=[]
            if kinds['I-l-source-case']:description.append(f"{kinds['I-l-source-case']} contextual capital-I/lowercase-l readings")
            if kinds['rn-m-source-segmentation']:description.append(f"{kinds['rn-m-source-segmentation']} visually ambiguous rn/m segmentations")
            if kinds['exact-root-bound-source-name-alternatives']:description.append(f"{kinds['exact-root-bound-source-name-alternatives']} separately root-adopted exact finite source-name alternatives")
            parts.append('Qualified source-name interpretations include '+', '.join(description)+'. Their exact affected rows, primary readings, finite visible alternatives and independently reviewed/root-adopted context are retained in provenance; a unique glyph interpretation is not claimed.')
    if source['sourceId']=='phsa-2015-16':
        parts.append('Zulfiqar,Muhammad* retains the printed $481,982 current-period payment. The source footnote reports $333,272 salary, $19,724 MOCAP/retroactive pay and a $128,986 correction of 2014/15 unpaid-leave coding reported in 2015/16; no amount was subtracted, annualized or moved to another year.')
    if source['sourceId']=='phsa-2017-18':
        parts.append('The cover category counts sum to 5,073, while its named headline and the complete original salary schedule contain 5,072 observations. The discrepancy is preserved without an inferred cause.')
    if source['sourceId']=='phsa-2018-19':
        parts.append('The complete original salary schedule contains 6,041 observations, while the cover headline states 6,042 and its category counts sum to 6,025 (17 below the headline). No missing observation was manufactured.')
    pay,expense=source['diagnosticControlResiduals']
    if pay or expense:
        controls=source['sourcePrintedControls']
        parts.append(f"Literal row sums are remuneration ${source['diagnosticRemunerationSum']:,} and known expenses ${source['diagnosticKnownExpenseSum']:,}, differing from printed controls ${controls['remuneration']:,}/${controls['expenses']:,} by {pay:+,}/{expense:+,}. No source cell was adjusted to balance; the cause is not established.")
    return ' '.join(parts)


def source_pins(references,source_id):
    """Identity comes from hash-pinned JSON, never a filename substring."""
    return [reference for reference in references if ledger.pinned(reference)['sourceId']==source_id]


def make(source,inventory,context,full_ledger,check=False,revision=2):
    rows=validate_source(source,inventory);key=source['sourceId'];year=inventory['year'];start=int(year[:4]);end=start+1
    file=key+'-employees'+(f'-v{revision}' if revision>=3 else '')+'.json.gzip';data=packed(rows);data_pin=save(COLLECTION/file,data,check)
    provenance={'version':2,'sourceId':key,'sourceSha256':inventory['sourceSha256'],
                'dataSha256':data_pin['sha256'],'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],
                'sourceInventory':full_ledger['sourceInventory'],'processingProfiles':full_ledger['processingProfiles'],
                'fieldPolicy':full_ledger['fieldPolicy'],'sourceContextControls':full_ledger['sourceContextControls'],
                'independentOriginalRowGeometry':full_ledger['independentOriginalRowGeometry'],
                'manualOverlayInputs':source_pins(full_ledger['manualOverlayInputs'],key),
                'rootHoldoutComparisons':source_pins(full_ledger['rootHoldoutComparisons'],key),
                'originalRowsAndPerFieldResolution':source,'allNineSourceHoldoutsPassed':full_ledger['allNineSourceHoldoutsPassed'],
                'allNineHoldoutReviewerReadingCorrectionsDisclosed':full_ledger['holdoutReviewerReadingCorrectionsDisclosed'],
                'noImplicitIdentityCasingMoneyBalanceOrPeriodReassignment':True}
    selections=source_pins(full_ledger.get('manualOverlaySupersessions',[]),key)
    if selections:provenance['manualOverlaySupersessions']=selections
    archives=[]
    for path in sorted((AREA/'triangulation').glob('archived-source-money-views-*.json')):
        archive=json.loads(path.read_text())
        references=archive.get('peerComparisons',[archive['sourcePeer']]if 'sourcePeer'in archive else [])
        if not references:raise ValueError('Source-money archive has no exact peer provenance')
        peers=[ledger.pinned(reference)for reference in references]
        if any(peer.get('sourceId')==key for peer in peers):archives.append(ledger.pin(path))
    if archives:provenance['archivedExactSourceMoneyViews']=archives
    if len(provenance['rootHoldoutComparisons'])!=1:raise ValueError('Exactly one closed source-specific holdout receipt is required')
    suffix=f'-v{revision}'
    provenance_name='evidence/'+key+'-provenance'+suffix+'.json.gzip'
    provenance_pin=save(COLLECTION/provenance_name,packed(provenance),check)
    source_warning=warning(source,context)
    field_counts=source['fieldResolutionCounts'];routes=collections.Counter()
    for counts in field_counts.values():routes.update(counts)
    notes=[context['literalScope'],
           'The literal remuneration column is retained. No annual salary rate or missing compensation component is inferred; nothing is annualized.',
           'No job titles are published: all positions are null. The reporting entity remains the printed Provincial Health Services Authority; no unit assignment or cross-year identity is inferred.',
           'Two independent OCR engines read every original salary page. Actual PDF-painted RGB 300-dpi source bytes and all original row boundaries have independent complete-source checks.',
           'Original reader streams/confidences/flags and all frozen review packets remain immutable. Every true disagreement, missing/unparsed field and source-name artifact is image resolved. A separately calibrated policy corroborates eligible unreserved confidence-only fields by exact independent agreement and source guards; these are not labelled personal image transcription.',
           'Ninety deterministic source-only holdout rows (222 fields across all nine layouts) independently matched the final source readings. Four reviewer-only first-pass name errors are preserved transparently in additive reread evidence; no machine data was changed by the holdout.',
           'Expense dashes require source-specific actual-image geometry or literal image review; blank regions or absent OCR detections never imply a dash or zero.',
           'Original physical pages, repeated names/observations and source order are preserved. No deduplication or generic name casing is performed.',
           'Compiled observations remain retained until root independently proves and adopts exact replacement scope.']
    if context['cashRemunerationComponentDefinitionPersonallySeenOnCover']:
        notes.append('This source cover defines remuneration as '+context['cashComponentDefinition'])
    else:notes.append(context['componentDefinitionLimit'])
    validation={'completeEmployeeSchedule':True,'independentlyComparedRows':len(rows),'physicalPdfPages':inventory['pdfPages'],
                'salaryPhysicalPages':[p['physicalPage'] for p in source['physicalPages'] if p['rows']],
                'originalNamedRows':len(rows),'originalPrintedNamedCount':context['printedNamedAboveThresholdCount'],
                'printedActiveEmployeeCountIsSeparateFromNamedRoster':context['printedActiveEmployeeCountNotNamedRoster'],
                'fieldResolutionCounts':field_counts,'resolutionRouteCounts':dict(routes),
                'personallyImageReviewedFieldCount':sum(v for k,v in routes.items() if k.startswith('manual-')),
                'calibratedPairedReaderConfidenceOnlyFieldCount':routes['calibrated-paired-reader-confidence-corroboration'],
                'sourceExplicitDashGeometryFieldCount':routes['original-source-explicit-dash-geometry'],
                'rootAdoptedQualifiedNameCases':source['rootAdoptedQualifiedNameCases'],
                'sourcePrintedControls':source['sourcePrintedControls'],'sourceControlResiduals':source['diagnosticControlResiduals'],
                'unknownExpenseRows':source['expenseNullRows'],'explicitZeroExpenseRows':source['explicitZeroExpenseRows'],
                'negativeExpenseRows':source['negativeExpenseRows'],'allNineSourceHoldoutsPassed':full_ledger['allNineSourceHoldoutsPassed'],
                'holdoutReviewerReadingCorrectionsAcrossNineSources':full_ledger['holdoutReviewerReadingCorrectionsDisclosed'],
                'allOriginalRawFlagsPreserved':True,'allActualImageDisagreementsResolved':True,
                'personalImageTranscriptionNotClaimedForEveryCell':True,
                'finalIndependentSourceClosureAndRootAcceptanceStillRequired':True}
    evidence={'sourceId':key,'sourceSha256':inventory['sourceSha256'],'data':data_pin,'provenance':provenance_pin,
              'validation':validation,'publicWarning':source_warning,'sourceNotes':context['sourceNotes'],
              'status':'held-for-peer-review','noAcceptanceClaim':True}
    evidence_name='evidence/'+key+'-validation'+suffix+'.json';evidence_pin=save(COLLECTION/evidence_name,evidence,check)
    result={'id':'queue-completion-'+key+'-employees','employerSlug':SLUG,'employerName':'Provincial Health Services Authority',
            'sector':'Health authorities','title':'Provincial Health Services Authority employee remuneration and expenses '+year,
            'year':year,'periodType':'fiscal','periodStart':f'{start}-04-01','periodEnd':f'{end}-03-31',
            'sourceUrl':inventory['sourceUrl'],'sourceIndexUrl':inventory['sourceIndexUrl'],'sha256':inventory['sourceSha256'],
            'pdfBytes':inventory['pdfBytes'],'sourceKind':'official','file':file,'dataSha256':data_pin['sha256'],
            'rowCount':len(rows),'totalRemuneration':source['diagnosticRemunerationSum'],
            'totalExpenses':source['diagnosticKnownExpenseSum'],'totalDisclosedExpenses':source['diagnosticKnownExpenseSum'],
            'status':'held-for-peer-review','category':'employee-remuneration','scope':'employee-remuneration',
            'threshold':75000,'thresholdComparison':'>','currency':'CAD','nameDisclosure':'named',
            'completeEmployeeSchedule':True,'publicationStatus':'official-published-unsigned-standalone-schedule',
            'retainCompiledPartition':True,'notes':notes,'publicWarning':source_warning,'validation':validation,
            'evidenceFile':evidence_name,'evidenceSha256':evidence_pin['sha256'],
            'provenanceFile':provenance_name,'provenanceSha256':provenance_pin['sha256']}
    save(AREA/'candidates'/(key+'-source'+suffix+'.json'),result,check)
    return result


def run(source_filter=None,check=False,revision=2):
    if revision<2:raise ValueError('First held provenance snapshots are archived; corrected replay starts at version2')
    # Reuse the pre-selection immutable inventory/profile pins. The finalizer
    # must not silently materialize metadata from an unpinned revised inventory.
    import finish_salary_phsa_holdouts as holdouts
    if sha(holdouts.CONFIG.read_bytes())!=holdouts.CONFIG_SHA:raise ValueError('Pre-selection source configuration changed')
    config=json.loads(holdouts.CONFIG.read_text())
    inventory_value=holdouts.pinned(config['sourceInventory'],AREA/'source-inventory.json')
    policy_value=holdouts.pinned(config['policy'],ledger.policy.POLICY)
    profiles=holdouts.pinned(policy_value['processingProfiles'],AREA/'processing-profile-index-001.json')
    for reference in profiles['sourceProfiles']:holdouts.pinned(reference)
    full=ledger.build(source_filter,verify_overlays=True)
    if not full['allNineSourceHoldoutsPassed']:raise ValueError('All nine source-specific holdouts must pass before materialization')
    inventory={s['id']:s for s in inventory_value['sources']}
    contexts={s['sourceId']:s for s in json.loads((REVIEWS/'independent-phsa-history-source-context-controls.json').read_text())['sources']}
    result=[make(s,inventory[s['sourceId']],contexts[s['sourceId']],full,check,revision) for s in full['sources']]
    if source_filter is None:
        if len(result)!=9:raise ValueError('The complete nine-source set is required')
        # Held research snapshots remain replayable after the separately
        # root-adopted active manifest is promoted to verified status.
        save(AREA/'candidates'/f'sources-v{revision}.json',{'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':result},check)
    print(json.dumps([{'sourceId':s['id'],'dataSha256':s['dataSha256'],'rowCount':s['rowCount'],'status':s['status']} for s in result]))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',action='append');p.add_argument('--check',action='store_true');p.add_argument('--revision',type=int,default=2);a=p.parse_args()
    run(a.source,a.check,a.revision)
