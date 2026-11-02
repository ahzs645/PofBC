#!/usr/bin/env python3
"""Replay19 newly uncovered health-board schedules using committed paired readers.

No network, PDF cache, OCR or image library is needed for normal/check replay.
--originals explicitly refreshes exact source word/paint evidence from pinned PDFs.
"""
import argparse
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re

from gap_health_boards import (SCHEMA, cell, flat, numeric, packed, pdf_readers,
                               primary, secondary, validate_source_readings, zipped)

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_board_supplement'
OUT=ROOT/'research/salaries/gap-fill-health-board-supplement'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gzip' else raw)
def reference(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
def exact_sum(values):
    total=sum((Decimal(str(v)) for v in values if v is not None),Decimal(0))
    return int(total) if total==total.to_integral_value() else float(total)
def exact_difference(a,b):return exact_sum([a,-b])
def emit(path,value,check):
    raw=zipped(value) if path.suffix=='.gzip' else packed(value)
    if check:
        if path.read_bytes()!=raw:raise ValueError('Replay differs: '+str(path))
    else:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)


def interpret(cells,spec):
    rows=[];details=[]
    for at,c in enumerate(cells,1):
        raw_name=c['name'];name=raw_name;position=c.get('position') or None
        chair=re.search(r',\s*(CHAIR|Chair)$',name)
        if chair:
            position=chair.group(1);name=name[:chair.start()].rstrip()
        elif spec['employerSlug']=='vancouver-coastal-health':
            # The original names beneath the explicit Directors: heading share this role.
            position='Director'
        pay=numeric(c['remuneration']);expense=numeric(c['expenses'])
        row=[spec['employerSlug'],name,position,pay,expense,spec['page']]
        rows.append(row);details.append({'sourceRow':at,'row':row,'rawCells':c,
             'literalSourceName':raw_name,'sourceRoleRule':'Literal separate position column, explicit Chair suffix, or Vancouver Coastal Health Directors: heading. No identity inference.',
             'sourceFootnoteMarker':c.get('footnote') or None,
             'expenseInclusivePrintedRowTotal':numeric(c['total']) if 'total'in c else None})
    return rows,details


def paired(spec,proof):
    if proof['sourceSha256']!=spec['sha256']:raise ValueError('Wrong source original')
    controls=validate_source_readings(proof,spec)
    first=primary(proof['pymupdf'][spec['page']-1],spec)
    second=secondary(proof['poppler'][spec['page']-1],spec)
    if [{k:r[k] for k in spec['fields']} for r in first]!=second:
        raise ValueError('Independent native cells differ: '+spec['id'])
    a,ad=interpret(first,spec);b,bd=interpret(second,spec)
    if a!=b:raise ValueError('Independent normalized rows differ')
    return a,ad,b,bd,controls


def adoption():
    path=AREA/'review-adoption.json'
    if not path.exists():return None
    q=read(path);ref=q['independentReview'];p=ROOT/ref['path']
    if digest(p.read_bytes())!=ref['sha256']:raise ValueError('Review receipt changed')
    receipt=read(p)
    if receipt.get('accepted')is not True or receipt.get('noOutreach')is not True:raise ValueError('Independent acceptance required')
    pins={s['sourceId']:s for s in receipt['sources']}
    if len(pins)!=len(receipt['sources']):raise ValueError('Duplicate review source')
    return {'reference':ref,'pins':pins}


def refresh_originals(specs):
    for spec in specs:
        raw=Path(spec['sourceCachePath']).read_bytes()
        if digest(raw)!=spec['sha256']:raise ValueError('Pinned PDF changed')
        doc,a,b=pdf_readers(Path(spec['sourceCachePath']),[spec['page']])
        if len(doc)!=spec['sourcePhysicalPages']:raise ValueError('Physical PDF page count changed')
        emit(ROOT/spec['nativeEvidence']['path'],{'sourceSha256':spec['sha256'],'pymupdf':a,'poppler':b},False)
    import gap_health_boards_visibility as visibility
    visibility.AREA=AREA;visibility.OUT=OUT
    visibility.main()


def run(check=False,originals=False):
    if check and originals:raise ValueError('Read-only check cannot refresh source evidence')
    specs=read(AREA/'source-specs.json');review=adoption()
    if len(specs)!=19 or len({s['id']for s in specs})!=19:raise ValueError('Exact19original supplement required')
    if review and set(review['pins'])!={s['id']for s in specs}:raise ValueError('Review coverage differs')
    if originals:refresh_originals(specs)
    sources=[];audits=[]
    for spec in specs:
        for view in spec['sourceViews']:
            if digest((ROOT/view['path']).read_bytes())!=view['sha256']:
                raise ValueError('Original source view changed')
        evidence_path=ROOT/spec['nativeEvidence']['path'];proof=read(evidence_path)
        if digest(evidence_path.read_bytes())!=spec['nativeEvidence']['sha256']:raise ValueError('Paired evidence changed')
        a,ad,b,bd,controls=paired(spec,proof)
        imported=[r for r in a if r[3]is not None];held=[r for r in a if r[3]is None]
        sums={'remuneration':exact_sum(r[3]for r in imported),'expenses':exact_sum(r[4]for r in a)}
        printed={k:v['value']for k,v in spec['printedControlCells'].items()}
        residuals={k:exact_difference(sums[k],printed[k])for k in ['remuneration','expenses']}
        if 'total'in printed:residuals['knownFieldsMinusPrintedGrand']=exact_difference(exact_sum(sums.values()),printed['total'])
        row_residuals=[{'sourceRow':d['sourceRow'],'name':d['row'][1],'residual':exact_difference(exact_sum([d['row'][3],d['row'][4]]),d['expenseInclusivePrintedRowTotal'])}for d in ad if d['row'][3]is not None and d['expenseInclusivePrintedRowTotal']is not None]
        visibility=read(AREA/'visibility-v2'/(spec['id']+'-visibility.json'))
        if visibility['sourceSha256']!=spec['sha256']:raise ValueError('Visibility original differs')
        v={'completeNamedBoardScopeRead':True,'completeBoardSchedule':not held,'completeEmployeeSchedule':False,
           'independentReaders':['PyMuPDF native word geometry / complete row bands','Poppler bbox-layout / independently assembled nearest name baselines'],
           'independentlyComparedRows':len(a),'namedRows':len(a),'numericPayRows':len(imported),'heldUnknownPayRows':held,
           'sourcePhysicalPages':spec['sourcePhysicalPages'],'schedulePhysicalPages':[spec['page']],
           'totalRemuneration':sums['remuneration'],'importedKnownExpenses':exact_sum(r[4]for r in imported),
           'heldKnownExpenses':exact_sum(r[4]for r in held),'allNamedKnownExpenses':sums['expenses'],
           'missingExpenseRows':sum(r[4]is None for r in imported),'explicitZeroExpenseRows':sum(r[4]==0 for r in imported),
           'printedControls':printed,'sourceControlResiduals':residuals,'rowInclusiveTotalResiduals':row_residuals,
           'compiledPartitionRetained':True,'compiledPartitionRetentionReason':'Complete copy equivalence with retained compiled observations has not been established; no calendar or identity match is assumed.',
           'nativeVisibilityDiagnostics':{'file':'visibility/'+spec['id']+'.json.gzip','sha256':digest(zipped(visibility)),
              'flags':{k:len(visibility[k])for k in ['ignoredOrLowOpacityCharacters','nearWhiteCharacters','unicodeReplacementCharacters','identicalGlyphOverprints','conflictingGlyphOverprints','nativeWordsCrossingReviewedFieldEdges','nativeWordsWithoutDarkRenderedInk']},
              'limitation':visibility['limitation']}}
        data=zipped(imported);filename=spec['id']+'.json.gzip'
        if review:
            pin=review['pins'][spec['id']]
            if pin['sourceSha256']!=spec['sha256']or pin['dataSha256']!=digest(data):raise ValueError('Independent review source/data pins differ')
            v['independentSourceReview']=review['reference']
        detail={'sourceId':spec['id'],'sourceSha256':spec['sha256'],'originalLeadIds':spec['originalLeadIds'],
             'originalWordEvidence':{'file':'evidence/'+spec['id']+'.json.gzip','sha256':digest(zipped(proof))},
             'originalSourceViews':spec['sourceViews'],'primaryRows':a,'secondaryRows':b,'allPrimaryCells':ad,'allSecondaryCells':bd,
             'printedControlReadings':controls,'validation':v}
        emit(OUT/filename,imported,check);emit(OUT/'evidence'/(spec['id']+'.json.gzip'),proof,check)
        emit(OUT/'visibility'/(spec['id']+'.json.gzip'),visibility,check)
        emit(OUT/'provenance'/(spec['id']+'.json.gzip'),detail,check)
        emit(AREA/(spec['id']+'-row-review.json'),detail,check)
        definition='Remuneration uses the separately labelled remuneration column. Expenses and any expense-inclusive total are excluded from pay. Blank and dash expense cells remain unknown (null), not zero.'
        warning='Board payment disclosures are not annual salary rates or employee rosters. '+definition+' '
        if held:warning+=str(len(held))+' named board observation(s) with nonnumeric remuneration remain supporting evidence; no zero pay is invented. Their known expenses total '+str(v['heldKnownExpenses'])+' CAD and remain included in full-board expense controls. '
        if any(residuals.values())or any(d['residual']for d in row_residuals):
            for field,label in [('remuneration','Named remuneration'),('expenses','Full-board known expenses'),('knownFieldsMinusPrintedGrand','Known remuneration plus known expenses')]:
                difference=residuals.get(field,0)
                if difference:
                    warning+=label+' minus its printed control is '+str(difference)+' CAD. '
            warning+='No payment has been balanced or adjusted. The cause is not established. '
        if spec['sourceKey']=='fraser-health-2004-05':warning+='The source states its July 2004 retainer-policy change means only three quarters of retainer payments appear in this fiscal disclosure. '
        warning+='Existing compiled observations are retained and may overlap this official schedule; no identity or reporting-period equivalence is assumed.'
        source={'id':spec['id'],'title':spec['employerName']+' Board Remuneration '+spec['year'],'year':spec['year'],'employerSlug':spec['employerSlug'],'employerName':spec['employerName'],'sector':'Health authorities',
           'sourceUrl':spec['sourceUrl'],'sha256':spec['sha256'],'file':filename,'dataSha256':digest(data),'rowCount':len(imported),
           'status':'verified'if review else'candidate','sourceKind':'official','category':'board-remuneration','scope':'board-remuneration',
           'provenanceFile':'provenance/'+spec['id']+'.json.gzip','provenanceSha256':digest(zipped(detail)),
           'evidenceFile':'evidence/'+spec['id']+'.json.gzip','evidenceSha256':digest(zipped(proof)),
           'completeEmployeeSchedule':False,'completeBoardSchedule':not held,'periodType':'fiscal','periodStart':spec['year'][:4]+'-04-01','periodEnd':str(int(spec['year'][:4])+1)+'-03-31',
           'nameDisclosure':'named','positionDisclosure':'literal-source-board-role','currency':'CAD','threshold':None,
           'validation':v,'publicWarning':warning,'notes':[definition,'Source spellings, footnote markers and original names including explicit Chair suffixes are retained in provenance.','The internally stated fiscal payment year is used even when source footnotes discuss earlier appointments, terms or retainer payments.']}
        if review:source['verifiedOn']='2026-11-02'
        sources.append(source);audits.append({'sourceId':spec['id'],'sourceSha256':spec['sha256'],'dataSha256':digest(data),'rows':len(imported),'held':len(held),'pay':sums['remuneration'],'importedExpenses':v['importedKnownExpenses'],'heldExpenses':v['heldKnownExpenses'],'controlResiduals':residuals,'nonzeroRowResiduals':[d for d in row_residuals if d['residual']]})
    manifest={'version':1,'rowSchema':SCHEMA,'sources':sources}
    emit(OUT/'sources.json',manifest,check);emit(AREA/'extraction-summary.json',audits,check)
    result={'sources':len(sources),'rows':sum(s['rowCount']for s in sources),'held':sum(a['held']for a in audits)}
    print(json.dumps(result));return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--originals',action='store_true');args=ap.parse_args();run(args.check,args.originals)
