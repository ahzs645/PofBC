PofBC / GeoLibre alignment review

Open health-map-review.geolibre in GeoLibre, or health-map-review.html in a browser with internet access to load the GeoLibre viewer. Project layers and rendered images are embedded; original institutional map rights and modern-data licences remain applicable.

For each map, open the matching *-source.png in GeoLibre Processing > GeoLibre toolbox > Raster > Georeferencing, then import its *-gcps.csv. Pixel coordinates are specific to that exact crop and resolution. Do not import the CSV against a resized image or the full PDF page. The manifest records dimensions, crop origin and checksums. If the embedded viewer cannot load, use the direct app link and open the downloaded project through Project > Open from > File.

Add independently identifiable physical landmarks across the map and held-out checkpoints. Never use the modern administrative edges under test as fitting controls. Export the edited GCP CSV and import it as a proposal with scripts/import_health_gcps.py; the active baseline is not overwritten automatically.

Current controls: three per main map. Affine is mathematically possible; polynomial needs six and TPS at least four independently identified points. A zero three-point fit residual is not accuracy. Insets and the twenty-region statistical map remain separate pending registrations.

IMPORTANT: GeoLibre's quick overlay fits longitude/latitude. The delivered working rasters instead fit in BC Albers (EPSG:3005) before GDAL reprojection to Web Mercator (EPSG:3857). This preserves the established projected-map baseline. A native geographic affine export is not a drop-in equivalent across the whole province. The GeoLibre fit report is diagnostic, not an accuracy finding.

The project also contains hidden working-estimate layers for 11 boards, 34 council/map labels and 7 societies, 52 independent source-drawing approximations, 20 separate statistical illustrations, current municipal, regional-district and school-district comparisons, and the provisional locally adjusted Vancouver/Richmond trace. Enable one framework at a time. The statistical illustration is a modern-LHA aggregate, not a registered historical statistical map. None is verified historical legal GIS.

Open vancouver-richmond-alignment.geolibre for a focused four-layer workspace: current coastal context, the seven current reference LHAs, the original trace and the working trace shifted 5 km north in BC Albers. Current reference and adjusted trace start visible. The local translation is an explicit provisional display choice; the original global controls are retained. The reference-and-traces GeoJSON and original source inset are included alongside the project.

The *-registered.tif files are actual Cloud-Optimized GeoTIFFs with CRS, transform and provenance tags. A projected warp and opening a project do not themselves improve or legally verify a boundary. Review all assumptions and remaining tasks in PofBC's research list.
