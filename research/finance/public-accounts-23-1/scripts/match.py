import csv,json,re,collections,difflib,sys
inv=list(csv.DictReader(open(sys.argv[1])))
site=json.load(open(sys.argv[2]))
STOP={'the','of','and','inc','ltd','corp','corporation','society','british','columbia','bc','b','c','limited','co','company','authority','association','assoc','commission','trust','fund','council','agency','board'}
def norm(s):
    s=s.lower().replace('’',"'").replace("'",'').replace('&',' and ')
    s=re.sub(r'\bb\.c\.','bc',s); s=re.sub(r'[^a-z0-9 ]+',' ',s)
    s=re.sub(r'\bbritish columbia\b','bc',s)
    return ' '.join(s.split())
def core(s): return ' '.join(w for w in norm(s).split() if w not in STOP)
orgs=collections.OrderedDict()
for r in inv:
    o=orgs.setdefault(r['org_key'],dict(names=collections.Counter(),years=[],sectors=collections.Counter(),basis=collections.Counter(),hosted=set()))
    o['names'][r['organization']]+=1; o['years'].append(r['fiscal_year']); o['sectors'][r['sector']]+=1; o['basis'][r['reporting_basis']]+=1; o['hosted'].add(r['hosted'])
sitenames=[]
for e in site:
    for n in e['names']:
        if len(n)>2: sitenames.append((norm(n),core(n),e))
res={}
for k,o in orgs.items():
    cands=[]
    for nm in o['names']:
        nn,cc=norm(nm),core(nm)
        for sn,sc,e in sitenames:
            if nn==sn: cands.append((1.0,'exact',e,nm))
            elif cc and cc==sc: cands.append((0.95,'core',e,nm))
            else:
                r=difflib.SequenceMatcher(None,nn,sn).ratio()
                if r>0.86: cands.append((r,'fuzzy',e,nm))
    best={}
    for sc,how,e,nm in sorted(cands,key=lambda x:-x[0]):
        kk=(e['src'],e['id'])
        if kk not in best: best[kk]=(round(sc,3),how,e['src'],e['id'],(e['names'] or [''])[0],nm)
    res[k]=dict(names=list(o['names']),first=min(o['years']),last=max(o['years']),n=len(set(o['years'])),sector=o['sectors'].most_common(1)[0][0],basis=o['basis'].most_common(1)[0][0],hosted=sorted(o['hosted']),cands=list(best.values())[:8])
json.dump(res,open(sys.argv[3],'w'),indent=1)
for k,v in res.items():
    print(k,'|',v['first'],v['last'],'|',v['names'][:2])
    for c in v['cands'][:5]: print('     ',c)
