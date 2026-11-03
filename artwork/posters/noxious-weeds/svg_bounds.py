"""Where each top-level element of a Poppler SVG sits on the page, in the page's own units.

`pdftocairo -svg` writes a page as a flat list: filled paths, text runs (a group of <use> glyphs
with x and y), and images (a <use> of an <image> in <defs>, with a matrix, often inside a group
clipped to a rectangle). That is regular enough to measure without a browser: a path's bounds are
its points', a glyph run's are its glyphs' origins (with the font size added above the baseline),
an image's are its rectangle through its matrix, cut to its clip.
"""
import re

from lxml import etree

SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
NUMBER = re.compile(r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def local(element):
    return etree.QName(element).localname if isinstance(element.tag, str) else None


def href(element):
    return element.get('{%s}href' % XLINK) or element.get('href')


def matrix(transform):
    """A transform attribute as (a, b, c, d, e, f); Poppler writes only matrix() and none."""
    if not transform:
        return (1, 0, 0, 1, 0, 0)
    m = re.search(r'matrix\(([^)]*)\)', transform)
    if not m:
        raise ValueError(f'unexpected transform {transform!r}')
    return tuple(float(v) for v in NUMBER.findall(m.group(1)))


def apply(m, x, y):
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def box_of_points(points):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def path_box(d):
    values = [float(v) for v in NUMBER.findall(d)]
    # Poppler writes absolute M/L/C/Z with coordinate pairs only, so the numbers pair up.
    points = list(zip(values[0::2], values[1::2]))
    return box_of_points(points) if points else None


def intersect(a, b):
    if a is None or b is None:
        return a or b
    box = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    return box if box[0] < box[2] and box[1] < box[3] else None


class Page:
    def __init__(self, root):
        self.root = root
        self.ids = {e.get('id'): e for e in root.iter() if isinstance(e.tag, str) and e.get('id')}

    def clip_box(self, element):
        ref = element.get('clip-path')
        if not ref:
            return None
        clip = self.ids[re.search(r'#([^)]+)', ref).group(1)]
        boxes = [path_box(p.get('d')) for p in clip if local(p) == 'path']
        return box_of_points([(b[0], b[1]) for b in boxes] + [(b[2], b[3]) for b in boxes]) if boxes else None

    def bounds(self, element, outer=(1, 0, 0, 1, 0, 0)):
        """The element's bounds on the page, cut to any clip on it or inside it."""
        kind = local(element)
        own = matrix(element.get('transform'))
        a1, b1, c1, d1, e1, f1 = outer
        a2, b2, c2, d2, e2, f2 = own
        m = (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
             a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)
        if kind == 'path':
            box = path_box(element.get('d'))
            return box and box_of_points([apply(m, box[0], box[1]), apply(m, box[2], box[3]),
                                          apply(m, box[0], box[3]), apply(m, box[2], box[1])])
        if kind == 'use':
            target = self.ids.get((href(element) or '#')[1:])
            if target is not None and local(target) == 'image':
                w, h = float(target.get('width')), float(target.get('height'))
                return box_of_points([apply(m, 0, 0), apply(m, w, 0), apply(m, 0, h), apply(m, w, h)])
            x, y = float(element.get('x', 0)), float(element.get('y', 0))
            return box_of_points([apply(m, x, y)] * 2)
        if kind == 'g':
            boxes = [self.bounds(child, m) for child in element if local(child)]
            boxes = [b for b in boxes if b]
            if not boxes:
                return None
            box = box_of_points([(b[0], b[1]) for b in boxes] + [(b[2], b[3]) for b in boxes])
            clip = self.clip_box(element)
            if clip:
                clip = box_of_points([apply(outer, clip[0], clip[1]), apply(outer, clip[2], clip[3])])
            return intersect(box, clip) if clip else box
        return None

    def image_of(self, element):
        """The <image> an element draws, if it draws one."""
        for use in element.iter('{%s}use' % SVG):
            target = self.ids.get((href(use) or '#')[1:])
            if target is not None and local(target) == 'image':
                return target
        return None

    def items(self):
        """Every drawn top-level element, with its kind and bounds."""
        out = []
        for element in self.root:
            kind = local(element)
            if kind in (None, 'defs'):
                continue
            box = self.bounds(element)
            image = self.image_of(element) if kind in ('g', 'use') else None
            glyphs = element.findall('{%s}use' % SVG) if kind == 'g' and image is None else []
            out.append({
                'element': element,
                'kind': 'image' if image is not None else 'text' if glyphs else kind,
                'image': image,
                'box': box,
            })
        return out


def load(path):
    return Page(etree.parse(path, etree.XMLParser(huge_tree=True)).getroot())
