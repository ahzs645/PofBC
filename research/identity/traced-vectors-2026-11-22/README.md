# Traced vectors, 22 November 2026

Vector reconstructions traced from images, for marks the gallery held only as images. Each is
labelled a reconstruction, says what it was traced from and how closely it follows it, and keeps
that image as a download. Read by `scripts/build-collected-marks.mjs` (VECTOR_SEARCHES), which makes
the published image it stands for one of its versions.

## Okanagan Similkameen Health Region

`public/identity-collected/okanagan-similkameen-health-region/okanagan-similkameen-health-region-traced.svg`

Traced from a black-and-white GIF of the logo, 600 × 490 px, supplied to the project on
21 November 2026 (`okanagan-similkameen-health-region-supplied.gif`, beside it); where the GIF was
published is not recorded. The design is the one on the cover of the region's June 1999 health
services plan, already in the gallery as an image, which becomes this vector's version.

Method: the GIF thresholded at mid-grey and traced with Potrace (the `potracer` port; turd size 2,
minority turn policy, corner threshold 1.0, curve optimization tolerance 0.2), every outline in one
even-odd path. Rendered at the GIF's size, the trace and the GIF's ink overlap by 98.0 percent
(intersection over union); the 2,581 differing pixels are the GIF's stair-stepped edges.
