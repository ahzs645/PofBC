#!/usr/bin/env python3
"""Pin complete manually reviewed small scanned schedules and exact OCR corrections."""
import csv,json,shutil,hashlib
from pathlib import Path
from decimal import Decimal
from continue_municipal import extract,money,dollars
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/salaries/continuation-municipal';CACHE=Path('/tmp/continuation-municipal')
def words(key,page):
 out=[]
 for r in csv.DictReader(open(CACHE/(key+'-p'+str(page)+'.tsv')),delimiter='\t'):
  if r['text'].strip():
   l,t,w,h=[int(r[k])/3 for k in ['left','top','width','height']];out.append([l,t,l+w,t+h,r['text']])
 return out
def cents(v):return None if v is None else int(Decimal(str(v))*100)
def rows(items,extra=None):
 out=[]
 for a in items:
  name,pos,pay,exp,*other=a;r={'name':name,'position':pos,'pay':cents(pay),'expenses':cents(exp)}
  if extra:r[extra]=cents(other[0])
  out.append(r)
 return out
def prepare(key,cat,pg,cols,yy,items,controls,extra=None,distance=5,ignore=None):
 manual=rows(items,extra);sec={'page':pg,'category':cat,'columns':cols,'y':yy,'rowCount':len(manual),'maxRowDistance':distance,'ignoreTokens':ignore or [],'corrections':[],'manualRows':manual,'controlsCents':{k:cents(v)for k,v in controls.items()},'controlBasis':'Printed subtotal for the complete named cohort; missing expenses are not assigned zero.'}
 raw=extract(words(key,pg),sec,raw_fields=True)
 for i,(ocr,correct)in enumerate(zip(raw,manual)):
  for field,v in correct.items():
   if field in ['name','position']:same=ocr.get(field)==v
   else:
    try:same=money(ocr.get(field)or'')==v
    except ValueError:same=False
   if not same:sec['corrections'].append({'row':i,'field':field,'before':ocr.get(field)or'','after':v if field in ['name','position']else ''if v is None else str(dollars(v)),'basis':'Complete rendered original independently transcribed and visually reviewed; OCR misreading only.'})
 parsed=extract(words(key,pg),sec);assert parsed==manual,(parsed,manual)
 res={k:sum(r.get(k)or 0 for r in manual)-v for k,v in sec['controlsCents'].items()};sec['reviewedResidualsCents']=res;print(key,cat,'rows',len(manual),'corrections',sec['corrections'],'residuals',res)
 return sec

def main():
 cfg=json.loads((OUT/'reviewed-layouts.json').read_text());cfg['reports']=[r for r in cfg['reports']if r.get('sourceKind')!='official-scanned-pdf'];rs=json.loads((ROOT/'research/salaries/continuation-2026-11-01/municipal/archive-receipts.json').read_text())+json.loads((ROOT/'research/salaries/continuation-2026-11-01/municipal/priority-receipts.json').read_text())
 defs=[('district-of-metchosin','2025','district-of-metchosin-cde2e7e380edbd','District of Metchosin','https://www.metchosin.ca/municipal-hall/taxes-budgets'),('village-of-fraser-lake','2023','village-of-fraser-lake-96b17d3209368f','Village of Fraser Lake','https://www.fraserlake.ca'),('district-of-wells','2020','district-of-wells-b52eea68b62eb7','District of Wells','https://www.wells.ca/district-wells/reports/statement-financial-information')]
 for slug,yr,key,name,index in defs:
  rec=next(r for r in rs if r.get('cachePath','').endswith(key+'.pdf'));report={'key':slug+'-'+yr,'employerSlug':slug,'employerName':name,'year':yr,'sourceUrl':rec['url'],'indexUrl':index,'sha256':rec['sha256'],'sourceKind':'official-scanned-pdf','allRowsVisuallyReviewed':True,'remunerationDefinition':'Remuneration is the separate source Remuneration column; expenses remain separate.','notes':['The salary schedule is scanned/image content. Tesseract provides one OCR transcription only. Every accepted row/field/control was independently transcribed from and checked against the complete rendered original; no independent OCR-engine agreement is claimed.'],'periodEvidence':[],'sections':[]};shutil.copyfile(rec['cachePath'],CACHE/(report['key']+'.pdf'))
  if slug=='district-of-metchosin':
   cols={'name':[115,200],'position':[200,310],'pay':[310,390],'taxableBenefits':[390,450],'expenses':[450,520]}
   council=[['Little, M.T.','Mayor','31999.44','2493.19',None],['Epp, S','Councillor','18908.76','1661.27',None],['Gray, S','Councillor','18908.76','1473.69',None],['Shukin, J','Councillor','18908.76','1473.69',None],['Donaldson, S','Councillor','18908.76','2607.06',None]]
   employees=[['Payette, B','CAO','155655.30','9801.09','15770.34'],['Whitmore, L','Finance','97756.30','407.31','531.82'],['Dunlop, S','Fire Chief','126984.58',None,'531.84'],['Grivel, G','Pub Works','97193.34','150.00','526.51'],['Hansen, T','Corporate','146853.20','2794.72','531.82'],['Lamb, J','Operations Officer','76182.12','1125.96','531.82'],['Watkins, C','Building Official','102996.88','1144.19','531.82'],['Brooks, T','Pub Works','78858.79','150.00','531.82'],['Bergen, G','Pub Works','77343.23','150.00','531.82'],['Windsor, P','Fire Prevention Officer','77800.32','525.00','356.48'],['Kreek, G','Finance','119592.28','3825.03','531.82']]
   report['sections']=[prepare(key,'elected-officials',39,cols,[179,244],council,{'pay':'107634.48','expenses':'9708.90'},'taxableBenefits'),prepare(key,'employee-remuneration',39,cols,[304,452],employees,{'pay':'1157216.34','taxableBenefits':'20907.91','expenses':'20073.30'},'taxableBenefits',ignore=['*','='])]
   report['periodEvidence']=[{'page':39,'text':'Year ended December 31, 2025'}]
   report['remunerationDefinition']='Remuneration is the source Remuneration column. Its note defines remuneration as including salary, wages and taxable benefits. The separately displayed Taxable Benefits column is retained in evidence and controls, and is not added a second time.'
   report['notes'].append('The source separately prints Taxable Benefits while its note defines Remuneration as including taxable benefits. The normalized measure faithfully retains the chosen Remuneration field without asserting that the separate column is an additional payment. Employee Dunlop S has an unpublished expense cell, retained null; the named expense control compares known cells only. Under-threshold expenses and taxable benefits are printed n/a and are not zero.')
   for sec in report['sections']:sec['publicWarning']='Metchosin 2025 separately displays Taxable Benefits while defining Remuneration as including taxable benefits. This dataset uses the published Remuneration column without adding the separate benefits column. Raw components and controls remain available in source evidence.'
  elif slug=='village-of-fraser-lake':
   employees=[['Bussi, Wade','Wastewater Operator/Public Works',77543,2749],['Campbell, Cameron','Arena Attendant/Public Works',79636,0],['Cruz, Zion','Arena Attendant/Public Works',86240,2845],['Graham, Jeffrey','Water Plant Operator',98878,2674],['Hilman, Vern','Director of Public Works',102163,28],['Holland, Rodney','Chief Administrative Officer',118875,6934],['McMaster, Laura','Director of Finance',94239,1394],['Pacheco, Joe','Fire Chief',87295,1037]]
   council=[['Fennema, Audrey','Councillor',12132,7964],['Jenkinson, Joseph','Councillor',12132,6520],['LePoidevin, Craig','Councillor',12132,4272],['Storey, Sarrah','Mayor',23740,16309],['Webb, Jolene','Councillor',12132,4338]]
   report['sections']=[prepare(key,'employee-remuneration',12,{'name':[43,180],'position':[180,360],'pay':[360,450],'expenses':[450,545]},[144,266],employees,{'pay':744869,'expenses':17661},distance=7),prepare(key,'elected-officials',13,{'name':[40,225],'position':[225,335],'pay':[335,450],'expenses':[450,535]},[146,222],council,{'pay':72268,'expenses':39403},distance=7)]
   report['periodEvidence']=[{'page':12,'text':'For the Year Ended December 31, 2023'},{'page':13,'text':'For the Year Ended December 31, 2023'}]
   report['notes'].append('Employee Campbell Cameron has an explicit printed expense zero; it remains zero. Complete original employee and council named subtotals agree exactly.')
  else:
   council=[['Gabe Fourchalk','Mayor','10191.48','3354.48'],['Mandy Kilsby','Councillor','4146.96','0.00'],['Ksenya Dorwart','Councillor','4146.96','0.00'],['Chris Cooley','Councillor','4146.96','0.00'],['Jordan Rohatynski','Councillor','4146.96','0.00']]
   report['sections']=[prepare(key,'elected-officials',3,{'name':[75,185],'position':[185,345],'pay':[345,455],'expenses':[455,530]},[362,461],council,{'pay':'26779.32','expenses':'3354.48'},ignore=['S$'])]
   report['periodEvidence']=[{'page':3,'text':'Mayor and Council 2020 Remuneration and Expenses'}]
   report['notes'].append('Only the council schedule with its own explicit 2020 heading is imported. On this same page the employee subsection says Staff2018 beneath the overall2020 schedule title. That employee row is held for reporting-period clarification; council dates do not resolve the employee conflict. Four council expenses are explicit printed0.00 and remain zero.')
  cfg['reports'].append(report)
 (OUT/'scanned-layouts.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
