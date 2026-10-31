# Round 4 integration — code audit

Reviewed commit: `0dbdb18cfebfb27e5529ce5940850e96eb9a995c`. Baseline: `0f1587c5e982135f155ba6660af5192509351511`.

Read-only review; no repository edits, no external writes. Full suite/build and idempotence checks delegated to root.

## Findings

### CODE-01 — Retain the old 1978 ministry ID as an alias (P2)

The spelling correction changes the canonical node ID. episodeById(old ID) is null, while the new ID resolves. readParams accepts the old node verbatim; selection cannot find it and the URL effect removes the node parameter. Existing shared/bookmarked government links therefore lose their selected ministry.

Keep the correct plural name and new canonical ID, and add an explicit legacy-ID resolver at URL input and public identity lookup boundaries. Add one regression case proving that the legacy selection resolves and canonicalizes. Do not change the ministry span to make it appear in 1980.

Locations: [src/government/episodes.js](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/episodes.js) — lines 62, 67, 145, 154, [src/government/GovernmentView.jsx](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/GovernmentView.jsx) — lines 34, 40, 224, 229

### CODE-02 — The advertised measurement command omits the zero-missing-minister metric (P3)

WANTED includes ministry-years with no minister matched (17 to0) in the table attributed to measure-government.mjs, but the script has no minister-coverage accumulator or output row. The existing test only checks greater than 95% minister coverage.

Add the missing ministry-year metric to the command. Add a focused Treasury regression covering the Finance and Agriculture alias and the later Finance style; the broad existing 95% test does not protect this fix.

Locations: [scripts/measure-government.mjs](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/scripts/measure-government.mjs) — lines 14, 29, 41, [research/WANTED.md](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/research/WANTED.md) — lines 15, 25, [src/government/government.test.js](https://github.com/ahzs645/PofBC/blob/0dbdb18cfebfb27e5529ce5940850e96eb9a995c/src/government/government.test.js) — lines 150, 161

This is a reproducibility/regression-gate gap. It does not contradict the current zero-missing result. Root is independently checking the full count.

## Decisions and changes supported by this review

### Treasury alias is appropriately constrained

The alias accepts both finance and finance agriculture while retaining episode/term date-overlap filtering. It adds the historical portfolio to Treasury rather than inventing minister tenures. The current department identity overlap remains a separate historical model question.

### All carried minister corroborations match their intended existing terms

Ten data_changes target nine Treasury/Finance term records plus Alex Fraser. All match assertions agree with current records. All 19 evidence additions are present: 18 Treasury transmittals and one Fraser appointment. Every extracted Treasury transmittal date lies within the matched tenure. The converter appends evidence and does not alter from/to.

### 1978 name, minister and event use the corrected identity

The new canonical ID resolves. The episode is 1978–1979, with Highways and Public Works as predecessor and Transportation and Highways as successor. The1978 snapshot names Alex Fraser with the plural Communications title. Its absence in 1980 is expected; the 1979 year-end view has the successor.

### EAB, Powertech and MSC decisions are explicit and refreshed

All three proposal IDs are unique, their stored records equal their proposal records, and all have decided=2026-10-21. EAB uses 1 January 1982; Powertech uses 29 September 1988 company incorporation and separately records 6 January 1989 naming. MSC retains the missing-proclamation and possible 1968 reconstitution qualifications. The changed tests assert accepted values and preserve BC Transplant as an unsettled example.

## Non-blocking qualifications

### Decision refresh is an authoritative replacement, not a merge

An already-held decision is replaced wholesale by its proposal object. In the reviewed commit every expected field is present and no actual loss was found. A later hand-edit in decisions.json would be overwritten by replay; proposals must remain the maintained source or the converter needs an explicit divergence guard. The held-ID index is not updated when appending, so future duplicate new IDs across modules would be appended twice; no such duplicate exists now.

### Interpret the minister metric as annual snapshot coverage

A zero count of ministry-years with no matched minister confirms the annual snapshots. It does not prove uninterrupted day-by-day officeholder coverage or settle whether two historical department names represent separate concurrent legal/administrative bodies.

## Checks performed

Read the exact commit diff; inspected the relevant converter and lookup logic; ran nonmutating Node probes for Treasury and the 1978 ministry; compared all carried corroborations to their target terms; verified the three new decisions against their proposal objects. The full 421-test suite and build/idempotence checks are being handled separately by root.
