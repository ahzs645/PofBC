"""Third-reader fixed-cell review of Museum4 and BC Housing FY2023/24."""
from pathlib import Path
from decimal import Decimal
import collections,gzip,hashlib,json,re
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'research/salaries/continuation-2026-11-01/reviews'
def sha(b):return hashlib.sha256(b).hexdigest()
def cash(s):
 if s in ['', '-', '—', '‐','–']:return None
 if not re.fullmatch(r'\(?-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\)?',s):raise ValueError(s)
 return Decimal(s.replace(',','').replace('(','-').replace(')',''))
def main():
 specs=json.loads((ROOT/'research/salaries/continuation-2026-11-01/crowns/source-specs.json').read_text());reports=[]
 for spec in specs:
  if spec['employerSlug']not in ['royal-bc-museum','bc-housing']:continue
  raw=Path(spec['localPath']).read_bytes();assert sha(raw)==spec['sha256'];rows=[];counts=[]
  name_edge,pay_edge,exp_edge=(330,450,550) if spec['employerSlug']=='royal-bc-museum' else (245,330,420)
  with pdfplumber.open(spec['localPath'])as d:
   for pn in spec['pages']:
    words=d.pages[pn-1].extract_words(x_tolerance=1,y_tolerance=1.5);groups=[]
    for w in sorted(words,key=lambda w:(w['top'],w['x0'])):
     if groups and abs(w['top']-groups[-1][0]['top'])<2:groups[-1].append(w)
     else:groups.append([w])
    before=len(rows)
    for g in groups:
     g.sort(key=lambda w:w['x0'])
     name=' '.join(w['text']for w in g if w['x0']<name_edge and w['text']!='$')
     if name.lower().startswith(('under $75','total')):break
     pay=''.join(w['text']for w in g if name_edge<=w['x0']<pay_edge and w['text']!='$')
     expense=''.join(w['text']for w in g if pay_edge<=w['x0']<exp_edge and w['text']!='$')
     try:v=cash(pay)
     except ValueError:continue
     if v is None or v<=75000:continue
     assert name and any(c.isalpha()for c in name)and not any(c.isdigit()for c in name),(spec['id'],pn,name)
     rows.append([spec['employerSlug'],name,None,v,cash(expense),pn])
    counts.append([pn,len(rows)-before])
  path=ROOT/'research/salaries/continuation-crowns'/spec['file'];expected=json.loads(gzip.decompress(path.read_bytes()),parse_float=Decimal,parse_int=Decimal)
  assert rows==expected,(spec['id'],len(rows),len(expected),[(i,a,b)for i,(a,b)in enumerate(zip(rows,expected))if a!=b][:4])
  sums=[sum((r[c]for r in rows if r[c]is not None),Decimal(0))for c in [3,4]]
  reports.append(dict(id=spec['id'],sourcePath=spec['localPath'],sourceSha256=spec['sha256'],dataSha256=sha(path.read_bytes()),independentReader='PDFMiner/pdfplumber fixed source cell rectangles; no Crown parser imported',rows=len(rows),pageCounts=counts,allRowsNamesAmountsNullsOrderMultiplicityAndPagesAgree=True,rowSums=list(map(str,sums)),sourceComparators=spec['controls'],residuals=[str(v-Decimal(str(c)))if c is not None else None for v,c in zip(sums,spec['controls'])],negativeExpenseRows=[dict(name=r[1],expense=str(r[4]),pdfPage=r[5])for r in rows if r[4]is not None and r[4]<0]))
 prior=json.loads((REVIEW/'crowns-museum-housing.json').read_text()) if (REVIEW/'crowns-museum-housing.json').exists() else {}
 previous={x['id']:x for x in prior.get('results',[])}
 for report in reports:
  merged=previous.get(report['id'],{});merged.update(report);report.update(merged)
 (REVIEW/'crowns-museum-housing.json').write_text(json.dumps({'reviewDate':'2026-11-01','results':reports},indent=2)+'\n')
 print([(r['id'],r['rows'],r['rowSums'])for r in reports])
if __name__=='__main__':main()
