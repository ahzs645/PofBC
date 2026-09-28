# Identity timelines: what the gallery knows about each body's marks over time

The gallery puts every mark on a timeline of the eras its body has had, oldest first, the way BC
Hydro's three identities are shown. The eras are in `src/gallery/timelines.js` (the one-offs'
timelines, and the BC Parks and BC Timber Sales collections' eras); each cites its sources inline.
This note records how they were found, and what is still open.

Researched 2026-09-26, mostly from Wayback Machine captures of each body's site, the Province's news
release archive, and the covers of its published plans and reports. Nothing was downloaded into the
repo.

## ICBC, BCLC and BC Ferries

Their timelines came as three research packages (27 September 2026), filed here whole in
[`icbc/`](icbc), [`bclc/`](bclc) and [`bc-ferries/`](bc-ferries): each package's own README
(`PACKAGE.md`), its evidence notes (`NOTES.md` and `SOURCES.md` for ICBC, `EVIDENCE.md` for BCLC,
`SOURCE-NOTES.md` for BC Ferries) and its machine-readable timeline and sources. The logo SVGs are
in `artwork/icbc/`, `artwork/bclc/` and `artwork/bc-ferries/`, with the files originally supplied
to the research in `supplied/` beside them; the packages' boards, previews and screenshots were left
out. Paths inside `PACKAGE.md` are the package's own (`logos/`, `data/`, …), not this repo's.

What the gallery took from them, and did not:

- **Evidence groups, not exclusive eras.** ICBC's five eras are the package's five dated groups; a
  trademark filing, a use claimed in one and a dated cover are kept apart, and no adoption or
  retirement date is invented. A filing is `first_observation`, never an adoption. Only BCLC's
  August 2008 redesign and BC Ferries' wave (announced 2 April 2003) rest on a record. BC Ferries'
  "about 1978" is the package's inference from that announcement ("unchanged for 25 years").
- **Colour variants are not eras.** ICBC's orange (on icbc.com in 2026) and black sit in the rounded
  badge's era beside the blue; the blue and black are declared recolours of the supplied orange paths.
- **Reconstructions say so.** ICBC's 1974 emblem (outlines only, colours not inferred), both 1989
  lockups and the serif badge are rebuilt; BCLC's red, orange and green mark is today's letters in the
  design system's older palette, not a 2008 master. Every BC Ferries dogwood mark is rebuilt; the 1963
  flag is an interpretation of a brochure illustration. The isolated geometric dogwood (white petals,
  no ground) and the uniform-patch photograph were left out; the flag carries the same flower.
- **Open:** a 1973 example; when any early ICBC mark was adopted or retired; the serif-to-sans change;
  what the orange treatment is for; the first appearance and colours of BCLC's sun and waves; and when
  BCLC's purple, coral and yellow palette came in; a dated introduction for BC Ferries' geometric
  dogwood, and whether its flower and lettering changed together. No body has supplied a master or
  permission. BC Ferries' wave belongs to BC Ferry Services Inc., which is not a public body; the
  collection links to the Crown corporation it replaced.

## The rules the timelines follow

- **A capture is an observation, not an adoption.** Nearly every date is the first or last capture
  that shows a mark (`first_observation`). Only a few rest on a record: the Best Place on Earth
  slogan (2005, dropped 2011), WelcomeBC's announcement (13 June 2007), "Where ideas work" (2007),
  Environmental Reporting BC (2012), StrongerBC (17 September 2020), PreparedBC (1 May 2015) and
  BC Timber Sales' establishment (20 June 2003).
- **A mark nobody has looked at is not described from its filename.** Several eras say an image was
  archived but not yet looked at; they are listed below so someone can.
- **An era with no mark of its own is not a missing mark.** Where a body went under the Province's
  or its ministry's marks (BC Stats since 2017, the Wildfire Management Branch, the Analytical
  Laboratory), the era is `none`, drawn with a solid slot, not the dashed one of a mark still to find.

## Artwork to obtain

Each is linked from its era as "Artwork seen at". In rough order of how much it would add:

| Body | Era | Where it is |
| --- | --- | --- |
| BC Parks | The BC Parks logo, 2023– | `bcparks.ca/static/BCParks_Primary_Reversed…svg` (and a vertical version) |
| WorkBC | The flat mark with a grey rule, 2018– | `workbc.ca/themes/custom/workbc/logo.svg` |
| WelcomeBC | Stacked, 2025– | `welcomebc.ca/getmedia/…/WelcomeBC_cmyk_pos_Print.svg` |
| WelcomeBC, WorkBC | The flat mark with a gold rule, 2016– | `…/welcomebc-header-logo.svg`, `…/workbc-header-logo.svg` (Wayback) |
| PreparedBC | Its own lockup, 2015– ("BC" in gold) | `…/embc/images/bcid_preparedbc_rgb_pos.png`; the guides' one-ink versions are PDFs |
| BC Timber Sales | Beside the oval crest, 2017–2022 | the covers of its business plans, 2017/18 to 2021/22 |
| BC Wildfire Service | The oval crest | e-know.ca's copy (2021), a JPEG |
| StrongerBC | Endorsed mark and wordmark, 2024 | the Province's download-marks page |

## Still open

- **The Province's own chronology.** When the flag logo came in (a flag historian says around 1983;
  licence-plate sources say 1963), when the sun mark's sun went flat (by 2016 on WelcomeBC's and
  WorkBC's sites; between 22 November and 2 December 2016 on BC Parks'; PreparedBC's flat lockup is
  on file from September 2015), and when today's ministry marks came in.
- **BC Parks' badge.** First seen on brochures printed in 2002; the 1980s start is inferred. BC
  Archives GR-3888 (BC Parks in-house materials master files, 1937–2008) holds its "logos, badges,
  stickers".
- **Marks archived but not looked at:** BC Stats' logos of 1996, 2004 and 2012; WelcomeBC's of 2010
  and 2013; WorkBC's headers of 2010–2015; Environmental Reporting BC's footer wordmark of 2012; the
  later "Where ideas work" logo.
- **Which years the gallery's own marks are from,** where they came to the project without a record:
  WelcomeBC's (before 2016), BC Stats' (probably its header of 2007–2012), Environmental Reporting
  BC's (probably its templates of 2015–2016). Each wants comparing with the capture its era links to.
- **BC Wildfire Service's oval crest:** when it started. The ministry it names existed 2010–2017.
- **Retirements:** no source dates the end of "Where ideas work" (still in use in 2023) or of the
  "StrongerBC for everyone" word mark.
- **WorkSafeBC** is on the "not yet in the gallery" shelf with its 1968 and 1983 logo dates already
  verified; a timeline for it waits on artwork.
