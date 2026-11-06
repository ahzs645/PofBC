# Salary name search

## Why a separate discovery directory exists

The original search interprets a single word as a surname and loads the salary-record shard for
that surname's first two letters. `milad` therefore loads `people/mi.json.gzip`, while the record
`Fathi Baghbadorani, Milad` is stored in `people/fa.json.gzip`. Better fuzzy scoring cannot find a
record that candidate retrieval never considers.

Free-text name searches now use every word of a disclosed name. `Milad`, `Fathi`, `Baghbadorani`,
`Milad Fathi`, and `Fathi Milad` can all find that record. Matching ignores case, diacritics and
optional apostrophes, separates hyphenated words, and accepts word prefixes. Every query word must
match within one disclosed or already-linked spelling. A comma retains the existing precise
surname/given-name matcher, including its initials rules.

Complete-word matches rank before prefix matches, then by the existing surname/name key. Normal
searches no longer select just one possible name order and conceal the other full-name matches.
Multiword searches retain a separately labelled list of compatible initials-only alternatives.

## Data flow and reusable parts

1. `scripts/build-salary-search.mjs` reads the published people exports and existing name-link
   files. It uses `linkLookup` and `personKey`; it does not make identity decisions or modify
   source rows.
2. `src/salaries/nameSearch.js` produces compact employer-scoped documents:
   `[key, displaySpelling, employerIndex, periodIndexes, spellings, recordShards]`.
   Every two-letter word prefix routes to its documents. The manifest records bucket sizes, so a
   multiword query downloads the smallest eligible bucket. Employer and period indexes remain
   paired, preventing a filter from combining an employer in one year with another employer's year.
3. `NameSearchResults.jsx` matches and filters these documents, combines only their existing keys,
   and paginates before loading salary rows. Only the current page of up to 24 results requests its
   original record/link shards. Cards use the same `describeNameGroup`, currency annotations,
   reviewed canonical spelling and `PersonCard` as the existing record view. Opening a card uses
   the existing person-history page.

Matching normalization is independent of identity normalization. It never changes a source name,
`personKey`, name-link decision, payment, source citation or reporting-period label. A shared name
is still not proof of a shared identity. Spellings from two aliases cannot supply different words
of a single match, and an employer's reviewed alias cannot create a match at another employer.

Normalized spelling tokens are cached by immutable document object using a WeakMap. Query and
filter results are not cached. Changing the query or filters resets paging, including when a
previous query is entered again.

## Employers and positions

Employer discovery uses `employerSearch.js` and the same text normalization. It searches the
published names and slug in any word order, plus explicit discovery-only aliases. UNBC and UVic
are supported from their universities' own [UNBC](https://www.unbc.ca/) and
[UVic](https://www.uvic.ca/about-uvic/about-the-university/index.php) naming. These aliases do not
alter disclosed names, employer identifiers or source evidence. Sector and period filters still
apply before the employer results are displayed.

Position discovery keeps the existing `titleMatcher` and expands its supported abbreviations
before checking query length, so `RN` and `VP` reach the registered-nurse and vice-president
matches. Its compact index lists titles across all sectors and periods; the interface now states
that scope. Opening a title applies the selected sector and period to its detailed records.
Within an employer, the existing local name/position filter remains available alongside the
global search field. The separate Government view's organization/timeline search is unchanged.

Role pages select the requested title from original CAD rows before applying the existing
compiled-repeat suppression. This preserves a title supplied only by the compilation when a
matching official payment omits the position, preventing a search result from opening an empty
role page. Such rows retain their original source and display an unverified compiled-position
label. Employer and person payment aggregates keep their existing repeat-suppression behavior.

## Build and verification

```sh
npm run build:salary-search
npm run check:salary-search
node --test src/salaries/*.test.js scripts/salary-search.test.mjs
npm run preview:salaries -- --build
```

The DOM integration harness mounts the actual salary components against the published files. It
uses the application's installed React and an isolated installation of test tools, without changing
the application's dependencies or lockfile:

```sh
npm install --prefix /tmp/salary-ui-tools --ignore-scripts --no-package-lock jsdom@29.1.1 esbuild@0.27.0
SALARY_UI_TEST_MODULES=/tmp/salary-ui-tools/node_modules node scripts/verify-salary-search-ui.mjs
```

Generate the search directory first. These checks exercise first-name and comma searches, original
card summaries and history, Back navigation, paging resets, sector/period filters, legitimate absent
optional links, and visible failures with successful retries. Expected counts and the target card's
summary come from the current published data. Employer cases cover published names, supported
aliases, filters, old-slug routes and local searches. Position cases cover abbreviations, global
versus detail filter scope, employer table filtering, and title-to-role-to-person navigation,
including a real compiled-title/untitled-official-payment regression. This is React DOM integration
coverage, not a visual browser test.

The directory is generated during `build:assets`, after name links in `build:salaries`, and before
the salary preview. Its output at `public/salaries/search/` is ignored by Git and included in site
builds. The salary export validator treats `search` as a generated companion directory while still
rejecting unknown directories and reconciling every published record. Rebuilding uses the checked-in
published exports and needs no live report downloads.
`check:salary-search` validates the reported Milad case against the complete dataset, including
query order, partial words, year/employer filters and first-page record-shard costs. The dedicated
salary-search workflow runs the unit, full-data and DOM checks, then builds the preview with the
repository's locked application dependencies; the existing salary source/export workflow continues
to run as well.

Builds validate each people shard against the published row count, produce deterministic
content-addressed bucket files, and replace the directory only after successful generation.
The manifest includes the employer and period tables needed to reject a stale numeric mapping.

Failed directory, record and required-link requests have separate retry states. A missing optional
link file is empty only for an actual HTTP 404; a network or server error must not silently remove
linked history. The shared loader requests JSON explicitly, preventing a development server's HTML
fallback from disguising a missing JSON file. Retries can refresh successful cached responses after
a deployment, and a changed employer/period mapping asks the reader to reload the page.

## Search packages and scope

[MiniSearch](https://lucaong.github.io/minisearch/) is a useful future option for ranked token
search and controlled typo suggestions. [Fuse.js](https://www.fusejs.io/token-search.html) and
[FlexSearch](https://github.com/nextapps-de/flexsearch) offer other fuzzy/token or worker-based
options. None repairs incomplete surname-only retrieval by itself.

This change adds no runtime package: the compact buckets, explicit relevance tiers and existing
row renderer cover the reported discovery problem. A future typo feature must also retrieve across
token-prefix buckets when a spelling error changes the prefix. Approximate suggestions should be
labelled and should never become identity-link evidence. This version supports complete words and
word beginnings, not arbitrary substrings, phonetic name equivalence or automatic typo correction.
