#!/usr/bin/env python3
"""Extract the City of Vancouver's marks from its February 2018 Visual Standards Guide.

The guide (https://policy.vancouver.ca/CP00103P2.pdf) draws every mark as native vector
paths and, for some lettering, as embedded font glyphs. MuPDF converts each page to SVG
with glyphs as outlines (text_as_path); a recipe keeps the elements whose drawn extent
lies inside the mark's region on its page, less any element the recipe excludes by its
fill (the guide's red "incorrect usage" crosses, a page's black backing plate) or by a box
(lettering of a clipped-away emblem under a retired mark), and writes them with only the
definitions they use. Nothing is traced, retyped, recoloured or redrawn.

The guide itself is not committed. Pass it with --source; its SHA-256 is checked first.
  python3 scripts/extract-vancouver-guide.py --source ~/Downloads/CP00103P2.pdf [--check]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_vector_region import produce  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / 'research/identity/vancouver-visual-standards-2026-11-27/extractions.json'
PACKAGE = ROOT / 'src/gallery/vancouverVisualStandards.json'
OBSERVED = '2026-11-27'
def asset_record(spec, recipe, data, box, counts, design_label):
    """A gallery record for one extracted file, in the shape the vector recoveries use."""
    page_url = f"{spec['source']}#page={recipe['page']}"
    retired = recipe.get('retired')
    partner = recipe.get('partner')
    date_note = recipe.get('dateNote') or (
        'The guide marks it as no longer in use; it gives no dates for the mark itself. February 2018 is the guide’s date.' if retired
        else 'The guide (page 7) shows how partner and departmental logos are sized beside the City emblem. It does not date these logos or say they were current; February 2018 is the guide’s date.' if partner
        else 'February 2018 is the guide’s date, not an adoption date.')
    record = {
        'id': recipe['id'],
        'label': f"Vancouver: {design_label}, {recipe['versionLabel'].split(' · ')[0].lower()}" if recipe.get('variantOf')
                 else design_label,
        'file': recipe['file'],
        'format': 'svg',
        'isVector': True,
        'containsRaster': False,
        'reconstruction': False,
        'supplied': False,
        'publisher': 'City of Vancouver',
        'sourceUrl': spec['source'],
        'sourcePage': page_url,
        'sourceLocator': f"Visual Standards Guide, PDF page {recipe['page']}: {recipe['where']}. Region recorded in the extraction recipe.",
        'sourceDate': 'February 2018' + (' (shown as no longer in use)' if retired else ''),
        'observedDate': OBSERVED,
        'dateNote': date_note,
        'evidenceType': 'native-pdf-vector-extraction',
        'notes': recipe['notes'],
        'fidelityNote': (f"The guide’s own {counts['paths']} filled paths, in its own colours and geometry, as MuPDF converts the page. "
                         'Only the mark’s paths are kept. No tracing, retyping, recolouring or redrawing.'),
        'darkBackground': recipe.get('ground') == 'dark',
        'sourceGround': recipe.get('ground', 'light'),
        'versionLabel': recipe['versionLabel'],
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'extraction': {
            'method': 'pdf-vector-region',
            'recipe': 'research/identity/vancouver-visual-standards-2026-11-27/extractions.json',
            'page': recipe['page'],
            'region': recipe['region'],
            **({'excludeFills': recipe['excludeFills']} if recipe.get('excludeFills') else {}),
            **({'excludeBoxes': recipe['excludeBoxes']} if recipe.get('excludeBoxes') else {}),
            'viewBox': box,
            'paths': counts['paths'],
            'sourceSha256': spec['sourceSha256'],
            'converter': f'PyMuPDF {pymupdf.VersionBind}'
        },
        'rightsNote': 'The guide states the emblem is the City’s property, protected by copyright and trademark, and that use needs the City’s authorization. No permission to reproduce it here has been sought.'
    }
    for key in ('variantOf', 'designLabel', 'adoption', 'alsoSeen'):
        if recipe.get(key):
            record[key] = recipe[key]
    return record


def package(spec, records):
    body = spec['body']
    gallery = [r for r in spec['extractions'] if r.get('gallery', True)]
    designs = lambda section: [r['id'] for r in gallery if r.get('section') == section and not r.get('variantOf')]
    emblem = next(iter(body['designPatch']))
    sections = [{'id': f"vancouver-{s['id']}", 'label': s['label'],
                 'marks': [emblem] if s['id'] == 'emblem' else designs(s['id'])} for s in body['sections']]
    return {
        'asOf': OBSERVED,
        'source': spec['source'],
        'sourceTitle': spec['sourceTitle'],
        'sourceSha256': spec['sourceSha256'],
        'additions': {body['id']: [records[r['id']] for r in gallery]},
        'assetPatches': body['designPatch'],
        # The emblem is the City's mark; the collection opens on it, not on the newest lockup.
        'bodyPatches': {body['id']: {'notes': body['notes'], 'cover': emblem, 'artworkSections': sections}},
        'otherViews': {r['id']: records[r['id']] for r in spec['extractions'] if not r.get('gallery', True)}
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='The guide PDF (not committed)')
    parser.add_argument('--check', action='store_true', help='Compare with the committed files instead of writing')
    args = parser.parse_args()
    spec = json.loads(RECIPES.read_text())
    source = Path(args.source).expanduser().read_bytes()
    if hashlib.sha256(source).hexdigest() != spec['sourceSha256']:
        raise SystemExit('The guide does not match the recorded SHA-256')
    document = pymupdf.open(stream=source, filetype='pdf')
    records = {}
    for recipe in spec['extractions']:
        data, box, counts = produce(recipe, document)
        if counts['images'] or counts['text'] or counts['glyphs']:
            raise ValueError(f'{recipe["id"]} is not pure vector paths: {counts}')
        # Gallery files are served from public/; the arms rendering joins the arms acquisition.
        target = ROOT / recipe.get('fileRoot', 'public') / recipe['file']
        if args.check:
            if target.read_bytes() != data:
                raise SystemExit(f'Extraction differs: {recipe["file"]}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        by_id = {r['id']: r for r in spec['extractions']}
        design = by_id.get(recipe.get('variantOf'), recipe)
        design_label = design.get('designLabel') or spec['body']['designPatch'].get(recipe.get('variantOf'), {}).get('designLabel', '')
        records[recipe['id']] = asset_record(spec, recipe, data, box, counts, design_label)
    text = json.dumps(package(spec, records), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if PACKAGE.read_text() != text:
            raise SystemExit(f'{PACKAGE.relative_to(ROOT)} differs from the recipes')
    else:
        PACKAGE.write_text(text)
    print(f'{"Verified" if args.check else "Wrote"} {len(records)} extractions and {PACKAGE.relative_to(ROOT)} with PyMuPDF {pymupdf.VersionBind}')


if __name__ == '__main__':
    main()
