# Validation

Validated **14 November 2026** against the frozen renderer at `d3e4fbf55538e3991179a9868496dcf2e28a68c5`.

- The complete retained Museum report PDF matched SHA-256 `a392cb514522f4b6f0568d9efcd456eeb49c22aa53b9a4eafdb36d81a6c7b679`. It has 36 pages. Its cover contains one native 2179 x 3162 JPEG, and page 36 carries the 1961 imprint.
- The retained cover JPEG matched the PDF's extracted JPEG bytes exactly. The 230 x 205 target crop reproduced pixel for pixel using the recorded native coordinates.
- Both 1954 native crops reproduced pixel for pixel from the held source PDF. The source PDF and all crop checksums were verified.
- The frozen candidate SVG was exported directly from the unchanged `emblem` renderer at the stated commit. Its SHA-256 and the generated-geometry SHA-256 are recorded in `registration.json`.
- Alignment uses one scale, two translations and zero rotation. Candidate dimensions are measured from a 4x rasterization of its SVG alpha channel, with the threshold recorded. Source dimensions are measured from the native grayscale crop, with five threshold settings checked.
- The candidate's full width at equal ink height is 74.37% of the selected source width, or approximately 26% narrower. The five source-threshold settings give 73.44% to 74.37%. This result includes the source's projecting scroll tails and is not an accuracy score.
- The primary overlay, native-source comparison and partial-structure comparison were rendered and visually inspected. All labels, images and source-limit statements fit their pages. The standalone overlay was also rendered.
- The structural-study SVG parses as XML and contains only manually constructed paths and metadata. It has no raster image, reused candidate geometry, font resource or external paint reference. It is labeled as a partial study and leaves anatomy, hatching and lettering unresolved.
- The builder was run with the optional original Museum PDF verification and again without it; derived deliverables reproduce identically.
- No application files, production renderer, heading fonts or deployment configuration are changed by this research update. Application regression tests do not validate historical drawing fidelity and were not claimed for this analysis.

The source detail is still insufficient for an authenticated full engraving. This validation establishes reproducibility and the stated comparison boundaries.
