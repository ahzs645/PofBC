#!/usr/bin/env python3
"""Check salary history and shared links against the real app or salary preview.

Start npm run preview:salaries -- --port 4182, or pass --url for the full site.
Requires Python Playwright and system Chromium. Artifacts go to --out.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

SEARCH = 'Search a name, an employer or a position'


def params(page):
    return parse_qs(urlparse(page.url).query)


def check_heading(page, selector):
    heading = page.locator(selector)
    row = page.locator('.salaries__page-heading').filter(has=heading)
    back = row.get_by_role('button', name='Back', exact=True)
    expect(back).to_be_visible()
    assert back.inner_text().strip() == '', 'Back must show only its arrow'
    button_box, heading_box = back.bounding_box(), heading.bounding_box()
    assert button_box['x'] + button_box['width'] <= heading_box['x']
    assert button_box['width'] >= 44 and button_box['height'] >= 44


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://localhost:4182/')
    parser.add_argument('--out', type=Path, default=Path('/tmp/pofbc-salary-navigation'))
    parser.add_argument('--full-app', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    root = args.url + '?view=salaries'
    reports = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in [320, 390, 1280]:
            page = browser.new_page(viewport={'width': width, 'height': 844},
                                    is_mobile=width < 640, has_touch=width < 640)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(root, wait_until='networkidle')
            search = page.get_by_role('searchbox', name=SEARCH)
            expect(search).to_be_visible()
            expect(search).to_be_in_viewport()
            initial_length = page.evaluate('history.length')
            search.press_sequentially('Nanaimo', delay=30)
            expect(search).to_be_focused()
            assert page.evaluate('history.length') == initial_length, 'typing created history entries'

            # Save filters in the parent entry before opening any institution.
            if width < 640:
                page.get_by_role('button', name=re.compile('^Filters')).click()
                filters = page.get_by_role('dialog', name='Search and filters')
            else:
                filters = page
                page.get_by_role('button', name='Every period', exact=True).click()
            filters.get_by_role('button', name=re.compile(r'^2024\/25:')).click()
            if width < 640:
                filters.get_by_role('button', name=re.compile('^School districts ')).click()
                filters.get_by_role('button', name='Done', exact=True).click()
            else:
                page.keyboard.press('Escape')
                page.get_by_role('button', name=re.compile('^School districts ')).click()
            results_url = page.url
            page.locator('button.salaries__card').filter(has_text='Nanaimo-Ladysmith').click()
            expect(page.locator('#salaries-employer')).to_be_visible()
            employer_url = page.url
            show = page.get_by_role('group', name='Show records', exact=True)
            show.get_by_role('button', name='People', exact=True).click()
            employer_people_url = page.url
            expect(show.get_by_role('button', name='People', exact=True)).to_have_attribute('aria-pressed', 'true')
            page.go_back(wait_until='networkidle')
            assert page.url == employer_url
            expect(show.get_by_role('button', name='Positions', exact=True)).to_have_attribute('aria-pressed', 'true')
            page.go_forward(wait_until='networkidle')
            assert page.url == employer_people_url
            expect(show.get_by_role('button', name='People', exact=True)).to_have_attribute('aria-pressed', 'true')
            page.go_back(wait_until='networkidle')
            page.locator('button.salaries__card').filter(has_text='TEACHER').first.click()
            expect(page.locator('#salaries-role')).to_be_visible()
            role_url = page.url
            page.locator('button.salaries-record-card__open').first.click()
            expect(page.locator('#salaries-person')).to_be_visible()
            check_heading(page, '#salaries-person')
            person_url = page.url
            person_heading = page.locator('#salaries-person').inner_text()
            assert page.evaluate('history.length') == initial_length + 3

            # Browser Back and Forward restore the actual page, not just its address.
            for url, heading in [(role_url, '#salaries-role'), (employer_url, '#salaries-employer'),
                                 (results_url, '#salaries-intro')]:
                page.go_back(wait_until='networkidle')
                assert page.url == url, (page.url, url)
                expect(page.locator(heading)).to_be_visible()
                if heading != '#salaries-intro':
                    check_heading(page, heading)
                expect(search).to_be_visible()
            expect(search).to_have_value('Nanaimo')
            assert params(page)['salary-year'] == ['2024/25']
            assert params(page)['salary-sector'] == ['School districts']
            for url, heading in [(employer_url, '#salaries-employer'), (role_url, '#salaries-role'),
                                 (person_url, '#salaries-person')]:
                page.go_forward(wait_until='networkidle')
                assert page.url == url, (page.url, url)
                expect(page.locator(heading)).to_be_visible()

            # Reload retains the in-site Back path; its button and browser Forward agree.
            page.reload(wait_until='networkidle')
            expect(page.locator('#salaries-person')).to_have_text(person_heading)
            page.locator('.salaries__back').click()
            expect(page.locator('#salaries-role')).to_be_visible()
            assert page.url == role_url
            page.go_forward(wait_until='networkidle')
            expect(page.locator('#salaries-person')).to_be_visible()

            # Fresh person links return to their employer; other details return to the root.
            shared = browser.new_page(viewport={'width': width, 'height': 844})
            shared.on('pageerror', lambda error: errors.append(str(error)))
            for url, heading in [(person_url, '#salaries-person'), (employer_url, '#salaries-employer'),
                                 (role_url, '#salaries-role'), (root + '&title=teacher', '#salaries-title')]:
                shared.goto(url, wait_until='networkidle')
                expect(shared.get_by_role('searchbox', name=SEARCH)).to_be_visible()
                expect(shared.locator(heading)).to_be_visible()
                check_heading(shared, heading)
                shared.locator('.salaries__back').click()
                if heading == '#salaries-person':
                    expect(shared.locator('#salaries-employer')).to_be_visible()
                    assert params(shared)['employer'] == params(page)['person-at']
                    assert params(shared)['employer-year'] == params(page)['employer-year']
                    shared.locator('.salaries__back').click()
                expect(shared.locator('#salaries-intro')).to_be_visible()
                expect(shared.get_by_role('searchbox', name=SEARCH)).to_be_visible()
                assert not any(key in params(shared) for key in ['employer', 'person', 'role', 'title'])

            # Starting a new search from a shared detail keeps focus throughout typing.
            shared.goto(person_url, wait_until='networkidle')
            expect(shared.locator('#salaries-person')).to_be_visible()
            field = shared.get_by_role('searchbox', name=SEARCH)
            field.fill('')
            field.press_sequentially('Smith', delay=30)
            expect(field).to_have_value('Smith')
            expect(field).to_be_focused()
            expect(shared.locator('#salaries-intro')).to_be_visible()
            assert not any(key in params(shared) for key in ['employer', 'person', 'role', 'title'])
            shared.go_back(wait_until='networkidle')
            expect(shared.locator('#salaries-person')).to_have_text(person_heading)

            # The supplied old O'Riley link has no person-at. Its records identify BC Hydro alone.
            shared.goto(root + '&q=O%27Riley%2C+CK&person=oriley%7Cck', wait_until='networkidle')
            expect(shared.locator('#salaries-person')).to_be_visible()
            shared.get_by_role('button', name='Back', exact=True).click()
            expect(shared.locator('#salaries-employer')).to_have_text('BC Hydro and Power Authority')
            assert params(shared)['employer'] == ['bc-hydro']
            assert 'person' not in params(shared)
            shared.close()

            # Browse tabs are pages too, and remain navigable after a detail visit.
            page.goto(root, wait_until='networkidle')
            page.get_by_role('group', name='Browse', exact=True).get_by_role('button', name='People', exact=True).click()
            people_url = page.url
            page.get_by_role('group', name='Browse', exact=True).get_by_role('button', name='Positions', exact=True).click()
            page.go_back(wait_until='networkidle')
            assert page.url == people_url
            expect(page.get_by_role('group', name='Browse', exact=True).get_by_role('button', name='People', exact=True)).to_have_attribute('aria-pressed', 'true')

            if args.full_app:
                # Cross-view navigation keeps the salary URL and does not leak its filters.
                page.goto(employer_url, wait_until='networkidle')
                page.locator('.view-switcher__trigger').click()
                page.get_by_role('menuitemradio', name=re.compile('^Generator')).click()
                expect(page.locator('.view-switcher__trigger')).to_have_text('Generator')
                assert not any(key in params(page) for key in ['q', 'employer', 'salary-year', 'salary-sector'])
                page.go_back(wait_until='networkidle')
                expect(page.locator('#salaries-employer')).to_be_visible()
                assert page.url == employer_url
                page.go_forward(wait_until='networkidle')
                expect(page.locator('.view-switcher__trigger')).to_have_text('Generator')

            page.goto(root, wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(args.out / f'{width}-search.png'))
            assert not errors, errors
            reports.append({'width': width, 'history': 'Back/Forward, reload and in-page Back passed',
                            'sharedLinks': 'person, employer, role and title passed',
                            'focusAndFilters': 'passed', 'fullApp': args.full_app, 'errors': errors})
            page.close()
        browser.close()
    (args.out / 'results.json').write_text(json.dumps(reports, indent=2) + '\n')
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
