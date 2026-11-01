#!/usr/bin/env python3
"""Build a labelled working estimate for every mapped historical health area.

Inputs are explicit source-space tracing/choice files and cached offline layers.
This never promotes a drawing or a modern proxy to a verified legal territory.
"""
import csv
from collections import Counter
from pathlib import Path

import fitz
import numpy as np
import rasterio.features
import shapely
from affine import Affine
from PIL import Image, ImageDraw
from scipy.ndimage import binary_closing, label
from shapely.affinity import affine_transform, translate
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import unary_union

from rectify_health_maps import PUBLIC, RESEARCH, TO_GEO, TO_METRES, coast_check, drawing_polygon, fit_affine, read, score, sha, transform, write


def polygonal(geometry):
    if geometry.geom_type in ('Polygon', 'MultiPolygon'):
        return geometry
    return unary_union([part for part in geometry.geoms if part.geom_type in ('Polygon', 'MultiPolygon')])


def trace_councils(settings, controls, province):
    pdf = PUBLIC / 'maps/BC-health-area-maps-1997-98.pdf'
    if sha(pdf) != settings['sourcePdfSha256']:
        raise ValueError('Source PDF changed; review tracing seeds and path indices')
    document = fitz.open(pdf)
    drawings = document[settings['pdfPage'] - 1].get_drawings()
    x0, y0, x1, y1 = settings['bounds']
    scale = settings['pixelsPerPoint']
    width, height = int((x1 - x0) * scale), int((y1 - y0) * scale)
    ink = Image.new('L', (width, height), 0)
    pen = ImageDraw.Draw(ink)

    def pixel(point):
        return ((point[0] - x0) * scale, (point[1] - y0) * scale)

    for drawing in drawings:
        bounds = drawing['rect']
        if not (x0 <= bounds.x0 and y0 <= bounds.y0 and bounds.x1 <= x1 and bounds.y1 <= y1):
            continue
        grey = drawing['fill'] and .7 < drawing['fill'][0] < .9
        thin = drawing['type'] == 's' and drawing['width'] < .04
        if grey:
            geometry = drawing_polygon(drawing)
            parts = [geometry] if geometry.geom_type == 'Polygon' else geometry.geoms
            for part in parts:
                for ring in [part.exterior, *part.interiors]:
                    pen.line([pixel(point) for point in ring.coords], fill=255, width=settings['strokePixels'])
        elif thin:
            for item in drawing['items']:
                if item[0] == 'l':
                    pen.line([pixel(tuple(item[1])), pixel(tuple(item[2]))], fill=255, width=settings['strokePixels'])
    # Only source-space local gaps are closed; modern administrative edges never
    # enter the extraction. Gray fill's implicit closing edges are retained.
    closed = binary_closing(np.array(ink) > 0, structure=np.ones((settings['closingPixels'], settings['closingPixels'])))
    cells, count = label(~closed)
    seeds = {int(number): points.copy() for number, points in settings['seedPagePoints'].items()}
    for number, indices in settings['componentSeedFromDrawing'].items():
        seeds[int(number)] = [list(drawing_polygon(drawings[index]).representative_point().coords)[0] for index in indices]
    if set(seeds) != set(range(1, 35)):
        raise ValueError('Every one of the 34 printed council labels needs a source seed')
    ownership = {}
    selected_cells = {}
    for number, points in seeds.items():
        selected_cells[number] = set()
        for point in points:
            col, row = [int(value) for value in pixel(point)]
            if not (0 <= row < height and 0 <= col < width):
                raise ValueError(f'Source seed is outside map: {number}')
            cell = int(cells[row, col])
            if not cell:
                raise ValueError(f'Source seed lies on a drawn edge: {number}')
            if cell in ownership and ownership[cell] != number:
                raise ValueError(f'Two labels merged into one source cell: {ownership[cell]}, {number}')
            ownership[cell] = number
            selected_cells[number].add(cell)
    page_transform = Affine(1 / scale, 0, x0, 0, 1 / scale, y0)
    affine, _ = fit_affine(controls['controls'])
    results = {}
    for number, ids in selected_cells.items():
        mask = np.isin(cells, list(ids))
        parts = [shape(geometry) for geometry, value in rasterio.features.shapes(mask.astype('uint8'), mask=mask, transform=page_transform) if value]
        source = unary_union(parts).simplify(.08, preserve_topology=True)
        for index in settings['extraFilledDrawings'].get(str(number), []):
            source = source.union(drawing_polygon(drawings[index]))
        # Preserve the source footprint for independent comparison. Clipping it
        # to modern land can conceal coastal displacement and inflate coverage.
        projected = polygonal(affine_transform(source, affine))
        if projected.is_empty or projected.area < 1_000_000:
            raise ValueError(f'Implausible empty/tiny council trace: {number}')
        results[number] = (projected, {'sourceCellIds': sorted(ids), 'extraFilledDrawings': settings['extraFilledDrawings'].get(str(number), []),
                                      'sourceSeedPoints': seeds[number], 'clippedToModernCoverage': False,
                                      'sourceCoverage': 'Generalized source footprint, without modern-land clipping; maritime legal limits are not reconstructed.'})
    return results


def feature(code, name, map_id, geometry, **properties):
    if geometry.is_empty or geometry.geom_type not in ('Polygon', 'MultiPolygon') or not geometry.is_valid:
        raise ValueError(f'Invalid estimate geometry: {code}')
    # Normalize topology at the delivered six-decimal coordinate precision.
    # Independently rounded rings can otherwise cross at sub-metre slivers.
    geographic = polygonal(shapely.set_precision(shapely.make_valid(transform(TO_GEO, geometry)), 1e-6))
    if geographic.is_empty or not geographic.is_valid:
        raise ValueError(f'Invalid delivered estimate geometry: {code}')
    return {'type': 'Feature', 'properties': {'code': code, 'name': name, 'mapId': map_id,
            'geometryStatus': 'historical-estimate', 'boundaryIdentityVerified': False, **properties},
            'geometry': mapping(geographic)}


def main():
    catalogue = read(PUBLIC / 'catalogue.json')
    candidates = read(PUBLIC / 'boundary-comparison.json')
    controls = read(RESEARCH / 'rectification-controls.json')
    settings = read(RESEARCH / 'council-tracing.json')
    decisions = read(RESEARCH / 'estimate-decisions.json')
    definitions = read(RESEARCH / 'boundary-definition-evidence.json')
    lha = read(PUBLIC / 'display-lha.geojson')
    lha_geometry = {f['properties']['code']: transform(TO_METRES, shape(f['geometry'])) for f in lha['features']}
    province = unary_union([transform(TO_METRES, shape(f['geometry'])) for f in read(PUBLIC / 'display-ha.geojson')['features']])
    traces = trace_councils(settings, next(page for page in controls['pages'] if page['mapId'] == 'councils'), province)
    regional = {f['properties']['code']: transform(TO_METRES, shape(f['geometry'])) for f in read(PUBLIC / 'registered-source-areas.geojson')['features']}
    choices = {choice['areaId']: choice for choice in decisions['choices']}
    legal = {entry['areaId']: entry for entry in definitions['records']}
    map_ids = {3: 'boards', 4: 'councils', 5: 'societies'}
    rows = {(map_ids[int(row['mapId'].rsplit('-', 1)[1])], row['sourceLegendNumber']): row for row in candidates['bodyMatches']}
    if set(choices) != {area['id'] for area in catalogue['areas']}:
        raise ValueError('Estimate choices must cover exactly the original 52 map labels')
    comparison_layers = {}
    for key, dataset in {**candidates['datasets'], **{entry['id']: entry for entry in definitions['extraLayers']}}.items():
        comparison_layers[key] = [(f['properties'], transform(TO_METRES, shape(f['geometry']))) for f in read(PUBLIC / dataset['file'])['features']]
    source_features, best_features, assessments = [], [], []
    for area in catalogue['areas']:
        choice = choices[area['id']]
        candidate = rows[(area['mapId'], area['number'])]
        proxy = unary_union([lha_geometry[code] for code in candidate['candidateLhaCodes']])
        source, trace_info = traces[area['number']] if area['mapId'] == 'councils' else (polygonal(regional[area['id']]), {'clippedToModernCoverage': False, 'sourceCoverage': 'Full registered main-map footprint, without modern-land clipping; southern insets and some offshore detail remain unresolved.'})
        selected = polygonal(source.intersection(province)) if choice['method'] == 'source-drawn' else proxy
        # One explicit legal latitude constraint, supported independently by the
        # 1997 Snow Country schedule, bounds the northern edge of its estimate.
        if area['id'] == 'snow-country-health-council' and choice['method'] == 'source-drawn':
            # Densify the parallel before projection; a four-corner box would
            # replace its projected curve with a straight chord.
            southern_side = [(lon, 45) for lon in np.linspace(-142, -110, 129)]
            northern_side = [(lon, 57) for lon in np.linspace(-110, -142, 129)]
            selected = polygonal(selected.intersection(transform(TO_METRES, Polygon(southern_side + northern_side))))
        source_features.append(feature(area['id'], area['sourceLabel'], area['mapId'], source, method='source-drawn', confidence='low'))
        best_features.append(feature(area['id'], area['sourceLabel'], area['mapId'], selected, method=choice['method'], confidence=choice['confidence'], modernLhaCodes=[] if choice['method'] == 'source-drawn' else candidate['candidateLhaCodes']))
        matches = {}
        for layer, features in comparison_layers.items():
            ranked = []
            for props, current in features:
                if not source.intersects(current):
                    continue
                metrics = score(source, current)
                ranked.append({'code': props['code'], 'name': props['name'], **metrics})
            matches[layer] = sorted(ranked, key=lambda result: result['iou'], reverse=True)[:3]
        assessment = {**choice, 'name': area['sourceLabel'], 'mapId': area['mapId'], 'legendNumber': area['number'],
                      'geometryAvailable': True, 'sourceDrawnGeometryAvailable': True, 'modernLhaCodes': candidate['candidateLhaCodes'],
                      'sourceDrawingVsModernCandidate': score(source, proxy), 'currentBoundaryScreening': matches,
                      'screeningCaveat': 'Scores compare the independently traced source drawing with current geometries. They are not scores of legal identity; marine depiction and registration affect them.',
                      'definition': legal.get(area['id']), 'trace': trace_info,
                      'estimatedAreaKm2': round(selected.area / 1e6),
                      'remaining': ('Check the historical service-area agreement and its geographic schedules.' if area['mapId'] == 'societies'
                                    else 'Trace the dated survey/watershed/municipal references and reconcile intervening amendments; keep source identity gaps explicit.')}
        assessments.append(assessment)
    # A separate statistical illustration, with every modern LHA assigned once.
    statistical_features, statistical_rows = [], []
    legend = read(RESEARCH / 'statcan-2000-map.json')['region_legend']
    flat_codes = [code for codes in decisions['statisticalLhaCodes'].values() for code in codes]
    if Counter(flat_codes) != Counter(lha_geometry.keys()):
        raise ValueError('The statistical illustration must cover each modern LHA once')
    for entry in legend:
        code = '59' + entry['code']
        codes = decisions['statisticalLhaCodes'][code]
        geometry = unary_union([lha_geometry[c] for c in codes])
        statistical_features.append(feature(code, entry['name'], 'regions-2000', geometry, method='modern-statistical-aggregate', confidence='low', modernLhaCodes=codes))
        statistical_rows.append({'code': code, 'name': entry['name'], 'modernLhaCodes': codes, 'method': 'modern-statistical-aggregate', 'confidence': 'low', 'boundaryIdentityVerified': False})
    datasets = {}
    for key, filename, features in [('estimates', 'best-estimates.geojson', best_features), ('drawn', 'source-drawn-estimates.geojson', source_features), ('historical', 'statistical-region-estimates.geojson', statistical_features)]:
        write(PUBLIC / filename, {'type': 'FeatureCollection', 'metadata': {'historicalBoundaryVerified': False,
              'sourceFootprintsClippedToModernCoverage': False if key == 'drawn' else None,
              'purpose': 'Labelled working estimates; not certified historical GIS', 'coordinateSystem': 'EPSG:4326'}, 'features': features})
        datasets[key] = {'file': filename, 'featureCount': len(features), 'sha256': sha(PUBLIC / filename)}
    for entry in definitions['extraLayers']:
        if sha(PUBLIC / entry['file']) != entry['sha256']:
            raise ValueError(f'Additional comparison layer changed: {entry["id"]}')
        datasets[entry['id']] = {key: entry[key] for key in ['file', 'featureCount', 'sha256']}
    summary = {'administrativeAreas': len(best_features), 'sourceDrawnAreas': len(source_features), 'statisticalRegions': len(statistical_features),
               'writtenTerritoriesLocated': sum(not entry['relatedEntityOnly'] for entry in definitions['records']),
               'relatedCouncilDefinitions': sum(entry['relatedEntityOnly'] for entry in definitions['records']),
               'verifiedHistoricalBoundaries': 0, 'methods': dict(Counter(choice['method'] for choice in choices.values())),
               'comparisonFeatureCount': sum(len(features) for features in comparison_layers.values())}
    review_input = read(RESEARCH / 'vancouver-richmond-alignment-review.json')
    reviewed = next(row for row in assessments if row['areaId'] == review_input['areaId'])
    reviewed_source = transform(TO_METRES, shape(next(f for f in source_features if f['properties']['code'] == reviewed['areaId'])['geometry']))
    diagnostic_steps = []
    for northing in review_input['northShiftMetres']:
        shifted = translate(reviewed_source, yoff=northing)
        diagnostic_metrics = {}
        for layer, features in comparison_layers.items():
            selected_codes = reviewed['modernLhaCodes'] if layer == 'lha' else [entry['code'] for entry in reviewed['currentBoundaryScreening'][layer][:1]]
            selected_geometries = [geometry for props, geometry in features if props['code'] in selected_codes]
            diagnostic_metrics[layer] = score(shifted, unary_union(selected_geometries)) if selected_geometries else None
        diagnostic_steps.append({'northShiftMetres': northing,
                                 'geometry': feature(reviewed['areaId'], reviewed['name'], 'boards', shifted)['geometry'],
                                 'metricsByLayer': diagnostic_metrics})
    # A physical shoreline withheld from both fitting and the Vancouver/Richmond
    # candidate. Its coarse drawing also contributes generalization error.
    bowen_candidates = [part for part in province.geoms
                        if -123.42 < transform(TO_GEO, part.centroid).x < -123.3
                        and 49.33 < transform(TO_GEO, part.centroid).y < 49.42]
    bowen_reference = max(bowen_candidates, key=lambda part: part.area)
    # Preserve a readable, untouched source excerpt showing both printed 9s.
    with fitz.open(PUBLIC / 'maps/BC-health-area-maps-1997-98.pdf') as document:
        document[0].get_pixmap(matrix=fitz.Matrix(6, 6), clip=fitz.Rect(163, 499, 242, 552), alpha=False).save(PUBLIC / 'vancouver-richmond-source-detail.png')
        board_affine, _ = fit_affine(controls['pages'][0]['controls'])
        bowen_source = affine_transform(drawing_polygon(document[0].get_drawings()[79]), board_affine)
    physical_check = {'feature': 'Bowen Island outer shoreline', 'sourceDrawingIndex': 79,
                      'targetBasis': 'Largest isolated modern HA outer-coverage polygon with centroid in -123.42 to -123.30 longitude / 49.33 to 49.42 latitude; the Bowen Island landmass, not a health-area internal edge.',
                      'targetAreaKm2': round(bowen_reference.area / 1e6, 2),
                      'usedForFitting': False, 'independentOfVancouverRichmondCandidate': True,
                      'targetMinusSourceCentroidMetres': {'east': round(bowen_reference.centroid.x - bowen_source.centroid.x),
                                                         'north': round(bowen_reference.centroid.y - bowen_source.centroid.y)},
                      'scenarios': [{'northShiftMetres': northing, **coast_check(translate(bowen_source, yoff=northing), bowen_reference)} for northing in [0, 5000]],
                      'caveat': 'Shoreline distances and polygon centroids include source generalization and reference differences. This is a held-out physical check, not an independent registration RMSE or a calibrated local correction.'}
    alignment_reviews = {reviewed['areaId']: {**review_input, 'activeRegistrationChanged': False, 'steps': diagnostic_steps, 'physicalCheck': physical_check}}
    working = review_input.get('workingAlignment')
    adjusted_features = []
    if working and working['enabled']:
        active_step = next(step for step in diagnostic_steps if step['northShiftMetres'] == working['northShiftMetres'])
        if working['eastShiftMetres'] != 0:
            raise ValueError('The reviewed local alignment currently supports a northward translation only')
        adjusted = feature(reviewed['areaId'], reviewed['name'], 'boards',
                           translate(reviewed_source, yoff=working['northShiftMetres']),
                           method='provisional-local-alignment', northShiftMetres=working['northShiftMetres'],
                           eastShiftMetres=0, sourceFile='source-drawn-estimates.geojson')
        adjusted_features.append(adjusted)
        reviewed['workingAlignment'] = working
        reviewed['workingDrawingVsModernCandidate'] = active_step['metricsByLayer']['lha']
        alignment_reviews[reviewed['areaId']]['localDisplayAlignmentApplied'] = True
        original = next(f for f in source_features if f['properties']['code'] == reviewed['areaId'])
        selected_reference = [f for f in lha['features'] if f['properties']['code'] in reviewed['modernLhaCodes']]
        export_features = [
            {**f, 'id': f"{f['properties']['code']}--{role}", 'properties': {**f['properties'], 'layerRole': role}}
            for role, features in [('original-trace', [original]), ('adjusted-trace', [adjusted]), ('current-reference', selected_reference)]
            for f in features
        ]
        write(PUBLIC / working['downloadFile'], {'type': 'FeatureCollection',
              'metadata': {'purpose': 'Current reference geography plus original and provisionally adjusted historical traces',
                           'coordinateSystem': 'EPSG:4326', 'translationCrs': 'EPSG:3005',
                           'northShiftMetres': working['northShiftMetres'], 'historicalBoundaryVerified': False,
                           'originalMapUrl': 'https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19980301-review-governance-and-accountability.pdf#page=28',
                           'referenceLicense': 'Open Government Licence – British Columbia'}, 'features': export_features})
    write(PUBLIC / 'adjusted-source-traces.geojson', {'type': 'FeatureCollection',
          'metadata': {'purpose': 'Explicit provisional local display alignments', 'historicalBoundaryVerified': False,
                       'translationCrs': 'EPSG:3005', 'coordinateSystem': 'EPSG:4326'}, 'features': adjusted_features})
    datasets['adjusted'] = {'file': 'adjusted-source-traces.geojson', 'featureCount': len(adjusted_features),
                            'sha256': sha(PUBLIC / 'adjusted-source-traces.geojson')}
    result = {'schemaVersion': 1, 'reviewedOn': '2026-10-31', 'summary': summary, 'datasets': datasets,
              'alignmentReviews': alignment_reviews,
              'assessments': assessments, 'statisticalRegions': statistical_rows,
              'statisticalCaveat': decisions['statisticalCaveat'], 'extraLayers': definitions['extraLayers'],
              'sources': definitions['sources'], 'findings': definitions['findings'], 'tracing': settings,
              'limitations': ['All 52 administrative map labels now have an explicit working geometry; this does not verify their legal limits.',
                             'The 20 statistical illustrations are modern-LHA aggregates, kept separate from the 1995 legal board definitions.',
                             'Best estimates mix documented modern proxies with source-drawn approximations. Their uncertain edges can overlap; they are not a certified partition.',
                             'Drawing comparisons retain the full traced source footprint without modern-land clipping. Source-drawn best estimates alone are clipped for land display; historical marine jurisdiction remains unresolved.',
                             'Current municipalities, regional districts and school districts are similarity-screening references, not automatic substitutes for their historical versions.']}
    write(PUBLIC / 'estimates-index.json', result)
    write(RESEARCH / 'estimate-results.json', result)
    markdown = render_review(result)
    (PUBLIC / 'boundary-estimates.md').write_text(markdown)
    (RESEARCH / 'boundary-estimates.md').write_text(markdown)
    with (PUBLIC / 'estimate-catalogue.csv').open('w', newline='') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['area_id', 'name', 'framework', 'method', 'confidence', 'modern_lha_codes', 'legal_definition_heading', 'historical_boundary_verified', 'local_north_shift_metres', 'local_alignment_status'])
        for row in assessments:
            local = row.get('workingAlignment', {})
            writer.writerow([row['areaId'], row['name'], row['mapId'], row['method'], row['confidence'], ';'.join(row['modernLhaCodes']), (row['definition'] or {}).get('heading', ''), 'false', local.get('northShiftMetres', 0), local.get('status', '')])
        for row in statistical_rows:
            writer.writerow([row['code'], row['name'], 'statistical-regions', row['method'], row['confidence'], ';'.join(row['modernLhaCodes']), '', 'false', 0, ''])
    print(summary)
    for row in assessments:
        school = row['currentBoundaryScreening']['schoolDistricts'][:1]
        if school and school[0]['iou'] > .8:
            print('School-district screening:', row['name'], school[0]['name'], school[0]['iou'])


def render_review(result):
    """A reviewable inventory, with source locators and a decision for every area."""
    lines = ['# Historical BC health boundaries: working estimates', '',
             f"Reviewed {result['reviewedOn']}. All 52 administrative labels have a working geometry and a separate source-drawing approximation. The twenty statistical regions have modern-LHA illustrations. None is a verified historical legal polygon.", '',
             '## Other boundaries that help', '',
             'Screening uses 89 current local health areas, 16 service delivery areas, 5 health authorities, 28 regional districts, 160 municipalities and 59 geographic school districts. Each score compares an independently traced historical drawing with a current feature. It does not compare a selected proxy with itself.', '',
             'School districts have useful resemblance to several councils, including Arrow Lakes, Boundary, Quesnel, Sea to Sky, South Peace, Fort Nelson and Bulkley Valley. This supports further edge review; it does not establish unchanged historical school-district or health boundaries.', '',
             '## What defines the territories', '',
             'Original B.C. Reg. 293/2001 Schedule B supplies written descriptions for 11 boards and 33 councils. These use watershed divides, rivers, shorelines, cadastral district lots, survey plans, latitude/longitude and dated municipal boundaries. They postdate the 1997/98 map and require reconciliation with original orders and intervening amendments. M87/1997 is a partial amendment, not a complete schedule for all councils.', '',
             'M191/1997 contains the related Nisga’a council definition. Its identity with the map’s differently labelled authority remains unresolved. The seven societies still need operative service-area agreements and schedules.', '',
             '## Method and limits', '',
             'The three main maps use the existing three-control BC Albers affine registration. Council polygons are extracted from gray fill boundaries and thin black linework, excluding text. Rasterization is 12 pixels per PDF point, with a 3-pixel local gap closure. Source-space seeds separate all 34 labels; a few coastal island components use explicit extra paths/seeds. No modern internal administrative edge is used to extract these source polygons. Comparisons use the full source footprint, without modern-land clipping. Only the four source-drawn best estimates are clipped for land display. Marine jurisdiction is not reconstructed.', '',
             'Vancouver/Richmond correction: the earlier 29% comparison is withdrawn. Richmond main-map drawing 76 was omitted and incorrectly assigned to South Fraser. The corrected trace includes 76 and 193; South Fraser uses 198. The inset labels both Vancouver and Richmond with 9. A 5 km northward local display alignment is now applied to this trace following user review. The original global registration and source trace are retained. This is a provisional display choice; independent coastal controls and inset registration remain necessary.', '',
             'Working choices use 28 single modern LHAs, 20 modern combinations and four source-drawn estimates. Snow Country is additionally capped at the independently documented 57th parallel, densified before projection. Insets and fine offshore details remain unresolved. Mixed-source estimates can overlap; they are not an exclusive certified partition. Three fitting controls do not provide independent registration accuracy. Scores are cartographic similarity, not legal verification.', '',
             '## Source provenance', '']
    for source in result['sources']:
        lines.append(f"- [{source.get('title', source.get('id', source.get('file', 'Source')))}]({source.get('url', source.get('sourceUrl', ''))})")
    for layer in result['extraLayers']:
        lines.append(f"- Current {layer['id']}: {layer.get('sourceUrl', layer.get('url', ''))}; normalized snapshot SHA-256 `{layer['sha256']}`.")
    lines.extend(['', '## Area-by-area choices', ''])
    for area in result['assessments']:
        lines.extend([f"### {area['name']} · {area['mapId']} {area['legendNumber']}", '',
                      f"ID: `{area['areaId']}`. Choice: **{area['method']}**, {area['confidence']} confidence in display approximation. Historical legal boundary unverified.", '', area['reason'], '',
                      'Modern comparison LHA codes: ' + ', '.join(area['modernLhaCodes']) + '.', '',
                      f"Independent source drawing / modern combination overlap: {area['sourceDrawingVsModernCandidate']['iou']:.1%} intersection over union.", ''])
        definition = area['definition']
        if definition:
            lines.extend([f"Written record: [{definition['heading']}]({definition['sourceUrl']}). {definition['dateContext']}.", '', definition['summary'], ''])
            if definition['relatedEntityOnly']:
                lines.extend(['Related entity only: the Nisga’a map-label identity is unresolved.', ''])
            if definition.get('namedWaterFeatures'):
                lines.extend(['Water features to trace: ' + '; '.join(definition['namedWaterFeatures']) + '.', ''])
        else:
            lines.extend(['Written service-area agreement/schedule: still to obtain.', ''])
        for layer, matches in area['currentBoundaryScreening'].items():
            if matches:
                best = matches[0]
                lines.append(f"- Closest individual {layer}: {best['name']} ({best['code']}); {best['iou']:.1%} drawing IoU.")
        lines.extend(['', '**Remaining:** ' + area['remaining'], ''])
    lines.extend(['## Twenty separate statistical illustrations', '', result['statisticalCaveat'], ''])
    for region in result['statisticalRegions']:
        lines.append(f"- {region['code']} {region['name']}: modern LHAs {', '.join(region['modernLhaCodes'])}; low-confidence illustration, unverified historical edges.")
    lines.extend(['', '## Records still needed', '',
                  '1. Original historical GIS/cartographic files and source metadata for the 1997/98 maps; public/archival retrieval first, then focused Ministry of Health FOI if unavailable.',
                  '2. Dated survey-plan and cadastral edges, watershed delineations and historical municipal/electoral-area limits referred to by the orders. Seek survey registry, DataBC and archived local-government records before FOI.',
                  '3. Society service-area agreements and geographic schedules; ask successor health authorities and society/registry record custodians.',
                  '4. Nisga’a map-entity identity and its relationship to the statutory council; obtain documentary confirmation rather than infer identity from geography.',
                  '5. Operative 2002 coastal-transfer records and completed service/asset transaction records; seek public instruments and successor files, then scoped FOI for unavailable provincial records.',
                  '6. January 2000 statistical GIS and official crosswalk metadata; request from Statistics Canada/provincial statistical custodians. The modern-LHA illustration does not replace these files.',
                  '7. PGMaps snapshot provenance and exact original dataset versions; recover from repository history or the source custodian.', '',
                  'The detailed research register and unsent draft requests are in records-to-obtain.md. No FOI, fee, access outcome or record holding is implied by this list.', ''])
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
