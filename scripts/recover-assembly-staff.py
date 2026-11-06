#!/usr/bin/env python3
"""Offline deterministic recovery from official Assembly employee PDFs. Requires pdfplumber and pdftotext."""
from pathlib import Path
import gzip, hashlib, json, re, subprocess
import pdfplumber
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'research/salaries/assembly-staff-recovery'
SLUG = 'legislative-assembly-staff'
EXPECTED = {'2021-22':92,'2022-23':119,'2023-24':144,'2024-25':178,'2025-26':210}
def digest(b): return hashlib.sha256(b).hexdigest()
def parse(path):
    rows=[]; controls=[]
    with pdfplumber.open(path) as pdf:
        for pn,page in enumerate(pdf.pages,1):
            words=page.extract_words()
            header=next(w for w in words if w['text']=='Overtime')
            hy=header['top']
            headers=[w for w in words if abs(w['top']-hy)<2]
            hx=lambda text: next(w['x0'] for w in headers if w['text']==text)
            job=136 if path.stem=='2021-22' else hx('Job')-1
            salary=hx('Salary')-15
            total=hx('Total')-1
            first=next((w['x0']-1 for w in headers if w['text']=='First'),None)
            for w in words:
                if w['x0']<total or w['top']<=hy+5 or not re.fullmatch(r'\d[\d,]*',w['text']): continue
                line=sorted([v for v in words if abs(v['top']-w['top'])<2],key=lambda v:v['x0'])
                left=[v for v in line if v['x0']<job]
                value=int(w['text'].replace(',',''))
                if not left or left[0]['text']=='Total': controls.append(value);continue
                if first is None: name=' '.join(v['text'] for v in left)
                else: name=' '.join(v['text'] for v in left if v['x0']<first)+', '+' '.join(v['text'] for v in left if v['x0']>=first)
                title=' '.join(v['text'] for v in line if job<=v['x0']<salary)
                assert name and title and value>=75000, (name,title,value)
                rows.append([SLUG,name,title,value,None,pn])
    # Grand totals may have individually positioned digit groups in the PDF.
    # Independent Poppler line extraction verifies each published total and row coverage.
    layout=subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)
    pay=[]; controls=[]
    for line in layout.splitlines():
        if line.strip().startswith('Total') or re.fullmatch(r'[\s\d,$]+',line) and re.search(r'\d,\d{3},\d{3}',line):
            match=re.search(r'(\d[\d,]+)\s*$',line)
            if match: controls.append(int(match[1].replace(',','')))
        if re.search(r'\d[\d,]+\s*$',line) and re.search('[A-Za-z]',line) and not line.strip().startswith(('Paid','Total','Page','Note')):
            pay.append(int(re.search(r'(\d[\d,]+)\s*$',line)[1].replace(',','')))
    assert len(controls)==1,controls
    assert pay==[r[3] for r in rows], (len(pay),len(rows),[(a,b) for a,b in zip(pay,[r[3] for r in rows]) if a!=b][:8])
    assert len(rows)==EXPECTED[path.stem]
    assert len({r[1] for r in rows})==len(rows)
    residual=sum(r[3] for r in rows)-controls[0]
    assert abs(residual)<=len(rows)/2, (len(rows),sum(r[3] for r in rows),controls,residual)
    return rows,controls[0],residual

def main():
    sources=[]
    for label in EXPECTED:
        path=DEST/'originals'/f'{label}.pdf'; rows,control,residual=parse(path)
        raw=path.read_bytes(); data=gzip.compress((json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
        (DEST/f'{label}.json.gzip').write_bytes(data)
        y=int(label[:4]);year=label.replace('-','/')
        sources.append(dict(id=f'assembly-staff-{label}',employerSlug=SLUG,employerName='Legislative Assembly of British Columbia staff',sector='Government',year=year,title=f'Legislative Assembly administration staff compensation {year}',sourceUrl=f'https://lims.leg.bc.ca/pdms/file/content-committees/AccountabilityDocuments/accountability/docs/{label}/Employee-Salaries-75k-FY{label}.pdf',indexUrl='https://www.leg.bc.ca/about/accountability/employee-disclosures',sha256=digest(raw),pdfBytes=len(raw),originalFile=f'originals/{label}.pdf',file=f'{label}.json.gzip',dataSha256=digest(data),periodType='fiscal',periodStart=f'{y}-04-01',periodEnd=f'{y+1}-03-31',currency='CAD',scope='employee-remuneration',category='employee-remuneration',threshold=75000,thresholdComparison='>=',nameDisclosure='as-published',positionDisclosure='as-published',amountUnit='dollars',amountPrecision='whole-dollar',rowCount=len(rows),totalRemuneration=sum(r[3] for r in rows),pages=sorted({r[5] for r in rows}),status='accepted',verifiedOn='2026-11-06',completeEmployeeSchedule=True,notes=['Administration employee payments of $75,000 or greater only; excludes caucus and constituency office staff and elected MLAs.','Cash-basis total salary payments include salary, overtime and vacation payout, not an annual salary rate. Salary also includes taxable benefits and other salary-related payments.','Expenses are not disclosed and remain null. Names and positions are preserved as published; no cross-year identity inference.','Published row totals are retained unchanged. Small differences against the printed grand total are recorded as whole-dollar reporting residuals.'],validation={'independentTotalColumnReadingsAgree':True,'publishedTotalRemuneration':control,'namedRemunerationResidual':residual,'rowCount':len(rows),'nullExpenseCount':len(rows)}))
        print(label,len(rows),sum(r[3] for r in rows),control,residual)
    (DEST/'sources.json').write_text(json.dumps({'version':1,'rowSchema':['employerSlug','name','position','remuneration','expenses','pdfPage'],'sources':sources,'coverageNotes':['Separate Assembly administration staff cohort. Not elected MLA compensation.','Annual reports recovered for 2021/22–2025/26 only. Earlier staff schedules not located. Executive-only reports are not added because they overlap the staff cohort.']},indent=2)+'\n')
if __name__=='__main__':main()
