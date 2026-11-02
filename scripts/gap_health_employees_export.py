#!/usr/bin/env python3
"""Prepare source-reviewed normalized health payloads; never register or publish.

The original primary extraction remains immutable evidence. An independently
image-read M.S. row is inserted at its actual printed location; no identity is
expanded and no monetary control supplies a value. Parent acceptance and the
remaining clipping review are required before any source status can be verified.
"""
import collections,copy,gzip,hashlib,json,pathlib,re
from decimal import Decimal
from gap_health_employees_fetch import ROOT,AREA,sha
from gap_health_employees_native import load,nameclean
from gap_health_employees_verification import clip_readings,null_adoptions,CLIP_SELECTION,CLIP_SELECTION_SHA,NULL_ADOPTION,NULL_ADOPTION_SHA,CONTEXT_ACCEPTANCE,CONTEXT_ACCEPTANCE_SHA

COLLECTION=ROOT/'research/salaries/gap-fill-health-employees'
FIRST_INDEX='research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/first-transcript-index.json'
FIRST_SHA='539fec65b1c7095b4b656ae8dec12f10ef1c30b12a979a35970f6898b1c0662c'
CURRENT_SELECTION='research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/current-reading-selection.json'
CURRENT_SHA='af3147662444fd25546b59d988f74a3ff3ce3064e392ff184b8c8042181116a3'
ADDITIVE='research/salaries/gap-fill-2026-11-02/health_boards/peer-health-employees/additive-reread-001.json'
ADDITIVE_SHA='c414982b6cc108452c38f6d3dd38f928e319478b6bcffee08ea31673b547aab7'

def pinned(path,expected):
    raw=(ROOT/path).read_bytes()
    if sha(raw)!=expected:raise ValueError(('Selected source-review bytes changed',path))
    return json.loads(raw)

def peer_readings():
    first=pinned(FIRST_INDEX,FIRST_SHA);pinned(CURRENT_SELECTION,CURRENT_SHA);change=pinned(ADDITIVE,ADDITIVE_SHA);rows={}
    if first['candidateValuesSeen'] is not False or change['candidateAmountsSeenBeforeFreshReading'] is not False:raise ValueError('First/fresh peer candidate-value withholding changed')
    for ref in first['files']:
        doc=pinned(ref['path'],ref['sha256'])
        for row in doc['observations']:
            if row['id'] in rows:raise ValueError('Repeated peer target')
            rows[row['id']]=copy.deepcopy(row)
    if set(c['id'] for c in change['corrections'])!={'health-reader-001-011','health-reader-001-051','health-reader-001-062'}:raise ValueError('Unexpected peer supersession scope')
    for c in change['corrections']:
        old=rows[c['id']]
        for key in ['sourceKey','sourceSha256','physicalPage','nameLiteral','expenses']:
            if old[key]!=c[key]:raise ValueError(('Peer fresh reread changed another field',c['id'],key))
        if old['remuneration']!=c['oldRemuneration']:raise ValueError('Peer predecessor amount changed')
        rows[c['id']]['remuneration']=c['freshRemuneration']
    if len(rows)!=88:raise ValueError('Expected the exact88source-image target readings')
    return rows

def definitions(context):
    first=context['firstSalaryPage']['layoutText'];last=context['lastSalaryPage']['layoutText'];text=first+'\n'+last
    paragraphs=[]
    for block in re.split(r'\n\s*\n',text):
        value=' '.join(block.split())
        if any(word in value.lower() for word in ['remuneration includes','expenses includes','travel and expenses includes','travel & expenses includes','cash basis','accrual basis','taxable benefits','employer portion','27 bi-weekly']):paragraphs.append(value)
    safe=[]
    for value in paragraphs:
        if len(value)>1800 or any(re.search(r'[A-Z][A-Z]+,[A-Z].*\d{2},\d{3}',part) for part in value.split('  ')):
            continue
        safe.append(value)
    return list(dict.fromkeys(safe))

def named_control(context):
    for row in context['allPrintedControls']:
        if re.search(r'equal.*greater|greater.*75|over.*75|(?:total|employees)\s*>\s*\$?75|remuneration exceeding',row['label'],re.I):return row
    return None

def build():
    peer=peer_readings();clip=clip_readings();nulls=null_adoptions();closure_path=AREA/'source-verification-closure.json';closure=json.loads(closure_path.read_bytes());assert closure['finalRowsExpected']==207001 and len(closure['readerFlagDecisions'])==93 and len(closure['sourceImageTargetDecisions'])==352;proof_by_key={r['key']:r for r in closure['sources']};originals={x['sourceSha256']:x for x in json.loads((AREA/'recovered-employee-originals-v2.json').read_bytes())};contexts={x['sourceSha256']:x for x in json.loads((AREA/'source-context-review-packet.json').read_bytes())['sources']};evidence={x['sourceSha256']:x for x in json.loads((AREA/'native-reader-evidence-index-v2.json').read_bytes())};index=json.loads((AREA/'native-primary-candidate-index.json').read_bytes());COLLECTION.mkdir(exist_ok=True);sources=[];summaries=[]
    for c in index:
        spec=originals[c['sourceSha256']];context=contexts[c['sourceSha256']];ev=evidence[c['sourceSha256']];primary=load(ROOT/c['file']);secondary=load(ROOT/c['secondaryFile']);key=c['key'];rows=copy.deepcopy(primary['rows']);raw_pairs=collections.Counter(tuple(x['row']) for x in secondary['rows'])
        for o in peer.values():
            if o['sourceKey']!=key or o['sourceRowOnPage'] is None:continue
            match=next(x for x in rows if x['row'][5]==o['physicalPage'] and x['sourceRowOnPage']==o['sourceRowOnPage'])
            literal=[nameclean(o['nameLiteral']),o['remuneration'],o['expenses']]
            if [match['row'][1],match['row'][3],match['row'][4]]!=literal:raise ValueError(('Peer source reading conflicts with primary',o['id']))
            match.setdefault('sourceImageTargetIds',[]).append(o['id'])
        for o in clip.values():
            if o['sourceKey']!=key:continue
            match=next(x for x in rows if x['row'][5]==o['physicalPage'] and x['sourceRowOnPage']==o['sourceRowOnPage'])
            assert [match['row'][3],match['row'][4]]==[o['remuneration'],o['expenses']]
            match.setdefault('sourceImageTargetIds',[]).append(o['id'])
            if o['id'] in nulls:
                adoption=nulls[o['id']];assert adoption['acceptedName'] is None
                match['candidateRowBeforeAdoptions']=copy.deepcopy(match['row'])
                match['nativeNameBeforeClippingAdoption']=match['row'][1]
                match['visibleSourceNameFragment']=adoption['nameLiteral']
                match['sourceNameWasDisclosedButClipped']=True
                match['sourceNameUncertainty']=adoption['uncertainty']
                match['row'][1]=None
                match['adoption']='Exact root source-image adoption: the original discloses a name but clips its trailing characters. Name remains unavailable, visible fragment remains supporting evidence, known remuneration/expenses/page retained. Hidden native suffix is not presented as a verified complete name. No inferred inter-year identity.'
            elif o['id'] in ['health-clip-001-243','health-clip-001-258']:
                assert match['row'][1].replace('‐','-')==nameclean(o['nameLiteral'])
            else:assert match['row'][1]==nameclean(o['nameLiteral'])
        if key=='island-health-2005-06':
            o=next(o for o in peer.values() if o['sourceKey']==key and o['sourceRowOnPage'] is None)
            if [o['nameLiteral'],o['remuneration'],o['expenses']]!=['M.S.',88941,0] or o['physicalPage']!=17:raise ValueError('Exact partial-name source adoption changed')
            positions=[i for i,x in enumerate(rows) if x['row'][1]=='STEVEN,LOIS' and x['row'][5]==17]
            if len(positions)!=1 or rows[positions[0]-1]['row'][1]!='STEEN,SARAH':raise ValueError('Partial-name original table position changed')
            rows.insert(positions[0],{'row':['island-health','M.S.',None,88941,0,17],'rawLine':'M.S.                       88,941                   0','payToken':'88,941','expenseToken':'0','sourceRowOnPage':None,'sourceImageTargetIds':[o['id']],'adoption':'Additional literal partial-name observation omitted by the comma-only candidate grammar; actual original source plus two native field-token outputs and independent original-image reading. No full identity inferred.'})
        values=[r['row'] for r in rows];pay=sum(Decimal(str(r[3])) for r in values);exp=sum(Decimal(str(r[4])) for r in values if r[4] is not None);control=named_control(context);residual=[str(pay-Decimal(str(control['remuneration']))),str(exp-Decimal(str(control['expenses'] or 0)))] if control else None
        warning='Official Legislative Library archival download with an added catalogue cover at physical page1; page citations identify this downloaded copy. These are published payment observations, not annual base salary rates or a workforce census. Source expense dashes and blanks remain unknown; numeric zero remains zero.'
        if control and any(Decimal(v)!=0 for v in residual):warning+=f' Literal named rows sum to ${pay:,.2f} remuneration and ${exp:,.2f} known expenses, differing from the printed named controls by {residual[0]}/{residual[1]} dollars. No source cell is adjusted and no cause is established.'
        if key=='fraser-health-2010-11':warning+=' A separate official contract-analysis summary counts 4,458 employees for 2010/11, whereas the complete printed main employee table has 4,439 observations. Both originals print a year ended March 31, 2011, but equivalence of their counting scopes is not established. The numeric difference is not treated as nineteen missing records; no observations are invented or removed. This import uses the main published employee schedule; the separate contract-detail table does not supply missing observations or inferred positions in this source.'
        if key=='island-health-2022-23':warning+=' The complete printed employee table has 8,252 observations, while the source narrative declares 8,264; the twelve-observation difference remains unresolved and no employees are invented.'
        if key=='island-health-2005-06':warning+=' One observation is disclosed only as M.S.; no full name or identity is inferred.'
        if key=='vancouver-coastal-health-2007-08':warning+=' Two named source amounts ($74,860.78 and $74,478.19) are below the printed $75,000 cutoff; both literal observations are retained without an inferred explanation.'
        if key.startswith('fraser-health-') and any(any(ch.isdigit() for ch in (r[1] or '')) for r in values):warning+=' Source digits appended to some disclosed names remain literal and do not establish identities or an explanation for those digits.'
        clipped=[r for r in rows if r.get('sourceNameWasDisclosedButClipped')]
        if clipped:warning+=f' {len(clipped)} source observations disclose a name whose trailing characters are physically clipped in the original. Their names remain unavailable in the app; literal visible fragments and partial-glyph uncertainty are preserved as supporting evidence. Known payment amounts, expenses and page citations remain unchanged; no identity is inferred.'
        warning+=' Existing compiled observations are retained and may overlap this official schedule; no identity or reporting-period equivalence is assumed.'
        year=spec['item']['candidateYear'];start=int(year[:4]);sourceid='gap-health-employees-'+key;fname=key+'-employees.json.gzip';raw=gzip.compress(json.dumps(values,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);(COLLECTION/fname).write_bytes(raw)
        provenance=[];pagecounts=collections.Counter()
        for n,r in enumerate(rows,1):
            pagecounts[r['row'][5]]+=1;item={'rowIndex':n,'physicalPage':r['row'][5],'sourceRowOnPage':pagecounts[r['row'][5]],'initialPrimarySourceRowOnPage':r['sourceRowOnPage'],'rawPrimaryLayoutLine':r['rawLine'],'rawRemunerationToken':r['payToken'],'rawExpenseToken':r['expenseToken'],'exactSecondaryNativeObservationPresent':raw_pairs[tuple(r.get('candidateRowBeforeAdoptions',r['row']))]>0,'sourceImageTargetIds':r.get('sourceImageTargetIds',[])}
            for field in ['adoption','nativeNameBeforeClippingAdoption','visibleSourceNameFragment','sourceNameWasDisclosedButClipped','sourceNameUncertainty']:
                if field in r:item[field]=r[field]
            assert item['exactSecondaryNativeObservationPresent'] or item['sourceImageTargetIds'],('Unverified native observation',key,n)
            provenance.append(item)
        provname=key+'-employees-provenance.json.gzip';provraw=gzip.compress(json.dumps({'sourceSha256':spec['sourceSha256'],'status':'complete source extraction and independent image exception review; root final publication adoption pending','nativeEvidence':ev,'primaryCandidate':{'path':c['file'],'sha256':c['sha256']},'secondaryCandidate':{'path':c['secondaryFile'],'sha256':c['secondarySha256']},'sourceImageReadingSelection':{'path':CURRENT_SELECTION,'sha256':CURRENT_SHA},'clipImageReadingSelection':{'path':CLIP_SELECTION,'sha256':CLIP_SELECTION_SHA},'clippedNameAdoption':{'path':NULL_ADOPTION,'sha256':NULL_ADOPTION_SHA},'sourceVerificationClosure':{'path':str(closure_path.relative_to(ROOT)),'sha256':sha(closure_path.read_bytes())},'rows':provenance},ensure_ascii=False,separators=(',',':')).encode(),mtime=0);(COLLECTION/provname).write_bytes(provraw)
        notes=['All printed named observations are retained in original document order, including repeated source observations. Names are disclosed strings, not resolved identities. Only source whitespace and comma spacing are standardized; Providence visibly separate surname/given-name columns are joined with a comma.','The source publishes no job title for these employee observations; position remains null.','Known expense sums exclude unknown/null cells; a printed subtotal never supplies a missing expense value.']+definitions(context)
        src={'id':sourceid,'employerSlug':spec['item']['employerSlug'],'employerName':spec['item']['issuer'],'sector':'Health authorities','year':year,'periodType':'fiscal','periodStart':f'{start}-04-01','periodEnd':f'{start+1}-03-31','periodEvidence':'Actual internally printed salary year-end or fiscal-period label on physical page'+str(context['employeePhysicalPages'][0])+', retained in the source context packet. Catalogue issue labels are discovery only. The start date represents the conventional twelve-month fiscal year endingMarch31.','title':spec['item']['issuer']+' employee remuneration '+year+' (official Legislative Library copy)','sourceUrl':spec['url'],'indexUrl':context['indexUrl'],'sha256':spec['sourceSha256'],'pdfBytes':spec['retrieval']['bytes'],'file':fname,'dataSha256':sha(raw),'rowCount':len(values),'status':'source-reviewed-awaiting-root-adoption','sourceKind':'official','category':'employee-remuneration','scope':'employee-remuneration','currency':'CAD','completeEmployeeSchedule':True,'threshold':75000,'thresholdComparison':'reported-conflict' if key=='vancouver-coastal-health-2007-08' else 'as-published','nameDisclosure':'source-names-and-initials','notes':notes,'publicWarning':warning,'provenanceFile':provname,'provenanceSha256':sha(provraw),'validation':{'status':'source-reviewed; root final normalized publication adoption pending','compiledPartitionRetained':True,'compiledPartitionRetentionReason':'Complete-copy equivalence with retained compiled observations has not been separately proved; retain all compiled rows without assuming identities or reporting-period equivalence.','completePrintedNamedScope':True,'literalRemunerationSum':str(pay),'literalKnownExpenseSum':str(exp),'printedNamedControls':control,'literalNamedControlResiduals':residual,'residualCauseEstablished':False,'exactReaderRowsBeforeSourceAdoptions':c['rowsExactlyEqual'],'sourceImageExceptionsSelected':{'path':CURRENT_SELECTION,'sha256':CURRENT_SHA},'candidateOnly':True,'independentImageTargetsClosed':True,'allReaderFlagsClosed':True,'completePhysicalPageCensus':proof_by_key[key],'sourceVerificationClosure':{'path':str(closure_path.relative_to(ROOT)),'sha256':sha(closure_path.read_bytes())},'clipImageReadingSelection':{'path':CLIP_SELECTION,'sha256':CLIP_SELECTION_SHA},'clippedNameAdoption':{'path':NULL_ADOPTION,'sha256':NULL_ADOPTION_SHA},'sourceContextAcceptance':{'path':CONTEXT_ACCEPTANCE,'sha256':CONTEXT_ACCEPTANCE_SHA},'unavailableNamesDueOriginalClipping':len(clipped),'pendingGates':['root final normalized payload adoption and owned input freeze']}}
        if key=='fraser-health-2010-11':
            supplement=AREA/'fraser-2010-11-contract-context-qualification.json';src['validation']['sourceContextSupplement']={'path':str(supplement.relative_to(ROOT)),'sha256':sha(supplement.read_bytes())};src['validation']['separateContractSummaryCount']=4458;src['validation']['printedMainNamedObservations']=4439;src['validation']['separateSummaryCountDifference']=19;src['validation']['countDifferenceCauseEstablished']=False
        sources.append(src);summaries.append({'id':sourceid,'sourceKey':key,'year':year,'rows':len(values),'dataSha256':src['dataSha256'],'provenanceSha256':src['provenanceSha256'],'literalNamedControlResiduals':residual,'candidate':True})
    manifest={'schemaVersion':1,'status':'Source-reviewed normalized candidates; root final publication adoption pending','noOutreach':True,'sources':sources};(COLLECTION/'sources-candidate.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(AREA/'normalized-candidate-summary.json').write_text(json.dumps({'status':manifest['status'],'sources':summaries,'candidateRows':sum(x['rows'] for x in summaries)},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sources':len(sources),'candidateRows':sum(x['rowCount'] for x in sources),'manifestSha256':sha((COLLECTION/'sources-candidate.json').read_bytes())}))

if __name__=='__main__':build()
