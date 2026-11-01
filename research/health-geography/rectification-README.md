# Registering the published maps to modern BC geography

Prepared 31 October 2026. This is a **preliminary cartographic experiment**, not recovered historical GIS or a verified legal-boundary reconstruction. Original source artwork remains unchanged.

**1 November follow-up:** the [GeoLibre workflow](geolibre-workflow.md) adds a portable SDK-authored project, exact image/control CSV pairs, actual projected GeoTIFFs and an edited-control import path. It preserves this registration as a baseline while additional landmarks and checkpoints are reviewed.

## In the app

Chapter 6 has a **Registered 1997/98 drawing** toggle. Dashed magenta lines show the administrative main map; a solid magenta outline shows the selected regional drawing where extracted. Brown polygons remain the predefined modern candidate. Both use the same geographic projection, zoom and pan.

All three OAG administrative main maps are registered. Comparisons cover eleven board and seven society drawings against the existing proposed LHA combinations and the best individual feature in each modern layer (89 LHAs, 16 HSDAs, five HAs). A spatially similar feature never replaces a documented candidate automatically.

The initial experiment below measured 18 regional drawings. The [extended boundary review](boundary-estimates.md) now extracts **all 34 council source polygons** from fill closures and thin strokes, using explicit source-space seeds and local gap closure without modern internal edges. It retains separate screening scores and uncertainty. The enlarged southern insets and separate twenty-region Statistics Canada map still need their own registrations; their provisional illustrations are not registered historical GIS.

## Inputs and method

- Original: the three-page OAG excerpt, `public/health-geography/maps/BC-health-area-maps-1997-98.pdf` (1997/98 Report 3, Exhibits 3–5, published March 1998).
- Reference: the existing simplified modern PGMaps `display-ha.geojson`, not a cadastral survey.
- Controls and manual source-path assignments: [rectification-controls.json](rectification-controls.json). Mandatory checksums prevent silently using changed inputs.
- Script: [rectify_health_maps.py](../../scripts/rectify_health_maps.py). Fitting, areas and intersections use EPSG:3005 metres; published vectors are EPSG:4326, rounded to six decimal places.

Each page has three non-collinear physical corner controls: the northwest provincial corner on the 60th parallel, northeast corner near 120°W/60°N and southeast corner near the 49th parallel. Their page positions come from original vector paths, with matching target corners from the modern reference. **No candidate health-region edges are fitting controls.** Explicit main-map bounds exclude insets, legends and off-page council material.

Three point pairs determine six affine coefficients exactly. Their near-zero residual is **not an accuracy estimate**: there is no redundant control or independent registration RMSE. The board map's Vancouver Island outline is a held-out shoreline check (500 equally spaced source-boundary points): median separation **4.9 km**, 95th percentile **14.2 km**, maximum **32.1 km**. This mixes registration error, source generalization and reference shoreline differences; it does not calibrate every page or inland region. Additional independent geographic checkpoints are needed.

Filled paths are assigned manually from the printed map/legend and require independent review, especially offshore components and tiny metropolitan drawings. Self-intersections use Shapely `make_valid`; non-area fragments are discarded. The explicit white Nisga’a exclusion is subtracted from North West. Modern candidates never complete or reshape a source polygon.

## Results and reuse

The script measures intersection over union (IoU), coverage of each side, best individual-feature IoU by modern layer, and eight **15 km translation scenarios**, plus nominal registration. The radius exceeds the shoreline check's 95th-percentile separation. These scenarios are **not a confidence interval or complete error model**: they omit rotation, scale, local distortion and path-assignment error.

| Source drawing | Modern comparison | Approximate nominal drawing IoU |
| --- | --- | ---: |
| Peace Liard society | Northeast HSDA | 97% |
| East Kootenay society | East Kootenay HSDA | 96% |
| Central Kootenay / Kootenay Boundary society | Kootenay Boundary HSDA | 96% |
| Northern Interior board | Burns Lake + Nechako + Prince George LHAs | 92% |
| Cariboo society | Proposed four-LHA combination | 91% |

Peace Liard retains at least 80% IoU in every tested shift. The other high nominal matches are more alignment-sensitive. High large-area IoU can conceal consequential local differences; preserve the Nisga’a exclusion, Quesnel's separate historical council, coastal transfers and all other documented constraints.

Triage rules: source drawings under 2,000 km² are detail-limited; otherwise “close” requires all shifts to retain IoU ≥0.80, “partial” requires nominal IoU ≥0.65, and the remainder are “poor”. These are exploratory display rules, not legal acceptance thresholds. Four southern/metropolitan board drawings are detail-limited. Upper Island/Central Coast does not fit its proposed combination well enough to reuse unchanged.

Predefined modern polygons remain usable as **explicitly approximate display candidates**. Historical verification still requires dated legal descriptions, intervening amendments, improved registration and reviewed extraction. `boundary-comparison.json` retains its false legal-verification flags. New cartographic scores live separately in `rectification.json`, distinct also from the existing modern-versus-modern provincial geometry audit.

## Reproduce

```sh
python3 -m venv /tmp/pofbc-rectification
/tmp/pofbc-rectification/bin/pip install -r research/health-geography/requirements-rectification.txt
/tmp/pofbc-rectification/bin/python scripts/rectify_health_maps.py
/tmp/pofbc-rectification/bin/python -m unittest discover -s scripts -p test_rectify_health_maps.py
npm run build:health-map
node --test src/health/*.test.js
npm run preview:health-map
```

Outputs: `registered-source-lines.geojson`, `registered-source-areas.geojson` and `rectification.json` in `public/health-geography`, plus [rectification-results.json](rectification-results.json) here. Remaining work and unsent request drafts are in [records-to-obtain.md](records-to-obtain.md).

## Source-membership correction

Vancouver/Richmond now includes main-map drawings 76 (Richmond) and 193 (Vancouver), consistent with the two printed 9s in the inset. Drawing 76 was erroneously included in South Fraser and is removed there. North Shore includes Bowen Island drawing 79. The former 29% Vancouver/Richmond result is withdrawn; comparisons now use the full source footprint without modern-land clipping. The working display now applies a provisional 5 km northward local adjustment to Vancouver/Richmond following user review. Original physical controls and the global GeoLibre registration baseline are retained. Other slider positions remain diagnostic scenarios.
