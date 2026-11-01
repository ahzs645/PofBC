#!/usr/bin/env python3
"""Verify seven newly covered island/coast municipalities, including reviewed OCR."""
import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/salaries/municipal-wave-island"
RECEIPTS = ROOT / "research/salaries/municipal-next-pass/island/retrieval-receipts.json"
MONEY = re.compile(r"^\$?-?(?:\d{1,3}(?:,\d{3})*|0)(?:\.\d{2})?$|^-$")
TABLES = {
    "city-of-courtenay": [("employees", [33,34,35], 0, 145, "Total"), ("council", [32], 0, 190, "TOTAL")],
    "village-of-cumberland": [("employees", [32], 1, 250, "Consolidated"), ("council", [32], 0, 240, "Total:")],
    "town-of-gibsons": [("employees", [10], 0, 145, "Remuneration:"), ("council", [9], 0, 190, "Total")],
    "village-of-gold-river": [("employees", [5], 1, 250, "Consolidated"), ("council", [5], 0, 300, "(A)")],
    "village-of-tahsis": [("employees", [28], 1, 265, "Consolidated"), ("council", [28], 0, 265, "Total")],
    "district-of-ucluelet": [("employees", [30], 0, 130, "Total"), ("council", [29], 0, 130, "Total")],
}
REVIEWED = {
    ("city-of-courtenay","employees"):(99,"10322461","256771"),
    ("city-of-courtenay","council"):(7,"302945","58952"),
    ("village-of-cumberland","employees"):(22,"2077429","48966"),
    ("village-of-cumberland","council"):(5,"90723","26852"),
    ("town-of-gibsons","employees"):(24,"2715735","71293"),
    ("town-of-gibsons","council"):(5,"198492","33276"),
    ("village-of-gold-river","employees"):(5,"551229","10261"),
    ("village-of-gold-river","council"):(5,"48148","13159"),
    ("village-of-tahsis","employees"):(8,"826838","68560"),
    ("village-of-tahsis","council"):(5,"33113","21836"),
    ("district-of-ucluelet","employees"):(19,"1788026.90","58958.69"),
    ("district-of-ucluelet","council"):(6,"104336.03","37834.41"),
}
# Each label is read by Poppler; the actual monetary row is independently read
# from MuPDF coordinates. Named controls derived by subtraction are identified.
CONTROLS = {
 ("city-of-courtenay","employees"):[("named",r"Total for employees where remuneration is over \$75,000",[10322461,256770])],
 ("city-of-courtenay","council"):[("named",r"TOTAL",[302948,58951])],
 ("village-of-cumberland","employees"):[("below",r"Consolidated total of other employees with\s+remuneration and expenses of \$75,000 or less",[1541319,29144]),("all",r"Total: Other Employees",[3618748,78109])],
 ("village-of-cumberland","council"):[("named",r"Total: Council/Elected Officials",[90723,26852])],
 ("town-of-gibsons","employees"):[("named",r"Remuneration:\s+Above \$75,000",[2715735,71293,2787028])],
 ("town-of-gibsons","council"):[("named",r"Total",[198492,33276,231768])],
 ("village-of-gold-river","employees"):[("below",r"Consolidated Total of Employees less than \$75,000",[965499,11336]),("all",r"(?m)^\s*\(B\)",[1516727,21597])],
 ("village-of-gold-river","council"):[("named",r"(?m)^\s*\(A\)",[48147,13159])],
 ("village-of-tahsis","employees"):[("below",r"remuneration of \$75,000 or less",[579585]),("all",r"Total Employees",[1406424,68560])],
 ("village-of-tahsis","council"):[("named",r"Total Elected Officials",[33113,21836])],
 ("district-of-ucluelet","employees"):[("named",r"Total Individual Remuneration Paid over \$75,000",[1788026.90,58958.68])],
 ("district-of-ucluelet","council"):[("named",r"Total Remuneration and Expenses",[104336.03,37834.41])],
}
NUM = r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
APPROVAL = {
 "city-of-courtenay":(45,"2026-06-24","Visible signatures"),
 "village-of-cumberland":(38,"2026-05-25","Published signature notation A. Bérard-Ball and V. Brown"),
 "town-of-gibsons":(1,"2026-06-02","Approved Council resolution R2026-130 and visible certification/finance signatures"),
 "village-of-gold-river":(2,None,"Published Signed notation for Mayor and CAO; date fields blank"),
 "village-of-tahsis":(31,"2026-06-02","Visible signatures"),
 "district-of-ucluelet":(3,"2026-10-05","Visible signatures"),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def amount(token):
    token = token.replace("$", "").strip()
    if token in ("", "-"):
        return None
    if not MONEY.fullmatch(token):
        raise ValueError(f"Unrecognized source amount {token!r}")
    d = Decimal(token.replace(",", ""))
    return int(d) if d == d.to_integral_value() else float(d)


def total(rows, index):
    return sum((Decimal(str(row[index])) for row in rows if row[index] is not None), Decimal(0))


def positioned_table(page, cohort, header_index, name_right, end_token):
    words = page.get_text("words")
    payheads = sorted([w for w in words if w[4] in ("Remuneration", "Renumeration") and (w[0] > 300 or w[4]=="Renumeration" or (w[0]>250 and any(z[4]=="Position" and abs(z[1]-w[1])<2 for z in words)))], key=lambda w: w[1])
    payhead = payheads[header_index]
    hy = payhead[1]
    expenseheads = [w for w in words if w[4] == "Expenses" and abs(w[1]-hy) < 2 and w[0] > payhead[0]]
    assert len(expenseheads) == 1, "Missing or ambiguous expense heading"
    expensehead = expenseheads[0]
    totalheads = [w for w in words if w[4] == "Total" and abs(w[1]-hy) < 2 and w[0] > expensehead[0]]
    heads = [payhead, expensehead] + totalheads
    cutoff = min([w[1] for w in words if w[4] == end_token and w[1] > hy + 2] + [page.rect.height-25])
    body = [w for w in words if hy+2 < w[1] < cutoff-.7]
    names = sorted([w for w in body if w[0] < name_right], key=lambda w: (round(w[1]), w[0]))
    namegroups = []
    for w in names:
        if not namegroups or abs(namegroups[-1][0]-w[1]) > 1:
            namegroups.append([w[1], []])
        namegroups[-1][1].append(w)
    # Tahsis prints the threshold as a full line between the header and the rows.
    namegroups = [g for g in namegroups if not " ".join(w[4] for w in g[1]).startswith("Remuneration over")]
    rows, evidence = [], []
    for i,(y, nw) in enumerate(namegroups):
        nxt = namegroups[i+1][0] if i+1 < len(namegroups) else cutoff
        rw = [w for w in body if y-2 <= w[1] < nxt-2]
        name = " ".join(w[4] for w in sorted(nw,key=lambda w:w[0]))
        assert name and not any(x in name for x in ["Prepared under", "Statement of", "TOTAL"]), (name,rw)
        if cohort != "tahsis":
            assert "," in name, ("Unreviewed name boundary", name)
        values, used = [], set()
        for j,h in enumerate(heads):
            right = heads[j+1][0]-4 if j+1 < len(heads) else page.rect.width
            candidates = [(k,w) for k,w in enumerate(rw) if h[0]-12 < w[0] < right and MONEY.fullmatch(w[4])]
            assert len(candidates) <= 1, ("Ambiguous monetary cell",name,j,candidates)
            values.append(amount(candidates[0][1][4]) if candidates else None)
            used.update(k for k,w in candidates)
        assert values[0] is not None, ("Missing remuneration",name,rw)
        titlewords = [w for k,w in enumerate(rw) if k not in used and w[0]>=name_right and w[4]!="$" and not w[4].startswith("$")]
        title = " ".join(w[4] for w in sorted(titlewords,key=lambda w:(round(w[1]),w[0]))) or None
        if len(values)==3:
            assert values[1] is not None and Decimal(str(values[0]))+Decimal(str(values[1])) == Decimal(str(values[2])), ("Printed row total differs",name,values)
        row = [name,title,values[0],values[1],page.number+1]
        rows.append(row)
        evidence.append({"row":row,"printedExpenseInclusiveTotal":values[2] if len(values)==3 else None,"words":[list(w[:5]) for w in rw]})
    return rows,evidence


def layout_table(text, slug, kind):
    lines=text.splitlines()
    if slug == "town-of-gibsons":
        headers=[i for i,l in enumerate(lines) if re.fullmatch(r"\s*(?:Remuneration|Renumeration)\s+Expenses\s+Total\s*",l)]
    elif slug == "village-of-gold-river":
        headers=[i for i,l in enumerate(lines) if ("Employees" in l if kind=="employees" else "Elected Official" in l) and "Remuneration" in l and "Expenses" in l]
    else:
        headers=[i for i,l in enumerate(lines) if re.search(r"(?:Name|Employee|Elected Official)\s+Position\s+(?:Total\s+)?Remuneration(?:\s+\(\$\)1)?\s+Expenses",l)]
        if slug in ["village-of-cumberland","village-of-tahsis"]:
            headers=[headers[1 if kind=="employees" else 0]]
    assert len(headers)==1, (slug,kind,"layout header",headers)
    out=[];current=None
    for line in lines[headers[0]+1:]:
        st=line.strip()
        if not st:continue
        if st.startswith(("Total", "TOTAL", "Consolidated", "Remuneration:", "(A)")):break
        if st.startswith("Remuneration over"):continue
        if st.startswith("Prepared under"):break
        parts=re.split(r"\s{2,}",st)
        starts_name=("," in parts[0] and not MONEY.fullmatch(parts[0].replace("$", "").strip())) if slug!="village-of-tahsis" else (len(line)-len(line.lstrip())<5)
        if starts_name:
            if current is not None:out.append(current)
            current=[parts.pop(0),[],[]]
        assert current is not None, (slug,kind,"text before name",line)
        for part in parts:
            clean=part.replace("$", "").strip()
            if MONEY.fullmatch(clean):current[2].append(amount(clean))
            elif clean:current[1].append(part)
    if current is not None:out.append(current)
    result=[]
    for name,title,nums in out:
        required=3 if slug=="town-of-gibsons" else 2
        assert 1<=len(nums)<=required,(slug,name,title,nums)
        nums+= [None]*(required-len(nums))
        if required==3:assert Decimal(str(nums[0]))+Decimal(str(nums[1]))==Decimal(str(nums[2]))
        result.append([name," ".join(title) or None,nums[0],nums[1]])
    return result


def read_controls(page,layout,specs):
    words=page.get_text("words");controls=[]
    for scope,label,expected in specs:
        matches=list(re.finditer(label+r"\s*\$?\s*("+NUM+r")([^\n]*)",layout,re.I))
        assert len(matches)==1,("Control label missing or ambiguous",label)
        match=matches[0]
        actual=[amount(match[1])]+[amount(x) for x in re.findall(NUM,match[2])]
        assert actual==expected,("Printed control changed",label,actual,expected)
        anchors=[w for w in words if w[0]>300 and MONEY.fullmatch(w[4]) and amount(w[4])==expected[0]]
        candidates=[]
        for anchor in anchors:
            row=sorted([w for w in words if abs(w[1]-anchor[1])<2 and w[0]>=anchor[0]-1 and MONEY.fullmatch(w[4])],key=lambda w:w[0])
            if [amount(w[4]) for w in row]==expected:candidates.append(row)
        assert len(candidates)==1,("Independent controls disagree or are ambiguous",label,candidates,expected)
        row=candidates[0]
        controls.append({"scope":scope,"labelRegex":label,"printedValues":actual,"physicalPdfPage":page.number+1,"bothReadersAgree":True,"positionedWords":[list(w[:5]) for w in row]})
    return controls


def visible_title_guard(slug,kind,page,rows):
    if slug=="city-of-courtenay" and kind=="employees" and page==35:
        # Poppler exposes hidden glyphs beyond the visibly clipped cell.
        targets=[r for r in rows if r[0]=="Wyka, R."]
        assert len(targets)==1
        target=targets[0]
        assert target==["Wyka, R.","Manager of Financial Planning, Payroll & Business Performance",131252,2362]
        target[1]="Manager of Financial Planning, Payroll & Business Perform"
    return rows


def sayward_ocr(cache,receipts,download=False):
    reviewfile=OUT/'review/sayward-2024-ocr.json';rawreview=reviewfile.read_bytes()
    assert sha(rawreview)=='0c231b9a98b8e5811e2c1ab746713f0c75de7aec1f26572539421fd9db60b160',"Reviewed OCR evidence changed"
    review=json.loads(rawreview);pdf=cache/'village-of-sayward.pdf'
    if not pdf.exists() and download:
        with urllib.request.urlopen(urllib.request.Request(review['sourceUrl'],headers={'User-Agent':'Mozilla/5.0 public source verification'}),timeout=60) as response:downloaded=response.read()
        assert downloaded.startswith(b'%PDF-'),"OCR original download is not a PDF"
        cache.mkdir(parents=True,exist_ok=True);pdf.write_bytes(downloaded)
    raw=pdf.read_bytes()
    assert sha(raw)==review['sourceSha256']==receipts['village-of-sayward']['sha256']
    doc=fitz.open(pdf);assert len(doc)==8 and not any(p.get_text() for p in doc)
    normalized=[]
    for index,reading in enumerate(review['rawReadings']):
        text=reading['text'];assert sha(text.encode())==reading['sha256']
        for correction in review['guardedCorrections']:
            if correction['reading']!=index:continue
            before,after=correction['before'],correction['after']
            lines=text.splitlines();assert lines.count(before)==1,("OCR correction context changed",before)
            text='\n'.join(after if line==before else line for line in lines)+'\n'
        rows=[]
        for line in text.splitlines():
            match=re.fullmatch(r"([A-Za-z ,]+) - ([A-Za-z ]+) ("+NUM+r") ("+NUM+r")",line)
            if match:rows.append([match[1],match[2],amount(match[3]),amount(match[4])])
        assert rows==review['manualImageTranscription'],("OCR and complete manual image reading differ",index,rows)
        normalized.append(rows)
    assert normalized[0]==normalized[1]
    outputs={'review/sayward-2024-ocr.json':rawreview};sources=[]
    for kind,rawrows in [('employees',normalized[0][7:]),('council',normalized[0][:7])]:
        rows=[['village-of-sayward']+r+[3] for r in rawrows]
        controls=review['printedControls'];paycontrol=controls['namedEmployeeRemuneration' if kind=='employees' else 'electedRemuneration'];expcontrol=controls['namedEmployeeExpenses' if kind=='employees' else 'electedExpenses']
        residuals=[float(total(rows,3)-Decimal(paycontrol)),float(total(rows,4)-Decimal(expcontrol))]
        assert residuals==([0,0] if kind=='employees' else [0,-1]),"Reviewed OCR controls changed"
        body=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode();packed=gzip.compress(body,mtime=0);filename=f'village-of-sayward-2024-{kind}.json.gzip';outputs[filename]=packed
        warning=None if kind=='employees' else 'Published council expenses sum to $16,876; the printed subtotal is $16,877. The $1 shortfall is unresolved. All published amounts, including two explicit zero expenses, are retained unchanged.'
        sources.append({'id':f'wave-island-village-of-sayward-2024-{kind}','employerSlug':'village-of-sayward','employerName':'Village of Sayward','sector':'Municipalities','year':'2024','periodType':'calendar','periodStart':'2024-01-01','periodEnd':'2024-12-31','title':f'Village of Sayward 2024 official {kind} remuneration and expenses (reviewed scanned original)','sourceUrl':review['sourceUrl'],'sourceIndexUrl':review['sourceIndexUrl'],'sha256':sha(raw),'pdfBytes':len(raw),'file':filename,'dataSha256':sha(packed),'normalizedSha256':sha(body),'currency':'CAD','scope':'employee-remuneration' if kind=='employees' else 'elected-officials','category':'employee-remuneration' if kind=='employees' else 'elected-officials','threshold':75000 if kind=='employees' else None,'thresholdComparison':'>' if kind=='employees' else None,'nameDisclosure':'as-published','positionDisclosure':'as-published','rowCount':len(rows),'totalRemuneration':float(total(rows,3)),'totalDisclosedExpenses':float(total(rows,4)),'pages':[3],'status':'verified','verifiedOn':'2026-10-31','publicWarning':warning,'notes':['Complete scanned named cohort transcribed. Two retained Tesseract configurations are checked against a separate complete manual image reading; they are not described as independent OCR engines.','Five OCR row contexts are guarded and corrected only from the rendered original. Every name, title, remuneration, expense, reporting heading and control was visually reviewed.','Numeric zero expenses for Gilkin, Kohen and Tinsley, Tom remain zero. No blank was inferred to be zero.','The report says calendar 2024 and is visibly approved May 6, 2025; its 2026 upload path is not its reporting period.','No compiled records are removed, relabelled or enriched from this source.'],'validation':{'sourceFingerprintLocked':True,'completeNamedCohort':True,'methods':['Tesseract250dpiPSM6 with guarded image-grounded corrections','Tesseract300dpiPSM3','Independent complete manual transcription of every rendered named row'],'allNamedCellsVisuallyVerified':True,'ocrReadingsAgreeAfterGuardedCorrections':True,'remunerationResidual':residuals[0],'expensesResidual':residuals[1],'summaryTotalReconciled':residuals==[0,0],'printedNamedRemuneration':paycontrol,'printedNamedExpenses':expcontrol,'missingExpenseRows':0,'explicitZeroExpenseRows':sum(r[4]==0 for r in rows),'negativeExpenseRows':0,'approvalPhysicalPage':7,'approvalDate':'2025-05-06','approvalRepresentation':review['visualReview']['approvalRepresentation'],'evidenceFile':'review/sayward-2024-ocr.json','evidenceSha256':sha(rawreview)}})
        sources[-1]['validation'].update({'ocrConfigurationsAreIndependentEngines':False,'secondHumanAllNamedCellsVerified':True,'independentCrossReviewFile':'../municipal-next-pass/reviews/sayward-ocr.md'})
    return outputs,sources


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache",type=Path,default=Path("/tmp/pofbc-wave-island"))
    ap.add_argument("--inspect",action="store_true",help="extract and report candidates without writing accepted outputs")
    ap.add_argument("--verify",action="store_true",help="compare accepted outputs without writing")
    ap.add_argument("--download",action="store_true",help="download a missing original from its pinned official URL")
    ap.add_argument("--output",type=Path,default=OUT)
    args=ap.parse_args()
    receipts={x['employerSlug']:x for x in json.loads(RECEIPTS.read_text())}
    outputs={};sources=[]
    for slug,tables in TABLES.items():
        receipt=receipts[slug];pdf=args.cache/(slug+".pdf")
        if not pdf.exists() and args.download:
            with urllib.request.urlopen(urllib.request.Request(receipt['sourceUrl'],headers={'User-Agent':'Mozilla/5.0 public source verification'}),timeout=60) as response:raw=response.read()
            assert raw.startswith(b'%PDF-'),"Original download is not a PDF"
            args.cache.mkdir(parents=True,exist_ok=True);pdf.write_bytes(raw)
        raw=pdf.read_bytes()
        assert sha(raw)==receipt['sha256'],(slug,"Original hash changed")
        doc=fitz.open(pdf)
        assert re.search(r"(?:December\s+31,?\s+2025|for the Year 2025)"," ".join(p.get_text() for p in doc),re.I),(slug,"Source period")
        for kind,pages,headindex,nameright,end in tables:
            allrows=[];allevidence=[];rawlayouts=[]
            for n in pages:
                primary,ev=positioned_table(doc[n-1],"tahsis" if slug=="village-of-tahsis" else kind,headindex,nameright,end)
                layout=subprocess.check_output(['pdftotext','-f',str(n),'-l',str(n),'-layout',str(pdf),'-'],text=True)
                rawlayouts.append({"physicalPdfPage":n,"popplerLayoutText":layout})
                secondary=layout_table(layout,slug,kind)
                secondary=visible_title_guard(slug,kind,n,secondary)
                assert [r[:4] for r in primary]==secondary,(slug,kind,n,"Independent readers differ",[(a,b) for a,b in zip(primary,secondary) if a[:4]!=b][:2],len(primary),len(secondary))
                allrows.extend([[slug]+r for r in primary]);allevidence.extend(ev)
            count,pay,expense=REVIEWED[(slug,kind)]
            assert (len(allrows),total(allrows,3),total(allrows,4))==(count,Decimal(pay),Decimal(expense)),("Reviewed counts/totals changed",slug,kind)
            controls=read_controls(doc[pages[-1]-1],rawlayouts[-1]['popplerLayoutText'],CONTROLS[(slug,kind)])
            byscope={x['scope']:x['printedValues'] for x in controls}
            if 'named' in byscope:
                named=byscope['named'][:2];basis='Directly printed named-cohort subtotal'
            else:
                named=[byscope['all'][i]-byscope['below'][i] if len(byscope['below'])>i else None for i in [0,1]]
                basis='Derived as printed all-employee total minus printed below-threshold aggregate; not a separately printed named subtotal'
            residuals=[float(total(allrows,i+3)-Decimal(str(named[i]))) if named[i] is not None else None for i in [0,1]]
            warnings=[]
            residual_text=["not separately controlled" if x is None else f"${x:+g}" for x in residuals]
            if any(x not in [None,0] for x in residuals):warnings.append(f"Published named rows differ from {'the printed named subtotals' if 'named' in byscope else 'controls derived from printed all-employee and below-threshold aggregates'}: remuneration {residual_text[0]}; expenses {residual_text[1]}. The cause is unresolved; every published cell is retained unchanged.")
            below=[r for r in allrows if kind=='employees' and r[3]<75000]
            if below:warnings.append(f"The source places {len(below)} employees with remuneration below $75,000 in its named schedule despite its remuneration threshold heading. The source rows and separate expenses are retained; no threshold explanation is assumed.")
            if slug=='village-of-tahsis' and kind=='employees':warnings.append('The source does not print a separate below-threshold expense aggregate or named-expense subtotal. The named numeric expense sum equals its all-employee expense total; no missing aggregate is assumed zero.')
            filename=f'{slug}-2025-{kind}.json.gzip'
            body=json.dumps(allrows,ensure_ascii=False,separators=(',',':')).encode();packed=gzip.compress(body,mtime=0)
            outputs[filename]=packed
            evidencefile=f'evidence/{slug}-2025-{kind}.json.gzip'
            evidence={"originalSha256":sha(raw),"independentReaders":["PyMuPDF positioned words","Poppler layout text"],"rows":allevidence,"layoutReadings":rawlayouts,"controls":controls,"guardedVisualCorrections":[{"physicalPdfPage":35,"name":"Wyka, R.","popplerHiddenTextTitle":"Manager of Financial Planning, Payroll & Business Performance","visibleTitle":"Manager of Financial Planning, Payroll & Business Perform","reason":"Rendered source clips the final word; source visible glyphs and MuPDF agree."}] if slug=='city-of-courtenay' and kind=='employees' else []}
            evidencepacked=gzip.compress(json.dumps(evidence,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);outputs[evidencefile]=evidencepacked
            sources.append({"id":f'wave-island-{slug}-2025-{kind}',"employerSlug":slug,"employerName":receipt['employerName'],"sector":"Municipalities","year":"2025","periodType":"calendar","periodStart":"2025-01-01","periodEnd":"2025-12-31","title":f"{receipt['employerName']} 2025 official {'employee' if kind=='employees' else 'elected official'} remuneration and expenses","sourceUrl":receipt['sourceUrl'],"sourceIndexUrl":receipt['sourceIndexUrl'],"sha256":sha(raw),"pdfBytes":len(raw),"file":filename,"dataSha256":sha(packed),"normalizedSha256":sha(body),"currency":"CAD","scope":"employee-remuneration" if kind=='employees' else "elected-officials","category":"employee-remuneration" if kind=='employees' else "elected-officials","threshold":75000 if kind=='employees' else None,"thresholdComparison":None if kind=='council' or slug=='village-of-cumberland' else ">","nameDisclosure":"as-published","positionDisclosure":"as-published","rowCount":len(allrows),"totalRemuneration":float(total(allrows,3)),"totalDisclosedExpenses":float(total(allrows,4)),"pages":pages,"status":"verified","verifiedOn":"2026-10-31","publicWarning":" ".join(warnings) or None,"notes":["Employee and elected-official cohorts remain separate. Under-threshold and grand-total aggregates are evidence controls only, not individual records.","Blank and dash expense cells remain missing; numeric zeroes and negative amounts retain their source meaning. Names, initials, published title abbreviations and source spelling are retained without identity inference.","Remuneration and expenses are separate source columns. Expense-inclusive Total columns in Gibsons are retained only as evidence; they are never imported as remuneration.","No compiled records are deleted or relabelled by this collection."]+( ["Remuneration includes gross salary and applicable benefits. The source defines expenses broadly, including third-party payments for job functions, and distinguishes cash payments from accrual-basis financial statements."] if slug=='district-of-ucluelet' else []),"validation":{"sourceFingerprintLocked":True,"completeNamedCohort":True,"rowsIndependentlyCompared":len(allrows),"bothReadersAgreeAfterGuardedVisibleTextCorrection":True,"physicalPdfPages":pages,"printedControls":controls,"namedControlBasis":basis,"namedControlValues":named,"remunerationResidual":residuals[0],"expensesResidual":residuals[1],"summaryTotalReconciled":residuals==[0,0],"belowPrintedRemunerationThresholdRows":[{"name":r[1],"remuneration":r[3],"expenses":r[4],"pdfPage":r[5]} for r in below],"missingExpenseRows":sum(r[4] is None for r in allrows),"explicitZeroExpenseRows":sum(r[4]==0 for r in allrows),"negativeExpenseRows":sum(r[4] is not None and r[4]<0 for r in allrows),"evidenceFile":evidencefile,"evidenceSha256":sha(evidencepacked)}})
            apage,adate,arep=APPROVAL[slug]
            sources[-1]['validation'].update({'visualReviewPdfPages':pages,'allNamedSchedulePagesVisuallyInspected':True,'approvalPhysicalPage':apage,'approvalDate':adate,'approvalRepresentation':arep,'approvalPageVisuallyReviewed':True})
            if slug=='city-of-courtenay' and kind=='employees':sources[-1]['notes'].append("Wyka, R.'s title is visibly clipped at Perform. A guarded correction removes hidden Poppler-only glyphs; the visible source and PyMuPDF agree. The full title is not inferred.")
            if slug=='village-of-cumberland' and kind=='employees':sources[-1]['notes'].append('The below-threshold aggregate says remuneration and expenses of $75,000 or less. The exact selection rule is not inferred; all 22 published named rows independently have remuneration above $75,000.')
            print(json.dumps(dict(slug=slug,kind=kind,count=len(allrows),pay=str(total(allrows,3)),expenses=str(total(allrows,4)),first=allrows[0],last=allrows[-1]),ensure_ascii=False))
            (args.cache/(slug+'-'+kind+'-candidate.json')).write_text(json.dumps(dict(rows=allrows,evidence=allevidence),ensure_ascii=False,indent=2))
    ocroutputs,ocrsources=sayward_ocr(args.cache,receipts,args.download);outputs.update(ocroutputs);sources.extend(ocrsources)
    outputs['sources.json']=(json.dumps({"version":1,"rowSchema":["employerSlug","name","position","remuneration","expenses","pdfPage"],"sources":sources},ensure_ascii=False,indent=2)+'\n').encode()
    if not args.inspect:
        for file,data in outputs.items():
            destination=args.output/file
            if args.verify:assert destination.read_bytes()==data,("Reproduction mismatch",destination)
            else:destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    print(json.dumps({"verifiedSources":len(sources),"verifiedRows":sum(s['rowCount'] for s in sources),"mode":"inspect" if args.inspect else "verify" if args.verify else "write"}))


if __name__=="__main__":main()
