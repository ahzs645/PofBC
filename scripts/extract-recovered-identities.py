#!/usr/bin/env python3
"""Reproduce acquired publication components from hash-checked local sources.

This extracts original paths, embedded glyph outlines and original raster pixels.
It never traces images, chooses substitute fonts, invents missing geometry or
downloads a replacement source. PyMuPDF 1.26.6 is the recorded conversion version.
"""
import argparse
import base64
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/identity/missing-recovery-2026-11-20/assets-manifest.json'
SPEC = importlib.util.spec_from_file_location('identity_extraction', ROOT / 'scripts/extract-identity-expansion.py')
EXISTING = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXISTING)
NS = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', NS)
ET.register_namespace('xlink', XLINK)


def static_svg_component(source, component_name):
    """Parse the preserved static JSX subset; never execute downloaded JavaScript."""
    text = source.decode('utf-8')
    prefix = component_name + '=e=>'
    if not text.startswith(prefix):
        raise ValueError('Static component prefix differs from the documented source')
    position = len(prefix)

    def eat(token):
        nonlocal position
        if not text.startswith(token, position):
            raise ValueError(f'Unexpected static component syntax at {position}')
        position += len(token)

    def string():
        nonlocal position
        quote = text[position]
        if quote not in '`"\'':
            raise ValueError('Expected a literal string')
        position += 1
        start = position
        while text[position] != quote:
            if text[position] == '\\':
                raise ValueError('Escaped JavaScript strings are outside this extraction recipe')
            position += 1
        result = text[start:position]
        position += 1
        if '${' in result:
            raise ValueError('Template expressions are not static artwork')
        return result

    def identifier():
        nonlocal position
        match = re.match(r'[A-Za-z_$][A-Za-z0-9_$]*', text[position:])
        if not match:
            raise ValueError(f'Expected static property name at {position}')
        position += len(match[0])
        return match[0]

    def value():
        nonlocal position
        if text.startswith('(0,H.jsx', position):
            eat('(0,H.')
            if identifier() not in ('jsx', 'jsxs'):
                raise ValueError('Only static JSX nodes are supported')
            eat(')(')
            tag = string()
            eat(',')
            props = value()
            eat(')')
            return tag, props
        if text[position] in '`"\'':
            return string()
        if text[position] == '{':
            eat('{')
            properties = {}
            while text[position] != '}':
                if text.startswith('...e', position):
                    eat('...e')  # No incoming props are supplied for this original component.
                else:
                    key = string() if text[position] in '`"\'' else identifier()
                    eat(':')
                    properties[key] = value()
                if text[position] != ',':
                    break
                eat(',')
            eat('}')
            return properties
        if text[position] == '[':
            eat('[')
            children = []
            while text[position] != ']':
                children.append(value())
                if text[position] != ',':
                    break
                eat(',')
            eat(']')
            return children
        number = re.match(r'-?\d+(?:\.\d+)?', text[position:])
        if not number:
            raise ValueError(f'Nonliteral value at {position}')
        position += len(number[0])
        return number[0]

    node = value()
    if node[0] != 'svg' or text[position:].strip():
        raise ValueError('Expected exactly one complete static SVG component')
    attributes = {'clipPath': 'clip-path', 'clipRule': 'clip-rule', 'fillRule': 'fill-rule',
                  'strokeWidth': 'stroke-width', 'strokeLinecap': 'stroke-linecap',
                  'strokeLinejoin': 'stroke-linejoin', 'className': 'class'}
    allowed = {'svg', 'g', 'path', 'defs', 'clipPath', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line'}

    def serialize(element):
        tag, props = element
        if tag not in allowed:
            raise ValueError(f'Non-artwork SVG element: {tag}')
        attrs = ''.join(' ' + attributes.get(key, key) + '=' + quoteattr(str(val))
                        for key, val in props.items() if key != 'children')
        children = props.get('children', [])
        if isinstance(children, tuple):
            children = [children]
        return ('<' + tag + attrs + '>' + ''.join(serialize(child) for child in children) + '</' + tag + '>') if children else '<' + tag + attrs + '/>'

    return (serialize(node) + '\n').encode('utf-8')


def references(element):
    found = set()
    for node in element.iter():
        for key, value in node.attrib.items():
            found.update(re.findall(r'url\(#([^)]*)\)', value))
            if key in ('href', '{' + XLINK + '}href') and value.startswith('#'):
                found.add(value[1:])
    return found


def retain_definitions(original, selected):
    definitions = original.find('{' + NS + '}defs')
    if definitions is None:
        return None
    by_id = {node.get('id'): node for node in definitions.iter() if node.get('id')}
    needed = set().union(*(references(node) for node in selected))
    done = set()
    while needed - done:
        for key in sorted(needed - done):
            needed.update(references(by_id[key]))
            done.add(key)
    if not needed:
        return None
    result = ET.Element('{' + NS + '}defs')
    for child in definitions:
        if child.get('id') in needed:
            result.append(copy.deepcopy(child))
    return result


def produce(recipe, source):
    method = recipe['method']
    if method == 'static-jsx-svg':
        return static_svg_component(source, recipe['componentName'])
    if method == 'svg-embedded-raster':
        root = ET.fromstring(source)
        embedded = [node for node in root.iter() if node.tag == '{' + NS + '}image']
        if len(embedded) != 1:
            raise ValueError('Expected exactly one embedded source raster')
        href = embedded[0].get('{' + XLINK + '}href') or embedded[0].get('href')
        if not href.startswith('data:image/jpeg;base64,'):
            raise ValueError('Expected the documented embedded JPEG')
        return base64.b64decode(href.split(',', 1)[1], validate=True)
    if method == 'pdf-raster-region':
        document = fitz.open(stream=source, filetype='pdf')
        page = document[recipe.get('pageIndex', 0)]
        scale = recipe['dpi'] / 72
        return page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=fitz.Rect(recipe['bounds']),
                               alpha=recipe.get('alpha', False)).tobytes('png')
    if method == 'first-inline-svg':
        return re.search(r'<svg\b.*?</svg>', source.decode('utf-8'), re.S).group(0).encode('utf-8')
    if method == 'pdf-vector-children':
        document = fitz.open(stream=source, filetype='pdf')
        original = ET.fromstring(document[recipe.get('pageIndex', 0)].get_svg_image(text_as_path=True))
        selected = [copy.deepcopy(original[index]) for index in recipe['childIndices']]
        box = recipe['viewBox']
        result = ET.Element('{' + NS + '}svg', {
            'viewBox': ' '.join(map(str, box)), 'width': str(box[2]), 'height': str(box[3])
        })
        definitions = retain_definitions(original, selected)
        if definitions is not None:
            result.append(definitions)
        result.extend(selected)
        ET.indent(result, space='  ')
        return ET.tostring(result, encoding='utf-8', xml_declaration=True) + b'\n'
    if method == 'pdf-vector-uses':
        document = fitz.open(stream=source, filetype='pdf')
        original = ET.fromstring(document[recipe.get('pageIndex', 0)].get_svg_image(text_as_path=True))
        uses = [node for node in original.iter() if node.tag == '{' + NS + '}use']
        selected = {id(uses[index]) for index in recipe['useIndices']}
        paths = []

        def gather_paths(node, in_definitions=False):
            in_definitions = in_definitions or node.tag == '{' + NS + '}defs'
            if node.tag == '{' + NS + '}path' and not in_definitions:
                paths.append(node)
            for child in node:
                gather_paths(child, in_definitions)

        gather_paths(original)
        selected.update(id(paths[index]) for index in recipe.get('pathIndices', []))

        def prune(node):
            if id(node) in selected or node.tag == '{' + NS + '}defs':
                return copy.deepcopy(node)
            kept = ET.Element(node.tag, node.attrib)
            for child in node:
                result = prune(child)
                if result is not None:
                    kept.append(result)
            return kept if len(kept) or node.tag == '{' + NS + '}svg' else None

        result = prune(original)
        definitions = result.find('{' + NS + '}defs')
        refs = {node.get('{' + XLINK + '}href')[1:] for node in result.iter() if node.tag == '{' + NS + '}use'}
        for child in list(definitions):
            if child.get('id') not in refs:
                definitions.remove(child)
        x0, y0, x1, y1 = recipe['bounds']
        result.set('viewBox', ' '.join(map(str, [x0, y0, x1-x0, y1-y0])))
        result.set('width', str(x1-x0))
        result.set('height', str(y1-y0))
        return ET.tostring(result, encoding='utf-8', xml_declaration=True)
    generated = EXISTING.produce(recipe, source)
    if method == 'pdf-embedded-raster' and recipe.get('pixelBounds'):
        image = Image.open(io.BytesIO(generated)).crop(recipe['pixelBounds'])
        output = io.BytesIO()
        image.save(output, format='PNG')
        generated = output.getvalue()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Compare regenerated bytes without changing accepted files')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    sources = {record['file']: record for record in manifest['sources']}
    assets = {asset['id']: asset for body in manifest['bodies'] for asset in body['assets']}
    for recipe in manifest['extractions']:
        record = sources[recipe['sourceFile']]
        source = (ROOT / 'public' / record['file']).read_bytes()
        if hashlib.sha256(source).hexdigest() != record['sha256']:
            raise ValueError(f'Source checksum mismatch: {record["file"]}')
        generated = produce(recipe, source)
        target = ROOT / 'public' / assets[recipe['assetId']]['file']
        if args.check:
            if target.read_bytes() != generated:
                raise ValueError(f'Derived artwork differs: {target.relative_to(ROOT)}')
        else:
            target.write_bytes(generated)
    print(f'{"Verified" if args.check else "Rebuilt"} {len(manifest["extractions"])} source extractions (PyMuPDF {fitz.VersionBind}).')


if __name__ == '__main__':
    main()
