# Forest Oval runtime

Vendored from https://github.com/ahzs645/forestoval at commit
`44ec88fc53cd2e4eb45e1f15ab094a98582a0fc2`.

This is the live-lettering runtime bridge and the local artwork, engine scripts and fonts
it imports. The original relative paths are preserved so
Vite bundles everything for PofBC, including deployment under `/PofBC/`. The
editor, viewer, research tooling and standalone studio are not needed here. Fontsource
dependencies are installed from PofBC's root package and lockfile.

The engine, runtime bridge, artwork and fonts are unchanged upstream files.
PofBC renders the three main ovals and their colour/service variants; it does not mount the editor or read its
stored drafts. The historical comments are maintained in `src/internal/forestLogos.js`.
The single-colour tree specimens also use Forest Oval's generated mountain ridge
and base line primitives, inserted behind the tree in its source coordinates.
The Airtanker badge composition, its SVG helpers, manifest, themes, master and
referenced primitives are also vendored unchanged. PofBC loads that composition
only for the shared-crest Airtanker card.

To update, copy these same runtime paths from a reviewed Forest Oval checkout,
update this commit reference and verify the rendered specimens, their variants and family
navigation. The font notes are retained.
These are reference-based reconstructions, not authenticated
government identity masters.
