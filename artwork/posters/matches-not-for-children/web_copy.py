"""Make the site's copy of MATCHES ARE NOT FOR CHILDREN!! from the supplied master.

The master (`BCFS_Matches_Reconstructed.svg`) is 11.3 MB, and 11.2 MB of that is the painted
background: 545 paths, but 780,000 straight segments, the outlines of the paint fields written
point by point as absolute two-decimal coordinates on a grid finer than a hundredth of the sheet.
Everything else (the white reserve, the matches, the lettering, the seal, the captions) is 140 KB.

This keeps every group, colour, clip and letter of the drawing, and changes three things:

1. The paint's outlines (the paths of `#painted-background` drawn with straight lines only) are
   simplified: a point is dropped where the outline without it stays within a fifth of a poster
   unit of the original (the poster is 1000 units wide, so a fifth is 0.05 mm on a 250 mm sheet).
   The points kept are rounded to a tenth of a unit and written as relative moves between the
   rounded points, so the rounding cannot accumulate along an outline. No other path is touched.
2. Every id is prefixed `mnc-` (and every reference to one with it), so the drawing can sit in a
   page beside the other posters without its ids meeting theirs.
3. The editor's markup is dropped: the Inkscape layer labels are kept as `data-label`, and the
   whitespace between tags goes. The title and description are reworded for the site.

Needs lxml:

    python3 web_copy.py BCFS_Matches_Reconstructed.svg ../../../src/posters/forest-service/matches-not-for-children.svg
"""
import re
import sys

from lxml import etree

SVG = 'http://www.w3.org/2000/svg'
INKSCAPE = 'http://www.inkscape.org/namespaces/inkscape'
PREFIX = 'mnc-'
TOLERANCE = 0.2  # poster units an outline may move when a point is dropped
GRID = 10  # steps per poster unit the kept points are rounded to

TITLE = 'Matches Are Not for Children!! British Columbia Forest Service poster F. P. 19, reconstruction'
DESCRIPTION = (
    'A vector reconstruction drawn from one supplied photograph: yellow, orange and red paint with a '
    'white reserve, a gallows made of matches with a match figure hanging from it, the headline in '
    'dark hand-drawn capitals, the Forest Service oval seal, and the Canadian centennial mark and '
    'captions for 1966 and 1967. Every shape and letter is a path, with no embedded image or '
    'external font. The paint is simplified for the web from the reconstruction master. Details and '
    'colours are interpreted, not a verified archival facsimile.'
)

TOKEN = re.compile(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)')


def rings(d):
    """A straight-line path as closed rings of absolute points, or None if it uses anything else."""
    out, ring, command = [], None, None
    tokens = TOKEN.findall(d)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.isalpha():
            command = token
            i += 1
            if command in 'Zz':
                if ring:
                    out.append(ring)
                ring = None
            elif command not in 'ML':
                return None
            continue
        x, y = float(tokens[i]), float(tokens[i + 1])
        i += 2
        if command == 'M':
            if ring:
                out.append(ring)
            ring = [(x, y)]
            command = 'L'
        elif command == 'L' and ring is not None:
            ring.append((x, y))
        else:
            return None
    if ring:
        return None  # an open outline: leave the path as it is
    return out


def simplify(points, tolerance):
    """Douglas-Peucker on a closed ring, keeping its first point and the point farthest from it."""
    n = len(points)
    if n < 4:
        return points
    far = max(range(n), key=lambda k: (points[k][0] - points[0][0]) ** 2 + (points[k][1] - points[0][1]) ** 2)
    keep = [False] * n
    keep[0] = keep[far] = True
    stack = [(0, far), (far, n)]
    t2 = tolerance * tolerance
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        ax, ay = points[a]
        bx, by = points[b % n]
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        worst, at = -1.0, -1
        for k in range(a + 1, b):
            px, py = points[k]
            if length2 == 0:
                dist2 = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length2))
                dist2 = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if dist2 > worst:
                worst, at = dist2, k
        if worst > t2:
            keep[at] = True
            stack += [(a, at), (at, b)]
    return [p for p, kept in zip(points, keep) if kept]


def number(steps):
    """A count of grid steps as the shortest decimal: 14 -> 1.4, 5 -> .5, -5 -> -.5, 20 -> 2."""
    whole, tenth = divmod(abs(steps), GRID)
    text = f'{whole}' if not tenth else (f'.{tenth}' if not whole else f'{whole}.{tenth}')
    return ('-' if steps < 0 else '') + text


def join(numbers):
    out = ''
    for text in numbers:
        if out and not (text.startswith('-') or (text.startswith('.') and '.' in out.split(' ')[-1].split('-')[-1])):
            out += ' '
        out += text
    return out


def relative(ring_list):
    parts = []
    here = (0, 0)  # the current point, in grid steps; after z, the start of the ring just closed
    for ring in ring_list:
        grid = []
        for x, y in ring:
            step = (round(x * GRID), round(y * GRID))
            if not grid or step != grid[-1]:
                grid.append(step)
        if len(grid) > 1 and grid[-1] == grid[0]:
            grid.pop()
        if len(grid) < 3:
            continue
        moves = [number(grid[0][0] - here[0]), number(grid[0][1] - here[1])]
        lines = []
        for (x0, y0), (x1, y1) in zip(grid, grid[1:]):
            lines += [number(x1 - x0), number(y1 - y0)]
        parts.append('m' + join(moves) + ('l' + join(lines) if lines else '') + 'z')
        here = grid[0]
    return ''.join(parts)


def main(source, target):
    tree = etree.parse(source, etree.XMLParser(remove_blank_text=True, huge_tree=True))
    root = tree.getroot()

    # 1. The paint.
    before = after = 0
    for path in root.iterfind(f'.//{{{SVG}}}g[@id="painted-background"]//{{{SVG}}}path'):
        d = path.get('d')
        ring_list = rings(d)
        if not ring_list:
            continue
        before += sum(len(r) for r in ring_list)
        simple = [simplify(r, TOLERANCE) for r in ring_list]
        after += sum(len(r) for r in simple)
        path.set('d', relative(simple))

    # 2. Ids and the references to them.
    ids = {el.get('id') for el in root.iter() if el.get('id')}
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if el.get('id'):
            el.set('id', PREFIX + el.get('id'))
        for name, value in list(el.attrib.items()):
            if 'url(#' in value:
                el.set(name, re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{PREFIX}{m.group(1)})', value))
            if name.endswith('href') and value.startswith('#') and value[1:] in ids:
                el.set(name, '#' + PREFIX + value[1:])

    # 3. Editor markup, title and description.
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        label = el.attrib.pop(f'{{{INKSCAPE}}}label', None)
        el.attrib.pop(f'{{{INKSCAPE}}}groupmode', None)
        if label is not None:
            el.set('data-label', label)
    title = root.find(f'{{{SVG}}}title')
    desc = root.find(f'{{{SVG}}}desc')
    title.text, desc.text = TITLE, DESCRIPTION
    title.set('id', PREFIX + 'poster-title')
    desc.set('id', PREFIX + 'poster-description')
    root.set('role', 'img')
    root.set('aria-labelledby', f'{PREFIX}poster-title {PREFIX}poster-description')
    etree.cleanup_namespaces(root)

    text = etree.tostring(root, encoding='unicode')
    text = re.sub(r'\s+xmlns="http://www.w3.org/2000/svg"(?=[ >])', '', text)  # the nested groups' repeats
    text = text.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1) if 'xmlns="' not in text[:200] else text
    with open(target, 'w', encoding='utf-8') as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>' + text)
    print(f'paint points {before:,} -> {after:,}; {len(open(source, "rb").read()):,} -> {len(text.encode()):,} bytes')


if __name__ == '__main__':
    main(*sys.argv[1:3])
