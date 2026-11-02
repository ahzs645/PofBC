#!/usr/bin/env python3
"""Census every monetary column anchor, including records with no parsed name."""
import json,gzip,collections,re
from gap_health_other_history import ROOT,AREA,dump,sha
from gap_health_employees_native import amount,nameclean,CONTROL

def main():
 evidence={x['key']:x for x in json.load(open(AREA/'native-reader-evidence-index-v2.json'))};transforms=json.load(open(AREA/'native-page-transforms.json'));out=[]
 for c in json.load(open(AREA/'native-primary-candidate-index.json')):
  e=evidence[c['key']];words=json.loads(gzip.decompress((ROOT/e['mupdfWords']['path']).read_bytes()))['pages'];secondary=json.loads(gzip.decompress((ROOT/c['secondaryFile']).read_bytes()));geoms={g['physicalPage']:g for g in secondary['pageGeometries']};rawrows=collections.defaultdict(list)
  for r in secondary['rows']:rawrows[r['row'][5]].append(r)
  extras=[];allcount=0;classified=collections.Counter()
  for p,tr in zip(words,transforms[c['sourceSha256']]):
   pg=p['physicalPage'];g=geoms.get(pg)
   if not g:continue
   w=p['words']
   if tr['rotation']:
    a,b,cc,d,ee,f=tr['rotationMatrix'];new=[]
    for word in w:
     pts=[(a*x+cc*y+ee,b*x+d*y+f) for x in [word[0],word[2]] for y in [word[1],word[3]]];xs,ys=zip(*pts);new.append([min(xs),min(ys),max(xs),max(ys),*word[4:]])
    w=new
   lo,hi=g['salaryCenterBounds'];seen=[]
   for q in sorted(w,key=lambda q:(q[1],q[0])):
    if q[1]<g['bodyAfter'] or not lo<(q[0]+q[2])/2<hi:continue
    try:value=amount(q[4])
    except ValueError:continue
    if value is None or any(abs(q[1]-y)<1 for y in seen):continue
    seen.append(q[1]);allcount+=1
    same=sorted([z for z in w if abs(z[1]-q[1])<2.1],key=lambda z:z[0]);name=nameclean(' '.join(z[4] for z in same if z[0]<q[0]-2 and z[4]!='$'))
    matches=[r for r in rawrows[pg] if abs(r['y']-q[1])<1]
    if matches:kind='parsed literal employee monetary anchor'
    elif re.fullmatch(r'Page\s+\d+\s+of',name,re.I):kind='published page-number footer anchor'
    elif CONTROL.match(name) or re.match(r'^(?:\$?[\d,]+|(?:over|under|less than|greater than)\b)',name,re.I):kind='published nonnamed control/aggregate anchor'
    else:kind='unparsed monetary anchor requires literal original review'
    classified[kind]+=1
    if not matches:extras.append({'physicalPage':pg,'rawMonetaryToken':q[4],'monetaryValue':value,'leftLiteral':name,'words':same,'classification':kind,'matchedEmployeeRows':len(matches)})
  # Keep the selected census's explicit footer addendum last for byte-stable replay.
  if 'published page-number footer anchor' in classified:
   footer_count=classified.pop('published page-number footer anchor');classified['published page-number footer anchor']=footer_count
  out.append({'key':c['key'],'sourceSha256':c['sourceSha256'],'totalMonetaryColumnAnchors':allcount,'parsedEmployeeObservations':c['secondaryRows'],'classifications':dict(classified),'allUnmatchedAnchorsRetained':extras})
 dump(AREA/'complete-monetary-column-census.json',{'method':'All native monetary anchors in independently source-header-defined remuneration column, including empty/partial/non-comma names; native row parser omissions are explicit, never silently waived.','sources':out,'noOutreach':True})
 for r in out:print(r['key'],r['totalMonetaryColumnAnchors'],r['classifications'],[(v['physicalPage'],v['leftLiteral'],v['rawMonetaryToken']) for v in r['allUnmatchedAnchorsRetained']])
if __name__=='__main__':main()
