# Northern BC travel guide selections, 2013 and 2014

Three sets of SVG selections were supplied on 2026-11-27: ten from the 2013 *Northern British Columbia Travel Guide* and sixteen from the 2014 guide. (The 2014 set came twice; the second copy added only page 97.) Each was checked in three ways:

1. Rendered as supplied, then again with every embedded bitmap removed. Whatever survived the second render is vector.
2. Compared with the gallery's holdings for the same body.
3. For each real gain, the logo was taken from the Legislative Library's copy of the guide, not from the selection file.

Extraction used MuPDF (PyMuPDF). Redaction removed the page's images, its text other than the logo's own, and the vector artwork touching the area outside the logo. The page was then cropped to the logo and exported with live text as glyph outlines. Bitmaps MuPDF still wrote into the SVG were removed. A pixel comparison before and after showed no change on a light or a dark ground. Each record in `src/gallery/northernTravelGuideArtwork.json` carries the page, bounds, method, native path count and any live text.

Sources (Legislative Library of BC):

- 2013: <https://digitalcollections.llbc.leg.bc.ca/handle/123456789/71173>
- 2014: <https://digitalcollections.llbc.leg.bc.ca/handle/123456789/71179>. The download is 77,187,864 bytes against a recorded 78,362,077. It is complete (it ends in `%%EOF`, all 97 pages open, and MuPDF needed no repair). Two downloads differ only in a few trailer bytes, so the server appears to stamp each copy.

## 2013

| Page | Logo | Vector in the selection? | Outcome |
|---|---|---|---|
| 3 | Super, Natural British Columbia Canada | No: part of the photograph | Native vector already held from the same page (`snbc-canada-no-oval-2013`) |
| 17 | Prince George moose | Moose and lettering only; the skyline is a page image | Not added; the held PNG notes the same image-dependent skyline |
| 25 | Tumbler Ridge | Yes | Already held (`tumbler-ridge-waterfall-colour-2013`) |
| 27 | Pouce Coupe | No | Nothing to add |
| 33 | District of Taylor with yellow swoosh | Yes | **Added** `taylor-district-swoosh-2013`, a separate design from the 2015 script |
| 47 | Fort St. James District | Symbol only; lettering is a bitmap | Symbol already held from the website |
| 52 | Houston | Yes | **Added** `houston-wilderness-script-2013-vector` as the preferred vector of the 2012 design |
| 62 | Blue “British Columbia” panel | Panel and text only | Not a logo; the page's Stewart Bear Arts mark is already held |
| 66 | Visit Terrace | Yes | Already held (`visit-terrace-bear-script-2013`) |
| 72 | Kitimat | Yes (renders broken in the selection) | Already held (`kitimat-tourism-script-2013`) |

## 2014

| Page | Logo | Vector in the selection? | Outcome |
|---|---|---|---|
| 3 | Travel Northern British Columbia tree | Yes | Same design as the held 2012 vector (`nbcta-travel-tree-2012`), reversed on blue |
| 24, 32, 38, 51, 68 | Frames, panels, advertisement copy | No logo | Nothing to add |
| 25 | Tumbler Ridge | Yes | Same as the held 2013 vector |
| 28 | Dawson Creek teal masthead | Yes | **Added** `tourism-dawson-creek-teal-2014-vector`, preferred over the 2015 printed crop |
| 28 | Tourism Dawson Creek emblem | Yes | Same design as the held 2015 vector |
| 55 | Smithers “I'm there.” | Yes | **Added** `smithers-im-there-2014`, a new design |
| 59 | “Historic Heartland of Northern British Columbia” | Text only | A tagline, not a logo |
| 61 | Stewart Cassiar | Yes, but only as typeset text | Not added. The title is live Georgia Bold and GoldFever type with no drawn paths, so it fails the gallery's native-path rule |
| 70 | Kitimat | No: the script is a page image | Nothing to add |
| 76 | Prince Rupert, Discover our nature | No | Nothing to add |
| 88 | Haida Gwaii | Yes | **Added** `haida-gwaii-red-2014`, the red-and-grey colourway of the held white 2015 wordmark |
| 97 | VIA Rail, A Green Choice | Yes | Same as the held 2012 vector |

## Leads

The Legislative Library also holds the 2016, 2017, 2018 and 2019 guides (handles 71174, 71172, 71178 and 71176), which the gallery has not drawn on yet.
