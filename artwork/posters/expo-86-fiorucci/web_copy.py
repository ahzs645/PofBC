"""Make the site's copy of the Expo 86 poster of Vittorio Fiorucci's artwork from the supplied master.

The master (`Expo86_Vittorio_Reconstructed.svg`) is drawn for an editor: it carries Inkscape layer
markup and a block of JSON metadata, its size is in millimetres, and its ids (`paper`, `footer`,
`poster-expo-logo`, `english-copy`) are ones the Davidson poster's drawing already uses, since its
logo and footer were taken from there. This keeps every shape, colour and letter as it is, and
changes four things:

1. Every id is prefixed `fio-` (and every reference to one with it).
2. The Inkscape layer labels are kept as `data-label`; the layer markup and the metadata go, and
   the size is the viewBox's, in user units, as the other drawings have it.
3. The title and description are reworded for the site.
4. The whitespace between tags goes.

Needs lxml:

    python3 web_copy.py Expo86_Vittorio_Reconstructed.svg ../../../src/posters/expo-86/expo-86-fiorucci.svg
"""
import re
import sys

from lxml import etree

SVG = 'http://www.w3.org/2000/svg'
INKSCAPE = 'http://www.inkscape.org/namespaces/inkscape'
PREFIX = 'fio-'

TITLE = 'Expo 86, art poster by Vittorio Fiorucci, reconstruction'
DESCRIPTION = (
    'A vector reconstruction drawn from one supplied photograph of a framed copy: four flat '
    'silhouettes, red, blue, yellow and green, pointing alternately left and right down a warm white '
    'sheet, each with a row of windows; the artist’s signature at the lower left, the stacked EXPO 86 '
    'mark below it, and the fair’s name and dates in English and French. Every letter is a path, '
    'with no embedded image or external font. Colours are estimated from the photograph and the '
    'signature is an approximate facsimile; not a verified archival facsimile.'
)


def main(source, target):
    tree = etree.parse(source, etree.XMLParser(remove_blank_text=True, huge_tree=True))
    root = tree.getroot()

    for el in root.findall(f'{{{SVG}}}metadata'):
        root.remove(el)

    # 1. Ids and the references to them.
    ids = {el.get('id') for el in root.iter() if isinstance(el.tag, str) and el.get('id')}
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

    # 2. Editor markup.
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        label = el.attrib.pop(f'{{{INKSCAPE}}}label', None)
        el.attrib.pop(f'{{{INKSCAPE}}}groupmode', None)
        if label is not None:
            el.set('data-label', label)

    # 3. Title and description, and the em dashes in the others.
    title = root.find(f'{{{SVG}}}title')
    desc = root.find(f'{{{SVG}}}desc')
    title.text, desc.text = TITLE, DESCRIPTION
    title.set('id', PREFIX + 'poster-title')
    desc.set('id', PREFIX + 'poster-description')
    root.set('aria-labelledby', f'{PREFIX}poster-title {PREFIX}poster-description')
    vb = root.get('viewBox').split()
    root.set('width', vb[2])
    root.set('height', vb[3])
    root.set('role', 'img')
    etree.cleanup_namespaces(root, top_nsmap={None: SVG})

    text = etree.tostring(root, encoding='unicode')
    with open(target, 'w', encoding='utf-8') as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>' + text)
    print(f'{len(open(source, "rb").read()):,} -> {len(text.encode()):,} bytes')


if __name__ == '__main__':
    main(*sys.argv[1:3])
