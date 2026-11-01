#!/usr/bin/env python3
"""Exercise the real salary preview: python3 verify_mobile_filters.py [--url URL].

Requires Python Playwright and Chromium. Start npm run preview:salaries separately.
Screenshots and interaction results are written beside this script.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

OUT = Path(__file__).resolve().parent
SEARCH = 'Search a name, an employer or a position'


def params(page):
    return parse_qs(urlparse(page.url).query)


def no_duplicate_ids(page):
    duplicates = page.evaluate('''() => {
      const ids = [...document.querySelectorAll('[id]')].map(node => node.id)
      return ids.filter((id, at) => ids.indexOf(id) !== at)
    }''')
    assert not duplicates, duplicates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:4182/')
    args = parser.parse_args()
    reports = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        for width, height in [(320, 760), (375, 812), (390, 844), (1280, 900)]:
            page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(args.url, wait_until='networkidle')
            expect(page.get_by_role('heading', name='Public-sector salaries')).to_be_visible()
            controls = page.locator('.salaries__browse-bar .segmented').evaluate_all('(nodes) => nodes.map(node => node.getBoundingClientRect().toJSON())')
            assert len(controls) == 2
            if width < 640:
                assert abs(controls[0]['y'] - controls[1]['y']) < 1, controls
            assert controls[1]['right'] <= width, controls
            for button in page.locator('.salaries__browse-bar button').all():
                expect(button).to_be_in_viewport()
                assert button.evaluate('(node) => node.scrollWidth <= node.clientWidth'), 'browse label clipped'
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            no_duplicate_ids(page)
            page.screenshot(path=str(OUT / f'{width}-browse.png'))

            if width >= 640:
                expect(page.get_by_role('searchbox', name=SEARCH)).to_be_visible()
                expect(page.get_by_role('button', name='Every period', exact=True)).to_be_visible()
                expect(page.get_by_role('group', name='Sector', exact=True)).to_be_visible()
                expect(page.get_by_role('button', name='Filters', exact=True)).not_to_be_visible()
                page.get_by_role('button', name='Every period', exact=True).click()
                expect(page.get_by_role('dialog', name='Reporting periods')).to_be_visible()
                page.keyboard.press('Escape')
                expect(page.get_by_role('dialog')).to_have_count(0)
                reports.append({'width': width, 'browseControls': controls, 'desktopControls': 'visible and period chooser usable', 'errors': errors})
                assert not errors, errors
                page.close()
                continue

            expect(page.get_by_role('searchbox', name=SEARCH)).to_have_count(0)
            expect(page.get_by_role('group', name='Sector', exact=True)).to_have_count(0)
            trigger = page.get_by_role('button', name=re.compile('^Filters'))
            trigger.click()
            sheet = page.get_by_role('dialog', name='Search and filters')
            expect(sheet).to_be_visible()
            assert sheet.evaluate('(node) => node.matches(":modal")')
            assert page.evaluate('document.documentElement.style.overflow') == 'hidden'
            assert page.evaluate('document.body.style.overflow') == 'hidden'
            expect(page.get_by_role('dialog')).to_have_count(1)
            assert sheet.locator('.salaries-range__panel').evaluate('(node) => getComputedStyle(node).position') == 'static'
            no_duplicate_ids(page)
            page.screenshot(path=str(OUT / f'{width}-sheet.png'))

            # The title receives initial focus without opening the phone keyboard.
            assert page.evaluate('document.activeElement.textContent') == 'Search and filters'
            page.keyboard.press('Tab')
            expect(sheet.get_by_role('button', name='Close filters')).to_be_focused()
            page.keyboard.press('Shift+Tab')
            expect(sheet.get_by_role('button', name='Done', exact=True)).to_be_focused()
            page.keyboard.press('Tab')
            expect(sheet.get_by_role('button', name='Close filters')).to_be_focused()
            page.locator('.salaries__browse-bar button').first.evaluate('(node) => node.focus()')
            assert sheet.evaluate('(node) => node.contains(document.activeElement)'), 'background received focus'

            # The body can scroll to the sector chips while Done remains reachable.
            sheet.get_by_role('button', name=re.compile('^Municipalities ')).scroll_into_view_if_needed()
            expect(sheet.get_by_role('button', name='Done', exact=True)).to_be_in_viewport()
            assert sheet.locator('.salaries-filter-sheet__body').evaluate('(node) => node.scrollTop > 0')
            page.screenshot(path=str(OUT / f'{width}-sectors.png'))
            sheet.get_by_role('searchbox', name=SEARCH).fill('Nanaimo')
            sheet.get_by_role('button', name=re.compile(r'^2024\/25:')).click()
            sheet.get_by_role('button', name=re.compile(r'^2025\/26:')).click()
            sheet.get_by_role('button', name=re.compile('^Municipalities ')).click()
            expect(trigger).to_have_attribute('aria-label', 'Filters, 3 active')
            expect(sheet.get_by_role('dialog')).to_have_count(0)
            expect(sheet.get_by_role('button', name='Done', exact=True)).to_be_in_viewport()
            sheet.get_by_role('button', name='Done', exact=True).click()
            expect(sheet).not_to_be_visible()
            expect(trigger).to_be_focused()
            assert page.evaluate('document.documentElement.style.overflow') == ''
            assert page.evaluate('document.body.style.overflow') == ''
            assert params(page)['q'] == ['Nanaimo']
            assert params(page)['salary-year'] == ['2024/25..2025/26']
            assert params(page)['salary-sector'] == ['Municipalities']
            saved = page.url

            # Shared links restore all three filter values, and Escape closes one sheet.
            page.reload(wait_until='networkidle')
            trigger = page.get_by_role('button', name=re.compile('^Filters'))
            trigger.click()
            sheet = page.get_by_role('dialog', name='Search and filters')
            expect(sheet.get_by_role('searchbox', name=SEARCH)).to_have_value('Nanaimo')
            expect(sheet.get_by_role('button', name=re.compile(r'^2024\/25:'))).to_have_attribute('aria-pressed', 'true')
            expect(sheet.get_by_role('button', name=re.compile(r'^2025\/26:'))).to_have_attribute('aria-pressed', 'true')
            expect(sheet.get_by_role('button', name=re.compile('^Municipalities '))).to_have_attribute('aria-pressed', 'true')
            page.keyboard.press('Escape')
            expect(sheet).not_to_be_visible()
            expect(trigger).to_be_focused()
            assert page.url == saved

            # Backdrop, close button and clear remain independent of URL filter state.
            trigger.click()
            page.mouse.click(8, 8)
            expect(sheet).not_to_be_visible()
            expect(trigger).to_be_focused()
            assert page.url == saved
            trigger.click()
            sheet.get_by_role('button', name='Close filters').click()
            expect(sheet).not_to_be_visible()
            expect(trigger).to_be_focused()
            trigger.click()
            sheet.get_by_role('button', name='Clear filters', exact=True).click()
            expect(sheet.get_by_role('searchbox', name=SEARCH)).to_have_value('')
            expect(sheet.get_by_role('button', name='Every period', exact=True)).to_have_attribute('aria-pressed', 'true')
            expect(sheet.get_by_role('button', name='All sectors', exact=True)).to_have_attribute('aria-pressed', 'true')
            # Clearing a half-selected range must discard its pending first endpoint.
            sheet.get_by_role('button', name=re.compile(r'^2020\/21:')).click()
            sheet.get_by_role('button', name='Clear filters', exact=True).click()
            sheet.get_by_role('button', name=re.compile(r'^2025\/26:')).click()
            expect(sheet.get_by_role('button', name=re.compile(r'^2020\/21:'))).to_have_attribute('aria-pressed', 'false')
            assert params(page)['salary-year'] == ['2025/26']
            sheet.get_by_role('button', name='Clear filters', exact=True).click()
            sheet.get_by_role('button', name='Done', exact=True).click()
            assert not any(key in params(page) for key in ['q', 'salary-year', 'salary-sector'])

            # Browse/layout are still separate stateful controls in their single mobile row.
            page.get_by_role('group', name='Browse', exact=True).get_by_role('button', name='Positions', exact=True).click()
            page.get_by_role('group', name='Layout', exact=True).get_by_role('button', name='Table', exact=True).click()
            expect(page.get_by_role('group', name='Layout', exact=True).get_by_role('button', name='Table', exact=True)).to_have_attribute('aria-pressed', 'true')
            assert params(page)['browse'] == ['positions']
            assert params(page)['layout'] == ['table']
            trigger.click()
            page.set_viewport_size({'width': 1280, 'height': 900})
            expect(sheet).not_to_be_visible()
            assert page.evaluate('document.documentElement.style.overflow') == ''
            expect(page.get_by_role('searchbox', name=SEARCH)).to_be_visible()
            assert params(page)['browse'] == ['positions']
            assert params(page)['layout'] == ['table']
            assert not errors, errors
            reports.append({'width': width, 'browseControls': controls, 'checks': ['nowrap browse/layout', 'desktop inputs hidden', 'native modal/background inert', 'initial focus', 'Tab/Shift+Tab trap', 'scroll lock and restore', 'inline period controls', 'scrollable sector chips and fixed Done', 'live query/range/sector state', 'URL reload', 'Done/Escape/backdrop/close', 'focus return', 'clear filters including pending range endpoint', 'browse/layout URL state', 'desktop resize cleanup', 'no duplicate IDs'], 'errors': errors})
            page.close()
        browser.close()
    (OUT / 'results.json').write_text(json.dumps(reports, indent=2) + '\n')
    print(json.dumps({'viewports': len(reports), 'result': 'passed', 'artifacts': str(OUT)}, indent=2))


if __name__ == '__main__':
    main()
