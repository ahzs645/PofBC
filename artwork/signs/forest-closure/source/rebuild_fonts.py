"""Rebuild the two small original OTF specimen subsets from explicit glyph paths."""
from pathlib import Path
import json
from glyphs import build_font
root=Path(__file__).resolve().parent.parent
for source,destination,family in [
    ('glyph_masters.json','ForestClosure1960-Reconstruction.otf','Forest Closure 1960 Reconstruction'),
    ('expanded_glyph_masters.json','ForestClosure1960-Expanded.otf','Forest Closure 1960 Expanded Reconstruction'),
]:
    data=json.loads((root/'source'/source).read_text())
    build_font(root/'fonts'/destination,{c:(g['path'],g['width']) for c,g in data.items()},family)
print('Rebuilt main 19-glyph subset and expanded OPEN 4-glyph subset.')
