#!/usr/bin/env python3
"""Retrieve public school archives and probe Ministry historical PDF endpoints.

This is source discovery only; no retrieved PDF becomes a salary cohort here.
"""
import argparse
import concurrent.futures
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.error import HTTPError
from html.parser import HTMLParser

import fitz

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.href=None;self.label=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.href=dict(attrs).get('href');self.label=[]
    def handle_data(self,data):
        if self.href is not None:self.label.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.href is not None:
            self.links.append((' '.join(self.label),self.href));self.href=None

def get(url):
    try:
        with urlopen(url,timeout=35) as response:return response.status,response.geturl(),response.read()
    except HTTPError as e:return e.code,url,e.read()

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/continuation-2026-11-01/schools'
CACHE=Path('/tmp/continuation-schools')
INDEX='https://www2.gov.bc.ca/gov/content/education-training/k-12/administration/financial-management/school-district-financial-reporting/statement-of-financial-information'
BASE='https://www2.gov.bc.ca/assets/gov/education/administration/resource-management/school-district-financial-reporting/financial-information'
NEW_INDEXES={
8:['https://sd8.bc.ca/finance'],
6:['https://www.sd6.bc.ca/departments/finance'],
10:['https://sd10.bc.ca/board-of-education/financial-information-budgets/','https://sd10.bc.ca/board-of-education/sd-10-board-meeting-minutes/'],
19:['https://www.sd19.bc.ca/our-district/policies-reports/financial-reports/'],
20:['https://www.sd20.bc.ca/apps/pages/index.jsp?pREC_ID=1370177&type=d&uREC_ID=1097679'],
22:['https://www.sd22.bc.ca/financial-information'],
23:['https://www.sd23.bc.ca/financial-information'],
27:['https://www.sd27.bc.ca/reports-and-publications-1738864389343'],
28:['https://www.sd28.bc.ca/finance'],
46:['https://sd46.bc.ca/district-information/board-of-education-and-governance/budget/'],
47:['https://www.sd47.bc.ca/district-plans-annual-reports'],
48:['https://www.sd48seatosky.org/apps/pages/financialinformation'],
51:['https://www.sd51.bc.ca/our-district/about-us/financial-information/'],
53:['https://www.sd53.bc.ca/financial-information'],
54:['https://bvec.sd54.bc.ca/district-financials/'],
57:['https://sd57.scholantisschools.com/apps/pages/index.jsp?pREC_ID=1388703&type=d&uREC_ID=1144483'],
58:['https://extranet.nssd.ca/finance'],
59:['https://www.sd59.bc.ca/district/financial-information'],
60:['https://policy.prn.bc.ca/public-documents/financial-statements/'],
63:['https://saanichschools.ca/sofi'],
67:['https://www.sd67.bc.ca/apps/pages/index.jsp?pREC_ID=1374587&type=d&uREC_ID=1102413'],
69:['https://www.qsdlearns.ca/about/financial-information'],
70:['https://www.sd70.bc.ca/financial-reports-1'],
71:['https://www.comoxvalleyschools.ca/reports/'],
72:['https://www.sd72.bc.ca/financial-information'],
73:['https://sd73-www-pri.schoolbundle.ca/finance'],
74:['https://www.sd74.bc.ca/apps/pages/index.jsp?pREC_ID=1397145&type=d&uREC_ID=1168428'],
81:['https://sd81.bc.ca/our-district/reports/'],
84:['https://sd84.bc.ca/about-sd84/reports/'],
85:['https://www.sd85.bc.ca/wordpress/finance/statement-of-financial-information/'],
87:['https://www.sd87.bc.ca/finance'],
91:['https://www.sd91.bc.ca/finance'],
93:['https://www.csf.bc.ca/rapports-financiers/'],
}

def fetch(job):
    number,year,url=job
    path=CACHE/f'ministry-sd{number:02}-{year}.pdf'
    row={'districtNumber':number,'indexedEndingYear':year,'sourceUrl':url,'sourceIndexUrl':INDEX,'cacheFile':str(path),'retrievedAt':datetime.now(timezone.utc).isoformat()}
    try:
        if path.exists():
            raw=path.read_bytes();row['httpStatus']=200;row['fromCache']=True
        else:
            status,final_url,raw=get(url);row['httpStatus']=status
        if row['httpStatus']==200 and raw.startswith(b'%PDF'):
            path.write_bytes(raw)
            row.update({'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'status':'retrieved-pending-original-and-cohort-review'})
            doc=fitz.open(path);row['pdfPages']=len(doc)
            row['nativeSchedulePages']=[i+1 for i,p in enumerate(doc) if re.search(r'(?:SCHEDULE.{0,25}REMUNERATION|DETAILED EMPLOYEES|LIST OF ELECTED)',p.get_text(),re.I)]
            row['headingEvidence']=[{'pdfPage':i+1,'text':m.group(0)} for i,p in enumerate(doc) for m in re.finditer(r'(?:Fiscal )?Year Ended June 30,?\s*20\d\d',p.get_text(),re.I)][:6]
        else:row['status']='not-retrieved-pdf'
    except Exception as e:row.update({'status':'retrieval-error','error':str(e)})
    return row

def index_fetch(job):
    number,url=job
    row={'districtNumber':number,'url':url,'retrievedAt':datetime.now(timezone.utc).isoformat()}
    try:
        status,final_url,raw=get(url)
        row.update({'httpStatus':status,'retrievedUrl':final_url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
        page=Links();page.feed(raw.decode(errors='replace'))
        row['relevantLinks']=[{'label':label.strip(),'url':urljoin(final_url,href)} for label,href in page.links if re.search(r'SOFI|statement.{0,10}financial.{0,10}information',label+' '+href,re.I)]
        row['status']='reviewed-public-index' if status==200 else 'public-index-retrieval-error'
    except Exception as e:row.update({'status':'public-index-retrieval-error','error':str(e)})
    return row

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--years',default='2024,2023,2022,2021,2020,2019');parser.add_argument('--indexes',action='store_true');parser.add_argument('--only-indexes',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    old=json.loads((ROOT/'research/salaries/sector-search-2026-10-31/schools/findings.json').read_text())
    jobs=[(e['districtNumber'],year,f"{BASE}/sd{e['districtNumber']:02}-sofi-{year}.pdf") for e in old['employers'] for year in map(int,args.years.split(','))]
    if not args.only_indexes:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            rows=list(pool.map(fetch,jobs))
        (OUT/'ministry-history-receipts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
        print('Historical endpoints:',len(rows),'PDFs:',sum(r['status'].startswith('retrieved-') for r in rows),flush=True)
    if args.indexes or args.only_indexes:
        jobs=[]
        for e in old['employers']:
            urls=set(NEW_INDEXES.get(e['districtNumber'],[])+e['archiveRange']['indexUrls'])
            jobs += [(e['districtNumber'],url) for url in sorted(urls)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:rows=list(pool.map(index_fetch,jobs))
        (OUT/'district-index-receipts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
        print('Public archive indexes:',len(rows),'links:',sum(len(r.get('relevantLinks',[])) for r in rows),flush=True)

if __name__=='__main__':main()
