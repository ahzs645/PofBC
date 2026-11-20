# Prevent Forest Fires oval: finalized vector reconstruction

Finalized 20 November 2026 from the supplied photograph.

## Included files

| File | Use |
|---|---|
| forest-fire-sign.svg | Primary full-colour editable vector, transparent outside the oval |
| forest-fire-sign.pdf | One-page vector export for print or placement |
| forest-fire-sign-lettering-only.svg | Black lettering on a transparent background, without the oval |
| README.md | Reconstruction details and editing notes (the package's `forest-fire-sign-notes.md`) |

## What is finalized

The artwork uses a 1440 × 880 canvas, 129 individual letter/punctuation paths,
and a completed symmetrical oval. Ten named layers organize the full-colour SVG;
the lettering-only SVG has nine. The original photograph clips a little of the
left edge, so the oval is completed from the visible boundary.

The large display letters and the bold supporting lettering are custom outlines.
All 23 letters in WHEN IN THE WOODS and DO NOT DROP were rebuilt to reflect the
source more closely, including the pointed W, curved R tail, broad T, shortened
E middle bars and H crossbars. The three upper R counters were also refined.
The distinctive display forms, curved lines, spacing, small CAMPFIRES A counter
and footer punctuation are retained.

The fine attribution line uses fitted Nimbus Sans Regular outlines as its
starting point. This is a reconstruction choice, not an identification of the
historical font. Earlier Albertus and Gill Sans specimen comparisons showed
family resemblances but did not establish an exact match. No font files are
required to use the final artwork.

All letterforms are closed editable paths. The final drawing contains no
embedded photographs, raster effects or live text. Letter shapes and colours
can be edited; the wording is not keyboard-editable as a text box.

## Perspective and layout

A single shared projective correction was inferred from the long strokes of
the main PUT / OUT lettering, followed by a small deskew and recentring. It is
applied consistently to every letter. The corrected visible rim supports a
clean ellipse centred at (720, 440), with radii 711 and 426 artwork units.

The existing reconstructed Bézier curves were transformed directly, with the
result represented as editable cubic paths. The final outlines were not made
by automatically tracing the photographic pixels. Approximation of the
projectively transformed curves used a 0.006-artwork-unit tolerance; this
describes computational curve approximation, not reconstruction accuracy.

The correction is an estimate based on one photograph. Original physical
dimensions, global foreshortening and camera calibration cannot be recovered
uniquely from it. The oval has not been forced into a circle. The completed
artwork represents a clean, plausible face-on reconstruction.

The package's comparison image (not kept here) projected the final corrected
vector back into the photograph's camera view. Its cyan contours provided a
registration check without confusing the estimated face-on layout with the
photographed perspective. It was a reconstruction comparison, not an
independent font-identification test.

## Wording

```text
PREVENT FOREST FIRES
WHEN IN THE WOODS
PUT YOUR CAMPFIRES OUT
DO NOT DROP
LIGHTED MATCHES OR TOBACCO
PRESENTED BY FOREST BRANCH. LANDS DEPT. VICTORIA B.C.
```

The period after BRANCH and the final B.C. dot are faint in the source. The tiny
pale mark inside the A of CAMPFIRES is retained as a small triangular opening.

## Palette

| Element | sRGB colour |
|---|---|
| Yellow oval | #E4D02B |
| Main lettering | #851820 |
| Lighter attribution | #A36C23 |

These colours reconstruct the appearance of the supplied photograph. They are
not measured original ink colours or Pantone matches. The lighter footer colour
preserves its visible appearance. The lettering-only SVG uses black throughout.

## Editing and output

Open the main SVG in a vector editor. Named layers separate the oval and each
line or main word. Change a layer's fill to recolour that part; edit individual
letters using the node tool. The lettering-only SVG offers a single-colour
version without the oval.

The SVG and PDF can be resized without losing vector sharpness. No original
physical size was supplied. The PDF page is 1080 × 660 points, nominally
15 × 9 1/6 inches. Set the intended finished dimensions in the print or layout
application. Print-specific colour conversion or bleed can be set for the intended
production method.

## Verification

- Final artwork, fine lettering and PDF rendering visually inspected.
- Complete wording and all counters retained.
- 129 glyph/punctuation paths; unique element IDs; all subpaths closed.
- No live text, embedded image elements or external resource dependencies.
- All lettering lies within the completed oval.
- PDF contains one page and vector drawing operations, with no image or font resources.
- Final cyan overlay registered back to the supplied photograph.

## In this repository

Kept as supplied: `forest-fire-sign.svg`, `forest-fire-sign-lettering-only.svg` and
`forest-fire-sign.pdf`, with these notes as this README. Left out: `forest-fire-sign.png` (a raster
copy) and `forest-fire-sign-comparison.png` (it carries the photograph).

The Pins view (`?view=pins&pin=forest-branch-campfires`) shows `forest-fire-sign.svg` as
`src/pins/forest-branch/forest-branch-campfires.svg`: its ids prefixed `fbc-`, its title reworded
without the dash, the dashes in its layer labels replaced, and its `<metadata>` block dropped, since
that names the photograph's file. The paths are unchanged. The site reads the object as a glossy
celluloid giveaway whose back is not shown: a pin-back button or possibly a pocket whetstone.

