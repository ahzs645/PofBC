# ICBC logo history — complete Edition 02 package

**Start with `index.html`** for the offline gallery, timeline and links to the notes. No web server is needed.

## Included

- `icbc-logo-timeline.svg`: editable caption text and embedded vector logo geometry.
- `icbc-logo-timeline-outlined.svg`: visible caption text converted to paths.
- `icbc-logo-timeline.pdf`: vector print/export edition.
- `icbc-logo-timeline.png`: rendered preview.
- `logos/`: nine separate SVG assets, including the added early emblem and all eight previous variants.
- `research/NOTES.md`, `SOURCES.md`, `CHANGES.md`: expanded chronology, source links, uncertainties and package changes.
- `data/`: machine-readable timeline, source register, original-reference mapping and output asset index.
- `source-assets/`: both original supplied SVGs, the useful original reference images, and the early registry drawing.
- `proofs/`: original reconstruction comparison, early-emblem comparison and validation results.
- `tools/build_timeline.py`: rebuilds the editable SVG and offline viewer from the JSON and logo assets.
- `tools/export_and_validate.py`: exports outlined SVG, PDF and PNG, and runs structural checks.

## Important qualifications

This is a historical research package, not an official brand manual or a complete set of verified launch/retirement dates. The board distinguishes evidence dates from exclusive logo eras. Expanded interpretation and all source locators are in the notes.

The early-emblem addition is **approximate unhatched boundary linework**, not a recovered official colour master. Earlier full-name, abbreviated and serif-road reconstructions also remain approximate. The later supplied vector paths are preserved. Blue and black modern variants are declared recolours; their values are not certified brand specifications.

No font files are included. Captions use Inter with an Arial/sans-serif fallback. Use the outlined version for stable display without caption fonts. Individual logo files have no live text or embedded bitmap images.

## Rebuilding

From this folder, with Python 3 and Pillow installed:

```sh
python3 tools/build_timeline.py
python3 tools/export_and_validate.py
```

The export step requires Inkscape on your PATH. The first script chooses an installed Inter or DejaVu Sans font for measurement and exports with the same caption family. It never downloads or bundles fonts. Review a rendered preview after changing wording or artwork.

## Rights

ICBC names and marks remain associated with their respective owner. This independent research and reconstruction package does not imply endorsement or grant trademark permission. Consult the linked owner policy before external brand use.
