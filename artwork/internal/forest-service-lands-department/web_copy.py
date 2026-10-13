"""Make the site's copy of the Lands Department seal from the supplied master.

The master is 5.6 MB: 11,600 shapes, each with an id and an editor label, and path data written as
absolute three-decimal coordinates on a 1536-unit page. The site needs none of that precision. This
keeps every shape, every group id and every transform as they are; it rounds coordinates to a tenth
of a unit (well under a pixel at any size the site shows the seal) and writes path data as relative
moves between those rounded points, so the rounding cannot accumulate along a path. Shape ids and
editor labels are dropped, and colours are written as hex so the site can recolour them.

Standard library only:

    python3 web_copy.py bcfs-lands-department-v2-editable.svg ../../../src/internal/forest-service-lands-department.svg
"""
import re
import sys

COMMAND = re.compile(r'([MLQCZHVmlqczhv])([^MLQCZHVmlqczhv]*)')
NUMBER = re.compile(r'-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?')
ARITY = {'M': 2, 'L': 2, 'Q': 4, 'C': 6, 'H': 1, 'V': 1, 'Z': 0}


def r10(value):
    """A coordinate on the tenth-of-a-unit grid, as an integer number of tenths."""
    return round(value * 10)


def fmt(tenths):
    """Tenths of a unit as the shortest SVG number: 15 -> 1.5, -5 -> -.5, 20 -> 2."""
    sign = '-' if tenths < 0 else ''
    whole, part = divmod(abs(tenths), 10)
    if part == 0:
        return f'{sign}{whole}'
    return f'{sign}{whole or ""}.{part}'


def join(values):
    """Numbers joined by commas, except before a minus sign, which separates itself."""
    out = ''
    for value in values:
        text = fmt(value)
        if out and not text.startswith('-'):
            out += ','
        out += text
    return out


def relative_path(d):
    """Absolute M/L/Q/C/H/V/Z data as relative data between rounded points."""
    x = y = sx = sy = 0  # current point and subpath start, in tenths
    parts = []
    last = ''  # the last command written, so a repeat of it can be implied
    for letter, args in COMMAND.findall(d):
        if letter.islower():
            raise ValueError(f'relative command {letter!r} in the master; expected absolute data')
        values = [float(v) for v in NUMBER.findall(args)]
        if letter == 'Z':
            parts.append('z')
            last = 'z'
            x, y = sx, sy
            continue
        n = ARITY[letter]
        for i in range(0, len(values), n):
            chunk = values[i:i + n]
            if letter == 'H':
                nx = r10(chunk[0])
                parts.append('h' + fmt(nx - x))
                last = 'h'
                x = nx
            elif letter == 'V':
                ny = r10(chunk[0])
                parts.append('v' + fmt(ny - y))
                last = 'v'
                y = ny
            else:
                points = [(r10(chunk[j]), r10(chunk[j + 1])) for j in range(0, n, 2)]
                deltas = []
                for px, py in points:
                    deltas += [px - x, py - y]
                # Every control point is relative to the segment's start, not to the previous point.
                command = {'M': 'm', 'L': 'l', 'Q': 'q', 'C': 'c'}[letter]
                if letter == 'M' and i > 0:
                    command = 'l'  # implicit lineto after a moveto's first pair
                # A command repeated is implied: its letter can be left out (never after a moveto, whose
                # implied successor is a lineto).
                letter_out = '' if command == last and command != 'm' else command
                if not letter_out and not fmt(deltas[0]).startswith('-'):
                    letter_out = ','
                parts.append(letter_out + join(deltas))
                last = command
                x, y = points[-1]
                if letter == 'M' and i == 0:
                    sx, sy = x, y
    return ''.join(parts)  # each part starts with its letter, a comma, or a minus sign


def main(source, target):
    svg = open(source, encoding='utf-8').read()
    svg = re.sub(r'\s+inkscape:(?:label|groupmode)="[^"]*"', '', svg)
    svg = svg.replace(' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"', '')
    # Shapes lose their ids; groups keep theirs, since they name the parts of the drawing.
    svg = re.sub(r'(<(?:path|circle|ellipse|rect|polygon)\b[^>]*?)\s+id="[^"]*"', r'\1', svg)
    svg = re.sub(r' d="([^"]*)"', lambda m: f' d="{relative_path(m.group(1))}"', svg)

    def geometry(m):
        return f'{m.group(1)}="{fmt(r10(float(m.group(2))))}"'

    svg = re.sub(r'\b(cx|cy|r|rx|ry)="(-?[\d.]+)"', geometry, svg)
    svg = re.sub(r'(fill|stroke)="black"', r'\1="#000000"', svg)
    svg = re.sub(r'(fill|stroke)="white"', r'\1="#FFFFFF"', svg)
    svg = re.sub(r'>\s+<', '><', svg)
    open(target, 'w', encoding='utf-8').write(svg)
    print(f'{len(svg) / 1e6:.2f} MB')


if __name__ == '__main__':
    main(*sys.argv[1:3])
