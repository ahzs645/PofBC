from pathlib import Path
import urllib.request,concurrent.futures,xml.etree.ElementTree as E,fitz
B=Path(__file__).resolve().parent/'foi-followup';B.mkdir(exist_ok=True)
reqs=[('haa1993.pdf','https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/206203074'),('year1998.xml','https://www.bclaws.gov.bc.ca/civix/content/hstats/hstats/1488685745/'),('rsbc1996.xml','https://www.bclaws.gov.bc.ca/civix/content/hstats/hstats/1768361481/'),('foippa_pit.html','https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96165_pit')]
def fetch(x):
 fn,u=x
 try:
  b=urllib.request.urlopen(u,timeout=35).read();(B/fn).write_bytes(b)
  if b.startswith(b'%PDF'):
   d=fitz.open(stream=b,filetype='pdf');(B/fn.replace('.pdf','.txt')).write_text('\n\f\n'.join(p.get_text() for p in d))
  return fn,len(b)
 except Exception as e:return fn,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(fetch,reqs):print(r)
for fn in ['year1998.xml','rsbc1996.xml']:
 print(fn)
 for x in E.parse(B/fn).getroot():
  t=x.findtext('CIVIX_DOCUMENT_TITLE','')
  if any(k in t for k in ['-- F','-- S','Table','Supp','Index']): print(t,x.findtext('CIVIX_DOCUMENT_ID'))
d=fitz.open(B/'haa1993.pdf')
for i,p in enumerate(d):
 t=p.get_text()
 if 'Consequential' in t or 'Commencement' in t or 'health care body' in t: print('HAA p',i+1,t[-6000:])
