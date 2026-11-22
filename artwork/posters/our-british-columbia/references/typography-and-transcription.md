# Our British Columbia — typography and credits research

## Source references

- User attachment: `../upload/s-l1600.webp`.
- Exact seller listing for the same physical poster: https://www.ebay.com/itm/397627062142 . The seller title mentions Heather Cooper, but this is not confirmed artist attribution and should not be repeated as authoritative.
- Main listing image: https://i.ebayimg.com/images/g/HocAAeSwemZplo8G/s-l1600.jpg (`other-poster.jpg`). This duplicates the user's photograph rather than supplying a better view of the text behind magnets.
- Pavilion detail: https://i.ebayimg.com/images/g/MawAAeSwl~Zplo8T/s-l1600.webp (`other-pavilion.webp`).
- Producer marks detail: https://i.ebayimg.com/images/g/YIEAAeSwWLhplo8j/s-l1600.webp (`other-bobrogers.webp`). This reveals the complete Industrial Showmanship emblem hidden by a magnet in the main photograph.

## Title typography

The serif title reproduces the British Columbia wordmark, including three designed joins: B–C (large initial capitals across lines), R–I (the R leg blends into the I foot), and C–O (the terminal of C crosses the O). These should be recreated as designed contours, not ordinary overlapping plain text. The `OUR` word is hand lettering.

The exact historical serif typeface is not confirmed. Do not label the reconstruction as an identified exact font. Font comparison sheet `title-font-comparison.jpg` fits every unmodified glyph to approximately the same photographed bounding box to compare contours rather than widths. EB Garamond 400 comes closest to the source weight among sampled unmodified options; Cormorant Garamond has some related graceful contour features but is too thin at 400–500. Source reconstruction benefits from custom B/C/R/I/U/M contours and serifs.

Downloaded open fonts come from `https://raw.githubusercontent.com/google/fonts/main/ofl/<family>/<fontfile>`; corresponding OFL text is included in this directory. Default downloads are variable fonts; static 400/500 instances were made with fontTools for comparison only.

## Credit typography

`credit-font-comparison.jpg` shows equal line widths and cap heights. **Six Caps** is the best sampled open substitute for uppercase billing. Its long parallel-sided bowls and rectangular counters are closer than the oval forms in horizontally compressed Nimbus Sans Narrow or Oswald. It is a visual substitute, not a confirmed historical font identification.

- Main uppercase credits/roles: Six Caps (`SixCaps.ttf`).
- Mixed-case small print: Oswald Light 300 (`Oswald300.ttf`) is a practical outlined approximation; horizontal fitting required.
- Bob Rogers & Company, Inc.: bold slab serif resembling Clarendon ExtraBold/Rockwell ExtraBold. `AlfaSlabOne.ttf` supplied as practical font-derived base. The logo has a filmstrip crossing through the ampersand.
- Industrial Showmanship: all caps stencil serif, sitting below a winged camera in front of the upper half of a toothed gear, two lightning bolts, and tripod legs crossing the words. This is fully visible in detail photo.

## Main credits — directly readable

Row 1:
- THE BRITISH COLUMBIA PAVILION
- presents [much smaller, baseline aligned]
- OUR BRITISH COLUMBIA
- WRITER/DIRECTOR [role above name] RICHARD JEFFERIES
- EDITOR [role above name] MARSHALL HARVEY

Row 2:
- DIRECTOR OF PHOTOGRAPHY / REED SMOOT
- CINEMATOGRAPHER / BRUCE INGRAM
- MUSIC / DAVID SPEAR
- WITH / THE NEW BC PHILHARMONIC ORCHESTRA

Row 3:
- PRODUCTION SUPERVISOR / GEORGE WIKTOR
- POST PRODUCTION SUPERVISOR / RICK GORDON
- ASSOCIATE PRODUCER / LYNNE CARROW
- PRODUCTION MANAGER / KAREN STEWART
- PRODUCER / BOB ROGERS

The separators between units are middle dots. In the photo glare makes several credits gray, but they are treated as the same intended black ink.

## Fine print — transcription with uncertainty explicit

Dedication: `For Lisa, Tyler and Jordy` (last letters under light/shadow; Jordy is the best visual reading, moderate confidence).

Line 1, visible transcription:
`Music Recorded at Little Mountain Sound, Vancouver · Processing by Alpha Cine Service, Vancouver [hidden]ment by W.F. White, Ltd., Vancouver · Video Post by Post Haste Video, Vanco[hidden]`

Natural reconstruction of line 1, with supplied material in brackets:
`Music Recorded at Little Mountain Sound, Vancouver · Processing by Alpha Cine Service, Vancouver [· Equip]ment by W.F. White, Ltd., Vancouver · Video Post by Post Haste Video, Vanco[uver]`

Line 2, visible transcription:
`Sincere appreciation to the Motion Picture Studio Production Technicians I.A.T.S.E. 891, Vancouver, Canada, with spec[hidden]George Chapman; and to Dianne Neufeld and the staff of the B.C. Film Production[hidden]`

Likely expansion of middle hidden words: `with special thanks to George Chapman`. This is consistent with the related Bob Rogers Rainbow War credits (https://rainbowwar.com/wp-content/uploads/2011/08/rainbow-war-film-credits5.pdf), but that separate film does not establish every missing word of this poster. The final institution word after `Production` is completely hidden; `Office` is plausible but **not verified**. Keep that uncertainty in reconstruction notes rather than claiming exact transcription.

Line 3, visible transcription:
`Sound Track distributed by Front Row Productions, Box 4486, Vancouver, B.C. V6B 3Z8, Canada · Film, Poster and Sound [hidden]buted by International Media Distribution, Inc., 824 N. Victory Blvd., Burbank, CA 915[hidden]`

Likely middle expansion: `Sound Track distributed`. ZIP `91502` is consistent with the street address, but the final characters and any country abbreviation are magnet-occluded in the poster. A later industry directory independently puts Eagle Eye Film Company at 824 N. Victory Blvd., Burbank, CA 91502; it does not prove this poster's punctuation or final country wording.

Printing line (small uppercase): `POSTER PRINTED IN BRITISH COLUMBIA BY MITCHELL PRESS.`
Copyright line: `© 1986 International Media Distribution, Inc.`

## Practical decisions

All major credit names/roles can be restored faithfully. Exact final words of two fine-print lines remain unavailable because both main and detail photographs retain an opaque magnet. A clean visual reconstruction can use clearly documented editorial expansions while retaining the observed transcription in metadata. A separate literal transcription should preserve the gaps.
