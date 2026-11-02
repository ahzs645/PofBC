#!/usr/bin/env python3
"""Read-only Chromium review of the existing local salary preview."""
import os,json,gzip,hashlib,urllib.request,pathlib,datetime,re,collections
from urllib.parse import urlencode
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/workspace/gap-fill-playwright'
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/workspace/PofBC'); AREA=ROOT/os.environ.get('SALARY_UI_REVIEW_OUT','research/salaries/gap-fill-2026-11-02/reviews/ui-health');AREA.mkdir(parents=True,exist_ok=True);BASE='http://127.0.0.1:4173/'
def fetch(path):return urllib.request.urlopen(BASE+path,timeout=20).read()
def load(path):
 b=fetch(path);return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def file_ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def snapshot(page,name):
 p=AREA/(name+'.png');page.screenshot(path=str(p),full_page=False);return file_ref(p)
def goto(page,params):
 page.goto(BASE+'?'+urlencode({'view':'salaries',**params}),wait_until='networkidle');page.locator('.salaries').wait_for();page.wait_for_timeout(100)
def active(page):return page.evaluate('''()=>({tag:document.activeElement?.tagName,text:document.activeElement?.innerText,aria:document.activeElement?.getAttribute('aria-label'),inDialog:!!document.activeElement?.closest('dialog[open]')})''')
def no_overflow(page):return page.evaluate('''()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth})''')
receipt={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseUrl':BASE,'readOnly':True,'implementationEdited':False,'serverRebuilt':False,'browser':'Chromium via Python Playwright','widths':[],'nullNameChecks':[],'consoleErrors':[],'pageErrors':[],'screenshots':[],'scopeLimit':os.environ.get('SALARY_UI_SCOPE','Current seven-collection preview only; final two history collections require a separate recheck after root rebuild.')}
html=fetch('');receipt['htmlSha256']=hashlib.sha256(html).hexdigest();receipt['assets']=[{'path':s,'sha256':hashlib.sha256(fetch(s.lstrip('/'))).hexdigest()} for s in re.findall(r'(?:src|href)="([^"]+\.(?:js|css))"',html.decode())]
idx=load('salaries/employers/index.json');receipt['publicCounts']=idx['recordCounts'];receipt['publicSourceCount']=len(idx['sources']);receipt['publicEmployerCount']=len(idx['employers']);receipt['publicPeriodCount']=len(idx['years'])
null_targets=[]
for e in idx['employers']:
 if e['slug'] not in ['school-district-58','delta-school-district','vancouver-coastal-health']:continue
 for row in load('salaries/employers/'+e['slug']+'.json.gzip'):
  if row[0] is None and (row[5].startswith('gap-school-north-sd58-') or row[5].startswith('gap-fill-school-south-sd37-') or row[5].startswith('gap-health-employees-')):
   null_targets.append({'slug':e['slug'],'year':idx['years'][row[4]],'row':row,'warning':idx['sources'][row[5]].get('publicWarning')})
assert len(null_targets)==10
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 page=b.new_page(viewport={'width':375,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda error:receipt['pageErrors'].append(str(error)))
 page.on('console',lambda msg:receipt['consoleErrors'].append(msg.text) if msg.type=='error' else None)
 receipt['browserVersion']=b.version
 for width in [320,375,883,1280]:
  page.set_viewport_size({'width':width,'height':900});goto(page,{'browse':'employers'})
  record={'width':width,'height':900,'overflow':no_overflow(page)}
  browse=page.get_by_role('group',name='Browse',exact=True);layout=page.get_by_role('group',name='Layout',exact=True)
  record['browseBounds']=browse.bounding_box();record['layoutBounds']=layout.bounding_box();record['browseAndLayoutSameLine']=abs(record['browseBounds']['y']-record['layoutBounds']['y'])<3
  record['buttons']=page.locator('.salaries__browse-bar').first.locator('button').evaluate_all('(es)=>es.map(e=>({text:e.textContent,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,scroll:e.scrollWidth,client:e.clientWidth}))')
  record['mobileFilterVisible']=page.get_by_role('button',name='Filters',exact=True).is_visible()
  sector=page.get_by_role('group',name='Sector',exact=True)
  record['desktopSectorVisible']=sector.is_visible()
  record['browseAboveSector']=not sector.is_visible() or browse.bounding_box()['y']+browse.bounding_box()['height']<=sector.bounding_box()['y']
  record['employerCardYearStrips']=page.locator('.salaries__card .salaries-strip__marks[role="img"]').count()
  receipt['screenshots'].append(snapshot(page,f'{width}-employers'))
  if width<640:
   trigger=page.get_by_role('button',name='Filters',exact=True);trigger.click();dialog=page.get_by_role('dialog',name='Search and filters',exact=True)
   sheet={'visible':dialog.is_visible(),'ariaModal':dialog.get_attribute('aria-modal'),'expanded':trigger.get_attribute('aria-expanded'),'controlsMatches':trigger.get_attribute('aria-controls')==dialog.get_attribute('id'),'initialFocus':active(page),'bounds':dialog.bounding_box(),'sectorPresent':dialog.get_by_role('group',name='Sector',exact=True).count(),'periodGroupPresent':dialog.get_by_role('group',name='Reporting periods',exact=True).count(),'backgroundScrollLocked':page.evaluate("document.body.style.overflow==='hidden' && document.documentElement.style.overflow==='hidden'")}
   dialog.get_by_role('button',name='Done',exact=True).focus();page.keyboard.press('Tab');sheet['tabWrapsToClose']=active(page)['aria']=='Close filters'
   page.keyboard.press('Shift+Tab');sheet['shiftTabWrapsToDone']=active(page)['text']=='Done'
   receipt['screenshots'].append(snapshot(page,f'{width}-filter-sheet-employers'))
   page.keyboard.press('Escape');sheet['escapeClosesAndReturnsFocus']=not dialog.is_visible() and page.evaluate("document.activeElement===document.querySelector('.salaries__filter-trigger')")
   trigger.click();dialog.get_by_role('button',name='Close filters',exact=True).click();sheet['closeButtonCloses']=not dialog.is_visible()
   trigger.click();dialog.get_by_role('searchbox',name='Search a name, an employer or a position',exact=True).fill('Smith');dialog.get_by_role('button',name='Done',exact=True).click();sheet['doneClosesAndRetainsSearch']='q=Smith' in page.url and not dialog.is_visible()
   page.get_by_role('button',name=re.compile('^Filters')).click();dialog.get_by_role('button',name='Clear filters',exact=True).click();dialog.get_by_role('button',name='Done',exact=True).click();sheet['clearRestoresSearch']='q=' not in page.url
   record['filterSheet']=sheet
  goto(page,{'browse':'positions','salary-sector':'Municipalities'})
  record['positionsSectorsVisible']=page.get_by_role('group',name='Sector',exact=True).is_visible() if page.get_by_role('group',name='Sector',exact=True).count() else False
  note=page.locator('.salaries__order-note');record['positionsNote']={'text':note.inner_text(),'lines':note.evaluate('(e)=>{const r=document.createRange();r.selectNodeContents(e);return [...new Set([...r.getClientRects()].map(x=>Math.round(x.top)))].length}'),'bounds':note.bounding_box()}
  receipt['screenshots'].append(snapshot(page,f'{width}-positions'))
  if width<640:
   page.get_by_role('button',name='Filters',exact=True).click();dialog=page.get_by_role('dialog',name='Search and filters',exact=True);record['positionsSheetSectorCount']=dialog.get_by_role('group',name='Sector',exact=True).count();receipt['screenshots'].append(snapshot(page,f'{width}-filter-sheet-positions'));dialog.get_by_role('button',name='Done',exact=True).click()
  receipt['widths'].append(record)
 # The user's duplicate municipal example: one name/employer browse card, all source observations retained on its detail page.
 page.set_viewport_size({'width':883,'height':900});goto(page,{'browse':'people','salary-sector':'Municipalities'})
 cards=page.locator('.salaries__grid .salaries__card').filter(has_text='Lalonde')
 receipt['peopleExample']={'lalondeVisibleCardCount':cards.count(),'cardText':cards.all_inner_texts(),'browseCaveat':page.locator('.salaries__records .salaries__hint--small').first.inner_text()}
 receipt['screenshots'].append(snapshot(page,'883-people-municipalities'))
 if cards.count()==1:
  cards.first.click();page.wait_for_timeout(250);receipt['peopleExample']['detailUrl']=page.url;receipt['peopleExample']['detailText']=page.locator('.salaries').inner_text();receipt['peopleExample']['sourceWarnings']=page.locator('.salaries__hint').filter(has_text='Source caveat:').all_inner_texts();receipt['screenshots'].append(snapshot(page,'883-lalonde-source-year-records'))
 # Group the ten damaged/clipped-name observations by actual employer/period, using only visible table column filters.
 grouped=collections.defaultdict(list)
 for target in null_targets:grouped[(target['slug'],target['year'])].append(target)
 for (slug,year),targets in grouped.items():
  page.set_viewport_size({'width':1280,'height':1000});goto(page,{'employer':slug,'employer-year':year,'show':'people','layout':'table'})
  page.get_by_role('searchbox',name='Filter Name',exact=True).fill('Name unavailable');page.wait_for_timeout(100)
  table=page.locator('.salaries-table table');rendered=table.locator('tbody tr[data-index]');rows=rendered.all_inner_texts();warnings=page.locator('.salaries__hint').filter(has_text='Source caveat:').all_inner_texts()
  check={'slug':slug,'year':year,'expectedRows':len(targets),'visibleRows':len(rows),'rowTexts':rows,'publicWarnings':warnings,'allFallbacksNoninteractive':rendered.locator('th button').count()==0,'sourceLinks':rendered.locator('a').evaluate_all('(es)=>es.map(e=>({text:e.textContent,href:e.href,title:e.title}))'),'expected':targets}
  assert len(rows)==len(targets),(slug,year,rows)
  for t in targets:
   pay=f"${t['row'][2]:,.2f}" if t['row'][2]%1 else f"${t['row'][2]:,.0f}"
   assert any(pay in r for r in rows),(slug,year,pay,rows)
  check['allKnownPaymentsVisible']=True;check['allNamesUnavailable']=all('Name unavailable' in r for r in rows);check['warningsVisible']=bool(warnings)
  receipt['screenshots'].append(snapshot(page,'1280-name-unavailable-'+slug+'-'+year.replace('/','-')))
  if slug=='school-district-58':
   page.set_viewport_size({'width':375,'height':900});page.locator('.salaries-table').scroll_into_view_if_needed();check['mobileOverflow']=no_overflow(page);receipt['screenshots'].append(snapshot(page,'375-name-unavailable-sd58-table'))
  receipt['nullNameChecks'].append(check)
 b.close()
receipt['allTenKnownPaymentsPreservedInUi']=sum(r['visibleRows'] for r in receipt['nullNameChecks'])==10
(AREA/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'receipt':file_ref(AREA/'receipt.json'),'screenshots':len(receipt['screenshots']),'widths':[{'width':r['width'],'sameLine':r['browseAndLayoutSameLine'],'overflow':r['overflow'],'positionNoteLines':r['positionsNote']['lines'],'sectorsHiddenForPositions':not r['positionsSectorsVisible']} for r in receipt['widths']],'nullRows':sum(r['visibleRows'] for r in receipt['nullNameChecks']),'pageErrors':receipt['pageErrors'],'consoleErrors':receipt['consoleErrors']},indent=2))
