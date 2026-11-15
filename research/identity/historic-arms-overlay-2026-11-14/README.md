# Historic arms: a measured reconstruction starting point

Reviewed **14 November 2026**. This provides the first reproducible, scale-matched comparison between the current provisional master and one named historical specimen. It also starts a **partial structural vector study** of that specimen. It does not replace the application renderer.

## Open the review material

- [Comparison and overlay](overlay-review.png) ([portable SVG](overlay-review.svg)).
- [Native source comparison](native-source-comparison.png): the selected 1960 cover beside the two separate 1954 mining specimens.
- [Partial structural study](structure-review.png) and its [editable SVG](museum-1960-structure.svg).
- [Overlay alone](aligned-overlay.svg), [registration and provenance](registration.json), and [measured results](measurements.json).

The review SVGs contain the identified reference raster where needed. They are review sheets, not exported logo artwork. The separate structural-study SVG contains manually constructed curves and no embedded reference image.

## Target choice and dating

The selected target remains **catalogue entry 14**, the arms on the cover of the [Provincial Museum report for 1960](https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1960.pdf#page=1), **printed in 1961**. The report's PDF page 36 supplies the 1961 imprint. The [museum's official annual report archive](https://rbcm.ca/corporate-information/reports-policies/annual-report-archive/) provides the report. The engraving's artist and creation date are not established.

The exact embedded cover JPEG is retained as [museum-report-1960-cover.jpg](reference/museum-report-1960-cover.jpg). It is **2179 x 3162 pixels**, but the arms themselves occupy only about **208 x 174 ink pixels**. The original JPEG was extracted without resampling. The [230 x 205 native crop](reference/museum-report-1960-native.png) is reproduced from coordinates recorded in `registration.json`.

The 1954 candidates were checked at their native embedded-image resolution, rather than from an enlarged PDF rendering:

| Source | Native full-page image | Approximate arms ink extent | Assessment |
| --- | --- | --- | --- |
| Museum report 1960, cover; printed 1961 | 2179 x 3162 | 208 x 174 | Best of these three for broad contour placement; light brown printing keeps some boundaries separated. |
| [Mining in British Columbia, 1954, cover](https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf#page=1) | 1473 x 2087 | 192 x 147 | A separate, broader drawing. Thick ink and grey paper merge small details. |
| [Mining in British Columbia, 1954, title page](https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf#page=2) | 1472 x 2092 | 173 x 146 | Similar broad domed-crown and long-scroll structure, but smaller and darker. An identical engraving is not established. |

All three native crops are shown at the same enlargement in the comparison sheet. Their different paper and ink tones require different measurement thresholds, which are recorded explicitly. The measurements describe the scan, not the physical print size or optical resolving power. A larger pixel count alone does not authenticate fine detail.

## What the overlay establishes

The candidate is frozen from application commit [`d3e4fbf`](https://github.com/ahzs645/PofBC/commit/d3e4fbf55538e3991179a9868496dcf2e28a68c5), using the `emblem` layout, black mark and zero clear space. Its geometry is the existing generated-master conversion shared with the 1919 cardboard plate. The candidate remains a **different, unauthenticated drawing**.

The comparison matches the two drawings' measured **full ink height** and aligns their ink-bounding-box centres. A single uniform scale and translation are used. There is no rotation, independent width adjustment, warping or fitting of separate parts. This is a common visual scale, not evidence that the original objects were printed at the same physical size.

At the selected threshold, the source ink is **208 x 174 pixels** and the aligned candidate is **154.69 x 174 pixels**. The candidate is therefore **about 26% narrower overall** at equal height. The source-threshold sensitivity check gives roughly **25.6% to 26.6%** narrower. This is a width comparison, **not an accuracy score**.

The broad differences visible in the aligned drawings are:

1. **Long forked scroll tails are absent from the current master.** Its short curled ends substantially reduce the full width. Stretching the entire current master to correct this would also distort its shield and animals.
2. **The lion and main crown occupy different shapes and proportions.** The crown arches, band spacing and relationship to the lion differ. They need source-specific reconstruction; changing an overall scale cannot reconcile them.
3. **The supporters, antlers and horns differ.** Their silhouettes and internal markings belong to different drawings. The source is sufficient to reject a line-for-line match, but insufficient to resolve every replacement contour.
4. **The shield interior and motto treatment differ.** Sun, rays, waves, scroll curvature and lettering need to be rebuilt as parts of the selected specimen. The current drawing's detailed hatching should not be treated as evidence for the older print.

The source is tinted cyan and the candidate magenta **only in analytical overlays**. The unchanged scan appears beside the overlay. Colour tinting is described in the registration file; it neither restores nor invents detail. No pixel similarity percentage is reported because the two drawings are different and the reference is small.

## What has been reconstructed so far

The [structural-study SVG](museum-1960-structure.svg) begins the selected specimen as a separate, editable study. It uses manually constructed Bezier curves and line segments for the **main crown envelope**, **visible shield sides**, and **motto-scroll structure with forked tails**. It uses neither automatic tracing nor animal parts from the generated master.

This is deliberately a partial scaffold. It establishes approximate locations and relationships that are visible in the source. It does not supply the lion, stag, ram, internal heraldic details, hatching or lettering, and its broad contours still require refinement against a better scan. It must not be offered as a finished coat of arms or substituted into production.

The Museum cover has no flanking government or blackletter heading. Selecting it as an arms target therefore does **not** resolve the original heading typefaces. The separate evidence for [OIC 1121/1978](../document-arms-2026-11-14/README.md) continues to establish the government heading on page 1 and blackletter map attachment on page 4. The map's creation date and the original grant's issue date remain unknown.

## Next source acquisition

The [focused acquisition pass](source-acquisition.md) records the additional
routes checked, access limits and identifying metadata for a source request.

Obtain a substantially clearer scan or reproduction master of **this particular engraving**, ideally the 1960 report cover or a demonstrably matching printing. Keep the 1954 cover, 1954 title page and different historical families separately identified. Similar composition is not proof of a shared block.

With a better source, continue the scaffold component by component, preserving meaningful gaps and crossings, then repeat the same-scale comparison. Do not infer eyes, faces, fur hatching or letter shapes from enlargement alone. The [Texas and Beddoe leads](../document-arms-2026-11-14/README.md#guides-and-archival-leads) remain acquisition leads; this work does not inspect their archival contents or contact an archive.

## Reproduction

From the repository root, with Python 3, Pillow, NumPy and PyMuPDF installed:

```sh
python research/identity/historic-arms-overlay-2026-11-14/build_overlay.py
```

The script verifies the pinned candidate and image hashes, reproduces all three crops pixel for pixel from native source images, measures the alignment and regenerates the four figures. The 1954 source PDF is already retained by the source-identification follow-up. The exact 1960 cover JPEG is retained here, so normal regeneration is offline and does not require the complete report PDF.

To additionally check the retained Museum JPEG against the original report, download the [official PDF](https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1960.pdf) and run:

```sh
python research/identity/historic-arms-overlay-2026-11-14/build_overlay.py --museum-pdf /path/to/annual_report_1960.pdf
```

The optional PDF must match the recorded SHA-256. Its extracted page image must match the retained JPEG byte for byte. Normal and extended verification produce the same deliverables. The candidate SVG is intentionally frozen, so a future application renderer change cannot silently change this historical comparison.

See [validation](validation.md) for the checks actually performed.
