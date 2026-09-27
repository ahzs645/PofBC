# Identity timelines: what the gallery knows about each body's marks over time

The gallery puts every mark on a timeline of the eras its body has had, oldest first, the way BC
Hydro's three identities are shown. The eras are in `src/gallery/timelines.js` (the one-offs'
timelines, and the BC Parks and BC Timber Sales collections' eras); each cites its sources inline.
This note records how they were found, and what is still open.

Researched 2026-09-26, mostly from Wayback Machine captures of each body's site, the Province's news
release archive, and the covers of its published plans and reports. Nothing was downloaded into the
repo.

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
