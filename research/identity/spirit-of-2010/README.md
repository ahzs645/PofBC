# Spirit of 2010

The Province used this emblem ahead of the Vancouver 2010 Olympic and Paralympic Winter Games. Its 2004 resort strategy prints the square on its cover and describes “British Columbia. Be Here.” as an advertising campaign on PDF page 5. The wording is recorded separately from the emblem. The 2004 Business Summit presentation supplies an unframed lettering variant. The attribution, introduction date, typeface and horizontal square-plus-slogan arrangement remain unverified.

| Specimen | Evidence and acquisition |
| --- | --- |
| [2004 provincial resort strategy](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/natural-resource-use/all-seasons-resorts/actionplan.pdf#page=1) | PDF page 1, image object 171. Original 200 × 201 colour JPEG, extracted losslessly. Its cover also carries the provincial rising-sun signature. |
| [2004 Business Summit tourism presentation](https://digitalcollections.llbc.leg.bc.ca/handle/123456789/307832) | Legislative Library PDF page 2, title slide, image object 159. A native 400 × 375 pixel image in ICC-based colour, decoded as PNG. The slide adds the words “Business Summit” beside this image. |
| [2006 Playmaker’s Guide](https://publications.gc.ca/collections/collection_2023/isde-ised/iu4/Iu4-374-2006-eng.pdf#page=2) | PDF page 2, acknowledgements. Image object 3 contains a 2543 × 3245 monochrome scan. The native crop uses the half-open pixel rectangle (2055, 1916) to (2256, 2115). |
| Archived summit JPG | The supplied historic government JPG URL returned no capture from the Wayback availability service for May 2004. The three documents above provide independently accessible artwork. |

## Reconstruction

The working coordinates follow the 200 × 201 square-cover image. The rectangular frame, two rules and twelve letters and numerals are individually editable. The second I and the second zero repeat their partner’s geometry at their own placements. The open P bowl, R leg, italic f descender, curved diagonal of the 2, and thin tops and bottoms of both zeros are drawn as Bézier outlines. No font install is required. The ink colours approximate the JPEG interiors. Compression and the absence of a colour standard limit their precision.

[Editable SVG](../../../public/initiatives/spirit-of-2010/spirit-of-2010.svg) · [Full overlay figure](../../../public/initiatives/spirit-of-2010/overlay.png)

## Overlay measurements

Run `python research/identity/spirit-of-2010/compare.py` from the repository. The script renders the SVG using MuPDF at four times the original size and downsamples with Lanczos. The primary comparison uses the colour JPEG’s native pixel grid without a fitted transform. At each pixel the estimated ink strength is one minus the minimum RGB channel divided by 255. Both images use the same threshold. Intersection-over-union divides the count of shared ink pixels by the count marked as ink in either image.

| 2004 colour square | Ink threshold | Intersection-over-union |
| --- | ---: | ---: |
| Whole square | 40% | 92.6% |
| Whole square | 50% | 95.0% |
| Whole square | 60% | 88.9% |
| SPIRIT only, columns 17–183 and rows 26–66 | 50% | 93.6% |
| Italic of and rules, columns 17–183 and rows 70–105 | 50% | 86.2% |
| Numerals, columns 17–183 and rows 108–175 | 50% | 92.7% |

The border is sufficiently long for a one-pixel change at threshold to affect the overall result. The lettering scores expose the fit within the border. The source resolutions limit what can be inferred about subpixel details.

The 2006 check uses a separate one-bit scan. Registration maps the scan’s outer frame bounds (2, 2) to (199, 196) to the reconstructed frame bounds (1.60, 2.43) to (198.73, 198.60). Only translation and axis scaling are applied. The lettering is held fixed throughout. Raw foreground IoU is **70.7%**. In particular the light gold numeral appears as a coarse screen of black dots in this printing. Smoothing both binary masks with a Gaussian of standard deviation 0.85 scan pixels gives IoUs of 82.3%, 79.7% and 80.1% at density thresholds 18%, 25% and 32%. The published figure shows the raw comparisons.

## File fingerprints

SHA-256 digests for the source PDFs and held specimens follow.

| File | SHA-256 |
| --- | --- |
| Resort strategy PDF | `409f74b344ae7606ca31e6d282f0928ee5009b9382961df02e44086d429e6960` |
| Business Summit PDF with library cover | `c7a0cc051c44a6afe82456ce63739bfc839c54952900b2c897bd7f4867fd2d8a` |
| Playmaker PDF | `021f90249e94487639f51c780a29a086a7f4a54845dc69634b5ba078666444a7` |
| business-summit-2004.png | `bea5498b7e8d7a1be296f43b09f73fd052ad8dd2707d7cbb83ca77e225594180` |
| overlay.png | `4a94c758f9f1113c276595286a5d5091e2c84bfd07199a3de1e41de119f65488` |
| playmaker-2006.png | `8ef45d33211f46929e51f8fe5c5c887dd1ea2c21278cc5414f0843556ca8f8f5` |
| resort-strategy-2004.jpg | `4230e8dac70334154f11a4d0a95e9610603a51d3d7a831733efb7ea0ee3bdeab` |
| spirit-of-2010.svg | `3e4e2416bc1b15f03b345d9feaf1825be710bb8bf38899c7020fbabc562e234f` |
