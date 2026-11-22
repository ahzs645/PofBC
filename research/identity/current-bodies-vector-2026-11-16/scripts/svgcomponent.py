"""Isolate one component of an official SVG: keep only the leaf shapes whose bounds lie inside a
rectangle (in the SVG's own user units), unchanged, and fit the viewBox to what remains.

    python -I svgcomponent.py SOURCE.svg x0 y0 x1 y1 OUT.svg

Element nodes are copied as they are (same path data, attributes and colours); groups left empty
are removed. Leaf bounds are computed with svgelements, including any transform on the leaf.
"""
import copy, hashlib, json, re, subprocess, sys, tempfile, os
import xml.etree.ElementTree as ET
import svgelements as se

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS); ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
LEAVES = {f'{{{NS}}}{t}' for t in ('path', 'polygon', 'polyline', 'rect', 'line', 'circle', 'ellipse')}
RENDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.cjs')


def leaf_bbox(el):
    mini = ET.Element(f'{{{NS}}}svg'); mini.append(copy.deepcopy(el))
    doc = se.SVG.parse(__import__('io').StringIO(ET.tostring(mini, encoding='unicode')))
    for e in doc.elements():
        if isinstance(e, se.Shape):
            return e.bbox(with_stroke=True)


def isolate(src, rect, out, pad=0.5):
    x0, y0, x1, y1 = rect
    tree = ET.parse(src); root = tree.getroot()
    parent = {c: p for p in root.iter() for c in p}
    removed = kept = 0
    for el in list(root.iter()):
        if el.tag in LEAVES:
            bb = leaf_bbox(el)
            if bb is None or not (bb[0] >= x0 and bb[1] >= y0 and bb[2] <= x1 and bb[3] <= y1):
                parent[el].remove(el); removed += 1
            else:
                kept += 1
    changed = True
    while changed:
        changed = False
        parent = {c: p for p in root.iter() for c in p}
        for g in list(root.iter(f'{{{NS}}}g')):
            if len(g) == 0 and g in parent:
                parent[g].remove(g); changed = True
    for k in ('x', 'y', 'enable-background', 'width', 'height', 'id'):
        root.attrib.pop(k, None)
    vb = [float(v) for v in re.split(r'[ ,]+', root.get('viewBox').strip())]
    tmp = tempfile.mkdtemp(); ET.ElementTree(root).write(f'{tmp}/a.svg')
    W = 4000
    subprocess.run(['node', RENDER, f'{tmp}/a.svg', f'{tmp}/a.png', str(W)], check=True)
    from PIL import Image
    im = Image.open(f'{tmp}/a.png'); bb = im.getchannel('A').getbbox(); k = im.width / vb[2]
    f = lambda v: f'{v:.3f}'.rstrip('0').rstrip('.')
    bx0, by0 = vb[0] + bb[0] / k - pad, vb[1] + bb[1] / k - pad
    bw, bh = (bb[2] - bb[0]) / k + 2 * pad, (bb[3] - bb[1]) / k + 2 * pad
    root.set('viewBox', f'{f(bx0)} {f(by0)} {f(bw)} {f(bh)}'); root.set('width', f(bw)); root.set('height', f(bh))
    data = ET.tostring(root, encoding='unicode')
    data = re.sub(r'>\s+<', '><', data)
    data = '<?xml version="1.0" encoding="UTF-8"?>\n' + data + '\n'
    open(out, 'w').write(data)
    return dict(out=out, source=src, sourceSha256=hashlib.sha256(open(src, 'rb').read()).hexdigest(), rect=list(rect),
                kept=kept, removed=removed, viewBox=root.get('viewBox'), bytes=len(data.encode()),
                sha256=hashlib.sha256(data.encode()).hexdigest(), images=data.count('<image'), texts=data.count('<text'))


if __name__ == '__main__':
    a = sys.argv[1:]
    print(json.dumps(isolate(a[0], tuple(map(float, a[1:5])), a[5]), indent=1))
