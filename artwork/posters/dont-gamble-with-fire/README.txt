DON’T GAMBLE WITH FIRE — VECTOR RECONSTRUCTION
B. C. Forest Service badge

START HERE

Open dont-gamble-with-fire.svg for the editable vector master.
Use dont-gamble-with-fire.pdf or .eps for a vector layout/print workflow.
Use the PNG files only when raster artwork is appropriate.

CONTENTS

  dont-gamble-with-fire.svg
    Editable vector master with named groups/layers for the circular field,
    border, two dice, individual faces and pips, headline, “with”, “FIRE”,
    and curved caption. Contains 43 paths, 10 circles, and 12 ellipses.
    No embedded or linked bitmap. Each main letter is an editable shape.

  dont-gamble-with-fire.pdf
    One-page vector export. Checked: no raster image objects and no font
    dependencies. Resize for the desired print dimensions. RGB artwork;
    this is not a colour-managed, bleed-ready or PDF/X production file.

  dont-gamble-with-fire.eps
    Vector export for workflows that accept EPS.

  dont-gamble-with-fire-preview.png
    4000 × 4000 px PNG, transparent outside the circular badge.

  dont-gamble-with-fire-white.png
    2000 × 2000 px PNG with a white background.

  reference-comparison.png
    Side-by-side view of the supplied reference and rebuilt vector.
    This comparison image is a raster visual aid, not the vector master.

  source/rebuild_badge.py
    Reproducible vector construction source. Requirements: Python 3.10+,
    lxml, fonttools, and a locally installed DejaVu Sans Bold font for the
    small caption. No reference image is needed to regenerate the artwork.
    Run from source/:
      python rebuild_badge.py --output ../dont-gamble-with-fire.svg
    Supply --caption-font PATH when the default Linux font path differs.
    Edit BLUE and CREAM near the top of the script to recolour the artwork.
    The distributed SVG/PDF/EPS already contain outlines and do not need fonts.

  validation.json
    Structural validation results for the SVG, PDF, and transparent PNG.

RECONSTRUCTION NOTES

The main lettering was rebuilt using deliberately placed Bézier curves and
straight segments, not an automatic bitmap-tracing operation. The dice use
separate face shapes and elliptical or circular pips. The outer badge was
regularized to a true circle, with a consistent concentric border. Surface
wear, photographic texture, and edge debris were intentionally omitted.

The small curved caption uses individually positioned, outlined DejaVu Sans
Bold glyphs with separate circular periods. This is a substitute for the
exact historic caption typeface, not an identification of that typeface.

All lettering is outlined: edit its contours as vector shapes rather than
retyping it as live text. No font installation is required to display the
finished artwork. No font files are embedded or included in this package.

PALETTE

Deep blue:  #01375D
Warm cream: #F1D8AC

These colours are approximations based on the supplied image, not verified
historic ink specifications or spot-colour standards. Both colours can be
changed by selecting matching fills and strokes in a vector editor.

This is a clean reconstruction of the supplied image, not an official
historic artwork master. Minor lettering, spacing, and geometry details
are interpreted.
