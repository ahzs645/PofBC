# Lettering reconstruction

The four lines were rebuilt using a custom set of hand-authored path outlines. No font file, bitmap embedding or automatic contour tracing is used. Letter placement and ink bounds were measured from the supplied 644 × 468 image; their geometry is deliberately drawn from reusable cubic Bézier and line constructions.

The design retains the source’s narrow proportions, subtly flared stems, thin crossbars, squared bowls, slight rightward shear toward the baseline, and original line and word placement. A small fill-matched outline strengthens the shapes at the original display size. Each of the 41 letters remains a separate path in one of four named line groups. The generator stores each reusable glyph as editable SVG path data.

The exact historical typeface has not been identified. These are reconstructed letterforms rather than a claim to use the original metal or phototype font. The small source is blurred and unevenly printed; the final curves interpret that evidence and remove print noise.

Files:
- lettering.svg: full-size, font-independent artwork with transparent canvas.
- rebuild_lettering.py: the geometric glyph definitions and placement source.
- ../bc_travel_industry_comparison.png: side-by-side source and reconstructed artwork.

Visual checks confirmed four line positions and the wording. The rendered lettering has exactly 41 separate glyph components, with no accidental joins between adjacent letters.
