#!/usr/bin/env python3
"""Build source crops and the patch review index from the pinned atlas snapshot.

Requires Pillow. SVG reference thumbnails use PofBC's existing @resvg/resvg-js.
The ledger contains human visual findings; this script does not assign fidelity
scores or declare an unreviewed drawing reviewed. Rebuild does not fetch sources.
"""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATCHER = '1e41f5e01a517d2232197ff57ba5b4f1c9d0636e'
PREFERRED = {
    'FO-green-gold': 'S35-O01',
    'FO-green-gold-light-band': 'S46-O01',
    'FO-forests': 'R15-O01',
    'FO-ministry-of-forests': 'S58-O05',
    'S56-O41': 'MC26-O02',
    'S56-O38': 'SUPPLIED-SPCA',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(path.read_text())

def safe_child(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes its root: {relative}')
    return path

def original_url(sighting, source):
    url = sighting.get('sourceUrl') or source.get('originalSourceUrl') or source.get('driveUrl')
    if url and not url.startswith(('https://', 'http://')):
        raise ValueError(f'Unsupported source URL: {url}')
    return url

def build(args):
    atlas_root = args.atlas.resolve()
    atlas = atlas_root / 'dist'
    snapshot = read_json(atlas_root / 'CODEBASE_SNAPSHOT.json')
    file_hashes = {f['path']: f['sha256'] for f in snapshot['files']}
    patcher = args.patcher.resolve()
    manifest = read_json(patcher / 'library/manifest.json')
    ledger = read_json(args.ledger)
    if snapshot['snapshotSha256'] != ledger['baseline']['atlasSnapshotSha256'] or snapshot['snapshotSha256'] != manifest['source']['snapshotSha256']:
        raise ValueError('The atlas snapshot differs from the reviewed snapshot.')
    def atlas_bytes(relative):
        path = safe_child(atlas, relative)
        data = path.read_bytes()
        if sha(data) != file_hashes.get(f'dist/{relative}'):
            raise ValueError(f'Atlas file does not match its snapshot: {relative}')
        return data, path
    for name in ['assets/catalogue.json', 'assets/object-inventory.json']:
        atlas_bytes(name)
    catalogue = read_json(atlas / 'assets/catalogue.json')
    inventory = read_json(atlas / 'assets/object-inventory.json')
    objects = {o['id']: o for o in inventory['objects']}
    sources = {s['sourceId']: s for s in catalogue['sources']}
    reviewed = {p['id']: p for p in ledger['patches']}
    patches = [(org, p) for org in manifest['orgs'] for p in org['patches'] if p['collection'] == 'patches']
    if len(reviewed) != len(ledger['patches']) or set(reviewed) != {p['id'] for _, p in patches}:
        raise ValueError('Review ledger must have exactly one entry for every patch variant.')
    output = ROOT / 'public/patch-review'
    crop_dir = output / 'crops'
    crop_dir.mkdir(parents=True, exist_ok=True)
    render_dir = ROOT / '.cache/patch-review-svg'
    render_dir.mkdir(parents=True, exist_ok=True)
    images = {}
    used = set()
    def open_source(source, obj):
        relative = source.get('fullImageUrl')
        dims = source.get('dimensions')
        page = obj.get('page')
        if not relative and page:
            entry = source.get('pageImages', {}).get(str(page))
            if entry:
                relative = entry['url']
                dims = [entry['width'], entry['height']]
        if not relative:
            return None
        if relative not in images:
            data, path = atlas_bytes(relative.split('?')[0])
            vector = path.suffix.lower() == '.svg'
            if vector:
                cached = render_dir / (sha(data) + '.png')
                if not cached.exists():
                    code = "const fs=require('fs');const{Resvg}=require(process.argv[1]);fs.writeFileSync(process.argv[3],new Resvg(fs.readFileSync(process.argv[2]),{fitTo:{mode:'width',value:700}}).render().asPng());"
                    subprocess.run(['node', '-e', code, str(ROOT/'node_modules/@resvg/resvg-js'), str(path), str(cached)], check=True, capture_output=True)
                picture = Image.open(cached).convert('RGBA')
            else:
                picture = Image.open(path).convert('RGBA')
            images[relative] = (picture, sha(data), vector)
        picture, digest, vector = images[relative]
        return picture, digest, vector, dims or list(picture.size)
    entries = []
    for org, patch in patches:
        record = reviewed[patch['id']]
        row = {**record, 'orgId': org['id'], 'orgName': org['name'], 'label': patch['label'], 'variant': patch.get('variant'), 'group': patch.get('group'), 'medium': patch['medium'], 'svgSha256': record['reviewedSvgSha256'], 'currentSvgSha256': patch['sha256'], 'preview': patch['preview'], 'limitations': patch['limitations'], 'sources': [], 'unavailableSources': []}
        for sighting in patch.get('sightings', []):
            occurrence = sighting['id']
            obj = objects.get(occurrence)
            source = sources.get(obj['sourceId']) if obj else None
            if not source:
                raise ValueError(f'{occurrence}: source inventory entry missing')
            url = original_url(sighting, source)
            opened = open_source(source, obj)
            bbox = obj.get('bbox')
            if opened is None or bbox is None:
                row['unavailableSources'].append({'occurrenceId': occurrence, 'sourceId': obj['sourceId'], 'url': url, 'page': obj.get('page'), 'reason': 'No source image supplied in the atlas' if opened is None else 'No individual crop rectangle recorded'})
                continue
            im, digest, vector, dims = opened
            x0, y0, x1, y1 = bbox
            if not (0 <= x0 < x1 <= dims[0] and 0 <= y0 < y1 <= dims[1]):
                raise ValueError(f'{occurrence}: crop outside source dimensions')
            if vector:
                box = [round(x0*im.width/dims[0]), round(y0*im.height/dims[1]), round(x1*im.width/dims[0]), round(y1*im.height/dims[1])]
            else:
                if tuple(dims) != im.size:
                    raise ValueError(f'{occurrence}: source dimensions differ from actual pixels')
                box = [round(v) for v in bbox]
            crop = im.crop(box)
            crop.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
            dest = crop_dir / f'{occurrence}.webp'
            if dest.name not in used:
                crop.save(dest, 'WEBP', quality=94, method=6)
                used.add(dest.name)
            medium = obj.get('medium', '')
            kind = 'vector' if vector else 'scan' if any(word in medium.lower() for word in ['printed', 'digital', 'document']) or obj.get('page') else 'photo'
            row['sources'].append({'occurrenceId': occurrence, 'sourceId': obj['sourceId'], 'url': url, 'cropUrl': f'patch-review/crops/{dest.name}', 'width': x1-x0, 'height': y1-y0, 'displayPixels': list(crop.size), 'sourceKind': kind, 'medium': medium, 'page': obj.get('page'), 'bbox': bbox, 'sourceDimensions': dims, 'sourceFileSha256': digest, 'cropSha256': sha(dest.read_bytes()), 'note': obj.get('notes', '')})
        if patch['id'] == 'S56-O38':
            relative = 'library/supplied/bc-spca-roundel/source/reference.jpeg'
            path = safe_child(patcher, relative)
            crop = Image.open(path).convert('RGB')
            dest = crop_dir / 'SUPPLIED-SPCA.webp'
            crop.save(dest, 'WEBP', quality=94, method=6)
            used.add(dest.name)
            row['sources'].append({'occurrenceId': 'SUPPLIED-SPCA', 'sourceId': 'Supplied SPCA reference', 'url': f'https://github.com/ahzs645/patcher/blob/{BASELINE_PATCHER}/{relative}', 'cropUrl': 'patch-review/crops/SUPPLIED-SPCA.webp', 'width': crop.width, 'height': crop.height, 'displayPixels': list(crop.size), 'sourceKind': 'photo', 'medium': 'Supplied patch photograph', 'bbox': [0,0,crop.width,crop.height], 'sourceDimensions': list(crop.size), 'sourceFileSha256': sha(path.read_bytes()), 'cropSha256': sha(dest.read_bytes()), 'note': 'The 66 × 55 supplied photograph used for the existing SPCA refinement; retained in Patcher. Its original external publication is not recorded.'})
        preferred = PREFERRED.get(patch['id'])
        row['sources'].sort(key=lambda s: (s['occurrenceId'] == preferred, s['sourceKind'] == 'photo', s['width']*s['height']), reverse=True)
        entries.append(row)
    all_ids = {p['id'] for _,p in patches}
    non_cards = {m['id'] for group in manifest['variants'] for m in group['members'][1:] if m['id'] in all_ids}
    result = {'version': 1, 'reviewedAt': ledger['reviewedAt'], 'baseline': ledger['baseline'], 'method': ledger['method'], 'statusDefinitions': ledger['statusDefinitions'], 'coordinateConvention': inventory['coordinateConvention'], 'summary': {'variants':len(entries), 'cards':len(entries)-len(non_cards), 'organizations':len({p['orgId'] for p in entries}), 'sourceCrops':len(used), 'variantsWithCrops':sum(bool(p['sources']) for p in entries), 'unavailableOccurrences':sum(len(p['unavailableSources']) for p in entries), 'partialRefinements':sum(bool(p['candidateChanges']) for p in entries), 'byStatus':dict(Counter(p['status'] for p in entries)), 'byPriority':dict(Counter(p['priority'] for p in entries))}, 'patches':entries}
    (output/'index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    # Do not silently remove unrelated or previously reviewed files.
    stale = {p.name for p in crop_dir.glob('*.webp')} - used
    if stale:
        raise ValueError(f'Unreferenced crop files require review: {sorted(stale)}')
    print(json.dumps(result['summary'], indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas', type=Path, required=True, help='Extracted snapshot root containing CODEBASE_SNAPSHOT.json and dist/')
    parser.add_argument('--patcher', type=Path, default=ROOT/'vendor/patcher')
    parser.add_argument('--ledger', type=Path, default=ROOT/'research/patches/review-2026-11-08.json')
    build(parser.parse_args())
