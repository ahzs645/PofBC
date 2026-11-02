# Name connections: complete index scan and BCI source review

Reviewed 2 November 2026. This is an identity research pass, separate from the
completed 65-lead source-acquisition pass. It adds no salary observations, deletes
no records and applies no new application joins or currency conversions.

The [subsequent source-verification pass](../source-verification-2026-11-02/README.md)
now records evidence for all 4,445 candidates and adopts 251 individually reviewed
source-spelling corrections. The files here remain the original candidate
snapshot; the follow-up contains current decisions and application changes.

## The reported Pittman example

The evidence strongly supports one BCI executive behind **“Pittman, J.”** and
**“Pittmsn, Jim.”** The latter spelling is an apparent transcription error in the
retained compilation. The current name-linker only considers the same normalized
surname, so it does not connect these two records. The appropriate reviewed name
is **Jim Pittman**, while retaining both disclosed spellings on the observations.

Primary evidence:

- [BCI 2017–2018 corporate annual report](https://www.bci.ca/wp-content/uploads/2018/01/17-18-corporate-annual-report-2018.pdf#page=46),
  physical PDF page 46 (printed page 44), names Jim Pittman as Senior Vice President,
  Private Equity. The executive management roster on physical page 78 agrees.
- [BCI 2023–2024 corporate annual report](https://www.bci.ca/wp-content/uploads/2018/01/2023-2024-corporate-annual-report_financial-statements-1.pdf#page=67),
  physical page 67 (printed page 65), names Jim Pittman as Executive Vice President
  & Global Head, Private Equity, with total compensation of **USD 3,902,330**.
  Physical page 92 (printed page 90), endnote 7 for printed page 65, explicitly
  confirms that his 2023–2024 compensation is reported in US dollars.
- [BCI's September 2024 interview](https://www.bci.ca/insights/article/jim-pittman-outlook-on-the-private-equity-market/)
  corroborates the full name and executive private-equity role.
- [BCI's January 2026 succession announcement](https://www.bci.ca/news/article/bci-appoints-jon-salon-as-global-head-of-private-equity/)
  states that Pittman led the program since 2016.
- [A public Jim Pittman LinkedIn post](https://www.linkedin.com/posts/jim-pittman-83979615_nyc-privateequity-activity-7054556811785371648-6p9X)
  corroborates his work leading BCI Private Equity and move to New York. The
  profile URL returned HTTP 999; the public post was readable. LinkedIn is
  corroboration only, and supplies no compensation verification.

**Identity and pay comparability are separate decisions.** The current
compilation displays the later USD amount with an unqualified dollar sign. The
earlier compiled amount, 1,512,762, is not the annual report's 2017–2018
total-compensation amount, 1,563,196. This review does not establish the meaning or
reporting period of the earlier compiled amount. It does not establish that the
two figures measure the same thing, and must not calculate a percentage raise.

The application join is therefore **held pending currency-aware record display
and comparison treatment**, and the financial issue is recorded in
[case-findings.json](case-findings.json). A complete implementation needs to:

1. Attach the original report, physical page, row currency and compensation
   definition to the exact compiled observation without overwriting its value or
   claiming the whole compilation is verified.
2. Show the later amount as US dollars in cards, tables and details. Keep it out
   of CAD rankings, averages and growth calculations unless an explicit,
   documented conversion policy is implemented. No exchange rate is assumed here.
3. Add an evidence-backed alias exception for the misspelled surname, preferably
   with the reviewed display name Jim Pittman. The automatic surname rule should
   stay conservative. The current loading scheme also needs consideration for
   reviewed aliases whose surname starts in a different index shard.
4. Preserve each original observation, including the compiled-period warning;
   hide mixed-currency comparison charts rather than plot incomparable amounts.

## The rest of BCI's high-pay name connections

The same two original reports corroborate the names and roles of **Gordon J.
Fyfe**, **Daniel Garant** and **Lincoln Webb**, supporting their connections to
the corresponding BCI initials. The app currently marks Fyfe and Garant verified,
and Webb likely. This review records primary-source support for all three,
without silently accepting their compiled pay definitions or periods.

For **R. Rayes / Ramy Rayes**, the full-name executive role and employment from
2016 are corroborated by [BCI's appointment announcement](https://www.bci.ca/news/article/ramy-rayes-appointed-as-bcis-executive-vice-president-of-investment-strategy-risk/)
and the 2023–2024 report. The exact earlier initial-only employee schedule still
needs direct verification; the existing likely status is retained.

## Full-index results

The repeatable scan read **all 1,379,680 published named observations** in the
270-employer people index, representing **368,224 normalized names within
employers**. These are name groups, not a count of distinct people. The remaining
5,341 published observations have no name and cannot enter a name-based review.

The current application decision ledger has:

| Existing status | Decisions | Interpretation for this review |
| --- | ---: | --- |
| Likely | 21,859 | Assumptions, requiring evidence before a confirmed identity claim |
| Apart | 4,275 | Kept separate by existing rules; inspect the recorded reason |
| Verified | 1,136 | Includes four reviewed overrides and 1,132 heuristic decisions |

The application's existing word **verified** includes matching positions,
extraction splits and matching amounts. It must not be described as 1,136
independent biography or original-source identity checks. A matching payment or
job title alone does not prove identity, and never proves that two payments are
duplicates. The existing ledger is [decisions.csv](../decisions.csv).

The additional detector found **4,445 possible one-edit surname pairs** that are
not already in the same application link group. Of these, 1,549 share at least
one reporting label and 2,896 do not. These are **review candidates, not 4,445
confirmed connections or errors**. No candidate was automatically joined.

Start with [surname-candidates.csv](surname-candidates.csv), or use the
[structured queue](surname-candidates.json). It records employer, both names,
their reporting labels, shared positions, shared-label cautions and next action.
Raw amount is a work-priority aid only; currencies and definitions may differ.
Some high-priority leads after Pittman include Germain/Getmain, Ionescu/lonescu,
Murthy/Murtby and Lefresne/Lefi"esne at PHSA. Others, such as Zhang/Zheng, may be
different people. They remain unreviewed.

## Review rules and scope

For each proposed connection, first inspect the original disclosure's name, row
boundaries and position. Then use dated employer announcements, official
biographies and public professional profiles to corroborate the employer, role
and dates. Keep conflicting middle names, homonyms, shared labels, employer
changes and salary-definition differences explicit. LinkedIn can support a
connection; a search snippet or matching profile name is insufficient by itself.

The new detector is deliberately bounded to surnames at least five letters long
that differ by one insertion, deletion, substitution or adjacent transposition,
with compatible given names at the same employer. It does not cover every
nickname, surname change, transliteration or cross-employer career. Existing
same-surname decisions are inventoried separately. The scan is complete for
these stated rules; individual external-source review of the whole queue is not.

## Reproduce and verify

From the repository root:

```sh
python3 -m unittest discover -s scripts -p test_name_connection_review.py -v
python3 scripts/build_name_connection_review.py --snapshot-ref 1a814359a0b74bbbc4620ba7ac3e5d2846ee1284 --check
```

[inputs.json](inputs.json) pins every people shard, link shard and input ledger
read by the scan. [summary.json](summary.json) contains counts and limitations.
[evidence](evidence) retains selected original-report page text, full-PDF hashes
and original URLs. The primary compensation tables and currency footnote were
also inspected as rendered pages. To reproduce extracts, retrieve the pinned PDF
and read the listed physical pages with PyMuPDF 1.26.6; verify the PDF SHA-256
before comparison. The full PDFs remain in the execution cache and are not new
accepted employee source cohorts.
