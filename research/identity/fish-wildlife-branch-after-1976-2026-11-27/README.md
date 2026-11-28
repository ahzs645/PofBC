# Fish and Wildlife Branch after 1976

Research, 27 November 2026. It covers the branch's parent bodies after the Department of Recreation and
Conservation, its later names, and any later marks.

## Sources read

- **BC Archives authority record 4108, "British Columbia. Fish and Wildlife Branch".** The live catalogue
  page sits behind a browser check that automated fetches cannot pass. The record was read in the
  Wayback capture of 3 January 2019:
  <https://web.archive.org/web/20190103101015/https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-fish-and-wildlife-branch-2>.
  Dates of existence: "1966-". History: "In 1966 the Fish and Game Branch changed its name to Fish and
  Wildlife Branch. The branch was transferred in December 1978 to Ministry of the Environment." Revised
  2017-02-24. No record was found for a "Wildlife Branch" (the slugs `british-columbia-wildlife-branch` and
  `british-columbia-fish-and-wildlife-branch` have no capture).
- **The hunting regulations synopses**, EcoCat report 22560:
  <https://a100.gov.bc.ca/pub/acat/public/viewReport.do?reportId=22560>. The synopses for 1973-74 to
  2005-06 were downloaded, read with `pdftotext`, and their covers rendered. The PDFs were then deleted.
  File names give the season's closing year (`BCHunt-Reg-1976` is the 1975/1976 synopsis).
- **The executive council records** already in `research/history/ministers-1975-1991.json` (source:
  <https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs/47984/execouncil.pdf>): Minister of Recreation and
  Tourism 22 Dec 1975 to 10 Feb 1976; Recreation and Travel Industry to 29 Oct 1976; Recreation and
  Conservation 29 Oct 1976 to 5 Dec 1978; Environment from 22 Dec 1975 on; Environment and Parks from
  14 Aug 1986.
- **The Ministry of Environment's Fish and Wildlife Branch page**, LAC web archive, 29 December 2006:
  <https://bac-lac.wayback.archive-it.org/web/20061229061732/http://www.env.gov.bc.ca/fw>.

## What the synopses show

| Synopsis | Cover: mark | Cover: parent body | Running footer |
|---|---|---|---|
| 1972-73 | F&W oval (already held) | | |
| 1973-74 | F&W oval beside "Fish and Wildlife Branch, Victoria" | | |
| 1974-75 | F&W oval beside "Fish & Wildlife Branch" | | |
| 1975/76 | F&W oval, foot of cover | Department of Recreation & Conservation, Hon. Jack Radford | British Columbia Fish & Wildlife Branch |
| 1976-77 | F&W oval beside the title | Department of Recreation and Travel Industry | Fish & Wildlife Branch |
| 1977-78 | Province's shield | Ministry of Recreation and Conservation, Hon. Sam Bawlf | Fish & Wildlife Branch |
| 1978-79 | Province's shield | Ministry of Recreation and Conservation | Fish & Wildlife Branch |
| 1979-80 to 1985-86 | Province's shield | Ministry of Environment | Fish and Wildlife Branch |
| 1986-87 | Province's shield | Ministry of Environment | **Wildlife Branch** |
| 1987-88 | Province's shield; the national "Wildlife '87" seal | Ministry of Environment and Parks | Wildlife Branch |
| 1989-90 | Province's shield | Ministry of Environment, Wildlife Branch (joint with Maclean Hunter) | Wildlife Branch |
| 1991-92, 1993-94 | "BC Environment" | | |

Only the oval is a branch mark. From 1977-78 the covers carry the Province's shield and the ministry's
name. The 1987-88 seal is the national Wildlife '87 / Faune 87 year, not the branch's.

## Findings

- After the department ended, the branch sat under the Department of Recreation and Travel Industry
  (1976-77 synopsis), then the Ministry of Recreation and Conservation (1977-78 and 1978-79 synopses).
- BC Archives records its transfer to the Ministry of Environment in December 1978. That fits the
  council record: the Minister of Recreation and Conservation's post ended on 5 December 1978.
- The synopses name it the Wildlife Branch from 1986-87; 1985-86 is the last "Fish and Wildlife Branch"
  footer. This is a publication date, not a record of the change.
- The Ministry of Environment had a "Fish and Wildlife Branch" again by 2006.
- The F&W oval is seen on every synopsis cover from 1972-73 to 1976-77. These are sightings: they date
  the files, not the mark's adoption or retirement.

## Applied

- `src/gallery/timelines.js`: the `fwb-emblem` era now cites the 1973-74 to 1977-78 covers and spans
  the 1972-73 to 1976-77 synopses; the department's `drc-1973-emblems` era cites the later covers too.
- `src/gallery/collections.js`: the oval's dates, and the collection's body, years (1971-1977) and intro.
- `src/gallery/reconciledSubjects.js`: the subject's note, sources and next action.
- `src/internal/internalPlaces.js`: the card note.

No new artwork was added. The covers show only the oval already held as a reconstruction.

## Still open

- When the Fish and Wildlife Branch split into wildlife and fisheries branches (about 1986), from a
  ministry annual report or an order.
- When the Fish and Wildlife Branch name came back (by 2006).
- Any branch mark after 1977.
