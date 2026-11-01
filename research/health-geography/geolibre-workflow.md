# GeoLibre georeferencing round trip

Prepared 31 October 2026 (America/Vancouver). The existing historical-map registration now has a working GeoLibre review/export path. This makes it easier to inspect and edit control points; it does **not** establish improved accuracy or verify a historical legal boundary by itself.

## Open the review

In Health Maps, use **Open GeoLibre review** or **Download the complete review package**. The package contains:

- An SDK-authored `health-map-review.geolibre` project with sixteen embedded layers: modern HA/HSDA/LHA datasets, three registered source images, society boundary vectors, three working-estimate frameworks (11 boards, 34 council/related labels, 7 societies), all 52 source-drawing approximations, twenty statistical illustrations, current municipalities, regional districts and school districts, and the provisional adjusted Vancouver/Richmond trace. New estimate/reference layers start hidden; enable one historical framework at a time. All data and images travel with the project; no author-machine paths are needed.
- `health-map-review.html`, which loads the hosted GeoLibre viewer and posts the embedded project to that viewer. Internet access is required for the viewer application. The project uses a blank background and needs no external basemap service or credentials. If browser privacy settings block storage inside the embedded viewer, the page also offers project download and a direct GeoLibre app link; open the downloaded project through Project → Open from → File.
- Three original administrative main-map PNG crops, each with its matching `*-gcps.csv` and exact pixel dimensions, crop origin and source checksum in `image-manifest.json`.
- Three **actual Cloud-Optimized GeoTIFFs**, tagged with CRS, geotransform and PDF provenance. These fit source pixels in **BC Albers EPSG:3005** and then resample into **Web Mercator EPSG:3857** at 2,000 m display resolution. This preserves the working projected registration; it is not additional source accuracy.
- A GeoLibre fit report and a compact SDK-validated project summary.

The source images exclude all enlarged insets and legend text. Their original complete pages remain downloadable in PofBC. Source maps and modern data retain their original attribution and licence conditions.

## Use the georeferencer

1. Open the project in GeoLibre. Toggle the source drawings and modern layers to inspect correspondence. The society raster is initially visible, alongside modern outlines and registered source vectors.
2. Open **Processing → GeoLibre toolbox → Raster → Georeferencing**. Load the desired `*-source.png`, then import that exact map's `*-gcps.csv`. Do not use the CSV against a resized image or the full PDF page: those have a different pixel coordinate system.
3. Add **independently identifiable physical landmarks**, distributed across the map, and reserve separate checkpoints. Do not use the administrative edges being tested as fitting controls.
4. Export the edited control CSV. GeoLibre supports affine export with three controls, order-two polynomial with six, and thin-plate spline with at least four. Those are mathematical minimums, not sufficient evidence of accuracy. Do not manufacture extra points by interpolating existing controls.
5. Bring the CSV back as a separate proposal, then rebuild comparison files into a separate directory for review.

GeoLibre's native quick image overlay fits **longitude and latitude directly**. It is not equivalent to fitting a province-wide projected publication map in BC Albers. The delivered working raster previews use a projected GDAL warp instead. A native geographic affine export should be evaluated against independent checkpoints before replacing that baseline. Polynomial/TPS can model local distortion once suitable controls exist; they do not locate landmarks or validate legal geography automatically.

## Import edited controls into PofBC

```sh
python3 -m venv /tmp/pofbc-geolibre
/tmp/pofbc-geolibre/bin/pip install -r research/health-geography/requirements-geolibre.txt
/tmp/pofbc-geolibre/bin/python scripts/import_health_gcps.py \
  --map boards --csv /path/to/edited-boards-gcps.csv \
  --out /tmp/proposed-board-controls.json
/tmp/pofbc-geolibre/bin/python scripts/rectify_health_maps.py \
  --controls /tmp/proposed-board-controls.json \
  --out-dir /tmp/proposed-health-registration
```

The importer validates the **exact original image checksum**, CSV headers, numeric/world/image bounds, duplicate pixels and non-collinear source/target controls. It reverses the real rendering scale/crop offset to recover PDF page coordinates. It rejects invalid rows rather than adopting GeoLibre's permissive parser's silent skips. The active control file is protected; proposal outputs cannot replace the public baseline implicitly.

Inspect training residuals, independently held-out checkpoint errors, local distortions and the recomputed area scores. A three-control fit's near-zero residual remains uninformative about accuracy. The importer marks the proposal as pending review and never marks a boundary verified. The current round-trip test exports/reimports the existing controls and reproduces all 18 baseline overlap scores; this tests interoperability, not improvement.

## Build and verify

```sh
/tmp/pofbc-geolibre/bin/pip install -r research/health-geography/requirements-estimates.txt
/tmp/pofbc-geolibre/bin/python scripts/build_health_estimates.py
/tmp/pofbc-geolibre/bin/python scripts/build_health_geolibre.py
/tmp/pofbc-geolibre/bin/python -m unittest discover -s scripts -p test_health_geolibre.py
node --test src/health/healthGeolibre.test.js
```

The authoring SDK is pinned to **GeoLibre Python 3.6.0**. The actual upstream CSV/fitting implementation is preserved, with MIT licence, under `vendor/geolibre-georeference`, pinned to `opengeos/GeoLibre` commit `44b9c42a16e055c400a04f49f45959100627cd03`. Only TypeScript annotations were stripped. No whole GeoLibre app or new map engine is bundled into the PofBC story renderer.

Official references: [GeoLibre processing tools](https://geolibre.app/user-guide/processing/), [project format](https://geolibre.app/project-format/), [georeferencing implementation](https://github.com/opengeos/GeoLibre/blob/44b9c42a16e055c400a04f49f45959100627cd03/apps/geolibre-desktop/src/lib/georeference.ts) and [GeoTIFF export](https://github.com/opengeos/GeoLibre/blob/44b9c42a16e055c400a04f49f45959100627cd03/apps/geolibre-desktop/src/lib/georeference-gdal.ts).

## Applied local display alignment

Open `vancouver-richmond-alignment.geolibre` for the focused reference/trace workspace. Its four embedded layers are modern coastal context, the seven current Vancouver/Richmond reference LHAs, the original source trace and a working trace translated 5,000 m north in EPSG:3005. Reference and adjusted trace start visible; the original can be toggled on. The source inset and combined reference-and-traces GeoJSON are included in the ZIP. The global three-control registration, its GCPs and its COGs remain the original baseline. This local display choice remains provisional and does not verify historical legal edges.
