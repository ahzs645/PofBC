#!/usr/bin/env python3
"""Prepare pinned native layout candidates. Complete image review is a separate gate."""
import json,re,sys,shutil,hashlib
from pathlib import Path
import fitz
from continue_municipal import words_mupdf,extract,money,dollars
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-municipal';CACHE=Path('/tmp/continuation-municipal')
rs=[]
for f in ['archive-receipts.json','additional-receipts.json','priority-receipts.json']:
 rs+=json.loads((ROOT/'research/salaries/continuation-2026-11-01/municipal'/f).read_text())
def y(w):return (w[1]+w[3])/2
def x(w):return (w[0]+w[2])/2
def values_at(ws,yy,cols):
 return {f:money(' '.join(w[4]for w in ws if abs(y(w)-yy)<2 and a<=x(w)<b and w[4]!='$'))for f,(a,b)in cols.items()if f in ['pay','expenses']}
def section(ws,cat,cols,low,high,control_y=None,count=None):
 anchors=[w for w in ws if low<=y(w)<=high and cols['pay'][0]<=x(w)<cols['pay'][1] and re.fullmatch(r'\d+(?:,\d{3})*(?:\.\d\d)?',w[4])]
 if count is not None:anchors=sorted(anchors,key=y)[:count]
 spec={'category':cat,'y':[round(min(map(y,anchors))-2,2),round(max(map(y,anchors))+2,2)],'columns':cols,'rowCount':len(anchors),'maxRowDistance':4,'corrections':[]}
 if control_y is not None:spec['controlsCents']=values_at(ws,control_y,cols)
 return spec
def print_control(report,sec,doc):
 a=[]
 for part in sec.get('parts',[sec]):a+=extract(words_mupdf(doc[part['page']-1]),part)
 residuals={k:sum(r.get(k)or 0 for r in a)-v for k,v in sec['controlsCents'].items()}
 sec['reviewedResidualsCents']=residuals
 sec['controlBasis']='Printed subtotal for the complete named cohort; blank/dash expenses remain unknown and are not imputed to zero.'
 if any(residuals.values()):sec['publicWarning']=f"{report['employerName']} {report['year']} {sec['category']}: known individual remuneration sum {dollars(sum(r['pay']for r in a)):,.2f} CAD versus printed named control {dollars(sec['controlsCents']['pay']):,.2f} CAD (residual {dollars(residuals['pay']):+,.2f}); known individual expenses {dollars(sum(r.get('expenses')or 0 for r in a)):,.2f} CAD versus printed named control {dollars(sec['controlsCents']['expenses']):,.2f} CAD (residual {dollars(residuals['expenses']):+,.2f}). Original values are preserved; the source differences remain unresolved."
 print(report['key'],sec['category'],len(a),'residuals',residuals,'first',a[0],'last',a[-1])
def main():
 reports=[]
 for yr in range(2016,2023):
  r=next(r for r in rs if r['employerSlug']=='city-of-campbell-river' and f'/{yr}-sofi' in r['url']);key=f'city-of-campbell-river-{yr}';shutil.copyfile(r['cachePath'],CACHE/(key+'.pdf'));d=fitz.open(r['cachePath'])
  if yr==2016:cols={'name':[45,173],'position':[173,365],'pay':[365,450],'expenses':[450,540]};ps=[5,6,7]
  elif yr==2017:cols={'name':[45,182],'position':[182,385],'pay':[385,475],'expenses':[475,565]};ps=[6,7,8]
  elif yr==2018:cols={'name':[35,167],'position':[167,405],'pay':[405,495],'expenses':[495,580]};ps=[6,7,8]
  elif yr in [2019,2020]:cols={'name':[53,177],'position':[177,393],'pay':[393,475],'expenses':[475,555]};ps=[6,7,8] if yr==2019 else [6,7,8,9]
  elif yr==2021:cols={'name':[53,153],'position':[153,325],'pay':[325,497],'expenses':[497,555]};ps=[6,7,8]
  elif yr==2022:cols={'name':[58,185],'position':[185,393],'pay':[393,475],'expenses':[475,553]};ps=[6,7,8]
  report={'key':key,'employerSlug':'city-of-campbell-river','employerName':'City of Campbell River','year':str(yr),'sourceUrl':r['url'],'indexUrl':'https://www.campbellriver.ca/financial-plans-and-reports','sha256':r['sha256'],'sourceKind':'official-native-pdf','allRowsVisuallyReviewed':False,'remunerationDefinition':'Remuneration is the separate published Remuneration column. Employer payroll-cost components in the financial-statement reconciliation are not added to individual pay.','periodEvidence':[{'page':5,'text':f'For the Year Ended December 31, {yr}'}],'notes':['Names, punctuation, initials and titles retain the published schedule; no compiled name enrichment is applied. Native tables were read independently with PyMuPDF and Poppler, then every named row and printed control was checked in the rendered original.'],'sections':[]}
  ws=words_mupdf(d[4]);head=[y(w)for w in ws if w[4]in ['Elected','Elected\u00a0Officials']];low=min(head)+5 if head else 170
  count=9 if yr==2018 else 11 if yr==2022 else 7
  # 2021 council uses a different horizontal scale from employee pages.
  ccols=cols
  council=section(ws,'elected-officials',ccols,low,400,count=count);council['page']=5
  control=[w for w in ws if ccols['pay'][0]<=x(w)<ccols['pay'][1]and y(w)>council['y'][1] and re.fullmatch(r'\d+(?:,\d{3})+',w[4])][0]
  council['controlsCents']=values_at(ws,y(control),ccols);report['sections'].append(council)
  parts=[];control=None
  for n in ps:
   ws=words_mupdf(d[n-1]);heads=[y(w)for w in ws if w[4]in ['Employees','Employee']and x(w)<150];low=max(heads)+5 if heads else 90
   totals=[y(w)for w in ws if w[4]=='Total'and x(w)<120 and y(w)>low]
   high=min(totals)-4 if totals else 735
   if any(low<=y(w)<=high and cols['pay'][0]<=x(w)<cols['pay'][1]and re.fullmatch(r'\d+(?:,\d{3})*',w[4])for w in ws):
    part=section(ws,'employee-remuneration',cols,low,high);part['page']=n;parts.append(part)
   if totals:control=values_at(ws,min(totals),cols)
  employee={'category':'employee-remuneration','parts':parts,'controlsCents':control};report['sections'].append(employee)
  for sec in report['sections']:print_control(report,sec,d)
  reports.append(report)
 p=OUT/'candidate-layouts.json';p.write_text(json.dumps({'version':1,'reports':reports},indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
