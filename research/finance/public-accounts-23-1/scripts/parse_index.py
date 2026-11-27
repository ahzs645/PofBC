import re,html,sys,json
# usage: parse_index.py file source_label -> JSON lines
def parse(path):
    t=open(path,encoding='utf8',errors='replace').read()
    t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S); t=re.sub(r'<svg.*?</svg>','',t,flags=re.S)
    toks=re.split(r'(<h[1-6][^>]*>.*?</h[1-6]>|<a\s[^>]*href="[^"]*"[^>]*>.*?</a>)',t,flags=re.S)
    heading=None; fy=None; out=[]
    for tok in toks:
        if re.match(r'<h[1-6]',tok):
            h=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',tok))).strip()
            m=re.search(r'Fiscal Year Ended March 31,\s*(\d{4})',h)
            if m: fy=int(m.group(1))
            heading=h; continue
        m=re.match(r'<a\s[^>]*href="([^"]*)"[^>]*>(.*?)</a>',tok,flags=re.S)
        if m and heading:
            href=html.unescape(m.group(1)); name=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',m.group(2)))).strip()
            name=re.sub(r'\s*\((PDF|pdf)[^)]*\)\s*$','',name).strip()
            if 'sup-e' in href or 'audited-financial-statements' in href or 'financial-reporting' in href or 'financial-management' in href or 'resource-management' in href:
                href=re.sub(r'^https?://web\.archive\.org/web/\d+(id_)?/','',href)
                if href.startswith('/'): href='https://www2.gov.bc.ca'+href
                out.append(dict(fy_end=fy,section=heading,name=name,url=href))
    return out
for p in sys.argv[1:]:
    for r in parse(p):
        r['index']=p.split('/')[-1]; print(json.dumps(r))
