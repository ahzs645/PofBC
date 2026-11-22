# Associated report emblems

Four production SVGs represent three additional documented designs: the later F&W emblem and its paired name-panel arrangement; the Parks dogwood/province shield; and the earlier departmental dogwood oval.

## Files

| File | Source | Qualification |
| --- | --- | --- |
| `06_Fish_Wildlife_Oval_1973.svg` | 1973 annual report, PDF22 / AA21 | Animal/fish silhouette and F/W letters rebuilt as manual curves. The ampersand uses close outlined Bookman lettering. |
| `07_Fish_Wildlife_Paired_Lockup_1973.svg` | Same page | The associated name panel is recreated with a fitted, outlined Bookman substitute. It is not an identification of the original serif typeface. |
| `08_Parks_Dogwood_Shield_1973.svg` | 1973 annual report, PDF80 / AA79 | Shield, simplified province shape, islands and five visible bracts rebuilt individually. Small caption lettering is approximate. |
| `09_Department_Dogwood_Oval_1970.svg` | 1970 annual report, PDF10 | Earlier, separate identity. Botanical linework is an interpreted reconstruction of the printed engraving, with conspicuous limitations in its hatching and small lettering. |

`Related_Emblems_Source_Vector_Overlay.png` shows each source, reconstruction and registered overlay at matching display dimensions. Cyan is source-only ink, magenta is reconstruction-only ink and dark is overlap. Because white letters are knockout holes in these designs, residual letter-shaped colours must be read in the opposite sense from positive black lettering.

`manifest.json` records source PDFs, public source URLs, page numbers, crop rectangles, dimensions and overlap measurements. The source crops were taken from 200 dpi page renders of the official monochrome reports; they are not claimed to add detail beyond the embedded scan. Crop coordinates are in those rendered-page pixels.

## Construction and editability

The production SVGs contain real compound path outlines with transparent holes. They have no raster image, live text, font dependency or SVG mask. Every master is1000 units high, retaining its own aspect ratio. The `*_construction.svg` versions retain individually drawn parts and vector knockout masks; edit those for component-level changes. The masks are resolved by exact curve boolean operations for the production files, not by raster tracing.

`build_related_emblems.py` and `flatten_knockouts.py` record the construction. Regeneration needs Python, Pillow, NumPy, CairoSVG, fontTools, lxml and skia-pathops, plus the named locally installed URW Nimbus/Bookman faces. Font software is not included in the deliverables. The bundled runtime dependency directory is an analysis environment, not a required distributable asset.

## Review and limits

After source comparison, the F&W fish was shortened to its observed extent, the paired-panel Branch line was moved up, the Parks frame and flower centre were corrected, and the earlier oval's curved heading was fitted to measured source letter positions. Current fixed-coordinate whole-ink intersection-over-union values are approximately0.870,0.788,0.705 and0.731 respectively. These scores include the frame and must not be described as percentages of historical accuracy.

The F&W graphic is the strongest of these additions. The Parks lettering and petal contours are less certain. The1970 predecessor should remain labelled as an approximate engraved-artwork reconstruction; its clean vector hatching deliberately does not imitate every damaged or blurred printed speck.

The1973 report also retains the earlier five-square family on its back cover. These additional designs must therefore not be used to assert a universal replacement date. Likewise the Parks shield on the organization chart is not automatically the unspecified logo proposal discussed later in the report.
