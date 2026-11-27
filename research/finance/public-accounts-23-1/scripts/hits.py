import re,json,sys
for p in sys.argv[1:]:
    t=open(p).read();m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',t,re.S)
    if not m: continue
    d=json.loads(m.group(1))
    def walk(o):
        if isinstance(o,dict):
            f=o.get('fields')
            if isinstance(f,list) and any(isinstance(x,dict) and x.get('name')=='number_of_results' for x in f):
                h={x['name']:x.get('value') for x in f}; h['_page']=p.split('/')[-1]; print(json.dumps(h))
            for v in o.values(): walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(d)
