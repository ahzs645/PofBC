# British Columbia Petroleum Corporation - vector reconstruction

Prepared 12 November 2026 from the two supplied monochrome image references.

## Start here

- **artwork/BCPC_stacked_logo_black.svg**: full four-line corporate logo, black, transparent background.
- **artwork/BCPC_stacked_logo_white.svg**: the same artwork in white for dark backgrounds.
- **artwork/BCPC_emblem_black.svg** and **BCPC_emblem_white.svg**: standalone emblem.
- **artwork/BCPC_vector_artwork.pdf**: two pages containing the stacked logo and standalone emblem, respectively. The artwork is entirely vector paths.
- Matching transparent PNG exports are in the artwork folder for applications that require raster images.
- **previews/BCPC_reconstruction_preview.png** shows the black and reversed white applications.
- **previews/BCPC_overlay_comparison.png** shows reference, registered reconstruction, and differences.

These are reconstructed files, not an authenticated original corporate master or a recovered original font. The exact historical typeface and original print colours remain unconfirmed.

## How the emblem was rebuilt

The master is a manually constructed compound shape. Its outer silhouette and inner cutout are related curved teardrop profiles. It uses eight cubic Bezier segments and two straight vertical edges. There are no scanned textures, embedded bitmap images or automatically traced contours in the artwork SVGs.

The normalized emblem coordinate system is 100 units wide by 128 units high. The tip is at (55, 0), the outer shoulder is at (55, 42), and the inner vertical ends at (55, 67). The outer lower extent is (50, 128); the inner lower extent is (52, 102). Tangents at the sides and bottom keep the curves smooth. The negative centre is a real transparent opening, not a white patch.

The supplied 1991/92 standalone example was the principal silhouette reference. The 1982/83 inverse example provided a useful independent check. The two tips and additional crescent on the 1985/86 cover arise from overlapping copies; that cover composition was not used as the single-emblem master.

The master allows the counter's upper corner and outer shoulder to meet at one vertex. The small inverse reference supports that construction. The larger reference appears to have a slight horizontal offset between those edges, about one or two source pixels. The supplied scans do not establish whether this reflects print gain, reproduction, or a small artwork difference, so no arbitrary extra bridge was introduced.

## How the lettering was rebuilt

The four-line wordmark uses 17 custom, reusable vector letterforms:

B, C, P, a, b, e, h, i, l, m, n, o, p, r, s, t, u.

Each glyph was drawn from explicit curves and straight segments. Repeated letters share their outline and scale; their placements preserve the optical spacing in the reference. The final SVG expands each occurrence into a separate path for straightforward editing. Text is therefore editable as shapes, not as live font-based text. No installed font is needed.

Features retained include the tilted e crossbar, flared ascender heads, dense lowercase bowls, compact t, right-aligned line arrangement, and the small emblem overhang beyond the wordmark's right edge. The worn C at the start of Corporation was completed using the intact C in Columbia. The final refinement pass softened the b junction, made the o counters more upright, and flattened the r shoulder.

The original letterforms appear visually consistent with the **Goudy Heavyface family**, but that is an inference from their shapes, not archival proof of BCPC's type specification. The delivered letters are custom reconstruction geometry; they are not a redistributed commercial font.

Reference type specimens consulted:

- P22/Lanston, Goudy Heavyface: https://p22.com/fonts/goudy-heavyface/
- Adobe type-name mapping: https://blog.typekit.com/wp-content/uploads/2005/10/type1-2-opentype.pdf
- Epson Adobe PostScript font specimen manual, printed page 40: https://download.epson-europe.com/pub/download/6289/epson628921eu.pdf

## Comparison and limits

The comparison sheet uses the following legend:

- Dark blue-grey: both source and reconstruction.
- Pink: source only.
- Cyan: reconstruction only.

Registration changes the placement of the clean artwork only for comparison with the skewed scans. It does not trace or deform individual glyph contours. The delivered artwork remains upright.

### Separate emblem checks

After affine registration of the same manually drawn emblem, thresholded silhouette intersection over union (IoU) was:

| Reference | Emblem IoU |
| --- | ---: |
| Large 1991/92 standalone example | 93.64% |
| Small 1982/83 inverse example | 95.71% |

These values apply to the **emblem only**. They do not describe the lettering or full logo.

### Lettering and complete composition

A separate registration of the entire four-line wordmark gave **77.21% text IoU** and **87.14% Dice overlap**. It used a 1.579-degree clockwise scan rotation, common horizontal/vertical scales and one translation. Individual letters were not independently registered.

The complete composition comparison on the sheet uses one affine transform for both the emblem and the lettering. Under that shared registration, full-logo IoU is **79.47%**, the text region is **76.89%**, and the emblem region is **91.04%**. These differ from the separate checks because one common placement must fit the complete scan.

IoU is an image-overlap measurement, not a percentage of design authenticity. Print wear, blur, thresholds, source resolution and residual differences in the custom letterforms all affect it. The emblem is the stronger reconstruction. The lettering is a clean approximation of the supplied wordmark; a confirmed original font or sharper original artwork would be needed to settle its finer details.

The two supplied images are included under references. Dates and report descriptions follow the supplied evidence board; no new historical claim is based on the type specimen pages.

## Editing and rebuilding

In a vector editor, select the emblem group or a wordmark line to recolour or move it. Each letter is separately editable. White files require a dark canvas to be visible. Preserve proportional scaling when resizing the logo.

The construction folder contains the emblem's exact path, shared glyph paths, placements and comparison metrics. To regenerate the four SVGs using Python 3's standard library:

```sh
python construction/rebuild_svgs.py --output rebuilt-artwork
```

The rebuild requires no reference image, font installation or tracing software. The supplied PDF and PNGs are already exported for immediate use.
