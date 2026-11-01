#!/usr/bin/env python3
"""Turn GeoLibre's edited pixel CSV into a separate, reviewable control proposal.

Never overwrites the active rectification-controls.json. Coordinates are checked
against the exact image manifest and converted back to original PDF page points.
"""
import argparse
import copy
import csv
import math
from pathlib import Path

import numpy as np

from rectify_health_maps import PUBLIC, RESEARCH, TO_METRES, fit_affine, read, sha, write


def import_gcps(map_id, csv_path, image_directory):
    manifest = read(image_directory / 'image-manifest.json')
    image = next((entry for entry in manifest['images'] if entry['mapId'] == map_id), None)
    if not image:
        raise ValueError('Map not found in image manifest')
    if sha(image_directory / image['file']) != image['sha256']:
        raise ValueError('Source image checksum changed; do not use a resized/replaced image')
    baseline = read(RESEARCH / 'rectification-controls.json')
    if baseline['sourceSha256'] != manifest['sourceSha256']:
        raise ValueError('Image manifest refers to a different source PDF')
    controls, seen = [], set()
    with Path(csv_path).open(newline='') as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ['pixelX', 'pixelY', 'lng', 'lat']:
            raise ValueError('Expected GeoLibre CSV header pixelX,pixelY,lng,lat')
        for line_number, row in enumerate(reader, 2):
            try:
                px, py, lng, lat = [float(row[key]) for key in reader.fieldnames]
            except (ValueError, TypeError):
                raise ValueError(f'Invalid numeric control on CSV line {line_number}') from None
            if not all(math.isfinite(value) for value in [px, py, lng, lat]):
                raise ValueError(f'Non-finite control on CSV line {line_number}')
            if not (0 <= px <= image['width'] and 0 <= py <= image['height'] and -180 <= lng <= 180 and -90 <= lat <= 90):
                raise ValueError(f'Control outside image/world bounds on CSV line {line_number}')
            key = (round(px, 6), round(py, 6))
            if key in seen:
                raise ValueError(f'Duplicate pixel control on CSV line {line_number}')
            seen.add(key)
            controls.append({'name': f'GeoLibre edited control {len(controls) + 1}',
                             'pagePoint': [round(px / image['pixelsPerPdfPoint'] + image['pageOrigin'][0], 6),
                                           round(py / image['pixelsPerPdfPoint'] + image['pageOrigin'][1], 6)],
                             'longitudeLatitude': [lng, lat], 'targetBasis': 'Imported from GeoLibre CSV; physical landmark identification and independence require review.'})
    if len(controls) < 3:
        raise ValueError('At least three non-collinear controls are required')
    targets = np.array([[*TO_METRES(*point['longitudeLatitude']), 1] for point in controls])
    if np.linalg.matrix_rank(targets) < 3:
        raise ValueError('Ground controls must not collapse to one point or line')
    _, residuals = fit_affine(controls)
    proposal = copy.deepcopy(baseline)
    next(page for page in proposal['pages'] if page['mapId'] == map_id)['controls'] = controls
    proposal.update(candidateOnly=True, method='Proposed BC Albers affine fit of the registered main maps, with GeoLibre-edited controls for ' + map_id + '.',
                    controlLimitation='Imported controls are a proposal. Fit residuals measure training consistency, not independent accuracy; physical landmarks and held-out checkpoints remain to be reviewed.',
                    proposal={'mapId': map_id, 'imageSha256': image['sha256'], 'csvSha256': sha(Path(csv_path)),
                              'reviewStatus': 'pending-review', 'activeBaselineOverwritten': False,
                              'trainingRmseMetres': round(math.sqrt(sum(r * r for r in residuals) / len(residuals)), 3),
                              'independentAccuracyEstablished': False})
    return proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map', required=True, choices=['boards', 'councils', 'societies'])
    parser.add_argument('--csv', required=True, type=Path)
    parser.add_argument('--images', type=Path, default=PUBLIC / 'geolibre')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.out.resolve() == (RESEARCH / 'rectification-controls.json').resolve():
        parser.error('Write the proposal to a separate path; the active control file is protected')
    proposal = import_gcps(args.map, args.csv, args.images)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write(args.out, proposal)
    print(f'Wrote {len(next(p for p in proposal["pages"] if p["mapId"] == args.map)["controls"])} proposed controls; active baseline unchanged: {args.out}')


if __name__ == '__main__':
    main()
