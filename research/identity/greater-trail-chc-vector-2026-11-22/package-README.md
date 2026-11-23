# Greater Trail Community Health Council — revised vector reconstruction

Revision 2, 22 November 2026. Replaces the earlier reconstruction.

## Main deliverables

- **Greater-Trail-CHC-Reconstructed.svg**: editable, transparent vector master. All lettering is outlined. The source positions and baseline differences are retained.
- **Greater-Trail-CHC-Reconstructed.pdf**: one-page pure-vector artwork.
- **Greater-Trail-CHC-Review.pdf**: four-page reference, typography and exact-master overlay review.
- **Greater-Trail-CHC-Preview.png**: white-background preview.
- **Greater-Trail-CHC-Transparent.png**: 4280 × 2080 transparent convenience export.
- **Greater-Trail-CHC-Source-Aligned.svg**: the identical artwork on the screenshot's 1166 × 488 canvas. Only the outer canvas differs from the master.
- **Greater-Trail-CHC-Symbol.svg**: separately editable reconstructed symbol.
- **Greater-Trail-CHC-Council-Detail.png**: source, refined COUNCIL and exact-master overlay.
- **Greater-Trail-CHC-Comparison.png** and **Greater-Trail-CHC-Overlay.png**: visual comparisons of the replacement artwork.

## What changed

The previous Bookman/Garamond caption approximation is replaced with Albertus-derived outlines. Shared edits refine the C terminals, O counter, U foot, N upright and L foot. The large name uses deliberately reconstructed reusable serif capitals, including revised A/R counters and R tails. The source word placements are restored. The lower-left outer oval and sloped underline are also refined.

The symbol is built from three analytic oval heads, three body paths and three independent oval bands. It remains a geometric construction with deliberate curve controls. No automatic raster tracing or extraction of bitmap contour nodes was used.

## Typeface finding

**Albertus is the strongest tested visual basis for the caption.** The labelled Albertus specimen in Epson's Adobe PostScript 3 manual (page 195) supplied genuine vector geometry for comparison: https://download.epson-europe.com/pub/download/271/epson27082eu.pdf

This is a visual reconstruction decision. It does not confirm the council's historical typeface or exact weight. The resulting caption outlines are customized. The large name is labelled **custom reconstructed serif capitals; historical font unconfirmed**. All delivery files are font-independent.

## Exact-master overlap

| Region | Previous delivered | Previous source-aligned | Replacement |
| --- | ---: | ---: | ---: |
| Full logo | 81.8% | 86.2% | 90.3% |
| Symbol | 94.1% | 94.1% | 94.4% |
| GREATER | 59.6% | 60.6% | 82.1% |
| TRAIL | 44.4% | 69.9% | 84.2% |
| COMMUNITY | 66.7% | 71.6% | 78.3% |
| HEALTH | 66.4% | 72.4% | 77.5% |
| COUNCIL | 46.8% | 70.4% | 78.0% |
| Underline | 54.2% | 80.6% | 82.2% |

All values were recomputed using the same Inkscape renderer, source-resolution canvas and fixed regions. For the master audit, only the outer canvas changes; artwork paths and placement remain untouched. The previous source-aligned column isolates much of the effect of the old master's baseline normalization.

These are foreground IoU diagnostics (shared black area / combined black area), not percentages of historical accuracy or proof of font identity. The source is small and blurred. The reconstruction deliberately avoids converting its scan noise into vector detail.

## Reference and editing

The supplied screenshot is the primary target. The linked gallery's preserved GIF has a different caption and thinner oval bands. It was used to corroborate the motif, not override the screenshot. See source/source-evidence.md.

Open the SVG in a vector editor. The symbol components and letter paths remain editable. The source folder includes the supplied reference, editable component fragments, source notes, before/after audit and a font-independent Python assembly script. Running source/rebuild.py creates an artwork-equivalent SVG from the fragments. Full font files and alphabet masters are not bundled.

This is a reconstructed vector, not a recovered historical original. No historical colour treatment, designer or adoption date is asserted.
