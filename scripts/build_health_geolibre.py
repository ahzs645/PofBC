#!/usr/bin/env python3
"""Build a portable GeoLibre review project, original image/GCP pairs and COGs.

GeoLibre's actual fitting/CSV code is exercised by health-geolibre-controls.mjs.
The saved map uses GDAL warps in BC Albers before reprojection to Web Mercator;
GeoLibre's native geographic quick-overlay fit remains separately documented.
"""
import base64
import hashlib
import json
import subprocess
import tempfile
import uuid
import zipfile
from pathlib import Path

import fitz
import geolibre
import numpy as np
import rasterio
from geolibre import Map
from geolibre.authoring import add_layer, describe_project
from PIL import Image
from rasterio.control import GroundControlPoint
from rasterio.shutil import copy as copy_raster
from rasterio.transform import from_gcps
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds

from rectify_health_maps import PUBLIC, RESEARCH, TO_METRES, read, sha

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PUBLIC / 'geolibre'
SCALE = 4


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def stable_id(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'https://github.com/ahzs645/PofBC/health-geolibre/' + name))


def main():
    OUTPUT.mkdir(exist_ok=True)
    controls = read(RESEARCH / 'rectification-controls.json')
    if sha(PUBLIC / controls['sourcePdf']) != controls['sourceSha256']:
        raise ValueError('Source PDF changed; review the image/control correspondence')
    pdf = fitz.open(PUBLIC / controls['sourcePdf'])
    images = []
    for page in controls['pages']:
        bounds = page['mainMapBounds']
        pix = pdf[page['pdfPage'] - 1].get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), clip=fitz.Rect(bounds), alpha=True)
        filename = f"{page['mapId']}-source.png"
        pix.save(OUTPUT / filename)
        # Pixel origin comes from the actual rendered crop, not guessed page size.
        origin = [pix.x / SCALE, pix.y / SCALE]
        image = {'mapId': page['mapId'], 'file': filename, 'sha256': sha(OUTPUT / filename),
                 'width': pix.width, 'height': pix.height, 'pdfPage': page['pdfPage'],
                 'pixelsPerPdfPoint': SCALE, 'pageOrigin': origin, 'insetsIncluded': False,
                 'controls': [{'name': point['name'], 'pixel': [round((point['pagePoint'][0] - origin[0]) * SCALE, 6), round((point['pagePoint'][1] - origin[1]) * SCALE, 6)],
                               'longitudeLatitude': point['longitudeLatitude']} for point in page['controls']]}
        for point in image['controls']:
            if not (0 <= point['pixel'][0] <= pix.width and 0 <= point['pixel'][1] <= pix.height):
                raise ValueError('A control falls outside its rendered image')
        images.append(image)
    manifest = {'schemaVersion': 1, 'preparedOn': '2026-10-31', 'sourceSha256': controls['sourceSha256'],
                'geolibrePythonVersion': geolibre.__version__, 'geolibreCode': read(ROOT / 'vendor/geolibre-georeference/provenance.json'),
                'images': images, 'baselineChanged': False,
                'note': 'Original main-map crops and correctly scaled GeoLibre control files. Reopening these files does not independently verify the controls or improve their accuracy.'}
    save(OUTPUT / 'image-manifest.json', manifest)
    subprocess.run(['node', str(ROOT / 'scripts/health-geolibre-controls.mjs'), str(OUTPUT)], check=True)

    # Actual SDK authoring; no external basemap or data is needed by the project.
    view = Map(center=(-126, 54), zoom=4, basemap=None)
    project = view.to_project()
    project.update(name='PofBC historical health maps — GeoLibre alignment review', basemapStyleUrl='', basemapVisible=False)
    for layer in ['ha', 'hsda', 'lha']:
        add_layer(project, {'id': stable_id(layer), 'name': f'Modern {layer.upper()} comparison', 'type': 'geojson',
                  'source': {'type': 'geojson'}, 'visible': layer != 'lha', 'opacity': 1,
                  'geojson': read(PUBLIC / f'display-{layer}.geojson'), 'metadata': {'historicalBoundaryVerified': False},
                  'style': {'fillColor': '#d7ddd5', 'fillOpacity': .3 if layer == 'ha' else 0,
                            'strokeColor': '#344f45', 'strokeWidth': 1}})
    for image in images:
        pixels = np.array(Image.open(OUTPUT / image['file']).convert('RGBA'))
        gcps = [GroundControlPoint(row=p['pixel'][1], col=p['pixel'][0], x=TO_METRES(*p['longitudeLatitude'])[0], y=TO_METRES(*p['longitudeLatitude'])[1]) for p in image['controls']]
        source_transform = from_gcps(gcps)
        corners = [source_transform * point for point in [(0, 0), (image['width'], 0), (image['width'], image['height']), (0, image['height'])]]
        extent = [min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners), max(p[1] for p in corners)]
        target_transform, width, height = calculate_default_transform('EPSG:3005', 'EPSG:3857', image['width'], image['height'], *extent, resolution=2000)
        warped = np.zeros((4, height, width), dtype=np.uint8)
        reproject(source=np.moveaxis(pixels, 2, 0), destination=warped, src_transform=source_transform, src_crs='EPSG:3005',
                  dst_transform=target_transform, dst_crs='EPSG:3857', src_alpha=4, dst_alpha=4, resampling=Resampling.bilinear)
        cog_name = f"{image['mapId']}-registered.tif"
        with tempfile.TemporaryDirectory() as temp:
            intermediate = Path(temp) / 'warped.tif'
            with rasterio.open(intermediate, 'w', driver='GTiff', width=width, height=height, count=4, dtype='uint8', crs='EPSG:3857', transform=target_transform) as dataset:
                dataset.write(warped)
                dataset.update_tags(SOURCE_PDF_SHA256=controls['sourceSha256'], REGISTRATION='Three-point BC Albers affine; preliminary, not legal verification')
            copy_raster(intermediate, OUTPUT / cog_name, driver='COG', compress='DEFLATE', blocksize=256)
        png = OUTPUT / f"{image['mapId']}-registered.png"
        Image.fromarray(np.moveaxis(warped, 0, 2)).save(png)
        with rasterio.open(OUTPUT / cog_name) as dataset:
            west, south, east, north = transform_bounds(dataset.crs, 'EPSG:4326', *dataset.bounds)
        image.update(cog=cog_name, cogSha256=sha(OUTPUT / cog_name), registeredPreview=png.name,
                     warp={'sourceCrs': 'EPSG:3005', 'displayCrs': 'EPSG:3857', 'resolutionMetres': 2000,
                           'bounds': [west, south, east, north], 'independentAccuracyEstablished': False})
        add_layer(project, {'id': stable_id(image['mapId']), 'name': f"Original {image['mapId']} drawing — preliminary alignment", 'type': 'image',
                  'source': {'type': 'image', 'url': 'data:image/png;base64,' + base64.b64encode(png.read_bytes()).decode(),
                             'coordinates': [[west, north], [east, north], [east, south], [west, south]]},
                  'visible': image['mapId'] == 'societies', 'opacity': .55, 'style': {},
                  'metadata': {'sourceKind': 'projected-georeferenced-image', 'bounds': [west, south, east, north],
                               'sourceImage': image['file'], 'sourceImageSha256': image['sha256'],
                               'gcps': [{'px': p['pixel'][0], 'py': p['pixel'][1], 'lng': p['longitudeLatitude'][0], 'lat': p['longitudeLatitude'][1]} for p in image['controls']],
                               'registration': image['warp'], 'copyright': 'Original Ministry of Health cartography, published by BC Auditor General, March 1998.'}})
    add_layer(project, {'id': stable_id('lines'), 'name': 'Registered society boundary vectors', 'type': 'geojson', 'source': {'type': 'geojson'},
              'visible': True, 'opacity': 1, 'style': {'strokeColor': '#a0267c', 'strokeWidth': 1.5, 'fillOpacity': 0}, 'metadata': {},
              'geojson': {'type': 'FeatureCollection', 'features': [f for f in read(PUBLIC / 'registered-source-lines.geojson')['features'] if f['properties']['mapId'] == 'societies']}})
    estimates = read(PUBLIC / 'best-estimates.geojson')
    for category in ['boards', 'councils', 'societies']:
        collection = {**estimates, 'features': [feature for feature in estimates['features'] if feature['properties']['mapId'] == category]}
        add_layer(project, {'id': stable_id('estimate-' + category), 'name': f'Working estimates — {category} (unverified)',
                  'type': 'geojson', 'source': {'type': 'geojson'}, 'visible': False, 'opacity': 1,
                  'style': {'fillColor': '#b65c2b', 'fillOpacity': .3, 'strokeColor': '#a04b24', 'strokeWidth': 1},
                  'metadata': {'historicalBoundaryVerified': False}, 'geojson': collection})
    for key, filename, name in [('drawn', 'source-drawn-estimates.geojson', 'Source drawing estimates — all 52 (overlapping frameworks)'),
                               ('historical', 'statistical-region-estimates.geojson', '20 statistical illustrations — modern LHA aggregates'),
                               ('municipalities', 'display-municipalities.geojson', 'Current municipalities — comparison only'),
                               ('regionalDistricts', 'display-regional-districts.geojson', 'Current regional districts — comparison only'),
                               ('schoolDistricts', 'display-school-districts.geojson', 'Current school districts — comparison only')]:
        add_layer(project, {'id': stable_id(key), 'name': name, 'type': 'geojson', 'source': {'type': 'geojson'},
                  'visible': False, 'opacity': 1, 'geojson': read(PUBLIC / filename),
                  'metadata': {'historicalBoundaryVerified': False},
                  'style': {'fillOpacity': 0, 'strokeColor': '#a0267c' if key == 'drawn' else '#346975', 'strokeWidth': 1}})
    adjusted = read(PUBLIC / 'adjusted-source-traces.geojson')
    add_layer(project, {'id': stable_id('adjusted-traces'), 'name': 'Vancouver/Richmond adjusted trace — provisional 5 km north',
              'type': 'geojson', 'source': {'type': 'geojson'}, 'visible': False, 'opacity': 1,
              'geojson': adjusted, 'metadata': {'historicalBoundaryVerified': False, 'northShiftMetres': 5000},
              'style': {'fillColor': '#c17522', 'fillOpacity': .2, 'strokeColor': '#a44c08', 'strokeWidth': 2}})
    project['metadata'].update(preparedOn='2026-10-31', evidenceStatus='Preliminary, three-control registration; no independent accuracy established.',
                               sourceSha256=controls['sourceSha256'], georeferencingImages=images)
    save(OUTPUT / 'image-manifest.json', manifest)
    view.project = project
    view.save_project(str(OUTPUT / 'health-map-review.geolibre'))
    # Keep SDK-authored data, with compact serialization for a downloadable asset.
    project_path = OUTPUT / 'health-map-review.geolibre'
    project_path.write_text(json.dumps(read(project_path), ensure_ascii=False, separators=(',', ':')) + '\n')
    view.to_html(str(OUTPUT / 'health-map-review.html'), title='PofBC — GeoLibre historical-map alignment review')
    # Keep a usable path when a browser blocks third-party storage in the iframe.
    # The SDK-generated project bridge and destination origin remain unchanged.
    html_path = OUTPUT / 'health-map-review.html'
    html = html_path.read_text()
    actions = '''<nav id="geolibre-actions" aria-label="Open the GeoLibre project"><strong>PofBC · GeoLibre alignment review</strong><a href="health-map-review.geolibre" download>Download project</a><a href="https://web.geolibre.app/" target="_blank" rel="noreferrer">Open GeoLibre app ↗</a><span>If the embedded map does not load, download the project and open it in GeoLibre: Project → Open from → File.</span></nav>'''
    html = html.replace('</head>', '<style>body{display:flex;flex-direction:column}#geolibre-actions{display:flex;flex-wrap:wrap;align-items:center;gap:10px 20px;padding:12px 16px;background:#f5f3ef;color:#182b3a;font:13px/1.5 system-ui,sans-serif}#geolibre-actions a{color:inherit}#geolibre-actions span{flex-basis:100%}#geolibre-frame{flex:1;min-height:300px}</style></head>')
    html = html.replace('<body>', '<body>' + actions)
    html_path.write_text(html)
    # Verify the delivered file through GeoLibre's own loader.
    reloaded = Map()
    reloaded.load_project(str(OUTPUT / 'health-map-review.geolibre'))
    summary = describe_project(reloaded.to_project())
    for layer in summary['layers']:
        if isinstance(layer.get('source'), str) and layer['source'].startswith('data:'):
            layer['source'] = '[embedded registered PNG]'
    save(OUTPUT / 'project-summary.json', summary)
    # A focused workspace opens with the reference map and working trace visible.
    index = read(PUBLIC / 'estimates-index.json')
    review = index['alignmentReviews']['vancouver-richmond-health-board']
    bundle = read(PUBLIC / review['workingAlignment']['downloadFile'])
    local = Map(center=(-123.15, 49.23), zoom=10, basemap=None)
    local_project = local.to_project()
    local_project.update(name='Vancouver/Richmond — reference map and provisional trace', basemapStyleUrl='', basemapVisible=False)
    layers = [('context', 'Current coastal context', read(PUBLIC / 'display-ha.geojson'), True, '#d7ddd5', '#82978b', .7),
              ('reference', 'Current Vancouver + Richmond reference boundaries', {'type': 'FeatureCollection', 'features': [f for f in bundle['features'] if f['properties']['layerRole'] == 'current-reference']}, True, '#2393a5', '#087c91', .2),
              ('original', 'Original trace — global registration', {'type': 'FeatureCollection', 'features': [f for f in bundle['features'] if f['properties']['layerRole'] == 'original-trace']}, False, '#b33378', '#ad256d', 0),
              ('adjusted', 'Working trace — provisional 5 km north', adjusted, True, '#c17522', '#a44c08', .25)]
    for key, name, collection, visible, fill, stroke, opacity in layers:
        add_layer(local_project, {'id': stable_id('vancouver-richmond-' + key), 'name': name, 'type': 'geojson',
                  'source': {'type': 'geojson'}, 'visible': visible, 'opacity': 1, 'geojson': collection,
                  'style': {'fillColor': fill, 'fillOpacity': opacity, 'strokeColor': stroke, 'strokeWidth': 1.5},
                  'metadata': {'historicalBoundaryVerified': False, 'layerRole': key}})
    local_project['metadata'].update(northShiftMetres=review['workingAlignment']['northShiftMetres'],
                                      alignmentStatus='provisional-local-display', globalRegistrationChanged=False,
                                      sourceMapUrl=bundle['metadata']['originalMapUrl'], referenceLicense=bundle['metadata']['referenceLicense'])
    local.project = local_project
    local_path = OUTPUT / 'vancouver-richmond-alignment.geolibre'
    local.save_project(str(local_path))
    local_path.write_text(json.dumps(read(local_path), ensure_ascii=False, separators=(',', ':')) + '\n')
    checked_local = Map()
    checked_local.load_project(str(local_path))
    if len(checked_local.to_project()['layers']) != 4:
        raise ValueError('Local GeoLibre alignment workspace did not round-trip')
    save(OUTPUT / 'vancouver-richmond-reference-and-traces.geojson', bundle)
    (OUTPUT / 'vancouver-richmond-source-detail.png').write_bytes((PUBLIC / 'vancouver-richmond-source-detail.png').read_bytes())
    readme = '''PofBC / GeoLibre alignment review

Open health-map-review.geolibre in GeoLibre, or health-map-review.html in a browser with internet access to load the GeoLibre viewer. Project layers and rendered images are embedded; original institutional map rights and modern-data licences remain applicable.

For each map, open the matching *-source.png in GeoLibre Processing > GeoLibre toolbox > Raster > Georeferencing, then import its *-gcps.csv. Pixel coordinates are specific to that exact crop and resolution. Do not import the CSV against a resized image or the full PDF page. The manifest records dimensions, crop origin and checksums. If the embedded viewer cannot load, use the direct app link and open the downloaded project through Project > Open from > File.

Add independently identifiable physical landmarks across the map and held-out checkpoints. Never use the modern administrative edges under test as fitting controls. Export the edited GCP CSV and import it as a proposal with scripts/import_health_gcps.py; the active baseline is not overwritten automatically.

Current controls: three per main map. Affine is mathematically possible; polynomial needs six and TPS at least four independently identified points. A zero three-point fit residual is not accuracy. Insets and the twenty-region statistical map remain separate pending registrations.

IMPORTANT: GeoLibre's quick overlay fits longitude/latitude. The delivered working rasters instead fit in BC Albers (EPSG:3005) before GDAL reprojection to Web Mercator (EPSG:3857). This preserves the established projected-map baseline. A native geographic affine export is not a drop-in equivalent across the whole province. The GeoLibre fit report is diagnostic, not an accuracy finding.

The project also contains hidden working-estimate layers for 11 boards, 34 council/map labels and 7 societies, 52 independent source-drawing approximations, 20 separate statistical illustrations, current municipal, regional-district and school-district comparisons, and the provisional locally adjusted Vancouver/Richmond trace. Enable one framework at a time. The statistical illustration is a modern-LHA aggregate, not a registered historical statistical map. None is verified historical legal GIS.

Open vancouver-richmond-alignment.geolibre for a focused four-layer workspace: current coastal context, the seven current reference LHAs, the original trace and the working trace shifted 5 km north in BC Albers. Current reference and adjusted trace start visible. The local translation is an explicit provisional display choice; the original global controls are retained. The reference-and-traces GeoJSON and original source inset are included alongside the project.

The *-registered.tif files are actual Cloud-Optimized GeoTIFFs with CRS, transform and provenance tags. A projected warp and opening a project do not themselves improve or legally verify a boundary. Review all assumptions and remaining tasks in PofBC's research list.
'''
    (OUTPUT / 'README.txt').write_text(readme)
    with zipfile.ZipFile(PUBLIC / 'health-geolibre-review.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUTPUT.iterdir()):
            if path.is_file():
                archive.write(path, path.name)
    print(f'GeoLibre {geolibre.__version__}: 3 original image/CSV pairs, 3 COGs, {len(project["layers"])} embedded layers, project and HTML exported.')


if __name__ == '__main__':
    main()
