from pathlib import Path
import urllib.request,xml.etree.ElementTree as E,concurrent.futures,json,subprocess,os,re,fitz
base=Path(__file__).resolve().parent
out=base/'raw'/'orders';out.mkdir(exist_ok=True)
ids=[]
for year in [2001,2002]:
    root=E.parse(base/'raw'/f'mo_index_{year}.xml').getroot()
    for d in root:
        oid=d.findtext('CIVIX_DOCUMENT_ID','')
        m=re.fullmatch(r'm(\d+)_(\d+)',oid)
        if m and ((year==2001 and int(m[1])>=270) or (year==2002 and int(m[1])<=110)):
            ids.append(oid)
def work(oid):
    url='https://www.bclaws.gov.bc.ca/civix/document/id/mo/hmo/'+oid
    path=out/(oid+'.pdf');txt=out/(oid+'.txt')
    try:
        if not path.exists():
            b=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read()
            if not b.startswith(b'%PDF'):return {'id':oid,'url':url,'status':'not_pdf'}
            path.write_bytes(b)
        if not txt.exists():
            doc=fitz.open(path);chunks=[]
            for pg in list(doc)[:2]:
                t=pg.get_text()
                if len(t.strip())<100:
                    pix=pg.get_pixmap(matrix=fitz.Matrix(1.8,1.8))
                    p=subprocess.run(['tesseract','stdin','stdout','--psm','3'],input=pix.tobytes('png'),capture_output=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
                    t=p.stdout.decode(errors='replace')
                chunks.append(t)
            txt.write_text('\n\f\n'.join(chunks))
        return {'id':oid,'url':url,'status':'success','pages_inspected':min(2,len(fitz.open(path))),'text':str(txt.relative_to(base))}
    except Exception as e:return {'id':oid,'url':url,'status':str(e)}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for i,r in enumerate(ex.map(work,ids)):
        results.append(r)
        if i%25==0:print('completed',i+1,'of',len(ids),flush=True)
(base/'restructuring_order_scan.json').write_text(json.dumps(results,indent=2))
print('done',len(results),'success',sum(r['status']=='success' for r in results),flush=True)
