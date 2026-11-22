#!/usr/bin/env python3
"""Rebuild documented derivatives from archived official source pages and files.

Requires PyMuPDF (fitz) and Pillow. All source inputs are local and hash-checked.
SVG components preserve original path nodes, ancestor transforms and referenced
definitions. This is extraction, never tracing or recolouring. Run the JS builder
after this script to verify the resulting recorded checksums.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/identity/coverage-expansion-2026-11-15/assets-manifest.json'
SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_NS = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG_NS)
ET.register_namespace('xlink', XLINK_NS)


def local_name(node):
    return node.tag.split('}')[-1]


def vector_component(page, indices, bounds):
    original = ET.fromstring(page.get_svg_image(text_as_path=True))
    paths = []

    def gather(node, in_defs=False):
        in_defs = in_defs or local_name(node) == 'defs'
        if local_name(node) == 'path' and not in_defs:
            paths.append(node)
        for child in node:
            gather(child, in_defs)

    gather(original)
    if indices is None:
        result = original
    else:
        if max(indices) >= len(paths):
            raise ValueError('Source path indexing changed')
        selected = {id(paths[index]) for index in indices}

        def prune(node):
            if id(node) in selected:
                return copy.deepcopy(node)
            if local_name(node) == 'defs':
                return copy.deepcopy(node)
            result = ET.Element(node.tag, node.attrib)
            for child in node:
                kept = prune(child)
                if kept is not None:
                    result.append(kept)
            return result if len(result) or local_name(node) == 'svg' else None

        result = prune(original)
        # Drop unreferenced definitions. Retain the transitive closure of references.
        defs = next((node for node in result if local_name(node) == 'defs'), None)
        if defs is not None:
            import re
            refs = set()
            for child in result:
                if child is not defs:
                    refs.update(re.findall(r'(?:url\(#|href="#)([^)"\s]+)', ET.tostring(child, encoding='unicode')))
            changed = True
            while changed:
                changed = False
                for node in defs:
                    if node.get('id') in refs:
                        more = set(re.findall(r'(?:url\(#|href="#)([^)"\s]+)', ET.tostring(node, encoding='unicode')))
                        if not more.issubset(refs):
                            refs.update(more)
                            changed = True
            for node in list(defs):
                if node.get('id') not in refs:
                    defs.remove(node)
            if not len(defs):
                result.remove(defs)
    if bounds:
        x0, y0, x1, y1 = bounds
        result.set('viewBox', ' '.join(f'{v:.6f}'.rstrip('0').rstrip('.') for v in (x0, y0, x1-x0, y1-y0)))
        result.set('width', f'{x1-x0:.6f}'.rstrip('0').rstrip('.'))
        result.set('height', f'{y1-y0:.6f}'.rstrip('0').rstrip('.'))
    if any(local_name(node) in ('image', 'text', 'script', 'foreignObject') for node in result.iter()):
        raise ValueError('Expected only native outlined vector art')
    return ET.tostring(result, encoding='utf-8', xml_declaration=True)


def produce(recipe, source_bytes):
    mode = recipe['method']
    if mode in ('pdf-vector-paths', 'pdf-vector-page'):
        doc = fitz.open(stream=source_bytes, filetype='pdf')
        return vector_component(doc[recipe.get('pageIndex', 0)], recipe.get('pathIndices'), recipe.get('bounds'))
    if mode == 'pdf-embedded-raster':
        doc = fitz.open(stream=source_bytes, filetype='pdf')
        page = doc[recipe.get('pageIndex', 0)]
        dims = recipe['imageDimensions']
        candidates = [item for item in page.get_images(full=True) if [item[2], item[3]] == dims]
        if 'imageXref' in recipe:
            # A PDF can list a separately stored soft mask at the same dimensions.
            # A recorded xref targets the actual image in the checksum-pinned source.
            candidates = [item for item in candidates if item[0] == recipe['imageXref']]
        if len(candidates) != 1:
            raise ValueError(f'Ambiguous embedded image {dims}')
        xref, mask = candidates[0][0:2]
        pixmap = fitz.Pixmap(doc, xref)
        # Some streams decode with an entirely opaque alpha channel although their
        # soft mask is still separate. Drop that empty channel before combining.
        # Retain a non-opaque decoded alpha channel without applying the mask twice.
        if mask and pixmap.alpha and all(value == 255 for value in pixmap.samples[pixmap.n - 1::pixmap.n]):
            pixmap = fitz.Pixmap(pixmap, 0)
        if mask and not pixmap.alpha:
            pixmap = fitz.Pixmap(pixmap, fitz.Pixmap(doc, mask))
        encoded = pixmap.tobytes('png')
        if recipe.get('flipVertical'):
            # Some PDFs store rows upside down and invert them with the image
            # placement matrix. Apply that lossless row permutation for display.
            image = Image.open(io.BytesIO(encoded)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            out = io.BytesIO()
            image.save(out, format='PNG')
            encoded = out.getvalue()
        return encoded
    if mode == 'raster-crop':
        image = Image.open(io.BytesIO(source_bytes))
        image = image.crop(recipe['pixelBounds'])
        out = io.BytesIO()
        image.save(out, format='PNG')
        return out.getvalue()
    if mode == 'inline-svg':
        # Preserve the original fragment exactly, except documented namespace repair.
        text = source_bytes.decode('utf-8')
        if recipe.get('repairNamespace'):
            text = text.replace('xmlns="https://www.w3.org/2000/svg"', 'xmlns="http://www.w3.org/2000/svg"')
        ET.fromstring(text)
        return text.encode('utf-8')
    raise ValueError(f'Unknown extraction method: {mode}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Compare reproducibly generated bytes without writing')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    records = {item['file']: item for item in manifest['sources']}
    assets = {item['id']: item for body in manifest['bodies'] for item in body['assets']}
    count = 0
    for recipe in manifest['extractions']:
        source = records[recipe['sourceFile']]
        data = (ROOT / 'public' / source['file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != source['sha256']:
            raise ValueError(f'Source checksum mismatch: {source["file"]}')
        generated = produce(recipe, data)
        asset = assets[recipe['assetId']]
        target = ROOT / 'public' / asset['file']
        if args.check:
            if target.read_bytes() != generated:
                raise ValueError(f'Derived artwork differs: {asset["file"]}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(generated)
        count += 1
    print(f'{"Verified" if args.check else "Rebuilt"} {count} documented artwork extractions (PyMuPDF {fitz.VersionBind}).')


if __name__ == '__main__':
    main()
