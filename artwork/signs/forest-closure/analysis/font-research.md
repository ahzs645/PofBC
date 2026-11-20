# Forest closure sign typography research

## Finding
The photographs support a heavy geometric sans-serif / sign-lettering classification. They do not establish a particular foundry, manufacturer, or original font. Futura/Spartan is a plausible stylistic family; an unchanged Futura Extra Bold identification would be too strong, especially because of the source numeral 3.

## Visible morphology
- Main letters: flat-topped A, conventional steep N diagonal, near-circular O exterior with taller oval counter, relatively short R leg, heavy B with unequal bowls.
- Source 3: large asymmetric rounded bowls; sloping top-left and bottom-left terminals; extended horizontal inner waist. Neither Jost's flat-cut 3 nor League Spartan's compact round 3 reproduces it faithfully unchanged.
- OPEN: expanded setting, approximately 1.2-width-to-height O compared with approximately 1.0 in BOUNDARY. This can be represented by width/height scaling of shared masters; distinct proportions do not establish a separate historical font.
- CLOSED panel: a condensed setting of the same general lettering style. TO is visibly smaller than the adjacent words, approximately three quarters of their cap height.

## Modern controls
Six static comparison instances are in candidates.json. All derive from the official Google Fonts sources, with adjacent OFL licenses. League Spartan 800/900 is more structurally promising for the source A and N than Jost 800/900. Noto Sans 900 provides a useful control for the broad open numeral 3 but has a narrower O. These are hypotheses for pixel comparisons, not numeric match rankings.

Jost's creator explicitly describes it as keeping Futura's attitude rather than the exact design, with deliberately changed capital forms. League Spartan's creators describe influence from ATF's Spartan and warn that its variable Bold differs slightly from its first release. These should not be labelled original historical fonts.

## Historical source
BC Forest Service, Protection Bulletin 1960 no. 3, printed p. 4, FOREST CLOSURE ZONE SIGNS, contains both supplied photographs. The text says twelve pilot highway signs were designed and placed and could be switched open or closed by local Rangers. It gives no font specification. Search retrieval ref turn661958307search7:
https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do%3Bjsessionid%3D690234DCED0227D6194FFE7ED54C63C7?subdocumentId=21448

## Source list
- Bauer Types Futura page: https://bauertypes.com/fonts/futura/ (turn682740805view0). Identifies original 1927 Futura, later digital ND version, and separate Bold/Extrabold/condensed variants. Do not treat ND as a 1960 font file.
- Jost creator: https://indestructibletype.com/Jost.html (turn664774481search1).
- League Spartan creators: https://www.theleagueofmoveabletype.com/league-spartan (turn664774481search0).
- League Spartan source repository: https://github.com/theleagueof/league-spartan (turn664774481search2).
- Monotype historical Gill Sans Extra Bold specimen 321, Science Museum: https://collection.sciencemuseumgroup.org.uk/documents/aa110126408/specimen-sheet-for-gill-sans-extra-bold-series-number-321 (turn682740805view1). Local specimen gill_extra_bold_specimen.jpg for inspection.
- Futura Extra Bold specimen photographed by James Puckett, CC BY 2.0: https://commons.wikimedia.org/wiki/File:Futura_Extra_Bold_Type_Specimen_(8555786350).jpg (turn795426796view0). Local specimen futura_historic_specimen.jpg; this specimen has much smaller counters and a materially different 3 than the source signs. Its photo date is 2013; the specimen's original publication date is not established here. If reproducing it, credit James Puckett and CC BY 2.0.

## Scope caveat
This research does not establish every possible historical sign alphabet was tested. Photographic perspective, edge blur, ink spread, and sign painters' adaptations affect matching. Actual overlay numbers must report their crop, threshold, alignment freedom, and whether glyph shapes or positioning were optimized on that same photo.

## Follow-up correction and shared-master test

The corrected panel boundaries support one 1000 x 130 strip convention for both states. The earlier CLOSED height included photographic background. Direct comparisons using unchanged main glyph masters and independent x/y scaling support a shared alphabet: O gives 90.0-93.1% across six settings. For OPEN, O/E/N mean88.69% vs93.02% for locally adjusted shapes; E is identical, O improves only1.11 percentage points, and N accounts for the main residual. P never appears in the triangle and cannot distinguish the alphabets. CLOSED shared-character mean87.77% vs89.39% for local variants, measured in the prior character crop grid solely for shape comparison. These are fitted similarities, not proof of font identity. See shared-master-benchmark.json for full method and inputs.
