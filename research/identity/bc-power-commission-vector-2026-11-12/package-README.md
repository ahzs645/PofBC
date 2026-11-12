# BC Power Commission emblem - rebuilt vector

Reconstructed from the supplied **BC Power Commission Emblem(1).png**.

The artwork is rebuilt from geometric components: a sunburst with deliberately
placed corners, a white plaque with two smooth Bezier arch segments, a straight
frame, and seventeen custom letter outlines. The SVG does not depend on a font
or a raster image. No automatic contour tracing was used.

## Files

- **BC_Power_Commission_Rebuilt.svg** - editable vector master, with five named layers.
- **BC_Power_Commission_Rebuilt.pdf** - vector export for print and placement.
- **BC_Power_Commission_Preview.png** - 2896 x 2172 transparent PNG rendering.
- **BC_Power_Commission_Comparison.png** - supplied image and reconstruction side by side.
- **rebuild_emblem.py** - the geometric construction source; uses only the Python standard library.

## Editing the master

The five named layers are Sunburst; White plaque and border; BC initials;
POWER lettering; and COMMISSION lettering. Each letter is a separate editable
path. The B, P, O and R counters are openings in compound paths.

The page is 1448 x 1086 units, matching the supplied reference. The area outside
the emblem is transparent; the plaque inside the black border remains white.
The small left/right differences in the sunburst and arch are retained.

Sunburst tips are subtly rounded, while the inward notches remain angular.
The sunburst, arch and frame keep editable strokes. If a particular production
process requires all strokes expanded to filled paths, expand them in the
destination vector editor after setting the final scale.

## Flat palette

These are visual approximations of the supplied image's colours, with its
texture and tonal variation removed.

| Element | sRGB hex |
| --- | --- |
| Sunburst | `#FFD800` |
| BC initials | `#E60010` |
| POWER / COMMISSION | `#011842` |
| Plaque | `#FFFFFF` |
| Outlines | `#000000` |

## Construction and checks

The master contains 22 vector paths in five layers, including a sparse path
that preserves pointed sunburst notches. It has no embedded images, linked
assets or live text. The PDF contains no raster image objects.

The master was rendered and compared with the supplied image. Letter counters,
spacing, arch curvature, the arch/frame joins and transparency were checked.
The PDF was rendered separately to check that the vector export preserves the
artwork.

To regenerate the SVG, run `python3 rebuild_emblem.py` in this folder.
This writes the master SVG next to the script. The script does not read or
trace the reference image.
