# WorkSafeBC visual identity timeline

Research edition 01 · 27 September 2026

Start with `index.html` for the offline viewer, or open `WorkSafeBC-timeline.pdf`.

## What is included

- `WorkSafeBC-timeline.editable.svg` — true vector poster with editable timeline text.
- `WorkSafeBC-timeline.outlined.svg` — font-independent path version of the poster.
- `WorkSafeBC-timeline.pdf` — one-page vector PDF.
- `WorkSafeBC-timeline.png` — 2880-pixel-wide rendered proof, not the vector master.
- `assets/` — two reconstructed logo lockups and a symbol-only convenience derivative. All are paths; no raster images or font files are embedded.
- `data/` — event chronology, source metadata and reconstruction provenance.
- `references/user-supplied-worksafebc.jpg` — the original user-supplied 210 × 38 pixel reference, preserved separately.
- `SOURCES.md` — sources, research limits and use notes.
- `scripts/build.py` — editable SVG/HTML builder and optional export pipeline.

## Read this before interpreting the artwork

This is a research timeline, not a recovered official master-artwork archive.

The 1968 and 1983 logo-change years are explicitly documented. The 1974 and 2005 entries are naming milestones, not automatically graphic redesigns. The orange graphic’s precise first-use date is left unknown. The 1983-family reconstruction is based on an undated specimen, pending a dated primary-source match. Earlier and 1968 artwork is not invented.

The old logo’s geometry is manually rebuilt. Its lettering is an approximation using fitted Noto Sans Condensed Medium outlines. The modern logo has custom path lettering rebuilt from the small reference JPEG. Orange #ED8B00 is a practical screen approximation, not an authenticated colour specification. Both files contain accessible titles/descriptions identifying reconstruction status. No designer attribution is asserted.

The separate symbol-only SVG is extracted from the reconstructed full lockup. It is not evidence that the symbol alone was a separate historical identity.

## Editing and exporting

Open the editable SVG in a vector editor. Logo shapes are editable paths; timeline labels remain text. Layout text uses Inter with Arial/sans-serif fallbacks. No font files are distributed. Use the outlined SVG when the same text appearance must be preserved without installed fonts.

To rebuild:

```sh
python scripts/build.py
# With Inkscape installed:
python scripts/build.py --exports
```

The builder runs offline. SVG and HTML generation need Python 3.10+ and its standard library. Optional exports need Inkscape on PATH. `build.py` contains the concise poster labels; edit it for layout/caption changes. Event and source tables in the viewer come from the JSON data. Keep those texts consistent after edits.

## Evidence policy

Do not turn a null date into a guessed year. Do not infer first appearance from the age of the organization, a website update date, the upload date of a third-party logo, or an operating-name change. Do not assert uninterrupted use from isolated examples. Source confidence and reconstruction fidelity are different things.

## Priority next archival checks

Obtain clear 1968–1982 stationery or report covers, compare 1982–1984 specimens, and inspect the 2004/2005 reports. Request a legacy identity sheet or master artwork from WorkSafeBC communications or archives, including first-use dates, overlap periods and designer credits. The source register identifies what was actually reviewed and what remains a lead.

## Rights

Independent historical study. The marks remain the property of their respective owner. WorkSafeBC’s published trademark terms require prior written permission for use; this package conveys no such permission and should not imply endorsement. No third-party original vector download is included.
