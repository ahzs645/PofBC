# Supplemental health board schedules

This finite follow-up processes 19 genuinely uncovered board scopes found while reading the 65 employee originals: six Fraser Health schedules (2004/05–2009/10), Interior Health 2010/11, and twelve Vancouver Coastal Health schedules (2008/09, 2009/10, 2013/14–2019/20, 2021/22, 2023/24, 2024/25). It adds 186 known-pay board observations. Eight named observations with nonnumeric remuneration remain supporting evidence; no zero pay is invented. Earlier accepted board histories and employee records are unchanged.

The exact 28-page source inventory subtracts seven already reviewed board scopes and two aggregate reconciliation pages. Source-to-original-lead mappings, official original links, physical pages and source/data/provenance hashes are in `source-lead-dispositions.json`. Catalogue years are discovery locators; acceptance uses the schedule's printed fiscal ending year. North independently read all 194 board observations from original images before opening candidates. Its first transcript and explicit corrections of its own readings remain immutable. Both complete native readers independently reproduce every raw name/position/pay/expense/total/footnote cell and printed control. The producer separately viewed six full original schedules; that bounded check is recorded honestly.

Pay uses the separate remuneration column. Expenses and inclusive totals are excluded from pay. Blank/dash expenses remain null. The eight nonnumeric-pay observations retain known expenses of 1,801.71 CAD, including VCH2009/10 DavidThompson 1,589.71, VCH2017/18 BillDuvall 18, and VCH2018/19 PennyBallem 194. They do not become salary rows. Board footnotes and source names before Chair separation remain in provenance. Source payment years are retained when footnotes discuss earlier terms or retainer payments.

VCH2023/24's complete literal expenses exceed its printed expense subtotal by 2 CAD; literal remuneration plus expenses also exceed its printed inclusive grand total by 2 CAD. VCH2018/19's complete literal expenses exceed its printed expense subtotal by 1 CAD, while literal remuneration plus expenses agree with the printed grand total. Independent source-first review confirmed the displayed fields. No amount was adjusted to balance controls; causes remain unestablished. Both qualifications are public warnings. Fraser2004/05 explicitly describes only three quarters of retainer payments after its July2004 policy change; this disclosure is not annualized.

Replay offline from committed evidence:

```
python3 scripts/gap_health_board_supplement.py --check
python3 -m unittest discover -s scripts -p test_gap_health_board_supplement.py -q
python3 scripts/gap_health_board_supplement_freeze.py --check
```

Default replay needs the Python standard library and the committed native fixtures. `--originals` additionally needs PyMuPDF, Poppler and the exact pinned public-source PDFs at the recorded workspace cache paths; it refreshes paired words and visibility diagnostics sequentially. Both check and originals modes together are rejected. Independent review is pinned through `review-adoption.json`; original candidate proofs are preserved under `pre-adoption/`. All19 salary-page paint/overprint/field-edge/visible-ink diagnostics have zero flags; those diagnostics do not prove pixel accuracy by themselves.

No outreach, contact form, FOI or fee action occurred. The four user-held issuer requests remain held. No compiled records are removed; possible overlap is disclosed. These board disclosures are not employee rosters or annual salary rates.
