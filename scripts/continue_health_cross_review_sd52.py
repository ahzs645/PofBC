"""Independent PDFMiner row/control review of SD52 FY2024/25."""
from pathlib import Path
from decimal import Decimal
import collections,gzip,hashlib,json,re
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
PDF=Path('/tmp/pofbc-schools/ministry-sd52-2025.pdf')
REVIEW=ROOT/'research/salaries/continuation-2026-11-01/reviews'
def sha(b):return hashlib.sha256(b).hexdigest()
def cash(s):
 if s in ['', '-', '—']:return None
 assert re.fullmatch(r'\d{1,3}(?:,\d{3})*\.\d{2}',s),s
 return Decimal(s.replace(',',''))
def main():
 raw=PDF.read_bytes();assert sha(raw)=='2fecb9155bd14fa68439947713730d0f1fe9716c332cb0aa3b6b341478e919d9'
 rows=[];trustees=[];counts={}
 with pdfplumber.open(PDF) as d:
  for pn in [53,54,55]:
   ws=d.pages[pn-1].extract_words(x_tolerance=1,y_tolerance=1.5)
   before=len(rows)
   for pay in sorted([w for w in ws if 445<w['x0']<510 and re.fullmatch(r'\d[\d,]*\.\d{2}',w['text'])],key=lambda w:w['top']):
    yy=(pay['top']+pay['bottom'])/2
    same=sorted([w for w in ws if abs((w['top']+w['bottom'])/2-yy)<2],key=lambda w:w['x0'])
    name=' '.join(w['text'] for w in same if w['x0']<200)
    if ',' not in name or name.startswith('TOTAL'):continue
    pos=' '.join(w['text'] for w in same if 200<=w['x0']<445)
    ex=[w['text'] for w in same if 510<=w['x0']<570 and w['text']!='$']
    assert len(ex)<=1,(name,ex)
    v=cash(pay['text']);e=cash(ex[0]) if ex else None
    row=['school-district-52',name,pos or None,v,e,pn]
    if pos.startswith('Board'):trustees.append(row)
    else:
     assert v>=75000,row
     rows.append(row)
   counts[str(pn)]=len(rows)-before
 evidence=ROOT/'research/salaries/continuation-schools/sd52-2025-employees-evidence.json.gzip'
 ev=json.loads(gzip.decompress(evidence.read_bytes()))
 expected=[['school-district-52',r['name'],r['position'],Decimal(r['remuneration']),Decimal(r['expenses']) if r['expenses'] is not None else None,r['pdfPage']] for r in ev['rows']]
 assert rows==expected,[(i,a,b) for i,(a,b) in enumerate(zip(rows,expected)) if a!=b][:4]
 def sums(rs):return [sum((r[j] for r in rs if r[j] is not None),Decimal(0)) for j in [3,4]]
 actual=sums(rows);tr=sums(trustees);printed=[Decimal('17009720.61'),Decimal('182940.38')]
 r=dict(reviewDate='2026-11-01',sourceSha256=sha(raw),sourcePath=str(PDF),sourceEvidenceSha256=sha(evidence.read_bytes()),independentReader='PDFMiner/pdfplumber; independent fixed source cell rectangles; no schools parser imported',employeeRows=len(rows),trusteeRows=len(trustees),employeeRowsByPhysicalPage=counts,allEmployeeNamesPositionsAmountsNullsOrderMultiplicityAndPagesAgree=True,employeeSums=list(map(str,actual)),printedControlLabel='TOTAL EMPLOYEES PAID AT LEAST $75,000',printedControls=list(map(str,printed)),residuals=list(map(str,[a-b for a,b in zip(actual,printed)])),trusteeControlLabel='TOTAL ELECTED OFFICIALS',trusteeSums=list(map(str,tr)),explicitCombinedControlFound=False,derivedCombinedComparatorPermitted=False,scopeConclusion='The printed label explicitly refers to employees. Equality of residuals with separate trustee totals is observed arithmetic, not a published explanation. No comparator adjustment is justified without issuer clarification.',fullRenderedPageReview=[53,54,55],renderedImagePaths=[f'/tmp/continuation-health/review-sd52-page-{n}.png' for n in [53,54,55]],renderedReviewCoverage='Every named employee/trustee row, all three table page boundaries, all monetary headers and the complete printed controls reviewed on rendered originals.',candidateDisposition='Source-faithful complete employee extraction independently corroborated. Source-control meaning remains unresolved; parent may consider warned acceptance under its documented source-control policy, or retain hold pending issuer clarification.',issuerClarificationDraft='The table labels 17,009,720.61 remuneration and182,940.38 expenses as TOTAL EMPLOYEES PAID AT LEAST$75,000. The156named employee rows sum16,901,344.89 and161,620.27. The differences equal the separately printed elected-official totals108,375.72 and21,320.11. Please confirm the intended control scope or provide a corrected schedule; do not change individual source cells without an amended original.',externalRequestsSent=0)
 r['normalizedDataSha256']=sha((ROOT/'research/salaries/continuation-schools/sd52-2025-employees.json.gzip').read_bytes())
 r['issuerClarificationDraft']='The table labels $17,009,720.61 remuneration and $182,940.38 expenses as TOTAL EMPLOYEES PAID AT LEAST $75,000. The 156 named employee rows sum $16,901,344.89 and $161,620.27. The differences equal the separately printed elected-official totals of $108,375.72 and $21,320.11. Please confirm the intended control scope or provide a corrected schedule. Individual source cells should stay unchanged without an amended original.'
 REVIEW.mkdir(parents=True,exist_ok=True);(REVIEW/'school-sd52-controls.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
