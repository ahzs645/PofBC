# SuperHost, 22 November 2026

A supplied vector reconstruction of SuperHost's "Expect the most" mark: the hospitality-training
program the Ministry of Tourism ran in the Expo 86 years. Read by `scripts/build-collected-marks.mjs`
(PROGRAM_PACKAGES) from `source-register.json`. It is shown in the gallery collection `superhost`,
which is tied to the government map's Ministry of Tourism (`ministry-of-tourism-1980`). The Tourism BC
& Destination BC initiative's SuperHost record links to it.

- Sources: a newspaper advertisement, supplied as a screenshot (`source/reference/newspaper-supplied.png`),
  credited to "The Honourable Claude Richmond, Minister of Tourism/Expo 86". Richmond was Minister of
  Tourism from 10 August 1982 to 14 August 1986. The package cites the Squamish Times of
  29 April 1986, page 19, for the program. That page wasn't checked here: the library's site serves
  an HTML page instead of the PDF to scripted requests. The second source is the SuperHost & Design
  specimen of CIPO record 0904301 (`source/reference/cipo-904301-logo.png`), whose Tourism British
  Columbia endorsement is left out.
- Method: the gallery's own twelve-path flag (`src/assets/flagMark.js`), every path unchanged
  (checked on import: 12 of 12 in each SVG), placed as one unit. The stars are regular five-point
  shapes fitted to the references; 145 for the newspaper layout and 128 for the CIPO one, partly
  inferred where the printed spray merges. The lettering comes from custom serif masters and
  brush-stroke skeletons. The original typefaces aren't identified.
- Revision 2 (`SuperHost_Vector_Package_Refined`, the same day) replaced the first delivery under
  the same file names. The serif masters and brush skeletons were refitted, and the flag, the
  stars and their placements are unchanged. Lettering overlap with the references (IoU at 0.5)
  rose from 0.57 to 0.70 (wordmark) and 0.41 to 0.58 (script) on the newspaper, and from 0.60 to
  0.83 and 0.37 to 0.64 on the CIPO specimen (`source/refinement-metrics.json`). The first
  revision's geometry is in `source/previous/`.
- Two layouts, reconstructed separately because the references place the stars differently. The
  newspaper layout is the gallery's main entry and is closest to its reference. The CIPO layout is
  a version.
- Colour: the colour versions use the gallery's flag blue #013366, red #AD0000 and gold #FCBA19.
  These are an interpretation, not SuperHost's inks.
- Files in `public/identity-collected/superhost/`: each layout in black and in colour, with a vector
  PDF of each (no fonts, no images).

The 2013 asset-transfer order's "SuperHost and Man design" (TMA631,599 and TMA672,366) is a later,
different mark. It stays in the Tourism BC & Destination BC initiative, from
`research/identity/tourism-asset-transfer-2013/`.

The supplier's notes are in `package-README.md`. `source/` holds the components, construction
JSON and rebuild scripts (`source/brush/` regenerates the slogan). `source/pofbc/` is the
supplier's snapshot of the flag at commit 46a0b38f2, which `source/rebuild.py` reads. `review/`
holds the before/after overlays and comparisons.
