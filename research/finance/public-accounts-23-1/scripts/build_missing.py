import json,csv,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from decisions import PRESENT,MISSING
m=json.load(open(sys.argv[1])); outdir=sys.argv[2]
cross=[];miss=[]
for k,v in m.items():
    names=' / '.join(v['names'])
    atlas=sorted({c[3] for c in v['cands'] if c[2].startswith('atlas:')})
    related=sorted({c[3] for c in v['cands'] if c[2].startswith('related:')})
    ident=sorted({c[3] for c in v['cands'] if c[2].startswith('identity:')})
    status='matched' if v['cands'] else 'missing'
    note=''
    if k=='school-districts': atlas=[];related=['school-district-*'];ident=['school-district-*'];status='matched';note=PRESENT[k][2]
    elif k in PRESENT:
        src,id_,note=PRESENT[k]; status='matched (other name)'; atlas=[id_]
    if k in MISSING and status=='missing':
        kind,rec,reason,mention=MISSING[k]
        if mention: status='mentioned only'
        miss.append(dict(org_key=k,organization=names,first_year=v['first'],last_year=v['last'],years_listed=v['n'],sector=v['sector'],reporting_basis=v['basis'],kind=kind,site_status=status,site_mentions=mention,recommendation=rec,reason=reason))
    elif status=='missing':
        print('UNDECIDED',k)
    cross.append(dict(org_key=k,organization=names,first_year=v['first'],last_year=v['last'],years_listed=v['n'],sector=v['sector'],status=status,
        atlas_ids=';'.join(atlas),related_body_ids=';'.join(related),identity_subject_ids=';'.join(ident),
        in_atlas='yes' if atlas else 'no',note=note))
for name,rows in [('missing.csv',miss),('crosswalk.csv',cross)]:
    with open(os.path.join(outdir,name),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import collections
print('orgs',len(cross),'missing',len(miss),collections.Counter(r['recommendation'] for r in miss))
print(collections.Counter(r['status'] for r in cross))
print('matched but not in atlas (register/related only):',[r['org_key'] for r in cross if r['status'].startswith('matched') and r['in_atlas']=='no'])
