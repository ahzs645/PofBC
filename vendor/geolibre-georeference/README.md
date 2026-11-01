# GeoLibre georeferencing math

Pinned to `opengeos/GeoLibre` commit `44b9c42a16e055c400a04f49f45959100627cd03`, file `apps/geolibre-desktop/src/lib/georeference.ts`. The upstream MIT license is preserved in LICENSE. `provenance.json` records the source checksum.

Only TypeScript annotations were stripped; the runtime implementation is unchanged. No complete GeoLibre application or map engine is bundled into PofBC. The review-package builder uses the actual GeoLibre CSV parser/writer, fit/residual calculation and transform requirements. GeoLibre's Python SDK authors the portable review project and HTML.

The native quick-overlay affine fits longitude/latitude directly. Province-wide projected publication maps need a separate projected-CRS warp for the working comparison. A near-zero residual with three controls does not establish positional accuracy. GeoLibre's polynomial/TPS exports need additional independently identified controls.
