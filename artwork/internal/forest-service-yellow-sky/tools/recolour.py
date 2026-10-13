#!/usr/bin/env python3
"""Recolour token-labelled SVG artwork without altering its vector geometry.

Python 3.9+; no third-party modules required.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
COLOUR = re.compile(r'^#[0-9a-fA-F]{6}$')

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Source SVG')
    parser.add_argument('--output', required=True, type=Path, help='Destination SVG')
    parser.add_argument('--palette-json', type=Path, help='JSON palette dictionary')
    parser.add_argument('--palette', help='Palette name in the dictionary')
    parser.add_argument('--set', action='append', default=[], metavar='TOKEN=#RRGGBB', help='Override a paint token; may be repeated')
    parser.add_argument('--overwrite', action='store_true', help='Permit overwriting an existing output')
    args = parser.parse_args()
    try:
        if not args.input.is_file():
            raise ValueError(f'Source SVG does not exist: {args.input}')
        if args.output.exists() and not args.overwrite:
            raise ValueError('Output exists. Choose a different file or explicitly pass --overwrite.')
        if bool(args.palette_json) != bool(args.palette):
            raise ValueError('Use --palette-json and --palette together.')
        palette: dict[str, str] = {}
        if args.palette_json:
            palettes = json.loads(args.palette_json.read_text(encoding='utf-8'))
            if args.palette not in palettes:
                raise ValueError(f'Unknown palette: {args.palette}')
            palette.update(palettes[args.palette])
        for item in args.set:
            if '=' not in item:
                raise ValueError(f'Expected TOKEN=#RRGGBB, got: {item}')
            token, colour = item.split('=', 1)
            palette[token] = colour
        if not palette:
            raise ValueError('Select a palette or supply at least one --set override.')
        if any(not isinstance(value, str) or not COLOUR.fullmatch(value) for value in palette.values()):
            raise ValueError('All paint values must be six-digit hexadecimal colours, such as #176B45.')
        tree = ET.parse(args.input)
        known = {e.get(attr) for e in tree.iter() for attr in ('data-fill', 'data-stroke') if e.get(attr)}
        unknown = set(palette) - known
        if unknown:
            raise ValueError('Paint tokens not present in this SVG: ' + ', '.join(sorted(unknown)))
        changed = 0
        for element in tree.iter():
            for attr, token_attr in [('fill', 'data-fill'), ('stroke', 'data-stroke')]:
                token = element.get(token_attr)
                if token in palette:
                    element.set(attr, palette[token])
                    changed += 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tree.write(args.output, encoding='utf-8', xml_declaration=True)
        print(f'Wrote {args.output}; updated {changed} paint attributes.')
        return 0
    except (ValueError, OSError, KeyError, ET.ParseError, json.JSONDecodeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
