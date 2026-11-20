# IUS application typography review

Scope: typography of the support brochure, 8 June 1988 invitation, business fundraising letter, petition/form applications, and partially visible sweatshirt. Reviewed against supplied original photographs, not the previously generated raster logo boards. This audit led to the scoped revision recorded below. Other font identities remain qualified.

## Findings and revision decisions

1. **Restore italic display capitals in the business appeal (high confidence in italic style; moderate confidence in proposed digital substitute).** In `IMG_7955(1).jpeg`, the lines `A UNIVERSITY FOR / PRINCE GEORGE / NOT KELOWNA` and `WE NEED A UNIVERSITY` have visibly right-sloping serif capitals. Their slant differs from the upright question lines and body type nearby, so it is not simply page perspective. The initial v1.0 `build_applications.py` used upright `NimbusRoman-Bold.otf` for those lines and the extracted `ius-university-for-prince-george` component. The revision uses actual `NimbusRoman-BoldItalic.otf` outlines as the closer working substitute; keep upright serif question lines and body. Do not identify the original as Times Bold Italic with certainty.

2. **Fix the latent italic font path (certain implementation error).** The initial v1.0 `source/vector_utils.py` mapped `italic` to nonexistent `NimbusRoman-RegularItalic.otf`; the installed file is `NimbusRoman-Italic.otf`. The revision adds a distinct `serif-bold-italic` mapping to `NimbusRoman-BoldItalic.otf` for the appeal, rather than skewing upright outlines.

3. **Brochure second-line size is slightly understated (moderate confidence; proportions remain approximate).** `IMG_7953(1).jpeg`, viewed through the analytical `tmp/audit/brochure-rectified.png` crop, shows the cap height of CAMPAIGN at roughly four-fifths of SUPPORT. The initial v1.0 component specified 120 versus 160, or 75%. The revision sets CAMPAIGN to 132 versus 160, or 82.5%, while preserving its width of 860, right anchor of 1000, and cap-top anchor of 200. SUPPORT and the overall canvas remain unchanged. This better reflects the visible relationship while retaining the approximately 0.86 word-width ratio. Do not treat these measurements as original specifications; the paper is oblique and its physical aspect ratio was not measured. Nimbus Sans Bold is a reasonable family substitute; a switch to a wholly different sans family is not justified by this source.

## Retain, with qualified identification

- **Invitation:** The photograph clearly supports monospaced slab-serif/typewriter lettering, predominantly uppercase with a mixed-case paragraph below. Nimbus Mono PS Regular is a defensible working proxy. The photograph has visibly heavier ink in places, but blur, ink spread and photography are insufficient to establish an original bold cut or exact machine/typeface. The attached candidate comparison shows both regular and bold without declaring either original.
- **Fundraising body:** High-contrast proportional serif body, upright serif question lines and a heavier organization-name line are supported. Nimbus Roman Regular/Bold provide reasonable editable surrogates. Font-family identity, point sizes and exact spacing remain unconfirmed.
- **Form headings:** All-cap bold sans headers are supported. Nimbus Sans Bold is defensible. Small field labels such as RECEIVED FROM, GIVEN NAMES and POSTAL CODE appear more widely spaced than ordinary text. This should be addressed as spacing/fit, not evidence for a different font. Retain reconstruction status and do not infer a precise tracking value from the blurred image.
- **Petition copy:** Sans body with an all-cap introductory line is supported. The source does not warrant claiming a named original face. Nimbus Sans Regular is a reasonable substitute; body weight/fit can be refined from clearer scans if found.
- **Sweatshirt:** The arched INTERIOR is outlined collegiate/slab lettering. The lower word is partly hidden by folds; the visible portion appears serif, but an exact Times-style identification is not warranted. Keep the current component labeled interpretive, not a verified font match. The source does not support extracting a complete original alphabet.

## Incidental transcription observation

The enlarged original invitation photograph reads **DAHLLOFF** in the uppercase name and **Dahlloff** in the following paragraph, with two final Fs in both occurrences. The initial v1.0 re-typesetting used DAHLLOF/Dahllof. This finding was reported to the integrator, who corrected the revised invitation to reproduce the photographed double-F spelling. The source spelling is preserved rather than silently normalized against any other spelling of the person's name.

## Evidence and comparison artifacts

- `applications-fundraising-detail.png`: original photograph crop with light rotation for reading; no contours extracted.
- `applications-invitation-detail.png`: original invitation crop; the original machine/font remains unidentified.
- `applications-brochure-wording-detail.png`: crop from the perspective-corrected analytical brochure reference.
- `applications-sweatshirt-detail.png`: partial source, insufficient for exact identification.
- `applications-candidate-sheet.png`: actual installed font outlines compared at controlled cap heights.
- `applications-font-comparison.png`: source/candidate board suitable for the audit report.

All font names here describe the fonts used in the reconstruction or candidate comparisons. None is confirmed as the original font solely from these photographs. No external historical claims or web sources were required for these visual findings.

## Scoped implementation and verification

The application-audit subtask changed only the CAMPAIGN cap-height parameter in `source/build_core.py` and rebuilt only `svg/support-campaign-wording.svg`. The SVG was rendered and visually checked after that change. Italic font mapping and fundraising changes were integrated separately by the primary agent. Affected derived artwork includes the brochure composite and corresponding PDF/EPS/PNG files; those are handled by the integration/export pass.

## Direct before-and-after evidence

`applications-before-after.png` compares the original photographs with direct Inkscape renders of the saved v1.0 SVGs and revised v1.1 SVGs. It shows the campaign headline component, the actual `we-need-a-university` group exported from each fundraising letter, and the support-campaign wording component. These panels display the delivered vector paths rather than separately generated font specimens.
