#!/usr/bin/env python3
"""Add individually reviewed native municipal layouts to the municipal continuation."""
import json,shutil
from pathlib import Path
import fitz
from continue_municipal import words_mupdf,extract,words_poppler
from continue_municipal_config import section,values_at,print_control
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-municipal';CACHE=Path('/tmp/continuation-municipal')
rs=json.loads((ROOT/'research/salaries/continuation-2026-11-01/municipal/archive-receipts.json').read_text())
def add():
 cfg=json.loads((OUT/'reviewed-layouts.json').read_text());base=[r for r in cfg['reports']if r['employerSlug']=='city-of-campbell-river']
 for yr,tok,pgs in [('2022','1170',[33,34]),('2024','1275',[42,43])]:
  receipt=next(r for r in rs if r['employerSlug']=='city-of-salmon-arm'and tok in r['url']);key='city-of-salmon-arm-'+yr;shutil.copyfile(receipt['cachePath'],CACHE/(key+'.pdf'));d=fitz.open(receipt['cachePath'])
  report={'key':key,'employerSlug':'city-of-salmon-arm','employerName':'City of Salmon Arm','year':yr,'sourceUrl':receipt['url'],'indexUrl':'https://www.salmonarm.ca/Archive.aspx?AMID=52','sha256':receipt['sha256'],'sourceKind':'official-native-pdf','allRowsVisuallyReviewed':True,'remunerationDefinition':'Remuneration is the source Remuneration column. Council Life & Health Benefit is separately disclosed and is not added to its chosen Remuneration measure; the expense-inclusive Total is not remuneration.','periodEvidence':[{'page':pgs[0],'text':'For the Year Ended December 31, '+yr}],'notes':['The employee schedule describes gross remuneration'+(', including vacation and overtime banks.'if yr=='2024'else ', bonuses and gratuities.'),'The source marks these named schedules Unaudited. Every named table cell and printed control was checked in the complete rendered original. Native source spellings and truncated published titles are retained.'],'sections':[]}
  if yr=='2022':
   cs=section(words_mupdf(d[pgs[0]-1]),'elected-officials',{'name':[35,175],'position':[175,265],'pay':[265,347],'expenses':[347,407],'lifeHealthBenefits':[407,486],'expenseInclusiveTotal':[486,545]},230,347,362)
   es=section(words_mupdf(d[pgs[1]-1]),'employee-remuneration',{'name':[35,155],'position':[155,370],'pay':[370,440],'expenses':[440,488],'expenseInclusiveTotal':[488,545]},209,595,603)
  else:
   cs=section(words_mupdf(d[pgs[0]-1]),'elected-officials',{'name':[50,190],'position':[190,278],'pay':[278,346],'expenses':[346,410],'lifeHealthBenefits':[410,475],'expenseInclusiveTotal':[475,535]},250,355,367)
   es=section(words_mupdf(d[pgs[1]-1]),'employee-remuneration',{'name':[50,150],'position':[150,323],'pay':[323,377],'expenses':[377,420],'expenseInclusiveTotal':[420,470]},209,670,680.9)
   es['ignoredClippedWords']=[{'text':'Engineer','x':324.0,'y':639.33,'tolerance':1,'reason':'Poppler exposes a glyph run clipped by the original position cell. The complete rendered source visibly ends this title at Coordinator/City; PyMuPDF correctly omits Engineer.'}]
   es['corrections']=[{'row':9,'field':'position','before':['Chief Operator of Waste Water Treatment Plan','Chief Operator of Waste Water Treatment Plant'],'after':'Chief Operator of Waste Water Treatment Plan','reason':'Original clips final t of Plant; visible truncated title retained and corroborating crop reviewed.'},{'row':39,'field':'name','before':'Van De Cappelle, ChelseaChief','after':'Van De Cappelle, Chelsea'},{'row':39,'field':'position','before':'Financial Officer','after':'Chief Financial Officer'}]
  cs['page']=pgs[0];es['page']=pgs[1];report['sections']=[cs,es]
  for sec in report['sections']:
   print_control(report,sec,d)
   a=extract(words_mupdf(d[sec['page']-1]),sec);b=extract(words_poppler(CACHE/(key+'.pdf'),sec['page']),sec)
   print('reader differences',[(i,a,b)for i,(a,b)in enumerate(zip(a,b))if a!=b])
  base.append(report)
 for yr in ['2024','2025']:
  receipt=next(r for r in rs if r['employerSlug']=='district-of-port-edward'and yr+'_Statement' in r['url']);key='district-of-port-edward-'+yr;shutil.copyfile(receipt['cachePath'],CACHE/(key+'.pdf'));d=fitz.open(receipt['cachePath'])
  report={'key':key,'employerSlug':'district-of-port-edward','employerName':'District of Port Edward','year':yr,'sourceUrl':receipt['url'],'indexUrl':'https://www.portedward.ca/municipal-hall/reports','sha256':receipt['sha256'],'sourceKind':'official-native-pdf','allRowsVisuallyReviewed':True,'remunerationDefinition':'Remuneration is the published Remuneration & Taxable Benefits column. Expenses are separate; the expense-inclusive Total is not remuneration.','periodEvidence':[{'page':5,'text':'For the Year Ended December 31, '+yr}],'notes':['Only the separately verified elected-official schedule is imported. The original employee table has separate Other Remuneration cells with blanks/dashes and an expense-inclusive field labelled Total Remuneration; it remains held for component/scope clarification.','Offices come from the printed Mayor and Councillors group labels and remain as published.'],'sections':[]}
  ws=words_mupdf(d[4]);cols={'name':[135,270],'pay':[270,365],'expenses':[365,455],'expenseInclusiveTotal':[455,540]}
  sec=section(ws,'elected-officials',cols,230,344,370.7,count=5);sec['page']=5;sec['y']=[230,345];sec['maxRowDistance']=10;sec['positionValues']=['Mayor']+['Councillors']*4
  report['sections']=[sec];print_control(report,sec,d);a=extract(ws,sec);b=extract(words_poppler(CACHE/(key+'.pdf'),5),sec);print('reader differences',[(i,a,b)for i,(a,b)in enumerate(zip(a,b))if a!=b]);base.append(report)
 cfg['reports']=base;(OUT/'extended-layouts.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':add()
