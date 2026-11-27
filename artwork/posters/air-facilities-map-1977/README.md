# Air Facilities Map — 1977/78

Modern mixed-media reconstruction of the British Columbia Aviation Council map cover. The historical source is the user-supplied eBay photograph `source/historical-cover.webp`; the clean aircraft/mountain scene is the user-supplied Gemini-generated JPEG, not an original photograph. The front cover visibly reads 1977/78. Maureen Wilson's bibliography in *BC Studies* 41 (Spring 1979), p. 113, records publication in Vancouver in 1977 by the British Columbia Aviation Council and map scale 1:1,900,800. The reverse link supplied by the user was not independently retrieved. Neither original designer nor photographer nor precise physical cover dimensions have been established. The interior map is out of scope.

## Reconstruction

- Photograph rectified using four corner correspondences in a 1000 × 1500 working canvas (estimated aspect ratio). The cover's paper and ink colours are interpretive rather than measured historical swatches. The modern scene is stretched to fit the measured picture panel; the landscape and aircraft vary from the photographed original.
- `source/build.py` constructs the large wordmark from separately authored cubic paths, not bitmap tracing. The title uses URW Bookman Demi with two keyline strokes; the tagline uses URW Bookman Light with an optical weight adjustment; the date uses Nimbus Sans Bold. The title/wordmark have features suggestive of ITC Souvenir, but the original typeface is unconfirmed. No fonts are distributed.
- `poster.svg`: self-contained, high-quality editable master; one embedded raster scene, no live text. the runtime folder’s `poster.svg` is the lower-bandwidth copy; `poster.pdf`: vector lettering and raster photograph, nominal 10 × 15 inch working size. `wordmark.svg`: standalone dark vector wordmark, no photograph. `comparison.jpg` and `overlay.jpg`: visual registration checks, not archival facsimiles.
- The gallery’s runtime drawing, thumbnail, reference photograph and parts are in `src/posters/air-facilities-map-1977/`. Open the cover at `?view=posters&poster=air-facilities-map-1977`.

## Sources

- Front cover: https://i.ebayimg.com/images/g/NFQAAOSwSZlmYOzj/s-l1600.webp
- Reverse (unverified link): https://i.ebayimg.com/images/g/rjQAAOSw7nlmYOzl/s-l1600.webp
- Bibliography, p. 113: https://ojs.library.ubc.ca/index.php/bcstudies/article/download/1014/1052/4247#page=1
