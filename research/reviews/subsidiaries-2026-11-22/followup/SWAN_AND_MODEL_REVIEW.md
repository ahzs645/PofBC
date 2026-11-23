# Swan Valley and graph representation

Reviewed 22 November 2026. This memo supplements the verified package; it does not change the user's uncommitted checkout.

## Swan Valley Foods

Do not enter 1 December 1977 as the start of public ownership. It is the sale date. The prior audited evidence establishes a 40% holding at 31 March 1977, further share purchases, and 100% sold to Standard Brands on 1 December 1977. Full ownership began after 31 March and on or before 1 December; its exact start remains unknown.

For the current dated ownership graph, retain the hold if an unknown/bounded ownership start cannot be represented. Keep the company, known ownership evidence and sale in the research catalogue. A future view can show a qualified transaction marker or an interval with an uncertain start; it must distinguish an ownership period from legal incorporation/existence. Do not invent a one-day ownership interval or use a sale as formation merely to satisfy an event-to-drawn-node test.

### Additional legal-history lead

Corporations Canada identifies Swan Valley Foods Ltd., federal no.026524-1, with a **certificate of continuance from British Columbia on 6 January 1978** and an **amalgamation on 28 April 1978**. The successor's official history records the name Standard Brands Canada Limited from 28 April 1978 and the later Nabisco name. The January date is federal continuance, not Swan Valley's original incorporation or a public acquisition. This does not resolve the earlier start of 100% provincial ownership. A provincial registry-number bridge remains useful before integrating the federal record into the existing provincial identity.

Sources:

- [Standard Brands annual report 1977](https://digital.library.mcgill.ca/images/hrcorpreports/pdfs/6/635434.pdf), printed 30 / PDF 33, note 6: exact share-sale event, previously visually verified.
- [Public Accounts 1977/78 in Auditor General 1978](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19780301-report-auditor-general-1978.pdf), B5 and B8: comparator holding and additional purchases.
- [Corporations Canada no.026524-1](https://ised-isde.canada.ca/cc/lgcy/fdrlCrpDtls.html?corpId=265241), Corporate history / certificate of continuance and amalgamation status; retrieved 22 November 2026.
- [Corporations Canada no.029823-9](https://ised-isde.canada.ca/cc/lgcy/fdrlCrpDtls.html?corpId=298239), successor name history and amalgamating corporations. Source text inspected; treat the provincial identity bridge separately.
- [Hansard 27 June 1977, night sitting](https://lims.leg.bc.ca/hdms/file/Debates/31st2nd/31p_02s_770627z.htm), discussion beginning printed 3135: earlier funding and the separate Creston Valley asset transaction. No exact start of 100% ownership established by the inspected passage.

## Direct ownership versus group membership

The V I T company group can be represented as qualified group interests, with percentages and dated observations. The source phrase 'directly or through a subsidiary' does not warrant five direct parent edges. Keep `immediate_parent` unknown where unproven. A separately typed group/ultimate-owner relationship is suitable if supported by the renderer. Otherwise preserve the source rows and delay those direct edges.

The follow-up transit memo documents changing percentages and an explicit direct Vancouver Island Transportation holding. Use those dates instead of applying one percentage to all years. Canadian Cellulose's majority interest is similarly distinct from a wholly owned subsidiary; Kootenay Forest Products has explicit 100% ownership evidence.

## What the public repository model supports

Read-only inspection of remote main found `coverage: observation_only`, `observed_on`, null unknown starts, and explicit distinctions between observations and continuous periods in `research/history/sub-agencies-researched.json` and `scripts/build-government-history.mjs`. The snapshot renderer uses an observation only in its observation year. Its sub-agency loop excludes an entity after the exclusive end boundary. Therefore setting a company's start equal to its sale/end is an unsuitable workaround for a short public-ownership phase.

The name renderer can display a sourced name observation in its observation year. An unresolved rename day does not require omitting all evidence for later names. Use exact Gazette changes where recovered, source-qualified name observations elsewhere, and an identity label or explanation where the selected date falls in an uncertain transition. A label should not imply that Panco remained its legal name until 1992.

These are model findings from remote files, not a review of the user's uncommitted implementation. File paths and Git blob hashes are recorded in `repo_read_metadata.json`. Public links:

- [Build script](https://github.com/ahzs645/PofBC/blob/main/scripts/build-government-history.mjs)
- [Snapshot renderer](https://github.com/ahzs645/PofBC/blob/main/src/government/snapshot.js)
- [Research data and policy](https://github.com/ahzs645/PofBC/blob/main/research/history/sub-agencies-researched.json)

## Scoped commit

Apply definite factual corrections from the follow-up before finalizing the subsidiary commit. Exact unknown dates and unresolved spelling bridges can remain explicit follow-ups. Stage an explicit list of subsidiary research, source data, relevant tests and reproducibly generated files. Leave the three BC Enterprise SVGs, `collected-display-overrides.json` and `collectedDisplay.js` outside this commit; do not discard or stash another session's changes.

Review the staged diff and validate that staged tree in an isolated local checkout/export, using the repository's existing tests and `npm run check:government`. This resolves the concrete risk that the unrelated working-tree failure could obscure a failure in the proposed commit. Do not trigger GitHub Actions for this check. Record pass/skip/fail counts accurately. The user's report is 1,141 passed, six skipped and one unrelated working-tree failure; this research review has not independently rerun that suite.
