# Tourism BC and Destination BC: brands, websites and program evidence

This collection connects the visual and digital tourism assets described in
Ministerial Order 68/2013 with the existing Tourism BC and Destination BC artwork
and corporate histories in PofBC. The order is dated **21 March 2013**; the asset
transfer agreement names **1 April 2013** as its completion date unless the parties
agree otherwise. Those are not logo-adoption, domain-registration or website-launch
dates.

## Where the collection appears

Tourism is the first collection in the site’s top-level **Initiatives** section:

- Index: `?view=initiatives`
- Tourism: `?view=initiatives&initiative=tourism`
- Website records: `?view=initiatives&initiative=tourism&section=websites`
- HelloBC detail: `?view=initiatives&initiative=tourism&section=websites&record=hellobc`

The [initiative registry and adapter](../../../src/initiatives/initiatives.js)
load the generated tourism dataset lazily. The shared renderer uses its existing
record, timeline, publication, source and inventory arrays without copying or
inventing entries. The [Initiatives contributor guide](../../../docs/initiatives.md)
explains how a future documented initiative can use the same model and include
only the sections supported by its evidence.

Corporate artwork remains in Logos at
`?view=gallery&logos=tourism-bc-destination-bc`. The earlier
`collected-tourism-bc` and `collected-destination-bc` IDs still resolve to that
gallery collection. Old `#tourism-…` section and record fragments on those
collection URLs migrate to the corresponding initiative route; links selecting
a corporate gallery mark stay in Logos. Tourism BC and Destination BC retain
their separate government graph nodes and artwork ownership.

The [implementation and visual review](../../../docs/reviews/tourism-collection-2026-11-21/README.md)
includes desktop and mobile captures, stable links, focused checks and the limits
of the local preview build.

## What is included

- Nine digital records: HelloBC / SupernaturalBC.com; SuperHost / WorldHost; Near
  Me BC; BC Escapes; British Columbia Magazine; Share Your B.C.; Tourism BC online;
  Destination BC online; and Canada’s West / Canada’s West Marketplace.
- Twenty-one mark and name groups. Illustrated specimens, original publication
  vectors and names recorded without artwork retain separate evidence labels.
- Thirteen dated events connecting the corporate, program, publication and website
  histories.
- Seven publication records and all sixteen program areas in Appendix 9, with an
  additional international-portfolio research lead.
- The complete Appendix 5 inventory: **193 listed table-cell entries**, containing
  **191 distinct addresses**. This is not a count of working websites. Seven cells
  contain email addresses and eight contain subdomains. Two repeated entries are
  retained and point to their first occurrence.

The body histories remain separate. Tourism BC’s corporation ended on 1 April
2010, when its assets and obligations vested in government. Destination BC was
established on 2 November 2012 and began operations on 1 April 2013. This is a
connected tourism collection, not a claim that one corporation simply changed its
name.

## Editorial sources and build

`catalogue.json` holds the editorial records. `source-register.json` resolves
source IDs to publications, dates and URLs. `domains.json` preserves the original
page, column and row of every listed address, its printed case and a lowercase
matching value.

`artwork-manifest.json`, `website-manifest.json` and `our-brand-2021-manifest.json` record the acquired visual
specimens, their exact source locations, methods, dimensions and SHA-256 checksums.
The builder resolves each record’s `assetIds` against these manifests and checks
the files under `public/tourism/` before writing the runtime module.

```sh
npm run build:tourism-collection
npm run check:tourism-collection
```

The generated module is `src/gallery/tourismData.js`. Edit the source records and
regenerate it; do not make editorial changes only in the generated output.
Generation contains no clock-dependent values, downloads or network requests.
The check command verifies source consistency, image checksums, exact
reproducibility and the focused collection and initiative regressions without
rewriting generated data. Validation and preview are local; this
addition does not require a GitHub Actions runner.

## Image evidence

The website collection uses images from original publications. The 2014 WorldHost
figure is a crop of an official PDF displayed in a browser; the retained viewport
and crop coordinates document that route. The July 2022 HelloBC listing is the
original embedded bitmap, with its PDF soft mask restored. The October 2025
SupernaturalBC image is the publisher’s original monitor mockup, kept unchanged.
None is a reconstruction of an unobserved website.

Publication dates remain distinct from screenshot-capture dates. The 2025 article
was published on 10 October and separately dates the website’s launch to
10 September. A screenshot in a 2014 or 2022 publication documents what that
publication shows; it does not establish the exact day the screenshot was taken.

The December 2005 standards provide original PDF vector artwork. These extractions
are identified as native publication specimens, not newly designed logos or
standalone master files supplied by the issuing organization. Scan crops from
the order remain raster evidence. Where the official Gazette’s standalone images
are available, their source and colours are identified separately from the scan.

The artwork and publications retain their original ownership. The asset-transfer
order is historical evidence of a transfer between the Province and Destination
BC; it is not an open-use licence for every item listed.

## Domain inventory decisions

Pages 83 and 84 were manually checked against rendered source pages. Line wraps
inside cells were joined. The official Gazette HTML provides an independent
transcription where the PDF’s OCR omits or distorts text.

- `britishcolombia` addresses retain the printed **o**.
- `commmunitytourismfoundations.com` retains the printed **three m characters**.
- `canadawestmarketplace.ca` remains separate from `canadaswestmarketplace.ca`.
- Both occurrences of `supernaturalbc.ca` and the repeated historical email cell
  remain in the inventory.
- Historical email addresses are classified as email, with no contact action.
- Technical/staging names and `.xxx` registrations are not presented as operating
  public websites. Their purpose is not inferred beyond the name-based grouping.
- The inventory prints `shareyourbc.com`; the 2011 announcement separately uses
  `shareyourbc.ca`. Neither observation silently replaces the other.

Domain families are browsing aids based on the names. No DNS lookup, current
ownership inference, website-launch date or present availability is implied by
the grouping. Current website links and authentic historical visual evidence are
recorded separately on the relevant digital record.

## Limits and next collection work

The transfer schedule supplies useful leads for complete guide issues, app
interfaces, campaign websites, training manuals and market-specific website
captures. A named asset is retained as a research lead until the actual material
is inspected. Word-only records such as 100 BC Moments, Share Your B.C. and Discover
Camping are not filled with invented logos.

The international schedule contains repeated country and trademark-class
references. Those entries can document the same design in more than one market.
Its V-prefixed references are retained as source references, without relabelling
them as independently verified national registration numbers.
