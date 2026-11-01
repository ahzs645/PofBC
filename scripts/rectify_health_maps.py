#!/usr/bin/env python3
"""Register OAG main-map vectors to the modern BC comparison layers, offline.

Dependencies: numpy, shapely>=2, pyproj, pymupdf. Run from any directory.
Edit the reviewed page controls/path assignments in rectification-controls.json.
This is an exploratory cartographic comparison, never a legal boundary finding.
"""
import hashlib
import json
import argparse
from pathlib import Path

import fitz
import numpy as np
import shapely
from pyproj import Transformer
from shapely.affinity import affine_transform, translate
from shapely.geometry import LineString, MultiLineString, Polygon, mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'public/health-geography'
RESEARCH = ROOT / 'research/health-geography'
TO_METRES = Transformer.from_crs(4326, 3005, always_xy=True).transform
TO_GEO = Transformer.from_crs(3005, 4326, always_xy=True).transform


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    if path.suffix == '.geojson':
        def rounded(value):
            if isinstance(value, dict):
                return {k: rounded(v) for k, v in value.items()}
            if isinstance(value, (tuple, list)):
                return [rounded(v) for v in value]
            return round(value, 6) if isinstance(value, float) else value
        data = rounded(data)
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n')
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def transform(function, geometry):
    return shapely.transform(geometry, function, interleaved=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_affine(controls):
    page = np.array([[*c['pagePoint'], 1] for c in controls])
    target = np.array([TO_METRES(*c['longitudeLatitude']) for c in controls])
    if np.linalg.matrix_rank(page) < 3:
        raise ValueError('Registration controls must not be collinear')
    # Sub-millimetre coefficient rounding avoids platform BLAS serialization noise;
    # it is far below the map's kilometre-scale cartographic uncertainty.
    coefficients = np.round(np.linalg.lstsq(page, target, rcond=None)[0], 6)
    residuals = np.linalg.norm(page @ coefficients - target, axis=1)
    a, b, offset = coefficients
    return [float(v) for v in [a[0], b[0], a[1], b[1], offset[0], offset[1]]], [round(float(v), 6) for v in residuals]


def drawing_polygon(drawing):
    rings, ring = [], []
    for item in drawing['items']:
        if item[0] != 'l':
            raise ValueError('Unexpected non-line command in a selected source polygon')
        start, end = tuple(item[1]), tuple(item[2])
        if ring and np.linalg.norm(np.array(start) - ring[-1]) > .02:
            if len(ring) > 3:
                rings.append(shapely.make_valid(Polygon(ring)))
            ring = []
        if not ring:
            ring = [start]
        ring.append(end)
    if len(ring) > 3:
        rings.append(shapely.make_valid(Polygon(ring)))
    result = shapely.make_valid(unary_union(rings))
    if result.geom_type == 'GeometryCollection':
        result = unary_union([g for g in shapely.get_parts(result) if g.geom_type in ('Polygon', 'MultiPolygon')])
    if result.is_empty or result.geom_type not in ('Polygon', 'MultiPolygon'):
        raise ValueError('Selected drawing did not yield a polygon')
    return result


def score(source, candidate):
    intersection = source.intersection(candidate).area
    return {'iou': round(intersection / source.union(candidate).area, 4),
            'sourceCovered': round(intersection / source.area, 4),
            'candidateCovered': round(intersection / candidate.area, 4)}


def coast_check(source, target):
    # Independent of the three corner controls. Distances also include coastline
    # generalization and differences in the reference layer's shoreline depiction.
    distances = [source.boundary.interpolate(i / 500, normalized=True).distance(target.boundary)
                 for i in range(500)]
    return {'medianMetres': round(float(np.median(distances))),
            'p95Metres': round(float(np.quantile(distances, .95))),
            'maxMetres': round(max(distances)), 'sampleCount': len(distances)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls', type=Path, default=RESEARCH / 'rectification-controls.json')
    parser.add_argument('--out-dir', type=Path, default=PUBLIC)
    args = parser.parse_args()
    controls = read(args.controls)
    output = args.out_dir
    if controls.get('candidateOnly') and output.resolve() == PUBLIC.resolve():
        parser.error('A GeoLibre control proposal requires a separate --out-dir')
    output.mkdir(parents=True, exist_ok=True)
    for path, expected in [(PUBLIC / controls['sourcePdf'], controls['sourceSha256']),
                           (PUBLIC / controls['referenceFile'], controls['referenceSha256'])]:
        if sha(path) != expected:
            raise ValueError(f'Input checksum changed: {path.name}; review controls before rebuilding')
    comparison = read(PUBLIC / 'boundary-comparison.json')
    layers = {key: [(f, transform(TO_METRES, shape(f['geometry'])))
                    for f in read(PUBLIC / value['file'])['features']]
              for key, value in comparison['datasets'].items()}
    modern = unary_union([geometry for _, geometry in layers['ha']])
    island = max((g for g in modern.geoms if -127 < transform(TO_GEO, g.centroid).x < -124
                  and 48 < transform(TO_GEO, g.centroid).y < 51), key=lambda g: g.area)
    source_doc = fitz.open(PUBLIC / controls['sourcePdf'])
    lines, areas, results, registrations = [], [], [], []
    for page in controls['pages']:
        drawings = source_doc[page['pdfPage'] - 1].get_drawings()
        affine, residuals = fit_affine(page['controls'])
        registration = {**page, 'affineToEpsg3005': affine, 'controlFitResidualMetres': residuals,
                        'independentRegistrationRmse': None}
        if page['mapId'] == 'boards':
            vi = unary_union([drawing_polygon(drawings[i]) for i in [52, 55, 202]])
            registration['vancouverIslandCoastCheck'] = coast_check(affine_transform(vi, affine), island)
        registrations.append(registration)
        x0, y0, x1, y1 = page['mainMapBounds']
        segments = []
        for drawing in drawings:
            bounds = drawing['rect']
            if not (bounds.x0 >= x0 and bounds.y0 >= y0 and bounds.x1 <= x1 and bounds.y1 <= y1):
                continue
            grey_fill = drawing['fill'] and .7 < drawing['fill'][0] < .9
            thin_stroke = drawing['type'] == 's' and drawing['width'] < .04
            if grey_fill or thin_stroke:
                segments.extend([tuple(item[1]), tuple(item[2])] for item in drawing['items'] if item[0] == 'l')
        line_geometry = transform(TO_GEO, affine_transform(MultiLineString(segments), affine))
        lines.append({'type': 'Feature', 'properties': {'mapId': page['mapId'], 'pdfPage': page['pdfPage'],
                      'geometryStatus': 'registered-source-drawing', 'insetsIncluded': False}, 'geometry': mapping(line_geometry)})
        for entry in page['areaDrawings']:
            original = unary_union([drawing_polygon(drawings[i]) for i in entry['drawingIndices']])
            for i in entry['subtractDrawingIndices']:
                original = original.difference(drawing_polygon(drawings[i]))
            registered = shapely.make_valid(affine_transform(original, affine))
            match = next(row for row in comparison['bodyMatches'] if row['bodyId'] == entry['areaId'])
            modern_codes = set(match['candidateLhaCodes'])
            candidate = unary_union([g for f, g in layers['lha'] if f['properties']['code'] in modern_codes])
            metrics = score(registered, candidate)
            radius = controls['sensitivityMetres']
            sensitivity = [score(translate(registered, xoff=radius * np.cos(angle), yoff=radius * np.sin(angle)), candidate)['iou']
                           for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False)] + [metrics['iou']]
            best = {}
            for layer, features in layers.items():
                ranked = sorted([(score(registered, g)['iou'], f['properties']['code'], f['properties']['name'])
                                 for f, g in features], reverse=True)
                best[layer] = {'code': ranked[0][1], 'name': ranked[0][2], 'iou': ranked[0][0]}
            small = registered.area < 2_000_000_000
            verdict = ('detail-limited' if small else 'close-cartographic-fit' if min(sensitivity) >= .8
                       else 'partial-cartographic-fit' if metrics['iou'] >= .65 else 'poor-cartographic-fit')
            result = {**entry, 'mapId': page['mapId'], 'metrics': metrics,
                      'translationSensitivity': {'radiusMetres': radius, 'minIou': min(sensitivity), 'maxIou': max(sensitivity),
                                                'interpretation': 'Eight fixed translation scenarios, not a statistical confidence interval or a complete error model.'},
                      'bestIndividualModernFeature': best, 'candidateLhaCodes': match['candidateLhaCodes'],
                      'sourceDrawingAreaKm2': round(registered.area / 1e6), 'verdict': verdict,
                      'boundaryIdentityVerified': False,
                      'reuse': 'Use predefined modern polygons only as an explicitly approximate display candidate; retain the registered drawing and legal-source caveats.'}
            results.append(result)
            areas.append({'type': 'Feature', 'properties': {'code': entry['areaId'], 'name': match['sourceLabel'],
                          'mapId': page['mapId'], 'geometryStatus': 'registered-source-drawing', 'boundaryIdentityVerified': False},
                          'geometry': mapping(transform(TO_GEO, registered))})
    datasets = {}
    for key, features in [('registeredLines', lines), ('registeredAreas', areas)]:
        filename = {'registeredLines': 'registered-source-lines.geojson', 'registeredAreas': 'registered-source-areas.geojson'}[key]
        write(output / filename, {'type': 'FeatureCollection', 'metadata': {'coordinateSystem': 'EPSG:4326',
              'geometryStatus': 'registered-source-drawing', 'sourceSha256': controls['sourceSha256']}, 'features': features})
        datasets[key] = {'file': filename, 'featureCount': len(features), 'sha256': sha(output / filename)}
    report = {'schemaVersion': 1, 'preparedOn': '2026-10-31', 'method': controls['method'],
              'sourceSha256': controls['sourceSha256'], 'referenceSha256': controls['referenceSha256'],
              'projectedCrs': controls['projectedCrs'], 'controlLimitation': controls['controlLimitation'],
              'limitations': [controls['deferred'], 'All path-to-area assignments are preliminary and require independent review, especially islands and metropolitan detail.',
                             'Overlap measures registered publication artwork against simplified modern comparison polygons, not recovered historical legal GIS.',
                             'All source maps retain their 1997/98 publication context. Alignment does not establish an unchanged territory through 2001.',
                             'Only the three OAG administrative main maps are registered. The separate twenty-region Statistics Canada map and all enlarged insets are not registered.',
                             '15 km translation sensitivity omits rotation, scale, local distortion, source-generalization and path-assignment errors; high IoU can conceal important local differences.'],
              'classificationRule': 'Under 2,000 km²: detail-limited. Otherwise close if all 15 km translation scenarios have IoU >= 0.80; partial if nominal IoU >= 0.65; poor otherwise. These are exploratory display triage rules, not legal acceptance thresholds.',
              'datasets': datasets, 'registrations': registrations, 'comparisons': results}
    if controls.get('candidateOnly'):
        report.update(candidateOnly=True, proposal=controls['proposal'])
    write(output / 'rectification.json', report)
    if output.resolve() == PUBLIC.resolve():
        write(RESEARCH / 'rectification-results.json', report)
    print('Initial registration: 3 main-map line layers and', len(results), 'regional area drawings. Extended council estimates are built separately.')
    for result in results:
        print(result['areaId'], result['metrics']['iou'], result['verdict'])


if __name__ == '__main__':
    main()
