# Parks' lineage (22 October 2026)

BC Parks was drawn only from 1957, under the Department of Recreation and Conservation as if it
had stayed there, and called the Provincial Parks Branch to this day. The atlas already held BC
Archives' account of the unit's names and ministries (`research/atlas/events-divisions.json`,
read 25 September 2026), as events only. `batch.json` gives them to the sub-agency record as dated
names and parents, with the archival locator for each, and merges with the house tool:

```sh
npm run research:merge -- research/reviews/parks-lineage-2026-10-22/batch.json
npm run build:government
```

Only what the two records state is supplied. Where they name no ministry (1945-1949, 1975-1978,
after 1986) none is given, and the diagram draws Parks under no ministry for those years. The
authority records were not re-fetched: search.bcarchives.gov.bc.ca returned 503 that day, so each
row keeps the day it was read.

How the rows are read (`periodsOf` and the sub-agency placement in `src/government/snapshot.js`):

- a period whose end its source does not give runs until the next dated row, not to today; a later
  sighting under another name shows only that it had ended by then, and is marked so;
- a stated ministry is the one of that name when the period begins, and holds the body only while
  that ministry stands, never what it became or a ministry with a near name;
- two styles of one name ("BC" and "British Columbia", capitals, stops) are not a change of name.

What is still open is `research/WANTED.md` F4a.
