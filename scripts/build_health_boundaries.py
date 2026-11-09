#!/usr/bin/env python3
"""Georectify the historical BC health maps and build organization boundaries.

One offline, deterministic pipeline:

1. Register every source map panel (three OAG 1997/98 exhibits with the board
   inset, and the Statistics Canada twenty-region map with its inset) to the
   modern LHA linework. Seeds give a starting position; an iterative
   closest-point fit then matches thousands of source boundary points to the
   coast, provincial border and LHA edges, with a cubic polynomial and a
   smoothed thin-plate spline for local distortion. Accuracy is measured on
   held-out map blocks the fit never saw.
2. Register each printed region (52 administrative labels, 20 statistical
   regions) and measure how much of every modern LHA it covers.
3. Combine those LHA shares with the reviewed decisions in
   research/health-geography/boundary-decisions.json into one boundary per
   organization, carrying its lineage (dates, names, 2001 successor).
4. Export the georectified source maps as vector overlays.

Dependencies: research/health-geography/requirements-boundaries.txt.
Run from any directory: python scripts/build_health_boundaries.py
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import fitz
import numpy as np
import shapely
from pyproj import Transformer
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import binary_closing, label
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point, Polygon, box, mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'public/health-geography'
RESEARCH = ROOT / 'research/health-geography'
LINEAGE = ROOT / 'research/history/bodies-health-lineage.json'
TO_METRES = Transformer.from_crs(4326, 3005, always_xy=True).transform
TO_GEO = Transformer.from_crs(3005, 4326, always_xy=True).transform
PREPARED_ON = '2026-11-09'


# ---------------------------------------------------------------- utilities

def read(path):
    return json.loads(Path(path).read_text())


def rounded(value, digits):
    if isinstance(value, dict):
        return {k: rounded(v, digits) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [rounded(v, digits) for v in value]
    return round(value, digits) if isinstance(value, float) else value


def write_json(path, data, compact=False, digits=None):
    if digits is not None:
        data = rounded(data, digits)
    text = json.dumps(data, ensure_ascii=False, separators=(',', ':') if compact else None,
                      indent=None if compact else 2, allow_nan=False)
    Path(path).write_text(text + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def project(geometry, function):
    return shapely.transform(geometry, function, interleaved=False)


def polygonal(geometry):
    geometry = shapely.make_valid(geometry)
    if geometry.geom_type in ('Polygon', 'MultiPolygon'):
        return geometry
    return unary_union([g for g in shapely.get_parts(geometry) if g.geom_type in ('Polygon', 'MultiPolygon')])


def densify(geometry, step):
    points = []
    for part in shapely.get_parts(geometry):
        if part.geom_type == 'Polygon':
            rings = [part.exterior, *part.interiors]
        else:
            rings = [part]
        for ring in rings:
            count = max(2, int(ring.length / step))
            points += [ring.interpolate(i / count, normalized=True).coords[0] for i in range(count)]
    return np.array(points)


def score(a, b):
    inter = a.intersection(b).area
    union = a.union(b).area
    return {'iou': round(inter / union, 4) if union else 0.0,
            'sourceCovered': round(inter / a.area, 4) if a.area else 0.0,
            'candidateCovered': round(inter / b.area, 4) if b.area else 0.0}


def clip_polygon(clip):
    include = unary_union([box(*rect) for rect in clip['include']])
    return include.difference(unary_union([box(*rect) for rect in clip['exclude']])) if clip['exclude'] else include


# ---------------------------------------------------------------- source paths

def path_rings(drawing):
    """Rings from a PyMuPDF drawing. Curves are flattened to their end points;
    at map scale the few quadratic segments are a fraction of a point long."""
    rings, ring = [], []
    for item in drawing['items']:
        kind = item[0]
        if kind == 're':
            r = item[1]
            rings.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
            continue
        if kind == 'l':
            start, end = tuple(item[1]), tuple(item[2])
        elif kind in ('c', 'qu'):
            points = item[1] if kind == 'qu' else item[1:]
            if kind == 'qu':
                points = [points.ul, points.ur, points.lr, points.ll]
            start, end = tuple(points[0]), tuple(points[-1])
        else:
            continue
        if ring and np.hypot(start[0] - ring[-1][0], start[1] - ring[-1][1]) > .02:
            rings.append(ring)
            ring = []
        if not ring:
            ring = [start]
        ring.append(end)
    if ring:
        rings.append(ring)
    return [r for r in rings if len(r) >= 2]


def drawing_polygon(drawing):
    parts = [shapely.make_valid(Polygon(r)) for r in path_rings(drawing) if len(r) > 3]
    return polygonal(unary_union(parts)) if parts else Polygon()


def drawing_lines(drawing):
    return [LineString(r) for r in path_rings(drawing)]


def is_glyph(drawing):
    fill = drawing.get('fill')
    return bool(fill) and max(fill) < .1


def colour_key(fill):
    return tuple(round(v, 2) for v in fill) if fill else None


def hex_colour(fill):
    return '#' + ''.join(f'{round(v * 255):02x}' for v in fill)


class SourcePage:
    def __init__(self, path, page):
        self.document = fitz.open(path)
        self.page = self.document[page - 1]
        self.drawings = self.page.get_drawings()

    def within(self, drawing, clip):
        r = drawing['rect']
        return clip.intersects(box(r.x0, r.y0, r.x1, r.y1))


def oag_boundary_lines(source, clip):
    """Grey/white region fills and thin black outlines; printed numbers excluded."""
    lines = []
    for drawing in source.drawings:
        if not source.within(drawing, clip) or is_glyph(drawing):
            continue
        thin = drawing['type'] == 's' and (drawing.get('width') or 0) < .1 and drawing.get('color') and max(drawing['color']) < .1
        if drawing.get('fill') or thin:
            lines += drawing_lines(drawing)
    return unary_union(lines).intersection(clip)


def statcan_region_fills(source, swatches):
    legend = {code: colour_key(source.drawings[index]['fill']) for code, index in swatches.items()}
    colours = set(legend.values())
    fills = defaultdict(list)
    for index, drawing in enumerate(source.drawings):
        if index in swatches.values():
            continue
        key = colour_key(drawing.get('fill'))
        if key in colours:
            fills[key].append(drawing_polygon(drawing))
    return legend, {key: polygonal(unary_union(parts)) for key, parts in fills.items()}


def statcan_boundary_lines(fills, clip):
    return unary_union([g.boundary for g in fills.values()]).intersection(clip)


# ---------------------------------------------------------------- registration

def terms(xy, order):
    x, y = xy[:, 0], xy[:, 1]
    return np.stack([x ** i * y ** j for i in range(order + 1) for j in range(order + 1 - i)], 1)


class Registration:
    """Page points -> EPSG:3005 metres: polynomial plus optional smoothed TPS residual."""

    def __init__(self, order, coef, mu, sd, rbf=None):
        self.order, self.coef, self.mu, self.sd, self.rbf = order, coef, mu, sd, rbf

    def __call__(self, points):
        points = np.asarray(points, dtype=float).reshape(-1, 2)
        if not len(points):
            return points
        out = terms((points - self.mu) / self.sd, self.order) @ self.coef
        if self.rbf is not None:
            out = out + self.rbf(points)
        return out

    def geometry(self, geometry):
        # Map unique coordinates once so closed rings stay exactly closed.
        def apply(points):
            unique, inverse = np.unique(points, axis=0, return_inverse=True)
            return self(unique)[inverse.reshape(-1)]
        return shapely.transform(geometry, apply)


class Target:
    def __init__(self, lha_geometries, step=300):
        self.edges = unary_union([g.boundary for g in lha_geometries])
        self.points = densify(self.edges, step)
        self.tree = cKDTree(self.points)

    def near(self, envelope):
        local = densify(self.edges.intersection(envelope), 150)
        return local, cKDTree(local)


def least_squares(source, target, order, mu, sd):
    return np.linalg.lstsq(terms((source - mu) / sd, order), target, rcond=None)[0]


def icp(points, model, target_points, tree, schedule, max_order):
    for order, thresholds in schedule:
        if order > max_order:
            break
        for threshold in thresholds:
            distance, index = tree.query(model(points))
            keep = distance <= threshold
            if keep.sum() < 50:
                raise ValueError('Registration lost its correspondences')
            model = Registration(order, least_squares(points[keep], target_points[index[keep]], order, model.mu, model.sd), model.mu, model.sd)
    return model


SCHEDULE = [(1, [15000, 10000, 6000, 4000, 3000, 2000]), (2, [2500, 2000, 1500, 1500]), (3, [1500, 1500, 1500, 1500])]
INSET_SCHEDULE = [(1, [6000, 4000, 3000, 2000, 1500, 1000, 800, 800]), (2, [800, 600, 600, 600])]


def fit_unit(unit, points, target_points, tree, initial=None, search=0, rng_seed=0):
    mu, sd = points.mean(0), points.std()
    if initial is None:
        seeds = np.array(unit['seeds'], dtype=float)
        page, metres = seeds[:, :2], np.array([TO_METRES(lon, lat) for lon, lat in seeds[:, 2:]])
        if len(seeds) == 2:
            # Similarity from two seeds; the page y axis points south.
            zp = complex(*(page[1] - page[0])); zp = complex(zp.real, -zp.imag)
            a = complex(*(metres[1] - metres[0])) / zp
            def similar(p):
                z = (p[:, 0] - page[0, 0]) - 1j * (p[:, 1] - page[0, 1])
                w = a * z + complex(*metres[0])
                return np.stack([w.real, w.imag], 1)
            model = Registration(1, least_squares(points, similar(points), 1, mu, sd), mu, sd)
        else:
            model = Registration(1, least_squares(page, metres, 1, mu, sd), mu, sd)
    else:
        model = Registration(1, least_squares(points, initial(points), 1, mu, sd), mu, sd)
    if search:
        sample = model(points[::10])
        best = max(((tree.query(sample + [dx, dy])[0] < 1500).mean(), dx, dy)
                   for dx in range(-search, search + 1, 3000) for dy in range(-search, search + 1, 3000))
        model.coef[0] += [best[1], best[2]]
    schedule = INSET_SCHEDULE if unit.get('inset') else SCHEDULE
    model = icp(points, model, target_points, tree, schedule, unit['order'])
    if unit.get('tps'):
        distance, index = tree.query(model(points))
        inliers = np.flatnonzero(distance < 2000)
        rng = np.random.default_rng(rng_seed)
        chosen = np.sort(rng.choice(inliers, min(2500, len(inliers)), replace=False))
        residual = target_points[index[chosen]] - model(points[chosen])
        model = Registration(model.order, model.coef, mu, sd,
                             RBFInterpolator(points[chosen], residual, kernel='thin_plate_spline', smoothing=1000, degree=1))
    return model


def residual_summary(distances):
    return {'medianMetres': round(float(np.median(distances))),
            'p90Metres': round(float(np.quantile(distances, .9))),
            'within1kmShare': round(float((distances < 1000).mean()), 3),
            'within3kmShare': round(float((distances < 3000).mean()), 3)}


def seed_affine(unit):
    seeds = np.array(unit['seeds'], dtype=float)
    page = np.c_[seeds[:, :2], np.ones(len(seeds))]
    metres = np.array([TO_METRES(lon, lat) for lon, lat in seeds[:, 2:]])
    coef = np.linalg.lstsq(page, metres, rcond=None)[0]
    return lambda p: np.c_[np.asarray(p), np.ones(len(p))] @ coef


def register_all(settings, sources, target):
    units, report = {}, []
    for unit in settings['units']:
        source = sources[(unit['source'], unit['page'])]
        clip = clip_polygon(unit['clip'])
        lines = oag_boundary_lines(source, clip) if unit['style'] == 'oag' else statcan_boundary_lines(source.statcan_fills, clip)
        points = densify(lines, .12 if not unit.get('inset') else .1)
        if unit.get('inset'):
            # The inset frame is a clipping edge, not geography.
            points = points[shapely.distance(clip.boundary, shapely.points(points)) > .4]
        initial = units[unit['initialFrom']]['model'] if unit.get('initialFrom') else None
        if unit.get('inset'):
            reach = (initial or seed_affine(unit))(np.array(clip.envelope.exterior.coords))
            envelope = box(*(reach.min(0) - 40000), *(reach.max(0) + 40000))
            target_points, tree = target.near(envelope)
        else:
            target_points, tree = target.points, target.tree
        model = fit_unit(unit, points, target_points, tree, initial=initial, search=unit.get('searchMetres', 0))
        fit_distance = tree.query(model(points))[0]
        # Blocked holdout: refit without one quarter of 25-point map blocks.
        block = ((points[:, 0] // 25).astype(int) + (points[:, 1] // 25).astype(int)) % 4 == 0
        holdout = fit_unit(unit, points[~block], target_points, tree, initial=initial, search=unit.get('searchMetres', 0), rng_seed=1)
        holdout_distance = tree.query(holdout(points[block]))[0]
        row = {'id': unit['id'], 'mapId': unit['mapId'], 'inset': bool(unit.get('inset')),
               'sourcePoints': int(len(points)), 'model': f"order-{unit['order']} polynomial" + (' + smoothed thin-plate spline' if unit.get('tps') else ''),
               'fit': residual_summary(fit_distance), 'heldOut': residual_summary(holdout_distance)}
        if 'seeds' in unit and len(unit['seeds']) >= 3:
            row['seedAffineBaseline'] = residual_summary(tree.query(seed_affine(unit)(points))[0])
        print(f"{unit['id']:24s} fit median {row['fit']['medianMetres']:5d} m · held-out median {row['heldOut']['medianMetres']:5d} m, p90 {row['heldOut']['p90Metres']:5d} m"
              + (f" (seed affine {row['seedAffineBaseline']['medianMetres']} m)" if 'seedAffineBaseline' in row else ''))
        units[unit['id']] = {'model': model, 'clip': clip, 'unit': unit}
        report.append(row)
    return units, report


# ---------------------------------------------------------------- region drawings

def trace_councils(source, settings):
    """Council polygons in page space, from the reviewed council-tracing seeds."""
    x0, y0, x1, y1 = settings['bounds']
    scale = settings['pixelsPerPoint']
    width, height = int((x1 - x0) * scale), int((y1 - y0) * scale)
    from PIL import Image, ImageDraw
    import rasterio.features
    from affine import Affine
    ink = Image.new('L', (width, height), 0)
    pen = ImageDraw.Draw(ink)
    pixel = lambda p: ((p[0] - x0) * scale, (p[1] - y0) * scale)
    for drawing in source.drawings:
        r = drawing['rect']
        if not (x0 <= r.x0 and y0 <= r.y0 and r.x1 <= x1 and r.y1 <= y1):
            continue
        grey = drawing.get('fill') and .7 < drawing['fill'][0] < .9
        thin = drawing['type'] == 's' and (drawing.get('width') or 0) < .04
        if grey:
            geometry = drawing_polygon(drawing)
            for part in shapely.get_parts(geometry):
                for ring in [part.exterior, *part.interiors]:
                    pen.line([pixel(p) for p in ring.coords], fill=255, width=settings['strokePixels'])
        elif thin:
            for item in drawing['items']:
                if item[0] == 'l':
                    pen.line([pixel(tuple(item[1])), pixel(tuple(item[2]))], fill=255, width=settings['strokePixels'])
    closed = binary_closing(np.array(ink) > 0, structure=np.ones((settings['closingPixels'],) * 2))
    cells, _ = label(~closed)
    seeds = {int(n): list(points) for n, points in settings['seedPagePoints'].items()}
    for n, indices in settings['componentSeedFromDrawing'].items():
        seeds[int(n)] = [drawing_polygon(source.drawings[i]).representative_point().coords[0] for i in indices]
    transform = Affine(1 / scale, 0, x0, 0, 1 / scale, y0)
    results = {}
    for n, points in seeds.items():
        ids = {int(cells[int(pixel(p)[1]), int(pixel(p)[0])]) for p in points}
        mask = np.isin(cells, list(ids))
        parts = [shape(g) for g, v in rasterio.features.shapes(mask.astype('uint8'), mask=mask, transform=transform) if v]
        geometry = unary_union(parts).simplify(.08, preserve_topology=True)
        for index in settings['extraFilledDrawings'].get(str(n), []):
            geometry = geometry.union(drawing_polygon(source.drawings[index]))
        results[n] = polygonal(geometry)
    return results


def register_region(units, main_id, main_geometry, inset_parts=()):
    """Main-map drawing, replaced inside each inset's footprint by the inset drawing."""
    main = units[main_id]
    geometry = polygonal(main['model'].geometry(main_geometry.intersection(main['clip'])))
    for inset_id, inset_geometry in inset_parts:
        inset = units[inset_id]
        footprint = polygonal(inset['model'].geometry(inset['clip']))
        detail = polygonal(inset['model'].geometry(inset_geometry.intersection(inset['clip'])))
        geometry = polygonal(geometry.difference(footprint).union(detail.intersection(footprint)))
    return geometry


def administrative_drawings(units, sources, settings, controls, tracing):
    oag = lambda page: sources[('oag', page)]
    regions = {}
    page_numbers = {'boards': 1, 'councils': 2, 'societies': 3}
    for page in controls['pages']:
        drawings = oag(page_numbers[page['mapId']]).drawings
        for entry in page['areaDrawings']:
            geometry = unary_union([drawing_polygon(drawings[i]) for i in entry['drawingIndices']])
            for i in entry['subtractDrawingIndices']:
                geometry = geometry.difference(drawing_polygon(drawings[i]))
            insets = []
            if entry['areaId'] in settings['insetDrawings']:
                inset = unary_union([drawing_polygon(drawings[i]) for i in settings['insetDrawings'][entry['areaId']]])
                insets = [('boards-inset-mainland', inset), ('boards-inset-island', inset)]
            regions[entry['areaId']] = register_region(units, page['mapId'], geometry, insets)
    return regions


def statistical_drawings(units, source, settings):
    legend = source.statcan_legend
    by_colour = defaultdict(list)
    for code, colour in legend.items():
        by_colour[colour].append(code)
    regions = defaultdict(list)
    for colour, codes in by_colour.items():
        fills = source.statcan_fills[colour]
        registered = register_region(units, 'regions-2000', fills, [('regions-2000-inset', fills)])
        if len(codes) == 1:
            regions[codes[0]].append(registered)
            continue
        northern, southern = sorted(codes)  # 11/18 and 12/20: the higher code is the southern region
        for part in shapely.get_parts(registered):
            lat = TO_GEO(*part.centroid.coords[0])[1]
            regions[southern if lat < 49.5 else northern].append(part)
    return {code: polygonal(unary_union(parts)) for code, parts in regions.items()}


# ---------------------------------------------------------------- LHA snapping

def lha_shares(drawing, lhas, land):
    shares = {}
    for code, geometry in lhas.items():
        if not drawing.intersects(geometry):
            continue
        share = drawing.intersection(geometry).area / geometry.area
        if share >= .01:
            shares[code] = round(share, 3)
    return dict(sorted(shares.items(), key=lambda kv: -kv[1]))


def snapped(shares, threshold):
    return sorted(code for code, share in shares.items() if share >= threshold)


# ---------------------------------------------------------------- overlays

def overlay_features(units, source, unit_ids, style, legend_colours=()):
    """Printed region fills and outlines, warped to longitude/latitude.

    Printed numbers are left out: warped glyphs are illegible and inset glyphs
    would be drawn several times larger. The app labels regions itself. Inside
    an inset's footprint the inset's more detailed drawing replaces the main map.
    """
    features = []
    insets = [units[u] for u in unit_ids if units[u]['unit'].get('inset')]
    hidden = unary_union([polygonal(u['model'].geometry(u['clip'])) for u in insets]) if insets else Polygon()
    for unit_id in unit_ids:
        unit = units[unit_id]
        clip = unit['clip']
        mask = Polygon() if unit['unit'].get('inset') else hidden
        for drawing in source.drawings:
            if not source.within(drawing, clip):
                continue
            fill = drawing.get('fill')
            if fill and max(fill) < .1:
                continue
            if style == 'statcan' and colour_key(fill) == (.82, 1.0, 1.0):
                kind = 'water'
            elif style == 'statcan' and fill and colour_key(fill) not in legend_colours:
                continue
            elif fill and min(fill) > .99:
                kind = 'paper'
            elif fill:
                kind = 'fill'
            elif style == 'oag' and drawing['type'] == 's' and (drawing.get('width') or 0) < .3:
                kind = 'line'
            else:
                continue
            if kind in ('fill', 'label', 'water', 'paper'):
                geometry = drawing_polygon(drawing).intersection(clip)
                geometry = polygonal(geometry)
            else:
                geometry = unary_union(drawing_lines(drawing)).intersection(clip)
            if geometry.is_empty:
                continue
            registered = unit['model'].geometry(geometry)
            if kind != 'line':
                registered = shapely.make_valid(registered)
            if not mask.is_empty:
                registered = registered.difference(mask)
            if kind in ('fill', 'water', 'paper'):
                registered = polygonal(shapely.make_valid(registered.simplify(200, preserve_topology=True)))
                registered = unary_union([p for p in shapely.get_parts(registered) if p.area >= 500_000])
            elif kind == 'line':
                registered = registered.simplify(200)
            if registered.is_empty:
                continue
            geographic = project(registered, TO_GEO)
            if kind != 'line':
                geographic = polygonal(shapely.set_precision(shapely.make_valid(geographic), 1e-5))
            else:
                geographic = shapely.set_precision(geographic, 1e-5)
            if geographic.is_empty:
                continue
            properties = {'kind': kind, 'panel': unit_id}
            if kind in ('fill', 'paper') and fill:
                properties['fill'] = hex_colour(fill)
            features.append({'type': 'Feature', 'properties': properties, 'geometry': mapping(geographic)})
    # Dissolve same-coloured fills and water so shared edges are stored once.
    groups = defaultdict(list)
    for feature in features:
        props = feature['properties']
        if props['kind'] in ('fill', 'water', 'paper'):
            groups[(props['kind'], props.get('fill'))].append(shape(feature['geometry']))
    merged = [{'type': 'Feature', 'properties': {'kind': kind, **({'fill': fill} if fill else {})},
               'geometry': mapping(polygonal(shapely.set_precision(shapely.make_valid(unary_union(parts)), 1e-5)))}
              for (kind, fill), parts in groups.items()]
    features = merged + [f for f in features if f['properties']['kind'] == 'line']
    order = {'paper': 0, 'fill': 1, 'water': 2, 'line': 3}
    return sorted(features, key=lambda f: order[f['properties']['kind']])


def display_coverage(lhas, tolerance=500, min_island=3_000_000):
    """LHAs simplified together as a coverage, so dissolved regions share identical edges."""
    codes = list(lhas)
    simplified = shapely.coverage_simplify([lhas[c] for c in codes], tolerance)
    result = {}
    for code, geometry in zip(codes, simplified):
        parts = list(shapely.get_parts(geometry))
        kept = [p for p in parts if p.area >= min_island] or [max(parts, key=lambda p: p.area)]
        result[code] = unary_union(kept)
    return result


def label_point(geometry):
    """Pole of inaccessibility of the largest part, as [longitude, latitude]."""
    from shapely.ops import polylabel
    largest = max(shapely.get_parts(geometry), key=lambda p: p.area)
    point = polylabel(largest, tolerance=500)
    return [round(v, 4) for v in TO_GEO(point.x, point.y)]


def deliver(geometry, tolerance=400):
    """Simplify in metres, project, then snap to the published 1e-5 degree grid."""
    geographic = polygonal(project(shapely.make_valid(geometry.simplify(tolerance, preserve_topology=True)), TO_GEO))
    return polygonal(shapely.set_precision(shapely.make_valid(geographic), 1e-5))


# ---------------------------------------------------------------- organizations

def lineage_summary(record, bodies):
    if not record:
        return None
    names = [n['name'] for n in record.get('names', [])] or [record['name']]
    successors = [record['becameId']] if record.get('becameId') else record.get('serviceSuccessorIds', [])
    return {'bodyId': record['id'], 'officialName': record['name'], 'established': record.get('established'),
            'ended': record.get('ended'), 'formerNames': [n for n in names if n != record['name']],
            'successorIds': successors, 'successorNames': [bodies[s]['name'] for s in successors if s in bodies],
            'successorRelationship': 'amalgamated' if record.get('becameId') else 'services transferred' if successors else None,
            'description': record.get('description'), 'source': record.get('source')}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--skip-overlays', action='store_true')
    args = parser.parse_args()
    settings = read(RESEARCH / 'georectification-settings.json')
    controls = read(RESEARCH / 'rectification-controls.json')
    tracing = read(RESEARCH / 'council-tracing.json')
    decisions = read(RESEARCH / 'boundary-decisions.json')
    catalogue = read(PUBLIC / 'catalogue.json')
    statcan_meta = read(RESEARCH / 'statcan-2000-map.json')
    lineage = {r['id']: r for r in read(LINEAGE)['records']}
    bodies = {**lineage, **{r['id']: r for r in read(ROOT / 'research/history/bodies.json').get('records', [])}} if (ROOT / 'research/history/bodies.json').exists() else lineage
    for key, entry in settings['sources'].items():
        if sha(PUBLIC / entry['file']) != entry['sha256']:
            raise ValueError(f'Source changed: {entry["file"]}; review the registration seeds')
    if sha(PUBLIC / settings['reference']['file']) != settings['reference']['sha256']:
        raise ValueError('Reference LHA layer changed; rerun and review the registration')

    lha_features = read(PUBLIC / settings['reference']['file'])['features']
    lha_props = {f['properties']['code']: f['properties'] for f in lha_features}
    lhas = {f['properties']['code']: project(shape(f['geometry']), TO_METRES) for f in lha_features}
    land = unary_union(list(lhas.values()))
    target = Target(lhas.values())
    display_lhas = display_coverage(lhas)

    sources = {}
    for unit in settings['units']:
        key = (unit['source'], unit['page'])
        if key not in sources:
            sources[key] = SourcePage(PUBLIC / settings['sources'][unit['source']]['file'], unit['page'])
    statcan = sources[('statcan', 1)]
    statcan.statcan_legend, statcan.statcan_fills = statcan_region_fills(statcan, settings['statcanLegendSwatches'])

    units, registration_report = register_all(settings, sources, target)

    # ---- registered region drawings
    drawings = administrative_drawings(units, sources, settings, controls, tracing)
    councils = trace_councils(sources[('oag', 2)], tracing)
    areas_by_number = {(a['mapId'], a['number']): a for a in catalogue['areas']}
    for number, geometry in councils.items():
        drawings[areas_by_number[('councils', number)]['id']] = register_region(units, 'councils', geometry)
    statistical = statistical_drawings(units, statcan, settings)

    threshold = settings['snapThreshold']
    decided = {d['id']: d for d in decisions['areas']}
    features, rows = [], []
    all_areas = [(a['id'], a['mapId'], a['number'], a['sourceLabel'], a.get('bodyId')) for a in catalogue['areas']]
    all_areas += [(f"statistical-region-{e['code']}", 'regions-2000', int(e['code']), e['name'], None) for e in statcan_meta['region_legend']]
    geometries, display = {}, {}
    for area_id, map_id, number, label_text, body_id in all_areas:
        decision = decided.get(area_id, {})
        drawing = drawings[area_id] if map_id != 'regions-2000' else statistical[f'{number:02d}']
        drawing_land = polygonal(drawing.intersection(land))
        shares = lha_shares(drawing_land, lhas, land)
        snap = snapped(shares, threshold)
        codes = sorted(decision.get('lhaCodes', snap))
        geometry = polygonal(unary_union([lhas[c] for c in codes]))
        geometries[area_id] = geometry
        fit = score(drawing_land, geometry)
        reviewed = set(codes) != set(snap)
        # Confidence: how cleanly the georectified drawing resolves into whole LHAs.
        clean = all(shares.get(c, 0) >= .8 for c in codes) and not any(.2 <= v < threshold for c, v in shares.items() if c not in codes)
        confidence = decision.get('confidence') or ('high' if clean and fit['iou'] >= .8 else 'medium')
        org = lineage_summary(lineage.get(body_id), bodies) if body_id else None
        properties = {
            'id': area_id, 'name': label_text, 'framework': map_id, 'legendNumber': number, 'organization': org,
            'lhaCodes': codes, 'lhaNames': [lha_props[c]['name'] for c in codes],
            'basis': 'reviewed' if reviewed else 'drawing',
            'confidence': confidence, 'note': decision.get('note'),
            'drawingOverlap': fit['iou'], 'areaKm2': round(geometry.area / 1e6),
            'labelPoint': label_point(geometry),
        }
        features.append({'type': 'Feature', 'id': area_id, 'properties': properties, 'geometry': mapping(deliver(geometry, 150))})
        display[area_id] = unary_union([display_lhas[c] for c in codes])
        rows.append({'id': area_id, 'name': label_text, 'framework': map_id, 'legendNumber': number,
                     'drawingAreaKm2': round(drawing_land.area / 1e6), 'lhaShares': shares, 'snappedLhaCodes': snap,
                     'chosenLhaCodes': codes, 'reviewOverride': reviewed, 'note': decision.get('note'), 'drawingVsBoundary': fit,
                     'confidence': confidence})

    # ---- the five authorities on 12 December 2001, rebuilt from their predecessors
    authority_parts = defaultdict(list)
    for area_id, map_id, number, label_text, body_id in all_areas:
        record = lineage.get(body_id) if body_id else None
        if map_id in ('boards', 'councils') and record and record.get('becameId'):
            authority_parts[record['becameId']].append(area_id)
    for authority_id, members in sorted(authority_parts.items()):
        record = bodies[authority_id]
        geometry = polygonal(unary_union([geometries[m] for m in members]))
        codes = sorted({c for m in members for c in next(f for f in features if f['id'] == m)['properties']['lhaCodes']})
        features.append({'type': 'Feature', 'id': f'{authority_id}-2001', 'properties': {
            'id': f'{authority_id}-2001', 'name': record['name'].replace(' Authority', ''), 'framework': 'authorities-2001', 'legendNumber': None,
            'organization': {'bodyId': authority_id, 'officialName': record['name'], 'established': record.get('established'), 'ended': record.get('ended'),
                             'formerNames': [], 'successorIds': [], 'successorNames': [], 'successorRelationship': None,
                             'description': record.get('description'), 'source': record.get('source')},
            'predecessorIds': members, 'lhaCodes': codes, 'lhaNames': [lha_props[c]['name'] for c in codes],
            'basis': 'predecessors', 'confidence': 'high', 'note': None, 'drawingOverlap': None, 'areaKm2': round(geometry.area / 1e6),
            'labelPoint': label_point(geometry)},
            'geometry': mapping(deliver(geometry, 150))})
        display[f'{authority_id}-2001'] = unary_union([display[m] for m in members])

    # ---- coverage checks: each framework should partition the province without overlap
    coverage = {}
    for framework, members in [('boards+councils', [a for a in all_areas if a[1] in ('boards', 'councils')]),
                               ('regions-2000', [a for a in all_areas if a[1] == 'regions-2000'])]:
        assigned = defaultdict(list)
        for area in members:
            for code in next(f for f in features if f['id'] == area[0])['properties']['lhaCodes']:
                assigned[code].append(area[0])
        coverage[framework] = {'unassignedLhas': sorted(set(lhas) - set(assigned)),
                               'lhasInMoreThanOneArea': {c: ids for c, ids in sorted(assigned.items()) if len(ids) > 1}}
        print(framework, coverage[framework])

    # ---- outputs
    write_json(PUBLIC / 'historical-boundaries.geojson', {
        'type': 'FeatureCollection',
        'metadata': {'preparedOn': PREPARED_ON, 'coordinateSystem': 'EPSG:4326',
                     'method': 'Each printed region was georectified onto modern BC geography and snapped to the modern local health areas (LHAs) it covers; see georectification.json.',
                     'building blocks': 'Ministry of Health local health areas (PGMaps snapshot), Open Government Licence – British Columbia',
                     'sources': ['BC Auditor General, 1997/98 Report 3, Exhibits 3–5 (March 1998)', 'Statistics Canada, Health Indicators, April 2001']},
        'features': features}, compact=True, digits=5)
    (PUBLIC / 'boundaries').mkdir(exist_ok=True)
    for framework in ['boards', 'councils', 'societies', 'regions-2000', 'authorities-2001']:
        chosen = [f for f in features if f['properties']['framework'] == framework]
        write_json(PUBLIC / f'boundaries/{framework}.geojson', {'type': 'FeatureCollection',
                   'metadata': {'framework': framework, 'coordinateSystem': 'EPSG:4326', 'display': 'Simplified for display; use historical-boundaries.geojson for analysis.'},
                   'features': [{**f, 'geometry': mapping(polygonal(shapely.set_precision(shapely.make_valid(project(display[f['id']], TO_GEO)), 1e-4)))} for f in chosen]},
                   compact=True, digits=4)
    write_json(PUBLIC / 'georectification.json', {
        'schemaVersion': 1, 'preparedOn': PREPARED_ON, 'projectedCrs': 'EPSG:3005',
        'method': ('Each map panel is registered to the modern LHA linework (coast, provincial border and LHA edges). '
                   'Printed city dots or provincial corners give a starting position. An iterative closest-point fit then '
                   'matches every sampled source boundary point to the nearest modern edge, rejecting matches beyond a shrinking '
                   'distance threshold, and fits an affine, then quadratic, then cubic polynomial. Main maps add a smoothed '
                   'thin-plate spline for local distortion. Insets are registered separately.'),
        'accuracy': ('Distances are from each registered source boundary point to the nearest modern LHA edge or coastline. '
                     '"heldOut" refits the panel without one quarter of the map (a checkerboard of 25-point blocks) and measures '
                     'those unseen blocks. Source generalization (a 1:10-million-scale drawing) is part of the residual.'),
        'snapThreshold': threshold, 'coverage': coverage,
        'panels': registration_report, 'regions': rows}, digits=4)
    if not args.skip_overlays:
        (PUBLIC / 'rectified').mkdir(exist_ok=True)
        for map_id, unit_ids, source, style in [('boards', ['boards', 'boards-inset-mainland', 'boards-inset-island'], sources[('oag', 1)], 'oag'),
                                                ('councils', ['councils'], sources[('oag', 2)], 'oag'),
                                                ('societies', ['societies'], sources[('oag', 3)], 'oag'),
                                                ('regions-2000', ['regions-2000', 'regions-2000-inset'], statcan, 'statcan')]:
            legend_colours = set(statcan.statcan_legend.values()) if style == 'statcan' else ()
            write_json(PUBLIC / f'rectified/{map_id}.geojson', {'type': 'FeatureCollection',
                       'metadata': {'mapId': map_id, 'coordinateSystem': 'EPSG:4326', 'note': 'Original printed map, warped onto modern geography. Legends and titles are omitted.'},
                       'features': overlay_features(units, source, unit_ids, style, legend_colours)}, compact=True, digits=5)
    changed = [r['id'] for r in rows if r['reviewOverride']]
    print(f'{len(features)} boundaries written; reviewed overrides: {changed}')


if __name__ == '__main__':
    main()
