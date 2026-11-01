"""Independent PDFMiner review of the two assigned current Crown employee tables."""
import collections,gzip,hashlib,json,re
from pathlib import Path
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'research/salaries/continuation-2026-11-01/reviews'
TARGETS={'continuation-crowns-icbc-2025-26':[(30,200,253,310),(310,460,514,585)],'continuation-crowns-bclc-2024-25':[(55,395,475,560)]}
def sha(b):return hashlib.sha256(b).hexdigest()
def value(s):
 if s in ['-','—','–','‐','']:return None
 if not re.fullmatch(r'\(?-?\d[\d,]*\)?',s):raise ValueError(s)
 return int(s.replace(',','').replace('(','-').replace(')',''))
def main():
 specs=json.loads((ROOT/'research/salaries/continuation-2026-11-01/crowns/source-specs.json').read_text())
 reports=[]
 for s in specs:
  if s['id'] not in TARGETS:continue
  raw=Path(s['localPath']).read_bytes();assert sha(raw)==s['sha256']
  result=[];counts=[]
  with pdfplumber.open(s['localPath']) as pdf:
   for pn in s['pages']:
    words=pdf.pages[pn-1].extract_words(x_tolerance=1.2,y_tolerance=2)
    before=len(result)
    for lo,name_end,pay_end,exp_end in TARGETS[s['id']]:
     # Select salary tokens from the salary cell, then read the same baseline's
     # name and expense from fixed, reviewed published column rectangles.
     pays=[w for w in words if name_end<w['x0']<pay_end and re.fullmatch(r'\d[\d,]*',w['text'])]
     for p in sorted(pays,key=lambda w:w['top']):
      yy=(p['top']+p['bottom'])/2
      same=[w for w in words if abs((w['top']+w['bottom'])/2-yy)<2 and lo<=w['x0']<exp_end and w['text']!='$']
      n=' '.join(w['text'] for w in sorted(same,key=lambda w:w['x0']) if w['x0']<name_end)
      if not n or n.upper()!=n or n.startswith(('RECEIVER GEN.','TOTAL FOR','OTHER UNDER','GRAND TOTAL')):continue
      if s['employerSlug']=='bclc' and ',' not in n:continue
      if any(c.isdigit() for c in n):continue
      ex=[w['text'] for w in same if w['x0']>=pay_end]
      assert len(ex)==1,(s['id'],pn,n,ex)
      pay=value(p['text']);assert pay>75000
      result.append([s['employerSlug'],n,None,pay,value(ex[0]),pn])
    counts.append([pn,len(result)-before])
  target=ROOT/'research/salaries/continuation-crowns'/s['file'];expected=json.loads(gzip.decompress(target.read_bytes()))
  assert result==expected,[(i,a,b) for i,(a,b) in enumerate(zip(result,expected)) if a!=b][:5]
  reports.append(dict(id=s['id'],originalPath=s['localPath'],sourceSha256=s['sha256'],dataSha256=sha(target.read_bytes()),independentReader='PDFMiner/pdfplumber fixed cell rectangles; no worker parser imported',rows=len(result),allRowsAndPagesExactlyAgree=True,pageCounts=counts,paySum=sum(r[3] for r in result),expensesSum=sum(r[4] or 0 for r in result),nullExpenses=sum(r[4] is None for r in result),zeroExpenses=sum(r[4]==0 for r in result),negativeExpenses=sum(r[4] is not None and r[4]<0 for r in result),repeatedPublishedNames=[{'name':k,'count':v} for k,v in collections.Counter(r[1] for r in result).items() if v>1]))
 REVIEW.mkdir(exist_ok=True,parents=True)
 prior=json.loads((REVIEW/'crowns-current.json').read_text()) if (REVIEW/'crowns-current.json').exists() else {}
 previous={x['id']:x for x in prior.get('results',[])}
 for report in reports:
  merged=previous.get(report['id'],{});merged.update(report);report.update(merged)
 (REVIEW/'crowns-current.json').write_text(json.dumps({'reviewDate':'2026-11-01','reviewer':'health-continuation independent worker','results':reports},indent=2)+'\n')
 print([(r['id'],r['rows'],r['paySum'],r['expensesSum']) for r in reports])
if __name__=='__main__':main()
