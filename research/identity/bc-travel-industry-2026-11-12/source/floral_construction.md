# Revised dogwood illustration

Fresh hand-authored vector geometry based on the newer screenshot. It does not reuse the earlier floral paths.

`floral.svg` has a transparent background and the original master coordinate system, viewBox 0 0 644 468. Import its group `dogwood-illustration`. Geometry was drawn in screenshot coordinates, with the transform translate(-32.3152107514 141.1728772144) scale(0.6108735492).

The two smooth white blossoms, five leaves, merged orange branch silhouette, packed round yellow florets, pointed petal rays and branching pointed leaf veins are independent vector paths in named groups. There are 116 path objects and no embedded bitmaps, fonts, or external assets.

Veins are filled tapered paths, not uniform strokes. The middle leaf sits in front of the right blossom, naturally producing the reference overlap. Branch outlines are merged at main junctions and the orange left-to-main band was widened to preserve its visible fill.

Palette uses sampled source colours: petal #FDFDFB, leaf #88B96D, stem #C95632, gold #F2D532, main contour #111711. Small details were deliberately rebuilt as clean artwork rather than copying screenshot antialiasing or texture.

`build_floral.py` reproduces the illustration and screenshot-space preview. `floral-comparison.png` compares the supplied screenshot crop with the reconstruction at identical scale.

Final reference refinements: 19 individually drawn floret cells per blossom; overall clusters approximately 40px left / 38px right in screenshot coordinates; contours 4px, branch contour 3px, floret contour 0.85px before cluster scaling. Left-to-main orange band is visibly retained. Petal ray fill #53554E, leaf vein fill #20301F, floret outline/base #302D15.
