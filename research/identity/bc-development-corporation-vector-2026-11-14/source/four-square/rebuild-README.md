# Rebuilding the SVGs

Run these commands with Python 3 from this directory:

```
python3 build_serif.py
python3 build_sans.py
python3 build_logo_set.py
```

The scripts use the Python standard library. The first two construct all glyphs
from their explicit path definitions; the third combines them with the frames.
To adjust the panels, edit `frame-construction.json`. To adjust letter design,
edit the relevant glyph definitions in `build_serif.py` or `build_sans.py`.
Source-aligned glyph placements are also recorded in the JSON files.

PDFs and raster proofs are exports of the finished SVGs. These scripts regenerate
the SVG files only. Export the updated SVGs from your preferred vector editor
when you need new PDFs or previews.
