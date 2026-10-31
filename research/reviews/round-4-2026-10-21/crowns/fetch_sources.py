import json,pathlib,urllib.request,hashlib,subprocess,concurrent.futures,sys,datetime
ROOT=pathlib.Path(__file__).parent
RAW=ROOT/'raw'
RAW.mkdir(exist_ok=True)
def fetch(row):
    key,url,title=row
    rec={'key':key,'url':url,'title':title,'retrieved_at':'2026-10-21'}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (historical research)'})
        with urllib.request.urlopen(req,timeout=45) as r:
            b=r.read(); rec.update(final_url=r.url,status_code=r.status,content_type=r.headers.get('Content-Type'))
        ext='.pdf' if b[:4]==b'%PDF' else '.json' if b.lstrip()[:1] in (b'{',b'[') else '.html' if b'<html' in b[:2000].lower() or b'<!doctype' in b[:100].lower() else '.txt'
        p=RAW/(key+ext);p.write_bytes(b)
        rec.update(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),status='retrieved')
        if ext=='.pdf':
            tp=p.with_suffix('.txt');subprocess.run(['pdftotext','-layout',str(p),str(tp)],check=True,capture_output=True);rec['text_path']=str(tp.resolve())
        elif ext=='.json':
            obj=json.loads(b)
            text=json.dumps(obj,ensure_ascii=False,indent=2)
            tp=p.with_suffix('.txt');tp.write_text(text);rec['text_path']=str(tp.resolve())
    except Exception as e:rec.update(status='failed',error=str(e))
    return rec
if __name__=='__main__':
    rows=json.load(sys.stdin)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(fetch,rows))
    p=ROOT/'download_ledger.json'
    old=json.loads(p.read_text()) if p.exists() else []
    old=[x for x in old if x['key'] not in {r['key'] for r in results}]+results
    p.write_text(json.dumps(old,indent=2))
    for x in results:print(x['key'],x['status'],x.get('bytes'),x.get('error',''))
