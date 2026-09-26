# Acceptance cases for a future implementation

These are proposed tests. They have not been run against the user’s existing application or logo generator.

1. **Parks origins versus organization.** Selecting 1911 exposes the first-park event, not a fabricated 1957 Parks Branch. Selecting 1957 shows the evidenced organizational milestone. Sources S10; seeds parks-first-park and parks-branch-1957.
2. **Wildfire identity.** The 1912 origin claim does not trigger display of the current logo/name as an original 1912 identity. S11.
3. **WorkSafe legal name.** At 2005, a WorkSafeBC brand label coexists with Workers’ Compensation Board as the legal name; no duplicate legal entity is created. S15.
4. **Year-only boundaries.** 1968/1983 logo events remain year-precision; exporting data does not silently generate exact January 1 adoption dates. S14.
5. **Appointment versus office assumption.** Wendy Cocchia’s commission on 2024-12-19 does not make her the sworn-in incumbent on that date; the separate 2025-01-30 event is preserved. S07.
6. **LG reconciliation.** A difference between 32 local records and an official sequence of 31 triggers review, not automatic deletion. S07–S08.
7. **Future election.** At 2026-09-25, future milestones are scheduled/planned and all 2026 result fields remain unpopulated. S01.
8. **Election versus cabinet.** Final Voting Day does not automatically terminate a minister’s role or create a new premier appointment. Appointment evidence is required.
9. **Phased transfer.** FNHA’s July and October 2013 transfers remain separate function-transfer events; FNHA is not a generic Ministry of Health child. S32–S33.
10. **Unknown reporting line.** BC Rail or WCB records with known existence but unknown responsibility remain visible in an uncertainty lane, without a guessed ministry edge.
11. **Current observation.** A 2026 deputy/CEO observation does not appear as fact in an earlier year without supporting evidence.
12. **Session/report year.** A report about year Y published in session Y+1 retains both fields. S26.
13. **District vintage.** A candidate result uses its election’s district geometry, not the most recent boundary with the same name. S05.
14. **Multi-member representation.** A district can return more than one member when the underlying historical election record requires it; there is no global one-district/one-seat constraint.
15. **Caucus timeline.** Changing caucus does not rewrite a person’s party-at-election field.
16. **Staffing comparison.** FTE, headcount, budget and actual values remain separate; incomparable reporting scopes generate a warning rather than a false trend.
17. **Artwork status.** A media-contact page alone cannot mark a logo as “verified original vector.” A file must actually be obtained and inspected.
18. **Identity generator.** Historical-name/current-style outputs are labeled generated interpretations; source artwork and generated exports are distinguishable.
19. **Counterfactual absence.** An unknown founding date is not rendered as “did not exist,” and an uncatalogued logo is not rendered as “no logo.”
20. **Graph accessibility.** Every graph node, relationship and evidence item is reachable through an equivalent searchable table and keyboard navigation; mobile details are readable without a giant fixed-width chart.
21. **Reproducible views.** A copied URL restores date, selected entity, scope, uncertainty and identity-mode settings.
22. **Conflicting evidence.** Contradictory dates retain both source claims and a visible editorial resolution; no silent overwrite.
23. **Original versus reviewed data.** Source transcription, correction and reconstruction remain distinct, matching the earlier reviewed-atlas approach.
24. **Source freshness.** A record can show historical validity and a separate last-reviewed date; users can see when “today” was actually checked.
