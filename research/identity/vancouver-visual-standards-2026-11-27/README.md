# City of Vancouver Visual Standards Guide, February 2018

Source: [policy.vancouver.ca/CP00103P2.pdf](https://policy.vancouver.ca/CP00103P2.pdf), 21 pages,
created in InDesign by Elaine Ayres, 27 February 2018. SHA-256
`baa38a1913417a9dcda1cf8e18cb7e7ce17c7a879af506f3f5311105b0adb2a1`, the same file the
[earlier reference note](../current-primary-logo-search/vancouver-reference.md) recorded. The PDF is
not committed. Pass a copy to the extraction:

    python3 scripts/extract-vancouver-guide.py --source path/to/CP00103P2.pdf          # write
    python3 scripts/extract-vancouver-guide.py --source path/to/CP00103P2.pdf --check  # verify

`extractions.json` holds one recipe per mark: its page, the region it occupies (PDF points from the
page's top-left), any fills the guide lays over it (the red `#c22134` "incorrect usage" crosses, the
black panels behind reversed artwork) and any box to leave out (an emblem the page clips away
behind Talk Green to Us). The script keeps the paths drawn inside the region, with only the
definitions they use, and writes `src/gallery/vancouverVisualStandards.json`, which the gallery
reads through `withVectorRecovery`. Every file is the guide's own filled paths: no images, no live
text, no glyph substitutes, nothing traced or recoloured.

## What the guide gives, and where it went

| Page | Content | In PofBC |
| --- | --- | --- |
| 4 | Emblem introduction: designed by in-house graphic designer Elaine Ayres, adopted unanimously by Council on 18 July 2006; its forms read as blossoms, waves, peaks, birds, Canada Place's sails and a V | The emblem's design is dated by that adoption (`adoption` on its files) |
| 4 | Coat of arms, granted by the College of Arms, London, 31 March 1969; reserved for Mayor and Council and ceremonial use; the guide's own small rendering | Coats of Arms → City of Vancouver (`vancouver-arms-visual-standards-2018`) |
| 5 | Emblem in colour, solid black and reversed white; the one-colour versions have gaps the colour overlap does not, so they must not be made by recolouring; grayscale retired | Versions of the existing emblem design; the colour vector is its default (`preferredVector`) and the website PNG stays a version |
| 7 | Partner and department logos sized to the emblem's full height or to the top of its middle arch: Vancouver Public Library, Police Department, Economic Commission, Board of Parks and Recreation, Fire Rescue Services, Greenest City | Five separate entries under "Agencies and boards beside the emblem"; dated only as the guide's specimens |
| 8 | Emblem with a department name (Engineering Services, Public Art Program) in three versions; the former centred Engineering Services lockup marked as replaced | Two lockup designs with three versions each; the former lockup as its own retired entry |
| 9 | Clear space: the width of "OU" in VANCOUVER; colour emblem no smaller than 0.75 in wide | Recorded here |
| 10 | Misuse examples (stretching, boxes, shadows, busy grounds, rotation, chrome, retyping, altering, recolouring) | Not collected: they are deliberately wrong |
| 6 | Extended palette (below) | Recorded here |
| 11–12 | Gotham for design materials (Thin to Ultra, with condensed widths; optical spacing), Arial for Office documents and PowerPoint | Recorded here |
| 13–17 | Greenest City: Council approved the Greenest City Action Plan in July 2011; the logo's two speech bubbles, turned upside down on a base as trees, come from the Talk Green to Us engagement; it always appears to the right of the emblem; minimum colour width 1.75 in | The co-brand in three versions; Talk Green to Us, Greenest City 2020 and Greenest City 2020 Access to Nature as retired entries |
| 18–21 | Business card, letterhead and envelope templates (kraft envelopes take only the black emblem) | Not collected |

### Extended palette (page 6)

| Name | Pantone | CMYK | Hex |
| --- | --- | --- | --- |
| Emblem Blue | 3005 | 84 51 0 0 | `#0074C8` |
| Emblem Green | 369 | 67 12 100 1 | `#61A644` |
| Dark Green | 363 | 74 24 100 8 | `#4D8C3F` |
| Dark Blue | 288 | 100 88 27 19 | `#1E366C` |
| Purple | 2602 | 56 98 1 0 | `#872A90` |
| Brown | 463 | 39 64 90 34 | `#784E28` |
| Yellow | 012 | 2 13 100 0 | `#FCD700` |
| Amber | 143 | 2 32 91 0 | `#F6B332` |
| Orange | 021 | 0 83 100 0 | `#FF5000` |
| Red | 200 | 17 100 86 6 | `#C21F32` |
| Teal | 7472 | 63 7 33 0 | `#5AB6B2` |

The guide notes that colours vary between programs. The emblem's paths are drawn in `#0081C6` and
`#6CB33F`, not the palette's hex values; the Greenest City page gives Emblem Green as `#6CB33F` and
Dark Green as `#3D8E33` (drawn as `#439539`). The files keep the colours the PDF draws.

## Rights

The guide states that the emblem and the arms are the City's property, protected by copyright and
trademark, and that their use needs the City's authorization. No permission has been sought; the
files are kept, as the gallery's other collected marks are, as documentary specimens with their
source.

## Dates of the Greenest City marks and the emblem (second pass, 27 November 2026)

vancouver.ca and council.vancouver.ca refuse automated fetches (403), so the documents below were read
from Wayback captures. The capture index came from the LAC web archive's CDX endpoint
(`https://bac-lac.wayback.archive-it.org/web/timemap/cdx`).

**The emblem.** The card already reads "Adopted 18 July 2006" from the guide's page 4. The council
record confirms it. The
[minutes of the Regular Council meeting of 18 July 2006](https://web.archive.org/web/20120118032333/http://vancouver.ca/ctyclerk/cclerk/20060718/documents/regularminutes.pdf),
item 15, "Visual Identity Program for the City of Vancouver": "THAT Council approve Option B2 … adapt a
current visual element as the City's new emblem for day-to-day use, and develop a standards manual".
CARRIED; three councillors opposed part A (the coat of arms), not B. The
[administrative report of 10 July 2006](https://web.archive.org/web/20241219152603/https://council.vancouver.ca/20060718/documents/a15.pdf),
page 12, shows the element: the in-house Host City blossom used at Torino 2006. It is the same symbol
as the held emblem.

**"Dates unestablished" on the City of Vancouver collection.** That label is not about a logo. It is
the collection's lifespan, from the body's `from` and `to` in `recoveredIdentityData.js`, which are
null for Vancouver (as for most municipalities). The gallery's timeline modes read the collection's
years as the body's life (`galleryModes.js`), so putting the 2006 adoption there would make the City
date from 2006. The logo's own date is already on the emblem card. Nothing was changed. Setting
`from: 1886` would need a sourced incorporation date; that is a separate change.

**Greenest City marks.** No council record adopts or retires any of the three marks. The Greenest
City Action Plan went to Council on 12 July 2011
([report RR-1](https://web.archive.org/web/20191105031618/https://council.vancouver.ca/20110712/documents/rr1.pdf)), and the guide says Council approved it in July 2011.
That is the plan, not a logo, so it is kept in the notes only. The yearly implementation updates
(2011-12 to 2019-20, and the 2021 final update) were checked by their covers. They carry a typeset
"GREENEST CITY / 2020 ACTION PLAN" title, not the bubble-tree logos, so they are not sightings of the
held marks. Dated sightings of the held designs, found as image files:

| Mark | File | Captures with the same content |
|---|---|---|
| Talk Green to Us | `talkgreentous.ca/images/logo_tgtu.gif` | [30 Aug 2011](https://web.archive.org/web/20110830121913/http://talkgreentous.ca/images/logo_tgtu.gif) to [1 Apr 2012](https://web.archive.org/web/20120401200131/http://talkgreentous.ca/images/logo_tgtu.gif) |
| Greenest City 2020 | `vancouver.ca/images/cov/content/gc2020-horiz.gif` | [12 Oct 2012](https://web.archive.org/web/20121012053655/http://vancouver.ca/images/cov/content/gc2020-horiz.gif) to [30 May 2015](https://web.archive.org/web/20150530090231/http://vancouver.ca/images/cov/content/gc2020-horiz.gif) |

Both were compared by eye with the guide's vectors: same bubble and lettering; same two bubble-trees
with GREENEST CITY 2020. They are recorded as `alsoSeen` on the two files, in both the recipe
(`extractions.json`) and the package. `scripts/extract-vancouver-guide.py` now copies `alsoSeen`
from the recipe. The engagement site was live from June 2010, but the logo file was first captured
in August 2011.

Still open: no dated sighting of the Greenest City 2020 · Access to Nature logo, and none of the
current Greenest City lockup before the 2018 guide.
