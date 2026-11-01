#!/usr/bin/env python3
"""Append pinned complete Grand Forks and Lake Country native schedules."""
import json,re,shutil
from pathlib import Path
import fitz
from continue_municipal import words_mupdf,words_poppler,extract
from continue_municipal_config import section,values_at,print_control,y,x
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-municipal';CACHE=Path('/tmp/continuation-municipal')
def main():
 cfg=json.loads((OUT/'reviewed-layouts.json').read_text());rs=json.loads((ROOT/'research/salaries/continuation-2026-11-01/municipal/new-search-document-receipts.json').read_text())
 for slug,yr,name,index in [('city-of-grand-forks','2024','City of Grand Forks','https://www.grandforks.ca/financial-administration-department/'),('district-of-lake-country','2025','District of Lake Country','https://www.lakecountry.bc.ca/government/document-library/2025-statements-financial-information-sofi-report')]:
  if any(r['key']==slug+'-'+yr for r in cfg['reports']):continue
  rec=next(r for r in rs if r['employerSlug']==slug);key=slug+'-'+yr;shutil.copyfile(rec['cachePath'],CACHE/(key+'.pdf'));d=fitz.open(rec['cachePath'])
  report={'key':key,'employerSlug':slug,'employerName':name,'year':yr,'sourceUrl':rec['url'],'indexUrl':index,'sha256':rec['sha256'],'sourceKind':'official-native-pdf','allRowsVisuallyReviewed':False,'remunerationDefinition':'Remuneration is the source Remuneration column. Expenses and separately published general Benefits remain distinct; the expense-inclusive Total is not pay.','periodEvidence':[],'notes':['Full published named schedules are retained with names/initials and positions exactly as disclosed; no external identity enrichment or additional threshold filtering is applied.'],'sections':[]}
  if slug=='city-of-grand-forks':
   cs=section(words_mupdf(d[37]),'elected-officials',{'name':[80,190],'position':[190,265],'pay':[265,350],'expenses':[350,420],'generalBenefits':[420,485],'expenseInclusiveTotal':[485,545]},180,283,295.1);cs['page']=38
   es=section(words_mupdf(d[38]),'employee-remuneration',{'name':[70,195],'position':[195,340],'pay':[340,425],'expenses':[425,495],'expenseInclusiveTotal':[495,545]},165,576,588);es['page']=39
   report['sections']=[cs,es];report['periodEvidence']=[{'page':38,'text':'Fiscal Year Ended December 31, 2024'},{'page':39,'text':'Fiscal Year Ended December 31, 2024'}]
   report['notes']+=['The report defines the employee schedule as calendar cash payments in its remuneration reconciliation on physical page40. Council Remuneration excludes the separate general Benefits field, matching the source reconciliation measure.', 'The source includes Klein Tanis at74717? Check exact named remuneration before acceptance.']
   es['publicWarning']='The complete published employee cohort includes Klein, Tanis with Remuneration74,917 CAD, Expenses573 CAD and expense-inclusive Total75,490 CAD, despite the printed remuneration-over75,000 label. The original named row is retained; no additional threshold filter is imposed.'
  else:
   cols={'name':[50,148],'position':[148,405],'pay':[405,490],'expenses':[490,550]}
   cs=section(words_mupdf(d[3]),'elected-officials',cols,175,350,count=7);cs['page']=4;cs['ignoreTokens']=['Councillors'];ws=words_mupdf(d[3]);ctrl=next(w for w in ws if w[4]=='217,852.52');cs['controlsCents']=values_at(ws,y(ctrl),cols)
   p1=section(words_mupdf(d[4]),'employee-remuneration',cols,160,752);p1['page']=5
   p2=section(words_mupdf(d[5]),'employee-remuneration',cols,55,486);p2['page']=6
   es={'category':'employee-remuneration','parts':[p1,p2],'controlsCents':{'pay':905465629,'expenses':27770621}}
   report['sections']=[cs,es];report['periodEvidence']=[{'page':4,'text':'for the year ended December 31, 2025'},{'page':5,'text':'for the year ended December 31, 2025'}]
   report['remunerationDefinition']='Remuneration is the published Taxable Remuneration column, including the described accumulated vacation or sick payouts on termination. Other Expenses remain separate; employer EI/CPP costs in the bottom reconciliation are not added to individual pay or named expenses.'
   report['notes'].append('The report labels named schedules Unaudited. Employee controls use the named Employees75,000andgreater subtotal only, not the broader expense column grand total that includes employerEI/CPP.')
  for s in report['sections']:
   print_control(report,s,d)
   for part in s.get('parts',[s]):
    a=extract(words_mupdf(d[part['page']-1]),part);b=extract(words_poppler(CACHE/(key+'.pdf'),part['page']),part)
    assert a==b,[(i,x,y)for i,(x,y)in enumerate(zip(a,b))if x!=y]
  cfg['reports'].append(report)
 (OUT/'more-native-layouts.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
