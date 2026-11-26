# Revelstoke Bear Awareness Program — 1997 vector reconstruction

A historical recreation of the artwork in the two supplied PDFs. This is a reconstruction, not an official vector archive and not updated bear-safety guidance.

## Contents

- `svg/`: 27 individual self-contained SVG compositions — one window sign, two checklists, ten Times Review ads, twelve Unique placements (ten distinct designs plus two repeats), and two large campaign ads. All lettering is outlined. All backgrounds are vector shapes.
- `components/`: 10 standalone, reusable SVG marks, including the five-claw paw, walking bear, Friends of Mt. Revelstoke & Glacier crest, Columbia Basin signatures, BC Hydro and BC Environment wordmarks.
- `source/rebuild.py`: the reproducible vector artwork generator, with independent editable geometry, placement coordinates, typography and line breaks. Requires Python, fontTools, and locally installed Nimbus/URW, Noto and Lobster Two typefaces. Font files are not included; all exported SVGs are font-independent.
- `source/advertisement-copy.json`: transcribed campaign texts for editing/reuse.
- `manifest.json`: source page, placement, publication, date notes and dimensions for each composition.
- `qa/`: full artwork and component contact sheets, side-by-side comparison of the checklists and all 22 small advertisement placements, and a measured window sign overlay.

## Reconstruction decisions

1. The window-sign oval is a clean ellipse. The W is built from interlocking contrasting V shapes, the A has a wedge crossbar, and the E is constructed as a reusable serif master; B/R use independently resized font outlines. The paw/claws are manually designed cubic curves rather than bitmap contour extraction.
2. The walking bear and sponsor marks are hand-constructed from visual references. The crest trees, landscape, ram/fish and mountain, and typography are simplified approximations; they are not authenticated original vector artwork. The historic typefaces are not conclusively identified. The source scan is monochrome, so no undocumented original colours have been invented.
3. The Times Review and Unique use separate layout templates. The Times Review line breaks are reconstructed from the visible scans; Unique uses reflowed text, and clipped right-hand text is recovered from the corresponding intact Times Review edition where possible. The two repeated Unique placements are kept and dated separately. The source has some uncertain/faint date annotations, marked in the manifest.
4. The large campaign ad was rebuilt in both newspaper styles. The Times Review's original halftone photograph was not converted into vector art; the SVG contains a clearly labelled placeholder. The cropped material is supplemented using the other edition, and the small checklist illustrations are interpreted line-art recreations. No attempt was made to recreate the full newspaper articles, radio scripts, administrative documents, or the children's winning posters, which are mentioned but not reproduced in the supplied report.
5. Historical wording and phone numbers are retained for archival purposes; do not use them as current guidance or contact details. Some publication-specific punctuation, line breaks, and emphasis may differ. Print dimensions are normalized SVG units, not verified physical dimensions.

## Quality assurance

Every SVG was parsed as XML and rendered using CairoSVG. No `<image>`, `<foreignObject>` or `<text>` elements occur in the SVGs. This verifies that no bitmap content or font dependency is embedded in the vector artwork. The generator and text file preserve editability for future layout revisions; SVG glyph outlines are editable as paths, not live text.

For the window sign, the source scan and reconstruction were normalized to the same 764 x 1000 canvas. Dark ink was thresholded at grayscale 145 and compared with intersection-over-union (IoU = shared dark area / union of dark area). This measures geometrical ink overlap, not semantic accuracy or overall quality. Small registration errors affect the metric. Cyan in the overlay = original-only ink; magenta = reconstruction-only ink; dark = overlap. Results: main oval/sign artwork 80.24%, paw 91.13%, lettering 65.69%, sponsor area 49.25%, overall 74.18%. The initial main sign overlap was 77.78% and lettering 60.46%; subsequent passes rebuilt the serif forms. The standalone components and remaining layouts were visually compared, not assigned a numeric accuracy score.

The PNG comparison and contact sheets are reference/QA materials only. They are not part of the SVG art.

## PofBC source record

The B.C. Ecological Reports Catalogue holds Debby Robinson’s November 1997 final report (report 40226). The archived full report and the supplied eight-page selection are in `source/`. The selection’s pages 1–8 correspond to PDF pages 27–29, 34–36 and 47–48 in the full report. The large advertisements are on PDF pages 33 and 46.

Run `python3 artwork/initiatives/bear-aware-1997/source/extract_scans.py` from the repository with Pillow and Poppler installed to regenerate the public scan crops and their page manifest. Crops retain the surviving print, including text cut off by the scan. PDF page 46 is rotated to read upright. The recovered artwork in the report is raster. Original campaign production artwork remains a lead for the Revelstoke Bear Aware Society or Revelstoke Museum & Archives.

- [EcoCat report record](https://a100.gov.bc.ca/pub/acat/public/viewReport.do?reportId=40226)
- [1997 Final Report](https://a100.gov.bc.ca/pub/acat/documents/r40226/Rev_Bear_Aware_1997_1385746991273_5746493974.pdf)
