#!/usr/bin/env python3
"""Prepare complete historical Revelstoke native schedules for final rendered review."""
import json,shutil,hashlib
from pathlib import Path
import fitz
from continue_municipal import words_mupdf,words_poppler,extract
from continue_municipal_config import section,print_control
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-municipal';CACHE=Path('/tmp/continuation-municipal')
def main():
 cfg=json.loads((OUT/'reviewed-layouts.json').read_text());rs=json.loads((ROOT/'research/salaries/sector-search-2026-10-31/municipal/document-receipts.json').read_text())
 for yr,pgs in [('2021',[39,40]),('2023',[48,49]),('2024',[46,47])]:
  rec=next(r for r in rs if r['employerSlug']=='city-of-revelstoke'and r['year']==yr);key='city-of-revelstoke-'+yr;old=Path('/tmp/pofbc-sector-municipal')/(key+'.pdf');shutil.copyfile(old,CACHE/(key+'.pdf'));assert hashlib.sha256(old.read_bytes()).hexdigest()==rec['sha256'];d=fitz.open(old)
  rep={'key':key,'employerSlug':'city-of-revelstoke','employerName':'City of Revelstoke','year':yr,'sourceUrl':rec['url'],'indexUrl':rec['indexUrl'],'sha256':rec['sha256'],'sourceKind':'official-native-pdf','allRowsVisuallyReviewed':False,'remunerationDefinition':'Remuneration is the separate source Remuneration column. Employer benefit expense and payroll-reconciliation components are not added to individual pay.','notes':['These older official originals were previously located but had no accepted cohorts. The complete published named schedules now receive independent PDF-reader comparison and full rendered original review. Names, initials, titles and source spelling are retained; no across-year identity enrichment is applied.'],'periodEvidence':[{'page':3,'text':'Fiscal Year End: December 31, '+yr},{'page':pgs[0],'text':'Elected Officials '+yr},{'page':pgs[1],'text':"Employee's Remuneration over $75,000 & Employment Expenses "+yr}],'sections':[]}
  if yr=='2021':
   cs=section(words_mupdf(d[pgs[0]-1]),'elected-officials',{'name':[54,230],'pay':[230,318],'expenses':[318,380]},190,290,300.4);cs['officePrefixInName']=True
   es=section(words_mupdf(d[pgs[1]-1]),'employee-remuneration',{'name':[25,175],'position':[175,410],'pay':[410,510],'expenses':[510,580]},130,575,585.9)
  elif yr=='2023':
   cs=section(words_mupdf(d[pgs[0]-1]),'elected-officials',{'name':[54,230],'pay':[230,318],'expenses':[318,380]},188,282,291.4);cs['officePrefixInName']=True
   es=section(words_mupdf(d[pgs[1]-1]),'employee-remuneration',{'name':[50,191],'position':[191,430],'pay':[430,505],'expenses':[505,550]},113,628,635.1)
  else:
   cs=section(words_mupdf(d[pgs[0]-1]),'elected-officials',{'name':[54,275],'position':[275,350],'pay':[350,455],'expenses':[455,545]},188,282,291.4)
   es=section(words_mupdf(d[pgs[1]-1]),'employee-remuneration',{'name':[50,183],'position':[183,348],'pay':[348,445],'expenses':[445,535]},117,695,700)
  cs['page']=pgs[0];es['page']=pgs[1];rep['sections']=[cs,es]
  if yr!='2024':rep['notes'].append('Council office is printed as a Mayor/Councillor prefix inside the Name cell; that original prefix is separated into the normalized position field, with the remaining printed name retained.')
  for sec in rep['sections']:
   print_control(rep,sec,d);a=extract(words_mupdf(d[sec['page']-1]),sec);b=extract(words_poppler(CACHE/(key+'.pdf'),sec['page']),sec);assert a==b,[(i,a,b)for i,(a,b)in enumerate(zip(a,b))if a!=b]
  cfg['reports'].append(rep)
 (OUT/'revelstoke-layouts.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
