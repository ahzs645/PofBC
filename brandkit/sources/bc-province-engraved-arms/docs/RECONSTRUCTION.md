# Grace M. McCarthy calling-card reconstruction

This study rebuilds the seven lines of the supplied calling card as editable vector lettering and places the supplied BC coat-of-arms path in the photographed layout. It adds three reusable, source-informed script fonts derived from Pinyon, seven comparison fonts, portable SVGs and an offline editor.

**Status: review candidate.** The historical typeface remains unidentified. The supplied arms are a different engraving from the card. These qualifications are carried in the editor, SVG metadata, font provenance and validation report.

## Use the files

| File | Purpose |
| --- | --- |
| [Offline editor](grace-mccarthy-card-editor.html) | Download/open the HTML file to edit wording, fonts, size, placement, ink and paper. Everything it needs is embedded. |
| [Editable SVG](grace-mccarthy-card-editable.svg) | Seven live text objects, embedded font data and actual font-family fallbacks. Install the included TTFs for desktop editors that ignore embedded web fonts. |
| [Outlined SVG](grace-mccarthy-card-outlined.svg) | Portable vector artwork with no installed-font requirement; preserves the reference wording. |
| [Preview](grace-mccarthy-card.png) | 1800 × 1038 render of the outlined vector. |
| [Model](evidence/model.json) | Exact font bytes, complete licenses, source positions, shaped outline runs, supplied arms and coverage. |
| [Font comparison](grace-mccarthy-font-comparison.png) | All seven original lines beside the source-informed lettering. |
| [Overlay diagnostics](grace-mccarthy-font-overlays.png) | Source/study ink overlays and measured limitations. |

The editor supports source, overlay and side-by-side views. Its SVG export retains current edited text; its outlined-reference download preserves the original wording. PNG output draws from loaded fonts and the vector arms directly, avoiding embedded-font loss during SVG-image conversion. Projects can be downloaded as JSON and reopened; changes are otherwise kept only in the page. Font files, licenses and provenance can be downloaded together from the editor.

The separate static page is located at `public/stationery/grace-mccarthy/`. It does not assign stationery fonts to plate serial dies or alter the existing renderer.

## Lettering and font provenance

The photograph is consistent with formal engraved/copperplate script. [Commercial Script from Bitstream](https://www.myfonts.com/collections/commercial-script-font-bitstream) and [URW](https://www.myfonts.com/collections/commercial-script-font-urw/) were inspected as historical identification candidates. The specimens do not establish an exact match to the photograph. No proprietary Commercial Script binary is included.

Seven open fonts were compared at consistent ink height: Pinyon Script, Imperial Script, Luxurious Script, Mea Culpa, Herr Von Muellerhoff, Monsieur La Doulaise and Italianno. [Pinyon](https://github.com/google/fonts/tree/main/ofl/pinyonscript) was the most useful starting point, particularly for G and the angular M. Its source binary is checksum-pinned in the model, along with the [upstream snapshot](https://github.com/SorkinType/Pinyon/tree/91d502f9b3a98c210c54916c356caa534cdc4d70) and complete SIL Open Font License.

Three renamed study cuts adapt that open font:

| Cut | Card role | Reconstruction work |
| --- | --- | --- |
| PlateForge Card Script Display Study | Name | Lower x-height, revised M proportions and advances, reconstructed C and adjusted stroke weight. |
| PlateForge Card Script Compact Study | Three title lines | Narrower lowercase forms, adjusted capital metrics, spacing and printed weight. |
| PlateForge Card Script Study | Telephone, city and province | Moderate spacing changes, reconstructed C/V and compact hand-drawn numerals. |

The C, V, 0, 1, 3, 6, 7, 8 and hyphen study forms use explicit curves. Other shapes are derived from Pinyon using documented transforms in an unslanted coordinate system and a modest FreeType outline-weight adjustment. The lettering was not extracted by raster tracing. Full rules, source hashes and evidence are recorded in [font-study.json](evidence/font-study.json).

These three cuts are reconstruction choices; they do not establish that three different fonts were used on the original card. The card only shows capitals `BCDGIMPRSTV`, lowercase `abcdefhilmnoprstuvy`, digits `013678`, spaces, ampersand, hyphen and period. Other available characters are inherited or inferred and have no source evidence from this card. In particular, the card does not establish numeral shapes for 2, 4, 5 or 9.

### Overlay results

Native widths, source-sized comparisons and placement diagnostics are kept separate. The final card uniformly resizes complete text runs to their measured source widths; it does not stretch a complete line horizontally. Width agreement alone cannot establish correct letter anatomy or spacing.

The diagnostic overlay compares stock Pinyon with the study using the same translation and uniform-fitting rules:

| Diagnostic | Stock Pinyon | Study |
| --- | ---: | ---: |
| Name ink intersection-over-union | 0.2557 | 0.2526 |
| Name foreground F1 within 2 px | 0.5965 | 0.5710 |
| Telephone ink intersection-over-union | 0.1775 | 0.2875 |
| Telephone foreground F1 within 2 px | 0.5442 | 0.6615 |

The telephone line improves on these diagnostics. The name's aggregate overlap is essentially unchanged/slightly worse despite some more appropriate letter details and proportions. Its curves, joins and spacing remain approximation work. These scores are geometric diagnostics for this blurred photograph, not historical accuracy percentages or a certification of the full font.

## Arms, layout and colour

The supplied path is preserved exactly, including `fill-rule="evenodd"`. Its natural aspect ratio is approximately **0.889**, while the photographed crest is approximately **1.515**. The source has a different ribbon arrangement and supporter drawing. The reconstruction uniformly fits the supplied vector to the source crest's height and centres it in that area; it does not widen the vector to conceal the mismatch.

The artboard is **1800 × 1038**. Estimated paper corners are `[109,63]`, `[1918,95]`, `[1903,1137]`, `[89,1112]` in the original 2048 × 1179 image. The upper-right corner is particularly uncertain. The screenshot does not establish a physical print size, issue date or exact original ink colour. The olive-gold is a visual approximation. The pale photographed paper edge is omitted from the clean reconstruction.

The original screenshot and supplied SVG fragment are retained byte-for-byte, with hashes in [geometry.json](evidence/geometry.json) and [validation.json](evidence/validation.json). The analytical perspective-adjusted reference is also retained. The upload date is not assigned as the card's historical date.

## Rebuild

Regular regeneration uses the exact font bytes already embedded in `model.json` and requires no downloads:

```bash
python scripts/rebuild-mccarthy-card.py
python scripts/mccarthy-card/build-editor.py
inkscape public/stationery/grace-mccarthy/card-outlined.svg \
  --export-type=png --export-width=1800 \
  --export-filename=public/stationery/grace-mccarthy/card-preview.png
```

The vector builder needs Python, Pillow, numpy, fontTools and the system HarfBuzz library. The editor assembler uses the Python standard library. The committed layout is [reference-layout.json](evidence/reference-layout.json).

To reconstruct the three font binaries from the pinned Pinyon base:

```bash
python scripts/mccarthy-card/rebuild-study-fonts.py \
  --output-dir /tmp/plateforge-card-fonts
```

The font builder needs fontTools and system FreeType through `ctypes`. It was checked with Python 3.12.14, fontTools 4.61.1 and FreeType 2.13.3. Its three TTF outputs were byte-identical across independent rebuilds in this environment. It also emits complete OFL files and provenance. The comparison PNGs are evidence snapshots from the recorded analysis, not outputs of this font-building command.

To incorporate regenerated fonts, pass each emitted font directory to `scripts/rebuild-mccarthy-card.py --extra-font-directory DIRECTORY`, then regenerate the editor. This preserves explicit per-line font assignments and the saved layout.

## Validation

[validation.json](evidence/validation.json) records exact preservation of the source and arms, font hashes and licenses, coverage of all selected characters, vector-only SVG contents, seven live text objects in the editable version, correct negative spaces, actual-family fallbacks, no clipped ink, and byte-identical repeat builds.

At 1800 × 1038, Inkscape rendered the live-text SVG using the exact supplied fonts and the outlined SVG with a mean absolute RGB-channel difference of **0.01870 / 255**. Only **one pixel** had any channel difference above 20. This checks export consistency; it does not measure historical likeness.

The editor's JavaScript and generated HTML scripts are syntax-checked. A separate review checked project-file validation, font-family resolution, mobile access to the comparison and pointer/keyboard focus. Browser acceptance remains unverified: command-line Chromium was blocked by a socket permission restriction and the shared browser could not access this local workspace preview. No claim of browser-tested downloads, mobile acceptance or live deployment is made.

The normal project checks also passed locally: **70 test files / 1,977 tests**, followed by `BASE_PATH=/plateforge/ npm run build` including TypeScript compilation. The initial sparse checkout lacked existing research fixtures; materializing those fixtures resolved the setup failures without source changes. The built card assets matched their public-source bytes. See [editor-validation.json](evidence/editor-validation.json) for the boundary between these checks and the still-unverified browser interactions.

## Rights

Each included font has its complete original SIL Open Font License in the model and downloadable font package. The renamed Pinyon-derived studies preserve that license and attribution. Pinyon's embedded 2022 copyright and distributed 2024 OFL text are both retained as supplied. The historical reference image and supplied coat of arms are user-provided evidence; font licensing does not establish rights to those separate materials.
