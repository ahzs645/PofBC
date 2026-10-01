# How this release was imported (1 October 2026)

The release's README, REPORT and INTEGRATION are kept as delivered; its data tables are in `data/`.
`convert.py` turned them into `handback.json` (merged with `npm run research:merge`) and
`research/atlas/events-historical-checkpoints.json`. What it accepted and why is in its docstring:

- **Sightings, 61 bodies:** 198 observations where a budget prints the body's own name (or an earlier
  name a reviewed source bridges), naming a body or programme. 171 new name observations; the rest were
  already held.
- **Unresolved checks:** label variants ("Corrections", "Court Services") and functions, funds or
  headings mapped to a body. Kept in `review.sources_checked` with their outcome, not as sightings.
- **No parents:** the ministry a budget printed a body under is kept on the check, never as a parent.
- **18 events** on bodies the atlas already draws. The 4 planned events and the 4 with no atlas body
  (Real Estate Council, Human Rights Advisory Council, the Medical Review Panel process, the broad
  child-care transfer) stay here.
- **Not imported:** the 228 unmatched labels (historical or out-of-scope candidates for the gone-bodies
  work), the body-year matrix and the review queue. None create a body automatically.
