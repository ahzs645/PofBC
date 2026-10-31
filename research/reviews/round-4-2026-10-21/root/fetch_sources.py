import concurrent.futures, hashlib, json, subprocess, sys, time
from pathlib import Path
import urllib.request, urllib.error, re, html

BASE=Path(__file__).resolve().parent
RAW=BASE/'raw'; RAW.mkdir(parents=True,exist_ok=True)

def fetch(s):
    out=dict(s)
    try:
        req=urllib.request.Request(s['url'],headers={'User-Agent':'Mozilla/5.0 (historical public-document research)'})
        r=urllib.request.urlopen(req,timeout=40)
        content=r.read()
        out.update(http_status=r.status,resolved_url=r.url,content_type=r.headers.get('Content-Type',''),retrieved_at='2026-10-21')
        if r.status != 200:
            out['retrieval_status']='http_error'; return out
        ext='.pdf' if content.startswith(b'%PDF') else ('.json' if 'json' in out['content_type'] else '.html')
        p=RAW/(s['id']+ext); p.write_bytes(content)
        out.update(local_file=str(p.relative_to(BASE)),sha256=hashlib.sha256(content).hexdigest(),bytes=len(content),retrieval_status='retrieved')
        if ext=='.pdf':
            q=p.with_suffix('.txt')
            proc=subprocess.run(['pdftotext','-layout',str(p),str(q)],capture_output=True)
            out['text_extracted']=proc.returncode==0
        elif ext=='.html':
            try:
                p.with_suffix('.txt').write_text(html.unescape(re.sub('<[^>]*>','\n',content.decode('utf-8','replace'))))
            except Exception: pass
    except Exception as e:
        out.update(retrieval_status='error',error=str(e))
    return out

if __name__=='__main__':
    batch=json.loads(Path(sys.argv[1]).read_text())
    existing=BASE/'sources.json'
    sources=json.loads(existing.read_text()) if existing.exists() else []
    byid={s['id']:s for s in sources}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for s in pool.map(fetch,batch):
            byid[s['id']]=s
            existing.write_text(json.dumps(list(byid.values()),indent=2,ensure_ascii=False))
            print(json.dumps({k:s.get(k) for k in ['id','http_status','retrieval_status','bytes','local_file','error']}),flush=True)
