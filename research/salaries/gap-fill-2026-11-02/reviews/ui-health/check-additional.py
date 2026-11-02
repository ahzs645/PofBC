#!/usr/bin/env python3
"""Additive read-only screenshots and modal state checks; preserves first receipt."""
import os,json,gzip,urllib.request,hashlib,pathlib,datetime
from urllib.parse import urlencode
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/workspace/gap-fill-playwright'
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/workspace/PofBC');A=ROOT/os.environ.get('SALARY_UI_REVIEW_OUT','research/salaries/gap-fill-2026-11-02/reviews/ui-health');A.mkdir(parents=True,exist_ok=True);BASE='http://127.0.0.1:4173/'
def load(p):
 b=urllib.request.urlopen(BASE+p).read();return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def shot(page,n):
 p=A/(n+'.png');page.screenshot(path=str(p));return ref(p)
def go(page,params):page.goto(BASE+'?'+urlencode({'view':'salaries',**params}),wait_until='networkidle')
first=json.load(open(A/'receipt.json'));out={'readOnly':True,'firstReceipt':ref(A/'receipt.json'),'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'screenshots':[],'modalChecks':{},'nullRowLinks':[]}
idx=load('salaries/people/index.json');la=load('salaries/people/la.json.gzip');rows=[]
for r in la:
 if r[0].lower().startswith('lalonde,') and idx['employers'][r[4]][3]=='city-of-surrey':rows.append({'disclosedRow':r,'periodLabel':idx['years'][r[5]],'source':idx['sources'].get(r[6])})
out['surreyLalondeSourceEvidence']=rows
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':375,'height':900})
 go(page,{'browse':'employers'});page.get_by_role('button',name='Filters',exact=True).click();d=page.get_by_role('dialog',name='Search and filters');d.get_by_role('group',name='Sector').scroll_into_view_if_needed();out['screenshots'].append(shot(page,'375-filter-sheet-sector-controls'))
 d.get_by_role('group',name='Sector').get_by_role('button',name='Health authorities',exact=False).click();d.get_by_role('button',name='Done',exact=True).click();out['modalChecks']['sectorStatePersists']='salary-sector=Health+authorities' in page.url and 'Health authorities' in page.locator('.salaries__filter-summary').inner_text()
 page.get_by_role('button',name='Filters, 1 active',exact=True).click();page.mouse.click(5,10);out['modalChecks']['backdropClosesAndReturnsFocus']=not d.is_visible() and page.evaluate("document.activeElement===document.querySelector('.salaries__filter-trigger')")
 page.get_by_role('button',name='Filters, 1 active',exact=True).click();page.set_viewport_size({'width':883,'height':900});page.wait_for_timeout(100);out['modalChecks']['resizeToDesktopCloses']=not d.is_visible();out['modalChecks']['resizeFocusReturnsToDesktopSearch']=page.evaluate("document.activeElement===document.querySelector('.salaries__desktop-filters input[type=search]')");out['screenshots'].append(shot(page,'883-resized-from-mobile-sheet'))
 for c in first['nullNameChecks']:
  page.set_viewport_size({'width':1280,'height':900});go(page,{'employer':c['slug'],'employer-year':c['year'],'show':'people','layout':'table'});page.get_by_role('searchbox',name='Filter Name',exact=True).fill('Name unavailable');page.locator('.salaries-datatable').scroll_into_view_if_needed();page.wait_for_timeout(60);out['screenshots'].append(shot(page,'1280-known-payment-rows-'+c['slug']+'-'+c['year'].replace('/','-')))
  for r in page.locator('tbody tr[data-index]').all():
   out['nullRowLinks'].append({'slug':c['slug'],'year':c['year'],'rowText':r.inner_text(),'nameIsNoninteractive':r.locator('th button').count()==0,'links':r.locator('a').evaluate_all('(es)=>es.map(e=>({text:e.textContent,href:e.href,title:e.title}))')})
 # Separate paired-year source cues are kept visible in one screenshot.
 go(page,{'person':'lalonde|vincent a','person-at':'city-of-surrey','q':'Lalonde, Vincent A.','browse':'people','salary-sector':'Municipalities'});page.locator('.salaries-years').scroll_into_view_if_needed();out['screenshots'].append(shot(page,'1280-lalonde-official-and-compiled-year-rows'))
 b.close()
(A/'additional-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'receipt':ref(A/'additional-checks.json'),'modalChecks':out['modalChecks'],'nullRowCount':len(out['nullRowLinks']),'screenshots':len(out['screenshots']),'lalondeSourceRecords':len(rows)},indent=2))
