# Salary search and browser navigation

The salary search is visible beside Filters on phones before choosing an employer and remains available on person, employer, role and title pages. Starting another search from a detail page preserves focus in the same field. The mobile Filters sheet shares its query, period and sector state with the page. Desktop search remains above the salary content.

Opening a salary page or choosing a browse/employer tab pushes a browser history entry. Query typing, filters and layout changes replace the current entry. Browser Back/Forward restores the URL's page and filters. Salary Back links use that same history, including after reload. A shared person link retains its originating employer and selected employer year; without local history, its Back arrow opens that employer. Older links without an origin return to an employer only when all the name's records identify one employer (including the supplied O'Riley link, which returns to BC Hydro). Ambiguous names and other shared details return to the searchable salary root. Normal browser Back remains free to return to the recipient's preceding website.

The site's view switcher and links between views also push history entries. The App restores the active view and its URL selection on browser Back/Forward.

Every salary detail heading (person, employer, employer position and cross-employer title) places a 44px arrow-only Back button to the left of its title, with an accessible Back label. Employer names with a government body link directly to that body in the selected year. On mobile, the employer's disclosure-summary line is hidden while expandable source notes remain available; desktop keeps the full summary.

Run against the full Vite site (after its asset build), or omit `--full-app` and use the salary preview:

```sh
python3 research/reviews/salary-navigation/verify_navigation.py --url http://localhost:4183/ --full-app
python3 research/reviews/salary-mobile-filters/verify_mobile_filters.py --out /tmp/pofbc-mobile-filter-checks
node --test src/site/browserHistory.test.js src/salaries/*.test.js
npm run build
```

The navigation check exercises 320px, 390px and 1280px viewports using real published data. It checks results → employer → role → person, browser Back/Forward, reload plus in-page Back, fresh shared person/employer/role/title links, new-search focus, retained period/sector filters, browse tabs, cross-view history and horizontal overflow. Screenshots and JSON results are written to `/tmp/pofbc-salary-navigation` by default. Chromium mobile emulation does not substitute for hardware Safari testing.
