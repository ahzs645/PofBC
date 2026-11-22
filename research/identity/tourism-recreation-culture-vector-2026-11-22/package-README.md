# Tourism - Recreation and Culture

Recreated from the screenshot supplied in this conversation, using the existing
PofBC Super, Natural sign's vector flag component as the starting geometry.

## Main files

- BC_Tourism_Recreation_Culture.svg: transparent, straightened artwork master.
  There are 59 editable vector paths, including the outlined lettering. No fonts,
  raster images, linked assets, or external resources are required.
- BC_Tourism_Recreation_Culture.pdf: print copy of that same vector artwork.
  One page, 160 x 68.034 mm. Verified to contain no raster images.
- BC_Tourism_Recreation_Culture_Black.svg: one-colour black master.
- BC_Tourism_Recreation_Culture_Transparent.png: 2808 px transparent raster export.
- BC_Tourism_Recreation_Culture_Preview.png: white-background viewing copy.

## Comparison and editing

- BC_Tourism_Recreation_Culture_Source_Aligned.svg: reconstruction on the exact
  730 x 442 reference coordinate system, before baseline straightening.
- BC_Tourism_Recreation_Culture_Overlap_Analysis.png: reference, reconstruction,
  full overlay, enlarged flag overlay, and measured comparisons.
- BC_Tourism_Recreation_Culture_Overlap_Raw.png: full-size overlay without labels.
- BC_Tourism_Recreation_Culture_Interactive_Review.html: offline split-view slider,
  opacity overlay, colour-difference view, native SVG master, and measurements.
  Open this file in a web browser. Every visual asset is embedded.
- BC_Tourism_Recreation_Culture_Editable_Text.svg: alternative with individual
  editable text characters. Requires C059 Italic and Liberation Serif Italic.
  Its characters can be edited directly, although substitutions will affect the
  match. The small Tourism weight adjustment in the outlined master is not
  included in this live-text editing alternative.
- Overlap_Measurements.json: final reproducible metric definitions and results.
- Reconstruction_Data/: source path provenance and final placement/curve data.

## What was rebuilt

Eight existing flag paths were reused from PofBC, with their original Bezier
path definitions retained and individual affine placements fitted to the
reference. Three lower bands were rebuilt as continuous closed cubic curves,
with their long left extensions and wave joins adjusted for this particular
lockup. All three bands remain separate: the final sampled gap review found
no intersections, with minimum separations of approximately 3.07 and 1.56
reference pixels between adjacent bands.

The reference uses one blue-purple ink. The original coloured flag's gold sun
path was omitted, leaving the central area transparent. On the white reference
page, an omitted shape and a white knockout would look the same; the screenshot
alone cannot distinguish the original production method.

The wording is preserved:

Tourism
Recreation and Culture
HON. BILL REID, MINISTER

There is a full stop after HON and a comma after REID. There is no final full
stop after MINISTER.

## Lettering and colour

The original historical typeface cannot be confirmed from this small image.
C059 Italic supplied the main line's outline shapes; Liberation Serif Italic
supplied Tourism and the minister line. Spacing, proportions and optical
placement were adjusted to the screenshot. Tourism received a restrained
0.4-source-pixel same-colour outline weight adjustment. The final master
remains entirely vector.

The colour #3C40A0 is estimated from the screenshot, not an archival Pantone or
CMYK specification. Change the artwork group's fill and colour together when
recolouring the SVG, so Tourism's same-colour stroke changes too.

## Reading the overlap

Magenta means ink coverage present in the reference but absent in the vector.
Cyan means vector coverage outside the reference. Dark blue means shared ink.
The comparison uses the source-aligned SVG; the main master straightens each
text baseline and the long bands for use as clean artwork.

Silhouette intersection over union is calculated at a 50% ink threshold on
the 730 x 442 source grid. The SVG is rendered at 4x resolution and reduced to
that grid. The JSON also records 35% and 65% threshold checks. Distances are
symmetric Euclidean boundary distances, in source pixels. Low-resolution scan
blur and the estimated ink density affect these values. These are comparison
metrics, not percentages of historical authenticity.

- Flag and stripes: 95.0% silhouette overlap; 0.26 px mean edge distance.
- Flag detail: 88.8% silhouette overlap; 0.51 px mean edge distance.
- Tourism: 66.3% silhouette overlap; 0.57 px mean edge distance.
- Recreation and Culture: 62.6% silhouette overlap; 0.59 px mean edge distance.
- Minister line: 58.4% silhouette overlap; 0.43 px mean edge distance.

The typography is the main remaining uncertainty. Its lower silhouette overlap
reflects approximate letter shapes/weight as well as the small, blurred source.
The flag and stripes are a closer match, and the report gives the flag-only
result separately so the long simple bars do not conceal its residuals.

## Reused artwork provenance

Sign page:
https://projects.ahmadjalil.com/PofBC/?view=signs&sign=super-natural

Deployed sign SVG:
https://projects.ahmadjalil.com/PofBC/assets/super-natural-BsHkU2n2.svg

Flag component:
https://github.com/ahzs645/PofBC/blob/main/src/assets/flagMark.js

Original repository vector:
https://github.com/ahzs645/PofBC/blob/main/artwork/flag/spirit-of-bc-flag.svg

Verified flagMark.js Git blob:
50be0e64651e66809102f48e5491fecf7ea0cd3d

The twelve deployed sign path definitions were compared with flagMark.js and
all matched. This reconstruction retains eight of those definitions, replaces
three lower paths for the extended-stripe version, and omits the gold sun path.
