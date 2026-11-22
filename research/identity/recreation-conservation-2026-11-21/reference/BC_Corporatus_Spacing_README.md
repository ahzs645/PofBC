# Corporatus spacing study

Use the preset table in BC_Corporatus_Spacing_Settings.json. The main practical result is normal width for General Administration, tracking about -50, and word spacing about65% before tracking. The long department line prefers a very mild97% horizontal scale in these raster fits, tracking about -22, and word spacing about52%;100% width is also close with tracking -33 and about54% word spacing.

Word spacing percentages refer to the nominal default space, approximately0.625em inferred from public previews, before tracking is applied. CSS word-spacing is an extra adjustment: -0.22em for General Administration, -0.30em for the97% department setting. Do not apply the numeric percentage to the final visible gap between words.

BC_Corporatus_Live_Type.svg is editable text, not outlined lettering, and requires Corporatus installed to display correctly. It contains no font binary. The raster comparison shows the measured appearance independently of font installation.

The study compares real scanned report artwork with official public font raster specimens; it does not recover historical production settings. At about21 native pixels of cap height, a few percent of width is uncertain. The97% department fit is a useful reconstruction preset, not proof that the original was intentionally condensed. The General Administration evidence rules out a large80-85% squash.

Source reports:1971 PDF page10 and1973 PDF page12 for detailed fitting. Additional repeated wordmarks and square symbols on1971 pages16,64,98,126 and1973 page144 test scan geometry. Source URLs and native crop coordinates are in source_geometry.json and the PDF study.

Preview metadata and code document the measurement process. The public raster renderer rounds individual advances; these settings should be treated as starting values and checked after loading the actual font in the chosen layout application. Optical kerning was not modelled.
