# Revision 4 paint construction

`paint_design.py` contains the authored colour fields and localized brush gestures on the 1000 × 1400 plane. `build_paint_v4.py` creates seeded synthetic deposition, pigment variation and dry coverage, then exports opaque vector paths. It does not open the supplied photograph or any evaluation mask.

## Reproduce the vector components

Keep these source files in a folder named `paint-source`, beside the intended `paint_v4.svg` and `paint_v4_clean.svg` outputs. From its parent directory:

```bash
python3 -m pip install -r paint-source/requirements.txt
python3 paint-source/build_paint_v4.py --svg
```

The generator writes `paint_v4.svg`, `paint_v4_clean.svg`, `paint_v4_draft.png` and construction statistics to the parent directory. Omitting `--svg` writes only the direct synthetic-coverage draft for faster iteration. The seed is 14201967. The exact SVG render can differ slightly from the direct draft because vector contours are smoothed, simplified and antialiased; final metrics use the SVG rendered by Inkscape.

```bash
inkscape paint_v4.svg --export-width=1000 --export-filename=paint_v4.png
inkscape paint_v4_clean.svg --export-width=1000 --export-filename=paint_v4_clean.png
```

`analyze_paint_candidate.py` is a record of the original workspace evaluation. It expects the registered photograph, V3 snapshot and fixed V2 paint mask under the original `work/revision4` / `work/revision2` layout. It is separate from construction and never writes artwork geometry. The final package's main paint analyzer is the portable entry point for reproducing the delivered comparison.

The colours fit the photograph's appearance, not physically calibrated historical inks. Fine grain, transparent residue and paint hidden by the illustration remain interpreted.
