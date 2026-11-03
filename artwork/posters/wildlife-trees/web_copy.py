"""Make the site's copy of Wildlife Trees from the supplied outlined master.

The master (`Wildlife-Trees-outlined.svg`) is 45 MB: 104,800 separate paths, each with its own id,
path data written as absolute three-decimal coordinates, and a title, description and JSON metadata
block inside every animal and context group. A browser has to build a node for every one of those
paths before it can draw the poster, and the site needs none of the editing structure.

This keeps every group that names a part of the drawing (its id and its transform), every colour,
every clip and every glyph, and changes three things:

1. Coordinates are rounded to a grid no coarser than a tenth of a poster unit (the poster is 1000
   units wide, so a tenth is 0.03 mm on the printed sheet), and a hundredth for the two identity
   marks, which are small and looked at closely. A group drawn at a smaller scale gets a finer grid
   of its own. Path data is written as relative moves between the rounded points, so the rounding
   cannot accumulate along a path.
2. Runs of sibling paths that paint the same way are joined into one path. Each is first turned
   to wind the same way round, so that under the non-zero fill rule the join paints exactly the
   union of what the separate paths painted. A path that crosses itself has loops winding both
   ways, so it is joined only with others whose bounds it cannot touch. Runs under an even-odd fill
   are left alone.
3. Shape ids, editor labels, and the titles, descriptions and metadata inside the drawing are
   dropped. The poster's own title stays, and so do the lettering groups' aria-labels.

Needs lxml and numpy:

    python3 web_copy.py Wildlife-Trees-outlined.svg ../../../src/posters/wildlife-trees/wildlife-trees.svg
"""
import math
import re
import sys

import numpy
from lxml import etree

SVG = 'http://www.w3.org/2000/svg'
INKSCAPE = 'http://www.inkscape.org/namespaces/inkscape'
XLINK = 'http://www.w3.org/1999/xlink'
TARGET = 0.1  # the coarsest grid allowed, in poster units: a tenth
FINE = 0.01  # for the identity marks, which are small and looked at closely
SCALE = 10  # grid steps per local unit, set for each group from its place on the poster

TOKEN = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
ARITY = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}


# ── Parsing to absolute segments ────────────────────────────────────────────────────────────────

def parse(d):
    """Path data as subpaths: [(start, [segment, ...], closed)], every point absolute.

    A segment is ('L', p), ('C', c1, c2, p), ('Q', c, p) or ('A', rx, ry, rotation, large, sweep, p).
    Smooth and shorthand commands are expanded, so the segments carry every control point.
    """
    tokens = TOKEN.findall(d)
    subpaths = []
    i = 0
    x = y = 0.0
    start = (0.0, 0.0)
    segments = None
    command = None
    last_cubic = last_quad = None  # reflected control points for S and T

    def begin(point):
        nonlocal segments, start
        if segments is not None:
            subpaths.append((start, segments, False))
        segments = []
        start = point

    while i < len(tokens):
        token = tokens[i]
        if token.isalpha():
            command = token
            i += 1
            if command in 'Zz':
                if segments is not None:
                    subpaths.append((start, segments, True))
                    segments = None
                x, y = start
                last_cubic = last_quad = None
                continue
        elif command is None:
            raise ValueError('path data starts with a number')
        upper = command.upper()
        relative = command.islower()
        n = ARITY[upper]
        args = [float(v) for v in tokens[i:i + n]]
        if len(args) < n:
            raise ValueError(f'short {command!r} in path data')
        i += n
        ox, oy = (x, y) if relative else (0.0, 0.0)

        if upper == 'M':
            x, y = args[0] + ox, args[1] + oy
            begin((x, y))
            command = 'l' if relative else 'L'  # a moveto's later pairs are linetos
            last_cubic = last_quad = None
            continue
        if segments is None:  # drawing after a closepath starts a new subpath at the same point
            begin((x, y))
        if upper == 'L':
            p = (args[0] + ox, args[1] + oy)
            segments.append(('L', p))
            last_cubic = last_quad = None
        elif upper == 'H':
            p = (args[0] + (x if relative else 0.0), y)
            segments.append(('L', p))
            last_cubic = last_quad = None
        elif upper == 'V':
            p = (x, args[0] + (y if relative else 0.0))
            segments.append(('L', p))
            last_cubic = last_quad = None
        elif upper == 'C':
            c1 = (args[0] + ox, args[1] + oy)
            c2 = (args[2] + ox, args[3] + oy)
            p = (args[4] + ox, args[5] + oy)
            segments.append(('C', c1, c2, p))
            last_cubic, last_quad = c2, None
        elif upper == 'S':
            c1 = (2 * x - last_cubic[0], 2 * y - last_cubic[1]) if last_cubic else (x, y)
            c2 = (args[0] + ox, args[1] + oy)
            p = (args[2] + ox, args[3] + oy)
            segments.append(('C', c1, c2, p))
            last_cubic, last_quad = c2, None
        elif upper == 'Q':
            c = (args[0] + ox, args[1] + oy)
            p = (args[2] + ox, args[3] + oy)
            segments.append(('Q', c, p))
            last_cubic, last_quad = None, c
        elif upper == 'T':
            c = (2 * x - last_quad[0], 2 * y - last_quad[1]) if last_quad else (x, y)
            p = (args[0] + ox, args[1] + oy)
            segments.append(('Q', c, p))
            last_cubic, last_quad = None, c
        elif upper == 'A':
            p = (args[5] + ox, args[6] + oy)
            segments.append(('A', args[0], args[1], args[2], int(args[3]), int(args[4]), p))
            last_cubic = last_quad = None
        x, y = segments[-1][-1]
    if segments is not None:
        subpaths.append((start, segments, False))
    return subpaths


# ── Orientation ─────────────────────────────────────────────────────────────────────────────────

def _cubic(p0, c1, c2, p3, t):
    u = 1 - t
    return (u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p3[1])


def _quad(p0, c, p1, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0], u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1])


def outline(start, segments):
    """Points along a subpath, close enough to tell which way round it winds."""
    points = [start]
    here = start
    for segment in segments:
        kind, end = segment[0], segment[-1]
        if kind == 'C':
            points += [_cubic(here, segment[1], segment[2], end, t / 8) for t in range(1, 9)]
        elif kind == 'Q':
            points += [_quad(here, segment[1], end, t / 8) for t in range(1, 9)]
        else:
            points.append(end)  # an arc's chord: the poster has 35 tiny ones, none that decide a winding
        here = end
    return points


def signed_area(subpaths):
    total = 0.0
    for start, segments, _ in subpaths:
        points = outline(start, segments)
        for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
            total += ax * by - bx * ay
    return total / 2


def crosses_itself(start, segments):
    """Whether a subpath's outline crosses itself, so that part of it winds the other way."""
    points = numpy.array(outline(start, segments))
    if len(points) < 4:
        return False
    a, b = points, numpy.roll(points, -1, axis=0)
    d = b - a

    def side(origin, direction, point):  # which side of each segment (rows) each point (columns) is on
        return (direction[:, None, 0] * (point[None, :, 1] - origin[:, None, 1])
                - direction[:, None, 1] * (point[None, :, 0] - origin[:, None, 0]))

    straddles = (side(a, d, a) * side(a, d, b)) < 0  # segment j's ends lie either side of segment i
    proper = straddles & straddles.T
    n = len(points)
    i, j = numpy.nonzero(numpy.triu(proper, 2))
    keep = ~((i == 0) & (j == n - 1))  # the first and last segments meet at the start
    return bool(keep.any())


def joinable(subpaths):
    """A path whose every part winds one way, so that joining it to others adds only its own ink."""
    if not all(closed for _, _, closed in subpaths):
        return False
    signs = {signed_area([subpath]) >= 0 for subpath in subpaths}
    if len(signs) > 1:  # a hole cut by winding the other way
        return False
    return not any(crosses_itself(start, segments) for start, segments, _ in subpaths)


def bounds(subpaths):
    points = numpy.array([point for start, segments, _ in subpaths for point in outline(start, segments)])
    (x0, y0), (x1, y1) = points.min(axis=0), points.max(axis=0)
    return x0, y0, x1, y1


def packed(items, cell=8.0):
    """Items (index, bounds) sorted into as few groups as possible in which no two bounds touch."""
    groups = []  # [indexes, {cell: [bounds]}]
    for index, box in items:
        x0, y0, x1, y1 = box
        cells = [(i, j) for i in range(int(x0 // cell), int(x1 // cell) + 1)
                 for j in range(int(y0 // cell), int(y1 // cell) + 1)]
        for indexes, grid_cells in groups:
            if not any(b[0] <= x1 and x0 <= b[2] and b[1] <= y1 and y0 <= b[3]
                       for c in cells for b in grid_cells.get(c, ())):
                break
        else:
            indexes, grid_cells = [], {}
            groups.append((indexes, grid_cells))
        indexes.append(index)
        for c in cells:
            grid_cells.setdefault(c, []).append(box)
    return [indexes for indexes, _ in groups]


def reverse(start, segments):
    """The same closed subpath, run the other way."""
    ends = [start] + [segment[-1] for segment in segments]
    out = []
    for k in range(len(segments) - 1, -1, -1):
        segment, back_to = segments[k], ends[k]
        kind = segment[0]
        if kind == 'L':
            out.append(('L', back_to))
        elif kind == 'C':
            out.append(('C', segment[2], segment[1], back_to))
        elif kind == 'Q':
            out.append(('Q', segment[1], back_to))
        else:
            _, rx, ry, rotation, large, sweep, _ = segment
            out.append(('A', rx, ry, rotation, large, 1 - sweep, back_to))
    return ends[-1], out


def wound(subpaths, positive):
    """The subpaths turned, all together, so that their total area has the sign asked for."""
    area = signed_area(subpaths)
    if (area >= 0) == positive:
        return subpaths
    if not all(closed for _, _, closed in subpaths):
        return None  # an open subpath has no inside to keep; leave the path as it is
    return [(*reverse(start, segments), True) for start, segments, _ in subpaths]


# ── Writing ─────────────────────────────────────────────────────────────────────────────────────

def grid(value):
    return round(value * SCALE)


def number(steps):
    """Grid steps as the shortest SVG number: on a hundredth grid, 150 -> 1.5, -5 -> -.05, 200 -> 2."""
    sign = '-' if steps < 0 else ''
    whole, part = divmod(abs(steps), SCALE)
    if part == 0:
        return f'{sign}{whole}'
    digits = str(part).zfill(len(str(SCALE)) - 1).rstrip('0')
    return f'{sign}{whole or ""}.{digits}'


def plain(value):
    """A number that is not on the grid (an arc's rotation), shortened."""
    text = f'{value:.3f}'.rstrip('0').rstrip('.')
    return text.replace('0.', '.', 1) if text.startswith('0.') else text.replace('-0.', '-.', 1)


def joined(texts):
    """Numbers joined so each is parsed alone: a comma, except where a minus sign or a second
    decimal point already separates them."""
    out = ''
    previous = None
    for text in texts:
        if previous is not None and not (text.startswith('-') or (text.startswith('.') and '.' in previous)):
            out += ','
        out += text
        previous = text
    return out


def write(subpaths):
    """Subpaths as relative path data between grid points."""
    parts = []
    x = y = 0
    last = ''
    for start, segments, closed in subpaths:
        sx, sy = grid(start[0]), grid(start[1])
        parts.append(('m', [number(sx - x), number(sy - y)]))
        x, y = sx, sy
        for segment in segments:
            kind = segment[0]
            ex, ey = grid(segment[-1][0]), grid(segment[-1][1])
            if kind == 'L':
                if ex == x and ey == y:
                    continue
                if ey == y:
                    parts.append(('h', [number(ex - x)]))
                elif ex == x:
                    parts.append(('v', [number(ey - y)]))
                else:
                    parts.append(('l', [number(ex - x), number(ey - y)]))
            elif kind == 'C':
                values = []
                for point in (segment[1], segment[2], segment[3]):
                    values += [number(grid(point[0]) - x), number(grid(point[1]) - y)]
                parts.append(('c', values))
            elif kind == 'Q':
                values = []
                for point in (segment[1], segment[2]):
                    values += [number(grid(point[0]) - x), number(grid(point[1]) - y)]
                parts.append(('q', values))
            else:
                _, rx, ry, rotation, large, sweep, _ = segment
                parts.append(('a', [number(grid(rx)), number(grid(ry)), plain(rotation), str(large), str(sweep),
                                    number(ex - x), number(ey - y)]))
            x, y = ex, ey
        if closed:
            parts.append(('z', []))
            x, y = sx, sy
    out = []
    for letter, values in parts:
        body = joined(values)
        # A repeated command can drop its letter (never a moveto, whose repeats are linetos, or a
        # closepath, which takes no numbers).
        if letter == last and letter not in 'mz':
            out.append(body if body.startswith('-') else ',' + body)
        else:
            out.append(letter + body)
        last = letter
    return ''.join(out)


# ── The document ────────────────────────────────────────────────────────────────────────────────

PAINT = ('fill', 'fill-rule', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin', 'clip-rule',
         'transform', 'opacity', 'fill-opacity', 'stroke-opacity', 'style', 'clip-path', 'mask')


def tag(element):
    return etree.QName(element).localname if isinstance(element.tag, str) else None


def linear_scale(transform):
    """How much a transform attribute enlarges areas, as a length: the root of its determinant."""
    total = 1.0
    for name, args in re.findall(r'(\w+)\s*\(([^)]*)\)', transform or ''):
        values = [float(v) for v in re.findall(r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', args)]
        if name == 'scale':
            total *= math.sqrt(abs(values[0] * (values[1] if len(values) > 1 else values[0])))
        elif name == 'matrix':
            total *= math.sqrt(abs(values[0] * values[3] - values[1] * values[2]))
    return total


def grid_for(element):
    """Grid steps per local unit for the paths in an element: the coarsest power of ten whose step,
    on the poster, is no larger than the target."""
    scale, target = 1.0, TARGET
    while element is not None:
        scale *= linear_scale(element.get('transform'))
        if element.get('id') == 'identity-marks':
            target = FINE
        element = element.getparent()
    return 10 ** max(0, math.ceil(math.log10(scale / target) - 1e-9))


def effective(element, name, default):
    while element is not None:
        value = element.get(name)
        if value is not None:
            return value
        element = element.getparent()
    return default


def slim(root):
    stats = {'paths': 0, 'joined': 0, 'reversed': 0, 'apart': 0, 'packed': 0, 'kept-evenodd': 0}

    # Editor-only structure and per-group notes.
    for element in list(root.iter()):
        name = tag(element)
        if name in ('title', 'desc', 'metadata') and element.getparent() is not root:
            element.getparent().remove(element)
        elif name is None:  # comments
            element.getparent().remove(element)
    for element in root.iter():
        for key in list(element.attrib):
            if key.startswith('{%s}' % INKSCAPE):
                del element.attrib[key]
        if tag(element) == 'path' and element.getparent() is not None and tag(element.getparent()) != 'defs':
            element.attrib.pop('id', None)

    # Join runs of like paths, and rewrite every path's data.
    global SCALE
    for parent in list(root.iter()):
        SCALE = grid_for(parent)
        if tag(parent) in ('defs', 'clipPath'):
            for child in parent:
                if tag(child) == 'path':
                    child.set('d', write(parse(child.get('d'))))
            continue
        run = []

        def flush():
            if not run:
                return
            first = run[0]
            nonzero = effective(first, 'fill-rule', 'nonzero') == 'nonzero'
            stroked = effective(first, 'stroke', 'none') != 'none'
            if len(run) > 1 and nonzero and not stroked:
                parsed = [parse(path.get('d')) for path in run]
                apart = [k for k, own in enumerate(parsed) if not joinable(own)]
                together = [k for k in range(len(run)) if k not in set(apart)]
                stats['apart'] += len(apart)
                if together:
                    # Turn the fewer: the joined path winds whichever way most of its parts already do.
                    positive = sum(1 if signed_area(parsed[k]) >= 0 else -1 for k in together) >= 0
                    subpaths = []
                    for k in together:
                        turned = wound(parsed[k], positive)
                        if turned is not parsed[k]:
                            stats['reversed'] += 1
                        subpaths += turned
                    run[together[0]].set('d', write(subpaths))
                    for k in together[1:]:
                        parent.remove(run[k])
                    stats['joined'] += len(together) - 1
                # A path that crosses itself keeps its own element, unless it shares one with others it
                # cannot touch: paths whose bounds are apart cannot change each other's winding. They
                # are the same ink as the joined path, so where they sit beside it changes nothing.
                for group in packed([(k, bounds(parsed[k])) for k in apart]):
                    run[group[0]].set('d', write([subpath for k in group for subpath in parsed[k]]))
                    for k in group[1:]:
                        parent.remove(run[k])
                    stats['packed'] += len(group) - 1
                run.clear()
                return
            if len(run) > 1 and not nonzero:
                stats['kept-evenodd'] += len(run)
            for path in run:
                path.set('d', write(parse(path.get('d'))))
            run.clear()

        for child in list(parent):
            if tag(child) == 'path':
                stats['paths'] += 1
                signature = tuple((key, child.get(key)) for key in PAINT)
                if run and tuple((key, run[0].get(key)) for key in PAINT) != signature:
                    flush()
                extra = set(child.attrib) - set(PAINT) - {'d'}
                if extra:  # an id kept for a reason, or something unexpected: leave it alone
                    flush()
                    child.set('d', write(parse(child.get('d'))))
                    continue
                run.append(child)
            else:
                flush()
        flush()

    for element in root.iter():
        for key in ('cx', 'cy', 'r', 'rx', 'ry', 'x', 'y', 'width', 'height'):
            value = element.get(key)
            if value is not None and tag(element) != 'svg' and re.fullmatch(r'-?[\d.]+', value):
                SCALE = grid_for(element.getparent())
                element.set(key, number(grid(float(value))))
    return stats


def main(source, target):
    parser = etree.XMLParser(huge_tree=True, remove_blank_text=True)
    tree = etree.parse(source, parser)
    root = tree.getroot()
    stats = slim(root)
    etree.cleanup_namespaces(root)
    text = etree.tostring(root, encoding='unicode')
    text = text.replace(' xmlns:inkscape="%s"' % INKSCAPE, '')
    with open(target, 'w', encoding='utf-8') as out:
        out.write(text)
    print(f"{stats['paths']} paths, {stats['joined']} joined into their neighbours "
          f"({stats['reversed']} turned to wind the same way); {stats['apart']} that cross themselves, "
          f"packed {stats['apart'] - stats['packed']} paths of ink that cannot touch; "
          f"{stats['kept-evenodd']} left apart under even-odd")
    print(f'{len(text) / 1e6:.2f} MB')


if __name__ == '__main__':
    main(*sys.argv[1:3])
