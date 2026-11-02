#!/usr/bin/env python3
"""Literal two-reader contract-detail extraction and exact bounded overlap census.

Context only: no salary observation, identity link or title is adopted by this
script. Empty and dashed source components remain literal evidence.
"""
import json,pathlib,subprocess,re,gzip,collections,fitz
from decimal import Decimal
from gap_health_other_history import ROOT,AREA,dump,sha
from gap_health_employees_native import amount,nameclean
FIELDS=['vp','ed','name','position','department','contract','regular','overtime','relief','premiumPay','onCall','lumpSumPayout','sickSeverance','total']
MONEYFIELDS=FIELDS[6:]
DEP=re.compile(r'\b\d{3}\.\d{2}\.\d{7}\b')
HEAD=['Regular','Overtime','Relief','Premium','On Call','Lump Sum','Sick','Total']
def words_display(page):
 out=[]
 for w in page.get_text('words'):
  q=fitz.Rect(w[:4])*page.rotation_matrix;out.append([q.x0,q.y0,q.x1,q.y1,*w[4:]])
 return out

def main():
 spec=next(s for s in json.load(open(AREA/'all-ten-originals.json')) if s['scopeRole']=='context-comparison-only');raw=pathlib.Path(spec['retrieval']['cachePath']).read_bytes();assert sha(raw)==spec['sourceSha256'];doc=fitz.open(stream=raw,filetype='pdf');text=subprocess.check_output(['pdftotext','-layout','-enc','UTF-8',spec['retrieval']['cachePath'],'-']).decode();pages=text.split('\f')[:-1];primary=[];secondary=[];flags=[];rawAnchors=[];geometries=[]
 for pn,(page,t) in enumerate(zip(doc,pages),1):
  if pn<3:continue
  lines=t.splitlines();header=next(l for l in lines if 'Employee Name' in l and 'Regular' in l and 'Total' in l);centers=[header.index(v)+len(v)/2 for v in HEAD];left=(header.index('Contract')+len('Contract')/2+centers[0])/2;bounds=[round(left)]+[round((a+b)/2) for a,b in zip(centers,centers[1:])]+[max(len(l) for l in lines)+1]
  ordinal=0
  for li,l in enumerate(lines,1):
   m=DEP.search(l)
   if not m:
    if re.search(r'\d{1,3},\d{3}\s*$',l):rawAnchors.append({'physicalPage':pn,'lineOnPage':li,'raw':l,'classification':'nonnamed group/control candidate; no employee department anchor'})
    continue
   bits=re.split(r'\s{2,}',l[:m.start()].strip());tail=l[m.end():];contract=tail.split()[0];cells=[l[a:b].strip() for a,b in zip(bounds,bounds[1:])];ordinal+=1
   if len(bits)!=4:flags.append({'reader':'primary','physicalPage':pn,'lineOnPage':li,'kind':'ambiguous-name-position-columns','prefixLiteral':l[:m.start()],'split':bits})
   assert len(bits)==4,(pn,l,bits)
   for cell in cells:amount(cell)
   row=dict(zip(FIELDS,bits+[m.group(),contract]+cells));row.update(physicalPage=pn,sourceRowOnPage=ordinal,rawLine=l);primary.append(row)
  # Completely independent positioned field extraction: literal source drawing
  # cell boundaries and visible column labels, with a Total monetary anchor.
  w=words_display(page);edges=[]
  for path in page.get_drawings():
   for it in path['items']:
    if it[0]=='l':
     a=it[1]*page.rotation_matrix;b=it[2]*page.rotation_matrix
     if abs(a.x-b.x)<.2 and abs(a.y-b.y)>5:edges.append(a.x)
    elif it[0]=='re':
     r=it[1]*page.rotation_matrix
     if r.height>5:edges.extend([r.x0,r.x1])
  # Thick cell borders have two edges less than one point apart. Their center
  # defines a boundary; this changes no source text or salary value.
  groups=[]
  for x in sorted(edges):
   if groups and x-groups[-1][-1]<1:groups[-1].append(x)
   else:groups.append([x])
  edges=[sum(g)/len(g) for g in groups];assert len(edges)==15,(pn,edges);totals=[q for q in w if q[4]=='Total' and q[1]<115];headerTotal=min(totals,key=lambda q:q[1]);payleft=max(x for x in edges if x<(headerTotal[0]+headerTotal[2])/2);payright=min(x for x in edges if x>(headerTotal[0]+headerTotal[2])/2);geometries.append({'physicalPage':pn,'literalCellBorders':edges,'totalHeader':headerTotal[:5]});ordinal=0
  anchors=[]
  for q in w:
   if q[1]<=headerTotal[3]+6 or not payleft<(q[0]+q[2])/2<payright:continue
   try:v=amount(q[4])
   except ValueError:continue
   if v is not None:anchors.append(q)
  for q in sorted(anchors,key=lambda q:q[1]):
   line=sorted([a for a in w if abs(a[1]-q[1])<1.2],key=lambda a:a[0]);cells=[]
   for a,b in zip(edges,edges[1:]):cells.append(' '.join(z[4] for z in line if a<(z[0]+z[2])/2<b))
   if not cells[2]:
    rawAnchors.append({'physicalPage':pn,'rawWords':line,'classification':'nonnamed total anchor with visibly empty EmployeeName cell'});continue
   ordinal+=1;assert len(cells)==14
   for cell in cells[6:]:amount(cell)
   row=dict(zip(FIELDS,cells));row.update(physicalPage=pn,sourceRowOnPage=ordinal,sourceWords=line);secondary.append(row)
 assert len(primary)==len(secondary)==492
 differences=[]
 for p,q in zip(primary,secondary):
  for f in FIELDS:
   a,b=p[f],q[f]
   # Numeric/blank/dash remain literal in saved readers, compared by decimal
   # only for published numeric formatting. Text word boundaries preserved.
   if f in MONEYFIELDS:
    same=amount(a)==amount(b) and (a not in ['','-'] or a==b)
   elif f in ['vp','ed','name']:same=nameclean(a)==nameclean(b)
   else:same=' '.join(a.split())==' '.join(b.split())
   if not same:differences.append({'physicalPage':p['physicalPage'],'sourceRowOnPage':p['sourceRowOnPage'],'field':f,'primary':a,'secondary':b})
 area=AREA/'fraser-contract-context';area.mkdir(exist_ok=True)
 for name,data in [('poppler-layout.json.gzip',{'sourceSha256':spec['sourceSha256'],'pages':pages}),('primary-literal-rows.json.gzip',{'sourceSha256':spec['sourceSha256'],'rows':primary}),('secondary-literal-rows.json.gzip',{'sourceSha256':spec['sourceSha256'],'rows':secondary,'geometries':geometries}),('outside-named-anchors.json.gzip',rawAnchors)]:
  p=area/name;p.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 mainidx=json.load(open(ROOT/'research/salaries/gap-fill-2026-11-02/health_employees/native-primary-candidate-index.json'));main=next(c for c in mainidx if c['key']=='fraser-health-2010-11');mainrows=json.loads(gzip.decompress((ROOT/main['file']).read_bytes()))['rows'];byname=collections.defaultdict(list)
 for r in mainrows:byname[r['row'][1]].append(r['row'])
 detailkeys=collections.Counter((nameclean(r['name']),amount(r['total'])) for r in primary);comparison=[]
 for r in primary:
  key=(nameclean(r['name']),amount(r['total']));sameName=byname[key[0]];sameBoth=[p for p in sameName if Decimal(str(p[3]))==Decimal(str(key[1]))];comparison.append({'physicalPage':r['physicalPage'],'sourceRowOnPage':r['sourceRowOnPage'],'nameLiteral':r['name'],'totalLiteral':r['total'],'positionLiteral':r['position'],'exactNameMainRows':sameName,'exactNameAndTotalMainRows':sameBoth,'detailExactKeyMultiplicity':detailkeys[key],'classification':'unique exact employer-period/name/payment candidate overlap; no title adoption' if len(sameBoth)==1 and detailkeys[key]==1 else 'unresolved literal name/payment/observation multiplicity; no inferred identity or additional salary row'})
 summary={'sourceSha256':spec['sourceSha256'],'actualPeriodEnd':'2011-03-31','totalNamedDetailRows':492,'expectedNamedDetailCountFromActualContractSummary':{'nursesOver100000':402,'paramedicalOver100000':88,'facilitiesOver100000':2,'total':492,'excludedGroup371NotInContractDetail':True},'twoReaderLiteralFieldDifferences':differences,'flags':flags,'uniqueExactNameAndPaymentOverlaps':sum(v['classification'].startswith('unique exact') for v in comparison),'unresolvedComparisonRows':sum(v['classification'].startswith('unresolved') for v in comparison),'noSalaryRowsAppended':True,'noPositionsAdopted':True,'noInferredIdentities':True,'comparison':comparison,'noOutreach':True};dump(area/'comparison-candidate.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['comparison','twoReaderLiteralFieldDifferences','flags']}));print('differences',len(differences),json.dumps(differences[:10],ensure_ascii=False))
if __name__=='__main__':main()
