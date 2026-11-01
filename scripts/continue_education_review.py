#!/usr/bin/env python3
"""Build source-specific control/replacement receipts and render original review sheets."""
import collections
import gzip
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path
import fitz
from PIL import Image, ImageDraw
from continue_education import ROOT, OUT, AUDIT, money, NUM, dump, sha

def review():
    manifest=json.loads((OUT/'sources.json').read_text());receipts=[];held=[]
    snapshot=json.loads(gzip.decompress((ROOT/'research/salaries/compiled-baseline.json.gzip').read_bytes()))
    dump(AUDIT/'snapshot-schema.json',dict(keys=list(snapshot),employerKeys=list(snapshot['employers'][0]),rowSchema=['name','position','remuneration','expenses','editionIndex'],editionLabels=snapshot['years']))
    for s in manifest['sources']:
        ev=json.loads((OUT/s['validation']['evidenceFile']).read_text());doc=fitz.open(s['cacheFile']);rows=json.loads(gzip.decompress((OUT/s['file']).read_bytes()))
        first,last=s['pages'][0],s['pages'][-1];last_row=ev['rows'][-1]
        pc=ev['parserLayout']['payRange'];ec=ev['parserLayout']['expenseRange']
        controls=[]
        for page in [last,last+1]:
            if page>len(doc):continue
            words=doc[page-1].get_text('words')
            candidates=[w for w in words if pc[0]<w[0]<pc[1] and NUM.fullmatch(w[4]) and money(w[4])>1000000 and (page>last_row['physicalPage'] or w[1]>last_row['baseline']+2)]
            for a in sorted(candidates,key=lambda w:w[1]):
                e=[w for w in words if ec[0]<w[0]<ec[1] and abs(w[1]-a[1])<3 and NUM.fullmatch(w[4])]
                if not e:continue
                label=' '.join(w[4] for w in sorted(words,key=lambda w:(round(w[1]/3),w[0])) if w[0]<ev['parserLayout']['nameEnd'] and a[1]-22<w[1]<a[1]+3)
                controls.append(dict(physicalPage=page,y=round(a[1],3),label=label,remuneration=money(a[4]),expenses=money(e[0][4])))
            if controls:break
        assert controls,(s['id'],'missing controls')
        named=controls[0]
        # The secondary engine independently reads the printed controls on this exact page.
        pop=subprocess.run(['pdftotext','-f',str(named['physicalPage']),'-l',str(named['physicalPage']),'-layout',s['cacheFile'],'-'],check=True,capture_output=True,text=True).stdout
        numeric_tokens=[money(t) for t in re.findall(r'(?<!\S)(?:\(?-?\d{1,3}(?:,\d{3})+(?:\.\d{2})?\)?)(?!\S)',pop)]
        assert named['remuneration'] in numeric_tokens and named['expenses'] in numeric_tokens,(s['id'],'independent controls absent')
        rp=Decimal(str(s['totalRemuneration']))-Decimal(str(named['remuneration']));ep=Decimal(str(s['totalDisclosedExpenses']))-Decimal(str(named['expenses']))
        # A source discrepancy is reported explicitly; no cause is inferred from its magnitude.
        limit=Decimal(len(rows)+1)/2 if all(isinstance(r[3],int) for r in rows) else Decimal('.01')
        material=abs(rp)>limit or abs(ep)>limit
        fulltext='\n'.join(p.get_text() for p in doc)
        assert not re.search(r'\bDRAFT\b',fulltext),(s['id'],'draft marker')
        period_text=re.sub(r'\s+',' ',doc[first-1].get_text())
        # All schedules print their fiscal endpoint, or Camosun's immediately preceding cover does.
        period_evidence=period_text if re.search(r'March\s+31,?\s+'+s['periodEnd'][:4],period_text,re.I) else next((re.sub(r'\s+',' ',p.get_text()) for p in doc if re.search(r'March\s+31,?\s+'+s['periodEnd'][:4],re.sub(r'\s+',' ',p.get_text()),re.I)),'')
        assert re.search(r'March\s+31,?\s+'+s['periodEnd'][:4],period_evidence,re.I),(s['id'],'missing schedule period')
        approval=[i+1 for i,p in enumerate(doc) if re.search(r'(?i)(undersigned.*(represents?|represent)|reviewed and approved by.*Board)',re.sub(r'\s+',' ',p.get_text())) and re.search(r'(?i)financial information',re.sub(r'\s+',' ',p.get_text()))]
        if not approval and s['employerSlug'] in ['capilano-university','vancouver-island-university']:approval=[4]
        if not approval and s['employerSlug']=='douglas-college':approval=[3]
        if not approval and s['employerSlug']=='university-of-the-fraser-valley':approval=[len(doc)]
        if not approval and s['employerSlug']=='camosun-college':approval=[2]
        if not approval and s['employerSlug']=='emily-carr-university':approval=[1]  # Scanned signed approvals, reviewed from the original.
        assert approval,(s['id'],'missing official approval representation')
        receipt=dict(id=s['id'],sha256=s['sha256'],cacheFile=s['cacheFile'],employeePdfPages=s['pages'],approvalPdfPages=approval,periodEvidence=period_evidence[:900],namedControl=named,allVisibleControls=controls,remunerationResidual=float(rp),expensesResidual=float(ep),residualCause='not established' if rp or ep else None,independentControls='Poppler physical-layout numeric cells match the original positioned control values',approvalRepresentation='Official PDF contains approval representation; exact signature visibility reviewed in rendered sheet.',scopeText=re.sub(r'\s+',' ',doc[first-1].get_text())[:700])
        receipts.append(receipt)
        s['validation'].update(controlsReviewPending=False,publishedNamedRemuneration=named['remuneration'],publishedNamedExpenses=named['expenses'],namedRemunerationSum=s['totalRemuneration'],namedExpensesSum=s['totalDisclosedExpenses'],remunerationResidual=float(rp),expensesResidual=float(ep),residualCause=receipt['residualCause'],summaryTotalReconciled=not bool(rp or ep),maximumIndependentWholeDollarRoundingDifference=float(limit),approvalPdfPages=approval,periodVerifiedFromOriginal=True,controlPdfPage=named['physicalPage'])
        s['threshold']=75000;s['thresholdRule']='as-published';s['amountPrecision']='whole-dollars' if all(isinstance(r[3],int) for r in rows) else 'cents'
        s['scopeDescription']='Complete named employee disclosure at the published threshold; separate board and aggregate scopes excluded.' if s['completeEmployeeSchedule'] else 'Published employee schedule excluding board-member employees and severance; incomplete for all employees.'
        if rp or ep:
            warning=f"Published named controls differ from the sums of the displayed rows: remuneration sum {s['totalRemuneration']:,.2f} versus printed {named['remuneration']:,.2f} (residual {rp:+,.2f}); disclosed expenses sum {s['totalDisclosedExpenses']:,.2f} versus printed {named['expenses']:,.2f} (residual {ep:+,.2f}). Rows are reproduced as published; the cause is not established."
            s['publicWarning']=' '.join(x for x in [s.get('publicWarning'),warning] if x)
            s['notes'].append(warning)
        if s['employerSlug']=='okanagan-college':
            s['notes'].append('The schedule defines remuneration to include taxable benefits and deferred income, with severance exclusions explained in the original reconciliation note. The separate audited salaries-and-benefits figure is not imported as individual pay.')
        if s['employerSlug']=='camosun-college' and s['year'] in snapshot['years']:
            s['retainCompiledPartition']=True
            s['validation'].update(compiledPartitionRetained=True,compiledPartitionRetentionReason='The official employee schedule expressly excludes board-member employees and severance; the unverified compiled partition may have a broader scope.')
            warning='The same-label compiled partition is retained separately because this official schedule excludes board-member employees and severance. Compiled periods and scope remain unverified; the two partitions may overlap and must not be summed as unique employees.'
            s['publicWarning']=' '.join(x for x in [s.get('publicWarning'),warning] if x)
            s['notes'].append(warning)
        if material:
            s['status']='held-for-review';s['reason']='Material published named-control discrepancy; independent full original scope/control review required. Cause not established.';held.append(s)
        dump(OUT/'evidence'/f"{s['id']}-review.json",receipt)
    manifest['sources']=[s for s in manifest['sources'] if s not in held]
    if held:
        held_dir=OUT/'held';held_dir.mkdir(exist_ok=True)
        for s in held:
            (held_dir/s['file']).write_bytes((OUT/s['file']).read_bytes());(OUT/s['file']).unlink()
        dump(held_dir/'sources.json',dict(version=1,rowSchema=manifest['rowSchema'],sources=held))
    dump(OUT/'sources.json',manifest);dump(AUDIT/'control-review.json',receipts)
    # Three original crops per cohort: approval, schedule beginning, schedule end/controls.
    image_dir=Path('/tmp/continuation-education/review');image_dir.mkdir(exist_ok=True)
    for s in manifest['sources']+held:
        r=next(r for r in receipts if r['id']==s['id'])
        doc=fitz.open(s['cacheFile']);spec=[(r['approvalPdfPages'][-1],None),(s['pages'][0],None),(r['namedControl']['physicalPage'],max(0,r['namedControl']['y']-180))]
        sheet=Image.new('RGB',(1800,1050),'white');draw=ImageDraw.Draw(sheet);draw.text((10,5),s['id'],fill='black')
        for i,(p,y) in enumerate(spec):
            page=doc[p-1];rect=page.rect if y is None else fitz.Rect(0,y,page.rect.width,min(y+360,page.rect.height))
            pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),clip=rect);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((590,1010));sheet.paste(im,(i*600,30));draw.text((i*600+5,18),f'Original physical page {p}',fill='black')
        sheet.save(image_dir/f"{s['id']}.png")
    print(json.dumps(dict(cohorts=len(receipts),rows=sum(s['rowCount'] for s in manifest['sources']),renderedSheets=str(image_dir)),indent=2))

if __name__=='__main__':review()
