#!/usr/bin/env python3
"""Verify keyboard-sized visual viewport geometry without an OS keyboard.

Start the salary preview on 4182 first; Python Playwright + system Chromium required.
"""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

OUT=Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 # Change only the viewport API consumed by the component, leaving the layout
 # viewport at 844px. This tests the case that ordinary viewport resizing misses.
 page.add_init_script('''(() => {
   const viewport = new EventTarget()
   Object.assign(viewport, { height: innerHeight, offsetTop: 0 })
   window.salaryReviewViewport = viewport
   Object.defineProperty(window, 'visualViewport', { configurable: true, get: () => viewport })
 })()''')
 page.goto('http://localhost:4182/',wait_until='networkidle')
 trigger=page.get_by_role('button',name=re.compile('^Filters'))
 trigger.click()
 sheet=page.get_by_role('dialog',name='Search and filters')
 expect(sheet).to_be_visible()
 reports=[]
 for height,offset in [(420,0),(390,80)]:
  page.evaluate('''({height,offset}) => {
   Object.assign(window.salaryReviewViewport, {height,offsetTop:offset})
   window.salaryReviewViewport.dispatchEvent(new Event('resize'))
   window.salaryReviewViewport.dispatchEvent(new Event('scroll'))
  }''',{'height':height,'offset':offset})
  assert page.evaluate('innerHeight')==844
  rect=sheet.bounding_box();done=sheet.get_by_role('button',name='Done',exact=True).bounding_box()
  assert rect['y']>=offset-1,(rect,offset)
  assert rect['y']+rect['height']<=offset+height+1,(rect,height,offset)
  assert done['y']>=offset and done['y']+done['height']<=offset+height+1,done
  sheet.get_by_role('searchbox').fill('Nanaimo')
  sheet.get_by_role('button',name='All sectors',exact=True).scroll_into_view_if_needed()
  footer=sheet.get_by_role('button',name='Done',exact=True).bounding_box()
  assert footer['y']+footer['height']<=offset+height+1
  reports.append({'layoutHeight':844,'visualHeight':height,'visualOffsetTop':offset,'sheet':rect,'done':done,'sectorScrollAndSearch':'passed'})
 page.screenshot(path=str(OUT/'390-keyboard-viewport-simulation.png'))
 sheet.get_by_role('button',name='Done',exact=True).click()
 expect(sheet).not_to_be_visible();expect(trigger).to_be_focused()
 assert page.locator('.salaries-filter-sheet').evaluate('(node)=>node.style.getPropertyValue("--salaries-sheet-height")')==''
 assert page.locator('.salaries-filter-sheet').evaluate('(node)=>node.style.getPropertyValue("--salaries-sheet-bottom")')==''
 assert page.evaluate('document.documentElement.style.overflow')==''
 (OUT/'visual-viewport-results.json').write_text(json.dumps({'method':'Simulated visualViewport resize/scroll events in Chromium; no hardware OS keyboard was opened.','results':reports,'closeRestoresFocusStylesAndScroll':True},indent=2)+'\n')
 browser.close()
 print('Visual-viewport-only keyboard shrink/offset checks passed.')
