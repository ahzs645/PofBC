#!/usr/bin/env python3
"""Complete physical-page/native-row census, retaining outside-table money anchors."""
import sys,json,gzip,pathlib,re,hashlib,collections
from gap_health_employees_native import ROOT,AREA,ROW,CONTROL,selected_page,load,amount

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writegzip(p,x):p.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def classify(pn,text,rows):
 f=' '.join(text.split());low=f.lower();head=low[:1300]
 if rows:return 'individual-employee-schedule'
 if pn==1 and 'legislative library' in low:return 'archival-library-cover'
 if not f:return 'no-poppler-visible-text'
 if re.search(r'board (?:member|of directors|remuneration|members)',head):return 'separate-board-disclosure'
 if 'contract totals' in head or 'employee earnings in excess' in head:return 'aggregate-contract-counts'
 if re.search(r'schedule of payments to (?:suppliers|vendors)|payments for (?:suppliers|goods)|payments to suppliers|payments for goods',head):return 'supplier-payments-not-individual-salaries'
 if 'statement of financial information approval' in head:return 'sofi-approval-or-section-cover'
 if 'management report' in head or 'management responsibility' in head:return 'management-report-or-section-cover'
 if 'reconciliation of remuneration' in head:return 'aggregate-payroll-reconciliation'
 if 'statement of severance' in head or 'severance agreements' in head:return 'severance-narrative-or-section-cover'
 if 'table of contents' in head or 'index to audited' in head:return 'document-index'
 if re.search(r'financial statements|financial position|statement of operations|statement of cash flows|statement of (?:changes|remeasurement)|independent auditor|notes to|audit report|auditor.s report',head):return 'aggregate-financial-statements-or-audit'
 if len(f)<240:return 'short-cover-continuation-or-footer'
 if 'remuneration' in head and ('expenses' in head) and not ROW.search(text):return 'employee-definition-or-control-continuation'
 return 'requires-explicit-context-classification'

def main():
 idx=json.load(open(AREA/'native-primary-candidate-index.json')); evs={v['key']:v for v in json.load(open(AREA/'native-reader-evidence-index-v2.json'))}; manifest=[]; allflags=[]; unknown=[]; target=AREA/'native-census';target.mkdir(exist_ok=True)
 for c in idx:
  e=evs[c['key']]; pp=ROOT/e['popplerLayout']['path'];mp=ROOT/e['mupdfWords']['path'];tp=ROOT/e['textProbe']['path']
  for p,h in [(pp,e['popplerLayout']['sha256']),(mp,e['mupdfWords']['sha256']),(tp,e['textProbe']['sha256']),(ROOT/c['file'],c['sha256']),(ROOT/c['secondaryFile'],c['secondarySha256'])]:assert sha(p)==h
  pages=load(pp)['pages']; words=load(mp)['pages'];probes=load(tp)['pages'];pr=load(ROOT/c['file']);sr=load(ROOT/c['secondaryFile']);count=collections.Counter(r['row'][5] for r in pr['rows']);scount=collections.Counter(r['row'][5] for r in sr['rows']);out=[]
  for n,(text,wp,probe) in enumerate(zip(pages,words,probes),1):
   typ=classify(n,text,count[n]);anchors=[]
   for li,line in enumerate(text.splitlines(),1):
    m=ROW.fullmatch(line)
    if not m:continue
    disposition='literal-named-employee-candidate' if count[n] and ',' in m['name'] and not CONTROL.match(m['name'].strip()) else 'outside-or-nonnamed-monetary-anchor-retained'
    if CONTROL.match(m['name'].strip()):disposition='published-control-retained'
    if c['key'].startswith('providence-health-care-') and count[n]:disposition='separate-surname-firstname-employee-candidate'
    anchors.append({'lineOnPage':li,'raw':line,'leftLiteral':m['name'],'payLiteral':m['pay'],'expenseLiteral':m['expense'],'disposition':disposition})
   item={'physicalPage':n,'classification':typ,'independentMupdfPhysicalPage':wp['physicalPage'],'primaryRowCount':count[n],'secondaryRowCount':scount[n],'nativePageSelection':selected_page(c['key'],n,text),'popplerCharacters':len(text),'mupdfVisibleTextCharacters':probe['textLength'],'nativeWords':len(wp['words']),'headingLiteral':' '.join(text.split())[:700],'monetaryAnchors':anchors}
   out.append(item)
   if typ=='requires-explicit-context-classification':unknown.append({'key':c['key'],'page':n,'heading':item['headingLiteral'],'anchors':len(anchors)})
  assert len(out)==len(pages)==len(words)==len(probes)
  flags=[]
  for side,d in [('primary',pr),('secondary',sr)]:
   for ordinal,flag in enumerate(d['flags'],1):
    v={'id':c['key']+'-'+side+'-flag-'+str(ordinal).zfill(3),'sourceKey':c['key'],'sourceSha256':c['sourceSha256'],'reader':side,'flag':flag};flags.append(v);allflags.append(v)
  doc={'sourceKey':c['key'],'sourceSha256':c['sourceSha256'],'rawReaders':e,'primaryCandidateSha256':c['sha256'],'secondaryCandidateSha256':c['secondarySha256'],'pages':out,'readerFlags':flags,'acceptance':False};p=target/(c['key']+'.json.gzip');writegzip(p,doc);manifest.append({'key':c['key'],'sourceSha256':c['sourceSha256'],'path':str(p.relative_to(ROOT)),'sha256':sha(p),'physicalPages':len(out),'primaryRows':sum(count.values()),'secondaryRows':sum(scount.values()),'classifications':dict(collections.Counter(v['classification'] for v in out)),'outsideTableMonetaryAnchors':sum(len(v['monetaryAnchors']) for v in out if not v['primaryRowCount']),'readerFlags':len(flags)})
 (AREA/'native-census-index-v1.json').write_text(json.dumps(manifest,indent=2)+'\n');(AREA/'native-census-reader-flags-v1.json').write_text(json.dumps(allflags,ensure_ascii=False,indent=2)+'\n');(AREA/'native-census-unclassified-pages-v1.json').write_text(json.dumps(unknown,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sources':len(manifest),'physicalPages':sum(v['physicalPages'] for v in manifest),'primaryRows':sum(v['primaryRows'] for v in manifest),'flags':len(allflags),'unclassifiedPages':len(unknown),'classifications':dict(sum((collections.Counter(v['classifications']) for v in manifest),collections.Counter()))}));print(json.dumps(unknown[:30],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
