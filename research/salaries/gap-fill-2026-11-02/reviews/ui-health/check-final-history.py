#!/usr/bin/env python3
"""Final historical-source and compiled-label browser review; public data only."""
import os,json,gzip,urllib.request,pathlib,hashlib,collections,datetime
from urllib.parse import urlencode
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/workspace/gap-fill-playwright'
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/workspace/PofBC');A=ROOT/'research/salaries/gap-fill-2026-11-02/reviews/ui-health/final-nine';BASE='http://127.0.0.1:4173/'
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(p):return urllib.request.urlopen(BASE+p,timeout=30).read()
def load(p):
 b=fetch(p);return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def shot(page,n):
 p=A/(n+'.png');page.screenshot(path=str(p));return ref(p)
def go(page,params):page.goto(BASE+'?'+urlencode({'view':'salaries',**params}),wait_until='networkidle')
def fold(t):return ' '.join(t.split())
idx=load('salaries/employers/index.json');assert idx['recordCounts']=={'official':1156657,'compiled':228364};assert len(idx['employers'])==270 and len(idx['years'])==51
out={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'readOnly':True,'scope':'Final nine-collection rebuilt preview','expectedRecordCounts':idx['recordCounts'],'totalRecords':sum(idx['recordCounts'].values()),'finalResponsiveReceipt':ref(A/'receipt.json'),'finalAdditionalReceipt':ref(A/'additional-checks.json'),'sourceCollections':[],'contexts':[],'screenshots':[],'consoleErrors':[],'pageErrors':[],'lalondeChecks':[]}
cache={}
for dirname in ['gap-fill-phsa-history','gap-fill-health-other-history']:
 mp=ROOT/'research/salaries'/dirname/'sources.json';sources=json.loads(mp.read_bytes())['sources'];co={'manifest':ref(mp),'sources':[]}
 for source in sources:
  sid=source['id'];public=idx['sources'][sid];assert public['sha256']==source['sha256'] and public['dataSha256']==source['dataSha256'];assert public['publicWarning']==source['publicWarning']
  slug=source['employerSlug']
  if slug not in cache:cache[slug]=load('salaries/employers/'+slug+'.json.gzip')
  current=[r for r in cache[slug] if r[5]==sid]
  candidate=json.loads(gzip.decompress((mp.parent/source['file']).read_bytes()))
  target=[[r[1],r[2],r[3],r[4],idx['years'].index(source['year']),sid,r[5]] for r in candidate]
  assert collections.Counter(map(tuple,current))==collections.Counter(map(tuple,target)),sid
  assert len(current)==source['rowCount'];co['sources'].append({'sourceId':sid,'year':source['year'],'rows':len(current),'sourceSha256':public['sha256'],'dataSha256':public['dataSha256'],'publicWarningRetained':True,'allPublishedRowsExactlyMatchFrozenPayload':True})
 out['sourceCollections'].append(co)
assert sum(s['rows'] for c in out['sourceCollections'] for s in c['sources'])==34267
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':1280,'height':1000})
 page.on('pageerror',lambda e:out['pageErrors'].append(str(e)));page.on('console',lambda m:out['consoleErrors'].append(m.text) if m.type=='error' else None)
 targets=[('provincial-health-services-authority','2006/07','gap-phsa-history-phsa-2006-07'),('northern-health','2003/04','gap-health-other-history-northern-health-2003-04'),('island-health','2009/10','gap-health-other-history-island-health-2009-10')]
 for slug,year,sid in targets:
  source=idx['sources'][sid];go(page,{'employer':slug,'employer-year':year,'show':'people','layout':'table'})
  categories=page.get_by_label('Disclosure category',exact=False)
  if categories.count():categories.select_option('employee-remuneration')
  page.wait_for_timeout(100)
  warning=page.locator('.salaries__hint').filter(has_text=source['publicWarning']);assert warning.count()==1 and warning.is_visible()
  links=page.locator('a').evaluate_all('(es)=>es.map(e=>({text:e.textContent,href:e.href,title:e.title}))');assert any(a['href']==source['url'] for a in links)
  title=page.locator('.salaries__year-title').inner_text();assert year in title
  c={'slug':slug,'year':year,'sourceId':sid,'yearTitle':title,'publicWarning':warning.inner_text(),'warningVisible':True,'matchingSourceLinks':[a for a in links if a['href']==source['url']],'publishedRows':sum(r[5]==sid for r in cache[slug])}
  out['screenshots'].append(shot(page,'1280-history-'+slug+'-'+year.replace('/','-')))
  if slug=='island-health':
   page.get_by_role('searchbox',name='Filter Name',exact=True).fill('Wilson. Tom');page.locator('.salaries-datatable').scroll_into_view_if_needed();page.wait_for_timeout(100)
   rows=page.locator('tbody tr[data-index]').all_inner_texts();assert len(rows)==1 and 'Wilson. Tom' in rows[0] and '$77,451' in rows[0] and '$0' in rows[0]
   c['literalWilsonRow']=rows[0];c['wilsonSourceLinks']=page.locator('tbody tr[data-index] a').evaluate_all('(es)=>es.map(e=>({text:e.textContent,href:e.href,title:e.title}))');out['screenshots'].append(shot(page,'1280-island-2009-literal-wilson-zero-expense'))
  if slug=='provincial-health-services-authority':
   page.get_by_role('searchbox',name='Filter Name',exact=True).fill('Shirin Abadi');name=page.get_by_role('button',name='Shirin Abadi',exact=True);assert name.count()==1;name.click();page.wait_for_timeout(150)
   personWarning=page.locator('.salaries__hint').filter(has_text=source['publicWarning']);assert personWarning.count()==1 and personWarning.is_visible();c['personWarningVisible']=True;c['personUrl']=page.url;c['personWarningText']=personWarning.inner_text();personWarning.scroll_into_view_if_needed();out['screenshots'].append(shot(page,'1280-phsa-2006-source-warning-on-person-detail'))
  out['contexts'].append(c)
 for width in [320,375,883,1280]:
  page.set_viewport_size({'width':width,'height':1000});go(page,{'person':'lalonde|vincent a','person-at':'city-of-surrey','q':'Lalonde, Vincent A.','browse':'people','salary-sector':'Municipalities'})
  body=page.locator('.salaries').inner_text();assert 'Compiled edition labels have unverified reporting years and may overlap employer reports.' in body;assert 'All observations are retained; labels on the chart and list do not establish separate payment years.' in body
  latest=page.locator('.salaries__tiles > div').filter(has=page.locator('dt',has_text='Latest label')).inner_text();assert '2023/24 · compiled edition' in latest
  entries=page.locator('.salaries-years__year').all_inner_texts();compiled=[s for s in entries if s.startswith('2023/24')];official=[s for s in entries if s.startswith('2023\n')]
  assert len(compiled)==1 and '$750,302' in compiled[0] and 'Compiled edition · reporting year unverified' in compiled[0]
  assert len(official)==1 and '$750,302.39' in official[0] and 'Source · p. 86' in official[0] and 'Compiled edition' not in official[0]
  overflow=page.evaluate('({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})');assert overflow['scroll']<=overflow['client']
  out['lalondeChecks'].append({'width':width,'compiledEditionWarningVisible':True,'latestTile':latest,'official2023Row':official[0],'compiled2023EditionRow':compiled[0],'originalPaymentRowCount':len(entries),'noDocumentOverflow':True,'chartAccessibleName':page.locator('figure.salaries-chart').get_attribute('aria-label')})
  out['screenshots'].append(shot(page,str(width)+'-lalonde-qualified-edition-header'))
  page.locator('.salaries-years__year').filter(has_text='2023/24 · compiled edition').scroll_into_view_if_needed();out['screenshots'].append(shot(page,str(width)+'-lalonde-qualified-edition-source-rows'))
 b.close()
assert not out['pageErrors'] and not out['consoleErrors'];(A/'history-and-label-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'receipt':ref(A/'history-and-label-verification.json'),'sourcesChecked':18,'exactPublishedRows':34267,'historyContexts':len(out['contexts']),'qualifiedPersonWidths':len(out['lalondeChecks']),'screenshots':len(out['screenshots']),'consoleErrors':out['consoleErrors'],'pageErrors':out['pageErrors']},indent=2))
