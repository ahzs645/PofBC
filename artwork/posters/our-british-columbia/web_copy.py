"""Make the site's copy of OUR BRITISH COLUMBIA from the supplied master.

The master (`Our_British_Columbia_1986.svg`) is drawn for an editor: its emblems were pasted in with
their own namespace prefix (`ns0:`), it carries Inkscape layer markup and a block of JSON metadata,
and its ids (`paper`, `geometry`, `billing`) are the kind another drawing on the page could share.
This keeps every shape, colour and letter as it is, and changes five things:

1. Every id is prefixed `obc-` (and every reference to one with it).
2. The Inkscape layer labels are kept as `data-label`; the layer markup and the metadata go, and
   the emblems' elements are written in the drawing's own namespace.
3. The title and description are reworded for the site, and the em dashes in the emblems' own
   titles and descriptions become commas. The credit groups keep their titles and the notes on the
   words restored under the photograph's holders.
4. The white paper moves out of the first layer to just before it, and the fine print out of the
   billing layer to a layer of its own just after it (each drawn in the same place, in the same
   order), so the Posters view can dim each layer as one: the colours without the paper, the
   credits without the fine print, and the reverse.
5. The whitespace between tags goes.

Needs lxml:

    python3 web_copy.py Our_British_Columbia_1986.svg ../../../src/posters/expo-86/our-british-columbia.svg
"""
import re
import sys

from lxml import etree

SVG = 'http://www.w3.org/2000/svg'
INKSCAPE = 'http://www.inkscape.org/namespaces/inkscape'
PREFIX = 'obc-'

FINE_PRINT = ['dedication', 'processing-credit', 'acknowledgements', 'distribution-credit', 'printer-credit', 'copyright-credit']

TITLE = 'Our British Columbia, the British Columbia Pavilion film poster for Expo 86, reconstruction'
DESCRIPTION = (
    'A vector reconstruction drawn from one supplied photograph: red, white and blue rays above a '
    'yellow sunburst, the handwritten OUR and the large BRITISH COLUMBIA, the film credits in three '
    'lines, and fine print with the production emblems and the British Columbia Pavilion badge. '
    'Every letter is a path, with no embedded image or external font. A few words of fine print '
    'hidden by the photograph’s holders are restored, and marked as such. Colours, lettering and '
    'sheet proportions are interpreted, not a verified archival facsimile.'
)


def main(source, target):
    tree = etree.parse(source, etree.XMLParser(remove_blank_text=True, huge_tree=True))
    root = tree.getroot()

    for el in root.findall(f'{{{SVG}}}metadata'):
        root.remove(el)
    # The white paper is the first shape of the first layer; it goes before that layer, on its own,
    # so the stage can dim the layer's colours as one while the paper stays white.
    paper = root.find(f'.//{{{SVG}}}rect[@id="paper"]')
    layer = paper.getparent()
    layer.remove(paper)
    root.insert(root.index(layer), paper)
    # The billing layer holds both the credits and the fine print under them; the fine print gets a
    # layer of its own after it, so lighting either dims the other as one group, not glyph by glyph.
    billing = root.find(f'{{{SVG}}}g[@id="billing"]')
    ink = billing.find(f'{{{SVG}}}g')  # the billing's one inner group, which sets its ink
    fine = etree.Element(f'{{{SVG}}}g', id='fine-print', fill=ink.get('fill'))
    fine.set(f'{{{INKSCAPE}}}label', '04b, Fine print / outlined')
    for name in FINE_PRINT:
        fine.append(ink.find(f'{{{SVG}}}g[@id="{name}"]'))
    billing.addnext(fine)

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
    for el in root.iter(f'{{{SVG}}}title', f'{{{SVG}}}desc'):
        el.text = re.sub(r'\s*—\s*', ', ', el.text or '')
    etree.cleanup_namespaces(root, top_nsmap={None: SVG})

    text = etree.tostring(root, encoding='unicode')
    with open(target, 'w', encoding='utf-8') as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>' + text)
    print(f'{len(open(source, "rb").read()):,} -> {len(text.encode()):,} bytes')


if __name__ == '__main__':
    main(*sys.argv[1:3])
