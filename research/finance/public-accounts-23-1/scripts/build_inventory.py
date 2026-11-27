import json,re,csv,sys,collections,os
sys.path.insert(0,os.path.dirname(__file__))
from names import MANUAL,ORG_KEY,RENAME_NOTES
P=sys.argv[1]; OUT=sys.argv[2]
hits=[json.loads(l) for l in open(P+'/search/hits.jsonl')]
idx=[json.loads(l) for l in open(P+'/parsed.jsonl')]
def fy_label(end): return f"{end-1}-{str(end)[2:]}"
def slug_of(u):
    m=re.search(r'/sup-e/(.+?)-fs-(\d{4}-\d{2})\.pdf',u); return m.groups() if m else (None,None)
# best index capture per FY: the latest capture for that FY
cap_for={}
for r in idx:
    fy=fy_label(r['fy_end']); cap_for[fy]=max(cap_for.get(fy,''),r['index'])
idx=[r for r in idx if r['index']==cap_for[fy_label(r['fy_end'])]]
def cap_label(c):
    if c=='financial-statements.html': return 'live index page (fetched 2026-11-27)'
    ts=re.search(r'fs_(\d+)',c).group(1); return f'Wayback index capture {ts}'
def cap_url(c):
    base='https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/financial-statements'
    if c=='financial-statements.html': return base
    return f'https://web.archive.org/web/{re.search(r"fs_(\d+)",c).group(1)}/{base}'
named=collections.defaultdict(collections.Counter)
for r in idx:
    s,_=slug_of(r['url'])
    if s: named[s][r['name']]+=1
def basis_of(section):
    if section is None: return ''
    if 'Self-Supported' in section or 'Government Enterprises' in section: return 'self-supported Crown (GBE, modified equity)'
    return 'taxpayer-supported (consolidated)'
rows={}
SECTOR_FROM_TYPE={'Health':'Health sector','Education':'Education sector','Natural Resources & Economic Dev.':'Natural resources and economic development sector','Transportation':'Transportation sector','Protection of Persons & Property':'Protection of persons and property','Social Services':'Social services sector','Other Sectors':'Other sector','Government Enterprises':'Self-Supported Crown Corporations & Agencies (Government Business Enterprises)'}
for x in hits:
    s,fy=slug_of(x['url']); t=x.get('Organization Type')
    sec=SECTOR_FROM_TYPE.get(t,'')
    rows[(fy,s)]=dict(fiscal_year=fy,slug=s,section=sec,archive_type=t or '',url=x['url'],via={'archive-search'},index_name='',index_section='',index_cap='')
for r in idx:
    fy=fy_label(r['fy_end']); s,fy2=slug_of(r['url'])
    sec=r['section']
    sec_norm=sec if 'Self-Supported' not in sec else SECTOR_FROM_TYPE['Government Enterprises']
    if s:
        k=(fy2,s)
        row=rows.setdefault(k,dict(fiscal_year=fy2,slug=s,section=sec_norm,archive_type='',url=r['url'],via=set(),index_name='',index_section='',index_cap=''))
        row['via'].add('index-page'); row['index_name']=r['name']; row['index_section']=sec_norm; row['index_cap']=r['index']; row['section']=sec_norm
    else:
        nslug='linked:'+re.sub(r'[^a-z0-9]+','-',r['name'].lower()).strip('-')
        rows[(fy,nslug)]=dict(fiscal_year=fy,slug=nslug,section=sec_norm,archive_type='',url=r['url'],via={'index-page'},index_name=r['name'],index_section=sec_norm,index_cap=r['index'])
out=[]
for (fy,s),r in sorted(rows.items()):
    if r['index_name']: name,ns=r['index_name'],'index page (as published)'
    elif s in named: name,ns=named[s].most_common(1)[0][0],'index page of another year (same file slug)'
    elif s in MANUAL: name,ns=MANUAL[s][0],{'T':'statement title page','S':'expanded from file slug (scan has no text layer)'}[MANUAL[s][1]]
    else: name,ns=s,'file slug'
    hosted='Public Accounts sup-e PDF' if '/sup-e/' in r['url'] else ('school district statements page' if 'school-district' in r['url'] else 'post-secondary statements page (ministry)')
    key=ORG_KEY.get(s,s)
    if s.startswith('linked:'):
        key=ORG_KEY.get(s[7:],s[7:])
    out.append(dict(fiscal_year=fy,fy_end=f"{int(fy[:4])+1}-03-31",organization=name,org_key=key,file_slug=s if not s.startswith('linked:') else '',
        sector=r['section'],reporting_basis=basis_of(r['section']),hosted=hosted,document_url=r['url'],
        found_via='+'.join(sorted(r['via'])),index_capture=cap_url(r['index_cap']) if r['index_cap'] else '',name_source=ns,
        url_status='',note=RENAME_NOTES.get(s,'')))
# url status: archive results are live documents; mark index-only pdfs checked separately
broken={('legal-services-society','2022-23')}
for o in out:
    if (o['file_slug'],o['fiscal_year']) in broken: o['url_status']='404 (index link broken; archive has legal-aid-bc 2022-23)'
    elif o['hosted']=='Public Accounts sup-e PDF': o['url_status']='200 (listed by live archive search)' if 'archive-search' in o['found_via'] else '200 (HEAD 2026-11-27)'
    else: o['url_status']='page link'
with open(OUT,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
c=collections.Counter(o['fiscal_year'] for o in out)
c2=collections.Counter(o['fiscal_year'] for o in out if o['hosted']=='Public Accounts sup-e PDF' and not o['url_status'].startswith('404'))
for k in sorted(c): print(k,c[k],c2[k])
print(len(out),'rows; orgs',len(set(o['org_key'] for o in out)))
