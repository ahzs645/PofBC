# British Columbia arms: five refined vector editions

Prepared for Ahmad Jalil, 21 November 2026.

This package contains five refined drawings from the supplied collection. The
latest correction cycle focuses on the first two, 1895 followed by 1956, with
repeated source, overlay and authored-geometry review passes. It preserves the
different renditions, records the source search, and provides visible
before-and-after comparisons for each.
The SVGs remain constructed artwork: manually authored curves, editable fills,
geometric components and outlined lettering. They contain no traced bitmap
contours and no embedded reference image.

## Start here

- `deliverables/BC_Arms_First_Two_Recursive_Review.pdf`: focused review of the
  additional 1895 and 1956 correction passes, compared with the previous
  delivered SVGs. The matching `BC_Arms_1895_Recursive_Comparison.png` and
  `BC_Arms_1956_Recursive_Comparison.png` provide convenient whole-art views.
- `deliverables/BC_Arms_Overlap_Analysis.pdf`: illustrated comparison report,
  including whole drawings, component crops, and the recovered 1960 source.
- `deliverables/BC_Arms_Interactive_Overlay_Review.html`: self-contained viewer.
  Download and open it in a browser. No external scripts or image downloads are
  required.
- `deliverables/BC_Arms_All_Five_Refined_Vectors.pdf`: one vector-art page per
  edition, without the analytical reference panels.
- `deliverables/svg/`: the five editable SVGs.
- `deliverables/pdf/`: individual vector PDFs.
- `deliverables/previews/`: large transparent PNG previews.
- `revised/editions/`: edition-specific construction scripts, source notes,
  diagnostic data and additional comparisons.

The supplied source images and uploaded SVGs are retained in
`source_package/BC_Arms_Vector_Editions/` so the original state remains
recoverable and the comparisons can be rebuilt.

The archive also retains the original construction scripts and README for
context. Its earlier bulky review exports are superseded by this review and
are not duplicated. `VALIDATION.md` records the checks performed, and
`CHECKSUMS.json` records each packaged file's SHA-256 digest.

## The drawings and their dates

| Edition | What the date identifies |
| --- | --- |
| 1895 Beanlands | Adoption of the design; the reproduced engraving is itself undated. The sun and waves remain above the Union Flag. |
| 1956 Empire Day | Publication of the colour plate, not a new grant of arms. |
| 1960 Museum report | The report year; the printing imprint is 1961. The cover and title page repeat the distinctive engraving with long forked ribbon tails. |
| 1987/88 Ministry report | A contemporary colour painting of the completed 1987 arms. |
| 1990 Register | The Canadian Heraldic Authority registration date, 17 April 1990. This is a different painted rendition of the 1987 design. |

The B.C. government history identifies the main design stages as 1895, 1906 and
1987. Publication and registration dates should therefore not be presented as
five successive official redesigns.

## What the source search found

### 1895: apparent enlargements were not new evidence

The supplied reference is only 257 × 190 pixels. A promising reproduction in
*The Blazon*, Winter 2012, PDF page 2, Fig. 3, embeds exactly the same RGB image.
Its larger placement in a PDF does not create more detail. Hubert Herald also
uses a small original and an enlarged display derivative. A large stained-glass
photograph and a modern Wikimedia SVG are different renditions, so neither was
substituted for the engraving.

Four additional correction passes rebuilt the ram's face and horn opening,
raised its tail, narrowed the haunch, corrected elbows and cloven hooves,
restored dark ribbon turns, reset the compact motto, rebalanced the engraved
shield and refined the crown and lion. Overlay review also reversed trial
changes that made the diagonal bands too heavy or the stag's thigh cuts too
wide. The small source still limits facial marks, fur, ornament and exact
letterforms; narrow horn-opening and some crest diagnostics remain mixed.

### 1956: the original scan was recovered

The Internet Archive JP2 master was recovered for *Empire Day* (1956). The
relevant emblem crop contains about the same 1030 × 1020 native pixels as the
supplied crop. This is useful source provenance and detail evidence, but it is
not described as a higher-resolution recovery.

The additional reconstruction restores the stag's antler opening and ram's
ear, corrects horn relief and supporter anatomy, rebuilds ribbon folds without
the false straight bridge above SINE, and resets each outlined motto letter.
The crown and lion have separately authored ornaments, arches, jewels, paws,
legs, mane and facial details. Source-supported wave and sun-ray differences
are retained. The colour plate's halftone dots and paper texture are not
converted into arbitrary vector noise. Component and full-art pass records
show both retained corrections and local regressions that required rework.

### 1960: a better impression of the engraving was found

The University of Toronto Thomas Fisher Library scan of the Museum report,
available through Internet Archive as `report1960brit`, has a 305 × 255 cover
crop and a cleaner 310 × 300 title-page crop. These improve on the supplied
230 × 205 crop. The clearer black impression reveals the curved ornaments and
scalloped front of the crown, and clarifies the sun and other engraved forms.

The independent title-page impression is registered using only the two source
rasters. The same resulting scale, rotation and translation are applied to both
vector versions. This prevents the improved vector from receiving a more
favourable alignment than the uploaded version. Registration data is retained
with the edition.

### 1987 and 1990: preserve the identity of the paintings

No larger exact copy of either painting was verified. The supplied report crop
is 1300 × 1515 pixels; the registered painting is 490 × 548 pixels. The
candidate full-size registry image could not be retrieved, and no claim about
its unseen resolution is made.

A Legislature fact-sheet illustration was inspected at 1189 × 1354 pixels,
but its lettering, antlers and other details belong to a different rendition.
It was not used to replace either painting. A smaller, cleaner reproduction of
the 1987 painting in *The Blazon* supplies useful supporting evidence without
being labelled a resolution upgrade.

The modern revisions address the six-bract dogwoods, branch and leaf layouts,
straight and flame-shaped sun rays, antlers, helmet bars, wreath, mantling and
selected animal contours. The two paintings retain their own colour and form.
Their irregular painted modelling remains more complex than the constructed
vector geometry.

## Using the interactive review

Choose an edition, then select one of the comparison modes:

1. **Reference · previous delivery · latest** compares the additional 1895 and
   1956 refinements with the versions delivered before the user's latest
   review. This is the default opening view. Its saved SVG snapshots use the
   same coordinates and are available in the overlay and wipe controls too.
2. **Reference · uploaded · refined** places the original uploaded vectors and
   latest revisions in matching coordinates for all five editions.
3. **Cyan / magenta overlap** shows source ink in cyan and the selected vector
   revision in magenta. Change the vector revision to compare the original and
   revised fits without moving the reference.
4. **Source / vector wipe** reveals the reference and vector through an
   adjustable dividing line.
5. **Vector artwork** displays the actual SVG, which remains sharp when zoomed.
6. **Recovered source evidence** is enabled where additional source material
   is included. For 1960 it provides a registered comparison against the newly
   recovered title-page impression.

The **Detail** selector gives matching crops of the crown, supporters,
lettering, rays or flowers. Zoom enlarges the display; it does not improve the
native source evidence. Use the download button to save the selected refined
SVG directly from the viewer.

## What the overlap analysis measures

The central comparisons retain the original SVG coordinate frames. Both
revisions receive the same uniform display scale. No changed ink-bounding-box
fit, horizontal stretch or local component warp is used. The supporting 1960
comparison has a separately documented whole-image similarity registration.

The cyan/magenta layers are analytical visualizations of ink density. They are
not artwork assets. Colour, paper, halftone and painted shading affect an ink
comparison, so a close silhouette or high intersection score is not an overall
accuracy percentage. The per-edition diagnostic files state their own masks,
regions and limitations. Measurements from different masks or sources should
not be combined into one quality ranking.

The remaining differences are intentionally visible. Some can be improved by
further authored geometry; others require better archival originals. The
package does not claim that unavailable fine detail has been recovered.

## Editing and reproduction

Open the SVG files in Inkscape, Illustrator, Affinity Designer or another SVG
editor. Artwork components are grouped. Intended white regions inside the
animals, flowers, shields and ribbons remain white; the surrounding page is
transparent. The motto is vector geometry rather than live text, so no
installed font is needed to display it. No historical typeface attribution is
asserted where the source does not establish one.

Each edition includes its build/refinement script. Follow its README to rebuild
that edition. To rebuild the central comparison report and viewer from the
package root:

```sh
python3 work/build_comparison.py
python3 work/recursive_refinement/build_focused_review.py
```

The focused builder verifies that its canonical diagnostic records match the
previous-delivery and final SVG hashes. Recorded intermediate passes and
their fixed-coordinate comparison images are retained under
`work/recursive_refinement/`. The per-edition histories identify corrections
that were retained and trial changes that were revised or rejected.

The review builder requires Inkscape, Python 3, Pillow, NumPy, PyMuPDF and
ReportLab. Some edition-specific builders and analytical scripts additionally
use lxml and SciPy. The central builder expects DejaVu Sans, Sans Bold, Serif,
and Serif Bold in `/usr/share/fonts/truetype/dejavu/`; on another operating
system, point `FONT_DIR` in `work/build_comparison.py` and `FONT` in
`work/recursive_refinement/build_focused_review.py` at the installed DejaVu
font directory. These fonts affect the review pages, not the outlined artwork.
The build uses locally supplied references and authored geometry; it does not
need an image tracing service or remote rendering system.

## Saved passes and replay

The saved pass SVGs can be opened directly. Normal rebuilding uses the complete
builders in `revised/editions/`, alongside their source references and helper
modules. The 1956 final builder reads its preserved `svg/` baseline and applies
four component helpers.

The 1956 numbered pass folders preserve the exact rebuild and helper snapshots
used at that stage. To replay one, copy its `rebuild.py` and component modules
to a new working folder and provide the immutable baseline at
`svg/BC_Arms_1956_Empire_Day.svg`, copied from `revised/editions/1956/svg/`.
The earlier `previous_delivery/rebuild.py` instead requires the packaged
`base_geometry.py` beside it. These replay dependencies are supplied once in
the edition folder rather than duplicated in every pass folder.

Scripts named `apply_pass03.py`, `apply_pass02_edits.py`,
`apply_pass03_edits.py` and `refine_lettering_pass02.py` are one-time historical
edit records. They assume the former workspace layout and a specific earlier
builder state. They are unnecessary for normal rebuilding; use the complete
final builders or saved pass snapshots for that purpose.

## Principal sources

- B.C. government's coat-of-arms history:
  https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms
- Ontario Department of Education, *Empire Day*, 1956:
  https://archive.org/details/empireday195600onta
- Provincial Museum report for 1960, Thomas Fisher Library scan:
  https://archive.org/details/report1960brit
- Museum's report PDF:
  https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1960.pdf
- Ministry annual report, 1987/88, PDF page 8:
  https://rbcm.ca/wp-content/uploads/2025/07/bca_annual_report_1987_88.pdf#page=8
- Canadian Heraldic Authority, Province of British Columbia:
  https://www.gg.ca/en/heraldry/public-register/project/1406
- *The Blazon*, Winter 2012, figures 3 and 6:
  https://bc-yukon.heraldry.ca/archives/blazon/issues/Blazon-2012-2-Winter.pdf

Additional exact image URLs, native dimensions, extraction details and
rejected alternatives are recorded in the edition-specific source notes.

## Measured limits of the revision

The modern editions' crest ink-overlap diagnostic decreased: 0.734 to 0.723
for 1987 and 0.697 to 0.676 for 1990. Antler, sun and flower regions improved
under the same fixed-registration masks. The crest changes therefore are not
claimed as an across-the-board fidelity improvement. The full results,
including those regressions, appear on the report's final page and in each
modern edition's `review.json`. These are regional diagnostics, not overall
accuracy percentages.
