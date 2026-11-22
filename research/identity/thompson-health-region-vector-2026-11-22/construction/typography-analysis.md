# Thompson Health Region lettering reconstruction

## Final choice

The outlined reconstruction uses **EB Garamond upright, weight 500** for “Thompson Health Region”, and **Nimbus Roman Italic, regular weight** for “A Path to Better Health”. These are fitted substitutes. The original font names, original typesetting parameters and original vector artwork have not been recovered.

The 9 September 1999 letterhead is the primary geometric reference. The 9 June 2000 and 1 November 2001 letterheads provide independent shape checks. All three originals are monochrome scans, with different ink loss, bleed and page skew. The 2000 tagline is too incomplete to rank fonts reliably. The 2001 tagline is markedly heavier than the 1999 version; that difference does not prove a deliberate font-weight change.

## Delivered artwork and positioning

The main outlined SVGs in the package root contain 39 letter outlines plus the two symbol paths. Their groups are `wordmark`, `tagline` and `symbol`. The live-text SVG is supplementary and requires the named fonts.

The 1999 crop uses a 1230 × 312 coordinate system. Before the final canvas crop, the name ink bounds are x423–1124, y110–175, and the tagline ink bounds are x423–903, y197–236. Their baselines are y156.0553 and y235.3818 respectively. The combined master moves this whole arrangement by (−19,−8), preserving the relationship to the symbol while adding clear space.

The name's horizontal/vertical scale ratio is 1.0309; the tagline's is 0.9103. The clean artwork uses straight baselines. These fitting choices are documented in `type-geometry.json`. `typography-review.png` shows the source, new lettering and registration overlay. Black text follows the monochrome references; its historical colour is unverified.

## Comparison and uncertainty

Candidate fonts were rendered at high resolution, fitted to the source line's ink rectangle, reduced to source scale and compared with a mean symmetric nearest-ink-pixel distance. Small translation and rotation ranges compensated for scan registration. Lower scores indicate closer raster agreement. These are comparative fit measures, not probabilities of original-font identification. Different weights can compensate for scan bleed or dropout, so the minimum score alone was not treated as decisive.

| Name candidate, 1999 scan | Distance in source pixels |
|---|---:|
| EB Garamond weight 600 | 0.443 |
| **EB Garamond weight 500 — selected** | **0.447** |
| EB Garamond weight 450 | 0.471 |
| EB Garamond weight 400 | 0.588 |
| Nimbus Roman Regular | 0.645 |
| Sorts Mill Goudy Regular | 0.668 |
| P052 Roman | 0.718 |
| Times New Roman Regular, original corefonts distribution | 0.733 |
| Liberation Serif Regular | 0.778 |

EB Garamond's capital T, bracketed serifs, R leg and g structure were visibly closer than the initially tested Times- and Palatino-like substitutes. Weight 500 was selected after visual review: weight 600 gained very little in raster distance but looked substantially heavier. EB 500 has a 0.421-pixel fit to the 2001 name, versus 0.855 for P052 and 0.919 for Nimbus Roman. The lighter 2000 scan still marginally favours P052 (0.640 versus EB 500 at 0.737), underscoring that an exact original-font identification is not established.

For the 1999 tagline, Nimbus Roman Italic scored 0.652, Nimbus Roman Bold Italic 0.681, Times New Roman Bold Italic 0.712, and Times New Roman Italic 0.770. EB Garamond Italic scored substantially worse (1.39–1.68 depending on weight). The 2001 scan favours a heavier Times-like italic, but the regular Nimbus italic was retained for the selected 1999 layout. The likely font-family contrast is therefore Garamond-like upright lettering with a Times-like italic tagline.

Selected detailed scores are retained in `extended-font-fit-results.json` and `final-cross-source-fit.json`; a source/reconstruction/overlay plate is included as `typography-review.png`. URW Garamond No.8 was downloaded from the documented CTAN distribution late in the comparison, but was not used in the final artwork.

## Font sources

**EB Garamond:** official Google Fonts distribution, by Georg Duffner and Octavio Pardo. The variable upright font was instantiated at weight 500 for repeatable outlining. The package declares the SIL Open Font License. The original OFL text is included under `font-notices/` in the package; no font program is needed by, or included in, the outlined SVG.

- Family metadata: https://github.com/google/fonts/blob/main/ofl/ebgaramond/METADATA.pb
- Upright variable font: https://github.com/google/fonts/blob/main/ofl/ebgaramond/EBGaramond%5Bwght%5D.ttf
- License: https://github.com/google/fonts/blob/main/ofl/ebgaramond/OFL.txt
- Upstream project: https://github.com/octaviopardo/EBGaramond12

**Nimbus Roman:** installed URW Base35 OpenType font at `/usr/share/fonts/opentype/urw-base35/NimbusRoman-Italic.otf`. Its embedded name data identifies (URW)++ Design & Development, copyright 2014, version 1.00. The installed package declares AGPL-3 with its font exception. No font binary is bundled in either SVG.

- Upstream distribution: https://github.com/ArtifexSoftware/urw-base35-fonts
- Installed package notice inspected: `/usr/share/doc/fonts-urw-base35/copyright`

**Actual Times New Roman comparison:** Microsoft's original `times32.exe` corefonts package was obtained from the documented SourceForge distribution and unpacked without executing its installer. Its SHA-256 matched the published value `db56595ec6ef5d3de5c24994f001f03b2a13e37cee27bc25c58f6f43e8f807ab`. It was used for comparison only and is not included in the deliverable.

- https://sourceforge.net/projects/corefonts/files/the%20fonts/final/times32.exe/download

## Editing

Use the outlined SVG master in the root of this package for direct path editing. The optional live-text master requires the two named fonts. Numeric fitting information is preserved in `type-geometry.json`.
