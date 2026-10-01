# Worked review of the research queue, 30 September 2026

A second independent review (by ChatGPT): batch-by-batch triage of all 238 records
(`record-triage.json`, `batch-dispositions.json`) and 24 source-backed claims for 15 bodies
(`evidence-ledger.json`).

`handback.json` is that ledger converted to the queue's hand-back shape and merged on 30 September
2026. Each claim keeps the meaning the review gave it: Act sections in force are `legislation_in_force`
events, planned transfers and later accounts are their own events, and current BC Hydro ownership is an
observation on the review date, not a period. Only two claims became starts, the BC Teachers' Council
and the Disciplinary and Professional Conduct Board (Teachers Act ss. 9(1) and 26(1) "is
established"; OIC 620/2011 in force 9 January 2012), checked against BC Laws before merging. The
commissioner is appointed, not established, so its in-force date stays an event.

Not merged: three claims already held (Environmental Appeal Board 1982, Powertech 1989, Columbia Hydro
Constructors 1962); the Environmental Appeal Board home-page wording (C017), which carries no new
date; and the three discovery candidates (BC College of Teachers, Director of Certification, Teachers
Act Special Account), which need checking against the whole atlas before they get ids. The two BC Parks
locators it recovered were already in `research/atlas/events-divisions.json` but were not being
applied; the events build now applies them.
