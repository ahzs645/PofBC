#!/usr/bin/env python3
"""Retrieve newly located official histories; preserve acquisition and period receipts."""
import concurrent.futures
import datetime
import json
import re
import urllib.request
from pathlib import Path
import fitz
from continue_education import AUDIT,dump,sha

CACHE=Path('/tmp/continuation-education')
NEW=[
('university-of-the-fraser-valley','https://www.ufv.ca/media/assets/finance/SOFI--Year-Ended-March-2018.pdf','https://www.ufv.ca/finance/reporting/statement-of-financial-information-sofi/'),
('douglas-college','https://www.douglascollege.ca/sites/default/files/docs/finance/Statement%20of%20Financial%20Information%20%28SOFI%29%20March%2031%202020%20FINAL%20signed.pdf','https://www.douglascollege.ca/about-douglas/campus-information/finance-and-procurement/finance/publications-and-reports'),
('douglas-college','https://www.douglascollege.ca/sites/default/files/docs/finance/Financial%20Information%20Report%20-%20March%2031%2C%202021.pdf','https://www.douglascollege.ca/about-douglas/campus-information/finance-and-procurement/finance/publications-and-reports'),
('royal-roads-university','https://www.royalroads.ca/sites/default/files/2025-10/SOFI%20Report%202025_SIGNED_RRU.pdf','https://www.royalroads.ca/about/plans-reports'),
('university-of-bc','https://vpfo-finance-2024.sites.olt.ubc.ca/files/2024/11/FY24-UBC-Statement-of-Financial-Information.pdf','https://finance.ubc.ca/ubcs-finances/reporting/'),
('thompson-rivers-university','https://www.tru.ca/__shared/assets/Financial_Information_Act_202358384.pdf','https://www.tru.ca/finance/financial-statements.html'),
('emily-carr-university','https://ecuad.ca/wp-content/uploads/2026/06/2025-SOFI-Board-Report_signed.pdf','https://ecuad.ca/reports/'),
]

def retrieve(item):
    slug,url,index=item;entry=dict(employerSlug=slug,url=url,indexUrl=index,retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as response:body=response.read();entry.update(status=response.status,resolvedUrl=response.url,contentType=response.headers.get('Content-Type'))
        path=CACHE/(sha(url.encode())[:16]+'.pdf');path.write_bytes(body);entry.update(cacheFile=str(path),sha256=sha(body),bytes=len(body))
        if not body.startswith(b'%PDF'):entry['pdfStatus']='not-pdf';return entry
        doc=fitz.open(path);texts=[re.sub(r'\s+',' ',p.get_text()) for p in doc];periods=[]
        for i,t in enumerate(texts):
            for y in re.findall(r'(?i)(?:year\s+ended|year\s+ending|fiscal year end[ :]*|to)\s+March\s+31,?\s+(20\d{2})',t):periods.append(dict(physicalPage=i+1,endYear=int(y),text=t[:700]))
        candidate=periods[0]['endYear'] if periods else None
        entry.update(pdfStatus='native-text-candidate' if candidate else 'period-review-required',physicalPages=len(doc),periodHeadingEvidence=periods,candidateReportingPeriod=f'{candidate-1}/{str(candidate)[2:]}' if candidate else None,nativeTextCharacters=sum(len(t) for t in texts))
    except Exception as ex:entry.update(error=str(ex),pdfStatus='retrieval-failed')
    return entry

def main():
    CACHE.mkdir(exist_ok=True)
    indexed=json.loads((AUDIT/'current-index-receipts.json').read_text())
    oldurls={d['url'] for d in json.loads((AUDIT.parents[1]/'sector-search-2026-10-31/education/document-verification.json').read_text())['documents']}
    items=NEW+[(i['employerSlug'],link['url'],i['url']) for i in indexed if i['employerSlug']=='north-island-college' for link in i.get('links',[]) if '2019-20' in link['text'] and link['url'] not in oldurls]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:receipts=list(pool.map(retrieve,items))
    dump(AUDIT/'new-document-receipts.json',receipts)
    print(json.dumps([{k:d.get(k) for k in ['employerSlug','candidateReportingPeriod','pdfStatus','cacheFile','error']} for d in receipts],indent=2))

if __name__=='__main__':main()
