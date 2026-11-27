# PofBC project instructions

## Gallery artwork

- Prefer verified source vector artwork for collection covers and default logo previews at `/dev/data?view=gallery`. Before using a raster, check the entry's source versions, the local artwork holdings, and the cited brand kits or publications for a matching vector.
- Verify that the vector preserves the same symbol, lettering, layout, and historical treatment. Use the matching source colourway on the light gallery and the project's display pipeline for a legible dark-theme copy. Keep separately documented colourways selectable.
- When a matching vector is held, make it the default preview and download for that design. Use `preferredVector` to select a verified `variantOf` asset while keeping the existing design ID and raster source. Record the vector's publisher, source URL, page or file locator, and extraction or conversion method.
- For PDF or EPS artwork, preserve the native paths when making a browser-ready SVG. Verify that the logo itself contains vector geometry. An SVG that embeds a bitmap is still bitmap-containing artwork. Keep reconstructions identified as reconstructions.
- When no matching source vector is verified, show the best documented raster and record the open lead where applicable. Keep different layouts and historical designs as separate entries.
- Generate display copies with `scripts/build_collected_display.py` and verify the actual gallery card, mark details, and downloads in light and dark mode.

## Logo dates

- Date a design by its adoption only from a cited record of the adoption: a council or board decision, a guide or report that records one, or the body's own announcement of the new logo. The record must give an exact day and a source link, and goes on the file as `adoption: { date, note, source: { title, url } }` (announcements from school districts use `adoptionDate`, `adoptionDatePrecision: 'announcement'` and `adoptionSource`). The gallery shows it as "Adopted" or "Announced" and dates the design by it; `adoptionOf` in `src/gallery/collectedCollections.js` is the only reader.
- Everything else is a sighting: a publication that shows the logo, a website capture, a file's metadata or upload date, or a year in a file name. A sighting dates its file ("Seen 2013"), never the design's adoption. A year or month without a day is not an adoption record; keep it in `dateNote`.
