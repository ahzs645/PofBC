#!/usr/bin/env python3
"""Offline board-history normalization from two separately extracted PDF readers.

Originals mode refreshes word evidence and full-page renders. Default replay
never downloads and never uses a subtotal to infer or repair a payment.
"""
from __future__ import annotations
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/salaries/gap-fill-2026-11-02/health_boards'
OUT=ROOT/'research/salaries/gap-fill-health-boards'
CACHE=Path('/workspace/gap-health-boards-cache')
SCHEMA=['employerSlug','name','position','remuneration','expenses','pdfPage']
EMPLOYERS={'island-health':'Island Health','provincial-health-services-authority':'Provincial Health Services Authority','vancouver-coastal-health':'Vancouver Coastal Health','providence-health-care':'Providence Health Care'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def packed(v):return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def zipped(v):return gzip.compress(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode(),mtime=0)
def flat(v):return re.sub(r'\s+',' ',v).strip()

def numeric(value):
    value=flat(value.replace('$',''))
    if value in ['', '-', '‐', '–', '—']:return None
    if not re.fullmatch(r'(?:-?\d[\d,]*(?:\.\d{2})?|\(\d[\d,]*(?:\.\d{2})?\))',value):
        raise ValueError('Nonmonetary source cell '+repr(value))
    n=Decimal(value.replace(',','').replace('(','-').replace(')',''))
    return int(n) if n==n.to_integral() else float(n)

def component_values(value):
    """Blank unused role columns contribute no disclosed component, not an invented cell."""
    return [numeric(t) for t in flat(value.replace('$',' ')).split()]

def word_lines(words):
    lines=[]
    for w in sorted(words,key=lambda x:(x[1],x[0])):
        if lines and abs(w[1]-lines[-1][0][1])<2.8:lines[-1].append(w)
        else:lines.append([w])
    return [sorted(line,key=lambda x:x[0]) for line in lines]

def cell(words,x0,x1,y0,y1):
    selected=[w for w in words if x0<=(w[0]+w[2])/2<x1 and y0<=(w[1]+w[3])/2<y1]
    return flat(' '.join(' '.join(w[4] for w in line) for line in word_lines(selected)))

def primary(words,spec):
    top,bottom=spec['yRange'];left,right=spec['fields']['name']
    excluded=set(spec.get('excludedNameTokens',[]))
    name_words=[w for w in words if left<=(w[0]+w[2])/2<right and top<=(w[1]+w[3])/2<bottom and w[4] not in excluded]
    anchors=[]
    for line in word_lines(name_words):
        text=flat(' '.join(w[4] for w in line))
        if not re.search('[A-Za-z]',text):continue
        anchors.append(((min(w[1] for w in line)+max(w[3] for w in line))/2,text))
    if len(anchors)!=spec['namedRows']:raise ValueError((spec['id'],'primary named row count',len(anchors),anchors))
    cells=[]
    for i,(y,name) in enumerate(anchors):
        low=top if i==0 else (anchors[i-1][0]+y)/2
        high=bottom if i==len(anchors)-1 else (y+anchors[i+1][0])/2
        row={field:cell([w for w in words if field!='name' or w[4] not in excluded],*limits,low,high) for field,limits in spec['fields'].items()}
        row.update(yRange=[low,high],rawAnchorName=name)
        cells.append(row)
    return cells

def secondary(words,spec):
    """Second layout assembly: assign each word to nearest independent name baseline."""
    top,bottom=spec['yRange'];left,right=spec['fields']['name']
    excluded=set(spec.get('excludedNameTokens',[]))
    candidates=sorted([w for w in words if left<=(w[0]+w[2])/2<right and top<=(w[1]+w[3])/2<bottom and w[4] not in excluded],key=lambda w:((w[1]+w[3])/2,w[0]))
    groups=[]
    for w in candidates:
        cy=(w[1]+w[3])/2
        if groups and abs(cy-groups[-1][0])<3.5:groups[-1][1].append(w)
        else:groups.append([cy,[w]])
    groups=[g for g in groups if re.search('[A-Za-z]',' '.join(w[4] for w in g[1]))]
    if len(groups)!=spec['namedRows']:raise ValueError((spec['id'],'secondary named row count',len(groups)))
    rows=[{field:[] for field in spec['fields']} for _ in groups]
    for w in words:
        cx,cy=(w[0]+w[2])/2,(w[1]+w[3])/2
        if not top<=cy<bottom:continue
        row=min(range(len(groups)),key=lambda i:abs(groups[i][0]-cy))
        for field,(a,b) in spec['fields'].items():
            if a<=cx<b and (field!='name' or w[4] not in excluded):rows[row][field].append(w)
    out=[]
    for row in rows:
        result={}
        for field,values in row.items():
            # Independent reading-order method bins baselines before horizontal ordering.
            buckets=[]
            for w in sorted(values,key=lambda z:((z[1]+z[3])/2,z[0])):
                cy=(w[1]+w[3])/2
                if buckets and abs(cy-buckets[-1][0])<3.5:buckets[-1][1].append(w)
                else:buckets.append([cy,[w]])
            result[field]=flat(' '.join(' '.join(w[4] for w in sorted(v,key=lambda z:z[0])) for _,v in buckets))
        out.append(result)
    return out

def interpreted(cells,spec):
    rows=[];evidence=[]
    for source_row,c in enumerate(cells,1):
        raw_name=c['name'];name=spec.get('nameAnnotations',{}).get(raw_name,raw_name)
        if name!=raw_name:annotation={'sourceNameWithFootnote':raw_name,'nameWithoutSourceFootnote':name}
        else:annotation=None
        if spec.get('directPayField'):
            pay=numeric(c[spec['directPayField']]);components=None
        else:
            components={f:component_values(c[f]) for f in spec['payComponentFields']}
            values=[v for vs in components.values() for v in vs if v is not None]
            pay=sum(values) if values else None
        expense=numeric(c['expenses']) if 'expenses' in c else None
        row=[spec['employerSlug'],name,c.get('position') or None,pay,expense,spec['page']]
        rows.append(row)
        evidence.append({'sourceRow':source_row,'row':row,'rawCells':c,'disclosedPayComponents':components,'nameFootnote':annotation,'printedRowTotal':numeric(c['total']) if 'total' in c else None})
    return rows,evidence

def pdf_readers(path,selected_pages=None):
    import fitz
    doc=fitz.open(path);a=[]
    selected=set(selected_pages or range(1,len(doc)+1))
    for page in doc:
        if page.number+1 not in selected:
            a.append([]);continue
        words=[]
        for w in page.get_text('words'):
            q=fitz.Rect(w[:4])*page.rotation_matrix
            words.append([q.x0,q.y0,q.x1,q.y1,w[4]])
        a.append(words)
    ns={'h':'http://www.w3.org/1999/xhtml'}
    b=[[] for _ in doc]
    for n in sorted(selected):
        raw=subprocess.check_output(['pdftotext','-f',str(n),'-l',str(n),'-bbox-layout',str(path),'-'])
        pages=ET.fromstring(raw).findall('.//h:page',ns);assert len(pages)==1
        b[n-1]=[[float(w.attrib[k]) for k in ['xMin','yMin','xMax','yMax']]+[w.text or ''] for w in pages[0].findall('.//h:word',ns)]
    return doc,a,b

def validate_source_readings(proof,spec):
    """Require the internally printed period and literal control cells in both readers."""
    assert proof['sourceSha256']==spec['sha256']
    readings={}
    for engine in ['pymupdf','poppler']:
        words=proof[engine][spec['page']-1]
        header=flat(' '.join(w[4] for line in word_lines([w for w in words if (w[1]+w[3])/2<spec['yRange'][0]]) for w in line))
        assert re.search(r'March\s+31\s*,?\s*'+str(int(spec['year'][:4])+1),header,re.I),(spec['id'],engine,'internal header period')
        controls={}
        for label,c in spec.get('printedControlCells',{}).items():
            observed=numeric(cell(words,*c['xRange'],*c['yRange']))
            assert observed==c['value'],(spec['id'],engine,label,observed,c['value'])
            controls[label]=observed
        readings[engine]=controls
    return readings

def compare_native_rows(proof,spec):
    a=primary(proof['pymupdf'][spec['page']-1],spec);b=secondary(proof['poppler'][spec['page']-1],spec)
    try:ra,ea=interpreted(a,spec);rb,eb=interpreted(b,spec)
    except ValueError as exc:raise ValueError(spec['id']+': '+str(exc)) from exc
    if ra!=rb:
        differences=[{'index':i,'primary':x,'secondary':y} for i,(x,y) in enumerate(zip(ra,rb)) if x!=y]
        raise ValueError((spec['id'],'independent reader disagreement',differences))
    return ra,ea,rb,eb

def review_adoption():
    path=AREA/'review-adoption.json'
    if not path.exists():return None
    adoption=json.loads(path.read_bytes());ref=adoption['independentReview']
    raw=(ROOT/ref['path']).read_bytes();assert sha(raw)==ref['sha256'],'Independent review receipt changed'
    receipt=json.loads(raw);assert receipt['accepted'] is True and receipt['noOutreach'] is True
    pins={s['sourceId']:s for s in receipt['sources']}
    assert len(pins)==len(receipt['sources'])
    return {'reference':ref,'pins':pins}

def validate_review_source(review,source_id,source_sha,data_sha):
    pin=review['pins'][source_id]
    assert pin['sourceSha256']==source_sha,(source_id,'reviewed source changed')
    assert pin['dataSha256']==data_sha,(source_id,'reviewed rows changed')

def run(originals=False,check=False):
    OUT.mkdir(exist_ok=True);(OUT/'evidence').mkdir(exist_ok=True);(OUT/'provenance').mkdir(exist_ok=True);(OUT/'visibility').mkdir(exist_ok=True)
    specs=json.loads((AREA/'source-specs.json').read_bytes());sources=[];audits=[];review=review_adoption()
    if review:assert set(review['pins'])=={s['id'] for s in specs},'Review must cover the exact25 original scopes'
    for spec in specs:
        evidence_path=OUT/'evidence'/(spec['id']+'.json.gzip')
        if originals:
            path=Path(spec['cachePath']);raw=path.read_bytes();assert sha(raw)==spec['sha256']
            captured=sorted(set([spec['page'],*spec.get('contextPages',[])]))
            doc,a,b=pdf_readers(path,captured)
            renders=[]
            for p in sorted(set([spec['page'],*spec.get('contextPages',[])])):
                pix=doc[p-1].get_pixmap(dpi=200);dest=CACHE/(spec['id']+f'-page-{p}.png');pix.save(dest)
                renders.append({'physicalPage':p,'dpi':200,'sha256':sha(dest.read_bytes()),'cachePath':str(dest)})
            evidence_path.write_bytes(zipped({'sourceSha256':spec['sha256'],'pymupdf':a,'poppler':b,'capturedPhysicalPages':captured,'renderedOriginals':renders}))
        raw_evidence=evidence_path.read_bytes();proof=json.loads(gzip.decompress(raw_evidence))
        control_readings=validate_source_readings(proof,spec)
        ra,ea,rb,eb=compare_native_rows(proof,spec)
        imported=[r for r in ra if r[3] is not None];held=[r for r in ra if r[3] is None]
        row_residuals=[{'name':x['row'][1],'residual':x['row'][3]+(x['row'][4] or 0)-x['printedRowTotal']} for x in ea if x['row'][3] is not None and x['printedRowTotal'] is not None]
        v={'independentReaders':['PyMuPDF rotated word geometry / row bands','Poppler bbox-layout / nearest independent name baseline'], 'independentlyComparedRows':len(ra),'completeBoardSchedule':not held,'completeEmployeeSchedule':False,'namedRows':len(ra),'numericPayRows':len(imported),'heldUnknownPayRows':held,'expensesNotDisclosed': 'expenses' not in spec['fields'],'missingExpenseRows':sum(r[4] is None for r in imported),'explicitZeroExpenseRows':sum(r[4]==0 for r in imported),'totalRemuneration':sum(r[3] for r in imported),'knownExpenses':sum(r[4] or 0 for r in imported),'heldKnownExpenses':sum(r[4] or 0 for r in held),'allNamedKnownExpenses':sum(r[4] or 0 for r in ra),'rowInclusiveTotalResiduals':row_residuals,'sourceOriginalEvidenceSha256':sha(raw_evidence),'sourcePhysicalPages':len(proof['pymupdf']),'schedulePhysicalPages':[spec['page']],'compiledPartitionRetained':True,'compiledPartitionRetentionReason':'Full-copy equivalence with retained compiled observations has not been established; no identity or reporting-period equivalence is assumed.'}
        visibility_file=AREA/'visibility-v2'/(spec['id']+'-visibility.json');visibility=json.loads(visibility_file.read_bytes())
        assert visibility['sourceSha256']==spec['sha256']
        visibility_relative='visibility/'+spec['id']+'.json.gzip';visibility_bytes=zipped(visibility)
        if check:assert (OUT/visibility_relative).read_bytes()==visibility_bytes
        else:(OUT/visibility_relative).write_bytes(visibility_bytes)
        v['nativeVisibilityDiagnostics']={'file':visibility_relative,'sha256':sha(visibility_bytes),'method':'Original PDF paint trace, glyph-overlap, field-edge and200dpi dark-ink diagnostics; no assertion that paired native text proves pixel accuracy.','reviewFieldEdgeCrossings':len(visibility['nativeWordsCrossingReviewedFieldEdges']),'ignoredOrLowOpacityCharacters':len(visibility['ignoredOrLowOpacityCharacters']),'nearWhiteCharacters':len(visibility['nearWhiteCharacters']),'identicalGlyphOverprints':len(visibility['identicalGlyphOverprints']),'conflictingGlyphOverprints':len(visibility['conflictingGlyphOverprints']),'nativeWordsWithoutDarkRenderedInk':len(visibility['nativeWordsWithoutDarkRenderedInk'])}
        if spec.get('printedGrandTotal') is not None:
            v['printedGrandTotal']=spec['printedGrandTotal'];v['knownFieldsMinusPrintedGrandTotal']=v['totalRemuneration']+v['allNamedKnownExpenses']-spec['printedGrandTotal']
        if spec.get('printedRemunerationControl') is not None:
            v['printedRemunerationControl']=spec['printedRemunerationControl'];v['remunerationControlResidual']=v['totalRemuneration']-spec['printedRemunerationControl']
        if spec.get('printedExpensesControl') is not None:
            v['printedExpensesControl']=spec['printedExpensesControl'];v['allNamedExpenseControlResidual']=v['allNamedKnownExpenses']-spec['printedExpensesControl']
        data=zipped(imported);filename=spec['id']+'.json.gzip'
        if review:
            validate_review_source(review,spec['id'],spec['sha256'],sha(data))
            v['independentSourceReview']=review['reference']
        if check:assert (OUT/filename).read_bytes()==data
        else:(OUT/filename).write_bytes(data)
        detail={'sourceId':spec['id'],'sourceSha256':spec['sha256'],'primaryRows':ra,'secondaryRows':rb,'allPrimaryCells':ea,'allSecondaryCells':eb,'printedControlReadings':control_readings,'originalWordEvidence':{'file':'evidence/'+spec['id']+'.json.gzip','sha256':sha(raw_evidence)},'validation':v}
        dest=AREA/(spec['id']+'-row-review.json')
        if check:assert dest.read_bytes()==packed(detail)
        else:dest.write_bytes(packed(detail))
        provenance_relative='provenance/'+spec['id']+'.json.gzip';provenance_bytes=zipped(detail)
        if check:assert (OUT/provenance_relative).read_bytes()==provenance_bytes
        else:(OUT/provenance_relative).write_bytes(provenance_bytes)
        warning='Board payment disclosures are not annual salary rates or an employee roster. '+spec['definition']+' Source expense blanks and dashes stay unknown (null); no printed amount is adjusted to balance a subtotal. '
        if held:
            warning+=str(len(held))+' named board observation(s) with nonnumeric remuneration are held as supporting evidence rather than assigned zero pay. '
            warning+='Imported numeric-pay rows carry '+str(v['knownExpenses'])+' CAD in known expenses; excluded nonnumeric-pay rows carry '+str(v['heldKnownExpenses'])+' CAD. The full named-board expense control includes both subsets. '
        residuals=[x for x in row_residuals if x['residual']]
        if residuals or v.get('knownFieldsMinusPrintedGrandTotal'):
            warning+='Literal displayed fields and printed totals disagree; known remuneration plus known expenses minus the printed grand control is '+str(v.get('knownFieldsMinusPrintedGrandTotal'))+' CAD. The cause is not established; individual row differences remain in source evidence. '
        if spec.get('sourceCaveat'):warning+=spec['sourceCaveat']+' '
        warning+='Existing compiled observations are retained and may overlap this official schedule; no identity or reporting-period equivalence is assumed.'
        source={k:spec[k] for k in ['id','title','year','employerSlug','sourceUrl','sha256']}
        source.update(file=filename,dataSha256=sha(data),rowCount=len(imported),status='verified' if review else 'candidate',sourceKind='official',category='board-remuneration',scope='board-remuneration',sector='Health authorities',employerName=EMPLOYERS[spec['employerSlug']],provenanceFile=provenance_relative,provenanceSha256=sha(provenance_bytes),evidenceFile='evidence/'+spec['id']+'.json.gzip',evidenceSha256=sha(raw_evidence),completeEmployeeSchedule=False,completeBoardSchedule=not held,periodType='fiscal',periodStart=spec['year'][:4]+'-04-01',periodEnd=str(int(spec['year'][:4])+1)+'-03-31',nameDisclosure='named',positionDisclosure='source-board-position' if 'position' in spec['fields'] else 'not-published',currency='CAD',threshold=None,validation=v,publicWarning=warning,notes=[spec['definition'],'Names retain the source spelling; adjacent footnote markers are separately preserved in row provenance.','Source footnotes may describe payments for meetings or travel from earlier years; observations retain the internally stated payment disclosure year.'])
        if review:source['verifiedOn']='2026-11-02'
        if imported:sources.append(source)
        audits.append({'sourceId':spec['id'],'rows':len(imported),'held':len(held),'pay':v['totalRemuneration'],'expenses':v['knownExpenses'],'heldKnownExpenses':v['heldKnownExpenses'],'nonzeroRowResiduals':residuals,'grandResidual':v.get('knownFieldsMinusPrintedGrandTotal')})
    manifest=packed({'version':1,'rowSchema':SCHEMA,'sources':sources})
    if check:assert (OUT/'sources.json').read_bytes()==manifest
    else:(OUT/'sources.json').write_bytes(manifest)
    if not check:(AREA/'extraction-summary.json').write_bytes(packed(audits))
    print(json.dumps({'sources':len(sources),'rows':sum(s['rowCount'] for s in sources),'summary':audits},ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--originals',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args();run(args.originals,args.check)
