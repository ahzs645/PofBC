#!/usr/bin/env python3
"""Compose the 1984 Spring visitors study from photographs and native type outlines.

No image tracing, font download or system font is involved. Change design.json to
adjust the composition. The glyph table comes from PofBC's TeX Gyre Termes table.
Run from any directory: python3 artwork/posters/super-natural-spring/source/build.py
"""
from __future__ import annotations

import argparse
import base64
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[2]
SITE = (ROOT / 'src/posters/super-natural-spring' if (ROOT / 'src/hydro/serif.js').exists()
        else PACKAGE / 'gallery')
DESIGN = json.loads((HERE / 'design.json').read_text())
TYPE = json.loads((HERE / 'type-glyphs.json').read_text())
ITALIC = json.loads((HERE / 'type-glyphs-italic.json').read_text())
GLYPHS = TYPE['glyphs']
KERNING = TYPE['kerning']


def n(value):
    return format(value, '.6f').rstrip('0').rstrip('.') or '0'


def esc(value):
    return html.escape(str(value), quote=True)


def data_url(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def fitted_letter(char, box, index, outline=True):
    glyph = GLYPHS[char]
    l, t, r, b = glyph['box']
    x, y, w, h = box
    sx, sy = w / (r - l), h / (b - t)
    transform = f'matrix({n(sx)} 0 0 {n(sy)} {n(x-l*sx)} {n(y-t*sy)})'
    if outline:
        return (f'<path id="spring-letter-{index:02d}" data-letter="{esc(char)}" '
                f'transform="{transform}" d="{glyph["d"]}"/>')
    return (f'<text id="spring-letter-{index:02d}" transform="{transform}" x="0" y="0" '
            'font-family="TeX Gyre Termes, Nimbus Roman, Times New Roman, serif" font-size="1000">'
            + esc(char) + '</text>')


def run(text, x, baseline, width, size=7.8, fill='#85898b', tracking=0, outline=True, italic=False):
    glyphs = ITALIC['glyphs'] if italic else GLYPHS
    kerning = ITALIC['kerning'] if italic else KERNING
    positions = []
    cursor = 0
    ink_left = None
    ink_right = None
    for i, char in enumerate(text):
        if i:
            cursor += kerning.get(text[i-1] + char, 0)
        glyph = glyphs[char]
        positions.append(cursor)
        if 'box' in glyph:
            ink_left = min(ink_left if ink_left is not None else 1e9, cursor + glyph['box'][0])
            ink_right = max(ink_right if ink_right is not None else -1e9, cursor + glyph['box'][2])
        cursor += glyph['w'] + tracking
    sx = width / (ink_right - ink_left)
    sy = size / 1000
    tx = x - ink_left*sx
    opening = (f'<g data-text="{esc(text)}" fill="{fill}" '
               f'transform="matrix({n(sx)} 0 0 {n(sy)} {n(tx)} {n(baseline)})">')
    if outline:
        letters = ''.join(f'<path transform="translate({n(pos)} 0)" d="{glyphs[char]["d"]}"/>'
                          for char, pos in zip(text, positions) if 'd' in glyphs[char])
    else:
        letters = (f'<text x="{" ".join(n(pos) for pos in positions)}" y="0" '
                   'font-family="TeX Gyre Termes, Nimbus Roman, Times New Roman, serif" '
                   f'font-size="1000" font-style="{"italic" if italic else "normal"}" font-kerning="none">' + esc(text) + '</text>')
    return opening + letters + '</g>'


def document(*, variant='both', text_only=False, outline=True):
    vintage = PACKAGE/'photos/vintage-orcas.png'
    gemini = PACKAGE/'photos/alternate-orcas.jpeg'
    metadata = {
        'work': DESIGN['title'], 'historicalDate': 1984,
        'award': 'ADCC Gold 1985, Consumer Magazine Ad',
        'originalCredits': {'client': 'Tourism B.C.', 'agency': 'McKim Advertising',
            'writerAndCreativeDirector': 'Alvin Wasserman',
            'designerAndArtDirector': 'Bill Cozens', 'photographer': 'Peter Thomas'},
        'status': 'Modern reconstruction; supplied reconstructed photographs and fitted serif outlines.',
        'typography': DESIGN['headline']['basis'],
        'sources': DESIGN['sources'], 'uncertainCopy': DESIGN['uncertainCopy'],
        'photoSources': ['Vintage Orcas in British Columbia Waters.png',
                        'Gemini_Generated_Image_6ia0526ia0526ia0.jpeg'],
        'fontTable': 'PofBC src/hydro/serif.js, TeX Gyre Termes Regular (GUST Font License)',
        'printSize': '12.4 × 8.36 inches; chosen export size, not a measurement of the original'
    }
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 620 418" width="12.4in" height="8.36in" '
        'role="img" aria-labelledby="spring-title spring-description">',
        '<title id="spring-title">So many of our visitors return in Spring.</title>',
        '<desc id="spring-description">A reconstruction of the 1984 Tourism B.C. magazine advertisement. '
        'Three orcas surface beneath forested mountains. The headline, two columns of copy and '
        'Super,Natural British Columbia signature are rebuilt as serif outlines. The photographs '
        'are supplied modern recreations. The exact historical typeface remains unconfirmed.</desc>',
        '<metadata>'+esc(json.dumps(metadata,ensure_ascii=False))+'</metadata>',
        '<defs><clipPath id="spring-photo-window"><rect x="0" y="53" width="620" height="365"/></clipPath></defs>',
    ]
    if not text_only:
        parts.append('<g id="spring-paper"><rect width="620" height="418" fill="#ffffff"/></g>')
        if variant in ('both', 'vintage'):
            parts.append('<g id="spring-photo-vintage" clip-path="url(#spring-photo-window)">'
                         '<image x="0" y="53" width="620" height="365" preserveAspectRatio="xMidYMid slice" '
                         f'xlink:href="{data_url(vintage,"image/png")}"/></g>')
        if variant in ('both', 'gemini'):
            hidden = ' display="none"' if variant == 'both' else ''
            # The alternate's extra sky lies above the original picture window.
            parts.append(f'<g id="spring-photo-gemini" clip-path="url(#spring-photo-window)"{hidden}>'
                         '<image x="0" y="0" width="620" height="417.933227" '
                         f'xlink:href="{data_url(gemini,"image/jpeg")}"/></g>')
    parts.append('<g id="spring-copy" aria-label="Travel information">')
    for row in DESIGN['copy']:
        parts.append(run(**row,outline=outline))
    credit = DESIGN['credit']
    parts.append(run(**credit,fill='#85898b',outline=outline))
    if not text_only:
        # Deliberately keep the unreadable reply code as evidence, not an invented transcription.
        code = PACKAGE/'photos/reply-code-facsimile.png'
        if code.exists():
            parts.append('<image id="spring-reply-code-facsimile" x="589" y="30" width="18" height="8" '
                         f'xlink:href="{data_url(code,"image/png")}">'
                         '<title>Unresolved reply code retained from the supplied reference</title></image>')
    parts.append('</g>')
    parts.append('<g id="spring-wordmark" aria-label="Super,Natural British Columbia">')
    parts.append(run(**DESIGN['wordmark'],fill='#444b50',tracking=-30,outline=outline))
    parts.append('</g>')
    parts.append('<g id="spring-headline" fill="#ffffff" data-text="'+esc(DESIGN['title'])+'">')
    parts.extend(fitted_letter(row['char'],row['box'],i,outline=outline) for i,row in enumerate(DESIGN['headline']['letters']))
    parts.append('</g></svg>')
    return '\n'.join(parts)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proof', action='store_true', help='also write a transparent typography-only SVG')
    args = parser.parse_args()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE/'spring-visitors.svg').write_text(document(),encoding='utf-8')
    (PACKAGE/'spring-visitors.svg').write_text(document(variant='vintage'),encoding='utf-8')
    (PACKAGE/'spring-visitors-alternate.svg').write_text(document(variant='gemini'),encoding='utf-8')
    (PACKAGE/'spring-visitors-editable-text.svg').write_text(document(variant='vintage',outline=False),encoding='utf-8')
    if args.proof:
        (PACKAGE/'review/typography.svg').write_text(document(text_only=True),encoding='utf-8')
    print('Built the gallery master and two standalone photograph variants.')
