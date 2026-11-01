# Salary mobile filters review

The mobile salary browse controls now keep **Employers / People / Positions** and **Cards / Table** on one line. Below 640px, a Filters button replaces the main search/period toolbar and sector strip. It opens one bottom sheet containing the same live search, period-range and sector state. Desktop retains the visible toolbar and sector chips.

The sheet uses a native modal dialog to make the background inert, plus explicit Tab/Shift+Tab wrapping, initial heading focus, return focus, Escape/backdrop/Close/Done dismissal and restored page scroll styles. Its title/search help IDs use React IDs. PeriodRange has an inline mode in this sheet, so period chips never create a second dialog or compete for Escape. Clearing filters also discards a pending first range endpoint. Filter values continue through the existing URL state and survive closing/reloading.

The header and Done footer stay visible while the middle scrolls. The sheet follows visualViewport resize/scroll height and vertical offset when available, keeping its footer above a keyboard even when the layout viewport and 90dvh remain unchanged. Listeners and custom sizing styles are removed on close. Opening at the heading avoids raising a phone keyboard before the user chooses Search.

## Changed application files

* `src/salaries/MobileFilters.jsx` — shared search/sector controls and the mobile modal.
* `src/salaries/SalariesView.jsx` — desktop/mobile presentation bound to existing filter state.
* `src/salaries/parts.jsx` — inline period-picker presentation and external clear handling.
* `src/site/site.css` — salary-scoped mobile, dialog and inline-picker rules only.

## Verification

Chromium checks passed at **320×760, 375×812, 390×844 and 1280×900**. At 320px, both groups have the same top coordinate, every button is in the viewport, labels fit their button boxes, and the document has no horizontal overflow. The script also checks modal/background focus, keyboard cycling, page scroll lock/restore, a scrollable sector list with reachable Done, live query/range/sector updates, URL reload, all dismissal methods, focus return, clear/reset behavior, no duplicate IDs and desktop resize cleanup. No page JavaScript errors occurred.

Additional 390px touch/dark emulation passed. A separate visualViewport-only test kept innerHeight at 844px while reducing the visible height to 420px and then 390px with an 80px vertical offset. Search, sector scrolling and Done remained inside the simulated visible area, and closing cleared sizing/scroll styles and restored focus. This is browser viewport simulation; an actual hardware keyboard/Safari session was not run.

The 62 salary Node tests passed, the real salary preview production build passed, and `git diff --check` passed. The browser scripts require Python Playwright and `/usr/bin/chromium`; they are review tools and do not add production dependencies.

```sh
npm run preview:salaries -- --port 4182
# In another terminal:
python3 research/reviews/salary-mobile-filters/verify_mobile_filters.py
python3 research/reviews/salary-mobile-filters/verify_visual_viewport.py
node --test scripts/salary-data.test.mjs src/salaries/*.test.js
npm run preview:salaries -- --build --out /tmp/pofbc-mobile-salary-preview
```

Interaction receipts are in `results.json`, `touch-dark-results.json` and `visual-viewport-results.json`.

## Screenshots

* [320px browse](320-browse.png), [375px browse](375-browse.png), [390px browse](390-browse.png)
* [320px sheet](320-sheet.png), [375px sheet](375-sheet.png), [390px sheet](390-sheet.png)
* [320px sectors and fixed footer](320-sectors.png), [375px sectors](375-sectors.png), [390px sectors](390-sectors.png)
* [Desktop](1280-browse.png)
* [390px touch/dark sheet](390-touch-dark-sheet.png), [touch/dark browse](390-touch-dark-browse.png)
* [390px keyboard viewport simulation](390-keyboard-viewport-simulation.png)

No branch changes, commits, salary registry edits or generated salary-data edits were made by this UI task.
