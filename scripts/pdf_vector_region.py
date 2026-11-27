"""Keep the native vector artwork a PDF draws inside one region of one page, as SVG.

MuPDF converts the page to SVG with glyphs as outlines (text_as_path). `produce` keeps the elements
whose drawn extent lies inside the region, less any the recipe excludes by fill or by box, and
writes them with only the definitions they use. Nothing is traced, retyped, recoloured or redrawn.
Used by scripts/extract-vancouver-guide.py and for single extractions recorded in research notes.

A recipe is { page (1-based), region: [x0, y0, x1, y1] in PDF points from the top-left,
excludeFills?: ["#c22134", "" for unfilled], excludeBoxes?: [[x0, y0, x1, y1]] }.
"""
import copy
import re
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', NS)
ET.register_namespace('xlink', XLINK)
TAG = lambda name: '{' + NS + '}' + name
HREF = ('href', '{' + XLINK + '}href')
NUMBER = re.compile(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def multiply(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f)


def matrix_of(node):
    value = node.get('transform')
    if not value:
        return (1, 0, 0, 1, 0, 0)
    result = (1, 0, 0, 1, 0, 0)
    for kind, args in re.findall(r'(matrix|translate|scale)\(([^)]*)\)', value):
        nums = [float(x) for x in NUMBER.findall(args)]
        if kind == 'matrix':
            step = tuple(nums)
        elif kind == 'translate':
            step = (1, 0, 0, 1, nums[0], nums[1] if len(nums) > 1 else 0)
        else:
            step = (nums[0], 0, 0, nums[1] if len(nums) > 1 else nums[0], 0, 0)
        result = multiply(result, step)
    return result


def points_of(d):
    """Every point a path's data reaches or pulls toward. MuPDF writes absolute M, L, H, V, C and Z."""
    tokens = re.findall(r'[A-Za-z]|' + NUMBER.pattern, d)
    points, at, command, x, y = [], 0, None, 0.0, 0.0
    sizes = {'M': 2, 'L': 2, 'C': 6, 'Q': 4, 'H': 1, 'V': 1, 'Z': 0}
    while at < len(tokens):
        if tokens[at].isalpha():
            command = tokens[at]
            if command not in sizes:
                raise ValueError(f'Unexpected path command {command}')
            at += 1
            if command == 'Z':
                continue
        args = [float(v) for v in tokens[at:at + sizes[command]]]
        at += sizes[command]
        if command == 'H':
            x = args[0]
        elif command == 'V':
            y = args[0]
        else:
            pairs = list(zip(args[0::2], args[1::2]))
            points.extend(pairs[:-1])
            x, y = pairs[-1]
        points.append((x, y))
    return points


def extent(points, m):
    a, b, c, dd, e, f = m
    xs, ys = [], []
    for x, y in points:
        xs.append(a * x + c * y + e)
        ys.append(b * x + dd * y + f)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def drawn(root):
    """Each drawn element outside <defs>, with its composed matrix, its extent and its fill."""
    definitions = {node.get('id'): node for node in root.iter() if node.get('id')}
    found = []

    def walk(node, m, fill, in_defs):
        if node.tag == TAG('defs') or in_defs:
            return
        m = multiply(m, matrix_of(node))
        fill = node.get('fill', fill)
        if node.tag == TAG('path'):
            found.append((node, extent(points_of(node.get('d', '')), m), fill))
        elif node.tag == TAG('use'):
            target = definitions[(node.get(HREF[1]) or node.get(HREF[0]))[1:]]
            inner = multiply(m, matrix_of(target))
            pts = [p for part in target.iter(TAG('path')) for p in points_of(part.get('d', ''))]
            found.append((node, extent(pts, inner), fill))
        for child in node:
            walk(child, m, fill, False)

    walk(root, (1, 0, 0, 1, 0, 0), None, False)
    return found


def references(node):
    refs = set()
    for element in node.iter():
        for key, value in element.attrib.items():
            refs.update(re.findall(r'url\(#([^)]*)\)', value))
            if key in HREF and value.startswith('#'):
                refs.add(value[1:])
    return refs


def produce(recipe, document):
    page = document[recipe['page'] - 1]
    root = ET.fromstring(page.get_svg_image(text_as_path=True))
    x0, y0, x1, y1 = recipe['region']
    excluded = {colour.lower() for colour in recipe.get('excludeFills', [])}
    tolerance = 0.5
    selected = [(node, box) for node, box, fill in drawn(root)
                if box and box[0] >= x0 - tolerance and box[1] >= y0 - tolerance
                and box[2] <= x1 + tolerance and box[3] <= y1 + tolerance
                and (fill or '').lower() not in excluded
                and not any(box[0] >= e[0] and box[1] >= e[1] and box[2] <= e[2] and box[3] <= e[3]
                            for e in recipe.get('excludeBoxes', []))]
    if not selected:
        raise ValueError(f'Nothing drawn inside {recipe["id"]}')
    keep = {id(node) for node, _ in selected}

    def prune(node):
        if node.tag == TAG('defs'):
            return None
        if id(node) in keep:
            return copy.deepcopy(node)
        kept = ET.Element(node.tag, node.attrib)
        for child in node:
            result = prune(child)
            if result is not None:
                kept.append(result)
        return kept if len(kept) else None

    body = prune(root)
    # The definitions the kept elements use (glyph outlines and clip paths), and theirs in turn.
    by_id = {node.get('id'): node for node in root.iter() if node.get('id')}
    needed, done = references(body), set()
    while needed - done:
        for key in sorted(needed - done):
            needed |= references(by_id[key])
            done.add(key)
    bx0 = min(box[0] for _, box in selected)
    by0 = min(box[1] for _, box in selected)
    bx1 = max(box[2] for _, box in selected)
    by1 = max(box[3] for _, box in selected)
    box = [round(v, 3) for v in (bx0, by0, bx1 - bx0, by1 - by0)]
    svg = ET.Element(TAG('svg'), {'viewBox': ' '.join(map(str, box)), 'width': str(box[2]), 'height': str(box[3])})
    if needed:
        defs = ET.SubElement(svg, TAG('defs'))
        for node in root.iter():
            if node.get('id') in needed and node.tag != TAG('svg'):
                defs.append(copy.deepcopy(node))
    for child in body:
        svg.append(child)
    ET.indent(svg, space=' ')
    data = ET.tostring(svg, encoding='utf-8', xml_declaration=True) + b'\n'
    counts = {
        'paths': sum(1 for node, _ in selected if node.tag == TAG('path')),
        'glyphs': sum(1 for node, _ in selected if node.tag == TAG('use')),
        'images': len(list(svg.iter(TAG('image')))),
        'text': len(list(svg.iter(TAG('text'))))
    }
    return data, box, counts


